import json
import logging
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import boto3
from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

S3 = boto3.client("s3")
CW = boto3.client("cloudwatch", region_name="us-east-1")

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
SIZE_THRESHOLD_BYTES = int(os.getenv("SIZE_THRESHOLD_BYTES", str(100 * 1024**3)))
TIMEZONE = os.getenv("TIMEZONE", "US/Eastern")
LOG_TZ = ZoneInfo(TIMEZONE)


def ts() -> str:
    return datetime.now(tz=LOG_TZ).isoformat()


def log(message: str, **extra) -> None:
    payload = {"timestamp": ts(), "message": message, **extra}
    LOGGER.info(json.dumps(payload, default=str))


def list_buckets_paginated():
    response = S3.list_buckets()
    for bucket in response.get("Buckets", []):
        yield bucket["Name"]


def get_bucket_tags(bucket_name: str) -> dict[str, str]:
    try:
        response = S3.get_bucket_tagging(Bucket=bucket_name)
        return {item["Key"]: item["Value"] for item in response.get("TagSet", [])}
    except ClientError as exc:
        code = exc.response["Error"].get("Code", "Unknown")
        if code in {"NoSuchTagSet", "NoSuchBucket"}:
            return {}
        raise


def has_lifecycle_policy(bucket_name: str) -> bool:
    try:
        S3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return True
    except ClientError as exc:
        code = exc.response["Error"].get("Code", "Unknown")
        if code == "NoSuchLifecycleConfiguration":
            return False
        if code == "NoSuchBucket":
            log("Bucket disappeared during evaluation", bucket=bucket_name)
            return True
        raise


def get_bucket_size_bytes(bucket_name: str) -> int | None:
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=3)

    for storage_type in ("StandardStorage", "StandardIAStorage", "GlacierStorage"):
        response = CW.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="BucketSizeBytes",
            Dimensions=[
                {"Name": "BucketName", "Value": bucket_name},
                {"Name": "StorageType", "Value": storage_type},
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=["Average"],
        )
        datapoints = sorted(
            response.get("Datapoints", []),
            key=lambda x: x["Timestamp"],
            reverse=True,
        )
        if datapoints:
            return int(datapoints[0]["Average"])

    return None


def standard_policy() -> dict:
    return {
        "Rules": [
            {
                "ID": "auto-tier-standard-ia-30d-glacier-180d",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Transitions": [
                    {"Days": 30, "StorageClass": "STANDARD_IA"},
                    {"Days": 180, "StorageClass": "GLACIER"},
                ],
                "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
            }
        ]
    }


def apply_policy(bucket_name: str) -> None:
    if DRY_RUN:
        log(
            "DRY_RUN enabled - would apply lifecycle policy",
            bucket=bucket_name,
            policy=standard_policy(),
        )
        return

    S3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration=standard_policy(),
    )
    log("Lifecycle policy applied", bucket=bucket_name)


def retryable(fn, *args, **kwargs):
    retries = 3
    delay = 1.0

    for attempt in range(1, retries + 1):
        try:
            return fn(*args, **kwargs)
        except ClientError as exc:
            code = exc.response["Error"].get("Code", "Unknown")
            if code in {
                "Throttling",
                "ThrottlingException",
                "TooManyRequestsException",
                "RequestTimeout",
                "InternalError",
            } and attempt < retries:
                log("Retrying after AWS API error", error_code=code, attempt=attempt)
                time.sleep(delay)
                delay *= 2
                continue
            raise


def evaluate_bucket(bucket_name: str) -> dict:
    log("Evaluating bucket", bucket=bucket_name)

    if retryable(has_lifecycle_policy, bucket_name):
        log("Bucket already has lifecycle policy - skip", bucket=bucket_name)
        return {"bucket": bucket_name, "action": "skip_existing_policy"}

    tags = retryable(get_bucket_tags, bucket_name)
    if tags.get("lifecycle-exempt", "").lower() == "true":
        log("Exempt - No Action Taken", bucket=bucket_name)
        return {"bucket": bucket_name, "action": "skip_exempt"}

    size_bytes = retryable(get_bucket_size_bytes, bucket_name)
    if size_bytes is None:
        log("No CloudWatch size metric returned - skip", bucket=bucket_name)
        return {"bucket": bucket_name, "action": "skip_no_metric"}

    if size_bytes <= SIZE_THRESHOLD_BYTES:
        log("Bucket below threshold - skip", bucket=bucket_name, size_bytes=size_bytes)
        return {
            "bucket": bucket_name,
            "action": "skip_below_threshold",
            "size_bytes": size_bytes,
        }

    retryable(apply_policy, bucket_name)
    return {
        "bucket": bucket_name,
        "action": "applied",
        "size_bytes": size_bytes,
        "dry_run": DRY_RUN,
    }


def lambda_handler(event, context):
    results = []
    errors = 0

    for bucket_name in list_buckets_paginated():
        try:
            results.append(evaluate_bucket(bucket_name))
        except ClientError as exc:
            errors += 1
            log(
                "Bucket evaluation failed",
                bucket=bucket_name,
                error_code=exc.response["Error"].get("Code", "Unknown"),
                error_message=exc.response["Error"].get("Message", ""),
            )

    summary = {
        "timestamp": ts(),
        "dry_run": DRY_RUN,
        "evaluated": len(results) + errors,
        "successful_evaluations": len(results),
        "errors": errors,
        "results": results,
    }
    log("Run complete", summary=summary)
    return summary

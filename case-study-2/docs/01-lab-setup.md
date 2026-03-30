# 01. Lab Setup — Case Study 2

## Goal
Show a real deployment path for the Lambda + Scheduler solution.

## Components
- 1 Lambda function
- 1 EventBridge Scheduler schedule
- 1 IAM role with least privilege
- CloudWatch Logs group
- test S3 buckets:
  - `demo-bucket-no-policy`
  - `demo-bucket-exempt`
  - `demo-bucket-with-policy`

## Suggested test cases

1. Bucket has lifecycle already -> skip
2. Bucket is <100 GB -> skip
3. Bucket has `lifecycle-exempt=true` -> skip
4. Bucket is >100 GB and no policy -> apply policy
5. `DRY_RUN=true` -> log only, no mutation

## Test note
`BucketSizeBytes` is a daily metric. In a lab, you may need to wait for metrics or temporarily lower the size gate in code for functional testing.

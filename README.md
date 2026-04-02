# Cloud & Storage Engineering Case Study

Prepared By  **Mohammed Tahir Khan**

This repository is designed for a README-driven walkthrough and covers both case studies.

## What is included

- **Case Study 1 — 400TB Hybrid Data Dilemma**
  - architecture diagram 
  - decision matrix (SnapMirror vs DataSync)
  - FinOps cost model
  - cutover and rollback playbook
  - data integrity strategy
  - Python pre-check orchestrator for 300 volumes
  - lab setup and mock execution guidance

- **Case Study 2 — Automated S3 Lifecycle Enforcement**
  - production-style Lambda code in Python/Boto3
  - Terraform for EventBridge Scheduler, Lambda, CloudWatch logging, IAM
  - DRY_RUN support
  - pagination, retry handling, exemption-tag logic
  - scale-out redesign notes

## Recommended presentation flow

1. Open `case-study-1/diagrams/hybrid-data-migration-architecture.svg`
2. Walk through `case-study-1/docs/01-executive-architecture.md`
3. Use `case-study-1/docs/02-decision-matrix.md` to justify SnapMirror + targeted archive pattern
4. Use `case-study-1/docs/03-finops-cost-model.md` to show savings
5. Use `case-study-1/docs/04-cutover-and-rollback.md` for operations depth
6. Show `case-study-1/automation/netapp_cutover_precheck.py`
7. Move to `case-study-2/src/main.py`
8. Finish with `case-study-2/terraform/` and `case-study-2/docs/02-scale-redesign.md`

### Case Study 1 
Use a **hybrid approach**:
- **SnapMirror** for hot and warm NAS volumes that must cut over within the 4-hour window
- **Metadata-led cold data identification** before cutover
- **Direct archive path to S3 Glacier Flexible Retrieval** for data older than 3 years
- **FSx for ONTAP capacity pool tier** for warm data accessed between 1 and 3 years

This keeps the final cutover predictable while still satisfying FinOps.

### Case Study 2 
Use **EventBridge Scheduler + Lambda + CloudWatch Logs + least-privilege IAM**, with:
- strict skip logic for exempt buckets
- CloudWatch `BucketSizeBytes` daily metrics
- safe mode through `DRY_RUN=true`
- idempotent lifecycle application only when needed

## Assumptions used in the cost model

- Total dataset: **400 TB**
- Cold data (>3 years): **60% = 240 TB**
- Warm data (1–3 years): **20% = 80 TB**
- Hot data (<1 year): **20% = 80 TB**
- Pricing is **illustrative**, based on current public AWS pricing pages and should be region-tuned in AWS Pricing Calculator before delivery.

## demo lab

See:
- `case-study-1/docs/06-lab-setup.md`
- `case-study-2/docs/01-lab-setup.md`

## Quick commands

```bash
# run case study 1 mock pre-check
python3 case-study-1/automation/netapp_cutover_precheck.py --mock --output reports/precheck.csv

# package lambda zip locally
cd case-study-2/src && zip -r ../lambda_bundle.zip main.py

# terraform plan
cd ../terraform
terraform init
terraform plan -var="lambda_zip=../lambda_bundle.zip"
```

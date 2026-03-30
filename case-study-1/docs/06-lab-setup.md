# 06. Lab Setup — Case Study 1

## Goal
Create a small but explainable demo environment.

## Suggested lab components

### On-prem simulation
- 1 Linux VM running simulator or a placeholder NAS export
- directory trees representing 3 classes:
  - hot
  - warm
  - cold
- CSV inventory describing 20 mock volumes

### AWS side
- 1 VPC
- 1 FSx for ONTAP file system
- optional EC2 instance for validation
- 1 S3 bucket for archive landing
- 1 Glacier lifecycle-enabled bucket/prefix

## Demo flow

1. Build mock inventory for 20 volumes.
2. Generate synthetic cold percentage report.
3. Show which volumes are:
   - full SnapMirror candidates
   - mixed volumes requiring owner review
   - archive-heavy candidates
4. Run the Python pre-check script against a mock JSON API response.
5. Export RAG status CSV.
6. Walk the cutover checklist.

## Files to demo
- `automation/netapp_cutover_precheck.py`
- `automation/sample_snapmirror_status.json`
- `automation/sample_output_precheck.csv`

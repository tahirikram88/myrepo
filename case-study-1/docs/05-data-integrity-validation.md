# 05. Data Integrity Validation Strategy

## Goal
Validate migration quality without forcing a full 400 TB re-read.

## Multi-layer strategy

### 1. Replication health evidence
Use SnapMirror transfer logs and relationship state as the first line of evidence.

### 2. Statistical file validation
Sample across:
- top 20 business-critical volumes
- all protocol types
- small, medium, and large file populations
- high-churn and low-churn datasets

Check:
- file count
- directory count
- total logical bytes
- random sample hashes
- metadata parity where relevant

### 3. Application validation
Technical parity is necessary but not sufficient.
Run business smoke tests:
- source code checkout/build access
- CAD or media open tests
- user home/share access
- app service account validation

### 4. Namespace validation
Confirm:
- junction paths
- export policies
- SMB share names
- DNS aliases
- quotas and snapshots as designed

### 5. Exception register
Track any mismatch with:
- source volume
- path
- issue type
- severity
- owner
- go/no-go impact

## Recommended line

> “I would combine platform evidence, sampled checksum validation, and business smoke tests. I do not need to re-read 400 TB to make a credible cutover decision.”

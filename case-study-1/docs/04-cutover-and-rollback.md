# 04. Cutover and Rollback Playbook

## Pre-cutover conditions (must all be green)

- SnapMirror relationship healthy for all in-scope volumes
- latest transfer completed successfully
- lag within approved threshold
- destination volumes mounted and export/share configuration validated
- security style, ACL behavior, junction paths, qtrees, quota settings reviewed
- DNS records prepared with low TTL ahead of cutover
- client mount scripts / DFS referrals / autofs maps pre-staged
- application owners on bridge and business validation plan ready
- rollback command sheet prepared and tested

## Go / No-Go criteria

### Go
- 100% of critical volumes = green
- amber volumes only if explicitly waived
- no red volume in critical app chain
- no unresolved identity, ACL, or namespace issue
- test client mounts succeed from AWS target
- monitoring confirms target network path healthy

### No-Go
- final mirror update exceeds forecast
- lag breach on critical volume
- destination permission mismatch
- critical client unable to remount
- business smoke tests fail
- incident on Direct Connect / routing / DNS

## Cutover runbook

1. Freeze writes on source applications.
2. Confirm final user communication sent.
3. Quiesce and update SnapMirror relationships.
4. Wait for final transfer completion.
5. Break mirrors on destination volumes.
6. Present destination volumes through target SVM interfaces.
7. Update DNS/DFS/autofs/client mount targets.
8. Validate sample NFS and SMB clients.
9. Execute app smoke tests.
10. Monitor errors, locks, permissions, and latency.
11. Declare success only after business owner sign-off.

## DNS and client strategy

### NFS
Prefer mount abstraction:
- automounter maps
- CNAMEs that point to current NAS endpoint
- staged mount change scripts for static clients

### SMB
Prefer:
- DFS Namespace or DNS aliasing
- SPN/computer object planning if needed
- test Kerberos and NTLM flows before the change

TTL must be reduced well before the event, not during the event.

## Rollback plan

1. Stop client writes to AWS target.
2. Unmount or disable client access to destination shares/exports.
3. Restore client mappings to on-prem target names or IPs.
4. Re-enable source write access.
5. Re-run validation on source.
6. Capture divergence window and incident notes.
7. Resume mirror relationship only after root cause is resolved.

## Important rollback rule

Keep the on-prem source authoritative and recoverable until:
- business validation is complete
- audit logs are reviewed
- the post-cutover stabilization period ends

## soundbite

> “Rollback is not a vague intention. It is a pre-written sequence that restores client access to the original authoritative source before any data divergence becomes unmanageable.”

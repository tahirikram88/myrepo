# 01.Architecture

## Recommended architecture

The winning design is **not** pure SnapMirror and **not** pure DataSync.

It is a **two-lane migration**:

### Lane A — Hot/Warm production cutover path
Use **NetApp SnapMirror** from on-prem ONTAP to **Amazon FSx for NetApp ONTAP** for:
- active engineering shares
- application-bound NAS volumes
- all datasets that need a deterministic final delta sync
- volumes where near-zero downtime matters more than object-level filtering

### Lane B — Cold data optimization path
Use a **metadata-first classification workflow** to identify files untouched for 3+ years.
Cold data is then:
- exported out of the file path before final cutover window
- written to **Amazon S3**
- lifecycle-managed to **S3 Glacier Flexible Retrieval**

Warm data (1–3 years) stays in FSx for ONTAP, but is expected to age into the **capacity pool tier** instead of remaining on SSD.

## Why this is the best interview answer

A pure DataSync answer sounds FinOps-friendly, but it creates cutover risk:
- file-by-file comparison takes longer than block replication
- the last incremental over 300 volumes is much less predictable
- large metadata trees and many small files can blow out the maintenance window

A pure SnapMirror answer sounds operationally safe, but it fails the FinOps mandate because it mirrors entire volumes as-is.

The hybrid pattern resolves the conflict:
- **SnapMirror handles the cutover**
- **classification and archive handle the waste**

## Data classes

| Class | Definition | Target |
|---|---|---|
| Hot | Accessed within 12 months | FSx ONTAP SSD |
| Warm | Accessed between 12 and 36 months | FSx ONTAP, expected to age into capacity pool |
| Cold | Not accessed for more than 36 months | S3 + Glacier Flexible Retrieval |

## Migration sequence

1. Inventory 300+ volumes and business owners.
2. Run low-impact metadata scan from a mounted analytics host or secondary mirror/SnapLock/reporting context.
3. Produce volume-level cold percentage report.
4. Select archive candidates:
   - whole stale directories
   - dormant project shares
   - old release trees
   - old home drives and compliance-retained content
5. Pre-stage hot/warm data to FSx with SnapMirror.
6. Continuously update replication until cutover day.
7. Execute go/no-go checks.
8. Quiesce source workloads.
9. Run final SnapMirror update.
10. Break mirror, present new NFS/SMB endpoints, and validate.
11. Keep source read-only for rollback window.

# 02. Decision Matrix — SnapMirror vs DataSync

## Decision summary

| Criterion | NetApp SnapMirror | AWS DataSync | Verdict |
|---|---|---|---|
| Final cutover predictability | Excellent | Moderate | SnapMirror wins |
| Block-level efficiency | Excellent | No | SnapMirror wins |
| Preserve ONTAP efficiencies/snapshots | Yes | No | SnapMirror wins |
| Filter out cold files | No | Yes | DataSync wins |
| Operate at 300-volume scale for final delta | Strong | Riskier | SnapMirror wins |
| Direct route to S3 archive | Indirect | Native destination option | DataSync wins |
| Best fit for 4-hour maintenance window | Strong | Conditional | SnapMirror wins |

## safe verdict

### Primary migration engine
**SnapMirror** is the primary engine for production NAS cutover because it gives the most defensible answer for the 4-hour downtime constraint.

### Secondary optimization engine
Use **targeted archive workflows** for cold data before or alongside the migration program:
- report-driven archive of cold datasets to S3
- optional DataSync use only for scoped archive jobs, not for the final all-volume cutover
- isolate low-value data from the mirror set rather than forcing DataSync to own the whole migration

## Bandwidth framing

Use this formula in the interview:

```text
Transfer time (seconds) = dataset_bytes / effective_bytes_per_second
```

### Illustrative baseline
400 TB over a **1 Gbps** effective path:
- 1 Gbps ≈ 125 MB/s theoretical
- after protocol overhead and real-world efficiency, assume ~90–100 MB/s usable
- 400 TB would take **well over 40 days**

400 TB over a **10 Gbps** effective path:
- assume ~0.9–1.0 GB/s usable
- baseline roughly **4.5 to 5.5 days**

That means:
- **1 Gbps is not viable**
- **10 Gbps is just barely feasible**
- **multiple links / compression / pre-seeding / aggressive pre-stage window** greatly improve safety

## Best practice position

- Use **Direct Connect** rather than VPN for predictable throughput and latency.
- Start baseline replication well before the cutover week.
- Reduce the mirror set by archiving cold data first.
- Group volumes into waves based on business criticality and change rate.
- Reserve the 4-hour window only for final delta, validation, and client remount activity.

## What to say when challenged

> “I would not stake a 300-volume global NAS cutover on a file-walk engine during the final maintenance window. I would use SnapMirror for deterministic delta sync, and solve FinOps with pre-classification and archive segregation rather than making the cutover tool carry both objectives.”

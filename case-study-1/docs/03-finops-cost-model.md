# 03. FinOps Cost Model

## Costing method

Use the public AWS pricing pages only as **illustrative list prices** and then re-run the numbers in AWS Pricing Calculator for the target region.

### Assumed split
- Total data: 400 TB
- Hot: 80 TB
- Warm: 80 TB
- Cold: 240 TB

## Scenario A — Bad pattern: full lift-and-shift to FSx SSD

If all 400 TB is treated like active NAS and effectively charged at high-performance FSx storage, the monthly bill is materially higher and cold data wastes premium file-storage spend.

## Scenario B — Recommended pattern

### Hot data
80 TB stays performance-oriented in FSx ONTAP SSD.

### Warm data
80 TB stays on FSx ONTAP but is expected to age into the **capacity pool tier** for lower $/GB-month.

### Cold data
240 TB bypasses premium NAS economics and lands in **Amazon S3 Glacier Flexible Retrieval**.

### Illustrative storage math
- 400 TB on premium file storage is the costliest option.
- Moving 240 TB of cold data off premium NAS avoids paying file-system economics for archive content.
- Warm data kept in ONTAP capacity tier gives you namespace continuity without paying SSD economics for everything.

## Soundbite

> “My design pays premium storage rates only for premium behavior.”

## Savings narrative to use verbally

1. The mandate says up to 60% is dead data.
2. If that is true, a lift-and-shift means premium spend on 240 TB that produces no productivity value.
3. The hybrid design keeps only the data that actually needs file semantics and low-latency access in FSx.
4. Archive content is redirected to object/archive economics.

## Example presentation line

> “Even before throughput, backups, and request costs, the big cost lever is simply avoiding the mistake of storing 240 TB of dead data on a premium NAS target.”

## Extra FinOps controls

- chargeback by business unit from scan report
- archive approval workflow for data owners
- tag archive buckets by source volume, owner, retention class, and restore priority
- monthly access review of warm tier growth
- restore SLA classes:
  - P1 restore: hot path
  - P2 restore: warm path
  - P3 restore: archive retrieval

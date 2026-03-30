# Automation Proposal — Option 2

This repo implements **Option 2** from the prompt because it is stronger :
it shows operational thinking for the actual cutover day.

## What it checks per volume

- SnapMirror relationship state
- lag time
- last transfer type
- last transfer end time
- health flag
- last transfer error (if any)

## Output
- per-volume **Red / Amber / Green**
- one consolidated CSV
- overall **GO / NO-GO**

## RAG policy

### Green
- state = SnapMirrored
- healthy = true
- lag <= threshold
- no transfer error

### Amber
- healthy but lag above warning threshold
- stale update but still within possible recovery window

### Red
- broken mirror
- unhealthy relation
- failed recent transfer
- lag above hard stop threshold

## Why this is friendly
It maps directly to the operations mandate and proves you are thinking like a cutover engineer, not just a slide architect.

# 02. Scale Redesign

## Problem
A single Lambda can time out if the account contains thousands of buckets and serial metric lookups become too slow.

## Fan-out redesign

### Option A — Step Functions Map state
1. Scheduler triggers a controller Lambda.
2. Controller lists buckets and chunks them into batches.
3. Step Functions Map distributes batches to worker Lambdas.
4. Each worker evaluates its subset and writes structured results.
5. Aggregator summarizes actions and failures.

### Option B — SQS fan-out
1. Scheduler triggers a producer Lambda.
2. Producer enqueues one message per bucket.
3. Worker Lambda consumes from SQS with reserved concurrency controls.
4. DLQ captures failures.

## Why this is better
- horizontal scale
- better retry isolation
- lower blast radius
- clearer observability per bucket/batch


> “If the serial Lambda approaches the 15-minute ceiling, I would decouple listing from evaluation and turn the bucket loop into a fan-out/fan-in workflow.”

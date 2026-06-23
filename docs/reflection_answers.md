# Engineering Reflection

## What trade-off does this architecture make?

It favors simplicity, low administration, and current-state lookups over rich
historical analytics. A single country partition key overwrites the previous
snapshot. That is appropriate for a compact portfolio serving layer but not for
trend analysis or audit-grade history.

## Why retain raw JSON?

Raw retention separates source acquisition from business logic. It supports
reprocessing, debugging, schema comparison, and evidence of what the provider
returned. Without it, a transformation defect can be difficult to reproduce
after the API changes.

## Why not catch every exception and return partial success?

Infrastructure failures are materially different from rejected business rows.
A bad row can be counted and skipped. A failed S3 read or DynamoDB batch means
the pipeline cannot prove that the snapshot was loaded, so the invocation must
fail and become visible to retry and monitoring systems.

## How is idempotency handled?

Country is both the logical grain and DynamoDB partition key. Reprocessing the
same file writes the same country keys, replacing their values instead of
creating duplicates. The result is idempotent at the table-key level, although
the processing timestamp changes.

## What would be changed for production at larger scale?

- Use infrastructure as code and separate development/staging/production stacks.
- Write immutable, date-partitioned raw keys and attach source metadata.
- Send invalid rows and rejection reasons to a quarantine dataset.
- Add schema/version contracts and source-quality checks.
- Emit custom metrics and configure alarms and failure destinations.
- Add CI/CD, dependency locking, security scans, and integration tests.
- Move analytical history to S3/Glue/Athena or a warehouse.

## How is testability achieved?

Validation and mapping are pure functions. The handler keeps AWS interaction at
the edges, allowing tests to replace S3 loading, timestamps, and the DynamoDB
resource. Tests therefore run without credentials, network access, or billable
AWS resources.

## What data caveats remain?

The upstream API is public and can change availability, definitions, field
population, or update cadence. The simple active-case risk label ignores
population scale, reporting differences, and clinical context. It is a
technical demonstration, not health guidance.


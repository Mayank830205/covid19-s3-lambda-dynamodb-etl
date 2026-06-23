# Architecture Explanation

## Why S3 is the pipeline boundary

The extractor and transformer are deliberately decoupled. S3 provides a durable
raw copy, absorbs timing differences, and permits replay when transformation
logic changes. A direct API-to-DynamoDB process would be simpler but would lose
the original input after each run.

## Why Lambda

The source dataset is small and event-oriented, so a continuously running
service would add operational work without improving throughput. Lambda starts
on demand, integrates with S3 notifications, sends logs to CloudWatch, and uses
an execution role without embedded credentials.

## Why DynamoDB

The primary access pattern is "return the latest item for this country."
DynamoDB serves that lookup efficiently through the `country` partition key.
Batch writing fits the approximately country-sized source collection, and
on-demand capacity is a practical default for intermittent loads.

This design is not optimized for historical time-series analysis. If history
becomes a requirement, add a sort key such as `snapshot_date`, retain a
date-partitioned S3 curated layer, or load an analytical warehouse.

## Failure model

- Extraction HTTP or JSON failures stop before upload.
- S3 read or document-shape failures fail Lambda.
- Individual domain validation failures increment `rejected_records`.
- DynamoDB failures fail Lambda after SDK retries.
- Successful runs satisfy:
  `input_records = clean_records + rejected_records` and
  `clean_records = inserted_records`.

## Security model

The bucket and table remain private. Lambda receives only object-read,
table-write, and log-write permissions. The fixed-object policy is the preferred
deployment baseline; the prefix policy is useful when date-partitioned source
keys are introduced.

Encryption at rest is provided by AWS-managed encryption by default and can be
upgraded to customer-managed KMS keys. If a customer-managed key is used, add
only the required KMS permissions for that key.

## Operational model

CloudWatch Logs records start, rejected indexes, completion summary, and stack
traces on failures. Recommended alarms include:

- Lambda `Errors > 0`
- Lambda `Throttles > 0`
- duration approaching configured timeout
- dead-letter queue or on-failure destination messages
- a custom rejection-rate metric above an agreed threshold


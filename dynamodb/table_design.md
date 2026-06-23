# DynamoDB Table Design

## Table definition

| Setting | Value |
|---|---|
| Table name | `covid_country_stats` |
| Partition key | `country` (String) |
| Sort key | none |
| Recommended billing mode | On-demand |
| Recommended recovery | Point-in-time recovery enabled |
| Recommended encryption | AWS-owned key or a scoped customer-managed KMS key |

## Item contract

```text
country             String   required, partition key, uppercase
continent           String   required
population          Number   required
total_cases         Number   required
active_cases        Number   required
recovered           Number   required
deaths              Number   required
critical            Number   required
cases_per_million   Number   required
risk_level          String   required: LOW | MEDIUM | HIGH
processed_at_utc    String   required, ISO 8601
```

## Primary access patterns

| Access pattern | DynamoDB operation |
|---|---|
| Get the latest snapshot for one country | `GetItem(country="INDIA")` |
| Load or refresh all country snapshots | `BatchWriteItem` through `batch_writer()` |
| Explore the full current snapshot | `Scan` with pagination |

`Query` is also demonstrated in the notebook for a partition-key equality
condition. With a single-partition-key item, `GetItem` is the more direct
production operation for one country.

## Idempotency and overwrite behavior

Each country has one item. Reprocessing replaces attributes on the same
partition key rather than creating a duplicate. The Lambda batch writer uses
`overwrite_by_pkeys=["country"]` to de-duplicate repeated keys within its local
buffer.

## Capacity notes

The source contains only a few hundred records, so on-demand capacity is a safe
starting point. Provisioned capacity may cost less for a highly predictable
schedule, but should be selected only after observing consumed capacity.

## Limitations

This schema stores only the latest snapshot. Historical analysis requires a sort
key such as `snapshot_date` or a separate historical table/data lake. A scan is
acceptable for this small portfolio dataset but should not become a
latency-sensitive application pattern at scale.


# Business Scenario

## Context

A public-health analytics team needs a simple, inexpensive way to expose current
country-level COVID-19 statistics to dashboards and exploratory notebooks. The
team does not want to operate servers, schedule database maintenance, or
manually normalize the public API response.

## Users and decisions

- **Analysts** compare case load and risk classification by country.
- **Operations teams** identify countries with elevated active-case levels.
- **Data engineers** monitor data freshness, rejected rows, and load success.
- **Application developers** retrieve a country snapshot by primary key.

The table is a serving dataset, not a clinical decision system. `risk_level` is
a simple portfolio rule based only on active-case count; it must not be
interpreted as epidemiological advice.

## Functional requirements

1. Preserve the raw source before transformation.
2. Produce one standardized item per valid country.
3. Support direct country lookup.
4. Reject unusable records without stopping the entire batch.
5. Make every run auditable.
6. Keep cloud permissions narrow and credentials outside source code.

## Non-functional requirements

- **Availability:** managed AWS services avoid host management.
- **Scalability:** S3, Lambda, and DynamoDB scale beyond the current dataset.
- **Recoverability:** the raw object can be replayed.
- **Security:** private S3/DynamoDB resources and role-based access.
- **Maintainability:** pure transformation functions and mocked unit tests.
- **Cost control:** short Lambda executions and on-demand DynamoDB are suitable
  for a small, intermittent workload.

## Success measures

- All valid input rows are inserted or updated.
- Input equals clean plus rejected.
- Inserted equals clean for successful runs.
- Every item has a nonblank country and processing timestamp.
- No floating-point values reach DynamoDB.
- Failures are visible in CloudWatch and do not masquerade as successful runs.


# End-to-End Workflow

## 1. Extract

`extraction/extract_covid_data.py` sends a `GET` request to disease.sh. A
requests session retries HTTP 429 and transient 5xx responses with exponential
backoff. The process fails rather than silently accepting a non-array payload.

## 2. Land raw data

The response is written to `data/raw/covid_data.json` with UTF-8 encoding. The
upload script sends the file to the bucket from `BUCKET_NAME`, using
`OBJECT_KEY` or `raw/covid_data.json`.

The bucket should have block-public-access enabled. Versioning is recommended
when the fixed key is retained; a date-partitioned key is preferable when
historical raw snapshots are required.

## 3. Trigger

The Lambda can be invoked:

- by an S3 `ObjectCreated` event, in which case the event bucket/key wins; or
- manually/on a schedule, in which case `BUCKET_NAME` and `OBJECT_KEY` are used.

`TABLE_NAME` always identifies the target table. Missing configuration fails
fast with a clear error.

## 4. Read and parse

Lambda calls `GetObject`, decodes UTF-8, and parses JSON numbers directly as
`Decimal`. The top-level document must be an array and every element must be an
object.

## 5. Validate and transform

Each record is checked independently. A row is rejected when:

- `country` is absent or blank; or
- `population` is absent, invalid, zero, or negative.

Valid rows are mapped to the target schema, country is uppercased, missing
optional numbers become zero, risk is derived from active cases, and the run
timestamp is attached.

## 6. Load

Clean items are sent through the DynamoDB table resource's `batch_writer`.
Country is the overwrite key, so the table represents the most recent snapshot
for every country.

If an AWS write fails after SDK retries, the invocation fails. This avoids
returning a misleading successful audit record and allows Lambda/S3 retry or a
dead-letter strategy to handle the failure.

## 7. Audit and observe

The handler logs and returns:

- S3 source URI
- target table
- input record count
- clean record count
- rejected record count
- inserted record count
- UTC processing timestamp

CloudWatch should alarm on Lambda errors, throttles, duration near timeout, and
an abnormal rejection ratio.


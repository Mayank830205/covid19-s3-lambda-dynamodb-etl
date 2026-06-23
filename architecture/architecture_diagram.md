# Architecture Diagram

```mermaid
flowchart TB
    subgraph Source["External source"]
        API["disease.sh<br/>/v3/covid-19/countries"]
    end

    subgraph Landing["Raw data landing"]
        EXTRACT["Python extraction client<br/>retry + timeout + JSON validation"]
        S3[("Amazon S3<br/>raw/covid_data.json")]
    end

    subgraph Processing["Serverless processing"]
        EVENT["S3 ObjectCreated event<br/>or test/manual event"]
        LAMBDA["AWS Lambda (Python 3.12)<br/>load → validate → transform → audit"]
        LOGS["Amazon CloudWatch Logs"]
    end

    subgraph Serving["Serving layer"]
        DDB[("Amazon DynamoDB<br/>covid_country_stats")]
        CLIENT["Notebook / dashboard / application"]
    end

    API -->|HTTPS GET| EXTRACT
    EXTRACT -->|boto3 upload_file| S3
    S3 --> EVENT --> LAMBDA
    LAMBDA -->|GetObject| S3
    LAMBDA -->|BatchWriteItem| DDB
    LAMBDA -->|structured execution log| LOGS
    DDB -->|Scan or Query| CLIENT
```

## Trust boundaries

- The public API is untrusted input. The extractor verifies HTTP success and
  response shape; Lambda validates every record before writing.
- S3 is the durable hand-off between extraction and transformation.
- Lambda receives AWS access only from its execution role.
- DynamoDB is not public and is accessed through IAM-authenticated AWS APIs.
- CloudWatch receives execution metadata and counts, not credentials.

## Reliability properties

- API requests use timeouts and bounded retries for transient status codes.
- Raw data is stored before transformation, making a run replayable.
- DynamoDB `batch_writer()` retries unprocessed writes.
- `overwrite_by_pkeys=["country"]` collapses duplicate country writes in a
  batch and supports snapshot-style idempotency.
- A single `processed_at_utc` value identifies every item written in one run.


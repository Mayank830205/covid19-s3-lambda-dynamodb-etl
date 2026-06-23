# Transformation Specification

## Validation

| Rule | Result |
|---|---|
| `country` is missing, null, or whitespace | Reject record |
| `population` is missing, nonnumeric, zero, or negative | Reject record |
| Optional numeric field is missing or null | Use numeric zero |
| Source document is not an array of objects | Fail the invocation |

Rejecting a malformed document protects the entire contract. Rejecting an
individual bad country record allows the remaining valid countries to load.

## Field mapping

| Source field | Target field | Transformation |
|---|---|---|
| `country` | `country` | trim and uppercase |
| `continent` | `continent` | trim; default `UNKNOWN` |
| `population` | `population` | `Decimal` |
| `cases` | `total_cases` | `Decimal` |
| `active` | `active_cases` | `Decimal` |
| `recovered` | `recovered` | `Decimal` |
| `deaths` | `deaths` | `Decimal` |
| `critical` | `critical` | `Decimal` |
| `casesPerOneMillion` | `cases_per_million` | `Decimal` |
| derived | `risk_level` | threshold rule |
| generated | `processed_at_utc` | ISO 8601 UTC timestamp |

## Risk rule

```text
if active_cases >= 100000: HIGH
elif active_cases >= 10000: MEDIUM
else: LOW
```

The thresholds are inclusive. Negative active-case values, if supplied, are
classified `LOW`; a stricter domain rule can reject them in a future schema
version.

## Decimal rationale

Python floats are not accepted by boto3's DynamoDB serializer because binary
floating-point values can be imprecise. S3 JSON is parsed with
`parse_int=Decimal` and `parse_float=Decimal`, and the transformation layer also
normalizes ordinary Python test values. This keeps local tests and Lambda
behavior consistent.

## Timestamp consistency

The handler generates one timestamp before processing and reuses it for all
items and the audit response. Consumers can therefore identify which countries
belong to the same load.


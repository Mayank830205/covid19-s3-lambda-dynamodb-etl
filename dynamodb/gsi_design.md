# Optional GSI Design

No global secondary index is required for the core country lookup. If the
application must list countries by risk and rank them by case load, add:

## `risk_level-total_cases-index`

| Setting | Value |
|---|---|
| Partition key | `risk_level` (String) |
| Sort key | `total_cases` (Number) |
| Projection | `INCLUDE` |
| Included fields | `country`, `continent`, `active_cases`, `deaths`, `processed_at_utc` |

Example access patterns:

- Query all `HIGH` risk countries.
- Query `MEDIUM` risk countries in descending `total_cases` order.
- Limit to the top N countries in a risk group.

Example Python:

```python
from boto3.dynamodb.conditions import Key

response = table.query(
    IndexName="risk_level-total_cases-index",
    KeyConditionExpression=Key("risk_level").eq("HIGH"),
    ScanIndexForward=False,
    Limit=20,
)
```

## Trade-offs

The GSI adds write cost and storage because every matching item is copied into
the index. Risk level may be unevenly distributed, so it is not a suitable
high-scale partition key without further sharding. For the small country
dataset, the distribution is operationally acceptable, but the index should be
created only when the access pattern exists.


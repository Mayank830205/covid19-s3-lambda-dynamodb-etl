"""Transform and validate COVID-19 records."""

from decimal import Decimal


def get_risk_level(active_cases):
    """Return the risk level based on active cases."""
    active_cases = Decimal(str(active_cases))

    if active_cases >= 100000:
        return "HIGH"
    elif active_cases >= 10000:
        return "MEDIUM"
    else:
        return "LOW"


def validate_record(record):
    """Check whether the record is valid."""

    if not record.get("country"):
        return False

    if record.get("population", 0) <= 0:
        return False

    return True


def build_item(record, processed_at):
    """Convert API record into a DynamoDB item."""

    return {
        "country": record["country"].strip().upper(),
        "continent": record.get("continent", "UNKNOWN"),
        "population": Decimal(str(record.get("population", 0))),
        "total_cases": Decimal(str(record.get("cases", 0))),
        "active_cases": Decimal(str(record.get("active", 0))),
        "recovered": Decimal(str(record.get("recovered", 0))),
        "deaths": Decimal(str(record.get("deaths", 0))),
        "critical": Decimal(str(record.get("critical", 0))),
        "cases_per_million": Decimal(str(record.get("casesPerOneMillion", 0))),
        "risk_level": get_risk_level(record.get("active", 0)),
        "processed_at_utc": processed_at,
    }


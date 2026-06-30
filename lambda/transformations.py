from decimal import Decimal


def decimal(value):

    if value in (None, ""):
        return Decimal("0")

    return Decimal(str(value))


def get_risk_level(active_cases):

    active_cases = decimal(active_cases)

    if active_cases >= Decimal("100000"):
        return "HIGH"

    elif active_cases >= Decimal("10000"):
        return "MEDIUM"

    return "LOW"


def validate_record(record, file_type):

    if file_type == "json":

        if not record.get("country"):
            return False

        try:
            return int(record.get("population", 0)) > 0
        except:
            return False

    elif file_type == "csv":

        if not record.get("country"):
            return False

        return True

    elif file_type == "parquet":

        if not record.get("location_key"):
            return False

        return True

    return False


def build_item(record, processed_at, file_type):

    if file_type == "json":

        return {

            "country": record["country"].strip().upper(),

            "continent": record.get("continent", "UNKNOWN"),

            "population": decimal(record.get("population")),

            "total_cases": decimal(record.get("cases")),

            "active_cases": decimal(record.get("active")),

            "recovered": decimal(record.get("recovered")),

            "deaths": decimal(record.get("deaths")),

            "critical": decimal(record.get("critical")),

            "cases_per_million":
                decimal(record.get("casesPerOneMillion")),

            "risk_level":
                get_risk_level(record.get("active")),

            "processed_at_utc":
                processed_at,
        }

    elif file_type == "csv":

        vaccine_column = next(
            col for col in record.keys()
            if col.startswith("timeline.")
        )

        return {

            "country": record["country"].strip().upper(),

            "vaccinations":
                decimal(record[vaccine_column]),

            "processed_at_utc":
                processed_at,
        }

    elif file_type == "parquet":

        return {

            "location_key":
                record["location_key"],

            "date":
                record["date"],

            "new_hospitalized_patients":
                decimal(record.get("new_hospitalized_patients")),

            "cumulative_hospitalized_patients":
                decimal(record.get("cumulative_hospitalized_patients")),

            "current_hospitalized_patients":
                decimal(record.get("current_hospitalized_patients")),

            "new_intensive_care_patients":
                decimal(record.get("new_intensive_care_patients")),

            "cumulative_intensive_care_patients":
                decimal(record.get("cumulative_intensive_care_patients")),

            "current_intensive_care_patients":
                decimal(record.get("current_intensive_care_patients")),

            "new_ventilator_patients":
                decimal(record.get("new_ventilator_patients")),

            "cumulative_ventilator_patients":
                decimal(record.get("cumulative_ventilator_patients")),

            "current_ventilator_patients":
                decimal(record.get("current_ventilator_patients")),

            "processed_at_utc":
                processed_at,
        }

    raise ValueError(f"Unsupported file type: {file_type}")
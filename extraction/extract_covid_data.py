"""Fetch country-level COVID-19 data and save the raw response locally."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOGGER = logging.getLogger(__name__)
DEFAULT_API_URL = "https://disease.sh/v3/covid-19/countries"
DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "raw" / "covid_data.json"
)


def create_http_session() -> requests.Session:
    """Create a requests session with retry behavior for transient failures."""
    retry_policy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_policy))
    return session


def fetch_covid_data(
    api_url: str = DEFAULT_API_URL,
    timeout_seconds: int = 30,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Fetch and validate the country collection returned by the source API."""
    http_session = session or create_http_session()
    try:
        LOGGER.info("Fetching COVID-19 data from %s", api_url)
        response = http_session.get(api_url, timeout=timeout_seconds)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        LOGGER.exception("The COVID-19 API request failed")
        raise
    except ValueError:
        LOGGER.exception("The COVID-19 API returned invalid JSON")
        raise

    if not isinstance(payload, list):
        raise ValueError("Expected the COVID-19 API response to be a JSON array")

    LOGGER.info("Fetched %d country records", len(payload))
    return payload


def save_json(
    records: list[dict[str, Any]],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Write raw records as formatted UTF-8 JSON and return the saved path."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        LOGGER.exception("Could not write raw data to %s", output_path)
        raise

    LOGGER.info("Saved raw data to %s", output_path)
    return output_path


def main() -> None:
    """Run the extraction process with optional environment overrides."""
    api_url = os.getenv("COVID_API_URL", DEFAULT_API_URL)
    output_path = Path(os.getenv("LOCAL_DATA_PATH", str(DEFAULT_OUTPUT_PATH)))
    records = fetch_covid_data(api_url=api_url)
    save_json(records, output_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    main()


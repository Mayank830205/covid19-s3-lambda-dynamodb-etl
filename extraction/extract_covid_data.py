"""Extract COVID-19 data from API and save it locally."""

import json
from pathlib import Path

import requests

API_URL = "https://disease.sh/v3/covid-19/countries"
OUTPUT_FILE = Path("data/raw/covid_data.json")


def fetch_covid_data():
    """Fetch COVID-19 country data."""

    print("========== Data Extraction Started ==========")
    print("Fetching data from API...")

    response = requests.get(API_URL)
    response.raise_for_status()

    data = response.json()

    print(f"Records fetched: {len(data)}")

    return data


def save_json(data):
    """Save JSON data locally."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Data saved to {OUTPUT_FILE}")


def main():
    data = fetch_covid_data()
    save_json(data)

    print("========== Data Extraction Completed ==========")


if __name__ == "__main__":
    main()


import json
from pathlib import Path

import pandas as pd
import requests

COVID_URL = "https://disease.sh/v3/covid-19/countries"
VACCINE_URL = "https://disease.sh/v3/covid-19/vaccine/coverage/countries?lastdays=1"
HOSPITAL_URL = "https://storage.googleapis.com/covid19-open-data/v3/hospitalizations.csv"

RAW_DIR = Path("data/raw")

COVID_FILE = RAW_DIR / "covid_data.json"
VACCINE_FILE = RAW_DIR / "vaccine_data.csv"
HOSPITAL_FILE = RAW_DIR / "hospital_data.parquet"


def fetch_covid_data():
    print("Fetching COVID-19 data...")

    response = requests.get(COVID_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    print(f"COVID records: {len(data)}")

    return data


def fetch_vaccine_data():
    print("Fetching vaccination data...")

    response = requests.get(VACCINE_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    df = pd.json_normalize(data)

    df.to_csv(VACCINE_FILE, index=False)

    print(f"Vaccination records: {len(df)}")
    print(f"Saved -> {VACCINE_FILE}")


def fetch_hospital_data():
    print("Fetching hospital data...")

    df = pd.read_csv(HOSPITAL_URL)

    df.to_parquet(HOSPITAL_FILE, index=False)

    print(f"Hospital records: {len(df)}")
    print(f"Saved -> {HOSPITAL_FILE}")


def save_covid_json(data):
    with open(COVID_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Saved -> {COVID_FILE}")


def main():
    print("=" * 50)
    print("COVID-19 ETL Extraction Started")
    print("=" * 50)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    covid_data = fetch_covid_data()
    save_covid_json(covid_data)

    fetch_vaccine_data()
    fetch_hospital_data()

    print("=" * 50)
    print("Extraction Completed Successfully")
    print("=" * 50)


if __name__ == "__main__":
    main()
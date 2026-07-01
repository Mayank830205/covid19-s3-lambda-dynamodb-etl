# Multi-Format COVID-19 Serverless ETL Pipeline on AWS

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=awslambda)
![Amazon S3](https://img.shields.io/badge/Amazon-S3-569A31?logo=amazons3)
![DynamoDB](https://img.shields.io/badge/Amazon-DynamoDB-4053D6?logo=amazondynamodb)
![License](https://img.shields.io/badge/License-MIT-green)

## Project Overview

This project demonstrates a beginner-friendly serverless ETL pipeline on AWS.
It extracts COVID-19 datasets in JSON, CSV, and Parquet formats, uploads the raw
files to Amazon S3, processes each format with a dedicated AWS Lambda function,
and stores transformed records in Amazon DynamoDB.

## Architecture

![Architecture](architecture.png)

```text
COVID API    -> JSON    -> raw/json/    -> covid-lambda    -> covid-table
Vaccine API  -> CSV     -> raw/csv/     -> vaccine-lambda  -> vaccine-table
Hospital API -> Parquet -> raw/parquet/ -> hospital-lambda -> hospital-table

S3 -> Lambda -> DynamoDB
```

## AWS Services Used

- Amazon S3
- AWS Lambda
- Amazon DynamoDB
- AWS IAM
- Amazon CloudWatch
- AWS CodeBuild

## Folder Structure

```text
covid19-s3-lambda-dynamodb-etl/
|-- extraction/
|   |-- extract_covid_data.py
|   `-- upload_to_s3.py
|-- lambda/
|   |-- covid_lambda.py
|   |-- vaccine_lambda.py
|   |-- hospital_lambda.py
|   |-- utils.py
|   `-- requirements.txt
|-- screenshots/
|-- .github/
|-- buildspec.yml
|-- architecture.png
`-- README.md
```

## Pipeline Workflow

1. `extract_covid_data.py` downloads the COVID, vaccine, and hospital datasets.
2. The files are saved locally as JSON, CSV, and Parquet.
3. `upload_to_s3.py` uploads the files to the S3 raw prefixes.
4. S3 object-created events trigger the correct Lambda function.
5. Each Lambda validates, transforms, and writes records to DynamoDB.

## Features

- Multi-format ingestion using JSON, CSV, and Parquet
- Separate Lambda function for each dataset format
- Simple validation and transformation inside each Lambda
- Batch writes to DynamoDB
- UTC processing timestamp for audit tracking
- Simple CodeBuild deployment using `aws lambda update-function-code`

## How to Run

### Prerequisites

- Python 3.12
- AWS CLI configured with access to S3, Lambda, DynamoDB, and CloudWatch
- An S3 bucket for raw dataset uploads
- DynamoDB tables named `covid-table`, `vaccine-table`, and `hospital-table`
- Lambda functions named `covid-lambda`, `vaccine-lambda`, and `hospital-lambda`

### Installation

```bash
git clone https://github.com/Mayank830205/covid19-s3-lambda-dynamodb-etl.git
cd covid19-s3-lambda-dynamodb-etl
python -m venv .venv
source .venv/bin/activate
pip install -r lambda/requirements.txt
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r lambda\requirements.txt
```

### Execution

```bash
python extraction/extract_covid_data.py
```

Set the target bucket and upload the raw files:

```bash
export BUCKET_NAME=your-s3-bucket-name
python extraction/upload_to_s3.py
```

On Windows PowerShell:

```powershell
$env:BUCKET_NAME = "your-s3-bucket-name"
python extraction\upload_to_s3.py
```

## AWS Configuration

### S3 Triggers

Configure object-created triggers on the raw S3 prefixes:

| Prefix | Lambda |
| --- | --- |
| `raw/json/*.json` | `covid-lambda` |
| `raw/csv/*.csv` | `vaccine-lambda` |
| `raw/parquet/*.parquet` | `hospital-lambda` |

### DynamoDB Tables

| Table | Partition Key | Sort Key |
| --- | --- | --- |
| `covid-table` | `country` | - |
| `vaccine-table` | `country` | - |
| `hospital-table` | `location_key` | `date` |

## Screenshots

Add screenshots for:

- S3 raw folders
- Lambda functions
- DynamoDB tables
- CloudWatch logs
- CodeBuild deployment

## Future Improvements

- Add EventBridge scheduling for automated extraction
- Add Athena queries for S3 analytics
- Add dashboard reporting with QuickSight or Power BI
- Add infrastructure as code with AWS CDK or Terraform

## Technologies

- Python 3.12
- AWS Lambda
- Amazon S3
- Amazon DynamoDB
- Boto3
- Pandas
- PyArrow
- AWS CLI

## Author

**Mayank Shringi**

MCA | Data Engineering Enthusiast

GitHub: [Mayank830205](https://github.com/Mayank830205)

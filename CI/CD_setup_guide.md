## ⚙️ CI/CD Setup Guide

Follow these steps to configure the CI/CD pipeline for automatic AWS Lambda deployment.

### 1. Clone the Repository

```bash
git clone https://github.com/Mayank830205/covid19-s3-lambda-dynamodb-etl.git
cd covid19-s3-lambda-dynamodb-etl
```

---

### 2. Create an AWS Lambda Function

* Open **AWS Console**
* Go to **Lambda**
* Click **Create Function**
* Select **Author from scratch**
* Runtime: **Python 3.12**
* Create the function

---

### 3. Create an IAM Role

Grant the Lambda function permissions to:

* Amazon S3
* DynamoDB
* CloudWatch Logs

Example permissions:

* `AmazonS3ReadOnlyAccess`
* `AmazonDynamoDBFullAccess`
* `AWSLambdaBasicExecutionRole`

---

### 4. Configure Lambda Environment Variables

| Variable    | Example             |
| ----------- | ------------------- |
| BUCKET_NAME | covid19-data-bucket |
| OBJECT_KEY  | raw/covid_data.json |
| TABLE_NAME  | covid_country_stats |

---

### 5. Create a CodeBuild Project

Configuration:

| Setting          | Value                            |
| ---------------- | -------------------------------- |
| Source           | No Source (used by CodePipeline) |
| Environment      | Managed Image                    |
| Operating System | Ubuntu                           |
| Runtime          | Standard                         |
| Image            | aws/codebuild/standard:7.0       |
| Runtime Version  | Python 3.12                      |
| Service Role     | New or Existing CodeBuild Role   |
| Buildspec        | `buildspec.yml`                  |

---

### 6. Add `buildspec.yml`

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.12
    commands:
      - mkdir package
      - pip install -r lambda/requirements.txt -t package

  build:
    commands:
      - cp lambda/*.py package/
      - cd package
      - zip -r ../function.zip .

artifacts:
  files:
    - function.zip
```

---

### 7. Create a CodePipeline

Configure the pipeline with the following stages:

#### Source Stage

* Provider: **GitHub (via GitHub App)**
* Repository: `Mayank830205/covid19-s3-lambda-dynamodb-etl`
* Branch: `main`

#### Build Stage

* Provider: **AWS CodeBuild**
* Project: `covid-etl-build`

#### Deploy Stage

* Provider: **AWS Lambda**
* Function: `covid19-s3-lambda-dynamodb-etl`

---

### 8. Configure GitHub Actions

Workflow location:

```text
.github/workflows/ci.yml
```

This workflow:

* Installs dependencies
* Runs unit tests
* Validates the project before deployment

---

### 9. Push Code

```bash
git add .
git commit -m "Update Lambda"
git push origin main
```

---

### 10. Automatic Deployment

Every push to the **main** branch automatically triggers:

```text
GitHub
    │
    ▼
GitHub Actions (CI)
    │
    ▼
AWS CodePipeline
    │
    ▼
AWS CodeBuild
    │
    ▼
AWS Lambda Deployment
```

---

## ✅ Verify Deployment

1. Modify `lambda/lambda_function.py`

```python
print("Deployment Successful!")
```

2. Push the changes

```bash
git add .
git commit -m "Verify deployment"
git push origin main
```

3. Confirm:

* ✅ GitHub Actions completed successfully
* ✅ CodePipeline completed successfully
* ✅ CodeBuild completed successfully
* ✅ Lambda **Last Modified** timestamp updated
* ✅ CloudWatch Logs show the new message

\# Deployment Guide



This document describes the high-level deployment process for the Spotify AWS Data Engineering Pipeline.



\## Prerequisites



\- AWS account

\- Spotify Developer application

\- Python 3.12

\- uv

\- AWS CLI

\- Git



\## 1. Configure Spotify API



Create a Spotify Developer application and obtain:



```text

SPOTIFY\_CLIENT\_ID

SPOTIFY\_CLIENT\_SECRET

```



Never commit these credentials to GitHub.



\## 2. Create Amazon S3 Storage



Create an S3 bucket and organize the data lake into:



```text

raw/spotify/

silver/spotify/

gold/artists/

athena-results/

```



Keep S3 Block Public Access enabled.



\## 3. Deploy AWS Lambda



Deploy:



```text

lambda/spotify\_data\_extraction.py

```



Configure the Lambda environment variables:



```text

SPOTIFY\_CLIENT\_ID

SPOTIFY\_CLIENT\_SECRET

S3\_BUCKET

S3\_RAW\_PREFIX

```



The Lambda function extracts Spotify data and writes JSON files to the Raw S3 layer.



\## 4. Configure AWS Glue



Deploy the PySpark ETL scripts:



```text

glue/raw\_to\_silver.py

glue/silver\_to\_gold.py

```



The processing flow is:



```text

Raw JSON

&#x20;  ↓

AWS Glue / PySpark

&#x20;  ↓

Silver Parquet

&#x20;  ↓

AWS Glue / PySpark

&#x20;  ↓

Gold Parquet

```



\## 5. Configure AWS Glue Data Catalog



Create catalog databases for the processed datasets:



```text

spotify\_silver\_db

spotify\_gold\_db

```



Use AWS Glue Crawlers to discover the Parquet schemas.



\## 6. Query with Amazon Athena



Configure an Athena query-result location in S3.



Analytics and validation queries are available in:



```text

sql/athena\_queries.sql

```



\## 7. Configure Amazon Redshift Serverless



Create a Redshift Serverless namespace and workgroup.



Grant Redshift permission to read the Gold S3 prefix.



Create and load the warehouse table using:



```text

sql/redshift\_queries.sql

```



\## 8. Configure Step Functions



Use:



```text

step-functions/spotify\_pipeline.json

```



to represent the ETL orchestration workflow.



The workflow coordinates the Glue transformation jobs.



\## 9. Configure EventBridge



Create a scheduled EventBridge rule/schedule for automated pipeline execution.



The schedule can invoke the required orchestration/extraction workflow according to the deployment design.



\## 10. Monitoring



Use Amazon CloudWatch to monitor:



\- Lambda execution

\- Glue ETL jobs

\- Glue crawlers

\- errors and operational logs



\## Security



Do not store the following in GitHub:



\- AWS access keys

\- AWS secret access keys

\- Spotify Client Secret

\- passwords

\- `.env` files



For production deployments, AWS Secrets Manager or another managed secret-storage mechanism should be used.



\## Local Setup



Install dependencies:



```bash

uv sync

```



Verify Python:



```bash

uv run python --version

```



Copy `.env.example` to `.env` only for local development and populate it with your own credentials.



The `.env` file must remain excluded from Git.


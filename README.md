\# Spotify AWS Data Engineering Pipeline



An end-to-end serverless data engineering project that extracts data from the Spotify Web API, processes it through a Medallion-style architecture on AWS, and delivers analytics-ready data through Amazon Athena and Amazon Redshift Serverless.



\## Project Overview



This project demonstrates how a production-style cloud data pipeline can be designed using managed and serverless AWS services.



The pipeline extracts Spotify artist data using Python, stores immutable API responses in Amazon S3, transforms the data through Raw, Silver, and Gold layers using AWS Glue and PySpark, catalogs the datasets with AWS Glue Data Catalog, performs analytics with Amazon Athena, and loads curated data into Amazon Redshift Serverless.



Pipeline orchestration is handled with AWS Step Functions and Amazon EventBridge, while Amazon CloudWatch provides centralized logging and monitoring.



\## Architecture



```text

&#x20;                      Spotify Web API

&#x20;                             |

&#x20;                             v

&#x20;                        AWS Lambda

&#x20;                             |

&#x20;                             v

&#x20;                   Amazon S3 - Raw JSON

&#x20;                             |

&#x20;                             v

&#x20;                    AWS Glue + PySpark

&#x20;                      Raw -> Silver

&#x20;                             |

&#x20;                             v

&#x20;                 Amazon S3 - Silver Parquet

&#x20;                             |

&#x20;                             v

&#x20;                    AWS Glue + PySpark

&#x20;                      Silver -> Gold

&#x20;                             |

&#x20;                             v

&#x20;                  Amazon S3 - Gold Parquet

&#x20;                        /           \\

&#x20;                       /             \\

&#x20;                      v               v

&#x20;             Amazon Athena     Amazon Redshift

&#x20;                 SQL              Serverless

```



\### Supporting AWS Services



```text

EventBridge -> Step Functions -> Glue ETL Jobs



AWS Glue Data Catalog -> Dataset Metadata



Amazon CloudWatch -> Logs \& Monitoring



AWS IAM -> Access Control

```



\## Data Architecture



The project follows a three-layer data architecture.



\### Raw Layer



Stores the original Spotify Web API responses as JSON.



Data is organized using date-based S3 prefixes:



```text

raw/spotify/

└── year=YYYY/

&#x20;   └── month=MM/

&#x20;       └── day=DD/

&#x20;           └── spotify\_TIMESTAMP.json

```



\### Silver Layer



AWS Glue and PySpark transform raw JSON into cleaned and structured Parquet datasets.



The Silver layer provides:



\- structured schemas

\- cleaned fields

\- normalized timestamps

\- column selection

\- analytics-friendly Parquet storage



\### Gold Layer



The Gold layer contains curated data designed for analytics and warehouse consumption.



PySpark Window functions and `ROW\_NUMBER()` are used to retain the latest record for each artist.



\## Pipeline Components



\### AWS Lambda



Python-based extraction calls the Spotify Web API and writes the API response to the S3 Raw layer.



Secrets are provided through environment configuration and are never committed to the repository.



\### Amazon S3



S3 provides the data lake storage layer for:



```text

Raw -> JSON

Silver -> Parquet

Gold -> Parquet

```



\### AWS Glue + PySpark



Two ETL jobs implement the transformation pipeline:



```text

spotify-raw-to-silver

spotify-silver-to-gold

```



PySpark is used for distributed transformations, validation, deduplication, and Parquet generation.



\### AWS Glue Data Catalog



Metadata for the processed datasets is maintained in:



```text

spotify\_silver\_db

spotify\_gold\_db

```



\### Amazon Athena



Athena provides serverless SQL analytics directly over the curated S3 datasets.



The repository contains queries for:



\- data validation

\- freshness analysis

\- data-quality checks

\- window-function analytics



\### Amazon Redshift Serverless



Curated Gold Parquet data is loaded into Redshift Serverless for warehouse-based analytics.



Warehouse table:



```text

public.spotify\_artists\_gold

```



\### AWS Step Functions



Step Functions orchestrates the ETL workflow and ensures transformation jobs execute in sequence.



```text

Raw -> Silver

&#x20;     |

&#x20;     v

Silver -> Gold

```



\### Amazon EventBridge



EventBridge provides scheduled execution for the cloud pipeline.



\### Amazon CloudWatch



CloudWatch provides centralized logs for:



\- Lambda executions

\- Glue ETL jobs

\- Glue crawlers

\- pipeline troubleshooting



\### AWS IAM



IAM roles and policies enforce service-specific access between Lambda, S3, Glue, Redshift, Step Functions, and CloudWatch.



\## Data Engineering Concepts Demonstrated



\- Serverless data engineering

\- ETL/ELT pipeline design

\- Medallion architecture

\- Data lake design

\- JSON ingestion

\- Parquet optimization

\- PySpark transformations

\- Distributed data processing

\- Data deduplication

\- Spark Window functions

\- Data quality validation

\- Data freshness monitoring

\- Metadata management

\- SQL analytics

\- Cloud data warehousing

\- Workflow orchestration

\- Event-driven scheduling

\- IAM-based security

\- Cloud observability



\## Project Structure



```text

spotify-aws-data-pipeline/

|

├── architecture/

│   └── architecture.md

|

├── docs/

│   └── deployment-guide.md

|

├── glue/

│   ├── raw\_to\_silver.py

│   └── silver\_to\_gold.py

|

├── iam/

│   └── README.md

|

├── lambda/

│   └── spotify\_data\_extraction.py

|

├── sql/

│   ├── athena\_queries.sql

│   └── redshift\_queries.sql

|

├── step-functions/

│   └── spotify\_pipeline.json

|

├── .env.example

├── .gitignore

├── .python-version

├── pyproject.toml

├── uv.lock

└── README.md

```



\## Local Development



This repository uses `uv` for Python environment and dependency management.



Install the project dependencies:



```bash

uv sync

```



Verify Python:



```bash

uv run python --version

```



\## Environment Variables



Create a local `.env` from `.env.example` when testing locally.



Required configuration includes:



```text

SPOTIFY\_CLIENT\_ID

SPOTIFY\_CLIENT\_SECRET

AWS\_REGION

S3\_BUCKET

S3\_RAW\_PREFIX

```



Never commit the real `.env` file or AWS credentials.



\## SQL Analytics



Athena queries are available at:



```text

sql/athena\_queries.sql

```



Redshift warehouse queries are available at:



```text

sql/redshift\_queries.sql

```



\## Monitoring



The pipeline uses Amazon CloudWatch for operational visibility.



CloudWatch log groups capture Lambda extraction activity, Glue ETL execution output, errors, and crawler activity.



\## Future Enhancements



Potential extensions include:



\- Power BI integration with the warehouse layer

\- AWS Secrets Manager for Spotify credentials

\- automated Redshift loading as part of orchestration

\- CloudWatch alarms and notifications

\- CI/CD deployment

\- Infrastructure as Code using Terraform or AWS CDK



\## Security



No API secrets, AWS access keys, passwords, or private credentials are stored in this repository.



Sensitive values should be supplied through secure environment configuration or AWS-managed secret services.



\## Tech Stack



\*\*Programming:\*\* Python, SQL, PySpark



\*\*AWS:\*\* Lambda, S3, Glue, Glue Data Catalog, Athena, Redshift Serverless, Step Functions, EventBridge, CloudWatch, IAM



\*\*Data Formats:\*\* JSON, Parquet



\*\*Development:\*\* uv, Git, GitHub



\## Status



Core data pipeline completed and validated on AWS.



```text

Spotify API

&#x20;  -> S3 Raw

&#x20;  -> Glue/PySpark Silver

&#x20;  -> Glue/PySpark Gold

&#x20;  -> Athena

&#x20;  -> Redshift Serverless

```


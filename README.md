# Spotify AWS Data Engineering Pipeline

An end-to-end, automated, serverless data engineering pipeline that extracts data from the Spotify Web API, stores raw data in Amazon S3, transforms it through Bronze/Raw, Silver, and Gold layers using AWS Glue and PySpark, orchestrates ETL workflows with AWS Step Functions, and enables analytics through Amazon Athena and Amazon Redshift Serverless.

The pipeline is automatically triggered using Amazon EventBridge Scheduler and monitored through Amazon CloudWatch.

---

## Project Overview

Modern data platforms require more than simply extracting data from an API. They need automated ingestion, scalable transformation, orchestration, monitoring, data quality controls, and analytics-ready storage.

This project demonstrates a production-style AWS data engineering workflow built using managed and serverless AWS services.

The pipeline:

- Extracts artist data from the Spotify Web API
- Runs automatically on a schedule
- Stores immutable raw JSON data in Amazon S3
- Organizes raw data using date-based S3 partitions
- Transforms data using AWS Glue and PySpark
- Implements Raw → Silver → Gold data layers
- Uses Spark window functions for distributed deduplication
- Registers datasets in the AWS Glue Data Catalog
- Enables SQL analytics using Amazon Athena
- Loads curated Gold data into Amazon Redshift Serverless
- Orchestrates ETL jobs using AWS Step Functions
- Monitors executions using Amazon CloudWatch
- Uses AWS IAM for service-level access control

---

## Architecture

```text
                   SPOTIFY AWS DATA ENGINEERING PIPELINE

                         Amazon EventBridge
                         Daily Scheduler
                               |
                               v
                          AWS Lambda
                               |
                               v
                        Spotify Web API
                               |
                               v
                     Amazon S3 - Raw JSON
                               |
                               v
                      AWS Step Functions
                               |
                               v
                     AWS Glue + PySpark
                       Raw -> Silver
                               |
                               v
                  Amazon S3 - Silver Parquet
                               |
                               v
                     AWS Glue + PySpark
                       Silver -> Gold
                               |
                               v
                   Amazon S3 - Gold Parquet
                         /             \
                        v               v
                 Amazon Athena     Amazon Redshift
                  SQL Analytics       Serverless


              Monitoring : Amazon CloudWatch
              Security   : AWS IAM
              Metadata   : AWS Glue Data Catalog
```

---

## Automated Pipeline Execution

The complete data pipeline is automated using Amazon EventBridge Scheduler.

```text
EventBridge Scheduler
        |
        v
AWS Lambda
        |
        v
Spotify Web API
        |
        v
Amazon S3 Raw
        |
        v
AWS Step Functions
        |
        v
Glue Raw -> Silver
        |
        v
S3 Silver
        |
        v
Glue Silver -> Gold
        |
        v
S3 Gold
        |
        +------------------+
        |                  |
        v                  v
     Athena             Redshift
```

Amazon EventBridge invokes the Spotify extraction Lambda on a daily schedule.

The Lambda authenticates with the Spotify Web API, extracts the required artist data, writes the API response into the Raw S3 layer, and starts the AWS Step Functions workflow.

Step Functions then orchestrates the transformation jobs sequentially.

This allows the pipeline to operate without manual execution.

<img width="1915" height="812" alt="image" src="https://github.com/user-attachments/assets/40b4583b-5701-44eb-8932-8fc7969bad5a" />


---

## Data Lake Architecture

The project follows a three-layer data architecture.

### Raw Layer

Raw responses from the Spotify Web API are stored as JSON without modifying the source structure.

Example:

```text
s3://spotify-data-pipeline-vishal/
└── raw/
    └── spotify/
        └── year=YYYY/
            └── month=MM/
                └── day=DD/
                    └── spotify_TIMESTAMP.json
```

Date-based S3 prefixes make the ingestion layer easier to organize and maintain.

---

### Silver Layer

AWS Glue and PySpark process the raw JSON data and convert it into structured Parquet datasets.

The Silver layer performs operations such as:

- Schema normalization
- Nested JSON extraction
- Column selection
- Type conversion
- Null handling
- Data cleaning
- Deduplication
- Parquet conversion

Example:

```text
s3://spotify-data-pipeline-vishal/
└── silver/
    └── spotify/
```

Parquet provides a columnar format suitable for analytical workloads.

---

### Gold Layer

The Gold layer contains curated, analytics-ready datasets.

Example:

```text
s3://spotify-data-pipeline-vishal/
└── gold/
    └── artists/
```

The Gold artist dataset contains fields such as:

```text
artist_id
artist_name
artist_type
spotify_url
image_url
extracted_at
extraction_date
data_layer
```

This dataset can be consumed directly by analytical services such as Athena and Redshift.

---

## Data Transformation with PySpark

AWS Glue provides managed Apache Spark compute for the transformation layer.

The Gold transformation performs validation and deduplication before publishing the curated dataset.

A Spark Window is used to retain the latest record for each artist.

Conceptually:

```python
Window.partitionBy("artist_id").orderBy(
    col("extracted_at").desc()
)
```

A row number is assigned within each artist partition, and only the latest record is retained.

This provides distributed deduplication suitable for Spark workloads.

---

## Data Structures and Algorithms

Data structures are used at different stages of the pipeline depending on the processing environment.

During Python-based extraction, a Hash Set can be used for ID-based deduplication.

```python
seen_artist_ids = set()
```

Set membership provides average:

```text
O(1)
```

lookup complexity.

For distributed processing, Spark Window operations are used instead because the dataset can be processed across multiple workers.

This demonstrates the difference between local in-memory deduplication and distributed data processing.

---

## AWS Step Functions Orchestration

AWS Step Functions controls the ETL workflow.

The transformation sequence is:

```text
Start
  |
  v
RawToSilver
  |
  v
SilverToGold
  |
  v
End
```

The Raw-to-Silver Glue job must complete successfully before the Silver-to-Gold job begins.

This provides deterministic workflow execution and prevents downstream transformations from running before their dependencies are ready.

---

## Amazon EventBridge Scheduler

Amazon EventBridge Scheduler provides time-based pipeline automation.

The active production schedule invokes:

```text
spotify-data-extraction
```

The Lambda subsequently starts the Step Functions workflow after successfully writing the raw Spotify response to S3.

An older duplicate extraction schedule was disabled to prevent the pipeline from executing twice.

---

## AWS Glue Data Catalog

AWS Glue Data Catalog provides centralized metadata management for the datasets stored in Amazon S3.

Separate databases are used for analytical layers.

```text
spotify_silver_db
spotify_gold_db
```

The Silver catalog contains structured transformed datasets.

The Gold catalog contains curated analytics-ready datasets.

AWS Glue Crawlers detect Parquet schemas and register tables in the Data Catalog.

---

## Amazon Athena

Amazon Athena provides serverless SQL analytics directly on top of S3.

Example:

```sql
SELECT *
FROM spotify_gold_db.artists
LIMIT 10;
```

More advanced analytical queries can use:

- Common Table Expressions
- Window functions
- Aggregations
- Data quality checks
- Freshness calculations
- Ranking
- Distinct counts

Because Athena queries data directly from S3, no dedicated database server is required for exploratory analytics.

---

## Amazon Redshift Serverless

Amazon Redshift Serverless is used as the analytical warehouse layer.

A curated table was created for the Gold artist dataset:

```sql
CREATE TABLE public.spotify_artists_gold (
    artist_id       VARCHAR(255),
    artist_name     VARCHAR(500),
    artist_type     VARCHAR(100),
    spotify_url     VARCHAR(1000),
    image_url       VARCHAR(2000),
    extracted_at    TIMESTAMP,
    extraction_date DATE,
    data_layer      VARCHAR(50)
);
```

Gold Parquet data can be loaded from Amazon S3 using:

```sql
COPY public.spotify_artists_gold
FROM 's3://spotify-data-pipeline-vishal/gold/artists/'
IAM_ROLE default
FORMAT AS PARQUET;
```

The loaded dataset can then be queried using standard SQL.

Example:

```sql
SELECT
    COUNT(*) AS total_rows,
    MAX(extracted_at) AS latest_extraction
FROM public.spotify_artists_gold;
```

---

## Monitoring with Amazon CloudWatch

<img width="1917" height="762" alt="image" src="https://github.com/user-attachments/assets/21d649d0-962c-4194-9225-1ca58ad4ddff" />
<img width="1917" height="827" alt="image" src="https://github.com/user-attachments/assets/e19ac196-55df-4b1e-88c5-92762d73e0d5" />



Amazon CloudWatch provides centralized logging and monitoring.

CloudWatch logs are available for:

```text
AWS Lambda
AWS Glue jobs
AWS Glue Crawlers
```

The Lambda execution logs provide visibility into stages such as:

```text
Starting Spotify data extraction
        ↓
Spotify authentication successful
        ↓
Artist extracted
        ↓
Spotify data uploaded to Amazon S3
        ↓
Step Functions pipeline started
```

This provides operational evidence that the automated pipeline is executing correctly.

---

## Security

AWS IAM controls communication between services.

Dedicated roles and policies are used for:

```text
Lambda → S3
Lambda → Step Functions
Glue → S3
Step Functions → Glue
Redshift → S3
EventBridge → Lambda
```

Credentials and secrets are not committed to the Git repository.

Local environment variables should be stored in:

```text
.env
```

The `.env` file is excluded using `.gitignore`.

Only a template is committed:

```text
.env.example
```

Example:

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
AWS_REGION=ap-southeast-2
S3_BUCKET=your_bucket_name
```

Never commit real credentials or AWS access keys.

---

## Project Structure

```text
spotify-aws-data-pipeline/
│
├── architecture/
│   └── architecture.md
│
├── docs/
│   └── images/
│
├── glue/
│   ├── raw_to_silver.py
│   └── silver_to_gold.py
│
├── iam/
│   └── policies/
│
├── lambda/
│   └── spotify_data_extraction.py
│
├── sql/
│   ├── athena_queries.sql
│   └── redshift_queries.sql
│
├── step-functions/
│   └── spotify_pipeline.json
│
├── .env.example
├── .gitignore
├── .python-version
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Technology Stack

| Category | Technology |
|---|---|
| Programming | Python |
| API | Spotify Web API |
| Cloud Platform | AWS |
| Serverless Compute | AWS Lambda |
| Object Storage | Amazon S3 |
| Data Processing | AWS Glue |
| Distributed Processing | Apache Spark / PySpark |
| Workflow Orchestration | AWS Step Functions |
| Scheduling | Amazon EventBridge Scheduler |
| Metadata | AWS Glue Data Catalog |
| SQL Analytics | Amazon Athena |
| Data Warehouse | Amazon Redshift Serverless |
| Monitoring | Amazon CloudWatch |
| Security | AWS IAM |
| Data Format | JSON / Apache Parquet |
| Dependency Management | uv |
| Version Control | Git / GitHub |

---

## Pipeline Workflow

```text
1. EventBridge triggers the pipeline
                ↓
2. Lambda authenticates with Spotify
                ↓
3. Spotify Web API data is extracted
                ↓
4. Raw JSON is written to Amazon S3
                ↓
5. Lambda starts Step Functions
                ↓
6. Step Functions starts Raw → Silver Glue job
                ↓
7. PySpark cleans and structures the data
                ↓
8. Silver Parquet is written to S3
                ↓
9. Step Functions starts Silver → Gold Glue job
                ↓
10. Gold dataset is created
                ↓
11. Glue Data Catalog exposes the datasets
                ↓
12. Athena provides serverless SQL analytics
                ↓
13. Gold data can be loaded into Redshift Serverless
                ↓
14. CloudWatch provides execution monitoring
```

---

## Key Engineering Concepts Demonstrated

This project demonstrates practical implementation of:

- ETL / ELT pipeline development
- REST API data ingestion
- Serverless data engineering
- Data lake architecture
- Raw / Silver / Gold data modeling
- Apache Spark transformations
- Distributed deduplication
- Columnar Parquet storage
- Workflow orchestration
- Scheduled data pipelines
- Data cataloging
- Serverless SQL analytics
- Cloud data warehousing
- IAM access control
- Pipeline monitoring
- Environment variable management
- Git-based source control

---

## What I Learned

Building this project provided hands-on experience designing a cloud-native data pipeline rather than working with isolated AWS services.

Key learning areas included:

- Designing an end-to-end AWS data architecture
- Integrating external APIs with AWS Lambda
- Organizing S3 as a multi-layer data lake
- Processing semi-structured JSON with PySpark
- Building managed Spark ETL jobs with AWS Glue
- Using Spark Window functions for deduplication
- Managing metadata using Glue Crawlers and the Data Catalog
- Querying S3 datasets using Athena
- Loading Parquet datasets into Redshift Serverless
- Orchestrating dependent ETL jobs using Step Functions
- Automating executions with EventBridge Scheduler
- Troubleshooting IAM permissions between AWS services
- Monitoring serverless workloads using CloudWatch
- Managing secrets safely outside Git

---

## Future Improvements

Potential extensions include:

- AWS Secrets Manager for Spotify credentials
- Least-privilege IAM policies
- Automated Redshift loading as part of orchestration
- Step Functions retry and failure-handling logic
- CloudWatch alarms and notifications
- Dead-letter queues
- Data quality validation framework
- Incremental processing
- CI/CD deployment
- Infrastructure as Code using Terraform or AWS CDK
- Power BI integration with the analytical layer
- Additional Spotify entities such as albums, tracks, and playlists

---

## Project Status

**Completed**

The core AWS data engineering pipeline has been implemented and validated end-to-end.

```text
Spotify API       ✓
AWS Lambda        ✓
Amazon S3         ✓
AWS Glue          ✓
PySpark           ✓
Glue Data Catalog ✓
AWS Step Functions✓
EventBridge       ✓
Amazon Athena     ✓
Redshift Serverless ✓
Amazon CloudWatch ✓
AWS IAM           ✓
GitHub            ✓
```

---

## Author

**Vishal Muralikumar**

Data Engineering | Cloud Data Platforms | AWS | Python | PySpark

---

## License

This project is licensed under the MIT License.

\# Spotify AWS Data Engineering Pipeline — Architecture



\## Architecture Overview



The project implements a serverless AWS data engineering pipeline that extracts Spotify artist data, stores raw data in Amazon S3, transforms it through Silver and Gold layers using AWS Glue and PySpark, and exposes curated data for analytics through Amazon Athena and Amazon Redshift Serverless.



\## Data Flow



```text

&#x20;                   Spotify Web API

&#x20;                          |

&#x20;                          v

&#x20;                    AWS Lambda

&#x20;                   Data Extraction

&#x20;                          |

&#x20;                          v

&#x20;                Amazon S3 - RAW Layer

&#x20;                      JSON Data

&#x20;                          |

&#x20;                          v

&#x20;                 AWS Glue + PySpark

&#x20;                   Raw -> Silver

&#x20;                          |

&#x20;                          v

&#x20;               Amazon S3 - SILVER Layer

&#x20;                    Parquet Data

&#x20;                          |

&#x20;                          v

&#x20;                 AWS Glue + PySpark

&#x20;                  Silver -> Gold

&#x20;                          |

&#x20;                          v

&#x20;                Amazon S3 - GOLD Layer

&#x20;                   Curated Parquet

&#x20;                     /          \\

&#x20;                    /            \\

&#x20;                   v              v

&#x20;         AWS Glue Data       Amazon Redshift

&#x20;            Catalog             Serverless

&#x20;               |

&#x20;               v

&#x20;         Amazon Athena

&#x20;         SQL Analytics


Orchestration



Amazon EventBridge

&#x20;       |

&#x20;       v

AWS Step Functions

&#x20;       |

&#x20;       +--> AWS Glue Raw -> Silver

&#x20;       |

&#x20;       +--> AWS Glue Silver -> Gold


Monitoring



CloudWatch provides centralized logging and monitoring for the cloud pipeline.



Monitored components include:



AWS Lambda extraction logs

AWS Glue ETL job logs

AWS Glue crawler logs

Pipeline execution troubleshooting

Storage Architecture

Raw Layer

s3://spotify-data-pipeline-vishal/raw/spotify/



Raw Spotify API responses are stored as JSON and organized using date-based S3 prefixes.



Example:



year=YYYY/month=MM/day=DD/spotify\_TIMESTAMP.json

Silver Layer



The Silver layer contains cleaned and structured Spotify data stored in Parquet format.



Gold Layer



The Gold layer contains curated analytics-ready datasets stored in Parquet format.



s3://spotify-data-pipeline-vishal/gold/artists/

Data Catalog



AWS Glue Data Catalog manages metadata for the Silver and Gold datasets.



Databases:



spotify\_silver\_db

spotify\_gold\_db



The catalog enables Athena to query S3 datasets using SQL.



Data Warehouse



Amazon Redshift Serverless provides the warehouse layer.



Gold Parquet files are loaded from Amazon S3 into:



public.spotify\_artists\_gold



This provides a warehouse-ready analytics layer for downstream BI and reporting.



Transformation Strategy



PySpark transformations include:



schema normalization

null filtering

column selection

timestamp processing

Parquet conversion

deduplication

data quality preparation



The Gold transformation uses Spark Window functions and ROW\_NUMBER() to retain the latest artist record.



Security



AWS IAM is used to implement service-specific permissions.



Examples include:



Lambda write access to the S3 Raw layer

Glue access to Raw, Silver and Gold prefixes

Redshift read access to Gold Parquet data

CloudWatch logging permissions



Secrets and credentials are not stored in the GitHub repository.



Technology Stack

Python 3.12

uv

Spotify Web API

AWS Lambda

Amazon S3

AWS Glue

PySpark

AWS Glue Data Catalog

Amazon Athena

Amazon Redshift Serverless

AWS Step Functions

Amazon EventBridge

Amazon CloudWatch

AWS IAM

SQL


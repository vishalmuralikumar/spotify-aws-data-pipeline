import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window


# --------------------------------------------------
# Initialize AWS Glue / Spark
# --------------------------------------------------
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)


# --------------------------------------------------
# 1. READ SILVER DATA
# Using the Glue Data Catalog table created by crawler
# --------------------------------------------------
artists_df = (
    spark.table("spotify_silver_db.artists")
)


# --------------------------------------------------
# 2. DATA QUALITY
# Remove invalid records
# --------------------------------------------------
artists_clean = (
    artists_df
    .filter(F.col("artist_id").isNotNull())
    .filter(F.col("artist_name").isNotNull())
)


# --------------------------------------------------
# 3. DEDUPLICATION
# Keep latest record for each artist
# --------------------------------------------------
window_spec = (
    Window
    .partitionBy("artist_id")
    .orderBy(F.col("extracted_at").desc())
)

artists_latest = (
    artists_clean
    .withColumn(
        "row_number",
        F.row_number().over(window_spec)
    )
    .filter(F.col("row_number") == 1)
    .drop("row_number")
)


# --------------------------------------------------
# 4. GOLD TRANSFORMATION
# Create business-ready columns
# --------------------------------------------------
gold_df = (
    artists_latest
    .select(
        "artist_id",
        "artist_name",
        "artist_type",
        "spotify_url",
        "image_url",
        "extracted_at"
    )
    .withColumn(
        "extraction_date",
        F.to_date("extracted_at")
    )
    .withColumn(
        "data_layer",
        F.lit("gold")
    )
)


# --------------------------------------------------
# 5. WRITE GOLD DATA TO S3
# --------------------------------------------------
GOLD_PATH = (
    "s3://spotify-data-pipeline-vishal/"
    "gold/artists/"
)

(
    gold_df
    .write
    .mode("overwrite")
    .format("parquet")
    .save(GOLD_PATH)
)


print("Silver to Gold transformation completed successfully.")
print(f"Gold data written to: {GOLD_PATH}")


# --------------------------------------------------
# Finish Glue Job
# --------------------------------------------------
job.commit()
-- ============================================================
-- Spotify AWS Data Pipeline
-- Amazon Redshift Serverless
-- Gold Layer Warehouse Queries
-- ============================================================


-- 1. Create Gold Artists Table

CREATE TABLE IF NOT EXISTS public.spotify_artists_gold (
    artist_id       VARCHAR(255),
    artist_name     VARCHAR(500),
    artist_type     VARCHAR(100),
    spotify_url     VARCHAR(1000),
    image_url       VARCHAR(2000),
    extracted_at    TIMESTAMP,
    extraction_date DATE,
    data_layer      VARCHAR(50)
);


-- 2. Load Gold Parquet Data from Amazon S3
--
-- COPY appends data to the table.
-- For a full refresh, run the TRUNCATE statement first.

TRUNCATE TABLE public.spotify_artists_gold;

COPY public.spotify_artists_gold
FROM 's3://spotify-data-pipeline-vishal/gold/artists/'
IAM_ROLE default
FORMAT AS PARQUET;


-- 3. Validate Row Count

SELECT
    COUNT(*) AS total_rows
FROM public.spotify_artists_gold;


-- 4. Validate Data Freshness

SELECT
    COUNT(*) AS total_rows,
    MAX(extracted_at) AS latest_extraction
FROM public.spotify_artists_gold;


-- 5. Preview Warehouse Data

SELECT *
FROM public.spotify_artists_gold
ORDER BY extracted_at DESC
LIMIT 20;


-- 6. Data Quality Check

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT artist_id) AS unique_artists,
    SUM(CASE WHEN artist_id IS NULL THEN 1 ELSE 0 END)
        AS missing_artist_ids,
    SUM(CASE WHEN artist_name IS NULL THEN 1 ELSE 0 END)
        AS missing_artist_names
FROM public.spotify_artists_gold;
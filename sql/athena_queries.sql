-- ============================================================
-- Spotify AWS Data Pipeline
-- Amazon Athena Analytics Queries
-- Database: spotify_gold_db
-- ============================================================


-- 1. Preview Gold Layer
SELECT *
FROM spotify_gold_db.artists
LIMIT 10;


-- 2. Gold Layer Data Quality & Freshness
SELECT
    extraction_date,
    artist_type,
    COUNT(DISTINCT artist_id) AS unique_artists,
    MIN(extracted_at) AS first_extraction_time,
    MAX(extracted_at) AS latest_extraction_time,
    DATE_DIFF(
        'minute',
        MAX(extracted_at),
        CURRENT_TIMESTAMP
    ) AS data_age_minutes
FROM spotify_gold_db.artists
WHERE data_layer = 'gold'
GROUP BY
    extraction_date,
    artist_type
ORDER BY
    extraction_date DESC,
    unique_artists DESC;


-- 3. Artist Analytics using Window Functions
WITH artist_metrics AS (
    SELECT
        artist_id,
        artist_name,
        artist_type,
        spotify_url,
        extraction_date,
        extracted_at,

        COUNT(*) OVER (
            PARTITION BY artist_type
        ) AS artists_in_type,

        ROW_NUMBER() OVER (
            PARTITION BY artist_type
            ORDER BY extracted_at DESC
        ) AS freshness_rank

    FROM spotify_gold_db.artists
    WHERE
        data_layer = 'gold'
        AND artist_id IS NOT NULL
        AND artist_name IS NOT NULL
)

SELECT
    artist_id,
    artist_name,
    artist_type,
    extraction_date,
    extracted_at,
    artists_in_type,
    freshness_rank,

    CASE
        WHEN spotify_url IS NULL THEN 'Missing Spotify URL'
        ELSE 'Valid'
    END AS data_quality_status

FROM artist_metrics
ORDER BY
    artist_type,
    freshness_rank;
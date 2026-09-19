import json
import os
from datetime import datetime, timezone

import boto3
import requests


SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

ARTIST_ID = "4YRxDV8wJFPHPTeXepOstw"


def get_access_token():
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(
            os.environ["SPOTIFY_CLIENT_ID"],
            os.environ["SPOTIFY_CLIENT_SECRET"],
        ),
        timeout=30,
    )

    response.raise_for_status()
    return response.json()["access_token"]


def get_artist(token):
    response = requests.get(
        f"{SPOTIFY_API_URL}/artists/{ARTIST_ID}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def lambda_handler(event, context):
    token = get_access_token()
    artist = get_artist(token)

    extracted_at = datetime.now(timezone.utc)

    payload = {
        "artist": artist,
        "extracted_at": extracted_at.isoformat(),
    }

    bucket = os.environ["S3_BUCKET"]
    prefix = os.environ.get("S3_RAW_PREFIX", "raw/spotify/")

    s3_key = (
        f"{prefix}"
        f"year={extracted_at:%Y}/"
        f"month={extracted_at:%m}/"
        f"day={extracted_at:%d}/"
        f"spotify_{extracted_at:%Y%m%dT%H%M%SZ}.json"
    )

    s3 = boto3.client("s3")

    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=json.dumps(payload),
        ContentType="application/json",
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Spotify data extracted successfully",
                "s3_key": s3_key,
            }
        ),
    }

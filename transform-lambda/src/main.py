import os
import boto3
import logging
import pandas as pd
from spotipy import Spotify
from helper import Helper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def transform(albums, artists, songs):
    albums_df = pd.DataFrame(albums)
    artists_df = pd.DataFrame(artists)
    songs_df = pd.DataFrame(songs)

    #drop duplicate records
    albums_df.drop_duplicates(subset='album_id', inplace=True)
    artists_df.drop_duplicates(subset='artist_id', inplace=True)
    songs_df.drop_duplicates(subset='song_id', inplace=True)

    #convert data columns from string to dates
    albums_df['release_date'] = pd.to_datetime(albums_df['release_date'])
    songs_df['added_at'] = pd.to_datetime(songs_df['added_at'])

    return albums_df, artists_df, songs_df

def store_to_s3(albums_df, artists_df, songs_df):
    try:
        bucket = os.environ['BUCKET_NAME']
        path = os.environ['BUCKET_PATH']
        s3client = boto3.resource('s3')
        logger.info(f"Saving data to S3 bucket: {bucket}/{path}")
        s3client.put_object(Bucket=bucket, Key=f'{path}/albums.csv', Body=albums_df.to_json(index=False))
        s3client.put_object(Bucket=bucket, Key=f'{path}/artists.csv', Body=artists_df.to_json(index=False))
        s3client.put_object(Bucket=bucket, Key=f'{path}/songs.csv', Body=songs_df.to_json(index=False))
        logger.info(f"Data saved to S3 bucket: {bucket}/{path}")
    except Exception as e:
        logger.error(f"Error occurred while writing data to S3: {e}")

def read_from_s3(bucket, key):
    s3client = boto3.client('s3')
    logger.info(f"Reading data from S3 bucket: {bucket}/{key}")
    response = s3client.get_object(Bucket=bucket, Key=key)
    return pd.read_json(response['Body'].read())

def handler(event, context):
    bucket = os.environ['BUCKET_NAME']
    path = os.environ['BUCKET_PATH']

    data = read_from_s3(bucket, f'{path}/data.json')
    albums, artists, songs = Helper.flatten(data)
    albums_df, artists_df, songs_df = transform(albums, artists, songs)
    store_to_s3(albums_df, artists_df, songs_df)

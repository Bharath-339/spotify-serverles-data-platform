import os
import boto3
import logging
from spotify import Spotify

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def handler(event, context):
    # load_env_variables()
    client = Spotify()
    playlist_url = ["https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f"]
    data = client.get_playlist_tracks(playlist_url)

    bucket_name = os.environ['BUCKET_NAME']
    path = os.environ['BUCKET_PATH']
    s3client = boto3.client('s3')

    # writing raw data to s3
    s3client.upload_file('data.json', bucket_name, path)

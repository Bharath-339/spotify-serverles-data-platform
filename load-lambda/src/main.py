from dotenv import load_dotenv
from spotify import Spotify

def load_env_variables():
    load_dotenv()

def handler(event, context):
    load_env_variables()
    spotify_client = Spotify()
    spotify_token = spotify_client.bearer_token
    print(spotify_token)

handler({},{})
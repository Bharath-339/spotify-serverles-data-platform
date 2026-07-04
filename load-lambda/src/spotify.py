import os
import requests
import base64
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Spotify:
    def __init__(self):
        self.token = os.environ["SPOTIFY_CLIENT_SECRET"]
        self.client_id = os.environ["SPOTIFY_CLIENT_ID"]
        self.url = "https://accounts.spotify.com/api/token"
        self.bearer_token = self.get_token()

    def get_token(self):
        try:
            logger.info("initializing Spotify client to get bearer token")
            auth_string = base64.b64encode("{}:{}".format(self.client_id, self.token).encode()).decode()
            headers = {
                            "Authorization": f"Basic {auth_string}",
                            "Content-Type" : "application/x-www-form-urlencoded"
                      }
            response = requests.post(
                            self.url,
                            headers = headers,
                            data = {"grant_type": "client_credentials"}
                        )
            response.raise_for_status()
            bearer_token = response.json()["access_token"]
            logger.info("bearer token received")
            return bearer_token
        except Exception as e:
            logger.error("something went wrong: {}".format(str(e)))
            return None

    def fetch_data(self):
        pass
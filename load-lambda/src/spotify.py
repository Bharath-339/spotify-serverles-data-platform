import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Spotify:
    def __init__(self):
        self.token = os.environ["SPOTIFY_CLIENT_SECRET"]
        self.client_id = os.environ["SPOTIFY_CLIENT_ID"]
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_id
        )
        self.sp = spotipy.Spotify(auth_manager=self.client_credentials_manager)

    def get_playlist_tracks(self, playlist_url):
        data = []
        for url in playlist_url:
            playlist_id = url.split("/")[-1].split('?')[0]
            logger.info(f"Getting tracks for {playlist_id}")
            data.extend(self.sp.playlist_items(playlist_id)["items"])
            logger.info(f"Finished getting tracks for {playlist_id}")
        return data

    @classmethod
    def flatten(cls, data):
        albums = cls.flatten_albums(data)
        artists = cls.flatten_artists(data)
        songs = cls.flatten_songs(data)

        return albums, artists, songs


    @classmethod
    def flatten_albums(cls, data):
        albums = []
        for item in data:
            album_id = item['track']['album']['id']
            album_name = item['track']['album']['name']
            album_release_date = item['track']['album']['release_date']
            album_total_tracks = item['track']['album']['total_tracks']
            album_url = item['track']['album']['external_urls']['spotify']

            albums.append({
                "id": album_id,
                "name": album_name,
                "release_date": album_release_date,
                "total_tracks": album_total_tracks,
                "url": album_url
            })

        return albums

    @classmethod
    def flatten_artists(cls, data):
        artists = []
        for item in data:
            for key, value in item.items():
                if key == "track":
                    for artist in value['artists']:
                        artist_dict = {
                            'artist_id': artist['id'],
                            'artist_name': artist['name'],
                            'external_url': artist['href']
                        }
                        artists.append(artist_dict)
        return artists

    @classmethod
    def flatten_songs(cls, data):
        songs = []
        for item in data:
            song_id = item['track']['id']
            song_name = item['track']['name']
            song_duration = item['track']['duration_ms']
            song_url = item['track']['external_urls']['spotify']
            song_popularity = item['track']['popularity']
            song_added = item['added_at']
            album_id = item['track']['album']['id']
            artist_id = item['track']['album']['artists'][0]['id']

            song_element = {
                'song_id': song_id,
                'song_name': song_name,
                'duration_ms': song_duration,
                'url': song_url,
                'popularity': song_popularity,
                'song_added': song_added,
                'album_id': album_id,
                'artist_id': artist_id
            }
            songs.append(song_element)
        return songs
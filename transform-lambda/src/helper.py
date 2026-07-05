import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Helper:
    @classmethod
    def flatten(cls, data):
        albums = cls.flatten_albums(data)
        artists = cls.flatten_artists(data)
        songs = cls.flatten_songs(data)

        return albums, artists, songs


    @classmethod
    def flatten_albums(cls, data):
        logger.info("flattening albums")
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
        logger.info("flattening artists")
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
        logger.info("flattening songs")
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
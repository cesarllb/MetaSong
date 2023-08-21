import musicbrainzngs as api


class QueryMusicMetadata:
    
    def __init__(self) -> None:
        api.set_useragent(app='meta_song', version= '0.0.1', contact = 'https://github.com/cesarllb/MetaSong')
        
    def search_songs(self, artist: str, album: str):    
        result = api.search_releases(artist=artist, release=album, limit=5)
        if result['release-list']:
            for idx, release in enumerate(result['release-list']):
                if idx == 0:
                    return_dict = release
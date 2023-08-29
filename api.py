import asyncio
import musicbrainzngs
from pprint import pprint
from Levenshtein import distance


musicbrainzngs.set_useragent(app='meta_song', version= '0.0.1', contact = 'https://github.com/cesarllb/MetaSong')
    

async def search_songs(artist: str, album: str, precision: float = 0.9) -> list[str]:
    '''Precision says how much error tolerant the search must be'''
    result = musicbrainzngs.search_recordings(artist=artist + f"~{precision}", release=album + f"~{precision}")
    title_list: list = []
    if result["recording-list"]:
        for recording in result["recording-list"]:
            title_list.append(recording["title"])
    return title_list

# pprint(asyncio.run(search_songs(artist='One Direction', album='Take me home')))

async def search_albums(artist: str, precision: float = 0.9) -> list[str]:
    '''Precision says how much error tolerant the search must be'''
    result = musicbrainzngs.search_releases(artist=artist + f"~{precision}")
    album_list: list = []
    if result["release-list"]:
        for release in result["release-list"]:
            album_list.append(release["title"])
    return album_list

async def search_song(artist: str, album: str, song: str, precision: float = 0.9) -> str:
    result = musicbrainzngs.search_recordings(artist=artist + f"~{precision}", release=album + f"~{precision}")
    if result["recording-list"]:
        for recording in result["recording-list"]:
            if song in recording["title"]:
                return recording["title"]
            
async def search_artist(artist: str = None, precision: float = 0.9) -> str:
    result = musicbrainzngs.search_artists(artist=artist + f"~{precision}")
    similar_artist = ''
    #algoritm for find the element in artist_list more similar to the artist parameter
    if result["artist-list"]:
        min = 9999
        for r in result["artist-list"]:
            r = r['name']
            dist = distance(r, artist)
            if dist < min:
                min = dist; similar_artist = r
                
    return similar_artist
    

    
async def search_album(artist: str, song: str, precision: float = 0.9) -> str:
    '''Precision says how much error tolerant the search must be'''
    result = musicbrainzngs.search_recordings(artist=artist + f"~{precision}", recording=song + f"~{precision}")
    if result["recording-list"]:
        album = result["recording-list"][0]["release-list"][0]["title"]
        return album
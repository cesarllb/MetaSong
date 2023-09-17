import os
from pprint import pprint
import musicbrainzngs
from Levenshtein import distance

from code.logger import log_data


musicbrainzngs.set_useragent(app='meta_song', version= '0.0.1', contact = 'https://github.com/cesarllb/MetaSong')
    

async def search_songs(artist: str, album: str, precision: float = 0.9) -> list[str]:
    '''Precision says how much error tolerant the search must be'''
    result = musicbrainzngs.search_recordings(artist=artist + f"~{precision}", release=album + f"~{precision}")
    title_list: list = []
    if result["recording-list"]:
        for recording in result["recording-list"]:
            title_list.append(recording["title"])
    return title_list

async def search_song(artist: str, album: str, song: str, precision: float = 0.9, threshold: int = 0) -> str:
    result = musicbrainzngs.search_recordings(artist=artist + f"~{precision}", release=album + f"~{precision}")
    if result["recording-list"]:
        similar_song = ''; min = 9999; best_distance = 0
        for r in result["recording-list"]:
            r = r['title']
            dist = distance(r, song)
            if dist < min:
                min = dist; similar_song = r; best_distance = dist
            if best_distance < threshold:
                return similar_song
            
async def search_artist(artist: str = None, precision: float = 0.9, threshold: int = 6) -> str:
    result = musicbrainzngs.search_artists(artist=artist + f"~{precision}")
    similar_artist = ''
    #algorithm for find the element in artist_list more similar to the artist parameter
    if result["artist-list"]:
        min = 9999; best_distance = 0
        for r in result["artist-list"]:
            r = r['name']
            dist = distance(r, artist)
            if dist < min:
                min = dist; similar_artist = r; best_distance = dist
        if best_distance <= threshold:
            return similar_artist
    
async def search_albums(artist: str, precision: float = 0.9) -> list[str]:
    '''Precision says how much error tolerant the search must be'''
    result = musicbrainzngs.search_releases(artist=artist + f"~{precision}")
    album_list: list = []
    if result["release-list"]:
        for release in result["release-list"]:
            album_list.append(release["title"])
    return album_list
    
async def search_album(artist: str, album: str, precision: float = 0.9, threshold: int = 6) -> str:
    '''Precision says how much error tolerant the search must be'''
    result = musicbrainzngs.search_releases(artist = artist + f"~{precision}", release = album + f"~{precision}")
    if result["release-list"]:
        similar_album = ''; min = 9999; best_distance = 0
        for r in result["release-list"]:
            r = r["title"]
            dist = distance(r, album)
            if dist < min:
                min = dist; similar_album = r; best_distance = dist
        if best_distance < threshold:   
            return similar_album
    
async def search_album_by_song(artist: str, song: str, precision: float = 0.9) -> str:
    '''Precision says how much error tolerant the search must be'''
    result = musicbrainzngs.search_recordings(artist = artist + f"~{precision}", recording = song + f"~{precision}")
    if result["recording-list"]:
        album = result["recording-list"][0]["release-list"][0]["title"]
        return album


async def download_and_add_album_cover(artist: str, album: str, path: str, precision: float = 0.9):
    musicbrainzngs.set_rate_limit(limit_or_interval=1.0, new_requests=1)
    results = musicbrainzngs.search_releases(artist = artist + f"~{precision}", release = album + f"~{precision}", limit=1)
    if "release-list" in results and len(results["release-list"]) > 0:
        release_id = results["release-list"][0]["id"]; images = []
        try:
            images = musicbrainzngs.get_image_list(release_id)
            if len(images) > 0:
                image_data = musicbrainzngs.get_image(mbid= release_id, coverid = images["images"][0]['id'], size=500)
                with open(os.path.join(path, f"{album}_cover.jpg"), "wb") as f:
                    f.write(image_data)
        except musicbrainzngs.musicbrainz.ResponseError as e:
            log_data(f"An error occurred: {e}")
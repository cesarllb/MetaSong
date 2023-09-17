import os
import asyncio
import music_tag
import itertools
from logger import log_data
from Levenshtein import distance
from api import search_songs, search_artist, search_album
from db import get_serialized_dict, update_serialized_dict, update_db, DB_NEW, DB_PATH

class SongTag:
    TITLE, ARTIST, ALBUM = 1, 2, 3

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]
        self.song_tag = music_tag.load_file(self.path)
    
    def set_tag(self, type: int, value: str, save: bool = False) -> None:
        if type == SongTag.TITLE:
            self.song_tag['title'] = value
        elif type == SongTag.ARTIST:
            self.song_tag['artist'] = value
        elif type == SongTag.ALBUM:
            self.song_tag['album'] = value
        elif isinstance(type, str):
            self.song_tag[type] = value
        if save:
            self.song_tag.save()
    def save(self):
        self.song_tag.save()

class AlbumTag:

    def __init__(self, path, songs_path: list, NO_ALBUM: bool = False):
        self.path = path
        self.NO_ALBUM = NO_ALBUM
        self.album_name = path.split('/')[-1] if not NO_ALBUM else 'Unknown'
        self.artist_name = path.split('/')[-2] if not NO_ALBUM else path.split('/')[-1]
        self.songs_path = [s for s in songs_path if os.path.isfile(s)]
        self.songs_tag = self._get_album_song_tag_list()

    def _get_album_song_tag_list(self) -> list[SongTag]:
        list_of_songs_tag = []
        for path in self.songs_path:
            list_of_songs_tag.append(SongTag(path))
        return list_of_songs_tag

    def set_songs_tag_by_type(self, type: int, 
                            values: list[str] = None, 
                            save: bool = False) -> bool:

        for i, song_tag in enumerate(self.songs_tag):
            if type == 1 and len(values) == len(self.songs_tag):
                song_tag.set_tag(type, values[i])
            elif type == 1:
                raise Exception('The len of values is not equal to the number of song. ')
            if type == 2:
                song_tag.set_tag(type, self.artist_name)
            elif type == 3:
                song_tag.set_tag(type, self.album_name)
            if save:
                song_tag.save()
        return True
        
        
    def save(self):
        for song_tag in self.songs_tag:
            song_tag.save()
        
    def set_song_tag_by_name(self, type: int, 
                            song_name: str, 
                            value: str, 
                            save: bool = False) -> None:
        
        for song_tag in self.songs_tag:
            if song_tag.name in song_name or song_name in song_tag.name:
                song_tag.set_tag(type, value)
                if save:
                    song_tag.save()
        return True

class ArtistTag:
    def __init__(self, name: str) -> None:
        self.name = name
        self.album_song_dict_path = get_serialized_dict(DB_PATH, self.name)
        self.NO_ALBUM = self._is_NO_ALBUM()
        self.albums_tag = self._get_albums_tag()

    def _is_NO_ALBUM(self) -> bool:
        album_dict = get_serialized_dict(DB_NEW, self.name)
        return True if list(album_dict)[0] == 'NO ALBUM' else False
    
    def get_album_tag(self, album_name: str) -> AlbumTag:
        tag = list([ a for a in self.albums_tag if a.album_name == album_name])
        return tag[0] if tag else None

    def _get_albums_tag(self) -> list[AlbumTag]:
        list_albums_tag = []
        for album_path in self.album_song_dict_path:
            if os.path.isdir(album_path):
                list_albums_tag.append(AlbumTag(album_path, self.album_song_dict_path[album_path], self.NO_ALBUM))
        return list_albums_tag
    
    def apply_by_dict(self):
        for album in self.albums_tag:
            #Set tags to all song
            self.set_tags_to_songs(SongTag.ALBUM, album)
            self.set_tags_to_songs(SongTag.ARTIST, album)
            self.set_tags_to_songs(SongTag.TITLE, album)

    def set_tags_to_songs(self, type: int, album_tag: AlbumTag):
        album_len = len(album_tag.songs_tag)
        if type in (1, 2, 3):
            if type == SongTag.TITLE:
                values = [album_tag.songs_tag[i].name for i in range(album_len)]
                album_tag.set_songs_tag_by_type(type, values)
            else:
                if self.NO_ALBUM:
                    album_tag.album_name = album_tag.artist_name + ' Mix'
                album_tag.set_songs_tag_by_type(type)
                
            album_tag.save()
            
    async def update_all_by_api(self):
        if self.NO_ALBUM:
            asyncio.gather( self.update_albums_name(), self.update_songs_name() )
            await self.update_unknown_album()
        else:
            asyncio.gather( self.update_albums_name(), self.update_songs_name() )
        await self.update_artist_name()

    async def update_unknown_album(self):
        if self.NO_ALBUM:
            album_tag = self.albums_tag[0]
            api_artist = await search_artist(self.name)
            if api_artist:
                album_tag.artist_name = api_artist
                album_tag.set_songs_tag_by_type(SongTag.ARTIST, save= True)
            
    async def update_albums_name(self, threshold: int = 6):
        album_song_dict: dict = get_serialized_dict(DB_NEW, self.name)
        new_album_song_dict: dict = {}
        if not self.NO_ALBUM:
            results = [None] * len(album_song_dict)
            for i, album in enumerate(album_song_dict): #get info from API
                result = await search_album(self.name, album)
                results[i] = result
            for i, album in enumerate(album_song_dict):
                api_album = results[i]
                if api_album:
                    album_tag = self.get_album_tag(album)
                    for s in album_song_dict[album]:
                        if album_tag and distance(s, api_album) < threshold:
                            album_tag.set_song_tag_by_name(SongTag.ALBUM, song_name = s, value = api_album, save = True)
                            log_data(album_tag.album_name + ' -> ' + api_album)
                    if album_tag:
                        new_album_song_dict[api_album] = album_song_dict[album]
            if len(list(itertools.chain(*album_song_dict.values()))) == \
                            len(list(itertools.chain(*new_album_song_dict.values()))):
                update_serialized_dict(DB_NEW, self.name, new_album_song_dict)
                
    async def update_songs_name(self, threshold: int = 6):
        album_song_dict: dict = get_serialized_dict(DB_NEW, self.name)
        new_album_song_dict: dict = {}
        if not self.NO_ALBUM:
            results = [None] * len(album_song_dict.keys())
            for i, album in enumerate(album_song_dict): #get info from API
                results_api = await search_songs(self.name, album)
                results[i] = results_api
            for i, a in enumerate(album_song_dict):
                api_songs =  results[i] #songs searched in api for this album
                api_songs = self._best_api_songs(api_songs, album_song_dict[a]) #the most similar api_song for each old song in this album
                album_tag = self.get_album_tag(a)
                count = 0
                for s, api_s in zip(album_song_dict[a], api_songs):
                    if api_s and album_tag and distance(s, api_s) < threshold:
                        album_tag.set_song_tag_by_name(SongTag.TITLE, song_name = s, value = api_s, save = True)
                        count += 1; log_data(s + ' -> ' + api_s)
                if len(api_songs) == count:
                    new_album_song_dict[a] = api_songs
                    
            if len(list(itertools.chain(*album_song_dict.values()))) == \
                            len(list(itertools.chain(*new_album_song_dict.values()))):
                update_serialized_dict(DB_NEW, self.name, new_album_song_dict)
            
    def _best_api_songs(self, api_songs: list[str], old_songs: list[str], threshold: int = 6):
        new_api_songs = []
        for song in old_songs:
            min = 9999; best_api_for_song = ''; best_distance = 0
            for api in api_songs:
                dist = distance(song, api)
                if dist < min:
                    min = dist; best_distance = dist; best_api_for_song = api
            if best_distance <= threshold:
                new_api_songs.append(best_api_for_song)
            else:
                new_api_songs.append(None)
        return new_api_songs
                
    async def update_artist_name(self):  
        api_artist = await search_artist(artist=self.name) #find in the api
        if api_artist != self.name and api_artist:
            update_db(self.name, api_artist)
            self.name =  api_artist
            for tag in self.albums_tag:
                log_data(tag.artist_name + ' -> ' + api_artist)
                tag.artist_name = api_artist
                tag.set_songs_tag_by_type(SongTag.ARTIST, save= True)
                    
async def apply_tags(names: list[str], api: bool = False):
    for name in names:
        a_tag = ArtistTag(name)
        a_tag.apply_by_dict()
        if api:
            await a_tag.update_all_by_api()
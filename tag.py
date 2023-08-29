import os
import db
import asyncio
import music_tag
from Levenshtein import distance
from db import get_serialized_dict, update_serialized_dict, update_db
from api import search_albums, search_songs, search_artist, search_album
              
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
            else:
                raise Exception('The len of values is not equal to the number of song. ')
            if type == 2:
                song_tag.set_tag(type, self.artist_name)
            elif type == 3:
                song_tag.set_tag(type, self.album_name)
            if save:
                song_tag.save()
            return True
            
        return False
        
    def save(self):
        for song_tag in self.songs_tag:
            song_tag.save()
        
    def set_song_tag_by_name(self, type: str | int, 
                             song_name: str, 
                             value: str, 
                             save: bool = False) -> None:
        
        for song_tag in self.songs_tag:
            if song_tag.name in song_name or song_name in song_tag.name:
                song_tag.set_tag(type, value)
                if save:
                    song_tag.save()
                return True
        return False

class ArtistTag:
    def __init__(self, name: str) -> None:
        self.name = name
        self.album_song_dict_path = get_serialized_dict(db.DB_PATH, self.name)
        self.NO_ALBUM = self._is_NO_ALBUM()
        self.albums_tag = self._get_albums_tag()
        
    def _is_NO_ALBUM(self):
        album_dict = get_serialized_dict(db.DB_NEW, self.name)
        return True if list(album_dict)[0] == 'NO ALBUM' else False

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
                album_tag.set_songs_tag_by_type(type)
                
            album_tag.save()
            
    async def update_all_by_api(self): 
        if self.NO_ALBUM:
            asyncio.gather( self.update_albums_name(), self.update_songs_name(),
                            self.update_unknown_album() )
        else:
            asyncio.gather( self.update_albums_name(), self.update_songs_name() )

    async def update_unknown_album(self):
        album_song_dict: dict = get_serialized_dict(db.DB_NEW, self.name)
        if self.NO_ALBUM:
            songs_values: list = list(album_song_dict.values())
            for i in range(len(songs_values)):
                a_song_name = str(songs_values[i])
                album_name = await search_album(self.name, a_song_name)
                self.albums_tag[0].set_song_tag_by_name(SongTag.ALBUM, a_song_name, album_name, save = True)
                
    async def update_songs_name(self):
        album_song_dict: dict = get_serialized_dict(db.DB_NEW, self.name)
        new_album_song_dict: dict = {}
        if len(album_song_dict.keys()) == len(self.albums_tag):
            for album, album_tag in zip(album_song_dict, self.albums_tag):
                api_songs = await search_songs(self.name, album)
                # api_songs = await task #find in the api
                if len(api_songs) == len(album_tag.songs_tag):
                    album_tag.set_songs_tag_by_type(SongTag.ARTIST, api_songs, save= True)
                    new_album_song_dict[album] = api_songs
                else:    
                    songs_list = []
                    for i1, api_s in enumerate(api_songs):
                        dist, index_api, index_album = 9999, 0, 0
                        for i2, album_s in enumerate(album_song_dict[album]): # min distance api search songs and existing songs in db
                            temp_dist = distance(api_s, album_s)
                            if temp_dist < dist:
                                dist = temp_dist; index_api = i1; index_album = i2
                        if album_song_dict[album][index_album].lower() != api_songs[index_api].lower():    
                            album_tag.set_song_tag_by_name(SongTag.TITLE, song_name= album_song_dict[album][index_album], value= api_songs[index_api], save= True)
                            songs_list.append(api_songs[index_api])
                    new_album_song_dict[album] = songs_list 
        if len(album_song_dict.values()) == len(new_album_song_dict.values()):
            update_serialized_dict(db.DB_NEW, self.name, new_album_song_dict)
            
    async def update_albums_name(self):
        album_song_dict: dict = get_serialized_dict(db.DB_NEW, self.name)
        new_album_song_dict: dict = {}
        if len(album_song_dict.keys()) == len(self.albums_tag): 
            api_albums = await search_albums(self.name) #find in the api
            
            if len(api_albums) == len(self.albums_tag):
                songs_list = []
                for i2, album_tag in enumerate(self.albums_tag):
                    dist, index_api, index_album = 9999, 0, 0
                    for i1, album_api in enumerate(api_albums):# min distance api search album and existing album in db
                        temp_dist = distance(album_tag.album_name, album_api)
                        if temp_dist < dist:
                            dist = temp_dist; index_api = i1; index_tag = i2
                            
                    if not album_tag.NO_ALBUM and album_tag.album_name in album_song_dict.keys() \
                                    and album_tag.album_name.lower() != api_albums[index_api].lower(): #updating the albums_name of the db
                            
                        songs_list = album_song_dict[album_tag.album_name] #get the list of songs of the album
                        new_album_song_dict[ api_albums[index_api] ] = songs_list #update the album name
                        
                        self.albums_tag[index_tag].album_name = api_albums[index_api]
                        self.albums_tag[index_tag].set_songs_tag_by_type(SongTag.ALBUM, save= True)
        if len(album_song_dict.values()) == len(new_album_song_dict.values()): 
            update_serialized_dict(db.DB_NEW, self.name, new_album_song_dict)
            
    async def update_artist_name(self):
        album_song_dict: dict = get_serialized_dict(db.DB_NEW, self.name)
        if not self.NO_ALBUM:     
            first_album = list(album_song_dict.keys())[0]
            first_song = album_song_dict[first_album][0]
            api_artist = await search_artist(artist=self.name) #find in the api
            if api_artist != self.name:
                update_db(self.name, api_artist)
                self.name =  api_artist
                for tag in self.albums_tag:
                    tag.artist_name = api_artist
                    tag.set_songs_tag_by_type(SongTag.ARTIST, save= True)
                    
async def apply_tags(names: list[str], api: bool = False):
    for name in names:
        a_tag = ArtistTag(name)
        a_tag.apply_by_dict()
        if api:
            await a_tag.update_all_by_api()
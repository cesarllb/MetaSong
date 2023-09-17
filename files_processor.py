import os
from abc import ABC, abstractmethod
from collections import defaultdict
from logger import log_multiple_data
from db import get_serialized_dict, save_serialized_dict, DB_NEW, DB_PATH, DB_OLD
from chain import run_chain, RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, \
                                    RemoveSubstrings, CompatibleFormat, RemoveExtension, \
                                    RemoveMultiplesSpaces, RemoveSpaceBeforeExtension

class IArtistFolderProcessor(ABC):
    
    @abstractmethod
    def __init__(self, path:str, load_db: bool = True):
        ...

    @abstractmethod
    def refresh(self):
        ...
        

class ArtistFolderProcessor(IArtistFolderProcessor):
    NO_ALBUM: str = 'NO ALBUM'
    
    def __init__(self, path:str, load_db: bool = True):
        self.root = path
        self.name = path.split('/')[-1]

        self.album_song_dict = self._get_album_song_dict(load_db)
        self.albums = list(self.album_song_dict.keys())
        self.songs = list([song for album in self.albums for song in self.album_song_dict[album]])
        
        self.new_album_song_dict = self._get_new_album_song_dict(load_db)
        self.new_albums = list(self.new_album_song_dict.keys())
        self.new_songs = list([song for album in self.new_albums for song in self.new_album_song_dict[album]])
        
        log_multiple_data({'name: ': self.name , 'old: \n': self.album_song_dict, 'new: \n': self.new_album_song_dict})
        

    def _get_album_song_dict(self, load_db: bool = True):
        album_song_dict = get_serialized_dict(DB_OLD, self.name)
        if album_song_dict and load_db:
            return album_song_dict
        no_album = self.check_no_album(self.root)
        for elem in os.listdir(self.root):
            elem_path = os.path.join(self.root, elem)
            if os.path.isdir(elem_path) and not no_album:
                album_song_dict[elem] = list([f for f in os.listdir(elem_path) if os.path.isfile(os.path.join(elem_path, f)) 
                                            and run_chain(f, chain=[CompatibleFormat])])
            elif os.path.isfile(elem_path) and no_album:
                album_song_dict[self.NO_ALBUM] = list([f for f in os.listdir(self.root) if os.path.isfile(os.path.join(self.root, f)) 
                                                        and run_chain(f, chain=[CompatibleFormat])])
        save_serialized_dict(DB_OLD, self.name, album_song_dict)
        return album_song_dict
    
    def check_no_album(self, root: str) -> bool:
        dirs = False; files = False
        for elem in os.listdir(self.root):
            elem_path = os.path.join(self.root, elem)
            if os.path.isdir(elem_path):
                dirs = True
            if os.path.isfile(elem_path):
                files = True
        return True if not dirs and files else False

    def _get_new_album_song_dict(self, load_db: bool = True):
        '''If it have subfolders/albums it not analyze files in the root/artist path'''
        new_album_song_dict = get_serialized_dict(DB_NEW, self.name)
        if new_album_song_dict and load_db:
            return new_album_song_dict
        
        for album in self.albums:
            new_album_name = run_chain(album, chain = (RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, RemoveMultiplesSpaces)) \
                            if album != self.NO_ALBUM else self.NO_ALBUM
            list_songs = []
            for song in self.album_song_dict[album]:
                new_file_name = run_chain(song, chain= [CompatibleFormat, RemoveBetweenParenthesis, 
                            BeginsNumber, RemoveSubstrings, RemoveSymbols, RemoveMultiplesSpaces, RemoveSpaceBeforeExtension])
                list_songs.append(new_file_name if new_file_name else song)
            new_album_song_dict[new_album_name] = list_songs
            
        # new_album_song_dict = self.remove_duplicates(new_album_song_dict)
        save_serialized_dict(DB_NEW, self.name, new_album_song_dict)
        return new_album_song_dict

    def remove_duplicates(self, dictionary: dict) -> dict:
        new_dict = defaultdict(list)
        unique_keys = set()
        for key, value in dictionary.items():
            if key not in unique_keys:
                unique_keys.add(key)
                for item in set(value):
                    new_dict[key].append(item)
        return dict(new_dict)

    def refresh(self):
        self.album_song_dict = self._get_album_song_dict(load_db = False)
        self.new_album_song_dict = self._get_new_album_song_dict(load_db = False)
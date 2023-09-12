import os
from abc import ABC, abstractmethod
from code.files_processor import ArtistFolderProcessor, IArtistFolderProcessor
from code.db import save_serialized_dict, update_serialized_dict
from code.chain import RemoveBetweenParenthesis, RemoveMultiplesSpaces, RemoveSymbols, run_chain

class IArtistFolderEditor(ABC):
    
    @abstractmethod
    def __init__(self, path: str) -> None:
        ...
    
    @abstractmethod
    def apply_artist_name(self, path: str):
        ...
        
    @abstractmethod
    def refresh(self):
        ...
        
    @abstractmethod
    def apply(self) -> dict[ str , list[str]]:
        ...

class ArtistFolderEditor:

    def __init__(self, path: str):
        self.root = self.apply_artist_name(path)
        self.processor: IArtistFolderProcessor = ArtistFolderProcessor(self.root)
        self.name = self.processor.name
        self.NO_ALBUM = False
        self.albums_path: list = self._get_album_path()
        self.songs_path: list = self._get_songs_path()
        self.album_song_dict_path: dict = self._get_album_song_dict_path()
        save_serialized_dict(db.DB_PATH, self.name, self.album_song_dict_path)
        self.unsolved_song_path: list = []

    def apply_artist_name(self, path: str):
        self.new_name = run_chain(path.split('/')[-1], chain = (RemoveBetweenParenthesis, RemoveSymbols, RemoveMultiplesSpaces))
        new_path = os.path.join( os.path.dirname(path) , self.new_name)
        os.rename(path, new_path)# Rename the artist dir name
        return new_path
        
    def refresh(self):
        self.processor.refresh()
        self.NO_ALBUM = False
        self.albums_path: list = self._get_album_path()
        self.songs_path: list = self._get_songs_path()
        self.album_song_dict_path: dict = self._get_album_song_dict_path()

    def _get_unsolved_song_path(self):
        unsolved = []
        for song_path, new_song_name in zip(self.songs_path, self.processor.new_songs):
            path = ''
            for s in song_path.split('/')[:-1]:
                path = os.path.join(path, s)

            new_song = os.path.join(path, new_song_name)
            if not os.path.isfile(new_song):
                unsolved.append(song_path)
        return unsolved

    def _get_album_path(self):
        albums_path = []
        for a in self.processor.albums:
            if a == self.processor.NO_ALBUM:
                albums_path.append(self.root)
                self.NO_ALBUM = True
                break
            else:
                albums_path.append(os.path.join(self.root, a))
        return albums_path

    def _get_songs_path(self):
        songs_path = []
        for album in self.processor.albums:
            for song in self.processor.album_song_dict[album]:
                if album == self.processor.NO_ALBUM:
                    songs_path.append(os.path.join(self.root, song))
                else:
                    songs_path.append(os.path.join(self.root, album, song))
        return songs_path

    def _get_album_song_dict_path(self):
        album_song_dict_path = {}
        for album_path in self.albums_path:
            songs_list = []
            for song_path in self.songs_path:
                song = song_path.split('/')[-1]
                album = album_path.split('/')[-1] if not self.NO_ALBUM else self.processor.NO_ALBUM
                if song in self.processor.album_song_dict[album]:
                    songs_list.append(song_path)
            album_song_dict_path[album_path] = songs_list
        return album_song_dict_path

    def apply(self) -> dict[ str , list[str]]:
        new_album_song_dict_path = {}
        try:
            for album_path, new_album in zip(self.albums_path, self.processor.new_albums):
                is_dir = os.path.isdir(album_path)
                if is_dir:
                    list_songs_path = []
                    for song_path, new_song in zip(self.album_song_dict_path[album_path], self.processor.new_album_song_dict[new_album]):
                        if os.path.isfile(song_path):
                            new_song_path = os.path.join(album_path, new_song)
                            os.rename(song_path, new_song_path)
                            if self.NO_ALBUM:
                                list_songs_path.append(os.path.join(self.root, new_song))
                            else:
                                list_songs_path.append(os.path.join(self.root, new_album, new_song))
                    if self.NO_ALBUM:
                        new_album_song_dict_path[ self.root ] = list_songs_path
                    else:
                        new_album_path = os.path.join(self.root, new_album)
                        os.rename(album_path, new_album_path)
                        new_album_song_dict_path[new_album_path] = list_songs_path 
        except FileNotFoundError as e:
            print('The file: ', e.filename, ' not found. \n')
        except NotADirectoryError as e:
            print('The dir: ', e.filename, ' error. \n')
        
        update_serialized_dict(db.DB_PATH, self.name, new_album_song_dict_path)
        self.album_song_dict_path = new_album_song_dict_path
            
        self.unsolved_song_path = self._get_unsolved_song_path()
        
def initialize_editors(path: str) -> list[IArtistFolderEditor]:
    list_editor = []
    try:
        for dir in os.listdir(path):
            if os.path.isdir(os.path.join(path, dir)):
                editor = ArtistFolderEditor(os.path.join(path, dir))
                list_editor.append(editor)
    except Exception as e:
        print(e.args)
    return list_editor

def apply_changes_to_files(editors: list[IArtistFolderEditor]) -> None:
    for e in editors:
        e.apply()

def get_unsolved(editors: list[IArtistFolderEditor]):
    return [u for i in range(len(editors)) \
            for u in editors[i].unsolved_song_path] \
            if editors else None
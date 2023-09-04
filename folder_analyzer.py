import os
import db
from collections import defaultdict
from logger import log_multiple_data
from db import get_serialized_dict, save_serialized_dict
from chain import run_chain, RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, \
                                    RemoveSubstrings, CompatibleFormat, RemoveExtension, \
                                    RemoveMultiplesSpaces, RemoveSpaceBeforeExtension
            
class ArtistFolderProcessor:
    NO_ALBUM: str = 'NO ALBUM'
    
    def __init__(self, path:str, load_db: bool = True):
        self.root = path
        self.name = path.split('/')[-1]
        self.new_name = run_chain(self.name, chain = (RemoveBetweenParenthesis, RemoveSymbols, RemoveMultiplesSpaces))

        self.album_song_dict = self._get_album_song_dict(load_db)
        self.albums = list(self.album_song_dict.keys())
        self.songs = list([song for album in self.albums for song in self.album_song_dict[album]])
        
        self.new_album_song_dict = self._get_new_album_song_dict(load_db)
        self.new_albums = list(self.new_album_song_dict.keys())
        self.new_songs = list([song for album in self.new_albums for song in self.new_album_song_dict[album]])
        
        log_multiple_data({'name: ': self.name , 'old: \n': self.album_song_dict, 'new: \n': self.new_album_song_dict})
        

    def _get_album_song_dict(self, load_db: bool = True):
        album_song_dict = get_serialized_dict(db.DB_OLD, self.name)
        if album_song_dict and load_db:
            return album_song_dict
        
        root_files = []
        for elem in os.listdir(self.root):
            elem_path = os.path.join(self.root, elem)
            if os.path.isdir(elem_path):
                album_song_dict[elem] = list([f for f in os.listdir(elem_path) if os.path.isfile(os.path.join(elem_path, f)) 
                                              and run_chain(f, chain=[CompatibleFormat])])
            elif os.path.isfile(elem_path):
                 if run_chain(elem, chain=[CompatibleFormat]):
                    root_files.append(elem)
        if root_files and not album_song_dict:
            album_song_dict[self.NO_ALBUM] = root_files
            
        save_serialized_dict(db.DB_OLD, self.name, album_song_dict)
        return album_song_dict
    
    def _get_new_album_song_dict(self, load_db: bool = True):
        '''If it have subfolders/albums it not analyze files in the root/artist path'''
        new_album_song_dict = get_serialized_dict(db.DB_NEW, self.name)
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
        save_serialized_dict(db.DB_NEW, self.name, new_album_song_dict)
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
    
class ArtistFolderEditor:
    
    def __init__(self, path: str) -> None:
        self.processor = ArtistFolderProcessor(path)
        self.name = self.processor.name
        self.root = self.processor.root
        self.NO_ALBUM = False
        self.albums_path: list = self._get_album_path()
        self.songs_path: list = self._get_songs_path()
        self.album_song_dict_path: dict = self._get_album_song_dict_path()
        self.new_album_song_dict_path: dict = {}
        self.unsolved_song_path: list = []
    
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
        new_album_song_dict_path = get_serialized_dict(db.DB_PATH, self.name)
        try:
            for album_path, new_album in zip(self.albums_path, self.processor.new_albums):
                list_songs_path = []
                if os.path.isdir(album_path):
                    for song_path, new_song in zip(self.album_song_dict_path[album_path], self.processor.new_album_song_dict[new_album]):
                        if os.path.isfile(song_path):
                            new_song_path = os.path.join(album_path, new_song)
                            os.rename(song_path, new_song_path)
                            list_songs_path.append(new_song_path)
                if not self.NO_ALBUM:
                    new_album_path = os.path.join(self.root, new_album)
                    os.rename(album_path, new_album_path)
                    new_album_song_dict_path[new_album_path] = list_songs_path
                else:
                    new_album_song_dict_path[ self.root ] = list_songs_path
        except FileNotFoundError as e:
            print('The file: ', e.filename, ' not found. \n')
        except NotADirectoryError as e:
            print('The dir: ', e.filename, ' error. \n')
            
        self.new_album_song_dict_path = new_album_song_dict_path
        save_serialized_dict(db.DB_PATH, self.name, new_album_song_dict_path)
        self.unsolved_song_path = self._get_unsolved_song_path()
        os.rename(self.root, os.path.join( os.path.dirname(self.root) , self.processor.new_name))# Rename the artist dir name
        log_multiple_data({'\n old paths: \n': self.album_song_dict_path, '\n new paths: \n': new_album_song_dict_path,
                           '\n unsolved path: \n': self.unsolved_song_path})


        
        
artists_editor: list[ArtistFolderEditor] = []

def apply_changes_to_files(path: str) -> list[ArtistFolderEditor]:
    list_editor = []
    try:
        for dir in os.listdir(path):
            if os.path.isdir(os.path.join(path, dir)):
                editor = ArtistFolderEditor(os.path.join(path, dir))
                list_editor.append(editor)
                editor.apply()       
    except Exception as e:
        print(e.args)
    
    global artists_editor; artists_editor = list_editor
    return list_editor

def get_unsolved():
    return [u for i in range(len(artists_editor)) \
            for u in artists_editor[i].unsolved_song_path] \
            if artists_editor else None
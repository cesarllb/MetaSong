import os
import db
from db import get_serialized_dict, save_serialized_dict
from chain import run_chain, RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, \
                                    RemoveSubstrings, CompatibleFormat, RemoveExtension, \
                                    RemoveMultiplesSpaces, RemoveSpaceBeforeExtension
            
class ArtistFolderProcessor:
    NO_ALBUM: str = 'NO ALBUM'
    
    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]

        self.album_song_dict = self._get_album_song_dict()
        self.albums = list(self.album_song_dict.keys())
        self.songs = list([song for album in self.albums for song in self.album_song_dict[album]])
        
        self.new_album_song_dict = self._get_new_album_song_dict()
        self.new_albums = list(self.new_album_song_dict.keys())
        self.new_songs = list([song for album in self.new_albums for song in self.new_album_song_dict[album]])
       
    def _get_album_song_dict(self, db: bool = True):
        album_song_dict = get_serialized_dict(db.DB_OLD, self.name)
        if album_song_dict and db:
            return album_song_dict
        root_files = []
        for elem in os.listdir(self.path):
            elem_path = os.path.join(self.path, elem)
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
    
    def _get_new_album_song_dict(self, db: bool = True):
        '''If it have subfolders/albums it not analyze files in the root/artist path'''
        new_path_dict = get_serialized_dict(db.DB_NEW, self.name)
        if new_path_dict and db:
            return new_path_dict
        list_songs = []
        for album in self.albums:
            new_album_name = run_chain(album, chain = (RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, RemoveMultiplesSpaces)) \
                            if album != self.NO_ALBUM else self.NO_ALBUM
            for song in self.album_song_dict[album]:
                new_file_name = run_chain(song, chain= [CompatibleFormat, RemoveBetweenParenthesis, 
                         BeginsNumber, RemoveSubstrings, RemoveSymbols, RemoveMultiplesSpaces, RemoveSpaceBeforeExtension])
                list_songs.append(new_file_name)
            new_path_dict[new_album_name] = list_songs
        save_serialized_dict(db.DB_NEW, self.name, new_path_dict)
        return new_path_dict

    def refresh(self):
        self.album_song_dict = self._get_album_song_dict(db = False)
        self.new_album_song_dict = self._get_new_album_song_dict(db = False)
    
class ArtistFolderEditor:
    
    def __init__(self, path: str) -> None:
        self.processor = ArtistFolderProcessor(path)
        self.name = self.processor.name
        self.root = self.processor.path
        self.NO_ALBUM = False
        self.albums_path: list = self._get_album_path()
        self.songs_path: list = self._get_songs_path()
        self.unsolved_song_path: list = self._get_unsolved_song_path()
        self.album_song_dict_path: dict = self._get_album_song_dict_path()
        self.new_album_song_dict_path: dict = {}
        
    

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
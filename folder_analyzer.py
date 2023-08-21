import os
import db
from tag import ArtistTag
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
        self.new_album_song_dict, self.new_album_song_dict_with_extensions = self._get_new_album_song_dict()
        self.albums = list(self.album_song_dict.keys())
        self.new_albums = list(self.new_album_song_dict.keys())

        self.songs = list([song for album in list(self.album_song_dict.keys()) for song in self.album_song_dict[album]])
        self.new_songs = list([song for album in list(self.new_album_song_dict.keys()) 
                                    for song in self.new_album_song_dict[album]])
        
       
    def _get_album_song_dict(self):
        album_song_dict = get_serialized_dict(db.PICKLE_DB_OLD, self.name)
        if album_song_dict:
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
            
        save_serialized_dict(db.PICKLE_DB_OLD, self.name, album_song_dict)
        return album_song_dict
    
    def _get_new_album_song_dict(self):
        '''If it have subfolders/albums it not analyze files in the root/artist path'''
        new_album_song_dict = self.db.get_serialized_dict(db.PICKLE_DB_NEW, self.name)
        new_album_song_dict_with_extensions = self.db.get_serialized_dict(db.PICKLE_DB_NEW_EXT, self.name)
        if new_album_song_dict and new_album_song_dict_with_extensions:
            return new_album_song_dict, new_album_song_dict_with_extensions
        else:
            new_album_song_dict, new_album_song_dict_with_extensions = {}, {}
            
        root_folder_done, album_folder_done = False, False
        for elem in os.listdir(self.path):
            elem_path = os.path.join(self.path, elem)
            if os.path.isdir(elem_path):
                processed_file_names, processed_file_names_with_extensions = self._process_files_in_dir(elem_path, chain= [CompatibleFormat, RemoveBetweenParenthesis, 
                         BeginsNumber, RemoveSubstrings, RemoveSymbols, RemoveMultiplesSpaces, RemoveSpaceBeforeExtension])
                processed_album_name = run_chain(elem, chain = (RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, RemoveMultiplesSpaces))
                new_album_song_dict[processed_album_name] = processed_file_names
                new_album_song_dict_with_extensions[processed_album_name] = processed_file_names_with_extensions
                album_folder_done = True
            elif os.path.isfile(elem_path) and not root_folder_done and not album_folder_done:
                processed_file_names, processed_file_names_with_extensions = self._process_files_in_dir(self.path, chain= [CompatibleFormat, RemoveBetweenParenthesis, 
                         BeginsNumber, RemoveSubstrings, RemoveSymbols, RemoveMultiplesSpaces, RemoveSpaceBeforeExtension])
                new_album_song_dict[self.NO_ALBUM] = processed_file_names
                new_album_song_dict_with_extensions[self.NO_ALBUM] = processed_file_names_with_extensions
                root_folder_done = True
                
        save_serialized_dict(db.PICKLE_DB_NEW, self.name, new_album_song_dict)
        save_serialized_dict(db.PICKLE_DB_NEW_EXT, self.name, new_album_song_dict_with_extensions)
        return new_album_song_dict, new_album_song_dict_with_extensions

    def _process_files_in_dir(self, path: str, chain: list):
        '''Process all filenames in a folder with and without extensions'''
        processed_file_names, processed_file_names_with_extensions = [], []
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                processed = run_chain(file, chain = chain, substring= [self.name])
                processed_file_names_with_extensions.append(processed)
                chain_2 = [RemoveExtension]
                processed_file_names.append(run_chain(processed, chain = chain_2) if processed else None)

        return list(filter(None, processed_file_names)), list(filter(None, processed_file_names_with_extensions))

    
class ArtistFolderEditor:
    
    def __init__(self, path: str) -> None:
        self.processor = ArtistFolderProcessor(path)
        self.root = self.processor.path
        self.NO_ALBUM = False
        self.albums_path = self._get_album_path()
        self.songs_path = self._get_songs_path()
        self.unsolved_song_path = self._get_unsolved_song_path()
        self.album_song_dict_path = self._get_new_album_song_dict_path()

    def _get_unsolved_song_path(self):
        unsolved = []
        for song in self.songs_path:
            if not os.path.isfile(song):
                unsolved.append(song)
        return unsolved
    
    def _get_album_path(self):
        albums_path = []
        for a in self.processor.new_albums:
            if a == self.processor.NO_ALBUM:
                albums_path.append(self.root)
                self.NO_ALBUM = True
                break
            else:
                albums_path.append(os.path.join(self.root, a))
        return albums_path

    def _get_songs_path(self):
        songs_path = []
        for album in self.processor.new_albums:
            for song in self.processor.new_album_song_dict_with_extensions[album]:
                if album == self.processor.NO_ALBUM:
                    songs_path.append(os.path.join(self.root, song))
                else:
                    songs_path.append(os.path.join(self.root, album, song))
        return songs_path
    
    def _get_new_album_song_dict_path(self):
        album_song_dict_path = {}
        for album_path in self.albums_path:
            this_album_songs_list = []
            for song_path in self.songs_path:
                song = song_path.split('/')[-1]
                album = album_path.split('/')[-1] if not self.NO_ALBUM else self.processor.NO_ALBUM
                if song in self.processor.new_album_song_dict_with_extensions[album]:
                    this_album_songs_list.append(song_path)
            album_song_dict_path[album_path] = this_album_songs_list
        return album_song_dict_path

    def apply(self) -> dict[ str , list[str]]:
        try:
            for elem in os.listdir(self.root): #loop for artist/root dir
                elem_path = os.path.join(self.root, elem)
                album_path = ''
                if os.path.isdir(elem_path):
                    #Rename the album
                    for album, new_album in zip(self.processor.albums, self.processor.new_albums): #loop for albums
                        if album == elem and album != self.processor.NO_ALBUM:
                            new_album_dir_name = os.path.join(self.root, new_album)
                            os.rename(elem_path, new_album_dir_name)
                            album_path = new_album_dir_name #update the path of the album for later, changes the names of the songs
                    #Change songs name inside the album
                    songs = list([f for f in os.listdir(album_path) if os.path.isfile(os.path.join(album_path, f))]) if album_path else None
                    if songs:
                        for old_song_name in songs:
                            for new_song_path in self.album_song_dict_path[album_path]:
                                new_song_name = new_song_path.split('/')[-1]                              
                                if new_song_name in old_song_name and new_song_name != old_song_name:
                                    os.rename(os.path.join(album_path, old_song_name), new_song_path)
                                    break
                elif os.path.isfile(elem_path) and self.NO_ALBUM:
                    #Rename the outer songs
                    for song_path in self.album_song_dict_path[self.root]:
                        new_song_name = song_path.split('/')[-1]; extension = elem.split('.')[-1]
                        if song_path in elem_path and new_song_name != elem:
                            os.rename(elem_path, os.path.join(self.root, new_song_name, extension))
                            break
        except FileNotFoundError as e:
            print('The file: ', e.filename, ' not found. \n')
        except NotADirectoryError as e:
            print('The dir: ', e.filename, ' error. \n')

        return self.album_song_dict_path
    
class MusicFolder:

    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]
        
        self.artist_editors: list[ArtistFolderEditor] = self._get_artist_list()
        self.artist_names: list[str] = list([a.processor.name for a in self.artist_editors])

        self.artist_tag = self._get_artist_tag()
        self.unsolved_songs_path = [u for i in range(len(self.artist_editors)) for u in self.artist_editors[i].unsolved_song_path]
        
    def _get_artist_tag(self) -> list[ArtistTag]:
        artists_tag = []
        for name, editor in zip(self.artist_names, self.artist_editors):
            artists_tag.append(ArtistTag(name, editor.album_song_dict_path))
        return artists_tag

    def _get_artist_list(self):
        list_artist = []
        for dir in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, dir)):
                list_artist.append(ArtistFolderEditor(os.path.join(self.path, dir)))
        return list_artist
    
    def apply_changes_to_files_and_dirs(self):
        try:
            for editor in self.artist_editors:
                editor.apply()
        except Exception as e:
            print(e.with_traceback())

    def apply_tags(self):
        for tag in self.artist_tag:
            tag.apply_tags_by_dict()

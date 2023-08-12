import os
from chain import chain_naming_run, RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, RemoveSubstrings, CompatibleFormat, RemoveExtension, RemoveMultiplesSpaces


class ArtistFolderProcessor:
    NO_ALBUM: str = str('1')

    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]

        self.album_song_dict = self._get_album_song_dict()
        self.fixed_album_song_dict, self.fixed_album_song_dict_with_extensions = self._get_fixed_album_song_dict()
        self.albums = list(self.album_song_dict.keys())
        self.fixed_albums = list(self.fixed_album_song_dict.keys())

        self.songs = list([song for album in self.albums for song in self.album_song_dict[album]])
        self.fixed_songs = list([song for album in self.fixed_albums for song in self.fixed_album_song_dict[album]])

    def _get_album_song_dict(self):
        album_song_dict = {}
        root_files = []
        for elem in os.listdir(self.path):
            elem_path = os.path.join(self.path, elem)
            if os.path.isdir(elem_path):
                album_song_dict[elem] = list([f for f in os.listdir(elem_path) if os.path.isfile(os.path.join(elem_path, f))])
            elif os.path.isfile(elem_path):
                 root_files.append(elem)
        if root_files:
            album_song_dict[self.NO_ALBUM] = root_files
        return album_song_dict
    
    def _get_fixed_album_song_dict(self):
        fixed_album_song_dict, fixed_album_song_dict_with_extensions = {}, {}
        root_folder_done = False
        for elem in os.listdir(self.path):
            elem_path = os.path.join(self.path, elem)
            if os.path.isdir(elem_path):
                processed_file_names, processed_file_names_with_extensions = self._process_dir_files(elem_path)
                processed_album_name = chain_naming_run(elem, chain = (RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, RemoveMultiplesSpaces))
                fixed_album_song_dict[processed_album_name] = processed_file_names
                fixed_album_song_dict_with_extensions[processed_album_name] = processed_file_names_with_extensions
            elif os.path.isfile(elem_path) and not root_folder_done:
                processed_file_names, processed_file_names_with_extensions = self._process_dir_files(self.path)
                fixed_album_song_dict[self.NO_ALBUM] = processed_file_names
                fixed_album_song_dict_with_extensions[self.NO_ALBUM] = processed_file_names_with_extensions
                root_folder_done = True

        return fixed_album_song_dict, fixed_album_song_dict_with_extensions

    def _process_dir_files(self, path: str):
        '''Process all filenames in a folder with and without extensions'''
        processed_file_names, processed_file_names_with_extensions = [], []
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                chain = [CompatibleFormat, RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber, RemoveSubstrings, RemoveMultiplesSpaces]
                processed = chain_naming_run(file, chain = chain, substring= [self.name])
                processed_file_names_with_extensions.append(processed)
                chain_2 = [RemoveExtension]
                processed_file_names.append(chain_naming_run(processed, chain = chain_2) if processed else None)

        return list(filter(None, processed_file_names)), list(filter(None, processed_file_names_with_extensions))

    
class ArtistFolderEditor:
    
    def __init__(self, processor: ArtistFolderProcessor) -> None:
        self.processor = processor
        self.path = processor.path
        self.albums_path = self._get_album_path()
        self.songs_path = self._get_songs_path()
        self.album_song_dict_path = self._get_fixed_album_song_dict_path()

    def _get_album_path(self):
        albums_path = []
        for a in self.processor.fixed_albums:
            if a == self.processor.NO_ALBUM:
                albums_path.append(self.path)
            else:
                albums_path.append(self.path + '/' + a)
        return albums_path

    def _get_songs_path(self):
        songs_path = []
        for album in self.processor.fixed_albums:
            for song in self.processor.fixed_album_song_dict_with_extensions[album]:
                if album == self.processor.NO_ALBUM:
                    songs_path.append(self.path + '/' + song)
                else:
                    songs_path.append(self.path + '/' + album + '/' + song)
        return songs_path
    
    def _get_fixed_album_song_dict_path(self):
        album_song_dict_path = {}
        for album_path in self.albums_path:
            this_album_songs_list = []
            for song_path in self.songs_path:
                song = song_path.split('/')[-1]
                album = album_path.split('/')[-1]
                plapla = song_path.split('/')[-2]
                if self.processor.albums[0] == self.processor.NO_ALBUM:
                    '''This if checks if there is no album, therefore the album is the same that the artist'''

                    if song in self.processor.fixed_album_song_dict_with_extensions[self.processor.NO_ALBUM]:
                        this_album_songs_list.append(song_path)
                else:
                    if song in self.processor.fixed_album_song_dict_with_extensions[album]:
                        this_album_songs_list.append(song_path)
            album_song_dict_path[album_path] = this_album_songs_list
        return album_song_dict_path

    def apply(self) -> dict[ str , list[str]]:
        try:
            for elem in os.listdir(self.path):
                elem_path = os.path.join(self.path, elem)
                if os.path.isdir(elem_path):
                    #Rename the album
                    for album, fixed in zip(self.processor.albums, self.processor.fixed_albums):
                        ppe = False
                        if album == elem and fixed != self.processor.NO_ALBUM:
                            os.rename(elem_path, os.path.join(self.path, fixed))
                            elem_path = os.path.join(self.path, fixed)
                    #Change files inside the album
                    files = list([f for f in os.listdir(elem_path) if os.path.isfile(os.path.join(elem_path, f))])
                    if files:
                        for filename in files:
                            fixed_song_name = [a for a in self.processor.fixed_songs if a in filename]
                            if len(fixed_song_name) == 1:
                                new_song_name = fixed_song_name[0]  + '.' + filename.split('.')[-1]
                                if filename != new_song_name:
                                    os.rename(os.path.join(elem_path, filename), os.path.join(elem_path, new_song_name))
                elif os.path.isfile(elem_path):
                    fixed_song_name = [s for s in self.processor.fixed_songs if s in elem]
                    if len(fixed_song_name) == 1:
                        new_song_name = self.path + '/' + fixed_song_name[0] + '.' + elem.split('.')[-1]
                        os.rename(elem_path, new_song_name)
        except FileNotFoundError as e:
            print('The file: ', e.filename, ' not found. \n')
        except NotADirectoryError as e:
            print('The dir: ', e.filename, ' error. \n')

        return self.album_song_dict_path
    
class MusicFolder:

    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]
        
        self.artist_processors: list[ArtistFolderProcessor] = self._get_artist_list()
        self.artist_names: list[str] = list([a.name for a in self.artist_processors])

    def _get_artist_list(self):
        list_artist = []
        for dir in os.listdir(self.path):
            if os.path.isdir(self.path + '/' + dir):
                list_artist.append(ArtistFolderProcessor(self.path + '/' + dir))
        return list_artist
    
    def apply(self):
        try:
            for artist_analyzer in self.artist_processors:
                editor = ArtistFolderEditor(artist_analyzer)
                editor.apply()
        except Exception as e:
            print(e)

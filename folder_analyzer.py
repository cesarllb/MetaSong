import os
import itertools
from chain import chain_naming_run, RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber


class ArtistFolderAnalyzer:

    def __init__(self, path:str):
        self.path = path
        self.artist = path.split('/')[-1]

        self.album_song_dict = self._get_album_song_dict()
        self.fixed_album_song_dict = self._get_fixed_album_song_dict()

        self.albums = list(self.album_song_dict.keys())
        self.fixed_albums = list(self.fixed_album_song_dict.keys())

        self.songs = list([song for album in self.albums for song in self.album_song_dict[album]])
        self.fixed_songs = list([song for album in self.fixed_albums for song in self.fixed_album_song_dict[album]])

    def _get_album_song_dict(self):
        album_song_dict = {}
        iter = itertools.count(0,1)
        for root, dirs, files in os.walk(self.path):
            if files:
                if root:
                    root_dir = root.split('/')[-1]
                    album_song_dict[root_dir] = files
                else:
                    album_song_dict[str(iter.__next__())] = files

        return album_song_dict
    
    def _get_fixed_album_song_dict(self):
        fixed_album_song_dict = {}
        iter = itertools.count(0,1)
        for root, _, files in os.walk(self.path):
            if files:
                # processed_files_names = list( [chain_naming_run(file, [self.artist]) for file in files] )
                processed_files_names = list([chain_naming_run(file, [self.artist]) for file in files])

                # processed_files_names = list(map(chain_naming_run, files))

                processed_files_names = list(filter(None, processed_files_names))
                if root:
                    root_dir = root.split('/')[-1]
                    root_processed_name = chain_naming_run(root_dir, chain= (RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber))
                    fixed_album_song_dict[root_processed_name] = processed_files_names
                else:
                    fixed_album_song_dict[str(iter.__next__())] = processed_files_names

        return fixed_album_song_dict

    
class ArtistFolderEditor:
    
    def __init__(self, analyzer: ArtistFolderAnalyzer) -> None:
        self.analyzer = analyzer
        self.path = analyzer.path
        self.albums_path = list([path + '/' + a for a in self.analyzer.fixed_albums]) 
        self.songs_path = list([path + '/' + album + '/' + song \
                                for album in self.analyzer.fixed_albums \
                                for song in self.analyzer.fixed_album_song_dict[album]])
        self.album_song_dict_path = self._get_fixed_album_song_dict_path()

    def _get_fixed_album_song_dict_path(self):
        album_song_dict_path = {}
        for album_path in self.albums_path:
            this_album_songs_list = []
            for song_path in self.songs_path:
                song = song_path.split('/')[-1]
                album = album_path.split('/')[-1]
                if song in self.analyzer.fixed_album_song_dict[album]:
                     this_album_songs_list.append(song_path)
            album_song_dict_path[album_path] = this_album_songs_list
        return album_song_dict_path

    def apply(self) -> dict[ str , list[str]]:
        for root, dirs, files in os.walk(self.path):
            if files:
                for filename in files:
                    aux = [a for a in self.songs if a in filename]
                    if len(aux):
                        new_song_name = aux[0]  + '.' + filename.split('.')[-1]
                        if filename != new_song_name:
                            os.rename(os.path.join(root, filename), os.path.join(root, new_song_name))
            if dirs:
                for dirname in dirs:
                    aux = [a for a in self.albums if a in dirname]
                    if len(aux):
                        new_album_name = aux[0]
                        if dirname != new_album_name:
                            os.rename(os.path.join(root, dirname), os.path.join(root, new_album_name))
        return self.album_song_dict_path
    
class MusicFolder:

    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]
        
        self.list_artist: list[ArtistFolderAnalyzer] = self._get_artist_list()
        self.artist_names: list[str] = list([a.artist for a in self.list_artist])

    def _get_artist_list(self):
        list_artist = []
        for dir in os.listdir(self.path):
            if os.path.isdir(self.path + '/' + dir):
                list_artist.append(ArtistFolderAnalyzer(self.path + '/' + dir))
        return list_artist
    
    def apply(self):
        try:
            for artist_analyzer in self.list_artist:
                editor = ArtistFolderEditor(artist_analyzer)
                editor.apply()
        except Exception as e:
            print(e)

from pprint import pprint



# a = MusicFolderAnalyzer('/media/cesarlinares/08050A6608050A66/Música')
# print(a.artist_names)

path = ArtistFolderAnalyzer('/media/cesarlinares/08050A6608050A66/Música/Motionless_in_Withe')
# path.update_songs(['Without Walls.mp3', 'Alive In The Lights.mp3', 'Prove Me Right.mp3', 'Red In Tooth & Claw.mp3'])
pprint(path.fixed_album_song_dict)
# pprint(len(path.list_artist))
# pprint(path.fixed_songs)
# path.edit_music_files_name()


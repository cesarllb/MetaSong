import os
import re
# import music_tag
# import musicbrainzngs
from abc import ABC, abstractmethod


class NamingInterface(ABC):

    @abstractmethod
    def handle(name:str):
        ...
    
    @abstractmethod
    def set_next(self, next) -> None:
        ...

class BaseNaming(NamingInterface):
    next: NamingInterface = None
    def set_next(self, next: NamingInterface) -> None:
        self.next = next

class CompatibleFormat(BaseNaming):
    compatible_format = ('mp3', 'm4a', 'flac', 'wav', 'aac', 'ogg')
    def handle(self, name:str) -> str:
        return_name = ''
        splitted = name.split('.')
        if splitted[-1] in self.compatible_format:
            return_name = ''.join(splitted[:-1]).strip()

        return self.next.handle(return_name) if self.next and return_name else None

class BeginsNumber(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        for i in range(len(name)):
            if not name[i].isdigit():
                return_name = name[i:].strip()
                break
            else:
                return_name = name
            
        return self.next.handle(return_name) if self.next else return_name
    
class RemoveBetweenParenthesis(BaseNaming):
    def handle(self, name:str) -> str:
        def find_parenthesis(return_name, symbols = (('(', ')'), ('[', ']'), ('{', '}'))):
            for i, s in enumerate(symbols):
                first = return_name.find(s[0])
                last = return_name.find(s[1])
                if last != -1:
                    while True:
                        if last < len(return_name) - 1:
                            from_last_to_end:str = return_name[last+1:]
                            if from_last_to_end[0] == s[1]:
                                last +=1
                            else:
                                break
                        else:
                            break
                if first != -1 and last != -1:
                    return_name = (return_name[:first].strip() + ' ' + return_name[last+1:].strip()).strip()

            recursive = False
            #check if there is another open parenthesis and go recursive
            recursive = [True for i in range(len(symbols)) if return_name.find(symbols[i][0]) != -1 and return_name.find(symbols[i][1]) != -1]

            return find_parenthesis(return_name, symbols) if recursive else return_name

        return_name = find_parenthesis(name)
        return self.next.handle(return_name) if self.next else return_name
    
aux = RemoveBetweenParenthesis()
print(aux.handle('Rock Down 13 (((Acesse)))'))

class RemoveSymbols(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        if bool(re.search(r'[^\w\s]', name)):
            return_name = re.sub(r'(?<!\w)(?!\s)[^\w\s]+(?<!\s)(?!\w)', '', name).strip()
        else:
            return_name = name

        return self.next.handle(return_name) if self.next else return_name
    

def chain_naming_run(name:str, 
                     chain: tuple = (CompatibleFormat ,RemoveBetweenParenthesis ,RemoveSymbols , BeginsNumber)) -> str:
    list_chain = []
    for i, ch in enumerate(chain):
        ch_obj = ch()
        list_chain.append(ch_obj)
        if i > 0:
            list_chain[i-1].set_next(ch_obj)

    return list_chain[0].handle(name)


class ArtistFolderAnalyzer:

    def __init__(self, path:str):
        self.path = path
        self.album_song_dict: dict = self._get_album_song_dict()
        self.fixed_album_song_dict = self._get_fixed_album_song_dict()
        self.files: list = self._get_files()

        self.albums = list(self.album_song_dict.keys())
        self.fixed_albums = list(self.fixed_album_song_dict.keys())
        self.fixed_albums_path = list([path + '/' + a for a in self.albums]) 

        self.songs = list([song for album in self.albums for song in self.album_song_dict[album]])
        self.fixed_songs = list([song for album in self.fixed_albums for song in self.fixed_album_song_dict[album]])
        self.fixed_songs_path = list([[path + '/' + album + '/' + \
                                       song for album in self.fixed_albums for song in self.fixed_album_song_dict[album]]])

    def _get_album_song_dict(self):
        album_song_dict = {}
        for root, dirs, files in os.walk(self.path):
            if files:
                root_dir = root.split('/')[-1]
                album_song_dict[root_dir] = files

        return album_song_dict
    
    def _get_fixed_album_song_dict(self):
        fixed_album_song_dict = {}
        for root, dirs, files in os.walk(self.path):
            if files:
                processed_files_names = list(map(chain_naming_run, files))
                processed_files_names = list(filter(None, processed_files_names))
                root_dir = root.split('/')[-1]
                root_processed_name = chain_naming_run(root_dir, (RemoveBetweenParenthesis, RemoveSymbols, BeginsNumber))
                fixed_album_song_dict[root_processed_name] = processed_files_names

        return fixed_album_song_dict
    
    def edit_music_files_name(self):
        for root, dirs, files in os.walk(self.path):
            if files:
                for filename in files:
                    if isinstance(filename, str):
                        aux = [a for a in self.songs if a in filename]
                        if len(aux) > 0:
                            new_song_name = aux[0]  + '.' + filename.split('.')[-1]
                            if filename != new_song_name:
                                os.rename(os.path.join(root, filename), os.path.join(root, new_song_name))
            if dirs:
                for dirname in dirs:
                    if isinstance(dirname, str):
                        aux_1 = [a for a in self.albums if a in dirname]
                        if len(aux_1) > 0:
                            new_album_name = aux_1[0]
                            if dirname != new_album_name:
                                os.rename(os.path.join(root, dirname), os.path.join(root, new_album_name))
        return self._get_album_song_dict()
    
    def _get_files(self):
        files = []
        for root, dirs, files in os.walk(self.path):
            if files:
                for filename in files:
                    if isinstance(filename, str):
                        with open(os.path.join(root, filename), 'rb') as f:
                            files.append(f.read())
        return files
    
    def update_songs(self, songs: list) -> list:
        self.songs = songs
        for k in self.album_song_dict.keys():
            for i, _ in enumerate(self.album_song_dict[k]):
                for s in songs:
                    if s in self.album_song_dict[k][i]:
                        self.album_song_dict[k][i] = s
        return self.album_song_dict

# class MusicTag:
#     def __init__(self)
    
from pprint import pprint

path = ArtistFolderAnalyzer('/media/cesarlinares/08050A6608050A66/Música/Motionless_in_Withe (copia)')
# path.update_songs(['Without Walls.mp3', 'Alive In The Lights.mp3', 'Prove Me Right.mp3', 'Red In Tooth & Claw.mp3'])
# pprint(path.album_song_dict)
pprint(path.fixed_songs_path)
# pprint(path.songs)
# path.edit_music_files_name()


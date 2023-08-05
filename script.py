import os
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
        if name.split('.')[-1] in self.compatible_format:
            return_name = name.split('.')[:-1]
        return self.next.handle(return_name) if self.next else return_name

class BeginsNumber(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        for i in range(len(name)):
            if not name[0][i].isdigit():
                return_name = name[i:]
                break
            
        return self.next.handle(return_name) if self.next else return_name


class RemoveSymbols(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        for char in name:
            if not char.isalpha():
                return_name = name.replace(char, '')
        
        return self.next.handle(return_name) if self.next else return_name

chain: tuple = (CompatibleFormat, BeginsNumber, RemoveSymbols)
    
def chain_naming_run(name:str) -> str:
    first_chain: NamingInterface = None
    def run(chain_list: tuple) -> NamingInterface:

        if len(chain_list) == 1:
            return chain_list[0]
        
        if len(chain_list) == len(chain):
            nonlocal first_chain 
            first_chain = chain_list[0]()
        chain_obj = chain_list[0]()


        chain_obj.set_next( run( chain_list[1:] ) )
        return chain_obj
    
    run(chain)
    return first_chain.handle(name)


class ArtistFolderAnalyzer:

    def __init__(self, path:str):
        self.album_song_dict: dict = self._get_album_song_dict(path)
        self.files: list = self._get_files(path)
        self.albums = list(self.album_song_dict.keys())
        self.songs = list(self.album_song_dict.values())

    def _get_album_song_dict(self, path:str):
        album_song_dict = {}
        for root, dirs, files in os.walk(path):
            if files:
                processed_files_names = [chain_naming_run(f) for f in files]
                root = root.split('/')[-1]
                album_song_dict[root] = processed_files_names

        return album_song_dict
    
    def _get_files(self, path: str):
        files = []
        for root, dirs, files in os.walk(path):
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

    


path = ArtistFolderAnalyzer('/media/cesarlinares/08050A6608050A66/Música/Memphis_may_Fire')
# print(path.album_song_dict)
# path.update_songs(['Without Walls.mp3', 'Alive In The Lights.mp3', 'Prove Me Right.mp3', 'Red In Tooth & Claw.mp3'])
print(path.album_song_dict)


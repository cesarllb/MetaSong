import os


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
                root = root.split('/')[-1]
                album_song_dict[root] = files

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

    def update_albums(self, albums: list) -> list:
        self.albums = albums
        for k in self.album_song_dict.keys():
            for a in albums:
                if a in self.album_song_dict[k][i]:
                    self.album_song_dict[k][i] = s
        return self.album_song_dict
    


path = ArtistFolderAnalyzer('/media/cesarlinares/08050A6608050A66/Música/Memphis_may_Fire')
# print(path.album_song_dict)
path.update_songs(['Without Walls.mp3', 'Alive In The Lights.mp3', 'Prove Me Right.mp3', 'Red In Tooth & Claw.mp3'])
# print(path.album_song_dict)


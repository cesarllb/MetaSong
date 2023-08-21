import os
import music_tag

class SongTag:
    TITLE, ARTIST, ALBUM = 1, 2, 3

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]
        self.song_tag = music_tag.load_file(self.path)
    
    def set_tag(self, type: str | int, value: str, save: bool = False) -> None:
        if type == SongTag.TITLE:
            self.song_tag['title'] = value
        elif type == SongTag.ARTIST:
            self.song_tag['artist'] = value
        elif type == SongTag.ALBUM:
            self.song_tag['album'] = value
        elif isinstance(type, str):
            self.song_tag[type] = value
        if save:
            self.song_tag.save()

    def save(self):
        self.song_tag.save()

class AlbumTag:

    def __init__(self, path, songs_path: list):
        self.path = path
        self.album_name = path.split('/')[-1]
        self.artist_name = path.split('/')[-2]
        self.songs_path = [s for s in songs_path if os.path.isfile(s)]
        self.songs_tag = self._get_album_song_tag_list()

    def _get_album_song_tag_list(self) -> list[SongTag]:
        list_of_songs_tag = []
        for path in self.songs_path:
            list_of_songs_tag.append(SongTag(path))
        return list_of_songs_tag

    def set_songs_tag_by_type(self, type: str | int, 
                              values: list[str], 
                              save: bool = False) -> None:
        
        if len(values) == len(self.songs_tag):
            for i, song_tag in enumerate(self.songs_tag):
                song_tag.set_tag(type, values[i])
                if save:
                    song_tag.save()
        else:
            raise Exception('Values length is not equal to songs length')
        
    def save(self):
        for song_tag in self.songs_tag:
            song_tag.save()
        
    def set_song_tag_by_name(self, type: str | int, 
                             song_name: str, 
                             value: str, 
                             save: bool = False) -> None:
        
        for song_tag in self.songs_tag:
            if song_tag.song_name == song_name:
                song_tag.set_tag(type, value)
                if save:
                    song_tag.save()
                break

class ArtistTag:
    def __init__(self, name: str, album_song_dict_path: dict) -> None:
        self.name = name
        self.album_song_dict_path = album_song_dict_path
        self.albums_tag = self._get_albums_tag()

    def _get_albums_tag(self) -> list[AlbumTag]:
        list_albums_tag = []
        for album_path in self.album_song_dict_path:
            if os.path.isdir(album_path):
                list_albums_tag.append(AlbumTag(album_path, self.album_song_dict_path[album_path]))
        return list_albums_tag
    
    def apply_tags_by_dict(self):
        for album in self.albums_tag:
            #Set tags to all song
            self.set_tags_to_songs(SongTag.ALBUM, album)
            self.set_tags_to_songs(SongTag.ARTIST, album)
            self.set_tags_to_songs(SongTag.TITLE, album)

    def set_tags_to_songs(self, type: int, album_tag: AlbumTag):
        album_len = len(album_tag.songs_tag)
        if type in (1, 2, 3):
            if type == SongTag.ALBUM:
                values = [album_tag.album_name] * album_len
            elif type == SongTag.ARTIST:
                values = [album_tag.artist_name] * album_len
            elif type == SongTag.TITLE:
                values = [album_tag.songs_tag[i].name for i in range(album_len)]
            
            album_tag.set_songs_tag_by_type(type, values)
            album_tag.save()


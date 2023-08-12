# import musicbrainzngs as music
import music_tag

class SongTag:
    TITLE, ARTIST, ALBUM = 1, 2, 3

    def __init__(self, path, filetype = {'mp3', 'm4a', 'flac', 'wav', 'aac', 'ogg'}):
        self.path = path
        self.name = path.split('/')[-1]
        # music_tag.register_filetype_extensions(filetype)
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
        self.songs_path = songs_path
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
    
    def apply_tags_by_dict(self):
        for album_path in self.album_song_dict_path:
            album_tag_obj = AlbumTag(album_path, self.album_song_dict_path[album_path])
            #Set tags to all song
            self.set_tags_to_songs(SongTag.ALBUM, album_tag_obj)
            self.set_tags_to_songs(SongTag.ARTIST, album_tag_obj)
            self.set_tags_to_songs(SongTag.TITLE, album_tag_obj)

    def set_tags_to_songs(self, type: int, album_tag_obj: AlbumTag):
        album_len = len(self.album_song_dict_path[album_tag_obj.path])
        if type in (1, 2, 3):
            if type == SongTag.ALBUM:
                values = [album_tag_obj.album_name] * album_len
            elif type == SongTag.ARTIST:
                values = [album_tag_obj.artist_name] * album_len
            elif type == SongTag.TITLE:
                values = [album_tag_obj.songs_tag[i].name for i in range(album_len)]
            
            album_tag_obj.set_songs_tag_by_type(type, values)
            album_tag_obj.save()


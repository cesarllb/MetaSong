
import musicbrainzngs as music
import music_tag

class SongTag:
    TITLE, ARTIST, ALBUM = 1, 2, 3

    def __init__(self, path, filetype = {'mp3', 'm4a', 'flac', 'wav', 'aac', 'ogg'}):
        self.path = path
        self.song_name = path.split('/')[-1]
        music_tag.register_filetype_extensions(filetype)
        self.song_tag = music_tag.load_file(self.path)

    
    def set_tag(self, type: str | int, value: str, save: bool = False) -> None:
        if type == SongTag.TITLE:
            self.metadata['title'] = value
        elif type == SongTag.ARTIST:
            self.metadata['artist'] = value
        elif type == SongTag.ALBUM:
            self.metadata['album'] = value
        elif isinstance(type, str):
            self.metadata[type] = value
        if save:
            self.metadata.save()

    def save(self):
        self.metadata.save()

class AlbumTag:

    def __init__(self, name, songs_path: list):
        self.name = name
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
        
        if len(values) != len(self.songs_tag):
            for i, song_tag in enumerate(self.songs_tag):
                song_tag.set_tag(type, values[i])
                if save:
                    song_tag.save()
        else:
            raise Exception('Values length is not equal to songs length')
        
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

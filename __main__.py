from pprint import pprint
from folder_analyzer import MusicFolder



if __name__ == '__main__':
    a = MusicFolder('/media/cesarlinares/08050A6608050A66/Música/test')
    a.apply_changes_to_files_and_dirs()
    a.apply_tags()
    for a in a.artist_editors:
        # pprint(a.processor.album_song_dict)
        pprint(a.processor.new_album_song_dict)
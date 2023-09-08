import os
import shutil
import asyncio
from tag import apply_tags
from db import get_serialized_dict
from folder_analyzer import apply_changes_to_files, get_unsolved, ArtistFolderEditor

root = '/run/media/cesarlinares/08050A6608050A66/Música/test'

class MusicFolder:

    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]
        self.artist_editors: list[ArtistFolderEditor] = apply_changes_to_files(path)
        self.artist_names = list([ a_editor.name for a_editor in self.artist_editors ])
        self.unsolved_songs_path = get_unsolved()
        
    async def apply_all_tags(self, use_api: bool = False):
        await apply_tags(names = self.artist_names, api= use_api)


def restart(list_artist = ['Five_finger_death_punch', 'Nickelback', 'Led Zeppelin - Essentials']):
    if os.path.exists(os.path.join(os.curdir, 'db')):
        shutil.rmtree(os.path.join(os.curdir, 'db'))
    if os.path.exists(os.path.join(os.curdir, 'log')):
        shutil.rmtree(os.path.join(os.curdir, 'log'))
    base = os.path.dirname(root)
    test_path = os.path.join(base, 'test')
    if os.path.isdir(test_path):
        shutil.rmtree(test_path)
    for a in list_artist:
        artist_path = os.path.join(base, a)
        if os.path.exists(artist_path):
            shutil.copytree(artist_path, os.path.join(test_path, a))


if __name__ == '__main__':
    # restart() # si ejecuto con el restart activado, no se crean bien las bases de dato
    a = MusicFolder(root)
    asyncio.run( a.apply_all_tags(use_api = False) )

    # pprint(get_serialized_dict(db.DB_OLD, a.artist_names[0]))
    # pprint(get_serialized_dict(db.DB_NEW, a.artist_names[0]))
    # for a in a.artist_editors:
    #     pprint('Old: ')
    #     pprint(a.processor.album_song_dict, width=160)
    #     pprint('New: ')
    #     pprint(a.processor.new_album_song_dict, width=160)
    #     # pprint(a.processor.albums)
    #     # pprint('New: ')
    #     # pprint(a.processor.new_albums)
    #     # pprint(a.unsolved_song_path, width=160)

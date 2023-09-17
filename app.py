import os
import shutil
import asyncio
from code.tag import apply_tags
from code.files_editor import initialize_editors, apply_changes_to_files, get_unsolved, ArtistFolderEditor

root = '/run/media/cesarlinares/08050A6608050A66/Música/test'

class MusicFolder:

    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]
        self.artist_editors: list[ArtistFolderEditor] = initialize_editors(self.path)
        self.artist_names = list([ a_editor.name for a_editor in self.artist_editors ])
        
    def apply_to_files(self):
        apply_changes_to_files(self.artist_editors)
        
    def add_new_artist_path(self, path: str):
        self.artist_editors.append(ArtistFolderEditor(path))
        
    def add_new_dir_of_artist(self, path: str):
        editors: list[ArtistFolderEditor] = initialize_editors(path)
        for e in editors:
            self.artist_editors.append(e)
        
    def get_unsolved(self):
        return get_unsolved(self.artist_editors)

    async def apply_all_tags(self, use_api: bool = False, covers: bool = False):
        await apply_tags(names = self.artist_names, api= use_api, covers= covers)
    
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
    restart()
    a = MusicFolder(root)
    a.apply_to_files()
    asyncio.run( a.apply_all_tags( use_api = False, covers= True) )
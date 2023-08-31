import asyncio
from pprint import pprint
from tag import apply_tags
from folder_analyzer import apply_changes_to_files, get_unsolved, ArtistFolderEditor

class MusicFolder:

    def __init__(self, path:str):
        self.path = path
        self.name = path.split('/')[-1]
        self.artist_editors: list[ArtistFolderEditor] = apply_changes_to_files(path)
        self.artist_names = list([ a_editor.name for a_editor in self.artist_editors ])
        self.unsolved_songs_path = get_unsolved()
        
    async def apply_all_tags(self, use_api: bool = False):
        await apply_tags(names = self.artist_names, api= use_api)
            

if __name__ == '__main__':
    a = MusicFolder('/run/media/cesarlinares/08050A6608050A66/Música/test')
    asyncio.run( a.apply_all_tags(use_api = True) )
    
    for a in a.artist_editors:
        pprint('Old: ')
        pprint(a.processor.album_song_dict, width=160)
        pprint('New: ')
        pprint(a.processor.new_album_song_dict, width=160)
        # pprint(a.processor.albums)
        # pprint('New: ')
        # pprint(a.processor.new_albums)
        # pprint(a.unsolved_song_path, width=160)
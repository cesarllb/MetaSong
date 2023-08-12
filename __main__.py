from pprint import pprint
from folder_analyzer import MusicFolder, ArtistFolderEditor
from tag import ArtistTag



if __name__ == '__main__':
    a = MusicFolder('/media/cesarlinares/08050A6608050A66/Música/test')
    # for a in a.artist_processors:
    #     pprint(a.fixed_album_song_dict)
        # if 'Beatles' in a.name:
        #     aux = ArtistFolderEditor(a)
        #     print(aux.album_song_dict_path)
    artist_tag_list = []
    for a in a.artist_processors:
        folder_editor = ArtistFolderEditor(a)
        # pprint(folder_editor.processor.fixed_album_song_dict_with_extensions)
        folder_editor.apply()
        artist_tag = ArtistTag(a.name, folder_editor.album_song_dict_path)
        # artist_tag_list.append(artist_tag)
        artist_tag.apply_tags_by_dict()
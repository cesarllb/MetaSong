import os
import pickle


PICKLE_DB_OLD, PICKLE_DB_NEW, PICKLE_DB_NEW_EXT = 'old', 'new', 'ext'
    
def get_serialized_dict(type: str, name: str):
    '''Type hint: 
        album_song_dict: old
        new_album_song_dict: new
        new_album_song_dict_with_extensions: ext
        album_song_dict_path: path'''

    name = name.replace(" ","_").lower()
    pickle_db_path = os.path.join(os.path.curdir, 'db', name, f'{type}.pickle')
    if os.path.exists(pickle_db_path):
        with open(pickle_db_path, 'rb') as handle:
            pickle_dict: dict = pickle.load(handle)
            return pickle_dict
    else:
        return {}
        
def save_serialized_dict(type: str, name: str, dict_to_save: dict) -> bool:
    '''Type hint: 
        album_song_dict: old
        new_album_song_dict: new
        new_album_song_dict_with_extensions: ext
        album_song_dict_path: path'''
        
    name = name.replace(" ","_").lower()
    pickle_db_path = os.path.join(os.path.curdir, 'db', name, f'{type}.pickle')
    if not os.path.exists(pickle_db_path):
        with open(pickle_db_path, 'wb') as handle:
            pickle.dump(dict_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)
            return True
    else:
        return False
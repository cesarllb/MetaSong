import os
import pickle

DB_OLD, DB_NEW, DB_PATH = 'old', 'new', 'path',
    
def get_serialized_dict(type: str, name: str):
    '''Type hint: 
        album_song_dict: old
        new_album_song_dict: new
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
        album_song_dict_path: path'''

    name = name.replace(" ","_").lower()
    pickle_db_path = os.path.join(os.path.curdir, 'db', name, f'{type}.pickle')
    if not os.path.exists(pickle_db_path):
        os.makedirs( os.path.join(os.path.curdir, 'db', name), exist_ok = True )
        with open(pickle_db_path, 'wb', ) as handle:
            pickle.dump(dict_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)
            return True
    else:
        return False
    
def update_db(old_name: str, new_name: str):
    old_name, new_name = old_name.replace(" ","_").lower(), new_name.replace(" ","_").lower()
    
    old_name_path = os.path.join(os.path.curdir, 'db', old_name)
    new_name_path = os.path.join(os.path.curdir, 'db', new_name)
    if os.path.exists(old_name_path):
        if old_name != new_name:
            os.rename(old_name_path, new_name_path)
    else:
        raise FileNotFoundError()
    
def update_serialized_dict(type: str, name: str, dict_to_save: dict) -> dict:
    '''Type hint: 
        album_song_dict: old
        new_album_song_dict: new
        album_song_dict_path: path'''
        
    name = name.replace(" ","_").lower()
    pickle_db_path = os.path.join(os.path.curdir, 'db', name, f'{type}.pickle')
    if os.path.exists(pickle_db_path):
        os.remove(pickle_db_path)
        with open(pickle_db_path, 'wb', ) as handle:
            pickle.dump(dict_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)
            return dict_to_save
    else:
        return None
    
def remove_serialized_dict(type: str, name: str) -> bool:
    '''Type hint: 
        album_song_dict: old
        new_album_song_dict: new
        album_song_dict_path: path'''
        
    name =  name.replace(" ", "_").lower()
    pickle_db_path = os.path.join(os.path.curdir, 'db', name, f'{type}.pickle')
    if os.path.exists(pickle_db_path):
        os.remove(pickle_db_path)
        return True
    return False
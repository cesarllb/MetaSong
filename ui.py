import asyncio
import streamlit as st
from app import MusicFolder

def initialize_music_folder(path: str) -> MusicFolder:
    st.session_state.mf = MusicFolder(path)

def apply_names():
    if 'mf' in st.session_state:
        st.session_state.mf.apply_to_files()
    else:
        st.write('Introduce el directorio a analizar primero')

def apply_tags(use_api: bool):
    if 'mf' in st.session_state:
        asyncio.run( st.session_state.mf.apply_all_tags(use_api) )
    else:
        st.write('Introduce el directorio a analizar primero.')

button_col1, button_col2, button_col3 = st.columns(3)
path = st.text_input("Introduce el path")
button_col1.button('Escanear path', on_click=initialize_music_folder, args=(path,))
button_col2.button("Aplicar nombres", on_click=apply_names)
use_api = st.checkbox("Usar datos online")
button_col3.button("Aplicar etiquetas", on_click=apply_tags, args=(use_api,))

col1, col2 = st.columns(2)

if 'mf' in st.session_state:
    col1.header("Directorio de música:")
    col2.header("Propuesta de edición:")

    mf = st.session_state.mf
    for artist_editor in mf.artist_editors:
        processor = artist_editor.processor
        col1.subheader(artist_editor.processor.name); col2.subheader(artist_editor.processor.name)
        for old_album, new_album in zip(processor.album_song_dict, processor.new_album_song_dict):
            col1.write(f'*{old_album}*'); col2.write(f'*{new_album}*')
            for old_song, new_song in zip(processor.album_song_dict[old_album], processor.new_album_song_dict[new_album]):
                col1.write('  ' + old_song); col2.write('  ' + new_song)

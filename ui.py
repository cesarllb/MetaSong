import asyncio
import streamlit as st
from app import MusicFolder
import streamlit_scrollable_textbox as stb

st.set_page_config(page_title='Music Metadata Processor', layout="wide")

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

def get_artist_info(dict_info: dict) -> str:
    long_text = []
    for album in dict_info:
        if album != 'NO ALBUM': 
            long_text.append(f'{album} \n')
        for song in dict_info[album]:
            long_text.append(f' - {song} \n')
    return "".join(long_text)

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
    for i, artist_editor in enumerate(mf.artist_editors):
        processor = artist_editor.processor
        with col1:
            col1.subheader(artist_editor.name)
            text = get_artist_info(artist_editor.processor.album_song_dict)
            stb.scrollableTextbox(text, height = 200, key=f"col1_{i}")
        with col2:
            col2.subheader(artist_editor.name)
            text = get_artist_info(artist_editor.processor.new_album_song_dict)
            stb.scrollableTextbox(text, height = 200, key=f"col2_{i}")
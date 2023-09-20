import asyncio
import streamlit as st
from app import MusicFolder
import streamlit_scrollable_textbox as stb

st.set_page_config(page_title='MetaSong', layout="wide")

def init_or_add(path: str) -> MusicFolder:
    if not 'mf' in st.session_state:
        st.session_state.mf = MusicFolder(path)
        st.session_state.list_path = [path]
    elif 'mf' in st.session_state:
        st.session_state.mf.add_new_dir_of_artist(path)
        st.session_state.list_path.append(path)

def apply_names():
    if 'mf' in st.session_state:
        st.session_state.mf.apply_to_files()
    else:
        st.write('Introduce el directorio a analizar primero')

def apply_tags(use_api: bool, covers: bool):
    if 'mf' in st.session_state:
        asyncio.run( st.session_state.mf.apply_all_tags(use_api, covers) )
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

button_col1, button_col2, button_col3 = st.columns(3, gap='small')

if not 'mf' in st.session_state:
    st.session_state.path = st.text_input('Introduce el path')
    st.session_state.init = button_col1.button('Escanear path')
    if st.session_state.path and st.session_state.init:
        init_or_add(st.session_state.path)
        st.experimental_rerun()

if 'mf' in st.session_state:
    st.session_state.new_path = st.text_input('Añade otro path a analizar')
    st.session_state.init2 = button_col1.button('Escanear nuevo path')
    if st.session_state.new_path and st.session_state.init2:
        init_or_add(st.session_state.new_path)
        st.session_state.new_path = ''; st.session_state.init2 = False

button_col2.button('Aplicar nombres', on_click=apply_names)
checkbox_col1, checkbox_col2 = st.columns(2, gap='small')
use_api = checkbox_col1.checkbox('Usar datos online')
covers = checkbox_col2.checkbox('Descargar covers')
button_col3.button('Aplicar etiquetas', on_click=apply_tags, args=(use_api, covers))

col1, col2 = st.columns(2)

if 'mf' in st.session_state:
    col1.header("Directorio de música:")
    col2.header("Propuesta de edición:")
    st.subheader('Lista de path analizados: '); list_path = []
    for path in st.session_state.list_path:
        list_path.append(path)
    st.text(list_path)
    
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
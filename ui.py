import streamlit as st
from folder_analyzer import MusicFolder

def initialize_music_folder(path: str) -> MusicFolder:
    st.session_state.mf = MusicFolder(path)

path = st.text_input("Introduce el path")
st.button('Escanear path', on_click=initialize_music_folder, args=(path,))

col1, col2 = st.columns(2)


if 'mf' in st.session_state:
    col1.header("Directorio de música:")
    col2.header("Propuesta de edición:")
    st.button("Aplicar nombres")
    st.button("Aplicar etiquetas")
    mf = st.session_state.mf
    for artist_editor in mf.artist_editors:
        processor = artist_editor.processor
        col1.subheader(artist_editor.processor.name); col2.subheader(artist_editor.processor.name)
        for old_album, new_album in zip(processor.album_song_dict, processor.new_album_song_dict_with_extensions):
            col1.write(f'*{old_album}*'); col2.write(f'*{new_album}*')
            for old_song, new_song in zip(processor.album_song_dict[old_album], processor.new_album_song_dict_with_extensions[new_album]):
                col1.write(' ', old_song); col2.write(' ', new_song)
                print(old_song, new_song)
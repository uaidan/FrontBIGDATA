import pandas as pd
import requests
from time import sleep
import streamlit as st

# Estado inicial de listas
final_data_movies = []
final_data_series = []

# Función para obtener datos detallados de un anime
def obtain_movie_data(anime_id):
    url = f"https://api.jikan.moe/v4/anime/{anime_id}/full"
    response = requests.get(url)
    if response.status_code == 200:
        datos = response.json().get('data', {})

        datos_extraidos = {
            "url": datos.get("url", "N/A"),
            "large_image_url": datos.get("images", {}).get("jpg", {}).get("large_image_url", "N/A"),
            "trailer_embed_url": datos.get("trailer", {}).get("embed_url", "N/A"),
            "title_english": datos.get("title_english", "N/A"),
            "title_japanese": datos.get("title_japanese", "N/A"),
            "type": datos.get("type", "N/A"),
            "synopsis": datos.get("synopsis", "N/A"),
            "genres": [genre.get("name", "N/A") for genre in datos.get("genres", [])],
            "opening_themes": datos.get("theme", {}).get("openings", [])
        }

        return datos_extraidos
    else:
        return {"error": f"Error al hacer la solicitud. Código de estado: {response.status_code}"}


pelis_csv = 'recommendations_movies.csv'
series_csv = 'recommendations_series.csv'

df_movies = pd.read_csv(pelis_csv)
df_series = pd.read_csv(series_csv)

df_movies = df_movies[['ID', 'avg_rating']]
df_series = df_series[['ID', 'avg_rating']]

tupla_movies = list(df_movies.itertuples(index=False, name=None)) # Tupla con (ID, rating) de películas
tupla_series = list(df_series.itertuples(index=False, name=None)) # Tupla con (ID, rating) de series

rating_movies = [t[1] for t in tupla_movies]
rating_series = [t[1] for t in tupla_series]
ids_movies = [t[0] for t in tupla_movies]
ids_series = [t[0] for t in tupla_series]

# Carga de datos (solo sse realiza una vez)
if "final_data_loaded" not in st.session_state:
    st.session_state.final_data_movies = []
    st.session_state.final_data_series = []

    for n in ids_movies:
        data = obtain_movie_data(n)
        st.session_state.final_data_movies.append(data)
        sleep(1)

    for n in ids_series:
        data = obtain_movie_data(n)
        st.session_state.final_data_series.append(data)
        sleep(1)

    st.session_state.final_data_loaded = True

# Recuperar datos de la sesión
final_data_movies = st.session_state.final_data_movies
final_data_series = st.session_state.final_data_series


# Estado para controlar selección
if "selected_index" not in st.session_state:
    st.session_state.selected_index = None
if "selected_type" not in st.session_state:
    st.session_state.selected_type = None

st.title("Recomendador de Anime!")

# Si hay un ítem seleccionado, mostramos detalles
if st.session_state.selected_index is not None and st.session_state.selected_type is not None:
    if st.session_state.selected_type == "movie":
        datos = final_data_movies[st.session_state.selected_index]
        anime_id = ids_movies[st.session_state.selected_index]
    else:
        datos = final_data_series[st.session_state.selected_index]
        anime_id = ids_series[st.session_state.selected_index]

    # Mostrar datos detallados
    st.image(datos.get("large_image_url"), width=300)
    st.header(datos.get("title_english", "Título no disponible"))
    st.subheader(datos.get("title_japanese", "Título japonés no disponible"))
    st.markdown(f"**Géneros:** {', '.join(datos.get('genres', []))}")
    st.markdown("### Sinopsis")
    st.write(datos.get("synopsis", "N/A"))
    st.markdown("### Temas de Apertura")
    for theme in datos.get("opening_themes", []):
        st.write(f"- {theme}")
    if datos.get("trailer_embed_url") != "N/A":
        st.markdown("### Tráiler")
        st.video(datos["trailer_embed_url"])
    else:
        st.info("No hay tráiler disponible.")

    # Volver a la lista
    if st.button("Volver a la lista"):
        st.session_state.selected_index = None
        st.session_state.selected_type = None

else:
    # Mostrar películas
    st.markdown("## Recomendación de Películas")
    if final_data_movies:
        cols = st.columns(len(final_data_movies))
        for i, movie_data in enumerate(final_data_movies):
            with cols[i]:
                st.write(f"Nota: {rating_movies[i]:.2f}")
                st.image(movie_data["large_image_url"], use_container_width=True)
                titulo = movie_data["title_english"] or movie_data["title_japanese"]
                if st.button(titulo, key=f"movie_{i}"):
                    st.session_state.selected_index = i
                    st.session_state.selected_type = "movie"

    # Mostrar series
    st.markdown("## Recomendación de Series")
    if final_data_series:
        cols = st.columns(len(final_data_series))
        for i, serie_data in enumerate(final_data_series):
            with cols[i]:
                st.write(f"Nota: {rating_series[i]:.2f}")
                st.image(serie_data["large_image_url"], use_container_width=True)
                titulo = serie_data["title_english"] or serie_data["title_japanese"]
                if st.button(titulo, key=f"serie_{i}"):
                    st.session_state.selected_index = i
                    st.session_state.selected_type = "series"

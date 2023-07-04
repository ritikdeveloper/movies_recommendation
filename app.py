import streamlit as st
import pickle
import pandas as pd
import requests
from pytube import YouTube

similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=33b05f603b4693be98ad9b30d93c2ea3')
    data = response.json()
    return "https://image.tmdb.org/t/p/w185" + data['poster_path']

def fetch_movie_details(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=33b05f603b4693be98ad9b30d93c2ea3')
    data = response.json()
    return data

def fetch_trailer(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=33b05f603b4693be98ad9b30d93c2ea3')
    data = response.json()
    if 'results' in data:
        results = data['results']
        for result in results:
            if result['type'] == 'Trailer' and result['site'] == 'YouTube':
                return result['key']
    return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = [movies.iloc[i[0]].title for i in movie_indices]
    movie_id = [movies.iloc[i[0]].movie_id for i in movie_indices]
    posters = [fetch_poster(movies.iloc[i[0]].movie_id) for i in movie_indices]
    details = [fetch_movie_details(movies.iloc[i[0]].movie_id) for i in movie_indices]
    trailers = [fetch_trailer(movies.iloc[i[0]].movie_id) for i in movie_indices]

    return recommended_movies, posters, details, trailers

movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Set up the sidebar
st.sidebar.title('Movie Recommender System')

# Add input field in the sidebar for movie selection
selected_movie = st.sidebar.selectbox('Select a movie:', movies['title'].values)

# Add recommend button in the sidebar
if st.sidebar.button('Recommend'):
    recommended_movies, posters, movie_details, trailers = recommend(selected_movie)

    # Clear the main page
    st.header('')

    # Display recommended movie names under the sidebar
    st.sidebar.subheader('Recommended Movies')
    for movie_name in recommended_movies:
        st.sidebar.write(movie_name)

    # Display recommended movies and their details on the main page
    st.subheader('Recommended Movies')
    for i in range(len(recommended_movies)):
        st.subheader(recommended_movies[i])
        st.image(posters[i])
        st.write('**Overview:**', movie_details[i]['overview'])
        st.write('**Release Date:**', movie_details[i]['release_date'])
        if trailers[i]:
            st.write('**Trailer:**')
            st.video(f"https://www.youtube.com/watch?v={trailers[i]}")
        else:
            st.write('**Trailer:** Trailer not available')

        # Add more details here

import pickle
import streamlit as st
import mysql.connector

# Establish MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0708",
    database="login"
)

# Function to fetch movie poster from the database
def fetch_poster(movie_id):
    with db.cursor() as cursor:
        query = "SELECT poster_path FROM new_full WHERE original_title = %s"
        cursor.execute(query, (movie_id,))
        result = cursor.fetchone()

        if result:
            poster_path = result[0]
            cursor.fetchall()  # Consume and discard any remaining result sets
            return poster_path
        else:
            return None
        
# Function to recommend movies
# Function to recommend movies and fetch posters of movies with the same genre
def recommend(selected_movie):
    index = movies[movies['original_title'] == selected_movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    # Recommendations
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].original_title
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].original_title)

    #
    with db.cursor() as cursor:
        name_query = "SELECT genres FROM new_full WHERE original_title = %s"
        cursor.execute(name_query, (selected_movie,))
        name_result = cursor.fetchone()

# Check if the query returned a result
    if name_result:
        selected_genre = name_result[0].split('|')[0].strip()  # Get the first actor
    else:
        selected_genre = None

    with db.cursor() as cursor:
        genre_query = """
        SELECT original_title, poster_path 
        FROM new_full 
        WHERE SUBSTRING_INDEX(genres, '|', 2) = SUBSTRING_INDEX((SELECT genres FROM new_full WHERE original_title = %s), '|', 1)
        AND original_title <> %s 
        ORDER BY imdb_rating DESC
        LIMIT 5
        """
        cursor.execute(genre_query, (selected_movie, selected_movie))
        genre_results = cursor.fetchall()

        top_5_genre_names = [result[0] for result in genre_results] if genre_results else []
        top_5_genre_paths = [result[1] for result in genre_results] if genre_results else []

    # Actor-based recommendations
    with db.cursor() as cursor:
        actor_name_query = "SELECT actors FROM new_full WHERE original_title = %s"
        cursor.execute(actor_name_query, (selected_movie,))
        actor_name_result = cursor.fetchone()

# Check if the query returned a result
    if actor_name_result:
        selected_actor = actor_name_result[0].split('|')[0].strip()  # Get the first actor
    else:
        selected_actor = None

    with db.cursor() as cursor:
        actor_query = """
        SELECT original_title, poster_path 
        FROM new_full 
        WHERE SUBSTRING_INDEX(actors, ' ', 1) = SUBSTRING_INDEX((SELECT actors FROM new_full WHERE original_title = %s), ' ', 1)
        AND original_title <> %s 
        ORDER BY imdb_rating DESC
        LIMIT 5
        """

        cursor.execute(actor_query, (selected_movie, selected_movie))
        actor_results = cursor.fetchall()

        top_5_actor_names = [result[0] for result in actor_results] if actor_results else []
        top_5_actor_paths = [result[1] for result in actor_results] if actor_results else []

#year based

        with db.cursor() as cursor:
            year_name_query = "SELECT release_date FROM new_full WHERE original_title = %s"
            cursor.execute(year_name_query, (selected_movie,))
            year_name_result = cursor.fetchone()

        if year_name_result:
            selected_year = year_name_result[0].split(' ')[2].strip()  # Get the first actor
        else:
            selected_year = None

        with db.cursor() as cursor:
            year_query = """
            SELECT original_title, poster_path 
            FROM new_full 
            WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(release_date, ' ', -2), ' ', 1) = SUBSTRING_INDEX((SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(release_date, ' ', -2), ' ', 1) FROM new_full WHERE original_title = %s), ' ', 1)
            AND original_title <> %s 
            ORDER BY imdb_rating DESC
            LIMIT 5
            """

            cursor.execute(year_query, (selected_movie, selected_movie))
            year_results = cursor.fetchall()

            year_names = [result[0] for result in year_results] if year_results else []
            year_paths = [result[1] for result in year_results] if year_results else []

    return recommended_movie_names, recommended_movie_posters, top_5_genre_names, top_5_genre_paths, top_5_actor_names, top_5_actor_paths, year_names, year_paths, selected_actor, selected_genre, selected_year



    
## --------------------------------------------------------------------------------------------------------------------------
###                                           FUNCTIONS ABOVE 
## --------------------------------------------------------------------------------------------------------------------------

def authenticate(username, password):
    return True  # Return True for demonstration purposes

# Streamlit app header and movie selection


st.set_page_config(
    page_title="Movie Recommender",
    page_icon=":movie_camera:",
    layout="wide",
    initial_sidebar_state="expanded"  # You can customize the background color here
)

background_color = "#F9F9E0"
st.markdown(
    f"""
    <style>
        body {{
            background-color: {background_color};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for login
with st.sidebar:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

# Check login credentials
if login_button:
    if authenticate(username, password):
        st.sidebar.success("Login Successful!")
    else:
        st.sidebar.error("Login Failed. Please check your credentials.")
        st.stop()


# Load movie data and similarity matrix
movies = pickle.load(open("C:\\Users\\Lenovo\\OneDrive\\Desktop\\Pickle\\movies.pkl", 'rb'))
similarity = pickle.load(open("C:\\Users\\Lenovo\\OneDrive\\Desktop\\Pickle\\similarity.pkl", 'rb'))

# Streamlit app header and movie selection
st.title('Movie Recommender System')
selected_movie = st.selectbox("Select a movie", movies['original_title'].values)

# Show recommendation button
if st.button('Show Recommendations'):
    recommended_movie_names, recommended_movie_posters, same_genre_movie_names, same_genre_movie_posters, same_actor_movie_names, same_actor_movie_posters, year_name, year_path, selected_actor, selected_genre, selected_year= recommend(selected_movie)

    if recommended_movie_names:
        # Display recommendations in one horizontal row
        st.write('---')  # Add a horizontal rule for separation
        st.write("**Recommended Movies:**")

        # Create separate columns for each recommended movie
        col1, col2, col3, col4, col5 = st.columns(5)
 # Custom CSS for hover effect
        hover_css = """
        <style>
            img:hover {
                transform: scale(1.2);
                transition: transform 0.3s ease;
                outline: 2px solid #BAD7DF; /* Add the outline style here */
                z-index: 1;
            }
        </style>
        """
        st.markdown(hover_css, unsafe_allow_html=True)

        for name, poster, col in zip(recommended_movie_names, recommended_movie_posters, [col1, col2, col3, col4, col5]):
            with col:
                st.subheader(name)
                if poster is not None:
                    st.image(poster, use_column_width=True)
                else:
                    st.warning("No poster available")

    else:
        st.warning("No recommendations available.")

    if same_genre_movie_names:
        # Display movies with the same genre below the recommended movies
        st.write('---')  # Add a horizontal rule for separation
        st.write(f"**More {selected_genre}**")

        # Create separate columns for each movie with the same genre
        col1, col2, col3, col4, col5 = st.columns(5)
        for name, poster, col in zip(same_genre_movie_names, same_genre_movie_posters, [col1, col2, col3, col4, col5]):
            with col:
                st.subheader(name)
                if poster is not None:
                    st.image(poster, use_column_width=True)
                else:
                    st.warning("No poster available")
    else:
        st.warning("No Movies")
    
    if same_actor_movie_names:
        # Display movies with the same genre below the recommended movies
        st.write('---')  # Add a horizontal rule for separation
        st.write(f"**More from {selected_actor}:**")

        # Create separate columns for each movie with the same genre
        col1, col2, col3, col4, col5 = st.columns(5)
        for name, poster, col in zip(same_actor_movie_names, same_actor_movie_posters, [col1, col2, col3, col4, col5]):
            with col:
                st.subheader(name)
                if poster is not None:
                    st.image(poster, use_column_width=True)
                else:
                    st.warning("No poster available")
    else:
        st.warning("No Movies")

    if year_name:
        # Display movies with the same genre below the recommended movies
        st.write('---')  # Add a horizontal rule for separation
        st.write(f"**Top Movies from {selected_year}:**")

        # Create separate columns for each movie with the same genre
        col1, col2, col3, col4, col5 = st.columns(5)
        for name, poster, col in zip(year_name, year_path, [col1, col2, col3, col4, col5]):
            with col:
                st.subheader(name)
                if poster is not None:
                    st.image(poster, use_column_width=True)
                else:
                    st.warning("No poster available")
    else:
        st.warning("No Movies")
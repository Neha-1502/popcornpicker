import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import db

def main():
    st.set_page_config(page_title="PopcornPicker - Analytics", layout="wide")
    
    if not st.session_state.get("logged_in"):
        st.warning("Please login first")
        st.switch_page("pages/1_🏠_Home.py")
    
    user_id = st.session_state.user_id
    
    st.title("📊 Your Movie Analytics")
    
    # Load data with proper copy
    @st.cache_data
    def load_movie_data():
        df = pd.read_csv("data/imdb_top_1000.csv")
        df = df.copy()  # Explicit copy of the entire DataFrame
        df['Stars'] = df['Star1'] + ', ' + df['Star2'] + ', ' + df['Star3'] + ', ' + df['Star4']
        return df
    
    df = load_movie_data()
    
    # Get user data
    watch_history = db.get_watch_history(user_id)
    ratings = db.get_ratings(user_id)
    
    # Create watched movies DataFrame safely
    if watch_history:
        history_df = df.loc[df['Series_Title'].isin(watch_history)].copy()
    else:
        history_df = pd.DataFrame()

    # Display sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Watch History")
        if not watch_history:
            st.info("You haven't watched any movies yet")
        else:
            st.dataframe(
                history_df[['Series_Title', 'Released_Year', 'Genre', 'IMDB_Rating']],
                hide_index=True
            )
    
    with col2:
        st.subheader("Your Ratings")
        if not ratings:
            st.info("You haven't rated any movies yet")
        else:
            ratings_df = pd.DataFrame.from_dict(ratings, orient='index', columns=['Your Rating'])
            st.dataframe(ratings_df)
    
    # Visualizations
    if watch_history:
        st.subheader("Your Movie Preferences")
        
        # Extract genres safely
        all_genres = []
        for _, row in history_df.iterrows():
            genres = row['Genre'].split(', ')
            all_genres.extend(genres)
        
        genre_counts = pd.Series(all_genres).value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Count']
        
        fig1 = px.pie(
            genre_counts,
            names='Genre',
            values='Count',
            title="Your Favorite Genres",
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Ratings visualization
        if ratings:
            rated_movies = df.loc[df['Series_Title'].isin(ratings.keys())].copy()
            rated_movies = rated_movies.assign(Your_Rating=rated_movies['Series_Title'].map(ratings))
            
            fig2 = px.scatter(
                rated_movies,
                x='IMDB_Rating',
                y='Your_Rating',
                hover_data=['Series_Title'],
                title="Your Ratings vs IMDB Ratings",
                color='Your_Rating',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Statistics
    st.subheader("Statistics")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric("Movies Watched", len(watch_history))
    
    with col4:
        avg_rating = sum(ratings.values()) / len(ratings) if ratings else 0
        st.metric("Your Average Rating", f"{avg_rating:.1f}/10")
    
    with col5:
        fav_genre = genre_counts['Genre'].iloc[0] if watch_history and not genre_counts.empty else "N/A"
        st.metric("Favorite Genre", fav_genre)

if __name__ == "__main__":
    main()
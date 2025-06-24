import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.database import db
import time

@st.cache_data
def load_data():
    df = pd.read_csv("data/imdb_top_1000.csv")
    
    # Clean the Released_Year column
    df['Released_Year'] = pd.to_numeric(df['Released_Year'].str.replace('PG', ''), errors='coerce')
    df['Released_Year'] = df['Released_Year'].fillna(df['Released_Year'].median()).astype(int)
    
    # Clean other columns
    df['Runtime'] = df['Runtime'].str.replace(' min', '').astype(int)
    df['Stars'] = df['Star1'] + ', ' + df['Star2'] + ', ' + df['Star3'] + ', ' + df['Star4']
    df['Content'] = (df['Series_Title'] + ' ' + df['Overview'] + ' ' + 
                    df['Stars'] + ' ' + df['Director'] + ' ' + df['Genre'])
    return df

def compute_similarity(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['Content'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def get_recommendations(title, df, cosine_sim, n=5):
    indices = pd.Series(df.index, index=df['Series_Title'])
    try:
        idx = indices[title]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        movie_indices = [i[0] for i in sim_scores[1:n+1] if i[0] != idx]  # Exclude self
        return df.iloc[movie_indices]
    except KeyError:
        return pd.DataFrame()

def main():
    st.set_page_config(page_title="PopcornPicker - Recommendations", layout="wide")
    
    if not st.session_state.get("logged_in"):
        st.warning("Please login first")
        st.switch_page("pages/1_🏠_Home.py")
    
    user_id = st.session_state.user_id
    df = load_data()
    cosine_sim = compute_similarity(df)
    
    st.title("🎬 Movie Recommendations")
    
    # Initialize session state
    if 'last_recommendation' not in st.session_state:
        st.session_state.last_recommendation = None
    if 'last_selection' not in st.session_state:
        st.session_state.last_selection = None
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Select a Movie")
        selected_movie = st.selectbox(
            "Choose a movie you like:",
            df['Series_Title'].sort_values().unique(),
            index=None,
            key="movie_select"
        )
        
        if selected_movie and selected_movie != st.session_state.last_selection:
            with st.spinner(f"Finding similar movies to {selected_movie}..."):
                time.sleep(0.5)
                recommendations = get_recommendations(selected_movie, df, cosine_sim, 10)
                st.session_state.last_recommendation = recommendations
                st.session_state.last_selection = selected_movie
        
        # Filters with cleaned year data
        st.subheader("Filters")
        genre_filter = st.multiselect(
            "Filter by genre",
            sorted(set(g for genres in df['Genre'].str.split(', ') for g in genres)),
            key="genre_filter"
        )
        
        year_range = st.slider(
            "Release year range",
            min_value=int(df['Released_Year'].min()),
            max_value=int(df['Released_Year'].max()),
            value=(int(df['Released_Year'].quantile(0.25)), int(df['Released_Year'].quantile(0.75))),
            key="year_filter"
        )
        
        runtime_filter = st.slider(
            "Runtime (minutes)",
            min_value=int(df['Runtime'].min()),
            max_value=int(df['Runtime'].max()),
            value=(90, 120),
            key="runtime_filter"
        )
        
        rating_filter = st.slider(
            "IMDB Rating",
            min_value=float(df['IMDB_Rating'].min()),
            max_value=float(df['IMDB_Rating'].max()),
            value=(7.0, 9.0),
            step=0.1,
            key="rating_filter"
        )
    
    with col2:
        if st.session_state.last_recommendation is not None:
            recommendations = st.session_state.last_recommendation.copy()
            
            # Apply filters
            if genre_filter:
                recommendations = recommendations[
                    recommendations['Genre'].apply(lambda x: any(g in x for g in genre_filter))
                ]
            
            recommendations = recommendations[
                (recommendations['Released_Year'] >= year_range[0]) &
                (recommendations['Released_Year'] <= year_range[1]) &
                (recommendations['Runtime'] >= runtime_filter[0]) &
                (recommendations['Runtime'] <= runtime_filter[1]) &
                (recommendations['IMDB_Rating'] >= rating_filter[0]) &
                (recommendations['IMDB_Rating'] <= rating_filter[1])
            ]
            
            if recommendations.empty:
                st.warning("No recommendations match your filters. Try adjusting them.")
            else:
                st.subheader(f"Movies similar to {st.session_state.last_selection}")
                
                for _, movie in recommendations.iterrows():
                    cols = st.columns([1, 3])
                    with cols[0]:
                        st.image(movie['Poster_Link'], width=150)
                    
                    with cols[1]:
                        st.markdown(f"""
                        <h3 style='color: #f72585;'>{movie['Series_Title']} ({int(movie['Released_Year'])})</h3>
                        <p><strong style='color: #4cc9f0;'>⭐ IMDB:</strong> 
                           <span style='color: #a8dadc;'>{movie['IMDB_Rating']}</span></p>
                        <p><strong style='color: #4cc9f0;'>🎭 Genre:</strong> 
                           <span style='color: #a8dadc;'>{movie['Genre']}</span></p>
                        <p><strong style='color: #4cc9f0;'>⏱️ Runtime:</strong> 
                           <span style='color: #a8dadc;'>{movie['Runtime']} min</span></p>
                        <p><strong style='color: #4cc9f0;'>🎬 Director:</strong> 
                           <span style='color: #a8dadc;'>{movie['Director']}</span></p>
                        <p><strong style='color: #4cc9f0;'>🌟 Stars:</strong> 
                           <span style='color: #a8dadc;'>{movie['Stars']}</span></p>
                        <p style='color: #f1faee;'>{movie['Overview']}</p>
                        """, unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Add to Watch History", key=f"watch_{movie['Series_Title']}"):
                            db.add_to_watch_history(user_id, movie['Series_Title'])
                            st.success("Added to watch history!")
                            st.rerun()
                    
                    with btn_col2:
                        rating = st.slider(
                            "Your Rating",
                            1, 10, 5,
                            key=f"rate_{movie['Series_Title']}"
                        )
                        if st.button("Submit Rating", key=f"submit_{movie['Series_Title']}"):
                            db.add_rating(user_id, movie['Series_Title'], rating)
                            st.success("Rating submitted!")
                            st.rerun()
                    
                    st.write("---")

if __name__ == "__main__":
    main()
import re
import hashlib
import pandas as pd
from typing import Dict, List, Union
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate an email address"""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    """Validate a username (3-20 chars, letters, numbers, underscores)"""
    pattern = r"^[a-zA-Z0-9_]{3,20}$"
    return re.match(pattern, username) is not None

def apply_preferences_filter(df: pd.DataFrame, preferences: Dict) -> pd.DataFrame:
    """
    Filter a DataFrame of movies based on user preferences
    Args:
        df: DataFrame containing movie data
        preferences: Dictionary of user preferences
    Returns:
        Filtered DataFrame
    """
    if not preferences:
        return df
    
    filtered_df = df.copy()
    
    # Filter by minimum rating
    if 'min_rating' in preferences:
        filtered_df = filtered_df[filtered_df['IMDB_Rating'] >= preferences['min_rating']]
    
    # Filter by genres
    if 'genres' in preferences and preferences['genres']:
        filtered_df = filtered_df[
            filtered_df['Genre'].apply(
                lambda x: any(g in x for g in preferences['genres'])
            )
        ]
    
    # Filter by directors
    if 'directors' in preferences and preferences['directors']:
        filtered_df = filtered_df[filtered_df['Director'].isin(preferences['directors'])]
    
    # Filter by runtime
    if 'runtime' in preferences:
        if preferences['runtime'] == 'Short (<90 min)':
            filtered_df = filtered_df[filtered_df['Runtime'] < 90]
        elif preferences['runtime'] == 'Medium (90-150 min)':
            filtered_df = filtered_df[(filtered_df['Runtime'] >= 90) & (filtered_df['Runtime'] <= 150)]
        elif preferences['runtime'] == 'Long (>150 min)':
            filtered_df = filtered_df[filtered_df['Runtime'] > 150]
    
    return filtered_df

def get_personalized_recommendations(
    user_id: str, 
    df: pd.DataFrame, 
    model: Dict, 
    n: int = 5
) -> pd.DataFrame:
    """
    Get personalized recommendations based on user's watch history and ratings
    Args:
        user_id: User ID from database
        df: DataFrame containing movie data
        model: Recommendation model dictionary
        n: Number of recommendations to return
    Returns:
        DataFrame of recommended movies
    """
    from utils.database import db
    
    user = db.get_user(user_id)
    watch_history = user.get('watch_history', [])
    ratings = user.get('ratings', {})
    preferences = user.get('preferences', {})
    
    # If user has rated movies, find similar to highest rated
    if ratings:
        # Get top 3 highest rated movies
        top_rated = sorted(ratings.items(), key=lambda x: x[1], reverse=True)[:3]
        recommendations = []
        
        for movie, _ in top_rated:
            recs = get_recommendations(movie, model, df, n=3)
            recommendations.append(recs)
        
        if recommendations:
            combined_recs = pd.concat(recommendations).drop_duplicates()
            # Remove movies already watched
            combined_recs = combined_recs[~combined_recs['Series_Title'].isin(watch_history)]
            # Apply user preferences
            combined_recs = apply_preferences_filter(combined_recs, preferences)
            return combined_recs.head(n)
    
    # Fallback to popular movies if no ratings
    popular_movies = df.sort_values('IMDB_Rating', ascending=False)
    popular_movies = popular_movies[~popular_movies['Series_Title'].isin(watch_history)]
    popular_movies = apply_preferences_filter(popular_movies, preferences)
    return popular_movies.head(n)

def format_movie_card(movie: pd.Series) -> str:
    """
    Format movie data as HTML for display
    Args:
        movie: Pandas Series containing movie data
    Returns:
        HTML string for the movie card
    """
    return f"""
    <div style="
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    ">
        <div style="display: flex;">
            <div style="flex: 1;">
                <img src="{movie['Poster_Link']}" width="150">
            </div>
            <div style="flex: 3; padding-left: 20px;">
                <h3>{movie['Series_Title']} ({movie['Released_Year']})</h3>
                <p><strong>⭐ IMDB:</strong> {movie['IMDB_Rating']}</p>
                <p><strong>🎭 Genre:</strong> {movie['Genre']}</p>
                <p><strong>⏱️ Runtime:</strong> {movie['Runtime']} min</p>
                <p><strong>🎬 Director:</strong> {movie['Director']}</p>
                <p><strong>🌟 Stars:</strong> {movie['Stars']}</p>
                <p>{movie['Overview']}</p>
            </div>
        </div>
    </div>
    """

def log_activity(user_id: str, activity_type: str, details: Dict):
    """
    Log user activity to database
    Args:
        user_id: User ID from database
        activity_type: Type of activity (e.g., 'login', 'recommendation', 'rating')
        details: Dictionary containing activity details
    """
    from utils.database import db
    
    log_entry = {
        'user_id': user_id,
        'activity_type': activity_type,
        'details': details,
        'timestamp': datetime.now()
    }
    
    db.db['activity_logs'].insert_one(log_entry)

def get_recommendations(title: str, model: Dict, df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Get recommendations for a given movie title
    Args:
        title: Movie title to get recommendations for
        model: Recommendation model dictionary
        df: DataFrame containing movie data
        n: Number of recommendations to return
    Returns:
        DataFrame of recommended movies
    """
    idx = model['indices'][title]
    sim_scores = list(enumerate(model['cosine_sim'][idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    movie_indices = [i[0] for i in sim_scores[1:n+1]]
    return df.iloc[movie_indices]
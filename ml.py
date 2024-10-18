import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Load the dataset globally
path = "imdb_top_1000.csv"  # Update this path if necessary
try:
    df = pd.read_csv(path)
    print("Loaded DataFrame:", df.head())  # Debugging: Print the first few rows
except Exception as e:
    logging.error(f"Error loading dataset: {e}")
    raise

# Preprocess the dataset
df['Stars'] = df['Star1'] + ', ' + df['Star2'] + ', ' + df['Star3'] + ', ' + df['Star4']
df.drop(['Star1', 'Star2', 'Star3', 'Star4'], axis=1, inplace=True)

# Clean the Released_Year column
df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
df['Released_Year'] = df['Released_Year'].fillna(0).astype(int)  # Fill NaN and convert to int

df['Runtime'] = df['Runtime'].str.replace(' min', '').astype(int)
df['Gross'] = df['Gross'].str.replace(',', '').astype(float)

# Create a content column for recommendations
content = (df['Series_Title'] + ' ' + df['Overview'] + ' ' + df['Stars'] + ' ' + df['Director'] + ' ' + df['Genre']).to_list()
recom_df = pd.DataFrame(content, columns=["Content"], index=df.Series_Title)

# Define a TF-IDF Vectorizer and compute the cosine similarity matrix
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(recom_df['Content'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
print("Cosine similarity matrix shape:", cosine_sim.shape)  # Debugging: Print the shape of the matrix

# Create a reverse map of indices and movie titles
idxs = pd.Series(df.index, index=df.Series_Title)

# Function to get recommendations
def get_recommendations(title):
    idx = idxs.get(title)
    logging.info(f"Getting recommendations for: {title}, Index: {idx}")
    
    if idx is None:
        logging.warning(f"Movie title '{title}' not found.")
        return pd.DataFrame()  # Return empty DataFrame for invalid title
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    movie_indices = [i[0] for i in sim_scores[1:6]]  # Get top 5 recommendations
    return df.iloc[movie_indices]

def main():
    logging.info("Starting the application")
    
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://images.pond5.com/old-movie-texture-overlay-vertical-footage-227741327_iconl.jpeg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Streamlit UI code here
    selected_movie_name = st.selectbox("Select a movie", df['Series_Title'].values)

    if st.button("Show Recommendations"):
        recommended_movies = get_recommendations(selected_movie_name)

        # Display the recommended movies
        if recommended_movies.empty:
            st.warning("No recommendations found for this movie.")
        else:
            for index, row in recommended_movies.iterrows():
                st.image(row['Poster_Link'], width=150)  # Display movie poster
                st.subheader(row['Series_Title'])
                st.write(f"Released Year: {row['Released_Year']}")
                st.write(f"Genre: {row['Genre']}")
                st.write(f"IMDB Rating: {row['IMDB_Rating']}")
                st.write(f"Overview: {row['Overview']}")
                st.write(f"Stars: {row['Stars']}")
                st.write("---")  # Separator for each movie

if __name__ == "__main__":
    main()
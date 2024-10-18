import unittest
import pandas as pd
from ml import get_recommendations  

class TestMovieRecommendations(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Load test data
        cls.df = pd.read_csv('test_imdb_top_1000.csv')
        print("Loaded DataFrame:", cls.df.head())  # Debugging: Print the first few rows
        
        cls.df['Stars'] = cls.df['Star1'] + ', ' + cls.df['Star2'] + ', ' + cls.df['Star3'] + ', ' + cls.df['Star4']
        cls.content = (cls.df['Series_Title'] + ' ' + cls.df['Overview'] + ' ' + cls.df['Stars'] + ' ' + cls.df['Director'] + ' ' + cls.df['Genre']).to_list()
        cls.recom_df = pd.DataFrame(cls.content, columns=["Content"], index=cls.df.Series_Title)

    def test_get_recommendations(self):
        recommendations = get_recommendations("The Shawshank Redemption")
        print("Recommendations:", recommendations['Series_Title'].values)  # Debugging: Print actual recommendations
        self.assertEqual(len(recommendations), 5)  # Expecting 5 recommendations
        
        # Adjust this movie title based on actual recommendations printed
        self.assertIn("Dev.D", recommendations['Series_Title'].values)

    def test_invalid_movie(self):
        recommendations = get_recommendations("Nonexistent Movie")
        self.assertTrue(recommendations.empty)  # Expecting empty DataFrame for invalid movie

if __name__ == '__main__':
    unittest.main()
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Union
import hashlib
import threading

# Use thread-local storage for SQLite connections
local_storage = threading.local()

def get_db_connection():
    """Get a thread-local SQLite connection"""
    if not hasattr(local_storage, 'conn'):
        Path("data").mkdir(exist_ok=True)
        local_storage.conn = sqlite3.connect("data/users.db", check_same_thread=False)
        local_storage.conn.row_factory = sqlite3.Row
    return local_storage.conn

class LocalDatabase:
    def __init__(self):
        self._init_db()
        
    def _init_db(self):
        """Initialize database and tables"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            preferences TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create watch_history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS watch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id TEXT NOT NULL,
            watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Create ratings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, movie_id)
        )
        """)
        
        conn.commit()
    
    @property
    def conn(self):
        return get_db_connection()
    
    def add_user(self, user_data: Dict) -> tuple:
        """Add new user to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
                """,
                (user_data['username'], user_data['email'], user_data['password'])
            )
            self.conn.commit()
            return True, cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already exists"
            elif "email" in str(e):
                return False, "Email already exists"
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, email: str, password: str) -> tuple:
        """Authenticate user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, password FROM users WHERE email = ?",
            (email,)
        )
        result = cursor.fetchone()
        if result and result[1] == password:
            return True, result[0]
        return False, "Invalid credentials"
    
    def get_user(self, user_id: int) -> Dict:
        """Get user data"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'preferences': json.loads(user[4]) if user[4] else {}
            }
        return None
    
    def update_user_preferences(self, user_id: int, preferences: Dict):
        """Update user preferences"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE users SET preferences = ? WHERE id = ?",
            (json.dumps(preferences), user_id)
        )
        self.conn.commit()
    
    def add_to_watch_history(self, user_id: int, movie_id: str):
        """Add movie to watch history"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO watch_history (user_id, movie_id)
            VALUES (?, ?)
            """,
            (user_id, movie_id)
        )
        self.conn.commit()
    
    def get_watch_history(self, user_id: int) -> List:
        """Get user's watch history"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT movie_id FROM watch_history WHERE user_id = ?",
            (user_id,)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def add_rating(self, user_id: int, movie_id: str, rating: int):
        """Add or update movie rating"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO ratings (user_id, movie_id, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, movie_id) DO UPDATE SET rating = ?
            """,
            (user_id, movie_id, rating, rating)
        )
        self.conn.commit()
    
    def get_ratings(self, user_id: int) -> Dict:
        """Get all user ratings"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT movie_id, rating FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def delete_user_data(self, user_id: int):
        """Delete all user data"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        cursor.execute("DELETE FROM watch_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM ratings WHERE user_id = ?", (user_id,))
        self.conn.commit()

db = LocalDatabase()
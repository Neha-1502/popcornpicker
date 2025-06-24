import streamlit as st
from utils.database import db
from utils.helpers import hash_password, validate_email, validate_username
import pandas as pd
import random

def show_intro():
    # Load movie data for the slideshow
    @st.cache_data
    def load_movie_data():
        df = pd.read_csv("data/imdb_top_1000.csv")
        return df[['Series_Title', 'Poster_Link']].dropna().sample(20)
    
    movies = load_movie_data()
    
    # Dark mode CSS with animations
    st.markdown(f"""
    <style>
    :root {{
        --primary: #f72585;
        --secondary: #4cc9f0;
        --accent: #a8dadc;
        --text: #f1faee;
        --bg: #1a1a2e;
        --card-bg: #16213e;
    }}
    
    body {{
        background-color: var(--bg);
        color: var(--text);
        overflow-x: hidden;
    }}
    
    .slideshow {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        opacity: 0.15;
    }}
    
    .slide {{
        position: absolute;
        width: 200px;
        height: 300px;
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        transition: transform 0.5s ease, opacity 0.5s ease;
        animation: float 15s infinite ease-in-out;
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0) rotate(-5deg); }}
        50% {{ transform: translateY(-20px) rotate(5deg); }}
    }}
    
    .intro-container {{
        background-color: rgba(26, 26, 46, 0.85);
        border-radius: 15px;
        padding: 2rem;
        backdrop-filter: blur(5px);
        border: 1px solid var(--secondary);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }}
    
    .intro-header {{
        font-size: 2.8rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        animation: fadeIn 1.5s ease;
    }}
    
    .intro-text {{
        font-size: 1.2rem;
        line-height: 1.6;
        color: var(--text);
        margin-bottom: 2rem;
        animation: fadeIn 2s ease;
    }}
    
    .feature-card {{
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border-left: 4px solid var(--primary);
        height: 100%;
        transition: transform 0.3s ease;
    }}
    
    .feature-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }}
    
    .feature-card h3 {{
        color: var(--secondary);
    }}
    
    .feature-card p {{
        color: var(--accent);
    }}
    
    .stButton>button {{
        background-color: var(--primary);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background-color: #b5179e;
        transform: scale(1.05);
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    </style>
    """, unsafe_allow_html=True)
    
    # Create movie slideshow background
    slideshow_html = "<div class='slideshow'>"
    for i, (_, row) in enumerate(movies.iterrows()):
        slideshow_html += f"""
        <div class='slide' id='slide{i}' 
             style='left: {random.randint(5, 85)}%; 
                    top: {random.randint(5, 85)}%;
                    background-image: url("{row['Poster_Link']}");
                    animation-delay: {i*0.5}s;'>
        </div>
        """
    slideshow_html += "</div>"
    st.markdown(slideshow_html, unsafe_allow_html=True)
    
    # Main content container
    with st.container():
        st.markdown('<div class="intro-header">Welcome to PopcornPicker! 🎬</div>', unsafe_allow_html=True)
        
        # App Introduction
        st.markdown("""
        <div class="intro-text">
        Discover your next favorite movie with our intelligent recommendation system. 
        Whether you're in the mood for a classic or something new, we've got you covered!
        </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards with hover effects
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="feature-card">
            <h3>🎭 Smart Recommendations</h3>
            <p>Get personalized suggestions based on your taste</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
            <h3>📊 Your Movie Stats</h3>
            <p>Track your watch history and ratings</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
            <h3>⚡ Lightning Fast</h3>
            <p>Find perfect movies in seconds</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation Buttons with animation
        if st.session_state.get("logged_in"):
            if st.button("🚀 Go to Recommendations", type="primary", use_container_width=True):
                st.switch_page("pages/2_🎬_Recommendations.py")
        else:
            if st.button("👉 Login / Register", type="primary", use_container_width=True):
                st.session_state.show_login = True
                st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption("© 2025 PopcornPicker - Made with ❤️ for movie lovers")

def show_auth():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3418/3418886.png", width=200)
        st.markdown("""
        ## 🍿 PopcornPicker
        Your personal movie recommendation engine
        
        - Discover new movies
        - Get personalized recommendations
        - Track your watch history
        - Rate and review films
        """)
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        success, result = db.authenticate_user(email, hash_password(password))
                        if success:
                            st.session_state.user_id = result
                            st.session_state.logged_in = True
                            st.session_state.show_login = False
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error(result)
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Create New Account")
                email = st.text_input("Email", placeholder="your@email.com")
                username = st.text_input("Username", placeholder="Choose a username")
                password1 = st.text_input("Password", type="password")
                password2 = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Register")
                
                if submit:
                    if not all([email, username, password1, password2]):
                        st.error("Please fill in all fields")
                    elif not validate_email(email):
                        st.error("Please enter a valid email address")
                    elif not validate_username(username):
                        st.error("Username must be 3-20 characters (letters, numbers, underscores)")
                    elif len(password1) < 6:
                        st.error("Password must be at least 6 characters")
                    elif password1 != password2:
                        st.error("Passwords don't match")
                    else:
                        user_data = {
                            "username": username,
                            "email": email,
                            "password": hash_password(password1)
                        }
                        success, result = db.add_user(user_data)
                        if success:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error(result)
        
        if st.button("← Back to Home"):
            st.session_state.show_login = False
            st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.show_login = False
    st.success("Logged out successfully!")
    st.rerun()

def main():
    st.set_page_config(
        page_title="PopcornPicker - Welcome",
        page_icon="🍿",
        layout="centered"
    )
    
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    
    # Check if user is logged in and wants to logout
    if st.session_state.get("logout_requested"):
        logout()
    
    # Show appropriate page based on state
    if st.session_state.get("logged_in"):
        show_intro()
        
        # Add logout button in sidebar
        with st.sidebar:
            if st.button("Logout", type="primary"):
                st.session_state.logout_requested = True
                st.rerun()
    elif st.session_state.get("show_login"):
        show_auth()
    else:
        show_intro()

if __name__ == "__main__":
    main()
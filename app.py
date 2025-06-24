import streamlit as st
from utils.database import db

def main():
    st.set_page_config(
        page_title="PopcornPicker",
        page_icon="🍿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    # Redirect to intro page if not coming from auth flow
    if not st.session_state.get("from_auth", False):
        st.switch_page("pages/1_🏠_Home.py")
    
    # Sidebar navigation (for other pages)
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3418/3418886.png", width=100)
        st.title("PopcornPicker")
        
        if st.session_state.logged_in:
            user = db.get_user(st.session_state.user_id)
            st.write(f"Welcome, {user['username']}!")
            
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.rerun()
            
            st.divider()
            
            nav_options = {
                "Recommendations": "🎬 Recommendations",
                "Analytics": "📊 Analytics",
                "Settings": "⚙️ Settings"
            }
            
            selected = st.radio(
                "Navigation",
                list(nav_options.values()),
                label_visibility="collapsed"
            )
            
            if selected == "🎬 Recommendations":
                st.switch_page("pages/2_🎬_Recommendations.py")
            elif selected == "📊 Analytics":
                st.switch_page("pages/3_📊_Analytics.py")
            elif selected == "⚙️ Settings":
                st.switch_page("pages/4_⚙️_Settings.py")
                
# Add this to your existing app.py
def set_theme():
    theme_toggle = st.sidebar.toggle("Dark Mode", value=True)
    if theme_toggle:
        st.markdown("""
        <style>
        :root {
            --primary: #f72585;
            --secondary: #4cc9f0;
            --text: #f1faee;
            --bg: #1a1a2e;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        :root {
            --primary: #e63946;
            --secondary: #1d3557;
            --text: #2b2d42;
            --bg: #f9f9f9;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
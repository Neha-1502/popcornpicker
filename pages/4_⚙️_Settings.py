import streamlit as st
import pandas as pd
from utils.database import db
from utils.helpers import hash_password

def main():
    st.set_page_config(page_title="PopcornPicker - Settings", layout="wide")
    
    if not st.session_state.get("logged_in"):
        st.warning("Please login first")
        st.switch_page("pages/1_🏠_Home.py")
    
    user_id = st.session_state.user_id
    user = db.get_user(user_id)
    
    st.title("⚙️ Account Settings")
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Preferences", "Data"])
    
    with tab1:
        st.subheader("Update Profile Information")
        
        with st.form("profile_form"):
            new_username = st.text_input(
                "Username",
                value=user.get('username', '')
            )
            
            new_email = st.text_input(
                "Email",
                value=user.get('email', '')
            )
            
            new_password = st.text_input(
                "New Password",
                type="password",
                placeholder="Leave blank to keep current password"
            )
            
            submit = st.form_submit_button("Save Changes")
            
            if submit:
                updates = {}
                if new_username != user.get('username', ''):
                    # Check if username is available
                    cursor = db.conn.cursor()
                    cursor.execute(
                        "SELECT id FROM users WHERE username = ? AND id != ?",
                        (new_username, user_id)
                    )
                    if cursor.fetchone():
                        st.error("Username already taken")
                    else:
                        updates['username'] = new_username
                
                if new_email != user.get('email', ''):
                    # Check if email is available
                    cursor.execute(
                        "SELECT id FROM users WHERE email = ? AND id != ?",
                        (new_email, user_id)
                    )
                    if cursor.fetchone():
                        st.error("Email already in use")
                    else:
                        updates['email'] = new_email
                
                if new_password:
                    updates['password'] = hash_password(new_password)
                
                if updates:
                    try:
                        cursor.execute(
                            "UPDATE users SET " + 
                            ", ".join(f"{k} = ?" for k in updates.keys()) +
                            " WHERE id = ?",
                            (*updates.values(), user_id)
                        )
                        db.conn.commit()
                        st.success("Profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update profile: {str(e)}")
                else:
                    st.info("No changes made")

    with tab2:
        st.subheader("Your Movie Preferences")
        
        df = pd.read_csv("data/imdb_top_1000.csv")
        all_genres = sorted(set(g for genres in df['Genre'].str.split(', ') for g in genres))
        all_directors = sorted(df['Director'].unique())
        
        with st.form("preferences_form"):
            favorite_genres = st.multiselect(
                "Favorite Genres",
                all_genres,
                default=user.get('preferences', {}).get('genres', [])
            )
            
            favorite_directors = st.multiselect(
                "Favorite Directors",
                all_directors,
                default=user.get('preferences', {}).get('directors', [])
            )
            
            min_rating = st.slider(
                "Minimum IMDB Rating Preference",
                min_value=0.0,
                max_value=10.0,
                value=user.get('preferences', {}).get('min_rating', 7.0),
                step=0.1
            )
            
            runtime_preference = st.select_slider(
                "Preferred Runtime",
                options=['Short (<90 min)', 'Medium (90-150 min)', 'Long (>150 min)'],
                value=user.get('preferences', {}).get('runtime', 'Medium (90-150 min)')
            )
            
            submit = st.form_submit_button("Save Preferences")
            
            if submit:
                preferences = {
                    'genres': favorite_genres,
                    'directors': favorite_directors,
                    'min_rating': min_rating,
                    'runtime': runtime_preference
                }
                db.update_user_preferences(user_id, preferences)
                st.success("Preferences saved!")

    with tab3:
        st.subheader("Your Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export Your Data")
            
            watch_history = db.get_watch_history(user_id)
            history_df = pd.DataFrame(watch_history, columns=['Movie Title'])
            st.download_button(
                label="Download Watch History",
                data=history_df.to_csv(index=False),
                file_name="popcornpicker_watch_history.csv",
                mime="text/csv"
            )
            
            ratings = db.get_ratings(user_id)
            ratings_df = pd.DataFrame.from_dict(ratings, orient='index', columns=['Rating'])
            st.download_button(
                label="Download Ratings",
                data=ratings_df.to_csv(index=False),
                file_name="popcornpicker_ratings.csv",
                mime="text/csv"
            )
        
        with col2:
            st.markdown("#### Account Actions")
            
            if st.button("Clear Watch History"):
                db.conn.cursor().execute(
                    "DELETE FROM watch_history WHERE user_id = ?",
                    (user_id,)
                )
                db.conn.commit()
                st.success("Watch history cleared!")
                st.rerun()
            
            if st.button("Clear Ratings"):
                db.conn.cursor().execute(
                    "DELETE FROM ratings WHERE user_id = ?",
                    (user_id,)
                )
                db.conn.commit()
                st.success("Ratings cleared!")
                st.rerun()
            
            if st.button("Delete Account", type="primary"):
                if st.checkbox("I understand this action cannot be undone"):
                    if st.button("Confirm Account Deletion"):
                        db.delete_user_data(user_id)
                        st.session_state.logged_in = False
                        st.session_state.user_id = None
                        st.success("Account deleted successfully")
                        st.switch_page("pages/1_🏠_Home.py")

if __name__ == "__main__":
    main()
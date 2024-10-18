import streamlit as st
import login_form
import ml
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

st.set_page_config(page_title="My App", page_icon=":shark:", layout="wide")

def main():
    logging.info("Application started.")
    
    if st.session_state.get('logged_in', False):
        logging.info("User  is logged in, displaying movie recommendations.")
        ml.main()
    else:
        logging.info("User  is not logged in, displaying login form.")
        login_form.main()

if __name__ == "__main__":
    main()
import streamlit as st
import pyrebase
import re
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, initialize_app, app_check, auth

def main():
    st.markdown(
        '''
        <style>
        .stApp {
            background-image: url('https://thumbs.dreamstime.com/b/background-watching-movies-objects-left-reel-background-watching-movies-objects-left-wooden-125816705.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )
    
    # Firebase configuration keys
    firebaseConfig = {
        'apiKey': "AIzaSyCaUj2MWDet3Tiiq-TqmUzFf72FvRxpbAc",
        'authDomain': "movie-recommendation-27052.firebaseapp.com",
        'projectId': "movie-recommendation-27052",
        'databaseURL': "https://movie-recommendation-27052-default-rtdb.asia-southeast1.firebasedatabase.app/",
        'storageBucket': "movie-recommendation-27052.appspot.com",
        'messagingSenderId': "629217816297",
        'appId': "1:629217816297:web:4c434531b5980f41718a78",
        'measurementId': "G-Z0XCQ2YG42"
    }
    
    service_account_key_path = "C:/Users/Neha/Downloads/movie-recommendation-27052-firebase-adminsdk-y68vp-11aa5b7431.json"
    
    # Initialize Firebase app only if it hasn't been initialized yet
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred, firebaseConfig)
            st.success("Firebase initialized successfully.")
        except Exception as e:
            st.error(f"Firebase initialization failed: {e}")
            return  # Exit if initialization fails
    
    # Initialize Firebase app
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()

    popcorn_image_url = "https://cdn-icons-png.flaticon.com/512/3418/3418886.png"

    # Display the title with the popcorn image
    st.markdown(
        f"<h1 style='display:inline; font-family: Times New Roman; font-weight: bold; font-size: {len('PopcornPicker')}0px;'><span style='font-size: {len('PopcornPicker')}0px;'>PopcornPicker</span><img src='{popcorn_image_url}' height='100' style='vertical-align:middle;'></h1>",
        unsafe_allow_html=True
    )

    choice = st.selectbox(':red[LOGIN / SIGN-UP]', ['LOGIN', 'SIGN-UP'])

    if choice == 'LOGIN':
        email = st.text_input(':red[Please Enter Your Email]')
        password = st.text_input(':red[Please Enter Your Password]', type="password")
        login_button = st.button('Login')

        if login_button:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.success('Logged in successfully!')
                st.balloons()
                # Get the username from the database
                username = db.child(user['localId']).child("Handle").get().val()
                st.title('WELCOME ' + username + '!!!')
                
                st.session_state.logged_in = True
                st.rerun()
                
            except Exception as e:
                st.error('Error logging in: ' + str(e))

    elif choice == 'SIGN-UP':
        with st.form(key='signup', clear_on_submit=True):
            st.subheader(':green[Sign Up]')
            email = st.text_input(':red[Email]', placeholder='Enter Your Email')
            handle = st.text_input(':red[Username]', placeholder='Enter Your Username')
            password1 = st.text_input(':red[Password]', placeholder='Enter Your Password', type='password')
            password2 = st.text_input(':red[Confirm Password]', placeholder='Confirm Your Password', type='password')

            def validate_email(email):
                pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
                if re.match(pattern, email):
                    return True
                return False

            def validate_username(username):
                pattern = "^[a-zA-Z0-9]*$"
                if re.match(pattern, username):
                    return True
                return False

            def get_user_emails():
                users = db.get().val()
                if users is None:
                    return []
                emails = []
                for key, user in users.items():
                    if 'ID' in user:
                        emails.append(user['ID'])
                return emails

            def get_usernames():
                users = db.get().val()
                if users is None:
                    return []
                usernames = []
                for key, user in users.items():
                    if 'Handle' in user:
                        usernames.append(user['Handle'])
                return usernames

            if email:
                if validate_email(email):
                    if email not in get_user_emails():
                        if validate_username(handle):
                            if handle not in get_usernames():
                                if len(handle) >= 2:
                                    if len(password1) >= 6:
                                        if password1 == password2:
                                            try:
                                                user = auth.create_user_with_email_and_password(email, password1)
                                                db.child(user['localId']).child("Handle").set(handle)
                                                db.child(user['localId']).child("ID").set(user['localId'])
                                                st.success('Account created successfully!!')
                                                st.balloons()
                                            except Exception as e:
                                                st.error('Error creating account: ' + str(e))
                                        else:
                                            st.warning('Passwords Do Not Match')
                                    else:
                                        st.warning('Password is too Short')
                                else:
                                    st.warning('Username Too short')
                            else:
                                st.warning('Username Already Exists')

                        else:
                            st.warning('Invalid Username')
                    else:
                        st.warning('Email Already exists!!')
                else:
                    st.warning('Invalid Email')

            st.form_submit_button('Sign Up')

if __name__ == "__main__":
    main()
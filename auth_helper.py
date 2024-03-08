import streamlit as st
import streamlit_authenticator as stauth

def get_auth_status():
    # Fix to hide sidebar from: https://github.com/bharath5673/streamlit-multipage-authentication/blob/main/1_%F0%9F%93%88_Main.py
    hide_bar= """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            visibility:hidden;
            width: 0px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            visibility:hidden;
        }
        </style>
    """

    ## Set up authentication
    PASSWORD = st.secrets["PASSWORD"]
    USERS = st.secrets["USERS"]
    hashed_password = stauth.Hasher([PASSWORD]).generate()[0]

    # Credentials follows the following format:
    # "usernames": {
    #     user1: {
    #        "password": hashed_password
    #     },
    #  
    credentials = {"usernames": {user: {"password": hashed_password, "name": user} for user in USERS}}

    authenticator = stauth.Authenticate(
        credentials,
        "SIMBA",
        "1234354",
        90
    )

    name, authentication_status, username = authenticator.login(
        location='main',
        fields = {
            'Form name':'Login', 
            'Username':'Mail UC', 
            'Password':'Contraseña (entregada en el curso)', 
            'Login':'Login'
            }
        )

    authentication_status = st.session_state['authentication_status']

    if authentication_status == False:
        st.error('Username/password is incorrect')
        st.markdown(hide_bar, unsafe_allow_html=True)

    if authentication_status is None:
        st.warning('Por favor, inicia sesión para continuar.')
        st.markdown(hide_bar, unsafe_allow_html=True)

    if authentication_status == True:
        # # ---- SIDEBAR ----
        authenticator.logout(location='sidebar')
        
    return authentication_status
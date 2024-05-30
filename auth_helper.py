import uuid
import streamlit as st

def get_auth_status():
    st.session_state['authentication_status'] = True
    if 'username' not in st.session_state:
        st.session_state['username'] = uuid.uuid4().hex
    return st.session_state['authentication_status']
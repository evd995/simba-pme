from google.oauth2 import service_account
from google.cloud import firestore
import openai
from openai import OpenAI
import streamlit as st
from datetime import datetime

openai.api_key = st.secrets["OPENAI_API_KEY"]
openai_client = OpenAI()

GCP_PROJECT = st.secrets["GCP_PROJECT"]
COURSE_ID = st.secrets["COURSE_ID"]

creds = service_account.Credentials.from_service_account_info(st.secrets["FIRESTORE_CREDS"])
db = firestore.Client(credentials=creds, project=GCP_PROJECT)

def save_navigation(activity_id):
    user_id = st.session_state['username']
    course_db = db.collection('courses').document(str(COURSE_ID))
    users_db = course_db.collection('users')
    user_db = users_db.document(str(user_id))
    action_timestamp = datetime.now().astimezone().isoformat()

    activity_trace = user_db.collection('traces').document(action_timestamp)
    activity_trace.set({
        'activity_id': activity_id,
        'timestamp': action_timestamp
    })


    
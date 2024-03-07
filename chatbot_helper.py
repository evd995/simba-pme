from google.cloud import firestore
from openai import OpenAI
import streamlit as st

GCP_PROJECT = st.secrets["GCP_PROJECT"]
COURSE_ID = st.secrets["COURSE_ID"]

db = firestore.Client(project=GCP_PROJECT)
course_db = db.collection('courses').document(str(COURSE_ID))
users_db = course_db.collection('users')

def get_activity_thread(activity_id):
    # Load Firebase

    # Get thread_id from Firebase

    # If thread_id is None, create a new thread

    # Save thread_id to Firebase
    pass


def create_thread():
    # Call OpenAI API to create a new thread
    pass


def create_message():
    pass


def get_messages(thread_id):
    # Get messages from thread

    # Reorder messages

    # Reassign roles to messages
    pass
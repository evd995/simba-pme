import openai
from openai import OpenAI
import streamlit as st
import logging
import time
import sys

st.set_page_config(
    page_title="SIMBA-Gemini Demo",
    page_icon="😸",
)

# Title of the webpage
st.title("Bienvenido a SIMBA - Tu Asistente de Aprendizaje")

# Using columns to place text and image side by side
col1, col2 = st.columns(2)
with col1:  # First column for the text
    st.markdown("""
    ## **Apoyando la educación mediante la innovación**

    SIMBA (Sistema Inteligente de Mentoría, Bienestar y Apoyo) está diseñado para apoyar la experiencia de aprendizaje. Durante el curso podrá ayudarte a organizar tus estudios, responder preguntas sobre el contenido del curso y proporcionar orientación personalizada para mejorar tus hábitos de estudio.
    """)
    

with col2:  # Second column for the image
    st.image("SIMBA_img.jpeg", caption='SIMBA - Your Learning Partner')

st.markdown("---")

# Introduction and brief summary
st.markdown("""

## **Cómo usar SIMBA:**

""")
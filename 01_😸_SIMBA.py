import streamlit as st
from auth_helper import get_auth_status
from streamlit_config_helper import set_streamlit_page_config_once

set_streamlit_page_config_once()
get_auth_status()

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
    st.image("SIMBA_img.jpeg", caption='SIMBA - Tu compañero de estudio')

st.markdown("---")

# Introduction and brief summary
st.markdown("""

## **Cómo usar SIMBA:**

A la izquierda encontraras pestañas con las actividades que se realizarán en este taller. Puedes seleccionar la actividad que deseas realizar y SIMBA te guiará a través de ella.            
""")
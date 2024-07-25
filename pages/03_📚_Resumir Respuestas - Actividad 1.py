import streamlit as st
from chatbot_helper import summarize_responses

activity_id = ('Actividad_1',)
st.write("Presiona el botón para obtener un resumen de las respuestas a la actividad.")
st.button("Resumir respuestas", on_click=summarize_responses, args=activity_id)

from chatpage_template import load_template
import streamlit as st

assistant_id = st.secrets["OPENAI_ASSISTANT_ID"]
activity_id = 'Actividad_1'

load_template(assistant_id, title="SIMBA - Actividad formativa")
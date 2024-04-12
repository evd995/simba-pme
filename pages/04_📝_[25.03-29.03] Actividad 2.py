from streamlit_config_helper import set_streamlit_page_config_once

set_streamlit_page_config_once()

from auth_helper import get_auth_status
from chatpage_template import load_template
import streamlit as st


activity_id = 'Actividad_2'
assistant_id = st.secrets["ASSISTANT_IDS"][activity_id]

if get_auth_status():
    # print("\nHola\n")
    load_template(
        activity_id=activity_id, 
        assistant_id=assistant_id, 
        title="SIMBA - Actividad formativa"
    ) 
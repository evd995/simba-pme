# Code from https://discuss.streamlit.io/t/multipage-app-not-running-st-set-page-config-when-going-directly-to-subpage/29531/5
import streamlit

def set_streamlit_page_config_once():
    try:
        streamlit.set_page_config(    
            page_title="SIMBA",
            page_icon="😸"
        )
    except streamlit.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            # ignore this error
            print("--------- Ignoring error ---------")
            return
        raise e
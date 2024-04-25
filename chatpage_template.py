import streamlit as st
import logging
import sys

import chatbot_helper
import chatbot_eval as ce
from traces_helper import save_navigation

def disable():
    st.session_state["text_disabled"] = True

def enable():
    st.session_state["text_disabled"] = False

def load_template(activity_id, assistant_id, title):

    save_navigation(activity_id)
    
    if "text_disabled" not in st.session_state:
        st.session_state["text_disabled"] = False

    # Configure LlamaIndex logging to output to stdout at DEBUG level in a single line
    if 'debug_logging_configured' not in st.session_state:
        logging.basicConfig(stream=sys.stdout)
        st.session_state.debug_logging_configured = True

    st.title(title)
    intro_placeholder = st.empty()
    if "messages" not in st.session_state:
        intro_placeholder.markdown("Cargando chatbot...")

    # Get thread_id
    thread_id = chatbot_helper.get_activity_thread(activity_id)

    # Get message history
    st.session_state.messages = chatbot_helper.get_messages(thread_id)

    if len(st.session_state.messages):
        intro_placeholder.markdown("")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        avatar = "😸" if message["role"] == "model" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    if "tru_recorder" not in st.session_state:
        tru = ce.build_tru_recorder()

        exchange = {"input" : "","output" : ""}
        for message in st.session_state.messages:
            if message["role"] == "user":
                exchange["input"] = message["content"]
            elif exchange["input"] != "" and message["role"] == "model":
                exchange["output"] = message["content"]
            
            if exchange["input"] != "" and exchange["output"] != "":
                ce.addRecord(exchange["input"], exchange["output"], "", tru)

        st.session_state["tru_recorder"] = tru
    else :
        tru = st.session_state["tru_recorder"]

    prompt = st.chat_input("What is up?", on_submit=disable, disabled=st.session_state["text_disabled"])
    if prompt and thread_id is not None:
        disable()
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        logging.info('Creating message in thread...')
        with st.status("..."):
            st.write("Espera un momento, estoy pensando en una respuesta...")
            response_message = chatbot_helper.create_message(prompt, thread_id, assistant_id)        
            logging.info(f'Response message: {response_message}')

        # Start streaming model response
        with st.chat_message("model", avatar="😸"):
            st.markdown(response_message)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "content": response_message})
        ce.addRecord(prompt,response_message,"",st.session_state["tru_recorder"])
        enable()
        st.rerun()
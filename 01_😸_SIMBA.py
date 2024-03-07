import openai
from openai import OpenAI
import streamlit as st
import logging
import time
import sys

# Configure LlamaIndex logging to output to stdout at DEBUG level in a single line
if 'debug_logging_configured' not in st.session_state:
    logging.basicConfig(stream=sys.stdout)
    st.session_state.debug_logging_configured = True

openai.api_key = st.secrets["OPENAI_API_KEY"]
openai_client = OpenAI()

assistant_id = st.secrets["OPENAI_ASSISTANT_ID"]

st.set_page_config(
    page_title="SIMBA-Hábitos de Estudio",
    page_icon="😸",
)

st.title("SIMBA - Hábitos de Estudio")
st.write("¡Hola! Soy SIMBA, tu asistente personal para ayudarte a mejorar tus hábitos de estudio. ¿En qué puedo ayudarte hoy?")

if "messages" in st.session_state:
    if st.button("Reset chat"):
        st.session_state.messages = []
        st.session_state.agent.reset()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    thread = openai_client.beta.threads.create()
    st.session_state["thread_id"] = thread.id

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = "😸" if message["role"] == "model" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

prompt = st.chat_input("What is up?")
if prompt and 'thread_id' in st.session_state:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    logging.info('Creating message in thread...')
    with st.status("..."):
        st.write("Espera un momento, estoy pensando en una respuesta...")
        message = openai_client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        )

        logging.info('Starting run...')
        # The assistant's id belongs to the run, not the thread
        run = openai_client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id
        )

        logging.info('Checking run status...')
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        
        while run.status not in ["completed", "failed", "cancelled", "expired"]:
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            time.sleep(1)

        logging.info('Run completed.')

        messages = openai_client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id,
        )
        response_message = messages.data[0].content[0].text.value
        logging.info(f'Response message: {response_message}')

    # Start streaming model response
    with st.chat_message("model", avatar="😸"):
        st.markdown(response_message)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "model", "content": response_message})

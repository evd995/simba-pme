import streamlit as st
import logging
import sys

import chatbot_helper
import chatbot_eval as ce
from traces_helper import save_navigation
from trulens_eval import Tru
# from streamlit_js_eval import streamlit_js_eval

put_all_messages = True
means = False
reset = True

def disable():
    st.session_state["text_disabled"] = True

def enable():
    st.session_state["text_disabled"] = False

# # Save viewport height to session state
# st.session_state["ViewportHeight"] = streamlit_js_eval(
#     js_expressions="window.innerHeight", key="ViewportHeight"
# )

def load_template(activity_id, assistant_id, title):

    save_navigation(activity_id)
    if "text_disabled" not in st.session_state:
        st.session_state["text_disabled"] = False

    # Configure LlamaIndex logging to output to stdout at DEBUG level in a single line
    if 'debug_logging_configured' not in st.session_state:
        logging.basicConfig(stream=sys.stdout)
        st.session_state.debug_logging_configured = True

    # Get thread_id
    thread_id = chatbot_helper.get_activity_thread(activity_id)

    # Get message history
    st.session_state.messages = chatbot_helper.get_messages(thread_id)

    tru = Tru()

    if reset and ("already_reset" not in st.session_state) :
        st.session_state["already_reset"] = False

    if reset and not st.session_state["already_reset"] :
        tru.reset_database()
        st.session_state["already_reset"] = True

    if "tru_recorder" not in st.session_state :
        tru_virtual = ce.build_tru_recorder()
        if "all_messages-put" not in st.session_state:
            st.session_state["all_messages-put"]  = False

        if put_all_messages and not st.session_state["all_messages-put"] :
            exchange = {"input" : "","output" : ""}
            for message in st.session_state.messages:

                if message["role"] == "user":
                    exchange["input"] = message["content"]
                elif exchange["input"] != "" and message["role"] == "model":
                    exchange["output"] = message["content"]
                
                if exchange["input"] != "" and exchange["output"] != "":
                    ce.addRecord(exchange["input"], exchange["output"], "", tru_virtual)
                    exchange["input"] = ""
                    exchange["output"] = ""

        st.session_state["tru_recorder"] = tru_virtual

    # Using columns to place text and monitoring side by side
    col1, col2 = st.columns([0.5,0.5])
    with col1.container(height=1000, border=False):
        
        st.title(title)
        intro_placeholder = st.empty()
        if "messages" not in st.session_state:
            intro_placeholder.markdown("Cargando chatbot...")

        if len(st.session_state.messages):
            intro_placeholder.markdown("")

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            avatar = "😸" if message["role"] == "model" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

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
            if "tru_recorder" in st.session_state:
                ce.addRecord(prompt,response_message,"",st.session_state["tru_recorder"])
                # ce.evaluateLast(col2,tru)
            enable()
            st.rerun()

    with col2:
        st.header("Monitor Assistant Performance")

        if "tru_recorder" in st.session_state:

            if st.button("Check Performance (TruLens)"):
                tru = Tru()
                records, _ = tru.get_records_and_feedback(app_ids=[])
                if len(records) == 0:
                    st.write("There are no conversations loaded in TruLens. Please start a conversation with the assistant and come back.")
                else:
                    metric_cols_ix = records.columns.str.startswith("[METRIC]") & ~records.columns.str.endswith("_calls")
                    metric_cols = records.columns[metric_cols_ix]
                    mean_metrics = records[metric_cols].mean()

                    # Show alerts for metrics that are below 0.3
                    if '[METRIC] Answer Relevance' in records.columns:
                        if mean_metrics['[METRIC] Answer Relevance'] < (1/3):
                            st.markdown("🚨 **Low relevance of the assistant's answers.** The assistant may not have all the information needed to answer the question. You can try adding more documents related to the activity.")
                    
                    if '[METRIC] Groundedness' in records.columns:            
                        if mean_metrics['[METRIC] Groundedness'] < (1/3):
                            st.markdown("🚨 **Low groundedness of the assistant's answers.** The assistant may be hallucinating some facts, giving information that is not based on course context or related sources. Try discussing this with your students in class to avoid misconceptions.")
                    
                    if '[METRIC] Insensitivity' in records.columns:            
                        if mean_metrics['[METRIC] Insensitivity'] > (2/3):
                            st.markdown("🚨 **Insensitive answers from the assistant.** The assistant may be giving insensitive answers. In the activity goal you can try adding your desired tone for the bot (friendly, formal, etc).")
                    
                    if '[METRIC] Input Maliciousness' in records.columns:
                        if mean_metrics['[METRIC] Input Maliciousness'] > (2/3):
                            st.markdown("🚨 **Malicious input from the user detected.** The users may be trying to trick the assistant. You can modify the assisant's goal or discuss with your students in class the best uses for this technology.")
                    

                    records['ts'] = records['ts'].apply(lambda x: x[:16])
                    process_str = lambda x: x.encode("latin_1").decode("raw_unicode_escape").encode('utf-16', 'surrogatepass').decode('utf-16')
                    records['input'] = records['input'].apply(process_str)
                    records['output'] = records['output'].apply(process_str)
                    config = {
                        'input' : st.column_config.TextColumn('input', width="small"),
                        'output' : st.column_config.TextColumn('output', width="small"),
                    }

                    HELP_DICT = {
                        '[METRIC] Answer Relevance': 'A low score could indicate a lack of relevant context in the files.',
                        '[METRIC] Groundedness': 'A low score could indicate hallucinations from the assistant.',
                        '[METRIC] Insensitivity': 'A high score could represent inappropiate answers.',
                        '[METRIC] Input Maliciousness': 'A high score could represent attempts to trick the assistant.',
                    }

                    for col in metric_cols:
                        config[col] = st.column_config.TextColumn(col.replace('[METRIC] ', '').replace(' ', '\n'), width="small", help=HELP_DICT[col])
                    records = records[["ts", "input", "output", *metric_cols]]
                    records[metric_cols] = records[metric_cols].round(3)
                    def color_code(val):
                        if val < 0.3:
                            color = '#d7481d'
                        elif (0.3 <= val <= 0.6):
                            color = '#fff321'
                        else:
                            color = '#59f720'
                        return f'background-color: {color}'

                    # Apply color coding to the DataFrame
                    styled_records = records.style.map(color_code, subset=metric_cols)
                    styled_records = styled_records.map(lambda x: color_code(1 - x), subset=['[METRIC] Input Maliciousness', '[METRIC] Insensitivity'])

                    st.dataframe(styled_records, use_container_width=True, column_config=config)

            if st.button("Evaluate last message"):
                tru = Tru()
                records, _ = tru.get_records_and_feedback(app_ids=[])
                if len(records) == 0:
                    st.write("There are no conversations loaded in TruLens. Please start a conversation with the assistant and come back.")
                else:
                    metric_cols_ix = records.columns.str.startswith("[METRIC]") & ~records.columns.str.endswith("_calls")
                    metric_cols = records.columns[metric_cols_ix]
                    last_metrics = records[metric_cols].iloc[-1]

                    # Show alerts for metrics that are below 0.3
                    if '[METRIC] Answer Relevance' in records.columns:
                        if last_metrics['[METRIC] Answer Relevance'] < (1/3):
                            st.markdown("🚨 **Low relevance of the assistant's answers.** The assistant may not have all the information needed to answer the question. You can try adding more documents related to the activity.")
                    
                    if '[METRIC] Groundedness' in records.columns:            
                        if last_metrics['[METRIC] Groundedness'] < (1/3):
                            st.markdown("🚨 **Low groundedness of the assistant's answers.** The assistant may be hallucinating some facts, giving information that is not based on course context or related sources. Try discussing this with your students in class to avoid misconceptions.")
                    
                    if '[METRIC] Insensitivity' in records.columns:            
                        if last_metrics['[METRIC] Insensitivity'] > (2/3):
                            st.markdown("🚨 **Insensitive answers from the assistant.** The assistant may be giving insensitive answers. In the activity goal you can try adding your desired tone for the bot (friendly, formal, etc).")
                    
                    if '[METRIC] Input Maliciousness' in records.columns:
                        if last_metrics['[METRIC] Input Maliciousness'] > (2/3):
                            st.markdown("🚨 **Malicious input from the user detected.** The users may be trying to trick the assistant. You can modify the assisant's goal or discuss with your students in class the best uses for this technology.")
                    

                    # records['ts'] = records['ts'].apply(lambda x: x[:16])
                    # process_str = lambda x: x.encode("latin_1").decode("raw_unicode_escape").encode('utf-16', 'surrogatepass').decode('utf-16')
                    # records['input'] = records['input'].apply(process_str)
                    # records['output'] = records['output'].apply(process_str)
                    # config = {
                    #     'input' : st.column_config.TextColumn('input', width="small"),
                    #     'output' : st.column_config.TextColumn('output', width="small"),
                    # }

                    # HELP_DICT = {
                    #     '[METRIC] Answer Relevance': 'A low score could indicate a lack of relevant context in the files.',
                    #     '[METRIC] Groundedness': 'A low score could indicate hallucinations from the assistant.',
                    #     '[METRIC] Insensitivity': 'A high score could represent inappropiate answers.',
                    #     '[METRIC] Input Maliciousness': 'A high score could represent attempts to trick the assistant.',
                    # }

                    # for col in metric_cols:
                    #     config[col] = st.column_config.TextColumn(col.replace('[METRIC] ', '').replace(' ', '\n'), width="small", help=HELP_DICT[col])
                    # records = records[["ts", "input", "output", *metric_cols]]
                    # records[metric_cols] = records[metric_cols].round(3)
                    # def color_code(val):
                    #     if val < 0.3:
                    #         color = '#d7481d'
                    #     elif (0.3 <= val <= 0.6):
                    #         color = '#fff321'
                    #     else:
                    #         color = '#59f720'
                    #     return f'background-color: {color}'

                    # # Apply color coding to the DataFrame
                    # styled_records = records.style.map(color_code, subset=metric_cols)
                    # styled_records = styled_records.map(lambda x: color_code(1 - x), subset=['[METRIC] Input Maliciousness', '[METRIC] Insensitivity'])

                    # st.dataframe(styled_records, use_container_width=True, column_config=config)
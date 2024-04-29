import os
from trulens_eval import Feedback, Select, Tru
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as fOpenAI
from trulens_eval.tru_virtual import TruVirtual, VirtualApp, VirtualRecord
import streamlit as st
import openai
from openai import OpenAI
import numpy as np

import nest_asyncio
nest_asyncio.apply()

import numpy as np

openai.api_key = st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
openai_client = OpenAI()

def build_tru_recorder():
    provider = fOpenAI()

    #Setting up the virtual app
    grounded = Groundedness(groundedness_provider=provider)

    virtual_dict = dict(
        llm=dict(
            modelname="SIMBA"
        )
    )

    virtual_app = VirtualApp(virtual_dict)
    virtual_app[Select.RecordCalls.llm.maxtokens] = 1024

    context_retriever = Select.RecordCalls.retriever

    virtual_app[context_retriever] = "context_retriever"

    context_call = context_retriever.get_context

    context = context_call.rets[:]

    # HONEST
    # Answer Relevance
    f_qa_relevance = Feedback(
        provider.relevance_with_cot_reasons,
        name="[METRIC] Answer Relevance"
    ).on_input_output()

    # Context Relevance
    context_selection = context.collect()
    f_qs_relevance = (
        Feedback(provider.qs_relevance_with_cot_reasons,
                name="[METRIC] Context Relevance")
        .on_input()
        .on(context_selection)
        .aggregate(np.mean)
    )

    # Groundedness of reponse based on context
    grounded = Groundedness(groundedness_provider=provider)
    f_groundedness = (
        Feedback(grounded.groundedness_measure_with_cot_reasons,
                name="[METRIC] Groundedness"
                )
        .on(context_selection)
        .on_output()
        .aggregate(grounded.grounded_statements_aggregator)
    )

    # HARMLESS
    f_insensitivity = Feedback(
        provider.insensitivity_with_cot_reasons,
        name="[METRIC] Insensitivity",
        higher_is_better=False,
    ).on_output()

    f_input_maliciousness = Feedback(
        provider.maliciousness_with_cot_reasons,
        name="[METRIC] Input Maliciousness",
        higher_is_better=False,
    ).on_input()


    f_output_maliciousness = Feedback(
        provider.maliciousness_with_cot_reasons,
        name="[METRIC] Output Maliciousness",
        higher_is_better=False,
    ).on_output()

    # HELPFUL
    f_coherence = Feedback(
        provider.coherence_with_cot_reasons, name="[METRIC] Coherence"
    ).on_output()

    f_input_sentiment = Feedback(
        provider.sentiment_with_cot_reasons, name="[METRIC] Input Sentiment"
    ).on_input()

    f_output_sentiment = Feedback(
        provider.sentiment_with_cot_reasons, name="[METRIC] Ouput Sentiment"
    ).on_input()

    tru_recorder = TruVirtual(
        virtual_app,
        app_id="SIMBA_virtual",
        feedbacks=[
            f_qa_relevance,
            #f_qs_relevance,
            f_groundedness,
            f_insensitivity,
            f_input_maliciousness,
            #f_output_maliciousness,
            #f_coherence,
            #f_input_sentiment,
            #f_output_sentiment,
        ]
    )
    return tru_recorder

def addRecord(input,output,context,recorder):
    context_retriever = Select.RecordCalls.retriever
    context_call = context_retriever.get_context
    rec = VirtualRecord(
        main_input=input,
        main_output=output,
        calls = 
        {
             context_call: dict(
                 rets=[context]
             )
        }
    )
    recorder.add_record(rec)

def evaluateLast(col,tru):
    if "tru_recorder" in st.session_state:
        records, _ = tru.get_records_and_feedback(app_ids=[])

        if len(records) != 0:
            metric_cols_ix = records.columns.str.startswith("[METRIC]") & ~records.columns.str.endswith("_calls")
            metric_cols = records.columns[metric_cols_ix]
            print(records)
            # last_metrics = records[metric_cols][-1]
        
            # with col:
            #     # Show alerts for metrics that are below 0.3
            #     if '[METRIC] Answer Relevance' in records.columns:
            #         if last_metrics['[METRIC] Answer Relevance'] < (1/3):
            #             st.markdown("🚨 **Low relevance of the assistant's answers.** The assistant may not have all the information needed to answer the question, his answers may be incomplete.")
                
            #     if '[METRIC] Groundedness' in records.columns:            
            #         if last_metrics['[METRIC] Groundedness'] < (1/3):
            #             st.markdown("🚨 **Low groundedness of the assistant's answers.** The assistant may be hallucinating some facts, giving information that is not based on course context or related sources.")
                
            #     if '[METRIC] Insensitivity' in records.columns:            
            #         if last_metrics['[METRIC] Insensitivity'] > (2/3):
            #             st.markdown("🚨 **Insensitive answers from the assistant.** The assistant may be giving insensitive answers. In the activity goal you can try adding your desired tone for the bot (friendly, formal, etc).")
                
            #     if '[METRIC] Input Maliciousness' in records.columns:
            #         if last_metrics['[METRIC] Input Maliciousness'] > (2/3):
            #             st.markdown("🚨 **Malicious input from the user detected.** The users may be trying to trick the assistant. You can modify the assisant's goal or discuss with your students in class the best uses for this technology.")
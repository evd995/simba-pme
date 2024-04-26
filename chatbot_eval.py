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

import os
from trulens_eval import Feedback, Select, Tru
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI
from trulens_eval.tru_virtual import TruVirtual, VirtualApp, VirtualRecord

import numpy as np

os.environ["OPENAI_API_KEY"] = ""
provider = OpenAI()

grounded = Groundedness(groundedness_provider=provider)

virtual_dict = dict(
    llm=dict(
        modelname="SIMBA"
    )
)

virtual_app = VirtualApp(virtual_dict)
virtual_app[Select.RecordCalls.llm.maxtokens] = 1024

retriever = Select.RecordCalls.retriever
synthesizer = Select.RecordCalls.synthesizer

virtual_app[retriever] = "retriever"
virtual_app[synthesizer] = "synthesizer"

context_call = retriever.get_context
generation = synthesizer.generate

## For testing purposes
# rec1 = VirtualRecord(
#     main_input="Where is Germany?",
#     main_output="Germany is in Europe",
#     calls=
#         {
#             context_call: dict(
#                 args=["Where is Germany?"],
#                 rets=["Germany is a country located in Europe."]
#             ),
#             generation: dict(
#                 args=["""
#                     We have provided the below context: \n
#                     ---------------------\n
#                     Germany is a country located in Europe.
#                     ---------------------\n
#                     Given this information, please answer the question: 
#                     Where is Germany?
#                       """],
#                 rets=["Germany is a country located in Europe."]
#             )
#         }
#     )
# rec2 = VirtualRecord(
#     main_input="Where is Germany?",
#     main_output="Poland is in Europe",
#     calls=
#         {
#             context_call: dict(
#                 args=["Where is Germany?"],
#                 rets=["Poland is a country located in Europe."]
#             ),
#             generation: dict(
#                 args=["""
#                     We have provided the below context: \n
#                     ---------------------\n
#                     Germany is a country located in Europe.
#                     ---------------------\n
#                     Given this information, please answer the question: 
#                     Where is Germany?
#                       """],
#                 rets=["Poland is a country located in Europe."]
#             )
#         }
#     )

# data = [rec1, rec2]

context = context_call.rets[:]

# Question/statement relevance between question and each context chunk.
f_context_relevance = (
    Feedback(provider.context_relevance)
    .on_input()
    .on(context)
)

from trulens_eval.feedback import Groundedness
grounded = Groundedness(groundedness_provider=provider)

# Define a groundedness feedback function
f_groundedness = (
    Feedback(grounded.groundedness_measure_with_cot_reasons, name = "Groundedness")
    .on(context.collect())
    .on_output()
    .aggregate(grounded.grounded_statements_aggregator)
)

# Question/answer relevance between overall question and answer.
f_qa_relevance = (
    Feedback(provider.relevance_with_cot_reasons, name = "Answer Relevance")
    .on_input_output()
)

virtual_recorder = TruVirtual(
    app_id="SIMBA",
    app=virtual_app,
    feedbacks=[f_context_relevance,f_groundedness, f_qa_relevance],
    feedback_mode = "deferred" # optional
)

## For testing purposes :
# for record in data:
#     virtual_recorder.add_record(record)

def addRecord(input,output):
    rec = VirtualRecord(
        main_input=input,
        main_output=output)
    virtual_recorder.add_record(rec)
    
tru = Tru()
tru.run_dashboard()
tru.start_evaluator()

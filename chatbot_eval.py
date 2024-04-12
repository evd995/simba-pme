from trulens_eval import Feedback, Select
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI

import numpy as np

provider = OpenAI()

grounded = Groundedness(groundedness_provider=provider)

# Define a groundedness feedback function
f_groundedness = (
    Feedback(grounded.groundedness_measure_with_cot_reasons, name = "Groundedness")
    .on(Select.RecordCalls.retrieve.rets.collect())
    .on_output()
    .aggregate(grounded.grounded_statements_aggregator)
)

# Question/answer relevance between overall question and answer.
f_answer_relevance = (
    Feedback(provider.relevance_with_cot_reasons, name = "Answer Relevance")
    .on(Select.RecordCalls.retrieve.args.query)
    .on_output()
)

# Question/statement relevance between question and each context chunk.
f_context_relevance = (
    Feedback(provider.context_relevance_with_cot_reasons, name = "Context Relevance")
    .on(Select.RecordCalls.retrieve.args.query)
    .on(Select.RecordCalls.retrieve.rets.collect())
    .aggregate(np.mean)
)

from trulens_eval.tru_virtual import TruVirtual

virtual_recorder = TruVirtual(
    app_id="a virtual app",
    app=virtual_app,
    feedbacks=[f_context_relevance, f_groundedness, f_answer_relevance],
    feedback_mode = "deferred" # optional
)

from trulens_eval import TruCustomApp
tru_rag = TruCustomApp(rag,
    app_id = 'RAG v1',
    feedbacks = [f_groundedness, f_answer_relevance, f_context_relevance])

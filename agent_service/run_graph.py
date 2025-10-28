from agent_service.graph import build_graph
from langchain.schema import HumanMessage
from pydantic import BaseModel
from typing import Literal

graph = build_graph()

class ReviewDecision(BaseModel):
    decision: Literal["ok", "needs_more"]
    rationale: str = ""
    answer: str = ""
    todo: str = ""

# user query
user_input = "hey i want to visit you guys if you serve spagetti also tell me where are you located"
human_msg = HumanMessage(content=user_input)


# ensure state exists
state = {
    "messages": [],
    "summary": "",
    "review_decision": ReviewDecision(decision="needs_more", rationale="", answer="", todo="")
}

state["messages"].append(human_msg)
state["summary"] += f"\nHuman: {human_msg.content}"
# invoke the graph
result = graph.invoke(state)  # state is mutated in-place

# now extract the final user-facing answer
final_answer = result["review_decision"].answer

# and also get the summary for chat history
chat_summary = result["summary"]

print(final_answer)
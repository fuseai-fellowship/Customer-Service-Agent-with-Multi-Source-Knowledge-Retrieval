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

def code_runner(user_name:str, user_input:str, chat_history:str):
        # fresh state for this run
    state = {
        "messages": [],
        "summary": f"Chat History:{chat_history}\n",  # inject prior conversation
        "tool_output": "",
        "review_decision": ReviewDecision(decision="needs_more"),  # initial placeholder
        "user_name": user_name
    }

    # add current user message
    human_msg = HumanMessage(content=user_input)
    state["messages"].append(human_msg)
    state["summary"] += f"\nCurrent User Query: {user_input}"

    # invoke graph
    result = graph.invoke(state)

    # Extract final answer from result's review_decision
    review = result.get("review_decision")
    final_answer = review.answer if review else "(no answer)"

    chat_summary = f"\nHuman: {user_input}\nAI: {final_answer}"
    # chat_summary = result.get("summary", chat_history)
    return final_answer, chat_summary

from typing import Literal
from pydantic import BaseModel
from agent_service.state import State
from agent_service.llm import llm
from agent_service.prompts import REVIEWER_PROMPT
from langchain.schema import AIMessage

class ReviewDecision(BaseModel):
    """Structured output for the reviewer node."""
    decision: Literal["ok", "needs_more"]
    rationale: str = ""
    answer: str = ""
    todo: str = ""

# Wrap the model to return the Pydantic object directly:
reviewer_llm = llm
structured_reviewer = reviewer_llm.with_structured_output(ReviewDecision)

def reviewer_node(state: State):
    from langchain.schema import SystemMessage
    msgs = [SystemMessage(content=REVIEWER_PROMPT)]

    # include summary as a system message
    if "summary" in state and state["summary"]:
        msgs.append(SystemMessage(content=f"Summary: {state['summary']}"))
    
    if "tool_output" in state and state["tool_output"]:
        msgs.append(SystemMessage(content=f"Tool Output: {state['tool_output']}"))

    # Call structured reviewer
    review: ReviewDecision = structured_reviewer.invoke(msgs)
    
    updates = {}

    state.setdefault("summary", "")

    if review.decision == "ok" and review.answer:
        state["summary"] += f"\nAI: {review.answer}"
    

    # Store the full ReviewDecision object in state
    state["review_decision"] = review

    updates["messages"] = [AIMessage(content=review.answer)] if review.decision == "ok" else [SystemMessage(content=f"Reviewer: needs more info → {review.todo}")]

    return updates
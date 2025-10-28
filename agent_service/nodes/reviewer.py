from typing import Literal
from pydantic import BaseModel
from agent_service.state import State
from agent_service.llm import llm
from agent_service.prompts import REVIEWER_PROMPT
from langchain.schema import AIMessage

class ReviewDecision(BaseModel):
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

    # include summary as a system message (compressed menu_tool output)
    if "summary" in state and state["summary"]:
        msgs.append(SystemMessage(content=f"Summary: {state['summary']}"))

    # Call structured reviewer
    review: ReviewDecision = structured_reviewer.invoke(msgs)
    
    updates = {}

    # Update messages with final answer or reviewer note
    if review.decision == "ok" and review.answer:
        updates["messages"] = [AIMessage(content=review.answer)]
        # Append reviewer info to summary
        state.setdefault("summary", "")
        state["summary"] += f"\nReviewer decision: OK\nRationale: {review.rationale}\nAnswer: {review.answer}"
    else:
        updates["messages"] = [SystemMessage(content=f"Reviewer: needs more info → {review.todo}")]
        # Append reviewer info to summary
        state.setdefault("summary", "")
        state["summary"] += f"\nReviewer decision: Needs more info\nRationale: {review.rationale}\nTodo: {review.todo}"

    # Always update review_decision in state
    updates["review_decision"] = review.decision
    return updates
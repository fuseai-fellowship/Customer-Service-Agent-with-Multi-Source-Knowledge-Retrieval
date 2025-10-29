from typing import TypedDict, Annotated, List, Optional, Literal
from langgraph.graph.message import add_messages
from langchain.schema import BaseMessage
from pydantic import BaseModel

class ReviewDecision(BaseModel):
    decision: Literal["ok", "needs_more"]
    rationale: str = ""
    answer: str = ""
    todo: str = ""

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    review_decision: Optional[ReviewDecision]
    summary: Optional[str]
    tool_output: Optional[str]
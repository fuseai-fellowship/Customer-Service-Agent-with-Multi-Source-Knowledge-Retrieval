from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
from langchain.schema import BaseMessage

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    review_decision: Optional[str]
    summary: Optional[str]
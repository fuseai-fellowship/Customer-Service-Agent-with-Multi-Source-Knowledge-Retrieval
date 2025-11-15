from typing import List, Dict, Optional, TypedDict, Annotated, Literal
from operator import add
from pydantic import BaseModel

# Define State
class State(TypedDict):
    query: str
    chat_history: List[Dict[str, str]]  # List of {"user": ..., "bot": ...}
    query_types: Optional[List[Dict]]  # Will be filled by orchestrator
    subagent_outputs: Annotated[list, add]
    final_response: Optional[str]


class Parameters(BaseModel):
    search: Optional[str] = None
    type: Optional[Literal["veg", "non-veg"]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    topic: Optional[str] = None

class QueryTypeItem(BaseModel):
    type: Literal["menu", "info", "escalation", "chitchat", "ambiguous"]
    parameters: Optional[Parameters] = None
    clarification: Optional[str] = None

class OrchestratorOutput(BaseModel):
    query_types: List[QueryTypeItem]

class SynthesizerOutput(BaseModel):
    final_answer: str  

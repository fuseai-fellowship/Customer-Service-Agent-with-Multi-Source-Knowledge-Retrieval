from pydantic import BaseModel, ConfigDict
from typing import Optional

# Base schema for creating data
class KnowledgeBaseCreate(BaseModel):
    topic: Optional[str] = None
    content: str

# Schema for updating data
class KnowledgeBaseUpdate(BaseModel):
    topic: Optional[str] = None
    content: Optional[str] = None

# Schema for sending data out (includes the ID)
class KnowledgeBaseOut(BaseModel):
    id: int
    topic: Optional[str] = None
    content: str
    
    model_config = ConfigDict(from_attributes=True)
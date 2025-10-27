from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import KnowledgeBase
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseOut
)
from app.core.embedding import get_embedding_model
from typing import List

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
model = get_embedding_model() # Load the model once on startup

@router.post("", response_model=KnowledgeBaseOut, status_code=201)
def create_knowledge_item(
    payload: KnowledgeBaseCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge base item.
    The embedding will be generated automatically.
    """
    # Create the new KB object
    obj = KnowledgeBase(**payload.dict())
    
    # Generate and assign the embedding
    embedding_vector = model.encode(obj.content).tolist()
    obj.emb = embedding_vector
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[KnowledgeBaseOut])
def list_knowledge_items(db: Session = Depends(get_db)):
    """
    List all knowledge base items.
    """
    return db.query(KnowledgeBase).order_by(KnowledgeBase.id.asc()).all()

@router.patch("/{kb_id}", response_model=KnowledgeBaseOut)
def update_knowledge_item(
    kb_id: int, 
    payload: KnowledgeBaseUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update a knowledge base item.
    If the 'content' changes, the embedding will be regenerated.
    """
    obj = db.get(KnowledgeBase, kb_id)
    if not obj:
        raise HTTPException(404, "Knowledge item not found")

    update_data = payload.dict(exclude_unset=True)
    content_changed = False

    for key, value in update_data.items():
        if key == "content" and value != obj.content:
            content_changed = True
        setattr(obj, key, value)
    
    # Regenerate embedding ONLY if content changed
    if content_changed:
        print("Content changed, regenerating embedding...")
        embedding_vector = model.encode(obj.content).tolist()
        obj.emb = embedding_vector
    
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{kb_id}", status_code=204)
def delete_knowledge_item(kb_id: int, db: Session = Depends(get_db)):
    """
    Delete a knowledge base item.
    """
    obj = db.get(KnowledgeBase, kb_id)
    if not obj:
        raise HTTPException(404, "Knowledge item not found")
    
    db.delete(obj)
    db.commit()
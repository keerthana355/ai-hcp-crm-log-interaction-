"""
Interaction endpoints — READ ONLY from this router.

By design, interactions are never created or edited through a direct
REST call here. Every write happens exclusively through the LangGraph
agent's tools (see agent/tools.py + routers/agent.py), per the
assignment's explicit rule that the form must be AI-driven, not
manually editable.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Interaction
from app.schemas.schemas import InteractionOut

router = APIRouter(prefix="/api/interactions", tags=["interactions"])


@router.get("/", response_model=List[InteractionOut])
def list_interactions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Interaction).order_by(Interaction.created_at.desc()).all()


@router.get("/{interaction_id}", response_model=InteractionOut)
def get_interaction(interaction_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction

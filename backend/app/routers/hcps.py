"""
HCP endpoints — simple read access (HCPs are created implicitly by the
agent's log_interaction tool when a new name is mentioned).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import HCP
from app.schemas.schemas import HCPOut

router = APIRouter(prefix="/api/hcps", tags=["hcps"])


@router.get("/", response_model=List[HCPOut])
def list_hcps(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(HCP).order_by(HCP.name).all()

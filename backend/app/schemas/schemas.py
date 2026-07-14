"""
Pydantic schemas — define what's allowed IN and OUT of the API.
Kept separate from SQLAlchemy models (models/models.py) on purpose:
these describe the API contract, not the database table.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---------- Auth ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- HCP ----------

class HCPOut(BaseModel):
    id: int
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Interaction ----------

class InteractionOut(BaseModel):
    id: int
    hcp: Optional[HCPOut] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[datetime] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    materials_shared: Optional[List[str]] = None
    samples_distributed: Optional[List[str]] = None
    follow_up_actions: Optional[List[Dict[str, Any]]] = None
    compliance_note: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Agent chat ----------

class AgentChatRequest(BaseModel):
    conversation_id: str
    message: str


class AgentChatResponse(BaseModel):
    reply: str
    interaction: Optional[InteractionOut] = None
    conversation_id: str

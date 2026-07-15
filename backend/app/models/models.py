"""
Database schema (SQLAlchemy ORM models) — simplified 3-table design.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SentimentEnum(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class InteractionTypeEnum(str, enum.Enum):
    meeting = "meeting"
    call = "call"
    email = "email"
    conference = "conference"


class User(Base):
    """A field representative (the person logging interactions)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    interactions = relationship("Interaction", back_populates="created_by")


class HCP(Base):
    """A Healthcare Professional (doctor) the rep interacts with."""
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    specialty = Column(String(150), nullable=True)
    hospital = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    """
    The core record — one logged HCP interaction.

    IMPORTANT: nothing in this table is ever written by direct form
    input. Every field is populated exclusively by the LangGraph
    agent's tools (log_interaction / edit_interaction / etc.), per
    the assignment's explicit rule.
    """
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    interaction_type = Column(Enum(InteractionTypeEnum), default=InteractionTypeEnum.meeting)
    interaction_date = Column(DateTime, nullable=True)

    attendees = Column(Text, nullable=True)              # comma-separated names
    topics_discussed = Column(Text, nullable=True)
    sentiment = Column(Enum(SentimentEnum), nullable=True)
    outcomes = Column(Text, nullable=True)

    # Simple JSON lists — e.g. materials_shared = ["Brochure - Product X"]
    materials_shared = Column(JSON, nullable=True)
    samples_distributed = Column(JSON, nullable=True)

    # Populated by the suggest_followups tool, e.g.
    # [{"action": "Schedule follow-up meeting in 2 weeks", "done": false}]
    follow_up_actions = Column(JSON, nullable=True)

    # Populated (only) by the flag_compliance_risk tool
    compliance_note = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    hcp = relationship("HCP", back_populates="interactions")
    created_by = relationship("User", back_populates="interactions")

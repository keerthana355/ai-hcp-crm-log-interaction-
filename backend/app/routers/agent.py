"""
The single endpoint the AI Assistant chat panel talks to.

Conversation state (message history + which interaction is "current")
is kept in a simple in-memory dict, keyed by conversation_id. This is
fine for an assessment/demo project — a production version would
persist this in Redis or a DB table instead so it survives a server
restart and works across multiple backend instances.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Interaction
from app.schemas.schemas import AgentChatRequest, AgentChatResponse, InteractionOut
from app.agent.graph import get_agent

router = APIRouter(prefix="/api/agent", tags=["agent"])

# conversation_id -> {"messages": [...], "session_state": {"current_interaction_id": None}}
_conversations: dict = {}


def _get_conversation(conversation_id: str) -> dict:
    if conversation_id not in _conversations:
        _conversations[conversation_id] = {
            "messages": [],
            "session_state": {"current_interaction_id": None},
        }
    return _conversations[conversation_id]


@router.post("/chat", response_model=AgentChatResponse)
def chat(payload: AgentChatRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    convo = _get_conversation(payload.conversation_id)

    try:
        agent = get_agent(db, convo["session_state"])
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    convo["messages"].append(HumanMessage(content=payload.message))

    try:
        result = agent.invoke({"messages": convo["messages"]})
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent/LLM call failed: {e}")

    result_messages = result["messages"]
    convo["messages"] = result_messages  # persist full history including tool calls

    # last message is the agent's final natural-language reply
    reply_text = result_messages[-1].content if result_messages else "..."

    interaction_out = None
    iid = convo["session_state"].get("current_interaction_id")
    if iid:
        interaction = db.query(Interaction).filter(Interaction.id == iid).first()
        if interaction:
            interaction_out = InteractionOut.model_validate(interaction)

    return AgentChatResponse(
        reply=reply_text,
        interaction=interaction_out,
        conversation_id=payload.conversation_id,
    )

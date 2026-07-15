"""
Builds the LangGraph agent: a Groq-hosted LLM bound to our 5 tools,
wired into LangGraph's prebuilt ReAct-style agent graph.

Why `create_react_agent`? It's LangGraph's own scaffold for exactly
this pattern: LLM decides which tool(s) to call and with what
arguments -> tools execute -> LLM sees results -> LLM crafts the final
natural-language reply.
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from sqlalchemy.orm import Session

from app.agent.tools import build_tools

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_PRIMARY = os.getenv("GROQ_MODEL_PRIMARY", "openai/gpt-oss-20b")

SYSTEM_PROMPT = """You are the AI Assistant inside an HCP (Healthcare Professional) CRM \
for a pharmaceutical field representative. The rep describes their interactions with \
doctors in plain language, and you use your tools to log or edit that data — the rep \
never fills the form by hand, you are the only way data gets written.

Guidelines:
- If the rep describes a NEW interaction ("Today I met with Dr. X..."), call log_interaction.
- If the rep is CORRECTING something just logged ("actually it was...", "change the... to..."), \
call edit_interaction with ONLY the fields being corrected.
- After successfully logging an interaction, you may proactively call suggest_followups and \
mention the suggestions in your reply.
- If the rep asks about past visits with a doctor, call search_interaction_history.
- If materials/samples/gifts sound unusual, or the rep asks for a compliance check, call \
flag_compliance_risk.
- Always reply in a short, friendly, professional confirmation — mention exactly what was \
logged or changed. Never invent data the rep didn't mention.
- Reply in PLAIN TEXT only — no Markdown. Do not use **asterisks** for bold, do not use \
bullet points with dashes or numbers, do not use headers. Write plain sentences, and if you \
need to list multiple things, separate them with commas or write "First... Then..." in prose.
"""


def get_agent(db: Session, session_state: dict):
    """
    Returns a compiled LangGraph agent for a single request. `session_state`
    is a small dict (e.g. {"current_interaction_id": None}) that the tools
    close over, so edit_interaction/suggest_followups/flag_compliance_risk
    know which row is "current" within this conversation.
    """
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to backend/.env — see README for how to get one."
        )

    llm = ChatGroq(
        model=GROQ_MODEL_PRIMARY,
        api_key=GROQ_API_KEY,
        temperature=0.2,
    )

    tools = build_tools(db, session_state)

    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
    return agent

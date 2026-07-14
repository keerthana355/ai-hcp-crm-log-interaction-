"""
The 5 LangGraph tools.

Each tool is a plain Python function decorated with @tool. When bound
to a Groq LLM via `.bind_tools()`, the LLM itself reads each tool's
docstring + parameter descriptions and decides (a) which tool to call
and (b) what argument values to extract from the rep's natural-language
message. We never hand-parse the message with regex — the LLM does the
entity extraction, which is the whole point of using LangGraph here.

Tools 1 & 2 are mandatory per the assignment. Tools 3-5 are ours.
"""
from datetime import datetime
from typing import Optional, List
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.models.models import HCP, Interaction, SentimentEnum, InteractionTypeEnum

# Simple keyword list for the compliance tool. Kept small and readable
# on purpose — this is a demo-grade heuristic, not a legal compliance
# engine, and the LLM adds judgment on top of the raw keyword hits.
COMPLIANCE_KEYWORDS = [
    "cash", "gift card", "expensive dinner", "vacation", "free trip",
    "large sample quantity", "personal gift", "kickback",
]

def _regenerate_followups(interaction: Interaction):
    """Shared logic so both suggest_followups and edit_interaction (on
    sentiment change) produce consistent, up-to-date suggestions."""
    suggestions = []
    topic = (interaction.topics_discussed or "").lower()
    sentiment = interaction.sentiment.value if interaction.sentiment else "neutral"

    if sentiment == "positive":
        suggestions.append("Schedule a follow-up meeting in 2 weeks")
    elif sentiment == "negative":
        suggestions.append("Address concerns raised before next contact")
    else:
        suggestions.append("Check in within 3-4 weeks")

    if "efficacy" in topic or "trial" in topic or "study" in topic:
        suggestions.append("Send relevant clinical study data / Phase III results")
    if interaction.materials_shared:
        suggestions.append("Confirm materials were received and reviewed")
    if not suggestions:
        suggestions.append("Send a thank-you note summarizing the discussion")

    interaction.follow_up_actions = [{"action": s, "done": False} for s in suggestions[:3]]

def build_tools(db: Session, session_state: dict):
    """
    Factory that returns the 5 tools, each closing over the current
    DB session and a small `session_state` dict that tracks which
    interaction is "current" for this conversation — this is what
    lets edit_interaction know which row to patch.
    """

    def _get_or_create_hcp(name: str) -> HCP:
        hcp = db.query(HCP).filter(HCP.name.ilike(name.strip())).first()
        if not hcp:
            hcp = HCP(name=name.strip())
            db.add(hcp)
            db.commit()
            db.refresh(hcp)
        return hcp

    def _current_interaction() -> Optional[Interaction]:
        iid = session_state.get("current_interaction_id")
        if not iid:
            return None
        return db.query(Interaction).filter(Interaction.id == iid).first()

    @tool
    def log_interaction(
        hcp_name: str,
        interaction_type: Optional[str] = "meeting",
        topics_discussed: Optional[str] = None,
        sentiment: Optional[str] = None,
        materials_shared: Optional[List[str]] = None,
        samples_distributed: Optional[List[str]] = None,
        attendees: Optional[str] = None,
        outcomes: Optional[str] = None,
    ) -> str:
        """
        Log a brand-new HCP interaction from the rep's natural-language
        description. Extract the HCP's name, the interaction type
        (meeting/call/email/conference — default 'meeting' if unclear),
        topics discussed, sentiment (positive/neutral/negative),
        any materials (e.g. brochures) or samples mentioned as shared,
        attendees, and outcomes/agreements. Only call this for a NEW
        interaction, not a correction to one just logged (use
        edit_interaction for corrections instead).
        """
        hcp = _get_or_create_hcp(hcp_name)

        sentiment_val = None
        if sentiment and sentiment.lower() in SentimentEnum.__members__:
            sentiment_val = SentimentEnum(sentiment.lower())

        type_val = InteractionTypeEnum.meeting
        if interaction_type and interaction_type.lower() in InteractionTypeEnum.__members__:
            type_val = InteractionTypeEnum(interaction_type.lower())

        interaction = Interaction(
            hcp_id=hcp.id,
            interaction_type=type_val,
            interaction_date=datetime.utcnow(),
            attendees=attendees,
            topics_discussed=topics_discussed,
            sentiment=sentiment_val,
            outcomes=outcomes,
            materials_shared=materials_shared or [],
            samples_distributed=samples_distributed or [],
            follow_up_actions=[],
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        session_state["current_interaction_id"] = interaction.id

        return (
            f"Interaction logged successfully. HCP: {hcp.name}, "
            f"Sentiment: {sentiment_val.value if sentiment_val else 'not specified'}, "
            f"Topics: {topics_discussed or 'not specified'}."
        )

    @tool
    def edit_interaction(
        hcp_name: Optional[str] = None,
        interaction_type: Optional[str] = None,
        topics_discussed: Optional[str] = None,
        sentiment: Optional[str] = None,
        materials_shared: Optional[List[str]] = None,
        samples_distributed: Optional[List[str]] = None,
        attendees: Optional[str] = None,
        outcomes: Optional[str] = None,
    ) -> str:
        """
        Correct or update ONE OR MORE fields on the interaction that was
        just logged in this conversation. Only pass the fields the rep
        is actually correcting (e.g. just hcp_name and sentiment) —
        leave everything else as None so it stays untouched. Use this
        when the rep says things like "actually it was Dr. John" or
        "change the sentiment to negative", NOT for logging a new
        interaction from scratch.
        """
        interaction = _current_interaction()
        if not interaction:
            return "There's no interaction logged yet in this conversation to edit. Please log one first."

        changed = []

        if hcp_name:
            hcp = _get_or_create_hcp(hcp_name)
            interaction.hcp_id = hcp.id
            changed.append("HCP name")
        if interaction_type and interaction_type.lower() in InteractionTypeEnum.__members__:
            interaction.interaction_type = InteractionTypeEnum(interaction_type.lower())
            changed.append("interaction type")
        if topics_discussed:
            interaction.topics_discussed = topics_discussed
            changed.append("topics discussed")
        sentiment_changed = False
        if sentiment and sentiment.lower() in SentimentEnum.__members__:
            interaction.sentiment = SentimentEnum(sentiment.lower())
            changed.append("sentiment")
            sentiment_changed = True
        if materials_shared is not None:
            interaction.materials_shared = materials_shared
            changed.append("materials shared")
        if samples_distributed is not None:
            interaction.samples_distributed = samples_distributed
            changed.append("samples distributed")
        if attendees:
            interaction.attendees = attendees
            changed.append("attendees")
        if outcomes:
            interaction.outcomes = outcomes
            changed.append("outcomes")

        db.commit()
        db.refresh(interaction)

        followup_note = ""
        if sentiment_changed:
            _regenerate_followups(interaction)
            db.commit()
            followup_note = " Follow-up suggestions were also updated to match the new sentiment."

        if not changed:
            return "I didn't detect any specific fields to change — could you clarify what to update?"
        return f"Updated: {', '.join(changed)}. Everything else was left as-is.{followup_note}"

    @tool
    def search_interaction_history(hcp_name: str) -> str:
        """
        Look up past logged interactions with a given HCP by name, so
        the rep can recall what was discussed previously before logging
        a new interaction. Returns a short summary of the most recent
        interactions found.
        """
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name.strip()}%")).first()
        if not hcp:
            return f"No prior interactions found with anyone matching '{hcp_name}'."

        past = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp.id)
            .order_by(Interaction.created_at.desc())
            .limit(3)
            .all()
        )
        if not past:
            return f"{hcp.name} is on record, but no interactions have been logged with them yet."

        lines = []
        for i in past:
            date_str = i.interaction_date.strftime("%Y-%m-%d") if i.interaction_date else "unknown date"
            lines.append(
                f"- {date_str}: {i.topics_discussed or 'no topic noted'} "
                f"(sentiment: {i.sentiment.value if i.sentiment else 'n/a'})"
            )
        return f"Recent interactions with {hcp.name}:\n" + "\n".join(lines)

    @tool
    def suggest_followups() -> str:
        """
        Generate 2-3 suggested follow-up actions for the interaction
        that was just logged in this conversation (e.g. scheduling a
        next meeting, sending requested materials). Writes them into
        the interaction's follow-up list. Call this after a successful
        log_interaction, or whenever the rep asks for follow-up ideas.
        """
        interaction = _current_interaction()
        if not interaction:
            return "There's no current interaction to suggest follow-ups for yet."

        _regenerate_followups(interaction)
        db.commit()

        actions = [f["action"] for f in interaction.follow_up_actions]
        return "Suggested follow-ups added: " + "; ".join(actions)

    @tool
    def flag_compliance_risk() -> str:
        """
        Check the interaction just logged in this conversation for
        potential compliance concerns (e.g. mentions of cash, gifts,
        or unusually large sample quantities — relevant in pharma
        sales regulation). Writes a compliance note to the record
        without changing any other field. Call this after logging,
        or when the rep explicitly asks for a compliance check.
        """
        interaction = _current_interaction()
        if not interaction:
            return "There's no current interaction to check for compliance risk yet."

        text_blob = " ".join(filter(None, [
            interaction.topics_discussed or "",
            interaction.outcomes or "",
            " ".join(interaction.materials_shared or []),
            " ".join(interaction.samples_distributed or []),
        ])).lower()

        hits = [kw for kw in COMPLIANCE_KEYWORDS if kw in text_blob]

        if hits:
            note = f"Potential compliance concern — mentions of: {', '.join(hits)}. Recommend manager review."
            interaction.compliance_note = note
            db.commit()
            return note

        interaction.compliance_note = "No compliance concerns detected."
        db.commit()
        return "No compliance concerns detected in this interaction."

    return [
        log_interaction,
        edit_interaction,
        search_interaction_history,
        suggest_followups,
        flag_compliance_risk,
    ]

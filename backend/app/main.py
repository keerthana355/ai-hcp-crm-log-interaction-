"""
Entry point. Wires together the database, auth, HCP/interaction
read endpoints, and the LangGraph agent chat endpoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models import models  # noqa: F401 — import so tables register with Base
from app.routers import auth, hcps, interactions, agent

app = FastAPI(title="AI-First HCP CRM", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(hcps.router)
app.include_router(interactions.router)
app.include_router(agent.router)


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist yet. Fine for an assessment
    # project; a production app would use Alembic migrations instead.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}

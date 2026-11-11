"""
main.py - FastAPI Backend Service for the AI-Powered SQL Agent.
Provides RESTful APIs for the Streamlit UI or any external client.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from .agent import run_agent
from .conversation import conversation_manager
from .database import get_schema_summary

app = FastAPI(
    title="AI-Powered SQL Agent API",
    description="Translates natural language questions to safe SQL, executes them, and returns explained results.",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(..., description="The user's question in plain English")
    session_id: Optional[str] = Field("default", description="Session identifier for multi-turn conversations")


class QueryResponse(BaseModel):
    success: bool
    question: str
    sql: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    explanation: str
    error: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "AI SQL Agent"}


@app.get("/api/schema")
def get_schema():
    """Returns database schema representation."""
    return {"schema": get_schema_summary()}


@app.post("/api/query", response_model=QueryResponse)
def execute_nl_query(req: QueryRequest):
    """Processes user question into SQL and returns execution results."""
    try:
        result = run_agent(question=req.question, session_id=req.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
def get_history(session_id: str = "default"):
    """Returns conversation history for the given session."""
    return {"session_id": session_id, "history": conversation_manager.get_session(session_id)}


@app.post("/api/reset-session")
def reset_session(session_id: str = "default"):
    """Resets conversation history for the given session."""
    conversation_manager.clear_session(session_id)
    return {"status": "success", "message": f"Session '{session_id}' cleared."}

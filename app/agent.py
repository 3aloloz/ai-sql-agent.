"""
agent.py - Core Orchestrator for the AI SQL Agent.
Coordinates SQL generation, security validation, database execution,
and natural language explanation synthesis.
"""

from typing import Dict, Any
from .conversation import conversation_manager
from .sql_generator import generate_sql, generate_explanation
from .sql_validator import validate_sql
from .database import execute_query


def run_agent(question: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Main pipeline execution:
    1. Context retrieval
    2. SQL generation
    3. Security validation
    4. Safe execution
    5. Natural explanation
    6. Context storage
    """
    if not question or not question.strip():
        return {
            "success": False,
            "question": "",
            "sql": "",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "explanation": "Please enter a valid question.",
            "error": "Empty question provided."
        }

    # Step 1: Retrieve context
    history_context = conversation_manager.get_history_summary_for_prompt(session_id)

    # Step 2: Generate SQL
    raw_sql, is_unanswerable = generate_sql(question, history_context)

    if is_unanswerable:
        explanation = raw_sql.replace("CANNOT_ANSWER:", "").strip()
        conversation_manager.add_interaction(
            session_id=session_id,
            question=question,
            sql="",
            explanation=explanation,
            is_error=True
        )
        return {
            "success": False,
            "question": question,
            "sql": "",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "explanation": explanation,
            "error": "Query cannot be answered from the database schema."
        }

    # Step 3: Security Validation
    is_valid, cleaned_sql, validation_err = validate_sql(raw_sql)
    if not is_valid:
        error_explanation = f"⚠️ Query Blocked for Security: {validation_err}"
        conversation_manager.add_interaction(
            session_id=session_id,
            question=question,
            sql=cleaned_sql,
            explanation=error_explanation,
            is_error=True
        )
        return {
            "success": False,
            "question": question,
            "sql": cleaned_sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "explanation": error_explanation,
            "error": validation_err
        }

    # Step 4: Execute on Read-Only Connection
    try:
        columns, rows, count = execute_query(cleaned_sql)
    except Exception as e:
        exec_err = f"Database execution error: {str(e)}"
        conversation_manager.add_interaction(
            session_id=session_id,
            question=question,
            sql=cleaned_sql,
            explanation=exec_err,
            is_error=True
        )
        return {
            "success": False,
            "question": question,
            "sql": cleaned_sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "explanation": exec_err,
            "error": exec_err
        }

    # Step 5: Synthesize human-readable explanation
    explanation = generate_explanation(question, cleaned_sql, rows)

    # Step 6: Save conversation turn
    conversation_manager.add_interaction(
        session_id=session_id,
        question=question,
        sql=cleaned_sql,
        explanation=explanation,
        is_error=False
    )

    return {
        "success": True,
        "question": question,
        "sql": cleaned_sql,
        "columns": columns,
        "rows": rows,
        "row_count": count,
        "explanation": explanation,
        "error": None
    }

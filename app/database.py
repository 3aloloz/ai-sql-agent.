"""
database.py - SQLite database management with read-only connection mode.
Ensures query execution cannot mutate the database under any circumstance.
"""

import sqlite3
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database.db"


def get_db_path() -> str:
    return str(DB_PATH)


def get_read_only_connection() -> sqlite3.Connection:
    """
    Open SQLite database in strict Read-Only URI mode.
    Even if an injection bypassed the validator, SQLite engine itself
    will raise an operational error on any write attempt.
    """
    if not DB_PATH.exists():
        # Auto-initialize and seed if running in fresh cloud deployment
        from data.seed_data import init_db
        init_db()
    
    # SQLite URI mode for read-only
    uri_path = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri_path, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(sql: str, max_rows: int = 100) -> Tuple[List[str], List[Dict[str, Any]], int]:
    """
    Executes a SELECT query on the read-only connection.
    Returns:
        (column_names, rows_as_dicts, total_row_count)
    """
    conn = get_read_only_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Extract column names
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
        else:
            columns = []
        
        # Fetch up to max_rows
        raw_rows = cursor.fetchmany(max_rows)
        rows = [dict(row) for row in raw_rows]
        return columns, rows, len(rows)
    finally:
        conn.close()


def get_schema_summary() -> str:
    """
    Inspects live SQLite schema to provide an accurate description to the LLM.
    """
    conn = get_read_only_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        summary = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            cols = cursor.fetchall()
            col_strs = [f"{col['name']} ({col['type']})" for col in cols]
            summary.append(f"Table: {table}\n  Columns: {', '.join(col_strs)}")
        
        return "\n\n".join(summary)
    finally:
        conn.close()

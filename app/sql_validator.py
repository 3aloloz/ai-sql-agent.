"""
sql_validator.py - Security and validation layer for generated SQL queries.
Enforces:
1. Pure SELECT statements only (Read-Only).
2. Blocks destructive verbs: DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE, etc.
3. Single statement restriction (no semicolon chaining or stacked queries).
4. Blocks comment smuggling and PRAGMA execution.
5. AST validation using sqlglot (with regex fallback).
"""

import re
from typing import Tuple
try:
    import sqlglot
    from sqlglot import exp
    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False


# Forbidden SQL keywords / verbs
FORBIDDEN_KEYWORDS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bREPLACE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bVACUUM\b",
    r"\bREINDEX\b",
]

FORBIDDEN_PATTERN = re.compile("|".join(FORBIDDEN_KEYWORDS), re.IGNORECASE)


class SQLValidationError(Exception):
    """Raised when an SQL query violates security or syntax rules."""
    pass


def clean_sql(raw_sql: str) -> str:
    """
    Strips markdown code blocks, trailing semicolons, and excess whitespace.
    """
    cleaned = raw_sql.strip()
    # Strip markdown ```sql ... ```
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    
    # Strip trailing semicolons
    cleaned = cleaned.rstrip(";").strip()
    return cleaned


def validate_sql(raw_sql: str) -> Tuple[bool, str, str]:
    """
    Validates the given SQL string.
    Returns:
        (is_valid: bool, cleaned_sql: str, error_message: str)
    """
    if not raw_sql or not raw_sql.strip():
        return False, "", "Empty query provided."

    cleaned = clean_sql(raw_sql)

    # 1. Check for multiple statements (prevent query chaining via semicolon)
    # Exclude semicolons that might be inside single/double quotes
    # Simple check: splitting by ; after removing string literals
    temp_no_strings = re.sub(r"'[^']*'|\"[^\"]*\"", "", cleaned)
    if ";" in temp_no_strings:
        return False, cleaned, "Security Violation: Multiple SQL statements (semicolon chaining) are forbidden."

    # 2. Check for forbidden destructive keywords
    match = FORBIDDEN_PATTERN.search(cleaned)
    if match:
        forbidden_word = match.group(0).upper()
        return False, cleaned, f"Security Violation: Destructive command '{forbidden_word}' is strictly prohibited. Only read-only SELECT queries are allowed."

    # 3. Must begin with SELECT or WITH (for CTEs)
    first_token = cleaned.split()[0].upper()
    if first_token not in ("SELECT", "WITH"):
        return False, cleaned, f"Security Violation: Query must start with 'SELECT' or 'WITH'. Received: '{first_token}'"

    # 4. AST validation using sqlglot if installed
    if HAS_SQLGLOT:
        try:
            expressions = sqlglot.parse(cleaned, read="sqlite")
            if not expressions:
                return False, cleaned, "Invalid SQL syntax: Query could not be parsed."
            if len(expressions) > 1:
                return False, cleaned, "Security Violation: Multiple SQL statements detected in AST."
            
            root_expr = expressions[0]
            # Ensure the root expression is either Select or Union/CTE leading to Select
            if not isinstance(root_expr, (exp.Select, exp.Union)):
                return False, cleaned, f"Security Violation: Expected SELECT expression, got '{type(root_expr).__name__}'."
        except sqlglot.errors.ParseError as e:
            return False, cleaned, f"SQL Syntax Error: {str(e)}"

    return True, cleaned, ""

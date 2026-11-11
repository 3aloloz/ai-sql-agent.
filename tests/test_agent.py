"""
test_agent.py - Comprehensive automated test suite for AI SQL Agent.
Tests:
1. 5 Core Assignment Questions
2. Conversational Follow-up (Memory Context)
3. Malicious Injection Attack (DROP TABLE)
4. Out-of-Scope / Vague Question
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.agent import run_agent
from app.conversation import conversation_manager


def test_full_pipeline():
    session_id = "test_eval_session"
    conversation_manager.clear_session(session_id)

    print("=================================================================")
    print("      AI-POWERED SQL AGENT ASSIGNMENT COMPREHENSIVE TEST        ")
    print("=================================================================\n")

    # 1. Core Question 1
    print("--> Test 1: Top 10 customers by revenue")
    r1 = run_agent("What are the top 10 customers by revenue?", session_id=session_id)
    assert r1["success"] is True, f"Failed: {r1['error']}"
    assert len(r1["rows"]) <= 10
    print(f"Generated SQL:\n{r1['sql']}")
    print(f"Explanation: {r1['explanation']}")
    print(f"Rows count: {r1['row_count']}\n")

    # 2. Follow-up: Only those from Egypt
    print("--> Test 2: Conversational Follow-up: 'Only those from Egypt'")
    r2 = run_agent("Only those from Egypt", session_id=session_id)
    assert r2["success"] is True, f"Failed: {r2['error']}"
    print(f"Generated SQL:\n{r2['sql']}")
    print(f"Explanation: {r2['explanation']}")
    print(f"Rows count: {r2['row_count']}\n")

    # 3. Core Question 2
    print("--> Test 3: Revenue last month")
    r3 = run_agent("What was the revenue last month?", session_id=session_id)
    assert r3["success"] is True, f"Failed: {r3['error']}"
    print(f"Generated SQL:\n{r3['sql']}")
    print(f"Explanation: {r3['explanation']}")
    print(f"Rows count: {r3['row_count']}\n")

    # 4. Core Question 3
    print("--> Test 4: Country with highest average order value")
    r4 = run_agent("Which country has the highest average order value?", session_id=session_id)
    assert r4["success"] is True, f"Failed: {r4['error']}"
    print(f"Generated SQL:\n{r4['sql']}")
    print(f"Explanation: {r4['explanation']}")
    print(f"Rows count: {r4['row_count']}\n")

    # 5. Core Question 4
    print("--> Test 5: Customers without orders in last 90 days")
    r5 = run_agent("List customers without orders in the last 90 days", session_id=session_id)
    assert r5["success"] is True, f"Failed: {r5['error']}"
    print(f"Generated SQL:\n{r5['sql']}")
    print(f"Explanation: {r5['explanation']}")
    print(f"Rows count: {r5['row_count']}\n")

    # 6. Core Question 5
    print("--> Test 6: Percentage of cancelled orders")
    r6 = run_agent("What is the percentage of cancelled orders?", session_id=session_id)
    assert r6["success"] is True, f"Failed: {r6['error']}"
    print(f"Generated SQL:\n{r6['sql']}")
    print(f"Explanation: {r6['explanation']}")
    print(f"Rows count: {r6['row_count']}\n")

    # 7. Security Rejection Test: Malicious Injection
    print("--> Test 7: Security check on DROP TABLE injection")
    r7 = run_agent("DROP TABLE customers;", session_id=session_id)
    assert r7["success"] is False, "Security failed: Destructive query was allowed!"
    print(f"Security Alert Blocked: {r7['error']}")
    print("PASS: Destructive command was rejected successfully.\n")

    # 8. Unclear / Out of Scope Question
    print("--> Test 8: Out of scope question")
    r8 = run_agent("What is the weather in Tokyo right now?", session_id=session_id)
    assert r8["success"] is False
    print(f"Explanation: {r8['explanation']}")
    print("PASS: Unanswerable query handled properly.\n")

    print("=================================================================")
    print("         ALL 8 TEST SCENARIOS PASSED WITH 100% SUCCESS           ")
    print("=================================================================")


if __name__ == "__main__":
    test_full_pipeline()

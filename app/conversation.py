"""
conversation.py - Multi-turn conversation and session state manager.
Maintains history of user queries, generated SQL, and human answers
to provide contextual follow-up capabilities (e.g., "Only those from Egypt").
"""

from typing import Dict, List, Any
import datetime


class ConversationManager:
    def __init__(self):
        # Maps session_id -> list of turn dicts
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}

    def get_session(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        return self._sessions[session_id]

    def add_interaction(
        self,
        session_id: str,
        question: str,
        sql: str,
        explanation: str,
        is_error: bool = False
    ) -> None:
        history = self.get_session(session_id)
        history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "question": question,
            "sql": sql,
            "explanation": explanation,
            "is_error": is_error,
        })
        # Keep recent 10 turns to avoid unbounded prompt growth
        if len(history) > 10:
            self._sessions[session_id] = history[-10:]

    def get_history_summary_for_prompt(self, session_id: str) -> str:
        """
        Formats recent turns as contextual guidance for SQL generation.
        """
        history = self.get_session(session_id)
        if not history:
            return "No previous conversation history."

        lines = []
        for i, turn in enumerate(history[-4:], start=1):
            status = "ERROR" if turn.get("is_error") else "SUCCESS"
            lines.append(f"Turn {i} [{status}]:")
            lines.append(f"  User Question: {turn['question']}")
            if turn.get("sql"):
                lines.append(f"  Generated SQL: {turn['sql']}")
            if turn.get("explanation"):
                lines.append(f"  Answer: {turn['explanation'][:150]}...")
        return "\n".join(lines)

    def clear_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id] = []


# Global singleton instance
conversation_manager = ConversationManager()

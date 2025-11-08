"""Agent that handles administrative or scheduling related requests."""

from __future__ import annotations

from core import AgentQuery, AgentResult, BaseAgent


class AdministrationAgent(BaseAgent):
    """Assists with appointments, reminders, and general admin logistics."""

    KEYWORDS = {
        "schedule",
        "meeting",
        "appointment",
        "remind",
        "due date",
        "deadline",
        "calendar",
    }

    def __init__(self) -> None:
        super().__init__(name="administration")

    def can_handle(self, query: AgentQuery) -> bool:
        lower = query.text.lower()
        return any(keyword in lower for keyword in self.KEYWORDS)

    def handle(self, query: AgentQuery) -> AgentResult:
        response = (
            "It sounds like you have an administrative task. "
            "I can help you draft reminders, create calendar events, "
            "or list follow-up steps. Please provide details such as dates, "
            "times, and participants."
        )
        return AgentResult(text=response)

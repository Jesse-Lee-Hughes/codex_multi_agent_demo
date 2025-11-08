"""Agent that handles open-ended research tasks."""

from __future__ import annotations

from core import AgentQuery, AgentResult, BaseAgent


class ResearchAgent(BaseAgent):
    """Performs background research and information gathering."""

    KEYWORDS = {
        "research",
        "investigate",
        "background",
        "learn about",
        "study",
        "compare",
        "analysis",
    }

    def __init__(self) -> None:
        super().__init__(name="research")

    def can_handle(self, query: AgentQuery) -> bool:
        lower = query.text.lower()
        return any(keyword in lower for keyword in self.KEYWORDS)

    def handle(self, query: AgentQuery) -> AgentResult:
        response = (
            "I'll gather relevant information, sources, and comparisons for your topic. "
            "Please share any constraints or preferred formats so I can tailor the output."
        )
        return AgentResult(text=response)

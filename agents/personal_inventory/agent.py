"""Agent that helps the user locate personal belongings."""

from __future__ import annotations

from core import AgentQuery, AgentResult, BaseAgent


class PersonalInventoryAgent(BaseAgent):
    """Suggests strategies to locate misplaced personal items."""

    KEYWORDS = {"key", "keys", "wallet", "phone", "glasses"}

    def __init__(self) -> None:
        super().__init__(name="personal_inventory")

    def can_handle(self, query: AgentQuery) -> bool:
        lower = query.text.lower()
        return any(keyword in lower for keyword in self.KEYWORDS)

    def handle(self, query: AgentQuery) -> AgentResult:
        suggestions = [
            "Retrace your steps over the last few rooms visited.",
            "Check surfaces near the front door or charging stations.",
            "Look inside bags, jacket pockets, or drawers you used today.",
            "Use Bluetooth trackers or smart-home routines if you have them configured.",
        ]

        response = (
            "Here are a few ideas to help locate your keys:\n"
            + "\n".join(f"- {item}" for item in suggestions)
        )
        return AgentResult(text=response)

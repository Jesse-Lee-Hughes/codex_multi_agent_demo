"""Coordinator agent that routes queries to the appropriate specialist."""

from __future__ import annotations

from core import AgentQuery, AgentResult, RoutingAgent

from agents.administration import AdministrationAgent
from agents.personal_inventory import PersonalInventoryAgent
from agents.research import ResearchAgent


class RoutingCoordinator(RoutingAgent):
    """Routes the incoming query to one of the specialist agents."""

    def __init__(self) -> None:
        super().__init__(
            name="router",
            agents=[
                PersonalInventoryAgent(),
                AdministrationAgent(),
                ResearchAgent(),
            ],
        )

    def handle(self, query: AgentQuery) -> AgentResult:
        result = super().handle(query)
        if result.routed_to is None:
            # Default to the research agent when no direct match is found.
            research = self.registry["research"]
            result = research.handle(query)
            result.routed_to = research.name
            result.debug.setdefault("router", self.name)
            result.debug["fallback"] = True
        return result

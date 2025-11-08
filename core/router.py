"""Routing agent implementation that delegates to registered sub-agents."""

from __future__ import annotations

from typing import Iterable

from .base import BaseAgent
from .contexts import AgentQuery, AgentResult
from .registry import AgentRegistry


class RoutingAgent(BaseAgent):
    """Generic routing agent that delegates to the first matching sub-agent."""

    def __init__(self, name: str, agents: Iterable[BaseAgent]) -> None:
        super().__init__(name=name)
        self.registry = AgentRegistry(agents)

    def can_handle(self, query: AgentQuery) -> bool:  # pragma: no cover - router always handles
        return True

    def handle(self, query: AgentQuery) -> AgentResult:
        for agent in self.registry.values():
            if agent.can_handle(query):
                result = agent.handle(query)
                result.routed_to = agent.name
                result.debug.setdefault("router", self.name)
                return result

        return AgentResult(
            text=(
                "I could not determine the best assistant for your request. "
                "Please try rephrasing the query."
            ),
            routed_to=None,
            debug={"router": self.name, "reason": "no matching agent"},
        )

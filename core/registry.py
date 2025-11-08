"""Utility registry used by the router to manage child agents."""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, MutableMapping

from .base import BaseAgent
from .contexts import AgentQuery


class AgentRegistry(MutableMapping[str, BaseAgent]):
    """Simple dictionary-backed registry for agents."""

    def __init__(self, agents: Iterable[BaseAgent] | None = None) -> None:
        self._agents: Dict[str, BaseAgent] = {}
        if agents is not None:
            for agent in agents:
                self.register(agent)

    def __getitem__(self, key: str) -> BaseAgent:
        return self._agents[key]

    def __setitem__(self, key: str, value: BaseAgent) -> None:
        self._agents[key] = value

    def __delitem__(self, key: str) -> None:
        del self._agents[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._agents)

    def __len__(self) -> int:
        return len(self._agents)

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def find_best_agent(self, query_text: str) -> BaseAgent | None:
        """Return the first agent whose matcher accepts the query."""

        for agent in self._agents.values():
            if agent.can_handle(AgentQuery(text=query_text)):
                return agent
        return None

"""Abstract base class for agents in the sample system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from .contexts import AgentQuery, AgentResult


class BaseAgent(ABC):
    """Common interface that all concrete agents must implement."""

    name: Final[str]

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def can_handle(self, query: AgentQuery) -> bool:
        """Return True if the agent is a good match for the query."""

    @abstractmethod
    def handle(self, query: AgentQuery) -> AgentResult:
        """Produce a response for the query."""

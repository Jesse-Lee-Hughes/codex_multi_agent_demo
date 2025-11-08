"""Helpers for wiring Google Agent Development Kit agents into the system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .contexts import AgentQuery, AgentResult

try:  # pragma: no cover - optional import
    from google.agents import Agent as GoogleAgent
except ModuleNotFoundError:  # pragma: no cover - executed only when ADK missing
    GoogleAgent = None  # type: ignore[assignment]


class ADKNotAvailableError(RuntimeError):
    """Raised when code requires the Google ADK but the package is missing."""


@dataclass
class ADKConfig:
    """Configuration for instantiating an ADK-backed agent."""

    agent_name: str
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ADKAgentAdapter:
    """Convenience wrapper around a Google ADK agent instance."""

    def __init__(self, config: ADKConfig):
        if GoogleAgent is None:
            raise ADKNotAvailableError(
                "google-agents package is not installed. Install it to use the ADK adapter."
            )

        params = config.parameters or {}
        model = config.model or "models/gemini-1.5-flash-latest"
        # This call mirrors the documented constructor in the Google ADK samples.
        self._agent = GoogleAgent(
            name=config.agent_name,
            model=model,
            **params,
        )

    def run(self, query: AgentQuery) -> AgentResult:
        """Invoke the wrapped Google ADK agent."""

        response = self._agent.generate_response(query.text)
        text = getattr(response, "text", str(response))
        return AgentResult(text=text, routed_to=self._agent.name)

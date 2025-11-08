"""Shared request/response dataclasses used across agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class AgentQuery:
    """Represents a user request entering the agent system."""

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentResult:
    """Represents an agent response as it flows back to the caller."""

    text: str
    routed_to: Optional[str] = None
    debug: Dict[str, Any] = field(default_factory=dict)

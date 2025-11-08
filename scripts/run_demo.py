"""Simple demo runner for the multi-agent system."""

from __future__ import annotations

from agents.routing import RoutingCoordinator
from core import AgentQuery


def run_demo(query_text: str) -> None:
    """Run the coordinator against a single query and print the response."""

    coordinator = RoutingCoordinator()
    result = coordinator.handle(AgentQuery(text=query_text))
    routed = result.routed_to or "none"

    print(f"Router: {coordinator.name}")
    print(f"Delegated to: {routed}")
    print("Response:")
    print(result.text)


if __name__ == "__main__":
    run_demo("I want you to summarize my emails and create a brief overview in my calendar at 8 am tomorrow")

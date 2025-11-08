from agents.routing import RoutingCoordinator
from core import AgentQuery


def test_router_sends_key_query_to_personal_inventory() -> None:
    coordinator = RoutingCoordinator()
    result = coordinator.handle(AgentQuery(text="Help me find my keys"))

    assert result.routed_to == "personal_inventory"
    assert "Here are a few ideas" in result.text
    assert "- Retrace your steps" in result.text


def test_router_falls_back_to_research() -> None:
    coordinator = RoutingCoordinator()
    result = coordinator.handle(AgentQuery(text="Explain the history of chess clocks"))

    assert result.routed_to == "research"
    assert result.debug.get("fallback") is True

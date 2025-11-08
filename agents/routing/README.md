# Routing Coordinator

The routing coordinator is the system's entry point. It inspects incoming user queries, selects an appropriate specialist agent, and passes the request along. The default priority order is:

1. `personal_inventory`
2. `administration`
3. `research` (also used as the fallback)

## ADK Notes

In a full Google ADK deployment each specialist can wrap an ADK agent configured with its own tools and prompt. The coordinator itself can remain lightweight, using simple keyword heuristics or an ADK classifier model depending on latency budgets.

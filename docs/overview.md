# Multi-Agent Sample Overview

This repository demonstrates a minimal multi-agent system assembled with lightweight Python classes. Each specialist agent can wrap a Google Agent Development Kit (ADK) agent, allowing you to plug in Gemini models, tools, and prompt templates tailored to the task.

## Components

- `agents/routing` – entry point that routes user queries.
- `agents/personal_inventory` – assists with locating personal items such as keys.
- `agents/administration` – covers scheduling and reminders.
- `agents/research` – handles open-ended investigations and serves as the fallback.
- `core/` – shared plumbing (agent interface, routing, and optional ADK adapter).
- `scripts/run_demo.py` – convenience script that runs the orchestrator on a single query.

## Integrating the Google ADK

1. Install the ADK and export required environment variables (for example `GOOGLE_API_KEY`).
2. Replace or augment the specialist agents with instances of `core.google_adk.ADKAgentAdapter`, passing the relevant ADK configuration.
3. Optional: swap `RoutingCoordinator`'s keyword heuristics with an ADK classifier agent for smarter routing.

## Local Development

Create a virtual environment and install the project in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Before sending changes, lint and test:

```bash
ruff check .
ruff format .
mypy agents core
pytest
```

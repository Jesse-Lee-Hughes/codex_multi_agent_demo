# Research Agent

The research agent responds to exploratory questions and aggregates findings. Backed by the Google Agent Development Kit, it can chain knowledge graph calls or web search tools to produce succinct digests.

## Environment

Configure ADK-related credentials such as `GOOGLE_API_KEY` before running the orchestrator. Tool-specific configuration (for example web search quotas) should remain outside of version control.

## Behavior

- Detects requests for analyses, comparisons, or background information.
- Prompts the user for clarifying data to keep responses focused.

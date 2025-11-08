# Personal Inventory Agent

This agent focuses on helping users track and recover personal items such as keys, wallets, phones, or glasses. It is intended to run on top of the Google Agent Development Kit (ADK), where it can be associated with a small-talk or task-oriented Gemini model.

## Environment

Set any ADK-related environment variables (for example `GOOGLE_API_KEY`) before running the system. The agent itself is stateless and does not persist personal information.

## Behavior

- Accepts queries mentioning personal items.
- Suggests practical steps and smart-home automations that may help recover the item.

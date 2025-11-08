# Administration Agent

This agent takes care of day-to-day logistics such as meetings, appointments, reminders, and checklists. It is a good target for ADK actions that integrate with Google Calendar or task systems.

## Environment

Provide credentials through environment variables supported by the Google Agent Development Kit (for example `GOOGLE_API_KEY`). Additional integration-specific secrets should stay in local `.env` files.

## Behavior

- Detects scheduling and reminder language.
- Guides the user to supply the metadata required to complete administrative tasks.

# Implementation Plan - Journey Agent (Stage 2) Overhaul

Refactor `journey_agent.py` to match the "Agente 2" specifications provided by the user.

## User Objectives
- Use the specific "Consultor experto en Buyer Personas y HubSpot" prompt.
- Implement sequential journey mapping (Awareness -> Consideration -> Decision).
- Generate specific deliverables: Narrative, Markdown Table, CSV Block, and HubSpot KPIs.

## Proposed Changes

### 1. `backend/app/agents/journey_agent.py`
- **Replace `SYSTEM_PROMPT`**: Inject the full text from `Agente2.md`.
- **Logic Update**:
    - **Context Injection**: Automatically feed the Stage 1 Buyer Persona into the prompt as the "ingested" data.
    - **State Management**: The agent needs to track the current phase of the conversation (Awareness, Consideration, etc.).
    - **JSON Output**: Ensure the final JSON structure includes fields for `narrative`, `markdown_table`, `csv_block`, and `hubspot_props`.

### 2. Output Schema
Update the expected output schema to handle the new format.
```json
{
  "buyer_journey": {
     "narrative": "Full narrative...",
     "stages": [...]
  },
  "markdown_table": "| Header | ... |",
  "csv_copy": "Column1,Column2...",
  "hubspot_props": [...]
}
```

## Verification Plan

### Manual Verification
1.  **Reset Stage 2**: Use the UI to reset Stage 2 (or create a new account/stage flow).
2.  **Initial Chat**: Confirm the Agent starts by acknowledging the Stage 1 Persona (acting as the "uploaded file") and proposes starting with Awareness.
3.  **Flow Test**: Answer questions for Awareness -> Consideration -> Decision.
4.  **Completion**: Verify the final output contains the Table, Narrative, and CSV block.

### Automated/Subagent Verification
1.  Run the browser subagent to step through the chat or use `demo_service` (Auto-Chat) if updated.
2.  Since Auto-Chat might fail with the new complex logic without updates, manual browser verification is safer.

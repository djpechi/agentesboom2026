# Implementation Plan - Deliverables View & Auto-Chat Stability

This plan addresses the user's feedback regarding the infinite loop in Auto-Chat and finalizes the improvements to the Deliverables View.

## User Objectives
1.  **Fix Auto-Chat Infinite Loop**: Prevent the "No entendí bien" cycle between the Agent and the Simulator.
2.  **Verify Deliverables View**: Ensure the "Scaling Up" table and other deliverables are displayed detailed and correctly (Full Width).
3.  **Ensure Robustness**: Add safeguards to the demo service to prevent future loops.

## Proposed Changes

### 1. Robustness in Agent Response Parsing (Completed)
- **File**: `backend/app/agents/booms_agent.py`
- **Change**: Updated the JSON parsing logic to fallback to alternative keys (`message`, `response`, `text`) if `agentMessage` is missing. This prevents the default "No entendí bien" trigger when the LLM uses a slightly different schema.

### 2. Auto-Chat Loop Safeguard
- **File**: `backend/app/services/demo_service.py`
- **Change**: Implement a loop detection mechanism.
    - Track text hashes of recent messages.
    - If the Agent sends the same message 3 times in a row, force the loop to break or inject a "system reset" message to the simulator.
    - Reduce `max_iterations` from 60 to 45 to prevent excessive runaways.

### 3. Deliverables View Verification
- **File**: `frontend/src/pages/StageChat.tsx` / `frontend/src/components/Stage1Output.tsx`
- **Status**: Verified via Browser Subagent. The view now correctly toggles to full width and checks for the existence of the table.
- **Action**: No further code changes needed here unless user requests specific styling tweaks.

### 4. Orchestrator Integration (Upcoming)
- **Context**: Once Stage 1 is stable, we move to Stage 2.
- **Action**: Ensure `StageChat` correctly transitions to Stage 2 upon completion.

## Verification Plan

### Auto-Chat Stability
- **Action**: Trigger Auto-Chat on a new "Test Company" account.
- **Expectation**: The chat should progress through company context and buyer persona questions without getting stuck.
- **Fail Condition**: If the log shows repeated "No entendí bien" messages.

### Deliverables View
- **Action**: Completed stage view should show the "View Deliverables" toggle.
- **Expectation**: Clicking it reveals the `Stage1Output` component in full width (no chat sidebar).

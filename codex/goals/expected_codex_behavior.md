# Expected Codex Behavior

This document outlines how Codex processes prompts and generates work items.

## Prompt conversion with `sf ask`

1. The command loads the template at
   `codex/prompts/work_item_generator.md`.
2. The user question is appended to the system prompt.
3. The messages are sent to the OpenAI API.
4. The response text becomes a work item printed to the terminal.

Codex should return concise tasks that follow the template structure.

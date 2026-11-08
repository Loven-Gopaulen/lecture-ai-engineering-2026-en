# Lecture 03 Answers

## Exercises

- Differences between the Lecture 01 (bare LLM) and agent answers:
  - The bare LLM answer is more general and may rely on prior knowledge, without checking the course glossary or lecture context.
  - The agent answer is grounded in the course glossary: it looks up each term (`LoRA`, `QLoRA`) and then answers using the course definition and a short conceptual comparison, ending with the relevant lecture label.
  - The agent is more consistent with the course material and gives a brief reasoning prompt instead of a generic explanation.
- Tool calls shown by `--trace` (tool names and arguments):
  - `search_glossary({'query': 'LoRA'})`
  - `search_glossary({'query': 'QLoRA'})`
- Number of LLM calls for one question (`requests`):
  - `requests=2`
- Tool added and the description in its docstring:
  - Added `make_quiz(lecture: int) -> str`.
  - Docstring: "Create a quick review question from the glossary for a lecture. Use when the user asks for a review question, quiz question, or practice question from a specific session, such as 'Give me one review question from Lecture 02.' This tool helps the model generate a simple self-test by picking a term from the requested lecture and returning both the question and its answer."

## Homework

- Level attempted: Implementation
- What you did:
  - Added `save_learning_log(topic: str, note: str) -> str` in [app/tools.py]
  - Registered the tool in [app/agent.py] with `requires_approval=True`.
  - Set the agent's output type to `[str, DeferredToolRequests]` and added a CLI approval loop that asks the user to confirm and resumes the run with `DeferredToolResults(approvals={...})`.
  - The CLI now prompts with a message like: "Allow save_learning_log with arguments {...}? [y/N]" and only continues after a `yes`.
- Results:
  - With approval `yes`, a JSON file is created in `learning_log/` and the save completes.
  - With approval `no`, the tool is denied and no file is created.
  - `uv run pytest -q` still passes after the fix.
- Observations and questions:
  - This design is useful for irreversible actions because it keeps final execution under explicit user control.

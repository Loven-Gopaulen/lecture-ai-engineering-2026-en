# Lecture 06 answers

## Exercises

<!-- Paste the original [tool call] lines. Leave unfinished steps blank. -->

- Tool name in STEP 1 — glossary_search_glossary
- STEP 2 [tool call] — glossary_search_glossary({'query': '3 levels'})
- STEP 3 [tool call] — fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 [tool call] — aws_aws___search_documentation({'search_phrase': 'Amazon S3 versioning overview', 'topics': ['general']})
- Observations and questions — The local glossary MCP server, published fetch MCP server, and externally hosted AWS MCP server all connected successfully. The tools were exposed to the agent with the expected names. The initial `uvx` download timed out, but retrying with `UV_HTTP_TIMEOUT=120` succeeded. The AWS request returned a temporary 503 once, then succeeded on retry.
## Homework

<!-- Complete one of the Basic, Implementation, or Advanced levels. -->

- Level attempted (Basic / Implementation / Advanced) — Implementation
- What you did — Added `make_quiz` in `app/tools.py`, registered it on the glossary MCP server, and returned lecture source material for valid requests. For an unavailable lecture, the tool lists available lectures.
- Results — `glossary_make_quiz` appeared in `--list-tools`. The `--trace` run for “Make a quiz for Lecture 99.” showed `{'lecture': 99}` in the tool call and “Lecture 99 does not exist. Available lectures: Lecture 01, Lecture 02, Lecture 03, Lecture 04, Lecture 06.” in the tool return. The model then told the user to choose one of the available lectures.
- Observations and questions — The clear return message reached the model without raising an exception, and the model used it to avoid inventing a quiz for an unavailable lecture.

# Lecture 01 Answers

## Exercises

- Model's answer to the course-specific question (the 3 homework levels; a summary is fine):
- What you noticed when comparing it with the correct meaning in the glossary:
- Token counts you displayed (input / output):

## Homework

- Level attempted: `Basic`
- What you did: 
Executed the same query (`"What are the “3 levels” in the AIE2026 course homework?"`) across three different models (gemini-3.5-flash-lite, gemini-3.8-flash, and gemini-3.5-flash) using the `AIE_MODEL` environment variable.

- Results:
  - gemini-3.5-flash-lite: Recognized that "AIE2026" was a specific identifier outside its knowledge base and refrained from guessing, prompting for context (19 input / 175 output tokens).
  - gemini-3.8-flash: Assumed standard academic frameworks and provided two hypothetical structures (Tiered Grading vs. AI Abstraction) (19 input / 578 output tokens).
  - gemini-3.5-flash: Confidently hallucinated a highly detailed, 3-tier AI engineering stack (Baseline, Application & Integration, Production & Evals) (19 input / 723 output tokens).
  None hit the actual glossary terms (Basic, Implementation, Advanced)

- Observations and questions:
Lite models tend to acknowledge missing context, whereas larger models generate confident, lengthy hallucinations when queried on private domain terms. Token usage varies dramatically for the exact same prompt depending on the model tier (from 175 tokens up to 723 tokens), directly influencing response latency and API cost.



- Level attempted: `Implementation`
- What you did:
  Modified `app/ask.py` to use `client.chats.create(model=MODEL)` and an interactive `while` loop with `chat.send_message()`, enabling multi-turn conversation memory and tested it across three sequential turns with `gemini-3.5-flash-lite`.

- Results:
  - Turn 1: Asked about the 3 homework levels. Model stated it lacked context (`input_tokens=18`, `output_tokens=77`).
  - Turn 2: Provided the ground-truth terms ("Basic, Implementation, Advanced"). Model summarized what each level meant (`input_tokens=107`, `output_tokens=275`).
  - Turn 3: Asked *"What would be the roadmap to answer the Basic level?"*. Model correctly recalled what "Basic" meant from Turn 2 without needing the context restated (`input_tokens=395`, `output_tokens=467`).
- Observations and questions:
  - The model successfully referenced facts provided in previous turns, proving state retention across messages using `chat.send_message()`.
  - The prompt token count grew steadily across turns ($18 to 107 to 395$). Because `client.chats.create()` automatically appends all previous prompts and completion outputs into the active message context, input costs and latency compound with each turn in long chat sessions.


- Level attempted: Advanced
- What you did:
  - Added latency (`time.perf_counter()`) and generation throughput (`tokens/sec`) logging to `app/ask.py`.
  - Benchmarked two prompts; a general concept ("What is LoRA?") and a course-specific term ("What are the 3 homework levels in the AIE2026 course?")—across `gemini-3.5-flash-lite` and `gemini-3.5-flash`.
  - Evaluated the impact of model latency, throughput, and token consumption on Gemini API Free Tier rate limits.

- Results:
  
  | Model | Question | Latency | Input Tokens | Output Tokens | Generation Speed |
  | `gemini-3.5-flash-lite` | "What is LoRA?" | 3.11s | 6 | 765 | 246.16 tokens/sec |
  | `gemini-3.5-flash` | "What is LoRA?" | 11.86s | 6 | 889 | 74.97 tokens/sec |
  | `gemini-3.5-flash-lite` | "3 homework levels" | 1.56s | 18 | 236 | 151.25 tokens/sec |
  | `gemini-3.5-flash` | "3 homework levels" | 8.13s | 18 | 433 | 53.27 tokens/sec |

- Observations and Discussion on Free-Tier Limits:
  - Speed & Latency: `gemini-3.5-flash-lite` is significantly faster (1.5s–3.1s) with higher throughput (up to ~246 tokens/sec), while `gemini-3.5-flash` is much slower (8.1s–11.8s).
  - Output Verbosity: Standard Flash generates much longer answers (nearly 2x the tokens on the course prompt), increasing latency without adding necessary value.
  - Free-Tier Rate Limits:
    - TPM (Tokens/Min): Flash's verbose outputs drain your token allowance quickly. Lite conserves TPM by keeping responses compact.
    - RPM (Requests/Min): Fast responses from Lite allow quick turnaround, but rapid sequential calls still risk hitting the 15 RPM cap.
    - Strategy: Route simple queries or initial classification tasks to `flash-lite` to minimize latency and stretch your free daily quota.
"""Lecture 01: a script that asks a bare LLM a single question.

Usage:
    uv run python -m app.ask "What is LoRA?"
    uv run python -m app.ask            # Ask a course-specific question if none is supplied

A "bare" call with no tools or conversation history.
Check that, when asked about course-specific information, it either says "I don't know"
or gives a plausible general answer (which differs from the actual course).
(In Lecture 03, improve it by making an agent that can search the glossary.)
"""

import argparse
import time

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

DEFAULT_QUESTION = "What are the 3 homework levels in the AIE2026 course?"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())

    start_time = time.perf_counter()
    response = client.models.generate_content(model=MODEL, contents=question)
    elapsed_time = time.perf_counter() - start_time

    usage = response.usage_metadata
    if usage:
        in_tokens = usage.prompt_token_count or 0
        out_tokens = usage.candidates_token_count or 0
        speed = out_tokens / elapsed_time if elapsed_time > 0 else 0

        print(f"[metrics] Latency: {elapsed_time:.2f}s")
        print(f"[usage] input_tokens={in_tokens} output_tokens={out_tokens}")
        print(f"[speed] {speed:.2f} tokens/sec\n")
    else:
        print("[usage] Token counts unavailable\n")

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark model response times and token counts")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print(f"[question] {args.question}\n")

    try:
        print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
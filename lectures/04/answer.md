# Lecture 04 Answers

## Exercises

- Agreement by criterion (before revision): Grounding 9/9, Scope 9/10, Hint 10/10, Clarity 10/10, Lecture marker 9/10

- Number of items needing review (before revision): 1

- Criterion revised and the policy added: Grounding. I added the policy that when an answer explicitly states that information is not in the glossary and then provides a general explanation, the explanation is not treated as an unsupported assertion; therefore, the judgment is pass.

- Agreement by criterion and number of review items (after revision): Grounding 10/10, Scope 9/10, Hint 10/10, Clarity 10/10, Lecture marker 9/10; number of items needing review: 0

- Items where your labels differed from the instructor's, and your reasons:
  - #07 Lecture marker: False alarm. The code checks whether a `Lecture N` marker appears in the final line. I labeled it pass, but the LLM labeled it fail.
  - #10 Scope: Missed failure. I labeled it fail, but the LLM labeled it pass because the answer addressed a question about the course content or sessions.

- Observations and questions:
  - Revising the Grounding rubric resolved the only needs-review item. The #05 Grounding judgment changed from unsure to pass.
  - The automatically judged coverage increased from 90% to 100%.
  - Overall agreement improved from 8/9 to 9/10.
  - The remaining disagreements concern the Lecture marker and Scope criteria. The Lecture marker is checked mechanically by code, while Scope is more subjective and may require a clearer policy for questions about course sessions.

## Homework

- Level attempted: Implementation

- What you did:
I created a custom evaluation set with
  10 questions in `data/eval/my_cases.jsonl`, including normal cases and
  edge cases such as an absent glossary term, a homework request, an
  out-of-scope question, prompt injection, unclear input, and a nonexistent
  lecture.
  I generated answers with my Lecture 3 agent using:
  ```bash
  uv run python -m app.judge --generate \
    --cases data/eval/my_cases.jsonl

- Results:

    Number of cases: 10
    Grounding agreement: 10/10
    Scope agreement: 10/10
    Hint agreement: 10/10
    Clarity agreement: 10/10
    Lecture marker agreement: 7/10
    Overall agreement: 7/10
    Coverage: 100%
    Needs-review items: 0

The three disagreements were #07, #08, and #09, all for the Lecture marker criterion. In each case, the LLM judged the answer as fail, while my label was pass. The reason reported by the grader was that the code checks whether the final line contains a Lecture N marker.

- Observations and questions:
The custom evaluation set achieved complete agreement for Grounding, Scope, Hint, and Clarity. The only disagreements involved the Lecture marker criterion.
This suggests that the Lecture marker is suitable for code-based checking, because its format can be tested mechanically. Grounding, Scope, Hint, and Clarity require interpreting the meaning and quality of the answer, so they are better evaluated by an LLM or a human.
I would like to confirm whether a Lecture N marker should be required for out-of-scope, unclear, and prompt-injection cases. In particular, I would check cases #07, #08, and #09 to determine whether my labels or the automatic lecture-marker check should be revised.
# Lecture 05 Answers

## Exercises

- Answering model (`[model]` shown during execution): `google:gemini-3.5-flash-lite`
- Comparison question: In Lecture 2, what does LoRA freeze and what does it train? What does QLoRA add?
- Target materials (also record the difference in scope between full context and the other methods):
  - Full context: all lecture materials were supplied to the model at once. The run reported 315,665 characters and 81,725 input tokens.
  - Vector search: the system searched the indexed lecture pages and passed the relevant results to the model.
  - Tree: the system navigated the table of contents from the course root to Lecture 2, the relevant section, and page 52.
  - Graph: the system searched the material graph and followed the relevant page relationships.
  - The search-based methods supplied only selected/retrieved material rather than the complete course corpus.

### Results by Method

| Method | Key points and correctness of the answer | Cited pages and evidence | Time (seconds) | Input/output tokens | Model responses | Estimated generation API cost (USD) |
|---|---|---|---:|---:|---:|---:|
| Full context | Correct. LoRA freezes the original weights and trains low-rank matrices $A$ and $B$. QLoRA adds 4-bit compression of the frozen weights. | Lecture 2, Japanese source p.52 / translated PDF p.75 | 8.45 | 81,725 / 250 | 1 | $0.025142 |
| Vector search | Correct. LoRA freezes the base weights and trains the low-rank adapter; QLoRA adds 4-bit compression. | Lecture 2, Japanese source pp.51–52; translated PDF p.75 | 6.06 | 2,756 / 185 | 2 | $0.001289 |
| Tree | Correct. LoRA freezes the original weights and trains low-rank matrices. QLoRA compresses the frozen weights to 4 bits. | Lecture 2, Japanese source p.52 / translated PDF p.75 | 11.48 | 9,437 / 367 | 5 | $0.003749 |
| Graph | Correct. LoRA freezes the original weights and trains low-rank matrices $A$ and $B$. QLoRA adds 4-bit compression. | Lecture 2, Japanese source pp.51–52 | 3.90 | 5,186 / 321 | 2 | $0.002358 |

- Pages found by running search alone, and what their text confirmed:
  - **Lecture 2, Japanese source p.52 / translated PDF p.75 — “LoRA and QLoRA: adapting a large model on one GPU.”** This directly confirmed that LoRA freezes the original weights and trains only a small delta using matrices $A$ and $B$. It also confirmed that QLoRA stores the original weights at 4 bits.
  - **Lecture 2, Japanese source p.51 — “PEFT: train only part of a model.”** This corroborated the distinction between full fine-tuning, LoRA, and QLoRA.
  - Other returned pages discussed QLoRA exercises and fine-tuning more generally but were not needed for the answer.

- Tool calls shown by `--trace`:
  - **Full context:** no search tool was used; all materials were passed directly to the model.
  - **Vector search:** `search_materials` was called once with a query similar to `LoRA freeze train QLoRA`.
  - **Tree:** `browse_tree` was called four times:
    1. Opened the course table of contents.
    2. Opened Lecture 2.
    3. Opened the section “When and how to adapt the selected model.”
    4. Opened page `lec02-main-p052`.
  - **Graph:** `search_graph` was called once with a query similar to `LoRA freeze train QLoRA add Lecture 2`. It returned Lecture 2 page 52 as the seed.

- Examples where retrieved information was insufficient, or was retrieved but not used in the answer:
  - No method showed a clear evidence failure in these runs.
  - Vector search returned several related pages, but only pages 51–52 were necessary.
  - Tree navigation returned the relevant page successfully after following the table-of-contents path.
  - The full-context method provided the answer but used substantially more input context.
  - An earlier full-context attempt returned an HTTP 503 service-availability error; that attempt was not included in the measurements above.

- Method you would adopt for this use case, your reasons, and limitations of the comparison conditions:
  - I would adopt **vector search/basic RAG** for this use case. It returned the directly relevant evidence, produced a correct answer, and used much less input context and cost than full context.
  - In these measurements, vector search used 2,756 input tokens and cost $0.001289, compared with 81,725 input tokens and $0.025142 for full context.
  - Graph search was also effective and was fastest in this particular run, but its performance may depend on graph structure and query quality.
  - Tree search gives a transparent table-of-contents path and found the correct page, but it used more tokens and took longer in this run.
  - These are single runs with one question, so they do not establish a general performance ranking. API load, caching, query wording, and model variation may affect the results.

- Observations and questions:
  - Retrieval allowed the model to answer correctly while receiving far less context than the full-context method.
  - The relevant evidence was concentrated on Lecture 2 pages 51–52.
  - Full context had the largest input and highest estimated cost.
  - Tree used the most model responses because it browsed several levels of the table of contents.
  - Graph and vector search both reached the relevant page efficiently.
  - A useful follow-up experiment would be to test several questions, including questions whose evidence is spread across different lectures or pages.

## Homework

<!-- Completing any one of Basic, Implementation, or Advanced is sufficient. -->

- Level attempted: **Implementation**
- What I changed:
  - In `app/retrieval.py`, each vector-search hit now includes an `adjacent_pages` list with the immediately previous and next available pages in the same document.
  - Neighbors are ordered by the stored page number (with page ID as a deterministic tie-breaker), not by assuming page IDs are consecutive.
  - The list excludes the hit itself, any page already in the search results, and any adjacent page already included for another hit. Each added page includes its ID, title, PDF-page label, position, and text.
  - Added tests for page-order selection, document boundaries, metadata, and de-duplication.
- Comparison question and conditions:
  - “In Lecture 2, what does LoRA freeze and what does it train? What does QLoRA add?”
  - The model was `google:gemini-3.5-flash-lite`, and the target materials and question were the same as the earlier vector-search run in Exercises. The before/after figures are single runs, so timing may also reflect API and embedding variability.
- Results:

  | Run | Answer and evidence | Time | Input/output tokens | Model responses | Estimated generation API cost |
  |---|---|---:|---:|---:|---:|
  | Normal vector search (before) | Correct; LoRA freezes the base weights and trains low-rank adapters, while QLoRA adds 4-bit weight compression. Cited Lecture 2 pp. 51–52. | 6.06 s | 2,756 / 185 | 2 | $0.001289 |
  | Search with adjacent pages (after) | Correct with the same key points; cited Lecture 2 pp. 51–52. | 15.72 s | 4,588 / 267 | 2 | $0.002044 |

  The after-run search retained the relevant page 52 and page 51 hits. It also added page 50 next to page 51 and page 53 next to page 52. Other returned hits gained adjacent text as well, including pages 59, 46, and 80. The duplicate page 59 was included only once.
- Comparison and observations:
  - **More useful evidence:** page 50 gives the decision sequence leading to fine-tuning and explicitly contrasts knowledge retrieval with behavior changes. It adds relevant background, although the answer was already supported by pages 51–52.
  - **More noise:** page 53 focuses on fine-tuning output format rather than LoRA/QLoRA. The other added pages (59, 46, and 80) are also tangential to this question. The model did not cite these pages, and its answer remained correct.
  - The added context coincided with 1,832 more input tokens, 9.66 seconds more elapsed time, and $0.000755 more estimated generation cost in these runs. The cost excludes embedding and index construction. One run per condition is not enough to conclude that adjacent-page retrieval generally increases latency or cost.
  - Adjacent pages can help when a page’s explanation spans a boundary, but a fixed one-page window can add unrelated material. A larger evaluation across questions is needed to measure the trade-off.
- Questions:
  - Would a query-dependent choice of previous versus next page retain useful context while avoiding irrelevant neighbors?

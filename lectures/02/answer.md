# Lecture 02 Answers

## Exercises

- Model and settings used (from `config` in `result.json`):
"config": {
    "base_model": "Qwen/Qwen3.5-0.8B",
    "revision": "2fc06364715b967f1860aea9cf38778875588b17",
    "seed": 42,
    "num_train_epochs": 20,
    "warmup_steps": 6,
    "lr": 0.0002,
    "lora_r": 16,
    "lora_alpha": 32,
    "max_seq_len": 512,
    "max_new_tokens": 96,
    "gen": {
      "do_sample": false
    }

- Did you run training yourself (`executed_training_myself`): Yes 
- Before training: `format_rate` = 0.09523809523809523 / `content_rate` = 0.0
- After training: `format_rate` = 1.0 / `content_rate` = 0.9047619047619048
- Questions that regressed:
None (0 questions). Before training, format_rate was 9.5% and both_rate was 0%, so no previously passing questions failed after training.

- Failures remaining after training and their types (assertion without evidence / evasion through a confirmation request despite evidence being present / broken format):
Out of the 21 questions, 2 questions failed:
  1. 「成績はいつ出ますか」(When will grades be released?): Failed content_ok because the model answered with an unrelated file-format string instead of flagging for review.
  2. 「オフィスアワーは事前予約が必要ですか」(Is an appointment needed for office hours?): Failed content_ok because it asserted the office hour schedule with `needs_review: false` instead of asking for review.

- Results of knowledge questions (section 6; classification before → after training) and observations:
Before training, all knowledge questions failed with `format_error`. After training:
  - 2 questions correctly produced `needs_review: true` (e.g., teacher name, next lecture topic).
  - 2 questions produced unfounded assertions (`asserted`) with `needs_review: false` (e.g., final assignment deadline).

- What changed and what stayed the same with training:
What Changed:
Format Compliance: Format accuracy (format_rate) increased dramatically from 9.5% to 100%. LoRA training successfully taught the small model to reliably adhere to the requested two-key JSON schema ({"answer": ..., "needs_review": ...}).   
In-Domain Accuracy: Content accuracy (content_rate) rose from 0% to 90.5%. The model learned to output ground-truth FAQ content almost verbatim for questions covered in the training dataset.   

What Stayed the Same:
Judgment on Unknowns: Fine-tuning did not guarantee reliable judgment on ungrounded questions outside the FAQ. The model still makes unfounded assertions with high confidence (needs_review: false) on certain unknown topics instead of consistently requesting review (needs_review: true).   Knowledge Boundaries: Fine-tuning effectively aligns output formatting and style, but it does not instill true self-awareness of the model's underlying knowledge limitations.   

## Homework

### Selected Level
Basic

### Changed Setting
- **Parameter:** `lora_r`[cite: 39]
- **Original:** `16`[cite: 40]
- **Modified:** `32`[cite: 39]

### Results Comparison Table

| Metric | Original Settings (`lora_r=16`) | Modified Settings (`lora_r=32`) |
| :--- | :--- | :--- |
| **Final Loss** | ~0.0140 | 0.015067 |
| **Training Time** | ~260s | 264s |
| **Format Rate (Before / After)** | 9.5% / 100.0% | 9.5% / 100.0% |
| **Content Rate (Before / After)** | 0.0% / 90.5% | 0.0% / 90.5% |

### Discussion: Fine-Tuning Fit vs. Unfit Scenarios
- **When Fine-Tuning Fits:** Enforcing specific output formatting (e.g., JSON schema adherence), domain-specific output style, and structural constraints on model responses.
- **When Fine-Tuning Does Not Fit:** Storing dynamic external facts, resolving queries requiring real-time knowledge, or serving as a replacement for Retrieval-Augmented Generation (RAG).

# Award Criteria Mapping
How the Absolute Zero AI Command Center provides evidence for the Artificial Intelligence
Trailblazer Award. Every row points to where the evidence lives in the app / shared log
(`data/ai_feedback_log.csv`). Nothing here is fabricated — the app only shows real entries.

## A) Problem solved
Each logged entry starts from a real team problem, captured in the `problem` and
`input_summary` columns. The six tools cover the breadth of team goals:
robot (Auto Autopsy), design (Design Opposition Board), strategy (Scout Question Generator),
documentation (Notebook Critic), outreach/inclusion (Accessibility Translator), and code
(Code Debugger Log), plus operations (Team Tracking Summarizer).

## B) AI tools / process used
- The `generated_prompt` column shows the exact structured prompt sent to the AI.
- The `ai_output` column shows what the AI returned.
- Manual mode (copy/paste into ChatGPT/Claude/Gemini) is the default; optional Direct API
  mode calls an OpenAI-compatible model. Either way the process is identical: structured
  prompt in, raw AI output captured, human review next.

## C) Reflection / lessons learned
The `reflection` column on every entry captures what AI helped with and where it fell short.
The Judge Handout Builder aggregates these into a Reflection section.

## Documentation / evidence
- The whole shared CSV is the documentation trail.
- `evidence_link` and `result` columns link to or describe the concrete proof (a test result,
  photo, log, notebook page, or commit).
- The Evidence Dashboard shows counts, breakdowns, a filterable table, a CSV download, and a
  "Judge Demo Mode" listing the most complete entries.

## Benefits / challenges
- **Benefits** are shown by entries labeled Accepted/Modified — cases where AI structuring
  genuinely helped after human review (see `action_taken`, `result`).
- **Challenges** are shown by entries labeled Rejected/Needs Testing — cases where the AI was
  wrong or unproven and human testing caught it. Keeping these is deliberate: they prove the
  humans, not the AI, are in control.

## Adaptation based on AI output
The `action_taken` and `validation_label` columns document how the team adapted: accepted as
is, modified before use, rejected, or flagged for more testing. This is the core of the loop —
AI proposes, the team decides — and it is visible on every single entry.

## Responsible-use ground rule (threaded throughout)
"AI helped us structure information, but human testing and review determined what we actually
used." Every tool page shows the reviewer requirement, and no entry is saved without a named
human reviewer and a validation label.

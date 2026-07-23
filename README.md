# Absolute Zero AI Command Center
FTC Team #12096 "Absolute Zero" — FTC DECODE presented by RTX

## What this is
A small, reliable Streamlit app that documents how our team uses AI **responsibly**.
It is not a chatbot. Each tool turns real team evidence into a structured prompt,
we run that prompt in an AI assistant, and then a human reviews and validates the
output before the team acts. Every interaction is logged to one shared file so we
can show judges exactly how, and how carefully, we used AI.

Guiding loop: **Evidence → AI Structure → Human Validation → Team Action → Reflection.**

## Project structure
```
az-ai-command-center/
  app.py                 The whole Streamlit app (self-contained)
  data/
    ai_feedback_log.csv  The shared log of every AI interaction (committed)
  docs/
    prompt_library.md          Reusable prompt templates for each tool
    award_criteria_mapping.md  How the app maps to the award criteria
    judging_demo_script.md     A 2-minute demo script
  README.md
  requirements.txt
  .gitignore
  .streamlit/config.toml Dark navy / electric blue theme
```

## How it supports the AI Trailblazer Award
The award recognizes teams that use AI tools effectively **and** responsibly.
This app is our evidence. It shows a real, repeatable process (not hype): every
AI output is paired with a human decision, a result, and a reflection, and the
Evidence Dashboard and Judge Handout Builder summarize that record for the
structured interview.

## How to run
```bash
pip install -r requirements.txt      # only streamlit + pandas
streamlit run app.py
```
No API key is required. Each tool builds a prompt you copy into
ChatGPT / Claude / Gemini; you paste the answer back and record the validation.
The app auto-creates `data/ai_feedback_log.csv` on first launch.

### Optional: Direct API mode
Install `openai` and set `OPENAI_API_KEY` to unlock a "Run AI Analysis" button
that fills the paste field for you. The mode only appears when both are present;
otherwise the app stays in Manual mode. No key is ever hardcoded.

## How the feedback loop works
1. **Collect real team evidence** — match data, logs, designs, notes.
2. **Use AI to structure the information** — a tool builds a structured prompt.
3. **Human team members validate** — a reviewer labels and checks the output.
4. **Take action based on testing and review** — the team acts only after review.
5. **Reflect on benefits, limits, and lessons** — captured with every entry.

## Validation labels
- **Accepted** — team verified and used the AI suggestion.
- **Modified** — suggestion was partly useful but changed by humans.
- **Rejected** — suggestion was wrong, irrelevant, or untestable.
- **Needs Testing** — suggestion is plausible but requires more evidence.

## Responsible-use ground rule
AI is used as a structure-and-critique tool, **not as an authority**. Every AI
output is reviewed by a team member before the team acts on it, and nothing in
this app is fabricated — the dashboards only ever show real logged data.

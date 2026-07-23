# Judging Demo Script (~2 minutes)
For the Artificial Intelligence Trailblazer Award structured interview. One presenter drives
the laptop; one narrates. Have the app already running (`streamlit run app.py`) with a few
real entries logged. Speak to the process, not the tool.

## 0:00–0:20 — Framing
"We're Team 12096, Absolute Zero. We built the AI Command Center to use AI **responsibly**.
Our rule is one sentence: *AI helped us structure information, but human testing and review
determined what we actually used.* Everything runs through this loop: Evidence → AI Structure
→ Human Validation → Team Action → Reflection."
(Show the **Home** page — point to the five-step loop and the warning banner.)

## 0:20–1:00 — One real tool, end to end
"Here's a real example." Open **Auto Autopsy**.
- "We enter actual failure evidence from a match — route, expected vs. actual, sensor logs."
- "The app builds a structured prompt that tells the AI to separate symptoms from causes and
  to never invent data." (Click **Generate**, point at the prompt.)
- "A team member runs it, then we paste the answer back — and this part is the point: a human
  reviews it and labels it Accepted, Modified, Rejected, or Needs Testing, with the action and
  the result." (Scroll to the validation fields.)

## 1:00–1:30 — Proof it's honest, not hype
Open **Evidence Dashboard**.
- "Every interaction is logged to one CSV. Here are the totals and the validation breakdown."
- "Notice we have Modified and Rejected entries — that's evidence the humans, not the AI, made
  the calls. We keep the times AI was wrong because that's more honest than a perfect story."
- Point to **Award Criteria Mapping**: "Each judged criterion maps to a specific column."

## 1:30–2:00 — The handout and close
Open **Judge Handout Builder**.
- "We pick our strongest 3–6 entries and it generates this one-page summary for you — problem,
  tools, a use-case table, benefits, challenges, reflection, and our validation method."
- Hand over the printed handout.
- Close: "AI made us faster at structuring problems. But every decision on our robot was made
  by a person who tested the idea. That's the responsible use we're most proud of."

## If a judge asks…
- **"Does it need an API key?"** No — it runs fully in manual copy/paste. There's an optional
  direct-API mode, but it's off by default and no key is stored.
- **"Is any of this fake?"** No. The dashboards only show entries we actually logged; blank
  fields show "[add evidence]" instead of anything invented.
- **"What did AI get wrong?"** (Open a Rejected entry and read the result — have one ready.)

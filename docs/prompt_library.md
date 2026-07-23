# Prompt Library
Reusable prompt templates behind each tool in the Absolute Zero AI Command Center.
Every template shares one rule: **the AI structures and critiques; a human validates
before the team acts.** Fill the bracketed fields with real evidence — never invent data.

---

## 1. Auto Autopsy
Opens with: *"We are an FTC robotics team analyzing an autonomous failure. Do not invent
data. Separate symptoms from possible causes. Use only the evidence provided. For each
possible cause, explain what evidence would confirm or reject it. Suggest safe next tests."*

Evidence: auto route name, date/run, starting position, expected vs. actual behavior,
final robot position, battery voltage, IMU/encoder/sensor notes, log notes, video link,
driver notes, mechanical notes, code changes since last success, team's initial hypothesis.

Required output sections: 1) Symptom summary 2) Top 3 likely causes 3) Evidence supporting
each 4) Evidence missing 5) Next test to run 6) Risk level 7) Human validation checklist
8) What not to assume.

---

## 2. Design Opposition Board
Acts as a strict FTC engineering design reviewer / devil's advocate. Does not invent robot
facts; separates **high-confidence** from **speculative** concerns.

Evidence: mechanism, game task/goal, design description, sketch link, materials, actuators,
size/weight constraints, manufacturing constraints, maintenance constraints, driver-control
concerns, known risks, alternatives considered, why the team likes the design.

Identifies: 1) Mechanical failure modes 2) Driver-control risks 3) Maintenance issues
4) Manufacturing complexity 5) Rule/size/weight risks 6) Testing questions 7) Improvements/
alternatives 8) Most testable concerns.
Output table: `Concern | Why it matters | Evidence needed | Suggested test | Priority`.

---

## 3. Scout Question Generator
Uses ONLY observed match behavior. Does not assume unobserved abilities. Avoids generic
questions like "What can your robot do?". Prioritizes questions that change strategy.

Evidence: event, team scouted, observed strengths/weaknesses, auto notes, TeleOp notes,
reliability, defense, endgame, driver/traffic notes, penalty concerns, unknowns, our
possible alliance strategy.

Produces: 1) 5 targeted questions 2) why each matters 3) good sign 4) concerning sign
5) follow-up 6) strategy impact.
Output table: `Question | Why it matters | Good sign | Concerning sign | Follow-up | Strategy impact`.

---

## 4. Notebook Critic
Reviews a team-authored entry. **Does not rewrite it and does not invent evidence** — only
flags missing proof and questions.

Evidence: entry title, subteam/mechanism, draft text, problem the entry explains, design
alternatives, testing data available, photos/diagrams available, decision made, what changed
after testing, current reflection.

Reviews for: 1) Clear problem statement 2) Design alternatives 3) Evidence/test data
4) Photos/diagrams needed 5) Decision justification 6) Iteration shown 7) Reflection/lesson
8) Missing judge-relevant details. Gives a 1–5 score per category + a before-revision checklist.
Output table: `Category | Score 1-5 | Missing evidence | Questions team should answer | Suggested improvement`.

---

## 5. Accessibility Translator
The AI **drafts**; the team **verifies accuracy and edits** before use. Keeps claims accurate,
uses only the provided robot context, marks anything to verify.

Evidence: concept, audience, current technical explanation, robot-specific context, desired
length, jargon to avoid, required terms, analogy preference, where it will be used.

Produces: 1) Simple explanation 2) Analogy 3) Visual/demo idea 4) Check-for-understanding
question 5) Optional shorter version 6) Terms/claims that still need team verification.

---

## 6. Code Debugger Log
May explain errors, propose causes, suggest fixes and a test plan — but **programmers own the
final code decision** and test everything. Does not invent hardware or APIs; asks if something
is missing; prefers small testable changes.

Evidence: code area/module, language, error/bug, code snippet, intended behavior, actual
behavior, what was tried, hardware, FTC SDK/library context, safety concerns, current hypothesis.

Does: 1) Explain the issue 2) Identify causes 3) Suggest minimal changes 4) Suggest a test plan
5) Point out assumptions 6) Warn about safety risks 7) Avoid large rewrites.
Output table: `Possible cause | Evidence | Suggested fix | Test to run | Risk/assumption`.

---

## 7. Team Tracking Summarizer
Turns messy meeting notes into a task list. **Team leads approve** before use. Does not invent
members; marks unclear owners "Unassigned" and unclear deadlines "Needs deadline"; separates
confirmed decisions from possible ideas.

Evidence: meeting date, meeting type, raw notes, known deadlines, current blockers, members
mentioned, decisions made, things still unclear.

Produces: 1) Summary of decisions 2) Action items 3) Owners 4) Suggested deadlines 5) Blockers
6) Follow-up questions 7) Risks if missed 8) Priority levels.
Output table: `Task | Owner | Deadline | Priority | Blocker | Follow-up question`.

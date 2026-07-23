"""
Absolute Zero AI Command Center
Team #12096 "Absolute Zero" -- FTC DECODE presented by RTX

A structured evidence and decision-support system (NOT a chatbot). The loop:
Evidence -> AI Structure -> Human Validation -> Team Action -> Reflection.
AI is used to structure and critique; humans validate every output before use.

Run:  streamlit run app.py
Requires only:  streamlit, pandas
"""
from __future__ import annotations

import csv
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------- #
# Shared log (single source of truth). Everything the team saves lands in ONE
# CSV: data/ai_feedback_log.csv, using the exact schema below.
# --------------------------------------------------------------------------- #
FIELDS: List[str] = [
    "entry_id", "timestamp", "tool_name", "subteam", "problem", "input_summary",
    "generated_prompt", "ai_output", "human_reviewer", "validation_label",
    "action_taken", "result", "reflection", "evidence_link",
]
VALIDATION_LABELS: List[str] = ["Accepted", "Modified", "Rejected", "Needs Testing"]

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = APP_ROOT / "data"
LOG_PATH = DATA_DIR / "ai_feedback_log.csv"


def generate_entry_id() -> str:
    """Short, unique id for one logged AI interaction."""
    return uuid.uuid4().hex[:12]


def ensure_data_file(path: Path = LOG_PATH) -> Path:
    """Create the data folder and the CSV (with header) if they do not exist."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()
    return path


def save_entry(entry: Dict, path: Path = LOG_PATH) -> Dict:
    """Append one entry to the shared CSV, filling id/timestamp if missing."""
    ensure_data_file(path)
    row = {k: "" for k in FIELDS}
    row.update({k: v for k, v in entry.items() if k in FIELDS})
    if not row["entry_id"]:
        row["entry_id"] = generate_entry_id()
    if not row["timestamp"]:
        row["timestamp"] = datetime.now().isoformat(timespec="seconds")
    for k, v in row.items():
        row[k] = str(v).replace("\r\n", "\n")
    with Path(path).open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow(row)
    return row


def load_entries(path: Path = LOG_PATH) -> List[Dict]:
    """Return all logged entries. Empty list if none."""
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

st.set_page_config(
    page_title="Absolute Zero AI Command Center",
    page_icon="🛡️",
    layout="wide",
)

# --------------------------------------------------------------------------- #
# Styling: clean, modern FTC-robotics look (dark navy / white / electric blue).
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.4rem; max-width: 1120px; padding-bottom: 4rem; }
      h1, h2, h3 { letter-spacing: -0.01em; }
      /* Section headers get a subtle electric-blue accent rule. */
      h3 { border-bottom: 1px solid #21406e; padding-bottom: 6px; }
      /* Consistent slim brand header on every page. */
      .az-topbar {
        display:flex; align-items:center; justify-content:space-between;
        background: linear-gradient(90deg, #0b1220 0%, #0d1b34 100%);
        border: 1px solid #21406e; border-left: 4px solid #2f81f7;
        border-radius: 10px; padding: 10px 16px; margin-bottom: 14px;
      }
      .az-topbar .brand { color:#ffffff; font-weight:700; font-size:.98rem; }
      .az-topbar .brand span { color:#2f81f7; }
      .az-topbar .meta { color:#9aa7b8; font-size:.74rem; letter-spacing:.06em;
                         text-transform:uppercase; }
      .az-hero {
        background: linear-gradient(135deg, #0d1b34 0%, #12305c 100%);
        border: 1px solid #21406e; border-radius: 14px;
        padding: 22px 26px; margin-bottom: 8px;
      }
      .az-hero h1 { margin: 0; color: #ffffff; font-size: 2.0rem; }
      .az-hero p { margin: 6px 0 0; color: #9fc0ff; font-size: 1.05rem; }
      .az-kicker { color:#2f81f7; font-weight:700; letter-spacing:.14em;
                   font-size:.72rem; text-transform:uppercase; }
      /* The loop shown on every tool page. */
      .az-loop {
        background:#111c30; border:1px solid #21406e; border-radius:8px;
        padding:8px 14px; margin:6px 0 4px; color:#c9d6e5; font-size:.86rem;
      }
      .az-loop b { color:#2f81f7; }
      .az-step { background:#111c30; border:1px solid #21406e; border-radius:10px;
                 padding:14px 16px; height:100%; }
      .az-step .n { color:#2f81f7; font-weight:700; font-size:.8rem; }
      .az-step .t { color:#e6edf3; font-weight:600; margin-top:2px; }
      .az-step .d { color:#9aa7b8; font-size:.86rem; margin-top:4px; }
      div[data-testid="stMetricValue"] { color:#2f81f7; }
      div[data-testid="stMetric"] {
        background:#111c30; border:1px solid #21406e; border-radius:10px;
        padding:10px 14px;
      }
      /* Footer on every page. */
      .az-footer {
        margin-top: 26px; padding-top: 12px; border-top: 1px solid #21406e;
        color:#7f8ea3; font-size:.8rem; text-align:center;
      }
      .az-footer b { color:#9fc0ff; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_topbar():
    """Consistent slim brand header shown at the top of every page."""
    st.markdown(
        '<div class="az-topbar">'
        '<span class="brand">Absolute Zero <span>AI Command Center</span></span>'
        '<span class="meta">Team #12096 · FTC DECODE presented by RTX</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_footer():
    """Consistent footer shown at the bottom of every page."""
    st.markdown(
        '<div class="az-footer">FTC Team Absolute Zero #12096 — '
        '<b>AI used as a structured feedback tool, not as an authority.</b></div>',
        unsafe_allow_html=True,
    )


def render_loop_line():
    """One-line explanation of the feedback loop for tool pages."""
    st.markdown(
        '<div class="az-loop"><b>Evidence</b> → <b>AI Structure</b> → '
        '<b>Human Validation</b> → <b>Team Action</b> → <b>Reflection</b></div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# OPTIONAL AI API mode.
# The manual copy/paste workflow is always available. API mode is only offered
# when the OpenAI SDK is installed AND OPENAI_API_KEY is set; otherwise the app
# runs exactly as before with only streamlit + pandas. No keys are hardcoded.
# --------------------------------------------------------------------------- #
API_MODE = "Direct API mode (OpenAI-compatible)"
MANUAL_MODE = "Manual mode (copy / paste)"


def _openai_sdk_installed() -> bool:
    try:
        import openai  # noqa: F401
        return True
    except Exception:
        return False


def api_mode_available() -> bool:
    """API mode is only possible with both the SDK and a key present."""
    return _openai_sdk_installed() and bool(os.environ.get("OPENAI_API_KEY"))


def current_ai_mode() -> str:
    """Resolved mode; always falls back to manual if API is not available."""
    if not api_mode_available():
        return MANUAL_MODE
    return st.session_state.get("ai_mode", MANUAL_MODE)


def run_ai_analysis(prompt: str):
    """
    Send the prompt to an OpenAI-compatible endpoint. Returns (ok, text_or_error).
    Never raises — a missing dependency, missing key, or API error is returned as
    a message so the user can fall back to copying the prompt manually.
    """
    try:
        from openai import OpenAI
    except Exception:
        return False, ("OpenAI SDK not installed. Run `pip install openai`, or use "
                       "Manual mode and copy the prompt above.")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return False, "OPENAI_API_KEY is not set. Use Manual mode instead."
    base_url = os.environ.get("OPENAI_BASE_URL")  # optional: compatible endpoints
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    try:
        client = OpenAI(api_key=key, base_url=base_url) if base_url else OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return True, (resp.choices[0].message.content or "").strip()
    except Exception as e:  # network, auth, quota, model name, etc.
        return False, f"{type(e).__name__}: {e}"


def render_ai_output_area(state_key: str, generated_prompt: str,
                          height: int = 220, placeholder: str = ""):
    """
    The 'Paste AI output here' field, shared by every tool page. In API mode it
    also shows a 'Run AI Analysis' button that fills this same field. The prompt
    stays visible in all modes, and any API failure leaves manual copy available.
    """
    if current_ai_mode() == API_MODE:
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        cols = st.columns([1, 3])
        with cols[0]:
            run = st.button("Run AI Analysis", key=state_key + "_runai",
                            type="secondary")
        with cols[1]:
            st.caption(f"Sends the prompt above to the API (model: {model}). "
                       "You can still copy it and run it manually.")
        if run:
            with st.spinner("Calling the AI API..."):
                ok, text = run_ai_analysis(generated_prompt)
            if ok:
                st.session_state[state_key] = text
                st.success("AI response loaded below. Review it before validating.")
            else:
                st.error(f"API call failed — {text}")
                st.info("The prompt above is unchanged; copy it into your AI tool "
                        "and paste the result below.")
    return st.text_area("Paste AI output here", key=state_key, height=height,
                        placeholder=placeholder)


def sidebar_ai_settings():
    """Sidebar mode chooser. Only offers API mode when it is actually usable."""
    st.markdown("#### Settings")
    if api_mode_available():
        st.radio("AI mode", [MANUAL_MODE, API_MODE], key="ai_mode",
                 label_visibility="collapsed")
        if st.session_state.get("ai_mode") == API_MODE:
            st.caption("API mode on. Key read from OPENAI_API_KEY; model from "
                       "OPENAI_MODEL (default gpt-4o-mini).")
        else:
            st.caption("Manual mode. Switch to API mode to run prompts directly.")
    else:
        # Force/fall back to manual and explain why.
        st.session_state["ai_mode"] = MANUAL_MODE
        reasons = []
        if not _openai_sdk_installed():
            reasons.append("OpenAI SDK not installed")
        if not os.environ.get("OPENAI_API_KEY"):
            reasons.append("OPENAI_API_KEY not set")
        st.caption("Manual mode (copy / paste). " + " · ".join(reasons) +
                   ". The app runs fully without an API key.")

ensure_data_file()

PAGES = [
    "Home",
    "Auto Autopsy",
    "Design Opposition Board",
    "Scout Question Generator",
    "Notebook Critic",
    "Accessibility Translator",
    "Code Debugger Log",
    "Team Tracking",
    "Evidence Dashboard",
    "Judge Handout Builder",
]


def validation_banner(show_loop=True):
    st.warning(
        "AI is used as a structure and critique tool, not as an authority. "
        "All outputs are reviewed by team members before the team acts on them.",
        icon="⚠️",
    )
    if show_loop:
        render_loop_line()


# --------------------------------------------------------------------------- #
# Core reusable widget: human-validation fields + Save.
# --------------------------------------------------------------------------- #
def render_validation_fields(tool_name, subteam, problem, input_summary,
                             generated_prompt, ai_output, extra_result_note=""):
    st.divider()
    st.subheader("Human validation")
    st.caption("A team member reviews the AI output and records the decision. "
               "Nothing is acted on until it is validated here.")

    c1, c2 = st.columns(2)
    with c1:
        human_reviewer = st.text_input(
            "Human reviewer (name / initials)",
            key=f"{tool_name}_reviewer",
            placeholder="Who reviewed this AI output",
        )
    with c2:
        validation_label = st.selectbox(
            "Validation label", VALIDATION_LABELS, key=f"{tool_name}_label",
            help="Accepted, Modified, Rejected, or Needs Testing.",
        )

    action_taken = st.text_area(
        "Action taken", key=f"{tool_name}_action",
        placeholder="What the team actually did with this output.",
    )
    result = st.text_area(
        "Result", key=f"{tool_name}_result",
        placeholder="What happened after the action (test outcome, measurement).",
    )
    reflection = st.text_area(
        "Reflection", key=f"{tool_name}_reflection",
        placeholder="Benefits, limits, and lessons learned from using AI here.",
    )
    evidence_link = st.text_input(
        "Evidence link", key=f"{tool_name}_evidence",
        placeholder="Link to a photo, log, notebook page, or commit (optional).",
    )

    if st.button("Save entry", type="primary", key=f"{tool_name}_save"):
        if not human_reviewer.strip():
            st.error("A human reviewer is required before saving.")
            return
        result_value = result
        if extra_result_note.strip():
            result_value = (result + "\n\n" + extra_result_note).strip() \
                if result.strip() else extra_result_note.strip()
        row = {
            "entry_id": generate_entry_id(),
            "tool_name": tool_name,
            "subteam": subteam,
            "problem": problem,
            "input_summary": input_summary,
            "generated_prompt": generated_prompt,
            "ai_output": ai_output,
            "human_reviewer": human_reviewer,
            "validation_label": validation_label,
            "action_taken": action_taken,
            "result": result_value,
            "reflection": reflection,
            "evidence_link": evidence_link,
        }
        saved = save_entry(row)
        st.success(
            f"✅ Saved. Entry {saved['entry_id']} ({tool_name}) was logged as "
            f"**{validation_label}** by {human_reviewer}. View it under "
            f"Evidence Dashboard.")
        st.toast("Entry logged to Evidence Dashboard", icon="✅")


# --------------------------------------------------------------------------- #
# Auto Autopsy (fully implemented, bespoke page)
# --------------------------------------------------------------------------- #
AA_FIELD_LABELS = {
    "route": "1. Auto route name",
    "run": "2. Date / run number",
    "start": "3. Starting position",
    "expected": "4. Expected behavior",
    "actual": "5. Actual behavior",
    "final_pos": "6. Final robot position",
    "battery": "7. Battery voltage",
    "sensors": "8. IMU / encoder / sensor notes",
    "logs": "9. Driver station or robot log notes",
    "video": "10. Video link",
    "driver": "11. Driver notes",
    "mechanical": "12. Mechanical notes",
    "code_changes": "13. Code changes since last successful run",
    "hypothesis": "14. Team's initial hypothesis",
}


def build_auto_autopsy_prompt(v: dict) -> str:
    """Assemble the structured autopsy prompt from only the fields provided."""
    def line(label, key):
        val = v.get(key, "").strip()
        return f"{label}: {val if val else '(not provided)'}"

    fields_block = "\n".join(line(lbl, k) for k, lbl in AA_FIELD_LABELS.items())
    return (
        "We are an FTC robotics team analyzing an autonomous failure. Do not "
        "invent data. Separate symptoms from possible causes. Use only the "
        "evidence provided. For each possible cause, explain what evidence "
        "would confirm or reject it. Suggest safe next tests.\n\n"
        "=== EVIDENCE FROM THIS RUN ===\n"
        f"{fields_block}\n\n"
        "=== REQUIRED OUTPUT STRUCTURE ===\n"
        "Respond using exactly these numbered sections:\n"
        "1) Symptom summary\n"
        "2) Top 3 likely causes\n"
        "3) Evidence supporting each cause\n"
        "4) Evidence missing\n"
        "5) Next test to run\n"
        "6) Risk level\n"
        "7) Human validation checklist\n"
        "8) What not to assume\n\n"
        "Reminder: base every statement on the evidence above. Where evidence "
        "is missing, say so under section 4 instead of guessing."
    )


def _serialize_verification_table(df) -> str:
    """Turn the AI-vs-human verification table into plain text for the log."""
    try:
        rows = df.to_dict("records")
    except AttributeError:
        rows = list(df)
    lines = []
    for r in rows:
        cells = [str(r.get(c, "")).strip() for c in
                 ["AI predicted cause", "Human verified cause", "Correctness",
                  "Fix attempted", "Retest result"]]
        if any(cells):
            lines.append(
                f"- AI cause: {cells[0] or '-'} | Human verified: {cells[1] or '-'} "
                f"| Correctness: {cells[2] or '-'} | Fix attempted: {cells[3] or '-'} "
                f"| Retest: {cells[4] or '-'}"
            )
    if not lines:
        return ""
    return "AI-vs-human cause verification:\n" + "\n".join(lines)


def render_auto_autopsy():
    st.markdown('<span class="az-kicker">Software / Autonomous</span>',
                unsafe_allow_html=True)
    st.title("Auto Autopsy")
    st.write("Analyze failed autonomous runs by turning robot evidence into "
             "testable debugging hypotheses.")
    validation_banner()

    st.subheader("1. Enter the failure evidence")
    subteam = st.text_input("Subteam", value="Software / Autonomous",
                            key="aa_subteam")

    v = {}
    c1, c2 = st.columns(2)
    with c1:
        v["route"] = st.text_input(AA_FIELD_LABELS["route"], key="aa_route",
                                   placeholder="e.g. Left-3-artifact")
        v["start"] = st.text_input(AA_FIELD_LABELS["start"], key="aa_start")
        v["expected"] = st.text_area(AA_FIELD_LABELS["expected"], key="aa_expected")
        v["final_pos"] = st.text_input(AA_FIELD_LABELS["final_pos"], key="aa_final_pos")
        v["sensors"] = st.text_area(AA_FIELD_LABELS["sensors"], key="aa_sensors")
        v["video"] = st.text_input(AA_FIELD_LABELS["video"], key="aa_video",
                                   placeholder="Optional link")
        v["mechanical"] = st.text_area(AA_FIELD_LABELS["mechanical"], key="aa_mech")
    with c2:
        v["run"] = st.text_input(AA_FIELD_LABELS["run"], key="aa_run",
                                 placeholder="e.g. 2026-01-18 / Qual 12")
        v["battery"] = st.text_input(AA_FIELD_LABELS["battery"], key="aa_battery",
                                     placeholder="e.g. 12.9 V at start")
        v["actual"] = st.text_area(AA_FIELD_LABELS["actual"], key="aa_actual")
        v["logs"] = st.text_area(AA_FIELD_LABELS["logs"], key="aa_logs")
        v["driver"] = st.text_area(AA_FIELD_LABELS["driver"], key="aa_driver")
        v["code_changes"] = st.text_area(AA_FIELD_LABELS["code_changes"],
                                         key="aa_code_changes")
    v["hypothesis"] = st.text_area(AA_FIELD_LABELS["hypothesis"], key="aa_hypothesis",
                                   help="Your best guess — the AI will test it, "
                                        "not simply agree with it.")

    st.subheader("2. Generate the structured prompt")
    if st.button("Generate Auto Autopsy Prompt", type="primary", key="aa_generate"):
        st.session_state["aa_show_prompt"] = True

    if not st.session_state.get("aa_show_prompt"):
        st.info("Fill in the evidence above, then click "
                "**Generate Auto Autopsy Prompt**.")
        return

    generated_prompt = build_auto_autopsy_prompt(v)
    st.caption("Copy this into ChatGPT / Claude / Gemini. It instructs the AI to "
               "use only your evidence and to never invent data.")
    st.text_area("Generated prompt (copy this)", value=generated_prompt,
                 height=360, key="aa_prompt_display")

    st.subheader("3. Paste AI output here")
    ai_output = render_ai_output_area("aa_ai_output", generated_prompt, height=220,
                                      placeholder="Paste the AI's numbered response "
                                                  "exactly as returned.")

    st.subheader("4. Verify AI causes against reality (optional)")
    st.caption("Record how each AI-predicted cause held up once your team tested "
               "it. This is saved into the entry's Result field — no separate "
               "database.")
    import pandas as _pd
    default_table = _pd.DataFrame(
        [{"AI predicted cause": "", "Human verified cause": "",
          "Correctness": "", "Fix attempted": "", "Retest result": ""}
         for _ in range(3)]
    )
    edited = st.data_editor(
        default_table, num_rows="dynamic", use_container_width=True,
        key="aa_verify_table",
        column_config={
            "Correctness": st.column_config.SelectboxColumn(
                "Correctness",
                options=["Correct", "Partially Correct", "Incorrect", "Needs Testing"],
            ),
        },
    )
    verification_note = _serialize_verification_table(edited)

    # Save mapping per spec.
    problem = (f"Autonomous failure: {v['route'] or '(unnamed route)'} "
               f"— {(v['actual'] or '').strip()[:80]}")
    input_summary = " | ".join(x for x in [
        f"route: {v['route']}" if v['route'] else "",
        f"expected: {v['expected'][:60]}" if v['expected'] else "",
        f"actual: {v['actual'][:60]}" if v['actual'] else "",
        f"final: {v['final_pos']}" if v['final_pos'] else "",
        f"battery: {v['battery']}" if v['battery'] else "",
        f"sensors: {v['sensors'][:40]}" if v['sensors'] else "",
    ] if x)

    render_validation_fields(
        "Auto Autopsy", subteam, problem, input_summary,
        generated_prompt, ai_output, extra_result_note=verification_note,
    )


# --------------------------------------------------------------------------- #
# Design Opposition Board (fully implemented, bespoke page)
# --------------------------------------------------------------------------- #
DO_FIELD_LABELS = {
    "mechanism": "1. Mechanism name",
    "goal": "2. Game task or robot goal",
    "description": "3. Design description",
    "sketch": "4. Sketch / photo link",
    "materials": "5. Materials",
    "actuators": "6. Motors / servos / actuators",
    "size_weight": "7. Size and weight constraints",
    "manufacturing": "8. Manufacturing constraints",
    "maintenance": "9. Maintenance constraints",
    "driver": "10. Driver-control concerns",
    "risks": "11. Known risks",
    "alternatives": "12. Alternatives considered",
    "why_like": "13. Why the team currently likes this design",
}


def build_design_critique_prompt(v: dict) -> str:
    """Assemble the design-review prompt from only the fields provided."""
    def line(label, key):
        val = v.get(key, "").strip()
        return f"{label}: {val if val else '(not provided)'}"

    fields_block = "\n".join(line(lbl, k) for k, lbl in DO_FIELD_LABELS.items())
    return (
        "You are a strict FTC engineering design reviewer acting as a devil's "
        "advocate. Your job is to find weaknesses in the design below BEFORE the "
        "team commits to it. Do not invent robot facts or specifications. Use "
        "only the information provided; where information is missing, say what is "
        "missing instead of assuming. Clearly separate \"high confidence "
        "concerns\" (supported by the evidence given) from \"speculative "
        "concerns\" (things to check).\n\n"
        "=== DESIGN UNDER REVIEW ===\n"
        f"{fields_block}\n\n"
        "=== WHAT TO IDENTIFY ===\n"
        "1) Mechanical failure modes\n"
        "2) Driver-control risks\n"
        "3) Maintenance issues\n"
        "4) Manufacturing complexity\n"
        "5) Rule / size / weight risks\n"
        "6) Testing questions\n"
        "7) Improvements / alternatives\n"
        "8) Which concerns are most testable\n\n"
        "=== REQUIRED OUTPUT ===\n"
        "First, two labeled lists: \"High confidence concerns\" and "
        "\"Speculative concerns.\" Then a table with exactly these columns:\n"
        "Concern | Why it matters | Evidence needed | Suggested test | Priority\n\n"
        "Every row must tie to the evidence above; do not fabricate measurements "
        "or part specs the team did not provide."
    )


def _serialize_team_response_table(df) -> str:
    """Turn the team-response-to-critique table into plain text for the log."""
    try:
        rows = df.to_dict("records")
    except AttributeError:
        rows = list(df)
    cols = ["AI concern selected", "Team response", "Test performed",
            "Test result", "Design change made", "Validation label"]
    lines = []
    for r in rows:
        cells = [str(r.get(c, "")).strip() for c in cols]
        if any(cells):
            lines.append(
                f"- Concern: {cells[0] or '-'} | Team response: {cells[1] or '-'} "
                f"| Test performed: {cells[2] or '-'} | Test result: {cells[3] or '-'} "
                f"| Design change: {cells[4] or '-'} | Validation: {cells[5] or '-'}"
            )
    if not lines:
        return ""
    return "Team response to AI critique:\n" + "\n".join(lines)


def render_design_opposition():
    st.markdown('<span class="az-kicker">Build / Design</span>',
                unsafe_allow_html=True)
    st.title("Design Opposition Board")
    st.write("Use AI as a structured devil's advocate to identify failure modes, "
             "tradeoffs, and tests before committing to a robot design.")
    validation_banner()
    st.info("AI critiques are not final decisions. The team must test or reject "
            "each critique using evidence.", icon="🧪")

    st.subheader("1. Describe the design under review")
    subteam = st.text_input("Subteam", value="Build / Design", key="do_subteam")

    v = {}
    c1, c2 = st.columns(2)
    with c1:
        v["mechanism"] = st.text_input(DO_FIELD_LABELS["mechanism"], key="do_mechanism",
                                       placeholder="e.g. Dual-flywheel shooter")
        v["description"] = st.text_area(DO_FIELD_LABELS["description"], key="do_description")
        v["materials"] = st.text_area(DO_FIELD_LABELS["materials"], key="do_materials")
        v["size_weight"] = st.text_area(DO_FIELD_LABELS["size_weight"], key="do_size_weight")
        v["maintenance"] = st.text_area(DO_FIELD_LABELS["maintenance"], key="do_maintenance")
        v["risks"] = st.text_area(DO_FIELD_LABELS["risks"], key="do_risks")
        v["why_like"] = st.text_area(DO_FIELD_LABELS["why_like"], key="do_why_like")
    with c2:
        v["goal"] = st.text_input(DO_FIELD_LABELS["goal"], key="do_goal",
                                  placeholder="e.g. Score artifacts in high goal")
        v["sketch"] = st.text_input(DO_FIELD_LABELS["sketch"], key="do_sketch",
                                    placeholder="Optional link")
        v["actuators"] = st.text_area(DO_FIELD_LABELS["actuators"], key="do_actuators")
        v["manufacturing"] = st.text_area(DO_FIELD_LABELS["manufacturing"], key="do_manufacturing")
        v["driver"] = st.text_area(DO_FIELD_LABELS["driver"], key="do_driver")
        v["alternatives"] = st.text_area(DO_FIELD_LABELS["alternatives"], key="do_alternatives")

    st.subheader("2. Generate the critique prompt")
    if st.button("Generate Design Critique Prompt", type="primary", key="do_generate"):
        st.session_state["do_show_prompt"] = True

    if not st.session_state.get("do_show_prompt"):
        st.info("Fill in the design details above, then click "
                "**Generate Design Critique Prompt**.")
        return

    generated_prompt = build_design_critique_prompt(v)
    st.caption("Copy this into ChatGPT / Claude / Gemini. It asks the AI to attack "
               "the design honestly, separate confident from speculative concerns, "
               "and never invent robot facts.")
    st.text_area("Generated prompt (copy this)", value=generated_prompt,
                 height=380, key="do_prompt_display")

    st.subheader("3. Paste AI output here")
    ai_output = render_ai_output_area("do_ai_output", generated_prompt, height=220,
                                      placeholder="Paste the AI's concern lists and "
                                                  "table exactly as returned.")

    st.subheader("4. Team Response to AI Critique")
    st.caption("For each concern you engaged with, record how the team tested or "
               "rejected it. Saved into the entry's Result field — no separate "
               "database.")
    import pandas as _pd
    default_table = _pd.DataFrame(
        [{"AI concern selected": "", "Team response": "", "Test performed": "",
          "Test result": "", "Design change made": "", "Validation label": ""}
         for _ in range(3)]
    )
    edited = st.data_editor(
        default_table, num_rows="dynamic", use_container_width=True,
        key="do_response_table",
        column_config={
            "Validation label": st.column_config.SelectboxColumn(
                "Validation label",
                options=["Accepted", "Modified", "Rejected", "Needs Testing"],
            ),
        },
    )
    response_note = _serialize_team_response_table(edited)

    # Save mapping per spec.
    problem = (f"Design review: {v['mechanism'] or '(unnamed mechanism)'} "
               f"for {v['goal'] or '(unstated goal)'}")
    input_summary = " | ".join(x for x in [
        f"mechanism: {v['mechanism']}" if v['mechanism'] else "",
        f"goal: {v['goal']}" if v['goal'] else "",
        f"materials: {v['materials'][:50]}" if v['materials'] else "",
        f"actuators: {v['actuators'][:50]}" if v['actuators'] else "",
        f"size/weight: {v['size_weight'][:40]}" if v['size_weight'] else "",
        f"known risks: {v['risks'][:50]}" if v['risks'] else "",
    ] if x)

    render_validation_fields(
        "Design Opposition Board", subteam, problem, input_summary,
        generated_prompt, ai_output, extra_result_note=response_note,
    )


# --------------------------------------------------------------------------- #
# Scout Question Generator (fully implemented, bespoke page)
# --------------------------------------------------------------------------- #
SC_FIELD_LABELS = {
    "event": "1. Event name",
    "team": "2. Team number being scouted",
    "strengths": "3. Observed robot strengths",
    "weaknesses": "4. Observed robot weaknesses",
    "auto": "5. Auto performance notes",
    "teleop": "6. TeleOp scoring notes",
    "reliability": "7. Reliability notes",
    "defense": "8. Defense notes",
    "endgame": "9. Endgame notes",
    "driver": "10. Driver skill / traffic notes",
    "penalties": "11. Penalty or rule concerns",
    "unknowns": "12. What we are unsure about",
    "strategy": "13. Our possible alliance strategy with this team",
}


def build_scout_prompt(v: dict) -> str:
    """Assemble the scouting-question prompt from only the observations provided."""
    def line(label, key):
        val = v.get(key, "").strip()
        return f"{label}: {val if val else '(not provided)'}"

    fields_block = "\n".join(line(lbl, k) for k, lbl in SC_FIELD_LABELS.items())
    return (
        "You are helping an FTC team turn MATCH OBSERVATIONS into targeted "
        "pit-scouting questions. Use ONLY the observations provided below. Do "
        "not assume any ability that was not observed; if something was not "
        "observed, treat it as unknown. Avoid generic questions such as \"What "
        "can your robot do?\". Prioritize questions whose answers would actually "
        "change our alliance-strategy decisions.\n\n"
        "=== OBSERVATIONS (the questions are only as good as these) ===\n"
        f"{fields_block}\n\n"
        "=== WHAT TO PRODUCE ===\n"
        "1) 5 targeted pit-scouting questions\n"
        "2) why each matters\n"
        "3) what answer would be a good sign\n"
        "4) what answer would be concerning\n"
        "5) a follow-up question for each\n"
        "6) how the answer could affect match strategy\n\n"
        "=== REQUIRED OUTPUT ===\n"
        "Return a table with exactly these columns:\n"
        "Question | Why it matters | Good sign | Concerning sign | Follow-up | "
        "Strategy impact\n\n"
        "Ground every question in the observations above; do not invent robot "
        "abilities or stats the team did not record."
    )


def _serialize_scout_use_fields(asked, answers, changed, decision, useful) -> str:
    """Fold the human-use scouting fields into text for the log."""
    parts = []
    if asked.strip():
        parts.append(f"Questions actually asked: {asked.strip()}")
    if answers.strip():
        parts.append(f"Answers received: {answers.strip()}")
    parts.append(f"Did answers change strategy?: {changed}")
    if decision.strip():
        parts.append(f"Strategy decision made: {decision.strip()}")
    parts.append(f"Was the AI question useful?: {useful}")
    return "Scouting use:\n" + "\n".join(f"- {p}" for p in parts)


def render_scout_generator():
    st.markdown('<span class="az-kicker">Strategy / Scouting</span>',
                unsafe_allow_html=True)
    st.title("Scout Question Generator")
    st.write("Turn match observations into targeted pit questions that improve "
             "alliance strategy.")
    validation_banner()
    st.info("This tool only works if the observations are accurate. The AI cannot "
            "see the robot — it can only build on what your scouts actually "
            "recorded.", icon="👀")

    st.subheader("1. Enter what your scouts observed")
    subteam = st.text_input("Subteam", value="Strategy / Scouting", key="sc_subteam")

    v = {}
    c1, c2 = st.columns(2)
    with c1:
        v["event"] = st.text_input(SC_FIELD_LABELS["event"], key="sc_event")
        v["strengths"] = st.text_area(SC_FIELD_LABELS["strengths"], key="sc_strengths")
        v["auto"] = st.text_area(SC_FIELD_LABELS["auto"], key="sc_auto")
        v["reliability"] = st.text_area(SC_FIELD_LABELS["reliability"], key="sc_reliability")
        v["endgame"] = st.text_area(SC_FIELD_LABELS["endgame"], key="sc_endgame")
        v["penalties"] = st.text_area(SC_FIELD_LABELS["penalties"], key="sc_penalties")
        v["strategy"] = st.text_area(SC_FIELD_LABELS["strategy"], key="sc_strategy")
    with c2:
        v["team"] = st.text_input(SC_FIELD_LABELS["team"], key="sc_team",
                                  placeholder="e.g. 12096")
        v["weaknesses"] = st.text_area(SC_FIELD_LABELS["weaknesses"], key="sc_weaknesses")
        v["teleop"] = st.text_area(SC_FIELD_LABELS["teleop"], key="sc_teleop")
        v["defense"] = st.text_area(SC_FIELD_LABELS["defense"], key="sc_defense")
        v["driver"] = st.text_area(SC_FIELD_LABELS["driver"], key="sc_driver")
        v["unknowns"] = st.text_area(SC_FIELD_LABELS["unknowns"], key="sc_unknowns")

    st.subheader("2. Generate the targeted questions")
    if st.button("Generate Targeted Scout Questions", type="primary", key="sc_generate"):
        st.session_state["sc_show_prompt"] = True

    if not st.session_state.get("sc_show_prompt"):
        st.info("Fill in the observations above, then click "
                "**Generate Targeted Scout Questions**.")
        return

    generated_prompt = build_scout_prompt(v)
    st.caption("Copy this into ChatGPT / Claude / Gemini. It uses only your "
               "observations, avoids generic questions, and prioritizes questions "
               "that change strategy.")
    st.text_area("Generated prompt (copy this)", value=generated_prompt,
                 height=360, key="sc_prompt_display")

    st.subheader("3. Paste AI output here")
    ai_output = render_ai_output_area("sc_ai_output", generated_prompt, height=220,
                                      placeholder="Paste the AI's question table "
                                                  "exactly as returned.")

    st.subheader("4. How the questions were actually used")
    st.caption("Recorded into the entry's Result field — no separate database.")
    asked = st.text_area("Questions actually asked", key="sc_asked")
    answers = st.text_area("Answers received", key="sc_answers")
    cc1, cc2 = st.columns(2)
    with cc1:
        changed = st.radio("Did the answers change strategy?", ["Yes", "No"],
                           key="sc_changed", horizontal=True)
    with cc2:
        useful = st.radio("Was the AI question useful?",
                          ["Yes", "No", "Partially"], key="sc_useful",
                          horizontal=True)
    decision = st.text_area("Strategy decision made", key="sc_decision")
    use_note = _serialize_scout_use_fields(asked, answers, changed, decision, useful)

    # Save mapping per spec.
    problem = (f"Targeted scouting for Team {v['team'] or '(unknown)'} "
               f"at {v['event'] or '(unnamed event)'}")
    input_summary = " | ".join(x for x in [
        f"strengths: {v['strengths'][:50]}" if v['strengths'] else "",
        f"weaknesses: {v['weaknesses'][:50]}" if v['weaknesses'] else "",
        f"auto: {v['auto'][:40]}" if v['auto'] else "",
        f"teleop: {v['teleop'][:40]}" if v['teleop'] else "",
        f"reliability: {v['reliability'][:40]}" if v['reliability'] else "",
        f"unknowns: {v['unknowns'][:40]}" if v['unknowns'] else "",
    ] if x)

    render_validation_fields(
        "Scout Question Generator", subteam, problem, input_summary,
        generated_prompt, ai_output, extra_result_note=use_note,
    )


# --------------------------------------------------------------------------- #
# Notebook Critic (fully implemented, bespoke page)
# --------------------------------------------------------------------------- #
NB_FIELD_LABELS = {
    "title": "1. Entry title",
    "subteam_mech": "2. Subteam or mechanism",
    "draft": "3. Draft entry text",
    "problem_explained": "4. What problem the entry is supposed to explain",
    "alternatives": "5. Design alternatives considered",
    "test_data": "6. Testing data currently available",
    "photos": "7. Photos or diagrams available",
    "decision": "8. Decision made by the team",
    "changed": "9. What changed after testing",
    "reflection": "10. Current reflection or lesson learned",
}


def build_notebook_prompt(v: dict) -> str:
    """Assemble the notebook-critique prompt from only the material provided."""
    def line(label, key):
        val = v.get(key, "").strip()
        return f"{label}: {val if val else '(not provided)'}"

    fields_block = "\n".join(line(lbl, k) for k, lbl in NB_FIELD_LABELS.items())
    return (
        "You are an FTC engineering-portfolio reviewer. The team wrote the entry "
        "below themselves. Your job is to CRITIQUE it, not to rewrite it. Do NOT "
        "draft, rewrite, or ghost-write any part of the entry. Do NOT invent test "
        "data, photos, measurements, or decisions. Only identify missing evidence "
        "and the questions the team should answer to strengthen it. The team must "
        "remain the sole author, and all evidence must be real.\n\n"
        "=== ENTRY AND SUPPORTING MATERIAL (team-authored) ===\n"
        f"{fields_block}\n\n"
        "=== REVIEW THE ENTRY FOR ===\n"
        "1) Clear problem statement\n"
        "2) Design alternatives\n"
        "3) Evidence and test data\n"
        "4) Photos / diagrams needed\n"
        "5) Decision justification\n"
        "6) Iteration shown\n"
        "7) Reflection / lesson learned\n"
        "8) Missing judge-relevant details\n\n"
        "=== REQUIRED OUTPUT ===\n"
        "Give a 1-5 rubric score for EACH category above, then a "
        "before-revision checklist the team should complete. Present it as a "
        "table with exactly these columns:\n"
        "Category | Score 1-5 | Missing evidence | Questions team should answer | "
        "Suggested improvement\n\n"
        "Reminder: do not write the entry for the team and do not fabricate any "
        "evidence. If a category has no supporting material, score it low and say "
        "what real evidence the team needs to add."
    )


def _serialize_notebook_revision(changes, evidence_added, media_added,
                                 before_score, after_score, final_link) -> str:
    parts = []
    if changes.strip():
        parts.append(f"Changes made after AI critique: {changes.strip()}")
    if evidence_added.strip():
        parts.append(f"Evidence added: {evidence_added.strip()}")
    if media_added.strip():
        parts.append(f"Photos/data added: {media_added.strip()}")
    if before_score.strip() or after_score.strip():
        parts.append(f"Score before -> after: {before_score.strip() or '-'} -> "
                     f"{after_score.strip() or '-'}")
    if final_link.strip():
        parts.append(f"Final entry link: {final_link.strip()}")
    if not parts:
        return ""
    return "Notebook revision:\n" + "\n".join(f"- {p}" for p in parts)


def render_notebook_critic():
    st.markdown('<span class="az-kicker">Portfolio / Documentation</span>',
                unsafe_allow_html=True)
    st.title("Notebook Critic")
    st.write("Use AI to check whether engineering documentation has enough "
             "evidence, iteration, and reflection.")
    validation_banner()
    st.warning("This tool critiques entries. It should not invent test data, "
               "photos, or decisions — and it never writes the entry for the "
               "team. The team stays the author.", icon="✍️")

    st.subheader("1. Paste your team-authored draft and its evidence")
    subteam = st.text_input("Subteam", value="Portfolio / Documentation",
                            key="nb_subteam")

    v = {}
    v["title"] = st.text_input(NB_FIELD_LABELS["title"], key="nb_title")
    v["subteam_mech"] = st.text_input(NB_FIELD_LABELS["subteam_mech"], key="nb_subteam_mech")
    v["draft"] = st.text_area(NB_FIELD_LABELS["draft"], key="nb_draft", height=180,
                              help="Paste the entry your team wrote. The AI reviews "
                                   "it; it does not rewrite it.")
    c1, c2 = st.columns(2)
    with c1:
        v["problem_explained"] = st.text_area(NB_FIELD_LABELS["problem_explained"],
                                              key="nb_problem_explained")
        v["test_data"] = st.text_area(NB_FIELD_LABELS["test_data"], key="nb_test_data")
        v["decision"] = st.text_area(NB_FIELD_LABELS["decision"], key="nb_decision")
        v["reflection"] = st.text_area(NB_FIELD_LABELS["reflection"], key="nb_reflection")
    with c2:
        v["alternatives"] = st.text_area(NB_FIELD_LABELS["alternatives"], key="nb_alternatives")
        v["photos"] = st.text_area(NB_FIELD_LABELS["photos"], key="nb_photos")
        v["changed"] = st.text_area(NB_FIELD_LABELS["changed"], key="nb_changed")

    st.subheader("2. Generate the critique prompt")
    if st.button("Generate Notebook Critique Prompt", type="primary", key="nb_generate"):
        st.session_state["nb_show_prompt"] = True

    if not st.session_state.get("nb_show_prompt"):
        st.info("Fill in the draft and evidence above, then click "
                "**Generate Notebook Critique Prompt**.")
        return

    generated_prompt = build_notebook_prompt(v)
    st.caption("Copy this into ChatGPT / Claude / Gemini. It reviews and scores the "
               "entry, flags missing evidence, and is instructed never to rewrite "
               "the entry or invent data.")
    st.text_area("Generated prompt (copy this)", value=generated_prompt,
                 height=380, key="nb_prompt_display")

    st.subheader("3. Paste AI output here")
    ai_output = render_ai_output_area("nb_ai_output", generated_prompt, height=220,
                                      placeholder="Paste the AI's rubric table and "
                                                  "checklist exactly as returned.")

    st.subheader("4. Revision after the critique")
    st.caption("Record how the team improved the entry. Saved into the entry's "
               "Result field — no separate database.")
    changes = st.text_area("Changes made after AI critique", key="nb_changes")
    r1, r2 = st.columns(2)
    with r1:
        evidence_added = st.text_area("Evidence added", key="nb_evidence_added")
        before_score = st.text_input("Before score (1-5)", key="nb_before_score")
    with r2:
        media_added = st.text_area("Photos / data added", key="nb_media_added")
        after_score = st.text_input("After score (1-5)", key="nb_after_score")
    final_link = st.text_input("Final entry link", key="nb_final_link",
                               placeholder="Optional link to the revised entry")
    revision_note = _serialize_notebook_revision(
        changes, evidence_added, media_added, before_score, after_score, final_link)

    # Save mapping per spec.
    problem = f"Notebook critique: {v['title'] or '(untitled entry)'}"
    input_summary = " | ".join(x for x in [
        f"title: {v['title']}" if v['title'] else "",
        f"problem: {v['problem_explained'][:50]}" if v['problem_explained'] else "",
        f"evidence: {v['test_data'][:40]}" if v['test_data'] else "",
        f"decision: {v['decision'][:40]}" if v['decision'] else "",
        f"reflection: {v['reflection'][:40]}" if v['reflection'] else "",
    ] if x)

    render_validation_fields(
        "Notebook Critic", subteam, problem, input_summary,
        generated_prompt, ai_output, extra_result_note=revision_note,
    )


# --------------------------------------------------------------------------- #
# Accessibility Translator (fully implemented, bespoke page)
# --------------------------------------------------------------------------- #
AC_AUDIENCES = ["Middle school student", "New FTC member", "Parent", "Sponsor",
                "Judge", "Outreach visitor"]
AC_LENGTHS = ["30 seconds", "1 minute", "2 minutes", "Slide text", "Handout text"]


def build_accessibility_prompt(v: dict) -> str:
    """Assemble the accessible-explanation prompt from the provided material."""
    def line(label, val):
        val = (val or "").strip()
        return f"{label}: {val if val else '(not provided)'}"

    fields_block = "\n".join([
        line("Robotics concept", v.get("concept")),
        line("Audience", v.get("audience")),
        line("Current technical explanation", v.get("explanation")),
        line("Robot-specific context", v.get("context")),
        line("Desired length", v.get("length")),
        line("Words / jargon to avoid", v.get("avoid")),
        line("Required technical terms to include", v.get("require")),
        line("Analogy preference", v.get("analogy")),
        line("Where this explanation will be used", v.get("use_case")),
    ])
    return (
        "You are helping an FTC robotics team explain a technical concept to a "
        "specific audience. Draft an explanation the team will then VERIFY and "
        "EDIT for accuracy before any real use. Keep the explanation technically "
        "accurate; do not oversimplify in a way that becomes wrong. Explain "
        "jargon only when it is needed for that audience. Use the robot-specific "
        "context provided and do not invent facts about the robot. Mark any "
        "technical claim that the team should double-check.\n\n"
        "=== MATERIAL PROVIDED BY THE TEAM ===\n"
        f"{fields_block}\n\n"
        "=== WHAT TO PRODUCE ===\n"
        "1) Simple explanation (matched to the audience and desired length)\n"
        "2) An analogy\n"
        "3) A visual or demo idea\n"
        "4) A check-for-understanding question\n"
        "5) An optional shorter version\n"
        "6) Terms or claims that still need team verification\n\n"
        "Reminder: the team, not you, is responsible for the final wording. "
        "Flag anything you are not certain is accurate rather than stating it "
        "confidently."
    )


def _serialize_accessibility_use(edits, final_used, where, feedback,
                                 clarity, verified_by) -> str:
    parts = []
    if edits.strip():
        parts.append(f"Team edits made: {edits.strip()}")
    if final_used.strip():
        parts.append(f"Final explanation used: {final_used.strip()}")
    if where.strip():
        parts.append(f"Where it was used: {where.strip()}")
    if feedback.strip():
        parts.append(f"Audience feedback: {feedback.strip()}")
    parts.append(f"Clarity rating (1-5): {clarity}")
    if verified_by.strip():
        parts.append(f"Accuracy verified by: {verified_by.strip()}")
    return "Accessibility use:\n" + "\n".join(f"- {p}" for p in parts)


def render_accessibility_translator():
    st.markdown('<span class="az-kicker">Outreach / Training</span>',
                unsafe_allow_html=True)
    st.title("Accessibility Translator")
    st.write("Turn technical robotics concepts into accurate, audience-friendly "
             "explanations.")
    validation_banner()
    st.info("The AI drafts a first version. Team members must check all "
            "explanations for technical accuracy before using them — AI drafts, "
            "the team verifies and edits.", icon="🌍")

    st.subheader("1. Describe the concept and audience")
    subteam = st.text_input("Subteam", value="Outreach / Training", key="ac_subteam")

    v = {}
    c1, c2 = st.columns(2)
    with c1:
        v["concept"] = st.text_input("1. Robotics concept", key="ac_concept",
                                     placeholder="e.g. PID control, odometry")
        v["audience"] = st.selectbox("2. Audience", AC_AUDIENCES, key="ac_audience")
        v["explanation"] = st.text_area("3. Current technical explanation",
                                        key="ac_explanation")
        v["context"] = st.text_area("4. Robot-specific context", key="ac_context")
        v["length"] = st.selectbox("5. Desired length", AC_LENGTHS, key="ac_length")
    with c2:
        v["avoid"] = st.text_area("6. Words or jargon to avoid", key="ac_avoid")
        v["require"] = st.text_area("7. Required technical terms to include",
                                    key="ac_require")
        v["analogy"] = st.text_input("8. Analogy preference", key="ac_analogy",
                                     placeholder="e.g. sports, cooking, driving")
        v["use_case"] = st.text_area("9. Where this explanation will be used",
                                     key="ac_use_case")

    st.subheader("2. Generate the explanation prompt")
    if st.button("Generate Accessible Explanation Prompt", type="primary",
                 key="ac_generate"):
        st.session_state["ac_show_prompt"] = True

    if not st.session_state.get("ac_show_prompt"):
        st.info("Fill in the concept and audience above, then click "
                "**Generate Accessible Explanation Prompt**.")
        return

    generated_prompt = build_accessibility_prompt(v)
    st.caption("Copy this into ChatGPT / Claude / Gemini. It drafts an "
               "audience-appropriate explanation and flags claims the team must "
               "verify — it does not invent robot facts.")
    st.text_area("Generated prompt (copy this)", value=generated_prompt,
                 height=360, key="ac_prompt_display")

    st.subheader("3. Paste AI output here")
    ai_output = render_ai_output_area("ac_ai_output", generated_prompt, height=220,
                                      placeholder="Paste the AI's drafted explanation "
                                                  "exactly as returned, before editing.")

    st.subheader("4. Team verification and use")
    st.caption("The team edits for accuracy, then records real use. Saved into the "
               "entry's Result field — no separate database.")
    edits = st.text_area("Team edits made", key="ac_edits")
    final_used = st.text_area("Final explanation used", key="ac_final_used")
    u1, u2 = st.columns(2)
    with u1:
        where = st.text_input("Where it was used", key="ac_where")
        clarity = st.select_slider("Clarity rating (1-5)",
                                   options=[1, 2, 3, 4, 5], value=3,
                                   key="ac_clarity")
    with u2:
        feedback = st.text_area("Audience feedback", key="ac_feedback")
        verified_by = st.text_input("Accuracy verified by", key="ac_verified_by",
                                    placeholder="Team member who confirmed accuracy")
    use_note = _serialize_accessibility_use(
        edits, final_used, where, feedback, clarity, verified_by)

    # Save mapping per spec.
    problem = (f"Accessible explanation for {v['concept'] or '(concept)'} "
               f"for {v['audience']}")
    input_summary = " | ".join(x for x in [
        f"concept: {v['concept']}" if v['concept'] else "",
        f"audience: {v['audience']}",
        f"current: {v['explanation'][:50]}" if v['explanation'] else "",
        f"length: {v['length']}",
        f"use case: {v['use_case'][:40]}" if v['use_case'] else "",
    ] if x)

    render_validation_fields(
        "Accessibility Translator", subteam, problem, input_summary,
        generated_prompt, ai_output, extra_result_note=use_note,
    )


# --------------------------------------------------------------------------- #
# Code Debugger Log (fully implemented, bespoke page)
# --------------------------------------------------------------------------- #
CD_FIELD_LABELS = {
    "module": "1. Code area / module",
    "language": "2. Programming language",
    "error": "3. Error message or bug behavior",
    "snippet": "4. Code snippet",
    "intended": "5. What the robot was supposed to do",
    "actual": "6. What actually happened",
    "tried": "7. What the team already tried",
    "hardware": "8. Hardware involved",
    "sdk": "9. Relevant FTC SDK / library context",
    "safety": "10. Safety concerns",
    "hypothesis": "11. Current hypothesis",
}


def build_debugger_prompt(v: dict) -> str:
    """Assemble the debugging prompt from only the information provided."""
    def line(label, key):
        val = v.get(key, "").strip()
        return f"{label}: {val if val else '(not provided)'}"

    fields_block = "\n".join(line(lbl, k) for k, lbl in CD_FIELD_LABELS.items())
    return (
        "You are helping FTC programmers debug robot code. You may explain the "
        "error, propose causes, suggest fixes and a test plan, but the team's "
        "programmers own the final code decision and will review and test "
        "everything before it runs. Do not invent robot hardware, sensors, or "
        "library APIs that are not listed below; if something is missing, ASK for "
        "it inside your response instead of assuming. Prefer small, testable "
        "changes over large rewrites, and explain why each change might work.\n\n"
        "=== DEBUGGING CONTEXT ===\n"
        f"{fields_block}\n\n"
        "=== WHAT TO DO ===\n"
        "1) Explain the likely issue in plain language\n"
        "2) Identify possible causes\n"
        "3) Suggest minimal code changes\n"
        "4) Suggest a test plan\n"
        "5) Point out your assumptions\n"
        "6) Warn about any robot-safety risks\n"
        "7) Avoid rewriting large sections unless necessary\n\n"
        "=== REQUIRED OUTPUT ===\n"
        "Return a table with exactly these columns:\n"
        "Possible cause | Evidence | Suggested fix | Test to run | Risk/assumption\n\n"
        "Reminder: prefer the smallest change that can be tested, and never "
        "assume hardware or APIs that were not provided above."
    )


def _serialize_debugger_validation(reviewer, compiled, tested, fix_summary,
                                   commit, helped) -> str:
    parts = [
        f"Programmer reviewer: {reviewer.strip()}" if reviewer.strip() else "",
        f"Did the code compile?: {compiled}",
        f"Tested on robot/simulator?: {tested}",
        f"Final fix summary: {fix_summary.strip()}" if fix_summary.strip() else "",
        f"Commit link: {commit.strip()}" if commit.strip() else "",
        f"Did AI suggestion help?: {helped}",
    ]
    parts = [p for p in parts if p]
    return "Programmer validation:\n" + "\n".join(f"- {p}" for p in parts)


def render_code_debugger():
    st.markdown('<span class="az-kicker">Software / Programming</span>',
                unsafe_allow_html=True)
    st.title("Code Debugger Log")
    st.write("Document how AI helped programmers understand errors, generate "
             "debugging hypotheses, and create test plans.")
    validation_banner()
    st.warning("AI-generated code is not accepted unless it compiles, is reviewed "
               "by a programmer, and is tested on the robot or simulator. AI "
               "assists debugging; humans own the final code decision.", icon="🧑‍💻")

    st.subheader("1. Describe the bug and its context")
    subteam = st.text_input("Subteam", value="Software / Programming", key="cd_subteam")

    v = {}
    c1, c2 = st.columns(2)
    with c1:
        v["module"] = st.text_input(CD_FIELD_LABELS["module"], key="cd_module",
                                    placeholder="e.g. AutoShooter OpMode")
        v["error"] = st.text_area(CD_FIELD_LABELS["error"], key="cd_error")
        v["intended"] = st.text_area(CD_FIELD_LABELS["intended"], key="cd_intended")
        v["tried"] = st.text_area(CD_FIELD_LABELS["tried"], key="cd_tried")
        v["sdk"] = st.text_area(CD_FIELD_LABELS["sdk"], key="cd_sdk")
        v["hypothesis"] = st.text_area(CD_FIELD_LABELS["hypothesis"], key="cd_hypothesis")
    with c2:
        v["language"] = st.text_input(CD_FIELD_LABELS["language"], key="cd_language",
                                      value="Java (FTC SDK)")
        v["actual"] = st.text_area(CD_FIELD_LABELS["actual"], key="cd_actual")
        v["hardware"] = st.text_area(CD_FIELD_LABELS["hardware"], key="cd_hardware")
        v["safety"] = st.text_area(CD_FIELD_LABELS["safety"], key="cd_safety")
    v["snippet"] = st.text_area(CD_FIELD_LABELS["snippet"], key="cd_snippet", height=160,
                                help="Paste only the relevant code. The AI must not "
                                     "assume APIs or hardware you did not include.")

    st.subheader("2. Generate the debugging prompt")
    if st.button("Generate Debugging Prompt", type="primary", key="cd_generate"):
        st.session_state["cd_show_prompt"] = True

    if not st.session_state.get("cd_show_prompt"):
        st.info("Fill in the bug context above, then click "
                "**Generate Debugging Prompt**.")
        return

    generated_prompt = build_debugger_prompt(v)
    st.caption("Copy this into ChatGPT / Claude / Gemini. It prefers small testable "
               "changes, flags safety risks, and is told not to invent hardware or "
               "APIs — your programmers still review and test everything.")
    st.text_area("Generated prompt (copy this)", value=generated_prompt,
                 height=380, key="cd_prompt_display")

    st.subheader("3. Paste AI output here")
    ai_output = render_ai_output_area("cd_ai_output", generated_prompt, height=220,
                                      placeholder="Paste the AI's cause/fix table "
                                                  "exactly as returned. Do not apply "
                                                  "it yet.")

    st.subheader("4. Programmer validation")
    st.caption("No AI-suggested code is accepted until it compiles, is reviewed, and "
               "is tested. Saved into the entry's Result field — no separate "
               "database.")
    reviewer = st.text_input("Programmer reviewer", key="cd_reviewer_prog")
    p1, p2 = st.columns(2)
    with p1:
        compiled = st.radio("Did the code compile?",
                            ["Yes", "No", "Not applicable"], key="cd_compiled",
                            horizontal=True)
        commit = st.text_input("Commit link", key="cd_commit",
                               placeholder="Optional link to the reviewed commit")
    with p2:
        tested = st.radio("Was it tested on robot / simulator?",
                          ["Robot", "Simulator", "No"], key="cd_tested",
                          horizontal=True)
        helped = st.radio("Did the AI suggestion help?",
                          ["Yes", "Partially", "No"], key="cd_helped",
                          horizontal=True)
    fix_summary = st.text_area("Final fix summary", key="cd_fix_summary")
    validation_note = _serialize_debugger_validation(
        reviewer, compiled, tested, fix_summary, commit, helped)

    # Save mapping per spec.
    problem = (f"Code debugging: {v['module'] or '(unspecified module)'} "
               f"— {(v['error'] or '').strip()[:80]}")
    input_summary = " | ".join(x for x in [
        f"module: {v['module']}" if v['module'] else "",
        f"error/bug: {v['error'][:50]}" if v['error'] else "",
        f"intended: {v['intended'][:40]}" if v['intended'] else "",
        f"actual: {v['actual'][:40]}" if v['actual'] else "",
        f"code: {v['snippet'][:40]}" if v['snippet'] else "",
    ] if x)

    render_validation_fields(
        "Code Debugger Log", subteam, problem, input_summary,
        generated_prompt, ai_output, extra_result_note=validation_note,
    )


# --------------------------------------------------------------------------- #
# Home
# --------------------------------------------------------------------------- #
def render_home():
    st.markdown(
        """
        <div class="az-hero">
          <span class="az-kicker">Team #12096 · Absolute Zero · FTC DECODE presented by RTX</span>
          <h1>Absolute Zero AI Command Center</h1>
          <p>Turning team evidence into structured decisions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    validation_banner(show_loop=False)

    st.subheader("How the loop works")
    steps = [
        ("1", "Collect real team evidence", "Bring in actual match data, logs, designs, and notebook text — not guesses."),
        ("2", "Use AI to structure the information", "A tool builds a structured prompt that asks AI to organize and critique."),
        ("3", "Human team members validate", "A reviewer labels the output Accepted, Modified, Rejected, or Needs Testing."),
        ("4", "Take action based on testing and review", "The team acts only after a human validates and, where needed, tests."),
        ("5", "Reflect on benefits, limits, lessons", "Every entry captures what AI helped with and where it fell short."),
    ]
    cols = st.columns(5)
    for col, (n, t, d) in zip(cols, steps):
        col.markdown(
            f'<div class="az-step"><div class="n">STEP {n}</div>'
            f'<div class="t">{t}</div><div class="d">{d}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.subheader("What this is (and is not)")
    st.markdown(
        "- **Is:** a shared, auditable record of how the team uses AI responsibly — "
        "every prompt, every output, every human decision in one log.\n"
        "- **Is not:** a chatbot or an autopilot. The AI never has the final word."
    )

    entries = load_entries()
    st.divider()
    if entries:
        st.caption(f"Shared log: {len(entries)} validated entr"
                   f"{'y' if len(entries)==1 else 'ies'} recorded. "
                   "See Evidence Dashboard for the full picture.")
    else:
        st.info("The shared log is empty. Use any tool tab to record your first "
                "AI interaction — no sample or fake data is pre-loaded.")


# --------------------------------------------------------------------------- #
# Team Tracking Summarizer (fully implemented, bespoke page)
# --------------------------------------------------------------------------- #
TT_MEETING_TYPES = ["Full team", "Build", "Software", "Outreach", "Portfolio",
                    "Strategy", "Leadership"]

TT_FIELD_ORDER = [
    ("date", "1. Meeting date"),
    ("mtype", "2. Meeting type"),
    ("notes", "3. Raw meeting notes"),
    ("deadlines", "4. Known deadlines"),
    ("blockers", "5. Current blockers"),
    ("members", "6. Team members mentioned"),
    ("decisions", "7. Important decisions made"),
    ("unclear", "8. Things that still feel unclear"),
]


def build_team_tracking_prompt(v: dict) -> str:
    """Assemble the meeting-notes prompt from only the material provided."""
    def line(label, key):
        val = v.get(key, "").strip()
        return f"{label}: {val if val else '(not provided)'}"

    fields_block = "\n".join(line(lbl, k) for k, lbl in TT_FIELD_ORDER)
    return (
        "You are helping an FTC team turn messy meeting notes into a clear, "
        "structured task list. Team leads will review and approve your output "
        "before it is used, because you may misread priorities. Do NOT invent "
        "team members or names that are not listed below. If an owner is unclear, "
        "mark it \"Unassigned\". If a deadline is unclear, mark it \"Needs "
        "deadline\". Preserve uncertainty rather than guessing, and clearly "
        "separate CONFIRMED decisions from possible ideas that still need a "
        "decision.\n\n"
        "=== MEETING MATERIAL ===\n"
        f"{fields_block}\n\n"
        "=== WHAT TO PRODUCE ===\n"
        "1) Summary of decisions (confirmed vs. possible ideas, labeled)\n"
        "2) Action items\n"
        "3) Owners\n"
        "4) Suggested deadlines\n"
        "5) Blockers\n"
        "6) Follow-up questions\n"
        "7) Risks if tasks are missed\n"
        "8) Priority levels\n\n"
        "=== REQUIRED OUTPUT ===\n"
        "Return a table with exactly these columns:\n"
        "Task | Owner | Deadline | Priority | Blocker | Follow-up question\n\n"
        "Reminder: use only the names and facts in the notes above. Mark unknown "
        "owners as \"Unassigned\" and unknown deadlines as \"Needs deadline\"."
    )


def _serialize_team_tracking_validation(lead, accepted, changed, rejected,
                                        tracker_link, improved) -> str:
    parts = [
        f"Team lead reviewer: {lead.strip()}" if lead.strip() else "",
        f"Tasks accepted: {accepted.strip()}" if accepted.strip() else "",
        f"Tasks changed: {changed.strip()}" if changed.strip() else "",
        f"Tasks rejected: {rejected.strip()}" if rejected.strip() else "",
        f"Final task tracker link: {tracker_link.strip()}" if tracker_link.strip() else "",
        f"Did this improve clarity?: {improved}",
    ]
    parts = [p for p in parts if p]
    return "Team-lead validation:\n" + "\n".join(f"- {p}" for p in parts)


def render_team_tracking():
    st.markdown('<span class="az-kicker">Team Operations</span>',
                unsafe_allow_html=True)
    st.title("Team Tracking Summarizer")
    st.write("Convert messy meeting notes into clear team action items, blockers, "
             "and follow-ups.")
    validation_banner()
    st.info("AI-generated task lists must be approved by team leads because AI may "
            "misread priorities.", icon="🗒️")

    st.subheader("1. Paste the meeting notes")
    subteam = st.text_input("Subteam", value="Team Operations", key="tt_subteam")

    v = {}
    c1, c2 = st.columns(2)
    with c1:
        v["date"] = st.text_input("1. Meeting date", key="tt_date",
                                  placeholder="e.g. 2026-02-03")
        v["deadlines"] = st.text_area("4. Known deadlines", key="tt_deadlines")
        v["members"] = st.text_area("6. Team members mentioned", key="tt_members",
                                    help="Only these names may be used as owners.")
        v["unclear"] = st.text_area("8. Things that still feel unclear", key="tt_unclear")
    with c2:
        v["mtype"] = st.selectbox("2. Meeting type", TT_MEETING_TYPES, key="tt_mtype")
        v["blockers"] = st.text_area("5. Current blockers", key="tt_blockers")
        v["decisions"] = st.text_area("7. Important decisions made", key="tt_decisions")
    v["notes"] = st.text_area("3. Raw meeting notes", key="tt_notes", height=180,
                              placeholder="Paste the unedited notes. The AI will "
                                          "not invent names or deadlines not present.")

    st.subheader("2. Generate the tracking prompt")
    if st.button("Generate Team Tracking Prompt", type="primary", key="tt_generate"):
        st.session_state["tt_show_prompt"] = True

    if not st.session_state.get("tt_show_prompt"):
        st.info("Paste the meeting notes above, then click "
                "**Generate Team Tracking Prompt**.")
        _team_usage_overview()
        return

    generated_prompt = build_team_tracking_prompt(v)
    st.caption("Copy this into ChatGPT / Claude / Gemini. It structures the notes "
               "into tasks, marks unknown owners/deadlines, and preserves "
               "uncertainty instead of guessing.")
    st.text_area("Generated prompt (copy this)", value=generated_prompt,
                 height=360, key="tt_prompt_display")

    st.subheader("3. Paste AI output here")
    ai_output = render_ai_output_area("tt_ai_output", generated_prompt, height=220,
                                      placeholder="Paste the AI's task table exactly "
                                                  "as returned, before lead approval.")

    st.subheader("4. Team-lead approval")
    st.caption("A team lead approves before any task list is used. Saved into the "
               "entry's Result field — no separate database.")
    lead = st.text_input("Team lead reviewer", key="tt_lead")
    a1, a2 = st.columns(2)
    with a1:
        accepted = st.text_area("Tasks accepted", key="tt_accepted")
        rejected = st.text_area("Tasks rejected", key="tt_rejected")
    with a2:
        changed = st.text_area("Tasks changed", key="tt_changed")
        tracker_link = st.text_input("Final task tracker link", key="tt_tracker",
                                     placeholder="Optional link to the real tracker")
    improved = st.radio("Did this improve clarity?", ["Yes", "Partially", "No"],
                        key="tt_improved", horizontal=True)
    validation_note = _serialize_team_tracking_validation(
        lead, accepted, changed, rejected, tracker_link, improved)

    # Save mapping per spec.
    problem = f"Team tracking for {v['mtype']} meeting on {v['date'] or '(no date)'}"
    input_summary = " | ".join(x for x in [
        f"type: {v['mtype']}",
        f"notes: {v['notes'][:50]}" if v['notes'] else "",
        f"deadlines: {v['deadlines'][:40]}" if v['deadlines'] else "",
        f"blockers: {v['blockers'][:40]}" if v['blockers'] else "",
        f"decisions: {v['decisions'][:40]}" if v['decisions'] else "",
    ] if x)

    render_validation_fields(
        "Team Tracking Summarizer", subteam, problem, input_summary,
        generated_prompt, ai_output, extra_result_note=validation_note,
    )

    _team_usage_overview()


def _team_usage_overview():
    """Small, collapsed overview of AI-usage across the whole log (real data only)."""
    entries = load_entries()
    with st.expander("Team AI-usage overview (all logged entries)"):
        if not entries:
            st.info("No entries yet. This overview fills in as tools are used. "
                    "No fabricated data is shown.")
            return
        df = pd.DataFrame(entries)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total entries", len(df))
        c2.metric("Subteams active", int(df["subteam"].replace("", pd.NA).nunique()))
        c3.metric("Reviewers", int(df["human_reviewer"].replace("", pd.NA).nunique()))
        st.bar_chart(df["subteam"].replace("", "(unspecified)").value_counts())


# --------------------------------------------------------------------------- #
# Evidence Dashboard
# --------------------------------------------------------------------------- #
def _counts_table(series, index_name, value_name="entries"):
    """Simple pandas value_counts as a clean two-column table (no chart libs)."""
    return (series.replace("", "(unspecified)").value_counts()
            .rename_axis(index_name).reset_index(name=value_name))


def render_dashboard():
    st.title("Evidence Dashboard")
    st.caption("How Absolute Zero evaluated and applied AI outputs.")

    entries = load_entries()
    if not entries:
        st.info("No AI feedback entries saved yet.")
        st.write("Entries will appear here automatically after your team uses any "
                 "of the tools and saves a validated entry. This dashboard only "
                 "ever shows real logged data — nothing is fabricated.")
        return

    df = pd.DataFrame(entries)

    # 1) Headline counts.
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total AI entries", len(df))
    c2.metric("Tools used", int(df["tool_name"].replace("", pd.NA).nunique()))
    c3.metric("Subteams", int(df["subteam"].replace("", pd.NA).nunique()))
    c4.metric("Human reviewers", int(df["human_reviewer"].replace("", pd.NA).nunique()))

    # 2-4) Breakdowns (simple pandas counts, no chart libraries).
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown("**Entries by tool**")
        st.dataframe(_counts_table(df["tool_name"], "tool_name"),
                     use_container_width=True, hide_index=True)
    with b2:
        st.markdown("**Entries by validation label**")
        st.dataframe(_counts_table(df["validation_label"], "validation_label"),
                     use_container_width=True, hide_index=True)
    with b3:
        st.markdown("**Entries by subteam**")
        st.dataframe(_counts_table(df["subteam"], "subteam"),
                     use_container_width=True, hide_index=True)

    # 5) Recent entries + 6) filters.
    st.subheader("Recent entries")
    f1, f2, f3 = st.columns(3)
    with f1:
        tool_pick = st.selectbox(
            "Filter by tool", ["All"] + sorted(x for x in df["tool_name"].unique() if x),
            key="ed_tool")
    with f2:
        label_pick = st.selectbox(
            "Filter by validation label",
            ["All"] + sorted(x for x in df["validation_label"].unique() if x),
            key="ed_label")
    with f3:
        subteam_pick = st.selectbox(
            "Filter by subteam", ["All"] + sorted(x for x in df["subteam"].unique() if x),
            key="ed_subteam")

    view = df.copy()
    if tool_pick != "All":
        view = view[view["tool_name"] == tool_pick]
    if label_pick != "All":
        view = view[view["validation_label"] == label_pick]
    if subteam_pick != "All":
        view = view[view["subteam"] == subteam_pick]

    # newest first if timestamps present
    view = view.sort_values("timestamp", ascending=False)
    st.dataframe(
        view[["timestamp", "tool_name", "subteam", "problem",
              "validation_label", "human_reviewer"]],
        use_container_width=True, hide_index=True,
    )
    st.caption(f"Showing {len(view)} of {len(df)} entries.")

    # 7) Download.
    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="ai_feedback_log.csv",
        mime="text/csv",
    )

    # -------- Award Criteria Mapping --------
    st.divider()
    st.subheader("Award Criteria Mapping")
    st.caption("Where each judged criterion is documented in the log above.")
    st.markdown(
        "- **Problem solved** → the `problem` column of each entry.\n"
        "- **AI tools / process used** → the `generated_prompt` and `ai_output` columns.\n"
        "- **Reflection / lessons learned** → the `reflection` column.\n"
        "- **Evidence used / applied** → the `evidence_link` and `result` columns.\n"
        "- **Benefits / challenges** → inferred from the `result` and `reflection` columns.\n"
        "- **Adapted approach** → the `action_taken` and `validation_label` columns."
    )

    # -------- Validation Philosophy --------
    st.subheader("Validation Philosophy")
    label_counts = df["validation_label"].value_counts().to_dict()
    def n(label):
        return int(label_counts.get(label, 0))
    st.markdown(
        f"- **Accepted ({n('Accepted')})** = team verified and used the AI suggestion.\n"
        f"- **Modified ({n('Modified')})** = AI suggestion was partly useful but changed by humans.\n"
        f"- **Rejected ({n('Rejected')})** = AI suggestion was wrong, irrelevant, or untestable.\n"
        f"- **Needs Testing ({n('Needs Testing')})** = AI suggestion is plausible but requires more evidence."
    )
    st.caption("A healthy record includes Modified, Rejected, and Needs Testing "
               "entries — proof that humans, not the AI, made the decisions.")

    # -------- Judge Demo Mode --------
    st.divider()
    st.subheader("Judge Demo Mode")
    st.caption("The most complete entries — full evidence from AI output through "
               "human action, result, reflection, and a linked artifact.")
    complete_cols = ["ai_output", "action_taken", "result", "reflection", "evidence_link"]
    complete = df[df[complete_cols].apply(
        lambda r: all(str(r[c]).strip() for c in complete_cols), axis=1)]
    if complete.empty:
        st.info("No fully-complete entries yet. An entry qualifies once it has a "
                "non-empty AI output, action taken, result, reflection, and "
                "evidence link. Fill those in to feature it here.")
    else:
        top = complete.sort_values("timestamp", ascending=False).head(5)
        for _, row in top.iterrows():
            with st.expander(f"{row['tool_name']} — {row['problem']}"):
                st.markdown(f"**Subteam:** {row['subteam']}  |  "
                            f"**Reviewer:** {row['human_reviewer']}  |  "
                            f"**Validation:** {row['validation_label']}")
                st.markdown(f"**Action taken:** {row['action_taken']}")
                st.markdown(f"**Result:** {row['result']}")
                st.markdown(f"**Reflection:** {row['reflection']}")
                st.markdown(f"**Evidence:** {row['evidence_link']}")


# --------------------------------------------------------------------------- #
# Judge Handout Builder (reads shared log; produces a judge-facing markdown)
# --------------------------------------------------------------------------- #
CENTRAL_LANGUAGE = ("AI helped us structure information, but human testing and "
                    "review determined what we actually used.")


def _md_cell(text: str) -> str:
    """Make a value safe for a one-line markdown table cell; blank -> marker."""
    t = str(text or "").strip().replace("\n", " ").replace("|", "\\|")
    return t if t else "[add evidence]"


def _field_or_marker(text: str) -> str:
    t = str(text or "").strip()
    return t if t else "[add evidence]"


def build_judge_handout_md(rows: list) -> str:
    """Build a polished, honest judge handout from ONLY the selected entries."""
    tools = sorted({r.get("tool_name", "").strip()
                    for r in rows if r.get("tool_name", "").strip()})
    tools_line = ", ".join(tools) if tools else "[add evidence]"

    # Use-case table.
    table = ["| Tool | Problem addressed | What the AI did | Human validation | Result |",
             "|---|---|---|---|---|"]
    for r in rows:
        table.append(
            f"| {_md_cell(r.get('tool_name'))} | {_md_cell(r.get('problem'))} "
            f"| {_md_cell(r.get('input_summary'))} "
            f"| {_md_cell(r.get('validation_label'))} by {_md_cell(r.get('human_reviewer'))} "
            f"| {_md_cell(r.get('result'))} |"
        )
    table_md = "\n".join(table)

    # Benefits: entries the team accepted or modified (AI genuinely helped).
    benefits = []
    for r in rows:
        if r.get("validation_label", "").strip() in ("Accepted", "Modified"):
            benefits.append(
                f"- On \"{_field_or_marker(r.get('problem'))}\", the AI's structuring "
                f"was {r.get('validation_label').strip().lower()} after review; "
                f"team action: {_field_or_marker(r.get('action_taken'))}."
            )
    if not benefits:
        benefits = ["- [add evidence] (no Accepted/Modified entries among the "
                    "featured items yet)"]

    # Challenges: entries rejected or still needing testing (AI fell short / unproven).
    challenges = []
    for r in rows:
        if r.get("validation_label", "").strip() in ("Rejected", "Needs Testing"):
            challenges.append(
                f"- \"{_field_or_marker(r.get('problem'))}\" was marked "
                f"{r.get('validation_label').strip()} — "
                f"{_field_or_marker(r.get('result') or r.get('reflection'))}."
            )
    if not challenges:
        challenges = ["- [add evidence] (no Rejected/Needs-Testing entries among "
                      "the featured items yet)"]

    # Reflections: real reflection text only.
    reflections = [f"- {r.get('reflection').strip()}" for r in rows
                   if r.get("reflection", "").strip()]
    if not reflections:
        reflections = ["- [add evidence]"]

    # Validation method: counts among the featured entries.
    label_counts = {}
    for r in rows:
        lbl = r.get("validation_label", "").strip() or "(unlabeled)"
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
    counts_line = ", ".join(f"{k}: {v}" for k, v in sorted(label_counts.items()))

    problems = [f"- {_field_or_marker(r.get('problem'))}" for r in rows]

    return f"""# Absolute Zero AI Feedback Loop
**Team #12096 "Absolute Zero" — FTC DECODE presented by RTX**

*{CENTRAL_LANGUAGE}*

## Problem Statement
We used AI to work through specific, real team problems and validated every
output before acting. Featured problems:

{chr(10).join(problems)}

## Tools Used
{tools_line}

Each tool produced a structured prompt that a team member ran in an external AI
assistant (ChatGPT / Claude / Gemini). The output was pasted back and reviewed.

## Use Cases
{table_md}

## Benefits
{chr(10).join(benefits)}

## Challenges
{chr(10).join(challenges)}

## Reflection
{chr(10).join(reflections)}

## Validation Method
Every AI output was labeled by a human reviewer as Accepted, Modified, Rejected,
or Needs Testing, and logged with the action taken and the result. Among the
featured entries: {counts_line}. {CENTRAL_LANGUAGE}

---
*Generated from {len(rows)} logged entr{'y' if len(rows)==1 else 'ies'}. "[add "
"evidence]" marks fields the team still needs to fill in — nothing here is "
"fabricated.*
"""


def render_judge_handout():
    st.title("Judge Handout Builder")
    st.caption("Generate a concise, judge-facing summary of your AI use from saved "
               "entries — for the Trailblazer Award interview.")

    entries = load_entries()
    if not entries:
        st.info("No AI feedback entries saved yet.")
        st.write("Use any tool to log validated entries first; then come back to "
                 "build the handout. This page only ever uses your real logged "
                 "data.")
        return

    st.info("This handout is built only from saved entries. Missing fields are "
            "marked \"[add evidence]\" rather than invented.", icon="📝")

    # Build selectable labels for each entry.
    def label_for(i, r):
        return (f"{i+1}. {r.get('tool_name','?')} — "
                f"{(r.get('problem','') or '(no problem)')[:60]} "
                f"[{r.get('validation_label','') or 'unlabeled'}]")

    labels = [label_for(i, r) for i, r in enumerate(entries)]
    default = labels[:min(6, len(labels))]

    st.subheader("1. Choose entries to feature")
    st.caption("Pick 3–6 of your strongest entries. Works with fewer if that is "
               "all you have logged.")
    picked = st.multiselect("Featured entries", labels, default=default,
                            key="jh_pick")

    if len(picked) > 6:
        st.warning("You selected more than 6 entries. A handout is punchiest with "
                   "3–6; consider trimming for the interview.")
    if not picked:
        st.warning("Select at least one entry to generate the handout.")
        return

    idx = [labels.index(p) for p in picked]
    rows = [entries[i] for i in idx]

    md = build_judge_handout_md(rows)

    st.subheader("2. Preview")
    st.markdown(md)

    st.subheader("3. Download")
    st.download_button(
        "Download handout (Markdown)",
        data=md.encode("utf-8"),
        file_name="absolute_zero_ai_feedback_loop.md",
        mime="text/markdown",
    )


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown('<span class="az-kicker">Absolute Zero</span>',
                unsafe_allow_html=True)
    st.markdown("### AI Command Center")
    page = st.radio("Navigate", PAGES, label_visibility="collapsed")
    st.divider()
    sidebar_ai_settings()
    st.divider()
    st.caption("Evidence → AI Structure → Human Validation → Action → Reflection")
    st.caption("AI suggestions must be human-validated before use.")

render_topbar()

if page == "Home":
    render_home()
elif page == "Auto Autopsy":
    render_auto_autopsy()
elif page == "Design Opposition Board":
    render_design_opposition()
elif page == "Scout Question Generator":
    render_scout_generator()
elif page == "Notebook Critic":
    render_notebook_critic()
elif page == "Accessibility Translator":
    render_accessibility_translator()
elif page == "Code Debugger Log":
    render_code_debugger()
elif page == "Team Tracking":
    render_team_tracking()
elif page == "Evidence Dashboard":
    render_dashboard()
elif page == "Judge Handout Builder":
    render_judge_handout()
else:
    render_home()

render_footer()

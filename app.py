"""
Interactive Python/R Coding Tutor — Powered by Claude
Full course using real Pitch Profiler MLB pitching data throughout.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import anthropic
import streamlit as st

st.set_page_config(
    page_title="Pitch Profiler Coding Tutor",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
.stApp { background-color: #0d1117; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #010409 !important;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: #8b949e;
    font-size: 0.78rem;
    margin: 0;
}

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] button {
    background-color: #0d1117 !important;
    border: 1px solid #21262d !important;
    color: #c9d1d9 !important;
    text-align: left !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    padding: 6px 10px !important;
    margin-bottom: 2px !important;
    transition: border-color 0.15s ease, color 0.15s ease !important;
}
[data-testid="stSidebar"] button:hover {
    border-color: #FF6B35 !important;
    color: #FF6B35 !important;
    background-color: #1a1008 !important;
}
[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #1a1008 !important;
    border-color: #FF6B35 !important;
    color: #FF6B35 !important;
    font-weight: 600 !important;
}

/* ── Main area buttons ── */
.stButton > button {
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"] {
    background-color: #FF6B35 !important;
    border-color: #FF6B35 !important;
    color: #ffffff !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #e85d2a !important;
}
.stButton > button[kind="secondary"] {
    background-color: #161b22 !important;
    border-color: #30363d !important;
    color: #c9d1d9 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #8b949e !important;
    color: #e6edf3 !important;
}

/* ── Language toggle radio ── */
[data-testid="stSidebar"] [role="radiogroup"] label {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px 14px;
    color: #8b949e;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.15s;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background-color: #1a1008;
    border-color: #FF6B35;
    color: #FF6B35;
    font-weight: 600;
}

/* ── Lesson header card ── */
.lesson-header {
    padding: 18px 20px;
    border-radius: 10px;
    background-color: #161b22;
    border: 1px solid #21262d;
    margin-bottom: 20px;
}
.phase-tag {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.lesson-title-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 6px;
    line-height: 1.3;
}
.lesson-goal-text {
    font-size: 0.9rem;
    color: #8b949e;
    line-height: 1.5;
}
.concept-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 12px;
}
.concept-tag {
    font-size: 0.72rem;
    padding: 3px 10px;
    border-radius: 20px;
    background-color: #21262d;
    color: #8b949e;
    border: 1px solid #30363d;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background-color: #FF6B35 !important;
    border-radius: 4px;
}
.stProgress > div > div {
    background-color: #21262d !important;
    border-radius: 4px;
}

/* ── Lesson content markdown ── */
.lesson-content h2 {
    color: #FF6B35;
    font-size: 1.05rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 1px solid #21262d;
    padding-bottom: 6px;
    margin-top: 24px;
    margin-bottom: 12px;
}
.lesson-content code {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.85em;
    color: #79c0ff;
}
.lesson-content pre {
    background-color: #161b22 !important;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
}

/* ── Chat panel ── */
.chat-panel-header {
    font-size: 1rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 4px;
}
.chat-panel-sub {
    font-size: 0.8rem;
    color: #8b949e;
    margin-bottom: 12px;
}
[data-testid="stChatMessageContent"] {
    font-size: 0.88rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 4px 8px;
}

/* ── Phase section headers in sidebar ── */
.phase-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 14px 4px 4px 4px;
    margin-bottom: 2px;
}

/* ── Status badges ── */
.status-complete { color: #3fb950; }
.status-current  { color: #FF6B35; }
.status-locked   { color: #484f58; }

/* ── Dividers ── */
hr {
    border-color: #21262d !important;
    margin: 16px 0 !important;
}

/* ── Info/success/error boxes ── */
[data-testid="stAlert"] {
    border-radius: 8px;
    border-left-width: 3px;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
    background-color: #161b22 !important;
}

/* ── Text inputs ── */
[data-testid="stTextInput"] input {
    background-color: #0d1117 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
    border-radius: 6px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #FF6B35 !important;
    box-shadow: 0 0 0 1px #FF6B35 !important;
}

/* ── Chat input ── */
[data-testid="stChatInputTextArea"] {
    background-color: #161b22 !important;
    border-color: #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}
[data-testid="stChatInputTextArea"]:focus {
    border-color: #FF6B35 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background-color: #161b22;
    border-radius: 8px 8px 0 0;
    border: 1px solid #21262d;
    border-bottom: none;
    padding: 4px 6px 0 6px;
    gap: 4px;
}
[data-testid="stTabs"] [role="tab"] {
    color: #8b949e !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
    border-radius: 6px 6px 0 0 !important;
    border: none !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #e6edf3 !important;
    background-color: #0d1117 !important;
    border-bottom: 2px solid #FF6B35 !important;
}
[data-testid="stTabsContent"] {
    border: 1px solid #21262d;
    border-radius: 0 0 8px 8px;
    padding: 12px;
    background-color: #0d1117;
}

/* ── Code editor textarea ── */
textarea[data-testid="stTextArea"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    color: #e6edf3 !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.5 !important;
}
textarea[data-testid="stTextArea"]:focus {
    border-color: #FF6B35 !important;
    box-shadow: 0 0 0 1px #FF6B35 !important;
}

/* ── Output / grade panels ── */
.output-panel {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 14px;
    font-family: 'Consolas', monospace;
    font-size: 0.8rem;
    color: #79c0ff;
    max-height: 180px;
    overflow-y: auto;
    white-space: pre-wrap;
    margin-bottom: 10px;
}
.output-error {
    color: #f78166;
}
.grade-panel {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 14px 16px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
PROGRESS_FILE = Path.home() / ".pp_tutor_progress.json"

PHASE_COLORS = {
    "🚀 Getting Started":   "#FF6B35",
    "🔧 Data Wrangling":    "#58a6ff",
    "📊 Visualization":     "#3fb950",
    "🔬 Advanced Analysis": "#d2a8ff",
    "🤖 Machine Learning":  "#f78166",
}

# ── Curriculum ───────────────────────────────────────────────────────────────
CURRICULUM = [
    {
        "phase": "🚀 Getting Started",
        "lessons": [
            {
                "id": "gs_01",
                "title": "Your First API Call",
                "goal": "Fetch MLB pitcher data from the Pitch Profiler API and load it into a table",
                "concepts": ["HTTP GET requests", "JSON responses", "DataFrame / tibble"],
                "data": "GET_CAREER_PITCHERS — 1,659 pitchers, 103 columns",
            },
            {
                "id": "gs_02",
                "title": "Exploring the Dataset",
                "goal": "Understand what's in the 103-column dataset before touching it",
                "concepts": ["Shape / dimensions", "Column types", "Missing values", "Summary stats"],
                "data": "career_pitchers — era, stuff_plus, whiff_rate, arm_angle, primary_fb_velo",
            },
        ],
    },
    {
        "phase": "🔧 Data Wrangling",
        "lessons": [
            {
                "id": "dw_01",
                "title": "Filtering Pitchers",
                "goal": "Select subsets: qualified starters, lefties, high-whiff arms",
                "concepts": ["Boolean filtering", "Multiple conditions (&, |)", "query() vs filter()"],
                "data": "Filter to IP >= 162, p_throws == 'L', whiff_rate > 0.30",
            },
            {
                "id": "dw_02",
                "title": "Creating New Columns",
                "goal": "Derive K-BB%, stuff tier, and a composite ace score",
                "concepts": ["Column assignment", "Conditional columns", "np.select / case_when"],
                "data": "K-BB%, stuff_tier from stuff_plus, ace_score composite",
            },
            {
                "id": "dw_03",
                "title": "Grouping & Summarizing",
                "goal": "Aggregate stats by handedness, stuff tier, or any grouping",
                "concepts": ["groupby / group_by + summarise", "Multiple aggregations", "Named aggs"],
                "data": "Mean ERA by stuff_tier, avg velo by p_throws, pitch count by pitch_type",
            },
            {
                "id": "dw_04",
                "title": "Joining Datasets",
                "goal": "Combine career_pitchers with career_pitches to analyze full arsenals",
                "concepts": ["Inner / left joins", "Merge on pitcher_id", "Duplicate checks"],
                "data": "career_pitchers + career_pitches joined on pitcher_name or pitcher_id",
            },
        ],
    },
    {
        "phase": "📊 Visualization",
        "lessons": [
            {
                "id": "viz_01",
                "title": "Bar Charts & Rankings",
                "goal": "Show top 20 pitchers by stuff+ with a clean horizontal bar chart",
                "concepts": ["Horizontal bar charts", "Color by value", "Value labels", "Sorting"],
                "data": "Top 20 stuff_plus leaders; ERA leaders among qualified starters",
            },
            {
                "id": "viz_02",
                "title": "Scatter Plots & Correlations",
                "goal": "Explore relationships — stuff+ vs whiff rate, arm angle vs velo",
                "concepts": ["Scatter plots", "Color/size encoding", "Trendlines", "Correlation"],
                "data": "stuff_plus vs whiff_rate, arm_angle vs primary_fb_velo, era vs fip",
            },
            {
                "id": "viz_03",
                "title": "Distributions & Pitch Arsenal",
                "goal": "Visualize arm angle distribution and a pitcher's pitch mix",
                "concepts": ["Histograms", "Box plots by group", "Pie / donut charts", "Faceting"],
                "data": "arm_angle distribution, pitch_type usage %, whiff by pitch_type",
            },
        ],
    },
    {
        "phase": "🔬 Advanced Analysis",
        "lessons": [
            {
                "id": "adv_01",
                "title": "Arm Angle Analysis",
                "goal": "Understand how arm slot affects velo, movement, and outcomes",
                "concepts": ["Binning with pd.cut / cut()", "Group comparisons", "Annotated scatter"],
                "data": "arm_angle bucketed: Submarine < 0, Sidearm 0-20, 3/4 20-45, Overhand > 45",
            },
            {
                "id": "adv_02",
                "title": "Pitch Arsenal Deep Dive",
                "goal": "Rank pitch types by effectiveness — whiff rate, run value, usage",
                "concepts": ["Multi-level groupby", "Ranking within groups", "Heatmaps"],
                "data": "career_pitches — stuff_plus and whiff_rate by pitch_type across the league",
            },
            {
                "id": "adv_03",
                "title": "Building a Pitcher Scouting Report",
                "goal": "Complete pitcher profile: stats + arsenal + percentile ranks vs league",
                "concepts": ["Percentile ranks", "Combining DataFrames", "Clean output formatting"],
                "data": "Any pitcher — overall stats + pitch mix + league comparison",
            },
        ],
    },
    {
        "phase": "🤖 Machine Learning",
        "lessons": [
            {
                "id": "ml_01",
                "title": "Predicting Stuff+ Tier with XGBoost",
                "goal": "Classify pitchers as Elite / Above Avg / Below Avg using their metrics",
                "concepts": ["Train/test split", "Feature engineering", "XGBoost classifier"],
                "data": "Features: era, whiff_rate, primary_fb_velo, arm_angle → Target: stuff_tier",
            },
            {
                "id": "ml_02",
                "title": "Feature Importance & Model Insights",
                "goal": "Learn which metrics drive the model and whether arm angle matters",
                "concepts": ["feature_importances_", "Cross-validation", "Model interpretation"],
                "data": "Feature importance bar chart, does arm_angle predict stuff+?",
            },
        ],
    },
]

ALL_LESSONS = [
    {**lesson, "phase": section["phase"]}
    for section in CURRICULUM
    for lesson in section["lessons"]
]
LESSON_IDS = [l["id"] for l in ALL_LESSONS]

# ── Context strings ──────────────────────────────────────────────────────────
DATA_CONTEXT = """
PITCH PROFILER API — Real MLB pitching data
Base URL: https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon

Endpoints (all return JSON with an "items" array):
  GET_CAREER_PITCHERS/{api_key}           — 1,659 pitchers, 103 columns, career stats since 2020
  GET_CAREER_PITCHES/{api_key}            — 25,694 rows, pitch-level data (one row per pitcher per pitch type)
  GET_SEASON_PITCHERS/{season}/{api_key}  — single-season stats (seasons: 2020–2025)

KEY career_pitchers COLUMNS:
  Identity:    pitcher_name, pitcher_id, p_throws (R/L)
  Workload:    innings_pitched, games_played, games_started, wins, losses
  Traditional: era, fip, whip, babip, left_on_base_percentage
  Stuff grades: stuff_plus, location_plus, pitching_plus (100 = avg, >100 = better)
  Outcomes:    strike_out_percentage, walk_percentage, whiff_rate (0.0–1.0 decimal), strikeouts_per_9
  Batted ball: barrel_percentage, hard_hit, ground_ball_percentage, fly_ball_percentage
  Physical:    arm_angle (degrees; submarine ≈ -150, overhand ≈ 108),
               primary_fb_velo, primary_fb_spin_rate, release_extension
  Quality:     woba, wobacon, xwobacon, run_value_per_100_pitches

KEY career_pitches COLUMNS:
  pitcher_name, pitcher_id, p_throws, pitch_type, pitch_group
  thrown, percentage_thrown, velocity, spin_rate, ivb, hb, vaa, haa
  whiff_rate, stuff_plus, location_plus, pitching_plus, run_value_per_100_pitches
  primary_fb_flag, pitch_rk

NOTES:
- whiff_rate is 0.0–1.0 in raw data (multiply ×100 for %)
- stuff_plus > 100 = above average
- arm_angle negative = submarine/sidearm, positive = overhand
- No "team" column — use pitcher_name and pitcher_id as identifiers
"""

PYTHON_ENV = """
PYTHON ENVIRONMENT:
baseball_data.py helper (caching built in):
  from baseball_data import career_pitchers, career_pitches, season_pitchers
  df = career_pitchers()

Raw requests (teach in early lessons):
  import requests, pandas as pd
  BASE = "https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon"
  df = pd.json_normalize(requests.get(f"{BASE}/GET_CAREER_PITCHERS/{api_key}").json()["items"])

Packages: requests, pandas, numpy, matplotlib, plotly, xgboost, scikit-learn
"""

R_ENV = """
R ENVIRONMENT:
  library(httr); library(jsonlite); library(tidyverse)
  base_url <- "https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon"
  df <- fromJSON(content(GET(paste0(base_url, "/GET_CAREER_PITCHERS/", api_key)), "text"))$items |> as_tibble()

Packages: tidyverse (dplyr, ggplot2, tidyr), httr, jsonlite, xgboost, skimr
Pipe: |>  Verbs: filter, select, mutate, group_by, summarise, arrange, left_join, case_when
"""

# ── Progress ─────────────────────────────────────────────────────────────────
def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text())
        except Exception:
            pass
    return {"completed": []}

def save_progress(p: dict) -> None:
    PROGRESS_FILE.write_text(json.dumps(p, indent=2))

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("language", "Python"),
    ("lesson_idx", 0),
    ("generated", {}),
    ("chat", {}),
    ("code_drafts", {}),
    ("grade_results", {}),
    ("run_output", {}),
    ("progress", load_progress()),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Claude ───────────────────────────────────────────────────────────────────
def _secret(key: str) -> str:
    try:
        return st.secrets.get(key, os.environ.get(key, ""))
    except Exception:
        return os.environ.get(key, "")

def lesson_system_prompt(lesson: dict, language: str) -> str:
    env = PYTHON_ENV if language == "Python" else R_ENV
    return f"""You are an expert {language} coding tutor for Ian Bach — an intermediate developer
learning {language} data skills using real MLB pitching data from the Pitch Profiler API.

{DATA_CONTEXT}
{env}

Lesson: "{lesson['title']}" | Goal: {lesson['goal']}
Concepts: {', '.join(lesson['concepts'])} | Data: {lesson['data']}

Rules:
- Every example MUST use Pitch Profiler data and real column names — no iris/mtcars/toy datasets
- Code must be complete and immediately runnable
- Explain WHY each technique matters for this specific data
- Keep explanations tight — one clear sentence beats two vague ones
- End with a single "Key Takeaway" sentence"""

def chat_system_prompt(lesson: dict, language: str) -> str:
    env = PYTHON_ENV if language == "Python" else R_ENV
    return f"""You are a {language} coding tutor helping with: "{lesson['title']}"
Goal: {lesson['goal']} | Concepts: {', '.join(lesson['concepts'])}

{DATA_CONTEXT}
{env}

Answer questions directly. Show corrected code using real Pitch Profiler column names.
If they paste code, identify the bug and explain why. Keep responses focused and short."""

def generate_lesson(client, lesson: dict, language: str):
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=2500,
        system=lesson_system_prompt(lesson, language),
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": f"""Generate a complete lesson for: "{lesson['title']}"

Use these exact markdown section headers:

## Concept
[2–3 tight paragraphs: what it is, why it matters for this pitching data]

## Code Example
[Complete runnable {language} code. Real columns. Inline comments on key lines. Interesting output.]

## Your Challenge
[A specific task — slightly harder than the example, one real-world twist. Real column names.]

## Hints
[3 progressive hints. Hint 1 = gentle nudge. Hint 3 = nearly the answer.]

## Key Takeaway
[One sentence to remember forever.]"""}],
    ) as stream:
        for text in stream.text_stream:
            yield text

def stream_chat(client, lesson: dict, language: str, history: list):
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=1500,
        system=chat_system_prompt(lesson, language),
        thinking={"type": "adaptive"},
        messages=[{"role": m["role"], "content": m["content"]} for m in history],
    ) as stream:
        for text in stream.text_stream:
            yield text

def run_code(code: str, language: str) -> tuple:
    """Run code locally, return (stdout, stderr, success)."""
    tutor_dir = str(Path(__file__).parent)
    try:
        if language == "Python":
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=30, cwd=tutor_dir,
            )
        else:
            result = subprocess.run(
                ["Rscript", "-e", code],
                capture_output=True, text=True, timeout=30, cwd=tutor_dir,
            )
        return result.stdout.strip(), result.stderr.strip(), result.returncode == 0
    except FileNotFoundError:
        return "", f"{language} interpreter not found. Make sure {'Python' if language == 'Python' else 'R'} is installed.", False
    except subprocess.TimeoutExpired:
        return "", "Code timed out after 30 seconds.", False

def grade_code(client, lesson: dict, language: str, code: str, stdout: str, stderr: str):
    generated = st.session_state.generated.get(lesson["id"], "")
    challenge = ""
    if "## Your Challenge" in generated:
        start = generated.index("## Your Challenge")
        end = generated.index("## Hints") if "## Hints" in generated else len(generated)
        challenge = generated[start:end].strip()

    output_block = stdout if stdout else "(no output)"
    if stderr:
        output_block += f"\n\nERRORS:\n{stderr}"

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=1200,
        thinking={"type": "adaptive"},
        system=f"""You are a {language} coding tutor grading a student submission.
{DATA_CONTEXT}
Lesson: "{lesson['title']}" | Goal: {lesson['goal']}
Concepts: {', '.join(lesson['concepts'])}""",
        messages=[{"role": "user", "content": f"""Grade this code. Be honest, specific, and encouraging.

{challenge if challenge else f'Lesson goal: {lesson["goal"]}'}

STUDENT CODE:
```
{code}
```

OUTPUT:
{output_block}

Use EXACTLY these headers:

## Score
X/10 — one sentence verdict.

## What Works
- bullet points on correct/well-done parts

## What to Fix
- specific issues or "Nothing — great job!" if perfect

## Improved Version
Show corrected code ONLY if there are real fixes needed. Skip this section if the code is correct.
"""}],
    ) as stream:
        for text in stream.text_stream:
            yield text

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚾ Coding Tutor")
    st.markdown("<p style='color:#8b949e;margin-top:-8px'>Learn Python or R with real MLB data</p>", unsafe_allow_html=True)
    st.divider()

    with st.expander("🔑 API Keys", expanded=not bool(_secret("ANTHROPIC_API_KEY"))):
        anthropic_key = st.text_input("Anthropic Key", value=_secret("ANTHROPIC_API_KEY"), type="password", key="ak")
        pp_key = st.text_input("Pitch Profiler Key", value=_secret("PITCH_PROFILER_API_KEY"), type="password", key="ppk")
        st.caption("Persist keys → `~/.streamlit/secrets.toml`")

    if not anthropic_key:
        st.warning("Enter your Anthropic API key above to start.")
        st.stop()

    st.divider()

    # Language toggle
    st.markdown("<p style='color:#8b949e;font-size:0.75rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px'>Language</p>", unsafe_allow_html=True)
    lang = st.radio("lang", ["Python", "R"], horizontal=True,
                    index=0 if st.session_state.language == "Python" else 1,
                    label_visibility="collapsed")
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.session_state.generated = {}
        st.session_state.chat = {}
        st.rerun()

    st.divider()

    # Progress
    completed = set(st.session_state.progress.get("completed", []))
    done, total = len(completed), len(ALL_LESSONS)
    st.markdown(f"<p style='color:#8b949e;font-size:0.75rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px'>PROGRESS — {done}/{total}</p>", unsafe_allow_html=True)
    st.progress(done / total)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Lesson nav
    for section in CURRICULUM:
        phase = section["phase"]
        color = PHASE_COLORS.get(phase, "#8b949e")
        st.markdown(f"<p class='phase-header' style='color:{color}'>{phase}</p>", unsafe_allow_html=True)
        for lesson in section["lessons"]:
            is_done    = lesson["id"] in completed
            is_current = ALL_LESSONS[st.session_state.lesson_idx]["id"] == lesson["id"]
            icon = "✓" if is_done else ("▶" if is_current else "·")
            label = f"{icon}  {lesson['title']}"
            btn_type = "primary" if is_current else "secondary"
            if st.button(label, key=f"nav_{lesson['id']}", use_container_width=True, type=btn_type):
                st.session_state.lesson_idx = LESSON_IDS.index(lesson["id"])
                st.rerun()

    st.divider()
    if st.button("Reset progress", type="secondary", use_container_width=True):
        st.session_state.progress = {"completed": []}
        save_progress(st.session_state.progress)
        st.rerun()

# ── Main ──────────────────────────────────────────────────────────────────────
client      = anthropic.Anthropic(api_key=anthropic_key)
lesson      = ALL_LESSONS[st.session_state.lesson_idx]
lesson_id   = lesson["id"]
language    = st.session_state.language
phase_color = PHASE_COLORS.get(lesson["phase"], "#FF6B35")
lesson_num  = st.session_state.lesson_idx + 1

if lesson_id not in st.session_state.chat:
    st.session_state.chat[lesson_id] = []

# ── Lesson header ─────────────────────────────────────────────────────────────
concept_tags = "".join(f'<span class="concept-tag">{c}</span>' for c in lesson["concepts"])
st.markdown(f"""
<div class="lesson-header" style="border-left: 4px solid {phase_color};">
    <div class="phase-tag" style="color:{phase_color}">{lesson['phase']}  ·  Lesson {lesson_num} of {len(ALL_LESSONS)}</div>
    <div class="lesson-title-text">{lesson['title']}</div>
    <div class="lesson-goal-text">{lesson['goal']}</div>
    <div class="concept-tags">{concept_tags}</div>
</div>
""", unsafe_allow_html=True)

# Prev / Next nav
nav_l, nav_r, nav_spacer = st.columns([1, 1, 6])
with nav_l:
    if st.button("← Prev", disabled=st.session_state.lesson_idx == 0, use_container_width=True):
        st.session_state.lesson_idx -= 1
        st.rerun()
with nav_r:
    if st.button("Next →", disabled=st.session_state.lesson_idx == len(ALL_LESSONS) - 1, use_container_width=True):
        st.session_state.lesson_idx += 1
        st.rerun()

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Two-column layout ─────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    if lesson_id not in st.session_state.generated:
        with st.spinner(f"Building your {language} lesson…"):
            gen = st.empty()
            text = ""
            try:
                for chunk in generate_lesson(client, lesson, language):
                    text += chunk
                    gen.markdown(text + "▌")
                gen.markdown(text)
                st.session_state.generated[lesson_id] = text
            except anthropic.AuthenticationError:
                gen.error("Invalid Anthropic API key. Get a new one at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) and paste it in the sidebar.")
            except Exception as e:
                gen.error(f"Error generating lesson: {e}")
    else:
        st.markdown(st.session_state.generated[lesson_id])

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    btn_a, btn_b = st.columns(2)
    with btn_a:
        if st.button("🔄  Regenerate", key=f"regen_{lesson_id}", use_container_width=True):
            del st.session_state.generated[lesson_id]
            st.rerun()
    with btn_b:
        is_complete = lesson_id in completed
        if not is_complete:
            if st.button("✅  Mark complete", key=f"done_{lesson_id}", type="primary", use_container_width=True):
                st.session_state.progress.setdefault("completed", []).append(lesson_id)
                save_progress(st.session_state.progress)
                if st.session_state.lesson_idx < len(ALL_LESSONS) - 1:
                    st.session_state.lesson_idx += 1
                st.rerun()
        else:
            st.success("Complete ✓", icon="⚾")

# ── Right panel: Chat + Code tabs ─────────────────────────────────────────────
with right:
    tab_chat, tab_code = st.tabs(["💬 Ask Tutor", "💻 Code Playground"])

    # ── Chat tab ──────────────────────────────────────────────────────────────
    with tab_chat:
        chat_history = st.session_state.chat[lesson_id]
        chat_box = st.container(height=400)
        with chat_box:
            if not chat_history:
                st.markdown("<p style='color:#484f58;font-size:0.85rem;padding:8px 0'>No messages yet. Ask anything about this lesson.</p>", unsafe_allow_html=True)
            for msg in chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_input = st.chat_input(f"Ask about {lesson['title']}…", key=f"ci_{lesson_id}")
        if user_input:
            chat_history.append({"role": "user", "content": user_input})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(user_input)
                with st.chat_message("assistant"):
                    ph = st.empty()
                    resp = ""
                    try:
                        for chunk in stream_chat(client, lesson, language, chat_history):
                            resp += chunk
                            ph.markdown(resp + "▌")
                        ph.markdown(resp)
                    except anthropic.AuthenticationError:
                        resp = "Invalid API key — update it in the sidebar."
                        ph.error(resp)
                    except Exception as e:
                        resp = f"Error: {e}"
                        ph.error(resp)
            chat_history.append({"role": "assistant", "content": resp})
            st.session_state.chat[lesson_id] = chat_history

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        qa1, qa2, qa3 = st.columns(3)
        with qa1:
            if st.button("💡 Hint", key=f"hint_{lesson_id}", use_container_width=True):
                chat_history.append({"role": "user", "content": "Give me a hint for the challenge without giving away the answer."})
                st.session_state.chat[lesson_id] = chat_history
                st.rerun()
        with qa2:
            if st.button("🔍 Explain", key=f"explain_{lesson_id}", use_container_width=True):
                chat_history.append({"role": "user", "content": "Walk me through the code example line by line."})
                st.session_state.chat[lesson_id] = chat_history
                st.rerun()
        with qa3:
            if st.button("🗑 Clear", key=f"clear_{lesson_id}", use_container_width=True):
                st.session_state.chat[lesson_id] = []
                st.rerun()

    # ── Code Playground tab ───────────────────────────────────────────────────
    with tab_code:
        st.markdown(f"<p style='color:#8b949e;font-size:0.82rem;margin-bottom:8px'>Write your solution to the challenge below, then hit <strong style='color:#FF6B35'>Run & Grade</strong>.</p>", unsafe_allow_html=True)

        default_code = st.session_state.code_drafts.get(lesson_id, f"# {lesson['title']} — Your solution\n# Goal: {lesson['goal']}\n\n")
        code_input = st.text_area(
            "Your code",
            value=default_code,
            height=260,
            key=f"code_{lesson_id}",
            label_visibility="collapsed",
            placeholder=f"# Write your {language} solution here…",
        )
        st.session_state.code_drafts[lesson_id] = code_input

        run_col, clear_col = st.columns([3, 1])
        with run_col:
            run_btn = st.button("▶  Run & Grade", key=f"run_{lesson_id}", type="primary", use_container_width=True)
        with clear_col:
            if st.button("🗑", key=f"clrcode_{lesson_id}", use_container_width=True):
                st.session_state.code_drafts[lesson_id] = f"# {lesson['title']} — Your solution\n# Goal: {lesson['goal']}\n\n"
                st.session_state.grade_results.pop(lesson_id, None)
                st.session_state.run_output.pop(lesson_id, None)
                st.rerun()

        if run_btn and code_input.strip():
            with st.spinner("Running your code…"):
                stdout, stderr, success = run_code(code_input, language)
                st.session_state.run_output[lesson_id] = (stdout, stderr, success)
            st.session_state.grade_results.pop(lesson_id, None)

        # Output panel
        if lesson_id in st.session_state.run_output:
            stdout, stderr, success = st.session_state.run_output[lesson_id]
            label = "Output" if success else "Output (errors)"
            color_cls = "" if success else "output-error"
            display = stdout if stdout else "(no output)"
            if stderr:
                display += f"\n\n{stderr}"
            st.markdown(f"<p style='color:#8b949e;font-size:0.75rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin:10px 0 4px'>{label}</p>", unsafe_allow_html=True)
            st.markdown(f'<div class="output-panel {color_cls}">{display}</div>', unsafe_allow_html=True)

            # Grade
            if lesson_id not in st.session_state.grade_results:
                grade_ph = st.empty()
                grade_text = ""
                try:
                    with st.spinner("Claude is grading your code…"):
                        for chunk in grade_code(client, lesson, language, code_input, stdout, stderr):
                            grade_text += chunk
                            grade_ph.markdown(grade_text + "▌")
                    grade_ph.markdown(grade_text)
                    st.session_state.grade_results[lesson_id] = grade_text
                except anthropic.AuthenticationError:
                    grade_ph.error("Invalid API key — update it in the sidebar.")
                except Exception as e:
                    grade_ph.error(f"Grading error: {e}")
            else:
                st.markdown(st.session_state.grade_results[lesson_id])

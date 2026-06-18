"""
Interactive Python/R Coding Tutor — Powered by Claude
Full course using real Pitch Profiler MLB pitching data throughout.
"""

import json
import os
from pathlib import Path
import anthropic
import streamlit as st

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pitch Profiler Coding Tutor",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROGRESS_FILE = Path.home() / ".pp_tutor_progress.json"

# ── Curriculum ───────────────────────────────────────────────────────────────
CURRICULUM = [
    {
        "phase": "🚀 Getting Started",
        "lessons": [
            {
                "id": "gs_01",
                "title": "Your First API Call",
                "goal": "Fetch MLB pitcher data from the Pitch Profiler API and load it into a table",
                "concepts": ["HTTP GET requests", "JSON responses", "Creating a DataFrame / tibble"],
                "data": "GET_CAREER_PITCHERS — 1,659 pitchers, 103 columns",
            },
            {
                "id": "gs_02",
                "title": "Exploring the Dataset",
                "goal": "Understand what's in the 103-column dataset before touching it",
                "concepts": ["Shape / dimensions", "Column types", "Missing values", "Summary statistics"],
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
                "concepts": ["Column assignment", "Conditional columns", "np.select / case_when", "Vectorized math"],
                "data": "K-BB% = k_pct - bb_pct, stuff_tier from stuff_plus, ace_score composite",
            },
            {
                "id": "dw_03",
                "title": "Grouping & Summarizing",
                "goal": "Aggregate stats by handedness, stuff tier, or any grouping",
                "concepts": ["groupby / group_by + summarise", "Multiple aggregations", "Named aggregations"],
                "data": "Mean ERA by stuff_tier, avg velo by p_throws, pitch count by pitch_type",
            },
            {
                "id": "dw_04",
                "title": "Joining Datasets",
                "goal": "Combine career_pitchers with career_pitches to analyze full arsenals",
                "concepts": ["Inner / left joins", "Merge on pitcher_id", "Checking for duplicates after joining"],
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
                "goal": "Explore relationships between metrics — stuff+ vs whiff rate, arm angle vs velo",
                "concepts": ["Scatter plots", "Color/size encoding", "Trendlines", "Correlation"],
                "data": "stuff_plus vs whiff_rate, arm_angle vs primary_fb_velo, era vs fip",
            },
            {
                "id": "viz_03",
                "title": "Distributions & Pitch Arsenal",
                "goal": "Visualize arm angle distribution and a pitcher's pitch mix",
                "concepts": ["Histograms", "Box plots by group", "Pie / donut charts", "Faceting"],
                "data": "arm_angle distribution, pitch_type usage % (career_pitches), whiff by pitch_type",
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
                "concepts": ["Binning with pd.cut / cut()", "Group comparisons", "Annotated scatter plots"],
                "data": "arm_angle bucketed: Submarine < 0, Sidearm 0-20, Low 3/4 20-30, 3/4 30-45, Overhand > 45",
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
                "goal": "Build a complete pitcher profile: stats + arsenal + percentile ranks vs league",
                "concepts": ["Percentile ranks", "Combining DataFrames", "Clean output formatting"],
                "data": "Any pitcher from the dataset — overall stats + pitch mix + league comparison",
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
                "concepts": ["Train/test split", "Feature engineering", "XGBoost classifier", "Accuracy + classification report"],
                "data": "Features: era, whiff_rate, primary_fb_velo, arm_angle, k_pct, bb_pct → Target: stuff_tier",
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

# All lessons as a flat list for navigation
ALL_LESSONS = [
    {**lesson, "phase": section["phase"]}
    for section in CURRICULUM
    for lesson in section["lessons"]
]
LESSON_IDS = [l["id"] for l in ALL_LESSONS]


# ── Data & API context ───────────────────────────────────────────────────────
DATA_CONTEXT = """
PITCH PROFILER API — Real MLB pitching data

Base URL: https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon

Endpoints (all return JSON with an "items" array):
  GET_CAREER_PITCHERS/{api_key}           — 1,659 pitchers, 103 columns, career stats since 2020
  GET_CAREER_PITCHES/{api_key}            — 25,694 rows, pitch-level career data (one row per pitcher per pitch type)
  GET_SEASON_PITCHERS/{season}/{api_key}  — single-season pitcher stats (seasons: 2020–2025)
  GET_TEAM_SEASON_PITCHERS/{season}/{api_key}
  GET_SEASON_PITCHES/{season}/{api_key}
  GET_TEAM_SEASON_PITCHES/{season}/{api_key}

KEY career_pitchers COLUMNS:
  Identity:   pitcher_name, pitcher_id, p_throws (R/L), game_type
  Workload:   innings_pitched, ip_decimal, games_played, games_started, wins, losses, saves
  Traditional: era, fip, whip, babip, left_on_base_percentage
  Stuff grades: stuff_plus, location_plus, pitching_plus, mix_plus, match_plus, max_plus
                (all centered at 100 = league avg; higher = better)
  Run values: stuff_run_value_per_100, location_run_value_per_100, pitching_run_value_per_100
  Outcomes:   strike_out_percentage, walk_percentage, strike_out_minus_walk_percentage,
              whiff_rate (raw: 0.0–1.0 decimal), strikeouts_per_9, walks_per_9
  Batted ball: barrel_percentage, hard_hit, ground_ball_percentage, fly_ball_percentage
  Physical:   arm_angle (degrees; submarine ≈ -150 to overhand ≈ 108),
              primary_fb_velo, primary_fb_spin_rate, release_extension
  Quality of contact: woba, wobacon, xwobacon, run_value_per_100_pitches
  Zone:       heart_percentage, shadow_percentage, chase_percentage, zone_percentage

KEY career_pitches COLUMNS:
  pitcher_name, pitcher_id, p_throws, pitch_type, pitch_group
  thrown, percentage_thrown
  velocity, spin_rate, ivb (induced vert break), hb (horiz break), vaa, haa
  whiff_rate, stuff_plus, location_plus, pitching_plus
  run_value_per_100_pitches, woba, barrel_percentage
  primary_fb_flag, pitch_rk (rank of pitch in arsenal)

NOTES:
- whiff_rate in raw data is 0.0–1.0 (multiply by 100 for %)
- stuff_plus > 100 = above average, < 100 = below average
- arm_angle: negative = submarine/sidearm (below horizontal), positive = overhand
- No "team" column in the data — pitcher_name and pitcher_id are the identifiers
"""

PYTHON_ENV = """
PYTHON ENVIRONMENT:
The project has baseball_data.py with these helper functions (handles caching automatically):
  from baseball_data import career_pitchers, career_pitches, season_pitchers
  df = career_pitchers()   # returns pd.DataFrame

Or raw requests (teach this in early lessons):
  import requests, pandas as pd
  BASE = "https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon"
  r = requests.get(f"{BASE}/GET_CAREER_PITCHERS/{api_key}")
  df = pd.json_normalize(r.json()['items'])

Available packages: requests, pandas, numpy, matplotlib, plotly, xgboost, scikit-learn, statsmodels
"""

R_ENV = """
R ENVIRONMENT:
Use httr + jsonlite for API calls, tidyverse for wrangling and visualization:
  library(httr); library(jsonlite); library(tidyverse)
  base_url <- "https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon"
  resp <- GET(paste0(base_url, "/GET_CAREER_PITCHERS/", api_key))
  df <- fromJSON(content(resp, "text", encoding="UTF-8"))$items %>% as_tibble()

Key packages: tidyverse (dplyr, ggplot2, tidyr, stringr), httr, jsonlite, xgboost, skimr
dplyr pipe: use |> (native R 4.1+) or %>% (magrittr)
dplyr verbs: filter(), select(), mutate(), group_by(), summarise(), arrange(), left_join(), case_when()
ggplot2 for all visualization
"""


# ── Progress helpers ─────────────────────────────────────────────────────────
def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text())
        except Exception:
            pass
    return {"completed": []}


def save_progress(progress: dict) -> None:
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


# ── Session state init ───────────────────────────────────────────────────────
if "language" not in st.session_state:
    st.session_state.language = "Python"
if "lesson_idx" not in st.session_state:
    st.session_state.lesson_idx = 0
if "generated" not in st.session_state:
    st.session_state.generated = {}      # lesson_id → generated content string
if "chat" not in st.session_state:
    st.session_state.chat = {}           # lesson_id → list of {role, content}
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "hints_shown" not in st.session_state:
    st.session_state.hints_shown = {}   # lesson_id → bool
if "show_challenge" not in st.session_state:
    st.session_state.show_challenge = {}


# ── Claude helpers ───────────────────────────────────────────────────────────
def make_client(api_key: str) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key)


def lesson_system_prompt(lesson: dict, language: str) -> str:
    env = PYTHON_ENV if language == "Python" else R_ENV
    lang_note = (
        "Use Python with pandas, plotly, and requests throughout."
        if language == "Python"
        else "Use R with tidyverse (dplyr, ggplot2), httr, and jsonlite throughout."
    )
    return f"""You are an expert {language} coding tutor teaching Ian Bach to code using real MLB pitching data
from the Pitch Profiler API. Ian is an intermediate developer comfortable with Oracle REST APIs and
general programming, but building {language} data skills.

{DATA_CONTEXT}

{env}

Current lesson: "{lesson['title']}"
Learning goal: {lesson['goal']}
Key concepts to cover: {', '.join(lesson['concepts'])}
Data focus: {lesson['data']}

Teaching rules:
- {lang_note}
- Every code example MUST use the Pitch Profiler data — no toy datasets or iris/mtcars
- Be concrete: show actual column names, actual output examples
- Code must be complete and runnable
- Explain WHY, not just what — give context for why a technique matters for this data
- Keep explanations tight — don't pad. One clear sentence beats two vague ones
- When reviewing code: lead with what's right, then one specific improvement with corrected code
- Always give a "Key Takeaway" at the end: one sentence the student should remember"""


def chat_system_prompt(lesson: dict, language: str) -> str:
    env = PYTHON_ENV if language == "Python" else R_ENV
    return f"""You are a {language} coding tutor helping Ian Bach with a specific lesson.

{DATA_CONTEXT}

{env}

Current lesson: "{lesson['title']}" — Goal: {lesson['goal']}
Concepts: {', '.join(lesson['concepts'])}

You are in a Q&A chat. The student is working through code challenges using the Pitch Profiler data.
- Answer the specific question directly — don't re-teach the whole lesson
- Show corrected code when relevant, always using the real Pitch Profiler data and column names
- If they paste code, identify the bug and explain why it happened
- Keep responses focused. Short and precise beats long and comprehensive."""


def generate_lesson(client: anthropic.Anthropic, lesson: dict, language: str):
    """Stream lesson content from Claude."""
    prompt = f"""Generate a complete lesson for: "{lesson['title']}"

Structure your response with these exact sections using markdown headers:

## Concept
[2-3 focused paragraphs explaining the core idea and WHY it matters for working with this pitching data]

## Code Example
[Complete, runnable {language} code using the Pitch Profiler API data. Use actual column names.
Add brief inline comments explaining key lines. Should produce visible, interesting output.]

## Your Challenge
[A specific coding task the student must complete. Reference real columns and real data from the API.
Make it slightly harder than the example — one real-world twist added.]

## Hints
[3 progressive hints, numbered. First hint is gentle, last hint is almost the answer.]

## Key Takeaway
[One sentence: the single most important thing to remember from this lesson.]"""

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=2500,
        system=lesson_system_prompt(lesson, language),
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
    ) as stream:
        for text in stream.text_stream:
            yield text


def stream_chat_response(client: anthropic.Anthropic, lesson: dict, language: str, history: list):
    """Stream a chat response from Claude."""
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
    ]
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=1500,
        system=chat_system_prompt(lesson, language),
        messages=messages,
        thinking={"type": "adaptive"},
    ) as stream:
        for text in stream.text_stream:
            yield text


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚾ Coding Tutor")
    st.caption("Learn Python or R with real MLB pitching data")
    st.divider()

    # API keys — reads from ~/.streamlit/secrets.toml, then env vars, then UI input
    def _secret(key: str) -> str:
        try:
            return st.secrets.get(key, os.environ.get(key, ""))
        except Exception:
            return os.environ.get(key, "")

    with st.expander("🔑 API Keys", expanded=not bool(_secret("ANTHROPIC_API_KEY"))):
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=_secret("ANTHROPIC_API_KEY"),
            type="password",
            key="anthropic_key_input",
        )
        pp_key = st.text_input(
            "Pitch Profiler API Key",
            value=_secret("PITCH_PROFILER_API_KEY"),
            type="password",
            key="pp_key_input",
        )
        st.caption("Keys saved? Add them to `~/.streamlit/secrets.toml` so they auto-fill.")

    if not anthropic_key:
        st.warning("Add your Anthropic API key to begin.")
        st.stop()

    st.divider()

    # Language toggle
    st.subheader("Language")
    lang = st.radio(
        "Select language",
        ["Python", "R"],
        horizontal=True,
        index=0 if st.session_state.language == "Python" else 1,
        label_visibility="collapsed",
    )
    if lang != st.session_state.language:
        st.session_state.language = lang
        # Clear generated content so lessons regenerate in the new language
        st.session_state.generated = {}
        st.session_state.chat = {}
        st.rerun()

    st.divider()

    # Course navigation
    st.subheader("Course")
    completed = set(st.session_state.progress.get("completed", []))
    total = len(ALL_LESSONS)
    done = len(completed)
    st.progress(done / total, text=f"{done}/{total} lessons complete")

    for section in CURRICULUM:
        st.markdown(f"**{section['phase']}**")
        for lesson in section["lessons"]:
            is_done = lesson["id"] in completed
            is_current = ALL_LESSONS[st.session_state.lesson_idx]["id"] == lesson["id"]
            icon = "✅" if is_done else ("▶️" if is_current else "○")
            label = f"{icon} {lesson['title']}"
            if st.button(label, key=f"nav_{lesson['id']}", use_container_width=True,
                         type="primary" if is_current else "secondary"):
                idx = LESSON_IDS.index(lesson["id"])
                st.session_state.lesson_idx = idx
                st.rerun()

    st.divider()
    if st.button("🔄 Reset all progress", type="secondary", use_container_width=True):
        st.session_state.progress = {"completed": []}
        save_progress(st.session_state.progress)
        st.rerun()


# ── Main content ─────────────────────────────────────────────────────────────
client = make_client(anthropic_key)
lesson = ALL_LESSONS[st.session_state.lesson_idx]
lesson_id = lesson["id"]
language = st.session_state.language

# Init per-lesson state
if lesson_id not in st.session_state.chat:
    st.session_state.chat[lesson_id] = []
if lesson_id not in st.session_state.hints_shown:
    st.session_state.hints_shown[lesson_id] = False

# Header
col_title, col_nav = st.columns([4, 1])
with col_title:
    st.markdown(f"### {lesson['phase']}  ·  {lesson['title']}")
    st.caption(f"**Goal:** {lesson['goal']}")
with col_nav:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Prev", disabled=st.session_state.lesson_idx == 0):
            st.session_state.lesson_idx -= 1
            st.rerun()
    with c2:
        if st.button("Next →", disabled=st.session_state.lesson_idx == len(ALL_LESSONS) - 1):
            st.session_state.lesson_idx += 1
            st.rerun()

st.divider()

# ── Lesson content (two-column layout) ──────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    # Generate or show lesson
    if lesson_id not in st.session_state.generated:
        st.info(f"Generating {language} lesson using Pitch Profiler data...")
        gen_container = st.empty()
        full_text = ""
        try:
            for chunk in generate_lesson(client, lesson, language):
                full_text += chunk
                gen_container.markdown(full_text + "▌")
            gen_container.markdown(full_text)
            st.session_state.generated[lesson_id] = full_text
        except anthropic.AuthenticationError:
            gen_container.error(
                "**Invalid Anthropic API key.** "
                "Go to [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) "
                "to create a new key, then paste it in the 🔑 API Keys section of the sidebar."
            )
        except Exception as e:
            gen_container.error(f"Failed to generate lesson: {e}")
    else:
        st.markdown(st.session_state.generated[lesson_id])

    st.divider()

    # Regenerate button
    col_regen, col_done = st.columns([1, 1])
    with col_regen:
        if st.button("🔄 Regenerate lesson", key=f"regen_{lesson_id}"):
            del st.session_state.generated[lesson_id]
            st.rerun()
    with col_done:
        is_complete = lesson_id in st.session_state.progress.get("completed", [])
        if not is_complete:
            if st.button("✅ Mark complete", key=f"done_{lesson_id}", type="primary"):
                if "completed" not in st.session_state.progress:
                    st.session_state.progress["completed"] = []
                st.session_state.progress["completed"].append(lesson_id)
                save_progress(st.session_state.progress)
                # Auto-advance to next lesson
                if st.session_state.lesson_idx < len(ALL_LESSONS) - 1:
                    st.session_state.lesson_idx += 1
                st.rerun()
        else:
            st.success("Lesson complete ✅")

with right:
    st.subheader(f"💬 Ask a question")
    st.caption(f"Stuck on the challenge? Ask anything about this lesson.")

    # Show API key reminder if pp_key not set
    if not pp_key:
        st.info("💡 Add your Pitch Profiler API key in the sidebar to run the code examples.")

    # Chat history
    chat_container = st.container(height=460)
    with chat_container:
        chat_history = st.session_state.chat[lesson_id]
        if not chat_history:
            st.markdown("*Ask a question, paste your code for review, or say \"give me a hint\".*")
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input(
        f"Ask about {lesson['title']}...",
        key=f"chat_input_{lesson_id}",
    )

    if user_input:
        chat_history.append({"role": "user", "content": user_input})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                try:
                    for chunk in stream_chat_response(client, lesson, language, chat_history):
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                    response_placeholder.markdown(full_response)
                except anthropic.AuthenticationError:
                    full_response = "Invalid API key — check the 🔑 API Keys section in the sidebar."
                    response_placeholder.error(full_response)
                except Exception as e:
                    full_response = f"Error: {e}"
                    response_placeholder.error(full_response)

        chat_history.append({"role": "assistant", "content": full_response})
        st.session_state.chat[lesson_id] = chat_history

    # Quick action buttons
    st.divider()
    st.caption("Quick actions:")
    qa_cols = st.columns(3)
    with qa_cols[0]:
        if st.button("💡 Hint", key=f"hint_{lesson_id}", use_container_width=True):
            hint_msg = "Can you give me a hint for the challenge without giving away the answer?"
            chat_history.append({"role": "user", "content": hint_msg})
            st.session_state.chat[lesson_id] = chat_history
            st.rerun()
    with qa_cols[1]:
        if st.button("🔍 Explain code", key=f"explain_{lesson_id}", use_container_width=True):
            explain_msg = "Can you walk me through the code example line by line?"
            chat_history.append({"role": "user", "content": explain_msg})
            st.session_state.chat[lesson_id] = chat_history
            st.rerun()
    with qa_cols[2]:
        if st.button("🗑️ Clear chat", key=f"clear_{lesson_id}", use_container_width=True):
            st.session_state.chat[lesson_id] = []
            st.rerun()

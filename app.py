import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pitch Profiler Analytics",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_KEY_ENV = "PITCH_PROFILER_API_KEY"
BASE_URL = (
    "https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com"
    "/ords/admin/patreon"
)

# ── Data loading ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_career_pitchers(api_key: str) -> pd.DataFrame:
    import requests
    r = requests.get(f"{BASE_URL}/GET_CAREER_PITCHERS/{api_key}", timeout=30)
    r.raise_for_status()
    return pd.json_normalize(r.json().get("items", []))


@st.cache_data(ttl=3600)
def load_career_pitches(api_key: str) -> pd.DataFrame:
    import requests
    r = requests.get(f"{BASE_URL}/GET_CAREER_PITCHES/{api_key}", timeout=30)
    r.raise_for_status()
    return pd.json_normalize(r.json().get("items", []))


@st.cache_data(ttl=3600)
def load_season_pitchers(api_key: str, season: int) -> pd.DataFrame:
    import requests
    r = requests.get(f"{BASE_URL}/GET_SEASON_PITCHERS/{season}/{api_key}", timeout=30)
    r.raise_for_status()
    return pd.json_normalize(r.json().get("items", []))


# ── Helpers ─────────────────────────────────────────────────────────────────
DISPLAY_COLS = [
    "pitcher_name", "p_throws", "innings_pitched", "era", "fip", "whip",
    "stuff_plus", "location_plus", "pitching_plus",
    "whiff_rate", "strike_out_percentage", "walk_percentage",
    "barrel_percentage", "primary_fb_velo", "arm_angle",
]

METRIC_LABELS = {
    "era": "ERA", "fip": "FIP", "whip": "WHIP",
    "stuff_plus": "Stuff+", "location_plus": "Location+", "pitching_plus": "Pitching+",
    "mix_plus": "Mix+", "match_plus": "Match+", "max_plus": "Max+",
    "whiff_rate": "Whiff%", "strike_out_percentage": "K%", "walk_percentage": "BB%",
    "strike_out_minus_walk_percentage": "K-BB%",
    "barrel_percentage": "Barrel%", "hard_hit": "Hard Hit",
    "ground_ball_percentage": "GB%", "fly_ball_percentage": "FB%",
    "primary_fb_velo": "FB Velo", "primary_fb_spin_rate": "FB Spin",
    "arm_angle": "Arm Angle", "release_extension": "Extension",
    "innings_pitched": "IP", "games_started": "GS",
    "woba": "wOBA", "xwobacon": "xwOBACON",
    "run_value_per_100_pitches": "RV/100",
}

# metrics where lower = better (for coloring / ranking)
LOWER_IS_BETTER = {"era", "fip", "whip", "walk_percentage", "barrel_percentage", "woba", "xwobacon"}

RADAR_METRICS = [
    "stuff_plus", "location_plus", "pitching_plus",
    "whiff_rate", "strike_out_percentage", "walk_percentage",
    "barrel_percentage", "primary_fb_velo",
]

PITCH_TYPE_COLORS = {
    "4-Seam Fastball": "#e63946", "Sinker": "#f4a261",
    "Cutter": "#e9c46a", "Changeup": "#2a9d8f",
    "Splitter": "#264653", "Curveball": "#457b9d",
    "Slider": "#6a4c93", "Sweeper": "#9b2226",
    "Slurve": "#ae2012", "Knuckleball": "#94d2bd",
}


def pct_rank(series: pd.Series, lower_is_better: bool = False) -> pd.Series:
    """0–100 percentile rank; 100 = best."""
    r = series.rank(pct=True) * 100
    return (100 - r) if lower_is_better else r


def fmt(val, col: str) -> str:
    if pd.isna(val):
        return "—"
    if col in ("era", "fip", "whip", "woba", "xwobacon"):
        return f"{val:.3f}"
    if col in ("whiff_rate",):
        return f"{val:.1%}"
    if "percentage" in col:
        return f"{val * 100:.1f}%" if val <= 1 else f"{val:.1f}%"
    if col in ("primary_fb_velo",):
        return f"{val:.1f}"
    if col in ("arm_angle",):
        return f"{val:.0f}°"
    if col in ("stuff_plus", "location_plus", "pitching_plus", "mix_plus", "match_plus", "max_plus"):
        return f"{val:.1f}"
    return f"{val:.1f}"


def metric_card(label: str, value: str, delta: str = ""):
    st.metric(label=label, value=value, delta=delta if delta else None)


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚾ Pitch Profiler")
    st.divider()

    api_key = st.text_input(
        "API Key",
        value=os.environ.get(API_KEY_ENV, ""),
        type="password",
        help="Your Pitch Profiler API key",
    )

    if not api_key:
        st.warning("Enter your API key to load data.")
        st.stop()

    st.divider()
    st.subheader("Filters")
    min_ip = st.slider("Min Innings Pitched", 0, 200, 20, step=5)
    hand = st.multiselect("Handedness", ["R", "L"], default=["R", "L"])
    st.divider()
    season_options = [2020, 2021, 2022, 2023, 2024, 2025]
    selected_season = st.selectbox("Season data (Profile tab)", season_options, index=5)


# ── Load data ───────────────────────────────────────────────────────────────
with st.spinner("Loading pitcher data..."):
    try:
        df_raw = load_career_pitchers(api_key)
        df_pitches = load_career_pitches(api_key)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

df = df_raw.copy()
df = df[df["innings_pitched"] >= min_ip]
if hand:
    df = df[df["p_throws"].isin(hand)]

# Whiff rate: convert to 0–100 scale if it's 0–1
if df["whiff_rate"].max() <= 1:
    df["whiff_rate"] = df["whiff_rate"] * 100
    df_pitches["whiff_rate"] = df_pitches["whiff_rate"] * 100

# K% / BB% same
for col in ["strike_out_percentage", "walk_percentage", "barrel_percentage",
            "ground_ball_percentage", "fly_ball_percentage", "line_drive_percentage"]:
    if col in df.columns and df[col].max() <= 1:
        df[col] = df[col] * 100

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Leaderboard",
    "🎯 Pitcher Profile",
    "📈 Scatter Explorer",
    "💪 Arm Angle Lab",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Leaderboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        sort_metric = st.selectbox(
            "Sort by",
            options=[k for k in METRIC_LABELS if k in df.columns],
            format_func=lambda x: METRIC_LABELS.get(x, x),
            index=list(METRIC_LABELS.keys()).index("stuff_plus") if "stuff_plus" in METRIC_LABELS else 0,
        )
    with col2:
        top_n = st.slider("Show top N", 10, 100, 30, step=5)
    with col3:
        asc = sort_metric in LOWER_IS_BETTER
        st.markdown(f"**Sort order:** {'↑ Ascending (lower = better)' if asc else '↓ Descending (higher = better)'}")

    # League leader cards
    st.subheader("League Leaders")
    ldr_cols = st.columns(5)
    leader_metrics = ["stuff_plus", "whiff_rate", "era", "strike_out_percentage", "primary_fb_velo"]
    for i, m in enumerate(leader_metrics):
        if m not in df.columns:
            continue
        asc_m = m in LOWER_IS_BETTER
        leader_row = df.sort_values(m, ascending=asc_m).iloc[0]
        ldr_cols[i].metric(
            label=METRIC_LABELS.get(m, m),
            value=fmt(leader_row[m], m),
            delta=leader_row["pitcher_name"],
            delta_color="off",
        )

    st.divider()

    # Table
    display_cols = [c for c in DISPLAY_COLS if c in df.columns]
    df_sorted = df.sort_values(sort_metric, ascending=asc).head(top_n)[display_cols].copy()

    rename_map = {c: METRIC_LABELS.get(c, c) for c in display_cols}
    st.dataframe(
        df_sorted.rename(columns=rename_map).reset_index(drop=True),
        use_container_width=True,
        height=500,
    )

    # Bar chart of sort metric
    st.subheader(f"Top {top_n} — {METRIC_LABELS.get(sort_metric, sort_metric)}")
    fig_bar = px.bar(
        df_sorted.iloc[::-1] if not asc else df_sorted,
        x=sort_metric,
        y="pitcher_name",
        orientation="h",
        color=sort_metric,
        color_continuous_scale="RdYlGn_r" if asc else "RdYlGn",
        labels={sort_metric: METRIC_LABELS.get(sort_metric, sort_metric), "pitcher_name": ""},
        height=max(400, top_n * 18),
    )
    fig_bar.update_layout(
        coloraxis_showscale=False,
        yaxis={"categoryorder": "total ascending" if not asc else "total descending"},
        margin=dict(l=0, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PITCHER PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Pitcher Profile")

    all_pitchers = sorted(df_raw["pitcher_name"].unique())
    selected_pitcher = st.selectbox("Select pitcher", all_pitchers)

    pitcher_row = df_raw[df_raw["pitcher_name"] == selected_pitcher].iloc[0]
    pitcher_pitches = df_pitches[df_pitches["pitcher_name"] == selected_pitcher].copy()

    hand_label = "RHP" if pitcher_row["p_throws"] == "R" else "LHP"
    st.subheader(f"{selected_pitcher} · {hand_label} · {pitcher_row['innings_pitched']:.1f} IP (Career)")

    # Stat cards
    card_metrics = [
        ("era", "ERA"), ("fip", "FIP"), ("whip", "WHIP"),
        ("stuff_plus", "Stuff+"), ("location_plus", "Location+"), ("pitching_plus", "Pitching+"),
        ("whiff_rate", "Whiff%"), ("strike_out_percentage", "K%"), ("walk_percentage", "BB%"),
        ("primary_fb_velo", "FB Velo"), ("primary_fb_spin_rate", "FB Spin"), ("arm_angle", "Arm Angle"),
    ]
    rows = [card_metrics[:6], card_metrics[6:]]
    for row_metrics in rows:
        cols = st.columns(6)
        for i, (col_name, label) in enumerate(row_metrics):
            if col_name not in pitcher_row.index:
                continue
            val = pitcher_row[col_name]
            # Compute percentile vs filtered df
            if col_name in df.columns and df[col_name].notna().sum() > 5:
                pct = pct_rank(df[col_name], lower_is_better=(col_name in LOWER_IS_BETTER))
                pitcher_pct = pct[df["pitcher_name"] == selected_pitcher]
                delta_str = f"P{pitcher_pct.values[0]:.0f}" if len(pitcher_pct) else ""
            else:
                delta_str = ""
            cols[i].metric(label=label, value=fmt(val, col_name), delta=delta_str, delta_color="off")

    st.divider()

    col_left, col_right = st.columns([1, 1])

    # Radar chart
    with col_left:
        st.subheader("Percentile Radar")
        radar_cols = [m for m in RADAR_METRICS if m in df.columns]
        if radar_cols and selected_pitcher in df["pitcher_name"].values:
            pct_vals = []
            for m in radar_cols:
                pct_series = pct_rank(df[m], lower_is_better=(m in LOWER_IS_BETTER))
                row_match = df[df["pitcher_name"] == selected_pitcher]
                pct_vals.append(pct_series[row_match.index[0]] if len(row_match) else 50)

            fig_radar = go.Figure(go.Scatterpolar(
                r=pct_vals + [pct_vals[0]],
                theta=[METRIC_LABELS.get(m, m) for m in radar_cols] + [METRIC_LABELS.get(radar_cols[0], radar_cols[0])],
                fill="toself",
                fillcolor="rgba(99,110,250,0.3)",
                line=dict(color="#636efa", width=2),
                name=selected_pitcher,
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=380,
                margin=dict(l=40, r=40, t=40, b=40),
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("Pitcher not in current IP filter — radar unavailable. Lower Min IP filter.")

    # Pitch arsenal
    with col_right:
        st.subheader("Pitch Arsenal")
        if not pitcher_pitches.empty:
            arsenal_cols = [c for c in [
                "pitch_type", "thrown", "percentage_thrown",
                "velocity", "spin_rate", "whiff_rate",
                "stuff_plus", "location_plus", "pitching_plus",
                "run_value_per_100_pitches",
            ] if c in pitcher_pitches.columns]

            arsenal_df = pitcher_pitches[arsenal_cols].copy()
            if "whiff_rate" in arsenal_df.columns and arsenal_df["whiff_rate"].max() <= 1:
                arsenal_df["whiff_rate"] = arsenal_df["whiff_rate"] * 100

            arsenal_df = arsenal_df.sort_values("thrown", ascending=False) if "thrown" in arsenal_df.columns else arsenal_df
            st.dataframe(
                arsenal_df.rename(columns={c: METRIC_LABELS.get(c, c) for c in arsenal_cols}).reset_index(drop=True),
                use_container_width=True,
                height=340,
            )

            # Usage pie
            if "pitch_type" in pitcher_pitches.columns and "thrown" in pitcher_pitches.columns:
                fig_pie = px.pie(
                    pitcher_pitches,
                    names="pitch_type",
                    values="thrown",
                    color="pitch_type",
                    color_discrete_map=PITCH_TYPE_COLORS,
                    hole=0.4,
                    height=200,
                )
                fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No pitch-level data found for this pitcher.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SCATTER EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Scatter Explorer")

    numeric_cols = [c for c in df.select_dtypes(include="number").columns if c != "pitcher_id"]
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox(
            "X axis", numeric_cols,
            format_func=lambda c: METRIC_LABELS.get(c, c),
            index=numeric_cols.index("stuff_plus") if "stuff_plus" in numeric_cols else 0,
        )
    with col2:
        y_col = st.selectbox(
            "Y axis", numeric_cols,
            format_func=lambda c: METRIC_LABELS.get(c, c),
            index=numeric_cols.index("whiff_rate") if "whiff_rate" in numeric_cols else 1,
        )
    with col3:
        color_col = st.selectbox("Color by", ["p_throws", "stuff_plus", "era", "arm_angle"], index=0)

    # Filter out extreme outliers (ERA > 20)
    plot_df = df[df["era"] < 20].copy() if "era" in df.columns else df.copy()

    # Highlight pitcher
    highlight = st.selectbox("Highlight pitcher (optional)", ["None"] + sorted(plot_df["pitcher_name"].unique()))

    fig_scatter = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_col,
        hover_name="pitcher_name",
        hover_data={
            "p_throws": True,
            "innings_pitched": ":.1f",
            x_col: ":.2f",
            y_col: ":.2f",
        },
        labels={
            x_col: METRIC_LABELS.get(x_col, x_col),
            y_col: METRIC_LABELS.get(y_col, y_col),
        },
        opacity=0.65,
        height=580,
        color_continuous_scale="RdYlGn" if color_col not in ("p_throws",) else None,
    )

    # League average lines
    avg_x = plot_df[x_col].mean()
    avg_y = plot_df[y_col].mean()
    fig_scatter.add_vline(x=avg_x, line_dash="dash", line_color="gray", opacity=0.5)
    fig_scatter.add_hline(y=avg_y, line_dash="dash", line_color="gray", opacity=0.5)

    # Highlight selected pitcher
    if highlight != "None" and highlight in plot_df["pitcher_name"].values:
        h_row = plot_df[plot_df["pitcher_name"] == highlight]
        fig_scatter.add_trace(go.Scatter(
            x=h_row[x_col], y=h_row[y_col],
            mode="markers+text",
            text=[highlight],
            textposition="top center",
            marker=dict(size=14, color="yellow", line=dict(color="black", width=2)),
            showlegend=False,
        ))

    fig_scatter.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Correlation stat
    corr = plot_df[[x_col, y_col]].dropna().corr().iloc[0, 1]
    st.caption(f"Pearson correlation: **{corr:.3f}**  ·  n={len(plot_df.dropna(subset=[x_col, y_col]))}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ARM ANGLE LAB
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("Arm Angle Lab")
    st.caption("Arm angle = degrees from horizontal. Overhand ≈ 45–80°. Sidearm ≈ 0–20°. Submarine < 0°.")

    if "arm_angle" not in df.columns:
        st.error("arm_angle column not found in data.")
    else:
        aa_df = df.dropna(subset=["arm_angle"])

        # Distribution
        col1, col2 = st.columns(2)
        with col1:
            fig_hist = px.histogram(
                aa_df, x="arm_angle", color="p_throws",
                barmode="overlay", opacity=0.7, nbins=40,
                labels={"arm_angle": "Arm Angle (°)", "p_throws": "Hand"},
                title="Arm Angle Distribution by Handedness",
                height=350,
                color_discrete_map={"R": "#636efa", "L": "#ef553b"},
            )
            fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            aa_metric = st.selectbox(
                "Metric vs Arm Angle",
                [c for c in ["whiff_rate", "stuff_plus", "primary_fb_velo", "ground_ball_percentage", "era"] if c in aa_df.columns],
                format_func=lambda c: METRIC_LABELS.get(c, c),
            )
            fig_aa = px.scatter(
                aa_df[aa_df["era"] < 20] if "era" in aa_df.columns else aa_df,
                x="arm_angle", y=aa_metric,
                color="p_throws",
                hover_name="pitcher_name",
                trendline="ols",
                labels={"arm_angle": "Arm Angle (°)", aa_metric: METRIC_LABELS.get(aa_metric, aa_metric), "p_throws": "Hand"},
                title=f"Arm Angle vs {METRIC_LABELS.get(aa_metric, aa_metric)}",
                height=350,
                color_discrete_map={"R": "#636efa", "L": "#ef553b"},
                opacity=0.65,
            )
            fig_aa.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_aa, use_container_width=True)

        st.divider()

        # Bucket analysis
        st.subheader("Performance by Arm Slot")
        bins = [-180, -1, 15, 30, 45, 60, 180]
        labels_bins = ["Submarine (<0°)", "Sidearm (0–15°)", "Low 3/4 (15–30°)",
                       "3/4 (30–45°)", "High 3/4 (45–60°)", "Overhand (>60°)"]
        aa_df = aa_df.copy()
        aa_df["arm_slot"] = pd.cut(aa_df["arm_angle"], bins=bins, labels=labels_bins)

        slot_metrics = ["whiff_rate", "stuff_plus", "era", "strike_out_percentage", "primary_fb_velo"]
        slot_metrics = [m for m in slot_metrics if m in aa_df.columns]

        slot_summary = (
            aa_df.groupby("arm_slot", observed=True)[slot_metrics]
            .mean()
            .round(2)
            .reset_index()
        )
        slot_summary["Count"] = aa_df.groupby("arm_slot", observed=True).size().values

        st.dataframe(
            slot_summary.rename(columns={**{c: METRIC_LABELS.get(c, c) for c in slot_metrics}, "arm_slot": "Arm Slot"}),
            use_container_width=True,
        )

        # Slot comparison chart
        slot_bar_metric = st.selectbox(
            "Compare slots by",
            slot_metrics,
            format_func=lambda c: METRIC_LABELS.get(c, c),
            key="slot_bar_metric",
        )
        fig_slot = px.bar(
            slot_summary,
            x="arm_slot", y=slot_bar_metric,
            color=slot_bar_metric,
            color_continuous_scale="RdYlGn_r" if slot_bar_metric in LOWER_IS_BETTER else "RdYlGn",
            labels={"arm_slot": "Arm Slot", slot_bar_metric: METRIC_LABELS.get(slot_bar_metric, slot_bar_metric)},
            text_auto=".2f",
            height=360,
        )
        fig_slot.update_layout(
            coloraxis_showscale=False,
            xaxis_title="",
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_slot, use_container_width=True)

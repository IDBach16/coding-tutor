"""
Pitch Profiler API client with local caching.
Set PITCH_PROFILER_API_KEY env variable before use.

Usage:
    from baseball_data import career_pitchers, season_pitches
    df = career_pitchers()
    df_2024 = season_pitches(2024)
"""

import os
from pathlib import Path
import requests
import pandas as pd

BASE_URL = (
    "https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com"
    "/ords/admin/patreon"
)
CACHE_DIR = Path.home() / ".coding_tutor_cache" / "baseball"


def _api_key() -> str:
    key = os.environ.get("PITCH_PROFILER_API_KEY")
    if not key:
        raise RuntimeError(
            "PITCH_PROFILER_API_KEY environment variable is not set.\n"
            "Windows: set PITCH_PROFILER_API_KEY=your-key-here"
        )
    return key


def _fetch(endpoint: str, force_refresh: bool = False) -> pd.DataFrame:
    cache_file = CACHE_DIR / f"{endpoint.replace('/', '__')}.csv"

    if cache_file.exists() and not force_refresh:
        return pd.read_csv(cache_file)

    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    items = resp.json().get("items", [])
    df = pd.json_normalize(items)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_file, index=False)
    return df


# ── Public API ─────────────────────────────────────────────────────────────

def career_pitchers(force_refresh: bool = False) -> pd.DataFrame:
    """Aggregate pitcher statistics since 2020."""
    return _fetch(f"GET_CAREER_PITCHERS/{_api_key()}", force_refresh)


def career_pitches(force_refresh: bool = False) -> pd.DataFrame:
    """Career statistics broken down by pitch type."""
    return _fetch(f"GET_CAREER_PITCHES/{_api_key()}", force_refresh)


def season_pitchers(season: int, force_refresh: bool = False) -> pd.DataFrame:
    """Single-season pitcher statistics."""
    return _fetch(f"GET_SEASON_PITCHERS/{season}/{_api_key()}", force_refresh)


def team_season_pitchers(season: int, force_refresh: bool = False) -> pd.DataFrame:
    """Season statistics filtered by team."""
    return _fetch(f"GET_TEAM_SEASON_PITCHERS/{season}/{_api_key()}", force_refresh)


def season_pitches(season: int, force_refresh: bool = False) -> pd.DataFrame:
    """Season pitch-type breakdowns."""
    return _fetch(f"GET_SEASON_PITCHES/{season}/{_api_key()}", force_refresh)


def team_season_pitches(season: int, force_refresh: bool = False) -> pd.DataFrame:
    """Team-level season pitch-type data."""
    return _fetch(f"GET_TEAM_SEASON_PITCHES/{season}/{_api_key()}", force_refresh)


def clear_cache() -> None:
    """Delete all cached CSV files."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.csv"):
            f.unlink()
        print(f"Cache cleared: {CACHE_DIR}")


if __name__ == "__main__":
    print("Testing Pitch Profiler connection...")
    df = career_pitchers()
    print(f"Career pitchers: {len(df)} rows, {len(df.columns)} columns")
    print(df.head(3).to_string())

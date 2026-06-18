# Python Coding Tutor — Powered by Claude

A personal coding tutor that runs in your terminal, powered by the Claude API.

**20 lessons across two phases:**
- Phase 1: Python Efficiency — comprehensions, builtins, pathlib, collections, itertools, profiling, and more
- Phase 2: Data & Analytics — real baseball pitching data (Pitch Profiler API), pandas, numpy, matplotlib/plotly, REST APIs, XGBoost

Phase 2 uses real pitcher statistics (ERA, whiff rate, stuff+, arm angle, spin rate, and 100+ other metrics)
from the Pitch Profiler API instead of synthetic data.

## Setup

1. **Clone the repo**
   ```
   git clone https://github.com/idbach16/coding-tutor.git
   cd coding-tutor
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```
   # Windows — run both in your terminal before starting the tutor
   set ANTHROPIC_API_KEY=your-anthropic-key-here
   set PITCH_PROFILER_API_KEY=your-pitch-profiler-key-here
   ```

4. **Run the tutor**
   ```
   python tutor.py
   ```

## How it works

- Progress is saved locally in `~/.coding_tutor_progress.json` — persists between sessions
- Pitch Profiler API responses are cached in `~/.coding_tutor_cache/baseball/` — no repeated API calls
- Each lesson: concept explanation → coding challenge → Claude reviews your code
- Type `SKIP` to skip a challenge, `DONE` on a blank line to submit your code
- You can retry any lesson or jump to a specific one from the menu

## Test your data connection

```
python baseball_data.py
```

This fetches career pitcher data and prints the first few rows to confirm the API is working.

## Clearing the data cache

```python
from baseball_data import clear_cache
clear_cache()
```

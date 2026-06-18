# Python Coding Tutor — Powered by Claude

A personal coding tutor that runs in your terminal, powered by the Claude API.

**20 lessons across two phases:**
- Phase 1: Python Efficiency (comprehensions, builtins, pathlib, collections, itertools, profiling, and more)
- Phase 2: Data & Analytics (pandas, numpy, matplotlib/plotly, REST APIs, XGBoost)

Exercises are tailored to real-world work: Oracle Fusion BPA data, procurement APIs, and analytics.

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

3. **Set your Anthropic API key**
   ```
   # Windows
   set ANTHROPIC_API_KEY=your-key-here

   # Mac/Linux
   export ANTHROPIC_API_KEY=your-key-here
   ```

4. **Run the tutor**
   ```
   python tutor.py
   ```

## How it works

- Progress is saved locally in `~/.coding_tutor_progress.json` — it persists between sessions
- Each lesson: concept explanation → coding challenge → Claude reviews your code
- Type `SKIP` to skip a challenge, `DONE` on a blank line to submit your code
- You can retry any lesson or jump to a specific one from the menu

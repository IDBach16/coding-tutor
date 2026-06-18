#!/usr/bin/env python3
"""
Personal Python Coding Tutor — Powered by Claude
Covers: Python efficiency fundamentals + Data & analytics
Progress is stored locally in ~/.coding_tutor_progress.json
"""

import json
import os
import sys
from pathlib import Path
import anthropic

PROGRESS_FILE = Path.home() / ".coding_tutor_progress.json"
MODEL = "claude-opus-4-8"

CURRICULUM = [
    # ── Phase 1: Python Efficiency ─────────────────────────────────────────
    {
        "id": "comprehensions",
        "phase": "Phase 1: Python Efficiency",
        "title": "List, Dict & Set Comprehensions",
        "concept": (
            "Comprehensions replace verbose for-loops with a single expressive line. "
            "They're faster (compiled differently by CPython), more readable, and idiomatic Python. "
            "List: [expr for x in iterable if condition]. "
            "Dict: {k: v for k, v in items}. "
            "Set: {expr for x in iterable}. "
            "Generator: (expr for x in iterable) — lazy, no memory cost until iterated."
        ),
        "challenge": (
            "You have a list of BPA line items as dicts: "
            "[{'item': 'BOLT-10', 'price': 1.50, 'qty': 1000}, {'item': 'NUT-5', 'price': 0.25, 'qty': 500}, ...]. "
            "Write THREE things using comprehensions: "
            "(1) a list of item names where price > 1.00, "
            "(2) a dict mapping item name to total_value (price * qty), "
            "(3) a set of unique price tiers rounded to the nearest dollar."
        ),
    },
    {
        "id": "builtins",
        "phase": "Phase 1: Python Efficiency",
        "title": "Power Builtins: enumerate, zip, map, any, all",
        "concept": (
            "Python's builtins eliminate manual indexing and reduce bugs. "
            "enumerate(iterable, start=0) gives (index, value) pairs — never write 'i += 1' again. "
            "zip(a, b) pairs two iterables — stops at the shortest. "
            "zip(*rows) transposes a matrix. "
            "map(func, iterable) applies a function lazily. "
            "any()/all() short-circuit — faster than a manual loop for boolean checks."
        ),
        "challenge": (
            "Given two lists — agreement_numbers = ['BPA-001', 'BPA-002', 'BPA-003'] "
            "and suppliers = ['Acme Corp', 'Beta Supply', 'Gamma Ltd'] — "
            "use zip to build a list of formatted strings like 'BPA-001: Acme Corp'. "
            "Then use enumerate to print each with a 1-based index. "
            "Finally, given a list of statuses = ['Active', 'Active', 'Expired', 'Active'], "
            "use any() and all() to check if any are expired and if all are active."
        ),
    },
    {
        "id": "fstrings",
        "phase": "Phase 1: Python Efficiency",
        "title": "f-strings, String Methods & Formatting",
        "concept": (
            "f-strings (Python 3.6+) are the fastest string formatting method. "
            "They support expressions: f'{price:.2f}', f'{name!r}', f'{value:,}'. "
            "f'{x=}' (Python 3.8+) is a debug shortcut that prints 'x=value'. "
            "Key string methods: .strip(), .split(), .join(), .replace(), .startswith(), .endswith(). "
            ".join() is much faster than string concatenation in a loop."
        ),
        "challenge": (
            "Given: supplier = '  acme corp  ', price = 1234567.89, qty = 1000, item = 'BOLT-10'. "
            "Write an f-string that produces a clean report line like: "
            "'Item: BOLT-10 | Supplier: Acme Corp | Price: $1,234,567.89 | Qty: 1,000'. "
            "Then write a function that takes a list of such strings and joins them with newlines "
            "and a separator line of 60 dashes between each entry."
        ),
    },
    {
        "id": "pathlib",
        "phase": "Phase 1: Python Efficiency",
        "title": "Pathlib for File Operations",
        "concept": (
            "pathlib.Path replaces os.path with an object-oriented interface. "
            "Path('/some/dir') / 'file.csv' builds paths safely across OS. "
            "path.exists(), path.is_file(), path.stem, path.suffix, path.parent. "
            "path.read_text(), path.write_text(), path.glob('*.csv'). "
            "Path.home() gives the home directory. Path.cwd() gives working directory. "
            "It handles Windows backslashes vs Unix forward slashes automatically."
        ),
        "challenge": (
            "Write a function called find_data_files(root_dir, extension='.csv') "
            "that takes a directory path (as a string or Path), "
            "finds all files with the given extension recursively, "
            "and returns a list of dicts with keys: 'name' (stem only), 'path' (full path), "
            "'size_kb' (file size in KB rounded to 1 decimal). "
            "Use pathlib throughout — no os.path allowed."
        ),
    },
    {
        "id": "context_managers",
        "phase": "Phase 1: Python Efficiency",
        "title": "Context Managers & the with Statement",
        "concept": (
            "Context managers handle setup/teardown automatically via __enter__ and __exit__. "
            "File handles, database connections, locks — always use 'with'. "
            "contextlib.contextmanager lets you write one as a generator function. "
            "You can open multiple resources in one with: 'with open(a) as f1, open(b) as f2'. "
            "contextlib.suppress(Exception) silences specific exceptions cleanly."
        ),
        "challenge": (
            "Write a context manager called timer() using contextlib.contextmanager "
            "that measures how long a block of code takes and prints "
            "'Elapsed: X.XXXs' when the block exits. "
            "Then write a second context manager called temp_csv(data: list[dict]) "
            "that writes the data to a temporary CSV file on enter, "
            "yields the file path, and deletes the file on exit. "
            "Use it to wrap a block that reads the CSV back and prints row count."
        ),
    },
    {
        "id": "collections",
        "phase": "Phase 1: Python Efficiency",
        "title": "The collections Module",
        "concept": (
            "collections has specialized containers that beat plain dicts/lists for specific use cases. "
            "Counter(iterable) counts occurrences — .most_common(n) gives top N. "
            "defaultdict(list) auto-creates missing keys — eliminates 'if key not in d' checks. "
            "deque(maxlen=N) is a fixed-size queue — O(1) appends/pops from both ends. "
            "namedtuple creates lightweight immutable structs with named fields. "
            "OrderedDict remembers insertion order (less needed in Python 3.7+ but useful for .move_to_end())."
        ),
        "challenge": (
            "Given a flat list of BPA transactions: "
            "[{'supplier': 'Acme', 'amount': 500}, {'supplier': 'Beta', 'amount': 200}, "
            "{'supplier': 'Acme', 'amount': 750}, {'supplier': 'Gamma', 'amount': 300}, ...]. "
            "Use Counter to find the top 3 most active suppliers by transaction count. "
            "Use defaultdict to group transactions by supplier into a dict of lists. "
            "Then define a namedtuple BPASummary with fields: supplier, total_amount, tx_count, avg_amount. "
            "Build a list of BPASummary for each supplier."
        ),
    },
    {
        "id": "functions",
        "phase": "Phase 1: Python Efficiency",
        "title": "Writing Better Functions: Type Hints, Defaults & *args/**kwargs",
        "concept": (
            "Good functions are small, named clearly, and have type hints. "
            "Type hints don't enforce types but document intent and enable editor autocomplete. "
            "Default arguments are evaluated ONCE at definition — never use mutable defaults like []or {}. "
            "Use None as default, then assign inside the function. "
            "*args collects positional extras as a tuple; **kwargs collects keyword extras as a dict. "
            "The -> return type annotation documents what the function returns."
        ),
        "challenge": (
            "Write a function build_query_filter(field: str, value: str, operator: str = 'eq') -> str "
            "that builds Oracle REST API query strings. "
            "Operators: 'eq' → \"field='value'\", 'like' → \"field LIKE '%value%'\", "
            "'gt'/'lt' → \"field > value\" / \"field < value\". "
            "Then write build_multi_filter(*filters: str, join: str = ';') -> str "
            "that combines multiple filter strings with the given separator. "
            "Include type hints throughout and handle an unknown operator by raising ValueError."
        ),
    },
    {
        "id": "itertools",
        "phase": "Phase 1: Python Efficiency",
        "title": "itertools: Lazy Iteration at Scale",
        "concept": (
            "itertools provides memory-efficient iterators for common patterns. "
            "itertools.chain(*iterables) flattens nested iterables without building a list. "
            "itertools.islice(iterable, n) takes first N items lazily. "
            "itertools.groupby(iterable, key) groups consecutive items — sort first! "
            "itertools.product(a, b) gives Cartesian product (all combinations). "
            "itertools.batched(iterable, n) (Python 3.12) splits into chunks of n."
        ),
        "challenge": (
            "You have multiple lists of BPA records from different Oracle business units: "
            "bu1_bpas = [...], bu2_bpas = [...], bu3_bpas = [...]. "
            "Use itertools.chain to iterate all of them without building a combined list. "
            "Use itertools.islice to take only the first 10. "
            "Sort the combined records by supplier name, then use itertools.groupby "
            "to group them and print a count of BPAs per supplier. "
            "Finally, use itertools.product to generate all (supplier, status) combinations "
            "from two separate lists."
        ),
    },
    {
        "id": "error_handling",
        "phase": "Phase 1: Python Efficiency",
        "title": "Error Handling Done Right",
        "concept": (
            "Only catch exceptions you can actually handle. Never use bare 'except:' — it catches SystemExit and KeyboardInterrupt. "
            "except Exception as e: is the minimum. "
            "Be specific: except (ValueError, KeyError). "
            "Use 'else' on try blocks for code that should only run if no exception occurred. "
            "Use 'finally' for cleanup that must always happen. "
            "Custom exceptions: class BPANotFoundError(ValueError): pass — gives callers something specific to catch. "
            "logging.exception() inside an except block logs the full traceback."
        ),
        "challenge": (
            "Write a function fetch_bpa(agreement_number: str) -> dict "
            "that simulates calling an Oracle REST API. "
            "If agreement_number starts with 'BPA-', return {'number': agreement_number, 'status': 'Active'}. "
            "If it starts with 'EXP-', raise a custom BPAExpiredError. "
            "If it's empty or None, raise ValueError. "
            "Otherwise raise BPANotFoundError. "
            "Then write a safe_fetch(number) function that calls fetch_bpa, "
            "returns None on BPANotFoundError, re-raises BPAExpiredError, "
            "and logs a warning (using the logging module) for any other exception."
        ),
    },
    {
        "id": "profiling",
        "phase": "Phase 1: Python Efficiency",
        "title": "Profiling & Measuring Performance",
        "concept": (
            "Never optimize without measuring. timeit.timeit() benchmarks small snippets. "
            "time.perf_counter() is the highest-resolution timer for wall-clock measurement. "
            "cProfile.run('your_function()') shows where time is spent — sort by 'cumulative'. "
            "Memory: tracemalloc tracks allocations. "
            "Key insight: a list comprehension is ~35% faster than an equivalent for-loop. "
            "String join is O(n) vs concatenation which is O(n²). "
            "In a dict, key lookup is O(1); list search is O(n)."
        ),
        "challenge": (
            "Write two versions of a function that counts word frequency in a large string: "
            "version 1 uses a plain dict with manual 'if key in dict' checks, "
            "version 2 uses collections.Counter. "
            "Use timeit.timeit() to benchmark both on a string of 10,000 words "
            "(you can generate it with ' '.join(['word'] * 10000)). "
            "Print the results as 'Method 1: X.XXXs | Method 2: X.XXXs | Speedup: Xx'. "
            "Then use cProfile to profile the slower version and show the top 5 calls."
        ),
    },
    # ── Phase 2: Data & Analytics ──────────────────────────────────────────
    # All Phase 2 challenges use real baseball pitching data from the Pitch Profiler API.
    # Import helpers: from baseball_data import career_pitchers, season_pitchers, career_pitches, season_pitches
    # Set env var: PITCH_PROFILER_API_KEY before running any challenge below.
    {
        "id": "pandas_basics",
        "phase": "Phase 2: Data & Analytics",
        "title": "pandas Fundamentals: Reading & Inspecting Data",
        "concept": (
            "pandas is built on numpy and provides labeled, columnar data structures. "
            "pd.read_csv(), pd.read_json(), pd.read_excel() load data. "
            "df.head(), df.tail(), df.info(), df.describe() are your first inspections. "
            "df.dtypes shows column types — check this early since int/float/object affects operations. "
            "df.shape gives (rows, cols). df.columns gives column names. "
            "df.isnull().sum() shows missing counts per column. "
            "df.value_counts() counts unique values in a Series."
        ),
        "challenge": (
            "Load real pitcher data: from baseball_data import career_pitchers; df = career_pitchers(). "
            "This returns 100+ columns of pitching metrics (ERA, whiff_pct, stuff_rv, arm_angle, etc.). "
            "Build a function inspect_dataframe(df) -> dict with keys: "
            "'shape', 'numeric_cols' (count), 'string_cols' (count), "
            "'null_summary' (only cols with >5% nulls, showing pct), "
            "'top_numeric_ranges' (min/max for era, whiff_pct, stuff_rv, k_pct). "
            "Then print the 5 pitchers with the highest stuff_rv and the 5 with the lowest ERA "
            "(min 50 IP — filter first). Show only: pitcher_name, team, era, whiff_pct, stuff_rv."
        ),
    },
    {
        "id": "pandas_filtering",
        "phase": "Phase 2: Data & Analytics",
        "title": "pandas: Filtering, Selecting & Transforming",
        "concept": (
            "Boolean indexing: df[df['col'] > value] returns matching rows. "
            "Chain conditions with & (and) and | (or) — always wrap in parentheses: (cond1) & (cond2). "
            "df.loc[rows, cols] selects by label; df.iloc[rows, cols] selects by position. "
            "df['new_col'] = expression adds a column; avoid chained assignment (df[mask]['col'] = x). "
            "df.query('col > 100 and status == \"Active\"') is readable for complex filters. "
            ".str accessor: df['name'].str.upper(), .str.contains(), .str.startswith(). "
            "pd.to_datetime() converts string dates; then .dt.year, .dt.month, etc."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers; df = career_pitchers(). "
            "Do all four without loops: "
            "(1) Filter to qualified starters: ip >= 162 and starts >= 25. "
            "(2) From that group, find pitchers whose team name contains 'Sox' (case-insensitive). "
            "(3) Add a column 'stuff_tier': 'Elite' if stuff_rv > 5, 'Above Avg' if > 0, else 'Below Avg' "
            "— use np.select(), not apply(). "
            "(4) Add 'k_bb_ratio' = k_pct / bb_pct (handle division by zero with np.where). "
            "Print shape after each filter and show the top 10 Elite starters sorted by k_bb_ratio."
        ),
    },
    {
        "id": "pandas_groupby",
        "phase": "Phase 2: Data & Analytics",
        "title": "pandas: groupby, aggregations & pivot tables",
        "concept": (
            "groupby is the most powerful pandas operation for summarizing data. "
            "df.groupby('col')['value'].agg(['sum', 'mean', 'count']) computes multiple aggregates. "
            "Named aggregations: df.groupby('col').agg(total=('amount', 'sum'), avg=('amount', 'mean')). "
            ".transform() adds group-level stats back to the original df (same index). "
            "pd.pivot_table(df, values='amount', index='supplier', columns='status', aggfunc='sum') "
            "creates a cross-tab. "
            "reset_index() brings groupby keys back as columns."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers, career_pitches; "
            "pitchers = career_pitchers(); pitches = career_pitches(). "
            "(1) Group pitchers by team: compute mean ERA, mean whiff_pct, mean stuff_rv, pitcher count. "
            "Sort by mean stuff_rv descending. Which team has the best stuff? "
            "(2) Use transform to add 'era_vs_team_avg' = each pitcher's ERA minus their team's mean ERA. "
            "Show the 5 pitchers furthest below their team average (best relative performance). "
            "(3) From the pitches DataFrame, build a pivot table: pitch_type as rows, team as columns, "
            "values = mean whiff_pct. Fill NaN with 0. Which pitch type generates the most whiffs league-wide?"
        ),
    },
    {
        "id": "pandas_merge",
        "phase": "Phase 2: Data & Analytics",
        "title": "pandas: Merging, Joining & Concatenating",
        "concept": (
            "pd.merge(left, right, on='key', how='inner') joins DataFrames like SQL. "
            "how options: 'inner', 'left', 'right', 'outer'. "
            "Use suffixes=('_x', '_y') when both frames have the same column name. "
            "df.merge(df2, left_on='a', right_on='b') when key names differ. "
            "pd.concat([df1, df2], ignore_index=True) stacks frames vertically. "
            "df.join(other, on='key') is a shortcut when one frame's index is the key. "
            "After merging, always check shape — unexpected duplicates mean many-to-many."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers, career_pitches, season_pitchers; "
            "career = career_pitchers(); pitches = career_pitches(); s2024 = season_pitchers(2024). "
            "(1) Inner-join career pitchers with career_pitches on pitcher_name (or pitcher_id if available). "
            "Print shape before/after — did you get duplicates? Why or why not? "
            "(2) Left-join career onto s2024 to find pitchers who have career data but no 2024 season "
            "(retired or injured). How many? "
            "(3) Concat s2024 with season_pitchers(2023), add a 'season' column to each before concat. "
            "Then find pitchers who appear in both seasons and compute their ERA change year-over-year."
        ),
    },
    {
        "id": "numpy_vectors",
        "phase": "Phase 2: Data & Analytics",
        "title": "numpy: Vectorized Operations",
        "concept": (
            "numpy operations run in C — orders of magnitude faster than Python loops. "
            "np.array() creates arrays; operations apply element-wise automatically. "
            "Broadcasting: operations between arrays of compatible shapes work without loops. "
            "Useful: np.where(condition, a, b) — vectorized if/else. "
            "np.select([cond1, cond2], [val1, val2], default) — multi-branch if/else. "
            "np.clip(arr, min, max) caps values. "
            "np.percentile(), np.mean(), np.std() for statistics. "
            "Avoid Python loops over numpy arrays — that negates all the speed."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers; df = career_pitchers(). "
            "Extract these as numpy arrays: era = df['era'].values, whiff = df['whiff_pct'].values, "
            "stuff = df['stuff_rv'].values (drop NaNs first with dropna on those cols). "
            "Without any Python loops: "
            "(1) Compute mean, std, and 10/50/90th percentiles for all three metrics. "
            "(2) Build a composite 'ace_score' = (stuff / stuff.std()) + (whiff / whiff.std()) - (era / era.std()). "
            "(3) Classify pitchers: np.select — 'Ace' if ace_score > 2, 'Solid' if > 0, else 'Replacement'. "
            "(4) Count pitchers in each tier and print results. Time the whole thing."
        ),
    },
    {
        "id": "matplotlib_plotly",
        "phase": "Phase 2: Data & Analytics",
        "title": "Visualization: matplotlib & plotly",
        "concept": (
            "matplotlib is the foundation — fine control but verbose. "
            "fig, ax = plt.subplots() is the OO API — always use it, not plt.plot() directly. "
            "ax.set_title(), ax.set_xlabel(), ax.legend(), ax.tick_params() for polish. "
            "plotly (px and go) builds interactive charts in far less code. "
            "px.bar(), px.line(), px.scatter() handle 80% of use cases. "
            "fig.update_layout() and fig.update_traces() fine-tune. "
            "fig.write_html('chart.html') saves interactive charts. "
            "For DataFrames, plotly express accepts df directly: px.bar(df, x='col', y='val', color='cat')."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers, career_pitches; "
            "df = career_pitchers(); pitches = career_pitches(). "
            "Build two charts: "
            "(1) matplotlib: scatter plot of stuff_rv (x) vs whiff_pct (y) for qualified starters (ip >= 100). "
            "Color points by stuff_tier (Elite/Above Avg/Below Avg). Add pitcher name labels for top 10 by stuff_rv. "
            "Clean axes, title 'Stuff+ vs Whiff Rate — Career', legend. "
            "(2) plotly: bar chart of mean whiff_pct by pitch_type from the pitches DataFrame, "
            "sorted descending, colored by pitch_type, hover shows pitch count and mean spin_rate. "
            "Save as 'pitch_profiler_analysis.html'."
        ),
    },
    {
        "id": "api_requests",
        "phase": "Phase 2: Data & Analytics",
        "title": "Working with REST APIs & JSON in Python",
        "concept": (
            "requests is the standard HTTP library. Session reuse is important for repeated calls. "
            "session = requests.Session(); session.headers.update({'Authorization': ...}). "
            "response.raise_for_status() raises on 4xx/5xx — always call it. "
            "response.json() parses JSON automatically. "
            "Pagination: many REST APIs use offset/limit or 'hasMore' — loop until done. "
            "Caching: save responses to disk so you don't hammer the API during development. "
            "Rate limits: use time.sleep() or exponential backoff on 429 responses."
        ),
        "challenge": (
            "Rewrite the Pitch Profiler client from scratch (don't import baseball_data). "
            "Build a PitchProfilerClient class: "
            "(1) __init__(self, api_key: str) — stores key, creates requests.Session. "
            "(2) _get(self, endpoint: str) -> list[dict] — calls the API, calls raise_for_status(), "
            "returns response.json()['items']. Raises PitchProfilerError on failure. "
            "(3) career_pitchers(self) -> pd.DataFrame — calls GET_CAREER_PITCHERS/{key}, returns DataFrame. "
            "(4) season_pitchers(self, season: int) -> pd.DataFrame — same for seasonal endpoint. "
            "(5) Add file-based caching: check Path(f'~/.pp_cache/{endpoint}.json').expanduser() first; "
            "write to it on a live fetch. "
            "The base URL: https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon"
        ),
    },
    {
        "id": "pandas_optimization",
        "phase": "Phase 2: Data & Analytics",
        "title": "pandas Performance: Profiling & Optimizing",
        "concept": (
            "Category dtype for low-cardinality string columns cuts memory 10x+: df['status'].astype('category'). "
            "Downcasting numerics: pd.to_numeric(df['col'], downcast='float'). "
            "df.memory_usage(deep=True) shows actual memory per column. "
            "Avoid apply() on large DataFrames — it's a Python loop. Use vectorized operations instead. "
            "df.query() is faster than boolean indexing on large frames. "
            "Reading large CSVs: use dtype= param to avoid inference, usecols= to read only needed cols. "
            "chunksize= in read_csv lets you process huge files in batches."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers; df = career_pitchers(). "
            "This DataFrame has 100+ columns — a perfect optimization target. "
            "(1) Print total memory usage in MB before optimization. "
            "(2) Identify all string columns with fewer than 50 unique values and convert to category. "
            "(3) Downcast all float64 columns to float32 and all int64 to int32 where safe "
            "(check for value overflow before casting). "
            "(4) Print memory after — what's the % reduction? "
            "(5) The slow way: use apply() to compute 'era_label' = 'Good' if era < 3.5 else 'Average' if < 4.5 else 'Poor'. "
            "The fast way: use np.select(). Benchmark both with timeit on 10 iterations."
        ),
    },
    {
        "id": "data_pipelines",
        "phase": "Phase 2: Data & Analytics",
        "title": "Building Reusable Data Pipelines",
        "concept": (
            "A pipeline is a sequence of transformations — each step takes a DataFrame, returns a DataFrame. "
            "DataFrame.pipe(func, *args) chains transformations readably. "
            "Design each step as a pure function: def add_tier(df) -> pd.DataFrame. "
            "functools.reduce(pipe, [f1, f2, f3], df) runs a list of functions in sequence. "
            "Logging between steps (shape before/after, null counts) makes debugging easy. "
            "Type aliases: DataPipeline = list[Callable[[pd.DataFrame], pd.DataFrame]]. "
            "This pattern makes testing trivial — test each transform independently."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers; raw = career_pitchers(). "
            "Build a pitcher analysis pipeline with these steps as separate functions: "
            "(1) filter_qualified(df, min_ip=50): drop pitchers below min_ip threshold. "
            "(2) add_stuff_tier(df): add 'stuff_tier' column (Elite/Above Avg/Below Avg) from stuff_rv. "
            "(3) add_ace_score(df): add composite 'ace_score' = normalized stuff_rv + whiff_pct - era (z-scores). "
            "(4) rank_pitchers(df): add 'rank' column (1 = best ace_score). "
            "(5) select_report_cols(df): keep only pitcher_name, team, era, whiff_pct, stuff_rv, stuff_tier, ace_score, rank. "
            "Chain with .pipe(). Add run_pipeline(df, steps, verbose=True) that prints shape after each step. "
            "Final output: top 20 pitchers by ace_score."
        ),
    },
    {
        "id": "xgboost_basics",
        "phase": "Phase 2: Data & Analytics",
        "title": "Machine Learning Workflow with XGBoost",
        "concept": (
            "A clean ML workflow: load → split → preprocess → train → evaluate → iterate. "
            "train_test_split(X, y, test_size=0.2, random_state=42) for reproducibility. "
            "XGBClassifier/XGBRegressor from xgboost. Key params: n_estimators, max_depth, learning_rate. "
            "Always encode categoricals before fitting — pd.get_dummies() or OrdinalEncoder. "
            "eval_set=[(X_val, y_val)] with early_stopping_rounds prevents overfitting. "
            "feature_importances_ shows what the model relied on. "
            "Cross-validate before trusting a single train/test split."
        ),
        "challenge": (
            "Load: from baseball_data import career_pitchers; df = career_pitchers(). "
            "Goal: predict stuff_tier (Elite / Above Avg / Below Avg) from other pitching metrics. "
            "Steps: "
            "(1) Filter to pitchers with ip >= 50. Drop rows where stuff_rv is null (that's the source of the label). "
            "(2) Build stuff_tier target from stuff_rv as before. "
            "(3) Features: era, whiff_pct, k_pct, bb_pct, arm_angle, extension — drop nulls in these cols. "
            "(4) LabelEncode the target. Split 80/20 stratified. "
            "(5) Train XGBClassifier with early_stopping_rounds=20 on the val set. "
            "(6) Print accuracy, classification_report, and top 5 feature importances with a horizontal bar chart. "
            "Bonus: does arm_angle matter for predicting stuff tier?"
        ),
    },
]

SYSTEM_PROMPT = """You are a coding tutor for Ian Bach, a developer working on Oracle Fusion Procurement
extensions, sports analytics (baseball/march madness), and AI agents.

Ian's background: intermediate Python, working with Oracle REST APIs, pandas, XGBoost, and building
Claude-powered agents. He wants to become more efficient and idiomatic in Python and data work.

Phase 2 data context — Pitch Profiler API (baseball pitching analytics):
- Base URL: https://g837e5a6fbcb0dd-ch2sockkby63dgzo.adb.us-chicago-1.oraclecloudapps.com/ords/admin/patreon
- Endpoints: GET_CAREER_PITCHERS, GET_CAREER_PITCHES, GET_SEASON_PITCHERS/{season},
  GET_TEAM_SEASON_PITCHERS/{season}, GET_SEASON_PITCHES/{season}, GET_TEAM_SEASON_PITCHES/{season}
- Key metrics in the data: era, whiff_pct, stuff_rv, pitching_rv, command_rv, k_pct, bb_pct,
  arm_angle, extension, spin_rate, ip, starts, pitcher_name, team
- baseball_data.py is a helper module in the project that wraps this API with caching
- Import pattern: from baseball_data import career_pitchers, season_pitchers, career_pitches

Your teaching style:
- Concrete, practical examples using the Pitch Profiler data where relevant to Phase 2 lessons
- Show WHY something is better, not just that it is
- Point out common mistakes before Ian makes them
- Be direct and concise — no filler
- When reviewing code: lead with what's good, then specific improvements with corrected code shown inline
- Never just say "good job" — always give a specific next-level tip even on good code

When presenting a challenge, add 1-2 realistic twists to make it feel like real work."""


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed": [], "current_index": 0, "sessions": []}


def save_progress(progress: dict) -> None:
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def stream_response(client: anthropic.Anthropic, messages: list, extra_system: str = "") -> str:
    system = SYSTEM_PROMPT
    if extra_system:
        system += f"\n\n{extra_system}"

    collected = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=messages,
        thinking={"type": "adaptive"},
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            collected.append(text)
    print()
    return "".join(collected)


def get_multiline_input(prompt: str) -> str:
    print(f"\n{prompt}")
    print("(Type or paste your code. Enter a blank line then 'DONE' to submit, or 'SKIP' to skip.)\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "DONE":
            break
        if line.strip().upper() == "SKIP":
            return "SKIP"
        lines.append(line)
    return "\n".join(lines)


def print_header(text: str, char: str = "=") -> None:
    width = 70
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}\n")


def run_lesson(client: anthropic.Anthropic, lesson: dict, progress: dict) -> None:
    print_header(f"{lesson['phase']}  →  {lesson['title']}")

    # Teach the concept
    print("📚 CONCEPT\n")
    stream_response(client, [
        {
            "role": "user",
            "content": (
                f"Teach me this concept in 3-4 short paragraphs. Be concrete with code examples. "
                f"Topic: {lesson['title']}\n\nCore concept: {lesson['concept']}"
            ),
        }
    ])

    input("\n[Press Enter when ready for the challenge...]")

    # Present the challenge
    print_header("CHALLENGE", "-")
    stream_response(client, [
        {
            "role": "user",
            "content": (
                f"Present this coding challenge. Rewrite it slightly to make it feel like real work. "
                f"Add one realistic complication. Format it clearly with numbered steps.\n\n"
                f"Challenge: {lesson['challenge']}"
            ),
        }
    ])

    # Get the user's solution
    user_code = get_multiline_input("Your solution:")

    if user_code.strip().upper() == "SKIP":
        print("\n⏭  Skipped. Moving to next lesson.\n")
        return

    # Evaluate the solution
    print_header("FEEDBACK", "-")
    stream_response(
        client,
        [
            {
                "role": "user",
                "content": (
                    f"Evaluate this code submission for the lesson '{lesson['title']}'. "
                    f"Challenge was: {lesson['challenge']}\n\n"
                    f"Ian's code:\n```python\n{user_code}\n```\n\n"
                    f"Structure your feedback as:\n"
                    f"1. What's solid (specific, not generic)\n"
                    f"2. What to improve (show the corrected version inline)\n"
                    f"3. One advanced technique they could add next time\n"
                    f"4. A one-line key takeaway to remember"
                ),
            }
        ],
    )

    # Mark complete
    lesson_id = lesson["id"]
    if lesson_id not in progress["completed"]:
        progress["completed"].append(lesson_id)
    progress["sessions"].append({
        "lesson_id": lesson_id,
        "code_submitted": len(user_code) > 0,
    })
    save_progress(progress)

    retry = input("\n🔁 Retry this lesson? (y/N): ").strip().lower()
    if retry == "y":
        run_lesson(client, lesson, progress)


def show_progress_summary(progress: dict) -> None:
    total = len(CURRICULUM)
    done = len(progress["completed"])
    bar_filled = int((done / total) * 40)
    bar = "█" * bar_filled + "░" * (40 - bar_filled)
    print(f"\n  Progress: [{bar}] {done}/{total} lessons\n")

    current_phase = None
    for lesson in CURRICULUM:
        phase = lesson["phase"]
        if phase != current_phase:
            print(f"  {phase}")
            current_phase = phase
        status = "✅" if lesson["id"] in progress["completed"] else "○ "
        print(f"    {status} {lesson['title']}")
    print()


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Set it with: set ANTHROPIC_API_KEY=your-key-here (Windows)")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    progress = load_progress()

    print_header("Python Coding Tutor — Powered by Claude")

    while True:
        show_progress_summary(progress)

        print("  What would you like to do?")
        print("  [1] Continue from where I left off")
        print("  [2] Pick a specific lesson")
        print("  [3] Quit\n")

        choice = input("  Choice: ").strip()

        if choice == "3" or choice.lower() == "q":
            print("\n  See you next session!\n")
            break

        elif choice == "2":
            print("\n  Lessons:")
            for i, lesson in enumerate(CURRICULUM, 1):
                status = "✅" if lesson["id"] in progress["completed"] else "  "
                print(f"  {i:2}. {status} {lesson['title']}")
            try:
                idx = int(input("\n  Enter lesson number: ").strip()) - 1
                if 0 <= idx < len(CURRICULUM):
                    run_lesson(client, CURRICULUM[idx], progress)
                else:
                    print("  Invalid number.")
            except ValueError:
                print("  Please enter a number.")

        else:  # default: continue
            # Find next incomplete lesson
            next_lesson = None
            for lesson in CURRICULUM:
                if lesson["id"] not in progress["completed"]:
                    next_lesson = lesson
                    break

            if next_lesson is None:
                print("\n  🎉 You've completed the full curriculum! Choose option 2 to revisit any lesson.\n")
            else:
                run_lesson(client, next_lesson, progress)


if __name__ == "__main__":
    main()

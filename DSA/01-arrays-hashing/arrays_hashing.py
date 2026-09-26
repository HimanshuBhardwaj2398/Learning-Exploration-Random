import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Arrays & hashing · DSA")


@app.cell
def _():
    import random

    import marimo as mo

    from learnkit import (
        Case,
        array_view,
        assert_cases,
        check,
        kv_view,
        parse_ints,
        run_cases,
        solution,
        sudoku_view,
    )

    return (
        Case,
        array_view,
        assert_cases,
        check,
        kv_view,
        mo,
        parse_ints,
        random,
        run_cases,
        solution,
        sudoku_view,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Arrays & hashing

    **Pattern 01 · DSA.** *Have I seen this before?* is the question a hash set answers in O(1). *How many? Where? Which group?* is what a dict answers. Most array problems that look like O(n²) collapse to a single pass once you pick the right table.

    Anchors: **217 → 1 → 49 → 128** · the Sudoku check (36) and "why it's O(n)" (128) are worked visually below
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "**How to use this notebook.** Online, it runs real Python in your browser; the first load takes a few seconds. "
            "Locally, `marimo edit DSA/01-arrays-hashing/arrays_hashing.py` shows and lets you change every cell. "
            "Work top to bottom: **Spot it → Sudoku in three sets → Why it's O(n) → Templates → Practice → Traps → Recall.**"
        ),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Spot it

    | You read… | Reach for | Because |
    | :--- | :--- | :--- |
    | "contains duplicate", "seen before", "first repeated" | `set` | membership in O(1) average |
    | "anagram", "same letters", "frequency", "majority" | `Counter` / dict of counts | compare or query counts |
    | "group", "bucket", "categorise" | `defaultdict(list)` keyed by a *signature* | same signature ⇒ same group |
    | "two numbers add to target", **unsorted**, return **indices** | dict value → index | look up the complement as you go |
    | "longest consecutive", "run of values" | `set` + start detection | only walk from the start of a run |
    | "valid Sudoku / grid rules" | one set per unit (row, column, box) | each constraint is a membership test |

    **The trade:** a table buys time with memory, O(n) extra space for O(1) lookups. The alternative is usually **sorting** (O(n log n), little extra space) at the cost of the original order.

    **The honest caveat:** hash lookups are O(1) *on average*. Adversarial collisions can make a lookup O(n); for ints and short strings in interview problems, say "O(1) average" and name the assumption.

    **Pseudo code first, always.** Before touching Python, write the loop in words: *for each x: if the table already answers my question, return; otherwise record x.* Nearly every problem in this notebook is that sentence with a different table.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · Sudoku in three sets

    A board is valid when no digit repeats inside a **row**, a **column** or a **3×3 box**. That's one question asked three ways: *have I already placed this digit in this unit?* Keep three families of sets and check every filled cell against its three.

    The only trick worth learning is how a cell finds its box: **(r // 3, c // 3)**. Floor division is the general "which bucket of size k" move, and it tiles up in grids, pagination, time buckets and sharding.
    """)
    return


@app.cell
def _():
    VALID_BOARD = [
        "53..7....",
        "6..195...",
        ".98....6.",
        "8...6...3",
        "4..8.3..1",
        "7...2...6",
        ".6....28.",
        "...419..5",
        "....8..79",
    ]

    def with_cell(board: list[str], r: int, c: int, d: str) -> list[str]:
        rows = [list(row) for row in board]
        rows[r][c] = d
        return ["".join(row) for row in rows]

    BOARDS = {
        "Valid board (LC 36 example)": VALID_BOARD,
        "Row clash: a second 7 in row 0": with_cell(VALID_BOARD, 0, 2, "7"),
        "Column clash: a second 5 in column 0": with_cell(VALID_BOARD, 8, 0, "5"),
        "Box clash: a second 8 in the top-left box": with_cell(VALID_BOARD, 1, 1, "8"),
    }

    def sudoku_frames(board: list[str]) -> list[dict]:
        rows = [set() for _ in range(9)]
        cols = [set() for _ in range(9)]
        boxes: dict[tuple[int, int], set] = {}
        frames, done = [], []
        for r in range(9):
            for c in range(9):
                d = board[r][c]
                if d == ".":
                    continue
                b = (r // 3, c // 3)
                box = boxes.setdefault(b, set())
                clash = "row" if d in rows[r] else "column" if d in cols[c] else "box" if d in box else None
                frames.append(dict(r=r, c=c, d=d, b=b, row_set=sorted(rows[r]), col_set=sorted(cols[c]), box_set=sorted(box), clash=clash, done=list(done)))
                if clash:
                    return frames
                rows[r].add(d)
                cols[c].add(d)
                box.add(d)
                done.append((r, c))
        frames.append(dict(final=True, done=list(done)))
        return frames

    def is_valid_sudoku(board: list[str]) -> bool:
        return not sudoku_frames(board)[-1].get("clash")

    return BOARDS, VALID_BOARD, is_valid_sudoku, sudoku_frames


@app.cell
def _(BOARDS, mo):
    board_pick = mo.ui.dropdown(options=list(BOARDS), value="Valid board (LC 36 example)", label="Board")
    board_pick
    return (board_pick,)


@app.cell
def _(BOARDS, board_pick, mo, sudoku_frames):
    board = BOARDS[board_pick.value]
    board_frames = sudoku_frames(board)
    board_step = mo.ui.slider(0, max(len(board_frames) - 1, 1), value=0, label="Filled cell", full_width=True, show_value=True)
    board_step
    return board, board_frames, board_step


@app.cell
def _(board, board_frames, board_step, mo, sudoku_view):
    _f = board_frames[min(board_step.value, len(board_frames) - 1)]

    def _chips(title, key, values, digit, hot):
        body = " ".join(f"<b style='color:#dc2626'>{v}</b>" if (hot and v == digit) else v for v in values) or "∅"
        return mo.md(f"**{title}** `{key}`<br>{{ {body} }}")

    if _f.get("final"):
        _view = sudoku_view(board, done=_f["done"], show_peers=False)
        _panel = mo.callout(mo.md(f"All {len(_f['done'])} filled cells checked in clean: **valid**. One pass, O(81) time, O(81) space."), kind="success")
    else:
        _r, _c, _d, _b = _f["r"], _f["c"], _f["d"], _f["b"]
        _bad = [(_r, _c)]
        if _f["clash"]:
            for _rr in range(9):
                for _cc in range(9):
                    _same_unit = (_f["clash"] == "row" and _rr == _r) or (_f["clash"] == "column" and _cc == _c) or (_f["clash"] == "box" and (_rr // 3, _cc // 3) == _b)
                    if _same_unit and (_rr, _cc) in _f["done"] and board[_rr][_cc] == _d:
                        _bad.append((_rr, _cc))
        _view = sudoku_view(board, focus=(_r, _c), bad=_bad if _f["clash"] else [], done=_f["done"])
        _status = (
            mo.callout(mo.md(f"**{_d}** is already in this **{_f['clash']}**: stop, the board is **invalid**."), kind="danger")
            if _f["clash"] else mo.md(f"**{_d}** is new to all three, so add it to each set and move on.")
        )
        _panel = mo.vstack([
            mo.md(f"Cell **({_r}, {_c})** holds **{_d}**. Its box is (r // 3, c // 3) = **{_b}**."),
            _chips("row set", f"rows[{_r}]", _f["row_set"], _d, _f["clash"] == "row"),
            _chips("column set", f"cols[{_c}]", _f["col_set"], _d, _f["clash"] == "column"),
            _chips("box set", f"boxes[{_b}]", _f["box_set"], _d, _f["clash"] == "box"),
            _status,
        ])
    mo.hstack([_view, _panel], justify="start", align="start", gap=2, wrap=True)
    return


@app.cell
def _(mo):
    box_r = mo.ui.slider(0, 8, value=4, label="row r", show_value=True)
    box_c = mo.ui.slider(0, 8, value=7, label="column c", show_value=True)
    mo.vstack([mo.md("**The box trick, on any cell.** Move the sliders: the tinted cells are everything this cell has to be unique against."), mo.hstack([box_r, box_c], justify="start", gap=3)])
    return box_c, box_r


@app.cell
def _(box_c, box_r, mo, sudoku_view):
    _br, _bc = box_r.value // 3, box_c.value // 3
    mo.hstack(
        [
            sudoku_view(["." * 9] * 9, focus=(box_r.value, box_c.value), cell_px=26),
            mo.md(
                f"r = {box_r.value} → r // 3 = **{_br}** (box-row)<br>c = {box_c.value} → c // 3 = **{_bc}** (box-column)<br><br>"
                f"Box key: **({_br}, {_bc})**. Prefer one number? `3 * (r // 3) + c // 3` = **{3 * _br + _bc}**.<br><br>"
                "Rows 0–2 share box-row 0, rows 3–5 box-row 1, rows 6–8 box-row 2: grouping by threes is exactly what integer division does."
            ),
        ],
        justify="start", align="center", gap=2, wrap=True,
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Why Longest Consecutive is O(n), not O(n²)

    ```python
    def longest_consecutive(nums: list[int]) -> int:
        num_set = set(nums)
        best = 0
        for x in num_set:
            if x - 1 not in num_set:          # the guard: x starts a run
                y = x
                while y + 1 in num_set:       # walk the run forward
                    y += 1
                best = max(best, y - x + 1)
        return best
    ```

    A loop inside a loop: the classic shape of O(n²). But the inner walk only fires when **x starts a run** (x − 1 is absent), every run has exactly one start, and runs don't overlap. So across the whole scan each number is walked over **at most once**. Charge each number two checks, its own guard and one walk step, and the total is **≤ 2n**. That's **amortisation**: bound the total work, then divide by n.

    Step through it. Numbers are drawn in sorted order so the runs are visible; the scan itself visits them in input order.
    """)
    return


@app.cell
def _(mo):
    lcs_values = mo.ui.text(value="100, 4, 200, 1, 3, 2", label="nums", full_width=True)
    lcs_values
    return (lcs_values,)


@app.cell
def _():
    def lcs_frames(nums: list[int]) -> list[dict]:
        num_set, frames = set(nums), []
        outer = walk = checks = best = 0
        starts, reached = set(), set()

        def snap(x, y, note):
            frames.append(dict(x=x, y=y, note=note, starts=set(starts), reached=set(reached),
                               state={"outer visits": outer, "walk steps": walk, "membership checks": checks, "2n": 2 * len(num_set), "best": best}))

        for x in dict.fromkeys(nums):  # each distinct value once, in input order
            outer += 1
            checks += 1
            if x - 1 in num_set:
                snap(x, None, f"{x - 1} is in the set, so {x} is inside someone else's run: no walk. One check, move on.")
                continue
            starts.add(x)
            y = x
            snap(x, y, f"{x - 1} is absent, so {x} starts a run. Walk forward.")
            while y + 1 in num_set:
                checks += 1
                walk += 1
                y += 1
                reached.add(y)
                snap(x, y, f"{y} is in the set: extend the run to {x}..{y}.")
            checks += 1
            best = max(best, y - x + 1)
            snap(x, y, f"{y + 1} is absent: the run {x}..{y} has length {y - x + 1}. best = {best}.")
        return frames

    def naive_checks(nums: list[int]) -> int:
        """Walk forward from EVERY number, with no start guard."""
        num_set, checks = set(nums), 0
        for x in num_set:
            y = x
            checks += 1
            while y + 1 in num_set:
                checks += 1
                y += 1
        return checks

    return lcs_frames, naive_checks


@app.cell
def _(lcs_frames, lcs_values, mo, parse_ints):
    try:
        lcs_input = parse_ints(lcs_values.value, low=1, high=16)
        _err = None
    except ValueError as _e:
        lcs_input, _err = [], str(_e)
    mo.stop(_err is not None, mo.callout(_err or "", kind="warn"))
    lcs_seq = lcs_frames(lcs_input)
    lcs_step = mo.ui.slider(0, max(len(lcs_seq) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    lcs_step
    return lcs_input, lcs_seq, lcs_step


@app.cell
def _(array_view, kv_view, lcs_input, lcs_seq, lcs_step, mo, naive_checks):
    _f = lcs_seq[min(lcs_step.value, len(lcs_seq) - 1)]
    _line = sorted(set(lcs_input))
    _index = {v: k for k, v in enumerate(_line)}
    _marks = {_index[v]: "focus" for v in _f["starts"]}
    _marks.update({_index[v]: "hit" for v in _f["reached"]})
    _pointers = {"x": _index[_f["x"]]}
    if _f["y"] is not None and _f["y"] != _f["x"]:
        _pointers["y"] = _index[_f["y"]]
    mo.vstack([
        mo.hstack([array_view(_line, pointers=_pointers, marks=_marks, cell_px=40), kv_view(_f["state"])], justify="start", align="center", gap=2, wrap=True),
        mo.md(f"**Step {min(lcs_step.value, len(lcs_seq) - 1) + 1} of {len(lcs_seq)}.** {_f['note']} Indigo = starts a run, green = reached by a walk. "
              f"Without the guard (walk from every number) this input costs **{naive_checks(lcs_input)}** checks; the guarded scan never exceeds 2n = {2 * len(set(lcs_input))}."),
    ])
    return


@app.cell
def _(lcs_frames, mo, naive_checks, random):
    _rows = []
    _rng = random.Random(4)
    for _n in (10, 100, 1000):
        _worst = list(range(_n))
        _rng.shuffle(_worst)  # one long run: the worst case for the unguarded walk
        _guarded = lcs_frames(_worst)[-1]["state"]["membership checks"]
        _rows.append(f"| {_n:,} | {_guarded:,} | {naive_checks(_worst):,} |")
    mo.md(
        "Worst case for the unguarded version, one long run shuffled:\n\n| n | guarded scan (≤ 2n) | walk from every number |\n| :--- | :--- | :--- |\n"
        + "\n".join(_rows)
        + "\n\n**The trap:** reading a nested loop as O(n²) by reflex. The bound *n outer × n inner* is real but loose; when a guard makes the inner work fire only on run starts, and runs partition the input, the true bound collapses to linear."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · Templates

    | Question | Pseudo code | Python |
    | :--- | :--- | :--- |
    | seen before? | for x: if x in seen → yes; add x | `seen = set()` … `if x in seen: return True` … `seen.add(x)` |
    | counts equal? | count both, compare | `Counter(s) == Counter(t)` |
    | which group? | key = signature(x); groups[key].append(x) | `groups = defaultdict(list)` … `groups[tuple(sorted(w))].append(w)` |
    | complement? | for i, x: if target − x seen → pair; record x → i | `seen = {}` … `if target - x in seen: return [seen[target - x], i]` … `seen[x] = i` |
    | runs of values? | set; for x: if x − 1 absent → walk | the Longest Consecutive template above |

    **Order matters in the complement template:** look up *before* you record, or an element pairs with itself (trap 2 below).

    **Choosing a signature for grouping:** `tuple(sorted(word))` costs O(k log k) per word; a 26-slot count tuple costs O(k) and is the better answer for long words. Either way it must be **hashable**: a list is not (trap 1).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · Practice: worked → faded → solo
    """)
    return


@app.cell
def _(Case):
    CASES_217 = [
        Case(([1, 2, 3, 1],), True), Case(([1, 2, 3, 4],), False), Case(([1, 1, 1, 3, 3, 4, 3, 2, 4, 2],), True),
        Case(([],), False, label="empty"), Case(([7],), False, label="single"), Case(([-1, -1],), True, label="negatives"),
    ]
    SOLUTION_217 = '''
    def contains_duplicate(nums: list[int]) -> bool:
        seen = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False
    '''
    STUB_217 = '''def contains_duplicate(nums: list[int]) -> bool:
        # One pass with a set: have I seen x before?
        ...
    '''
    CASES_1 = [
        Case(([2, 7, 11, 15], 9), [0, 1]), Case(([3, 2, 4], 6), [1, 2], label="don't pair 3 with itself"),
        Case(([3, 3], 6), [0, 1], label="duplicates"), Case(([-3, 4, 3, 90], 0), [0, 2], label="negatives"),
        Case(([1, 5, 9, 2], 11), [2, 3]),
    ]
    SOLUTION_1 = '''
    def two_sum(nums: list[int], target: int) -> list[int]:
        seen = {}                        # value -> index
        for i, x in enumerate(nums):
            if target - x in seen:       # look up BEFORE recording
                return [seen[target - x], i]
            seen[x] = i
        return []
    '''
    STUB_1 = '''def two_sum(nums: list[int], target: int) -> list[int]:
        seen = {}                        # value -> index
        for i, x in enumerate(nums):
            if ...:                      # is the complement already recorded?
                return ...
            ...                          # record x, AFTER the check
        return []
    '''
    CASES_49 = [
        Case((["eat", "tea", "tan", "ate", "nat", "bat"],), [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]),
        Case(([""],), [[""]], label="one empty string"), Case((["a"],), [["a"]]),
        Case((["ab", "ba", "abc", "cab", "b"],), [["ab", "ba"], ["abc", "cab"], ["b"]]),
        Case((["aab", "abb"],), [["aab"], ["abb"]], label="same letters, different counts"),
    ]
    SOLUTION_49 = '''
    from collections import defaultdict

    def group_anagrams(strs: list[str]) -> list[list[str]]:
        groups = defaultdict(list)
        for word in strs:
            counts = [0] * 26
            for ch in word:
                counts[ord(ch) - ord("a")] += 1
            groups[tuple(counts)].append(word)   # a tuple is hashable; a list isn't
        return list(groups.values())
    '''
    STUB_49 = '''def group_anagrams(strs: list[str]) -> list[list[str]]:
        # Same signature => same group. What signature do all anagrams share, and is it hashable?
        ...
    '''
    CASES_128 = [
        Case(([100, 4, 200, 1, 3, 2],), 4), Case(([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), 9),
        Case(([],), 0, label="empty"), Case(([5],), 1), Case(([1, 2, 0, 1],), 3, label="duplicates"),
        Case(([-2, -1, 0, 10, 11],), 3, label="negatives"), Case((list(range(2000, 0, -1)),), 2000, label="2,000 descending values"),
    ]
    SOLUTION_128 = '''
    def longest_consecutive(nums: list[int]) -> int:
        num_set = set(nums)
        best = 0
        for x in num_set:
            if x - 1 not in num_set:         # only walk from the start of a run
                y = x
                while y + 1 in num_set:
                    y += 1
                best = max(best, y - x + 1)
        return best
    '''
    STUB_128 = '''def longest_consecutive(nums: list[int]) -> int:
        # O(n): a set, plus a guard so each run is walked exactly once.
        ...
    '''

    def norm_groups(groups):
        return sorted(sorted(g) for g in groups)

    def norm_pair(pair):
        return sorted(pair) if isinstance(pair, (list, tuple)) else pair

    return (
        CASES_1,
        CASES_128,
        CASES_217,
        CASES_49,
        SOLUTION_1,
        SOLUTION_128,
        SOLUTION_217,
        SOLUTION_49,
        STUB_1,
        STUB_128,
        STUB_217,
        STUB_49,
        norm_groups,
        norm_pair,
    )


@app.cell
def _(SOLUTION_217, STUB_217, mo, solution):
    ex217_editor = mo.ui.code_editor(value=STUB_217, language="python", min_height=160)
    ex217_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Worked: LC 217 Contains Duplicate\n\nThe base template: one pass, one set. Read the solution, close it, write it."),
        solution(SOLUTION_217, "Show the worked solution"), ex217_editor, ex217_run,
    ])
    return ex217_editor, ex217_run


@app.cell
def _(CASES_217, check, ex217_editor, ex217_run, mo):
    mo.stop(not ex217_run.value, mo.md("_Write your solution above, then press **Run tests**._"))
    check(ex217_editor.value, "contains_duplicate", CASES_217)
    return


@app.cell
def _(SOLUTION_1, STUB_1, mo, solution):
    ex1_editor = mo.ui.code_editor(value=STUB_1, language="python", min_height=200)
    ex1_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Faded: LC 1 Two Sum\n\nUnsorted input, return **original indices** (any order): the complement dict. Fill the blanks. Why can't you sort and use two pointers here?"),
        ex1_editor, ex1_run, solution(SOLUTION_1),
    ])
    return ex1_editor, ex1_run


@app.cell
def _(CASES_1, check, ex1_editor, ex1_run, mo, norm_pair):
    mo.stop(not ex1_run.value, mo.md("_Fill in the blanks, then press **Run tests**._"))
    check(ex1_editor.value, "two_sum", CASES_1, normalise=norm_pair)
    return


@app.cell
def _(SOLUTION_49, STUB_49, mo, solution):
    ex49_editor = mo.ui.code_editor(value=STUB_49, language="python", min_height=180)
    ex49_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Faded: LC 49 Group Anagrams\n\nGroup words that are anagrams of each other (any order). The whole problem is choosing the key."),
        ex49_editor, ex49_run, solution(SOLUTION_49),
    ])
    return ex49_editor, ex49_run


@app.cell
def _(CASES_49, check, ex49_editor, ex49_run, mo, norm_groups):
    mo.stop(not ex49_run.value, mo.md("_Write it, then press **Run tests**._"))
    check(ex49_editor.value, "group_anagrams", CASES_49, normalise=norm_groups)
    return


@app.cell
def _(SOLUTION_128, STUB_128, mo, solution):
    ex128_editor = mo.ui.code_editor(value=STUB_128, language="python", min_height=180)
    ex128_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md(
            "### Solo: LC 128 Longest Consecutive Sequence\n\n"
            "Length of the longest run of consecutive integers, in **O(n)**: no sorting. From scratch, then explain the amortised bound out loud. "
            "The 2,000-value test doubles as a time limit: an unguarded walk is O(n²) and runs out of budget there."
        ),
        ex128_editor, ex128_run, solution(SOLUTION_128),
    ])
    return ex128_editor, ex128_run


@app.cell
def _(CASES_128, check, ex128_editor, ex128_run, mo):
    mo.stop(not ex128_run.value, mo.md("_Write it from scratch, then press **Run tests**._"))
    check(ex128_editor.value, "longest_consecutive", CASES_128)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Ladder:** 242 Valid Anagram · 347 Top K Frequent Elements (bucket sort) · 238 Product of Array Except Self · 36 Valid Sudoku · 271 Encode and Decode Strings.
    """)
    return


@app.cell
def _():
    TRAPS = [
        ("1 · A list as a dict key", "Lists are mutable, so they're unhashable. Use a tuple (or a string) as the signature.",
         "def f(words):\n    groups = {}\n    for w in words:\n        groups.setdefault(sorted(w), []).append(w)\n    return list(groups.values())\n",
         "def f(words):\n    groups = {}\n    for w in words:\n        groups.setdefault(tuple(sorted(w)), []).append(w)\n    return list(groups.values())\n",
         (["eat", "tea", "tan"],)),
        ("2 · Two Sum: recording before looking up", "The element finds itself as its own complement.",
         "def f(nums, target):\n    seen = {}\n    for i, x in enumerate(nums):\n        seen[x] = i\n        if target - x in seen:\n            return [seen[target - x], i]\n    return []\n",
         "def f(nums, target):\n    seen = {}\n    for i, x in enumerate(nums):\n        if target - x in seen:\n            return [seen[target - x], i]\n        seen[x] = i\n    return []\n",
         ([3, 2, 4], 6)),
        ("3 · Anagram check with membership instead of counts", "A set test ignores how many times each letter appears.",
         "def f(s, t):\n    return len(s) == len(t) and all(ch in s for ch in t)\n",
         "def f(s, t):\n    from collections import Counter\n    return Counter(s) == Counter(t)\n",
         ("aab", "abb")),
        ("4 · Box index as r // 3 + c // 3", "Adding the coordinates merges different boxes: (0, 1) and (1, 0) collide, so a valid board looks invalid.",
         "def f(board):\n    boxes = {}\n    for r in range(9):\n        for c in range(9):\n            d = board[r][c]\n            if d == '.':\n                continue\n            key = r // 3 + c // 3\n            if d in boxes.setdefault(key, set()):\n                return False\n            boxes[key].add(d)\n    return True\n",
         "def f(board):\n    boxes = {}\n    for r in range(9):\n        for c in range(9):\n            d = board[r][c]\n            if d == '.':\n                continue\n            key = (r // 3, c // 3)\n            if d in boxes.setdefault(key, set()):\n                return False\n            boxes[key].add(d)\n    return True\n",
         None),
        ("5 · Deleting from a dict while iterating over it", "Python refuses: the dict changes size mid-iteration. Iterate over a copy of the keys.",
         "def f(counts):\n    for k in counts:\n        if counts[k] == 0:\n            del counts[k]\n    return counts\n",
         "def f(counts):\n    for k in list(counts):\n        if counts[k] == 0:\n            del counts[k]\n    return counts\n",
         ({"a": 0, "b": 2, "c": 0},)),
    ]

    def run_trap(code: str, args: tuple) -> str:
        import copy as _copy

        _ns: dict = {}
        exec(code, _ns)
        try:
            return repr(_ns["f"](*_copy.deepcopy(args)))
        except Exception as _exc:
            return f"{type(_exc).__name__}: {_exc}"

    return TRAPS, run_trap


@app.cell
def _(TRAPS, VALID_BOARD, mo, run_trap):
    _lines = ["| Trap | Input | Buggy output | Correct output |", "| :--- | :--- | :--- | :--- |"]
    _details = {}
    for _title, _why, _buggy, _correct, _args in TRAPS:
        _args = _args if _args is not None else (VALID_BOARD,)
        _shown = "the valid LC 36 board" if _args == (VALID_BOARD,) else ", ".join(repr(a) for a in _args)
        _lines.append(f"| {_title} | `{_shown}` | `{run_trap(_buggy, _args)}` | `{run_trap(_correct, _args)}` |")
        _details[_title] = mo.md(f"{_why}\n\n```python\n{_buggy}```")
    mo.vstack([
        mo.md("## 6 · Traps, with their actual wrong answers\n\nEach row runs the buggy code next to the fixed one, live."),
        mo.md("\n".join(_lines)),
        mo.accordion(_details),
        mo.md("**Cost traps that give right answers slowly:** `x in some_list` inside a loop is O(n) per check (use a set); walking from every number in Longest Consecutive is O(n²) (section 3); `Counter(a) == Counter(b)` inside a loop re-counts everything each time."),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7 · Recall: close everything and answer from memory
    """)
    return


@app.cell
def _(mo):
    mo.accordion({
        "1. What does a set buy you, what does it cost, and what's the alternative?": mo.md("O(1) average membership for O(n) extra space. The alternative is sorting: O(n log n) time, little space, but you lose the original order and indices."),
        "2. How does a Sudoku cell find its box, and why does it work?": mo.md("`(r // 3, c // 3)`: floor division buckets 0–2 → 0, 3–5 → 1, 6–8 → 2. As one number: `3 * (r // 3) + c // 3`."),
        "3. Why is Longest Consecutive O(n) despite the nested loop?": mo.md("The walk only starts at run starts (x − 1 absent); runs are disjoint, so every number is walked over at most once. Total checks ≤ 2n."),
        "4. In Two Sum, why must you look up before recording?": mo.md("Otherwise x can match itself when target = 2x, returning [i, i]."),
        "5. What's the best key for grouping anagrams, and why must it be a tuple?": mo.md("A 26-count signature (O(k) per word) or sorted letters (O(k log k)). Dict keys must be hashable, and lists aren't."),
        "6. When is 'O(1) lookup' not O(1)?": mo.md("Under heavy hash collisions a lookup can degrade to O(n). Say 'O(1) average' and name the assumption."),
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8 · Go deeper

    - **Labs in this folder:** [Sudoku in three sets](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/01-arrays-hashing/valid-sudoku-three-sets.html) · [Why it's O(n), not O(n²)](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/01-arrays-hashing/longest-consecutive-why-O-n.html)
    - [Python docs: collections](https://docs.python.org/3/library/collections.html): `Counter`, `defaultdict`
    - [Python wiki: TimeComplexity](https://wiki.python.org/moin/TimeComplexity): the real cost of list / dict / set operations
    - [Tech Interview Handbook: Hash table](https://www.techinterviewhandbook.org/algorithms/hash-table/)

    **Next:** [two pointers](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/notebooks/two_pointers.html), where sorted order replaces the table.
    """)
    return


@app.cell
def _(
    BOARDS,
    CASES_1,
    CASES_128,
    CASES_217,
    CASES_49,
    SOLUTION_1,
    SOLUTION_128,
    SOLUTION_217,
    SOLUTION_49,
    STUB_1,
    STUB_128,
    STUB_217,
    STUB_49,
    TRAPS,
    VALID_BOARD,
    assert_cases,
    is_valid_sudoku,
    lcs_frames,
    norm_groups,
    norm_pair,
    random,
    run_cases,
    run_trap,
    sudoku_frames,
):
    def test_answer_keys_pass():
        assert_cases(SOLUTION_217, "contains_duplicate", CASES_217)
        assert_cases(SOLUTION_1, "two_sum", CASES_1, normalise=norm_pair)
        assert_cases(SOLUTION_49, "group_anagrams", CASES_49, normalise=norm_groups)
        assert_cases(SOLUTION_128, "longest_consecutive", CASES_128)

    def test_stubs_do_not_pass_yet():
        for stub, name, cases, norm in ((STUB_217, "contains_duplicate", CASES_217, None), (STUB_1, "two_sum", CASES_1, norm_pair),
                                        (STUB_49, "group_anagrams", CASES_49, norm_groups), (STUB_128, "longest_consecutive", CASES_128, None)):
            assert not all(r.passed for r in run_cases(stub, name, cases, normalise=norm))

    def test_board_presets_fail_where_their_names_say():
        assert is_valid_sudoku(VALID_BOARD)
        for name, board in BOARDS.items():
            last = sudoku_frames(board)[-1]
            if name.startswith("Valid"):
                assert last.get("final")
            else:
                assert last["clash"] == name.split(" clash")[0].lower(), name

    def test_sudoku_scan_matches_a_direct_check():
        rng = random.Random(8)
        for _ in range(200):
            board = [list(row) for row in VALID_BOARD]
            r, c = rng.randrange(9), rng.randrange(9)
            board[r][c] = str(rng.randint(1, 9))
            board = ["".join(row) for row in board]
            units = [[board[r][c] for c in range(9)] for r in range(9)]
            units += [[board[r][c] for r in range(9)] for c in range(9)]
            units += [[board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)] for br in (0, 3, 6) for bc in (0, 3, 6)]
            direct = all(len([d for d in u if d != "."]) == len({d for d in u if d != "."}) for u in units)
            assert is_valid_sudoku(board) == direct

    def test_lcs_frames_are_linear_and_correct():
        rng = random.Random(9)
        for _ in range(300):
            nums = [rng.randint(-5, 15) for _ in range(rng.randint(1, 14))]
            frames = lcs_frames(nums)
            best = frames[-1]["state"]["best"]
            assert best == max(len(range(x, y + 1)) for x in set(nums) for y in set(nums) if all(v in set(nums) for v in range(x, y + 1)))
            assert frames[-1]["state"]["membership checks"] <= 2 * len(set(nums))

    def test_every_trap_really_fails():
        for title, _why, buggy, correct, args in TRAPS:
            args = args if args is not None else (VALID_BOARD,)
            assert run_trap(buggy, args) != run_trap(correct, args), title

    return


if __name__ == "__main__":
    app.run()

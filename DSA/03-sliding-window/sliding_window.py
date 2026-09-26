import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Sliding window · DSA")


@app.cell
def _():
    import random
    import textwrap

    import marimo as mo

    from learnkit import (
        Case,
        array_view,
        assert_cases,
        badge,
        check,
        code_view,
        kv_view,
        line_of,
        parse_ints,
        parse_text,
        run_cases,
        solution,
        staircase_view,
    )

    return (
        Case,
        array_view,
        assert_cases,
        badge,
        check,
        code_view,
        kv_view,
        line_of,
        mo,
        parse_ints,
        parse_text,
        random,
        run_cases,
        solution,
        staircase_view,
        textwrap,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Sliding window

    **Pattern 03 · DSA.** Two pointers moved toward each other and threw candidates away. A sliding window keeps **both pointers moving the same way** and cares about **everything between them**. That one change is the whole pattern, and it's why the cost stays O(n).

    Anchor ladder: **643 → 3 → 424** · builds on two pointers + hashing · leads to prefix sums and the monotonic deque
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "**How to use this notebook.** Online, it runs real Python in your browser; the first load takes a few seconds. "
            "Locally, `marimo edit DSA/03-sliding-window/sliding_window.py` shows and lets you change every cell. "
            "Work top to bottom: **Spot it → See it → Shapes → Counting → if vs while → Wrong tool → Practice → Traps → Recall.**"
        ),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Spot it

    A window is for one shape of question: find a **contiguous** run (subarray or substring) that satisfies a constraint, and report its length, sum, contents or count. Three signals, **all** present:

    1. **Contiguous.** *Subarray, substring, consecutive, window of size k.* The word *subsequence* rules it out: a window can only see an unbroken range.
    2. **A constraint you can check in O(1) from running state:** a sum, a count, a character-frequency dict, a set size.
    3. **Optimise or count:** longest / shortest / maximum / minimum / *how many*, or a fixed k.

    **What makes it legal: monotone validity.** If a window is invalid, every window containing it is invalid too (for *at most* constraints), or growing can only push a sum further past the target (for *at least* constraints with non-negative values). That's what lets `start` move forward and never look back. Add a negative number and the pattern silently returns wrong answers (section 6 shows one).

    | If the problem… | Pattern | Tell |
    | :--- | :--- | :--- |
    | cares about the contents between the pointers, both moving right | **Sliding window** | you keep running state |
    | cares only about the two endpoints, pointers converging | Two pointers | sorted input, pair / triplet |
    | counts subarrays with an **exact** sum, values may be negative | Prefix sum + hash | LC 560: a window is unsafe |
    | needs the max / min inside each window | Window + monotonic deque | LC 239: a dict can't pop the max |
    | says **subsequence** | DP / greedy | a window can't skip elements |

    **One-line discriminator:** two pointers asks *what's at the ends?*; a sliding window asks *what's inside?* If deleting an element from the middle would change your answer, you're holding a window.

    **Reflex:** if your brute force is *"for every start, extend to every end"*, the window is the fix. You're about to reuse almost all of that inner work.
    """)
    return


@app.cell
def _(mo):
    DRILL = [
        ("Longest substring with no repeating characters.", "Sliding window", "Contiguous + longest + a count you can update in O(1) (LC 3)."),
        ("Count subarrays whose sum is exactly k; values can be negative.", "Prefix sum + hash", "Exact sum with negatives breaks monotonicity (LC 560)."),
        ("Maximum value in every window of size k.", "Window + deque", "A dict can't give you the max after a removal (LC 239)."),
        ("Pair in a sorted array with sum = target.", "Two pointers", "Only the two ends matter (LC 167)."),
        ("Shortest subarray with sum ≥ target, all values positive.", "Sliding window", "Shortest shape: shrink while valid (LC 209)."),
        ("Longest increasing subsequence.", "DP", "Subsequence: a window can't skip elements (LC 300)."),
        ("Does s2 contain a permutation of s1?", "Sliding window", "Fixed window of len(s1) with a counter (LC 567)."),
        ("Number of subarrays with product < k, all values positive.", "Sliding window", "Counting shape: count += end - start + 1 (LC 713)."),
    ]
    _options = ["Sliding window", "Two pointers", "Prefix sum + hash", "Window + deque", "DP"]
    drill = mo.ui.array([mo.ui.radio(options=_options, label=f"**{k + 1}.** {q}", inline=True) for k, (q, _a, _w) in enumerate(DRILL)])
    drill_check = mo.ui.run_button(label="Check my answers")
    mo.vstack([mo.md("### Drill: name the pattern"), drill, drill_check])
    return DRILL, drill, drill_check


@app.cell
def _(DRILL, drill, drill_check, mo):
    mo.stop(not drill_check.value, mo.md("_Pick an answer for each, then press **Check my answers**._"))
    _rows, _score = [], 0
    for _k, ((_q, _answer, _why), _pick) in enumerate(zip(DRILL, drill.value)):
        _score += _pick == _answer
        _rows.append(f"| {_k + 1} | {'✓' if _pick == _answer else '✗'} | {_pick or '—'} | {_answer} | {_why} |")
    mo.md(f"**{_score} / {len(DRILL)}.** Target: 7 of 8, each justified in one sentence.\n\n| # | | You said | Answer | Why |\n| :--- | :--- | :--- | :--- | :--- |\n" + "\n".join(_rows))
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · See it: why the cost collapses to O(n)

    **Fixed length first (LC 643).** The brute force recomputes each window from scratch: k additions per position. The window reuses the previous sum and pays only for the difference: **add the incoming element, drop the outgoing one**. After the first fill that's 2 operations per step, however big k gets. Step through it and watch the two counters.
    """)
    return


@app.cell
def _(mo):
    fixed_values = mo.ui.text(value="2, 1, 5, 1, 3, 2", label="Array", full_width=True)
    fixed_k = mo.ui.number(start=1, stop=14, value=3, label="k")
    mo.hstack([fixed_values, fixed_k], widths=[3, 1])
    return fixed_k, fixed_values


@app.cell
def _(line_of, textwrap):
    CODE_FIXED = textwrap.dedent('''
    def max_sum_k(nums: list[int], k: int) -> int:
        window = sum(nums[:k])                  # pay O(k) once
        best = window
        for end in range(k, len(nums)):
            window += nums[end] - nums[end - k] # add incoming, drop outgoing
            best = max(best, window)
        return best
    ''').strip()

    def fixed_frames(nums: list[int], k: int) -> list[dict]:
        window = sum(nums[:k])
        best, naive, ops = window, k, k
        frames = [dict(start=0, end=k - 1, window=window, best=best, naive=naive, ops=ops, line=line_of(CODE_FIXED, "window = sum"),
                       note=f"First window: pay {k} additions once. Sum = {window}.")]
        for end in range(k, len(nums)):
            incoming, outgoing = nums[end], nums[end - k]
            window += incoming - outgoing
            best = max(best, window)
            naive += k
            ops += 2
            frames.append(dict(start=end - k + 1, end=end, window=window, best=best, naive=naive, ops=ops, line=line_of(CODE_FIXED, "window += nums[end]"),
                               note=f"Slide: + {incoming} (incoming) − {outgoing} (outgoing) = {window}. Brute force would add {k} numbers again."))
        return frames

    return CODE_FIXED, fixed_frames


@app.cell
def _(fixed_frames, fixed_k, fixed_values, mo, parse_ints):
    try:
        fixed_input = parse_ints(fixed_values.value, low=1, high=14)
        _k = int(fixed_k.value)
        if not 1 <= _k <= len(fixed_input):
            raise ValueError(f"k must be between 1 and {len(fixed_input)}.")
        fixed_seq = fixed_frames(fixed_input, _k)
        _err = None
    except ValueError as _e:
        fixed_seq, _err = [], str(_e)
    mo.stop(_err is not None, mo.callout(_err or "", kind="warn"))
    fixed_step = mo.ui.slider(0, max(len(fixed_seq) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    fixed_step
    return fixed_input, fixed_seq, fixed_step


@app.cell
def _(
    CODE_FIXED,
    array_view,
    code_view,
    fixed_input,
    fixed_seq,
    fixed_step,
    kv_view,
    mo,
):
    _f = fixed_seq[min(fixed_step.value, len(fixed_seq) - 1)]
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack([
                        array_view(fixed_input, pointers={"start": _f["start"], "end": _f["end"]}, window=(_f["start"], _f["end"]), cell_px=36 if len(fixed_input) > 10 else 44),
                        kv_view({"window sum": _f["window"], "best": _f["best"], "brute-force additions so far": _f["naive"], "window operations so far": _f["ops"]}),
                    ], align="center"),
                    code_view(CODE_FIXED, active=_f["line"]),
                ],
                wrap=True, align="start",
            ),
            mo.md(f"{_f['note']} The whole trick is `nums[end] - nums[end - k]`: if you ever write `sum(nums[i:i+k])` inside a loop, you've rebuilt the O(n·k) brute force."),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Variable windows: grow, shrink, record

    Almost every variable window is one skeleton: **grow `end` by one, update the state, then shrink `start` while a condition holds.** Only two lines change between shapes: the shrink condition, and *where you record the answer*.

    | The question says… | Shape | Shrink while | Record |
    | :--- | :--- | :--- | :--- |
    | "of size k", "every k consecutive" | **fixed** | the window is longer than k | every step once the window has size k |
    | "longest / maximum … such that" | **longest** | the window is **invalid** | **after** the shrink loop |
    | "shortest / minimum … such that" | **shortest** | the window is still **valid** | **inside** the shrink loop |
    | "number of subarrays … at most" | **counting** | the window is invalid | after the loop: `count += end - start + 1` |

    **The single most useful line in this notebook: longest records *after* shrinking; shortest records *inside* the shrinking.** Get those backwards and you get bugs 3 and 6 in section 8: plausible numbers, never an exception.

    Pick a problem and step through it. The badge tells you whether this step grows, shrinks or records.
    """)
    return


@app.cell
def _(textwrap):
    CODE_LONGEST = textwrap.dedent('''
    def longest_unique(s: str) -> int:
        count = defaultdict(int)
        start = best = 0
        for end, ch in enumerate(s):
            count[ch] += 1                      # grow: take s[end]
            while count[ch] > 1:                # only ch can have become a duplicate
                count[s[start]] -= 1            # shrink: drop s[start]
                if count[s[start]] == 0:
                    del count[s[start]]         # keep len(count) honest
                start += 1
            best = max(best, end - start + 1)   # record AFTER the shrink: window is valid
        return best
    ''').strip()
    CODE_SHORTEST = textwrap.dedent('''
    def min_subarray_len(target: int, nums: list[int]) -> int:
        start = total = 0
        best = float("inf")
        for end, v in enumerate(nums):
            total += v                          # grow
            while total >= target:              # while VALID: try shorter
                best = min(best, end - start + 1)   # record INSIDE the loop
                total -= nums[start]            # shrink
                start += 1
        return 0 if best == float("inf") else best
    ''').strip()
    CODE_ONES = textwrap.dedent('''
    def longest_ones(nums: list[int], k: int) -> int:
        start = zeros = best = 0
        for end, v in enumerate(nums):
            if v == 0:
                zeros += 1                      # grow
            while zeros > k:                    # invalid: more zeros than flips
                if nums[start] == 0:
                    zeros -= 1                  # shrink
                start += 1
            best = max(best, end - start + 1)   # record after the shrink
        return best
    ''').strip()
    CODE_COUNTING = textwrap.dedent('''
    def num_subarray_product_less_than_k(nums: list[int], k: int) -> int:
        if k <= 1:
            return 0                            # a product of positives is never < 1
        start, product, count = 0, 1, 0
        for end, v in enumerate(nums):
            product *= v                        # grow
            while product >= k:                 # invalid: shrink until product < k
                product //= nums[start]
                start += 1
            count += end - start + 1            # windows ending at end, starting >= start
        return count
    ''').strip()
    CODE_NEED_HAVE = textwrap.dedent('''
    def min_window(s: str, t: str) -> str:
        need = Counter(t)
        missing = len(t)                        # character slots still unfilled
        start, best = 0, (float("inf"), 0, 0)
        for end, ch in enumerate(s):
            if need[ch] > 0:
                missing -= 1                    # guard: surplus copies don't count
            need[ch] -= 1                       # grow
            while missing == 0:                 # valid: record, then try shorter
                if end - start + 1 < best[0]:
                    best = (end - start + 1, start, end)
                need[s[start]] += 1             # shrink
                if need[s[start]] > 0:
                    missing += 1
                start += 1
        return "" if best[0] == float("inf") else s[best[1]:best[2] + 1]
    ''').strip()

    WINDOW_PROBLEMS = {
        "LC 3 · longest substring without repeats (longest)": ("lc3", CODE_LONGEST, "abcabcbb", "", None),
        "LC 209 · min size subarray sum ≥ target (shortest)": ("lc209", CODE_SHORTEST, "2, 3, 1, 2, 4, 3", "7", "target"),
        "LC 1004 · max consecutive ones, flip ≤ k zeros (longest)": ("lc1004", CODE_ONES, "1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0", "2", "k"),
        "LC 713 · subarrays with product < k (counting)": ("lc713", CODE_COUNTING, "10, 5, 2, 6", "100", "k"),
        "LC 76 · minimum window substring (need / have)": ("lc76", CODE_NEED_HAVE, "ADOBECODEBANC", "ABC", "t"),
    }
    return (
        CODE_COUNTING,
        CODE_LONGEST,
        CODE_NEED_HAVE,
        CODE_ONES,
        CODE_SHORTEST,
        WINDOW_PROBLEMS,
    )


@app.cell
def _(
    CODE_COUNTING,
    CODE_LONGEST,
    CODE_NEED_HAVE,
    CODE_ONES,
    CODE_SHORTEST,
    line_of,
):
    def frames_lc3(s: str) -> list[dict]:
        code, frames = CODE_LONGEST, []
        count, start, best = {}, 0, 0

        def snap(end, snippet, note, event):
            frames.append(dict(arr=list(s), start=start, end=end, line=line_of(code, snippet), note=note, event=event,
                               state={"count": dict(count), "best": best}))

        for end, ch in enumerate(s):
            count[ch] = count.get(ch, 0) + 1
            snap(end, "count[ch] += 1", f"Grow: take '{ch}'. count['{ch}'] = {count[ch]}.", "grow")
            while count[ch] > 1:
                snap(end, "count[s[start]] -= 1", f"'{ch}' now appears twice: invalid. Shrink by dropping '{s[start]}'.", "shrink")
                count[s[start]] -= 1
                if count[s[start]] == 0:
                    del count[s[start]]
                start += 1
            best = max(best, end - start + 1)
            snap(end, "best = max", f"Valid: record length {end - start + 1}. best = {best}.", "record")
        return frames

    def frames_lc209(nums: list[int], target: int) -> list[dict]:
        code, frames = CODE_SHORTEST, []
        start, total, best = 0, 0, float("inf")

        def snap(end, snippet, note, event):
            frames.append(dict(arr=nums, start=start, end=end, line=line_of(code, snippet), note=note, event=event,
                               state={"total": total, "target": target, "best": "∞" if best == float("inf") else best}))

        for end, v in enumerate(nums):
            total += v
            snap(end, "total += v", f"Grow: take {v}. total = {total}.", "grow")
            while total >= target:
                best = min(best, end - start + 1)
                snap(end, "best = min", f"total {total} ≥ {target}: valid, so record length {end - start + 1} while it still is.", "record")
                snap(end, "total -= nums[start]", f"Try shorter: drop {nums[start]}.", "shrink")
                total -= nums[start]
                start += 1
        return frames

    def frames_lc1004(nums: list[int], k: int) -> list[dict]:
        code, frames = CODE_ONES, []
        start, zeros, best = 0, 0, 0

        def snap(end, snippet, note, event):
            frames.append(dict(arr=nums, start=start, end=end, line=line_of(code, snippet), note=note, event=event,
                               state={"zeros in window": zeros, "k": k, "best": best}))

        for end, v in enumerate(nums):
            if v == 0:
                zeros += 1
            snap(end, "zeros += 1" if v == 0 else "if v == 0", f"Grow: take {v}. zeros = {zeros}.", "grow")
            while zeros > k:
                snap(end, "zeros -= 1" if nums[start] == 0 else "start += 1", f"{zeros} zeros > k = {k}: invalid. Drop {nums[start]} at {start}.", "shrink")
                if nums[start] == 0:
                    zeros -= 1
                start += 1
            best = max(best, end - start + 1)
            snap(end, "best = max", f"Valid: record length {end - start + 1}. best = {best}.", "record")
        return frames

    def frames_lc713(nums: list[int], k: int) -> list[dict]:
        code, frames = CODE_COUNTING, []
        start, product, count = 0, 1, 0

        def snap(end, snippet, note, event):
            frames.append(dict(arr=nums, start=start, end=end, line=line_of(code, snippet), note=note, event=event,
                               state={"product": product, "k": k, "count": count}))

        if k <= 1:
            frames.append(dict(arr=nums, start=0, end=-1, line=line_of(code, "return 0"), note="k ≤ 1: no product of positive numbers is below it.", event="record",
                               state={"count": 0}))
            return frames
        for end, v in enumerate(nums):
            product *= v
            snap(end, "product *= v", f"Grow: product = {product}.", "grow")
            while product >= k:
                snap(end, "product //= nums[start]", f"{product} ≥ {k}: invalid. Drop {nums[start]}.", "shrink")
                product //= nums[start]
                start += 1
            count += end - start + 1
            snap(end, "count += end - start + 1", f"Every window ending at {end} and starting anywhere in [{start}, {end}] is valid: + {end - start + 1}. count = {count}.", "record")
        return frames

    def frames_lc76(s: str, t: str) -> list[dict]:
        code, frames = CODE_NEED_HAVE, []
        need = {}
        for c in t:
            need[c] = need.get(c, 0) + 1
        missing, start, best = len(t), 0, (float("inf"), 0, 0)

        def snap(end, snippet, note, event):
            shown = {c: need[c] for c in sorted(need) if c in t or need[c] < 0}
            best_text = "—" if best[0] == float("inf") else s[best[1]:best[2] + 1]
            frames.append(dict(arr=list(s), start=start, end=end, line=line_of(code, snippet), note=note, event=event,
                               state={"missing": missing, "need": shown, "best": best_text}))

        for end, ch in enumerate(s):
            useful = need.get(ch, 0) > 0
            if useful:
                missing -= 1
            need[ch] = need.get(ch, 0) - 1
            snap(end, "missing -= 1" if useful else "need[ch] -= 1",
                 f"Grow: take '{ch}'. " + (f"It was still needed, so missing = {missing}." if useful else "Not needed (or surplus): missing stays."), "grow")
            while missing == 0:
                if end - start + 1 < best[0]:
                    best = (end - start + 1, start, end)
                snap(end, "best = (end - start + 1", f"missing = 0: the window covers t. Record '{s[start:end + 1]}' if it's the shortest so far.", "record")
                need[s[start]] += 1
                if need[s[start]] > 0:
                    missing += 1
                snap(end, "need[s[start]] += 1", f"Shrink: drop '{s[start]}'." + (" It was needed, so missing = 1 again." if missing else " It was surplus, so the window stays valid."), "shrink")
                start += 1
        return frames

    return frames_lc1004, frames_lc209, frames_lc3, frames_lc713, frames_lc76


@app.cell
def _(WINDOW_PROBLEMS, mo):
    window_pick = mo.ui.dropdown(options=list(WINDOW_PROBLEMS), value="LC 3 · longest substring without repeats (longest)", label="Problem")
    window_pick
    return (window_pick,)


@app.cell
def _(WINDOW_PROBLEMS, mo, window_pick):
    _key, _code, _default, _param, _param_name = WINDOW_PROBLEMS[window_pick.value]
    window_input = mo.ui.text(value=_default, label="s" if _key in ("lc3", "lc76") else "nums", full_width=True)
    window_param = mo.ui.text(value=_param, label=_param_name or "")
    mo.hstack([window_input, window_param], widths=[3, 1]) if _param_name else window_input
    return window_input, window_param


@app.cell
def _(
    WINDOW_PROBLEMS,
    frames_lc1004,
    frames_lc209,
    frames_lc3,
    frames_lc713,
    frames_lc76,
    mo,
    parse_ints,
    parse_text,
    window_input,
    window_param,
    window_pick,
):
    window_key, window_code = WINDOW_PROBLEMS[window_pick.value][:2]
    try:
        if window_key == "lc3":
            window_frames = frames_lc3(parse_text(window_input.value, low=1, high=16))
        elif window_key == "lc76":
            window_frames = frames_lc76(parse_text(window_input.value, low=1, high=16), parse_text(window_param.value, low=1, high=6))
        else:
            _nums = parse_ints(window_input.value, low=1, high=16)
            _p = int(window_param.value)
            if window_key == "lc209":
                if min(_nums) < 0:
                    raise ValueError("This shape needs non-negative values (section 6 shows why).")
                window_frames = frames_lc209(_nums, _p)
            elif window_key == "lc1004":
                if any(v not in (0, 1) for v in _nums):
                    raise ValueError("LC 1004 takes only 0s and 1s.")
                window_frames = frames_lc1004(_nums, _p)
            else:
                if min(_nums) < 1:
                    raise ValueError("LC 713 takes positive integers.")
                window_frames = frames_lc713(_nums, _p)
        _err = None
    except ValueError as _e:
        window_frames, _err = [], str(_e)
    mo.stop(_err is not None, mo.callout(_err or "", kind="warn"))
    mo.stop(not window_frames, mo.callout("Nothing to step through for this input.", kind="warn"))
    window_step = mo.ui.slider(0, max(len(window_frames) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    window_step
    return window_code, window_frames, window_step


@app.cell
def _(
    array_view,
    badge,
    code_view,
    kv_view,
    mo,
    staircase_view,
    window_code,
    window_frames,
    window_step,
):
    _k = min(window_step.value, len(window_frames) - 1)
    _f = window_frames[_k]
    _tone = {"grow": "teal", "shrink": "amber", "record": "indigo"}[_f["event"]]
    _valid = _f["start"] <= _f["end"]
    _chart = staircase_view(
        {"start": [f["start"] for f in window_frames], "end": [f["end"] for f in window_frames]},
        top=len(_f["arr"]), current=_k,
    )
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack([
                        array_view(_f["arr"], pointers={"start": _f["start"], "end": _f["end"]} if _valid else {}, window=(_f["start"], _f["end"]) if _valid else None, cell_px=36 if len(_f["arr"]) > 10 else 44),
                        kv_view(_f["state"]),
                    ], align="center"),
                    code_view(window_code, active=_f["line"]),
                ],
                wrap=True, align="start",
            ),
            mo.hstack([badge(_f["event"], _tone), mo.md(f"**Step {_k + 1} of {len(window_frames)}.** {_f['note']}")], justify="start", align="center"),
            mo.hstack([_chart, mo.md(
                "**The amortised proof, drawn.** `start` and `end` only ever increase and neither passes n, so across the whole run there are at most "
                "n extensions and n contractions: **2n pointer moves**, each O(1). The inner `while` borrows from a budget that was already paid for. "
                "Both staircases never step down; the gap between them is the window."
            )], widths=[1, 1], align="center", wrap=True),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Brute force → bottleneck → window

    On LC 3, narrate the journey:

    - **Brute force (pseudo code).** For every start, extend to every end, keep a set, stop at the first repeat. That's O(n²) steps; with an O(n) validity check inside, O(n³).
    - **Bottleneck.** When `start` moves forward by one, you rebuild almost exactly the window you just had.
    - **Window.** Keep the state and repair it: grow `end`, shrink `start` only while invalid. 2n pointer moves: O(n).

    Measured on random strings over a 4-letter alphabet:
    """)
    return


@app.cell
def _(mo, random):
    def _brute_steps(s):
        steps, best = 0, 0
        for i in range(len(s)):
            seen = set()
            for j in range(i, len(s)):
                steps += 1
                if s[j] in seen:
                    break
                seen.add(s[j])
                best = max(best, j - i + 1)
        return steps, best

    def _brute_steps_with_check(s):
        steps = 0
        for i in range(len(s)):
            for j in range(i, len(s)):
                steps += j - i + 1  # re-check the whole window each time
        return steps

    def _window_moves(s):
        seen, start, moves, best = set(), 0, 0, 0
        for end, ch in enumerate(s):
            moves += 1
            while ch in seen:
                seen.remove(s[start])
                start += 1
                moves += 1
            seen.add(ch)
            best = max(best, end - start + 1)
        return moves, best

    _rng = random.Random(3)
    _rows = []
    for _n in (10, 100, 1000):
        _s = "".join(_rng.choice("abcd") for _ in range(_n))
        (_b, _best_b), (_w, _best_w) = _brute_steps(_s), _window_moves(_s)
        assert _best_b == _best_w
        _rows.append(f"| {_n:,} | {_brute_steps_with_check(_s):,} | {_b:,} | {_w:,} |")
    mo.md(
        "| n | every window, re-checked | every start, extend until a repeat | window moves |\n| :--- | :--- | :--- | :--- |\n" + "\n".join(_rows)
        + "\n\nThe middle column only looks linear because a 4-letter alphabet forces an early repeat; with long unique runs it's n²/2. The window never exceeds 2n."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · Counting windows, and the *exactly k* trick

    *How many subarrays have **exactly** k distinct values?* A direct window doesn't work: "exactly k" isn't monotone (dropping an element can move you from 3 distinct to 2, or leave you at 3). The standard move:

    > **exactly(k) = at_most(k) − at_most(k − 1)**

    and `at_most` is a clean counting window: every window ending at `end` and starting at or after `start` is valid, so `count += end - start + 1`. Check it against an exhaustive count:
    """)
    return


@app.cell
def _(mo):
    exact_values = mo.ui.text(value="1, 2, 1, 2, 3", label="nums", full_width=True)
    exact_k = mo.ui.number(start=1, stop=10, value=2, label="k")
    mo.hstack([exact_values, exact_k], widths=[3, 1])
    return exact_k, exact_values


@app.cell
def _():
    def at_most_k_distinct(nums: list[int], k: int) -> int:
        if k < 0:
            return 0
        count, start, total = {}, 0, 0
        for end, v in enumerate(nums):
            count[v] = count.get(v, 0) + 1
            while len(count) > k:
                count[nums[start]] -= 1
                if count[nums[start]] == 0:
                    del count[nums[start]]
                start += 1
            total += end - start + 1
        return total

    def exactly_k_brute(nums: list[int], k: int) -> int:
        return sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if len(set(nums[i:j + 1])) == k)

    return at_most_k_distinct, exactly_k_brute


@app.cell
def _(
    at_most_k_distinct,
    exact_k,
    exact_values,
    exactly_k_brute,
    mo,
    parse_ints,
):
    try:
        _nums = parse_ints(exact_values.value, low=1, high=16)
        _k = int(exact_k.value)
        _a, _b = at_most_k_distinct(_nums, _k), at_most_k_distinct(_nums, _k - 1)
        _brute = exactly_k_brute(_nums, _k)
        _out = mo.md(
            f"at_most({_k}) = **{_a}**, at_most({_k - 1}) = **{_b}**, so exactly({_k}) = {_a} − {_b} = **{_a - _b}**. "
            f"Exhaustive count over all {len(_nums) * (len(_nums) + 1) // 2} subarrays: **{_brute}**. "
            + ("✓ they agree." if _a - _b == _brute else "✗ they disagree!")
            + " The same trick powers LC 992, 930 and 1248."
        )
    except ValueError as _e:
        _out = mo.callout(str(_e), kind="warn")
    _out
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · `if` vs `while` in the shrink step, settled by experiment

    "Always use `while` to shrink" is safe advice, but the real answer is more interesting. Run the experiment: each variant is compared against a brute-force oracle on random inputs.
    """)
    return


@app.cell
def _(mo):
    experiment_run = mo.ui.run_button(label="Run 3,000 random cases per variant")
    experiment_run
    return (experiment_run,)


@app.cell
def _(random):
    def longest_at_most_k(s, k, use_while=True):
        count, start, best = {}, 0, 0
        for end, ch in enumerate(s):
            count[ch] = count.get(ch, 0) + 1
            if use_while:
                while len(count) > k:
                    count[s[start]] -= 1
                    if count[s[start]] == 0:
                        del count[s[start]]
                    start += 1
            elif len(count) > k:
                count[s[start]] -= 1
                if count[s[start]] == 0:
                    del count[s[start]]
                start += 1
            best = max(best, end - start + 1)
        return best

    def shortest_at_least(nums, target, use_while=True):
        start, total, best = 0, 0, float("inf")
        for end, v in enumerate(nums):
            total += v
            if use_while:
                while total >= target:
                    best = min(best, end - start + 1)
                    total -= nums[start]
                    start += 1
            elif total >= target:
                best = min(best, end - start + 1)
                total -= nums[start]
                start += 1
        return 0 if best == float("inf") else best

    def count_at_most_k(s, k, use_while=True):
        count, start, total = {}, 0, 0
        for end, ch in enumerate(s):
            count[ch] = count.get(ch, 0) + 1
            if use_while:
                while len(count) > k:
                    count[s[start]] -= 1
                    if count[s[start]] == 0:
                        del count[s[start]]
                    start += 1
            elif len(count) > k:
                count[s[start]] -= 1
                if count[s[start]] == 0:
                    del count[s[start]]
                start += 1
            total += end - start + 1
        return total

    def run_if_while_experiment(trials: int = 3000, seed: int = 11) -> list[tuple[str, int, int]]:
        rng = random.Random(seed)
        rows = []
        for name, variant, oracle, make in (
            ("longest · at most k distinct", longest_at_most_k,
             lambda s, k: max((j - i + 1 for i in range(len(s)) for j in range(i, len(s)) if len(set(s[i:j + 1])) <= k), default=0),
             lambda: ("".join(rng.choice("abc") for _ in range(rng.randint(0, 9))), rng.randint(1, 3))),
            ("shortest · sum ≥ target", shortest_at_least,
             lambda a, t: min((j - i + 1 for i in range(len(a)) for j in range(i, len(a)) if sum(a[i:j + 1]) >= t), default=0),
             lambda: ([rng.randint(0, 6) for _ in range(rng.randint(1, 9))], rng.randint(1, 15))),
            ("counting · at most k distinct", count_at_most_k,
             lambda s, k: sum(1 for i in range(len(s)) for j in range(i, len(s)) if len(set(s[i:j + 1])) <= k),
             lambda: ("".join(rng.choice("abc") for _ in range(rng.randint(0, 9))), rng.randint(1, 3))),
        ):
            fails_while = fails_if = 0
            for _ in range(trials):
                a, b = make()
                want = oracle(a, b)
                fails_while += variant(a, b, True) != want
                fails_if += variant(a, b, False) != want
            rows.append((name, fails_while, fails_if))
        return rows

    return run_if_while_experiment, shortest_at_least


@app.cell
def _(experiment_run, mo, run_if_while_experiment):
    mo.stop(not experiment_run.value, mo.md("_Press the button to run the experiment (a second or two)._"))
    _rows = run_if_while_experiment()
    mo.md(
        "| Shape | `while` failures | `if` failures | Verdict |\n| :--- | :--- | :--- | :--- |\n"
        + "\n".join(f"| {n} | {w} / 3000 | {i} / 3000 | {'`if` is fine' if i == 0 else '`while` required'} |" for n, w, i in _rows)
        + "\n\n**Why longest survives `if`:** each step grows the window by one and shrinks it by at most one, so its length is a high-water mark. "
        "The window may be momentarily invalid, but its *length* is still a valid answer found earlier. Shortest and counting read the window's current contents, "
        "so they need it genuinely valid. **Write `while` every time**, and if asked, give this answer."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6 · When it's the wrong tool: negatives break monotonicity

    Every "shrink while valid" argument assumes removing an element can only move you *away* from validity. With a negative ahead, a window you already discarded could have become valid later. Run the plain window on an array with negatives:
    """)
    return


@app.cell
def _(mo, shortest_at_least):
    def shortest_brute(nums, target):
        return min((j - i + 1 for i in range(len(nums)) for j in range(i, len(nums)) if sum(nums[i:j + 1]) >= target), default=0)

    _nums, _target = [-3, 2, -3, 0, 2, -3, -4], 1
    mo.md(
        f"`nums = {_nums}`, `target = {_target}`: the window returns **{shortest_at_least(_nums, _target)}**, "
        f"brute force says **{shortest_brute(_nums, _target)}** (the single element 2 already qualifies).\n\n"
        "| Looks like a window… | LC | Use instead |\n| :--- | :--- | :--- |\n"
        "| count subarrays with sum exactly k (negatives allowed) | 560 | prefix sum + hash map |\n"
        "| shortest subarray with sum ≥ k (negatives allowed) | 862 | prefix sum + monotonic deque |\n"
        "| max value in every window of size k | 239 | window + monotonic deque |\n"
        "| longest subsequence with a property | 300 | DP: a window can't skip |\n"
        "| median of every window of size k | 480 | window + two heaps |\n\n"
        "**Ask about negatives in the interview.** It's one of the highest-signal clarifying questions on this pattern."
    )
    return (shortest_brute,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 7 · Practice: worked → faded → solo

    Anchors first. They must become automatic before anything else on the ladder.
    """)
    return


@app.cell
def _(Case):
    CASES_643 = [
        Case(([1, 12, -5, -6, 50, 3], 4), 12.75),
        Case(([5], 1), 5.0, label="single element"),
        Case(([-1], 1), -1.0),
        Case(([0, 4, 0, 3, 2], 1), 4.0),
        Case(([-5, -5, -5], 2), -5.0, label="negatives: don't record partial windows"),
        Case(([4, 2, 1, 3, 3], 2), 3.0),
    ]
    SOLUTION_643 = '''
    def find_max_average(nums: list[int], k: int) -> float:
        window = sum(nums[:k])
        best = window
        for end in range(k, len(nums)):
            window += nums[end] - nums[end - k]
            best = max(best, window)
        return best / k
    '''
    STUB_643 = '''def find_max_average(nums: list[int], k: int) -> float:
        # Fixed window: pay for the first k once, then add incoming / drop outgoing.
        ...
    '''
    CASES_3 = [
        Case(("abcabcbb",), 3), Case(("bbbbb",), 1), Case(("pwwkew",), 3),
        Case(("",), 0, label="empty string"), Case((" ",), 1, label="a single space"),
        Case(("abba",), 2, label="abba: start must never move back"), Case(("dvdf",), 3),
    ]
    SOLUTION_3 = '''
    def length_of_longest_substring(s: str) -> int:
        count = {}
        start = best = 0
        for end, ch in enumerate(s):
            count[ch] = count.get(ch, 0) + 1
            while count[ch] > 1:
                count[s[start]] -= 1
                start += 1
            best = max(best, end - start + 1)
        return best
    '''
    STUB_3 = '''def length_of_longest_substring(s: str) -> int:
        count = {}
        start = best = 0
        for end, ch in enumerate(s):
            count[ch] = count.get(ch, 0) + 1     # grow
            while ...:                           # when is the window invalid?
                ...                              # drop s[start] from count, then move start
            best = ...                           # record: the window is valid here
        return best
    '''
    CASES_424 = [
        Case(("ABAB", 2), 4), Case(("AABABBA", 1), 4), Case(("A", 0), 1), Case(("AAAA", 0), 4),
        Case(("ABCDE", 1), 2), Case(("ABBB", 2), 4), Case(("BAAAB", 2), 5), Case(("AABA", 0), 2),
    ]
    SOLUTION_424 = '''
    def character_replacement(s: str, k: int) -> int:
        count = {}
        start = best = max_count = 0
        for end, ch in enumerate(s):
            count[ch] = count.get(ch, 0) + 1
            max_count = max(max_count, count[ch])
            while (end - start + 1) - max_count > k:   # more than k letters to replace
                count[s[start]] -= 1
                start += 1
            best = max(best, end - start + 1)
        return best
    '''
    STUB_424 = '''def character_replacement(s: str, k: int) -> int:
        # Longest shape. Validity: window length - count of its most common letter <= k.
        ...
    '''
    return (
        CASES_3,
        CASES_424,
        CASES_643,
        SOLUTION_3,
        SOLUTION_424,
        SOLUTION_643,
        STUB_3,
        STUB_424,
        STUB_643,
    )


@app.cell
def _(SOLUTION_643, STUB_643, mo, solution):
    ex643_editor = mo.ui.code_editor(value=STUB_643, language="python", min_height=170)
    ex643_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Worked: LC 643 Maximum Average Subarray I\n\nThe fixed shape. Talk through it while stepping the fixed-window visual in section 2, then write it without looking. Return the maximum **average** of any window of size k."),
        solution(SOLUTION_643, "Show the worked solution"),
        ex643_editor, ex643_run,
    ])
    return ex643_editor, ex643_run


@app.cell
def _(CASES_643, check, ex643_editor, ex643_run, mo):
    mo.stop(not ex643_run.value, mo.md("_Write your solution above, then press **Run tests**._"))
    check(ex643_editor.value, "find_max_average", CASES_643, normalise=lambda x: round(x, 6) if isinstance(x, (int, float)) else x)
    return


@app.cell
def _(SOLUTION_3, STUB_3, mo, solution):
    ex3_editor = mo.ui.code_editor(value=STUB_3, language="python", min_height=230)
    ex3_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Faded: LC 3 Longest Substring Without Repeating Characters\n\nThe longest shape with the template visible. Fill in the three blanks, then do it once more tomorrow with the template hidden."),
        ex3_editor, ex3_run, solution(SOLUTION_3),
    ])
    return ex3_editor, ex3_run


@app.cell
def _(CASES_3, check, ex3_editor, ex3_run, mo):
    mo.stop(not ex3_run.value, mo.md("_Fill in the blanks, then press **Run tests**._"))
    check(ex3_editor.value, "length_of_longest_substring", CASES_3)
    return


@app.cell
def _(SOLUTION_424, STUB_424, mo, solution):
    ex424_editor = mo.ui.code_editor(value=STUB_424, language="python", min_height=200)
    ex424_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md(
            "### Solo: LC 424 Longest Repeating Character Replacement\n\n"
            "You may replace at most k characters; return the length of the longest substring of one repeated letter you can make. "
            "From scratch, no notes: this is the solo still open from your last session. "
            "Before typing, say: shape, state, validity test, where you record."
        ),
        ex424_editor, ex424_run, solution(SOLUTION_424),
    ])
    return ex424_editor, ex424_run


@app.cell
def _(CASES_424, check, ex424_editor, ex424_run, mo):
    mo.stop(not ex424_run.value, mo.md("_Write it from scratch, then press **Run tests**._"))
    check(ex424_editor.value, "character_replacement", CASES_424)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Graded ladder:** 209 Minimum Size Subarray Sum (return 0!) · 438 Find All Anagrams · 567 Permutation in String · 1004 Max Consecutive Ones III · 904 Fruit Into Baskets. **Stretch:** 76 Minimum Window Substring · 239 Sliding Window Maximum · 992 Subarrays with K Different Integers · 862 Shortest Subarray with Sum at Least K.
    """)
    return


@app.cell
def _():
    BUGS = [
        ("1 · Fixed window never drops the outgoing element", "The window silently becomes a prefix sum and grows forever.",
         "def f(nums, k):\n    window = sum(nums[:k])\n    best = window\n    for end in range(k, len(nums)):\n        window += nums[end]\n        best = max(best, window)\n    return best\n",
         "def f(nums, k):\n    window = sum(nums[:k])\n    best = window\n    for end in range(k, len(nums)):\n        window += nums[end] - nums[end - k]\n        best = max(best, window)\n    return best\n",
         ([2, 1, 5, 1, 3, 2], 3)),
        ("2 · Recording before the window reaches size k", "Partial windows get counted. Invisible on non-negative input, wrong with negatives.",
         "def f(nums, k):\n    window, best = 0, float('-inf')\n    for end in range(len(nums)):\n        window += nums[end]\n        if end >= k:\n            window -= nums[end - k]\n        best = max(best, window)\n    return best\n",
         "def f(nums, k):\n    window, best = 0, float('-inf')\n    for end in range(len(nums)):\n        window += nums[end]\n        if end >= k:\n            window -= nums[end - k]\n        if end >= k - 1:\n            best = max(best, window)\n    return best\n",
         ([-5, -5, -5], 2)),
        ("3 · Longest: recording before shrinking", "It measures a window that still holds the repeat. The most common window bug.",
         "def f(s):\n    count, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        count[ch] = count.get(ch, 0) + 1\n        best = max(best, end - start + 1)\n        while count[ch] > 1:\n            count[s[start]] -= 1\n            start += 1\n    return best\n",
         "def f(s):\n    count, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        count[ch] = count.get(ch, 0) + 1\n        while count[ch] > 1:\n            count[s[start]] -= 1\n            start += 1\n        best = max(best, end - start + 1)\n    return best\n",
         ("abcabcbb",)),
        ("4 · Leaving zero-count keys in the state dict", "len(count) is the validity test; a stale key keeps it above k and the shrink loop runs off the end.",
         "def f(s, k):\n    count, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        count[ch] = count.get(ch, 0) + 1\n        while len(count) > k:\n            count[s[start]] -= 1\n            start += 1\n        best = max(best, end - start + 1)\n    return best\n",
         "def f(s, k):\n    count, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        count[ch] = count.get(ch, 0) + 1\n        while len(count) > k:\n            count[s[start]] -= 1\n            if count[s[start]] == 0:\n                del count[s[start]]\n            start += 1\n        best = max(best, end - start + 1)\n    return best\n",
         ("aabbcc", 2)),
        ("5 · Jumping start to last_seen + 1 without max()", "start moves backwards and the window re-swallows a repeat.",
         "def f(s):\n    last, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        if ch in last:\n            start = last[ch] + 1\n        last[ch] = end\n        best = max(best, end - start + 1)\n    return best\n",
         "def f(s):\n    last, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        if ch in last:\n            start = max(start, last[ch] + 1)\n        last[ch] = end\n        best = max(best, end - start + 1)\n    return best\n",
         ("abba",)),
        ("6 · Shortest: recording after the shrink loop", "The loop exits exactly when the window stopped qualifying, so you measure an invalid window.",
         "def f(target, nums):\n    start = total = 0\n    best = float('inf')\n    for end, v in enumerate(nums):\n        total += v\n        while total >= target:\n            total -= nums[start]\n            start += 1\n        best = min(best, end - start + 1)\n    return 0 if best == float('inf') else best\n",
         "def f(target, nums):\n    start = total = 0\n    best = float('inf')\n    for end, v in enumerate(nums):\n        total += v\n        while total >= target:\n            best = min(best, end - start + 1)\n            total -= nums[start]\n            start += 1\n    return 0 if best == float('inf') else best\n",
         (7, [2, 3, 1, 2, 4, 3])),
        ("7 · Window length written as end - start", "Both indices are inclusive. Sanity check: start == end must give length 1.",
         "def f(s):\n    count, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        count[ch] = count.get(ch, 0) + 1\n        while count[ch] > 1:\n            count[s[start]] -= 1\n            start += 1\n        best = max(best, end - start)\n    return best\n",
         "def f(s):\n    count, start, best = {}, 0, 0\n    for end, ch in enumerate(s):\n        count[ch] = count.get(ch, 0) + 1\n        while count[ch] > 1:\n            count[s[start]] -= 1\n            start += 1\n        best = max(best, end - start + 1)\n    return best\n",
         ("abcabcbb",)),
        ("8 · Using a window when values can be negative", "Extending can lower the sum, so shrinking is no longer safe. Use prefix sums (+ deque).",
         "def f(target, nums):\n    start = total = 0\n    best = float('inf')\n    for end, v in enumerate(nums):\n        total += v\n        while total >= target:\n            best = min(best, end - start + 1)\n            total -= nums[start]\n            start += 1\n    return 0 if best == float('inf') else best\n",
         "def f(target, nums):\n    n = len(nums)\n    best = min((j - i + 1 for i in range(n) for j in range(i, n) if sum(nums[i:j + 1]) >= target), default=0)\n    return best\n",
         (1, [-3, 2, -3, 0, 2, -3, -4])),
    ]

    def run_snippet(code: str, args: tuple) -> str:
        import copy as _copy

        _ns: dict = {}
        exec(code, _ns)
        try:
            return repr(_ns["f"](*_copy.deepcopy(args)))
        except Exception as _exc:
            return f"{type(_exc).__name__}: {_exc}"

    return BUGS, run_snippet


@app.cell
def _(BUGS, mo, run_snippet):
    _lines = ["| Bug | Input | Buggy output | Correct output |", "| :--- | :--- | :--- | :--- |"]
    _details = {}
    for _title, _why, _buggy, _correct, _args in BUGS:
        _lines.append(f"| {_title} | `{', '.join(repr(a) for a in _args)}` | `{run_snippet(_buggy, _args)}` | `{run_snippet(_correct, _args)}` |")
        _details[_title] = mo.md(f"{_why}\n\n```python\n{_buggy}```")
    mo.vstack([
        mo.md("## 8 · Traps: eight ways it breaks\n\nEvery output below is produced live by running the buggy code beside the correct one. Read the bug, predict the failure, then open it."),
        mo.md("\n".join(_lines)),
        mo.accordion(_details),
        mo.md(
            "**Also:** `list.pop(0)` is O(n) (use `collections.deque`), never slice the window (`s[l:r+1]`) inside the loop, and return `0` / `\"\"` when nothing qualifies. "
            "The state must support O(1) add, remove and validity check."
        ),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 9 · Recall: close everything and answer from memory
    """)
    return


@app.cell
def _(mo):
    mo.accordion({
        "1. Which three signals must all be present for a sliding window?": mo.md("Contiguous (subarray / substring); a constraint checkable in O(1) from running state; an optimise-or-count question (longest, shortest, how many, fixed k)."),
        "2. What makes the window legal, and what breaks it?": mo.md("Monotone validity: shrinking can only move you away from an *at least* target, and growing can only break an *at most* constraint. Negative values (with sums) break it, so use prefix sums."),
        "3. Where does the longest shape record, and where does the shortest?": mo.md("Longest: **after** the shrink loop, where the window is guaranteed valid. Shortest: **inside** the shrink loop, before each shrink, while it's still valid."),
        "4. Why is a `while` inside a `for` still O(n)?": mo.md("`start` and `end` only increase and never pass n: at most n extensions + n contractions = 2n moves, each O(1)."),
        "5. How do you count subarrays with exactly k distinct values?": mo.md("`at_most(k) - at_most(k - 1)`, where at_most is a counting window: `count += end - start + 1`."),
        "6. In LC 76, what does `missing` count and when does it change?": mo.md("Unfilled character slots of t. Decrement only when `need[ch] > 0` before the decrement (surplus doesn't count); increment when a shrink makes `need[c] > 0` again. Valid ⇔ `missing == 0`."),
        "7. When is `if` instead of `while` still correct?": mo.md("Only for the longest shape: the window length is a high-water mark. Shortest and counting need `while`."),
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 10 · Go deeper

    - **Lab in this folder:** [Sliding Window Workbench](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/03-sliding-window/sliding-window-workbench.html)
    - [Hello Interview: Fixed Length](https://www.hellointerview.com/learn/code/sliding-window/fixed-length) and [Variable Length](https://www.hellointerview.com/learn/code/sliding-window/variable-length) windows
    - [USACO Guide: Sliding Window](https://usaco.guide/gold/sliding-window): the deque method for window max
    - [Python docs: collections](https://docs.python.org/3/library/collections.html): `Counter`, `defaultdict`, `deque`

    **Next:** [pointers vs window](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/notebooks/pointers_vs_window.html), then prefix sums, the tool for when negatives break the window.
    """)
    return


@app.cell
def _(
    BUGS,
    CASES_3,
    CASES_424,
    CASES_643,
    SOLUTION_3,
    SOLUTION_424,
    SOLUTION_643,
    STUB_3,
    STUB_424,
    STUB_643,
    assert_cases,
    at_most_k_distinct,
    exactly_k_brute,
    fixed_frames,
    frames_lc1004,
    frames_lc209,
    frames_lc3,
    frames_lc713,
    frames_lc76,
    random,
    run_cases,
    run_if_while_experiment,
    run_snippet,
    shortest_brute,
):
    def test_answer_keys_pass():
        close = lambda x: round(x, 6) if isinstance(x, (int, float)) else x  # noqa: E731
        assert_cases(SOLUTION_643, "find_max_average", CASES_643, normalise=close)
        assert_cases(SOLUTION_3, "length_of_longest_substring", CASES_3)
        assert_cases(SOLUTION_424, "character_replacement", CASES_424)

    def test_stubs_do_not_pass_yet():
        for stub, name, cases in ((STUB_643, "find_max_average", CASES_643), (STUB_3, "length_of_longest_substring", CASES_3),
                                  (STUB_424, "character_replacement", CASES_424)):
            assert not all(r.passed for r in run_cases(stub, name, cases))

    def test_424_expectations_match_brute_force():
        def brute(s, k):
            return max((j - i + 1 for i in range(len(s)) for j in range(i, len(s))
                        if (j - i + 1) - max(s[i:j + 1].count(c) for c in set(s[i:j + 1])) <= k), default=0)
        for case in CASES_424:
            assert brute(*case.args) == case.expected, case

    def test_frames_agree_with_brute_force():
        rng = random.Random(5)
        for _ in range(300):
            s = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 12)))
            longest = max(j - i + 1 for i in range(len(s)) for j in range(i, len(s)) if len(set(s[i:j + 1])) == j - i + 1)
            assert max(f["state"]["best"] for f in frames_lc3(s)) == longest
            nums = [rng.randint(0, 6) for _ in range(rng.randint(1, 12))]
            target = rng.randint(1, 20)
            frames = frames_lc209(nums, target)
            got = min([f["state"]["best"] for f in frames if f["state"]["best"] != "∞"], default=0)
            assert got == shortest_brute(nums, target)
            bits, k = [rng.randint(0, 1) for _ in range(rng.randint(1, 12))], rng.randint(0, 3)
            ones = max(j - i + 1 for i in range(len(bits)) for j in range(i, len(bits)) if bits[i:j + 1].count(0) <= k) if any(bits) or k else 0
            assert max(f["state"]["best"] for f in frames_lc1004(bits, k)) == ones
            positives, kk = [rng.randint(1, 9) for _ in range(rng.randint(1, 10))], rng.randint(1, 60)
            product_brute = 0
            for i in range(len(positives)):
                p = 1
                for j in range(i, len(positives)):
                    p *= positives[j]
                    product_brute += p < kk
            assert frames_lc713(positives, kk)[-1]["state"]["count"] == product_brute
            fixed_nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 10))]
            kf = rng.randint(1, len(fixed_nums))
            assert fixed_frames(fixed_nums, kf)[-1]["best"] == max(sum(fixed_nums[i:i + kf]) for i in range(len(fixed_nums) - kf + 1))

    def test_need_have_frames_find_the_minimum_window():
        rng = random.Random(6)
        for _ in range(200):
            s = "".join(rng.choice("ABC") for _ in range(rng.randint(1, 12)))
            t = "".join(rng.choice("ABC") for _ in range(rng.randint(1, 3)))
            covers = [s[i:j + 1] for i in range(len(s)) for j in range(i, len(s)) if all(s[i:j + 1].count(c) >= t.count(c) for c in set(t))]
            want = min((len(w) for w in covers), default=0)
            best = frames_lc76(s, t)[-1]["state"]["best"] if frames_lc76(s, t) else "—"
            assert (0 if best == "—" else len(best)) == want

    def test_exactly_k_trick_matches_brute_force():
        rng = random.Random(7)
        for _ in range(300):
            nums, k = [rng.randint(1, 4) for _ in range(rng.randint(1, 10))], rng.randint(1, 4)
            assert at_most_k_distinct(nums, k) - at_most_k_distinct(nums, k - 1) == exactly_k_brute(nums, k)

    def test_if_while_claims_hold():
        rows = {name: (w, i) for name, w, i in run_if_while_experiment(trials=600, seed=3)}
        assert all(w == 0 for w, _ in rows.values())
        assert rows["longest · at most k distinct"][1] == 0
        assert rows["shortest · sum ≥ target"][1] > 0 and rows["counting · at most k distinct"][1] > 0

    def test_every_gallery_bug_really_fails():
        for title, _why, buggy, correct, args in BUGS:
            assert run_snippet(buggy, args) != run_snippet(correct, args), title

    return


if __name__ == "__main__":
    app.run()

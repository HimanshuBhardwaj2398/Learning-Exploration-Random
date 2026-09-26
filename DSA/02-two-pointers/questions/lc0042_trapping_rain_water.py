import marimo

__generated_with = "0.25.0"
app = marimo.App(
    width="medium",
    app_title="LC 42 Trapping Rain Water · question",
)


@app.cell
def _():
    import random
    import textwrap

    import marimo as mo

    from learnkit import Case, assert_cases, bars_view, check, code_view, kv_view, line_of, parse_ints, run_cases, solution

    return (
        Case,
        assert_cases,
        bars_view,
        check,
        code_view,
        kv_view,
        line_of,
        mo,
        parse_ints,
        random,
        run_cases,
        solution,
        textwrap,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # LC 42 · Trapping Rain Water

    **Question · two pointers (stretch anchor) · Hard.** Given `n` non-negative bar heights of width 1, how much water is trapped after it rains?

    ```text
    height = [0,1,0,2,1,0,1,3,2,1,2,1]   →   6
    height = [4,2,0,3,2,5]               →   9
    ```

    **The path through this notebook** is the one to narrate in an interview: first principles → brute force → the bottleneck → prefix maxima → two pointers → edge cases → your turn.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Clarify, and list the edge cases before any code

    - Heights are non-negative integers; n can be 0. Constraints: n ≤ 2·10⁴, so O(n²) = 4·10⁸ is too slow. **Aim for O(n).**
    - Edge cases to say out loud: **empty**, **one or two bars** (nothing can be trapped), **strictly increasing or decreasing** (water runs off), **all equal**, a **plateau**, a single deep **pit** like `[5, 0, 5]`.

    ## 2 · First principles: water above one bar

    Water above bar i is limited by the **shorter** of the tallest wall on its left and the tallest wall on its right:

    > water[i] = min(max_left(i), max_right(i)) − height[i]   (never negative, because max_left(i) includes height[i])

    Pick any bar to see its two walls:
    """)
    return


@app.cell
def _(mo):
    heights_text = mo.ui.text(value="0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1", label="height", full_width=True)
    heights_text
    return (heights_text,)


@app.cell
def _(heights_text, mo, parse_ints):
    try:
        heights = [abs(v) for v in parse_ints(heights_text.value, low=1, high=16)]
        _err = None
    except ValueError as _e:
        heights, _err = [0, 1, 0, 2], str(_e)
    mo.stop(_err is not None, mo.callout(_err or "", kind="warn"))

    def water_per_bar(h: list[int]) -> list[int]:
        return [min(max(h[: i + 1]), max(h[i:])) - h[i] for i in range(len(h))]

    bar_pick = mo.ui.slider(0, max(len(heights) - 1, 1), value=min(5, len(heights) - 1), label="bar i", show_value=True, full_width=True)
    bar_pick
    return bar_pick, heights, water_per_bar


@app.cell
def _(bar_pick, bars_view, heights, kv_view, mo):
    _i = min(bar_pick.value, len(heights) - 1)
    _left, _right = max(heights[: _i + 1]), max(heights[_i:])
    _water = min(_left, _right) - heights[_i]
    _l_at = heights.index(_left)
    _r_at = len(heights) - 1 - heights[::-1].index(_right)
    _only = [0] * len(heights)
    _only[_i] = _water
    mo.hstack([
        bars_view(heights, water=_only, marks={**{_l_at: "warn", _r_at: "warn"}, _i: "focus"}, unit=14, bar_px=24),
        kv_view({"height[i]": heights[_i], "max_left(i)": _left, "max_right(i)": _right, "water[i]": f"min({_left}, {_right}) − {heights[_i]} = {_water}"}),
    ], justify="start", align="center", gap=2, wrap=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Brute force → bottleneck → prefix maxima

    **Brute force, pseudo code first.** For each i: scan left for the max, scan right for the max, add `min(l, r) − h[i]`. Two scans per bar: **O(n²) time, O(1) space.**

    ```python
    def trap_brute(height: list[int]) -> int:
        total = 0
        for i in range(len(height)):
            left = max(height[: i + 1])
            right = max(height[i:])
            total += min(left, right) - height[i]
        return total
    ```

    **Bottleneck.** Neighbouring bars recompute almost the same maxima. `max_left(i)` is just `max(max_left(i − 1), height[i])`: a running maximum.

    **Prefix maxima: O(n) time, O(n) space.** Precompute both arrays once, then one pass.

    ```python
    def trap_prefix(height: list[int]) -> int:
        n = len(height)
        if n == 0:
            return 0
        left_max, right_max = [0] * n, [0] * n
        left_max[0], right_max[-1] = height[0], height[-1]
        for i in range(1, n):
            left_max[i] = max(left_max[i - 1], height[i])
        for i in range(n - 2, -1, -1):
            right_max[i] = max(right_max[i + 1], height[i])
        return sum(min(left_max[i], right_max[i]) - height[i] for i in range(n))
    ```

    Can we drop the two arrays? That's the interview's real question.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · Two pointers: O(n) time, O(1) space

    **The insight.** You don't need the *exact* taller maximum, only to know which side is the binding one. If `left_max < right_max`, there's already a wall on the right taller than `left_max`, so the water at the next left bar is decided by `left_max` alone: its answer is **final**. Process the shorter side first. Mirror image on the right.

    **Invariant:** every bar outside `[left, right]` has its water settled; `left_max` and `right_max` are the tallest walls seen from each side.

    **Order inside each branch matters:** move, **refresh the max, then measure.** Measure first and the total can go negative at a new tallest bar (trap in section 6).
    """)
    return


@app.cell
def _(heights, line_of, mo, textwrap):
    CODE_TRAP = textwrap.dedent('''
    def trap(height: list[int]) -> int:
        if not height:
            return 0
        left, right = 0, len(height) - 1
        left_max, right_max = height[left], height[right]
        water = 0
        while left < right:
            if left_max < right_max:            # left side is the binding constraint
                left += 1
                left_max = max(left_max, height[left])    # refresh BEFORE measuring
                water += left_max - height[left]
            else:
                right -= 1
                right_max = max(right_max, height[right])
                water += right_max - height[right]
        return water
    ''').strip()

    def trap_frames(h: list[int]) -> list[dict]:
        if not h:
            return []
        left, right = 0, len(h) - 1
        left_max, right_max, water = h[left], h[right], 0
        per_bar = [0] * len(h)
        frames = [dict(left=left, right=right, per_bar=list(per_bar), line=line_of(CODE_TRAP, "left_max, right_max ="),
                       note="Start with a pointer at each end; each side remembers its tallest wall.",
                       state={"left_max": left_max, "right_max": right_max, "water": water})]
        while left < right:
            if left_max < right_max:
                left += 1
                left_max = max(left_max, h[left])
                per_bar[left] = left_max - h[left]
                water += per_bar[left]
                frames.append(dict(left=left, right=right, per_bar=list(per_bar), line=line_of(CODE_TRAP, "water += left_max"),
                                   note=f"left_max < right_max, so the left side binds. Bar {left} holds {left_max} − {h[left]} = {per_bar[left]}. Final.",
                                   state={"left_max": left_max, "right_max": right_max, "water": water}))
            else:
                right -= 1
                right_max = max(right_max, h[right])
                per_bar[right] = right_max - h[right]
                water += per_bar[right]
                frames.append(dict(left=left, right=right, per_bar=list(per_bar), line=line_of(CODE_TRAP, "water += right_max"),
                                   note=f"right_max ≤ left_max, so the right side binds. Bar {right} holds {right_max} − {h[right]} = {per_bar[right]}. Final.",
                                   state={"left_max": left_max, "right_max": right_max, "water": water}))
        frames.append(dict(left=left, right=right, per_bar=list(per_bar), line=line_of(CODE_TRAP, "return water"),
                           note=f"The pointers met. Total water = {water}.", state={"left_max": left_max, "right_max": right_max, "water": water}))
        return frames

    trap_seq = trap_frames(heights)
    trap_step = mo.ui.slider(0, max(len(trap_seq) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    trap_step
    return CODE_TRAP, trap_frames, trap_seq, trap_step


@app.cell
def _(
    CODE_TRAP,
    bars_view,
    code_view,
    heights,
    kv_view,
    mo,
    trap_seq,
    trap_step,
):
    _f = trap_seq[min(trap_step.value, len(trap_seq) - 1)]
    mo.vstack([
        mo.hstack([
            mo.vstack([bars_view(heights, water=_f["per_bar"], pointers={"left": _f["left"], "right": _f["right"]}, unit=14, bar_px=24), kv_view(_f["state"])], align="center"),
            code_view(CODE_TRAP, active=_f["line"]),
        ], align="start", gap=2, wrap=True),
        mo.md(f"**Step {min(trap_step.value, len(trap_seq) - 1) + 1} of {len(trap_seq)}.** {_f['note']}"),
    ])
    return


@app.cell
def _(mo, random, trap_frames):
    def _count_brute(h):
        ops = 0
        for i in range(len(h)):
            ops += (i + 1) + (len(h) - i)
        return ops

    _rng = random.Random(42)
    _rows = []
    for _n in (10, 100, 1000):
        _h = [_rng.randint(0, 50) for _ in range(_n)]
        _rows.append(f"| {_n:,} | {_count_brute(_h):,} | {3 * _n:,} | {len(trap_frames(_h)) - 1:,} |")
    mo.md(
        "Work per approach (element reads), measured:\n\n| n | brute force | prefix maxima | two pointers (steps) |\n| :--- | :--- | :--- | :--- |\n"
        + "\n".join(_rows)
        + "\n\nPrefix maxima and two pointers are both O(n); the pointers win on **space**: O(1) instead of two extra arrays."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · Your turn

    From a blank function. Say the invariant and the refresh-then-measure order before you type.
    """)
    return


@app.cell
def _(CODE_TRAP, Case, mo, solution):
    CASES_42 = [
        Case(([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), 6), Case(([4, 2, 0, 3, 2, 5],), 9),
        Case(([],), 0, label="empty"), Case(([5],), 0, label="one bar"), Case(([1, 2],), 0, label="two bars"),
        Case(([3, 3, 3],), 0, label="all equal"), Case(([1, 2, 3, 4],), 0, label="increasing"), Case(([4, 3, 2, 1],), 0, label="decreasing"),
        Case(([5, 0, 5],), 5, label="one deep pit"), Case(([2, 0, 1, 0, 3],), 5), Case(([5, 4, 1, 2],), 1, label="water held by a later bar"),
    ]
    SOLUTION_42 = CODE_TRAP
    STUB_42 = '''def trap(height: list[int]) -> int:
        # Two pointers, O(1) space. Which side is binding? Refresh the max, then measure.
        ...
    '''
    ex42_editor = mo.ui.code_editor(value=STUB_42, language="python", min_height=200)
    ex42_run = mo.ui.run_button(label="Run tests")
    mo.vstack([ex42_editor, ex42_run, solution(SOLUTION_42)])
    return CASES_42, SOLUTION_42, STUB_42, ex42_editor, ex42_run


@app.cell
def _(CASES_42, check, ex42_editor, ex42_run, mo):
    mo.stop(not ex42_run.value, mo.md("_Write it, then press **Run tests**._"))
    check(ex42_editor.value, "trap", CASES_42)
    return


@app.cell
def _(mo, textwrap):
    TRAP_MEASURE_FIRST = textwrap.dedent('''
    def trap(height):
        if not height:
            return 0
        left, right = 0, len(height) - 1
        left_max, right_max = height[left], height[right]
        water = 0
        while left < right:
            if left_max < right_max:
                left += 1
                water += left_max - height[left]       # measured BEFORE refreshing
                left_max = max(left_max, height[left])
            else:
                right -= 1
                water += right_max - height[right]
                right_max = max(right_max, height[right])
        return water
    ''').strip()

    def run_trap(code: str, h: list[int]):
        _ns: dict = {}
        exec(code, _ns)
        return _ns["trap"](list(h))

    _bad_small = run_trap(TRAP_MEASURE_FIRST, [4, 2, 0, 3, 2, 5])
    _bad_example = run_trap(TRAP_MEASURE_FIRST, [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
    mo.md(
        "## 6 · The trap in this question\n\n"
        "Measure **before** refreshing the max and a new tallest bar contributes negative water. "
        f"On `[4, 2, 0, 3, 2, 5]` the buggy order returns **{_bad_small}** instead of **9**; "
        f"on the LeetCode example it returns **{_bad_example}** instead of **6**. Both are computed live from the code below.\n\n"
        f"```python\n{TRAP_MEASURE_FIRST}\n```"
    )
    return TRAP_MEASURE_FIRST, run_trap


@app.cell
def _(mo):
    mo.md(r"""
    ## 7 · Follow-ups your interviewer has loaded

    - **"Solve it with a stack."** A monotonic decreasing stack of indices: when a taller bar arrives, pop and fill the basin between it and the new top, layer by layer. Also O(n) / O(n).
    - **"What about 2D (LC 407)?"** Grow inward from the border with a min-heap: the lowest wall on the boundary is always the binding one. O(mn log(mn)).
    - **"Heights arrive as a stream?"** Two pointers needs both ends; with a stream you keep a stack of open basins.
    - **"Why is it safe to settle the shorter side?"** Because the other side already has a wall at least that tall, so min(left_max, true right max) = left_max.

    ## 8 · Recall

    1. Write the water formula for one bar. 2. Why is the prefix-max version O(n) space, and what lets the pointer version drop it? 3. What's the order inside each branch, and what breaks if you swap it? 4. Name four edge cases that return 0.

    **Back to the topic:** [two pointers notebook](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/notebooks/two_pointers.html) · [topic notes](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/02-two-pointers/index.html)
    """)
    return


@app.cell
def _(
    CASES_42,
    SOLUTION_42,
    STUB_42,
    TRAP_MEASURE_FIRST,
    assert_cases,
    random,
    run_cases,
    run_trap,
    trap_frames,
    water_per_bar,
):
    def test_answer_key_and_stub():
        assert_cases(SOLUTION_42, "trap", CASES_42)
        assert not all(r.passed for r in run_cases(STUB_42, "trap", CASES_42))

    def test_expectations_and_frames_match_brute_force():
        def brute(h):
            return sum(min(max(h[: i + 1]), max(h[i:])) - h[i] for i in range(len(h)))

        for case in CASES_42:
            assert brute(*case.args) == case.expected, case
        rng = random.Random(12)
        for _ in range(500):
            h = [rng.randint(0, 9) for _ in range(rng.randint(1, 15))]
            frames = trap_frames(h)
            assert frames[-1]["state"]["water"] == brute(h) == sum(frames[-1]["per_bar"])
            assert frames[-1]["per_bar"] == water_per_bar(h)

    def test_measure_first_bug_really_fails():
        assert run_trap(TRAP_MEASURE_FIRST, [4, 2, 0, 3, 2, 5]) != 9

    return


if __name__ == "__main__":
    app.run()

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="{{TITLE}} · question")


@app.cell
def _():
    import random
    import textwrap

    import marimo as mo

    from learnkit import Case, array_view, assert_cases, check, code_view, kv_view, line_of, parse_ints, run_cases, solution

    return (
        Case,
        array_view,
        assert_cases,
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
    # {{TITLE}}

    **Question · {{TOPIC}}.** TODO: the problem statement in two or three lines.

    ```text
    TODO example input   →   TODO output
    ```

    The path to narrate: clarify → first principles → brute force → bottleneck → optimal → edge cases → your turn.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Clarify, and list edge cases before any code

    - Constraints: TODO (n up to …, value range, sorted?, duplicates?, negatives?). They name the budget: TODO.
    - Edge cases to say out loud: empty · single element · all equal · TODO

    ## 2 · First principles

    TODO: the smallest true statement the solution rests on (a formula, an invariant, a recurrence).

    ## 3 · Brute force → bottleneck → optimal

    **Brute force, pseudo code first.** TODO. Cost: TODO.

    ```python
    # TODO brute force
    ```

    **Bottleneck.** TODO: which work is repeated or provably wasted?

    **Optimal, pseudo code first.** TODO. Why it's correct: TODO. Cost: TODO.
    """)
    return


@app.cell
def _(line_of, mo, textwrap):
    CODE_OPTIMAL = textwrap.dedent('''
    def solve(nums: list[int]) -> int:
        best = nums[0]
        for x in nums[1:]:
            best = max(best, x)
        return best
    ''').strip()

    def optimal_frames(nums: list[int]) -> list[dict]:
        best, out = nums[0], []
        for i, x in enumerate(nums):
            best = max(best, x)
            out.append(dict(pointers={"i": i}, line=line_of(CODE_OPTIMAL, "best = max"), note=f"TODO: explain step {i}.", state={"best": best}))
        return out

    q_values = mo.ui.text(value="2, 7, 1, 8, 2, 8", label="Input", full_width=True)
    q_values
    return CODE_OPTIMAL, optimal_frames, q_values


@app.cell
def _(mo, optimal_frames, parse_ints, q_values):
    try:
        q_input = parse_ints(q_values.value, low=1, high=14)
        _err = None
    except ValueError as _e:
        q_input, _err = [], str(_e)
    mo.stop(_err is not None, mo.callout(_err or "", kind="warn"))
    q_frames = optimal_frames(q_input)
    q_step = mo.ui.slider(0, max(len(q_frames) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    q_step
    return q_frames, q_input, q_step


@app.cell
def _(
    CODE_OPTIMAL,
    array_view,
    code_view,
    kv_view,
    mo,
    q_frames,
    q_input,
    q_step,
):
    _f = q_frames[min(q_step.value, len(q_frames) - 1)]
    mo.vstack([
        mo.hstack([
            mo.vstack([array_view(q_input, pointers=_f["pointers"]), kv_view(_f["state"])], align="center"),
            code_view(CODE_OPTIMAL, active=_f["line"]),
        ], align="start", gap=2, wrap=True),
        mo.md(_f["note"]),
    ])
    return


@app.cell
def _(CODE_OPTIMAL, Case, mo, solution):
    CASES = [
        Case(([2, 7, 1, 8],), 8),
        Case(([5],), 5, label="single element"),
        Case(([-3, -1],), -1, label="negatives"),
    ]
    STUB = '''def solve(nums: list[int]) -> int:
        # TODO: from a blank function
        ...
    '''
    editor = mo.ui.code_editor(value=STUB, language="python", min_height=180)
    run = mo.ui.run_button(label="Run tests")
    mo.vstack([mo.md("## 4 · Your turn\n\nFrom scratch. Say the invariant and the edge cases before you type."), editor, run, solution(CODE_OPTIMAL)])
    return CASES, STUB, editor, run


@app.cell
def _(CASES, check, editor, mo, run):
    mo.stop(not run.value, mo.md("_Write it, then press **Run tests**._"))
    check(editor.value, "solve", CASES)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · Traps and follow-ups

    - Trap: TODO (the input that breaks the most common wrong version, and what it returns)
    - Follow-up: TODO ("what if the input is streamed?", "can you do it in O(1) space?", …)

    ## 6 · Recall

    1. TODO  2. TODO  3. TODO
    """)
    return


@app.cell
def _(
    CASES,
    CODE_OPTIMAL,
    STUB,
    assert_cases,
    optimal_frames,
    random,
    run_cases,
):
    def test_answer_key_and_stub():
        assert_cases(CODE_OPTIMAL, "solve", CASES)
        assert not all(r.passed for r in run_cases(STUB, "solve", CASES))

    def test_frames_match_brute_force():
        rng = random.Random(0)
        for _ in range(200):
            nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
            assert optimal_frames(nums)[-1]["state"]["best"] == max(nums)

    return


if __name__ == "__main__":
    app.run()

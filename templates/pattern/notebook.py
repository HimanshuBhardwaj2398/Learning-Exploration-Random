import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="{{TITLE}} · {{AREA}}")


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

    **Pattern {{NUMBER}} · {{AREA}}.** TODO: one or two sentences — what this pattern does and the idea that makes it fast.

    Anchor ladder: **TODO → TODO → TODO** · builds on TODO · leads to TODO
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md("**How to use this notebook.** Online it runs in your browser; locally, `marimo edit {{NOTEBOOK_PATH}}`. "
              "Order: **Spot it → See it → Brute force → Template → Practice → Traps → Recall.**"),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Spot it

    | You read… | Shape | Because |
    | :--- | :--- | :--- |
    | TODO wording that points here | TODO | TODO |

    **The discriminator:** TODO — the one question that separates this pattern from its closest neighbour.

    **Constraints name the budget:** TODO (e.g. n ≤ 10⁵ → O(n log n) at most).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · See it

    TODO: say what to watch. The example below steps through a running maximum; replace `CODE` and `frames` with this pattern's algorithm.
    """)
    return


@app.cell
def _(mo):
    see_values = mo.ui.text(value="3, 1, 4, 1, 5, 9, 2, 6", label="Input", full_width=True)
    see_values
    return (see_values,)


@app.cell
def _(line_of, textwrap):
    CODE = textwrap.dedent('''
    def running_max(nums: list[int]) -> int:
        best = nums[0]
        for i in range(1, len(nums)):
            best = max(best, nums[i])
        return best
    ''').strip()

    def frames(nums: list[int]) -> list[dict]:
        """One dict per step: pointers, marks, the code line to highlight, a note, and state."""
        best, out = nums[0], []
        out.append(dict(pointers={"i": 0}, marks={0: "hit"}, line=line_of(CODE, "best = nums[0]"), note="Start with the first value.", state={"best": best}))
        for i in range(1, len(nums)):
            best = max(best, nums[i])
            out.append(dict(pointers={"i": i}, marks={nums.index(best): "hit"}, line=line_of(CODE, "best = max"),
                            note=f"Compare {nums[i]} with the best so far.", state={"best": best}))
        return out

    return CODE, frames


@app.cell
def _(frames, mo, parse_ints, see_values):
    try:
        see_input = parse_ints(see_values.value, low=1, high=14)
        _err = None
    except ValueError as _e:
        see_input, _err = [], str(_e)
    mo.stop(_err is not None, mo.callout(_err or "", kind="warn"))
    see_frames = frames(see_input)
    see_step = mo.ui.slider(0, max(len(see_frames) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    see_step
    return see_frames, see_input, see_step


@app.cell
def _(
    CODE,
    array_view,
    code_view,
    kv_view,
    mo,
    see_frames,
    see_input,
    see_step,
):
    _f = see_frames[min(see_step.value, len(see_frames) - 1)]
    mo.vstack([
        mo.hstack([
            mo.vstack([array_view(see_input, pointers=_f["pointers"], marks=_f["marks"]), kv_view(_f["state"])], align="center"),
            code_view(CODE, active=_f["line"]),
        ], align="start", gap=2, wrap=True),
        mo.md(f"**Step {min(see_step.value, len(see_frames) - 1) + 1} of {len(see_frames)}.** {_f['note']}"),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Brute force → bottleneck → optimal

    **Brute force (pseudo code):** TODO. Cost: TODO.

    **Bottleneck:** TODO — the exact work that gets repeated.

    **Optimal (pseudo code):** TODO. Why it's safe: TODO. Cost: TODO.

    ## 4 · Template

    ```python
    # TODO: the template you should be able to write from memory
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · Practice: worked → faded → solo

    Cap each problem at 25 minutes. To add an exercise, copy the three cells below (data, editor, result) and rename.
    """)
    return


@app.cell
def _(Case):
    CASES_WORKED = [
        Case(([3, 1, 4],), 4),
        Case(([-2, -7],), -2, label="all negative"),
        Case(([5],), 5, label="single element"),
    ]
    SOLUTION_WORKED = '''
    def running_max(nums: list[int]) -> int:
        best = nums[0]
        for x in nums[1:]:
            best = max(best, x)
        return best
    '''
    STUB_WORKED = '''def running_max(nums: list[int]) -> int:
        # TODO: replace with this topic's worked problem
        ...
    '''
    return CASES_WORKED, SOLUTION_WORKED, STUB_WORKED


@app.cell
def _(SOLUTION_WORKED, STUB_WORKED, mo, solution):
    worked_editor = mo.ui.code_editor(value=STUB_WORKED, language="python", min_height=160)
    worked_run = mo.ui.run_button(label="Run tests")
    mo.vstack([mo.md("### Worked: TODO problem\n\nTODO: one-line statement."), solution(SOLUTION_WORKED, "Show the worked solution"), worked_editor, worked_run])
    return worked_editor, worked_run


@app.cell
def _(CASES_WORKED, check, mo, worked_editor, worked_run):
    mo.stop(not worked_run.value, mo.md("_Write your solution above, then press **Run tests**._"))
    check(worked_editor.value, "running_max", CASES_WORKED)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6 · Traps

    | Bug | Input | Wrong output | Right output |
    | :--- | :--- | :--- | :--- |
    | TODO | TODO | TODO | TODO |

    Prefer computing these live (see the two-pointers notebook's bug gallery) so every wrong answer is real.

    ## 7 · Recall: close everything and answer from memory
    """)
    return


@app.cell
def _(mo):
    mo.accordion({
        "1. TODO: what is the invariant?": mo.md("TODO"),
        "2. TODO: when does this pattern NOT apply?": mo.md("TODO"),
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8 · Go deeper

    - TODO: 2–4 resources, each with what to read and what to skip

    **Next:** TODO
    """)
    return


@app.cell
def _(
    CASES_WORKED,
    SOLUTION_WORKED,
    STUB_WORKED,
    assert_cases,
    frames,
    random,
    run_cases,
):
    def test_answer_key_passes():
        assert_cases(SOLUTION_WORKED, "running_max", CASES_WORKED)

    def test_stub_does_not_pass_yet():
        assert not all(r.passed for r in run_cases(STUB_WORKED, "running_max", CASES_WORKED))

    def test_frames_agree_with_brute_force():
        rng = random.Random(0)
        for _ in range(200):
            nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
            assert frames(nums)[-1]["state"]["best"] == max(nums)

    return


if __name__ == "__main__":
    app.run()

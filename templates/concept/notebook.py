import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="{{TITLE}} · {{AREA}}")


@app.cell
def _():
    import contextlib
    import io
    import textwrap

    import marimo as mo

    from learnkit import Case, assert_cases, check, code_view, kv_view, line_of, run_cases, solution

    return (
        Case,
        assert_cases,
        check,
        code_view,
        contextlib,
        io,
        kv_view,
        line_of,
        mo,
        run_cases,
        solution,
        textwrap,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # {{TITLE}}

    **Concept {{NUMBER}} · {{AREA}}.** TODO: why this exists (the problem it solves) and where you already meet it in real code.

    **The one idea:** TODO, in one sentence.
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md("**How to use this notebook.** Online it runs in your browser; locally, `marimo edit {{NOTEBOOK_PATH}}`. "
              "Order: **mental model → prove it live → build it up → pitfalls → practice → recall.**"),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Mental model

    TODO: the picture to hold in your head. Step through the smallest example; each step highlights the line that runs.
    """)
    return


@app.cell
def _(mo, textwrap):
    EXAMPLE = textwrap.dedent('''
    x = [1, 2]
    y = x
    y.append(3)
    print(x)
    ''').strip()
    STEPS = [
        ("x = [1, 2]", "TODO: explain what this line does to names and objects."),
        ("y = x", "TODO"),
        ("y.append(3)", "TODO"),
        ("print(x)", "TODO"),
    ]
    step = mo.ui.slider(0, len(STEPS) - 1, value=0, label="Step", full_width=True, show_value=True)
    step
    return EXAMPLE, STEPS, step


@app.cell
def _(EXAMPLE, STEPS, code_view, line_of, mo, step):
    _snippet, _note = STEPS[step.value]
    mo.hstack([code_view(EXAMPLE, active=line_of(EXAMPLE, _snippet)), mo.md(f"**Step {step.value + 1}.** {_note}")], align="start", gap=2, wrap=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · Prove it, live

    TODO: run the idea and show the evidence (identities, attributes, printed output) computed in this cell.
    """)
    return


@app.cell
def _(EXAMPLE, contextlib, io, kv_view):
    _buffer = io.StringIO()
    with contextlib.redirect_stdout(_buffer):
        exec(EXAMPLE, {})
    kv_view({"printed": _buffer.getvalue().strip()})
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Build it up

    | Need | Pattern |
    | :--- | :--- |
    | TODO | TODO |

    ## 4 · Pitfalls

    | Pitfall | What happens | Fix |
    | :--- | :--- | :--- |
    | TODO | TODO | TODO |

    ## 5 · Practice
    """)
    return


@app.cell
def _(Case, mo, solution):
    CASES = [Case(([1, 2],), [1, 2, 3])]
    SOLUTION = '''
    def extend_copy(items: list[int]) -> list[int]:
        result = list(items)
        result.append(3)
        return result
    '''
    STUB = '''def extend_copy(items: list[int]) -> list[int]:
        # TODO: replace with this concept's exercise
        ...
    '''
    editor = mo.ui.code_editor(value=STUB, language="python", min_height=160)
    run = mo.ui.run_button(label="Run tests")
    mo.vstack([mo.md("### TODO exercise\n\nTODO statement."), editor, run, solution(SOLUTION)])
    return CASES, SOLUTION, STUB, editor, run


@app.cell
def _(CASES, check, editor, mo, run):
    mo.stop(not run.value, mo.md("_Write it, then press **Run tests**._"))
    check(editor.value, "extend_copy", CASES)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6 · Recall

    1. TODO  2. TODO  3. TODO

    ## 7 · Go deeper

    - TODO
    """)
    return


@app.cell
def _(CASES, EXAMPLE, SOLUTION, STEPS, STUB, assert_cases, line_of, run_cases):
    def test_answer_key_and_stub():
        assert_cases(SOLUTION, "extend_copy", CASES)
        assert not all(r.passed for r in run_cases(STUB, "extend_copy", CASES))

    def test_steps_point_at_real_lines():
        for snippet, _note in STEPS:
            line_of(EXAMPLE, snippet)

    return


if __name__ == "__main__":
    app.run()

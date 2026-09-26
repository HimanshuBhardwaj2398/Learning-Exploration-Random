"""Run a learner's code against test cases and report what passed.

Typical notebook use (two cells, because marimo reads a UI element's value in a
different cell from the one that creates it):

    editor = mo.ui.code_editor(value=STUB, language="python")
    run = mo.ui.run_button(label="Run tests")
    mo.vstack([editor, run])

    mo.stop(not run.value, mo.md("_Press **Run tests**._"))
    check(editor.value, "is_palindrome", CASES)

Answer keys are tested the same way from a notebook test cell:

    def test_answer_key():
        assert_cases(SOLUTION, "is_palindrome", CASES)
"""

from __future__ import annotations

import copy
import html as _html
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

DEFAULT_BUDGET = 300_000  # executed lines per test case before we call it an infinite loop


@dataclass(frozen=True)
class Case:
    """One test: call func(*args) and compare with expected.

    inplace: index of an argument that the function mutates; that argument is judged
             instead of the return value (e.g. Move Zeroes returns None).
    """

    args: tuple
    expected: Any
    label: str = ""
    inplace: int | None = None


@dataclass
class Result:
    case: Case
    passed: bool
    got: Any = None
    error: str | None = None
    lines: int = field(default=0, repr=False)


class LineBudgetExceeded(Exception):
    """Raised inside the learner's code when it runs too many lines."""


def _call_with_budget(fn: Callable, args: tuple, budget: int) -> tuple[Any, int]:
    count = 0

    def tracer(frame, event, arg):  # noqa: ARG001 - signature fixed by sys.settrace
        nonlocal count
        if event == "line":
            count += 1
            if count > budget:
                raise LineBudgetExceeded
        return tracer

    previous = sys.gettrace()
    try:
        sys.settrace(tracer)
    except Exception:  # pragma: no cover - platforms without settrace
        return fn(*args), 0
    try:
        return fn(*args), count
    finally:
        sys.settrace(previous)


def run_cases(
    code: str,
    func_name: str,
    cases: Sequence[Case],
    *,
    normalise: Callable[[Any], Any] | None = None,
    budget: int = DEFAULT_BUDGET,
) -> list[Result]:
    """Execute `code`, look up `func_name`, and run every case against it."""
    namespace: dict[str, Any] = {"__name__": "practice"}
    try:
        exec(compile(code, "<your code>", "exec"), namespace)  # noqa: S102 - running the learner's own code
    except Exception as exc:  # SyntaxError, NameError at import time, ...
        return [Result(case, False, error=f"{type(exc).__name__}: {exc}") for case in cases]

    fn = namespace.get(func_name)
    if not callable(fn):
        return [Result(case, False, error=f"no function named {func_name}() was defined") for case in cases]

    norm = normalise or (lambda value: value)
    results = []
    for case in cases:
        args = copy.deepcopy(case.args)
        try:
            got, lines = _call_with_budget(fn, args, budget)
        except LineBudgetExceeded:
            results.append(Result(case, False, error=f"stopped after {budget:,} lines: an infinite loop, or too slow for this input?"))
            continue
        except Exception as exc:
            results.append(Result(case, False, error=f"{type(exc).__name__}: {exc}"))
            continue
        if case.inplace is not None:
            got = args[case.inplace]
        try:
            passed = norm(got) == norm(case.expected)
        except Exception as exc:  # normalise choked on a wrong-shaped answer
            results.append(Result(case, False, got=got, error=f"could not compare: {exc}"))
            continue
        results.append(Result(case, passed, got=got, lines=lines))
    return results


def assert_cases(code: str, func_name: str, cases: Sequence[Case], **kwargs: Any) -> None:
    """For test cells: fail with a readable message if any case fails."""
    failures = [r for r in run_cases(code, func_name, cases, **kwargs) if not r.passed]
    if failures:
        lines = [f"{_label(r.case)}: expected {r.case.expected!r}, got {r.error or repr(r.got)}" for r in failures]
        raise AssertionError(f"{func_name}: {len(failures)} case(s) failed\n" + "\n".join(lines))


def _label(case: Case) -> str:
    if case.label:
        return case.label
    shown = ", ".join(repr(a) for a in case.args)
    return shown if len(shown) <= 70 else shown[:67] + "..."


def _cell(text: str, mono: bool = True) -> str:
    font = "font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;" if mono else ""
    return f'<td style="padding:5px 10px;border-top:1px solid rgba(127,127,127,.25);{font}">{_html.escape(text)}</td>'


def check(code: str, func_name: str, cases: Sequence[Case], **kwargs: Any) -> Any:
    """Run the cases and render a pass/fail table (marimo Html, or a string)."""
    results = run_cases(code, func_name, cases, **kwargs)
    passed = sum(r.passed for r in results)
    total = len(results)
    if passed == total:
        summary = f'<div style="color:#059669;font-weight:600;margin-bottom:6px">✓ All {total} tests pass</div>'
    else:
        summary = (
            f'<div style="color:#dc2626;font-weight:600;margin-bottom:6px">'
            f"✗ {total - passed} of {total} tests fail — read the first red row, fix, run again</div>"
        )
    rows = []
    for r in results:
        icon = '<td style="padding:5px 10px;border-top:1px solid rgba(127,127,127,.25);font-weight:700;color:' + (
            '#059669">✓</td>' if r.passed else '#dc2626">✗</td>'
        )
        got = r.error if r.error else repr(r.got)
        rows.append(f"<tr>{icon}{_cell(_label(r.case))}{_cell(repr(r.case.expected))}{_cell(got)}</tr>")
    head = "".join(
        f'<th style="text-align:left;padding:5px 10px;font-size:12px;opacity:.7">{h}</th>'
        for h in ("", "input", "expected", "got")
    )
    markup = (
        f"<div>{summary}<div style='overflow-x:auto'><table style='border-collapse:collapse;"
        f"border:1px solid rgba(127,127,127,.35);border-radius:8px'><tr>{head}</tr>{''.join(rows)}</table></div></div>"
    )
    try:
        import marimo as mo
    except ImportError:  # pragma: no cover
        return markup
    return mo.Html(markup)


def solution(code: str, title: str = "Show a solution") -> Any:
    """A collapsed accordion holding a reference solution."""
    import marimo as mo

    return mo.accordion({title: mo.md(f"```python\n{code.strip()}\n```")})

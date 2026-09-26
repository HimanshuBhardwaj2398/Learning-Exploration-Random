"""Tests for the practice runner and a smoke test for every view."""

from learnkit import (
    Case,
    array_view,
    assert_cases,
    bars_view,
    code_view,
    grid_legend,
    kv_view,
    pair_grid_view,
    run_cases,
    line_of,
    lookup_view,
    parse_ints,
    recursion_guard,
    staircase_view,
    sudoku_view,
)

ADD = "def add(a, b):\n    return a + b\n"
CASES = [Case((1, 2), 3), Case((-1, 1), 0, label="opposites")]


def test_passing_code_passes():
    assert all(r.passed for r in run_cases(ADD, "add", CASES))


def test_wrong_answer_is_reported():
    results = run_cases("def add(a, b):\n    return a - b\n", "add", CASES)
    assert [r.passed for r in results] == [False, False]
    assert results[0].got == -1


def test_syntax_error_fails_every_case():
    results = run_cases("def add(a, b)\n    return a + b\n", "add", CASES)
    assert all(not r.passed and r.error.startswith("SyntaxError") for r in results)


def test_missing_function_is_explained():
    results = run_cases("def plus(a, b):\n    return a + b\n", "add", CASES)
    assert "no function named add()" in results[0].error


def test_exception_is_captured():
    results = run_cases("def add(a, b):\n    return a / 0\n", "add", CASES)
    assert results[0].error.startswith("ZeroDivisionError")


def test_infinite_loop_is_stopped():
    results = run_cases("def add(a, b):\n    while True:\n        a += 1\n", "add", CASES[:1], budget=5_000)
    assert "infinite loop" in results[0].error and "too slow" in results[0].error


def test_inplace_argument_is_judged():
    code = "def zero_first(nums):\n    nums[0] = 0\n"
    assert run_cases(code, "zero_first", [Case(([5, 6],), [0, 6], inplace=0)])[0].passed


def test_cases_are_not_mutated_between_runs():
    case = Case(([3, 1, 2],), [1, 2, 3], inplace=0)
    run_cases("def s(nums):\n    nums.sort()\n", "s", [case])
    assert case.args == ([3, 1, 2],)


def test_normalise_ignores_order():
    code = "def pairs():\n    return [[2, 1], [4, 3]]\n"
    norm = lambda res: sorted(sorted(t) for t in res)  # noqa: E731
    assert run_cases(code, "pairs", [Case((), [[3, 4], [1, 2]])], normalise=norm)[0].passed


def test_assert_cases_raises_readably():
    try:
        assert_cases("def add(a, b):\n    return 99\n", "add", CASES)
    except AssertionError as err:
        assert "opposites" in str(err) and "2 case(s) failed" in str(err)
    else:  # pragma: no cover
        raise AssertionError("expected a failure")


def test_views_render():
    for view in (
        array_view([1, 2, 3], pointers={"left": 0, "write": 3}, window=(0, 1), marks={2: "hit"}, caption="x"),
        pair_grid_view(4, {(0, 3): "computed", (1, 2): ("answer", "9")}, labels=[1, 2, 3, 4]),
        sudoku_view(["." * 9] * 9, focus=(4, 4), bad=[(0, 0)]),
        bars_view([0, 1, 0, 2], water=[0, 0, 1, 0], pointers={"left": 1}, container=(1, 3)),
        code_view("a = 1\nb = 2", active=2),
        kv_view({"sum": 3}),
        grid_legend(),
        lookup_view([("obj", "instance", {"x": 1}), ("Cls", "class", {"x": 2, "f": "function"})], "x", searched=1),
    ):
        text = getattr(view, "text", view)
        assert "<" in text


def test_parse_ints_and_errors():
    assert parse_ints("1, 2,3") == [1, 2, 3]
    for bad in ("1, x", "", "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"):
        try:
            parse_ints(bad)
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError(bad)


def test_line_of_finds_nth_occurrence():
    code = "a = 1\nb = a\nc = a\n"
    assert line_of(code, "a") == 1 and line_of(code, "= a", nth=2) == 3


def test_staircase_renders():
    view = staircase_view({"start": [0, 0, 1], "end": [0, 1, 2]}, top=3, current=1)
    assert "polyline" in getattr(view, "text", view)


def test_runaway_recursion_is_reported_not_fatal():
    code = "def down(n):\n    return down(n + 1)\n"
    result = run_cases(code, "down", [Case((0,), 0)])[0]
    assert result.error.startswith("RecursionError")


def test_recursion_guard_restores_the_limit():
    import sys
    before = sys.getrecursionlimit()
    with recursion_guard(headroom=50):
        assert sys.getrecursionlimit() <= before
    assert sys.getrecursionlimit() == before


def test_lookup_view_marks_found_and_shadowed():
    chain = [("acct", "instance", {"rate": 0.1}), ("Savings", "class", {"rate": 0.04})]
    text = getattr(lookup_view(chain, "rate", searched=1), "text", "")
    assert "found here" in text and "shadowed" in text
    missing = getattr(lookup_view(chain, "nope", searched=2), "text", "")
    assert missing.count("not here") == 2

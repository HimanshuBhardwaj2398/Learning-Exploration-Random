"""learnkit: small, dependency-free helpers shared by the learning notebooks.

views     draw arrays with pointers, windows, grids, bars and highlighted code
practice  run a learner's code against test cases and show what passed

Everything here is plain Python (stdlib only) so the notebooks also run in the
browser through WebAssembly. The site build copies this package next to each
notebook before exporting it; locally, `pip install -e .` makes it importable.
"""

from learnkit.practice import Case, Result, assert_cases, check, run_cases, solution
from learnkit.util import line_of, parse_ints, parse_text, staircase_view
from learnkit.views import (
    array_view,
    badge,
    bars_view,
    code_view,
    grid_legend,
    kv_view,
    legend,
    pair_grid_view,
    sudoku_view,
)

__all__ = [
    "Case",
    "Result",
    "array_view",
    "assert_cases",
    "badge",
    "bars_view",
    "check",
    "code_view",
    "grid_legend",
    "kv_view",
    "legend",
    "line_of",
    "pair_grid_view",
    "parse_ints",
    "parse_text",
    "run_cases",
    "solution",
    "staircase_view",
    "sudoku_view",
]

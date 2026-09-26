"""HTML views for algorithm step-throughs.

Each function returns ``marimo.Html`` when marimo is installed (so a notebook
cell can simply end with the call) and a plain HTML string otherwise.

Colours are translucent tints over the current text colour, so every view reads
correctly in marimo's light and dark themes. Pointer colours are stable by
name: left-ish pointers (i, left, l, start, low, read) are indigo, right-ish
ones (j, right, r, end, high, write) teal, and a third (k, mid, anchor) amber.
"""

from __future__ import annotations

import html as _html
from typing import Any, Iterable, Mapping, Sequence

INDIGO, TEAL, AMBER, PINK, BLUE = "#6366f1", "#0d9488", "#d97706", "#db2777", "#3b82f6"
PALETTE = (INDIGO, TEAL, AMBER, PINK, BLUE)

_NAMED_COLOURS = {
    **dict.fromkeys(("i", "left", "l", "L", "lo", "low", "start", "read", "p1", "slow"), INDIGO),
    **dict.fromkeys(("j", "right", "r", "R", "hi", "high", "end", "write", "p2", "fast"), TEAL),
    **dict.fromkeys(("k", "mid", "anchor", "a", "p"), AMBER),
}

MARKS = {
    "hit": "background:rgba(16,185,129,.28);border-color:rgba(16,185,129,.95);",
    "bad": "background:rgba(239,68,68,.26);border-color:rgba(239,68,68,.95);",
    "focus": "background:rgba(99,102,241,.24);border-color:rgba(99,102,241,.95);",
    "warn": "background:rgba(217,119,6,.24);border-color:rgba(217,119,6,.95);",
    "done": "background:rgba(127,127,127,.16);",
    "skip": "opacity:.32;",
    "ghost": "border-style:dashed;opacity:.55;",
}

_BORDER = "rgba(127,127,127,.45)"
_MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
_WINDOW_TINT = "rgba(99,102,241,.13)"


def _out(markup: str) -> Any:
    try:
        import marimo as mo
    except ImportError:  # pragma: no cover - only without marimo
        return markup
    return mo.Html(markup)


def _esc(value: Any) -> str:
    return _html.escape(str(value))


def pointer_colour(name: str, order: int = 0) -> str:
    """Colour for a pointer name; unknown names fall back to palette order."""
    return _NAMED_COLOURS.get(name, PALETTE[order % len(PALETTE)])


def badge(text: str, tone: str = "indigo") -> Any:
    """A small coloured label, e.g. badge("grow", "teal")."""
    colour = {"indigo": INDIGO, "teal": TEAL, "amber": AMBER, "pink": PINK, "blue": BLUE,
              "green": "#059669", "red": "#dc2626", "grey": "#6b7280"}.get(tone, tone)
    return _out(
        f'<span style="display:inline-block;padding:1px 9px;border-radius:999px;'
        f"border:1px solid {colour};color:{colour};font:600 12px/1.6 {_MONO};"
        f'letter-spacing:.02em">{_esc(text)}</span>'
    )


def legend(items: Iterable[tuple[str, str]]) -> Any:
    """items: (label, css-for-swatch). Use MARKS values or any CSS."""
    parts = []
    for label, css in items:
        parts.append(
            f'<span style="display:inline-flex;align-items:center;gap:6px;margin-right:14px">'
            f'<span style="width:14px;height:14px;border-radius:4px;border:1.5px solid {_BORDER};{css}"></span>'
            f"{_esc(label)}</span>"
        )
    return _out(f'<div style="font-size:12.5px;opacity:.85;margin:4px 0">{"".join(parts)}</div>')


def array_view(
    values: Sequence[Any],
    *,
    pointers: Mapping[str, int | None] | None = None,
    window: tuple[int, int] | None = None,
    marks: Mapping[int, str] | None = None,
    caption: str | None = None,
    show_index: bool = True,
    cell_px: int = 44,
) -> Any:
    """A row of cells with pointer labels above, indices below and an optional window.

    pointers: {"left": 0, "right": 5}; a pointer equal to len(values) gets a dashed
              ghost cell (useful for a write pointer that has reached the end).
    window:   (lo, hi) inclusive; drawn as a tinted band with a bar underneath.
    marks:    {index: "hit" | "bad" | "focus" | "warn" | "done" | "skip"}.
    """
    values = list(values)
    n = len(values)
    pointers = dict(pointers or {})
    marks = dict(marks or {})
    ghost = any(pos == n for pos in pointers.values() if pos is not None)
    cols = n + (1 if ghost else 0)

    labels: list[list[tuple[str, str]]] = [[] for _ in range(cols)]
    off_grid = []
    for order, (name, pos) in enumerate(pointers.items()):
        if pos is None:
            continue
        colour = pointer_colour(name, order)
        if 0 <= pos < cols:
            labels[pos].append((name, colour))
        else:
            off_grid.append(f'<span style="color:{colour};font-weight:600">{_esc(name)}</span> = {pos}')

    lo, hi = window if window else (1, 0)
    cell_base = (
        f"width:{cell_px}px;min-width:{cell_px}px;height:{cell_px - 4}px;text-align:center;"
        f"border:1.5px solid {_BORDER};border-radius:8px;font:500 15px {_MONO};"
    )

    top, mid, bar, idx = [], [], [], []
    for c in range(cols):
        tags = "".join(
            f'<div style="color:{colour};font:700 12px/1.15 {_MONO}">{_esc(name)}</div>' for name, colour in labels[c]
        )
        arrow = '<div style="font-size:10px;line-height:1;opacity:.8">▼</div>' if labels[c] else ""
        top.append(f'<td style="vertical-align:bottom;text-align:center;height:34px;padding:0">{tags}{arrow}</td>')

        in_window = lo <= c <= hi
        style = cell_base
        if c == n:
            style += MARKS["ghost"]
            text = ""
        else:
            text = _esc(values[c])
            if in_window:
                style += f"background:{_WINDOW_TINT};"
            style += MARKS.get(marks.get(c, ""), "")
        mid.append(f'<td style="{style}">{text}</td>')

        if window:
            radius = "border-radius:3px;" if lo == hi else (
                "border-radius:3px 0 0 3px;" if c == lo else "border-radius:0 3px 3px 0;" if c == hi else ""
            )
            fill = f"background:{INDIGO};{radius}" if in_window else ""
            bar.append(f'<td style="padding:0"><div style="height:4px;{fill}"></div></td>')
        idx.append(f'<td style="text-align:center;font:11px {_MONO};opacity:.6;padding:0">{c if c < n else "end"}</td>')

    rows = [f"<tr>{''.join(top)}</tr>", f"<tr>{''.join(mid)}</tr>"]
    if window:
        rows.append(f"<tr>{''.join(bar)}</tr>")
    if show_index:
        rows.append(f"<tr>{''.join(idx)}</tr>")

    extra = ""
    if off_grid:
        extra = f'<div style="font:12px {_MONO};opacity:.8;text-align:center">off the array: {", ".join(off_grid)}</div>'
    cap = f'<div style="text-align:center;font-size:13.5px;margin-top:6px">{_esc(caption)}</div>' if caption else ""
    return _out(
        '<div style="overflow-x:auto;padding:2px 0">'
        '<table style="border-collapse:separate;border-spacing:5px 3px;margin:0 auto">'
        f"{''.join(rows)}</table>{extra}{cap}</div>"
    )


def kv_view(state: Mapping[str, Any], *, title: str | None = None) -> Any:
    """A compact two-column table of variable names and values."""
    rows = "".join(
        f'<tr><td style="padding:3px 12px 3px 0;opacity:.7;font:13px {_MONO}">{_esc(k)}</td>'
        f'<td style="padding:3px 0;font:600 13px {_MONO}">{_esc(v)}</td></tr>'
        for k, v in state.items()
    )
    head = f'<div style="font-weight:600;font-size:13px;margin-bottom:4px">{_esc(title)}</div>' if title else ""
    return _out(
        f'<div style="border:1px solid {_BORDER};border-radius:10px;padding:10px 14px;min-width:180px">'
        f"{head}<table style='border-collapse:collapse'>{rows}</table></div>"
    )


def code_view(source: str, active: int | Iterable[int] | None = None, *, title: str | None = None) -> Any:
    """Source code with line numbers; `active` (1-based) lines are highlighted."""
    if active is None:
        active_set: set[int] = set()
    elif isinstance(active, int):
        active_set = {active}
    else:
        active_set = set(active)
    lines = source.strip("\n").splitlines()
    out = []
    for number, line in enumerate(lines, start=1):
        on = number in active_set
        bg = f"background:rgba(99,102,241,.2);border-left:3px solid {INDIGO};" if on else "border-left:3px solid transparent;"
        out.append(
            f'<div style="{bg}padding:0 10px 0 6px;white-space:pre">'
            f'<span style="display:inline-block;width:22px;opacity:.45;user-select:none">{number}</span>'
            f"{_esc(line) or ' '}</div>"
        )
    head = f'<div style="font-weight:600;font-size:12.5px;padding:6px 10px;opacity:.8">{_esc(title)}</div>' if title else ""
    return _out(
        f'<div style="border:1px solid {_BORDER};border-radius:10px;overflow-x:auto;padding:4px 0;'
        f'font:12.5px/1.6 {_MONO}">{head}{"".join(out)}</div>'
    )


_GRID_STATES = {
    "unseen": "",
    "computed": "background:rgba(99,102,241,.28);",
    "eliminated": "background:rgba(127,127,127,.28);opacity:.55;",
    "current": f"background:rgba(217,119,6,.45);border-color:{AMBER};",
    "answer": "background:rgba(16,185,129,.55);border-color:#059669;",
    "lost": "background:rgba(239,68,68,.55);border-color:#dc2626;",
    "window": "background:rgba(13,148,136,.3);",
}


def pair_grid_view(
    n: int,
    cells: Mapping[tuple[int, int], str | tuple[str, str]],
    *,
    labels: Sequence[Any] | None = None,
    diagonal: bool = False,
    cell_px: int = 26,
    row_title: str = "i",
    col_title: str = "j",
) -> Any:
    """The (i, j) search grid: rows are i, columns j, only j > i (or j >= i) exist.

    cells maps (i, j) to a state name, or to (state, text) to print inside the cell.
    States: unseen, computed, eliminated, current, answer, lost, window.
    """
    head = [f'<td style="font:11px {_MONO};opacity:.6;text-align:right;padding-right:4px">{_esc(row_title)}\\{_esc(col_title)}</td>']
    for j in range(n):
        tag = _esc(labels[j]) if labels is not None else j
        head.append(f'<td style="text-align:center;font:11px {_MONO};opacity:.7">{tag}</td>')
    rows = [f"<tr>{''.join(head)}</tr>"]
    for i in range(n):
        tag = _esc(labels[i]) if labels is not None else i
        tds = [f'<td style="text-align:right;font:11px {_MONO};opacity:.7;padding-right:4px">{tag}</td>']
        for j in range(n):
            exists = j > i or (diagonal and j == i)
            if not exists:
                tds.append(f'<td style="width:{cell_px}px;height:{cell_px}px"></td>')
                continue
            value = cells.get((i, j), "unseen")
            state, text = (value, "") if isinstance(value, str) else value
            style = (
                f"width:{cell_px}px;height:{cell_px}px;border:1px solid {_BORDER};border-radius:4px;"
                f"text-align:center;font:10px {_MONO};{_GRID_STATES.get(state, '')}"
            )
            tds.append(f'<td style="{style}">{_esc(text)}</td>')
        rows.append(f"<tr>{''.join(tds)}</tr>")
    return _out(
        '<div style="overflow-x:auto"><table style="border-collapse:separate;border-spacing:2px;margin:0 auto">'
        f"{''.join(rows)}</table></div>"
    )


def grid_legend() -> Any:
    names = [("computed", "computed"), ("ruled out", "eliminated"), ("current", "current"),
             ("answer", "answer"), ("answer thrown away", "lost")]
    return legend((label, _GRID_STATES[state]) for label, state in names)


def sudoku_view(
    board: Sequence[Sequence[str]],
    *,
    focus: tuple[int, int] | None = None,
    bad: Iterable[tuple[int, int]] = (),
    done: Iterable[tuple[int, int]] = (),
    show_peers: bool = True,
    cell_px: int = 32,
) -> Any:
    """A 9x9 board with box borders. The focus cell's row, column and box are tinted."""
    bad_set, done_set = set(bad), set(done)
    fr, fc = focus if focus else (-1, -1)
    rows = []
    for r in range(9):
        tds = []
        for c in range(9):
            value = board[r][c]
            peer = show_peers and focus is not None and (r == fr or c == fc or (r // 3, c // 3) == (fr // 3, fc // 3))
            style = (
                f"width:{cell_px}px;height:{cell_px}px;text-align:center;font:500 15px {_MONO};"
                f"border:1px solid {_BORDER};"
            )
            if c in (2, 5):
                style += "border-right:2.5px solid rgba(127,127,127,.85);"
            if r in (2, 5):
                style += "border-bottom:2.5px solid rgba(127,127,127,.85);"
            if (r, c) in bad_set:
                style += MARKS["bad"]
            elif (r, c) == (fr, fc):
                style += MARKS["focus"]
            elif peer:
                style += "background:rgba(99,102,241,.08);"
            elif (r, c) in done_set:
                style += "background:rgba(127,127,127,.1);"
            tds.append(f'<td style="{style}">{"" if value == "." else _esc(value)}</td>')
        rows.append(f"<tr>{''.join(tds)}</tr>")
    return _out(
        '<table style="border-collapse:collapse;margin:0 auto;border:2.5px solid rgba(127,127,127,.85)">'
        f"{''.join(rows)}</table>"
    )


def bars_view(
    heights: Sequence[int],
    *,
    water: Sequence[int] | None = None,
    container: tuple[int, int] | None = None,
    pointers: Mapping[str, int | None] | None = None,
    marks: Mapping[int, str] | None = None,
    unit: int = 16,
    bar_px: int = 28,
    caption: str | None = None,
) -> Any:
    """Vertical bars (an elevation map or container walls) drawn as SVG.

    water:     per-index water height drawn on top of each bar (Trapping Rain Water).
    container: (l, r) draws the water held between two walls (Container With Most Water).
    pointers:  labels under the bars, coloured like array_view pointers.
    marks:     {index: "hit" | "bad" | "focus" | "warn"} tints a bar.
    """
    n = len(heights)
    gap = 6
    top = max([*heights, *(h + w for h, w in zip(heights, water or []))] + [1])
    plot_h = top * unit
    label_h = 40
    width = n * (bar_px + gap) + gap
    height = plot_h + label_h + 8
    base = plot_h + 4
    mark_fill = {"hit": "rgba(16,185,129,.8)", "bad": "rgba(239,68,68,.8)",
                 "focus": "rgba(99,102,241,.85)", "warn": "rgba(217,119,6,.85)"}
    parts = []
    if container:
        l, r = container
        level = min(heights[l], heights[r])
        x0 = gap + l * (bar_px + gap) + bar_px
        x1 = gap + r * (bar_px + gap)
        parts.append(
            f'<rect x="{x0}" y="{base - level * unit}" width="{max(x1 - x0, 0)}" height="{level * unit}" '
            f'fill="rgba(59,130,246,.22)" stroke="{BLUE}" stroke-dasharray="4 3"/>'
        )
    for idx, h in enumerate(heights):
        x = gap + idx * (bar_px + gap)
        fill = mark_fill.get((marks or {}).get(idx, ""), "rgba(127,127,127,.55)")
        parts.append(f'<rect x="{x}" y="{base - h * unit}" width="{bar_px}" height="{h * unit}" rx="3" fill="{fill}"/>')
        if water and water[idx] > 0:
            parts.append(
                f'<rect x="{x}" y="{base - (h + water[idx]) * unit}" width="{bar_px}" '
                f'height="{water[idx] * unit}" fill="rgba(59,130,246,.55)"/>'
            )
        parts.append(
            f'<text x="{x + bar_px / 2}" y="{base + 13}" text-anchor="middle" font-size="11" '
            f'fill="currentColor" opacity=".6" font-family="monospace">{h}</text>'
        )
    stacked: dict[int, int] = {}
    for order, (name, pos) in enumerate((pointers or {}).items()):
        if pos is None or not 0 <= pos < n:
            continue
        row = stacked.get(pos, 0)
        stacked[pos] = row + 1
        x = gap + pos * (bar_px + gap) + bar_px / 2
        parts.append(
            f'<text x="{x}" y="{base + 27 + row * 12}" text-anchor="middle" font-size="12" font-weight="700" '
            f'fill="{pointer_colour(name, order)}" font-family="monospace">{_esc(name)}</text>'
        )
    cap = f'<div style="text-align:center;font-size:13.5px;margin-top:2px">{_esc(caption)}</div>' if caption else ""
    return _out(
        f'<div style="overflow-x:auto;text-align:center"><svg width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="color:inherit;max-width:100%">'
        f'<line x1="0" y1="{base}" x2="{width}" y2="{base}" stroke="currentColor" stroke-opacity=".35"/>'
        f"{''.join(parts)}</svg>{cap}</div>"
    )

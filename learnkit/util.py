"""Small helpers the notebooks share: parsing inputs and locating code lines."""

from __future__ import annotations

from typing import Any, Sequence


def parse_ints(text: str, *, low: int = 1, high: int = 14) -> list[int]:
    """'1, 2, 3' -> [1, 2, 3]. Raises ValueError with a message fit to show the learner."""
    parts = [p for p in text.replace(",", " ").split() if p]
    try:
        values = [int(p) for p in parts]
    except ValueError:
        raise ValueError("Use whole numbers separated by commas, like 1, 2, 3") from None
    if not low <= len(values) <= high:
        raise ValueError(f"Give between {low} and {high} numbers (you gave {len(values)}).")
    return values


def parse_text(text: str, *, low: int = 0, high: int = 16) -> str:
    """Validate a short string input for a step-through."""
    if not low <= len(text) <= high:
        raise ValueError(f"Use between {low} and {high} characters (you gave {len(text)}).")
    return text


def line_of(code: str, snippet: str, nth: int = 1) -> int:
    """1-based line number of the nth line of `code` containing `snippet`.

    Step-through frames use this instead of hard-coded numbers, so editing the
    displayed code never silently points the highlight at the wrong line.
    """
    seen = 0
    for number, line in enumerate(code.strip("\n").splitlines(), start=1):
        if snippet in line:
            seen += 1
            if seen == nth:
                return number
    raise KeyError(f"{snippet!r} (occurrence {nth}) not found in code")


def staircase_view(series: dict[str, Sequence[int]], *, top: int, current: int | None = None,
                   width: int = 420, height: int = 170) -> Any:
    """Plot pointer positions over steps (e.g. start and end of a sliding window).

    series: {"start": [...], "end": [...]}, one value per frame; top is the largest position.
    """
    from learnkit.views import _out, pointer_colour

    steps = max((len(v) for v in series.values()), default=0)
    pad_l, pad_b, pad_t = 34, 22, 10
    plot_w, plot_h = width - pad_l - 8, height - pad_b - pad_t

    def x(k: int) -> float:
        return pad_l + (k * plot_w / max(steps - 1, 1))

    def y(v: int) -> float:
        return pad_t + plot_h - (v * plot_h / max(top, 1))

    parts = [
        f'<line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{pad_l + plot_w}" y2="{pad_t + plot_h}" stroke="currentColor" stroke-opacity=".3"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t + plot_h}" stroke="currentColor" stroke-opacity=".3"/>',
        f'<text x="{pad_l - 6}" y="{pad_t + 4}" text-anchor="end" font-size="10" fill="currentColor" opacity=".6">{top}</text>',
        f'<text x="{pad_l - 6}" y="{pad_t + plot_h}" text-anchor="end" font-size="10" fill="currentColor" opacity=".6">0</text>',
        f'<text x="{pad_l + plot_w}" y="{height - 6}" text-anchor="end" font-size="10" fill="currentColor" opacity=".6">step {steps}</text>',
    ]
    for order, (name, values) in enumerate(series.items()):
        colour = pointer_colour(name, order)
        points = []
        for k, v in enumerate(values):
            if k:
                points.append(f"{x(k):.1f},{y(values[k - 1]):.1f}")  # step shape: hold, then jump
            points.append(f"{x(k):.1f},{y(v):.1f}")
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{colour}" stroke-width="2.2"/>')
        if values:
            parts.append(
                f'<text x="{x(len(values) - 1) + 4:.1f}" y="{y(values[-1]) - 4:.1f}" font-size="11" font-weight="700" '
                f'fill="{colour}">{name}</text>'
            )
    if current is not None and steps:
        parts.append(f'<line x1="{x(current):.1f}" y1="{pad_t}" x2="{x(current):.1f}" y2="{pad_t + plot_h}" stroke="#d97706" stroke-dasharray="3 3"/>')
    return _out(
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="color:inherit;max-width:100%">'
        f"{''.join(parts)}</svg>"
    )

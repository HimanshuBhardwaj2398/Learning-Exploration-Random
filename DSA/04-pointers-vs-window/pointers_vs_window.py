import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Pointers or window? · DSA")


@app.cell
def _():
    import random

    import marimo as mo

    from learnkit import array_view, grid_legend, kv_view, pair_grid_view, parse_ints

    return (
        array_view,
        grid_legend,
        kv_view,
        mo,
        pair_grid_view,
        parse_ints,
        random,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Pointers or window?

    **Comparison 04 · DSA.** Both patterns search the same space, the grid of every (start, end) pair, and both finish in O(n) by throwing away a whole row or column per step. What differs is **the question they ask** and **the fact that makes the throw-away legal**.

    | | Asks | Legal because |
    | :--- | :--- | :--- |
    | **Two pointers** | what's at the two **ends**? | the input is **sorted** |
    | **Sliding window** | what's **inside** the range? | validity is **monotone** (e.g. no negative values) |
    | **Neither** | can't sort and need positions → **hash map**; negatives with a sum target → **prefix sums** | |

    Companion reading: the [five-session reading plan](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/04-pointers-vs-window/reading-plan.html) in this folder.
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md("**How to use this notebook.** Online it runs in your browser; locally, `marimo edit DSA/04-pointers-vs-window/pointers_vs_window.py`. "
              "Order: **two staircases → why the skip is safe (and breaking it) → same direction ≠ window → the decision → twins → drill → side by side.**"),
        kind="info",
    )
    return


@app.cell
def _():
    def pair_frames(a: list[int], target: int) -> list[dict]:
        """Converging pointers over the pair grid (i < j). Cells: computed / eliminated / current / answer."""
        n, cells, frames = len(a), {}, []
        i, j = 0, n - 1
        while i < j:
            s = a[i] + a[j]
            view = dict(cells)
            if s == target:
                view[(i, j)] = ("answer", str(s))
                frames.append(dict(cells=view, note=f"a[{i}] + a[{j}] = {s}: found.", done=True))
                return frames
            view[(i, j)] = ("current", str(s))
            if s < target:
                frames.append(dict(cells=view, note=f"{s} < {target}: row {i} is dead (every partner of a[{i}] left is ≤ a[{j}]). i += 1."))
                cells[(i, j)] = ("computed", str(s))
                for jj in range(i + 1, j):
                    cells.setdefault((i, jj), "eliminated")
                i += 1
            else:
                frames.append(dict(cells=view, note=f"{s} > {target}: column {j} is dead (every partner of a[{j}] left is ≥ a[{i}]). j -= 1."))
                cells[(i, j)] = ("computed", str(s))
                for ii in range(i + 1, j):
                    cells.setdefault((ii, j), "eliminated")
                j -= 1
        frames.append(dict(cells=dict(cells), note="The pointers met: no pair.", done=True))
        return frames

    def window_frames(a: list[int], target: int) -> list[dict]:
        """Shortest window with sum >= target over the window grid (l <= r)."""
        n, cells, frames = len(a), {}, []
        left, total, best = 0, 0, None
        for right in range(n):
            total += a[right]
            while left <= right:
                view = dict(cells)
                view[(left, right)] = ("current", str(total))
                if total >= target:
                    if best is None or right - left + 1 < best[1] - best[0] + 1:
                        best = (left, right)
                    frames.append(dict(cells=view, note=f"sum a[{left}..{right}] = {total} ≥ {target}: valid, record length {right - left + 1}. "
                                                        f"The rest of row {left} is only longer, so it's dead. Shrink: left += 1."))
                    cells[(left, right)] = ("computed", str(total))
                    for rr in range(right + 1, n):
                        cells.setdefault((left, rr), "eliminated")
                    total -= a[left]
                    left += 1
                else:
                    frames.append(dict(cells=view, note=f"sum a[{left}..{right}] = {total} < {target}: every shorter window ending at {right} only loses values, "
                                                        f"so column {right} below here is dead. Grow: right += 1."))
                    cells[(left, right)] = ("computed", str(total))
                    for ll in range(left + 1, right + 1):
                        cells.setdefault((ll, right), "eliminated")
                    break
        final = dict(cells)
        if best:
            final[best] = ("answer", final[best][1] if isinstance(final.get(best), tuple) else "")
        frames.append(dict(cells=final, note=f"Done. Shortest valid window: a[{best[0]}..{best[1]}]." if best else "Done: no window reaches the target.", done=True))
        return frames

    def mark_lost(frames: list[dict], answers: set) -> list[dict]:
        """Paint real answers that were eliminated without being looked at."""
        out = []
        for f in frames:
            cells = dict(f["cells"])
            for cell in answers:
                if cells.get(cell) == "eliminated":
                    cells[cell] = "lost"
            out.append({**f, "cells": cells})
        return out

    def grid_counts(cells: dict, total: int) -> dict:
        kinds = [c if isinstance(c, str) else c[0] for c in cells.values()]
        computed = sum(k in ("computed", "current", "answer") for k in kinds)
        ruled = sum(k in ("eliminated", "lost") for k in kinds)
        return {"cells": total, "computed": computed, "ruled out unseen": ruled, "unknown": total - computed - ruled}

    return grid_counts, mark_lost, pair_frames, window_frames


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · One grid, two staircases

    Brute force on n items looks at every cell of an n × n triangle: a pair (i, j) for two pointers, a window [l..r] for a sliding window. Both patterns compute one cell, **prove a whole row or column can't hold a better answer, and discard it unseen**. Two pointers walks in from the **top-right corner**; the window walks **along the diagonal**, top-left to bottom-right. Same array, same target, different routes.
    """)
    return


@app.cell
def _(mo):
    twin_values = mo.ui.text(value="1, 2, 3, 4, 6, 8, 9", label="Sorted array", full_width=True)
    twin_target = mo.ui.number(start=1, stop=200, value=14, label="Target")
    mo.hstack([twin_values, twin_target], widths=[3, 1])
    return twin_target, twin_values


@app.cell
def _(mo, pair_frames, parse_ints, twin_target, twin_values, window_frames):
    try:
        twin_input = sorted(abs(v) for v in parse_ints(twin_values.value, low=2, high=12))
        _err = None
    except ValueError as _e:
        twin_input, _err = [], str(_e)
    mo.stop(_err is not None, mo.callout(_err or "", kind="warn"))
    twin_pairs = pair_frames(twin_input, int(twin_target.value))
    twin_windows = window_frames(twin_input, int(twin_target.value))
    twin_step = mo.ui.slider(0, max(len(twin_pairs), len(twin_windows)) - 1 or 1, value=0, label="Step (both panels)", full_width=True, show_value=True)
    twin_step
    return twin_input, twin_pairs, twin_step, twin_windows


@app.cell
def _(
    array_view,
    grid_counts,
    grid_legend,
    kv_view,
    mo,
    pair_grid_view,
    twin_input,
    twin_pairs,
    twin_step,
    twin_windows,
):
    _n = len(twin_input)
    _p = twin_pairs[min(twin_step.value, len(twin_pairs) - 1)]
    _w = twin_windows[min(twin_step.value, len(twin_windows) - 1)]
    mo.vstack([
        array_view(twin_input, cell_px=38),
        mo.hstack([
            mo.vstack([mo.md("**Two pointers:** a pair with sum = target"), pair_grid_view(_n, _p["cells"]), kv_view(grid_counts(_p["cells"], _n * (_n - 1) // 2)), mo.md(_p["note"])]),
            mo.vstack([mo.md("**Window:** shortest run with sum ≥ target"), pair_grid_view(_n, _w["cells"], diagonal=True, row_title="l", col_title="r"), kv_view(grid_counts(_w["cells"], _n * (_n + 1) // 2)), mo.md(_w["note"])]),
        ], widths=[1, 1], align="start", gap=2),
        grid_legend(),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · Why the skip is safe, and how to break it

    Every elimination above rests on one inequality. Learn the inequality and you know when each pattern is allowed.

    **Two pointers needs order.** If `a` is sorted and a[i] + a[j] < target, every other partner j′ < j left in row i is no bigger than a[j], so a[i] + a[j′] ≤ a[i] + a[j] < target. Row i is dead. (Mirror argument kills column j.)

    **A window needs monotone validity.** If every value is ≥ 0 and sum(a[l..r]) < S, every shorter window ending at r only loses values: sum(a[l′..r]) ≤ sum(a[l..r]) < S for l′ > l. Column r is dead. When the window is valid, the rest of row l is only longer, so it's dead too.

    Now **remove the precondition and run the same code.** Left: an almost-sorted array with one 9 out of place. Right: a single negative. Watch for the **red** cell: a real answer, discarded without being looked at.
    """)
    return


@app.cell
def _(mark_lost, mo, pair_frames, window_frames):
    BROKEN_PAIR = ([1, 9, 2, 3, 4, 6, 8], 14)
    BROKEN_WINDOW = ([-3, 2, -3, 0, 2, -3, -4], 1)

    def pair_answers(a, target):
        return {(i, j) for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + a[j] == target}

    def shortest_answers(a, target):
        valid = [(l, r) for l in range(len(a)) for r in range(l, len(a)) if sum(a[l:r + 1]) >= target]
        if not valid:
            return set()
        shortest = min(r - l + 1 for l, r in valid)
        return {(l, r) for l, r in valid if r - l + 1 == shortest}

    broken_pairs = mark_lost(pair_frames(*BROKEN_PAIR), pair_answers(*BROKEN_PAIR))
    broken_windows = mark_lost(window_frames(*BROKEN_WINDOW), shortest_answers(*BROKEN_WINDOW))
    broken_step = mo.ui.slider(0, max(len(broken_pairs), len(broken_windows)) - 1, value=max(len(broken_pairs), len(broken_windows)) - 1,
                               label="Step (both panels)", full_width=True, show_value=True)
    broken_step
    return (
        BROKEN_PAIR,
        BROKEN_WINDOW,
        broken_pairs,
        broken_step,
        broken_windows,
        pair_answers,
        shortest_answers,
    )


@app.cell
def _(
    BROKEN_PAIR,
    BROKEN_WINDOW,
    array_view,
    broken_pairs,
    broken_step,
    broken_windows,
    grid_legend,
    mo,
    pair_grid_view,
):
    _p = broken_pairs[min(broken_step.value, len(broken_pairs) - 1)]
    _w = broken_windows[min(broken_step.value, len(broken_windows) - 1)]
    mo.vstack([
        mo.hstack([
            mo.vstack([mo.md(f"**Unsorted** `{BROKEN_PAIR[0]}`, target {BROKEN_PAIR[1]}"), array_view(BROKEN_PAIR[0], cell_px=34), pair_grid_view(7, _p["cells"]), mo.md(_p["note"])]),
            mo.vstack([mo.md(f"**Negatives** `{BROKEN_WINDOW[0]}`, target {BROKEN_WINDOW[1]}"), array_view(BROKEN_WINDOW[0], cell_px=34), pair_grid_view(7, _w["cells"], diagonal=True, row_title="l", col_title="r"), mo.md(_w["note"])]),
        ], widths=[1, 1], align="start", gap=2),
        grid_legend(),
        mo.md(
            "**What to reach for instead.** Can't sort because you must return original positions: a **hash map** in O(n), or sort `(value, index)` pairs and keep two pointers at O(n log n). "
            "Values can be negative: a window's shrink step is no longer safe. Count with **prefix sums + a hash map** (LC 560), or find the shortest with **prefix sums + a monotonic deque** (LC 862)."
        ),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Same direction is not the same as a window

    The confusing case: two pointers that **both move right**. Read/write pointers (Move Zeroes) and a window (Max Consecutive Ones III) look identical from a distance: `for r in range(n)`, a second pointer trailing behind, one pass. Run them on the same array and look at **what the gap between the pointers means**:

    - **Read/write:** the gap is **junk** waiting to be overwritten. Nothing in it is part of the answer.
    - **Window:** the gap **is** the answer. Its contents are what you measure.
    """)
    return


@app.cell
def _(mo):
    SAME_DIR = [1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1]

    def read_write_frames(nums):
        nums, write, frames = list(nums), 0, []
        for read in range(len(nums)):
            if nums[read] != 0:
                nums[write], nums[read] = nums[read], nums[write]
                write += 1
            marks = {k: "hit" for k in range(write)}
            marks.update({k: "warn" for k in range(write, read + 1)})
            frames.append(dict(arr=list(nums), pointers={"write": write, "read": read}, marks=marks))
        return frames

    def ones_frames(nums, k=1):
        start, zeros, best, frames = 0, 0, 0, []
        for end, v in enumerate(nums):
            zeros += v == 0
            while zeros > k:
                zeros -= nums[start] == 0
                start += 1
            best = max(best, end - start + 1)
            frames.append(dict(arr=list(nums), pointers={"start": start, "end": end}, window=(start, end), best=best))
        return frames

    same_rw, same_win = read_write_frames(SAME_DIR), ones_frames(SAME_DIR)
    same_step = mo.ui.slider(0, len(SAME_DIR) - 1, value=5, label="r (both)", full_width=True, show_value=True)
    same_step
    return SAME_DIR, same_rw, same_step, same_win


@app.cell
def _(array_view, mo, same_rw, same_step, same_win):
    _a, _b = same_rw[same_step.value], same_win[same_step.value]
    mo.vstack([
        mo.md("**Move Zeroes** (read/write): green = kept and final, amber = junk in the gap."),
        array_view(_a["arr"], pointers=_a["pointers"], marks=_a["marks"], cell_px=36),
        mo.md(f"**Max Consecutive Ones III, k = 1** (window): the band is the answer candidate. best = **{_b['best']}**."),
        array_view(_b["arr"], pointers=_b["pointers"], window=_b["window"], cell_px=36),
        mo.md("**Rule:** if the gap is junk to overwrite, it's read/write; if the gap is the answer, it's a window."),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · The decision, one question at a time

    Answer about a problem you're looking at; stop at the first leaf. (A single target in sorted data sits outside this chart: that's binary search.)
    """)
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
        flowchart TD
          A[Answer is a contiguous<br/>subarray or substring?] -->|yes| B[Validity monotone as<br/>the window grows or shrinks?]
          A -->|no| C[About a pair or triple<br/>of values?]
          B -->|yes| D[Needs the max or min<br/>inside the window?]
          D -->|no| W[Sliding window<br/>fixed, longest, shortest, count]
          D -->|yes| DQ[Window plus<br/>monotonic deque]
          B -->|no: negatives, exact sums| P[Prefix sum plus<br/>hash map or deque]
          C -->|yes| E[Allowed to sort?<br/>values, not indices]
          E -->|yes| T[Sort, then converging<br/>two pointers]
          E -->|no| H[Hash map]
          C -->|no| F[In-place rewrite, or<br/>two sorted inputs?]
          F -->|in place| RW[Read/write pointers]
          F -->|two inputs| TS[Two-sequence pointers]
        """
    )
    return


@app.cell
def _(mo):
    DECISION = {
        "A": ("Is the answer a contiguous subarray or substring?", {"yes": "B", "no": "C"}),
        "B": ("Does validity stay monotone as the window grows or shrinks (e.g. no negatives with a sum)?", {"yes": "D", "no": "leaf:prefix"}),
        "D": ("Do you need the max or min inside the window?", {"no": "leaf:window", "yes": "leaf:deque"}),
        "C": ("Is it about a pair or triple of values?", {"yes": "E", "no": "F"}),
        "E": ("Are you allowed to sort (the answer is values, not original indices)?", {"yes": "leaf:converging", "no": "leaf:hash"}),
        "F": ("Is it an in-place rewrite, or a walk over two sorted inputs?", {"in place": "leaf:readwrite", "two inputs": "leaf:twoseq"}),
    }
    LEAVES = {
        "window": ("Sliding window", "for right in range(n): … while not valid: shrink", "LC 3, 209, 424, 1004, 76"),
        "deque": ("Window + monotonic deque", "pop smaller values from the back; the front is the max", "LC 239, 1438"),
        "prefix": ("Prefix sum + hash map (count) or + deque (shortest)", "seen[prefix - k] counts subarrays ending here", "LC 560, 862, 974"),
        "converging": ("Sort, then converging two pointers", "while left < right:", "LC 167, 15, 11, 611"),
        "hash": ("Hash map", "if target - x in seen: …; seen[x] = i", "LC 1, 454"),
        "readwrite": ("Read/write pointers", "for read in range(n): if keep: nums[write] = …; write += 1", "LC 26, 27, 283, 80"),
        "twoseq": ("Two-sequence pointers", "one pointer per input, advance the smaller (or fill from the back)", "LC 88, 392, 844"),
    }
    decision = mo.ui.dictionary({key: mo.ui.radio(options=list(branches), label=question, inline=True) for key, (question, branches) in DECISION.items()})
    return DECISION, LEAVES, decision


@app.cell
def _(DECISION, LEAVES, decision, mo):
    _node, _shown = "A", []
    while not _node.startswith("leaf:"):
        _shown.append(decision[_node])
        _pick = decision.value[_node]
        if _pick is None:
            break
        _node = DECISION[_node][1][_pick]
    if _node.startswith("leaf:"):
        _name, _loop, _problems = LEAVES[_node.split(":", 1)[1]]
        _shown.append(mo.callout(mo.md(f"**{_name}**<br>Loop: `{_loop}`<br>Practise on: {_problems}"), kind="success"))
    mo.vstack(_shown)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · Twins: one word apart, different patterns

    Each pair reads almost the same. **Before opening one, name the pattern for each side and the word that decides it.**
    """)
    return


@app.cell
def _(mo):
    TWINS = [
        ("Sorted array, pair summing to target, return positions", "Unsorted array, pair summing to target, return original indices",
         "167 → converging pointers · 1 → hash map. The word: **sorted** (and whether indices must survive)."),
        ("Shortest subarray with sum ≥ target, all values positive", "Number of subarrays with sum exactly k, values may be negative",
         "209 → window (shortest) · 560 → prefix sum + hash. The words: **negative** and **exactly**."),
        ("Shortest subarray with sum ≥ target, values positive", "Shortest subarray with sum ≥ k, values may be negative",
         "209 → window · 862 → prefix sums + monotonic deque. The word: **negative**."),
        ("Move all zeros to the end in place, keeping order", "Longest run of 1s if you may flip at most k zeros",
         "283 → read/write (gap = junk) · 1004 → window (gap = answer). The question: what does the gap mean?"),
        ("Take k cards from either end to maximise the sum", "Remove from either end to reduce x to zero in the fewest moves",
         "1423 and 1658 are both a **fixed/shortest window on the middle you leave behind**: 'either end' is a window in disguise."),
        ("Is s a subsequence of t?", "Does s2 contain a permutation of s1?",
         "392 → two-sequence pointers · 567 → fixed window with a counter. The words: **subsequence** vs **permutation** (contiguous)."),
        ("Count triples that could form a triangle", "Count subarrays with product < k",
         "611 → sort + converging, count in bulk with right − left · 713 → window, count += end − start + 1. Both count by adding a width."),
        ("Pair with sum = target in a sorted array", "Shortest run with sum ≥ target in a positive array",
         "167 → converging from the corner · 209 → window along the diagonal. Same grid, different staircase (section 1)."),
    ]
    mo.accordion({f"{k + 1}. “{left}” vs “{right}”": mo.md(answer) for k, (left, right, answer) in enumerate(TWINS)})
    return


@app.cell
def _(mo):
    DRILL = [
        ("Longest substring with at most k distinct characters.", "Sliding window"),
        ("Two numbers in an unsorted array that add to target; return their indices.", "Hash map"),
        ("Remove duplicates from a sorted array in place.", "Two pointers"),
        ("Count subarrays with sum exactly k; values can be negative.", "Prefix sum"),
        ("Container that holds the most water between two lines.", "Two pointers"),
        ("Maximum of every window of size k.", "Window + deque"),
        ("Smallest window of s containing every character of t.", "Sliding window"),
        ("All unique triplets summing to zero.", "Two pointers"),
        ("Merge two sorted arrays in place.", "Two pointers"),
        ("Longest run of 1s with at most k flips.", "Sliding window"),
        ("Shortest subarray with sum ≥ k; values can be negative.", "Prefix sum"),
        ("Is one string a subsequence of another?", "Two pointers"),
    ]
    _options = ["Two pointers", "Sliding window", "Hash map", "Prefix sum", "Window + deque"]
    drill = mo.ui.array([mo.ui.radio(options=_options, label=f"**{k + 1}.** {q}", inline=True) for k, (q, _a) in enumerate(DRILL)])
    drill_check = mo.ui.run_button(label="Check my answers")
    mo.vstack([mo.md("## 6 · Name the pattern: twelve unlabelled prompts\n\nSay your reason out loud before you pick; the reason is what an interviewer listens for. Aim for **10 of 12** first time."), drill, drill_check])
    return DRILL, drill, drill_check


@app.cell
def _(DRILL, drill, drill_check, mo):
    mo.stop(not drill_check.value, mo.md("_Answer all twelve, then press **Check my answers**._"))
    _score = sum(p == a for (_q, a), p in zip(DRILL, drill.value))
    _wrong = [f"- **{k + 1}.** {q} → **{a}** (you said {p or 'nothing'})" for k, ((q, a), p) in enumerate(zip(DRILL, drill.value)) if p != a]
    mo.md(f"**{_score} / 12.** " + ("Below 10? Redo the twins before moving on.\n\n" if _score < 10 else "Solid.\n\n") + "\n".join(_wrong))
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7 · Side by side (keep this for revision)

    | | Converging two pointers | Sliding window |
    | :--- | :--- | :--- |
    | The question | what's at the two ends? | what's inside the range? |
    | Pointers start | at opposite ends | both at the left |
    | They move | toward each other until they meet | both rightward; right leads, left never passes it |
    | Loop | `while i < j:` | `for right in range(n):` |
    | State carried | nothing beyond a[i] and a[j] | a running summary of a[left..right] |
    | Each step decides by | comparing f(a[i], a[j]) with the target | whether the window is still valid |
    | Precondition | sorted, or allowed to sort | validity moves one way as the window grows/shrinks |
    | Path on the grid | top-right corner inward | along the diagonal |
    | Steps | at most n − 1 | at most 2n |
    | Breaks when | you need original positions | values go negative, or the target is an exact sum |
    | Relatives | read/write, two-sequence, fix-one k-sum | fixed length, at-most counting, window + deque |

    ```python
    def pair_with_sum(a, target):          # a is sorted
        i, j = 0, len(a) - 1
        while i < j:
            s = a[i] + a[j]
            if s == target:
                return i, j
            if s < target:
                i += 1                     # row i can't reach target
            else:
                j -= 1                     # column j overshoots
        return None


    def shortest_at_least(a, target):      # every a[x] >= 0
        best, left, window = float("inf"), 0, 0
        for right, x in enumerate(a):
            window += x                    # grow
            while window >= target:        # valid: record, then try shorter
                best = min(best, right - left + 1)
                window -= a[left]
                left += 1
        return 0 if best == float("inf") else best
    ```
    """)
    return


@app.cell
def _(mo):
    mo.accordion({
        "Recall 1. Why are both patterns O(n)?": mo.md("Each step deletes a whole row or column of the (start, end) grid: at most n − 1 steps for pointers, 2n for a window."),
        "Recall 2. What single fact decides between them?": mo.md("Does the answer depend on the ends (pointers) or on what's inside (window)? Then check the precondition: sorted for pointers, monotone validity for a window."),
        "Recall 3. Same-direction pointers: read/write or window?": mo.md("Ask what the gap means: junk to overwrite → read/write; the answer → window."),
        "Recall 4. What do you use when negatives break the window?": mo.md("Prefix sums: + hash map to count (560), + monotonic deque for the shortest (862)."),
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Go deeper

    - **In this folder:** [Pointers or Window? lab](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/04-pointers-vs-window/pointers-or-window.html) · [Reading plan](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/04-pointers-vs-window/reading-plan.html)
    - Topic notebooks: [two pointers](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/notebooks/two_pointers.html) · [sliding window](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/notebooks/sliding_window.html)
    - [Competitive Programmer's Handbook, Python edition](https://www2.compute.dtu.dk/courses/02110/2025/diverse/cses-book-python.pdf), ch. 8: the two-pointers method and sliding window minimum

    **Next:** prefix sums, the fallback when negatives break the window.
    """)
    return


@app.cell
def _(
    DECISION,
    LEAVES,
    SAME_DIR,
    broken_pairs,
    broken_windows,
    grid_counts,
    pair_answers,
    pair_frames,
    random,
    same_rw,
    same_win,
    shortest_answers,
    window_frames,
):
    def test_grids_classify_every_cell_when_the_search_runs_to_the_end():
        rng = random.Random(10)
        for _ in range(300):
            a = sorted(rng.randint(0, 20) for _ in range(rng.randint(2, 10)))
            n = len(a)
            final = window_frames(a, 10 ** 6)[-1]["cells"]  # unreachable target: the window visits the whole diagonal walk
            assert grid_counts(final, n * (n + 1) // 2)["unknown"] == 0
            final_pairs = pair_frames(a, -1)[-1]["cells"]  # no pair sums to -1
            assert grid_counts(final_pairs, n * (n - 1) // 2)["unknown"] == 0

    def test_answers_match_brute_force_when_preconditions_hold():
        rng = random.Random(11)
        for _ in range(300):
            a = sorted(rng.randint(0, 15) for _ in range(rng.randint(2, 10)))
            t = rng.randint(0, 40)
            found = pair_frames(a, t)[-1]["cells"]
            assert any(isinstance(v, tuple) and v[0] == "answer" for v in found.values()) == bool(pair_answers(a, t))
            wins = window_frames(a, t)[-1]["cells"]
            got = {c for c, v in wins.items() if isinstance(v, tuple) and v[0] == "answer"}
            want = shortest_answers(a, t)
            assert (len(got) == 1 and got <= want) if want else not got

    def test_broken_examples_really_lose_an_answer():
        assert any(v == "lost" for v in broken_pairs[-1]["cells"].values())
        assert any(v == "lost" for v in broken_windows[-1]["cells"].values())

    def test_every_decision_leaf_is_reachable_and_described():
        leaves = {target.split(":", 1)[1] for _q, branches in DECISION.values() for target in branches.values() if target.startswith("leaf:")}
        assert leaves == set(LEAVES)

    def test_same_direction_frames_are_right():
        assert same_rw[-1]["arr"] == [v for v in SAME_DIR if v] + [0] * SAME_DIR.count(0)
        brute = max(j - i + 1 for i in range(len(SAME_DIR)) for j in range(i, len(SAME_DIR)) if SAME_DIR[i:j + 1].count(0) <= 1)
        assert same_win[-1]["best"] == brute

    return


if __name__ == "__main__":
    app.run()

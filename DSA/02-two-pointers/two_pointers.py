import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Two pointers · DSA")


@app.cell
def _():
    import random

    import marimo as mo

    from learnkit import (
        Case,
        array_view,
        assert_cases,
        bars_view,
        check,
        code_view,
        grid_legend,
        kv_view,
        line_of,
        pair_grid_view,
        parse_ints,
        run_cases,
        solution,
    )

    return (
        Case,
        array_view,
        assert_cases,
        bars_view,
        check,
        code_view,
        grid_legend,
        kv_view,
        line_of,
        mo,
        pair_grid_view,
        parse_ints,
        random,
        run_cases,
        solution,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Two pointers

    **Pattern 02 · DSA.** Two indices walk a line, and every move throws away candidates you have *proved* can't be the answer. An invariant plus a safe move rule is what turns an O(n²) search over all pairs into a single O(n) pass.

    Anchor ladder: **125 → 15 → 42** · builds on sorting · leads to sliding window
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md(
            "**How to use this notebook.** Online, it runs real Python in your browser; the first load takes a few seconds. "
            "Locally, `marimo edit DSA/02-two-pointers/two_pointers.py` shows every cell's code so you can change it. "
            "Work top to bottom: **Spot it → See it → Five shapes → Brute force vs pointers → Practice → Traps → Recall.**"
        ),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Spot it

    Recognition is the skill that gets tested. Four families of wording point here:

    | You read… | Shape |
    | :--- | :--- |
    | **Sorted** (or cheap to sort) and you need a **pair / triplet** hitting a target, or a count of pairs | converging, fix-one |
    | **Both ends inward**: palindromes, containers between two walls, squares of a sorted array | converging |
    | **In place, O(1) extra space**: remove duplicates, move zeroes, partition | read / write, partition |
    | **Two sorted sequences**: merge them, or check one is a subsequence of the other | two sequences |

    **The discriminator:** *does the data between the pointers matter?* If you need the contents of the span (its counts, its running sum), that's a **sliding window**. Two pointers reads the **ends**, or a write frontier, never the middle.

    | Pattern | Reach for it when | The tell |
    | :--- | :--- | :--- |
    | Two pointers | sorted input, a relation between two elements, or an in-place rewrite | endpoints matter, the middle doesn't |
    | Hash map | unsorted input and you must return original indices | sorting would destroy the answer |
    | Sliding window | a contiguous run with a running constraint | both pointers move the same way, you keep state |
    | Binary search | one sorted array, locating a single value or boundary | you halve the range, you don't walk it |

    **Constraints name the budget:** n ≈ 10⁵–10⁶ allows O(n log n) at most, so sort + pointers or a hash pass. n ≈ 3000 allows O(n²): the 3Sum bound exactly.
    """)
    return


@app.cell
def _(mo):
    DRILL = [
        ("Sorted array: return the 1-indexed positions of two numbers adding to target.", "Two pointers",
         "Sorted + pair + positions in that sorted array: converging pointers (LC 167)."),
        ("Unsorted array: return the original indices of two numbers adding to target.", "Hash map",
         "Sorting would scramble the indices you must return (LC 1)."),
        ("Remove every copy of val in place and return the new length.", "Two pointers",
         "In place, keep order: read/write pointers (LC 27)."),
        ("Longest substring with at most two distinct characters.", "Sliding window",
         "Contiguous + a running count of what's inside (LC 159/904)."),
        ("Merge two sorted arrays into the first one, which has spare room at the end.", "Two pointers",
         "Two sorted sequences, filled from the back (LC 88)."),
        ("Is target present in a sorted array?", "Binary search",
         "One value in sorted data: halve, don't walk (LC 704)."),
        ("Count triplets that could be the sides of a triangle.", "Two pointers",
         "Sort, fix the longest side, count pairs in bulk with right - left (LC 611)."),
        ("Pick two lines that hold the most water.", "Two pointers",
         "Converging; moving the shorter wall is the only move that can help (LC 11)."),
    ]
    drill = mo.ui.array(
        [
            mo.ui.radio(options=["Two pointers", "Hash map", "Sliding window", "Binary search"], label=f"**{k + 1}.** {q}", inline=True)
            for k, (q, _answer, _why) in enumerate(DRILL)
        ]
    )
    drill_check = mo.ui.run_button(label="Check my answers")
    mo.vstack([mo.md("### Drill: name the pattern before you code"), drill, drill_check])
    return DRILL, drill, drill_check


@app.cell
def _(DRILL, drill, drill_check, mo):
    mo.stop(not drill_check.value, mo.md("_Pick an answer for each, then press **Check my answers**._"))
    _rows, _score = [], 0
    for _k, ((_q, _answer, _why), _pick) in enumerate(zip(DRILL, drill.value)):
        _ok = _pick == _answer
        _score += _ok
        _rows.append(f"| {_k + 1} | {'✓' if _ok else '✗'} | {_pick or '—'} | {_answer} | {_why} |")
    mo.md(
        f"**{_score} / {len(DRILL)}.** Aim for 7 of 8 before moving on.\n\n"
        "| # | | You said | Answer | Why |\n| :--- | :--- | :--- | :--- | :--- |\n" + "\n".join(_rows)
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · See it: every pair is a cell in a grid

    A question like *which two numbers add to 14?* is a search over every pair (i, j) with i < j. Lay those pairs out as the upper triangle of a grid: brute force visits every cell, about n²/2 of them.

    Two pointers starts in the **top-right corner** (smallest with largest) and, with one comparison, crosses off a **whole row or column**:

    - **Sum too small?** `a[i]` is already paired with its biggest available partner, so every pair in row *i* is too small. Row eliminated: `i += 1`.
    - **Sum too big?** Mirror image: column *j* is eliminated, `j -= 1`.

    Nothing discarded could have been the answer, and each step removes a line, so the walk ends within n − 1 steps. Container With Most Water uses the same grid with a different proof: the **shorter wall** caps every narrower container that keeps it.

    Pick a problem, edit the input, and drag the slider (or focus it and use the arrow keys).
    """)
    return


@app.cell
def _(mo):
    grid_problem = mo.ui.dropdown(
        options={"Two Sum II: a pair with sum = target": "twosum", "Container With Most Water": "container"},
        value="Two Sum II: a pair with sum = target",
        label="Problem",
    )
    grid_problem
    return (grid_problem,)


@app.cell
def _(grid_problem, mo):
    _defaults = {"twosum": "1, 2, 3, 4, 6, 8, 9", "container": "1, 8, 6, 2, 5, 4, 8, 3, 7"}
    grid_values = mo.ui.text(value=_defaults[grid_problem.value], label="Array", full_width=True)
    grid_target = mo.ui.number(start=-1000, stop=1000, value=14, label="Target")
    mo.hstack([grid_values, grid_target] if grid_problem.value == "twosum" else [grid_values], widths=[3, 1] if grid_problem.value == "twosum" else [1])
    return grid_target, grid_values


@app.cell
def _():
    def two_sum_grid_frames(a: list[int], target: int) -> list[dict]:
        n, cells, frames = len(a), {}, []
        i, j = 0, n - 1

        def snap(note, view, answer=False):
            computed = sum(1 for s in view.values() if (s if isinstance(s, str) else s[0]) in ("computed", "current", "answer"))
            eliminated = sum(1 for s in view.values() if s == "eliminated")
            frames.append(dict(i=i, j=j, cells=view, note=note, computed=computed, eliminated=eliminated, answer=answer))

        while i < j:
            s = a[i] + a[j]
            view = dict(cells)
            if s == target:
                view[(i, j)] = ("answer", str(s))
                snap(f"a[{i}] + a[{j}] = {a[i]} + {a[j]} = {s}, which is the target. Found after computing only a few cells.", view, True)
                return frames
            view[(i, j)] = ("current", str(s))
            if s < target:
                snap(f"{a[i]} + {a[j]} = {s} < {target}. {a[i]} is already paired with its biggest partner, so every pair in row {i} is too small: drop the row, i += 1.", view)
                cells[(i, j)] = ("computed", str(s))
                for jj in range(i + 1, j):
                    cells.setdefault((i, jj), "eliminated")
                i += 1
            else:
                snap(f"{a[i]} + {a[j]} = {s} > {target}. {a[j]} is already paired with its smallest partner, so every pair in column {j} is too big: drop the column, j -= 1.", view)
                cells[(i, j)] = ("computed", str(s))
                for ii in range(i + 1, j):
                    cells.setdefault((ii, j), "eliminated")
                j -= 1
        snap(f"i and j met: no pair adds up to {target}, and we proved it without computing most cells.", dict(cells))
        return frames

    def container_grid_frames(h: list[int]) -> list[dict]:
        n, cells, frames = len(h), {}, []
        i, j, best, best_pair = 0, n - 1, 0, None

        def snap(note, view):
            computed = sum(1 for s in view.values() if (s if isinstance(s, str) else s[0]) in ("computed", "current", "answer"))
            eliminated = sum(1 for s in view.values() if s == "eliminated")
            frames.append(dict(i=i, j=j, cells=view, note=note, computed=computed, eliminated=eliminated, best=best, best_pair=best_pair))

        while i < j:
            area = min(h[i], h[j]) * (j - i)
            if area > best:
                best, best_pair = area, (i, j)
            view = dict(cells)
            view[(i, j)] = ("current", str(area))
            if h[i] < h[j]:
                snap(f"Walls {h[i]} and {h[j]} hold {area}. The left wall is shorter: any narrower container that keeps it is capped at height {h[i]} and has less width, so row {i} can't beat {area}. Drop it: i += 1.", view)
                cells[(i, j)] = ("computed", str(area))
                for jj in range(i + 1, j):
                    cells.setdefault((i, jj), "eliminated")
                i += 1
            else:
                snap(f"Walls {h[i]} and {h[j]} hold {area}. The right wall is shorter (or equal): column {j} can't beat {area}. Drop it: j -= 1.", view)
                cells[(i, j)] = ("computed", str(area))
                for ii in range(i + 1, j):
                    cells.setdefault((ii, j), "eliminated")
                j -= 1
        view = dict(cells)
        if best_pair:
            view[best_pair] = ("answer", str(best))
        snap(f"The pointers met. Best area {best}, found with only {n - 1} of {n * (n - 1) // 2} pairs computed.", view)
        return frames

    return container_grid_frames, two_sum_grid_frames


@app.cell
def _(
    container_grid_frames,
    grid_problem,
    grid_target,
    grid_values,
    mo,
    parse_ints,
    two_sum_grid_frames,
):
    try:
        grid_input = parse_ints(grid_values.value, low=2)
        grid_error = None
    except ValueError as _err:
        grid_input, grid_error = [], str(_err)
    mo.stop(grid_error is not None, mo.callout(grid_error or "", kind="warn"))

    if grid_problem.value == "twosum":
        grid_input = sorted(grid_input)
        grid_frames = two_sum_grid_frames(grid_input, int(grid_target.value))
    else:
        grid_input = [abs(v) for v in grid_input]
        grid_frames = container_grid_frames(grid_input)
    grid_step = mo.ui.slider(0, max(len(grid_frames) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    grid_step
    return grid_frames, grid_input, grid_step


@app.cell
def _(
    array_view,
    bars_view,
    grid_frames,
    grid_input,
    grid_legend,
    grid_problem,
    grid_step,
    kv_view,
    mo,
    pair_grid_view,
):
    _k = min(grid_step.value, len(grid_frames) - 1)
    _f = grid_frames[_k]
    _n = len(grid_input)
    _total = _n * (_n - 1) // 2
    if grid_problem.value == "twosum":
        _left = array_view(grid_input, pointers={"i": _f["i"], "j": _f["j"]} if _f["i"] < _f["j"] or _f.get("answer") else {})
        _stats = {"pairs in the grid": _total, "computed": _f["computed"], "ruled out unseen": _f["eliminated"], "still unknown": _total - _f["computed"] - _f["eliminated"]}
    else:
        _left = bars_view(grid_input, pointers={"i": _f["i"], "j": _f["j"]} if _f["i"] < _f["j"] else {}, container=(_f["i"], _f["j"]) if _f["i"] < _f["j"] else None, unit=10, bar_px=24)
        _stats = {"pairs in the grid": _total, "computed": _f["computed"], "ruled out unseen": _f["eliminated"], "best area so far": _f["best"]}
    mo.vstack(
        [
            mo.hstack([mo.vstack([_left, kv_view(_stats)], align="center"), pair_grid_view(_n, _f["cells"])], justify="space-around", align="center", wrap=True),
            mo.md(f"**Step {_k + 1} of {len(grid_frames)}.** {_f['note']}"),
            grid_legend(),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Five shapes, and how to pick one

    "Two pointers" is an umbrella. In an interview, **name the shape** you're using. These five cover essentially every problem in the tier. Every shape is an **invariant** (what stays true between the pointers) plus a **move rule** (which pointer advances, and why that's safe). If you can't justify the move, you don't have a two-pointer solution yet.

    | Shape | Signature move | Loop guard | Canonical problems |
    | :--- | :--- | :--- | :--- |
    | **A · converging** | compare the ends, move the losing side inward | `while left < right` | 167, 125, 11, 42 |
    | **B · read / write** | scan with `read`, commit with `write` | `for read in range(n)` | 26, 27, 283 |
    | **C · partition** | three regions; `mid` classifies | `while mid <= high` | 75 |
    | **D · fix one (k-sum)** | pin an anchor, converge on the suffix | `for i … while left < right` | 15, 16, 18, 611 |
    | **E · two sequences** | one pointer per input | `while p2 >= 0` | 88, 392 |

    Pick a shape to step through it. The highlighted line is the one that decides the current step.
    """)
    return


@app.cell
def _():
    CODE_A = """
    def two_sum_sorted(nums: list[int], target: int) -> list[int]:
        left, right = 0, len(nums) - 1
        while left < right:                 # strict: a pair needs two distinct indices
            current = nums[left] + nums[right]
            if current == target:
                return [left, right]        # LeetCode 167 is 1-indexed: [left + 1, right + 1]
            if current < target:
                left += 1                   # need a bigger sum
            else:
                right -= 1                  # need a smaller sum
        return []
    """
    CODE_B = """
    def move_zeroes(nums: list[int]) -> None:
        write = 0                           # nums[:write] are the non-zeros, in order
        for read in range(len(nums)):
            if nums[read] != 0:
                nums[write], nums[read] = nums[read], nums[write]
                write += 1
    """
    CODE_C = """
    def sort_colors(nums: list[int]) -> None:
        low, mid, high = 0, 0, len(nums) - 1
        while mid <= high:                  # <= : index high is still unclassified
            if nums[mid] == 0:
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1                    # the value swapped in is already a 1
            elif nums[mid] == 1:
                mid += 1
            else:
                nums[mid], nums[high] = nums[high], nums[mid]
                high -= 1                   # mid does NOT move: the new value is unexamined
    """
    CODE_D = """
    def three_sum(nums: list[int]) -> list[list[int]]:
        nums.sort()
        n, results = len(nums), []
        for i in range(n - 2):
            if nums[i] > 0:
                break                       # sorted: three positives can't sum to 0
            if i > 0 and nums[i] == nums[i - 1]:
                continue                    # dedup 1: same anchor as last time
            left, right = i + 1, n - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                if total < 0:
                    left += 1
                elif total > 0:
                    right -= 1
                else:
                    results.append([nums[i], nums[left], nums[right]])
                    left += 1
                    right -= 1
                    while left < right and nums[left] == nums[left - 1]:
                        left += 1           # dedup 2: identical left partner
                    while left < right and nums[right] == nums[right + 1]:
                        right -= 1          # dedup 3: identical right partner
        return results
    """
    CODE_E = """
    def merge(nums1: list[int], m: int, nums2: list[int], n: int) -> None:
        p1, p2, write = m - 1, n - 1, m + n - 1
        while p2 >= 0:                      # nums2 used up => the rest of nums1 is in place
            if p1 >= 0 and nums1[p1] > nums2[p2]:
                nums1[write] = nums1[p1]
                p1 -= 1
            else:
                nums1[write] = nums2[p2]
                p2 -= 1
            write -= 1
    """
    import textwrap as _textwrap

    SHAPES = {
        "A · converging: Two Sum II": ("A", _textwrap.dedent(CODE_A).strip("\n"), "2, 7, 11, 15, 18", 26),
        "B · read / write: Move Zeroes": ("B", _textwrap.dedent(CODE_B).strip("\n"), "0, 1, 0, 3, 12", None),
        "C · partition: Sort Colors": ("C", _textwrap.dedent(CODE_C).strip("\n"), "2, 0, 2, 1, 1, 0", None),
        "D · fix one: 3Sum": ("D", _textwrap.dedent(CODE_D).strip("\n"), "-1, 0, 1, 2, -1, -4", None),
        "E · two sequences: Merge Sorted Array": ("E", _textwrap.dedent(CODE_E).strip("\n"), "1, 2, 3 | 2, 5, 6", None),
    }
    return (SHAPES,)


@app.cell
def _(line_of):
    def frames_converging(nums, target, code):
        frames, left, right = [], 0, len(nums) - 1
        frames.append(dict(arr=nums, pointers={"left": left, "right": right}, line=line_of(code, "left, right = 0"),
                           note="Start at both ends: the smallest value with the largest.", state={"target": target}))
        while left < right:
            current = nums[left] + nums[right]
            state = {"target": target, "current": current}
            if current == target:
                frames.append(dict(arr=nums, pointers={"left": left, "right": right}, marks={left: "hit", right: "hit"},
                                   line=line_of(code, "return [left, right]"), note=f"{nums[left]} + {nums[right]} = {target}: found.", state=state))
                return frames
            if current < target:
                frames.append(dict(arr=nums, pointers={"left": left, "right": right}, marks={left: "bad"}, line=line_of(code, "left += 1"),
                                   note=f"{nums[left]} + {nums[right]} = {current} < {target}: even the biggest partner is too small for {nums[left]}, so drop it.", state=state))
                left += 1
            else:
                frames.append(dict(arr=nums, pointers={"left": left, "right": right}, marks={right: "bad"}, line=line_of(code, "right -= 1"),
                                   note=f"{nums[left]} + {nums[right]} = {current} > {target}: even the smallest partner is too big for {nums[right]}, so drop it.", state=state))
                right -= 1
        frames.append(dict(arr=nums, pointers={"left": left, "right": right}, line=line_of(code, "return []"),
                           note="The pointers met: no pair works.", state={"target": target}))
        return frames

    def frames_read_write(nums, code):
        nums, frames, write = list(nums), [], 0

        def regions(read):
            marks = {k: "hit" for k in range(write)}
            marks.update({k: "warn" for k in range(write, read)})
            return marks

        frames.append(dict(arr=list(nums), pointers={"write": 0}, line=line_of(code, "write = 0"),
                           note="Green = final (the kept non-zeros). Amber = junk waiting to be overwritten. Everything from read on is untouched.", state={}))
        for read in range(len(nums)):
            if nums[read] != 0:
                frames.append(dict(arr=list(nums), pointers={"read": read, "write": write}, marks=regions(read), line=line_of(code, "nums[write], nums[read] ="),
                                   note=f"nums[{read}] = {nums[read]} is kept: swap it into position {write}, then write += 1.", state={"read": read, "write": write}))
                nums[write], nums[read] = nums[read], nums[write]
                write += 1
            else:
                frames.append(dict(arr=list(nums), pointers={"read": read, "write": write}, marks=regions(read), line=line_of(code, "if nums[read] != 0"),
                                   note=f"nums[{read}] is 0: read moves on, write waits.", state={"read": read, "write": write}))
        frames.append(dict(arr=list(nums), pointers={"write": write}, marks={k: "hit" for k in range(write)}, line=line_of(code, "write += 1"),
                           note="Done: non-zeros in their original order, zeros at the end. It's a swap, not a copy, so no stale values are left behind.", state={"write": write}))
        return frames

    def frames_partition(nums, code):
        nums, frames = list(nums), []
        low, mid, high = 0, 0, len(nums) - 1

        def regions():
            marks = {k: "focus" for k in range(low)}
            marks.update({k: "done" for k in range(low, mid)})
            marks.update({k: "warn" for k in range(high + 1, len(nums))})
            return marks

        while mid <= high:
            state = {"low": low, "mid": mid, "high": high}
            if nums[mid] == 0:
                frames.append(dict(arr=list(nums), pointers={"low": low, "mid": mid, "high": high}, marks=regions(), line=line_of(code, "nums[low], nums[mid] ="),
                                   note=f"nums[mid] = 0: swap it to low. The value that comes back is from the scanned middle, so it's a 1 and mid can advance.", state=state))
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1
            elif nums[mid] == 1:
                frames.append(dict(arr=list(nums), pointers={"low": low, "mid": mid, "high": high}, marks=regions(), line=line_of(code, "elif nums[mid] == 1"),
                                   note="nums[mid] = 1: already in the middle region, mid += 1.", state=state))
                mid += 1
            else:
                frames.append(dict(arr=list(nums), pointers={"low": low, "mid": mid, "high": high}, marks=regions(), line=line_of(code, "nums[mid], nums[high] ="),
                                   note="nums[mid] = 2: swap it to high. The value that comes back is unexamined, so mid stays put.", state=state))
                nums[mid], nums[high] = nums[high], nums[mid]
                high -= 1
        frames.append(dict(arr=list(nums), pointers={"low": low, "mid": mid, "high": high}, marks=regions(), line=line_of(code, "while mid <= high"),
                           note="mid passed high: the unknown region is empty. Indigo = 0s, grey = 1s, amber = 2s.", state={"low": low, "mid": mid, "high": high}))
        return frames

    def frames_three_sum(nums, code):
        nums = sorted(nums)
        frames, n, results = [], len(nums), []
        frames.append(dict(arr=nums, pointers={}, line=line_of(code, "nums.sort()"),
                           note=f"Sort first: it enables elimination, groups duplicates, and makes each triplet come out in order.", state={"results": []}))
        for i in range(n - 2):
            if nums[i] > 0:
                frames.append(dict(arr=nums, pointers={"anchor": i}, line=line_of(code, "break"),
                                   note="The anchor is positive, and so is everything after it: no zero sum is possible. Stop.", state={"results": list(results)}))
                break
            if i > 0 and nums[i] == nums[i - 1]:
                frames.append(dict(arr=nums, pointers={"anchor": i}, marks={i: "skip"}, line=line_of(code, "continue"),
                                   note=f"Dedup 1: anchor {nums[i]} is the same as the previous anchor, which already found every triplet it could. Skip.", state={"results": list(results)}))
                continue
            left, right = i + 1, n - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                ptrs = {"anchor": i, "left": left, "right": right}
                state = {"total": total, "results": list(results)}
                if total < 0:
                    frames.append(dict(arr=nums, pointers=ptrs, line=line_of(code, "left += 1"), note=f"{nums[i]} + {nums[left]} + {nums[right]} = {total} < 0: need more, left += 1.", state=state))
                    left += 1
                elif total > 0:
                    frames.append(dict(arr=nums, pointers=ptrs, line=line_of(code, "right -= 1"), note=f"{nums[i]} + {nums[left]} + {nums[right]} = {total} > 0: need less, right -= 1.", state=state))
                    right -= 1
                else:
                    results.append([nums[i], nums[left], nums[right]])
                    frames.append(dict(arr=nums, pointers=ptrs, marks={i: "hit", left: "hit", right: "hit"}, line=line_of(code, "results.append"),
                                       note=f"Hit: [{nums[i]}, {nums[left]}, {nums[right]}]. Record it and move both pointers; each endpoint's partner is used up.", state={"total": total, "results": list(results)}))
                    left += 1
                    right -= 1
                    while left < right and nums[left] == nums[left - 1]:
                        frames.append(dict(arr=nums, pointers={"anchor": i, "left": left, "right": right}, marks={left: "skip"}, line=line_of(code, "dedup 2"),
                                           note=f"Dedup 2: {nums[left]} is the same left value as the triplet we just recorded. Skip it.", state={"results": list(results)}))
                        left += 1
                    while left < right and nums[right] == nums[right + 1]:
                        frames.append(dict(arr=nums, pointers={"anchor": i, "left": left, "right": right}, marks={right: "skip"}, line=line_of(code, "dedup 3"),
                                           note=f"Dedup 3: {nums[right]} is the same right value as before. Skip it.", state={"results": list(results)}))
                        right -= 1
        frames.append(dict(arr=nums, pointers={}, line=line_of(code, "return results"), note=f"Done: {len(results)} unique triplet(s).", state={"results": list(results)}))
        return frames

    def frames_merge(nums1_values, nums2, code):
        m, n = len(nums1_values), len(nums2)
        nums1 = list(nums1_values) + [0] * n
        frames = []
        p1, p2, write = m - 1, n - 1, m + n - 1
        frames.append(dict(arr=list(nums1), pointers={"p1": p1, "write": write}, arr2=nums2, pointers2={"p2": p2}, line=line_of(code, "p1, p2, write ="),
                           note="nums1 has n spare slots at the end. Write from the back, so we never overwrite a value we haven't read.", state={}))
        while p2 >= 0:
            if p1 >= 0 and nums1[p1] > nums2[p2]:
                frames.append(dict(arr=list(nums1), pointers={"p1": p1, "write": write}, arr2=nums2, pointers2={"p2": p2}, line=line_of(code, "nums1[write] = nums1[p1]"),
                                   note=f"{nums1[p1]} > {nums2[p2]}: the larger value goes to the back, nums1[{write}] = {nums1[p1]}.", state={}))
                nums1[write] = nums1[p1]
                p1 -= 1
            else:
                frames.append(dict(arr=list(nums1), pointers={"p1": p1, "write": write}, arr2=nums2, pointers2={"p2": p2}, line=line_of(code, "nums1[write] = nums2[p2]"),
                                   note=f"nums2[{p2}] = {nums2[p2]} is at least as big: nums1[{write}] = {nums2[p2]}.", state={}))
                nums1[write] = nums2[p2]
                p2 -= 1
            write -= 1
        frames.append(dict(arr=list(nums1), pointers={}, arr2=nums2, pointers2={}, line=line_of(code, "while p2 >= 0"),
                           note="nums2 is used up. Whatever is left of nums1 was already in place.", state={}))
        return frames

    return (
        frames_converging,
        frames_merge,
        frames_partition,
        frames_read_write,
        frames_three_sum,
    )


@app.cell
def _(SHAPES, mo):
    shape_pick = mo.ui.dropdown(options=list(SHAPES), value="A · converging: Two Sum II", label="Shape")
    shape_pick
    return (shape_pick,)


@app.cell
def _(SHAPES, mo, shape_pick):
    _kind, _code, _default, _target = SHAPES[shape_pick.value]
    shape_values = mo.ui.text(value=_default, label="Input" + (" (nums1 | nums2)" if _kind == "E" else ""), full_width=True)
    shape_target = mo.ui.number(start=-1000, stop=1000, value=_target or 0, label="Target")
    mo.hstack([shape_values, shape_target], widths=[3, 1]) if _kind == "A" else shape_values
    return shape_target, shape_values


@app.cell
def _(
    SHAPES,
    frames_converging,
    frames_merge,
    frames_partition,
    frames_read_write,
    frames_three_sum,
    mo,
    parse_ints,
    shape_pick,
    shape_target,
    shape_values,
):
    shape_kind, shape_code = SHAPES[shape_pick.value][:2]
    try:
        if shape_kind == "E":
            _left_text, _, _right_text = shape_values.value.partition("|")
            _nums1 = sorted(parse_ints(_left_text, low=1, high=8))
            _nums2 = sorted(parse_ints(_right_text, low=1, high=8))
            shape_frames = frames_merge(_nums1, _nums2, shape_code)
        else:
            _nums = parse_ints(shape_values.value, low=2, high=14)
            if shape_kind == "A":
                shape_frames = frames_converging(sorted(_nums), int(shape_target.value), shape_code)
            elif shape_kind == "B":
                shape_frames = frames_read_write(_nums, shape_code)
            elif shape_kind == "C":
                mo.stop(any(v not in (0, 1, 2) for v in _nums), mo.callout("Sort Colors takes only 0, 1 and 2.", kind="warn"))
                shape_frames = frames_partition(_nums, shape_code)
            else:
                shape_frames = frames_three_sum(_nums, shape_code)
        _error = None
    except ValueError as _err:
        shape_frames, _error = [], str(_err)
    mo.stop(_error is not None, mo.callout(_error or "", kind="warn"))
    shape_step = mo.ui.slider(0, max(len(shape_frames) - 1, 1), value=0, label="Step", full_width=True, show_value=True)
    shape_step
    return shape_code, shape_frames, shape_step


@app.cell
def _(
    array_view,
    code_view,
    kv_view,
    mo,
    shape_code,
    shape_frames,
    shape_step,
):
    _k = min(shape_step.value, len(shape_frames) - 1)
    _f = shape_frames[_k]
    _arrays = [array_view(_f["arr"], pointers=_f["pointers"], marks=_f.get("marks"), cell_px=36 if len(_f["arr"]) > 10 else 44)]
    if "arr2" in _f:
        _arrays = [mo.md("`nums1`"), _arrays[0], mo.md("`nums2`"), array_view(_f["arr2"], pointers=_f["pointers2"])]
    _state = {k: v for k, v in _f["state"].items()}
    mo.vstack(
        [
            mo.hstack(
                [mo.vstack([*_arrays, kv_view(_state) if _state else mo.md("")]), code_view(shape_code, active=_f["line"])],
                align="start",
                wrap=True,
            ),
            mo.md(f"**Step {_k + 1} of {len(shape_frames)}.** {_f['note']}"),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · Brute force → bottleneck → pointers

    Say the journey out loud in an interview; teleporting to the optimum reads as memorisation.

    **Brute force (pseudo code).** For every i, for every j > i, check a[i] + a[j]. That's n(n − 1)/2 checks: O(n²).

    **Bottleneck.** Most of those checks are *provably pointless*: once a[i] + a[j] is too small, every partner of a[i] smaller than a[j] is too small as well, yet brute force checks them anyway.

    **Pointers.** Use sorted order to discard a whole row or column per comparison: at most n − 1 comparisons, O(n). If you sorted the input yourself, say **"O(n log n) overall, dominated by the sort"**.

    Measured on random sorted arrays where no pair works (the worst case for both):
    """)
    return


@app.cell
def _(mo, random):
    def _brute_checks(a, target):
        checks = 0
        for _i in range(len(a)):
            for _j in range(_i + 1, len(a)):
                checks += 1
                if a[_i] + a[_j] == target:
                    return checks
        return checks

    def _pointer_steps(a, target):
        steps, i, j = 0, 0, len(a) - 1
        while i < j:
            steps += 1
            s = a[i] + a[j]
            if s == target:
                return steps
            if s < target:
                i += 1
            else:
                j -= 1
        return steps

    _rng = random.Random(7)
    _rows = []
    for _n in (10, 100, 1000):
        _a = sorted(_rng.sample(range(0, 10 * _n, 2), _n))  # all even, so an odd target never matches
        _b, _p = _brute_checks(_a, 1), _pointer_steps(_a, 1)
        _rows.append(f"| {_n:,} | {_b:,} | {_p:,} | {_b / _p:,.0f}× |")
    mo.md(
        "| n | brute-force checks | pointer steps | brute / pointers |\n| :--- | :--- | :--- | :--- |\n"
        + "\n".join(_rows)
        + "\n\n10× more data costs brute force **100×** more work and the pointers only **10×**. That's the difference between O(n²) and O(n)."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5 · Practice: worked → faded → solo

    Cap each problem at 25 minutes. Past that, read the solution, close it, and rewrite from scratch tomorrow. Your code runs right here; **Run tests** checks it against normal cases *and* the edge cases that break most first attempts.
    """)
    return


@app.cell
def _(Case):
    CASES_125 = [
        Case(("A man, a plan, a canal: Panama",), True),
        Case(("race a car",), False),
        Case((" ",), True, label="only a space"),
        Case((".,",), True, label="no alphanumerics at all"),
        Case(("0P",), False, label="digits count, case doesn't"),
        Case(("Ab, Ba!",), True),
    ]
    SOLUTION_125 = '''
    def is_palindrome(s: str) -> bool:
        left, right = 0, len(s) - 1
        while left < right:
            if not s[left].isalnum():
                left += 1                   # skip, then re-check the loop condition
            elif not s[right].isalnum():
                right -= 1
            else:
                if s[left].lower() != s[right].lower():
                    return False
                left += 1
                right -= 1
        return True
    '''
    STUB_125 = '''def is_palindrome(s: str) -> bool:
        # Converging pointers. Skip characters that aren't letters or digits,
        # compare case-insensitively, and keep every skip inside the same loop.
        ...
    '''
    CASES_26 = [
        Case(([1, 1, 2],), (2, [1, 2])),
        Case(([0, 0, 1, 1, 1, 2, 2, 3, 3, 4],), (5, [0, 1, 2, 3, 4])),
        Case(([7],), (1, [7]), label="single element"),
        Case(([],), (0, []), label="empty"),
        Case(([2, 2, 2, 2],), (1, [2]), label="all equal"),
    ]
    HARNESS_26 = '''

    def _judge(nums):
        k = remove_duplicates(nums)
        return k, nums[:k]
    '''
    SOLUTION_26 = '''
    def remove_duplicates(nums: list[int]) -> int:
        if not nums:
            return 0
        write = 1                           # nums[:write] holds the unique values so far
        for read in range(1, len(nums)):
            if nums[read] != nums[write - 1]:
                nums[write] = nums[read]
                write += 1
        return write
    '''
    STUB_26 = '''def remove_duplicates(nums: list[int]) -> int:
        # Read/write pointers on a SORTED array. Return k; nums[:k] must hold the unique values.
        if not nums:
            return 0
        write = 1                           # nums[:write] holds the unique values so far
        for read in range(1, len(nums)):
            if ...:                         # when is nums[read] a value we haven't kept yet?
                ...                         # keep it, then move the write frontier
        return write
    '''
    CASES_15 = [
        Case(([-1, 0, 1, 2, -1, -4],), [[-1, -1, 2], [-1, 0, 1]]),
        Case(([0, 1, 1],), []),
        Case(([0, 0, 0],), [[0, 0, 0]]),
        Case(([0, 0, 0, 0],), [[0, 0, 0]], label="[0,0,0,0]: one triplet, not four"),
        Case(([-2, 0, 0, 2, 2],), [[-2, 0, 2]], label="two paths to one triplet"),
        Case(([-4, -2, -2, 0, 2, 2, 4],), [[-4, 0, 4], [-4, 2, 2], [-2, -2, 4], [-2, 0, 2]]),
        Case(([],), []),
    ]
    return (
        CASES_125,
        CASES_15,
        CASES_26,
        HARNESS_26,
        SOLUTION_125,
        SOLUTION_26,
        STUB_125,
        STUB_26,
    )


@app.cell
def _(SHAPES):
    SOLUTION_3SUM = "\n".join(SHAPES["D · fix one: 3Sum"][1].splitlines())
    STUB_15 = '''def three_sum(nums: list[int]) -> list[list[int]]:
        # Sort, pin an anchor, run converging pointers on the suffix.
        # Unique triplets only: think about the three places duplicates sneak in.
        ...
    '''

    def norm_triplets(result):
        return sorted(sorted(t) for t in result)

    return SOLUTION_3SUM, STUB_15, norm_triplets


@app.cell
def _(SOLUTION_125, STUB_125, mo, solution):
    ex125_editor = mo.ui.code_editor(value=STUB_125, language="python", min_height=190)
    ex125_run = mo.ui.run_button(label="Run tests")
    mo.vstack(
        [
            mo.md(
                "### Worked: LC 125 Valid Palindrome\n\n"
                "After lowercasing and ignoring everything that isn't a letter or digit, does the string read the same both ways? "
                "This is shape A with a **skip rule**: each skip is an `elif` branch of the same loop, never a nested `while` (bug 2 in section 6 shows why). "
                "Read the solution first, close it, then type it from memory."
            ),
            solution(SOLUTION_125, "Show the worked solution"),
            ex125_editor,
            ex125_run,
        ]
    )
    return ex125_editor, ex125_run


@app.cell
def _(CASES_125, check, ex125_editor, ex125_run, mo):
    mo.stop(not ex125_run.value, mo.md("_Write your solution above, then press **Run tests**._"))
    check(ex125_editor.value, "is_palindrome", CASES_125)
    return


@app.cell
def _(SOLUTION_26, STUB_26, mo, solution):
    ex26_editor = mo.ui.code_editor(value=STUB_26, language="python", min_height=230)
    ex26_run = mo.ui.run_button(label="Run tests")
    mo.vstack(
        [
            mo.md(
                "### Faded: LC 26 Remove Duplicates from Sorted Array\n\n"
                "The skeleton is filled in; complete the two `...` lines. The tests check both the returned `k` **and** that `nums[:k]` holds the unique values in order."
            ),
            ex26_editor,
            ex26_run,
            solution(SOLUTION_26),
        ]
    )
    return ex26_editor, ex26_run


@app.cell
def _(CASES_26, HARNESS_26, check, ex26_editor, ex26_run, mo):
    mo.stop(not ex26_run.value, mo.md("_Fill in the blanks, then press **Run tests**._"))
    check(ex26_editor.value + HARNESS_26, "_judge", CASES_26)
    return


@app.cell
def _(SOLUTION_3SUM, STUB_15, mo, solution):
    ex15_editor = mo.ui.code_editor(value=STUB_15, language="python", min_height=230)
    ex15_run = mo.ui.run_button(label="Run tests")
    mo.vstack(
        [
            mo.md(
                "### Solo: LC 15 3Sum\n\n"
                "Return every **unique** triplet that sums to zero, in any order. From a blank function, no notes. "
                "Before you type, say the invariant, the move rule and the three dedup points out loud. Say the edge cases too: `[]`, `[0,0,0,0]`, all positive."
            ),
            ex15_editor,
            ex15_run,
            solution(SOLUTION_3SUM),
        ]
    )
    return ex15_editor, ex15_run


@app.cell
def _(CASES_15, check, ex15_editor, ex15_run, mo, norm_triplets):
    mo.stop(not ex15_run.value, mo.md("_Write it from scratch, then press **Run tests**._"))
    check(ex15_editor.value, "three_sum", CASES_15, normalise=norm_triplets)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Next rungs on the ladder:** 167 Two Sum II · 977 Squares of a Sorted Array · 283 Move Zeroes · 88 Merge Sorted Array · 392 Is Subsequence · 11 Container With Most Water · 75 Sort Colors · 16 3Sum Closest · 611 Valid Triangle Number · 18 4Sum. The stretch anchor, **42 Trapping Rain Water**, has its own [question notebook](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/notebooks/lc0042_trapping_rain_water.html) (`questions/lc0042_trapping_rain_water.py`).
    """)
    return


@app.cell
def _():
    BUGS = [
        ("1 · `while left <= right` in a pair search",
         "The pointers can land on the same index, so an element pairs with itself.",
         "def f(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        s = nums[left] + nums[right]\n        if s == target:\n            return [left, right]\n        if s < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n",
         "def f(nums, target):\n    left, right = 0, len(nums) - 1\n    while left < right:\n        s = nums[left] + nums[right]\n        if s == target:\n            return [left, right]\n        if s < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n",
         ([1, 2, 3, 4], 8), None),
        ("2 · Nested `while` skips with no bound check",
         "A pointer runs off the end of a string with no letters or digits.",
         "def f(s):\n    left, right = 0, len(s) - 1\n    while left < right:\n        while not s[left].isalnum():\n            left += 1\n        while not s[right].isalnum():\n            right -= 1\n        if s[left].lower() != s[right].lower():\n            return False\n        left += 1\n        right -= 1\n    return True\n",
         "def f(s):\n    left, right = 0, len(s) - 1\n    while left < right:\n        if not s[left].isalnum():\n            left += 1\n        elif not s[right].isalnum():\n            right -= 1\n        else:\n            if s[left].lower() != s[right].lower():\n                return False\n            left += 1\n            right -= 1\n    return True\n",
         (".,",), None),
        ("3 · `while mid < high` in the partition",
         "The element sitting at high is never classified.",
         "def f(nums):\n    low, mid, high = 0, 0, len(nums) - 1\n    while mid < high:\n        if nums[mid] == 0:\n            nums[low], nums[mid] = nums[mid], nums[low]\n            low += 1\n            mid += 1\n        elif nums[mid] == 1:\n            mid += 1\n        else:\n            nums[mid], nums[high] = nums[high], nums[mid]\n            high -= 1\n    return nums\n",
         "def f(nums):\n    low, mid, high = 0, 0, len(nums) - 1\n    while mid <= high:\n        if nums[mid] == 0:\n            nums[low], nums[mid] = nums[mid], nums[low]\n            low += 1\n            mid += 1\n        elif nums[mid] == 1:\n            mid += 1\n        else:\n            nums[mid], nums[high] = nums[high], nums[mid]\n            high -= 1\n    return nums\n",
         ([2, 0, 1],), None),
        ("4 · Advancing `mid` after a 2-swap",
         "The value swapped in from the right was never examined. It passes on many inputs, which is how it survives casual testing.",
         "def f(nums):\n    low, mid, high = 0, 0, len(nums) - 1\n    while mid <= high:\n        if nums[mid] == 0:\n            nums[low], nums[mid] = nums[mid], nums[low]\n            low += 1\n            mid += 1\n        elif nums[mid] == 1:\n            mid += 1\n        else:\n            nums[mid], nums[high] = nums[high], nums[mid]\n            high -= 1\n            mid += 1\n    return nums\n",
         "def f(nums):\n    low, mid, high = 0, 0, len(nums) - 1\n    while mid <= high:\n        if nums[mid] == 0:\n            nums[low], nums[mid] = nums[mid], nums[low]\n            low += 1\n            mid += 1\n        elif nums[mid] == 1:\n            mid += 1\n        else:\n            nums[mid], nums[high] = nums[high], nums[mid]\n            high -= 1\n    return nums\n",
         ([1, 2, 0],), None),
        ("5 · 3Sum with no duplicate skipping",
         "The same triplet is reached through different index paths.",
         "def f(nums):\n    nums.sort()\n    res = []\n    for i in range(len(nums) - 2):\n        left, right = i + 1, len(nums) - 1\n        while left < right:\n            t = nums[i] + nums[left] + nums[right]\n            if t < 0:\n                left += 1\n            elif t > 0:\n                right -= 1\n            else:\n                res.append([nums[i], nums[left], nums[right]])\n                left += 1\n                right -= 1\n    return res\n",
         None, ([-1, 0, 1, 2, -1, -4],), "three_sum"),
        ("6 · Move Zeroes by copying instead of swapping",
         "The tail is never cleared, so stale values are stranded there. The prefix is right, which hides it.",
         "def f(nums):\n    write = 0\n    for read in range(len(nums)):\n        if nums[read] != 0:\n            nums[write] = nums[read]\n            write += 1\n    return nums\n",
         "def f(nums):\n    write = 0\n    for read in range(len(nums)):\n        if nums[read] != 0:\n            nums[write], nums[read] = nums[read], nums[write]\n            write += 1\n    return nums\n",
         ([0, 1, 0, 3, 12],), None),
        ("7 · Merging front-to-back, in place",
         "Writing forward into nums1 overwrites values you still need to read.",
         "def f(nums1, m, nums2, n):\n    p1 = p2 = write = 0\n    while p2 < n:\n        if p1 < m and nums1[p1] <= nums2[p2]:\n            nums1[write] = nums1[p1]\n            p1 += 1\n        else:\n            nums1[write] = nums2[p2]\n            p2 += 1\n        write += 1\n    return nums1\n",
         "def f(nums1, m, nums2, n):\n    p1, p2, write = m - 1, n - 1, m + n - 1\n    while p2 >= 0:\n        if p1 >= 0 and nums1[p1] > nums2[p2]:\n            nums1[write] = nums1[p1]\n            p1 -= 1\n        else:\n            nums1[write] = nums2[p2]\n            p2 -= 1\n        write -= 1\n    return nums1\n",
         ([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3), None),
        ("8 · Sorting, then returning indices (unsorted Two Sum)",
         "The pair of values is right, but the positions refer to the sorted copy.",
         "def f(nums, target):\n    nums = sorted(nums)\n    left, right = 0, len(nums) - 1\n    while left < right:\n        s = nums[left] + nums[right]\n        if s == target:\n            return [left, right]\n        if s < target:\n            left += 1\n        else:\n            right -= 1\n    return []\n",
         "def f(nums, target):\n    seen = {}\n    for i, x in enumerate(nums):\n        if target - x in seen:\n            return [seen[target - x], i]\n        seen[x] = i\n    return []\n",
         ([3, 2, 4], 6), None),
    ]

    def run_snippet(code: str, args: tuple, name: str = "f") -> str:
        import copy as _copy

        _ns: dict = {}
        exec(code, _ns)
        try:
            return repr(_ns[name](*_copy.deepcopy(args)))
        except Exception as _exc:
            return f"{type(_exc).__name__}: {_exc}"

    return BUGS, run_snippet


@app.cell
def _(BUGS, SOLUTION_3SUM, mo, run_snippet):
    _lines = ["| Bug | Input | Buggy output | Correct output |", "| :--- | :--- | :--- | :--- |"]
    _details = {}
    for _title, _why, _buggy, _correct, _args, _name in BUGS:
        # a missing correct version means "use the shape-D 3Sum template"
        _got_bad = run_snippet(_buggy, _args)
        _got_good = run_snippet(_correct or SOLUTION_3SUM, _args, _name or "f")
        _shown = ", ".join(repr(a) for a in _args)
        _lines.append(f"| {_title} | `{_shown}` | `{_got_bad}` | `{_got_good}` |")
        _details[_title.replace("`", "")] = mo.md(f"{_why}\n\n```python\n{_buggy}```")
    mo.vstack(
        [
            mo.md(
                "## 6 · Traps: the bugs, with their actual wrong answers\n\n"
                "Every output below is computed live by running the buggy code next to the correct one, so each bug fails on a small input you can keep in your head."
            ),
            mo.md("\n".join(_lines)),
            mo.accordion(_details),
            mo.md(
                "**Two Python costs that hide inside a loop.** `list.pop(0)`, `del nums[0]` and `nums[1:]` are O(n) each, and they quietly turn an O(n) pass into O(n²). "
                "Use indices, or `collections.deque` if you truly need to pop from the front. And never mutate a list while iterating over it: "
                "`for x in nums: nums.remove(x)` on `[0, 0, 1]` leaves `[0, 1]`."
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7 · Recall: close everything and answer from memory

    Say each answer out loud (or write it down) *before* opening it. Pulling it out of memory is what makes it stick; re-reading only feels productive.
    """)
    return


@app.cell
def _(mo):
    mo.accordion(
        {
            "1. What are the invariant and the move rule for converging pointers on a sorted pair search?": mo.md(
                "Invariant: if an answer exists, it lies within `nums[left..right]`. Move: sum too small, `left += 1` (row eliminated); too big, `right -= 1` (column eliminated). Each step discards only pairs proven impossible."
            ),
            "2. Why is moving the shorter wall safe in Container With Most Water?": mo.md(
                "Every narrower container that keeps the shorter wall is capped at its height and has less width, so none can beat the area you just measured. Moving the taller wall keeps the same cap and loses width: it can never help."
            ),
            "3. Where are 3Sum's three dedup points, and why does the anchor compare backwards?": mo.md(
                "Anchor: `nums[i] == nums[i-1]`, which keeps the *first* copy, so its suffix still contains the other copies. After a hit: skip equal `left` values and equal `right` values, both guarded by `left < right`. Comparing forward (`nums[i+1]`) keeps the last copy and loses triplets like [-1, -1, 2]."
            ),
            "4. When does this pattern NOT apply?": mo.md(
                "When you can't order the data without destroying the answer, as in unsorted Two Sum returning indices (use a hash map), or when the contents between the pointers matter (sliding window)."
            ),
            "5. Which loops use `<` and which `<=`?": mo.md(
                "Pair search: `left < right`, since a pair needs two indices. Partition: `mid <= high`, because index `high` is still unclassified. Ask of every loop guard: is it deliberate?"
            ),
            "6. What's the honest complexity of 3Sum?": mo.md(
                "O(n²) time: n anchors × one O(n) sweep each, about n²/2 pointer moves. The sort's O(n log n) is dominated. Space: O(1) beyond the output (sorting may use O(log n) to O(n))."
            ),
        }
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8 · Go deeper

    - **Labs in this folder:** [Two Pointers Workbench](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/02-two-pointers/two-pointers-workbench.html) · [Two-Pointer Elimination](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/02-two-pointers/two-pointer-elimination.html) · [3Sum Dissected](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/DSA/02-two-pointers/3sum-dissected.html)
    - [Hello Interview: Two Pointers](https://www.hellointerview.com/learn/code/two-pointers/overview): animated walkthroughs of these exact problems
    - [USACO Guide: Two Pointers](https://usaco.guide/silver/two-pointers): the (value, index) trick for keeping indices while sorting
    - [Competitive Programmer's Handbook, Python edition](https://www2.compute.dtu.dk/courses/02110/2025/diverse/cses-book-python.pdf), ch. 8: the amortised argument

    **Next:** sliding window, the same two indices moving the same direction, where the contents between them finally matter.
    """)
    return


@app.cell
def _(
    BUGS,
    CASES_125,
    CASES_15,
    CASES_26,
    HARNESS_26,
    SHAPES,
    SOLUTION_125,
    SOLUTION_26,
    SOLUTION_3SUM,
    STUB_125,
    STUB_15,
    assert_cases,
    container_grid_frames,
    frames_merge,
    frames_partition,
    frames_read_write,
    frames_three_sum,
    norm_triplets,
    random,
    run_cases,
    run_snippet,
    two_sum_grid_frames,
):
    def test_answer_keys_pass():
        assert_cases(SOLUTION_125, "is_palindrome", CASES_125)
        assert_cases(SOLUTION_26 + HARNESS_26, "_judge", CASES_26)
        assert_cases(SOLUTION_3SUM, "three_sum", CASES_15, normalise=norm_triplets)

    def test_stubs_do_not_pass_yet():
        assert not all(r.passed for r in run_cases(STUB_125, "is_palindrome", CASES_125))
        assert not all(r.passed for r in run_cases(STUB_15, "three_sum", CASES_15, normalise=norm_triplets))

    def test_grid_frames_agree_with_brute_force():
        rng = random.Random(1)
        for _ in range(300):
            a = sorted(rng.sample(range(-20, 40), rng.randint(2, 12)))
            target = rng.randint(-30, 70)
            frames = two_sum_grid_frames(a, target)
            exists = any(a[i] + a[j] == target for i in range(len(a)) for j in range(i + 1, len(a)))
            assert frames[-1].get("answer", False) == exists
            h = [rng.randint(0, 12) for _ in range(rng.randint(2, 12))]
            best = max(min(h[i], h[j]) * (j - i) for i in range(len(h)) for j in range(i + 1, len(h)))
            assert container_grid_frames(h)[-1]["best"] == best

    def test_shape_frames_end_in_the_right_state():
        rng = random.Random(2)
        for _ in range(200):
            nums = [rng.choice([0, 0, 1, 2, 3]) for _ in range(rng.randint(2, 12))]
            moved = frames_read_write(nums, SHAPES["B · read / write: Move Zeroes"][1])[-1]["arr"]
            assert moved == [v for v in nums if v] + [0] * nums.count(0)
            colours = [rng.choice([0, 1, 2]) for _ in range(rng.randint(2, 12))]
            assert frames_partition(colours, SHAPES["C · partition: Sort Colors"][1])[-1]["arr"] == sorted(colours)
            triple = [rng.randint(-4, 4) for _ in range(rng.randint(3, 10))]
            brute = {tuple(sorted((triple[i], triple[j], triple[k])))
                     for i in range(len(triple)) for j in range(i + 1, len(triple)) for k in range(j + 1, len(triple))
                     if triple[i] + triple[j] + triple[k] == 0}
            got = frames_three_sum(triple, SHAPES["D · fix one: 3Sum"][1])[-1]["state"]["results"]
            assert sorted(map(tuple, got)) == sorted(brute) and len(got) == len(brute)
            one, two = sorted(rng.sample(range(20), 4)), sorted(rng.sample(range(20), 3))
            assert frames_merge(one, two, SHAPES["E · two sequences: Merge Sorted Array"][1])[-1]["arr"] == sorted(one + two)

    def test_every_gallery_bug_really_fails():
        for title, _why, buggy, correct, args, name in BUGS:
            assert run_snippet(buggy, args) != run_snippet(correct or SOLUTION_3SUM, args, name or "f"), title

    return


if __name__ == "__main__":
    app.run()

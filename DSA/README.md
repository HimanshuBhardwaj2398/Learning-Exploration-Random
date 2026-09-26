# DSA — labs & notes

Local copies of every interactive lab and plan from the **Coding practice** project. Open any `.html` file in a browser; it runs offline (fonts fall back if you're not online). Each row also links to the live version on claude.ai, which is the one that gets updated.

Study loop: **Spot it → See it → Template → Worked / Faded / Solo → Traps.** Each session: Read → See → Do → Recall, and the recall step is never cut.

## Map

| # | Pattern | Status | Anchor ladder |
| --- | --- | --- | --- |
| 01 | Arrays & hashing | Two labs (14 Sep) | 36 Valid Sudoku, 128 Longest Consecutive |
| 02 | Two pointers | Taught | 125 → 15 → 42 |
| 03 | Sliding window | Taught; LC 424 solo still open | 643 → 3 → 424 |
| 04 | Two pointers vs window | Comparison built | Twins: 167/209, 167/1, 209/862, 713/560, 283/1004, 881/1658, 392/567, 611/713 |
| — | Next up | — | Prefix sum, then binary search and stack |

## Files

### 01-arrays-hashing
| File | What it's for | Live |
| --- | --- | --- |
| [valid-sudoku-three-sets.html](01-arrays-hashing/valid-sudoku-three-sets.html) | Valid Sudoku as one question asked three times (row, column, box sets) | [open](https://claude.ai/artifact/C4hvXkrspgZJ3oJDkitezx) |
| [longest-consecutive-why-O-n.html](01-arrays-hashing/longest-consecutive-why-O-n.html) | Why the set-based Longest Consecutive Sequence is O(n), not O(n²) | [open](https://claude.ai/artifact/KaPJKVpdDM4mZyetPGxHuf) |

### 02-two-pointers
| File | What it's for | Live |
| --- | --- | --- |
| [two-pointers-workbench.html](02-two-pointers/two-pointers-workbench.html) | Five templates, six visualisers, bug gallery | [open](https://claude.ai/artifact/Hd56fc9MLui6AUt5Sxjumf) |
| [two-pointer-elimination.html](02-two-pointers/two-pointer-elimination.html) | Why each converging step safely discards a whole row or column (Container With Most Water) | [open](https://claude.ai/artifact/ThNyrhS2DyPaxC3NJbVwaD) |
| [3sum-dissected.html](02-two-pointers/3sum-dissected.html) | Fix one, two-pointer the rest, plus the dedup rules | [open](https://claude.ai/artifact/TYimuczmQqZ7nVAhz1UUZx) |

### 03-sliding-window
| File | What it's for | Live |
| --- | --- | --- |
| [sliding-window-workbench.html](03-sliding-window/sliding-window-workbench.html) | Fixed / longest / shortest shapes, need–have, the `if` vs `while` proof | [open](https://claude.ai/artifact/DDj3YdiHCGahAM149vgJE2) |

### 04-pointers-vs-window
| File | What it's for | Live |
| --- | --- | --- |
| [pointers-or-window.html](04-pointers-vs-window/pointers-or-window.html) | Both patterns on one pair grid, twin problems, the decision drill | [open](https://claude.ai/artifact/To4wXU3jpBo4FLz6vVB8RS) |
| [reading-plan.md](04-pointers-vs-window/reading-plan.md) | 5-session reading plan with spaced review (snapshot of the doc) | [open](https://claude.ai/artifact/UmkponGDnZHBzXBra7ubEs) |

### python-foundations
| File | What it's for | Live |
| --- | --- | --- |
| [rebinding-say-whee-decorators.html](python-foundations/rebinding-say-whee-decorators.html) | How a decorator is just name rebinding (`say_whee = deco(say_whee)`) | [open](https://claude.ai/artifact/AprBpx1k2Uu3pjEpoB41MS) |

## Key ideas to carry forward
- Both patterns are staircases through the (start, end) pair grid; each step deletes a row or column.
- Two pointers needs sorted order; a window needs monotone validity (e.g. no negatives). Can't sort and need positions → hash map. Negatives with a sum target → prefix sums (+ hash, or + deque for shortest).
- Same-direction pointers: if the gap is junk to overwrite it's read/write; if the gap is the answer it's a window.

## Conventions for new material
- One folder per pattern, numbered in study order: `05-prefix-sum/`, `06-binary-search/`, `07-stack/` …
- File names are kebab-case and say what the lab teaches.
- Your own solutions can live beside the labs, e.g. `02-two-pointers/solutions/lc15_3sum.py`.
- Links inside the labs still point at claude.ai; this README is the local map.

_Last synced: 26 Sep 2026._

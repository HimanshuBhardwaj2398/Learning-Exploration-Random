# DSA

> Coding-interview patterns and single-question deep dives in Python, each with a marimo notebook you can run in the browser.

Topics are numbered in study order. Each has a one-page README (spot-it cues, template, traps, ladder, review log) and a marimo notebook (visual step-throughs, brute force → optimal, practice with tests, recall). Some also have the original interactive labs and deep-dive **questions**. How a topic is run: [WORKFLOW.md](../WORKFLOW.md).

**Browse online:** [himanshubhardwaj2398.github.io/Learning-Exploration-Random](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/). The notebooks run Python in your browser.

## Topics

<!-- topics:start -->
| # | Topic | Kind | Status | Notebook | Also |
| --- | --- | --- | --- | --- | --- |
| 01 | [Arrays & hashing](01-arrays-hashing/README.md) | pattern | learning | [arrays_hashing.py](01-arrays-hashing/arrays_hashing.py) | [lab: Why It's O(n), Not O(n²)](01-arrays-hashing/longest-consecutive-why-O-n.html), [lab: Sudoku in three sets](01-arrays-hashing/valid-sudoku-three-sets.html) |
| 02 | [Two pointers](02-two-pointers/README.md) | pattern | practising | [two_pointers.py](02-two-pointers/two_pointers.py) | [LC 42 Trapping Rain Water](02-two-pointers/questions/lc0042_trapping_rain_water.py), [lab: 3Sum Dissected](02-two-pointers/3sum-dissected.html), [lab: Two-Pointer Elimination](02-two-pointers/two-pointer-elimination.html), [lab: Two Pointers Workbench](02-two-pointers/two-pointers-workbench.html) |
| 03 | [Sliding window](03-sliding-window/README.md) | pattern | practising | [sliding_window.py](03-sliding-window/sliding_window.py) | [lab: Sliding Window Workbench](03-sliding-window/sliding-window-workbench.html) |
| 04 | [Pointers or window?](04-pointers-vs-window/README.md) | comparison | learning | [pointers_vs_window.py](04-pointers-vs-window/pointers_vs_window.py) | [lab: Pointers or Window?](04-pointers-vs-window/pointers-or-window.html) |
<!-- topics:end -->

## Study loop
**Spot it → See it → Template → Worked / Faded / Solo → Traps → Recall.** Each session: Read → See → Do → Recall. If a session runs long, cut the reading, never the recall.

## Key ideas carried forward
- Two pointers and sliding window are both staircases through the (start, end) pair grid; each step deletes a row or column.
- Two pointers needs sorted order; a window needs monotone validity (e.g. no negatives). Can't sort and need positions → hash map. Negatives with a sum target → prefix sums (+ hash, or + deque for the shortest).
- Same-direction pointers: if the gap is junk to overwrite, it's read/write; if the gap is the answer, it's a window.
- A nested loop isn't automatically O(n²): bound the *total* work (amortisation), as in Longest Consecutive and every sliding window.

## Next up
Prefix sum (`python tools/new_topic.py pattern DSA "Prefix sum"`), then binary search and stack.

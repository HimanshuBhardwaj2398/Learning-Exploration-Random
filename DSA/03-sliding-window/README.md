# Sliding window

> Both pointers move the same way and you care about everything between them; each index enters and leaves the window once, so it's O(n).

Kind: pattern · Status: practising

**Notebook:** [sliding_window.py](sliding_window.py) (fixed-window counter, a grow/shrink/record explorer for five problems with a start/end staircase, the exactly-k trick, an if-vs-while experiment, negatives breaking it, a live bug gallery). Run `marimo edit DSA/03-sliding-window/sliding_window.py` locally, or open it on the site.

## Spot it
- **Contiguous** (subarray, substring, window of size k). *Subsequence* rules it out.
- A constraint checkable in **O(1) from running state** (sum, count, frequency dict, set size)
- **Optimise or count**: longest / shortest / how many / fixed k
- Legal only with **monotone validity**: negatives + sums → prefix sums instead

## Template
```python
start = best = 0
for end, x in enumerate(seq):
    add(x)                                   # grow
    while not valid():                       # longest: shrink while INVALID
        remove(seq[start]); start += 1
    best = max(best, end - start + 1)        # record AFTER the shrink
```
Shortest: `while valid(): best = min(best, end - start + 1); remove(...); start += 1` (record **inside**). Counting: `count += end - start + 1`. Exactly k: `at_most(k) - at_most(k - 1)`.

## Traps (the ones that bite)
- Longest records **after** shrinking; shortest records **inside** the shrink loop
- Fixed window: add incoming **and** drop outgoing; only record once the window has size k
- `end - start + 1`, never `end - start`
- Delete zero-count keys when `len(count)` is the condition
- Index jumps need `start = max(start, last[ch] + 1)`: start never moves back
- Return `0` / `""` when nothing qualifies

## Ladder
| # | Problem | Stage | Done |
| :--- | :--- | :--- | :--- |
| 643 | Maximum Average Subarray I | worked | |
| 3 | Longest Substring Without Repeating Characters | faded | |
| 424 | Longest Repeating Character Replacement | solo (open) | |
| 209, 438, 567, 1004, 904 | graded | graded | |
| 76, 239, 992, 862 | stretch | stretch | |

## Questions
<!-- question notebooks for this topic live in questions/; tools/new_topic.py adds them here -->

## Review log
Counted from the day this topic reaches `Status: solid`:
- [ ] +2 days: redo LC 424 from a blank file
- [ ] +5 days: LC 1658 and LC 76, then the drill in the pointers-vs-window notebook
- [ ] +12 days: two random rungs, unlabelled
- [ ] +26 days: mock round

## Resources
- Lab: [Sliding Window Workbench](sliding-window-workbench.html)
- [Hello Interview: fixed](https://www.hellointerview.com/learn/code/sliding-window/fixed-length) and [variable](https://www.hellointerview.com/learn/code/sliding-window/variable-length) windows
- [USACO Guide: Sliding Window](https://usaco.guide/gold/sliding-window): Method 1 (deque) for window max

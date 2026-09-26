# Pointers or window?

> Both search the (start, end) grid and delete a row or column per step; pointers ask what's at the ends (needs sorted order), a window asks what's inside (needs monotone validity).

Kind: comparison · Status: learning

**Notebook:** [pointers_vs_window.py](pointers_vs_window.py) (two staircases on one grid, breaking each precondition, same-direction ≠ window, a clickable decision tree, twins, a 12-prompt drill). Run `marimo edit DSA/04-pointers-vs-window/pointers_vs_window.py` locally, or open it on the site.

## Spot it
1. Contiguous subarray/substring? → is validity monotone? → window (max/min inside → + deque); not monotone → prefix sums
2. Otherwise a pair/triple of values? → allowed to sort → converging pointers; must keep indices → hash map
3. Otherwise in-place rewrite → read/write; two sorted inputs → two-sequence pointers

## Template
| | Converging pointers | Sliding window |
| :--- | :--- | :--- |
| Loop | `while i < j:` | `for right in range(n):` |
| State | only a[i], a[j] | a running summary of a[left..right] |
| Precondition | sorted | validity monotone (no negatives with sums) |
| Grid path | top-right corner inward | along the diagonal |
| Steps | ≤ n − 1 | ≤ 2n |

## Traps (the ones that bite)
- Same-direction pointers aren't automatically a window: if the gap is **junk**, it's read/write; if the gap is **the answer**, it's a window
- "Take from either end" (1423, 1658) is a window on the middle you leave behind
- Negatives + a sum target silently break a window

## Ladder
| Twins | The deciding word |
| :--- | :--- |
| 167 / 1 | sorted vs unsorted-with-indices |
| 209 / 560 / 862 | negative, exactly |
| 283 / 1004 | what the gap means |
| 1423 / 1658 | either end = window in disguise |
| 392 / 567 | subsequence vs permutation |
| 611 / 713 | both count by adding a width |

## Questions
<!-- question notebooks for this topic live in questions/; tools/new_topic.py adds them here -->

## Review log
Counted from the day this topic reaches `Status: solid`:
- [ ] +2 days: the 12-prompt drill, aim 10/12
- [ ] +5 days: redo LC 1658 and LC 76
- [ ] +12 days: two random problems from the reading plan, unlabelled
- [ ] +26 days: mock round

## Resources
- [Reading plan](reading-plan.md): five sessions, readings, problem sets, spaced review
- Lab: [Pointers or Window?](pointers-or-window.html)

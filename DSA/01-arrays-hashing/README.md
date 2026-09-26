# Arrays & hashing

> A set answers "have I seen this?" and a dict answers "how many, where, which group?", each in O(1) average: most O(n²) array scans collapse to one pass.

Kind: pattern · Status: learning

**Notebook:** [arrays_hashing.py](arrays_hashing.py) (Valid Sudoku in three sets, the box-index trick, why Longest Consecutive is O(n), live traps, four exercises). Run `marimo edit DSA/01-arrays-hashing/arrays_hashing.py` locally, or open it on the site.

## Spot it
- duplicates / seen before → `set`
- anagram, frequency, majority → `Counter`
- group, bucket → `defaultdict(list)` keyed by a hashable **signature**
- unsorted pair to a target, return indices → dict value → index, look up the **complement**
- consecutive runs → `set` + only walk from run **starts**
- grid rules (Sudoku) → one set per unit; box = `(r // 3, c // 3)`

## Template
```python
seen = set()
for x in nums:
    if x in seen:          # the table already answers the question
        return True
    seen.add(x)            # otherwise record x
return False
```
Complement: look up **before** recording. Grouping key: `tuple(counts)` or `tuple(sorted(word))`, never a list.

## Traps (the ones that bite)
- A list as a dict key → `TypeError: unhashable type`
- Two Sum recording before looking up pairs an element with itself
- Anagram check with membership instead of counts (`"aab"` vs `"abb"`)
- Box index as `r // 3 + c // 3` merges boxes
- Deleting from a dict while iterating → `RuntimeError`
- `x in some_list` inside a loop is O(n) per check

## Ladder
| # | Problem | Stage | Done |
| :--- | :--- | :--- | :--- |
| 217 | Contains Duplicate | worked | |
| 1 | Two Sum | faded | |
| 49 | Group Anagrams | faded | |
| 128 | Longest Consecutive Sequence | solo | |
| 36, 242, 347, 238, 271 | reps | graded | |

## Questions
<!-- question notebooks for this topic live in questions/; tools/new_topic.py adds them here -->

## Review log
Counted from the day this topic reaches `Status: solid`:
- [ ] +2 days:
- [ ] +5 days:
- [ ] +12 days:
- [ ] +26 days:

## Resources
- Labs: [Sudoku in three sets](valid-sudoku-three-sets.html) · [Why it's O(n), not O(n²)](longest-consecutive-why-O-n.html)
- [Python wiki: TimeComplexity](https://wiki.python.org/moin/TimeComplexity): what list/dict/set operations really cost
- [Python docs: collections](https://docs.python.org/3/library/collections.html)

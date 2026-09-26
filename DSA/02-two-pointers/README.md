# Two pointers

> Two indices walk a line; each move discards candidates you've proved can't be the answer, turning an O(n²) pair search into one O(n) pass.

Kind: pattern · Status: practising

**Notebook:** [two_pointers.py](two_pointers.py) (pair-grid elimination, five shapes with code-line step-through, a live bug gallery, practice with tests). Run `marimo edit DSA/02-two-pointers/two_pointers.py` locally, or open it on the site.

## Spot it
- **Sorted** (or cheap to sort) and you need a **pair / triplet** hitting a target, or a count of pairs
- **Both ends inward**: palindromes, containers between two walls, squares of a sorted array
- **In place, O(1) extra space**: remove duplicates, move zeroes, partition
- **Two sorted sequences**: merge, subsequence check
- Discriminator: does the data **between** the pointers matter? Yes → sliding window. Unsorted + must return indices → hash map.

## Template
```python
def two_sum_sorted(nums: list[int], target: int) -> list[int]:
    left, right = 0, len(nums) - 1
    while left < right:                 # strict: a pair needs two indices
        current = nums[left] + nums[right]
        if current == target:
            return [left, right]
        if current < target:
            left += 1                   # row eliminated: need a bigger sum
        else:
            right -= 1                  # column eliminated: need a smaller sum
    return []
```
Five shapes: **A** converging (167, 125, 11, 42) · **B** read/write (26, 27, 283) · **C** partition, `while mid <= high` (75) · **D** fix one + converge (15, 16, 18, 611) · **E** two sequences, fill from the back (88, 392).

## Traps (the ones that bite)
- `while left <= right` in a pair search pairs an element with itself (`[1,2,3,4]`, 8 → `[3, 3]`)
- Nested `while` skips without `left < right` run off the string (`".,"` → IndexError)
- 3Sum: three dedup points; the anchor compares **backwards** (`nums[i] == nums[i-1]`); inner skips need `left < right`
- Partition: `mid` must **not** advance after a 2-swap
- Merge in place: write from the **back**
- Honest complexity: "O(n log n), dominated by the sort" if you sorted

## Ladder
| # | Problem | Stage | Done |
| :--- | :--- | :--- | :--- |
| 125 | Valid Palindrome | worked | |
| 26 | Remove Duplicates from Sorted Array | faded | |
| 15 | 3Sum | solo (anchor) | |
| 42 | Trapping Rain Water | stretch anchor | |
| 167, 977, 283, 88, 392, 11, 75, 16, 611, 18 | reps for each shape | graded | |

## Questions
- [LC 42 · Trapping Rain Water](questions/lc0042_trapping_rain_water.py): first principles → brute force → prefix maxima → two pointers

## Review log
Counted from the day this topic reaches `Status: solid`:
- [ ] +2 days: redo LC 15 from a blank file
- [ ] +5 days: LC 11 and LC 75 unlabelled
- [ ] +12 days: two random rungs, then redraw the pair grid from memory
- [ ] +26 days: mock round, two problems in 45 minutes, narrated

## Resources
- Labs: [Two Pointers Workbench](two-pointers-workbench.html) · [Two-Pointer Elimination](two-pointer-elimination.html) · [3Sum Dissected](3sum-dissected.html)
- [Hello Interview: Two Pointers](https://www.hellointerview.com/learn/code/two-pointers/overview): overview, Move Zeroes, Sort Colors
- [USACO Guide: Two Pointers](https://usaco.guide/silver/two-pointers): "Sum of Two Values" for the (value, index) trick

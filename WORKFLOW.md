# How we learn a topic

Every topic (a DSA pattern, a single interview question, a Python concept, a small web build) runs through the same loop. It lives in this repo as plain files, and it reaches the [site](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/) through a pull request. The repo is the source of truth; the site is built from it.

## 1. Pick the kind of topic

| Kind | Examples | Lives in | You get |
| :--- | :--- | :--- | :--- |
| **pattern** | two pointers, sliding window, prefix sum, binary search | `DSA/NN-slug/` | README + marimo notebook |
| **question** | LC 42 Trapping Rain Water, LC 424 | `DSA/NN-topic/questions/lcNNNN_slug.py` | a question notebook, listed in the topic README |
| **concept** | decorators, OOP, generators, HTTP, async | `python/NN-slug/`, `web/NN-slug/` | README + marimo notebook |
| **build** | a FastAPI todo API, a small React page | `web/NN-slug/` | README with goal, spec, checkpoints, build log, retro (plus the code) |
| comparison | pointers vs window | `DSA/NN-slug/` | a pattern-style notebook built after both patterns are taught |

Each kind has its own notebook shape, and every shape starts simple and earns the optimum:

| Kind | Notebook sections |
| :--- | :--- |
| pattern | Spot it → See it (step-through) → brute force → bottleneck → optimal → template → practice (worked / faded / solo) → traps → recall → go deeper |
| question | Clarify + edge cases → first principles → brute force (pseudo code → code → cost) → bottleneck → optimal (pseudo code → code → why) → see it → your turn → traps + follow-ups → recall |
| concept | Why it exists → mental model (stepper) → prove it live → build it up → pitfalls (run live) → practice → recall → go deeper |
| build | Goal → spec → checkpoints (each ends runnable + committed) → tests → deploy → retro |

## 2. Run the loop

| Step | Time | What happens | Who |
| :--- | :--- | :--- | :--- |
| 0. Scaffold | 5 min | `python tools/new_topic.py <kind> <where> "<Title>"` creates the folder, README and notebook from `templates/`, then updates the indexes | Claude (or you) |
| 1. Read | 20–25 min | the README's resources, only for the stated purpose; stop once you can answer the notebook's first question | you |
| 2. See | 15 min | the notebook's step-throughs, until you can predict the next frame before moving the slider | you |
| 3. Template | 10 min | write the template from memory into the README, then compare | you |
| 4. Do | 40 min | worked → faded → solo, in the notebook's editors; 25-minute cap per problem, then read the solution, close it, and redo it tomorrow | you |
| 5. Traps | 5 min | add the bug you *actually* hit to the README's Traps | you |
| 6. Recall | 10 min | close everything, answer the Recall section from memory, paste your answers to Claude for review | you + Claude |
| 7. Ship | 5 min | `pytest <notebook>` passes → commit → push → PR → CI green → merge → the site updates | you + CI |
| 8. Review | later | spaced review at +2, +5, +12, +26 days from the day Status becomes `solid`; tick the README boxes | you |

If a session runs long, cut the reading, never the recall. **Status** in each README moves `new → learning → practising → solid`.

## 3. Who does what

- **Claude** scaffolds topics, drafts notebooks (visuals, templates, exercises, answer keys and their tests), opens pull requests, and reviews your recall answers. Claude works through git only, never by copying files into your folder, so there is one path to `main`.
- **You** work through the notebook, fill in the README (ladder ticks, traps, review log, status), merge PRs, and `git pull`.
- **CI** (`.github/workflows/pages.yml`) lints the notebooks, runs every test, checks the indexes are current, builds the site, and deploys it from `main`.

## 4. Definition of done

A topic is shipped when:

- [ ] the README has its summary line, `Kind · Status`, spot-it cues, template, traps, ladder and resources
- [ ] every notebook section is filled, and `pytest <notebook>` passes (answer keys pass, stubs fail, step-throughs agree with brute force, every gallery bug really fails)
- [ ] worked, faded and solo are done
- [ ] recall has been answered once without notes
- [ ] it's merged to `main` and visible on the site

## 5. What makes a notebook good here

- **Simple first.** Brute force as pseudo code, then code, then its cost; name the exact wasted work; only then the optimum and *why it's safe*.
- **Visuals come from code.** A step-through is a generator of frames, drawn with `learnkit` views; the highlighted line comes from `line_of(CODE, "snippet")`, never a hard-coded number.
- **Every claim is computed.** Step counts, "wrong answers" in the bug gallery, if-vs-while experiments: all run live, so nothing on the page can go stale.
- **Practice is tested.** `mo.ui.code_editor` + `mo.ui.run_button` + `learnkit.check(code, func, cases)`. Include the edge cases that break first attempts; a big input doubles as a time limit.
- **The notebook tests itself.** The last cell holds `test_` functions: answer keys pass, stubs don't, frames match a brute-force oracle on random inputs, gallery bugs really fail.
- **It runs in the browser.** Stick to the standard library, `marimo` and `learnkit`. Link to other pages with full site URLs (notebooks are served from `/notebooks/`).

## 6. Repo layout

```text
Learning-Exploration-Random/
├── WORKFLOW.md            ← this file
├── README.md              ← map of areas (generated table)
├── pyproject.toml         ← pip install -e ".[dev]"
├── learnkit/              ← shared helpers: array/grid/bar/code views, practice runner, parsing
├── templates/             ← pattern · question · concept notebooks; topic · build · area READMEs
├── tools/
│   ├── new_topic.py       ← scaffold a topic
│   ├── catalog.py         ← scan areas, regenerate README tables (--check in CI)
│   └── build_site.py      ← render READMEs, copy labs, export notebooks to WebAssembly
├── docs/adr/              ← architecture decision records
├── DSA/                   ← patterns and questions
├── python/                ← Python concepts
├── web/                   ← web development (when the first topic arrives)
└── devops/                ← earlier exercises (not on the site)
```

## 7. Commands

```bash
pip install -e ".[dev]"                                      # once: marimo, pytest, uv, learnkit
python tools/new_topic.py pattern DSA "Prefix sum"           # start a topic
marimo edit DSA/05-prefix-sum/prefix_sum.py                  # write / study it
pytest DSA/05-prefix-sum/prefix_sum.py                       # its tests
pytest                                                       # everything
marimo check --strict DSA python                             # lint notebooks
python tools/catalog.py                                      # refresh README tables
python tools/build_site.py && python -m http.server -d _site 8000   # build + preview the whole site
python tools/build_site.py --skip-notebooks                  # fast preview of pages only
```

## 8. Git flow

1. `git switch -c topic/<area>-<slug>` (the scaffolder prints this)
2. Commit in small steps; push; open a PR. CI runs lint + tests + a site build on every PR.
3. Merge when green. The deploy job publishes the site from `main`.
4. `git pull` on your Mac. If you've edited the same files elsewhere, pull first and resolve locally.

The older `.html` labs are snapshots of claude.ai artifacts and are kept as they are. New visuals go into notebooks, so they're diffable, tested and runnable. Why the setup looks like this: [ADR 0001](docs/adr/0001-learning-workflow.md).

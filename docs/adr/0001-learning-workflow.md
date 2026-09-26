# ADR 0001: Repo-first learning notebooks, published with GitHub Pages

- **Status:** accepted
- **Date:** 2026-09-26

## Context

Study visuals were made as claude.ai artifacts: hand-built HTML pages, 330–1,300 lines each, plus one Docs artifact. Getting them onto GitHub meant exporting or copying each one. The copies went stale as soon as the originals changed. Two writers (Claude copying into the local folder, and git) produced a conflicting `DSA/README.md` on day one. Nothing tested the pages, and diffs of 6,646 lines for 10 files were unreadable.

## Decision

1. **The repo is the source of truth.** Topics are plain files; the site and any claude.ai preview are build outputs.
2. **marimo notebooks are the unit of teaching.** They're stored as pure Python, so they diff cleanly and pytest can test them. They're reactive for sliders and editors, and they export to WebAssembly pages that run Python in the browser.
3. **One shared helper package, `learnkit`,** draws arrays, grids, bars and code highlights, and runs practice tests. marimo only bundles local modules that sit next to a notebook, so the site build copies `learnkit/` beside each notebook at export time. It exports every notebook into one `notebooks/` folder so they share a single copy of marimo's frontend (about 27 MB) instead of one per notebook.
4. **Notebooks test themselves.** Answer keys pass, stubs fail, step-throughs match brute force, and gallery bugs really fail. CI runs `marimo check --strict`, `pytest` and an index check on every PR, and deploys only from `main`.
5. **Scaffolding over copy-paste.** `tools/new_topic.py` creates each kind of topic from `templates/`, and `tools/catalog.py` generates the README tables, so nothing is hand-indexed.
6. **One write path.** Claude contributes through branches and pull requests; the local clone updates with `git pull`.

## Alternatives considered

- **Keep claude.ai artifacts as the source, sync copies to GitHub.** Rejected: copies drift, private artifacts can't be fetched by CI, and two writers conflict.
- **Jupyter notebooks.** Rejected: `.ipynb` is JSON with embedded outputs (noisy diffs), and it isn't reactive; interactivity needs a kernel or extra tooling.
- **Hand-built HTML labs with a shared JS kit.** Viable, but the logic would live in JavaScript rather than the Python being practised, and it cannot be tested with pytest. The existing labs stay as snapshots.
- **marimo `--single-file` exports.** They're lighter (about 20 KB each, assets from a CDN), but they refuse local modules, so `learnkit` would have to be copied into every notebook.

## Consequences

- The first load of a notebook page downloads Python (Pyodide) and takes a few seconds; after that it's cached.
- Notebooks must stick to the standard library, `marimo` and `learnkit` to run in the browser.
- Notebook-to-notebook links use full site URLs, because exported notebooks are served from `/notebooks/`.
- Adding a topic is one command, and CI keeps the indexes and answer keys honest.

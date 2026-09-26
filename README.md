# Learning & exploration

> Himanshu's learning notebook: DSA patterns and questions, Python concepts, and (soon) web development. Every topic is a one-page README plus a marimo notebook that runs in the browser.

**Site:** [himanshubhardwaj2398.github.io/Learning-Exploration-Random](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/). It's rebuilt from this repo on every merge to `main`.

**How a topic is run:** [WORKFLOW.md](WORKFLOW.md), covering the kinds of topic, the per-topic loop, the definition of done, commands and git flow.

## Areas

<!-- areas:start -->
| Area | What's in it | Topics |
| --- | --- | --- |
| [DSA](DSA/README.md) | Coding-interview patterns and single-question deep dives in Python, each with a marimo notebook you can run in the browser. | 4 |
| [Python](python/README.md) | The language itself, from first principles: how names, functions, objects and the data model actually work. | 1 |
<!-- areas:end -->

## Work on it locally

```bash
pip install -e ".[dev]"                              # marimo, pytest, markdown tools, learnkit
marimo edit DSA/02-two-pointers/two_pointers.py      # open a notebook
pytest                                               # every notebook's answer keys and checks
python tools/new_topic.py pattern DSA "Prefix sum"   # start the next topic
```

## Also in this repo
- `devops/`: Helsinki Docker MOOC exercises and a FastAPI-from-basics project (not part of the site)
- `docs/adr/`: decisions about how this repo works, and why

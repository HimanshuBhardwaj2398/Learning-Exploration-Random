"""Scan the learning areas and keep the README indexes in sync with the folders.

    python tools/catalog.py           # rewrite the generated tables in the READMEs
    python tools/catalog.py --check   # CI: fail if a table is out of date

Conventions it relies on (WORKFLOW.md explains them):
  * an area is a top-level folder listed in AREAS (DSA, python, web, ...)
  * a topic is a folder inside an area named NN-slug, holding a README.md
  * the topic README starts with "# Title", then "> one-line summary", then a
    line like "Kind: pattern · Status: taught"
  * a notebook is any .py file in the topic (or its questions/ folder) that
    defines a marimo App
  * generated tables live between <!-- topics:start --> / <!-- topics:end -->
    in an area README and <!-- areas:start --> / <!-- areas:end --> in the
    root README; everything outside the markers is hand-written
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AREAS = ("DSA", "python", "web")
TOPIC_DIR = re.compile(r"^\d{2}-[a-z0-9-]+$")
H1 = re.compile(r"^#\s+(.+?)\s*$", re.M)
SUMMARY = re.compile(r"^>\s*(.+?)\s*$", re.M)
FIELD = r"{name}:\s*\**\s*([^·\n*]+?)\s*(?:·|$)"


@dataclass
class Notebook:
    path: Path  # relative to REPO

    @property
    def stem(self) -> str:
        return self.path.stem


@dataclass
class Topic:
    area: str
    folder: Path  # relative to REPO
    title: str
    summary: str
    kind: str
    status: str
    notebooks: list[Notebook] = field(default_factory=list)
    questions: list[Notebook] = field(default_factory=list)
    labs: list[Path] = field(default_factory=list)

    @property
    def number(self) -> str:
        return self.folder.name.split("-", 1)[0]

    @property
    def main_notebook(self) -> Notebook | None:
        return self.notebooks[0] if self.notebooks else None


@dataclass
class Area:
    name: str
    title: str
    summary: str
    topics: list[Topic]


TITLE_TAG = re.compile(r"<title>\s*(.*?)\s*</title>", re.S | re.I)
APP_TITLE = re.compile(r'app_title="([^"]+)"')


def lab_title(path: Path) -> str:
    """A lab's <title>, falling back to its file name."""
    try:
        match = TITLE_TAG.search(path.read_text(encoding="utf-8", errors="ignore")[:20000])
    except OSError:
        match = None
    return match.group(1) if match else path.stem.replace("-", " ")


def notebook_title(path: Path) -> str:
    """A notebook's app_title without its ' · kind' suffix, e.g. 'LC 42 Trapping Rain Water'."""
    try:
        match = APP_TITLE.search(path.read_text(encoding="utf-8"))
    except OSError:
        match = None
    return match.group(1).split(" · ")[0] if match else path.stem


def is_notebook(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return "import marimo" in text and "marimo.App(" in text


def _field(text: str, name: str, default: str) -> str:
    match = re.search(FIELD.format(name=name), text, re.M | re.I)
    return match.group(1).strip() if match else default


def read_topic(area: str, folder: Path, repo: Path = REPO) -> Topic:
    readme = folder / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    title_match, summary_match = H1.search(text), SUMMARY.search(text)
    title = title_match.group(1) if title_match else folder.name.split("-", 1)[1].replace("-", " ").capitalize()
    topic = Topic(
        area=area,
        folder=folder.relative_to(repo),
        title=title,
        summary=summary_match.group(1) if summary_match else "",
        kind=_field(text, "Kind", "pattern").lower(),
        status=_field(text, "Status", "new").lower(),
    )
    for path in sorted(folder.glob("*.py")):
        if is_notebook(path):
            topic.notebooks.append(Notebook(path.relative_to(repo)))
    for path in sorted((folder / "questions").glob("*.py")):
        if is_notebook(path):
            topic.questions.append(Notebook(path.relative_to(repo)))
    topic.labs = [p.relative_to(repo) for p in sorted(folder.glob("*.html"))]
    return topic


def scan(repo: Path = REPO) -> list[Area]:
    areas = []
    for name in AREAS:
        root = repo / name
        if not root.is_dir():
            continue
        readme = root / "README.md"
        text = readme.read_text(encoding="utf-8") if readme.exists() else ""
        title_match, summary_match = H1.search(text), SUMMARY.search(text)
        topics = [read_topic(name, d, repo) for d in sorted(root.iterdir()) if d.is_dir() and TOPIC_DIR.match(d.name)]
        areas.append(
            Area(
                name=name,
                title=title_match.group(1) if title_match else name,
                summary=summary_match.group(1) if summary_match else "",
                topics=topics,
            )
        )
    return areas


def all_notebooks(areas: list[Area]) -> list[Notebook]:
    return [nb for area in areas for topic in area.topics for nb in (*topic.notebooks, *topic.questions)]


def _rel(path: Path, start: Path) -> str:
    return Path(*path.parts[len(start.parts):]).as_posix()


def topics_table(area: Area) -> str:
    base = Path(area.name)
    lines = [
        "| # | Topic | Kind | Status | Notebook | Also |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for t in area.topics:
        topic_link = f"[{t.title}]({_rel(t.folder, base)}/README.md)"
        nb = f"[{t.main_notebook.path.name}]({_rel(t.main_notebook.path, base)})" if t.main_notebook else "—"
        extras = [f"[{notebook_title(REPO / q.path)}]({_rel(q.path, base)})" for q in t.questions]
        extras += [f"[lab: {lab_title(REPO / lab)}]({_rel(lab, base)})" for lab in t.labs]
        lines.append(f"| {t.number} | {topic_link} | {t.kind} | {t.status} | {nb} | {', '.join(extras) or '—'} |")
    return "\n".join(lines)


def areas_table(areas: list[Area]) -> str:
    lines = ["| Area | What's in it | Topics |", "| --- | --- | --- |"]
    for a in areas:
        lines.append(f"| [{a.title}]({a.name}/README.md) | {a.summary or '—'} | {len(a.topics)} |")
    return "\n".join(lines)


def _replace_block(text: str, marker: str, body: str) -> str:
    start, end = f"<!-- {marker}:start -->", f"<!-- {marker}:end -->"
    if start not in text or end not in text:
        return text
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{start}\n{body}\n{end}{tail}"


def planned_updates(repo: Path = REPO) -> dict[Path, str]:
    """README path -> new content, for every README whose generated block changes."""
    areas = scan(repo)
    updates: dict[Path, str] = {}
    root = repo / "README.md"
    if root.exists():
        old = root.read_text(encoding="utf-8")
        new = _replace_block(old, "areas", areas_table(areas))
        if new != old:
            updates[root] = new
    for area in areas:
        readme = repo / area.name / "README.md"
        if readme.exists():
            old = readme.read_text(encoding="utf-8")
            new = _replace_block(old, "topics", topics_table(area))
            if new != old:
                updates[readme] = new
    return updates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="exit 1 if any README index is out of date")
    args = parser.parse_args()
    updates = planned_updates()
    if args.check:
        for path in updates:
            print(f"out of date: {path.relative_to(REPO)} (run: python tools/catalog.py)")
        return 1 if updates else 0
    for path, content in updates.items():
        path.write_text(content, encoding="utf-8")
        print(f"updated {path.relative_to(REPO)}")
    if not updates:
        print("indexes already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())

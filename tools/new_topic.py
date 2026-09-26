"""Start a new topic from the templates, following WORKFLOW.md.

    python tools/new_topic.py pattern  DSA    "Prefix sum"
    python tools/new_topic.py concept  python "Object-oriented Python" --slug oop
    python tools/new_topic.py question DSA/03-sliding-window "Longest Repeating Character Replacement" --lc 424
    python tools/new_topic.py build    web    "Todo API with FastAPI"

pattern / concept  ->  <area>/NN-slug/README.md + <area>/NN-slug/<slug>.py (a marimo notebook)
question           ->  <topic>/questions/lcNNNN_slug.py, listed in the topic README
build              ->  <area>/NN-slug/README.md (goal, spec, checkpoints, build log, retro)

Numbers are assigned in order (01, 02, ...), and the README indexes are refreshed.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402

REPO = catalog.REPO
TEMPLATES = REPO / "templates"
KINDS = ("pattern", "concept", "question", "build")


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        raise SystemExit(f"Can't make a folder name from {title!r}; pass --slug.")
    return slug


def next_number(area_dir: Path) -> str:
    numbers = [int(d.name[:2]) for d in area_dir.iterdir() if d.is_dir() and catalog.TOPIC_DIR.match(d.name)] if area_dir.exists() else []
    return f"{max(numbers, default=0) + 1:02d}"


def render(template: Path, values: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if leftover:
        raise SystemExit(f"Template {template} still has placeholders: {sorted(set(leftover))}")
    return text


def _write(path: Path, content: str) -> Path:
    if path.exists():
        raise SystemExit(f"{path} already exists; not overwriting it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if path.suffix == ".py":
        # let marimo normalise cell signatures (best effort: skipped if marimo is missing)
        subprocess.run([sys.executable, "-m", "marimo", "check", "--fix", str(path)], capture_output=True)
    return path


def scaffold(kind: str, where: str, title: str, *, slug: str | None = None, lc: int | None = None, root: Path = REPO) -> list[Path]:
    """Create the files for a new topic. Returns the paths written."""
    if kind not in KINDS:
        raise SystemExit(f"kind must be one of {', '.join(KINDS)}")
    slug = slug or slugify(title)
    written: list[Path] = []

    if kind == "question":
        topic_dir = root / where
        if not (topic_dir / "README.md").exists():
            raise SystemExit(f"{where} isn't a topic folder (no README.md). Questions live inside a topic, e.g. DSA/03-sliding-window.")
        module = (f"lc{lc:04d}_" if lc else "") + slug.replace("-", "_")
        path = topic_dir / "questions" / f"{module}.py"
        topic_title = catalog.read_topic(topic_dir.parent.name, topic_dir, root).title
        heading = f"LC {lc} · {title}" if lc else title
        written.append(_write(path, render(TEMPLATES / "question" / "notebook.py", {"TITLE": heading, "TOPIC": topic_title})))
        readme = topic_dir / "README.md"
        text = readme.read_text(encoding="utf-8")
        entry = f"- [{heading}](questions/{path.name})"
        if "## Questions" in text:
            head, tail = text.split("## Questions", 1)
            first_line_end = tail.find("\n") + 1
            text = head + "## Questions" + tail[:first_line_end] + entry + "\n" + tail[first_line_end:]
        else:
            text = text.rstrip() + f"\n\n## Questions\n{entry}\n"
        readme.write_text(text, encoding="utf-8")
        written.append(readme)
        return written

    area = where.strip("/")
    area_dir = root / area
    if not (area_dir / "README.md").exists():
        written.append(_write(area_dir / "README.md", render(TEMPLATES / "area" / "README.md", {"TITLE": area})))
    number = next_number(area_dir)
    folder = area_dir / f"{number}-{slug}"
    notebook_file = f"{slug.replace('-', '_')}.py"
    values = {
        "TITLE": title,
        "AREA": area,
        "NUMBER": number,
        "KIND": kind,
        "NOTEBOOK_FILE": notebook_file,
        "NOTEBOOK_PATH": f"{area}/{folder.name}/{notebook_file}",
    }
    if kind == "build":
        written.append(_write(folder / "README.md", render(TEMPLATES / "build" / "README.md", values)))
    else:
        written.append(_write(folder / "README.md", render(TEMPLATES / "topic" / "README.md", values)))
        written.append(_write(folder / notebook_file, render(TEMPLATES / kind / "notebook.py", values)))
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=KINDS)
    parser.add_argument("where", help="area (DSA, python, web) or, for a question, the topic folder")
    parser.add_argument("title")
    parser.add_argument("--slug", help="folder / file name (default: from the title)")
    parser.add_argument("--lc", type=int, help="LeetCode number, for questions")
    args = parser.parse_args()

    written = scaffold(args.kind, args.where, args.title, slug=args.slug, lc=args.lc)
    for path, content in catalog.planned_updates().items():
        path.write_text(content, encoding="utf-8")
        written.append(path)

    area = args.where.split("/")[0]
    if area not in catalog.AREAS:
        print(f"Note: {area}/ isn't in AREAS in tools/catalog.py yet; add it to publish it on the site.")
    print("Created or updated:")
    for path in dict.fromkeys(written):
        print(f"  {path.relative_to(REPO)}")
    notebook = next((p for p in written if p.suffix == ".py"), None)
    branch = f"topic/{area.lower()}-{args.slug or slugify(args.title)}"
    print("\nNext:")
    print(f"  git switch -c {branch}")
    if notebook:
        rel = notebook.relative_to(REPO)
        print(f"  marimo edit {rel}          # write it section by section")
        print(f"  pytest {rel}               # answer key + frames must pass")
    print("  git add -A && git commit -m \"Start topic: " + args.title + "\" && git push -u origin " + branch)


if __name__ == "__main__":
    main()

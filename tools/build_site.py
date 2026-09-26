"""Build the learning site for GitHub Pages.

    pip install -e ".[dev]"
    python tools/build_site.py                    # full build into ./_site
    python tools/build_site.py --skip-notebooks   # fast: pages and labs only
    python -m http.server -d _site 8000           # preview at localhost:8000

What ends up where
  * a README.md becomes index.html in its folder; other .md files become .html
  * labs (.html) and other assets are copied unchanged, keeping their repo paths
  * every marimo notebook is exported to notebooks/<name>.html; all of them share
    one copy of marimo's assets and run Python in the browser (WebAssembly)
  * the home page is generated from the catalog (tools/catalog.py)

Links in Markdown are rewritten for the site: .md -> .html, and a link to a
notebook's .py file -> its page under notebooks/.
"""

from __future__ import annotations

import argparse
import html
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path, PurePosixPath

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import REPO, Area, all_notebooks, lab_title, notebook_title, scan  # noqa: E402

REPO_URL = "https://github.com/HimanshuBhardwaj2398/Learning-Exploration-Random"
MARKER = ".learning-site"  # lets a rebuild wipe its own output, and nothing else
SKIP_DIRS = {"__pycache__", "tools", "__marimo__", ".pytest_cache"}
COPY_SUFFIXES = {".html", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js", ".json", ".csv", ".pdf"}
HREF = re.compile(r'href="([^"]*)"')
H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.M)


# --------------------------------------------------------------------------- markdown


def make_renderer() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
    md.use(tasklists_plugin)
    default_fence = md.renderer.rules["fence"]

    def fence(self, tokens, idx, options, env):
        token = tokens[idx]
        if token.info.strip().lower() == "mermaid":
            env["has_mermaid"] = True
            return f'<pre class="mermaid">{html.escape(token.content)}</pre>\n'
        return default_fence(tokens, idx, options, env)

    md.add_render_rule("fence", fence)
    return md


def site_path_for_markdown(repo_path: PurePosixPath) -> PurePosixPath:
    name = "index.html" if repo_path.stem.lower() == "readme" else repo_path.stem + ".html"
    return repo_path.with_name(name)


def rewrite_links(body: str, src: PurePosixPath, page: PurePosixPath, notebooks: dict[str, str]) -> str:
    """Point links at their site locations. src/page are repo-relative / site-relative paths."""

    def repl(match: re.Match) -> str:
        href = match.group(1)
        if not href or href.startswith(("#", "/", "mailto:")) or re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I):
            return match.group(0)
        path, suffix = re.match(r"([^#?]*)(.*)", href).groups()  # suffix keeps any #fragment or ?query
        target = posixpath.normpath(posixpath.join(str(src.parent), path))
        if target in notebooks:
            new = notebooks[target]
        elif target.lower().endswith(".md"):
            new = str(site_path_for_markdown(PurePosixPath(target)))
        else:
            return match.group(0)
        rel = posixpath.relpath(new, str(page.parent))
        return f'href="{rel}{suffix}"'

    return HREF.sub(repl, body)


# --------------------------------------------------------------------------- pages


def nav_html(areas: list[Area], page: PurePosixPath) -> str:
    here = str(page.parent)
    links = [f'<a href="{posixpath.relpath("index.html", here)}">Home</a>']
    for area in areas:
        links.append(f'<a href="{posixpath.relpath(f"{area.name}/index.html", here)}">{html.escape(area.title)}</a>')
    links.append(f'<a href="{posixpath.relpath("WORKFLOW.html", here)}">Workflow</a>')
    links.append(f'<a href="{REPO_URL}">GitHub</a>')
    return f'<nav>{" · ".join(links)}</nav>'


def write_page(out: Path, page: PurePosixPath, title: str, body: str, areas: list[Area], mermaid: bool = False) -> None:
    target = out / page
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        PAGE.format(
            title=html.escape(title),
            nav=nav_html(areas, page),
            body=body,
            mermaid=MERMAID_SCRIPT if mermaid else "",
        ),
        encoding="utf-8",
    )


def markdown_sources(areas: list[Area]) -> list[Path]:
    """Every README / note inside an area, plus the workflow and the ADRs."""
    sources = [REPO / "WORKFLOW.md", *sorted((REPO / "docs" / "adr").glob("*.md"))]
    for area in areas:
        for src in sorted((REPO / area.name).rglob("*.md")):
            rel = src.relative_to(REPO)
            if not any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
                sources.append(src)
    return [s for s in sources if s.exists()]


def render_markdown_pages(out: Path, areas: list[Area], notebooks: dict[str, str]) -> int:
    md = make_renderer()
    count = 0
    for src in markdown_sources(areas):
        rel = src.relative_to(REPO)
        text = src.read_text(encoding="utf-8")
        env: dict = {}
        body = md.render(text, env)
        repo_path = PurePosixPath(rel.as_posix())
        page = site_path_for_markdown(repo_path)
        body = rewrite_links(body, repo_path, page, notebooks)
        body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
        match = H1.search(text)
        write_page(out, page, match.group(1) if match else src.stem, body, areas, bool(env.get("has_mermaid")))
        count += 1
    return count


def copy_static(out: Path, areas: list[Area]) -> int:
    count = 0
    for area in areas:
        for src in sorted((REPO / area.name).rglob("*")):
            rel = src.relative_to(REPO)
            if src.is_dir() or any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
                continue
            if src.suffix.lower() in COPY_SUFFIXES:
                dest = out / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                count += 1
    return count


def inline_code(text: str) -> str:
    """Escape text, then turn `code` spans into <code> elements."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(text))


def home_body(areas: list[Area], notebooks: dict[str, str]) -> str:
    parts = [
        "<h1>Learning notebook</h1>",
        '<p class="lead">Interactive notebooks for DSA patterns, single questions and Python concepts. '
        "Each notebook runs real Python in your browser, so give the first one a few seconds to load; "
        "after that it is cached.</p>",
    ]
    for area in areas:
        parts.append(f'<h2><a href="{area.name}/index.html">{html.escape(area.title)}</a></h2>')
        if area.summary:
            parts.append(f"<p>{inline_code(area.summary)}</p>")
        cards = []
        for t in area.topics:
            links = []
            if t.main_notebook:
                links.append(f'<a class="primary" href="{notebooks[t.main_notebook.path.as_posix()]}">Open notebook</a>')
            links.append(f'<a href="{t.folder.as_posix()}/index.html">Notes</a>')
            for q in t.questions:
                links.append(f'<a href="{notebooks[q.path.as_posix()]}">{html.escape(notebook_title(REPO / q.path))}</a>')
            for lab in t.labs:
                links.append(f'<a href="{lab.as_posix()}">Lab: {html.escape(lab_title(REPO / lab))}</a>')
            cards.append(
                '<div class="card">'
                f'<div class="meta">{t.number} · {html.escape(t.kind)} · {html.escape(t.status)}</div>'
                f'<div class="title">{html.escape(t.title)}</div>'
                f'<div class="summary">{inline_code(t.summary)}</div>'
                f'<div class="links">{"".join(links)}</div></div>'
            )
        parts.append(f'<div class="cards">{"".join(cards)}</div>')
    parts.append(
        f'<p class="foot">How each topic is run: <a href="WORKFLOW.html">the workflow</a> '
        f'· source and notebooks: <a href="{REPO_URL}">GitHub</a></p>'
    )
    return "\n".join(parts)


# --------------------------------------------------------------------------- notebooks


def export_notebooks(out: Path, areas: list[Area]) -> dict[str, str]:
    """Export every notebook to notebooks/<stem>.html. Returns repo path -> site path."""
    notebooks = all_notebooks(areas)
    stems: dict[str, str] = {}
    for nb in notebooks:
        if nb.stem in stems:
            raise SystemExit(f"Two notebooks are both called {nb.stem}.py ({stems[nb.stem]} and {nb.path}); rename one.")
        stems[nb.stem] = nb.path.as_posix()

    mapping: dict[str, str] = {}
    target_dir = out / "notebooks"
    target_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for nb in notebooks:
            stage = Path(tmp) / nb.stem
            stage.mkdir()
            shutil.copy2(REPO / nb.path, stage / nb.path.name)
            # marimo bundles local modules only when they sit next to the notebook
            shutil.copytree(REPO / "learnkit", stage / "learnkit", ignore=shutil.ignore_patterns("__pycache__", "test_*"))
            cmd = [sys.executable, "-m", "marimo", "-y", "export", "html-wasm", str(stage / nb.path.name),
                   "-o", str(target_dir / f"{nb.stem}.html"), "--mode", "run"]
            result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "MARIMO_SKIP_UPDATE_CHECK": "1"})
            if result.returncode != 0:
                raise SystemExit(f"marimo export failed for {nb.path}:\n{result.stdout}\n{result.stderr}")
            mapping[nb.path.as_posix()] = f"notebooks/{nb.stem}.html"
            print(f"  exported {nb.path}")
    (target_dir / "CLAUDE.md").unlink(missing_ok=True)  # marimo's note for AI editors; not site content
    return mapping


def placeholder_notebooks(areas: list[Area]) -> dict[str, str]:
    return {nb.path.as_posix(): f"notebooks/{nb.stem}.html" for nb in all_notebooks(areas)}


# --------------------------------------------------------------------------- main


def prepare_out(out: Path) -> None:
    if out.exists() and any(out.iterdir()):
        if not (out / MARKER).exists():
            raise SystemExit(f"Refusing to overwrite {out}: it wasn't made by this script.")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)


def build(out: Path, skip_notebooks: bool = False) -> None:
    prepare_out(out)
    areas = scan()
    notebooks = placeholder_notebooks(areas) if skip_notebooks else export_notebooks(out, areas)
    pages = render_markdown_pages(out, areas, notebooks)
    files = copy_static(out, areas)
    write_page(out, PurePosixPath("index.html"), "Learning notebook", home_body(areas, notebooks), areas)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    (out / MARKER).write_text("built by tools/build_site.py\n", encoding="utf-8")
    exported = "skipped" if skip_notebooks else str(len(notebooks))
    print(f"Built {out}: {pages} pages, {files} copied files, notebooks: {exported}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("_site"), help="output folder (default: ./_site)")
    parser.add_argument("--skip-notebooks", action="store_true", help="don't export notebooks (fast preview)")
    args = parser.parse_args()
    try:
        build(args.out.resolve(), skip_notebooks=args.skip_notebooks)
    except BaseException as exc:
        if os.environ.get("GITHUB_ACTIONS") == "true":  # show the reason on the PR, not only in the raw log
            detail = str(exc) if isinstance(exc, SystemExit) else traceback.format_exc()
            print("::error title=Site build failed::" + detail.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A"))
        raise


MERMAID_SCRIPT = """<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "neutral" });
  await mermaid.run();
</script>"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #f6f5f1; --panel: #ffffff; --ink: #1f2328; --muted: #5f6672; --line: #dedbd2;
    --accent: #3f51b5; --accent-soft: #e8eafb; --code-bg: #f0eee8; --row: #faf9f6;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #13151a; --panel: #1b1e25; --ink: #e6e8eb; --muted: #9aa1ad; --line: #2f343e;
      --accent: #8c9bff; --accent-soft: #232845; --code-bg: #232731; --row: #1f232b;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #13151a; --panel: #1b1e25; --ink: #e6e8eb; --muted: #9aa1ad; --line: #2f343e;
    --accent: #8c9bff; --accent-soft: #232845; --code-bg: #232731; --row: #1f232b;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.65 Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }}
  main {{ max-width: 960px; margin: 0 auto; padding: 24px 16px 64px; }}
  nav {{ max-width: 960px; margin: 0 auto; padding: 18px 16px 0; font-size: 14px; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  h1 {{ font-size: clamp(28px, 5vw, 38px); line-height: 1.15; letter-spacing: -0.02em; margin: 8px 0 12px; }}
  h2 {{ font-size: 22px; margin: 40px 0 12px; padding-top: 18px; border-top: 1px solid var(--line); }}
  h3 {{ font-size: 17px; margin: 26px 0 8px; }}
  p, li {{ max-width: 76ch; }}
  .lead {{ font-size: 17.5px; color: var(--muted); }}
  code {{ font: 0.88em "JetBrains Mono", monospace; background: var(--code-bg); padding: 1px 5px; border-radius: 5px; }}
  pre {{ background: var(--code-bg); padding: 14px 16px; border-radius: 10px; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; }}
  pre.mermaid {{ background: var(--panel); border: 1px solid var(--line); text-align: center; }}
  blockquote {{ margin: 14px 0; padding: 6px 16px; border-left: 3px solid var(--accent); background: var(--accent-soft); border-radius: 0; }}
  .table-wrap {{ overflow-x: auto; margin: 14px 0 20px; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14.5px; }}
  th, td {{ text-align: left; padding: 9px 13px; border-bottom: 1px solid var(--line); vertical-align: top; }}
  th {{ font-weight: 600; color: var(--muted); font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.06em; }}
  tbody tr:last-child td {{ border-bottom: 0; }}
  tbody tr:nth-child(even) {{ background: var(--row); }}
  ul.contains-task-list {{ list-style: none; padding-left: 4px; }}
  .task-list-item-checkbox {{ margin-right: 8px; accent-color: var(--accent); }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; margin: 14px 0 8px; }}
  .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 16px; display: flex; flex-direction: column; gap: 6px; }}
  .card .meta {{ font: 12px "JetBrains Mono", monospace; color: var(--muted); text-transform: lowercase; }}
  .card .title {{ font-weight: 600; font-size: 17px; }}
  .card .summary {{ color: var(--muted); font-size: 14.5px; flex: 1; }}
  .card .links {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }}
  .card .links a {{ font-size: 13px; padding: 3px 10px; border: 1px solid var(--line); border-radius: 999px; }}
  .card .links a.primary {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
  .foot {{ margin-top: 40px; color: var(--muted); font-size: 14px; }}
</style>
</head>
<body>
{nav}
<main>
{body}
</main>
{mermaid}
</body>
</html>
"""


if __name__ == "__main__":
    main()

"""Build the DSA labs site for GitHub Pages.

    pip install -r DSA/tools/requirements.txt
    python DSA/tools/build_site.py              # writes ./_site
    python -m http.server -d _site 8000         # preview at localhost:8000

What it does
  * copies every lab (.html and any other asset) under DSA/ to <out>/DSA/
  * renders each Markdown file to HTML beside it; README.md becomes index.html
  * turns ```mermaid blocks into diagrams and rewrites links to .md files
  * writes <out>/index.html, which sends the site root to DSA/

A file's path in the repo is its path on the site:
    DSA/02-two-pointers/3sum-dissected.html
    -> https://<user>.github.io/<repo>/DSA/02-two-pointers/3sum-dissected.html
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin

DSA_DIR = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"tools", "__pycache__"}
MARKER = ".dsa-site"  # lets a rebuild wipe its own output, and nothing else

# href="x.md" or href="x.md#frag"; leaves absolute URLs and in-page anchors alone
MD_LINK = re.compile(r'href="(?![a-z][a-z0-9+.-]*:|#|/)([^"#?]+?)\.md([#?][^"]*)?"', re.I)
H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.M)


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


def html_name(md_path: Path) -> str:
    return "index.html" if md_path.stem.lower() == "readme" else md_path.stem + ".html"


def rewrite_md_links(body: str) -> str:
    def repl(m: re.Match) -> str:
        target, suffix = m.group(1), m.group(2) or ""
        head, _, stem = target.rpartition("/")
        new = "index" if stem.lower() == "readme" else stem
        return f'href="{head + "/" if head else ""}{new}.html{suffix}"'

    return MD_LINK.sub(repl, body)


def render_page(md: MarkdownIt, src: Path, out_file: Path, site_dsa: Path) -> None:
    text = src.read_text(encoding="utf-8")
    env: dict = {}
    body = md.render(text, env)
    body = rewrite_md_links(body)
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

    match = H1.search(text)
    title = match.group(1).strip() if match else src.stem.replace("-", " ").title()
    is_home = out_file.name == "index.html" and out_file.parent == site_dsa
    home = os.path.relpath(site_dsa / "index.html", out_file.parent)
    nav = "" if is_home else f'<nav><a href="{home}">&larr; All DSA labs</a></nav>'
    mermaid = MERMAID_SCRIPT if env.get("has_mermaid") else ""

    out_file.write_text(
        PAGE.format(title=html.escape(title), nav=nav, body=body, mermaid=mermaid),
        encoding="utf-8",
    )


def prepare_out(out: Path) -> None:
    if out.exists() and any(out.iterdir()):
        if not (out / MARKER).exists():
            raise SystemExit(f"Refusing to overwrite {out}: it wasn't made by this script.")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)


def build(out: Path) -> list[Path]:
    prepare_out(out)
    site_dsa = out / DSA_DIR.name
    md = make_renderer()
    written: list[Path] = []

    for src in sorted(DSA_DIR.rglob("*")):
        rel = src.relative_to(DSA_DIR)
        if src.is_dir() or rel.parts[0] in SKIP_DIRS or any(p.startswith(".") for p in rel.parts):
            continue
        dest_dir = site_dsa / rel.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() == ".md":
            dest = dest_dir / html_name(src)
            render_page(md, src, dest, site_dsa)
        else:
            dest = dest_dir / src.name
            shutil.copy2(src, dest)
        written.append(dest)

    (out / "index.html").write_text(ROOT_REDIRECT.format(target=f"{DSA_DIR.name}/"), encoding="utf-8")
    (out / MARKER).write_text("built by DSA/tools/build_site.py\n", encoding="utf-8")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("_site"), help="output folder (default: ./_site)")
    args = parser.parse_args()
    written = build(args.out.resolve())
    print(f"Built {len(written)} files into {args.out}/")


MERMAID_SCRIPT = """<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  mermaid.initialize({ startOnLoad: false, theme: dark ? "dark" : "neutral" });
  await mermaid.run();
</script>"""

ROOT_REDIRECT = """<!doctype html>
<meta charset="utf-8">
<title>DSA labs</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
<p><a href="{target}">DSA labs &rarr;</a></p>
"""

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
  main {{ max-width: 920px; margin: 0 auto; padding: 32px 16px 64px; }}
  nav {{ max-width: 920px; margin: 0 auto; padding: 20px 16px 0; font-size: 14px; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  h1 {{ font-size: clamp(28px, 5vw, 38px); line-height: 1.15; letter-spacing: -0.02em; margin: 0 0 12px; }}
  h2 {{ font-size: 22px; margin: 44px 0 12px; padding-top: 20px; border-top: 1px solid var(--line); }}
  h3 {{ font-size: 17px; margin: 28px 0 8px; font-family: "JetBrains Mono", monospace; font-weight: 500; }}
  p, li {{ max-width: 72ch; }}
  code {{ font: 0.88em "JetBrains Mono", monospace; background: var(--code-bg); padding: 1px 5px; border-radius: 5px; }}
  pre {{ background: var(--code-bg); padding: 14px 16px; border-radius: 10px; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; }}
  pre.mermaid {{ background: var(--panel); border: 1px solid var(--line); text-align: center; }}
  .table-wrap {{ overflow-x: auto; margin: 14px 0 20px; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14.5px; }}
  th, td {{ text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }}
  th {{ font-weight: 600; color: var(--muted); font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.06em; }}
  tbody tr:last-child td {{ border-bottom: 0; }}
  tbody tr:nth-child(even) {{ background: var(--row); }}
  td:first-child a {{ font-weight: 500; }}
  ul.contains-task-list {{ list-style: none; padding-left: 4px; }}
  .task-list-item-checkbox {{ margin-right: 8px; accent-color: var(--accent); }}
  blockquote {{ margin: 16px 0; padding: 4px 16px; border-left: 3px solid var(--accent); background: var(--accent-soft); border-radius: 0 8px 8px 0; }}
  em:only-child {{ color: var(--muted); }}
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

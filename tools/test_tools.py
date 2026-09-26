"""Tests for the topic scaffolder, the catalog, and the site build's link rewriting."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402
import new_topic  # noqa: E402
import build_site  # noqa: E402
from build_site import rewrite_links  # noqa: E402


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    # Drop PYTEST_* variables: marimo treats an inherited PYTEST_CURRENT_TEST as "already inside a test"
    # and skips collecting the nested notebook's tests.
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST_")}
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd, env=env)


def test_slugify():
    assert new_topic.slugify("Prefix sum") == "prefix-sum"
    assert new_topic.slugify("  Object-Oriented Python!  ") == "object-oriented-python"


@pytest.mark.parametrize("kind", ["pattern", "concept"])
def test_scaffolded_notebook_is_valid_runs_and_passes_its_tests(tmp_path, kind):
    written = new_topic.scaffold(kind, "DSA", "Prefix sum", root=tmp_path)
    notebook = next(p for p in written if p.suffix == ".py")
    assert notebook == tmp_path / "DSA" / "01-prefix-sum" / "prefix_sum.py"
    for path in written:
        assert "{{" not in path.read_text(encoding="utf-8"), path
    check = _run("-m", "marimo", "check", "--strict", str(notebook), cwd=tmp_path)
    assert check.returncode == 0, check.stdout + check.stderr
    script = _run(str(notebook), cwd=tmp_path)
    assert script.returncode == 0, script.stderr
    tests = _run("-m", "pytest", "-q", "-p", "no:cacheprovider", str(notebook), cwd=tmp_path)
    assert tests.returncode == 0, tests.stdout + tests.stderr

    topic = catalog.scan(tmp_path)[0].topics[0]
    assert (topic.title, topic.kind, topic.status) == ("Prefix sum", kind, "new")
    assert topic.main_notebook.path == Path("DSA/01-prefix-sum/prefix_sum.py")


def test_topics_are_numbered_in_order(tmp_path):
    new_topic.scaffold("pattern", "DSA", "First", root=tmp_path)
    written = new_topic.scaffold("pattern", "DSA", "Second", root=tmp_path)
    assert written[0].parent.name == "02-second"


def test_question_is_created_inside_a_topic_and_listed(tmp_path):
    new_topic.scaffold("pattern", "DSA", "Sliding window", root=tmp_path)
    written = new_topic.scaffold("question", "DSA/01-sliding-window", "Longest Repeating Character Replacement", lc=424, root=tmp_path)
    notebook = tmp_path / "DSA/01-sliding-window/questions/lc0424_longest_repeating_character_replacement.py"
    assert notebook in written
    assert "LC 424 · Longest Repeating Character Replacement" in notebook.read_text(encoding="utf-8")
    readme = (tmp_path / "DSA/01-sliding-window/README.md").read_text(encoding="utf-8")
    assert "(questions/lc0424_longest_repeating_character_replacement.py)" in readme
    check = _run("-m", "marimo", "check", "--strict", str(notebook), cwd=tmp_path)
    assert check.returncode == 0, check.stdout + check.stderr
    assert catalog.scan(tmp_path)[0].topics[0].questions[0].stem == "lc0424_longest_repeating_character_replacement"


def test_build_topic_gets_a_readme_only(tmp_path):
    written = new_topic.scaffold("build", "web", "Todo API with FastAPI", root=tmp_path)
    assert [p.name for p in written] == ["README.md", "README.md"]  # area README, then the topic README
    assert "## Plan: checkpoints" in written[1].read_text(encoding="utf-8")


def test_existing_topic_is_never_overwritten(tmp_path):
    new_topic.scaffold("pattern", "DSA", "Prefix sum", root=tmp_path, slug="prefix-sum")
    folder = tmp_path / "DSA" / "02-prefix-sum"
    folder.mkdir(parents=True)
    (folder / "README.md").write_text("# mine\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        new_topic._write(folder / "README.md", "replacement")
    assert (folder / "README.md").read_text(encoding="utf-8") == "# mine\n"


def test_repo_readme_indexes_are_up_to_date():
    stale = [str(p.relative_to(catalog.REPO)) for p in catalog.planned_updates()]
    assert not stale, f"run: python tools/catalog.py (stale: {stale})"


def test_every_topic_has_a_title_summary_and_known_kind():
    for area in catalog.scan():
        for topic in area.topics:
            assert topic.title and topic.summary, topic.folder
            assert topic.kind in {"pattern", "concept", "question", "build", "comparison"}, topic.folder


def test_notebook_names_are_unique():
    stems = [nb.stem for nb in catalog.all_notebooks(catalog.scan())]
    assert len(stems) == len(set(stems))


def test_links_are_rewritten_for_the_site():
    notebooks = {"DSA/02-two-pointers/two_pointers.py": "notebooks/two_pointers.html"}
    src, page = PurePosixPath("DSA/README.md"), PurePosixPath("DSA/index.html")
    body = (
        '<a href="02-two-pointers/README.md">a</a>'
        '<a href="02-two-pointers/two_pointers.py">b</a>'
        '<a href="04-pointers-vs-window/reading-plan.md#day-4">c</a>'
        '<a href="https://example.com/x.md">d</a>'
        '<a href="#top">e</a>'
        '<a href="02-two-pointers/two-pointers-workbench.html">f</a>'
    )
    out = rewrite_links(body, src, page, notebooks)
    assert 'href="02-two-pointers/index.html"' in out
    assert 'href="../notebooks/two_pointers.html"' in out
    assert 'href="04-pointers-vs-window/reading-plan.html#day-4"' in out
    assert 'href="https://example.com/x.md"' in out and 'href="#top"' in out
    assert 'href="02-two-pointers/two-pointers-workbench.html"' in out


def test_built_site_has_no_broken_internal_links(tmp_path):
    import re

    site = tmp_path / "site"
    build_site.build(site, skip_notebooks=True)
    broken = []
    for page in site.rglob("*.html"):
        if page.parent.name == "notebooks":
            continue
        for href in re.findall(r'href="([^"]+)"', page.read_text(encoding="utf-8")):
            if re.match(r"^([a-z][a-z0-9+.-]*:|#|/)", href, re.I):
                continue
            target = (page.parent / href.split("#")[0].split("?")[0]).resolve()
            if target.is_dir():
                target = target / "index.html"
            skipped_notebook = target.parent == (site / "notebooks").resolve()  # not exported in this fast build
            if not target.exists() and not skipped_notebook:
                broken.append(f"{page.relative_to(site)} -> {href}")
    assert not broken, "\n".join(broken)

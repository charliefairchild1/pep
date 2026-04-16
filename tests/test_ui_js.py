"""Catch JavaScript syntax errors in the inline UI script before they ship.

The web UI's `<script>` block is a single inline blob inside the Python
source. Twice now, a small Python-side mistake (an unescaped `\\n` in a
JS string, a top-level reference to `d3.zoomIdentity` before D3 loaded)
has produced a syntax error or runtime error that kills the *entire*
script block — including the tab click handler — leaving the UI looking
fine but actually unusable.

These tests are a backstop. If `node` is installed, we run `node -c` on
the extracted inline script and fail loudly on any syntax error. If
`node` is not installed, the tests skip rather than passing falsely.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pep.main import app


SCRIPT_RE = re.compile(r"<script>\n(.*?)\n</script>", re.DOTALL)


def _fetch_ui_html() -> str:
    with TestClient(app) as client:
        r = client.get("/ui")
        assert r.status_code == 200
        return r.text


def _extract_inline_script(html: str) -> str:
    """Pull the inline <script> block out of the served HTML."""
    matches = SCRIPT_RE.findall(html)
    assert matches, "no inline <script> block found in /ui"
    # Return the longest match (the real code, not stubs)
    return max(matches, key=len)


def test_inline_script_extracted() -> None:
    html = _fetch_ui_html()
    js = _extract_inline_script(html)
    assert len(js) > 1000  # we have substantial JS
    # A few sentinels confirming we got the right block
    assert "loadSky" in js
    assert "appendMsg" in js
    assert "startDialogue" in js


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node not installed; can't validate JS syntax",
)
def test_inline_script_parses_with_node() -> None:
    """Run `node -c` against the extracted JS. Fails loudly on syntax errors."""
    html = _fetch_ui_html()
    js = _extract_inline_script(html)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as f:
        f.write(js)
        tmp_path = Path(f.name)

    try:
        result = subprocess.run(
            ["node", "-c", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"Inline JS failed to parse:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
    finally:
        tmp_path.unlink(missing_ok=True)


def test_no_top_level_d3_references() -> None:
    """Top-level `d3.anything` is forbidden because the CDN may not be loaded
    yet at script parse time. References to d3 must live inside functions."""
    html = _fetch_ui_html()
    js = _extract_inline_script(html)

    # Strip strings and comments very crudely so we don't false-positive on
    # mentions inside string literals or // comments. This isn't a real JS
    # parser, but it's good enough for this guardrail.
    cleaned = re.sub(r"//.*", "", js)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'"[^"\n]*"', '""', cleaned)
    cleaned = re.sub(r"'[^'\n]*'", "''", cleaned)
    cleaned = re.sub(r"`[^`]*`", "``", cleaned, flags=re.DOTALL)

    depth = 0
    i = 0
    while i < len(cleaned):
        ch = cleaned[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif depth == 0 and cleaned[i : i + 3] == "d3.":
            start = max(0, i - 40)
            end = min(len(cleaned), i + 40)
            raise AssertionError(
                f"Top-level reference to `d3.` found at offset {i}: "
                f"...{cleaned[start:end]!r}... "
                f"All d3 access must live inside a function so the script "
                f"survives if the CDN hasn't loaded yet."
            )
        i += 1

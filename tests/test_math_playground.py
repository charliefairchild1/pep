"""Math playground page tests — endpoint + JS validation."""

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


def test_math_page_returns_200() -> None:
    with TestClient(app) as client:
        r = client.get("/math")
        assert r.status_code == 200
        assert "Graph Builder" in r.text
        assert "Spreading Activation" in r.text
        assert "Power" in r.text


def test_math_page_has_all_five_sections() -> None:
    with TestClient(app) as client:
        r = client.get("/math")
        html = r.text
        assert "graph-builder" in html
        assert "spreading" in html
        assert "scoring" in html
        assert "power-effect" in html
        assert "lifecycle" in html


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="node not installed; can't validate JS syntax",
)
def test_math_page_inline_js_parses_cleanly() -> None:
    """Run `node -c` against the inline script to catch syntax errors."""
    with TestClient(app) as client:
        html = client.get("/math").text

    matches = SCRIPT_RE.findall(html)
    assert matches, "no inline <script> block found in /math"
    js = max(matches, key=len)
    assert len(js) > 500  # substantial JS

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as f:
        f.write(js)
        tmp_path = Path(f.name)

    try:
        result = subprocess.run(
            ["node", "-c", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"Math playground JS failed to parse:\n{result.stderr}"
            )
    finally:
        tmp_path.unlink(missing_ok=True)

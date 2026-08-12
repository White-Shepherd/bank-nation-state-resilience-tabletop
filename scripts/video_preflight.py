from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = ROOT / "data" / "synthetic_assessments" / "harbor-ridge-2026.json"
REQUIRED = [
    ROOT / "app.py",
    SYNTHETIC,
    ROOT / "presentations/board/executive-resilience-briefing.pdf",
    ROOT / "examples/board-packet/board-packet.pdf",
]
PRIVATE_MARKERS = ["C:\\Users\\", "/Users/", "data/private_assessments/"]


def check(url: str, output: Path) -> tuple[list[str], list[str]]:
    passed, failed = [], []
    for path in REQUIRED:
        (passed if path.exists() else failed).append(f"required file: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(SYNTHETIC.read_text(encoding="utf-8"))
        assert payload["organization"]["name"] == "Harbor Ridge Bank"
        passed.append("canonical synthetic assessment loads")
    except (OSError, ValueError, KeyError, AssertionError) as exc:
        failed.append(f"canonical synthetic assessment: {exc}")
    output.mkdir(parents=True, exist_ok=True)
    passed.append("recording output directory exists")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            (passed if response.status == 200 else failed).append(f"application responds: {url}")
    except OSError as exc:
        failed.append(f"application unavailable at {url}: {exc}")
    video_root = ROOT / "video"
    for path in video_root.rglob("*.md") if video_root.exists() else []:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVATE_MARKERS:
            if marker in text:
                failed.append(f"privacy marker {marker!r}: {path.relative_to(ROOT)}")
    branch = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()
    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.splitlines()
    passed.append(
        f"repository documented: branch={branch}; commit={commit}; changed-files={len(status)}"
    )
    return passed, failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the Continuum Resilience recording state.")
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--output", type=Path, default=ROOT / "video/recordings")
    args = parser.parse_args()
    passed, failed = check(args.url, args.output)
    print("VIDEO PREFLIGHT")
    for item in passed:
        print(f"PASS  {item}")
    for item in failed:
        print(f"FAIL  {item}")
    print(f"RESULT {len(passed)} passed; {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

"""Validate governed Markdown records under docs/agent-learning."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ALLOWED_STATUSES = {"proposed", "validated", "rejected", "superseded"}
RECORD_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}-[a-z0-9][a-z0-9-]*\.md$")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_CODE = re.compile(r"`([^`\n]+)`")
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "credential assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
    "private data path": re.compile(r"(?i)(?:data/private_assessments|private[_-]telemetry|real[_-]client[_-]data)"),
}

SCHEMAS = {
    "builder": (
        "Agent role",
        "Task",
        "Branch",
        "Commit reviewed or produced",
        "Date",
        "Status",
    ),
    "reviewer": ("Reviewer role", "Scope", "Branch", "Commit reviewed", "Date", "Status"),
    "decisions": ("Decision owner", "Decision", "Branch", "Commit", "Date", "Status"),
    "patterns": ("Pattern owner", "Context", "Evidence commit", "Date", "Status"),
    "unresolved": ("Owner", "Question", "Branch", "Commit", "Date", "Status"),
    "synthesis": ("Synthesis owner", "Evidence through commit", "Date", "Status"),
}


def metadata(text: str) -> dict[str, str]:
    return {
        key.strip(): value.strip()
        for key, value in re.findall(r"(?m)^- ([^:\n]+):\s*(.*)$", text)
    }


def record_kind(path: Path, learning_root: Path) -> str | None:
    relative = path.relative_to(learning_root).as_posix()
    if relative.startswith("lessons/builder/"):
        return "builder"
    if relative.startswith("lessons/reviewer/"):
        return "reviewer"
    if relative.startswith("decisions/"):
        return "decisions"
    if relative.startswith("patterns/"):
        return "patterns"
    if relative.startswith("unresolved/"):
        return "unresolved"
    if relative == "synthesized-lessons.md":
        return "synthesis"
    return None


def is_repository_path(value: str) -> bool:
    value = value.strip().replace("\\", "/")
    if value.startswith(("http://", "https://", "C:/", "/")) or "*" in value:
        return False
    prefixes = (
        ".github/", "brand/", "data/", "docs/", "output/", "presentations/",
        "scripts/", "src/", "tests/", "tmp/", "video/", "README.md", ".gitignore",
    )
    return value.startswith(prefixes) and " " not in value


def validate(root: Path) -> list[str]:
    learning_root = root / "docs" / "agent-learning"
    errors: list[str] = []
    records: list[Path] = []

    for path in sorted(learning_root.rglob("*.md")):
        kind = record_kind(path, learning_root)
        if kind is None:
            continue
        records.append(path)
        text = path.read_text(encoding="utf-8")
        fields = metadata(text)
        for field in SCHEMAS[kind]:
            if not fields.get(field):
                errors.append(f"{path.relative_to(root)}: missing metadata '{field}'")
        status = fields.get("Status", "").split()[0].strip("`|")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{path.relative_to(root)}: invalid status '{status}'")
        if kind != "synthesis" and not RECORD_NAME.fullmatch(path.name):
            errors.append(f"{path.relative_to(root)}: invalid record filename")

    folded = [path.name.casefold() for path in records if path.name != "synthesized-lessons.md"]
    for name, count in Counter(folded).items():
        if count > 1:
            errors.append(f"duplicate record filename: {name}")

    for path in sorted(learning_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        for target in LINK.findall(text):
            target = target.split("#", 1)[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"{relative}: broken internal link '{target}'")
        for value in INLINE_CODE.findall(text):
            if is_repository_path(value) and not (root / value.replace("\\", "/")).exists():
                errors.append(f"{relative}: missing repository path '{value}'")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{relative}: possible {label} exposure")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Agent-learning validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Agent-learning validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Guard the compact PMO release-planning index."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


INDEX_PATH = Path("Documentation/zigux/release-planning-index.md")
REQUIRED_DOCS = [
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase13-release-coordination-matrix.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
]
REQUIRED_MARKERS = [
    "`RELEASE_PACKET_STATUS=active_not_closed`",
    "docs-root release index guard: `python3 scripts/zigux/check-release-planning-index.py`",
    "- Phase 12 remains the active shared release packet",
    "- Phase 13 remains the active helper-release packet",
    "- Phase 14 remains the release-boundary and productization reminder packet.",
    "- Phase 15 remains Architecture Council governance",
]


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    index_path = root / INDEX_PATH
    if not index_path.exists():
        return [f"missing_file:{INDEX_PATH.as_posix()}"]

    text = index_path.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing_marker:{marker}")

    for relpath in REQUIRED_DOCS:
        if relpath not in text:
            issues.append(f"missing_doc_reference:{relpath}")
        if not (root / relpath).exists():
            issues.append(f"missing_support_file:{relpath}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="release-planning-index-") as tmp:
        root = Path(tmp)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
        text = ["# Release Planning Index", ""]
        text.extend(REQUIRED_MARKERS)
        text.extend(REQUIRED_DOCS)
        (root / INDEX_PATH).write_text("\n".join(text) + "\n", encoding="utf-8")
        for relpath in REQUIRED_DOCS:
            path = root / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("ok\n", encoding="utf-8")

        assert collect_issues(root) == []

        (root / REQUIRED_DOCS[0]).unlink()
        issues = collect_issues(root)
        assert f"missing_support_file:{REQUIRED_DOCS[0]}" in issues

    print("RELEASE_PLANNING_INDEX_SELFTEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(Path.cwd())
    if issues:
        print("RELEASE_PLANNING_INDEX=fail")
        for issue in issues:
            print(issue)
        return 1

    print("RELEASE_PLANNING_INDEX=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

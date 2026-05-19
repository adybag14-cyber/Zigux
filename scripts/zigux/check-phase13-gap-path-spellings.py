#!/usr/bin/env python3
"""Guard Phase 13 contributor-facing gap path spellings."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


TRACKED_FILES = (
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase13-shared-summary-guard-gap.md",
    "Documentation/zigux/phase13-gap-path-spellings.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

CANONICAL_PATHS = (
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/helpers/notifier_chain_view.zig",
    "include/zigux/notifier_abi.h",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
)

STALE_SPELLINGS = (
    "zigux/tests/phase13Devres_reviewability.zig",
)

ALLOWED_STALE_CONTEXT_MARKERS = (
    "treat that as stale wording",
    "Stale Spellings To Reject",
    "historical wording only",
)

NOTE_PATH = "Documentation/zigux/phase13-gap-path-spellings.md"

NOTE_REQUIRED_MARKERS = (
    "validator: `python3 scripts/zigux/check-phase13-gap-path-spellings.py`",
    "## Canonical Gap Spellings",
    "## Stale Spellings To Reject",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13Devres_reviewability.zig",
    "Keep `zigux/Makefile` distinct from the still-missing Phase 13 route names above.",
)


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    try:
        note_text = read_text(root, NOTE_PATH)
    except SystemExit as exc:
        issues.append(str(exc))
        return issues

    for marker in NOTE_REQUIRED_MARKERS:
        if marker not in note_text:
            issues.append(f"missing_note_marker:{marker}")

    for relpath in TRACKED_FILES:
        try:
            text = read_text(root, relpath)
        except SystemExit as exc:
            issues.append(str(exc))
            continue

        for stale in STALE_SPELLINGS:
            if stale in text and not any(marker in text for marker in ALLOWED_STALE_CONTEXT_MARKERS):
                issues.append(f"stale_spelling_without_context:{relpath}:{stale}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_GAP_PATH_SPELLINGS=fail")
    print("PHASE13_GAP_PATH_SPELLINGS_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_GAP_PATH_SPELLINGS_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    note_body = """# Phase 13 Gap Path Spellings

validator: `python3 scripts/zigux/check-phase13-gap-path-spellings.py`

## Canonical Gap Spellings

- `zigux/tests/phase13_devres_reviewability.zig`

Keep `zigux/Makefile` distinct from the still-missing Phase 13 route names above.

## Stale Spellings To Reject

- `zigux/tests/phase13Devres_reviewability.zig`

Treat these as historical wording only.
"""
    write_text(root, NOTE_PATH, note_body)

    good_warning = (
        "If a contributor-facing note still uses `zigux/tests/phase13Devres_reviewability.zig`, "
        "treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig`."
    )

    for relpath in TRACKED_FILES:
        if relpath == NOTE_PATH:
            continue
        write_text(root, relpath, good_warning + "\n")


def expect_issue(issues: list[str], expected: str) -> None:
    assert expected in issues, f"missing expected issue: {expected}"


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-gap-path-spellings-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        note_path = tempdir / NOTE_PATH
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "## Stale Spellings To Reject\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_note_marker:## Stale Spellings To Reject",
        )
        checks_run += 1

        populate_repo(tempdir)
        sync_path = tempdir / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"
        sync_path.write_text(
            "Broad reminder drift: `zigux/tests/phase13Devres_reviewability.zig`\n",
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "stale_spelling_without_context:Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md:zigux/tests/phase13Devres_reviewability.zig",
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_GAP_PATH_SPELLINGS_SELF_TEST=pass")
    print(f"PHASE13_GAP_PATH_SPELLINGS_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard canonical Phase 13 gap path spellings in contributor-facing notes."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_GAP_PATH_SPELLINGS=pass")
    print(f"PHASE13_GAP_PATH_TRACKED_FILE_COUNT={len(TRACKED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
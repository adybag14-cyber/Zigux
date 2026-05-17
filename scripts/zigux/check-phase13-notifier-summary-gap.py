#!/usr/bin/env python3
"""Guard the current Phase 13 notifier summary drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GAP_NOTE = Path("Documentation/zigux/phase13-notifier-summary-gap.md")
SCRIPTS_README = Path("scripts/zigux/README.md")

MISSING_NOTE_MARKERS = (
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/tests/phase13_build.zig`",
)

SCRIPTS_README_GAP_MARKERS = (
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/tests/phase13_build.zig`",
)

STILL_MISSING_DIRECT_MARKERS = (
    "`scripts/zigux/check-phase13-notifier-packet.py`",
    "`include/zigux/notifier_abi.h`",
    "`zigux/helpers/list_view.zig`",
    "`zigux/helpers/hlist_view.zig`",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in (GAP_NOTE, SCRIPTS_README):
        if not (root / rel_path).exists():
            issues.append(f"missing_file:{rel_path}")
    if issues:
        return issues

    gap_note = read_text(root / GAP_NOTE)
    scripts_readme = read_text(root / SCRIPTS_README)

    for marker in MISSING_NOTE_MARKERS:
        if marker not in gap_note:
            issues.append(f"missing_gap_note_missing_packet_marker:{marker}")

    for marker in STILL_MISSING_DIRECT_MARKERS:
        if marker not in gap_note:
            issues.append(f"missing_gap_note_direct_gap_marker:{marker}")

    for marker in SCRIPTS_README_GAP_MARKERS:
        if marker not in scripts_readme:
            issues.append(f"missing_scripts_readme_gap_marker:{marker}")

    for marker in STILL_MISSING_DIRECT_MARKERS:
        if marker not in scripts_readme:
            issues.append(f"missing_scripts_readme_direct_gap_marker:{marker}")

    return issues


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def seed_tree(root: Path) -> None:
    gap_note = "\n".join(
        [
            "# Phase 13 Notifier Summary Gap",
            "",
            "Fresh current-`master` reads still return missing for these notifier-facing packet files:",
            "",
            *MISSING_NOTE_MARKERS,
            "",
            "These direct companions should remain treated as gaps unless a future same-lane reread proves otherwise:",
            "",
            *STILL_MISSING_DIRECT_MARKERS,
            "",
        ]
    )
    scripts_readme = "\n".join(
        [
            "# scripts/zigux",
            "",
            "Phase 13 still returns missing for these notifier-facing packet files:",
            "",
            *SCRIPTS_README_GAP_MARKERS,
            "",
            "Direct companions that should stay in the gap bucket include:",
            "",
            *STILL_MISSING_DIRECT_MARKERS,
            "",
        ]
    )

    write_text(root / GAP_NOTE, gap_note)
    write_text(root / SCRIPTS_README, scripts_readme)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase13-notifier-summary-gap-") as tmpdir:
        root = Path(tmpdir)
        seed_tree(root)
        assert_only(validate(root), [], "baseline_should_pass")

        seed_tree(root)
        write_text(root / GAP_NOTE, "# Phase 13 Notifier Summary Gap\n")
        assert_only(
            validate(root),
            [
                "missing_gap_note_missing_packet_marker:`Documentation/zigux/phase13-notifier-list-survey.md`",
                "missing_gap_note_missing_packet_marker:`zigux/tests/phase13_notifier_list_manifest.json`",
                "missing_gap_note_missing_packet_marker:`zigux/tests/phase13_notifier_list_reviewability.zig`",
                "missing_gap_note_missing_packet_marker:`zigux/tests/phase13_build.zig`",
                "missing_gap_note_direct_gap_marker:`scripts/zigux/check-phase13-notifier-packet.py`",
                "missing_gap_note_direct_gap_marker:`include/zigux/notifier_abi.h`",
                "missing_gap_note_direct_gap_marker:`zigux/helpers/list_view.zig`",
                "missing_gap_note_direct_gap_marker:`zigux/helpers/hlist_view.zig`",
            ],
            "gap_note_marker_failure",
        )

        seed_tree(root)
        write_text(root / SCRIPTS_README, "# scripts/zigux\n")
        assert_only(
            validate(root),
            [
                "missing_scripts_readme_gap_marker:`zigux/tests/phase13_notifier_list_manifest.json`",
                "missing_scripts_readme_gap_marker:`zigux/tests/phase13_notifier_list_reviewability.zig`",
                "missing_scripts_readme_gap_marker:`zigux/tests/phase13_build.zig`",
                "missing_scripts_readme_direct_gap_marker:`scripts/zigux/check-phase13-notifier-packet.py`",
                "missing_scripts_readme_direct_gap_marker:`include/zigux/notifier_abi.h`",
                "missing_scripts_readme_direct_gap_marker:`zigux/helpers/list_view.zig`",
                "missing_scripts_readme_direct_gap_marker:`zigux/helpers/hlist_view.zig`",
            ],
            "scripts_readme_marker_failure",
        )

    print("PHASE13_NOTIFIER_SUMMARY_GAP_SELF_TEST=pass")
    print("PHASE13_NOTIFIER_SUMMARY_GAP_SELF_TEST_CASES=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 13 notifier summary drift stays explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("PHASE13_NOTIFIER_SUMMARY_GAP=present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the current Phase 13 notifier summary drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GAP_NOTE = Path("Documentation/zigux/phase13-notifier-summary-gap.md")
SURVEY = Path("Documentation/zigux/phase13-notifier-list-survey.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
MANIFEST = Path("zigux/tests/phase13_notifier_list_manifest.json")
REVIEWABILITY = Path("zigux/tests/phase13_notifier_list_reviewability.zig")
PHASE13_BUILD = Path("zigux/tests/phase13_build.zig")

LIVE_MARKERS = (
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/tests/phase13_build.zig`",
)

BROAD_SURFACE_STALE_MARKERS = (
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/tests/phase13_build.zig`",
)

STILL_MISSING_MARKERS = (
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
    for rel_path in (GAP_NOTE, SURVEY, SCRIPTS_README, MANIFEST, REVIEWABILITY, PHASE13_BUILD):
        if not (root / rel_path).exists():
            issues.append(f"missing_file:{rel_path}")
    if issues:
        return issues

    gap_note = read_text(root / GAP_NOTE)
    survey = read_text(root / SURVEY)
    scripts_readme = read_text(root / SCRIPTS_README)

    for marker in LIVE_MARKERS:
        if marker not in gap_note:
            issues.append(f"missing_gap_note_live_marker:{marker}")

    for marker in STILL_MISSING_MARKERS:
        if marker not in gap_note:
            issues.append(f"missing_gap_note_still_missing_marker:{marker}")

    for marker in BROAD_SURFACE_STALE_MARKERS:
        if marker not in survey:
            issues.append(f"missing_survey_stale_marker:{marker}")
        if marker not in scripts_readme:
            issues.append(f"missing_scripts_readme_stale_marker:{marker}")

    for marker in STILL_MISSING_MARKERS:
        if marker not in survey:
            issues.append(f"missing_survey_gap_marker:{marker}")
        if marker not in scripts_readme:
            issues.append(f"missing_scripts_readme_gap_marker:{marker}")

    return issues


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def seed_tree(root: Path) -> None:
    gap_note = "\n".join(
        [
            "# Phase 13 Notifier Summary Gap",
            "",
            "Current `master` still materializes these notifier-facing packet files:",
            "",
            *LIVE_MARKERS,
            "",
            "These direct companions should remain treated as gaps unless a future same-lane reread proves otherwise:",
            "",
            *STILL_MISSING_MARKERS,
            "",
        ]
    )
    broad_surface = "\n".join(
        [
            "The broad reminder still lists these as repo-reality gaps:",
            "",
            *BROAD_SURFACE_STALE_MARKERS,
            "",
            "The real same-lane direct companions that still stay missing are:",
            "",
            *STILL_MISSING_MARKERS,
            "",
        ]
    )

    write_text(root / GAP_NOTE, gap_note)
    write_text(root / SURVEY, broad_surface)
    write_text(root / SCRIPTS_README, broad_surface)
    write_text(root / MANIFEST, "{\n  \"lane_key\": \"P13-L19\"\n}\n")
    write_text(root / REVIEWABILITY, 'test "phase13 notifier reviewability" {}\n')
    write_text(root / PHASE13_BUILD, 'const std = @import("std");\n')


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
                "missing_gap_note_live_marker:`zigux/tests/phase13_notifier_list_manifest.json`",
                "missing_gap_note_live_marker:`zigux/tests/phase13_notifier_list_reviewability.zig`",
                "missing_gap_note_live_marker:`zigux/tests/phase13_build.zig`",
                "missing_gap_note_still_missing_marker:`scripts/zigux/check-phase13-notifier-packet.py`",
                "missing_gap_note_still_missing_marker:`include/zigux/notifier_abi.h`",
                "missing_gap_note_still_missing_marker:`zigux/helpers/list_view.zig`",
                "missing_gap_note_still_missing_marker:`zigux/helpers/hlist_view.zig`",
            ],
            "gap_note_marker_failure",
        )

        seed_tree(root)
        write_text(root / SCRIPTS_README, "Phase 13 flow\n")
        assert_only(
            validate(root),
            [
                "missing_scripts_readme_stale_marker:`zigux/tests/phase13_notifier_list_manifest.json`",
                "missing_scripts_readme_stale_marker:`zigux/tests/phase13_notifier_list_reviewability.zig`",
                "missing_scripts_readme_stale_marker:`zigux/tests/phase13_build.zig`",
                "missing_scripts_readme_gap_marker:`scripts/zigux/check-phase13-notifier-packet.py`",
                "missing_scripts_readme_gap_marker:`include/zigux/notifier_abi.h`",
                "missing_scripts_readme_gap_marker:`zigux/helpers/list_view.zig`",
                "missing_scripts_readme_gap_marker:`zigux/helpers/hlist_view.zig`",
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

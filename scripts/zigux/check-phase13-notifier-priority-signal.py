#!/usr/bin/env python3
"""Fail closed on the current Phase 13 notifier priority-signal reminder surface."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase13-notifier-priority-signal.py"
NOTIFIER_SURVEY_PATH = "Documentation/zigux/phase13-notifier-list-survey.md"
RELEASE_NOTES_PATH = "Documentation/zigux/phase13-release-notes-survey.md"
TRACEABILITY_PATH = "Documentation/zigux/phase13-roadmap-traceability.md"
CONTRIBUTOR_GUIDE_PATH = "Documentation/zigux/phase13-contributor-workflow-guide.md"
LANE_NOTE_PATH = "Documentation/zigux/phase13-shared-helper-lane-sequencing.md"
CONTRIBUTOR_SYNC_PATH = "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"
TESTS_COMPANION_PATH = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
RELEASE_VALIDATOR_PATH = "scripts/zigux/validate-phase13-release.py"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
NOTIFIER_BINDINGS_PATH = "zigux/bindings/notifier_abi.zig"
NOTIFIER_HELPER_PATH = "zigux/helpers/notifier_chain_view.zig"
ABI_HEADER_PATH = "include/zigux/abi.h"
HVC_HEADER_PATH = "drivers/tty/hvc/hvc_console.h"

REQUIRED_FILES = (
    SCRIPT_PATH,
    NOTIFIER_SURVEY_PATH,
    RELEASE_NOTES_PATH,
    TRACEABILITY_PATH,
    CONTRIBUTOR_GUIDE_PATH,
    LANE_NOTE_PATH,
    CONTRIBUTOR_SYNC_PATH,
    TESTS_COMPANION_PATH,
    RELEASE_VALIDATOR_PATH,
    SCRIPTS_README_PATH,
    NOTIFIER_BINDINGS_PATH,
    NOTIFIER_HELPER_PATH,
    ABI_HEADER_PATH,
    HVC_HEADER_PATH,
)

REQUIRED_NOTIFIER_SURVEY_MARKERS = (
    "# Phase 13 Notifier List Survey",
    "nonincreasing-priority signal",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`scripts/zigux/validate-phase13-release.py`",
    "repo-reality gaps instead of independently shipped evidence",
    "`make -C zigux phase13-validate`",
)

REQUIRED_RELEASE_NOTES_MARKERS = (
    "Broad summaries should also keep the adjacent notifier evidence packet visible through the current materialized review surfaces:",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "broad summaries should record those paths as repo-reality gaps rather than independently shipped current-`master` evidence.",
)

REQUIRED_TRACEABILITY_MARKERS = (
    "adjacent notifier evidence maps to Phase 13 release-surface truthfulness only",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "record them as repo-reality gaps instead of presenting them here as independently shipped evidence.",
)

REQUIRED_CONTRIBUTOR_GUIDE_MARKERS = (
    "Keep notifier evidence adjacent to that packet rather than treating it as a fifth helper anchor.",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "record them as adjacent repo-reality gaps instead of as independently shipped review evidence:",
)

REQUIRED_LANE_NOTE_MARKERS = (
    "Adjacent notifier evidence stays in scope for release-surface truthfulness",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "keep them recorded as adjacent repo-reality gaps instead of shipped evidence.",
)

REQUIRED_CONTRIBUTOR_SYNC_MARKERS = (
    "## Phase 13 contributor packet",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "treat notifier evidence as adjacent release-surface support rather than a fifth shared-helper anchor",
)

REQUIRED_TESTS_COMPANION_MARKERS = (
    "## Phase 13 tests-root packet",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.",
)

REQUIRED_RELEASE_VALIDATOR_MARKERS = (
    '"scripts/zigux/check-phase13-notifier-priority-signal.py",',
    '"Documentation/zigux/phase13-notifier-list-survey.md",',
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "Phase 13 flow -",
    "`check-phase13-notifier-priority-signal.py`",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "adjacent release-surface evidence",
    "the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` stay explicit on current `master`.",
)

REQUIRED_NOTIFIER_BINDINGS_MARKERS = (
    "pub const NotifierBlock = extern struct {",
    "next: usize,",
    "priority: i32,",
)

REQUIRED_NOTIFIER_HELPER_MARKERS = (
    "pub const ChainView = struct {",
    "pub fn hasNonincreasingPriority(self: ChainView) bool {",
    "test \"chain view checks nonincreasing notifier priority\" {",
)

REQUIRED_ABI_HEADER_MARKERS = (
    "#define ZIGUX_ABI_VERSION 1U",
    "struct zigux_boundary_header {",
    "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
)

REQUIRED_HVC_HEADER_MARKERS = (
    "extern int notifier_add_irq(struct hvc_struct *hp, int data);",
    "extern void notifier_del_irq(struct hvc_struct *hp, int data);",
    "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    checks = (
        ("notifier-survey", NOTIFIER_SURVEY_PATH, REQUIRED_NOTIFIER_SURVEY_MARKERS),
        ("release-notes", RELEASE_NOTES_PATH, REQUIRED_RELEASE_NOTES_MARKERS),
        ("traceability", TRACEABILITY_PATH, REQUIRED_TRACEABILITY_MARKERS),
        ("contributor-guide", CONTRIBUTOR_GUIDE_PATH, REQUIRED_CONTRIBUTOR_GUIDE_MARKERS),
        ("lane-note", LANE_NOTE_PATH, REQUIRED_LANE_NOTE_MARKERS),
        ("contributor-sync", CONTRIBUTOR_SYNC_PATH, REQUIRED_CONTRIBUTOR_SYNC_MARKERS),
        ("tests-companion", TESTS_COMPANION_PATH, REQUIRED_TESTS_COMPANION_MARKERS),
        ("release-validator", RELEASE_VALIDATOR_PATH, REQUIRED_RELEASE_VALIDATOR_MARKERS),
        ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS),
        ("notifier-bindings", NOTIFIER_BINDINGS_PATH, REQUIRED_NOTIFIER_BINDINGS_MARKERS),
        ("notifier-helper", NOTIFIER_HELPER_PATH, REQUIRED_NOTIFIER_HELPER_MARKERS),
        ("abi-header", ABI_HEADER_PATH, REQUIRED_ABI_HEADER_MARKERS),
        ("hvc-header", HVC_HEADER_PATH, REQUIRED_HVC_HEADER_MARKERS),
    )
    for label, rel_path, markers in checks:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{label}:{marker}")
    return problems


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    write_text(root, SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write_text(root, NOTIFIER_SURVEY_PATH, "\n".join(REQUIRED_NOTIFIER_SURVEY_MARKERS) + "\n")
    write_text(root, RELEASE_NOTES_PATH, "\n".join(REQUIRED_RELEASE_NOTES_MARKERS) + "\n")
    write_text(root, TRACEABILITY_PATH, "\n".join(REQUIRED_TRACEABILITY_MARKERS) + "\n")
    write_text(root, CONTRIBUTOR_GUIDE_PATH, "\n".join(REQUIRED_CONTRIBUTOR_GUIDE_MARKERS) + "\n")
    write_text(root, LANE_NOTE_PATH, "\n".join(REQUIRED_LANE_NOTE_MARKERS) + "\n")
    write_text(root, CONTRIBUTOR_SYNC_PATH, "\n".join(REQUIRED_CONTRIBUTOR_SYNC_MARKERS) + "\n")
    write_text(root, TESTS_COMPANION_PATH, "\n".join(REQUIRED_TESTS_COMPANION_MARKERS) + "\n")
    write_text(root, RELEASE_VALIDATOR_PATH, "\n".join(REQUIRED_RELEASE_VALIDATOR_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, NOTIFIER_BINDINGS_PATH, "\n".join(REQUIRED_NOTIFIER_BINDINGS_MARKERS) + "\n")
    write_text(root, NOTIFIER_HELPER_PATH, "\n".join(REQUIRED_NOTIFIER_HELPER_MARKERS) + "\n")
    write_text(root, ABI_HEADER_PATH, "\n".join(REQUIRED_ABI_HEADER_MARKERS) + "\n")
    write_text(root, HVC_HEADER_PATH, "\n".join(REQUIRED_HVC_HEADER_MARKERS) + "\n")


def assert_missing_case(root: Path, label: str, rel_path: str, needle: str) -> None:
    text = read_text(root, rel_path)
    if needle not in text:
        raise SystemExit(f"self-test-fixture-missing:{label}")
    write_text(root, rel_path, text.replace(needle, "", 1))
    problems = validate(root)
    expected = f"missing-marker:{label}:{needle}"
    if expected not in problems:
        raise SystemExit(f"self-test-mismatch:{label}:{problems}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_notifier_signal_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = validate(baseline_root)
        if baseline:
            raise SystemExit(f"self-test-baseline-failed:{baseline}")

        mutations = (
            ("notifier-survey", NOTIFIER_SURVEY_PATH, REQUIRED_NOTIFIER_SURVEY_MARKERS[1]),
            ("release-notes", RELEASE_NOTES_PATH, REQUIRED_RELEASE_NOTES_MARKERS[3]),
            ("traceability", TRACEABILITY_PATH, REQUIRED_TRACEABILITY_MARKERS[3]),
            ("contributor-guide", CONTRIBUTOR_GUIDE_PATH, REQUIRED_CONTRIBUTOR_GUIDE_MARKERS[3]),
            ("lane-note", LANE_NOTE_PATH, REQUIRED_LANE_NOTE_MARKERS[3]),
            ("contributor-sync", CONTRIBUTOR_SYNC_PATH, REQUIRED_CONTRIBUTOR_SYNC_MARKERS[3]),
            ("contributor-sync", CONTRIBUTOR_SYNC_PATH, REQUIRED_CONTRIBUTOR_SYNC_MARKERS[5]),
            ("tests-companion", TESTS_COMPANION_PATH, REQUIRED_TESTS_COMPANION_MARKERS[3]),
            ("tests-companion", TESTS_COMPANION_PATH, REQUIRED_TESTS_COMPANION_MARKERS[5]),
            ("release-validator", RELEASE_VALIDATOR_PATH, REQUIRED_RELEASE_VALIDATOR_MARKERS[0]),
            ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS[3]),
            ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS[4]),
            ("notifier-bindings", NOTIFIER_BINDINGS_PATH, REQUIRED_NOTIFIER_BINDINGS_MARKERS[0]),
            ("notifier-helper", NOTIFIER_HELPER_PATH, REQUIRED_NOTIFIER_HELPER_MARKERS[1]),
            ("abi-header", ABI_HEADER_PATH, REQUIRED_ABI_HEADER_MARKERS[1]),
            ("hvc-header", HVC_HEADER_PATH, REQUIRED_HVC_HEADER_MARKERS[2]),
        )
        for label, rel_path, needle in mutations:
            case_root = Path(tmp) / f"{label}_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, label, rel_path, needle)
            cases += 1

    print("PHASE13_NOTIFIER_PRIORITY_SIGNAL_SELF_TEST=pass")
    print(f"PHASE13_NOTIFIER_PRIORITY_SIGNAL_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    root = Path(__file__).resolve()
    default_root = root.parents[2] if len(root.parents) > 2 else Path.cwd()
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 13 notifier priority-signal reminder surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage.")
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="Repository root to validate.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("PHASE13_NOTIFIER_PRIORITY_SIGNAL=fail")
        print("PHASE13_NOTIFIER_PRIORITY_SIGNAL_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE13_NOTIFIER_PRIORITY_SIGNAL_PROBLEMS_END")
        return 1

    print("PHASE13_NOTIFIER_PRIORITY_SIGNAL=pass")
    print(f"PHASE13_NOTIFIER_PRIORITY_SIGNAL_ROOT={args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

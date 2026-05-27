#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

LEDGER_PATH = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

PHASE5_HANDOFF_HEADING = "## Release-Planning Continuation"
PHASE5_HANDOFF_MARKER = (
    "For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the "
    "ledger-side handoff instead of inventing synthetic later-train commit entries:"
)
PRACTICAL_RULE = "- Practical rule:"
PHASE5_RULE = (
    "use the Phase 5 closure note plus its two shared reminder companions when the question is "
    "which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane "
    "on `master`"
)
PHASE5_WRAPUP = (
    "This keeps the ledger truthful about the early train while making the live release packet "
    "explicit for later scheduled PMO runs and the active Phase 5 closure packet explicit for "
    "sample-lane runs."
)

PHASE5_LINKED_PATHS = (
    Path("Documentation/zigux/phase5-closure.md"),
    Path("Documentation/zigux/phase5-sample-lane-sequencing.md"),
    Path("Documentation/zigux/phase5-sample-review-guide.md"),
)

REQUIRED_MARKERS = (
    PHASE5_HANDOFF_HEADING,
    PHASE5_HANDOFF_MARKER,
    "`Documentation/zigux/phase5-closure.md`",
    "`Documentation/zigux/phase5-sample-lane-sequencing.md`",
    "`Documentation/zigux/phase5-sample-review-guide.md`",
    PHASE5_RULE,
    PHASE5_WRAPUP,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ledger_text(root: Path) -> str:
    return (root / LEDGER_PATH).read_text(encoding="utf-8")


def collect_missing_markers(root: Path) -> list[str]:
    ledger = _ledger_text(root)
    return [marker for marker in REQUIRED_MARKERS if marker not in ledger]


def collect_missing_paths(root: Path) -> list[str]:
    missing: list[str] = []
    for linked_path in PHASE5_LINKED_PATHS:
        if not (root / linked_path).exists():
            missing.append(str(linked_path))
    return missing


def collect_order_errors(root: Path) -> list[str]:
    ledger = _ledger_text(root)
    headings = (
        "- For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:",
        PHASE5_HANDOFF_MARKER,
        PRACTICAL_RULE,
    )
    positions: list[int] = []
    for marker in headings:
        idx = ledger.find(marker)
        if idx == -1:
            return []
        positions.append(idx)

    errors: list[str] = []
    if positions != sorted(positions):
        errors.append("phase5 handoff order drifted from PMO packet -> Phase5 handoff -> Practical rule")
    return errors


def count_linked_paths(root: Path) -> int:
    ledger = _ledger_text(root)
    return sum(1 for linked_path in PHASE5_LINKED_PATHS if f"`{linked_path.as_posix()}`" in ledger)


def _sample_ledger() -> str:
    return """# Zigux Alpha Bootstrap Commit Ledger

## Scope Note

- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.

## Release-Planning Continuation

- For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/phase12-release-sequencing.md`
- For the active Phase 5 non-runtime sample tranche, treat the landed closure note as the ledger-side handoff instead of inventing synthetic later-train commit entries:
  - `Documentation/zigux/phase5-closure.md`
  - `Documentation/zigux/phase5-sample-lane-sequencing.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
- Practical rule:
  - use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train
  - use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`
  - use the Phase 5 closure note plus its two shared reminder companions when the question is which active non-runtime sample tranche evidence currently governs the bounded Phase 5 lane on `master`
- This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs and the active Phase 5 closure packet explicit for sample-lane runs.
"""


def _swap_first(text: str, left: str, right: str) -> str:
    placeholder = "__LANE01_PHASE5_SWAP__"
    return text.replace(left, placeholder, 1).replace(right, left, 1).replace(placeholder, right, 1)


def write_sample_root(root: Path) -> None:
    _write(root / LEDGER_PATH, _sample_ledger())
    _write(root / PHASE5_LINKED_PATHS[0], "# Phase 5 Closure\n")
    _write(root / PHASE5_LINKED_PATHS[1], "# Phase 5 Sample Lane Sequencing\n")
    _write(root / PHASE5_LINKED_PATHS[2], "# Phase 5 Sample Review Guide\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase5_handoff_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        if collect_missing_markers(root):
            raise AssertionError("baseline Phase 5 handoff markers should pass")
        if collect_missing_paths(root):
            raise AssertionError("baseline Phase 5 handoff paths should exist")
        if collect_order_errors(root):
            raise AssertionError("baseline Phase 5 handoff order should pass")
        case_count += 1

        _write(root / LEDGER_PATH, _sample_ledger().replace(PHASE5_HANDOFF_MARKER + "\n", "", 1))
        expected = [PHASE5_HANDOFF_MARKER]
        if collect_missing_markers(root) != expected:
            raise AssertionError(f"unexpected missing handoff marker result: {collect_missing_markers(root)}")
        write_sample_root(root)
        case_count += 1

        _write(root / LEDGER_PATH, _sample_ledger().replace("`Documentation/zigux/phase5-sample-review-guide.md`\n", "", 1))
        expected = ["`Documentation/zigux/phase5-sample-review-guide.md`"]
        if collect_missing_markers(root) != expected:
            raise AssertionError(f"unexpected missing linked marker result: {collect_missing_markers(root)}")
        write_sample_root(root)
        case_count += 1

        (root / PHASE5_LINKED_PATHS[1]).unlink()
        expected = ["Documentation/zigux/phase5-sample-lane-sequencing.md"]
        if collect_missing_paths(root) != expected:
            raise AssertionError(f"unexpected missing linked path result: {collect_missing_paths(root)}")
        write_sample_root(root)
        case_count += 1

        _write(root / LEDGER_PATH, _sample_ledger().replace(PHASE5_RULE + "\n", "", 1))
        expected = [PHASE5_RULE]
        if collect_missing_markers(root) != expected:
            raise AssertionError(f"unexpected missing rule result: {collect_missing_markers(root)}")
        write_sample_root(root)
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _swap_first(
                _sample_ledger(),
                "- For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:",
                PHASE5_HANDOFF_MARKER,
            ),
        )
        expected = ["phase5 handoff order drifted from PMO packet -> Phase5 handoff -> Practical rule"]
        if collect_order_errors(root) != expected:
            raise AssertionError(f"unexpected order result: {collect_order_errors(root)}")
        case_count += 1

    print("LANE01_BOOTSTRAP_LEDGER_PHASE5_SAMPLE_HANDOFF_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_PHASE5_SAMPLE_HANDOFF_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap ledger Phase 5 sample handoff packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Phase 5 handoff fixtures",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal current-like root for checker replay",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)

    if args.self_test:
        return run_self_test()

    missing_markers = collect_missing_markers(args.root)
    missing_paths = collect_missing_paths(args.root)
    order_errors = collect_order_errors(args.root)
    if missing_markers or missing_paths or order_errors:
        for marker in missing_markers:
            print(f"ERROR: missing marker: {marker}")
        for linked_path in missing_paths:
            print(f"ERROR: missing linked path: {linked_path}")
        for order_error in order_errors:
            print(f"ERROR: section order: {order_error}")
        return 1

    print("LANE01_BOOTSTRAP_LEDGER_PHASE5_SAMPLE_HANDOFF=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_PHASE5_SAMPLE_HANDOFF_REQUIRED_LINE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"LANE01_BOOTSTRAP_LEDGER_PHASE5_SAMPLE_HANDOFF_LINKED_PATH_COUNT={count_linked_paths(args.root)}")
    print("LANE01_BOOTSTRAP_LEDGER_PHASE5_SAMPLE_HANDOFF_SECTION_ORDER=PMOPacket->Phase5Handoff->PracticalRule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

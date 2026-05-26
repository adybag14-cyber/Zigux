#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

LEDGER_PATH = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

REQUIRED_MARKERS = (
    "## Scope Note",
    "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
    "## Release-Planning Continuation",
    "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.",
    "Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train",
    "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`",
)

LINKED_PATH_MARKERS = (
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
)

SECTION_ORDER = (
    "## Scope Note",
    "## Release-Planning Continuation",
    "- Practical rule:",
)


def collect_missing_markers(root: Path) -> list[str]:
    ledger = (root / LEDGER_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in ledger:
            missing.append(marker)
    return missing


def collect_section_order_errors(root: Path) -> list[str]:
    ledger = (root / LEDGER_PATH).read_text(encoding="utf-8")
    positions: list[int] = []
    for heading in SECTION_ORDER:
        index = ledger.find(heading)
        if index == -1:
            return []
        positions.append(index)
    errors: list[str] = []
    if positions != sorted(positions):
        errors.append(
            f"{SECTION_ORDER[0]} must appear before {SECTION_ORDER[1]} before {SECTION_ORDER[2]}"
        )
    if ledger.count(SECTION_ORDER[2]) != 1:
        errors.append(f"{SECTION_ORDER[2]} must appear exactly once")
    return errors


def count_linked_paths(root: Path) -> int:
    ledger = (root / LEDGER_PATH).read_text(encoding="utf-8")
    return sum(1 for marker in LINKED_PATH_MARKERS if marker in ledger)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_ledger() -> str:
    return """# Zigux Alpha Bootstrap Commit Ledger

## Commit Train

25. `docs(zigux): reopen and close broadened Phase 2 tranche`

## Scope Note

- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.
- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.

## Release-Planning Continuation

- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.
- Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.
- For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-release-closure-checklist.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
- Practical rule:
  - use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train
  - use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_ledger_continuation_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / LEDGER_PATH, _sample_ledger())

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 bootstrap ledger release-planning fixture should pass")
        if collect_section_order_errors(root):
            raise AssertionError("baseline Lane 01 bootstrap ledger section order should pass")
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("## Release-Planning Continuation\n\n", "", 1),
        )
        missing = collect_missing_markers(root)
        expected = ["## Release-Planning Continuation"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for release-planning heading case: {missing}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = ["Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only."]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for item-25 authority case: {missing}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("`Documentation/zigux/phase12-release-coordination-matrix.md`\n", "", 1),
        )
        missing = collect_missing_markers(root)
        expected = ["`Documentation/zigux/phase12-release-coordination-matrix.md`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for PMO path case: {missing}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`"
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for practical-rule case: {missing}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("## Scope Note", "## Scope Note (moved)", 1).replace(
                "## Release-Planning Continuation",
                "## Scope Note",
                1,
            ).replace(
                "## Scope Note (moved)",
                "## Release-Planning Continuation",
                1,
            ),
        )
        order_errors = collect_section_order_errors(root)
        expected_order = [
            "## Scope Note must appear before ## Release-Planning Continuation before - Practical rule:"
        ]
        if order_errors != expected_order:
            raise AssertionError(f"unexpected section-order errors: {order_errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap ledger continuation packet remains reviewable."
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
        help="exercise the checker against synthetic Lane 01 ledger release-planning fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    order_errors = collect_section_order_errors(args.root)
    if missing or order_errors:
        for item in missing:
            print(f"ERROR: missing marker: {item}")
        for item in order_errors:
            print(f"ERROR: section order: {item}")
        return 1

    print("LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_REQUIRED_LINE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_LINKED_PATH_COUNT={count_linked_paths(args.root)}")
    print("LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SECTION_ORDER=ScopeNote->ReleasePlanningContinuation->PracticalRule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

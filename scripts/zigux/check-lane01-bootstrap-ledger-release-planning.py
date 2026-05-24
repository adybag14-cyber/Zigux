#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

LEDGER_PATH = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

REQUIRED_LINES = (
    "## Release-Planning Continuation",
    "- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.",
    "- Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.",
    "- For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/phase12-release-sequencing.md`",
    "- `Documentation/zigux/phase12-release-readiness-survey.md`",
    "- `Documentation/zigux/phase12-release-closure-checklist.md`",
    "- `Documentation/zigux/phase12-release-coordination-matrix.md`",
    "- `Documentation/zigux/phase14-release-boundary-survey.md`",
    "- Practical rule:",
    "- use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train",
    "- use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`",
    "- This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs.",
)

ORDER_MARKERS = (
    "## Scope Note",
    "## Release-Planning Continuation",
    "- Practical rule:",
)

LINK_LINES = (
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/phase12-release-sequencing.md`",
    "- `Documentation/zigux/phase12-release-readiness-survey.md`",
    "- `Documentation/zigux/phase12-release-closure-checklist.md`",
    "- `Documentation/zigux/phase12-release-coordination-matrix.md`",
    "- `Documentation/zigux/phase14-release-boundary-survey.md`",
)


def read_ledger(root: Path) -> str:
    return (root / LEDGER_PATH).read_text(encoding="utf-8")


def collect_missing_lines(root: Path) -> list[str]:
    ledger = read_ledger(root)
    return [line for line in REQUIRED_LINES if line not in ledger]


def section_order(root: Path) -> str | None:
    ledger = read_ledger(root)
    positions: list[int] = []
    for marker in ORDER_MARKERS:
        position = ledger.find(marker)
        if position == -1:
            return None
        positions.append(position)
    if positions != sorted(positions):
        return None
    return "ScopeNote->ReleasePlanningContinuation->PracticalRule"


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
- This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_ledger_release_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / LEDGER_PATH, _sample_ledger())

        if collect_missing_lines(root):
            raise AssertionError("baseline ledger continuation fixture should pass")
        if section_order(root) != "ScopeNote->ReleasePlanningContinuation->PracticalRule":
            raise AssertionError("baseline section order should pass")
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("## Release-Planning Continuation\n\n", "", 1),
        )
        missing = collect_missing_lines(root)
        if missing != ["## Release-Planning Continuation"]:
            raise AssertionError(f"unexpected missing lines for heading case: {missing}")
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "- `Documentation/zigux/phase12-release-coordination-matrix.md`\n",
                "",
                1,
            ),
        )
        missing = collect_missing_lines(root)
        expected = ["- `Documentation/zigux/phase12-release-coordination-matrix.md`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing lines for path case: {missing}")
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "- use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`\n",
                "",
                1,
            ),
        )
        missing = collect_missing_lines(root)
        expected = [
            "- use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`"
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing lines for practical-rule case: {missing}")
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("## Scope Note", "## Scope-Notes", 1),
        )
        if section_order(root) is not None:
            raise AssertionError("order check should fail when scope note heading changes")
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("- Practical rule:", "## Practical rule", 1),
        )
        if section_order(root) is not None:
            raise AssertionError("order check should fail when practical rule marker changes")
        case_count += 1

    print("LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 bootstrap ledger release-planning continuation packet."
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
        help="exercise the checker against synthetic ledger fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_lines(args.root)
    if missing:
        for line in missing:
            print(f"ERROR: missing line: {line}")
        return 1

    order = section_order(args.root)
    if order is None:
        print("ERROR: section order drifted around the ledger continuation packet")
        return 1

    print("Lane 01 bootstrap ledger release-planning check passed.")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_LINKED_PATH_COUNT={len(LINK_LINES)}")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SECTION_ORDER={order}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

LEDGER_PATH = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
SCOPE_NOTE_HEADING = "## Scope Note"
RELEASE_PLANNING_HEADING = "## Release-Planning Continuation"
PRACTICAL_RULE_MARKER = "- Practical rule:"

EXPECTED_LINES = (
    "- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.",
    "- Do not backfill later release-planning state here as synthetic commit history when the live repo already exposes the active PMO packet directly.",
    "- For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:",
    "  - `Documentation/zigux/README.md`",
    "  - `Documentation/zigux/phase12-release-sequencing.md`",
    "  - `Documentation/zigux/phase12-release-readiness-survey.md`",
    "  - `Documentation/zigux/phase12-release-closure-checklist.md`",
    "  - `Documentation/zigux/phase12-release-coordination-matrix.md`",
    "  - `Documentation/zigux/phase14-release-boundary-survey.md`",
    PRACTICAL_RULE_MARKER,
    "  - use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train",
    "  - use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`",
    "- This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs.",
)

EXPECTED_LINK_PATHS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
)


def _read_lines(root: Path) -> list[str]:
    return (root / LEDGER_PATH).read_text(encoding="utf-8").splitlines()


def _index(lines: list[str], marker: str) -> int:
    try:
        return lines.index(marker)
    except ValueError as exc:
        raise AssertionError(f"missing marker: {marker}") from exc


def extract_release_planning_packet(root: Path) -> tuple[str, ...]:
    lines = _read_lines(root)
    scope_note_index = _index(lines, SCOPE_NOTE_HEADING)
    release_planning_index = _index(lines, RELEASE_PLANNING_HEADING)
    practical_rule_index = _index(lines, PRACTICAL_RULE_MARKER)

    if not scope_note_index < release_planning_index < practical_rule_index:
        raise AssertionError(
            "unexpected section order for Scope Note, Release-Planning Continuation, and Practical rule"
        )

    packet_lines: list[str] = []
    for line in lines[release_planning_index + 1 :]:
        if not line.strip():
            continue
        packet_lines.append(line)

    return tuple(packet_lines)


def check_release_planning_packet(root: Path) -> list[str]:
    try:
        packet = extract_release_planning_packet(root)
    except AssertionError as exc:
        return [str(exc)]

    errors: list[str] = []
    if packet != EXPECTED_LINES:
        errors.append("release-planning packet mismatch")
        errors.append(f"expected:{EXPECTED_LINES!r}")
        errors.append(f"actual:{packet!r}")

    for rel_path in EXPECTED_LINK_PATHS:
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing linked path: {rel_path}")

    return errors


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


def _write_link_targets(root: Path) -> None:
    for rel_path in EXPECTED_LINK_PATHS:
        _write(root / rel_path, f"# placeholder for {rel_path}\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_release_planning_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / LEDGER_PATH, _sample_ledger())
        _write_link_targets(root)

        errors = check_release_planning_packet(root)
        if errors:
            raise AssertionError(
                f"baseline Lane 01 ledger release-planning fixture should pass: {errors}"
            )
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("## Release-Planning Continuation\n\n", "", 1),
        )
        errors = check_release_planning_packet(root)
        if errors != ["missing marker: ## Release-Planning Continuation"]:
            raise AssertionError(f"unexpected missing-heading error: {errors}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "- Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.\n",
                "",
                1,
            ),
        )
        errors = check_release_planning_packet(root)
        if not errors or errors[0] != "release-planning packet mismatch":
            raise AssertionError(f"expected missing-line mismatch, got: {errors}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace(
                "  - `Documentation/zigux/phase12-release-readiness-survey.md`\n"
                "  - `Documentation/zigux/phase12-release-closure-checklist.md`\n",
                "  - `Documentation/zigux/phase12-release-closure-checklist.md`\n"
                "  - `Documentation/zigux/phase12-release-readiness-survey.md`\n",
                1,
            ),
        )
        errors = check_release_planning_packet(root)
        if not errors or errors[0] != "release-planning packet mismatch":
            raise AssertionError(f"expected reorder mismatch, got: {errors}")
        _write(root / LEDGER_PATH, _sample_ledger())
        case_count += 1

        (root / "Documentation/zigux/phase14-release-boundary-survey.md").unlink()
        errors = check_release_planning_packet(root)
        expected = "missing linked path: Documentation/zigux/phase14-release-boundary-survey.md"
        if expected not in errors:
            raise AssertionError(f"expected missing linked-path error, got: {errors}")
        _write_link_targets(root)
        case_count += 1

        _write(
            root / LEDGER_PATH,
            _sample_ledger().replace("- Practical rule:\n", "- Practical guidance:\n", 1),
        )
        errors = check_release_planning_packet(root)
        if errors != ["missing marker: - Practical rule:"]:
            raise AssertionError(f"unexpected practical-rule error: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap-ledger release-planning packet remains aligned."
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
        help="exercise the checker against synthetic Lane 01 ledger fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_release_planning_packet(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Lane 01 bootstrap ledger release-planning check passed.")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_REQUIRED_LINE_COUNT={len(EXPECTED_LINES)}")
    print(f"LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_LINKED_PATH_COUNT={len(EXPECTED_LINK_PATHS)}")
    print(
        "LANE01_BOOTSTRAP_LEDGER_RELEASE_PLANNING_SECTION_ORDER="
        "ScopeNote->ReleasePlanningContinuation->PracticalRule"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

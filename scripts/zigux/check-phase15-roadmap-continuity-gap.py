#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
SHARED_SUMMARY_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
ROADMAP_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-roadmap-continuity-gap.md")

MISSING_ROADMAP_PATHS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
)

FREEZE_GOVERNANCE_MARKERS = (
    "`Documentation/zigux/freeze-map.md`",
    "review-process",
    "indefinite-C policy",
    "`python3 scripts/zigux/validate-phase15.py`",
)

PARITY_SCORECARD_MARKERS = (
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "indefinite-C policy",
    "`python3 scripts/zigux/validate-phase15.py`",
)

SHARED_SUMMARY_GAP_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`scripts/zigux/validate-phase15.py`",
)

REQUIRED_NOTE_MARKERS = (
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`scripts/zigux/check-phase15-roadmap-continuity-gap.py`",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def collect_failures(root: Path) -> list[str]:
    freeze_governance = _read_text(root / FREEZE_GOVERNANCE_PATH)
    parity_scorecard = _read_text(root / PARITY_SCORECARD_PATH)
    shared_summary_gap = _read_text(root / SHARED_SUMMARY_GAP_PATH)
    roadmap_gap_note = _read_text(root / ROADMAP_GAP_NOTE_PATH)

    failures: list[str] = []

    for relative_path in MISSING_ROADMAP_PATHS:
        if (root / relative_path).exists():
            failures.append(
                "roadmap-required Phase 15 path now exists and the continuity-gap note must be refreshed: "
                + relative_path
            )

    for marker in FREEZE_GOVERNANCE_MARKERS:
        if marker not in freeze_governance:
            failures.append(f"freeze-map governance marker disappeared and the continuity note needs refresh: {marker}")

    for marker in PARITY_SCORECARD_MARKERS:
        if marker not in parity_scorecard:
            failures.append(f"parity-scorecard marker disappeared and the continuity note needs refresh: {marker}")

    for marker in SHARED_SUMMARY_GAP_MARKERS:
        if marker not in shared_summary_gap:
            failures.append(f"shared-summary gap marker disappeared and the continuity note needs refresh: {marker}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in roadmap_gap_note:
            failures.append(f"roadmap continuity gap note is missing required marker: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_freeze_governance() -> str:
    return """# Phase 15 Freeze-Map Governance

`Documentation/zigux/freeze-map.md`
review-process
indefinite-C policy
`python3 scripts/zigux/validate-phase15.py`
"""


def _sample_parity_scorecard() -> str:
    return """# Phase 15 Parity Scorecard

`Documentation/zigux/freeze-map.md`
`Documentation/zigux/phase15-architecture-council-review-process.md`
indefinite-C policy
`python3 scripts/zigux/validate-phase15.py`
"""


def _sample_shared_summary_gap() -> str:
    return """# Phase 15 Shared Summary Gap

`Documentation/zigux/phase15-architecture-council-review-process.md`
`Documentation/zigux/phase15-indefinite-c-policy.md`
`scripts/zigux/validate-phase15.py`
"""


def _sample_roadmap_gap_note() -> str:
    return """# Phase 15 Roadmap Continuity Gap

`Documentation/zigux/freeze-map.md`
`Documentation/zigux/phase15-architecture-council-review-process.md`
`Documentation/zigux/phase15-indefinite-c-policy.md`
`Documentation/zigux/phase15-freeze-map-governance.md`
`Documentation/zigux/phase15-parity-scorecard.md`
`Documentation/zigux/phase15-shared-summary-gap.md`
`scripts/zigux/check-phase15-roadmap-continuity-gap.py`
"""


def _seed_layout(root: Path) -> None:
    _write(root / FREEZE_GOVERNANCE_PATH, _sample_freeze_governance())
    _write(root / PARITY_SCORECARD_PATH, _sample_parity_scorecard())
    _write(root / SHARED_SUMMARY_GAP_PATH, _sample_shared_summary_gap())
    _write(root / ROADMAP_GAP_NOTE_PATH, _sample_roadmap_gap_note())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_layout(root)
        if collect_failures(root):
            raise AssertionError("baseline missing-layout fixture should pass")

        materialized_root = root / "materialized"
        _seed_layout(materialized_root)
        _write(materialized_root / "Documentation/zigux/freeze-map.md", "freeze map\n")
        failures = collect_failures(materialized_root)
        if len(failures) != 1 or "Documentation/zigux/freeze-map.md" not in failures[0]:
            raise AssertionError(f"materialized-path failure missing expected marker: {failures}")

        note_root = root / "note"
        _seed_layout(note_root)
        _write(
            note_root / ROADMAP_GAP_NOTE_PATH,
            _sample_roadmap_gap_note().replace("`Documentation/zigux/phase15-indefinite-c-policy.md`\n", ""),
        )
        failures = collect_failures(note_root)
        if len(failures) != 1 or "`Documentation/zigux/phase15-indefinite-c-policy.md`" not in failures[0]:
            raise AssertionError(f"note-marker failure missing expected marker: {failures}")

        governance_root = root / "governance"
        _seed_layout(governance_root)
        _write(
            governance_root / FREEZE_GOVERNANCE_PATH,
            _sample_freeze_governance().replace("indefinite-C policy\n", ""),
        )
        failures = collect_failures(governance_root)
        if len(failures) != 1 or "indefinite-C policy" not in failures[0]:
            raise AssertionError(f"governance-marker failure missing expected marker: {failures}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 roadmap continuity-gap note still matches the current "
            "Phase 15 overclaim surfaces and missing roadmap-required files."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux and scripts/zigux",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic repo layouts",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_failures(args.root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 roadmap continuity gap check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

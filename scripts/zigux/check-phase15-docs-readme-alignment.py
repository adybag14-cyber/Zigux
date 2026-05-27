#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
LANE_SEQ_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")

PARKED_DOCS_REQUIRED_MARKERS = (
    "Phase 14 notes",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
)

PARKED_DOCS_FORBIDDEN_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

LANDED_DOCS_REQUIRED_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-architecture-council-packet.py`",
    "`scripts/zigux/validate-phase15.py`",
)

PARKED_HANDOFF_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet",
    "keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there, reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py`, and only treat it as routine drift-follow-through after that wording exists and starts to diverge from the directly materialized governance packet",
)

LANDED_HANDOFF_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, which now carries a dedicated Phase 15 reminder packet and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py` whenever that shared docs-root wording drifts away from the directly materialized governance packet",
    "keep the landed docs-root reminder surface `Documentation/zigux/README.md` aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of carrying docs-root Phase 15 coverage as an active shared-summary gap",
)

PARKED_SHARED_GAP_REQUIRED_MARKERS = (
    "## Current shared-summary watchpoints",
    "`Documentation/zigux/README.md`",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims",
)

LANDED_SHARED_GAP_REQUIRED_MARKERS = (
    "## Current shared-summary watchpoints",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/README.md` now keeps a dedicated Phase 15 reminder packet explicit, so reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py` whenever that shared docs-root wording drifts away from the directly materialized governance packet",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims",
)

LANE_SEQ_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _docs_state(docs_readme: str) -> str:
    return "landed" if "Phase 15 notes" in docs_readme else "parked"


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (
        DOCS_README_PATH,
        HANDOFF_NOTE_PATH,
        SHARED_GAP_NOTE_PATH,
        LANE_SEQ_NOTE_PATH,
    ):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    docs_readme = _read(root / DOCS_README_PATH)
    handoff_note = _read(root / HANDOFF_NOTE_PATH)
    shared_gap_note = _read(root / SHARED_GAP_NOTE_PATH)
    lane_seq_note = _read(root / LANE_SEQ_NOTE_PATH)

    state = _docs_state(docs_readme)

    for marker in PARKED_DOCS_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:missing:{marker}")

    if state == "parked":
        for marker in PARKED_DOCS_FORBIDDEN_MARKERS:
            if marker in docs_readme:
                failures.append(f"docs_readme:unexpected_phase15_marker:{marker}")
        handoff_markers = PARKED_HANDOFF_REQUIRED_MARKERS
        shared_gap_markers = PARKED_SHARED_GAP_REQUIRED_MARKERS
    else:
        for marker in LANDED_DOCS_REQUIRED_MARKERS:
            if marker not in docs_readme:
                failures.append(f"docs_readme:missing_landed_marker:{marker}")
        handoff_markers = LANDED_HANDOFF_REQUIRED_MARKERS
        shared_gap_markers = LANDED_SHARED_GAP_REQUIRED_MARKERS

    for marker in handoff_markers:
        if marker not in handoff_note:
            failures.append(f"handoff:missing:{marker}")

    for marker in shared_gap_markers:
        if marker not in shared_gap_note:
            failures.append(f"shared_gap:missing:{marker}")

    for marker in LANE_SEQ_REQUIRED_MARKERS:
        if marker not in lane_seq_note:
            failures.append(f"lane_seq:missing:{marker}")

    return failures


def _sample_docs_readme_parked() -> str:
    return """# Zigux Documentation

Phase 14 notes
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
"""


def _sample_docs_readme_landed() -> str:
    return """# Zigux Documentation

Phase 14 notes
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`

Phase 15 notes
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-architecture-council-packet.py`
- `scripts/zigux/validate-phase15.py`
"""


def _sample_handoff_note_parked() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet
- keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there, reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py`, and only treat it as routine drift-follow-through after that wording exists and starts to diverge from the directly materialized governance packet
"""


def _sample_handoff_note_landed() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/README.md`, which now carries a dedicated Phase 15 reminder packet and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py` whenever that shared docs-root wording drifts away from the directly materialized governance packet
- keep the landed docs-root reminder surface `Documentation/zigux/README.md` aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of carrying docs-root Phase 15 coverage as an active shared-summary gap
"""


def _sample_shared_gap_note_parked() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/README.md`

## Recovery rule

- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims
"""


def _sample_shared_gap_note_landed() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/README.md`
- `Documentation/zigux/README.md` now keeps a dedicated Phase 15 reminder packet explicit, so reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py` whenever that shared docs-root wording drifts away from the directly materialized governance packet

## Recovery rule

- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims
"""


def _sample_lane_seq_note() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
"""


def _seed_parked(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme_parked())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note_parked())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note_parked())
    _write(root / LANE_SEQ_NOTE_PATH, _sample_lane_seq_note())


def _seed_landed(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme_landed())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note_landed())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note_landed())
    _write(root / LANE_SEQ_NOTE_PATH, _sample_lane_seq_note())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_docs_readme_gap_") as tmp_dir:
        root = Path(tmp_dir)

        parked_root = root / "parked"
        _seed_parked(parked_root)
        failures = collect_failures(parked_root)
        if failures:
            raise AssertionError(f"parked fixture should pass: {failures}")
        case_count += 1

        landed_root = root / "landed"
        _seed_landed(landed_root)
        failures = collect_failures(landed_root)
        if failures:
            raise AssertionError(f"landed fixture should pass: {failures}")
        case_count += 1

        partial_landed_root = root / "partial_landed"
        _seed_landed(partial_landed_root)
        _write(
            partial_landed_root / DOCS_README_PATH,
            _sample_docs_readme_landed().replace(
                "- `Documentation/zigux/phase15-architecture-council-review-process.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(partial_landed_root)
        expected = [
            "docs_readme:missing_landed_marker:`Documentation/zigux/phase15-architecture-council-review-process.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected partial-landed failure: {failures}")
        case_count += 1

        landed_handoff_root = root / "landed_handoff_gap"
        _seed_landed(landed_handoff_root)
        _write(
            landed_handoff_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note_landed().replace(
                LANDED_HANDOFF_REQUIRED_MARKERS[0] + "\n",
                "",
                1,
            ),
        )
        failures = collect_failures(landed_handoff_root)
        expected = [f"handoff:missing:{LANDED_HANDOFF_REQUIRED_MARKERS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected landed-handoff failure: {failures}")
        case_count += 1

        parked_phase15_root = root / "parked_unexpected_phase15"
        _seed_parked(parked_phase15_root)
        _write(
            parked_phase15_root / DOCS_README_PATH,
            _sample_docs_readme_parked() + "Phase 15 notes\n",
        )
        failures = collect_failures(parked_phase15_root)
        expected = ["docs_readme:missing_landed_marker:`Documentation/zigux/freeze-map.md`"]
        if failures[0] != expected[0]:
            raise AssertionError(f"unexpected parked-phase15 failure: {failures}")
        case_count += 1

    print("PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root Phase 15 reminder state matches the current shared-summary gap posture."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 docs README alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

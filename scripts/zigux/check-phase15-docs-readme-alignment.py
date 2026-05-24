#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")

README_REQUIRED_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain reminder surfaces",
    "`Documentation/zigux/phase15-shared-summary-gap.md` before they are treated as fully aligned current-`master` evidence",
    "do not by themselves imply a freeze-map status change or Architecture Council approval",
    "`Documentation/zigux/phase15-shared-summary-gap.md` and `Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "the shared Phase 15 docs-root handoff should also keep",
    "the named reopen trigger",
    "deep-core blocker-posture change",
)

HANDOFF_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, which now keeps the landed Phase 15 docs-root reminder explicit beside `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of being treated as a still-missing follow-up",
    "keep the landed docs-root Phase 15 reminder surface `Documentation/zigux/README.md` aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet, and only widen that reminder if fresh drift or ownership changes force it",
)

HANDOFF_FORBIDDEN_MARKERS = (
    "still stops at Phase 14 on current `master`",
    "keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there",
)

SHARED_GAP_REQUIRED_MARKERS = (
    "## Current shared-summary watchpoints",
    "`Documentation/zigux/README.md`",
    "the landed `Documentation/zigux/README.md` Phase 15 reminder still needs rereads with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the rest of the directly materialized governance packet whenever that broad docs-root summary drifts",
    "do keep the landed docs-root Phase 15 reminder aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the rest of the directly materialized governance packet instead of letting that summary drift back into missing-follow-up or implied-approval wording",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (DOCS_README_PATH, HANDOFF_NOTE_PATH, SHARED_GAP_NOTE_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    docs_readme = _read(root / DOCS_README_PATH)
    handoff_note = _read(root / HANDOFF_NOTE_PATH)
    shared_gap_note = _read(root / SHARED_GAP_NOTE_PATH)

    for marker in README_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:missing:{marker}")

    for marker in HANDOFF_REQUIRED_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff:missing:{marker}")

    for marker in HANDOFF_FORBIDDEN_MARKERS:
        if marker in handoff_note:
            failures.append(f"handoff:stale:{marker}")

    for marker in SHARED_GAP_REQUIRED_MARKERS:
        if marker not in shared_gap_note:
            failures.append(f"shared_gap:missing:{marker}")

    return failures


def _sample_docs_readme() -> str:
    return """Scope
Phase 15 notes
`Documentation/zigux/phase15-readiness-gate-survey.md`
`Documentation/zigux/phase15-handoff-next-steps-survey.md`
`Documentation/zigux/phase15-governance-lane-sequencing.md`
`Documentation/zigux/phase15-study-only-anchor-accounting.md`
`Documentation/zigux/phase15-shared-summary-gap.md`
`scripts/zigux/check-phase15-docs-readme-alignment.py`
`scripts/zigux/check-phase15-scripts-readme-alignment.py`
`scripts/zigux/check-phase15-shared-summary-gap.py`
`scripts/zigux/check-phase15-review-process-handoff.py`
`scripts/zigux/validate-phase15.py`
`zigux/tests/phase15_readiness_gate_manifest.json`
`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` remain reminder surfaces
`Documentation/zigux/phase15-shared-summary-gap.md` before they are treated as fully aligned current-`master` evidence
do not by themselves imply a freeze-map status change or Architecture Council approval
`Documentation/zigux/phase15-shared-summary-gap.md` and `Documentation/zigux/phase15-handoff-next-steps-survey.md`
the shared Phase 15 docs-root handoff should also keep
the named reopen trigger
deep-core blocker-posture change
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/README.md`, which now keeps the landed Phase 15 docs-root reminder explicit beside `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of being treated as a still-missing follow-up
- keep the landed docs-root Phase 15 reminder surface `Documentation/zigux/README.md` aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet, and only widen that reminder if fresh drift or ownership changes force it
"""


def _sample_shared_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/README.md`
- the landed `Documentation/zigux/README.md` Phase 15 reminder still needs rereads with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the rest of the directly materialized governance packet whenever that broad docs-root summary drifts

## Recovery rule

- do keep the landed docs-root Phase 15 reminder aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the rest of the directly materialized governance packet instead of letting that summary drift back into missing-follow-up or implied-approval wording
"""


def _seed(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_docs_readme_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_readme_root = root / "missing_readme"
        _seed(missing_readme_root)
        _write(
            missing_readme_root / DOCS_README_PATH,
            _sample_docs_readme().replace(
                "`Documentation/zigux/phase15-study-only-anchor-accounting.md`\n", "", 1
            ),
        )
        failures = collect_failures(missing_readme_root)
        expected = ["docs_readme:missing:`Documentation/zigux/phase15-study-only-anchor-accounting.md`"]
        if failures != expected:
            raise AssertionError(f"unexpected README-marker failure: {failures}")
        case_count += 1

        missing_handoff_root = root / "missing_handoff"
        _seed(missing_handoff_root)
        _write(
            missing_handoff_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(HANDOFF_REQUIRED_MARKERS[0] + "\n", "", 1),
        )
        failures = collect_failures(missing_handoff_root)
        expected = [f"handoff:missing:{HANDOFF_REQUIRED_MARKERS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected handoff-marker failure: {failures}")
        case_count += 1

        stale_handoff_root = root / "stale_handoff"
        _seed(stale_handoff_root)
        _write(
            stale_handoff_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note() + "still stops at Phase 14 on current `master`\n",
        )
        failures = collect_failures(stale_handoff_root)
        expected = ["handoff:stale:still stops at Phase 14 on current `master`"]
        if failures != expected:
            raise AssertionError(f"unexpected stale-handoff failure: {failures}")
        case_count += 1

        missing_gap_root = root / "missing_gap"
        _seed(missing_gap_root)
        _write(
            missing_gap_root / SHARED_GAP_NOTE_PATH,
            _sample_shared_gap_note().replace(SHARED_GAP_REQUIRED_MARKERS[2] + "\n", "", 1),
        )
        failures = collect_failures(missing_gap_root)
        expected = [f"shared_gap:missing:{SHARED_GAP_REQUIRED_MARKERS[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected shared-gap marker failure: {failures}")
        case_count += 1

        missing_gap_rule_root = root / "missing_gap_rule"
        _seed(missing_gap_rule_root)
        _write(
            missing_gap_rule_root / SHARED_GAP_NOTE_PATH,
            _sample_shared_gap_note().replace(SHARED_GAP_REQUIRED_MARKERS[3] + "\n", "", 1),
        )
        failures = collect_failures(missing_gap_rule_root)
        expected = [f"shared_gap:missing:{SHARED_GAP_REQUIRED_MARKERS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected shared-gap rule failure: {failures}")
        case_count += 1

    print("PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root Phase 15 summary and its handoff notes stay aligned."
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
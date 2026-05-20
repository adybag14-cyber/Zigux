#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
LANE_SEQ_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
READINESS_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"
SHARED_GAP_REL = "Documentation/zigux/phase15-shared-summary-gap.md"
HANDOFF_REL = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
FREEZE_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"
INDEFINITE_C_POLICY_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"
PARITY_SCORECARD_SURVEY_REL = "Documentation/zigux/phase15-parity-scorecard-survey.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
DOCS_CHECKER_REL = "scripts/zigux/check-phase15-docs-readme-alignment.py"
SCRIPTS_CHECKER_REL = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
TESTS_CHECKER_REL = "scripts/zigux/check-phase15-tests-readme-alignment.py"
HANDOFF_CHECKER_REL = "scripts/zigux/check-phase15-review-process-handoff.py"
HANDOFF_NOTE_CHECKER_REL = "scripts/zigux/check-phase15-handoff-note-alignment.py"
GAP_CHECKER_REL = "scripts/zigux/check-phase15-shared-summary-gap.py"
READINESS_CHECKER_REL = "scripts/zigux/check-phase15-readiness-gate-packet.py"
READINESS_MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
REVIEW_PROCESS_MANIFEST_REL = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
REVIEW_PROCESS_TEST_REL = "zigux/tests/phase15_architecture_council_review_process.zig"
REVIEW_PROCESS_BUILD_REL = "zigux/tests/phase15_architecture_council_review_process_build.zig"
HANDOFF_MANIFEST_REL = "zigux/tests/phase15_handoff_next_steps_manifest.json"
HANDOFF_TEST_REL = "zigux/tests/phase15_handoff_next_steps.zig"
FREEZE_GOVERNANCE_TEST_REL = "zigux/tests/phase15_freeze_map_governance.zig"
PARITY_SCORECARD_TEST_REL = "zigux/tests/phase15_parity_scorecard.zig"
INDEFINITE_C_POLICY_JSON_REL = "zigux/tests/phase15_indefinite_c_policy.json"
INDEFINITE_C_POLICY_TEST_REL = "zigux/tests/phase15_indefinite_c_policy.zig"
LANE_OWNER_ALIGNMENT_REL = "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    README_REL,
    TESTS_README_REL,
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    LANE_SEQ_REL,
    READINESS_REL,
    SHARED_GAP_REL,
    HANDOFF_REL,
    FREEZE_GOVERNANCE_REL,
    INDEFINITE_C_POLICY_REL,
    PARITY_SCORECARD_SURVEY_REL,
    STUDY_ONLY_REL,
    DOCS_CHECKER_REL,
    SCRIPTS_CHECKER_REL,
    TESTS_CHECKER_REL,
    HANDOFF_CHECKER_REL,
    HANDOFF_NOTE_CHECKER_REL,
    GAP_CHECKER_REL,
    READINESS_CHECKER_REL,
    READINESS_MANIFEST_REL,
    REVIEW_PROCESS_MANIFEST_REL,
    REVIEW_PROCESS_TEST_REL,
    REVIEW_PROCESS_BUILD_REL,
    HANDOFF_MANIFEST_REL,
    HANDOFF_TEST_REL,
    FREEZE_GOVERNANCE_TEST_REL,
    PARITY_SCORECARD_TEST_REL,
    INDEFINITE_C_POLICY_JSON_REL,
    INDEFINITE_C_POLICY_TEST_REL,
    LANE_OWNER_ALIGNMENT_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
)

README_PHASE15_MARKERS = (
    "Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work",
    f"`{DOCS_CHECKER_REL}`",
    f"`{SCRIPTS_CHECKER_REL}`",
    f"`{TESTS_CHECKER_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
    f"`{READINESS_CHECKER_REL}`",
    f"`{FREEZE_GOVERNANCE_REL}`",
    f"`{INDEFINITE_C_POLICY_REL}`",
    f"`{PARITY_SCORECARD_SURVEY_REL}`",
    f"`{LANE_SEQ_REL}`",
    f"`{READINESS_REL}`",
    f"`{HANDOFF_REL}`",
    f"`{STUDY_ONLY_REL}`",
    f"`{SHARED_GAP_REL}`",
    f"`{REVIEW_CHECKLIST_REL}`",
    f"`{TESTS_README_REL}`",
    f"`{REVIEW_PROCESS_MANIFEST_REL}`",
    f"`{REVIEW_PROCESS_TEST_REL}`",
    f"`{REVIEW_PROCESS_BUILD_REL}`",
    f"`{HANDOFF_MANIFEST_REL}`",
    f"`{HANDOFF_TEST_REL}`",
    f"`{FREEZE_GOVERNANCE_TEST_REL}`",
    f"`{PARITY_SCORECARD_TEST_REL}`",
    f"`{INDEFINITE_C_POLICY_JSON_REL}`",
    f"`{INDEFINITE_C_POLICY_TEST_REL}`",
    f"`{READINESS_MANIFEST_REL}`",
    f"`{LANE_OWNER_ALIGNMENT_REL}`",
    f"`{HANDOFF_NOTE_CHECKER_REL}`",
    f"`{WORKFLOW_REL}`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`",
    "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
    "`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

LANE_SEQ_MARKERS = (
    f"`{README_REL}`",
    f"`{REVIEW_CHECKLIST_REL}`",
    f"`{READINESS_REL}`",
    f"`{HANDOFF_REL}`",
)

READINESS_MARKERS = (
    f"`{DOCS_CHECKER_REL}`",
    f"`{SCRIPTS_CHECKER_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
    f"`{MAKEFILE_REL}`",
    "blocked route vocabulary",
)

SHARED_GAP_MARKERS = (
    f"`{README_REL}`",
    f"`{DOCS_CHECKER_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
    f"`{READINESS_MANIFEST_REL}`",
    f"`{HANDOFF_MANIFEST_REL}`",
    f"`{LANE_OWNER_ALIGNMENT_REL}`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
    "parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes",
)

HANDOFF_MARKERS = (
    f"`{TESTS_README_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
)

FOCUSED_COMPANION_RELS = (
    "zigux/tests/phase15_architecture_council_review_process.zig",
    REVIEW_PROCESS_MANIFEST_REL,
    HANDOFF_MANIFEST_REL,
    HANDOFF_TEST_REL,
    HANDOFF_CHECKER_REL,
    HANDOFF_NOTE_CHECKER_REL,
    LANE_OWNER_ALIGNMENT_REL,
)

MISSING_BROADER_PATHS = (
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
)

STALE_PRESENT_ROUTE_MARKERS = (
    "directly readable replay paths",
    "shipped replay paths",
    "direct tests-root evidence",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    readme = _read(root / README_REL)
    lane_seq = _read(root / LANE_SEQ_REL)
    readiness = _read(root / READINESS_REL)
    shared_gap = _read(root / SHARED_GAP_REL)
    handoff = _read(root / HANDOFF_REL)
    makefile = _read(root / MAKEFILE_REL)

    _require_markers(readme, README_PHASE15_MARKERS, "readme_phase15", failures)
    _require_markers(lane_seq, LANE_SEQ_MARKERS, "lane_seq", failures)
    _require_markers(readiness, READINESS_MARKERS, "readiness", failures)
    _require_markers(shared_gap, SHARED_GAP_MARKERS, "shared_gap", failures)
    _require_markers(handoff, HANDOFF_MARKERS, "handoff", failures)

    for rel in FOCUSED_COMPANION_RELS:
        marker = f"`{rel}`"
        if marker not in shared_gap and rel not in (HANDOFF_TEST_REL, HANDOFF_NOTE_CHECKER_REL):
            failures.append(f"shared_gap:missing_materialized:{marker}")
        if marker not in handoff and rel in (HANDOFF_TEST_REL, HANDOFF_NOTE_CHECKER_REL):
            failures.append(f"handoff:missing_materialized:{marker}")
        if not (root / rel).exists():
            failures.append(f"missing_materialized_file:{rel}")

    for rel in MISSING_BROADER_PATHS:
        marker = f"`{rel}`"
        if marker not in readiness:
            failures.append(f"readiness:missing_gap_path:{marker}")
        if marker not in shared_gap:
            failures.append(f"shared_gap:missing_gap_path:{marker}")
        if (root / rel).exists():
            failures.append(f"missing_gap_path_returned:{rel}")

    for marker in STALE_PRESENT_ROUTE_MARKERS:
        stale_phrase = f"keep those route names as {marker}"
        if stale_phrase in readme:
            failures.append(f"readme:stale_phase15_route_claim:{stale_phrase}")

    for marker in ("phase15-validate:", "phase15-test:", "phase15:", ".PHONY: phase15"):
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    return failures


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_scripts_readme_alignment_") as tmpdir:
        root = Path(tmpdir)
        _write(root / README_REL, SAMPLE_README)
        _write(root / LANE_SEQ_REL, SAMPLE_LANE_SEQ)
        _write(root / READINESS_REL, SAMPLE_READINESS)
        _write(root / SHARED_GAP_REL, SAMPLE_SHARED_GAP)
        _write(root / HANDOFF_REL, SAMPLE_HANDOFF)
        _write(root / MAKEFILE_REL, SAMPLE_MAKEFILE)
        for rel in REQUIRED_FILES:
            if not (root / rel).exists():
                _write(root / rel, "placeholder\n")

        failures = validate(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        bad = root / "bad"
        _write(bad / README_REL, SAMPLE_README.replace(f"`{HANDOFF_NOTE_CHECKER_REL}`", "`scripts/zigux/missing.py`", 1))
        _write(bad / LANE_SEQ_REL, SAMPLE_LANE_SEQ)
        _write(bad / READINESS_REL, SAMPLE_READINESS)
        _write(bad / SHARED_GAP_REL, SAMPLE_SHARED_GAP)
        _write(bad / HANDOFF_REL, SAMPLE_HANDOFF)
        _write(bad / MAKEFILE_REL, SAMPLE_MAKEFILE)
        for rel in REQUIRED_FILES:
            if not (bad / rel).exists():
                _write(bad / rel, "placeholder\n")
        failures = validate(bad)
        expected = [f"readme_phase15:missing:`{HANDOFF_NOTE_CHECKER_REL}`"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing handoff-note checker marker: {failures}")

        stale = root / "stale"
        _write(
            stale / README_REL,
            SAMPLE_README.replace(
                "keep those route names as blocked route vocabulary rather than directly readable replay paths",
                "keep those route names as directly readable replay paths",
                1,
            ),
        )
        _write(stale / LANE_SEQ_REL, SAMPLE_LANE_SEQ)
        _write(stale / READINESS_REL, SAMPLE_READINESS)
        _write(stale / SHARED_GAP_REL, SAMPLE_SHARED_GAP)
        _write(stale / HANDOFF_REL, SAMPLE_HANDOFF)
        _write(stale / MAKEFILE_REL, SAMPLE_MAKEFILE)
        for rel in REQUIRED_FILES:
            if not (stale / rel).exists():
                _write(stale / rel, "placeholder\n")
        failures = validate(stale)
        expected = [
            "readme_phase15:missing:although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
            "readme:stale_phase15_route_claim:keep those route names as directly readable replay paths",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for stale route wording: {failures}")

        returned = root / "returned"
        _write(returned / README_REL, SAMPLE_README)
        _write(returned / LANE_SEQ_REL, SAMPLE_LANE_SEQ)
        _write(returned / READINESS_REL, SAMPLE_READINESS)
        _write(returned / SHARED_GAP_REL, SAMPLE_SHARED_GAP)
        _write(returned / HANDOFF_REL, SAMPLE_HANDOFF)
        _write(returned / MAKEFILE_REL, SAMPLE_MAKEFILE)
        for rel in REQUIRED_FILES:
            if not (returned / rel).exists():
                _write(returned / rel, "placeholder\n")
        _write(returned / "scripts/zigux/validate-phase15.py", "present\n")
        failures = validate(returned)
        expected = ["missing_gap_path_returned:scripts/zigux/validate-phase15.py"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for returned missing path: {failures}")

        handoff_gap = root / "handoff_gap"
        _write(handoff_gap / README_REL, SAMPLE_README)
        _write(handoff_gap / LANE_SEQ_REL, SAMPLE_LANE_SEQ)
        _write(handoff_gap / READINESS_REL, SAMPLE_READINESS)
        _write(handoff_gap / SHARED_GAP_REL, SAMPLE_SHARED_GAP)
        _write(handoff_gap / HANDOFF_REL, SAMPLE_HANDOFF.replace(f"`{HANDOFF_TEST_REL}`", "`zigux/tests/missing_handoff_test.zig`", 1))
        _write(handoff_gap / MAKEFILE_REL, SAMPLE_MAKEFILE)
        for rel in REQUIRED_FILES:
            if not (handoff_gap / rel).exists():
                _write(handoff_gap / rel, "placeholder\n")
        failures = validate(handoff_gap)
        expected = [f"handoff:missing_materialized:`{HANDOFF_TEST_REL}`"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing handoff materialized marker: {failures}")

    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


SAMPLE_README = """# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 15

- Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision
- `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` keep the shipped docs-root, scripts-root, tests-root, handoff, shared-summary, and readiness packet guards explicit from the scripts root
- `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `.github/workflows/zigux-bootstrap.yml` keep the current directly readable governance packet explicit from the scripts root
- repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, so keep those broader validator-first and build companions framed as repo-reality gaps instead of shipped scripts-root evidence while `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` stays part of the directly readable governance packet
- although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths
- `.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route, so keep that workflow surface framed as shared-summary gap vocabulary rather than shipped Phase 15 replay evidence
- no Architecture Council approval is currently recorded for a freeze-map status change, and any future follow-through should tighten the smallest truthful reminder surface first instead of widening into a status-change claim
"""

SAMPLE_LANE_SEQ = """# Phase 15 Governance Lane Sequencing

- `scripts/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
"""

SAMPLE_READINESS = """# Phase 15 Readiness Gate Survey

- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `zigux/Makefile`
- broader replay remains blocked route vocabulary
"""

SAMPLE_SHARED_GAP = """# Phase 15 Shared Summary Gap

- `scripts/zigux/README.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `zigux/tests/phase15_readiness_gate_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes
"""

SAMPLE_HANDOFF = """# Phase 15 Handoff Next Steps Survey

- `zigux/tests/README.md`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
"""

SAMPLE_MAKEFILE = """PYTHON ?= python3
.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3 phase4 phase6 phase8 phase10 phase12 phase14-validate
phase2-toolchain:
	@true
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 scripts-root reminder stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

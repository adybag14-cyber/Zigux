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
DECISION_INDEX_REL = "Documentation/zigux/phase15-architecture-council-decision-index.md"
INDEFINITE_C_POLICY_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"
PARITY_SCORECARD_REL = "Documentation/zigux/phase15-parity-scorecard.md"
PARITY_SCORECARD_SURVEY_REL = "Documentation/zigux/phase15-parity-scorecard-survey.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
DOCS_CHECKER_REL = "scripts/zigux/check-phase15-docs-readme-alignment.py"
SCRIPTS_CHECKER_REL = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
TESTS_CHECKER_REL = "scripts/zigux/check-phase15-tests-readme-alignment.py"
ARCH_COUNCIL_PACKET_CHECKER_REL = "scripts/zigux/check-phase15-architecture-council-packet.py"
DECISION_INDEX_CHECKER_REL = "scripts/zigux/check-phase15-architecture-council-decision-index.py"
HANDOFF_CHECKER_REL = "scripts/zigux/check-phase15-review-process-handoff.py"
HANDOFF_NOTE_CHECKER_REL = "scripts/zigux/check-phase15-handoff-note-alignment.py"
STUDY_ONLY_CHECKER_REL = "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py"
GAP_CHECKER_REL = "scripts/zigux/check-phase15-shared-summary-gap.py"
READINESS_CHECKER_REL = "scripts/zigux/check-phase15-readiness-gate-packet.py"
VALIDATOR_REL = "scripts/zigux/validate-phase15.py"
READINESS_MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
REVIEW_PROCESS_TEST_REL = "zigux/tests/phase15_architecture_council_review_process.zig"
REVIEW_PROCESS_MANIFEST_REL = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
REVIEW_PROCESS_BUILD_REL = "zigux/tests/phase15_architecture_council_review_process_build.zig"
DECISION_INDEX_MANIFEST_REL = "zigux/tests/phase15_architecture_council_decision_index_manifest.json"
DECISION_INDEX_TEST_REL = "zigux/tests/phase15_architecture_council_decision_index.zig"
LANE_SEQ_MANIFEST_REL = "zigux/tests/phase15_governance_lane_sequencing_manifest.json"
LANE_SEQ_TEST_REL = "zigux/tests/phase15_governance_lane_sequencing.zig"
HANDOFF_MANIFEST_REL = "zigux/tests/phase15_handoff_next_steps_manifest.json"
HANDOFF_TEST_REL = "zigux/tests/phase15_handoff_next_steps.zig"
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
FREEZE_GOVERNANCE_TEST_REL = "zigux/tests/phase15_freeze_map_governance.zig"
PARITY_SCORECARD_TEST_REL = "zigux/tests/phase15_parity_scorecard.zig"
INDEFINITE_C_POLICY_JSON_REL = "zigux/tests/phase15_indefinite_c_policy.json"
INDEFINITE_C_POLICY_TEST_REL = "zigux/tests/phase15_indefinite_c_policy.zig"
LANE_OWNER_ALIGNMENT_REL = "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
BUILD_REL = "zigux/tests/phase15_build.zig"

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
    DECISION_INDEX_REL,
    INDEFINITE_C_POLICY_REL,
    PARITY_SCORECARD_REL,
    PARITY_SCORECARD_SURVEY_REL,
    STUDY_ONLY_REL,
    DOCS_CHECKER_REL,
    SCRIPTS_CHECKER_REL,
    TESTS_CHECKER_REL,
    ARCH_COUNCIL_PACKET_CHECKER_REL,
    DECISION_INDEX_CHECKER_REL,
    HANDOFF_CHECKER_REL,
    HANDOFF_NOTE_CHECKER_REL,
    STUDY_ONLY_CHECKER_REL,
    GAP_CHECKER_REL,
    READINESS_CHECKER_REL,
    VALIDATOR_REL,
    READINESS_MANIFEST_REL,
    REVIEW_PROCESS_TEST_REL,
    REVIEW_PROCESS_MANIFEST_REL,
    REVIEW_PROCESS_BUILD_REL,
    DECISION_INDEX_MANIFEST_REL,
    DECISION_INDEX_TEST_REL,
    LANE_SEQ_MANIFEST_REL,
    LANE_SEQ_TEST_REL,
    HANDOFF_MANIFEST_REL,
    HANDOFF_TEST_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
    FREEZE_GOVERNANCE_TEST_REL,
    PARITY_SCORECARD_TEST_REL,
    INDEFINITE_C_POLICY_JSON_REL,
    INDEFINITE_C_POLICY_TEST_REL,
    LANE_OWNER_ALIGNMENT_REL,
    BUILD_REL,
)

README_PHASE15_MARKERS = (
    "## Phase 15",
    "Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision",
    f"`{DOCS_CHECKER_REL}`",
    f"`{SCRIPTS_CHECKER_REL}`",
    f"`{TESTS_CHECKER_REL}`",
    f"`{ARCH_COUNCIL_PACKET_CHECKER_REL}`",
    f"`{DECISION_INDEX_CHECKER_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{HANDOFF_NOTE_CHECKER_REL}`",
    f"`{STUDY_ONLY_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
    f"`{READINESS_CHECKER_REL}`",
    f"`{VALIDATOR_REL}`",
    f"`{FREEZE_GOVERNANCE_REL}`",
    f"`{DECISION_INDEX_REL}`",
    f"`{INDEFINITE_C_POLICY_REL}`",
    f"`{PARITY_SCORECARD_REL}`",
    f"`{PARITY_SCORECARD_SURVEY_REL}`",
    f"`{LANE_SEQ_REL}`",
    f"`{READINESS_REL}`",
    f"`{HANDOFF_REL}`",
    f"`{STUDY_ONLY_REL}`",
    f"`{SHARED_GAP_REL}`",
    f"`{TESTS_README_REL}`",
    f"`{REVIEW_CHECKLIST_REL}`",
    f"`{REVIEW_PROCESS_MANIFEST_REL}`",
    f"`{REVIEW_PROCESS_BUILD_REL}`",
    f"`{DECISION_INDEX_MANIFEST_REL}`",
    f"`{DECISION_INDEX_TEST_REL}`",
    f"`{HANDOFF_MANIFEST_REL}`",
    f"`{HANDOFF_TEST_REL}`",
    f"`{FREEZE_GOVERNANCE_TEST_REL}`",
    f"`{PARITY_SCORECARD_TEST_REL}`",
    f"`{INDEFINITE_C_POLICY_JSON_REL}`",
    f"`{INDEFINITE_C_POLICY_TEST_REL}`",
    f"`{READINESS_MANIFEST_REL}`",
    f"`{LANE_OWNER_ALIGNMENT_REL}`",
    f"`{WORKFLOW_REL}`",
    f"`{BUILD_REL}`",
    "the directly readable `Documentation/zigux/phase15-architecture-council-decision-index.md` owner note, `scripts/zigux/check-phase15-architecture-council-decision-index.py` checker, `zigux/tests/phase15_architecture_council_decision_index_manifest.json` manifest, and `zigux/tests/phase15_architecture_council_decision_index.zig` focused replay now remain explicit beside the wider validator-first reminder family",
    "the directly readable `scripts/zigux/validate-phase15.py` maintenance gate and the directly readable `zigux/tests/phase15_build.zig` shared build companion both remain part of the wider validator-first reminder family",
    "repeated authenticated reads on current `master` do materialize `zigux/tests/phase15_build.zig`, so keep that shared build companion framed as directly readable governance evidence while the broader dedicated `phase15*` wrapper and shared-CI route names stay repo-reality gaps rather than shipped replay paths",
    "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths",
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
    f"`{TESTS_CHECKER_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
    f"`{READINESS_MANIFEST_REL}`",
    f"`{VALIDATOR_REL}`",
    f"`{BUILD_REL}`",
    "blocked route vocabulary",
)

SHARED_GAP_MARKERS = (
    f"`{README_REL}`",
    f"`{DOCS_CHECKER_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{HANDOFF_NOTE_CHECKER_REL}`",
    f"`{STUDY_ONLY_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
    f"`{READINESS_MANIFEST_REL}`",
    f"`{REVIEW_PROCESS_TEST_REL}`",
    f"`{REVIEW_PROCESS_MANIFEST_REL}`",
    f"`{REVIEW_PROCESS_BUILD_REL}`",
    f"`{LANE_SEQ_MANIFEST_REL}`",
    f"`{LANE_SEQ_TEST_REL}`",
    f"`{HANDOFF_MANIFEST_REL}`",
    f"`{HANDOFF_TEST_REL}`",
    f"`{LANE_OWNER_ALIGNMENT_REL}`",
    f"`{VALIDATOR_REL}`",
    f"`{BUILD_REL}`",
    "parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes",
)

HANDOFF_MARKERS = (
    f"`{README_REL}`",
    f"`{TESTS_README_REL}`",
    f"`{HANDOFF_CHECKER_REL}`",
    f"`{HANDOFF_NOTE_CHECKER_REL}`",
    f"`{GAP_CHECKER_REL}`",
)

FOCUSED_COMPANION_RELS = (
    REVIEW_PROCESS_TEST_REL,
    REVIEW_PROCESS_MANIFEST_REL,
    REVIEW_PROCESS_BUILD_REL,
    LANE_SEQ_MANIFEST_REL,
    LANE_SEQ_TEST_REL,
    HANDOFF_MANIFEST_REL,
    HANDOFF_TEST_REL,
    HANDOFF_CHECKER_REL,
    HANDOFF_NOTE_CHECKER_REL,
    STUDY_ONLY_CHECKER_REL,
    LANE_OWNER_ALIGNMENT_REL,
    BUILD_REL,
)

STALE_PRESENT_ROUTE_MARKERS = (
    "keep those route names as directly readable replay paths",
    "keep that workflow surface framed as shipped Phase 15 replay evidence",
)

WORKFLOW_STALE_MARKERS = (
    "Phase 15 validate",
    "Phase 15 test",
    "Run current Phase 15",
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
    if "## Phase 15" not in readme:
        return ["readme_phase15:missing_section:## Phase 15"]

    lane_seq = _read(root / LANE_SEQ_REL)
    readiness = _read(root / READINESS_REL)
    shared_gap = _read(root / SHARED_GAP_REL)
    handoff = _read(root / HANDOFF_REL)
    makefile = _read(root / MAKEFILE_REL)
    workflow = _read(root / WORKFLOW_REL)

    _require_markers(readme, README_PHASE15_MARKERS, "readme_phase15", failures)
    _require_markers(lane_seq, LANE_SEQ_MARKERS, "lane_seq", failures)
    _require_markers(readiness, READINESS_MARKERS, "readiness", failures)
    _require_markers(shared_gap, SHARED_GAP_MARKERS, "shared_gap", failures)
    _require_markers(handoff, HANDOFF_MARKERS, "handoff", failures)

    for rel in FOCUSED_COMPANION_RELS:
        marker = f"`{rel}`"
        if marker not in shared_gap:
            failures.append(f"shared_gap:missing_materialized:{marker}")
        if not (root / rel).exists():
            failures.append(f"missing_materialized_file:{rel}")

    for marker in STALE_PRESENT_ROUTE_MARKERS:
        if marker in readme:
            failures.append(f"readme:stale_phase15_route_claim:{marker}")

    for marker in ("phase15-validate:", "phase15-test:", "phase15:", ".PHONY: phase15"):
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    for marker in WORKFLOW_STALE_MARKERS:
        if marker in workflow:
            failures.append(f"workflow:unexpected_phase15_route:{marker}")

    return failures


def _sample_readme() -> str:
    return f"""# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 13

- keep the shipped Phase 13 helper packet explicit.

## Phase 15

- Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision
- `{DOCS_CHECKER_REL}`, `{SCRIPTS_CHECKER_REL}`, `{TESTS_CHECKER_REL}`, `{ARCH_COUNCIL_PACKET_CHECKER_REL}`, `{DECISION_INDEX_CHECKER_REL}`, `{HANDOFF_CHECKER_REL}`, `{HANDOFF_NOTE_CHECKER_REL}`, `{STUDY_ONLY_CHECKER_REL}`, `{GAP_CHECKER_REL}`, `{READINESS_CHECKER_REL}`, and `{VALIDATOR_REL}` keep the current scripts-root governance packet explicit from the scripts root while the broader dedicated `phase15*` wrapper and shared-CI companions still stay blocked
- `{FREEZE_GOVERNANCE_REL}`, `{DECISION_INDEX_REL}`, `{INDEFINITE_C_POLICY_REL}`, `{PARITY_SCORECARD_REL}`, `{PARITY_SCORECARD_SURVEY_REL}`, `{LANE_SEQ_REL}`, `{READINESS_REL}`, `{HANDOFF_REL}`, `{STUDY_ONLY_REL}`, `{SHARED_GAP_REL}`, `{TESTS_README_REL}`, `{REVIEW_CHECKLIST_REL}`, `{REVIEW_PROCESS_MANIFEST_REL}`, `{REVIEW_PROCESS_BUILD_REL}`, `{DECISION_INDEX_MANIFEST_REL}`, `{DECISION_INDEX_TEST_REL}`, `{HANDOFF_MANIFEST_REL}`, `{HANDOFF_TEST_REL}`, `{FREEZE_GOVERNANCE_TEST_REL}`, `{PARITY_SCORECARD_TEST_REL}`, `{INDEFINITE_C_POLICY_JSON_REL}`, `{INDEFINITE_C_POLICY_TEST_REL}`, `{READINESS_MANIFEST_REL}`, `{LANE_OWNER_ALIGNMENT_REL}`, and `{WORKFLOW_REL}` remain the current reminder-surface companions for that packet
- `{VALIDATOR_REL}`, `{REVIEW_PROCESS_TEST_REL}`, `{REVIEW_PROCESS_MANIFEST_REL}`, `{REVIEW_PROCESS_BUILD_REL}`, `{DECISION_INDEX_MANIFEST_REL}`, `{DECISION_INDEX_TEST_REL}`, `{LANE_SEQ_MANIFEST_REL}`, `{LANE_SEQ_TEST_REL}`, `{HANDOFF_MANIFEST_REL}`, `{HANDOFF_TEST_REL}`, `{FREEZE_GOVERNANCE_TEST_REL}`, `{PARITY_SCORECARD_TEST_REL}`, `{INDEFINITE_C_POLICY_JSON_REL}`, `{INDEFINITE_C_POLICY_TEST_REL}`, `{READINESS_MANIFEST_REL}`, `{LANE_OWNER_ALIGNMENT_REL}`, `{BUILD_REL}`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the directly materialized focused companions, manifests, replays, shared build companion, workflow surface, and returned shared governance references explicit without widening into approval or deep-core delivery claims
- the directly readable `Documentation/zigux/phase15-architecture-council-decision-index.md` owner note, `scripts/zigux/check-phase15-architecture-council-decision-index.py` checker, `zigux/tests/phase15_architecture_council_decision_index_manifest.json` manifest, and `zigux/tests/phase15_architecture_council_decision_index.zig` focused replay now remain explicit beside the wider validator-first reminder family
- the directly readable `scripts/zigux/validate-phase15.py` maintenance gate and the directly readable `zigux/tests/phase15_build.zig` shared build companion both remain part of the wider validator-first reminder family, and repeated authenticated reads on current `master` do materialize `zigux/tests/phase15_build.zig`, so keep that shared build companion framed as directly readable governance evidence while the broader dedicated `phase15*` wrapper and shared-CI route names stay repo-reality gaps rather than shipped replay paths
- although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths
- `.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route, so keep that workflow surface framed as shared-summary gap vocabulary rather than shipped Phase 15 replay evidence
- no Architecture Council approval is currently recorded for a freeze-map status change
"""


def _seed(root: Path) -> None:
    _write(root / README_REL, _sample_readme())
    _write(
        root / LANE_SEQ_REL,
        "# Phase 15 Governance Lane Sequencing\n\n"
        "- `scripts/zigux/README.md`\n"
        "- `Documentation/zigux/review-checklist.md`\n"
        "- `Documentation/zigux/phase15-readiness-gate-survey.md`\n"
        "- `Documentation/zigux/phase15-handoff-next-steps-survey.md`\n",
    )
    _write(
        root / READINESS_REL,
        "# Phase 15 Readiness Gate Survey\n\n"
        "- `scripts/zigux/check-phase15-docs-readme-alignment.py`\n"
        "- `scripts/zigux/check-phase15-scripts-readme-alignment.py`\n"
        "- `scripts/zigux/check-phase15-tests-readme-alignment.py`\n"
        "- `scripts/zigux/check-phase15-review-process-handoff.py`\n"
        "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n"
        "- `scripts/zigux/check-phase15-readiness-gate-packet.py`\n"
        "- `scripts/zigux/validate-phase15.py`\n"
        "- `zigux/tests/phase15_build.zig`\n"
        "- `zigux/tests/phase15_readiness_gate_manifest.json`\n"
        "- broader replay remains blocked route vocabulary\n",
    )
    _write(
        root / SHARED_GAP_REL,
        "# Phase 15 Shared Summary Gap\n\n"
        "- `scripts/zigux/README.md`\n"
        "- `scripts/zigux/check-phase15-docs-readme-alignment.py`\n"
        "- `scripts/zigux/check-phase15-review-process-handoff.py`\n"
        "- `scripts/zigux/check-phase15-handoff-note-alignment.py`\n"
        "- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`\n"
        "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n"
        "- `zigux/tests/phase15_readiness_gate_manifest.json`\n"
        "- `zigux/tests/phase15_architecture_council_review_process.zig`\n"
        "- `zigux/tests/phase15_architecture_council_review_process_manifest.json`\n"
        "- `zigux/tests/phase15_architecture_council_review_process_build.zig`\n"
        "- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`\n"
        "- `zigux/tests/phase15_governance_lane_sequencing.zig`\n"
        "- `zigux/tests/phase15_handoff_next_steps_manifest.json`\n"
        "- `zigux/tests/phase15_handoff_next_steps.zig`\n"
        "- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`\n"
        "- `scripts/zigux/validate-phase15.py`\n"
        "- `zigux/tests/phase15_build.zig`\n"
        "- parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes\n",
    )
    _write(
        root / HANDOFF_REL,
        "# Phase 15 Handoff Next Steps Survey\n\n"
        "- `scripts/zigux/README.md`\n"
        "- `zigux/tests/README.md`\n"
        "- `scripts/zigux/check-phase15-review-process-handoff.py`\n"
        "- `scripts/zigux/check-phase15-handoff-note-alignment.py`\n"
        "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n",
    )
    _write(
        root / MAKEFILE_REL,
        "PYTHON ?= python3\n"
        ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2\n"
        "phase2-toolchain:\n"
        "\t@true\n",
    )
    _write(
        root / WORKFLOW_REL,
        "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-scripts-readme-alignment.py\n",
    )
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            _write(root / rel, "placeholder\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_scripts_readme_alignment_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = validate(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_section = root / "missing_section"
        _seed(missing_section)
        _write(missing_section / README_REL, "# scripts/zigux\n")
        failures = validate(missing_section)
        expected = ["readme_phase15:missing_section:## Phase 15"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-section failure: {failures}")

        missing_marker = root / "missing_marker"
        _seed(missing_marker)
        _write(
            missing_marker / README_REL,
            _sample_readme().replace(
                f"`{DECISION_INDEX_CHECKER_REL}`",
                "`scripts/zigux/check-phase15-architecture-council-decision-index.py.missing`",
            ),
        )
        failures = validate(missing_marker)
        expected = [
            f"readme_phase15:missing:`{DECISION_INDEX_CHECKER_REL}`",
            "readme_phase15:missing:the directly readable `Documentation/zigux/phase15-architecture-council-decision-index.md` owner note, `scripts/zigux/check-phase15-architecture-council-decision-index.py` checker, `zigux/tests/phase15_architecture_council_decision_index_manifest.json` manifest, and `zigux/tests/phase15_architecture_council_decision_index.zig` focused replay now remain explicit beside the wider validator-first reminder family",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-marker failure: {failures}")

        stale_claim = root / "stale_claim"
        _seed(stale_claim)
        _write(
            stale_claim / README_REL,
            _read(stale_claim / README_REL).replace(
                "keep those route names as blocked route vocabulary rather than directly readable replay paths",
                "keep those route names as directly readable replay paths",
                1,
            ),
        )
        failures = validate(stale_claim)
        expected = [
            "readme_phase15:missing:although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths",
            "readme:stale_phase15_route_claim:keep those route names as directly readable replay paths",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-claim failure: {failures}")

        missing_build_marker = root / "missing_build_marker"
        _seed(missing_build_marker)
        _write(
            missing_build_marker / README_REL,
            _sample_readme().replace(
                "the directly readable `scripts/zigux/validate-phase15.py` maintenance gate and the directly readable `zigux/tests/phase15_build.zig` shared build companion both remain part of the wider validator-first reminder family, and repeated authenticated reads on current `master` do materialize `zigux/tests/phase15_build.zig`, so keep that shared build companion framed as directly readable governance evidence while the broader dedicated `phase15*` wrapper and shared-CI route names stay repo-reality gaps rather than shipped replay paths\n",
                "",
                1,
            ),
        )
        failures = validate(missing_build_marker)
        expected = [
            "readme_phase15:missing:the directly readable `scripts/zigux/validate-phase15.py` maintenance gate and the directly readable `zigux/tests/phase15_build.zig` shared build companion both remain part of the wider validator-first reminder family",
            "readme_phase15:missing:repeated authenticated reads on current `master` do materialize `zigux/tests/phase15_build.zig`, so keep that shared build companion framed as directly readable governance evidence while the broader dedicated `phase15*` wrapper and shared-CI route names stay repo-reality gaps rather than shipped replay paths",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-build-marker failure: {failures}")

        missing_direct_build = root / "missing_direct_build"
        _seed(missing_direct_build)
        (missing_direct_build / BUILD_REL).unlink()
        failures = validate(missing_direct_build)
        expected = ["missing_file:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct-build failure: {failures}")

        workflow_route = root / "workflow_route"
        _seed(workflow_route)
        _write(
            workflow_route / WORKFLOW_REL,
            _read(workflow_route / WORKFLOW_REL) + "      - name: Run current Phase 15 validate route\n",
        )
        failures = validate(workflow_route)
        expected = [
            "workflow:unexpected_phase15_route:Phase 15 validate",
            "workflow:unexpected_phase15_route:Run current Phase 15",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected workflow-route failure: {failures}")

    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


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
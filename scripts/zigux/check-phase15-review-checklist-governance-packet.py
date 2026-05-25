#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_RECORD_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
PARITY_SCORECARD_SURVEY_PATH = Path("Documentation/zigux/phase15-parity-scorecard-survey.md")
READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
LANE_SEQ_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
STUDY_ONLY_CHECKER_PATH = Path(
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py"
)
TESTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-tests-readme-alignment.py")
REVIEW_PROCESS_CHECKER_PATH = Path("scripts/zigux/check-phase15-review-process-handoff.py")
HANDOFF_CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-note-alignment.py")
SHARED_GAP_CHECKER_PATH = Path("scripts/zigux/check-phase15-shared-summary-gap.py")
READINESS_CHECKER_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
REVIEW_PROCESS_MANIFEST_PATH = Path(
    "zigux/tests/phase15_architecture_council_review_process_manifest.json"
)
REVIEW_PROCESS_BUILD_PATH = Path(
    "zigux/tests/phase15_architecture_council_review_process_build.zig"
)
LANE_SEQ_MANIFEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
LANE_SEQ_TEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing.zig")
HANDOFF_MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
HANDOFF_TEST_PATH = Path("zigux/tests/phase15_handoff_next_steps.zig")
PARITY_SCORECARD_JSON_PATH = Path("zigux/tests/phase15_parity_scorecard.json")
PARITY_SCORECARD_TEST_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
INDEFINITE_C_POLICY_JSON_PATH = Path("zigux/tests/phase15_indefinite_c_policy.json")
INDEFINITE_C_POLICY_TEST_PATH = Path("zigux/tests/phase15_indefinite_c_policy.zig")
LANE_OWNER_ALIGNMENT_PATH = Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
PHASE15_BUILD_PATH = Path("zigux/tests/phase15_build.zig")

REQUIRED_PRESENT_PATHS = (
    REVIEW_CHECKLIST_PATH,
    FREEZE_MAP_PATH,
    FREEZE_GOVERNANCE_PATH,
    REVIEW_PROCESS_PATH,
    DECISION_RECORD_TEMPLATE_PATH,
    INDEFINITE_C_POLICY_PATH,
    PARITY_SCORECARD_PATH,
    PARITY_SCORECARD_SURVEY_PATH,
    READINESS_NOTE_PATH,
    LANE_SEQ_PATH,
    STUDY_ONLY_PATH,
    SHARED_GAP_PATH,
    HANDOFF_NOTE_PATH,
    DOCS_README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    VALIDATOR_PATH,
    STUDY_ONLY_CHECKER_PATH,
    TESTS_CHECKER_PATH,
    REVIEW_PROCESS_CHECKER_PATH,
    HANDOFF_CHECKER_PATH,
    SHARED_GAP_CHECKER_PATH,
    READINESS_CHECKER_PATH,
    REVIEW_PROCESS_MANIFEST_PATH,
    REVIEW_PROCESS_BUILD_PATH,
    LANE_SEQ_MANIFEST_PATH,
    LANE_SEQ_TEST_PATH,
    HANDOFF_MANIFEST_PATH,
    HANDOFF_TEST_PATH,
    PARITY_SCORECARD_JSON_PATH,
    PARITY_SCORECARD_TEST_PATH,
    INDEFINITE_C_POLICY_JSON_PATH,
    INDEFINITE_C_POLICY_TEST_PATH,
    LANE_OWNER_ALIGNMENT_PATH,
    MAKEFILE_PATH,
)

REVIEW_CHECKLIST_REQUIRED_MARKERS = (
    "if the change touches the shared Phase 15 governance packet",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "keep `zigux/tests/phase15_build.zig` framed as a repo-reality gap",
    "keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still carries no `phase15-validate`, `phase15-test`, or `phase15` routes",
    "avoid implying any Architecture Council approval or freeze-map status change",
)

FREEZE_MAP_REQUIRED_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

LANE_SEQ_REQUIRED_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces",
    "`scripts/zigux/validate-phase15.py` is the current directly readable validator-first maintenance gate",
)

SHARED_GAP_REQUIRED_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    "`scripts/zigux/README.md` now keeps the directly materialized `scripts/zigux/validate-phase15.py` maintenance gate explicit while `zigux/tests/phase15_build.zig` remains the only broader dedicated-build companion still absent on current `master`",
)

HANDOFF_REQUIRED_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/validate-phase15.py`",
)

MAKEFILE_FORBIDDEN_MARKERS = (
    "phase15-validate:",
    "phase15-test:",
    ".PHONY: phase15",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_PRESENT_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    if (root / PHASE15_BUILD_PATH).exists():
        failures.append(f"repo:phase15_build_returned:{PHASE15_BUILD_PATH}")

    review_checklist = _read(root / REVIEW_CHECKLIST_PATH)
    freeze_map = _read(root / FREEZE_MAP_PATH)
    lane_seq = _read(root / LANE_SEQ_PATH)
    shared_gap = _read(root / SHARED_GAP_PATH)
    handoff = _read(root / HANDOFF_NOTE_PATH)
    makefile = _read(root / MAKEFILE_PATH)

    _require_markers(
        review_checklist,
        REVIEW_CHECKLIST_REQUIRED_MARKERS,
        "review_checklist",
        failures,
    )
    _require_markers(freeze_map, FREEZE_MAP_REQUIRED_MARKERS, "freeze_map", failures)
    _require_markers(lane_seq, LANE_SEQ_REQUIRED_MARKERS, "lane_seq", failures)
    _require_markers(shared_gap, SHARED_GAP_REQUIRED_MARKERS, "shared_gap", failures)
    _require_markers(handoff, HANDOFF_REQUIRED_MARKERS, "handoff", failures)

    for marker in MAKEFILE_FORBIDDEN_MARKERS:
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    return failures


def _sample_review_checklist() -> str:
    paths = "\n".join(f"- `{path.as_posix()}`" for path in REQUIRED_PRESENT_PATHS[:-1])
    return f"""# Zigux Review Checklist

- if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` still agree on the current maintenance-mode governance packet, keep `zigux/tests/phase15_build.zig` framed as a repo-reality gap, keep `zigux/Makefile` explicit only as a readable non-owner surface whose live body still carries no `phase15-validate`, `phase15-test`, or `phase15` routes, and avoid implying any Architecture Council approval or freeze-map status change that the current packet does not record?

## Fixture Paths

{paths}
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set
"""


def _sample_lane_seq() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
- `scripts/zigux/validate-phase15.py` is the current directly readable validator-first maintenance gate for the bounded governance packet without widening the lane into a dedicated-build or shared-route claim
"""


def _sample_shared_gap() -> str:
    return """# Phase 15 Shared Summary Gap

- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/README.md` now keeps the directly materialized `scripts/zigux/validate-phase15.py` maintenance gate explicit while `zigux/tests/phase15_build.zig` remains the only broader dedicated-build companion still absent on current `master`
"""


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/validate-phase15.py`
"""


def _sample_makefile() -> str:
    return """PYTHON ?= python3
.PHONY: phase2 phase14-validate
phase2:
\t@true
"""


def _seed(root: Path) -> None:
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / LANE_SEQ_PATH, _sample_lane_seq())
    _write(root / SHARED_GAP_PATH, _sample_shared_gap())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff())
    _write(root / MAKEFILE_PATH, _sample_makefile())
    for rel in REQUIRED_PRESENT_PATHS:
        if (root / rel).exists():
            continue
        if rel == REVIEW_CHECKLIST_PATH or rel == FREEZE_MAP_PATH or rel == LANE_SEQ_PATH or rel == SHARED_GAP_PATH or rel == HANDOFF_NOTE_PATH or rel == MAKEFILE_PATH:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_review_checklist_governance_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_prompt_root = root / "missing_prompt"
        _seed(missing_prompt_root)
        _write(
            missing_prompt_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "if the change touches the shared Phase 15 governance packet",
                "if the change touches another packet",
                1,
            ),
        )
        failures = collect_failures(missing_prompt_root)
        expected = [
            "review_checklist:missing:if the change touches the shared Phase 15 governance packet"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-prompt failure: {failures}")
        case_count += 1

        missing_gap_marker_root = root / "missing_gap_marker"
        _seed(missing_gap_marker_root)
        _write(
            missing_gap_marker_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "keep `zigux/tests/phase15_build.zig` framed as a repo-reality gap",
                "keep the broader dedicated-build companion explicit",
                1,
            ),
        )
        failures = collect_failures(missing_gap_marker_root)
        expected = [
            "review_checklist:missing:keep `zigux/tests/phase15_build.zig` framed as a repo-reality gap"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-gap-marker failure: {failures}")
        case_count += 1

        returned_build_root = root / "returned_build"
        _seed(returned_build_root)
        _write(returned_build_root / PHASE15_BUILD_PATH, "present\n")
        failures = collect_failures(returned_build_root)
        expected = [f"repo:phase15_build_returned:{PHASE15_BUILD_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-build failure: {failures}")
        case_count += 1

        returned_route_root = root / "returned_route"
        _seed(returned_route_root)
        _write(
            returned_route_root / MAKEFILE_PATH,
            _sample_makefile() + "phase15-validate:\n\t@true\n",
        )
        failures = collect_failures(returned_route_root)
        expected = ["makefile:unexpected_phase15_route:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected returned-route failure: {failures}")
        case_count += 1

        missing_approval_boundary_root = root / "missing_approval_boundary"
        _seed(missing_approval_boundary_root)
        _write(
            missing_approval_boundary_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "avoid implying any Architecture Council approval or freeze-map status change",
                "keep the packet narrow",
                1,
            ),
        )
        failures = collect_failures(missing_approval_boundary_root)
        expected = [
            "review_checklist:missing:avoid implying any Architecture Council approval or freeze-map status change"
        ]
        if failures != expected:
            raise AssertionError(
                f"unexpected missing-approval-boundary failure: {failures}"
            )
        case_count += 1

    print("PHASE15_REVIEW_CHECKLIST_GOVERNANCE_PACKET_SELF_TEST=pass")
    print(
        f"PHASE15_REVIEW_CHECKLIST_GOVERNANCE_PACKET_SELF_TEST_CASES={case_count}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the broad Phase 15 review-checklist governance packet stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE15_REVIEW_CHECKLIST_GOVERNANCE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

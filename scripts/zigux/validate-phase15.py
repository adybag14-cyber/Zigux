#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
]

MAKE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/validate-phase15.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 15 governance packet",
    "make -C zigux phase15-validate",
    "Run Phase 15 governance tests",
    "make -C zigux phase15-test",
]

DOCS_README_MARKERS = [
    "Phase 15 notes",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
    "no Architecture Council approval is recorded yet",
    "named reopen trigger",
    "deep-core blocker-posture change",
]

SCRIPTS_README_MARKERS = [
    "Phase 15 flow",
    "validate-phase15.py",
    "check-phase15-review-process-handoff.py",
    "check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 15 governance packet",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no-approval-yet posture",
]

READINESS_SURVEY_MARKERS = [
    "PHASE15_LANE_KEY=P15-L01",
    "The packet remains parked.",
    "no Architecture Council approval is currently recorded",
    "validator-first route stays explicit through `python3 scripts/zigux/validate-phase15.py` and `make -C zigux phase15-validate`",
    "shared replay route stays explicit through `zigux/tests/phase15_build.zig`",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15-test",
    "the remaining blocker is still `phase15-deep-core-status-change-blocker`",
    "Later repo movement still requires a fresh bounded provenance refresh",
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


missing: list[str] = []


def require_markers(name: str, source: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE15_VALIDATION=fail")
    print("MISSING_PHASE15_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE15_FILES_END")
    sys.exit(1)

require_markers("make", text("zigux/Makefile"), MAKE_MARKERS)
require_markers("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)
require_markers("docs_readme", text("Documentation/zigux/README.md"), DOCS_README_MARKERS)
require_markers("scripts_readme", text("scripts/zigux/README.md"), SCRIPTS_README_MARKERS)
require_markers("tests_readme", text("zigux/tests/README.md"), TESTS_README_MARKERS)
require_markers("review_checklist", text("Documentation/zigux/review-checklist.md"), REVIEW_CHECKLIST_MARKERS)
require_markers("readiness_survey", text("Documentation/zigux/phase15-readiness-gate-survey.md"), READINESS_SURVEY_MARKERS)

if missing:
    print("PHASE15_VALIDATION=fail")
    print("PHASE15_VALIDATION_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE15_VALIDATION_MISSING_END")
    sys.exit(1)

print("PHASE15_VALIDATION=pass")
print(f"PHASE15_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE15_REQUIRED_MARKER_COUNT="
    + str(
        len(MAKE_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(DOCS_README_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(READINESS_SURVEY_MARKERS)
    )
)
print("PHASE15_REMAINING_BLOCKERS=phase15-deep-core-status-change-blocker")

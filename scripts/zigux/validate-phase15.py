#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase15.py",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
]

MAKE_MARKERS = [
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/validate-phase15.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
]

WORKFLOW_MARKERS = [
    "Run Phase 15 governance tests",
    "make -C zigux phase15",
]

SURVEY_MARKERS = [
    "## Current Repo Readiness",
    "## Readiness Gate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
]

BUILD_MARKERS = [
    "phase15-freeze-map-governance-tests",
    "phase15-parity-scorecard-tests",
    "phase15-architecture-council-review-process-tests",
    "phase15-indefinite-c-policy-tests",
    "phase15-readiness-gate-tests",
    "phase15-handoff-next-steps-tests",
]

def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE15_VALIDATION=fail")
    print("MISSING_PHASE15_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE15_FILES_END")
    sys.exit(1)

missing: list[str] = []
for name, source, markers in [
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("survey", text("Documentation/zigux/phase15-readiness-gate-survey.md"), SURVEY_MARKERS),
    ("build", text("zigux/tests/phase15_build.zig"), BUILD_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

manifest = load_json("zigux/tests/phase15_readiness_gate_manifest.json")
if manifest.get("phase") != "Phase 15":
    missing.append("manifest:phase")
lane_key = manifest.get("lane_key")
if not isinstance(lane_key, str) or not lane_key.startswith("P15-L"):
    missing.append("manifest:lane_key")
surveyed_commit = manifest.get("surveyed_commit")
if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
    missing.append("manifest:surveyed_commit")

repo_evidence = manifest.get("repo_evidence")
if not isinstance(repo_evidence, dict):
    missing.append("manifest:repo_evidence")
else:
    for key in [
        "freeze_map_present",
        "review_checklist_present",
        "review_process_present",
        "parity_scorecard_present",
        "indefinite_c_policy_present",
        "handoff_next_steps_present",
        "phase15_build_present",
        "phase15_make_target_present",
        "shared_ci_phase15_present",
        "phase15_replay_green_on_current_master",
    ]:
        if repo_evidence.get(key) is not True:
            missing.append(f"manifest:repo_evidence:{key}")
    if repo_evidence.get("deep_core_status_change_ready") is not False:
        missing.append("manifest:repo_evidence:deep_core_status_change_ready")

remaining_gaps = manifest.get("remaining_gaps")
if not isinstance(remaining_gaps, list) or len(remaining_gaps) != 1:
    missing.append("manifest:remaining_gaps")
else:
    gap = remaining_gaps[0]
    if not isinstance(gap, dict):
        missing.append("manifest:remaining_gaps:shape")
    else:
        if gap.get("id") != "phase15-deep-core-status-change-blocker":
            missing.append("manifest:remaining_gaps:id")
        if gap.get("status") != "blocked_on_stay_in_c_evidence":
            missing.append("manifest:remaining_gaps:status")

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
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SURVEY_MARKERS) + len(BUILD_MARKERS)}"
)
print("PHASE15_REMAINING_BLOCKER=phase15-deep-core-status-change-blocker")

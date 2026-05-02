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
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_docs_root_reviewability.zig",
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

README_MARKERS = [
    "Phase 15 notes",
    "only remaining blocked work is the deep-core status-change evidence",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
]

SCRIPTS_README_MARKERS = [
    "Phase 15 flow",
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
]

TESTS_README_MARKERS = [
    "Phase 15 guidance",
    "zigux/tests/phase15_build.zig",
    "scripts/zigux/validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "blocked deep-core status-change posture",
]

SURVEY_MARKERS = [
    "## Current Repo Readiness",
    "## Readiness Gate",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "docs-root Phase 15 summary now matches the dedicated readiness and handoff packet",
    "phase15-docs-root-summary-alignment",
]

HANDOFF_MARKERS = [
    "PHASE15_LANE_KEY=P15-Y07",
    "## Current Handoff Surface",
    "## Open Handoff Gaps",
    "## Pending Next Steps",
    "## Maintenance Handoff Contract",
    "docs-root release evidence now matches the dedicated maintenance packet",
    "phase15-docs-root-summary-alignment",
    "phase15-deep-core-status-change-blocker",
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
    "phase15-docs-root-reviewability-tests",
]

HANDOFF_TEST_MARKERS = [
    'try std.testing.expectEqualStrings("P15-Y07", manifest.lane_key);',
    "phase15-deep-core-status-change-blocker",
    "make -C zigux phase15",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "docs_root_phase15_summary_aligned",
]

DOCS_ROOT_REVIEWABILITY_MARKERS = [
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "only remaining blocked work is the deep-core status-change evidence",
    "docs-root Phase 15 summary now matches the dedicated readiness and handoff packet",
    "phase15-docs-root-summary-alignment",
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str):
    return json.loads(text(path))


missing = []


def require(condition: bool, key: str) -> None:
    if not condition:
        missing.append(key)


def require_markers(name: str, source: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")


def require_true(mapping, prefix: str, keys: list[str]) -> None:
    for key in keys:
        if mapping.get(key) is not True:
            missing.append(f"{prefix}:{key}")


def require_false(mapping, prefix: str, keys: list[str]) -> None:
    for key in keys:
        if mapping.get(key) is not False:
            missing.append(f"{prefix}:{key}")


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print('PHASE15_VALIDATION=fail')
    print('MISSING_PHASE15_FILES_START')
    for path in missing_files:
        print(path)
    print('MISSING_PHASE15_FILES_END')
    sys.exit(1)

require_markers('make', text('zigux/Makefile'), MAKE_MARKERS)
require_markers('workflow', text('.github/workflows/zigux-bootstrap.yml'), WORKFLOW_MARKERS)
require_markers('readme', text('Documentation/zigux/README.md'), README_MARKERS)
require_markers('scripts_readme', text('scripts/zigux/README.md'), SCRIPTS_README_MARKERS)
require_markers('tests_readme', text('zigux/tests/README.md'), TESTS_README_MARKERS)
require_markers('survey', text('Documentation/zigux/phase15-readiness-gate-survey.md'), SURVEY_MARKERS)
require_markers('handoff', text('Documentation/zigux/phase15-handoff-next-steps-survey.md'), HANDOFF_MARKERS)
require_markers('handoff_test', text('zigux/tests/phase15_handoff_next_steps.zig'), HANDOFF_TEST_MARKERS)
require_markers('docs_root_reviewability', text('zigux/tests/phase15_docs_root_reviewability.zig'), DOCS_ROOT_REVIEWABILITY_MARKERS)
require_markers('build', text('zigux/tests/phase15_build.zig'), BUILD_MARKERS)

readiness_manifest = load_json('zigux/tests/phase15_readiness_gate_manifest.json')
require(readiness_manifest.get('phase') == 'Phase 15', 'manifest:phase')
require(readiness_manifest.get('lane_key') == 'P15-L01', 'manifest:lane_key')
require(readiness_manifest.get('surveyed_commit') == 'b5f64cf3306b706ea93cc9d3de769d545849b2d4', 'manifest:surveyed_commit')
repo_evidence = readiness_manifest.get('repo_evidence', {})
require_true(repo_evidence, 'manifest:repo_evidence', [
    'freeze_map_present', 'review_checklist_present', 'review_process_present', 'parity_scorecard_present',
    'indefinite_c_policy_present', 'handoff_next_steps_present', 'phase15_build_present',
    'phase15_make_target_present', 'shared_ci_phase15_present', 'phase15_replay_green_on_current_master',
    'docs_root_phase15_summary_aligned',
])
require_false(repo_evidence, 'manifest:repo_evidence', ['deep_core_status_change_ready'])
remaining_gaps = readiness_manifest.get('remaining_gaps')
require(isinstance(remaining_gaps, list) and len(remaining_gaps) == 1, 'manifest:remaining_gaps')
if isinstance(remaining_gaps, list) and len(remaining_gaps) == 1:
    gap = remaining_gaps[0]
    require(gap.get('id') == 'phase15-deep-core-status-change-blocker', 'manifest:remaining_gaps:id')
    require(gap.get('status') == 'blocked_on_stay_in_c_evidence', 'manifest:remaining_gaps:status')
    require(gap.get('zigux_destination') == 'Documentation/zigux/phase15-parity-scorecard.md', 'manifest:remaining_gaps:zigux_destination')

handoff_manifest = load_json('zigux/tests/phase15_handoff_next_steps_manifest.json')
require(handoff_manifest.get('phase') == 'Phase 15', 'handoff_manifest:phase')
require(handoff_manifest.get('lane_key') == 'P15-Y07', 'handoff_manifest:lane_key')
require(handoff_manifest.get('surveyed_commit') == 'b5f64cf3306b706ea93cc9d3de769d545849b2d4', 'handoff_manifest:surveyed_commit')
handoff_repo_evidence = handoff_manifest.get('repo_evidence', {})
require_true(handoff_repo_evidence, 'handoff_manifest:repo_evidence', [
    'freeze_map_governance_present', 'review_process_present', 'parity_scorecard_present',
    'indefinite_c_policy_present', 'readiness_gate_present', 'phase15_build_present',
    'phase15_make_target_present', 'shared_ci_phase15_present', 'docs_index_handoff_pointer_present',
    'docs_root_reviewability_guard_present', 'phase15_replay_green_on_current_master',
    'docs_root_phase15_summary_aligned',
])
require_false(handoff_repo_evidence, 'handoff_manifest:repo_evidence', ['deep_core_status_change_ready'])
open_handoff_gaps = handoff_manifest.get('open_handoff_gaps')
require(isinstance(open_handoff_gaps, list) and len(open_handoff_gaps) == 1, 'handoff_manifest:open_handoff_gaps')
if isinstance(open_handoff_gaps, list) and len(open_handoff_gaps) == 1:
    gap = open_handoff_gaps[0]
    require(gap.get('id') == 'phase15-deep-core-status-change-blocker', 'handoff_manifest:open_handoff_gaps:id')
    require(gap.get('status') == 'blocked_on_stay_in_c_evidence', 'handoff_manifest:open_handoff_gaps:status')

review_process_manifest = load_json('zigux/tests/phase15_architecture_council_review_process_manifest.json')
require(review_process_manifest.get('phase') == 'Phase 15', 'review_process_manifest:phase')
require(isinstance(review_process_manifest.get('lane_key'), str) and review_process_manifest['lane_key'].startswith('P15-L'), 'review_process_manifest:lane_key')
require(isinstance(review_process_manifest.get('surveyed_commit'), str) and HEX40.fullmatch(review_process_manifest['surveyed_commit']), 'review_process_manifest:surveyed_commit')

scorecard_manifest = load_json('zigux/tests/phase15_parity_scorecard.json')
require(scorecard_manifest.get('phase') == 'Phase 15', 'scorecard_manifest:phase')
require(scorecard_manifest.get('lane_key') == 'P15-L12', 'scorecard_manifest:lane_key')

if missing:
    print('PHASE15_VALIDATION=fail')
    print('PHASE15_VALIDATION_MISSING_START')
    for item in missing:
        print(item)
    print('PHASE15_VALIDATION_MISSING_END')
    sys.exit(1)

print('PHASE15_VALIDATION=pass')
print(f'PHASE15_REQUIRED_FILE_COUNT={len(FILES)}')
print(
    'PHASE15_REQUIRED_MARKER_COUNT=' + str(
        len(MAKE_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(README_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(SURVEY_MARKERS)
        + len(HANDOFF_MARKERS)
        + len(HANDOFF_TEST_MARKERS)
        + len(DOCS_ROOT_REVIEWABILITY_MARKERS)
        + len(BUILD_MARKERS)
    )
)
print('PHASE15_REMAINING_BLOCKERS=phase15-deep-core-status-change-blocker')

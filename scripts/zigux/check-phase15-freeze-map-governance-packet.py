#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
GOVERNANCE_NOTE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
STUDY_ONLY_NOTE_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MANIFEST_PATH = Path("zigux/tests/phase15_freeze_map_manifest.json")
TEST_PATH = Path("zigux/tests/phase15_freeze_map_governance.zig")
READINESS_CHECKER_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
CHECKLIST_CHECKER_PATH = Path("scripts/zigux/check-phase15-review-checklist-study-only-alignment.py")
TESTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-tests-readme-alignment.py")
SCRIPTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-scripts-readme-alignment.py")
REVIEW_PROCESS_CHECKER_PATH = Path("scripts/zigux/check-phase15-review-process-handoff.py")
SHARED_GAP_CHECKER_PATH = Path("scripts/zigux/check-phase15-shared-summary-gap.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_ZIG_PATH = Path("zigux/tests/phase15_build.zig")
LANE_OWNER_TEST_PATH = Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
PHASE14_RCU_NOTE_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
PHASE14_SKBUFF_NOTE_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")
PHASE14_TRACEABILITY_PATH = Path("Documentation/zigux/phase14-core-boundary-traceability.md")
SELF_PATH = Path("scripts/zigux/check-phase15-freeze-map-governance-packet.py")

EXPECTED_LANE_KEY = "P15-L04"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27"
EXPECTED_FREEZE_TARGETS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)
EXPECTED_STUDY_ONLY_TARGETS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)
EXPECTED_REPLAY_COMMANDS = (
    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-process-handoff.py",
    "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
    "python3 scripts/zigux/check-phase15-readiness-gate-packet.py",
    "zig test zigux/tests/phase15_freeze_map_governance.zig",
)
REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=governance_slice_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "PHASE15_SLICE=freeze-map-route-gap-truthfulness-refresh",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`zigux/tests/phase15_freeze_map_manifest.json`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`zigux/Makefile` still carries no `phase15-validate`, `phase15-test`, or `phase15` routes",
    "the freeze-map anchor set and study-only scope therefore stay unchanged on current `master`",
    "there is no silent exception path around the stay-in-C policy",
    "materialized_in_contents_readback `phase15-readiness-gate-note-readback`",
    "materialized_in_contents_readback `phase15-readiness-gate-checker-readback`",
    "materialized_in_contents_readback `phase15-shared-lane-owner-readback`",
    "materialized_in_contents_readback `phase15-review-checklist-study-only-boundary-guard`",
    "materialized_in_contents_readback `phase15-tests-readme-alignment-guard`",
    "materialized_in_contents_readback `phase15-shared-validator-route-readback`",
    "materialized_in_contents_readback `phase15-shared-build-route-readback`",
    "repo_reality_gap_confirmed `phase15-shared-wrapper-route-readback`",
    "blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`",
)
FREEZE_MAP_REQUIRED_TERMS = (
    "Architecture Council",
    "written rationale",
    "owner, phase, status bucket, validation gate summary, and rollback owner",
    "required approver set",
    "evidence archive path",
    "latest blocker disposition",
    "replay command",
    "rollback threshold",
    "retired_from_active_discussion",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
    "governance lane sequencing link or explicit scope note",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
    "## Stay-In-C Policy",
    "keep the code in C and record the blocker",
    "automatic return-to-blocked trigger",
    "no silent exception path",
)
EXPECTED_BLOCKERS = {
    "kernel/sched/core.c": "blocked_no_bounded_scheduler_seam",
    "mm/page_alloc.c": "blocked_no_bounded_allocator_seam",
    "kernel/rcu/tree.c": "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
    "net/core/skbuff.c": "blocked_packet_lifetime_boundary_still_too_wide",
}

def _read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def _makefile_has_target(root: Path, target: str) -> bool:
    makefile = root / MAKEFILE_PATH
    if not makefile.exists():
        return False
    return f"\n{target}:" in ("\n" + _read_text(makefile))

def collect_failures(root: Path) -> list[str]:
    failures = []
    required_paths = (
        FREEZE_MAP_PATH,GOVERNANCE_NOTE_PATH,STUDY_ONLY_NOTE_PATH,SHARED_GAP_NOTE_PATH,READINESS_NOTE_PATH,
        REVIEW_CHECKLIST_PATH,TESTS_README_PATH,MANIFEST_PATH,TEST_PATH,READINESS_CHECKER_PATH,CHECKLIST_CHECKER_PATH,
        TESTS_CHECKER_PATH,SCRIPTS_CHECKER_PATH,REVIEW_PROCESS_CHECKER_PATH,SHARED_GAP_CHECKER_PATH,VALIDATOR_PATH,
        BUILD_ZIG_PATH,LANE_OWNER_TEST_PATH,MAKEFILE_PATH,PHASE14_RCU_NOTE_PATH,PHASE14_SKBUFF_NOTE_PATH,
        PHASE14_TRACEABILITY_PATH,SELF_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures
    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    governance_note = _read_text(root / GOVERNANCE_NOTE_PATH)
    study_only_note = _read_text(root / STUDY_ONLY_NOTE_PATH)
    shared_gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    readiness_note = _read_text(root / READINESS_NOTE_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    tests_readme = _read_text(root / TESTS_README_PATH)
    rcu_note = _read_text(root / PHASE14_RCU_NOTE_PATH)
    skbuff_note = _read_text(root / PHASE14_SKBUFF_NOTE_PATH)
    traceability_note = _read_text(root / PHASE14_TRACEABILITY_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    if manifest.get('lane_key') != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get('phase') != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get('surveyed_commit') != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"surveyed_commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get('anchor') != str(FREEZE_MAP_PATH):
        failures.append('anchor')
    if tuple(manifest.get('freeze_in_c_targets', [])) != EXPECTED_FREEZE_TARGETS:
        failures.append('freeze_in_c_targets')
    if tuple(manifest.get('study_only_targets', [])) != EXPECTED_STUDY_ONLY_TARGETS:
        failures.append('study_only_targets')
    if EXPECTED_SURVEYED_COMMIT not in governance_note:
        failures.append('missing_note_surveyed_commit')
    if manifest.get('surveyed_commit_mode') != 'dated_master_readback':
        failures.append('surveyed_commit_mode')
    if 'readiness-gate survey' not in manifest.get('surveyed_commit_mode_reason', ''):
        failures.append('surveyed_commit_mode_reason')
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in governance_note:
            failures.append(f'missing_note_marker:{marker}')
    for term in FREEZE_MAP_REQUIRED_TERMS:
        if term not in freeze_map:
            failures.append(f'missing_freeze_map_term:{term}')
    for command in EXPECTED_REPLAY_COMMANDS:
        if command not in governance_note:
            failures.append(f'missing_replay_command:{command}')
    handoff = manifest.get('maintenance_handoff', {})
    if handoff.get('current_lane_posture') != 'maintenance_mode':
        failures.append('maintenance_handoff.current_lane_posture')
    if tuple(handoff.get('replay_before_trusting', [])) != EXPECTED_REPLAY_COMMANDS:
        failures.append('maintenance_handoff.replay_before_trusting')
    for condition in handoff.get('reopen_conditions', []):
        if condition not in governance_note.replace('`',''):
            failures.append(f'missing_reopen_condition:{condition}')
    if '`Documentation/zigux/phase15-study-only-anchor-accounting.md`' not in review_checklist:
        failures.append('review_checklist_study_only_link')
    if '`kernel/workqueue.c`' not in study_only_note:
        failures.append('study_only_kernel_workqueue')
    if '`kernel/trace/ring_buffer.c`' not in study_only_note:
        failures.append('study_only_ring_buffer')
    if '`scripts/zigux/check-phase15-readiness-gate-packet.py`' not in shared_gap_note:
        failures.append('shared_gap_readiness_checker')
    if 'Phase 15' not in tests_readme:
        failures.append('tests_readme_phase15_marker')
    if EXPECTED_SURVEYED_COMMIT not in readiness_note:
        failures.append('readiness_note_surveyed_commit')
    blocker_ownership = manifest.get('blocker_ownership', [])
    if len(blocker_ownership) != 4:
        failures.append('blocker_ownership_length')
    for entry in blocker_ownership:
        anchor = entry.get('anchor')
        expected_blocker = EXPECTED_BLOCKERS.get(anchor)
        if expected_blocker is None:
            failures.append(f'unexpected_blocker_anchor:{anchor}')
            continue
        if entry.get('latest_blocker_disposition') != expected_blocker:
            failures.append(f'blocker_disposition:{anchor}')
        if entry.get('replay_command') != 'zig test zigux/tests/phase15_freeze_map_governance.zig':
            failures.append(f'replay_command:{anchor}')
        snippet = f"- `{anchor}`: owner `{entry.get('owner')}`; phase `{entry.get('phase')}`; status bucket `{entry.get('status_bucket')}`; required approver set `{entry.get('required_approver_set')}`; validation gate `{entry.get('validation_gate')}`; rollback owner `{entry.get('rollback_owner')}`"
        if snippet not in governance_note:
            failures.append(f'missing_inventory_snippet:{anchor}')
    deep_core = manifest.get('deep_core_blocker_survey', [])
    if len(deep_core) != 4:
        failures.append('deep_core_blocker_survey_length')
    if 'PHASE14_LANE_KEY=P14-L16' not in rcu_note:
        failures.append('phase14_rcu_lane_key')
    if 'phase14-rcu-tree-bridge-blocker' not in rcu_note:
        failures.append('phase14_rcu_blocker')
    if 'PHASE14_LANE_KEY=P14-L11' not in skbuff_note:
        failures.append('phase14_skbuff_lane_key')
    if 'PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker' not in skbuff_note:
        failures.append('phase14_skbuff_blocker')
    if '`net/core/skbuff.c`: `Freeze In C Initially`' not in traceability_note:
        failures.append('phase14_traceability_skbuff_marker')
    for gap_id in (
        'phase15-readiness-gate-note-readback','phase15-readiness-gate-checker-readback','phase15-shared-lane-owner-readback',
        'phase15-review-checklist-study-only-boundary-guard','phase15-tests-readme-alignment-guard','phase15-shared-validator-route-readback',
        'phase15-shared-build-route-readback','phase15-shared-wrapper-route-readback','phase15-deep-core-status-change-blocker',
    ):
        if not any(gap.get('id') == gap_id for gap in manifest.get('gaps', [])):
            failures.append(f'missing_gap_id:{gap_id}')
    if _makefile_has_target(root, 'phase15-validate'):
        failures.append('unexpected_make_target:phase15-validate')
    if _makefile_has_target(root, 'phase15-test'):
        failures.append('unexpected_make_target:phase15-test')
    if _makefile_has_target(root, 'phase15'):
        failures.append('unexpected_make_target:phase15')
    return failures

def _placeholder_for(rel: Path) -> str:
    if rel.suffix == '.py':
        return '#!/usr/bin/env python3\n'
    if rel.suffix == '.zig':
        return 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n'
    if rel.suffix == '.json':
        return '{}\n'
    if rel.suffix == '.md':
        return f'# Placeholder for {rel.as_posix()}\n'
    return '\n'

def _sample_freeze_map() -> str:
    return """# Freeze Map

## Governance

- changes require Architecture Council approval with written rationale
- every lane must record owner, phase, status bucket, validation gate summary, and rollback owner
- status review must keep the required approver set, evidence archive path, latest blocker disposition, replay command, rollback threshold, retired_from_active_discussion, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, governance lane sequencing link or explicit scope note, study-only anchor accounting link or explicit freeze-map-anchor confirmation, explicit non-goals, and written rationale explicit

## Stay-In-C Policy

- ambiguous validation must keep the code in C and record the blocker
- every closeout keeps the automatic return-to-blocked trigger and no silent exception path
"""

def _sample_governance_note() -> str:
    return """# Phase 15 Freeze-Map Governance

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=freeze-map-route-gap-truthfulness-refresh`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`
- direct lane-owned boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
- adjacent governance inputs:
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-study-only-anchor-accounting.md`
  - `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
  - `scripts/zigux/check-phase15-tests-readme-alignment.py`
  - `scripts/zigux/check-phase15-readiness-gate-packet.py`
  - `scripts/zigux/validate-phase15.py`
  - `zigux/tests/phase15_build.zig`
  - `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

- `zigux/Makefile` still carries no `phase15-validate`, `phase15-test`, or `phase15` routes
- the freeze-map anchor set and study-only scope therefore stay unchanged on current `master`
- there is no silent exception path around the stay-in-C policy

## Freeze-In-C Anchor Governance Inventory

- `kernel/sched/core.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + PMO / Release Management`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + PMO / Release Management`
- `mm/page_alloc.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + Validation and Perf Team`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + Validation and Perf Team`
- `kernel/rcu/tree.c`: owner `ABI and Runtime Team`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + ABI and Runtime Team`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + ABI and Runtime Team`
- `net/core/skbuff.c`: owner `Shared Subsystems Pod`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + Shared Subsystems Pod`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Shared Subsystems Pod`

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this packet:
  - `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
  - `python3 scripts/zigux/check-phase15-tests-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
  - `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
  - `python3 scripts/zigux/check-phase15-readiness-gate-packet.py`
  - `zig test zigux/tests/phase15_freeze_map_governance.zig`
- reopen only when one of these packet-local conditions becomes true:
  - a freeze-map anchor changes status bucket, blocker disposition, or required approver set
  - the freeze-in-C or study-only anchor set changes in Documentation/zigux/freeze-map.md
  - the checker-backed shared reminder packet or an adjacent Phase 15 governance packet drifts enough to change the per-anchor evidence archive, replay command, stay-in-C, or no-silent-exception posture recorded here

## Recorded Gaps

- materialized_in_contents_readback `phase15-readiness-gate-note-readback`
- materialized_in_contents_readback `phase15-readiness-gate-checker-readback`
- materialized_in_contents_readback `phase15-shared-lane-owner-readback`
- materialized_in_contents_readback `phase15-review-checklist-study-only-boundary-guard`
- materialized_in_contents_readback `phase15-tests-readme-alignment-guard`
- materialized_in_contents_readback `phase15-shared-validator-route-readback`
- materialized_in_contents_readback `phase15-shared-build-route-readback`
- repo_reality_gap_confirmed `phase15-shared-wrapper-route-readback`
- blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`
"""

def _sample_manifest() -> str:
    payload = {
        'lane_key': EXPECTED_LANE_KEY,
        'phase': EXPECTED_PHASE,
        'surveyed_commit': EXPECTED_SURVEYED_COMMIT,
        'surveyed_commit_mode': 'dated_master_readback',
        'surveyed_commit_mode_reason': 'This freeze-map packet now records a dated current-master readback after a fresh reread confirmed that the readiness-gate survey, the focused readiness-packet checker, the tests-root alignment guard, the lane-owner replay, the validator-first companion, and the shared Phase 15 build companion are directly readable while the dedicated make-wrapper routes still remain broader repo-reality gaps.',
        'anchor': str(FREEZE_MAP_PATH),
        'freeze_in_c_targets': list(EXPECTED_FREEZE_TARGETS),
        'study_only_targets': list(EXPECTED_STUDY_ONLY_TARGETS),
        'blocker_ownership': [
            {'anchor': 'kernel/sched/core.c','owner': 'Architecture Council','phase': 'Phase 15','status_bucket': 'freeze_in_c','required_approver_set': 'Architecture Council + PMO / Release Management','validation_gate': 'Phase 15 parity scorecard plus Architecture Council reopen record','rollback_owner': 'Architecture Council + PMO / Release Management','evidence_archive_path': 'Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md','benchmark_notes': 'pending_until_bounded_scheduler_seam_exists','replay_command': 'zig test zigux/tests/phase15_freeze_map_governance.zig','latest_blocker_disposition': EXPECTED_BLOCKERS['kernel/sched/core.c']},
            {'anchor': 'mm/page_alloc.c','owner': 'Architecture Council','phase': 'Phase 15','status_bucket': 'freeze_in_c','required_approver_set': 'Architecture Council + Validation and Perf Team','validation_gate': 'Phase 15 parity scorecard plus Architecture Council reopen record','rollback_owner': 'Architecture Council + Validation and Perf Team','evidence_archive_path': 'Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md','benchmark_notes': 'pending_until_bounded_allocator_seam_exists','replay_command': 'zig test zigux/tests/phase15_freeze_map_governance.zig','latest_blocker_disposition': EXPECTED_BLOCKERS['mm/page_alloc.c']},
            {'anchor': 'kernel/rcu/tree.c','owner': 'ABI and Runtime Team','phase': 'Phase 15','status_bucket': 'freeze_in_c','required_approver_set': 'Architecture Council + ABI and Runtime Team','validation_gate': 'Phase 15 parity scorecard plus Architecture Council reopen record','rollback_owner': 'Architecture Council + ABI and Runtime Team','evidence_archive_path': 'Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md','benchmark_notes': 'pending_until_rcu_followup_is_narrower_than_freeze_boundary','replay_command': 'zig test zigux/tests/phase15_freeze_map_governance.zig','latest_blocker_disposition': EXPECTED_BLOCKERS['kernel/rcu/tree.c']},
            {'anchor': 'net/core/skbuff.c','owner': 'Shared Subsystems Pod','phase': 'Phase 15','status_bucket': 'freeze_in_c','required_approver_set': 'Architecture Council + Shared Subsystems Pod','validation_gate': 'Phase 15 parity scorecard plus Architecture Council reopen record','rollback_owner': 'Shared Subsystems Pod','evidence_archive_path': 'Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md','benchmark_notes': 'pending_until_skbuff_followup_is_narrower_than_lifetime_boundary','replay_command': 'zig test zigux/tests/phase15_freeze_map_governance.zig','latest_blocker_disposition': EXPECTED_BLOCKERS['net/core/skbuff.c']},
        ],
        'deep_core_blocker_survey': [{'anchor': anchor,'roadmap_basis': 'basis','repo_reality': 'reality','current_blocker': EXPECTED_BLOCKERS[anchor]} for anchor in EXPECTED_FREEZE_TARGETS],
        'maintenance_handoff': {'current_lane_posture': 'maintenance_mode','replay_before_trusting': list(EXPECTED_REPLAY_COMMANDS),'reopen_conditions': ['a freeze-map anchor changes status bucket, blocker disposition, or required approver set','the freeze-in-C or study-only anchor set changes in Documentation/zigux/freeze-map.md','the checker-backed shared reminder packet or an adjacent Phase 15 governance packet drifts enough to change the per-anchor evidence archive, replay command, stay-in-C, or no-silent-exception posture recorded here']},
        'gaps': [{'id': gap_id} for gap_id in ('phase15-readiness-gate-note-readback','phase15-readiness-gate-checker-readback','phase15-shared-lane-owner-readback','phase15-review-checklist-study-only-boundary-guard','phase15-tests-readme-alignment-guard','phase15-shared-validator-route-readback','phase15-shared-build-route-readback','phase15-shared-wrapper-route-readback','phase15-deep-core-status-change-blocker')],
    }
    return json.dumps(payload, indent=2) + '\n'

def _seed_repo(root: Path) -> None:
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / GOVERNANCE_NOTE_PATH, _sample_governance_note())
    _write(root / STUDY_ONLY_NOTE_PATH, '# Study only\n\n- `kernel/workqueue.c`\n- `kernel/trace/ring_buffer.c`\n')
    _write(root / SHARED_GAP_NOTE_PATH, '- `scripts/zigux/check-phase15-readiness-gate-packet.py`\n')
    _write(root / READINESS_NOTE_PATH, f'- `{EXPECTED_SURVEYED_COMMIT}`\n')
    _write(root / REVIEW_CHECKLIST_PATH, '- `Documentation/zigux/phase15-study-only-anchor-accounting.md`\n')
    _write(root / TESTS_README_PATH, '# Tests\n\nPhase 15 reminder\n')
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / TEST_PATH, _placeholder_for(TEST_PATH))
    _write(root / MAKEFILE_PATH, 'phase2-toolchain:\n\t@true\n')
    _write(root / PHASE14_RCU_NOTE_PATH, 'PHASE14_LANE_KEY=P14-L16\nphase14-rcu-tree-bridge-blocker\n')
    _write(root / PHASE14_SKBUFF_NOTE_PATH, 'PHASE14_LANE_KEY=P14-L11\nPHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker\n')
    _write(root / PHASE14_TRACEABILITY_PATH, '`net/core/skbuff.c`: `Freeze In C Initially`\n')
    for rel in (READINESS_CHECKER_PATH,CHECKLIST_CHECKER_PATH,TESTS_CHECKER_PATH,SCRIPTS_CHECKER_PATH,REVIEW_PROCESS_CHECKER_PATH,SHARED_GAP_CHECKER_PATH,VALIDATOR_PATH,BUILD_ZIG_PATH,LANE_OWNER_TEST_PATH,SELF_PATH):
        _write(root / rel, _placeholder_for(rel))

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase15_freeze_map_packet_') as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f'baseline fixture should pass: {failures}')
        case_root = root / 'lane_drift'
        _seed_repo(case_root)
        _write(case_root / MANIFEST_PATH, _sample_manifest().replace('"lane_key": "P15-L04"', '"lane_key": "P15-L99"', 1))
        failures = collect_failures(case_root)
        if failures != ["lane_key:'P15-L99'"]:
            raise AssertionError(f'unexpected lane drift failures: {failures}')
        case_root = root / 'note_marker'
        _seed_repo(case_root)
        _write(case_root / GOVERNANCE_NOTE_PATH, _sample_governance_note().replace('- materialized_in_contents_readback `phase15-shared-build-route-readback`\n', '', 1))
        failures = collect_failures(case_root)
        expected = ['missing_note_marker:materialized_in_contents_readback `phase15-shared-build-route-readback`']
        if failures != expected:
            raise AssertionError(f'unexpected note-marker failures: {failures}')
        case_root = root / 'freeze_term'
        _seed_repo(case_root)
        _write(case_root / FREEZE_MAP_PATH, _sample_freeze_map().replace('rollback threshold, ', '', 1))
        failures = collect_failures(case_root)
        if failures != ['missing_freeze_map_term:rollback threshold']:
            raise AssertionError(f'unexpected freeze-term failures: {failures}')
        case_root = root / 'make_target'
        _seed_repo(case_root)
        _write(case_root / MAKEFILE_PATH, 'phase15:\n\t@true\n')
        failures = collect_failures(case_root)
        if failures != ['unexpected_make_target:phase15']:
            raise AssertionError(f'unexpected make-target failures: {failures}')
    print('PHASE15_FREEZE_MAP_GOVERNANCE_PACKET_SELF_TEST=pass')
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description='Verify that the Phase 15 freeze-map governance packet stays aligned.')
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='repository root')
    parser.add_argument('--self-test', action='store_true', help='run the synthetic fixture coverage for this checker')
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        return 1
    print('Phase 15 freeze-map governance packet check passed.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

"""Fail closed when Phase 10 closure-manifest summary counts or route anchors drift."""
from __future__ import annotations
import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path
SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MANIFEST_PATH = 'zigux/tests/phase10_closure_manifest.json'
LEDGER_PATH = 'zigux-alpha/PHASE10_CLOSURE_LEDGER.md'
COUNT_FIELDS = {'doc_count': 'docs', 'manifest_count': 'manifests', 'driver_count': 'drivers', 'test_count': 'tests'}
REQUIRED_EXACT_CHECKS = ['python3 scripts/zigux/check-phase10-bootstrap-route.py', 'python3 scripts/zigux/check-phase10-core-packet.py', 'python3 scripts/zigux/check-phase10-shared-freeze-boundary.py', 'python3 scripts/zigux/check-phase10-ring-packet.py', 'python3 scripts/zigux/check-phase10-input-packet.py', 'python3 scripts/zigux/check-phase10-mmio-packet.py', 'python3 scripts/zigux/check-phase10-harness-coverage.py', 'python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py', 'python3 scripts/zigux/check-phase10-closure-manifest-counts.py', 'python3 scripts/zigux/validate-phase10.py', 'python3 scripts/zigux/validate-phase10-closure.py', 'make -C zigux phase10-validate', 'zig build test --build-file zigux/tests/phase10_build.zig --summary all', 'make -C zigux phase10-test', 'make -C zigux phase10']
REQUIRED_RING_SCOREBOARD_EVIDENCE = ['drivers/virtio/virtio_ring.zig', 'drivers/virtio/virtio_ring_publish_readiness.zig', 'zigux/tests/phase10_virtio_ring.zig', 'zigux/tests/phase10_virtio_ring_manifest.json', 'Documentation/zigux/phase10-virtio-ring-survey.md']
REQUIRED_MMIO_SCOREBOARD_EVIDENCE = ['drivers/virtio/virtio_mmio.zig', 'zigux/tests/phase10_virtio_mmio.zig', 'drivers/virtio/virtio_mmio_verify.zig', 'zigux/tests/phase10_virtio_mmio_manifest.json', 'Documentation/zigux/phase10-virtio-mmio-survey.md']
REQUIRED_LAB_VALIDATION_EVIDENCE = ['scripts/zigux/check-phase10-core-packet.py', 'scripts/zigux/check-phase10-closure-manifest-counts.py', 'scripts/zigux/validate-phase10.py', 'scripts/zigux/validate-phase10-closure.py', 'zigux/Makefile', '.github/workflows/zigux-bootstrap.yml', 'zigux/tests/phase10_virtio_ring_queue_build.zig', 'zigux/tests/phase10_virtio_ring_queue_build_survey.zig']
REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE = ['drivers/virtio/virtio_input_teardown_preflight.zig', 'zigux/tests/phase10_virtio_input_teardown_preflight.zig']
REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE = ['zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig']
REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE = ['samples/zigux', 'zigux/tests/phase5_build.zig', 'Documentation/zigux/review-checklist.md']
REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE = ['Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md', 'Documentation/zigux/phase9-runtime-trace-events-survey.md', 'samples/zigux/runtime_bitmap_loader.zig', 'samples/zigux/runtime_trace_events.zig', 'zigux/tests/phase9_build.zig', 'zigux/kernel/runtime_loader.zig', 'zigux/tests/runtime_trace_events_manifest.json', 'zigux/tests/runtime_trace_events_survey.zig']
REQUIRED_CORE_LAB_VALIDATION_EVIDENCE = ['Documentation/zigux/phase10-virtio-core-survey.md', 'drivers/virtio/virtio_driver_id.zig', 'zigux/tests/phase10_virtio_driver_id.zig', 'zigux/tests/phase10_virtio_core.zig', 'zigux/tests/phase10_virtio_core_reset_queue.zig', 'zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig', 'zigux/tests/phase10_virtio_core_survey.zig']
REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE = ['Documentation/zigux/phase10-closure-evidence.md', 'zigux/tests/phase10_virtio_core_manifest.json', 'zigux/tests/phase10_virtio_ring_manifest.json', 'zigux/tests/phase10_virtio_input_manifest.json', 'zigux/tests/phase10_virtio_mmio_manifest.json']
REQUIRED_SURVEY_PROVENANCE_SOURCE = 'manifest_derived'
REQUIRED_SURVEY_LANE_KEYS = {'core': 'P10-L01', 'ring': 'P10-L10', 'input': 'P10-L22', 'mmio': 'P10-L11'}
REQUIRED_SURVEY_COMMITS = {'core': 'c11221dc7a68d7511ae1c69d64b3f08528287ed8', 'ring': '0aa2db32bcb1c7065850ee3f66ec119b071fbf5c', 'input': 'ee789f026f11a0c5c70ded9a868979cdf4f55393', 'mmio': 'b53ec2bd507d0b3283486e76acc273b184ad5bf8'}
LEDGER_STATUS_FIELDS = {'virtqueue_wrappers': 'PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS', 'mmio_wrappers': 'PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS', 'lab_only_driver_validation': 'PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION', 'dual_implementations_for_risky_areas': 'PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS'}
LEDGER_EVIDENCE_FIELDS = {'virtqueue_wrappers': 'PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE', 'mmio_wrappers': 'PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE', 'lab_only_driver_validation': 'PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE', 'dual_implementations_for_risky_areas': 'PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE'}
REQUIRED_CORE_BLOCKED_TRANSPORT_PATH = 'zigux/tests/phase10_virtio_core_manifest.json'
REQUIRED_CORE_BLOCKED_TRANSPORT_GAP = 'phase10-core-probe-remove-lifecycle'
REQUIRED_INPUT_READY_TRANSPORT_PATH = 'zigux/tests/phase10_virtio_input_manifest.json'
REQUIRED_INPUT_READY_TRANSPORT_GAP = 'phase10-virtio-input-registration-lifecycle'
REQUIRED_MMIO_READY_TRANSPORT_PATH = 'zigux/tests/phase10_virtio_mmio_manifest.json'
REQUIRED_MMIO_READY_TRANSPORT_GAP = 'phase10-mmio-lifecycle-and-irq-paths'
REQUIRED_LANDED_CORE_HELPER_EVIDENCE = {'zigux/tests/phase10_virtio_core_manifest.json': ['phase10-queue-shape-bookkeeping-helper', 'phase10-config-generation-bookkeeping-helper', 'phase10-interrupt-ack-bookkeeping-helper', 'phase10-lifecycle-guard-bookkeeping-helper', 'phase10-driver-validation-narrowing-helper', 'phase10-core-attribute-summary-helper', 'phase10-reset-replay-bookkeeping-helper']}
REQUIRED_LANDED_RING_HELPER_EVIDENCE = {'zigux/tests/phase10_virtio_ring_manifest.json': ['phase10-virtqueue-shape-helper', 'phase10-used-buffer-polling-helper', 'phase10-callback-enable-helper', 'phase10-callback-delay-helper', 'phase10-notify-prepare-helper', 'phase10-notification-data-summary-helper', 'phase10-broken-queue-poll-guard', 'phase10-queue-publish-readiness-helper', 'phase10-queue-reset-helper', 'phase10-queue-reset-readiness-helper', 'phase10-ring-verify-replay', 'phase10-virtio-ring-slice-note']}
REQUIRED_LANDED_INPUT_HELPER_EVIDENCE = {'zigux/tests/phase10_virtio_input_manifest.json': ['phase10-virtio-input-capability-setup-helper', 'phase10-virtio-input-multitouch-slot-helper', 'phase10-virtio-input-probe-preflight-helper', 'phase10-virtio-input-teardown-preflight-helper', 'phase10-virtio-input-teardown-observation-helper', 'phase10-virtio-input-registration-preflight-helper', 'phase10-virtio-input-queue-callback-preflight-helper', 'phase10-virtio-input-status-drain-helper']}
REQUIRED_LANDED_MMIO_HELPER_EVIDENCE = {'zigux/tests/phase10_virtio_mmio_manifest.json': ['phase10-virtio-mmio-lab-helper', 'phase10-mmio-transport-identity-helper', 'phase10-mmio-probe-preflight-helper', 'phase10-mmio-selected-queue-readiness-helper', 'phase10-mmio-interrupt-ack-disposition-helper', 'phase10-mmio-feature-negotiation-summary-helper', 'phase10-mmio-config-write-plan-freshness-helper', 'phase10-mmio-config-write-disposition-helper', 'phase10-mmio-config-write-apply-observation-helper']}
REQUIRED_FOCUSED_HARNESS_REPLAYS = {
    'zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig': ['phase10 core interrupt-compound-ack replay'],
    'zigux/tests/phase10_virtio_core_reset_queue.zig': ['phase10 core reset-queue replay'],
    'zigux/tests/phase10_virtio_driver_id.zig': ['phase10 driver-id review path replay'],
    'zigux/tests/phase10_virtio_ring.zig': ['phase10 ring broader replay'],
    'zigux/tests/phase10_virtio_ring_notification_data_readiness.zig': ['phase10 ring notification-data readiness replay'],
    'zigux/tests/phase10_virtio_ring_registration_replay.zig': ['phase10 ring queue-registration replay'],
    'zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig': ['phase10 ring prepare-kick idempotence replay'],
    'zigux/tests/phase10_virtio_ring_reset_reuse.zig': ['phase10 ring drained-reset reuse replay'],
    'zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig': ['phase10 ring broken-queue queue-discipline replay'],
    'zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig': ['phase10 ring delayed-callback budget replay'],
    'zigux/tests/phase10_virtio_ring_queue_build.zig': ['phase10 ring focused queue-build replay'],
    'zigux/tests/phase10_virtio_ring_queue_build_survey.zig': ['phase10 ring queue-build survey replay'],
    'zigux/tests/phase10_virtio_input_queue_callback_preflight.zig': ['phase10 input queue-callback-preflight replay'],
    'zigux/tests/phase10_virtio_input_status_drain.zig': ['phase10 input status-drain replay'],
    'zigux/tests/phase10_virtio_input_probe_preflight.zig': ['phase10 input probe-preflight replay'],
    'zigux/tests/phase10_virtio_input_registration_preflight.zig': ['phase10 input registration-preflight replay'],
    'zigux/tests/phase10_virtio_input_teardown_preflight.zig': ['phase10 input teardown-preflight replay'],
    'zigux/tests/phase10_virtio_input_teardown_observation.zig': ['phase10 input teardown-observation replay'],
    'zigux/tests/phase10_virtio_mmio.zig': ['phase10 mmio lab replay'],
    'zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig': ['phase10 mmio apply-observation replay'],
    'drivers/virtio/virtio_mmio_verify.zig': ['phase10 mmio wrapper-facing verify replay'],
    'zigux/tests/phase10_virtio_mmio_survey.zig': ['phase10 mmio survey replay'],
    'drivers/virtio/virtio_ring_publish_readiness.zig': ['phase10 ring publish-readiness wrapper replay'],
}

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def build_expected_ledger_lines(manifest: dict) -> list[str]:
    scoreboard = manifest.get('roadmap_parity_scoreboard')
    provenance = manifest.get('survey_provenance')
    if not isinstance(scoreboard, dict) or not isinstance(provenance, dict):
        return []
    lane_keys = provenance.get('lane_keys')
    surveyed_commits = provenance.get('surveyed_commits')
    if not isinstance(lane_keys, dict) or not isinstance(surveyed_commits, dict):
        return []
    lines = [f'PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE={MANIFEST_PATH}']
    source = provenance.get('source')
    if isinstance(source, str) and source:
        lines.append(f'PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE={source}')
    for key in ('core', 'ring', 'input', 'mmio'):
        lane = lane_keys.get(key)
        if isinstance(lane, str) and lane:
            lines.append(f'PHASE10_LEDGER_SURVEY_{key.upper()}_LANE={lane}')
        commit = surveyed_commits.get(key)
        if isinstance(commit, str) and commit:
            lines.append(f'PHASE10_LEDGER_SURVEY_{key.upper()}_COMMIT={commit}')
    for key, ledger_key in LEDGER_STATUS_FIELDS.items():
        row = scoreboard.get(key)
        if isinstance(row, dict):
            status = row.get('status')
            if isinstance(status, str) and status:
                lines.append(f'{ledger_key}={status}')
    for key, ledger_key in LEDGER_EVIDENCE_FIELDS.items():
        row = scoreboard.get(key)
        if isinstance(row, dict):
            evidence = row.get('evidence')
            if isinstance(evidence, list) and evidence:
                lines.append(f"{ledger_key}={','.join(evidence)}")
    return lines

def collect_ledger_drift(manifest: dict, ledger_text: str) -> list[str]:
    drift: list[str] = []
    expected_lines = build_expected_ledger_lines(manifest)
    if not expected_lines:
        return ['ledger:expected_lines:missing']
    for line in expected_lines:
        if line not in ledger_text:
            drift.append(f'ledger:{line}')
    return drift

def require_list_members(drift: list[str], prefix: str, actual_list: object, required_items: list[str]) -> None:
    if not isinstance(actual_list, list) or not actual_list:
        drift.append(f'{prefix}:missing')
        return
    for item in required_items:
        if item not in actual_list:
            drift.append(f'{prefix}:{item!r}:missing')

def require_mapping_list_members(drift: list[str], manifest: dict, field_name: str, requirements: dict[str, list[str]]) -> None:
    evidence = manifest.get(field_name)
    if not isinstance(evidence, dict):
        drift.append(f'{field_name}:missing')
        return
    for path, required_labels in requirements.items():
        labels = evidence.get(path)
        if not isinstance(labels, list) or not labels:
            drift.append(f'{field_name}:{path}:missing')
            continue
        for label in required_labels:
            if label not in labels:
                drift.append(f'{field_name}:{path}:{label!r}:missing')

def collect_drift(manifest: dict) -> list[str]:
    drift: list[str] = []
    for count_field, list_field in COUNT_FIELDS.items():
        listed = manifest.get(list_field)
        if not isinstance(listed, list) or not listed:
            drift.append(f'{list_field}:missing')
            continue
        count = manifest.get(count_field)
        if not isinstance(count, int):
            drift.append(f'{count_field}:missing')
            continue
        actual = len(listed)
        if count != actual:
            drift.append(f'{count_field}:{count}!=len({list_field}):{actual}')
    exact_checks = manifest.get('exact_checks')
    if not isinstance(exact_checks, list) or not exact_checks:
        drift.append('exact_checks:missing')
        return drift
    indexes: list[int] = []
    for item in REQUIRED_EXACT_CHECKS:
        if item not in exact_checks:
            drift.append(f'exact_checks:{item!r}:missing')
            continue
        indexes.append(exact_checks.index(item))
    if len(indexes) == len(REQUIRED_EXACT_CHECKS) and indexes != sorted(indexes):
        drift.append('exact_checks:closure_route:out_of_order')
    scoreboard = manifest.get('roadmap_parity_scoreboard')
    if not isinstance(scoreboard, dict):
        drift.append('roadmap_parity_scoreboard:missing')
        return drift
    virtqueue_wrappers = scoreboard.get('virtqueue_wrappers')
    if not isinstance(virtqueue_wrappers, dict):
        drift.append('roadmap_parity_scoreboard:virtqueue_wrappers:missing')
        return drift
    require_list_members(drift, 'roadmap_parity_scoreboard:virtqueue_wrappers', virtqueue_wrappers.get('evidence'), REQUIRED_RING_SCOREBOARD_EVIDENCE)
    mmio_wrappers = scoreboard.get('mmio_wrappers')
    if not isinstance(mmio_wrappers, dict):
        drift.append('roadmap_parity_scoreboard:mmio_wrappers:missing')
        return drift
    require_list_members(drift, 'roadmap_parity_scoreboard:mmio_wrappers', mmio_wrappers.get('evidence'), REQUIRED_MMIO_SCOREBOARD_EVIDENCE)
    lab_only_driver_validation = scoreboard.get('lab_only_driver_validation')
    if not isinstance(lab_only_driver_validation, dict):
        drift.append('roadmap_parity_scoreboard:lab_only_driver_validation:missing')
        return drift
    require_list_members(drift, 'roadmap_parity_scoreboard:lab_only_driver_validation', lab_only_driver_validation.get('evidence'), REQUIRED_LAB_VALIDATION_EVIDENCE + REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE + REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE + REQUIRED_CORE_LAB_VALIDATION_EVIDENCE)
    dual_implementations = scoreboard.get('dual_implementations_for_risky_areas')
    if not isinstance(dual_implementations, dict):
        drift.append('roadmap_parity_scoreboard:dual_implementations_for_risky_areas:missing')
        return drift
    require_list_members(drift, 'roadmap_parity_scoreboard:dual_implementations_for_risky_areas', dual_implementations.get('evidence'), REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE)
    provenance = manifest.get('survey_provenance')
    if not isinstance(provenance, dict):
        drift.append('survey_provenance:missing')
        return drift
    if provenance.get('source') != REQUIRED_SURVEY_PROVENANCE_SOURCE:
        drift.append(f"survey_provenance:source:{provenance.get('source')!r}!={REQUIRED_SURVEY_PROVENANCE_SOURCE!r}")
    lane_keys = provenance.get('lane_keys')
    if not isinstance(lane_keys, dict):
        drift.append('survey_provenance:lane_keys:missing')
        return drift
    for key, expected in REQUIRED_SURVEY_LANE_KEYS.items():
        actual = lane_keys.get(key)
        if actual != expected:
            drift.append(f'survey_provenance:lane_keys:{key}:{actual!r}!={expected!r}')
    surveyed_commits = provenance.get('surveyed_commits')
    if not isinstance(surveyed_commits, dict):
        drift.append('survey_provenance:surveyed_commits:missing')
        return drift
    for key, expected in REQUIRED_SURVEY_COMMITS.items():
        actual = surveyed_commits.get(key)
        if actual != expected:
            drift.append(f'survey_provenance:surveyed_commits:{key}:{actual!r}!={expected!r}')
    cross_phase_boundary = manifest.get('cross_phase_scoreboard_boundary')
    if not isinstance(cross_phase_boundary, dict):
        drift.append('cross_phase_scoreboard_boundary:missing')
        return drift
    reference_samples = cross_phase_boundary.get('reference_samples')
    if not isinstance(reference_samples, dict):
        drift.append('cross_phase_scoreboard_boundary:reference_samples:missing')
        return drift
    if reference_samples.get('status') != 'out_of_scope':
        drift.append(f"cross_phase_scoreboard_boundary:reference_samples:status:{reference_samples.get('status')!r}!='out_of_scope'")
    require_list_members(drift, 'cross_phase_scoreboard_boundary:reference_samples', reference_samples.get('evidence'), REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE)
    runtime_starters = cross_phase_boundary.get('runtime_starters')
    if not isinstance(runtime_starters, dict):
        drift.append('cross_phase_scoreboard_boundary:runtime_starters:missing')
        return drift
    if runtime_starters.get('status') != 'out_of_scope':
        drift.append(f"cross_phase_scoreboard_boundary:runtime_starters:status:{runtime_starters.get('status')!r}!='out_of_scope'")
    require_list_members(drift, 'cross_phase_scoreboard_boundary:runtime_starters', runtime_starters.get('evidence'), REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE)
    require_mapping_list_members(drift, manifest, 'landed_core_helper_evidence', REQUIRED_LANDED_CORE_HELPER_EVIDENCE)
    require_mapping_list_members(drift, manifest, 'landed_ring_helper_evidence', REQUIRED_LANDED_RING_HELPER_EVIDENCE)
    require_mapping_list_members(drift, manifest, 'landed_input_helper_evidence', REQUIRED_LANDED_INPUT_HELPER_EVIDENCE)
    require_mapping_list_members(drift, manifest, 'landed_mmio_helper_evidence', REQUIRED_LANDED_MMIO_HELPER_EVIDENCE)
    require_mapping_list_members(drift, manifest, 'focused_harness_replays', REQUIRED_FOCUSED_HARNESS_REPLAYS)
    ready_transport_followups = manifest.get('ready_transport_followups')
    if not isinstance(ready_transport_followups, dict):
        drift.append('ready_transport_followups:missing')
        return drift
    input_followup = ready_transport_followups.get(REQUIRED_INPUT_READY_TRANSPORT_PATH)
    if input_followup != REQUIRED_INPUT_READY_TRANSPORT_GAP:
        drift.append(f'ready_transport_followups:{REQUIRED_INPUT_READY_TRANSPORT_PATH}:{input_followup!r}!={REQUIRED_INPUT_READY_TRANSPORT_GAP!r}')
    mmio_followup = ready_transport_followups.get(REQUIRED_MMIO_READY_TRANSPORT_PATH)
    if mmio_followup != REQUIRED_MMIO_READY_TRANSPORT_GAP:
        drift.append(f'ready_transport_followups:{REQUIRED_MMIO_READY_TRANSPORT_PATH}:{mmio_followup!r}!={REQUIRED_MMIO_READY_TRANSPORT_GAP!r}')
    blocked_transport_gaps = manifest.get('blocked_transport_gaps')
    if not isinstance(blocked_transport_gaps, dict):
        drift.append('blocked_transport_gaps:missing')
        return drift
    for path, expected in ((REQUIRED_CORE_BLOCKED_TRANSPORT_PATH, REQUIRED_CORE_BLOCKED_TRANSPORT_GAP), (REQUIRED_INPUT_READY_TRANSPORT_PATH, REQUIRED_INPUT_READY_TRANSPORT_GAP), (REQUIRED_MMIO_READY_TRANSPORT_PATH, REQUIRED_MMIO_READY_TRANSPORT_GAP)):
        actual = blocked_transport_gaps.get(path)
        if actual != expected:
            drift.append(f'blocked_transport_gaps:{path}:{actual!r}!={expected!r}')
    return drift

def validate(root: Path) -> tuple[list[str], list[str]]:
    tracked_paths = [MANIFEST_PATH, LEDGER_PATH]
    missing_files = [rel_path for rel_path in tracked_paths if not (root / rel_path).exists()]
    if missing_files:
        return (missing_files, [])
    manifest = read_json(root / MANIFEST_PATH)
    drift = collect_drift(manifest)
    drift.extend(collect_ledger_drift(manifest, (root / LEDGER_PATH).read_text(encoding='utf-8')))
    return ([], drift)

def fixture_manifest() -> dict:
    return {'doc_count': 7, 'manifest_count': 4, 'driver_count': 4, 'test_count': 30, 'docs': [f'doc-{index}' for index in range(7)], 'manifests': [f'manifest-{index}' for index in range(4)], 'drivers': [f'driver-{index}' for index in range(4)], 'tests': [f'test-{index}' for index in range(30)], 'exact_checks': REQUIRED_EXACT_CHECKS, 'roadmap_parity_scoreboard': {'virtqueue_wrappers': {'status': 'starter_landed', 'evidence': REQUIRED_RING_SCOREBOARD_EVIDENCE}, 'mmio_wrappers': {'status': 'starter_landed', 'evidence': REQUIRED_MMIO_SCOREBOARD_EVIDENCE}, 'lab_only_driver_validation': {'status': 'starter_landed', 'evidence': REQUIRED_LAB_VALIDATION_EVIDENCE + REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE + REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE + REQUIRED_CORE_LAB_VALIDATION_EVIDENCE}, 'dual_implementations_for_risky_areas': {'status': 'blocked_on_risky_transport', 'evidence': REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE}}, 'survey_provenance': {'source': REQUIRED_SURVEY_PROVENANCE_SOURCE, 'lane_keys': REQUIRED_SURVEY_LANE_KEYS, 'surveyed_commits': REQUIRED_SURVEY_COMMITS}, 'cross_phase_scoreboard_boundary': {'reference_samples': {'status': 'out_of_scope', 'evidence': REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE}, 'runtime_starters': {'status': 'out_of_scope', 'evidence': REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE}}, 'landed_core_helper_evidence': REQUIRED_LANDED_CORE_HELPER_EVIDENCE, 'landed_ring_helper_evidence': REQUIRED_LANDED_RING_HELPER_EVIDENCE, 'landed_input_helper_evidence': REQUIRED_LANDED_INPUT_HELPER_EVIDENCE, 'landed_mmio_helper_evidence': REQUIRED_LANDED_MMIO_HELPER_EVIDENCE, 'focused_harness_replays': REQUIRED_FOCUSED_HARNESS_REPLAYS, 'ready_transport_followups': {REQUIRED_INPUT_READY_TRANSPORT_PATH: REQUIRED_INPUT_READY_TRANSPORT_GAP, REQUIRED_MMIO_READY_TRANSPORT_PATH: REQUIRED_MMIO_READY_TRANSPORT_GAP}, 'blocked_transport_gaps': {REQUIRED_CORE_BLOCKED_TRANSPORT_PATH: REQUIRED_CORE_BLOCKED_TRANSPORT_GAP, REQUIRED_INPUT_READY_TRANSPORT_PATH: REQUIRED_INPUT_READY_TRANSPORT_GAP, REQUIRED_MMIO_READY_TRANSPORT_PATH: REQUIRED_MMIO_READY_TRANSPORT_GAP}}

def build_fixture_ledger(manifest: dict) -> str:
    lines = build_expected_ledger_lines(manifest)
    return '\n'.join((f'- `{line}`' for line in lines)) + '\n'

def write_fixture(root: Path) -> None:
    manifest = fixture_manifest()
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + '\n')
    write_text(root / LEDGER_PATH, build_fixture_ledger(manifest))

def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ','.join(items) if items else 'none'
        raise SystemExit(f'{label}:expected={expected}:actual={actual}')

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase10_manifest_counts_') as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        missing_files, drift = validate(root)
        if missing_files or drift:
            raise SystemExit(f"phase10-manifest-counts-self-test:baseline_failed:files={','.join(missing_files) or 'none'}:drift={','.join(drift) or 'none'}")
        manifest_path = root / MANIFEST_PATH
        ledger_path = root / LEDGER_PATH
        original = read_json(manifest_path)
        original_ledger = ledger_path.read_text(encoding='utf-8')
        def write_manifest(data: dict) -> None:
            write_text(manifest_path, json.dumps(data, indent=2) + '\n')
        def write_ledger(text: str) -> None:
            write_text(ledger_path, text)
        cases = 0
        broken = copy.deepcopy(original)
        broken['doc_count'] = 6
        write_manifest(broken)
        expect_contains(validate(root)[1], 'doc_count:6!=len(docs):7', 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['test_count'] = 29
        write_manifest(broken)
        expect_contains(validate(root)[1], 'test_count:29!=len(tests):30', 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['exact_checks'] = [item for item in broken['exact_checks'] if item != 'python3 scripts/zigux/check-phase10-ring-packet.py']
        write_manifest(broken)
        expect_contains(validate(root)[1], "exact_checks:'python3 scripts/zigux/check-phase10-ring-packet.py':missing", 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        reordered = list(REQUIRED_EXACT_CHECKS)
        reordered[-1], reordered[-2] = (reordered[-2], reordered[-1])
        broken['exact_checks'] = reordered
        write_manifest(broken)
        expect_contains(validate(root)[1], 'exact_checks:closure_route:out_of_order', 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['roadmap_parity_scoreboard']['virtqueue_wrappers']['evidence'] = [item for item in broken['roadmap_parity_scoreboard']['virtqueue_wrappers']['evidence'] if item != 'drivers/virtio/virtio_ring_publish_readiness.zig']
        write_manifest(broken)
        expect_contains(validate(root)[1], "roadmap_parity_scoreboard:virtqueue_wrappers:'drivers/virtio/virtio_ring_publish_readiness.zig':missing", 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['roadmap_parity_scoreboard']['lab_only_driver_validation']['evidence'] = [item for item in broken['roadmap_parity_scoreboard']['lab_only_driver_validation']['evidence'] if item != 'zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig']
        write_manifest(broken)
        expect_contains(validate(root)[1], "roadmap_parity_scoreboard:lab_only_driver_validation:'zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig':missing", 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['roadmap_parity_scoreboard']['lab_only_driver_validation']['evidence'] = [item for item in broken['roadmap_parity_scoreboard']['lab_only_driver_validation']['evidence'] if item != 'drivers/virtio/virtio_driver_id.zig']
        write_manifest(broken)
        expect_contains(validate(root)[1], "roadmap_parity_scoreboard:lab_only_driver_validation:'drivers/virtio/virtio_driver_id.zig':missing", 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['landed_ring_helper_evidence']['zigux/tests/phase10_virtio_ring_manifest.json'] = [item for item in broken['landed_ring_helper_evidence']['zigux/tests/phase10_virtio_ring_manifest.json'] if item != 'phase10-queue-publish-readiness-helper']
        write_manifest(broken)
        expect_contains(validate(root)[1], "landed_ring_helper_evidence:zigux/tests/phase10_virtio_ring_manifest.json:'phase10-queue-publish-readiness-helper':missing", 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['focused_harness_replays']['zigux/tests/phase10_virtio_ring_queue_build.zig'] = []
        write_manifest(broken)
        expect_contains(validate(root)[1], 'focused_harness_replays:zigux/tests/phase10_virtio_ring_queue_build.zig:missing', 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['focused_harness_replays']['zigux/tests/phase10_virtio_ring_queue_build_survey.zig'] = []
        write_manifest(broken)
        expect_contains(validate(root)[1], 'focused_harness_replays:zigux/tests/phase10_virtio_ring_queue_build_survey.zig:missing', 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        broken = copy.deepcopy(original)
        broken['ready_transport_followups'][REQUIRED_MMIO_READY_TRANSPORT_PATH] = 'phase10-mmio-lifecycle-and-irq-paths-missing'
        write_manifest(broken)
        expect_contains(validate(root)[1], "ready_transport_followups:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-lifecycle-and-irq-paths-missing'!='phase10-mmio-lifecycle-and-irq-paths'", 'phase10-manifest-counts-self-test')
        cases += 1
        write_fixture(root)
        write_ledger(original_ledger.replace('PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8', 'PHASE10_LEDGER_SURVEY_MMIO_COMMIT=deadbeef', 1))
        expect_contains(validate(root)[1], 'ledger:PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8', 'phase10-manifest-counts-self-test')
        cases += 1
    print('PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST_CASE_COUNT={cases}')
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the Phase 10 closure manifest summary-count packet.')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    missing_files, drift = validate(args.repo_root)
    if missing_files:
        print('PHASE10_CLOSURE_MANIFEST_COUNTS=fail')
        print('MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_START')
        for item in missing_files:
            print(item)
        print('MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_END')
        return 1
    if drift:
        print('PHASE10_CLOSURE_MANIFEST_COUNTS=fail')
        print('PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_START')
        for item in drift:
            print(item)
        print('PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_END')
        return 1
    print('PHASE10_CLOSURE_MANIFEST_COUNTS=pass')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_FIELD_COUNT={len(COUNT_FIELDS)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_EXACT_CHECK_COUNT={len(REQUIRED_EXACT_CHECKS)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_RING_EVIDENCE_COUNT={len(REQUIRED_RING_SCOREBOARD_EVIDENCE)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_MMIO_EVIDENCE_COUNT={len(REQUIRED_MMIO_SCOREBOARD_EVIDENCE)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LAB_VALIDATION_EVIDENCE_COUNT={len(REQUIRED_LAB_VALIDATION_EVIDENCE) + len(REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE) + len(REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE) + len(REQUIRED_CORE_LAB_VALIDATION_EVIDENCE)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_REFERENCE_SAMPLE_EVIDENCE_COUNT={len(REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_RUNTIME_STARTER_EVIDENCE_COUNT={len(REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_CORE_HELPER_COUNT={sum((len(labels) for labels in REQUIRED_LANDED_CORE_HELPER_EVIDENCE.values()))}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_RING_HELPER_COUNT={sum((len(labels) for labels in REQUIRED_LANDED_RING_HELPER_EVIDENCE.values()))}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_INPUT_HELPER_COUNT={sum((len(labels) for labels in REQUIRED_LANDED_INPUT_HELPER_EVIDENCE.values()))}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_MMIO_HELPER_COUNT={sum((len(labels) for labels in REQUIRED_LANDED_MMIO_HELPER_EVIDENCE.values()))}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_FOCUSED_HARNESS_REPLAY_COUNT={len(REQUIRED_FOCUSED_HARNESS_REPLAYS)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_DUAL_IMPLEMENTATION_EVIDENCE_COUNT={len(REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE)}')
    print(f'PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LEDGER_LINE_COUNT={len(build_expected_ledger_lines(read_json(args.repo_root / MANIFEST_PATH)))}')
    return 0
if __name__ == '__main__':
    sys.exit(main())

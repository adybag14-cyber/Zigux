#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

SURVEYED_COMMIT = "7361ac51374149a96b7a7a2c6ea3c995d8cc1231"

FILES = [
    "scripts/zigux/check-phase10-input-packet.py",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_build.zig",
]

SURVEY_MARKERS = [
    "PHASE10_STATUS=parked",
    "PHASE10_SLICE=virtio-input-survey",
    "PHASE10_LANE_KEY=P10-L13",
    "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport",
    SURVEYED_COMMIT,
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-status-drain-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-lifecycle",
]

SLICE_MARKERS = [
    "# Phase 10 Virtio Input Slice",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "scripts/zigux/check-phase10-input-packet.py",
]

MODULE_MARKERS = [
    "# Phase 10 Virtio Input Module Slice",
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "the bounded status-drain helper",
    "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
]

LANE_NOTE_MARKERS = [
    "input lane `P10-L13` currently owns the direct input packet",
    "`Documentation/zigux/phase10-virtio-input-survey.md`",
    "`drivers/virtio/virtio_input.zig`",
    "`drivers/virtio/virtio_input_probe_preflight.zig`",
    "`drivers/virtio/virtio_input_verify.zig`",
    "`scripts/zigux/check-phase10-input-packet.py`",
    "`zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_registration_preflight.zig`",
    "`zigux/tests/phase10_virtio_input_status_drain.zig`",
    "`zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "`zigux/tests/phase10_virtio_input_survey.zig`",
    "`Documentation/zigux/phase10-virtio-input-slice.md`",
    "`Documentation/zigux/phase10-virtio-input-module-slice.md`",
    "`P10-L15`",
]

INPUT_HELPER_MARKERS = [
    "pub const QueueCallbackPreflightSummary = struct {",
    "pub const RegistrationPreflightSummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub const TeardownObservationSummary = struct {",
    "pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
    "pub fn registrationPreflightSummary(self: *const Self) RegistrationPreflightSummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
    "pub fn teardownObservationSummary(self: *const Self) TeardownObservationSummary {",
    "pub fn drainStatusQueue(self: *Self, completed_count: usize) !StatusDrainSummary {",
    "pub fn planMultitouchSlots(self: *Self) !MultitouchSlotPlanSummary {",
]

PROBE_HELPER_MARKERS = [
    "pub const ProbePreflightSummary = struct {",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {",
    ".queue_plan_incomplete",
    ".multitouch_slots_unplanned",
]

VERIFY_MARKERS = [
    'test "virtio input wrapper-facing identity review keeps config snapshots anchored to the lab helper" {',
    'test "virtio input wrapper-facing queue review keeps queue plan readiness local to the helper packet" {',
    'test "virtio input wrapper-facing status review keeps suppressed multitouch timestamps explicit" {',
]

TEST_MARKERS = {
    "zigux/tests/phase10_virtio_input.zig": [
        'test "phase10 virtio input probe preflight keeps identity and capability staging ahead of registration claims" {',
        'test "phase10 virtio input reset clears queue plan and returns to default bus identity" {',
    ],
    "zigux/tests/phase10_virtio_input_probe_preflight.zig": [
        'test "phase10 virtio input probe preflight keeps identity visible before queue setup" {',
    ],
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig": [
        'test "phase10 virtio input queue callback preflight reports blockers before callback handoff" {',
        'test "phase10 virtio input queue callback preflight stays ready across bounded refill bookkeeping" {',
    ],
    "zigux/tests/phase10_virtio_input_registration_preflight.zig": [
        'test "phase10 virtio input registration preflight reports blockers before readiness" {',
    ],
    "zigux/tests/phase10_virtio_input_status_drain.zig": [
        'test "phase10 virtio input drains queued status completions without touching suppressed multitouch counters" {',
        'test "phase10 virtio input zero-completion status drain keeps pending and suppressed counters stable" {',
    ],
    "zigux/tests/phase10_virtio_input_teardown_observation.zig": [
        'test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {',
    ],
    "zigux/tests/phase10_virtio_input_survey.zig": [
        'test "phase10 virtio input survey note keeps the restored verifier and queue callback packet explicit" {',
        'test "phase10 virtio input manifest keeps the restored replay ids and blocked lifecycle posture explicit" {',
    ],
}

BUILD_MARKERS = [
    "phase10_virtio_input_module",
    "phase10_virtio_input_probe_preflight_module",
    "phase10_virtio_input_status_drain_module",
    "phase10_virtio_input_queue_callback_preflight_module",
    "phase10_virtio_input_registration_preflight_module",
    "phase10_virtio_input_teardown_observation_module",
    "phase10_virtio_input_verify_module",
    "phase10_virtio_input_survey_module",
    '"phase10-virtio-input-tests"',
    '"phase10-virtio-input-probe-preflight-tests"',
    '"phase10-virtio-input-queue-callback-preflight-tests"',
    '"phase10-virtio-input-registration-preflight-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-teardown-observation-tests"',
    '"phase10-virtio-input-verify-tests"',
    '"phase10-virtio-input-survey-tests"',
]

MANIFEST_SCALARS = {
    "lane_key": "P10-L13",
    "phase": "Phase 10",
    "surveyed_commit": SURVEYED_COMMIT,
    "anchor": "drivers/virtio/virtio_input.c",
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}

EXPECTED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]

EXPECTED_ALLOWED_EVIDENCE_KINDS = [
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
]

EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS = [
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]

EXPECTED_SUMMARY = {
    "virtio_input_c_lines": 421,
    "preexisting_phase10_test_files": 6,
    "preexisting_phase10_build_present": True,
    "preexisting_virtio_core_zig_present": True,
    "preexisting_virtio_ring_zig_present": True,
    "preexisting_virtio_mmio_survey_present": True,
    "preexisting_virtio_input_zig_present": True,
    "preexisting_virtio_input_test_present": True,
    "preexisting_virtio_input_slice_note_present": True,
    "preexisting_virtio_input_module_note_present": True,
}

REQUIRED_GAPS = {
    "phase10-build-gate": ("starter_landed", "zigux/tests/phase10_build.zig"),
    "phase10-virtio-core-lab-starter": ("starter_landed", "drivers/virtio/virtio.zig"),
    "phase10-virtio-ring-lab-helper": ("starter_landed", "drivers/virtio/virtio_ring.zig"),
    "phase10-virtio-input-lab-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-lab-gate": ("starter_landed", "zigux/tests/phase10_virtio_input.zig"),
    "phase10-virtio-input-verify-replay": ("starter_landed", "drivers/virtio/virtio_input_verify.zig"),
    "phase10-virtio-input-probe-preflight-replay": ("starter_landed", "zigux/tests/phase10_virtio_input_probe_preflight.zig"),
    "phase10-virtio-input-queue-callback-preflight-replay": ("starter_landed", "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig"),
    "phase10-virtio-input-registration-preflight-replay": ("starter_landed", "zigux/tests/phase10_virtio_input_registration_preflight.zig"),
    "phase10-virtio-input-teardown-observation-replay": ("starter_landed", "zigux/tests/phase10_virtio_input_teardown_observation.zig"),
    "phase10-virtio-input-slice-note": ("starter_landed", "Documentation/zigux/phase10-virtio-input-slice.md"),
    "phase10-virtio-input-module-note": ("starter_landed", "Documentation/zigux/phase10-virtio-input-module-slice.md"),
    "phase10-virtio-input-survey-gate": ("starter_landed", "zigux/tests/phase10_virtio_input_survey.zig"),
    "phase10-virtio-input-survey-note": ("starter_landed", "Documentation/zigux/phase10-virtio-input-survey.md"),
    "phase10-virtio-input-capability-setup-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-multitouch-slot-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-probe-preflight-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-registration-preflight-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-queue-callback-preflight-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-status-drain-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-teardown-observation-helper": ("starter_landed", "drivers/virtio/virtio_input.zig"),
    "phase10-virtio-input-wrapper-ownership-note": ("starter_landed", "Documentation/zigux/phase10-virtio-input-survey.md"),
    "phase10-virtio-input-registration-lifecycle": ("blocked_on_risky_transport", "zigux/tests/phase10_virtio_input.zig"),
}

EXPECTED_GAP_KINDS = {
    "phase10-build-gate": "validation",
    "phase10-virtio-core-lab-starter": "reviewability",
    "phase10-virtio-ring-lab-helper": "reviewability",
    "phase10-virtio-input-lab-helper": "reviewability",
    "phase10-virtio-input-lab-gate": "validation",
    "phase10-virtio-input-verify-replay": "validation",
    "phase10-virtio-input-probe-preflight-replay": "validation",
    "phase10-virtio-input-queue-callback-preflight-replay": "validation",
    "phase10-virtio-input-registration-preflight-replay": "validation",
    "phase10-virtio-input-teardown-observation-replay": "validation",
    "phase10-virtio-input-slice-note": "documentation",
    "phase10-virtio-input-module-note": "documentation",
    "phase10-virtio-input-survey-gate": "validation",
    "phase10-virtio-input-survey-note": "documentation",
    "phase10-virtio-input-capability-setup-helper": "reviewability",
    "phase10-virtio-input-multitouch-slot-helper": "reviewability",
    "phase10-virtio-input-probe-preflight-helper": "reviewability",
    "phase10-virtio-input-registration-preflight-helper": "reviewability",
    "phase10-virtio-input-queue-callback-preflight-helper": "reviewability",
    "phase10-virtio-input-status-drain-helper": "reviewability",
    "phase10-virtio-input-teardown-observation-helper": "reviewability",
    "phase10-virtio-input-wrapper-ownership-note": "documentation",
    "phase10-virtio-input-registration-lifecycle": "validation",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads(read_text(root, "zigux/tests/phase10_virtio_input_manifest.json"))


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []

    check_markers(missing, "survey", read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md"), SURVEY_MARKERS)
    check_markers(missing, "slice", read_text(root, "Documentation/zigux/phase10-virtio-input-slice.md"), SLICE_MARKERS)
    check_markers(missing, "module", read_text(root, "Documentation/zigux/phase10-virtio-input-module-slice.md"), MODULE_MARKERS)
    check_markers(missing, "lane_note", read_text(root, "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"), LANE_NOTE_MARKERS)
    check_markers(missing, "input_helper", read_text(root, "drivers/virtio/virtio_input.zig"), INPUT_HELPER_MARKERS)
    check_markers(missing, "probe_helper", read_text(root, "drivers/virtio/virtio_input_probe_preflight.zig"), PROBE_HELPER_MARKERS)
    check_markers(missing, "verify", read_text(root, "drivers/virtio/virtio_input_verify.zig"), VERIFY_MARKERS)
    check_markers(missing, "build", read_text(root, "zigux/tests/phase10_build.zig"), BUILD_MARKERS)

    for rel_path, markers in TEST_MARKERS.items():
        check_markers(missing, Path(rel_path).name, read_text(root, rel_path), markers)

    manifest = load_manifest(root)
    for key, expected in MANIFEST_SCALARS.items():
        if manifest.get(key) != expected:
            missing.append(f"manifest:{key}={manifest.get(key)!r}")

    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing.append("manifest:roadmap_destinations")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing.append("manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing.append("manifest:forbidden_transport_claims")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("manifest:survey_summary")
    else:
        for key, expected in EXPECTED_SUMMARY.items():
            if summary.get(key) != expected:
                missing.append(f"manifest:survey_summary:{key}={summary.get(key)!r}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps")
    else:
        if len(gaps) != len(REQUIRED_GAPS):
            missing.append(f"manifest:gap_count={len(gaps)}")
        gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
        for gap_id, (status, destination) in REQUIRED_GAPS.items():
            gap = gap_index.get(gap_id)
            if gap is None:
                missing.append(f"manifest:gap:{gap_id}")
                continue
            if gap.get("status") != status:
                missing.append(f"manifest:gap_status:{gap_id}={gap.get('status')!r}")
            expected_kind = EXPECTED_GAP_KINDS[gap_id]
            if gap.get("kind") != expected_kind:
                missing.append(f"manifest:gap_kind:{gap_id}={gap.get('kind')!r}")
            if gap.get("zigux_destination") != destination:
                missing.append(f"manifest:gap_destination:{gap_id}={gap.get('zigux_destination')!r}")

    return [], missing


def write_fixture(root: Path) -> None:
    contents = {
        "scripts/zigux/check-phase10-input-packet.py": "# fixture checker\n",
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-slice.md": "\n".join(SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-module-slice.md": "\n".join(MODULE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_NOTE_MARKERS) + "\n",
        "drivers/virtio/virtio_input.zig": "\n".join(INPUT_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_probe_preflight.zig": "\n".join(PROBE_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_verify.zig": "\n".join(VERIFY_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input.zig"]) + "\n",
        "zigux/tests/phase10_virtio_input_probe_preflight.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input_probe_preflight.zig"]) + "\n",
        "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input_queue_callback_preflight.zig"]) + "\n",
        "zigux/tests/phase10_virtio_input_registration_preflight.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input_registration_preflight.zig"]) + "\n",
        "zigux/tests/phase10_virtio_input_status_drain.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input_status_drain.zig"]) + "\n",
        "zigux/tests/phase10_virtio_input_teardown_observation.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input_teardown_observation.zig"]) + "\n",
        "zigux/tests/phase10_virtio_input_survey.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input_survey.zig"]) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_manifest.json": json.dumps(
            {
                **MANIFEST_SCALARS,
                "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
                "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
                "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
                "survey_summary": EXPECTED_SUMMARY,
                "gaps": [
                    {
                        "id": gap_id,
                        "status": status,
                        "kind": EXPECTED_GAP_KINDS[gap_id],
                        "zigux_destination": destination,
                    }
                    for gap_id, (status, destination) in REQUIRED_GAPS.items()
                ],
            },
            indent=2,
        )
        + "\n",
    }
    for rel_path, content in contents.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def expect_missing_file(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"{label}:unexpected_missing_markers:{','.join(missing_markers)}")
    if expected not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_input_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-input-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        case_count = 0

        survey_path = root / "Documentation/zigux/phase10-virtio-input-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(original_survey.replace("PHASE10_LANE_KEY=P10-L13", "PHASE10_LANE_KEY=P10-L22", 1), encoding="utf-8")
        expect_missing_marker(root, "survey:PHASE10_LANE_KEY=P10-L13", "phase10-input-self-test:survey_lane_key")
        survey_path.write_text(original_survey, encoding="utf-8")
        case_count += 1

        lane_note_path = root / "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"
        original_lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            original_lane_note.replace("`scripts/zigux/check-phase10-input-packet.py`", "`scripts/zigux/check-phase10-input-packet-missing.py`", 1),
            encoding="utf-8",
        )
        expect_missing_marker(root, "lane_note:`scripts/zigux/check-phase10-input-packet.py`", "phase10-input-self-test:lane_note_checker")
        lane_note_path.write_text(original_lane_note, encoding="utf-8")
        case_count += 1

        slice_path = root / "Documentation/zigux/phase10-virtio-input-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("scripts/zigux/check-phase10-input-packet.py", "scripts/zigux/check-phase10-input-packet-drift.py", 1),
            encoding="utf-8",
        )
        expect_missing_marker(root, "slice:scripts/zigux/check-phase10-input-packet.py", "phase10-input-self-test:slice_checker")
        slice_path.write_text(original_slice, encoding="utf-8")
        case_count += 1

        module_path = root / "Documentation/zigux/phase10-virtio-input-module-slice.md"
        original_module = module_path.read_text(encoding="utf-8")
        module_path.write_text(
            original_module.replace("the bounded status-drain helper", "the missing status-drain helper", 1),
            encoding="utf-8",
        )
        expect_missing_marker(root, "module:the bounded status-drain helper", "phase10-input-self-test:module_status_drain")
        module_path.write_text(original_module, encoding="utf-8")
        case_count += 1

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace('\"phase10-virtio-input-verify-tests\"', '\"phase10-virtio-input-verify-drift\"', 1),
            encoding="utf-8",
        )
        expect_missing_marker(root, 'build:"phase10-virtio-input-verify-tests"', "phase10-input-self-test:build_verify")
        build_path.write_text(original_build, encoding="utf-8")
        case_count += 1

        helper_path = root / "drivers/virtio/virtio_input.zig"
        original_helper = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(
            original_helper.replace(
                "pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
                "pub fn queueCallbackPreflightStatus(self: *const Self) QueueCallbackPreflightSummary {",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "input_helper:pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
            "phase10-input-self-test:helper_queue_callback",
        )
        helper_path.write_text(original_helper, encoding="utf-8")
        case_count += 1

        verify_path = root / "drivers/virtio/virtio_input_verify.zig"
        original_verify = verify_path.read_text(encoding="utf-8")
        verify_path.write_text(
            original_verify.replace(
                'test "virtio input wrapper-facing queue review keeps queue plan readiness local to the helper packet" {',
                'test "virtio input wrapper-facing queue review drift" {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'verify:test "virtio input wrapper-facing queue review keeps queue plan readiness local to the helper packet" {',
            "phase10-input-self-test:verify_queue_review",
        )
        verify_path.write_text(original_verify, encoding="utf-8")
        case_count += 1

        manifest_path = root / "zigux/tests/phase10_virtio_input_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P10-L22"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(root, "manifest:lane_key='P10-L22'", "phase10-input-self-test:manifest_lane_key")
        write_fixture(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["preexisting_virtio_input_module_note_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:survey_summary:preexisting_virtio_input_module_note_present=False",
            "phase10-input-self-test:manifest_summary_flag",
        )
        write_fixture(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-module-note":
                gap["zigux_destination"] = "Documentation/zigux/phase10-virtio-input-survey.md"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:gap_destination:phase10-virtio-input-module-note='Documentation/zigux/phase10-virtio-input-survey.md'",
            "phase10-input-self-test:manifest_gap_destination",
        )
        write_fixture(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-registration-lifecycle":
                gap["status"] = "starter_landed"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:gap_status:phase10-virtio-input-registration-lifecycle='starter_landed'",
            "phase10-input-self-test:manifest_gap_status",
        )
        write_fixture(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase10-virtio-input-wrapper-ownership-note":
                gap["kind"] = "validation"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            root,
            "manifest:gap_kind:phase10-virtio-input-wrapper-ownership-note='validation'",
            "phase10-input-self-test:manifest_gap_kind",
        )
        write_fixture(root)
        case_count += 1

        survey_gate_path = root / "zigux/tests/phase10_virtio_input_survey.zig"
        original_survey_gate = survey_gate_path.read_text(encoding="utf-8")
        survey_gate_path.write_text(
            original_survey_gate.replace(
                'test "phase10 virtio input manifest keeps the restored replay ids and blocked lifecycle posture explicit" {',
                'test "phase10 virtio input manifest drift" {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'phase10_virtio_input_survey.zig:test "phase10 virtio input manifest keeps the restored replay ids and blocked lifecycle posture explicit" {',
            "phase10-input-self-test:survey_gate",
        )
        survey_gate_path.write_text(original_survey_gate, encoding="utf-8")
        case_count += 1

        status_drain_path = root / "zigux/tests/phase10_virtio_input_status_drain.zig"
        original_status_drain = status_drain_path.read_text(encoding="utf-8")
        status_drain_path.write_text(
            original_status_drain.replace(
                'test "phase10 virtio input zero-completion status drain keeps pending and suppressed counters stable" {',
                'test "phase10 virtio input zero-completion drift" {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'phase10_virtio_input_status_drain.zig:test "phase10 virtio input zero-completion status drain keeps pending and suppressed counters stable" {',
            "phase10-input-self-test:status_drain_zero_completion",
        )
        status_drain_path.write_text(original_status_drain, encoding="utf-8")
        case_count += 1

        (root / "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig").unlink()
        expect_missing_file(
            root,
            "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
            "phase10-input-self-test:missing_queue_callback_test_file",
        )
        write_fixture(root)
        case_count += 1

        (root / "scripts/zigux/check-phase10-input-packet.py").unlink()
        expect_missing_file(
            root,
            "scripts/zigux/check-phase10-input-packet.py",
            "phase10-input-self-test:missing_checker_file",
        )
        case_count += 1

    print("PHASE10_INPUT_PACKET_SELF_TEST=pass")
    print(f"PHASE10_INPUT_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio input packet.")
    parser.add_argument("--self-test", action="store_true", help="run the checker's built-in synthetic drift tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_INPUT_PACKET=fail")
        print("MISSING_PHASE10_INPUT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_INPUT_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_INPUT_PACKET=fail")
        print("MISSING_PHASE10_INPUT_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_INPUT_MARKERS_END")
        return 1

    print("PHASE10_INPUT_PACKET=pass")
    print(f"PHASE10_INPUT_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE10_INPUT_REQUIRED_MARKER_COUNT="
        f"{len(SURVEY_MARKERS) + len(SLICE_MARKERS) + len(MODULE_MARKERS) + len(LANE_NOTE_MARKERS) + len(INPUT_HELPER_MARKERS) + len(PROBE_HELPER_MARKERS) + len(VERIFY_MARKERS) + len(BUILD_MARKERS) + sum(len(markers) for markers in TEST_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

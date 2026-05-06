#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_input_module",
    "phase10_virtio_input_status_drain_module",
    "phase10_virtio_input_verify_module",
    "phase10_virtio_input_survey_module",
    '"phase10-virtio-input-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-verify-tests"',
    '"phase10-virtio-input-survey-tests"',
]

EXPECTED_SCRIPTS_README_MARKERS = [
    "check-phase10-input-packet.py",
    "phase10_virtio_core_reset_queue.zig",
    "phase10_virtio_input_status_drain.zig",
    "make -C zigux phase10",
]

EXPECTED_TESTS_README_MARKERS = [
    "phase10_virtio_input.zig",
    "phase10_virtio_input_status_drain.zig",
    "phase10_virtio_input_survey.zig",
]

EXPECTED_MAKEFILE_MARKERS = [
    "phase10-test:",
    "scripts/zigux/check-phase10-input-packet.py --self-test",
    "scripts/zigux/check-phase10-input-packet.py",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig",
]

EXPECTED_HELPER_MARKERS = [
    "pub const RegistrationPreflightSummary = struct {",
    "pub const StatusDrainSummary = struct {",
    "pub fn registrationPreflightSummary(self: *const Self) RegistrationPreflightSummary {",
    "pub fn drainStatusQueue(self: *Self, completed_status_count: usize) !StatusDrainSummary {",
]

EXPECTED_VERIFY_MARKERS = [
    'test "virtio input wrapper-facing queue preflight advances in bounded order" {',
    'test "virtio input registration preflight keeps wrapper prerequisites ahead of registration claims" {',
    'try std.testing.expectEqualStrings("event_buffers_unfilled", @tagName(summary.blocker.?));',
    'try std.testing.expectEqualStrings("multitouch_slots_unplanned", @tagName(summary.blocker.?));',
]

EXPECTED_TEST_MARKERS = [
    'test "phase10 virtio input registration preflight reports blockers before readiness" {',
    'test "phase10 virtio input reset clears queue plan and returns to default bus identity" {',
    "RegistrationBlocker.multitouch_slots_unplanned",
    "RegistrationBlocker.event_queue_unconfigured",
]

EXPECTED_STATUS_DRAIN_MARKERS = [
    'test "phase10 virtio input drains queued status completions without touching suppressed multitouch counters" {',
    "suppressed_status_count",
    "StatusCompletionCountExceedsQueued",
]

EXPECTED_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio input survey manifest records the live starter and remaining gap" {',
    'try std.testing.expectEqualStrings("P10-L13", manifest.lane_key);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "lab-only driver validation") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "wrapper ownership stays with the already-landed shared Phase 10 packets") != null);',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-survey-note")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-queue-callback-preflight-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-virtio-input-wrapper-ownership-note")) {',
    'try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lab-only driver validation evidence") != null);',
    'try std.testing.expectEqual(@as(usize, 6), manifest.survey_summary.preexisting_phase10_test_files);',
    '"phase10-virtio-input-status-drain-helper"',
    'try std.testing.expect(saw_queue_callback_preflight_helper);',
    'try std.testing.expect(starter_landed_count >= 14);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
]

EXPECTED_SLICE_MARKERS = [
    "wrapper-facing `drivers/virtio/virtio_input_verify.zig` replay",
    "drivers/virtio/virtio_input_verify.zig",
    "bounded status-completion drain summaries",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "transport-backed probe, remove, freeze, restore, or reset paths",
]

EXPECTED_MODULE_MARKERS = [
    "drivers/virtio/virtio_input_verify.zig",
    "bounded status-drain helper",
    "reclaims queued status completions in memory",
    "queue callbacks",
]

EXPECTED_SURVEY_NOTE_MARKERS = [
    "PHASE10_STATUS=parked",
    "PHASE10_LANE_KEY=P10-L13",
    "drivers/virtio/virtio_input_verify.zig",
    "wrapper-facing verify replay",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-status-drain-helper",
    "phase10-virtio-input-wrapper-ownership-note",
    "queue-callback preflight summary",
    "wrapper ownership stays with the already-landed shared Phase 10 packets",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_mmio.zig",
    "phase10-virtio-input-registration-lifecycle",
    "real event delivery",
    "transport-backed status completion callbacks",
    "lab-only driver validation",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-input-lab-helper": "starter_landed",
    "phase10-virtio-input-lab-gate": "starter_landed",
    "phase10-virtio-input-survey-gate": "starter_landed",
    "phase10-virtio-input-capability-setup-helper": "starter_landed",
    "phase10-virtio-input-multitouch-slot-helper": "starter_landed",
    "phase10-virtio-input-registration-preflight-helper": "starter_landed",
    "phase10-virtio-input-queue-callback-preflight-helper": "starter_landed",
    "phase10-virtio-input-status-drain-helper": "starter_landed",
    "phase10-virtio-input-wrapper-ownership-note": "starter_landed",
    "phase10-virtio-input-registration-lifecycle": "blocked_on_risky_transport",
}

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


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    build_text = read_text(root, "zigux/tests/phase10_build.zig")
    for marker in EXPECTED_BUILD_MARKERS:
        if marker not in build_text:
            missing_markers.append(f"build:{marker}")

    scripts_readme_text = read_text(root, "scripts/zigux/README.md")
    for marker in EXPECTED_SCRIPTS_README_MARKERS:
        if marker not in scripts_readme_text:
            missing_markers.append(f"scripts_readme:{marker}")

    tests_readme_text = read_text(root, "zigux/tests/README.md")
    for marker in EXPECTED_TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            missing_markers.append(f"tests_readme:{marker}")

    makefile_text = read_text(root, "zigux/Makefile")
    for marker in EXPECTED_MAKEFILE_MARKERS:
        if marker not in makefile_text:
            missing_markers.append(f"makefile:{marker}")

    helper_text = read_text(root, "drivers/virtio/virtio_input.zig")
    for marker in EXPECTED_HELPER_MARKERS:
        if marker not in helper_text:
            missing_markers.append(f"helper:{marker}")

    verify_text = read_text(root, "drivers/virtio/virtio_input_verify.zig")
    for marker in EXPECTED_VERIFY_MARKERS:
        if marker not in verify_text:
            missing_markers.append(f"verify:{marker}")

    test_text = read_text(root, "zigux/tests/phase10_virtio_input.zig")
    for marker in EXPECTED_TEST_MARKERS:
        if marker not in test_text:
            missing_markers.append(f"tests:{marker}")

    status_drain_text = read_text(root, "zigux/tests/phase10_virtio_input_status_drain.zig")
    for marker in EXPECTED_STATUS_DRAIN_MARKERS:
        if marker not in status_drain_text:
            missing_markers.append(f"status_drain:{marker}")

    survey_test_text = read_text(root, "zigux/tests/phase10_virtio_input_survey.zig")
    for marker in EXPECTED_SURVEY_TEST_MARKERS:
        if marker not in survey_test_text:
            missing_markers.append(f"survey_test:{marker}")

    slice_text = read_text(root, "Documentation/zigux/phase10-virtio-input-slice.md")
    for marker in EXPECTED_SLICE_MARKERS:
        if marker not in slice_text:
            missing_markers.append(f"slice:{marker}")

    module_text = read_text(root, "Documentation/zigux/phase10-virtio-input-module-slice.md")
    for marker in EXPECTED_MODULE_MARKERS:
        if marker not in module_text:
            missing_markers.append(f"module:{marker}")

    survey_note_text = read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md")
    for marker in EXPECTED_SURVEY_NOTE_MARKERS:
        if marker not in survey_note_text:
            missing_markers.append(f"survey_note:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_input_manifest.json"))
    if manifest.get("lane_key") != "P10-L13":
        missing_markers.append("manifest:lane_key=P10-L13")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_input.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio_input.c")
    if manifest.get("surveyed_commit") != "7361ac51374149a96b7a7a2c6ea3c995d8cc1231":
        missing_markers.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]:
        missing_markers.append("manifest:roadmap_destinations")
    if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
        missing_markers.append("manifest:freeze_map")
    if manifest.get("freeze_boundary_status") != "aligned":
        missing_markers.append("manifest:freeze_boundary_status=aligned")
    if manifest.get("freeze_status_change_claimed") is not False:
        missing_markers.append("manifest:freeze_status_change_claimed=false")
    if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing_markers.append("manifest:risky_transport_posture=blocked_on_risky_transport")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing_markers.append("manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing_markers.append("manifest:forbidden_transport_claims")
    if manifest.get("architecture_council_reopen_required") is not True:
        missing_markers.append("manifest:architecture_council_reopen_required=true")
    if manifest.get("architecture_council_reopen_attached") is not False:
        missing_markers.append("manifest:architecture_council_reopen_attached=false")

    summary = manifest.get("survey_summary", {})
    if summary.get("preexisting_phase10_test_files") != 6:
        missing_markers.append("manifest:preexisting_phase10_test_files=6")
    for key in [
        "preexisting_phase10_build_present",
        "preexisting_virtio_core_zig_present",
        "preexisting_virtio_ring_zig_present",
        "preexisting_virtio_mmio_survey_present",
        "preexisting_virtio_input_zig_present",
        "preexisting_virtio_input_test_present",
        "preexisting_virtio_input_slice_note_present",
        "preexisting_virtio_input_module_note_present",
    ]:
        if summary.get(key) is not True:
            missing_markers.append(f"manifest:{key}")

    gaps = manifest.get("gaps", [])
    if len(gaps) < 14:
        missing_markers.append("manifest:gaps")
    gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

    return missing_files, missing_markers


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    fixture = {
        rel_path: read_text(ROOT, rel_path)
        for rel_path in FILES
        if rel_path != "scripts/zigux/check-phase10-input-packet.py"
    }
    fixture["scripts/zigux/check-phase10-input-packet.py"] = read_text(ROOT, "scripts/zigux/check-phase10-input-packet.py")

    with tempfile.TemporaryDirectory(prefix="zigux_phase10_input_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for rel_path, content in fixture.items():
            write_fixture(tmp_root, rel_path, content)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-input-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        manifest_path = tmp_root / "zigux/tests/phase10_virtio_input_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace('"lane_key": "P10-L13"', '"lane_key": "P10-drift"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:lane_key=P10-L13" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_lane_key_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace('"freeze_boundary_status": "aligned"', '"freeze_boundary_status": "drifted"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:freeze_boundary_status=aligned" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_freeze_boundary_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                '"risky_transport_posture": "blocked_on_risky_transport"',
                '"risky_transport_posture": "ready_next"',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:risky_transport_posture=blocked_on_risky_transport" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_transport_posture_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace('"freeze_status_change_claimed": false', '"freeze_status_change_claimed": true', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:freeze_status_change_claimed=false" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_freeze_status_claim_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                '"architecture_council_reopen_required": true',
                '"architecture_council_reopen_required": false',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:architecture_council_reopen_required=true" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_architecture_council_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                '"phase10-virtio-input-queue-callback-preflight-helper",\n      "status": "starter_landed"',
                '"phase10-virtio-input-queue-callback-preflight-helper",\n      "status": "blocked_on_risky_transport"',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if (
            "manifest:gap_status:phase10-virtio-input-queue-callback-preflight-helper=blocked_on_risky_transport"
            not in missing_markers
        ):
            raise SystemExit("phase10-input-self-test:expected_queue_callback_gap_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        verify_path = tmp_root / "drivers/virtio/virtio_input_verify.zig"
        original_verify = verify_path.read_text(encoding="utf-8")
        verify_path.write_text(
            original_verify.replace("event_buffers_unfilled", "event_buffers_drifted", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'verify:try std.testing.expectEqualStrings("event_buffers_unfilled", @tagName(summary.blocker.?));' not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_verify_marker_missing")
        verify_path.write_text(original_verify, encoding="utf-8")

        status_drain_path = tmp_root / "zigux/tests/phase10_virtio_input_status_drain.zig"
        original_status_drain = status_drain_path.read_text(encoding="utf-8")
        status_drain_path.write_text(
            original_status_drain.replace("suppressed_status_count", "suppressed_status_drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "status_drain:suppressed_status_count" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_status_drain_marker_missing")
        status_drain_path.write_text(original_status_drain, encoding="utf-8")

        survey_path = tmp_root / "Documentation/zigux/phase10-virtio-input-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace("phase10-virtio-input-wrapper-ownership-note", "phase10-virtio-input-wrapper-drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:phase10-virtio-input-wrapper-ownership-note" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_wrapper_ownership_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace("phase10-virtio-input-registration-lifecycle", "phase10-virtio-input-registration-drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:phase10-virtio-input-registration-lifecycle" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_survey_note_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace("phase10-virtio-input-queue-callback-preflight-helper", "phase10-virtio-input-queue-callback-drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:phase10-virtio-input-queue-callback-preflight-helper" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_queue_callback_note_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase10-input-packet.py --self-test", "scripts/zigux/check-phase10-input-drift.py --self-test", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "makefile:scripts/zigux/check-phase10-input-packet.py --self-test" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_makefile_marker_missing")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace("phase10_virtio_input_status_drain.zig", "phase10_virtio_input_status_drift.zig", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "scripts_readme:phase10_virtio_input_status_drain.zig" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_scripts_readme_marker_missing")
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace("phase10_virtio_input_status_drain.zig", "phase10_virtio_input_status_drift.zig", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "tests_readme:phase10_virtio_input_status_drain.zig" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_tests_readme_marker_missing")
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

    print("PHASE10_INPUT_PACKET_SELF_TEST=pass")
    print("PHASE10_INPUT_PACKET_SELF_TEST_CASE_COUNT=14")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio_input packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a temporary fixture tree.")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())

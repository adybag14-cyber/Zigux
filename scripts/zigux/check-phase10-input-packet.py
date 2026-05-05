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
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "drivers/virtio/virtio_input.zig",
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
    "phase10_virtio_input_survey_module",
    '"phase10-virtio-input-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-survey-tests"',
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
    'try std.testing.expectEqualStrings("P10-Y04", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
]

EXPECTED_SLICE_MARKERS = [
    "bounded status-completion drain summaries",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "transport-backed probe, remove, freeze, restore, or reset paths",
]

EXPECTED_MODULE_MARKERS = [
    "bounded status-drain helper",
    "reclaims queued status completions in memory",
    "queue callbacks",
]

EXPECTED_SURVEY_NOTE_MARKERS = [
    "PHASE10_STATUS=parked",
    "PHASE10_LANE_KEY=P10-Y04",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-registration-lifecycle",
    "real event delivery",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-input-lab-helper": "starter_landed",
    "phase10-virtio-input-lab-gate": "starter_landed",
    "phase10-virtio-input-survey-gate": "starter_landed",
    "phase10-virtio-input-capability-setup-helper": "starter_landed",
    "phase10-virtio-input-multitouch-slot-helper": "starter_landed",
    "phase10-virtio-input-registration-preflight-helper": "starter_landed",
    "phase10-virtio-input-registration-lifecycle": "blocked_on_risky_transport",
}


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

    makefile_text = read_text(root, "zigux/Makefile")
    for marker in EXPECTED_MAKEFILE_MARKERS:
        if marker not in makefile_text:
            missing_markers.append(f"makefile:{marker}")

    helper_text = read_text(root, "drivers/virtio/virtio_input.zig")
    for marker in EXPECTED_HELPER_MARKERS:
        if marker not in helper_text:
            missing_markers.append(f"helper:{marker}")

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
    if manifest.get("lane_key") != "P10-Y04":
        missing_markers.append("manifest:lane_key=P10-Y04")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_input.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio_input.c")
    if manifest.get("surveyed_commit") != "7361ac51374149a96b7a7a2c6ea3c995d8cc1231":
        missing_markers.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/helpers/"]:
        missing_markers.append("manifest:roadmap_destinations")

    summary = manifest.get("survey_summary", {})
    if summary.get("preexisting_phase10_test_files") != 5:
        missing_markers.append("manifest:preexisting_phase10_test_files=5")
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
    if len(gaps) < 11:
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
            original_manifest.replace('"lane_key": "P10-Y04"', '"lane_key": "P10-drift"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:lane_key=P10-Y04" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_lane_key_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

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
            original_survey.replace("phase10-virtio-input-registration-lifecycle", "phase10-virtio-input-registration-drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:phase10-virtio-input-registration-lifecycle" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_survey_note_marker_missing")
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

    print("PHASE10_INPUT_PACKET_SELF_TEST=pass")
    print("PHASE10_INPUT_PACKET_SELF_TEST_CASE_COUNT=4")
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

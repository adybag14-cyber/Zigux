#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

FILES = [
    "scripts/zigux/check-phase10-mmio-packet.py",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

EXPECTED_HELPER_MARKERS = [
    "pub const TransportIdentitySummary = struct {",
    "pub const SelectedQueueReadinessSummary = struct {",
    "pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {",
    "pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
]

EXPECTED_TEST_MARKERS = [
    'test "phase10 virtio mmio exposes a transport identity summary before lifecycle work" {',
    'test "phase10 virtio mmio summarizes selected-queue readiness before transport handoff" {',
]

EXPECTED_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio mmio survey manifest records the landed identity-backed packet" {',
    'try std.testing.expectEqualStrings("P10-L10", manifest.lane_key);',
    'try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);',
    'try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);',
    'try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);',
    'try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);',
    'try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_ring_verify.zig") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_input_verify.zig") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "transport-identity summary") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "consumes that identity snapshot") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "selected-queue readiness summary") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "drivers/virtio/virtio_ring_verify.zig") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "drivers/virtio/virtio_input_verify.zig") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, slice_note, "selected-queue readiness summary") != null);',
    'try std.testing.expect(starter_landed_count >= 16);',
    "var saw_mmio_transport_identity = false;",
    "var saw_mmio_selected_queue_readiness = false;",
]

EXPECTED_SLICE_MARKERS = [
    "one explicit transport-identity summary",
    "one bounded config-write disposition summary",
    "one bounded probe-preflight summary",
    "one bounded selected-queue readiness summary",
    "drivers/virtio/virtio_ring_verify.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zig test zigux/tests/phase10_virtio_mmio.zig",
    "zig test zigux/tests/phase10_virtio_mmio_survey.zig",
]

EXPECTED_SURVEY_NOTE_MARKERS = [
    "PHASE10_STATUS=parked",
    "PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport",
    "phase10-mmio-transport-identity-helper",
    "phase10-mmio-config-write-disposition-helper",
    "phase10-mmio-probe-preflight-helper",
    "phase10-mmio-selected-queue-readiness-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
    "drivers/virtio/virtio_ring_verify.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "transport-identity summary",
    "consumes that identity snapshot",
    "selected-queue readiness summary",
    "queue-ready-for-handoff posture",
    "zig test zigux/tests/phase10_virtio_mmio.zig",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-mmio-survey-gate": "starter_landed",
    "phase10-virtio-mmio-survey-note": "starter_landed",
    "phase10-mmio-register-window-helper": "starter_landed",
    "phase10-mmio-queue-size-helper": "starter_landed",
    "phase10-mmio-feature-word-selector-helper": "starter_landed",
    "phase10-mmio-config-window-helper": "starter_landed",
    "phase10-mmio-config-write-plan-helper": "starter_landed",
    "phase10-mmio-transport-identity-helper": "starter_landed",
    "phase10-mmio-config-write-disposition-helper": "starter_landed",
    "phase10-mmio-probe-preflight-helper": "starter_landed",
    "phase10-mmio-selected-queue-readiness-helper": "starter_landed",
    "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
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

BASELINE_FIXTURE = {
    "scripts/zigux/check-phase10-mmio-packet.py": "# synthetic fixture for self-test\n",
    "drivers/virtio/virtio_mmio.zig": """pub const TransportIdentitySummary = struct {};
pub const SelectedQueueReadinessSummary = struct {};
pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary { _ = self; return .{}; }
pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary { _ = self; return .{}; }
pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary { _ = self; return .{}; }
""",
    "drivers/virtio/virtio_ring_verify.zig": 'test "virtio ring verify fixture" {}\n',
    "drivers/virtio/virtio_input_verify.zig": 'test "virtio input verify fixture" {}\n',
    "zigux/tests/phase10_virtio_mmio.zig": """test "phase10 virtio mmio exposes a transport identity summary before lifecycle work" {}
test "phase10 virtio mmio summarizes selected-queue readiness before transport handoff" {}
""",
    "zigux/tests/phase10_virtio_mmio_survey.zig": """test "phase10 virtio mmio survey manifest records the landed identity-backed packet" {
    try std.testing.expectEqualStrings("P10-L10", manifest.lane_key);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_ring_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_input_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "transport-identity summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "consumes that identity snapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "selected-queue readiness summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "drivers/virtio/virtio_ring_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "drivers/virtio/virtio_input_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "selected-queue readiness summary") != null);
    try std.testing.expect(starter_landed_count >= 16);
    var saw_mmio_transport_identity = false;
    var saw_mmio_selected_queue_readiness = false;
}
""",
    "Documentation/zigux/phase10-virtio-mmio-slice.md": """- one explicit transport-identity summary
- one bounded config-write disposition summary
- one bounded probe-preflight summary
- one bounded selected-queue readiness summary
- `drivers/virtio/virtio_ring_verify.zig`
- `drivers/virtio/virtio_input_verify.zig`
- `zig test zigux/tests/phase10_virtio_mmio.zig`
- `zig test zigux/tests/phase10_virtio_mmio_survey.zig`
""",
    "Documentation/zigux/phase10-virtio-mmio-survey.md": """- `PHASE10_STATUS=parked`
- `PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`
- `phase10-mmio-transport-identity-helper`
- `phase10-mmio-config-write-disposition-helper`
- `phase10-mmio-probe-preflight-helper`
- `phase10-mmio-selected-queue-readiness-helper`
- `phase10-mmio-lifecycle-and-irq-paths`
- `drivers/virtio/virtio_ring_verify.zig`
- `drivers/virtio/virtio_input_verify.zig`
- transport-identity summary
- consumes that identity snapshot
- selected-queue readiness summary
- queue-ready-for-handoff posture
- `zig test zigux/tests/phase10_virtio_mmio.zig`
""",
    "zigux/tests/phase10_virtio_mmio_manifest.json": json.dumps(
        {
            "lane_key": "P10-L10",
            "phase": "Phase 10",
            "surveyed_commit": "84f90e23ad1c28ae345905d5293a8c5395f37d43",
            "anchor": "drivers/virtio/virtio_mmio.c",
            "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"],
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "risky_transport_posture": "blocked_on_risky_transport",
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "architecture_council_reopen_required": True,
            "architecture_council_reopen_attached": False,
            "survey_summary": {
                "virtio_mmio_c_lines": 829,
                "preexisting_phase10_test_files": 11,
                "preexisting_virtio_core_zig_present": True,
                "preexisting_phase10_build_present": True,
                "preexisting_phase10_core_doc_present": True,
                "preexisting_virtio_ring_zig_present": True,
                "preexisting_virtio_ring_doc_present": True,
                "preexisting_virtio_ring_survey_present": True,
                "preexisting_virtio_input_zig_present": True,
                "preexisting_virtio_input_test_present": True,
                "preexisting_virtio_input_survey_present": True,
                "preexisting_virtio_mmio_zig_present": True,
                "preexisting_virtio_mmio_test_present": True,
            },
            "gaps": [
                {"id": "phase10-build-gate", "status": "starter_landed"},
                {"id": "phase10-virtio-mmio-survey-gate", "status": "starter_landed"},
                {"id": "phase10-virtio-mmio-survey-note", "status": "starter_landed"},
                {"id": "phase10-mmio-register-window-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-queue-size-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-feature-word-selector-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-config-window-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-config-write-plan-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-transport-identity-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-config-write-disposition-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-probe-preflight-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-selected-queue-readiness-helper", "status": "starter_landed"},
                {"id": "phase10-mmio-lifecycle-and-irq-paths", "status": "blocked_on_risky_transport"},
            ],
        },
        indent=2,
    )
    + "\n",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    helper_text = read_text(root, "drivers/virtio/virtio_mmio.zig")
    for marker in EXPECTED_HELPER_MARKERS:
        if marker not in helper_text:
            missing_markers.append(f"helper:{marker}")

    test_text = read_text(root, "zigux/tests/phase10_virtio_mmio.zig")
    for marker in EXPECTED_TEST_MARKERS:
        if marker not in test_text:
            missing_markers.append(f"tests:{marker}")

    survey_test_text = read_text(root, "zigux/tests/phase10_virtio_mmio_survey.zig")
    for marker in EXPECTED_SURVEY_TEST_MARKERS:
        if marker not in survey_test_text:
            missing_markers.append(f"survey_test:{marker}")

    slice_text = read_text(root, "Documentation/zigux/phase10-virtio-mmio-slice.md")
    for marker in EXPECTED_SLICE_MARKERS:
        if marker not in slice_text:
            missing_markers.append(f"slice:{marker}")

    survey_note_text = read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md")
    for marker in EXPECTED_SURVEY_NOTE_MARKERS:
        if marker not in survey_note_text:
            missing_markers.append(f"survey_note:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_mmio_manifest.json"))
    if manifest.get("lane_key") != "P10-L10":
        missing_markers.append("manifest:lane_key=P10-L10")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_mmio.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio_mmio.c")
    if manifest.get("surveyed_commit") != "84f90e23ad1c28ae345905d5293a8c5395f37d43":
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
    if summary.get("virtio_mmio_c_lines") != 829:
        missing_markers.append("manifest:virtio_mmio_c_lines=829")
    if summary.get("preexisting_phase10_test_files") != 11:
        missing_markers.append("manifest:preexisting_phase10_test_files=11")

    gaps = manifest.get("gaps", [])
    if len(gaps) < 13:
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for rel_path, content in BASELINE_FIXTURE.items():
            write_fixture(tmp_root, rel_path, content)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-mmio-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        helper_path = tmp_root / "drivers/virtio/virtio_mmio.zig"
        original_helper = helper_path.read_text(encoding="utf-8")
        helper_path.writeText = None
        helper_path.write_text(
            original_helper.replace("pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {", "pub fn transportIdentityDrift(self: *const Self) TransportIdentitySummary {", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "helper:pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_identity_helper_marker_missing")
        helper_path.write_text(original_helper, encoding="utf-8")

        verify_path = tmp_root / "drivers/virtio/virtio_ring_verify.zig"
        verify_path.unlink()
        missing_files, _ = validate(tmp_root)
        if "drivers/virtio/virtio_ring_verify.zig" not in missing_files:
            raise SystemExit("phase10-mmio-self-test:expected_ring_verify_file_missing")
        write_fixture(tmp_root, "drivers/virtio/virtio_ring_verify.zig", 'test "virtio ring verify fixture" {}\n')

        test_path = tmp_root / "zigux/tests/phase10_virtio_mmio.zig"
        original_test = test_path.read_text(encoding="utf-8")
        test_path.write_text(
            original_test.replace(
                'test "phase10 virtio mmio exposes a transport identity summary before lifecycle work" {',
                'test "phase10 virtio mmio identity drift before lifecycle work" {',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'tests:test "phase10 virtio mmio exposes a transport identity summary before lifecycle work" {' not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_identity_test_marker_missing")
        test_path.write_text(original_test, encoding="utf-8")

        manifest_path = tmp_root / "zigux/tests/phase10_virtio_mmio_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(original_manifest)
        for gap in manifest.get("gaps", []):
            if gap.get("id") == "phase10-mmio-transport-identity-helper":
                gap["status"] = "ready_next"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        _, missing_markers = validate(tmp_root)
        if "manifest:gap_status:phase10-mmio-transport-identity-helper=ready_next" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_transport_identity_status_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path = tmp_root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace("drivers/virtio/virtio_input_verify.zig", "drivers/virtio/virtio_input_verify_drift.zig", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:drivers/virtio/virtio_input_verify.zig" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_survey_verify_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        slice_path = tmp_root / "Documentation/zigux/phase10-virtio-mmio-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("drivers/virtio/virtio_ring_verify.zig", "drivers/virtio/virtio_ring_verify_drift.zig", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "slice:drivers/virtio/virtio_ring_verify.zig" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_slice_verify_marker_missing")
        slice_path.write_text(original_slice, encoding="utf-8")

        survey_test_path = tmp_root / "zigux/tests/phase10_virtio_mmio_survey.zig"
        original_survey_test = survey_test_path.read_text(encoding="utf-8")
        survey_test_path.write_text(
            original_survey_test.replace(
                'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_ring_verify.zig") != null);',
                'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_ring_verify_drift.zig") != null);',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'survey_test:try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/virtio_ring_verify.zig") != null);' not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_survey_test_verify_marker_missing")
        survey_test_path.write_text(original_survey_test, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "zig test zigux/tests/phase10_virtio_mmio.zig",
                "zig test zigux/tests/phase10_virtio_mmio_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "slice:zig test zigux/tests/phase10_virtio_mmio.zig" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_slice_direct_replay_marker_missing")
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "zig test zigux/tests/phase10_virtio_mmio_survey.zig",
                "zig test zigux/tests/phase10_virtio_mmio_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "slice:zig test zigux/tests/phase10_virtio_mmio_survey.zig" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_slice_survey_gate_marker_missing")
        slice_path.write_text(original_slice, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "zig test zigux/tests/phase10_virtio_mmio.zig",
                "zig test zigux/tests/phase10_virtio_mmio_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:zig test zigux/tests/phase10_virtio_mmio.zig" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_survey_direct_replay_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        test_path.write_text(
            original_test.replace(
                'test "phase10 virtio mmio summarizes selected-queue readiness before transport handoff" {',
                'test "phase10 virtio mmio summarizes queue-handoff drift before transport handoff" {',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'tests:test "phase10 virtio mmio summarizes selected-queue readiness before transport handoff" {' not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_selected_queue_test_marker_missing")

    print("PHASE10_MMIO_PACKET_SELF_TEST=pass")
    print("PHASE10_MMIO_PACKET_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio_mmio packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a synthetic fixture tree.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_MMIO_PACKET=fail")
        print("MISSING_PHASE10_MMIO_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_MMIO_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_MMIO_PACKET=fail")
        print("MISSING_PHASE10_MMIO_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MMIO_MARKERS_END")
        return 1

    print("PHASE10_MMIO_PACKET=pass")
    print(f"PHASE10_MMIO_REQUIRED_FILE_COUNT={len(FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

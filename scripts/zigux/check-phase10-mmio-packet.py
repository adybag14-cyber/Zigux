#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


def default_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


ROOT = default_root()

FILES = [
    "scripts/zigux/check-phase10-mmio-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_mmio_module",
    "phase10_virtio_mmio_survey_module",
    '"phase10-virtio-mmio-tests"',
    '"phase10-virtio-mmio-survey-tests"',
]

EXPECTED_MAKEFILE_MARKERS = [
    "phase10-test:",
    "scripts/zigux/check-phase10-mmio-packet.py --self-test",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig",
]

EXPECTED_HELPER_MARKERS = [
    "pub const ConfigWriteDispositionSummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
]

EXPECTED_TEST_MARKERS = [
    'test "phase10 virtio mmio clears stale config words when a shorter window is restaged" {',
    'test "phase10 virtio mmio summarizes bounded probe preflight readiness before lifecycle work" {',
    'test "phase10 virtio mmio marks probe preflight incomplete when identity presence falls away" {',
    'test "phase10 virtio mmio summarizes config-write disposition without mutating config space" {',
]

EXPECTED_SURVEY_TEST_MARKERS = [
    'test "phase10 virtio mmio survey manifest records the live helper-backed transport gap" {',
    'try std.testing.expectEqualStrings("P10-L18", manifest.lane_key);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "shorter restaged config window clears stale second-word data") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "config-write disposition summary") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "probe-preflight summary flips from ready to blocked") != null);',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-config-write-disposition-helper")) {',
    'if (std.mem.eql(u8, gap.id, "phase10-mmio-probe-preflight-helper")) {',
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_count);',
]

EXPECTED_SLICE_MARKERS = [
    "one bounded config-write disposition summary",
    "one bounded probe-preflight summary",
    "helper-local interrupt-status staging",
    "make -C zigux phase10",
]

EXPECTED_SURVEY_NOTE_MARKERS = [
    "PHASE10_STATUS=parked",
    "PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport",
    "shorter restaged config window clears stale second-word data",
    "config-write disposition summary",
    "probe-preflight summary flips from ready to blocked",
    "make -C zigux phase10-test",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-mmio-survey-gate": "starter_landed",
    "phase10-virtio-mmio-survey-note": "starter_landed",
    "phase10-mmio-register-window-helper": "starter_landed",
    "phase10-mmio-queue-size-helper": "starter_landed",
    "phase10-virtio-mmio-slice-note": "starter_landed",
    "phase10-mmio-feature-word-selector-helper": "starter_landed",
    "phase10-mmio-config-window-helper": "starter_landed",
    "phase10-mmio-config-write-plan-helper": "starter_landed",
    "phase10-mmio-probe-preflight-helper": "starter_landed",
    "phase10-mmio-config-write-disposition-helper": "starter_landed",
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


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def require_markers(text: str, markers: list[str], prefix: str, missing_markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing_markers.append(f"{prefix}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    require_markers(read_text(root, "zigux/tests/phase10_build.zig"), EXPECTED_BUILD_MARKERS, "build", missing_markers)
    require_markers(read_text(root, "zigux/Makefile"), EXPECTED_MAKEFILE_MARKERS, "makefile", missing_markers)
    require_markers(read_text(root, "drivers/virtio/virtio_mmio.zig"), EXPECTED_HELPER_MARKERS, "helper", missing_markers)
    require_markers(read_text(root, "zigux/tests/phase10_virtio_mmio.zig"), EXPECTED_TEST_MARKERS, "tests", missing_markers)
    require_markers(read_text(root, "zigux/tests/phase10_virtio_mmio_survey.zig"), EXPECTED_SURVEY_TEST_MARKERS, "survey_test", missing_markers)
    require_markers(read_text(root, "Documentation/zigux/phase10-virtio-mmio-slice.md"), EXPECTED_SLICE_MARKERS, "slice", missing_markers)
    require_markers(read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md"), EXPECTED_SURVEY_NOTE_MARKERS, "survey_note", missing_markers)
    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_mmio_manifest.json"))
    if manifest.get("lane_key") != "P10-L18":
        missing_markers.append("manifest:lane_key=P10-L18")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio_mmio.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio_mmio.c")
    if manifest.get("surveyed_commit") != "5f476437a4a3b91d840dd75fca0bf684d1ccc4dd":
        missing_markers.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/helpers/"]:
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
    if summary.get("preexisting_phase10_test_files") != 10:
        missing_markers.append("manifest:preexisting_phase10_test_files=10")
    for key in [
        "preexisting_phase10_build_present",
        "preexisting_virtio_core_zig_present",
        "preexisting_virtio_ring_zig_present",
        "preexisting_virtio_input_zig_present",
        "preexisting_virtio_input_test_present",
        "preexisting_virtio_input_survey_present",
        "preexisting_virtio_mmio_zig_present",
        "preexisting_virtio_mmio_test_present",
    ]:
        if summary.get(key) is not True:
            missing_markers.append(f"manifest:{key}")

    gaps = manifest.get("gaps", [])
    if len(gaps) < 12:
        missing_markers.append("manifest:gaps")
    gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")

    return [], missing_markers


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def baseline_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P10-L18",
            "phase": "Phase 10",
            "surveyed_commit": "5f476437a4a3b91d840dd75fca0bf684d1ccc4dd",
            "anchor": "drivers/virtio/virtio_mmio.c",
            "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/helpers/"],
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "risky_transport_posture": "blocked_on_risky_transport",
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "architecture_council_reopen_required": True,
            "architecture_council_reopen_attached": False,
            "survey_summary": {
                "preexisting_phase10_test_files": 10,
                "preexisting_phase10_build_present": True,
                "preexisting_virtio_core_zig_present": True,
                "preexisting_virtio_ring_zig_present": True,
                "preexisting_virtio_input_zig_present": True,
                "preexisting_virtio_input_test_present": True,
                "preexisting_virtio_input_survey_present": True,
                "preexisting_virtio_mmio_zig_present": True,
                "preexisting_virtio_mmio_test_present": True,
            },
            "gaps": [{"id": gap_id, "status": status} for gap_id, status in EXPECTED_GAPS.items()],
        },
        indent=2,
    )


def run_self_test() -> int:
    fixture = {
        "scripts/zigux/check-phase10-mmio-packet.py": Path(__file__).read_text(encoding="utf-8"),
        "zigux/Makefile": "\n".join(EXPECTED_MAKEFILE_MARKERS),
        "zigux/tests/phase10_build.zig": "\n".join(EXPECTED_BUILD_MARKERS),
        "drivers/virtio/virtio_mmio.zig": "\n".join(EXPECTED_HELPER_MARKERS),
        "zigux/tests/phase10_virtio_mmio.zig": "\n".join(EXPECTED_TEST_MARKERS),
        "zigux/tests/phase10_virtio_mmio_manifest.json": baseline_manifest(),
        "zigux/tests/phase10_virtio_mmio_survey.zig": "\n".join(EXPECTED_SURVEY_TEST_MARKERS),
        "Documentation/zigux/phase10-virtio-mmio-slice.md": "\n".join(EXPECTED_SLICE_MARKERS),
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(EXPECTED_SURVEY_NOTE_MARKERS),
    }

    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for rel_path, content in fixture.items():
            write_fixture(tmp_root, rel_path, content)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-mmio-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase10-mmio-packet.py --self-test", "scripts/zigux/check-phase10-mmio-drift.py --self-test", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "makefile:scripts/zigux/check-phase10-mmio-packet.py --self-test" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_makefile_marker_missing")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        manifest_path = tmp_root / "zigux/tests/phase10_virtio_mmio_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace('"phase10-mmio-config-write-disposition-helper"', '"phase10-mmio-config-write-disposition-drift"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:gap:phase10-mmio-config-write-disposition-helper" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_disposition_gap_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_note_path = tmp_root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        original_survey = survey_note_path.read_text(encoding="utf-8")
        survey_note_path.write_text(
            original_survey.replace("probe-preflight summary flips from ready to blocked", "probe-preflight summary drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:probe-preflight summary flips from ready to blocked" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_survey_note_marker_missing")
        survey_note_path.write_text(original_survey, encoding="utf-8")

        helper_path = tmp_root / "drivers/virtio/virtio_mmio.zig"
        original_helper = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(
            original_helper.replace("pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {", "pub fn configWriteDispositionDrift(self: *const Self) !ConfigWriteDispositionSummary {", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "helper:pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {" not in missing_markers:
            raise SystemExit("phase10-mmio-self-test:expected_helper_marker_missing")
        helper_path.write_text(original_helper, encoding="utf-8")

    print("PHASE10_MMIO_PACKET_SELF_TEST=pass")
    print("PHASE10_MMIO_PACKET_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio_mmio packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a temporary fixture tree.")
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

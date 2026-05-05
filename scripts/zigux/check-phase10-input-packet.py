#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


FILES = [
    "scripts/zigux/check-phase10-input-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_input_module",
    'phase10-virtio-input-tests',
    "run_phase10_virtio_input_tests",
    "phase10_virtio_input_survey_module",
    'phase10-virtio-input-survey-tests',
    "run_phase10_virtio_input_survey_tests",
]

EXPECTED_MAKEFILE_MARKERS = [
    "phase10-test:",
    "scripts/zigux/check-phase10-core-packet.py --self-test",
    "scripts/zigux/check-phase10-core-packet.py",
    "zig build test --build-file zigux/tests/phase10_build.zig",
]

EXPECTED_SURVEY_NOTE_MARKERS = [
    "PHASE10_STATUS=parked",
    "PHASE10_LANE_KEY=P10-Y04",
    "check-phase10-input-packet.py",
    "phase10_virtio_input_manifest.json",
    "phase10_virtio_input_survey.zig",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-registration-lifecycle",
    "transport-backed queue callbacks",
]

EXPECTED_SLICE_NOTE_MARKERS = [
    "drivers/virtio/virtio_input.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_build.zig",
    "zigux/Makefile",
    "ABS_MT_SLOT",
    "MSC_TIMESTAMP",
]

EXPECTED_MODULE_NOTE_MARKERS = [
    "ABS_MT_SLOT",
    "EV_MSC",
    "MSC_TIMESTAMP",
    "input-device registration",
    "queue callbacks",
]

EXPECTED_SURVEY_ZIG_MARKERS = [
    'expectEqualStrings("P10-Y04", manifest.lane_key)',
    'expectEqual(@as(usize, 2), manifest.roadmap_destinations.len)',
    'expect(manifest.gaps.len >= 11)',
    '"phase10-virtio-input-registration-preflight-helper"',
    '"phase10-virtio-input-registration-lifecycle"',
    '"blocked_on_risky_transport"',
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-core-lab-starter": "starter_landed",
    "phase10-virtio-ring-lab-helper": "starter_landed",
    "phase10-virtio-input-lab-helper": "starter_landed",
    "phase10-virtio-input-lab-gate": "starter_landed",
    "phase10-virtio-input-slice-note": "starter_landed",
    "phase10-virtio-input-survey-gate": "starter_landed",
    "phase10-virtio-input-survey-note": "starter_landed",
    "phase10-virtio-input-capability-setup-helper": "starter_landed",
    "phase10-virtio-input-multitouch-slot-helper": "starter_landed",
    "phase10-virtio-input-registration-preflight-helper": "starter_landed",
    "phase10-virtio-input-registration-lifecycle": "blocked_on_risky_transport",
}

ROOT = Path(__file__).resolve().parents[2]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


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

    survey_note = read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md")
    for marker in EXPECTED_SURVEY_NOTE_MARKERS:
        if marker not in survey_note:
            missing_markers.append(f"survey_note:{marker}")

    slice_note = read_text(root, "Documentation/zigux/phase10-virtio-input-slice.md")
    for marker in EXPECTED_SLICE_NOTE_MARKERS:
        if marker not in slice_note:
            missing_markers.append(f"slice_note:{marker}")

    module_note = read_text(root, "Documentation/zigux/phase10-virtio-input-module-slice.md")
    for marker in EXPECTED_MODULE_NOTE_MARKERS:
        if marker not in module_note:
            missing_markers.append(f"module_note:{marker}")

    survey_zig = read_text(root, "zigux/tests/phase10_virtio_input_survey.zig")
    for marker in EXPECTED_SURVEY_ZIG_MARKERS:
        if marker not in survey_zig:
            missing_markers.append(f"survey_zig:{marker}")

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
    if summary.get("virtio_input_c_lines") != 421:
        missing_markers.append("manifest:virtio_input_c_lines=421")
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
    if len(gaps) < len(EXPECTED_GAPS):
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


def build_fixture() -> dict[str, str]:
    manifest = {
        "lane_key": "P10-Y04",
        "phase": "Phase 10",
        "surveyed_commit": "7361ac51374149a96b7a7a2c6ea3c995d8cc1231",
        "anchor": "drivers/virtio/virtio_input.c",
        "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/helpers/"],
        "survey_summary": {
            "virtio_input_c_lines": 421,
            "preexisting_phase10_test_files": 5,
            "preexisting_phase10_build_present": true,
            "preexisting_virtio_core_zig_present": true,
            "preexisting_virtio_ring_zig_present": true,
            "preexisting_virtio_mmio_survey_present": true,
            "preexisting_virtio_input_zig_present": true,
            "preexisting_virtio_input_test_present": true,
            "preexisting_virtio_input_slice_note_present": true,
            "preexisting_virtio_input_module_note_present": true
        },
        "gaps": [
            {"id": gap_id, "status": status}
            for gap_id, status in EXPECTED_GAPS.items()
        ],
    }

    return {
        "scripts/zigux/check-phase10-input-packet.py": "# input checker fixture\n",
        "zigux/Makefile": "\n".join(EXPECTED_MAKEFILE_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(EXPECTED_BUILD_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_input_manifest.json": json.dumps(manifest, indent=2) + "\n",
        "zigux/tests/phase10_virtio_input_survey.zig": "\n".join(EXPECTED_SURVEY_ZIG_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(EXPECTED_SURVEY_NOTE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-slice.md": "\n".join(EXPECTED_SLICE_NOTE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-module-slice.md": "\n".join(EXPECTED_MODULE_NOTE_MARKERS) + "\n",
    }


def run_self_test() -> int:
    fixture = build_fixture()

    with tempfile.TemporaryDirectory(prefix="zigux_phase10_input_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for rel_path, content in fixture.items():
            write_text(tmp_root, rel_path, content)

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
            original_manifest.replace('"phase10-virtio-input-registration-preflight-helper"', '"phase10-virtio-input-registration-preflight-drift"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:gap:phase10-virtio-input-registration-preflight-helper" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_preflight_gap_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

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

        survey_note_path = tmp_root / "Documentation/zigux/phase10-virtio-input-survey.md"
        original_survey_note = survey_note_path.read_text(encoding="utf-8")
        survey_note_path.write_text(
            original_survey_note.replace("phase10-virtio-input-registration-lifecycle", "phase10-virtio-input-registration-drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:phase10-virtio-input-registration-lifecycle" not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_survey_marker_missing")
        survey_note_path.write_text(original_survey_note, encoding="utf-8")

        survey_zig_path = tmp_root / "zigux/tests/phase10_virtio_input_survey.zig"
        original_survey_zig = survey_zig_path.read_text(encoding="utf-8")
        survey_zig_path.write_text(
            original_survey_zig.replace('expectEqual(@as(usize, 2), manifest.roadmap_destinations.len)', 'expectEqual(@as(usize, 3), manifest.roadmap_destinations.len)', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'survey_zig:expectEqual(@as(usize, 2), manifest.roadmap_destinations.len)' not in missing_markers:
            raise SystemExit("phase10-input-self-test:expected_survey_zig_marker_missing")

    print("PHASE10_INPUT_PACKET_SELF_TEST=pass")
    print("PHASE10_INPUT_PACKET_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio input review packet.")
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

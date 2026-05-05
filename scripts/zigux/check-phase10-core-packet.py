#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-core-slice.md",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_core_survey_module",
    'phase10-virtio-core-survey-tests',
    "run_phase10_virtio_core_survey_tests",
    "phase10_virtio_core_reset_queue_module",
    'phase10-virtio-core-reset-queue-tests',
    "run_phase10_virtio_core_reset_queue_tests",
    "phase10_virtio_driver_id_module",
    'phase10-virtio-driver-id-tests',
    "run_phase10_virtio_driver_id_tests",
]

EXPECTED_MAKEFILE_MARKERS = [
    "phase10-test:",
    "scripts/zigux/check-phase10-core-packet.py --self-test",
    "scripts/zigux/check-phase10-core-packet.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig",
]

EXPECTED_TESTS_README_MARKERS = [
    "phase10_virtio_core.zig",
    "phase10_virtio_core_reset_queue.zig",
    "phase10_virtio_core_survey.zig",
    "phase10_virtio_driver_id.zig",
]

EXPECTED_NOTE_MARKERS = [
    "phase10_virtio_core_manifest.json",
    "phase10_virtio_core_survey.zig",
    "check-phase10-core-packet.py",
    "phase10_virtio_core_reset_queue.zig",
    "phase10_virtio_driver_id.zig",
    "driver-validation narrowing",
]

EXPECTED_SURVEY_MARKERS = [
    "lane: `P10-L01`",
    "phase10-driver-id-helper",
    "phase10-driver-validation-narrowing-helper",
    "phase10-core-probe-remove-lifecycle",
    "phase10_virtio_core_reset_queue.zig",
    "phase10_virtio_driver_id.zig",
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]

EXPECTED_RESET_QUEUE_MARKERS = [
    "phase10 virtio core keeps reset replay teardown bookkeeping after driver validation narrows queue features",
    "try device.markDriverReady();",
    "try std.testing.expect(reset_summary.driver_ready);",
    "device.reset();",
    "try std.testing.expect(!cleared_summary.driver_ready);",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-core-survey-gate": "starter_landed",
    "phase10-virtio-core-survey-note": "starter_landed",
    "phase10-driver-id-helper": "starter_landed",
    "phase10-driver-validation-narrowing-helper": "starter_landed",
    "phase10-driver-id-gate": "starter_landed",
    "phase10-core-probe-remove-lifecycle": "blocked_on_risky_transport",
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

    tests_readme_text = read_text(root, "zigux/tests/README.md")
    for marker in EXPECTED_TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            missing_markers.append(f"tests_readme:{marker}")

    reset_queue_text = read_text(root, "zigux/tests/phase10_virtio_core_reset_queue.zig")
    for marker in EXPECTED_RESET_QUEUE_MARKERS:
        if marker not in reset_queue_text:
            missing_markers.append(f"reset_queue:{marker}")

    survey_note = read_text(root, "Documentation/zigux/phase10-virtio-core-survey.md")
    for marker in EXPECTED_SURVEY_MARKERS:
        if marker not in survey_note:
            missing_markers.append(f"survey_note:{marker}")

    slice_note = read_text(root, "Documentation/zigux/phase10-virtio-core-slice.md")
    for marker in EXPECTED_NOTE_MARKERS:
        if marker not in slice_note:
            missing_markers.append(f"slice_note:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_core_manifest.json"))
    if manifest.get("lane_key") != "P10-L01":
        missing_markers.append("manifest:lane_key=P10-L01")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio.c")
    if manifest.get("surveyed_commit") != "7a4454d0474106972cad7e164b79293bd54a40c6":
        missing_markers.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]:
        missing_markers.append("manifest:roadmap_destinations")

    summary = manifest.get("survey_summary", {})
    if summary.get("preexisting_phase10_test_files") != 9:
        missing_markers.append("manifest:preexisting_phase10_test_files=9")
    for key in [
        "preexisting_phase10_build_present",
        "preexisting_virtio_core_zig_present",
        "preexisting_virtio_core_test_present",
        "preexisting_virtio_core_reset_queue_test_present",
        "preexisting_virtio_driver_id_zig_present",
        "preexisting_virtio_driver_id_test_present",
        "preexisting_virtio_core_slice_note_present",
        "preexisting_virtio_ring_survey_present",
        "preexisting_virtio_input_survey_present",
        "preexisting_virtio_mmio_survey_present",
    ]:
        if summary.get(key) is not True:
            missing_markers.append(f"manifest:{key}")

    gaps = manifest.get("gaps", [])
    if len(gaps) < 16:
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


def run_self_test() -> int:
    fixture = {
        "scripts/zigux/check-phase10-core-packet.py": read_text(ROOT, "scripts/zigux/check-phase10-core-packet.py"),
        "zigux/Makefile": read_text(ROOT, "zigux/Makefile"),
        "zigux/tests/README.md": read_text(ROOT, "zigux/tests/README.md"),
        "zigux/tests/phase10_build.zig": read_text(ROOT, "zigux/tests/phase10_build.zig"),
        "zigux/tests/phase10_virtio_core_reset_queue.zig": read_text(ROOT, "zigux/tests/phase10_virtio_core_reset_queue.zig"),
        "zigux/tests/phase10_virtio_core_manifest.json": read_text(ROOT, "zigux/tests/phase10_virtio_core_manifest.json"),
        "zigux/tests/phase10_virtio_core_survey.zig": read_text(ROOT, "zigux/tests/phase10_virtio_core_survey.zig"),
        "Documentation/zigux/phase10-virtio-core-survey.md": read_text(ROOT, "Documentation/zigux/phase10-virtio-core-survey.md"),
        "Documentation/zigux/phase10-virtio-core-slice.md": read_text(ROOT, "Documentation/zigux/phase10-virtio-core-slice.md"),
    }

    with tempfile.TemporaryDirectory(prefix="zigux_phase10_core_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for rel_path, content in fixture.items():
            write_fixture(tmp_root, rel_path, content)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-core-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        manifest_path = tmp_root / "zigux/tests/phase10_virtio_core_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace('"phase10-driver-id-helper"', '"phase10-driver-id-helper-drift"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:gap:phase10-driver-id-helper" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_driver_id_gap_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        build_path = tmp_root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace('"phase10-virtio-core-survey-tests"', '"phase10-core-survey-drift"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'build:phase10-virtio-core-survey-tests' not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_build_marker_missing")
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace('run_phase10_virtio_core_reset_queue_tests', 'run_phase10_virtio_core_reset_queue_drift', 2),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'build:run_phase10_virtio_core_reset_queue_tests' not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_reset_queue_build_marker_missing")
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace('run_phase10_virtio_driver_id_tests', 'run_phase10_virtio_driver_id_drift', 2),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'build:run_phase10_virtio_driver_id_tests' not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_driver_id_build_marker_missing")
        build_path.write_text(original_build, encoding="utf-8")

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig",
                "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "makefile:cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase10_build.zig" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_makefile_marker_missing")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "phase10_virtio_core_reset_queue.zig",
                "phase10_virtio_core_reset_queue_drift.zig",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "tests_readme:phase10_virtio_core_reset_queue.zig" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_tests_readme_reset_queue_marker_missing")
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        reset_queue_path = tmp_root / "zigux/tests/phase10_virtio_core_reset_queue.zig"
        original_reset_queue = reset_queue_path.read_text(encoding="utf-8")
        reset_queue_path.write_text(
            original_reset_queue.replace(
                "try std.testing.expect(reset_summary.driver_ready);",
                "try std.testing.expect(reset_summary.driver_ready_drift);",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "reset_queue:try std.testing.expect(reset_summary.driver_ready);" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_reset_queue_driver_ready_marker_missing")
        reset_queue_path.write_text(original_reset_queue, encoding="utf-8")

        slice_path = tmp_root / "Documentation/zigux/phase10-virtio-core-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("phase10_virtio_core_reset_queue.zig", "phase10_virtio_core_reset_queue_drift.zig"),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "slice_note:phase10_virtio_core_reset_queue.zig" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_reset_queue_slice_marker_missing")
        slice_path.write_text(original_slice, encoding="utf-8")

        survey_path = tmp_root / "Documentation/zigux/phase10-virtio-core-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace("phase10-driver-validation-narrowing-helper", "phase10-driver-validation-drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:phase10-driver-validation-narrowing-helper" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_driver_validation_survey_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace('"phase10-driver-validation-narrowing-helper"', '"phase10-driver-validation-drift"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:gap:phase10-driver-validation-narrowing-helper" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_driver_validation_gap_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace('"zigux/kernel/"', '"zigux/kernel_drift/"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:roadmap_destinations" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_roadmap_destination_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace("zigux/helpers/", "zigux/helpers_drift/", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:zigux/helpers/" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_helpers_survey_marker_missing")

    print("PHASE10_CORE_PACKET_SELF_TEST=pass")
    print("PHASE10_CORE_PACKET_SELF_TEST_CASE_COUNT=12")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the restored Phase 10 virtio core governance packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a temporary fixture tree.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CORE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CORE_MARKERS_END")
        return 1

    print("PHASE10_CORE_PACKET=pass")
    print(f"PHASE10_CORE_REQUIRED_FILE_COUNT={len(FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

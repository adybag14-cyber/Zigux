#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_core_module",
    'phase10-virtio-core-tests',
    "run_phase10_virtio_core_tests",
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

EXPECTED_CORE_TEST_MARKERS = [
    "phase10 virtio core tracks lifecycle guard bookkeeping across driver model milestones",
    "phase10 virtio core exposes reset replay bookkeeping before reset clears state",
    "phase10 virtio core reaches queue runtime readiness after validated feature narrowing",
    "phase10 virtio core renders the bounded status_show surface after driver-model milestones",
    "phase10 virtio core renders bounded features_show bitstrings across device, driver, and negotiated views",
    "const lifecycle = device.lifecycleGuardSummary();",
    "const negotiated_bits = device.featureAttributeSummary(.negotiated);",
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

EXPECTED_CORE_HELPER_MARKERS = [
    'pub const default_driver_name = "anonymous_driver";',
    "pub const DriverLifecycleBlocker = enum {",
    "pub fn finalizeFeaturesWithDriverValidation(",
    "pub fn queueDescriptorShapeSummary(self: *const Self, queue_index: u16) !QueueDescriptorShapeSummary {",
    "pub fn resetReplaySummary(self: *const Self) ResetReplaySummary {",
]

EXPECTED_DRIVER_ID_HELPER_MARKERS = [
    "pub const any_id: u32 = 0xffff_ffff;",
    '.name = "virtio_driver_id_matcher_lab",',
    "pub fn registrationSummary(self: *const Self) RegistrationIdentitySummary {",
    "pub fn driverIdMatchSummary(",
    '"virtio:d{x:0>8}v{x:0>8}"',
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

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def is_lower_hex_commit(value: object) -> bool:
    return isinstance(value, str) and COMMIT_RE.fullmatch(value) is not None


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

    core_test_text = read_text(root, "zigux/tests/phase10_virtio_core.zig")
    for marker in EXPECTED_CORE_TEST_MARKERS:
        if marker not in core_test_text:
            missing_markers.append(f"core_test:{marker}")

    reset_queue_text = read_text(root, "zigux/tests/phase10_virtio_core_reset_queue.zig")
    for marker in EXPECTED_RESET_QUEUE_MARKERS:
        if marker not in reset_queue_text:
            missing_markers.append(f"reset_queue:{marker}")

    core_helper_text = read_text(root, "drivers/virtio/virtio.zig")
    for marker in EXPECTED_CORE_HELPER_MARKERS:
        if marker not in core_helper_text:
            missing_markers.append(f"core_helper:{marker}")

    driver_id_helper_text = read_text(root, "drivers/virtio/virtio_driver_id.zig")
    for marker in EXPECTED_DRIVER_ID_HELPER_MARKERS:
        if marker not in driver_id_helper_text:
            missing_markers.append(f"driver_id_helper:{marker}")

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

    surveyed_commit = manifest.get("surveyed_commit")
    if not is_lower_hex_commit(surveyed_commit):
        missing_markers.append("manifest:surveyed_commit_format")
    elif surveyed_commit not in survey_note:
        missing_markers.append("survey_note:surveyed_commit_alignment")

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
        "zigux/tests/phase10_virtio_core.zig": read_text(ROOT, "zigux/tests/phase10_virtio_core.zig"),
        "zigux/tests/phase10_virtio_core_reset_queue.zig": read_text(ROOT, "zigux/tests/phase10_virtio_core_reset_queue.zig"),
        "zigux/tests/phase10_virtio_core_manifest.json": read_text(ROOT, "zigux/tests/phase10_virtio_core_manifest.json"),
        "zigux/tests/phase10_virtio_core_survey.zig": read_text(ROOT, "zigux/tests/phase10_virtio_core_survey.zig"),
        "Documentation/zigux/phase10-virtio-core-survey.md": read_text(ROOT, "Documentation/zigux/phase10-virtio-core-survey.md"),
        "Documentation/zigux/phase10-virtio-core-slice.md": read_text(ROOT, "Documentation/zigux/phase10-virtio-core-slice.md"),
        "drivers/virtio/virtio.zig": read_text(ROOT, "drivers/virtio/virtio.zig"),
        "drivers/virtio/virtio_driver_id.zig": read_text(ROOT, "drivers/virtio/virtio_driver_id.zig"),
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
            original_build.replace("run_phase10_virtio_core_tests", "run_phase10_virtio_core_drift", 2),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'build:run_phase10_virtio_core_tests' not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_core_build_marker_missing")
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace(
                "run_phase10_virtio_core_reset_queue_tests",
                "run_phase10_virtio_core_reset_queue_drift",
                2,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if 'build:run_phase10_virtio_core_reset_queue_tests' not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_reset_queue_build_marker_missing")
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace("run_phase10_virtio_driver_id_tests", "run_phase10_virtio_driver_id_drift", 2),
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

        core_test_path = tmp_root / "zigux/tests/phase10_virtio_core.zig"
        original_core_test = core_test_path.read_text(encoding="utf-8")
        core_test_path.write_text(
            original_core_test.replace(
                "phase10 virtio core exposes reset replay bookkeeping before reset clears state",
                "phase10 virtio core reset replay drift",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "core_test:phase10 virtio core exposes reset replay bookkeeping before reset clears state" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_core_test_marker_missing")
        core_test_path.write_text(original_core_test, encoding="utf-8")

        core_test_path.write_text(
            original_core_test.replace(
                "phase10 virtio core renders the bounded status_show surface after driver-model milestones",
                "phase10 virtio core status-show drift",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "core_test:phase10 virtio core renders the bounded status_show surface after driver-model milestones" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_status_show_marker_missing")
        core_test_path.write_text(original_core_test, encoding="utf-8")

        core_test_path.write_text(
            original_core_test.replace(
                "const negotiated_bits = device.featureAttributeSummary(.negotiated);",
                "const negotiated_bits = device.featureAttributeSummary(.driver);",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "core_test:const negotiated_bits = device.featureAttributeSummary(.negotiated);" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_negotiated_feature_marker_missing")
        core_test_path.write_text(original_core_test, encoding="utf-8")

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

        core_helper_path = tmp_root / "drivers/virtio/virtio.zig"
        original_core_helper = core_helper_path.read_text(encoding="utf-8")
        core_helper_path.write_text(
            original_core_helper.replace(
                "pub fn resetReplaySummary(self: *const Self) ResetReplaySummary {",
                "pub fn resetReplayDrift(self: *const Self) ResetReplaySummary {",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "core_helper:pub fn resetReplaySummary(self: *const Self) ResetReplaySummary {" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_core_helper_marker_missing")
        core_helper_path.write_text(original_core_helper, encoding="utf-8")

        driver_id_helper_path = tmp_root / "drivers/virtio/virtio_driver_id.zig"
        original_driver_id_helper = driver_id_helper_path.read_text(encoding="utf-8")
        driver_id_helper_path.write_text(
            original_driver_id_helper.replace(
                "pub fn driverIdMatchSummary(",
                "pub fn driverIdMatchSummaryDrift(",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "driver_id_helper:pub fn driverIdMatchSummary(" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_driver_id_helper_marker_missing")
        driver_id_helper_path.write_text(original_driver_id_helper, encoding="utf-8")

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
        survey_path.write_text(original_survey, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace('"surveyed_commit": "7a4454d0474106972cad7e164b79293bd54a40c6"', '"surveyed_commit": "master"', 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "manifest:surveyed_commit_format" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_surveyed_commit_format_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace("7a4454d0474106972cad7e164b79293bd54a40c6", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "survey_note:surveyed_commit_alignment" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_surveyed_commit_alignment_missing")

    print("PHASE10_CORE_PACKET_SELF_TEST=pass")
    print("PHASE10_CORE_PACKET_SELF_TEST_CASE_COUNT=20")
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

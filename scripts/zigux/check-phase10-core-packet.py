#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

SURVEYED_COMMIT = "c11221dc7a68d7511ae1c69d64b3f08528287ed8"

FILES = [
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
]

EXPECTED_BUILD_MARKERS = [
    "phase10_virtio_core_module",
    '"phase10-virtio-core-tests"',
    "run_phase10_virtio_core_tests",
    "phase10_virtio_core_survey_module",
    '"phase10-virtio-core-survey-tests"',
    "run_phase10_virtio_core_survey_tests",
    "phase10_virtio_core_reset_queue_module",
    '"phase10-virtio-core-reset-queue-tests"',
    "run_phase10_virtio_core_reset_queue_tests",
    "phase10_virtio_driver_id_module",
    '"phase10-virtio-driver-id-tests"',
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
    "const lifecycle = device.lifecycleGuardSummary();",
]

EXPECTED_RESET_QUEUE_MARKERS = [
    "phase10 virtio core keeps reset replay teardown bookkeeping after driver validation narrows queue features",
    "try device.markDriverReady();",
    "try std.testing.expect(reset_summary.driver_ready);",
    "device.reset();",
    "try std.testing.expect(!cleared_summary.driver_ready);",
]

EXPECTED_SURVEY_MARKERS = [
    "lane: `P10-L01`",
    SURVEYED_COMMIT,
    "phase10-driver-id-helper",
    "phase10-driver-id-coverage-disposition-helper",
    "phase10-lifecycle-guard-bookkeeping-helper",
    "phase10-core-lab-validation-evidence",
    "phase10-virtio-core-slice.md",
    "phase10-core-slice-note",
    "phase10-core-dual-implementation-bridge",
    "phase10-core-probe-remove-lifecycle",
    "phase10_virtio_core_manifest.json",
    "phase10_virtio_core_survey.zig",
    "drivers/virtio/virtio_verify.zig",
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]

EXPECTED_SLICE_MARKERS = [
    "# Phase 10 Virtio Core Slice",
    "drivers/virtio/virtio.c",
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "drivers/virtio/virtio_verify.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
    "lab-only driver validation evidence",
    "blocked risky-transport posture",
]

EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-core-lab-starter": "starter_landed",
    "phase10-virtio-core-lab-gate": "starter_landed",
    "phase10-virtio-core-reset-queue-gate": "starter_landed",
    "phase10-virtio-core-slice-note": "starter_landed",
    "phase10-virtio-core-survey-gate": "starter_landed",
    "phase10-virtio-core-survey-note": "starter_landed",
    "phase10-virtio-core-verify-replay": "starter_landed",
    "phase10-driver-id-helper": "starter_landed",
    "phase10-driver-id-coverage-disposition-helper": "starter_landed",
    "phase10-driver-id-gate": "starter_landed",
    "phase10-queue-shape-bookkeeping-helper": "starter_landed",
    "phase10-config-generation-bookkeeping-helper": "starter_landed",
    "phase10-interrupt-ack-bookkeeping-helper": "starter_landed",
    "phase10-lifecycle-guard-bookkeeping-helper": "starter_landed",
    "phase10-driver-validation-narrowing-helper": "starter_landed",
    "phase10-core-attribute-summary-helper": "starter_landed",
    "phase10-reset-replay-bookkeeping-helper": "starter_landed",
    "phase10-core-lab-validation-evidence": "starter_landed",
    "phase10-core-dual-implementation-bridge": "blocked_on_risky_transport",
    "phase10-core-probe-remove-lifecycle": "blocked_on_risky_transport",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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

    survey_note = read_text(root, "Documentation/zigux/phase10-virtio-core-survey.md")
    for marker in EXPECTED_SURVEY_MARKERS:
        if marker not in survey_note:
            missing_markers.append(f"survey_note:{marker}")

    slice_note = read_text(root, "Documentation/zigux/phase10-virtio-core-slice.md")
    for marker in EXPECTED_SLICE_MARKERS:
        if marker not in slice_note:
            missing_markers.append(f"slice_note:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_core_manifest.json"))
    if manifest.get("lane_key") != "P10-L01":
        missing_markers.append("manifest:lane_key=P10-L01")
    if manifest.get("phase") != "Phase 10":
        missing_markers.append("manifest:phase=Phase 10")
    if manifest.get("anchor") != "drivers/virtio/virtio.c":
        missing_markers.append("manifest:anchor=drivers/virtio/virtio.c")
    if manifest.get("surveyed_commit") != SURVEYED_COMMIT:
        missing_markers.append("manifest:surveyed_commit")
    if manifest.get("roadmap_destinations") != ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]:
        missing_markers.append("manifest:roadmap_destinations")

    summary = manifest.get("survey_summary", {})
    if summary.get("preexisting_phase10_test_files") != 11:
        missing_markers.append("manifest:preexisting_phase10_test_files=11")
    if summary.get("preexisting_virtio_core_slice_note_present") is not True:
        missing_markers.append("manifest:preexisting_virtio_core_slice_note_present=true")
    for key in [
        "preexisting_phase10_build_present",
        "preexisting_virtio_core_zig_present",
        "preexisting_virtio_core_test_present",
        "preexisting_virtio_core_reset_queue_test_present",
        "preexisting_virtio_driver_id_zig_present",
        "preexisting_virtio_driver_id_test_present",
        "preexisting_virtio_ring_survey_present",
        "preexisting_virtio_input_survey_present",
        "preexisting_virtio_mmio_survey_present",
    ]:
        if summary.get(key) is not True:
            missing_markers.append(f"manifest:{key}")

    gaps = manifest.get("gaps", [])
    if len(gaps) < 21:
        missing_markers.append("manifest:gaps")
    gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    blocked_count = 0
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')}")
        if status == "blocked_on_risky_transport":
            blocked_count += 1
    if blocked_count != 2:
        missing_markers.append("manifest:blocked_gap_count=2")

    return [], missing_markers


def build_fixture_manifest() -> str:
    manifest = {
        "lane_key": "P10-L01",
        "phase": "Phase 10",
        "surveyed_commit": SURVEYED_COMMIT,
        "anchor": "drivers/virtio/virtio.c",
        "roadmap_destinations": [
            "drivers/virtio/*.zig",
            "zigux/kernel/",
            "zigux/helpers/",
        ],
        "survey_summary": {
            "virtio_c_lines": 730,
            "preexisting_phase10_test_files": 11,
            "preexisting_phase10_build_present": True,
            "preexisting_virtio_core_zig_present": True,
            "preexisting_virtio_core_test_present": True,
            "preexisting_virtio_core_reset_queue_test_present": True,
            "preexisting_virtio_driver_id_zig_present": True,
            "preexisting_virtio_driver_id_test_present": True,
            "preexisting_virtio_core_slice_note_present": True,
            "preexisting_virtio_ring_survey_present": True,
            "preexisting_virtio_input_survey_present": True,
            "preexisting_virtio_mmio_survey_present": True,
        },
        "gaps": [
            {
                "id": gap_id,
                "status": status,
                "kind": "validation" if "gate" in gap_id or "evidence" in gap_id or "replay" in gap_id else "lab_driver_starter",
                "zigux_destination": "drivers/virtio/virtio.zig",
                "why_now": gap_id,
            }
            for gap_id, status in EXPECTED_GAPS.items()
        ],
    }
    return json.dumps(manifest, indent=2) + "\n"


def build_fixture_files() -> dict[str, str]:
    build_markers = "\n".join(EXPECTED_BUILD_MARKERS)
    return {
        "scripts/zigux/check-phase10-core-packet.py": "# fixture copy\n",
        "zigux/Makefile": "\n".join(EXPECTED_MAKEFILE_MARKERS) + "\n",
        "zigux/tests/README.md": "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": build_markers + "\n",
        "zigux/tests/phase10_virtio_core.zig": "\n".join(EXPECTED_CORE_TEST_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_core_reset_queue.zig": "\n".join(EXPECTED_RESET_QUEUE_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_driver_id.zig": "phase10 virtio driver id coverage helper\n",
        "zigux/tests/phase10_virtio_core_survey.zig": f'const surveyed_commit = "{SURVEYED_COMMIT}";\n',
        "zigux/tests/phase10_virtio_core_manifest.json": build_fixture_manifest(),
        "Documentation/zigux/phase10-virtio-core-slice.md": "\n".join(EXPECTED_SLICE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-core-survey.md": "\n".join(EXPECTED_SURVEY_MARKERS) + "\n",
    }


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_core_packet_") as tmp_dir:
        root = Path(tmp_dir)
        fixture = build_fixture_files()
        for rel_path, content in fixture.items():
            write_fixture(root, rel_path, content)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-core-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        manifest_path = root / "zigux/tests/phase10_virtio_core_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(original_manifest.replace(SURVEYED_COMMIT, "deadbeef", 1), encoding="utf-8")
        _, missing_markers = validate(root)
        if "manifest:surveyed_commit" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_manifest_commit_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(original_manifest.replace('"preexisting_phase10_test_files": 11', '"preexisting_phase10_test_files": 9', 1), encoding="utf-8")
        _, missing_markers = validate(root)
        if "manifest:preexisting_phase10_test_files=11" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_manifest_test_count_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.writeText = None
        manifest_path.write_text(original_manifest.replace('"preexisting_virtio_core_slice_note_present": true', '"preexisting_virtio_core_slice_note_present": false', 1), encoding="utf-8")
        _, missing_markers = validate(root)
        if "manifest:preexisting_virtio_core_slice_note_present=true" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_slice_note_presence_marker_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                '"id": "phase10-virtio-core-slice-note",\n      "status": "starter_landed"',
                '"id": "phase10-virtio-core-slice-note",\n      "status": "repo_reality_gap"',
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        if "manifest:gap_status:phase10-virtio-core-slice-note=repo_reality_gap" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_slice_note_gap_status_missing")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path = root / "Documentation/zigux/phase10-virtio-core-survey.md"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace("phase10-core-slice-note", "phase10-core-slice-drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        if "survey_note:phase10-core-slice-note" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_slice_gap_survey_marker_missing")
        survey_path.write_text(original_survey, encoding="utf-8")

        slice_path = root / "Documentation/zigux/phase10-virtio-core-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("lab-only driver validation evidence", "review packet only", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        if "slice_note:lab-only driver validation evidence" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_slice_note_marker_missing")
        slice_path.write_text(original_slice, encoding="utf-8")

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("run_phase10_virtio_core_tests", "run_phase10_virtio_core_drift", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        if "build:run_phase10_virtio_core_tests" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_core_build_marker_missing")
        build_path.write_text(original_build, encoding="utf-8")

        core_test_path = root / "zigux/tests/phase10_virtio_core.zig"
        original_core_test = core_test_path.read_text(encoding="utf-8")
        core_test_path.write_text(
            original_core_test.replace(
                "phase10 virtio core exposes reset replay bookkeeping before reset clears state",
                "phase10 virtio core reset replay drift",
                1,
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        if "core_test:phase10 virtio core exposes reset replay bookkeeping before reset clears state" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_core_test_marker_missing")
        core_test_path.write_text(original_core_test, encoding="utf-8")

        readme_path = root / "zigux/tests/README.md"
        original_readme = readme_path.read_text(encoding="utf-8")
        readme_path.write_text(
            original_readme.replace("phase10_virtio_driver_id.zig", "phase10_virtio_driver_id_drift.zig", 1),
            encoding="utf-8",
        )
        _, missing_markers = validate(root)
        if "tests_readme:phase10_virtio_driver_id.zig" not in missing_markers:
            raise SystemExit("phase10-core-self-test:expected_tests_readme_marker_missing")

    print("PHASE10_CORE_PACKET_SELF_TEST=pass")
    print("PHASE10_CORE_PACKET_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 10 virtio core review packet.")
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

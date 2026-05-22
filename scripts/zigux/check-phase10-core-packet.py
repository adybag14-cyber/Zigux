#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase10_virtio_core_manifest.json"
EXPECTED_MANIFEST_FIELDS = {
    "lane_key": "P10-L01",
    "phase": "Phase 10",
    "anchor": "drivers/virtio/virtio.c",
    "roadmap_destinations": ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"],
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "allowed_evidence_kinds": [
        "driver_local_lab_slices",
        "survey_manifests",
        "shared_validation_gates",
    ],
    "forbidden_transport_claims": [
        "queue_setup_reset_paths",
        "irq_parity",
        "dma_paths",
        "input_registration_lifecycle",
        "probe_remove_lifecycle",
    ],
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}
EXPECTED_SUMMARY_TRUE_KEYS = (
    "preexisting_phase10_build_present",
    "preexisting_virtio_core_zig_present",
    "preexisting_virtio_core_test_present",
    "preexisting_virtio_core_reset_queue_test_present",
    "preexisting_virtio_core_slice_note_present",
)
EXPECTED_SUMMARY_FALSE_KEYS = (
    "preexisting_virtio_driver_id_zig_present",
    "preexisting_virtio_driver_id_test_present",
)
EXPECTED_GAP_METADATA = {
    "phase10-build-gate": ("validation", "starter_landed", "zigux/tests/phase10_build.zig"),
    "phase10-virtio-core-lab-starter": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-virtio-core-lab-gate": (
        "validation",
        "starter_landed",
        "zigux/tests/phase10_virtio_core.zig",
    ),
    "phase10-virtio-core-reset-queue-gate": (
        "validation",
        "starter_landed",
        "zigux/tests/phase10_virtio_core_reset_queue.zig",
    ),
    "phase10-virtio-core-slice-note": (
        "documentation",
        "starter_landed",
        "Documentation/zigux/phase10-virtio-core-slice.md",
    ),
    "phase10-virtio-core-survey-gate": (
        "validation",
        "starter_landed",
        "zigux/tests/phase10_virtio_core_survey.zig",
    ),
    "phase10-virtio-core-survey-note": (
        "documentation",
        "starter_landed",
        "Documentation/zigux/phase10-virtio-core-survey.md",
    ),
    "phase10-virtio-core-verify-replay": (
        "validation",
        "starter_landed",
        "drivers/virtio/virtio_verify.zig",
    ),
    "phase10-queue-shape-bookkeeping-helper": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-config-generation-bookkeeping-helper": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-interrupt-ack-bookkeeping-helper": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-lifecycle-guard-bookkeeping-helper": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-driver-validation-narrowing-helper": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-core-attribute-summary-helper": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-reset-replay-bookkeeping-helper": (
        "lab_driver_starter",
        "starter_landed",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-core-lab-validation-evidence": (
        "validation",
        "starter_landed",
        "Documentation/zigux/phase10-virtio-core-survey.md",
    ),
    "phase10-interrupt-compound-ack-gate": (
        "validation",
        "starter_landed",
        "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    ),
    "phase10-core-dual-implementation-bridge": (
        "dual_implementation_boundary",
        "blocked_on_risky_transport",
        "drivers/virtio/virtio.zig",
    ),
    "phase10-core-probe-remove-lifecycle": (
        "lab_driver_starter",
        "blocked_on_risky_transport",
        "drivers/virtio/virtio.zig",
    ),
}

REQUIRED_MARKERS = {
    "Documentation/zigux/phase10-virtio-core-survey.md": [
        "lane: `P10-L01`",
        "`drivers/virtio/virtio_verify.zig`",
        "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
        "`zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`",
        "`drivers/virtio/virtio_driver_id.zig`",
        "`zigux/tests/phase10_virtio_driver_id.zig`",
    ],
    "Documentation/zigux/phase10-virtio-core-slice.md": [
        "`drivers/virtio/virtio_verify.zig`",
        "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
        "`zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`",
        "`zigux/tests/phase10_virtio_core_survey.zig`",
        "landed `virtio_driver_id` helper or replay coverage on current `master`",
        "those exact paths stay unreadable as shipped evidence in this runtime",
    ],
    "drivers/virtio/virtio.zig": [
        "pub const DriverModelSummary = struct {",
        "pub const DriverIdCoverageSummary = struct {",
        "pub fn driverModelSummary(self: *const Self) DriverModelSummary {",
        "pub fn driverIdCoverageSummary(self: *const Self, rules: []const DriverIdMatchRule) DriverIdCoverageSummary {",
        "test \"phase10 virtio core driver model summary exposes wrapper stages for staged readiness\" {",
        "test \"phase10 virtio core driver id coverage summary keeps disposition bookkeeping local to the core helper\" {",
    ],
    "drivers/virtio/virtio_verify.zig": [
        "pub fn summarizeDriverModel(core: *const virtio_core.VirtioCoreLab) DriverModelSummary {",
        "pub fn resetReplayPreservesQueueShape(before: QueueBookkeepingSummary, after: QueueBookkeepingSummary) bool {",
        "test \"phase10 virtio core verify keeps lifecycle checkpoints explicit\" {",
        "test \"phase10 virtio core verify keeps reset replay below transport lifecycle claims\" {",
    ],
    "zigux/tests/phase10_build.zig": [
        ".name = \"phase10-virtio-core-tests\",",
        ".name = \"phase10-virtio-core-interrupt-compound-ack-tests\",",
        ".name = \"phase10-virtio-core-reset-queue-tests\",",
        ".name = \"phase10-virtio-core-verify-tests\",",
        ".name = \"phase10-virtio-core-survey-tests\",",
        ".name = \"phase10-virtio-driver-id-tests\",",
        "test_step.dependOn(&run_phase10_virtio_core_verify_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_driver_id_tests.step);",
    ],
    "zigux/tests/phase10_virtio_core.zig": [
        "test \"phase10 virtio core summary replay keeps status and feature bookkeeping reviewable\" {",
        "test \"phase10 virtio core reset replay clears interrupt debt and drops driver readiness\" {",
        "test \"phase10 virtio core driver id replay keeps exact wildcard and unmatched rules reviewable\" {",
    ],
    "zigux/tests/phase10_virtio_core_survey.zig": [
        "test \"phase10 virtio core survey gate keeps verify and focused replay surfaces explicit\" {",
        "test \"phase10 virtio core survey gate keeps slice-local review surfaces and blockers explicit\" {",
        "try expectContains(build_file, \"\\\"phase10-virtio-core-verify-tests\\\"\");",
        "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-core-probe-remove-lifecycle\\\"\");",
    ],
}

FORBIDDEN_MARKERS = {}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate_manifest(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    problems: list[str] = []
    for field_name, expected_value in EXPECTED_MANIFEST_FIELDS.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            problems.append(f"{MANIFEST_PATH}:{field_name}:{actual_value}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        return [f"{MANIFEST_PATH}:survey_summary:not_an_object"]

    for key in EXPECTED_SUMMARY_TRUE_KEYS:
        if summary.get(key) is not True:
            problems.append(f"{MANIFEST_PATH}:summary:{key}:{summary.get(key)}")
    for key in EXPECTED_SUMMARY_FALSE_KEYS:
        if summary.get(key) is not False:
            problems.append(f"{MANIFEST_PATH}:summary:{key}:{summary.get(key)}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return [f"{MANIFEST_PATH}:gaps:not_a_list"]
    gap_index = {
        gap.get("id"): gap for gap in gaps if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id, (expected_kind, expected_status, expected_destination) in EXPECTED_GAP_METADATA.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            problems.append(f"{MANIFEST_PATH}:gap_missing:{gap_id}")
            continue
        if gap.get("kind") != expected_kind:
            problems.append(f"{MANIFEST_PATH}:gap:{gap_id}:kind:{gap.get('kind')}")
        if gap.get("status") != expected_status:
            problems.append(f"{MANIFEST_PATH}:gap:{gap_id}:status:{gap.get('status')}")
        if gap.get("zigux_destination") != expected_destination:
            problems.append(
                f"{MANIFEST_PATH}:gap:{gap_id}:zigux_destination:{gap.get('zigux_destination')}"
            )
    return problems


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_MARKERS if not (root / path).exists()]
    if not (root / MANIFEST_PATH).exists():
        missing_files.append(MANIFEST_PATH)
    if missing_files:
        return missing_files, []

    problems: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"{rel_path}:{marker}")
    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                problems.append(f"{rel_path}:forbidden:{marker}")
    problems.extend(validate_manifest(root))
    return [], problems


def fixture_manifest() -> dict[str, object]:
    gaps = []
    for gap_id, (kind, status, destination) in EXPECTED_GAP_METADATA.items():
        gaps.append(
            {
                "id": gap_id,
                "kind": kind,
                "status": status,
                "zigux_destination": destination,
            }
        )

    return {
        **EXPECTED_MANIFEST_FIELDS,
        "surveyed_commit": "fixture",
        "survey_summary": {
            "preexisting_phase10_build_present": True,
            "preexisting_virtio_core_zig_present": True,
            "preexisting_virtio_core_test_present": True,
            "preexisting_virtio_core_reset_queue_test_present": True,
            "preexisting_virtio_driver_id_zig_present": False,
            "preexisting_virtio_driver_id_test_present": False,
            "preexisting_virtio_core_slice_note_present": True,
        },
        "gaps": gaps,
    }


def write_fixture(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(markers) + "\n", encoding="utf-8")

    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(fixture_manifest(), indent=2) + "\n", encoding="utf-8")


def expect_problem(root: Path, mutate, expected: str) -> None:
    mutate(root)
    missing_files, problems = validate(root)
    if missing_files:
        actual = ",".join(missing_files)
        raise SystemExit(f"phase10-core-self-test:unexpected_missing={actual}")
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"phase10-core-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_core_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        missing_files, problems = validate(root)
        if missing_files or problems:
            raise SystemExit(
                "phase10-core-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"problems={','.join(problems) or 'none'}"
            )

        def remove_checker_marker(tmp_root: Path) -> None:
            path = tmp_root / "Documentation/zigux/phase10-virtio-core-survey.md"
            text = path.read_text(encoding="utf-8")
            marker = "`drivers/virtio/virtio_verify.zig`"
            path.write_text(text.replace(marker, "__removed__", 1), encoding="utf-8")

        expect_problem(
            root,
            remove_checker_marker,
            "Documentation/zigux/phase10-virtio-core-survey.md:`drivers/virtio/virtio_verify.zig`",
        )
        write_fixture(root)

        def drift_manifest(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["risky_transport_posture"] = "starter_landed"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_manifest,
            f"{MANIFEST_PATH}:risky_transport_posture:starter_landed",
        )
        write_fixture(root)

        def remove_gap(tmp_root: Path) -> None:
            path = tmp_root / MANIFEST_PATH
            data = json.loads(path.read_text(encoding="utf-8"))
            data["gaps"] = [
                gap for gap in data["gaps"] if gap["id"] != "phase10-virtio-core-verify-replay"
            ]
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            remove_gap,
            f"{MANIFEST_PATH}:gap_missing:phase10-virtio-core-verify-replay",
        )
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_core_survey.zig").unlink()
        missing_files, problems = validate(root)
        if problems:
            actual = ",".join(problems)
            raise SystemExit(f"phase10-core-self-test:unexpected_problems={actual}")
        if "zigux/tests/phase10_virtio_core_survey.zig" not in missing_files:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(
                "phase10-core-self-test:expected_missing=zigux/tests/phase10_virtio_core_survey.zig:"
                f"actual={actual}"
            )

    print("PHASE10_CORE_PACKET_SELF_TEST=pass")
    print("PHASE10_CORE_PACKET_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current directly re-readable Phase 10 virtio core packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, problems = validate(Path(args.root))
    if missing_files:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CORE_FILES_END")
        return 1

    if problems:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_MARKERS_START")
        for item in problems:
            print(item)
        print("MISSING_PHASE10_CORE_MARKERS_END")
        return 1

    required_marker_count = sum(len(markers) for markers in REQUIRED_MARKERS.values())
    forbidden_marker_count = sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
    print("PHASE10_CORE_PACKET=pass")
    print(f"PHASE10_CORE_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS) + 1}")
    print(f"PHASE10_CORE_REQUIRED_MARKER_COUNT={required_marker_count}")
    print(f"PHASE10_CORE_FORBIDDEN_MARKER_COUNT={forbidden_marker_count}")
    print(f"PHASE10_CORE_EXPECTED_GAP_METADATA_COUNT={len(EXPECTED_GAP_METADATA)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

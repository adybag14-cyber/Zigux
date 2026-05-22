#!/usr/bin/env python3
"""Validate the current Phase 10 virtio core packet against live repo surfaces."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

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

EXPECTED_SUMMARY_VALUES = {
    "preexisting_phase10_test_files": 11,
    "preexisting_phase10_build_present": True,
    "preexisting_virtio_core_zig_present": True,
    "preexisting_virtio_core_test_present": True,
    "preexisting_virtio_core_reset_queue_test_present": True,
    "preexisting_virtio_driver_id_zig_present": False,
    "preexisting_virtio_driver_id_test_present": False,
    "preexisting_virtio_core_slice_note_present": True,
    "preexisting_virtio_ring_survey_present": True,
    "preexisting_virtio_input_survey_present": True,
    "preexisting_virtio_mmio_survey_present": True,
}

EXPECTED_GAP_FIELDS = {
    "phase10-virtio-core-lab-starter": {
        "kind": "lab_driver_starter",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
    "phase10-virtio-core-lab-gate": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_core.zig",
    },
    "phase10-virtio-core-reset-queue-gate": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_core_reset_queue.zig",
    },
    "phase10-virtio-core-survey-gate": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_core_survey.zig",
    },
    "phase10-virtio-core-verify-replay": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio_verify.zig",
    },
    "phase10-driver-validation-narrowing-helper": {
        "kind": "lab_driver_starter",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
    "phase10-core-attribute-summary-helper": {
        "kind": "lab_driver_starter",
        "status": "starter_landed",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
    "phase10-core-lab-validation-evidence": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "Documentation/zigux/phase10-virtio-core-survey.md",
    },
    "phase10-interrupt-compound-ack-gate": {
        "kind": "validation",
        "status": "starter_landed",
        "zigux_destination": "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    },
    "phase10-core-dual-implementation-bridge": {
        "kind": "dual_implementation_boundary",
        "status": "blocked_on_risky_transport",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
    "phase10-core-probe-remove-lifecycle": {
        "kind": "lab_driver_starter",
        "status": "blocked_on_risky_transport",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
}

REQUIRED_PATHS = {
    "Documentation/zigux/phase10-virtio-core-survey.md": [
        "lane: `P10-L01`",
        "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
        "`drivers/virtio/virtio.zig`",
        "`drivers/virtio/virtio_driver_id.zig`",
        "`drivers/virtio/virtio_verify.zig`",
        "`zigux/tests/phase10_virtio_core.zig`",
        "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
        "`zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`",
        "`zigux/tests/phase10_virtio_driver_id.zig`",
        "`zigux/tests/phase10_build.zig`",
        "`scripts/zigux/validate-phase10.py`",
        "`scripts/zigux/check-phase10-core-packet.py`",
        "stale guardrail reference drift",
    ],
    "drivers/virtio/virtio_driver_id.zig": [
        "pub fn reviewDriverIdMatch(",
        "pub fn reviewDevice(",
        'test "phase10 virtio driver id review keeps exact matches explicit" {',
        'test "phase10 virtio driver id review keeps wildcard matches and misses distinct" {',
    ],
    "drivers/virtio/virtio_verify.zig": [
        "pub fn summarizeDriverModel(",
        "pub fn resetReplayPreservesQueueShape(",
        'test "phase10 virtio core verify keeps lifecycle checkpoints explicit" {',
        'test "phase10 virtio core verify keeps reset replay below transport lifecycle claims" {',
    ],
    "zigux/tests/phase10_build.zig": [
        '".name = "phase10-virtio-core-tests""',
        '".name = "phase10-virtio-core-interrupt-compound-ack-tests""',
        '".name = "phase10-virtio-core-reset-queue-tests""',
        '".name = "phase10-virtio-core-verify-tests""',
        '".name = "phase10-virtio-core-survey-tests""',
        '".name = "phase10-virtio-driver-id-tests""',
        "test_step.dependOn(&run_phase10_virtio_core_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_core_interrupt_compound_ack_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_core_verify_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_driver_id_tests.step);",
    ],
    "zigux/tests/phase10_virtio_core.zig": [
        'test "phase10 virtio core summary replay keeps status and feature bookkeeping reviewable" {',
        'test "phase10 virtio core reset replay clears interrupt debt and drops driver readiness" {',
        'test "phase10 virtio core driver id replay keeps exact wildcard and unmatched rules reviewable" {',
    ],
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig": [
        'test "phase10 virtio core interrupt compound ack replay keeps queue-used and config-change bits isolated" {',
    ],
    "zigux/tests/phase10_virtio_core_reset_queue.zig": [
        'test "phase10 virtio core reset queue replay drops ready state until queue and status are replayed" {',
        'test "phase10 virtio core reset queue replay clears reset-required state" {',
    ],
    "zigux/tests/phase10_virtio_driver_id.zig": [
        'test "phase10 virtio driver id replay keeps exact and wildcard dispositions reviewable" {',
        'test "phase10 virtio driver id replay keeps vendor wildcard and no-match paths separate" {',
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate_manifest(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    problems: list[str] = []

    for key, expected_value in EXPECTED_MANIFEST_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected_value:
            problems.append(f"{MANIFEST_PATH}:{key}:{actual!r}")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or COMMIT_RE.fullmatch(surveyed_commit) is None:
        problems.append(f"{MANIFEST_PATH}:surveyed_commit:{surveyed_commit!r}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        return [f"{MANIFEST_PATH}:survey_summary:not_dict"]

    for key, expected_value in EXPECTED_SUMMARY_VALUES.items():
        actual = summary.get(key)
        if actual != expected_value:
            problems.append(f"{MANIFEST_PATH}:survey_summary:{key}:{actual!r}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return [f"{MANIFEST_PATH}:gaps:not_list"]

    gap_index = {
        gap.get("id"): gap
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id, expected_fields in EXPECTED_GAP_FIELDS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            problems.append(f"{MANIFEST_PATH}:gap_missing:{gap_id}")
            continue
        for field_name, expected_value in expected_fields.items():
            actual = gap.get(field_name)
            if actual != expected_value:
                problems.append(
                    f"{MANIFEST_PATH}:gap:{gap_id}:{field_name}:{actual!r}"
                )

    survey_text = read_text(root, "Documentation/zigux/phase10-virtio-core-survey.md")
    if isinstance(surveyed_commit, str) and COMMIT_RE.fullmatch(surveyed_commit) is not None:
        if surveyed_commit not in survey_text:
            problems.append(
                "Documentation/zigux/phase10-virtio-core-survey.md:surveyed_commit_alignment"
            )

    return problems


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [
        rel_path
        for rel_path in (*REQUIRED_PATHS.keys(), MANIFEST_PATH)
        if not (root / rel_path).exists()
    ]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in REQUIRED_PATHS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel_path}:{marker}")

    missing_markers.extend(validate_manifest(root))
    return [], missing_markers


def fixture_manifest() -> dict[str, object]:
    gaps = []
    for gap_id, gap_fields in EXPECTED_GAP_FIELDS.items():
        gaps.append({"id": gap_id, **gap_fields})

    return {
        **EXPECTED_MANIFEST_FIELDS,
        "surveyed_commit": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
        "survey_summary": EXPECTED_SUMMARY_VALUES,
        "gaps": gaps,
    }


def write_fixture(root: Path) -> None:
    for rel_path, markers in REQUIRED_PATHS.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(markers) + "\n", encoding="utf-8")

    manifest_target = root / MANIFEST_PATH
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    manifest_target.write_text(
        json.dumps(fixture_manifest(), indent=2) + "\n",
        encoding="utf-8",
    )


def expect_problem(root: Path, mutate, expected: str) -> None:
    mutate(root)
    missing_files, missing_markers = validate(root)
    if missing_files:
        actual = ",".join(missing_files)
        raise SystemExit(f"phase10-core-self-test:unexpected_missing={actual}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-core-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_core_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-core-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        def remove_driver_id_marker(tmp_root: Path) -> None:
            target = tmp_root / "Documentation/zigux/phase10-virtio-core-survey.md"
            text = target.read_text(encoding="utf-8")
            target.write_text(
                text.replace("`drivers/virtio/virtio_driver_id.zig`", "`removed`", 1),
                encoding="utf-8",
            )

        expect_problem(
            root,
            remove_driver_id_marker,
            "Documentation/zigux/phase10-virtio-core-survey.md:`drivers/virtio/virtio_driver_id.zig`",
        )
        write_fixture(root)

        def drift_commit(tmp_root: Path) -> None:
            target = tmp_root / MANIFEST_PATH
            data = json.loads(target.read_text(encoding="utf-8"))
            data["surveyed_commit"] = "master"
            target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            drift_commit,
            f"{MANIFEST_PATH}:surveyed_commit:'master'",
        )
        write_fixture(root)

        def remove_gap(tmp_root: Path) -> None:
            target = tmp_root / MANIFEST_PATH
            data = json.loads(target.read_text(encoding="utf-8"))
            data["gaps"] = [
                gap for gap in data["gaps"] if gap["id"] != "phase10-core-lab-validation-evidence"
            ]
            target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        expect_problem(
            root,
            remove_gap,
            f"{MANIFEST_PATH}:gap_missing:phase10-core-lab-validation-evidence",
        )
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_driver_id.zig").unlink()
        missing_files, missing_markers = validate(root)
        if missing_markers:
            actual = ",".join(missing_markers)
            raise SystemExit(f"phase10-core-self-test:unexpected_markers={actual}")
        if "zigux/tests/phase10_virtio_driver_id.zig" not in missing_files:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(
                "phase10-core-self-test:expected_missing=zigux/tests/phase10_virtio_driver_id.zig:"
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

    missing_files, missing_markers = validate(Path(args.root))
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

    required_marker_count = sum(len(markers) for markers in REQUIRED_PATHS.values())
    print("PHASE10_CORE_PACKET=pass")
    print(f"PHASE10_CORE_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS) + 1}")
    print(f"PHASE10_CORE_REQUIRED_MARKER_COUNT={required_marker_count}")
    print(f"PHASE10_CORE_EXPECTED_GAP_COUNT={len(EXPECTED_GAP_FIELDS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
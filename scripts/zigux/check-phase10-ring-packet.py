#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path(__file__).resolve().parent
)

SURVEYED_COMMIT = "e42103fc02f544e1bd23a5ec2e5b584734f5af7d"

RING_DIRECT_FILES = [
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
]

FILES = [
    "scripts/zigux/check-phase10-ring-packet.py",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/Makefile",
    *RING_DIRECT_FILES,
]

MARKERS = {
    "Documentation/zigux/phase10-closure-evidence.md": [
        "python3 scripts/zigux/check-phase10-ring-packet.py",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "phase10-validate",
        "phase10-test",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "ring lane `P10-L10`",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        "Documentation/zigux/phase10-virtio-ring-slice.md",
        "zigux/tests/phase10_build.zig",
        "scripts/zigux/check-phase10-ring-packet.py",
    ],
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "`PHASE10_STATUS=parked`",
        "`PHASE10_SLICE=virtio-ring-survey`",
        "lane: `P10-L10`",
        SURVEYED_COMMIT,
        "drivers/virtio/virtio_ring.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "zigux/tests/phase10_virtio_ring.zig",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "zigux/tests/phase10_virtio_ring_survey.zig",
        "public raw reread path",
        "phase10-virtio-ring-survey-gate` is `starter_landed`",
        "phase10-ring-verify-replay` is `starter_landed`",
        "phase10-ring-lab-driver-bridge` remains `blocked_on_risky_transport`",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "# Phase 10 virtio_ring Slice",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "drivers/virtio/virtio_ring.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "zigux/tests/phase10_virtio_ring.zig",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "zigux/tests/phase10_virtio_ring_survey.zig",
        "public raw reread path",
        "broader shared validation packet",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "scripts/zigux/check-phase10-ring-packet.py",
        "zigux/tests/phase10_build.zig",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        "Documentation/zigux/phase10-virtio-ring-slice.md",
    ],
    "scripts/zigux/README.md": [
        "check-phase10-ring-packet.py",
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        "Documentation/zigux/phase10-virtio-ring-slice.md",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "zigux/tests/phase10_build.zig",
        "drivers/virtio/virtio_ring.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
    ],
    "zigux/tests/README.md": [
        "phase10_virtio_ring.zig",
        "phase10_virtio_ring_reset_reuse.zig",
        "phase10_virtio_ring_survey.zig",
        "phase10_virtio_ring_manifest.json",
        "phase10_build.zig",
    ],
    "zigux/tests/phase10_build.zig": [
        "phase10_virtio_ring_module",
        "\"phase10-virtio-ring-tests\"",
        "run_phase10_virtio_ring_tests",
        "phase10_virtio_ring_survey_module",
        "\"phase10-virtio-ring-survey-tests\"",
        "run_phase10_virtio_ring_survey_tests",
        "phase10_virtio_ring_verify_module",
        "\"phase10-virtio-ring-verify-tests\"",
        "run_phase10_virtio_ring_verify_tests",
    ],
    "zigux/tests/phase10_closure_manifest.json": [
        "\"scripts/zigux/check-phase10-ring-packet.py\"",
        "\"zigux/tests/phase10_virtio_ring_reset_reuse.zig\"",
        "\"drivers/virtio/virtio_ring_verify.zig\"",
        "\"zig build test --build-file zigux/tests/phase10_build.zig --summary all\"",
        "\"make -C zigux phase10-test\"",
        "\"make -C zigux phase10\"",
    ],
    "zigux/Makefile": [
        "phase10-validate:",
        "scripts/zigux/check-phase10-ring-packet.py --self-test",
        "scripts/zigux/check-phase10-ring-packet.py",
        "$(ZIG) build test --build-file zigux/tests/phase10_build.zig",
    ],
}

MANIFEST_SCALARS = {
    "lane_key": "P10-L10",
    "phase": "Phase 10",
    "surveyed_commit": SURVEYED_COMMIT,
    "anchor": "drivers/virtio/virtio_ring.c",
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
    "freeze_boundary_owner_lane": "P10-L11",
}

EXPECTED_ROADMAP_DESTINATIONS = ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]
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
EXPECTED_STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]
EXPECTED_FREEZE_IN_C_ANCHORS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]
EXPECTED_SUMMARY = {
    "virtio_ring_c_lines": 3940,
    "preexisting_phase10_test_files": 11,
    "preexisting_phase10_build_present": True,
    "preexisting_phase10_core_doc_present": True,
    "preexisting_virtio_core_zig_present": True,
    "preexisting_virtio_ring_zig_present": True,
    "preexisting_virtio_ring_doc_present": True,
    "preexisting_ring_verify_present": True,
}
EXPECTED_GAPS = {
    "phase10-build-gate": {
        "status": "starter_landed",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase10_build.zig",
    },
    "phase10-virtio-core-lab-starter": {
        "status": "starter_landed",
        "kind": "lab_driver_starter",
        "zigux_destination": "drivers/virtio/virtio.zig",
    },
    "phase10-virtio-ring-survey-gate": {
        "status": "starter_landed",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase10_virtio_ring_survey.zig",
    },
    "phase10-virtio-ring-survey-note": {
        "status": "starter_landed",
        "kind": "documentation",
        "zigux_destination": "Documentation/zigux/phase10-virtio-ring-survey.md",
    },
    "phase10-virtqueue-shape-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-used-buffer-polling-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-callback-enable-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-callback-delay-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-notify-prepare-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-notification-data-summary-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-broken-queue-poll-guard": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-queue-reset-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-queue-reset-readiness-helper": {
        "status": "starter_landed",
        "kind": "queue_wrapper",
        "zigux_destination": "drivers/virtio/virtio_ring.zig",
    },
    "phase10-ring-verify-replay": {
        "status": "starter_landed",
        "kind": "validation",
        "zigux_destination": "drivers/virtio/virtio_ring_verify.zig",
    },
    "phase10-virtio-ring-slice-note": {
        "status": "starter_landed",
        "kind": "documentation",
        "zigux_destination": "Documentation/zigux/phase10-virtio-ring-slice.md",
    },
    "phase10-ring-lab-driver-bridge": {
        "status": "blocked_on_risky_transport",
        "kind": "roadmap_gap",
        "zigux_destination": "drivers/virtio/virtio_mmio.zig",
    },
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    for rel_path, markers in MARKERS.items():
        text = read_text(root, rel_path)
        label = Path(rel_path).name
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{label}:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_ring_manifest.json"))
    for key, value in MANIFEST_SCALARS.items():
        if manifest.get(key) != value:
            missing_markers.append(f"manifest:{key}={manifest.get(key)!r}")
    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing_markers.append("manifest:roadmap_destinations")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing_markers.append("manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing_markers.append("manifest:forbidden_transport_claims")
    if manifest.get("study_only_anchors") != EXPECTED_STUDY_ONLY_ANCHORS:
        missing_markers.append("manifest:study_only_anchors")
    if manifest.get("freeze_in_c_anchors") != EXPECTED_FREEZE_IN_C_ANCHORS:
        missing_markers.append("manifest:freeze_in_c_anchors")

    summary = manifest.get("survey_summary", {})
    for key, value in EXPECTED_SUMMARY.items():
        if summary.get(key) != value:
            missing_markers.append(f"manifest:survey_summary:{key}={summary.get(key)!r}")

    gaps = manifest.get("gaps", [])
    if len(gaps) != len(EXPECTED_GAPS):
        missing_markers.append(f"manifest:gaps={len(gaps)}")
    gap_index = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}
    for gap_id, expected in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:missing_gap:{gap_id}")
            continue
        if gap.get("status") != expected["status"]:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')!r}")
        if gap.get("kind") != expected["kind"]:
            missing_markers.append(f"manifest:gap_kind:{gap_id}={gap.get('kind')!r}")
        if gap.get("zigux_destination") != expected["zigux_destination"]:
            missing_markers.append(
                f"manifest:gap_destination:{gap_id}={gap.get('zigux_destination')!r}"
            )

    return [], missing_markers


def write_fixture(root: Path) -> None:
    fixture = {
        "scripts/zigux/check-phase10-ring-packet.py": "# synthetic fixture for self-test\n",
        "Documentation/zigux/freeze-map.md": "# synthetic freeze map\n",
        "drivers/virtio/virtio_ring.zig": "pub const VirtioRingLab = struct {};\n",
        "drivers/virtio/virtio_ring_verify.zig": "test \"virtio ring reset readiness tracks unpublished, outstanding, and unpolled work\" {}\n",
        "zigux/tests/phase10_virtio_ring.zig": "test \"phase10 virtio ring reset clears queue bookkeeping but preserves queue shape for reuse\" {}\n",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig": "test \"phase10 virtio ring drained reset clears the broken flag so the queue can be reused\" {}\n",
        "zigux/tests/phase10_virtio_ring_survey.zig": "test \"phase10 virtio ring survey gate\" {}\n",
    }
    for rel_path, markers in MARKERS.items():
        if rel_path in fixture or rel_path == "zigux/tests/phase10_virtio_ring_manifest.json":
            continue
        fixture[rel_path] = "\n".join(markers) + "\n"
    fixture["zigux/tests/phase10_virtio_ring_manifest.json"] = json.dumps(
        {
            "lane_key": "P10-L10",
            "phase": "Phase 10",
            "surveyed_commit": SURVEYED_COMMIT,
            "anchor": "drivers/virtio/virtio_ring.c",
            "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "risky_transport_posture": "blocked_on_risky_transport",
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "architecture_council_reopen_required": True,
            "architecture_council_reopen_attached": False,
            "freeze_boundary_owner_lane": "P10-L11",
            "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
            "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
            "survey_summary": EXPECTED_SUMMARY,
            "gaps": [
                {
                    "id": gap_id,
                    "status": expected["status"],
                    "kind": expected["kind"],
                    "zigux_destination": expected["zigux_destination"],
                }
                for gap_id, expected in EXPECTED_GAPS.items()
            ],
        },
        indent=2,
    ) + "\n"
    for rel_path, content in fixture.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-ring-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        case_count = 0

        def expect_missing_marker(expected: str) -> None:
            nonlocal case_count
            _, markers = validate(root)
            if expected not in markers:
                raise SystemExit(f"phase10-ring-self-test:expected_marker_missing:{expected}")
            case_count += 1

        def expect_missing_file(expected: str) -> None:
            nonlocal case_count
            files, _ = validate(root)
            if expected not in files:
                raise SystemExit(f"phase10-ring-self-test:expected_file_missing:{expected}")
            case_count += 1

        def replace_once(rel_path: str, old: str, new: str, expected: str) -> None:
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            expect_missing_marker(expected)
            path.write_text(original, encoding="utf-8")

        def mutate_manifest(mutator, expected: str) -> None:
            path = root / "zigux/tests/phase10_virtio_ring_manifest.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            manifest = json.loads(json.dumps(original))
            mutator(manifest)
            path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            expect_missing_marker(expected)
            path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")

        replace_once(
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "public raw reread path",
            "stale fallback path",
            "phase10-virtio-ring-survey.md:public raw reread path",
        )
        replace_once(
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "phase10-virtio-ring-survey-gate` is `starter_landed`",
            "phase10-virtio-ring-survey-gate` is `contents_bridge_gap`",
            "phase10-virtio-ring-survey.md:phase10-virtio-ring-survey-gate` is `starter_landed`",
        )
        replace_once(
            "Documentation/zigux/phase10-virtio-ring-slice.md",
            "public raw reread path",
            "stale fallback path",
            "phase10-virtio-ring-slice.md:public raw reread path",
        )
        replace_once(
            "zigux/tests/phase10_build.zig",
            "run_phase10_virtio_ring_verify_tests",
            "run_phase10_virtio_ring_verify_gate",
            "phase10_build.zig:run_phase10_virtio_ring_verify_tests",
        )
        replace_once(
            "zigux/Makefile",
            "scripts/zigux/check-phase10-ring-packet.py --self-test",
            "scripts/zigux/check-phase10-ring-packet-drift.py --self-test",
            "Makefile:scripts/zigux/check-phase10-ring-packet.py --self-test",
        )
        mutate_manifest(
            lambda manifest: manifest["survey_summary"].__setitem__("preexisting_virtio_ring_zig_present", False),
            "manifest:survey_summary:preexisting_virtio_ring_zig_present=False",
        )
        mutate_manifest(
            lambda manifest: manifest["survey_summary"].__setitem__("preexisting_ring_verify_present", False),
            "manifest:survey_summary:preexisting_ring_verify_present=False",
        )
        mutate_manifest(
            lambda manifest: next(
                gap for gap in manifest["gaps"] if gap["id"] == "phase10-virtio-ring-survey-gate"
            ).__setitem__("status", "contents_bridge_gap"),
            "manifest:gap_status:phase10-virtio-ring-survey-gate='contents_bridge_gap'",
        )
        mutate_manifest(
            lambda manifest: next(
                gap for gap in manifest["gaps"] if gap["id"] == "phase10-virtqueue-shape-helper"
            ).__setitem__("status", "contents_bridge_gap"),
            "manifest:gap_status:phase10-virtqueue-shape-helper='contents_bridge_gap'",
        )
        mutate_manifest(
            lambda manifest: next(
                gap for gap in manifest["gaps"] if gap["id"] == "phase10-ring-lab-driver-bridge"
            ).__setitem__("status", "starter_landed"),
            "manifest:gap_status:phase10-ring-lab-driver-bridge='starter_landed'",
        )

        for rel_path in (
            "drivers/virtio/virtio_ring.zig",
            "drivers/virtio/virtio_ring_verify.zig",
            "zigux/tests/phase10_virtio_ring.zig",
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "zigux/tests/phase10_virtio_ring_survey.zig",
        ):
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.unlink()
            expect_missing_file(rel_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(original, encoding="utf-8")

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print(f"PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 virtio ring review packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a synthetic fixture tree.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_RING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_RING_MARKERS_END")
        return 1

    print("PHASE10_RING_PACKET=pass")
    print(f"PHASE10_RING_REQUIRED_FILE_COUNT={len(FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

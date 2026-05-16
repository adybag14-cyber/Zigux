#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

SURVEYED_COMMIT = "e42103fc02f544e1bd23a5ec2e5b584734f5af7d"

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
        "contents-bridge read path",
    ],
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "`PHASE10_STATUS=parked`",
        "`PHASE10_SLICE=virtio-ring-survey`",
        "lane: `P10-L10`",
        SURVEYED_COMMIT,
        "zigux/tests/phase10_build.zig",
        "scripts/zigux/check-phase10-ring-packet.py",
        "phase10-build-gate` is `starter_landed`",
        "phase10-virtio-ring-survey-gate` is a `contents_bridge_gap`",
        "phase10-virtio-ring-slice-note` remains `starter_landed`",
        "phase10-ring-verify-replay` is a `contents_bridge_gap`",
        "phase10-ring-lab-driver-bridge` remains `blocked_on_risky_transport`",
        "drivers/virtio/virtio_ring.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "zigux/tests/phase10_virtio_ring.zig",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "zigux/tests/phase10_virtio_ring_survey.zig",
        "broader Phase 10 validation packet evidence",
        "does not yet materialize through one consistent current-head contents-bridge path",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "# Phase 10 virtio_ring Slice",
        "zigux/tests/phase10_virtio_ring_manifest.json",
        "Documentation/zigux/phase10-virtio-ring-survey.md",
        "Documentation/zigux/phase10-virtio-ring-slice.md",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
        "Documentation/zigux/phase10-closure-evidence.md",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
        "Documentation/zigux/freeze-map.md",
        "scripts/zigux/README.md",
        "scripts/zigux/check-phase10-ring-packet.py",
        "zigux/tests/phase10_build.zig",
        "broader shared validation packet",
        "drivers/virtio/virtio_ring.zig",
        "drivers/virtio/virtio_ring_verify.zig",
        "zigux/tests/phase10_virtio_ring.zig",
        "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        "zigux/tests/phase10_virtio_ring_survey.zig",
        "one consistent contents-bridge path",
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
    "preexisting_virtio_ring_doc_present": True,
    "preexisting_virtio_core_zig_present": False,
    "preexisting_virtio_ring_zig_present": False,
    "preexisting_ring_verify_present": False,
}
EXPECTED_GAPS = {
    "phase10-build-gate": "starter_landed",
    "phase10-virtio-core-lab-starter": "repo_reality_gap",
    "phase10-virtio-ring-survey-gate": "contents_bridge_gap",
    "phase10-virtio-ring-survey-note": "starter_landed",
    "phase10-virtqueue-shape-helper": "contents_bridge_gap",
    "phase10-used-buffer-polling-helper": "contents_bridge_gap",
    "phase10-callback-enable-helper": "contents_bridge_gap",
    "phase10-callback-delay-helper": "contents_bridge_gap",
    "phase10-notify-prepare-helper": "contents_bridge_gap",
    "phase10-notification-data-summary-helper": "contents_bridge_gap",
    "phase10-broken-queue-poll-guard": "contents_bridge_gap",
    "phase10-queue-reset-helper": "contents_bridge_gap",
    "phase10-queue-reset-readiness-helper": "contents_bridge_gap",
    "phase10-ring-verify-replay": "contents_bridge_gap",
    "phase10-virtio-ring-slice-note": "starter_landed",
    "phase10-ring-lab-driver-bridge": "blocked_on_risky_transport",
}
EXPECTED_GAP_KINDS = {
    "phase10-build-gate": "validation",
    "phase10-virtio-core-lab-starter": "lab_driver_starter",
    "phase10-virtio-ring-survey-gate": "validation",
    "phase10-virtio-ring-survey-note": "documentation",
    "phase10-virtqueue-shape-helper": "queue_wrapper",
    "phase10-used-buffer-polling-helper": "queue_wrapper",
    "phase10-callback-enable-helper": "queue_wrapper",
    "phase10-callback-delay-helper": "queue_wrapper",
    "phase10-notify-prepare-helper": "queue_wrapper",
    "phase10-notification-data-summary-helper": "queue_wrapper",
    "phase10-broken-queue-poll-guard": "queue_wrapper",
    "phase10-queue-reset-helper": "queue_wrapper",
    "phase10-queue-reset-readiness-helper": "queue_wrapper",
    "phase10-ring-verify-replay": "validation",
    "phase10-virtio-ring-slice-note": "documentation",
    "phase10-ring-lab-driver-bridge": "roadmap_gap",
}
EXPECTED_GAP_DESTINATIONS = {
    "phase10-build-gate": "zigux/tests/phase10_build.zig",
    "phase10-virtio-core-lab-starter": "drivers/virtio/virtio.zig",
    "phase10-virtio-ring-survey-gate": "zigux/tests/phase10_virtio_ring_survey.zig",
    "phase10-virtio-ring-survey-note": "Documentation/zigux/phase10-virtio-ring-survey.md",
    "phase10-virtqueue-shape-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-used-buffer-polling-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-callback-enable-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-callback-delay-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-notify-prepare-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-notification-data-summary-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-broken-queue-poll-guard": "drivers/virtio/virtio_ring.zig",
    "phase10-queue-reset-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-queue-reset-readiness-helper": "drivers/virtio/virtio_ring.zig",
    "phase10-ring-verify-replay": "drivers/virtio/virtio_ring_verify.zig",
    "phase10-virtio-ring-slice-note": "Documentation/zigux/phase10-virtio-ring-slice.md",
    "phase10-ring-lab-driver-bridge": "drivers/virtio/virtio_mmio.zig",
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
    for gap_id, status in EXPECTED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing_markers.append(f"manifest:missing_gap:{gap_id}")
            continue
        if gap.get("status") != status:
            missing_markers.append(f"manifest:gap_status:{gap_id}={gap.get('status')!r}")
        expected_kind = EXPECTED_GAP_KINDS[gap_id]
        if gap.get("kind") != expected_kind:
            missing_markers.append(f"manifest:gap_kind:{gap_id}={gap.get('kind')!r}")
        expected_destination = EXPECTED_GAP_DESTINATIONS[gap_id]
        if gap.get("zigux_destination") != expected_destination:
            missing_markers.append(
                f"manifest:gap_destination:{gap_id}={gap.get('zigux_destination')!r}"
            )

    return missing_files, missing_markers


def write_fixture(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_fixture() -> dict[str, str]:
    fixture: dict[str, str] = {
        "scripts/zigux/check-phase10-ring-packet.py": "# synthetic fixture for self-test\n",
        "Documentation/zigux/freeze-map.md": "# synthetic freeze map\n",
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
                    "status": status,
                    "kind": EXPECTED_GAP_KINDS[gap_id],
                    "zigux_destination": EXPECTED_GAP_DESTINATIONS[gap_id],
                }
                for gap_id, status in EXPECTED_GAPS.items()
            ],
        },
        indent=2,
    ) + "\n"
    return fixture


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_") as tmp_dir:
        root = Path(tmp_dir)
        fixture = build_fixture()
        for rel_path, content in fixture.items():
            write_fixture(root, rel_path, content)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-ring-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        case_count = 0

        def run_missing_case(rel_path: str, old: str, new: str, expected: str) -> None:
            nonlocal case_count
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            _, markers = validate(root)
            if expected not in markers:
                raise SystemExit(f"phase10-ring-self-test:expected_marker_missing:{expected}")
            path.write_text(original, encoding="utf-8")
            case_count += 1

        def run_missing_file_case(rel_path: str) -> None:
            nonlocal case_count
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.unlink()
            files, _ = validate(root)
            if rel_path not in files:
                raise SystemExit(f"phase10-ring-self-test:expected_file_missing:{rel_path}")
            write_fixture(root, rel_path, original)
            case_count += 1

        def run_manifest_case(mutator, expected: str) -> None:
            nonlocal case_count
            manifest_path = root / "zigux/tests/phase10_virtio_ring_manifest.json"
            original = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest = json.loads(json.dumps(original))
            mutator(manifest)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            _, markers = validate(root)
            if expected not in markers:
                raise SystemExit(f"phase10-ring-self-test:expected_marker_missing:{expected}")
            manifest_path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
            case_count += 1

        run_missing_case(
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "scripts/zigux/check-phase10-ring-packet.py",
            "scripts/zigux/check-phase10-ring-packet-drift.py",
            "phase10-virtio-ring-survey.md:scripts/zigux/check-phase10-ring-packet.py",
        )
        run_missing_case(
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "phase10-build-gate` is `starter_landed`",
            "phase10-build-gate` is `repo_reality_gap`",
            "phase10-virtio-ring-survey.md:phase10-build-gate` is `starter_landed`",
        )
        run_missing_case(
            "Documentation/zigux/phase10-virtio-ring-slice.md",
            "broader shared validation packet",
            "missing shared validation packet",
            "phase10-virtio-ring-slice.md:broader shared validation packet",
        )
        run_missing_case(
            "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
            "contents-bridge read path",
            "repo-absence claim",
            "phase10-virtio-driver-lane-sequencing.md:contents-bridge read path",
        )
        run_missing_case(
            "scripts/zigux/README.md",
            "check-phase10-ring-packet.py",
            "check-phase10-ring-packet-drift.py",
            "README.md:check-phase10-ring-packet.py",
        )
        run_missing_case(
            "zigux/tests/phase10_build.zig",
            "run_phase10_virtio_ring_verify_tests",
            "run_phase10_virtio_ring_verify_gate",
            "phase10_build.zig:run_phase10_virtio_ring_verify_tests",
        )
        run_missing_case(
            "zigux/Makefile",
            "scripts/zigux/check-phase10-ring-packet.py --self-test",
            "scripts/zigux/check-phase10-ring-packet-drift.py --self-test",
            "Makefile:scripts/zigux/check-phase10-ring-packet.py --self-test",
        )
        run_missing_case(
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "zigux/tests/phase10_virtio_ring_reset_reuse_drift.zig",
            "phase10-phase11-phase13-tests-root-review-companion.md:zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        run_missing_case(
            "zigux/tests/phase10_closure_manifest.json",
            "\"scripts/zigux/check-phase10-ring-packet.py\"",
            "\"scripts/zigux/check-phase10-ring-packet-drift.py\"",
            "phase10_closure_manifest.json:\"scripts/zigux/check-phase10-ring-packet.py\"",
        )

        run_manifest_case(
            lambda manifest: manifest["survey_summary"].__setitem__("preexisting_phase10_build_present", False),
            "manifest:survey_summary:preexisting_phase10_build_present=False",
        )
        run_manifest_case(
            lambda manifest: manifest["survey_summary"].__setitem__("preexisting_phase10_core_doc_present", False),
            "manifest:survey_summary:preexisting_phase10_core_doc_present=False",
        )
        run_manifest_case(
            lambda manifest: manifest["survey_summary"].__setitem__("preexisting_ring_verify_present", True),
            "manifest:survey_summary:preexisting_ring_verify_present=True",
        )
        run_manifest_case(
            lambda manifest: manifest["gaps"].__setitem__(0, {"id": "phase10-build-gate", "status": "repo_reality_gap"}),
            "manifest:gap_status:phase10-build-gate='repo_reality_gap'",
        )
        run_manifest_case(
            lambda manifest: manifest["gaps"].__setitem__(2, {"id": "phase10-virtio-ring-survey-gate", "status": "starter_landed"}),
            "manifest:gap_status:phase10-virtio-ring-survey-gate='starter_landed'",
        )
        run_manifest_case(
            lambda manifest: manifest["gaps"].__setitem__(
                4,
                {
                    "id": "phase10-virtqueue-shape-helper",
                    "status": "contents_bridge_gap",
                    "kind": "validation",
                    "zigux_destination": "drivers/virtio/virtio_ring.zig",
                },
            ),
            "manifest:gap_kind:phase10-virtqueue-shape-helper='validation'",
        )
        run_manifest_case(
            lambda manifest: manifest["gaps"].__setitem__(
                4,
                {
                    "id": "phase10-virtqueue-shape-helper",
                    "status": "contents_bridge_gap",
                    "kind": "queue_wrapper",
                    "zigux_destination": "drivers/virtio/virtio_ring_drift.zig",
                },
            ),
            "manifest:gap_destination:phase10-virtqueue-shape-helper='drivers/virtio/virtio_ring_drift.zig'",
        )
        run_manifest_case(
            lambda manifest: manifest["gaps"].__setitem__(
                15,
                {
                    "id": "phase10-ring-lab-driver-bridge",
                    "status": "blocked_on_risky_transport",
                    "kind": "validation",
                    "zigux_destination": "drivers/virtio/virtio_mmio.zig",
                },
            ),
            "manifest:gap_kind:phase10-ring-lab-driver-bridge='validation'",
        )
        run_manifest_case(
            lambda manifest: manifest["gaps"].__setitem__(
                15,
                {
                    "id": "phase10-ring-lab-driver-bridge",
                    "status": "blocked_on_risky_transport",
                    "kind": "roadmap_gap",
                    "zigux_destination": "drivers/virtio/virtio_probe_bridge.zig",
                },
            ),
            "manifest:gap_destination:phase10-ring-lab-driver-bridge='drivers/virtio/virtio_probe_bridge.zig'",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("allowed_evidence_kinds", ["driver_local_lab_slices"]),
            "manifest:allowed_evidence_kinds",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("architecture_council_reopen_required", False),
            "manifest:architecture_council_reopen_required=False",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("freeze_boundary_owner_lane", "P10-L10"),
            "manifest:freeze_boundary_owner_lane='P10-L10'",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("study_only_anchors", ["kernel/workqueue.c"]),
            "manifest:study_only_anchors",
        )
        run_manifest_case(
            lambda manifest: manifest.__setitem__("freeze_in_c_anchors", ["kernel/sched/core.c"]),
            "manifest:freeze_in_c_anchors",
        )
        run_missing_file_case("zigux/tests/phase10_build.zig")
        run_missing_file_case("Documentation/zigux/phase10-virtio-ring-survey.md")

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
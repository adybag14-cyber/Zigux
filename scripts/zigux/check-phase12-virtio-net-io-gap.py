#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


REQUIRED_FILES = (
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_net_survey.zig",
)

ABSENT_FILES = (
    "drivers/net/virtio_net.zig",
    "zigux/tests/phase12_virtio_net.zig",
)

SURVEY_MARKERS = (
    "PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only",
    "the packet still does not claim live DMA-safe receive ownership",
    "smoke still runs through the direct build-file command",
    "explicit receive-refill and transmit-recycle readiness booleans",
)

MANIFEST_MARKERS = (
    '"lane_key": "P12-L04"',
    '"phase": "Phase 12"',
    '"verified_on": "2026-05-25"',
    '"status": "split_helper_packet_present_runtime_data_path_blocked"',
    '"status": "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"',
    '"status": "throughput_parity_helper_present_review_only_runtime_completion_missing"',
    '"status": "split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"',
    '"id": "phase12-virtio-net-runtime-data-path"',
    '"status": "blocked_on_dma_transport_runtime"',
    "live DMA-safe receive ownership",
    "page-pool wiring",
    "transport-backed submit flow",
    "interrupt-backed completion handling",
)

HELPER_MARKERS = {
    "drivers/net/virtio_net_queue_resume.zig": (
        "receive_submission_owner",
        "transmit_submission_owner",
        "control_queue_restore",
        "probe_snapshot_replay",
        "can_resume_queues",
    ),
    "drivers/net/virtio_net_receive_refill_replay.zig": (
        "descriptors_pending_repost",
        ".descriptor_repost",
        "replay_ready",
        "queue_pairs_preserved",
    ),
    "drivers/net/virtio_net_transmit_recycle.zig": (
        "CompletedOwnershipDisposition",
        "returns_completed_ownership_to_driver",
        ".wake_queue",
        "free_descriptors_after",
    ),
    "drivers/net/virtio_net_post_reset_replay.zig": (
        "PostResetReplayCheckpoint",
        "after_probe_snapshot_replay",
        "resumes_receive_submission",
        "queues_ready_for_driver_ownership",
    ),
    "drivers/net/virtio_net_throughput_parity.zig": (
        "needs_post_reset_probe_replay",
        "receive_refill_ready",
        "transmit_recycle_ready",
        "throughput_ratio_pct",
    ),
}

SURVEY_GATE_MARKERS = (
    "phase12 virtio net survey manifest tracks the shared-build survey-gate coverage truthfully",
    "phase12 virtio net survey note reflects the shared survey-gate route",
    "phase12 virtio net survey gate keeps the present files and shared routes explicit",
    'try std.testing.expect(!try pathExists("drivers/net/virtio_net.zig"));',
    'try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net.zig"));',
)


class CheckError(RuntimeError):
    pass


def require_file(root: Path, rel: str) -> Path:
    path = root / rel
    if not path.is_file():
        raise CheckError(f"missing required file: {rel}")
    return path


def read_text(root: Path, rel: str) -> str:
    return require_file(root, rel).read_text(encoding="utf-8")


def require_markers(rel: str, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{rel}: missing marker {marker!r}")


def run_check(root: Path) -> None:
    for rel in REQUIRED_FILES:
        require_file(root, rel)
    for rel in ABSENT_FILES:
        if (root / rel).exists():
            raise CheckError(f"{rel}: stale direct-path scaffold unexpectedly present")

    require_markers(
        "Documentation/zigux/phase12-virtio-net-survey.md",
        read_text(root, "Documentation/zigux/phase12-virtio-net-survey.md"),
        SURVEY_MARKERS,
    )

    manifest_text = read_text(root, "zigux/tests/phase12_virtio_net_manifest.json")
    require_markers("zigux/tests/phase12_virtio_net_manifest.json", manifest_text, MANIFEST_MARKERS)
    manifest = json.loads(manifest_text)
    if manifest.get("lane_key") != "P12-L04":
        raise CheckError("zigux/tests/phase12_virtio_net_manifest.json: lane_key drifted from P12-L04")
    if manifest.get("phase") != "Phase 12":
        raise CheckError("zigux/tests/phase12_virtio_net_manifest.json: phase drifted from Phase 12")

    for rel, markers in HELPER_MARKERS.items():
        require_markers(rel, read_text(root, rel), markers)

    require_markers(
        "zigux/tests/phase12_virtio_net_survey.zig",
        read_text(root, "zigux/tests/phase12_virtio_net_survey.zig"),
        SURVEY_GATE_MARKERS,
    )


def write_fixture(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    write_fixture(
        root,
        "Documentation/zigux/phase12-virtio-net-survey.md",
        "\n".join(SURVEY_MARKERS) + "\n",
    )
    write_fixture(
        root,
        "zigux/tests/phase12_virtio_net_manifest.json",
        "{\n"
        '  "lane_key": "P12-L04",\n'
        '  "phase": "Phase 12",\n'
        '  "verified_on": "2026-05-25",\n'
        '  "roadmap_gap_check": {\n'
        '    "dma_safe_abstractions": {\n'
        '      "status": "split_helper_packet_present_runtime_data_path_blocked",\n'
        '      "current_surface": "live DMA-safe receive ownership page-pool wiring transport-backed submit flow",\n'
        '      "blocked_by": "interrupt-backed completion handling"\n'
        "    },\n"
        '    "queueing_correctness": {\n'
        '      "status": "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"\n'
        "    },\n"
        '    "throughput_and_recovery_parity": {\n'
        '      "status": "throughput_parity_helper_present_review_only_runtime_completion_missing"\n'
        "    },\n"
        '    "segmented_rollout": {\n'
        '      "status": "split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"\n'
        "    }\n"
        "  },\n"
        '  "gaps": [{"id": "phase12-virtio-net-runtime-data-path", "status": "blocked_on_dma_transport_runtime"}]\n'
        "}\n",
    )
    for rel, markers in HELPER_MARKERS.items():
        write_fixture(root, rel, "\n".join(markers) + "\n")
    write_fixture(
        root,
        "zigux/tests/phase12_virtio_net_survey.zig",
        "\n".join(SURVEY_GATE_MARKERS) + "\n",
    )


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-virtio-net-io-gap-") as tmp:
        root = Path(tmp)

        write_fixture_tree(root)
        run_check(root)
        cases += 1

        broken_survey = root / "Documentation/zigux/phase12-virtio-net-survey.md"
        broken_survey.write_text("broken\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError:
            pass
        else:
            raise AssertionError("expected survey marker failure")
        cases += 1

        write_fixture_tree(root)
        stale_direct = root / "drivers/net/virtio_net.zig"
        stale_direct.parent.mkdir(parents=True, exist_ok=True)
        stale_direct.write_text("// stale\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError:
            pass
        else:
            raise AssertionError("expected stale direct-path failure")
        cases += 1

        write_fixture_tree(root)
        broken_manifest = root / "zigux/tests/phase12_virtio_net_manifest.json"
        broken_manifest.writeText = broken_manifest.write_text
        broken_manifest.writeText(
            broken_manifest.read_text(encoding="utf-8").replace(
                "blocked_on_dma_transport_runtime",
                "missing",
            ),
            encoding="utf-8",
        )
        try:
            run_check(root)
        except CheckError:
            pass
        else:
            raise AssertionError("expected manifest runtime-gap failure")
        cases += 1

    print("PHASE12_VIRTIO_NET_IO_GAP_SELF_TEST=pass")
    print(f"PHASE12_VIRTIO_NET_IO_GAP_SELF_TEST_CASES={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed checker for the bounded Phase 12 virtio_net runtime I/O gap survey."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(args.root.resolve())
    except CheckError as err:
        print("PHASE12_VIRTIO_NET_IO_GAP=fail")
        print(str(err))
        return 1

    print("PHASE12_VIRTIO_NET_IO_GAP=pass")
    print("PHASE12_VIRTIO_NET_IO_GAP_SCOPE=virtio_net_runtime_io_gap_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

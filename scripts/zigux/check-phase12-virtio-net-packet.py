#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


REQUIRED_FILES = [
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "drivers/net/virtio_net.zig",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
]

MANIFEST_MARKERS = [
    '"lane_key": "P12-L02"',
    '"phase": "Phase 12"',
    '"anchor": "drivers/net/virtio_net.c"',
    '"status": "starter_queue_summary_control_queue_recovery_refill_payload_shape_transmit_recycle_and_post_reset_replay_present_direct_gate_present_shared_smoke_present"',
    '"status": "starter_control_queue_payload_shape_refill_transmit_recycle_and_post_reset_replay_present_runtime_completion_missing"',
    '"status": "starter_queue_summary_control_queue_recovery_refill_payload_shape_transmit_recycle_post_reset_replay_direct_lab_present_shared_route_present"',
    '"id": "phase12-build-gate"',
    '"status": "shared_build_present_with_queue_resume_and_transmit_recycle_replays_post_reset_replay_still_direct_only"',
    '"id": "phase12-virtio-net-post-reset-replay-followup"',
    '"zigux_destination": "drivers/net/virtio_net_post_reset_replay.zig"',
    '"id": "phase12-virtio-net-runtime-data-path"',
    '"status": "blocked_on_dma_transport_runtime"',
]

SURVEY_NOTE_MARKERS = [
    "`PHASE12_STATUS=starter-present-post-reset-replay-followup`",
    "lane owner: `P12-L02`",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "summarizeQueueTopology()",
    "planControlQueuePayloadShape()",
    "summarizePostResetReplay()",
    "shared Phase 12 smoke and test routes keep the dedicated `virtio_net` syntax-lab shard plus the queue-resume and transmit-recycle replays reachable",
    "post-reset replay still remains a dedicated driver-local test outside the shared Phase 12 build route",
    "while the post-reset replay remains outside `zigux/tests/phase12_build.zig`",
    "still does not claim live DMA-safe receive ownership",
]

SURVEY_GATE_MARKERS = [
    "phase12 virtio net survey manifest keeps the bounded post reset replay packet truthful",
    "phase12 virtio net survey note stays aligned with the bounded post reset replay follow-up",
    "phase12 virtio net survey gate keeps present lane files explicit",
    "phase12 virtio net survey gate keeps shared build surface explicit about post reset replay",
    "phase12 virtio net syntax lab keeps payload-shaping and recovery markers explicit",
    "phase12 virtio net survey gate keeps transmit recycle helper and replay markers explicit",
    'try std.testing.expectEqualStrings("P12-L02", manifest.lane_key);',
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "summarizePostResetReplay()",
    "phase12_virtio_net_queue_resume.zig",
    "phase12-virtio-net-queue-resume-tests",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12-virtio-net-transmit-recycle-tests",
    'phase12_virtio_net_post_reset_replay.zig") == null',
    '"phase12-virtio-net-post-reset-replay-tests") == null',
]

SYNTAX_LAB_MARKERS = [
    "phase12 virtio net syntax lab keeps control queue payload shaping separate from runtime commands",
    "phase12 virtio net syntax lab keeps rss payload shaping aligned with tunnel-header recovery",
    "planControlQueuePayloadShape",
    "controlQueueRecoveryPlan",
    "rss_config_payload_bytes",
    "requires_hash_report_payload",
    "requires_mergeable_buffer_refill",
]

BUILD_MARKERS = [
    "../../drivers/net/virtio_net.zig",
    '"phase12_virtio_net.zig"',
    '"phase12_virtio_net_syntax_lab.zig"',
    "phase12-virtio-net-tests",
    "phase12-virtio-net-syntax-lab-tests",
    'run_virtio_net_contract_tests.setCwd(b.path("../.."));',
    'run_virtio_net_syntax_tests.setCwd(b.path("../.."));',
    "../../drivers/net/virtio_net_queue_resume.zig",
    '"phase12_virtio_net_queue_resume.zig"',
    "phase12-virtio-net-queue-resume-tests",
    'run_virtio_net_queue_resume_tests.setCwd(b.path("../.."));',
    "../../drivers/net/virtio_net_transmit_recycle.zig",
    '"phase12_virtio_net_transmit_recycle.zig"',
    "phase12-virtio-net-transmit-recycle-tests",
    'run_virtio_net_transmit_recycle_tests.setCwd(b.path("../.."));',
    "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
    "test_step.dependOn(&run_virtio_net_contract_tests.step);",
]

MAKEFILE_MARKERS = [
    "phase12-smoke",
    "phase12-test",
    "phase12:",
]


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.is_file():
        raise CheckError(f"missing required file: {relpath}")
    return path.read_text(encoding="utf-8")


def require_markers(text: str, relpath: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{relpath}: missing marker {marker!r}")


def run_check(root: Path) -> None:
    for relpath in REQUIRED_FILES:
        if not (root / relpath).is_file():
            raise CheckError(f"missing required file: {relpath}")

    manifest_text = read_text(root, "zigux/tests/phase12_virtio_net_manifest.json")
    require_markers(manifest_text, "zigux/tests/phase12_virtio_net_manifest.json", MANIFEST_MARKERS)

    manifest = json.loads(manifest_text)
    if manifest.get("lane_key") != "P12-L02":
        raise CheckError("zigux/tests/phase12_virtio_net_manifest.json: lane_key drifted from P12-L02")
    if manifest.get("phase") != "Phase 12":
        raise CheckError("zigux/tests/phase12_virtio_net_manifest.json: phase drifted from Phase 12")

    survey_note = read_text(root, "Documentation/zigux/phase12-virtio-net-survey.md")
    require_markers(survey_note, "Documentation/zigux/phase12-virtio-net-survey.md", SURVEY_NOTE_MARKERS)

    survey_gate = read_text(root, "zigux/tests/phase12_virtio_net_survey.zig")
    require_markers(survey_gate, "zigux/tests/phase12_virtio_net_survey.zig", SURVEY_GATE_MARKERS)

    syntax_lab = read_text(root, "zigux/tests/phase12_virtio_net_syntax_lab.zig")
    require_markers(syntax_lab, "zigux/tests/phase12_virtio_net_syntax_lab.zig", SYNTAX_LAB_MARKERS)

    build_text = read_text(root, "zigux/tests/phase12_build.zig")
    require_markers(build_text, "zigux/tests/phase12_build.zig", BUILD_MARKERS)
    if "phase12_virtio_net_post_reset_replay.zig" in build_text:
        raise CheckError(
            "zigux/tests/phase12_build.zig: post-reset replay unexpectedly entered the shared build route"
        )
    if "phase12-virtio-net-post-reset-replay-tests" in build_text:
        raise CheckError(
            "zigux/tests/phase12_build.zig: post-reset replay run step unexpectedly entered the shared build route"
        )

    makefile_text = read_text(root, "zigux/Makefile")
    require_markers(makefile_text, "zigux/Makefile", MAKEFILE_MARKERS)


def make_fixture_tree(root: Path) -> None:
    file_payloads = {
        "Documentation/zigux/phase12-virtio-net-survey.md": "\n".join(SURVEY_NOTE_MARKERS) + "\n",
        "drivers/net/virtio_net.zig": "// fixture\n",
        "drivers/net/virtio_net_queue_resume.zig": "// fixture\n",
        "drivers/net/virtio_net_transmit_recycle.zig": "// fixture\n",
        "drivers/net/virtio_net_post_reset_replay.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_queue_resume.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_transmit_recycle.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_post_reset_replay.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_syntax_lab.zig": "\n".join(SYNTAX_LAB_MARKERS) + "\n",
        "zigux/tests/phase12_virtio_net_survey.zig": "\n".join(f"// {marker}" for marker in SURVEY_GATE_MARKERS) + "\n",
        "zigux/tests/phase12_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKEFILE_MARKERS) + "\n",
        "zigux/tests/phase12_virtio_net_manifest.json": json.dumps(
            {
                "lane_key": "P12-L02",
                "phase": "Phase 12",
                "anchor": "drivers/net/virtio_net.c",
                "roadmap_gap_check": {
                    "queueing_correctness": {
                        "status": "starter_queue_summary_control_queue_recovery_refill_payload_shape_transmit_recycle_and_post_reset_replay_present_direct_gate_present_shared_smoke_present"
                    },
                    "throughput_and_recovery_parity": {
                        "status": "starter_control_queue_payload_shape_refill_transmit_recycle_and_post_reset_replay_present_runtime_completion_missing"
                    },
                    "segmented_rollout": {
                        "status": "starter_queue_summary_control_queue_recovery_refill_payload_shape_transmit_recycle_post_reset_replay_direct_lab_present_shared_route_present"
                    },
                },
                "gaps": [
                    {
                        "id": "phase12-build-gate",
                        "status": "shared_build_present_with_queue_resume_and_transmit_recycle_replays_post_reset_replay_still_direct_only",
                    },
                    {
                        "id": "phase12-virtio-net-post-reset-replay-followup",
                        "zigux_destination": "drivers/net/virtio_net_post_reset_replay.zig",
                        "status": "landed_on_master",
                    },
                    {
                        "id": "phase12-virtio-net-runtime-data-path",
                        "status": "blocked_on_dma_transport_runtime",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    }

    for relpath, payload in file_payloads.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_fixture_tree(root)

        run_check(root)
        case_count += 1

        broken_note = root / "Documentation/zigux/phase12-virtio-net-survey.md"
        broken_note.write_text("broken\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError as err:
            if "phase12-virtio-net-survey.md" not in str(err):
                raise
        else:
            raise AssertionError("expected survey-note marker failure")
        case_count += 1

        make_fixture_tree(root)
        broken_manifest = root / "zigux/tests/phase12_virtio_net_manifest.json"
        broken_manifest.write_text(
            broken_manifest.read_text(encoding="utf-8").replace(
                "shared_build_present_with_queue_resume_and_transmit_recycle_replays_post_reset_replay_still_direct_only",
                "shared_build_present_with_direct_virtio_net_syntax_lab_and_transmit_recycle_replay",
            ),
            encoding="utf-8",
        )
        try:
            run_check(root)
        except CheckError as err:
            if "phase12_virtio_net_manifest.json" not in str(err):
                raise
        else:
            raise AssertionError("expected manifest marker failure")
        case_count += 1

        make_fixture_tree(root)
        broken_build = root / "zigux/tests/phase12_build.zig"
        broken_build.write_text(
            broken_build.read_text(encoding="utf-8").replace(
                "phase12-virtio-net-queue-resume-tests\n", ""
            ),
            encoding="utf-8",
        )
        try:
            run_check(root)
        except CheckError as err:
            if "phase12_build.zig" not in str(err):
                raise
        else:
            raise AssertionError("expected shared-build marker failure")
        case_count += 1

        make_fixture_tree(root)
        broken_build = root / "zigux/tests/phase12_build.zig"
        broken_build.write_text(
            broken_build.read_text(encoding="utf-8") + 'phase12_virtio_net_post_reset_replay.zig\n',
            encoding="utf-8",
        )
        try:
            run_check(root)
        except CheckError as err:
            if "phase12_build.zig" not in str(err):
                raise
        else:
            raise AssertionError("expected post-reset direct-only failure")
        case_count += 1

        make_fixture_tree(root)
        broken_syntax_lab = root / "zigux/tests/phase12_virtio_net_syntax_lab.zig"
        broken_syntax_lab.write_text("broken\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError as err:
            if "phase12_virtio_net_syntax_lab.zig" not in str(err):
                raise
        else:
            raise AssertionError("expected syntax-lab marker failure")
        case_count += 1

        make_fixture_tree(root)
        broken_makefile = root / "zigux/Makefile"
        broken_makefile.write_text("phase12-smoke\nphase12-test\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError as err:
            if "zigux/Makefile" not in str(err):
                raise
        else:
            raise AssertionError("expected makefile marker failure")
        case_count += 1

    print("PHASE12_VIRTIO_NET_PACKET_SELF_TEST=pass")
    print(f"PHASE12_VIRTIO_NET_PACKET_SELF_TEST_CASES={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(args.root.resolve())
    except CheckError as err:
        print("PHASE12_VIRTIO_NET_PACKET=fail")
        print(str(err))
        return 1

    print("PHASE12_VIRTIO_NET_PACKET=pass")
    print("PHASE12_VIRTIO_NET_PACKET_SCOPE=virtio_net_packet_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

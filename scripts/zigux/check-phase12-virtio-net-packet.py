#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


REQUIRED_FILES = [
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
]

ABSENT_FILES = [
    "drivers/net/virtio_net.zig",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
]

MANIFEST_MARKERS = [
    '"lane_key": "P12-L04"',
    '"phase": "Phase 12"',
    '"anchor": "drivers/net/virtio_net.c"',
    '"status": "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"',
    '"status": "throughput_parity_helper_present_review_only_runtime_completion_missing"',
    '"status": "split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"',
    '"id": "phase12-build-gate"',
    '"status": "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays"',
    '"id": "phase12-virtio-net-survey-gate"',
    '"zigux_destination": "zigux/tests/phase12_virtio_net_survey.zig"',
    '"id": "phase12-virtio-net-runtime-data-path"',
    '"status": "blocked_on_dma_transport_runtime"',
]

SURVEY_NOTE_MARKERS = [
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "lane owner: `P12-L04`",
    "scope: keep the bounded queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate review packet truthful without reopening live runtime data-path work",
    "verified head: `6791c1229b883d9f0acf9ec70e4159db1c9d1bf6`",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "`zigux/tests/phase12_build.zig` plus `zigux/Makefile` now keep the dedicated `virtio_net_queue_resume`, `virtio_net_receive_refill_replay`, `virtio_net_transmit_recycle`, `virtio_net_post_reset_replay`, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
    "current `master` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper proof for that sextet",
    "the throughput helper remains review-only throughput-ratio checks, but now also surfaces explicit receive-refill and transmit-recycle readiness booleans rather than measured transport throughput evidence",
    "the packet still does not claim live DMA-safe receive ownership",
    "performance-risk wording refresh remains bounded below runtime queue execution",
]

SURVEY_GATE_MARKERS = [
    'test "phase12 virtio net survey manifest tracks the shared-build survey-gate coverage truthfully"',
    'test "phase12 virtio net survey note reflects the shared survey-gate route"',
    'test "phase12 virtio net survey gate keeps the present files and shared routes explicit"',
    'try std.testing.expectEqualStrings("P12-L04", manifest.lane_key);',
    '"split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"',
    '"split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"',
    '"shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays"',
    'try expectContains(survey_note, "PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only");',
    'try expectContains(survey_note, "throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes");',
    'try expectContains(survey_note, "`phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper proof");',
    'try expectContains(build_zig, "phase12_virtio_net_survey.zig");',
    'try expectContains(build_zig, "phase12-virtio-net-survey-tests");',
    'try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_zig, "b.addTest(.{"));',
    'try std.testing.expectEqual(@as(usize, 6), std.mem.count(u8, build_zig, "smoke_step.dependOn("));',
    'try std.testing.expect(!try pathExists("drivers/net/virtio_net.zig"));',
    'try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net.zig"));',
    'try std.testing.expect(!try pathExists("zigux/tests/phase12_virtio_net_syntax_lab.zig"));',
    'try expectContains(makefile, "phase12: phase12-validate phase12-smoke phase12-test");',
]

BUILD_MARKERS = [
    "../../drivers/net/virtio_net_queue_resume.zig",
    '"phase12_virtio_net_queue_resume.zig"',
    "phase12-virtio-net-queue-resume-tests",
    "../../drivers/net/virtio_net_receive_refill_replay.zig",
    '"phase12_virtio_net_receive_refill_replay.zig"',
    "phase12-virtio-net-receive-refill-replay-tests",
    "../../drivers/net/virtio_net_transmit_recycle.zig",
    '"phase12_virtio_net_transmit_recycle.zig"',
    "phase12-virtio-net-transmit-recycle-tests",
    "../../drivers/net/virtio_net_post_reset_replay.zig",
    '"phase12_virtio_net_post_reset_replay.zig"',
    "phase12-virtio-net-post-reset-replay-tests",
    "../../drivers/net/virtio_net_throughput_parity.zig",
    '"phase12_virtio_net_throughput_parity.zig"',
    "phase12-virtio-net-throughput-parity-tests",
    '"phase12_virtio_net_survey.zig"',
    "phase12-virtio-net-survey-tests",
    "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
    "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    "test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
    "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
    "test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
    "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "test_step.dependOn(&run_virtio_net_survey_tests.step);",
]

MAKEFILE_MARKERS = [
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
]

STALE_BUILD_MARKERS = [
    "../../drivers/net/virtio_net.zig",
    '"phase12_virtio_net.zig"',
    "phase12-virtio-net-tests",
    '"phase12_virtio_net_syntax_lab.zig"',
    "phase12-virtio-net-syntax-lab-tests",
]

STALE_MAKEFILE_MARKERS = [
    "phase12: phase12-smoke phase12-test",
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


def require_absent(root: Path, relpath: str) -> None:
    if (root / relpath).exists():
        raise CheckError(f"{relpath}: stale scaffold unexpectedly present")


def run_check(root: Path) -> None:
    for relpath in REQUIRED_FILES:
        if not (root / relpath).is_file():
            raise CheckError(f"missing required file: {relpath}")

    for relpath in ABSENT_FILES:
        require_absent(root, relpath)

    manifest_text = read_text(root, "zigux/tests/phase12_virtio_net_manifest.json")
    require_markers(manifest_text, "zigux/tests/phase12_virtio_net_manifest.json", MANIFEST_MARKERS)

    manifest = json.loads(manifest_text)
    if manifest.get("lane_key") != "P12-L04":
        raise CheckError("zigux/tests/phase12_virtio_net_manifest.json: lane_key drifted from P12-L04")
    if manifest.get("phase") != "Phase 12":
        raise CheckError("zigux/tests/phase12_virtio_net_manifest.json: phase drifted from Phase 12")

    survey_note = read_text(root, "Documentation/zigux/phase12-virtio-net-survey.md")
    require_markers(survey_note, "Documentation/zigux/phase12-virtio-net-survey.md", SURVEY_NOTE_MARKERS)

    survey_gate = read_text(root, "zigux/tests/phase12_virtio_net_survey.zig")
    require_markers(survey_gate, "zigux/tests/phase12_virtio_net_survey.zig", SURVEY_GATE_MARKERS)

    build_text = read_text(root, "zigux/tests/phase12_build.zig")
    require_markers(build_text, "zigux/tests/phase12_build.zig", BUILD_MARKERS)
    for stale_marker in STALE_BUILD_MARKERS:
        if stale_marker in build_text:
            raise CheckError(
                f"zigux/tests/phase12_build.zig: stale monolithic or syntax-lab marker still present {stale_marker!r}"
            )

    makefile_text = read_text(root, "zigux/Makefile")
    require_markers(makefile_text, "zigux/Makefile", MAKEFILE_MARKERS)
    for stale_marker in STALE_MAKEFILE_MARKERS:
        if stale_marker in makefile_text:
            raise CheckError(
                f"zigux/Makefile: stale Phase 12 wrapper marker still present {stale_marker!r}"
            )


def make_fixture_tree(root: Path) -> None:
    file_payloads = {
        "Documentation/zigux/phase12-virtio-net-survey.md": "\n".join(SURVEY_NOTE_MARKERS) + "\n",
        "drivers/net/virtio_net_queue_resume.zig": "// fixture\n",
        "drivers/net/virtio_net_receive_refill_replay.zig": "// fixture\n",
        "drivers/net/virtio_net_transmit_recycle.zig": "// fixture\n",
        "drivers/net/virtio_net_post_reset_replay.zig": "// fixture\n",
        "drivers/net/virtio_net_throughput_parity.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_queue_resume.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_receive_refill_replay.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_transmit_recycle.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_post_reset_replay.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_throughput_parity.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_survey.zig": "\n".join(f"// {marker}" for marker in SURVEY_GATE_MARKERS) + "\n",
        "zigux/tests/phase12_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKEFILE_MARKERS) + "\n",
        "zigux/tests/phase12_virtio_net_manifest.json": json.dumps(
            {
                "lane_key": "P12-L04",
                "phase": "Phase 12",
                "anchor": "drivers/net/virtio_net.c",
                "roadmap_gap_check": {
                    "queueing_correctness": {
                        "status": "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"
                    },
                    "throughput_and_recovery_parity": {
                        "status": "throughput_parity_helper_present_review_only_runtime_completion_missing"
                    },
                    "segmented_rollout": {
                        "status": "split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"
                    },
                },
                "gaps": [
                    {
                        "id": "phase12-build-gate",
                        "status": "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays",
                    },
                    {
                        "id": "phase12-virtio-net-survey-gate",
                        "zigux_destination": "zigux/tests/phase12_virtio_net_survey.zig",
                        "status": "survey_present_shared_route_present",
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

    def fresh_root() -> Path:
        tmp = tempfile.TemporaryDirectory()
        roots.append(tmp)
        root = Path(tmp.name)
        make_fixture_tree(root)
        return root

    roots: list[tempfile.TemporaryDirectory[str]] = []
    try:
        root = fresh_root()
        run_check(root)
        case_count += 1

        root = fresh_root()
        (root / "Documentation/zigux/phase12-virtio-net-survey.md").write_text("broken\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError as err:
            if "phase12-virtio-net-survey.md" not in str(err):
                raise
        else:
            raise AssertionError("expected survey-note marker failure")
        case_count += 1

        root = fresh_root()
        broken_manifest = root / "zigux/tests/phase12_virtio_net_manifest.json"
        broken_manifest.write_text(
            broken_manifest.read_text(encoding="utf-8").replace(
                "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays",
                "stale_old_status",
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

        root = fresh_root()
        broken_build = root / "zigux/tests/phase12_build.zig"
        broken_build.write_text(
            broken_build.read_text(encoding="utf-8").replace(
                "phase12-virtio-net-survey-tests\n",
                "",
            ),
            encoding="utf-8",
        )
        try:
            run_check(root)
        except CheckError as err:
            if "phase12_build.zig" not in str(err):
                raise
        else:
            raise AssertionError("expected build marker failure")
        case_count += 1

        root = fresh_root()
        stale_file = root / "zigux/tests/phase12_virtio_net_syntax_lab.zig"
        stale_file.parent.mkdir(parents=True, exist_ok=True)
        stale_file.write_text("// stale\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError as err:
            if "phase12_virtio_net_syntax_lab.zig" not in str(err):
                raise
        else:
            raise AssertionError("expected stale scaffold failure")
        case_count += 1

        root = fresh_root()
        (root / "zigux/tests/phase12_virtio_net_survey.zig").writeText("broken\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError as err:
            if "phase12_virtio_net_survey.zig" not in str(err):
                raise
        else:
            raise AssertionError("expected survey-gate marker failure")
        case_count += 1

        root = fresh_root()
        (root / "zigux/Makefile").write_text("phase12-smoke:\nphase12-test:\n", encoding="utf-8")
        try:
            run_check(root)
        except CheckError as err:
            if "zigux/Makefile" not in str(err):
                raise
        else:
            raise AssertionError("expected makefile marker failure")
        case_count += 1

        root = fresh_root()
        makefile = root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "phase12: phase12-validate phase12-smoke phase12-test",
                "phase12: phase12-smoke phase12-test",
            ),
            encoding="utf-8",
        )
        try:
            run_check(root)
        except CheckError as err:
            if "zigux/Makefile" not in str(err):
                raise
        else:
            raise AssertionError("expected stale makefile wrapper failure")
        case_count += 1
    finally:
        for tmp in roots:
            tmp.cleanup()

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

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
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab_build.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

ABSENT_FILES = [
    "drivers/net/virtio_net.zig",
    "zigux/tests/phase12_virtio_net.zig",
]

SURVEY_MARKERS = (
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "drivers/net/virtio_net_queue_resume.zig",
    "drivers/net/virtio_net_receive_refill_replay.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/net/virtio_net_post_reset_replay.zig",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab_build.zig",
    "`zigux/tests/phase12_build.zig` plus `zigux/Makefile` now keep the dedicated `virtio_net_queue_resume`, `virtio_net_receive_refill_replay`, `virtio_net_transmit_recycle`, `virtio_net_post_reset_replay`, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
    "current `master` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper proof for that sextet",
    "the standalone syntax-lab companion remains compile-smoke evidence beside that sextet, but `zigux/tests/phase12_virtio_net_syntax_lab.zig` and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` are not wired into the shared Phase 12 validate, smoke, or test routes",
    "the packet still does not claim live DMA-safe receive ownership",
)

SURVEY_GATE_MARKERS = (
    '"split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"',
    '"split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"',
    '"shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays"',
    'try std.testing.expect(manifest.survey_summary.preexisting_phase12_virtio_net_syntax_lab_present);',
    'try expectContains(gap.why_now, "standalone syntax-lab compile-smoke companion");',
    'try std.testing.expect(try pathExists("zigux/tests/phase12_virtio_net_syntax_lab.zig"));',
    'try expectNotContains(build_zig, "phase12_virtio_net_syntax_lab.zig");',
    'try expectContains(makefile, "phase12: phase12-validate phase12-smoke phase12-test");',
)

BUILD_MARKERS = (
    "../../drivers/net/virtio_net_queue_resume.zig",
    "../../drivers/net/virtio_net_receive_refill_replay.zig",
    "../../drivers/net/virtio_net_transmit_recycle.zig",
    "../../drivers/net/virtio_net_post_reset_replay.zig",
    "../../drivers/net/virtio_net_throughput_parity.zig",
    '"phase12_virtio_net_survey.zig"',
    "phase12-virtio-net-survey-tests",
    "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
    "test_step.dependOn(&run_virtio_net_survey_tests.step);",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 12 release-readiness packet checker",
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "- name: Validate current Phase 12 support bundle",
    "run: python3 scripts/zigux/validate-phase12.py",
    "- name: Run current Phase 12 aggregate route",
    "run: make -C zigux phase12",
)


class CheckError(RuntimeError):
    pass


def require_file(root: Path, rel: str) -> Path:
    path = root / rel
    if not path.is_file():
        raise CheckError(f"missing required file: {rel}")
    return path


def require_markers(path: Path, markers: tuple[str, ...] | list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{path.as_posix()}: missing marker {marker!r}")
    return text


def run_check(root: Path) -> None:
    for rel in REQUIRED_FILES:
        require_file(root, rel)
    for rel in ABSENT_FILES:
        if (root / rel).exists():
            raise CheckError(f"{rel}: stale scaffold unexpectedly present")

    manifest_path = require_file(root, "zigux/tests/phase12_virtio_net_manifest.json")
    manifest_text = manifest_path.read_text(encoding="utf-8")
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise CheckError(f"{manifest_path.as_posix()}: invalid JSON: {exc.msg}") from exc
    expected = {
        "lane_key": "P12-L04",
        "phase": "Phase 12",
        "surveyed_commit": "e0c7303b0874af398d4f02221b97a6c9a1e49d5d",
        "verified_on": "2026-05-25",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise CheckError(f"{manifest_path.as_posix()}: {key} drifted from {value!r}")
    for marker in (
        '"preexisting_phase12_virtio_net_syntax_lab_present": true',
        '"status": "split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present"',
        '"status": "throughput_parity_helper_present_review_only_runtime_completion_missing"',
        '"status": "split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete"',
        '"status": "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays"',
        '"id": "phase12-virtio-net-runtime-data-path"',
        '"status": "blocked_on_dma_transport_runtime"',
    ):
        if marker not in manifest_text:
            raise CheckError(f"{manifest_path.as_posix()}: missing marker {marker!r}")

    require_markers(require_file(root, "Documentation/zigux/phase12-virtio-net-survey.md"), SURVEY_MARKERS)
    build_text = require_markers(require_file(root, "zigux/tests/phase12_build.zig"), BUILD_MARKERS)
    for stale in ("../../drivers/net/virtio_net.zig", '"phase12_virtio_net.zig"', '"phase12_virtio_net_syntax_lab.zig"'):
        if stale in build_text:
            raise CheckError(f"zigux/tests/phase12_build.zig: stale marker {stale!r}")
    require_markers(require_file(root, "zigux/tests/phase12_virtio_net_survey.zig"), SURVEY_GATE_MARKERS)
    require_markers(require_file(root, "zigux/Makefile"), MAKEFILE_MARKERS)
    require_markers(require_file(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)


def make_fixture_tree(root: Path) -> None:
    payloads = {
        "Documentation/zigux/phase12-virtio-net-survey.md": "\n".join(SURVEY_MARKERS) + "\n",
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
        "zigux/tests/phase12_virtio_net_syntax_lab.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_syntax_lab_build.zig": "// fixture\n",
        "zigux/tests/phase12_virtio_net_survey.zig": "\n".join(f"// {m}" for m in SURVEY_GATE_MARKERS) + "\n",
        "zigux/tests/phase12_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKEFILE_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
        "zigux/tests/phase12_virtio_net_manifest.json": json.dumps(
            {
                "lane_key": "P12-L04",
                "phase": "Phase 12",
                "surveyed_commit": "e0c7303b0874af398d4f02221b97a6c9a1e49d5d",
                "verified_on": "2026-05-25",
                "anchor": "drivers/net/virtio_net.c",
                "survey_summary": {
                    "preexisting_phase12_virtio_net_syntax_lab_present": True,
                },
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
                        "why_now": "standalone syntax-lab compile-smoke companion",
                    },
                    {
                        "id": "phase12-virtio-net-runtime-data-path",
                        "status": "blocked_on_dma_transport_runtime",
                    },
                ],
            },
            indent=2,
        ) + "\n",
    }
    for rel, text in payloads.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-virtio-net-packet-") as tmp:
        base = Path(tmp)
        make_fixture_tree(base)
        run_check(base)
        cases += 1

        for rel in (
            "Documentation/zigux/phase12-virtio-net-survey.md",
            "zigux/tests/phase12_virtio_net_manifest.json",
            "zigux/tests/phase12_build.zig",
            "zigux/tests/phase12_virtio_net_survey.zig",
            "zigux/Makefile",
            ".github/workflows/zigux-bootstrap.yml",
        ):
            make_fixture_tree(base)
            (base / rel).write_text("broken\n", encoding="utf-8")
            try:
                run_check(base)
            except CheckError:
                pass
            else:
                raise AssertionError(f"expected failure for {rel}")
            cases += 1

        make_fixture_tree(base)
        stale = base / "zigux/tests/phase12_virtio_net.zig"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("// stale\n", encoding="utf-8")
        try:
            run_check(base)
        except CheckError:
            pass
        else:
            raise AssertionError("expected stale scaffold failure")
        cases += 1

        make_fixture_tree(base)
        broken_manifest = base / "zigux/tests/phase12_virtio_net_manifest.json"
        payload = json.loads(broken_manifest.read_text(encoding="utf-8"))
        payload["verified_on"] = "2026-05-24"
        broken_manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            run_check(base)
        except CheckError:
            pass
        else:
            raise AssertionError("expected manifest drift failure")
        cases += 1

        make_fixture_tree(base)
        broken_build = base / "zigux/tests/phase12_build.zig"
        broken_build.write_text(
            broken_build.read_text(encoding="utf-8").replace("phase12-virtio-net-survey-tests", ""),
            encoding="utf-8",
        )
        try:
            run_check(base)
        except CheckError:
            pass
        else:
            raise AssertionError("expected survey route failure")
        cases += 1

    print("PHASE12_VIRTIO_NET_PACKET_SELF_TEST=pass")
    print(f"PHASE12_VIRTIO_NET_PACKET_SELF_TEST_CASES={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
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

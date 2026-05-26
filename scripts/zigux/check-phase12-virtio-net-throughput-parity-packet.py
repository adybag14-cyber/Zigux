#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

SURVEY_PATH = "Documentation/zigux/phase12-virtio-net-survey.md"
DRIVER_PATH = "drivers/net/virtio_net_throughput_parity.zig"
TEST_PATH = "zigux/tests/phase12_virtio_net_throughput_parity.zig"
MANIFEST_PATH = "zigux/tests/phase12_virtio_net_manifest.json"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
VIRTIO_NET_PACKET_CHECKER_PATH = "scripts/zigux/check-phase12-virtio-net-packet.py"
BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    SURVEY_PATH,
    DRIVER_PATH,
    TEST_PATH,
    MANIFEST_PATH,
    VALIDATOR_PATH,
    VIRTIO_NET_PACKET_CHECKER_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
)

SURVEY_MARKERS = (
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "drivers/net/virtio_net_throughput_parity.zig",
    "zigux/tests/phase12_virtio_net_throughput_parity.zig",
    "throughput helper remains review-only throughput-ratio checks",
    "explicit receive-refill and transmit-recycle readiness booleans",
)

DRIVER_MARKERS = (
    "pub const PostResetProbeReplayCheckpoint = enum {",
    "pub const ThroughputParityStatus = enum {",
    "needs_receive_refill,",
    "needs_transmit_recycle,",
    "needs_post_reset_probe_replay,",
    "parity_gate_ready,",
    "pub const ThroughputParityRequest = struct {",
    "free_transmit_descriptors_before_recycle: u16 = 0,",
    "replay_checkpoint: PostResetProbeReplayCheckpoint = .after_transmit_queue_restore,",
    "requires_control_queue_restore: bool = true,",
    "expected_min_ratio_pct: u8 = 90,",
    "pub const ThroughputParitySummary = struct {",
    "receive_refill_ready: bool,",
    "transmit_recycle_ready: bool,",
    "requires_post_reset_probe_replay: bool,",
    "meets_expected_min_ratio: bool,",
    "pub fn summarizeThroughputParity(request: ThroughputParityRequest) !ThroughputParitySummary {",
    'test "summarizeThroughputParity keeps post reset replay explicit after receive refill when transmit never stopped" {',
    'test "summarizeThroughputParity rejects free-descriptor overflow after recycle" {',
)

TEST_MARKERS = (
    'test "phase12 throughput parity gate counts preexisting free descriptors toward stopped-queue wake readiness" {',
    'test "phase12 throughput parity gate keeps queue-restore precedence explicit" {',
    "summary.free_transmit_descriptors_before_recycle",
    "summary.free_transmit_descriptors_after_recycle",
    "ThroughputParityStatus.parity_gate_ready",
    "ThroughputParityStatus.needs_queue_restore",
)

MANIFEST_MARKERS = (
    '"preexisting_virtio_net_throughput_parity_zig_present": true',
    '"preexisting_phase12_virtio_net_throughput_parity_present": true',
    '"status": "throughput_parity_helper_present_review_only_runtime_completion_missing"',
    "review-only throughput-ratio checks",
    "explicit receive-refill and transmit-recycle readiness booleans",
    '"status": "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays"',
    '"id": "phase12-virtio-net-runtime-data-path"',
    '"status": "blocked_on_dma_transport_runtime"',
)

VALIDATOR_MARKERS = (
    "scripts/zigux/check-phase12-virtio-net-packet.py",
    "Run current Phase 12 throughput-parity anchor",
    "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
)

BUILD_MARKERS = (
    '../../drivers/net/virtio_net_throughput_parity.zig',
    '"phase12_virtio_net_throughput_parity.zig"',
    "phase12-virtio-net-throughput-parity-tests",
    "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

WORKFLOW_MARKERS = (
    "- name: Run current Phase 12 throughput-parity anchor",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
    "- name: Validate current Phase 12 support bundle",
    "run: python3 scripts/zigux/validate-phase12.py",
)

SELF_SOURCE_MARKERS = (
    'write_text("broken\\n", encoding="utf-8")',
    'payload["verified_on"] = "2026-05-24"',
)


class CheckError(RuntimeError):
    pass


def require_file(root: Path, rel: str) -> Path:
    path = root / rel
    if not path.is_file():
        raise CheckError(f"missing required file: {rel}")
    return path


def require_markers(path: Path, markers: tuple[str, ...]) -> str:
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{path.as_posix()}: missing marker {marker!r}")
    return text


def run_check(root: Path) -> None:
    for rel in REQUIRED_FILES:
        require_file(root, rel)

    require_markers(require_file(root, SURVEY_PATH), SURVEY_MARKERS)
    require_markers(require_file(root, DRIVER_PATH), DRIVER_MARKERS)
    require_markers(require_file(root, TEST_PATH), TEST_MARKERS)
    require_markers(require_file(root, VALIDATOR_PATH), VALIDATOR_MARKERS)
    require_markers(require_file(root, BUILD_PATH), BUILD_MARKERS)
    require_markers(require_file(root, MAKEFILE_PATH), MAKEFILE_MARKERS)
    require_markers(require_file(root, WORKFLOW_PATH), WORKFLOW_MARKERS)

    manifest_path = require_file(root, MANIFEST_PATH)
    manifest_text = require_markers(manifest_path, MANIFEST_MARKERS)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise CheckError(f"{manifest_path.as_posix()}: invalid JSON: {exc.msg}") from exc

    expected = {
        "lane_key": "P12-L04",
        "phase": "Phase 12",
        "surveyed_commit": "e0c7303b0874af398d4f02221b97a6c9a1e49d5d",
        "verified_on": "2026-05-25",
        "anchor": "drivers/net/virtio_net.c",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise CheckError(f"{manifest_path.as_posix()}: {key} drifted from {value!r}")

    self_text = Path(__file__).read_text(encoding="utf-8")
    for marker in SELF_SOURCE_MARKERS:
        if marker not in self_text:
            raise CheckError(f"{Path(__file__).name}: missing self-source marker {marker!r}")


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    payloads = {
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        DRIVER_PATH: "\n".join(f"// {marker}" for marker in DRIVER_MARKERS) + "\n",
        TEST_PATH: "\n".join(f"// {marker}" for marker in TEST_MARKERS) + "\n",
        VALIDATOR_PATH: "\n".join(VALIDATOR_MARKERS) + "\n",
        VIRTIO_NET_PACKET_CHECKER_PATH: "#!/usr/bin/env python3\n",
        BUILD_PATH: "\n".join(BUILD_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
        WORKFLOW_PATH: "\n".join(WORKFLOW_MARKERS) + "\n",
        MANIFEST_PATH: json.dumps(
            {
                "lane_key": "P12-L04",
                "phase": "Phase 12",
                "surveyed_commit": "e0c7303b0874af398d4f02221b97a6c9a1e49d5d",
                "verified_on": "2026-05-25",
                "anchor": "drivers/net/virtio_net.c",
                "survey_summary": {
                    "preexisting_virtio_net_throughput_parity_zig_present": True,
                    "preexisting_phase12_virtio_net_throughput_parity_present": True,
                },
                "roadmap_gap_check": {
                    "throughput_and_recovery_parity": {
                        "status": "throughput_parity_helper_present_review_only_runtime_completion_missing",
                        "current_surface": "review-only throughput-ratio checks with explicit receive-refill and transmit-recycle readiness booleans",
                    }
                },
                "gaps": [
                    {
                        "id": "phase12-build-gate",
                        "status": "shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays",
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
    for rel, text in payloads.items():
        write_file(root / rel, text)


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-throughput-parity-packet-") as tmp:
        base = Path(tmp)
        write_fixture_tree(base)
        run_check(base)
        cases += 1

        for rel in (SURVEY_PATH, DRIVER_PATH, TEST_PATH, MANIFEST_PATH, VALIDATOR_PATH, BUILD_PATH):
            write_fixture_tree(base)
            (base / rel).write_text("broken\n", encoding="utf-8")
            try:
                run_check(base)
            except CheckError:
                pass
            else:
                raise AssertionError(f"expected failure for {rel}")
            cases += 1

        write_fixture_tree(base)
        broken_manifest = base / MANIFEST_PATH
        payload = json.loads(broken_manifest.read_text(encoding="utf-8"))
        payload["verified_on"] = "2026-05-24"
        broken_manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            run_check(base)
        except CheckError:
            pass
        else:
            raise AssertionError("expected manifest date drift failure")
        cases += 1

        write_fixture_tree(base)
        broken_build = base / BUILD_PATH
        broken_build.writeText = None
        broken_build.write_text(
            broken_build.read_text(encoding="utf-8").replace(
                "phase12-virtio-net-throughput-parity-tests",
                "",
                1,
            ),
            encoding="utf-8",
        )
        try:
            run_check(base)
        except CheckError:
            pass
        else:
            raise AssertionError("expected throughput build route drift failure")
        cases += 1

    print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET_SELF_TEST=pass")
    print(f"PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET_SELF_TEST_CASES={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_fixture_tree(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        run_check(args.root.resolve())
    except CheckError as err:
        print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET=fail")
        print(str(err))
        return 1

    print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET=pass")
    print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET_SCOPE=virtio_net_throughput_parity_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
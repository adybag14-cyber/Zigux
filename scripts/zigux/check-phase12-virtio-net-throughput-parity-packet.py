#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DOC_PATH = "Documentation/zigux/phase12-virtio-net-throughput-parity-slice.md"
DRIVER_PATH = "drivers/net/virtio_net_throughput_parity.zig"
TEST_PATH = "zigux/tests/phase12_virtio_net_throughput_parity.zig"
MANIFEST_PATH = "zigux/tests/fixtures/phase12_virtio_net_throughput_parity_manifest.json"
BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
CHECKER_PATH = "scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py"

REQUIRED_FILES = [
    DOC_PATH,
    DRIVER_PATH,
    TEST_PATH,
    MANIFEST_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    CHECKER_PATH,
]

EXPECTED_MANIFEST_FIELDS = {
    "lane_key": "P12-L04",
    "phase": "Phase 12",
    "slug": "phase12-virtio-net-throughput-parity-packet",
    "anchor": "drivers/net/virtio_net.c",
    "status": "throughput_parity_helper_present_direct_checker_and_isolated_route_guard_present",
    "scope": (
        "review-only virtio_net throughput parity helper evidence plus the direct "
        "isolated-route guard around the dedicated throughput replay"
    ),
    "next_safe_step": (
        "keep future same-lane follow-through narrowed to measured transport "
        "throughput replay or runtime completion only if this helper-local packet "
        "drifts on master"
    ),
}

DOC_MARKERS = (
    "This note records one bounded Validation and Perf packet for the current Phase 12 `virtio_net` throughput-parity replay.",
    "`drivers/net/virtio_net_throughput_parity.zig`",
    "`zigux/tests/phase12_virtio_net_throughput_parity.zig`",
    "`zigux/tests/fixtures/phase12_virtio_net_throughput_parity_manifest.json`",
    "`scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py`",
    "`zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12-virtio-net-throughput-parity-test`",
    "It does not claim live transport execution, measured wire throughput, DMA-safe receive ownership, or interrupt-backed completion evidence.",
)

DRIVER_MARKERS = (
    "pub const ThroughputParityStatus = enum {",
    "needs_post_reset_probe_replay,",
    "pub const ThroughputParitySummary = struct {",
    "receive_refill_ready: bool,",
    "transmit_recycle_ready: bool,",
    "throughput_ratio_pct: u8,",
    "pub fn summarizeThroughputParity(request: ThroughputParityRequest) !ThroughputParitySummary {",
    'test "summarizeThroughputParity keeps post reset replay explicit after receive refill when transmit never stopped" {',
)

TEST_MARKERS = (
    'test "phase12 throughput parity gate counts preexisting free descriptors toward stopped-queue wake readiness" {',
    'test "phase12 throughput parity gate keeps queue-restore precedence explicit" {',
    "summary.free_transmit_descriptors_after_recycle",
    "summary.queue_pair_ratio_pct",
)

BUILD_MARKERS = (
    "../../drivers/net/virtio_net_throughput_parity.zig",
    '"phase12_virtio_net_throughput_parity.zig"',
    '"phase12-virtio-net-throughput-parity-tests"',
    'throughput_parity_step = b.step(',
    '"phase12-virtio-net-throughput-parity"',
    "throughput_parity_step.dependOn(&throughput_parity_tests.step);",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-virtio-net-throughput-parity-test:",
    "$(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
)

WORKFLOW_MARKERS = (
    "Run current Phase 12 throughput-parity anchor",
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

    require_markers(require_file(root, DOC_PATH), DOC_MARKERS)
    require_markers(require_file(root, DRIVER_PATH), DRIVER_MARKERS)
    require_markers(require_file(root, TEST_PATH), TEST_MARKERS)
    require_markers(require_file(root, BUILD_PATH), BUILD_MARKERS)
    require_markers(require_file(root, MAKEFILE_PATH), MAKEFILE_MARKERS)
    require_markers(require_file(root, WORKFLOW_PATH), WORKFLOW_MARKERS)

    manifest_path = require_file(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"{manifest_path.as_posix()}: invalid JSON: {exc.msg}") from exc

    for key, value in EXPECTED_MANIFEST_FIELDS.items():
        if manifest.get(key) != value:
            raise CheckError(
                f"{manifest_path.as_posix()}: {key} drifted from {value!r}"
            )

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if packet_files != [
        DOC_PATH,
        DRIVER_PATH,
        TEST_PATH,
        MANIFEST_PATH,
        CHECKER_PATH,
    ]:
        raise CheckError(f"{manifest_path.as_posix()}: packet_files drifted")

    if replay_routes != [
        "python3 scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py --self-test",
        "python3 scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py --root .",
        "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
        "make -C zigux phase12-virtio-net-throughput-parity-test",
    ]:
        raise CheckError(f"{manifest_path.as_posix()}: replay_routes drifted")

    if repo_reality_gaps != [
        "measured transport throughput evidence remains outside the current helper-local throughput parity packet",
        "runtime queue execution and interrupt-backed transmit completion handling remain outside the current helper-local throughput parity packet",
    ]:
        raise CheckError(f"{manifest_path.as_posix()}: repo_reality_gaps drifted")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_manifest() -> str:
    payload = {
        **EXPECTED_MANIFEST_FIELDS,
        "packet_files": [
            DOC_PATH,
            DRIVER_PATH,
            TEST_PATH,
            MANIFEST_PATH,
            CHECKER_PATH,
        ],
        "replay_routes": [
            "python3 scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py --self-test",
            "python3 scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py --root .",
            "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
            "make -C zigux phase12-virtio-net-throughput-parity-test",
        ],
        "repo_reality_gaps": [
            "measured transport throughput evidence remains outside the current helper-local throughput parity packet",
            "runtime queue execution and interrupt-backed transmit completion handling remain outside the current helper-local throughput parity packet",
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def make_fixture_tree(root: Path) -> None:
    payloads = {
        DOC_PATH: "\n".join(DOC_MARKERS) + "\n",
        DRIVER_PATH: "\n".join(DRIVER_MARKERS) + "\n",
        TEST_PATH: "\n".join(TEST_MARKERS) + "\n",
        MANIFEST_PATH: fixture_manifest(),
        BUILD_PATH: "\n".join(BUILD_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
        WORKFLOW_PATH: "\n".join(WORKFLOW_MARKERS) + "\n",
        CHECKER_PATH: "# self marker\n",
    }
    for rel, text in payloads.items():
        write_text(root / rel, text)


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-throughput-parity-") as tmp:
        base = Path(tmp)
        make_fixture_tree(base)
        run_check(base)
        cases += 1

        for rel in (
            DOC_PATH,
            DRIVER_PATH,
            TEST_PATH,
            MANIFEST_PATH,
            BUILD_PATH,
            MAKEFILE_PATH,
            WORKFLOW_PATH,
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
        payload = json.loads((base / MANIFEST_PATH).read_text(encoding="utf-8"))
        payload["repo_reality_gaps"] = []
        (base / MANIFEST_PATH).write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        try:
            run_check(base)
        except CheckError:
            pass
        else:
            raise AssertionError("expected repo_reality_gaps drift failure")
        cases += 1

    print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET_SELF_TEST=pass")
    print(f"PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET_SELF_TEST_CASES={cases}")


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
        print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET=fail")
        print(str(err))
        return 1

    print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET=pass")
    print("PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_PACKET_SCOPE=throughput_parity_packet_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

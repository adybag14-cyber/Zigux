#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 12 throughput-parity packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

CHECK_NAME = "PHASE12_THROUGHPUT_PARITY_PACKET"

DRIVER_PATH = Path("drivers/net/virtio_net_throughput_parity.zig")
TEST_PATH = Path("zigux/tests/phase12_virtio_net_throughput_parity.zig")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase12_build_inventory.json")
DOC_PATH = Path("Documentation/zigux/phase12-virtio-net-raw-github-fallback-map.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    DRIVER_PATH,
    TEST_PATH,
    BUILD_PATH,
    INVENTORY_PATH,
    DOC_PATH,
    WORKFLOW_PATH,
)

REQUIRED_MARKERS = {
    DRIVER_PATH: (
        "pub const ThroughputParityStatus = enum {",
        "pub fn summarizeThroughputParity(request: ThroughputParityRequest) !ThroughputParitySummary {",
        "expected_min_ratio_pct: u8 = 90,",
        'test "summarizeThroughputParity counts preexisting free descriptors toward the stopped-queue wake gate" {',
        'test "summarizeThroughputParity rejects out-of-range target ratios" {',
    ),
    TEST_PATH: (
        'test "phase12 throughput parity gate counts preexisting free descriptors toward stopped-queue wake readiness" {',
        'test "phase12 throughput parity gate keeps queue-restore precedence explicit" {',
        "ThroughputParityStatus.parity_gate_ready,",
        "ThroughputParityStatus.needs_queue_restore,",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../../drivers/net/virtio_net_throughput_parity.zig"),',
        '.root_source_file = b.path("phase12_virtio_net_throughput_parity.zig"),',
        '.name = "phase12-virtio-net-throughput-parity-tests",',
        'const throughput_parity_step = b.step(',
        '"phase12-virtio-net-throughput-parity",',
        "throughput_parity_step.dependOn(&throughput_parity_tests.step);",
    ),
    INVENTORY_PATH: (
        '"phase12-virtio-net-throughput-parity-tests"',
        '"throughput_anchor_depend_steps": [',
        '"throughput_parity_tests"',
        '"path": "../../drivers/net/virtio_net_throughput_parity.zig"',
        '"path": "phase12_virtio_net_throughput_parity.zig"',
        '"step": "phase12-virtio-net-throughput-parity"',
    ),
    DOC_PATH: (
        "- driver shard: `drivers/net/virtio_net_throughput_parity.zig`",
        "- directly coupled replay: `zigux/tests/phase12_virtio_net_throughput_parity.zig`",
        "`make -C zigux phase12-virtio-net-throughput-parity-test`",
        "throughput-parity, and survey-gate sextet through shared `smoke` and shared `test`",
    ),
    WORKFLOW_PATH: (
        "- name: Run current Phase 12 throughput-parity anchor",
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    ),
}


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, path: Path) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing required file: {path}") from exc


def check(root: Path) -> None:
    for path in REQUIRED_FILES:
        if not (root / path).is_file():
            raise CheckFailure(f"missing required file: {path}")

    for path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, path)
        for marker in markers:
            if marker not in text:
                raise CheckFailure(f"{path} missing marker: {marker}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_text(path: Path) -> str:
    return "\n".join(REQUIRED_MARKERS[path]) + "\n"


def write_fixture_tree(root: Path) -> None:
    for path in REQUIRED_FILES:
        write_text(root / path, fixture_text(path))


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"{marker}\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    if updated == text:
        raise AssertionError(f"unable to remove marker: {marker}")
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        check(root)
    except CheckFailure as exc:
        if expected_fragment not in str(exc):
            raise
        return
    raise AssertionError(f"expected failure containing: {expected_fragment}")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-throughput-parity-packet-") as tmp:
        root = Path(tmp)

        write_fixture_tree(root)
        check(root)
        cases += 1

        for path in REQUIRED_FILES:
            write_fixture_tree(root)
            (root / path).unlink()
            expect_failure(root, f"missing required file: {path}")
            cases += 1

        for path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                write_fixture_tree(root)
                remove_marker(root / path, marker)
                expect_failure(root, f"{path} missing marker: {marker}")
                cases += 1

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        check(args.root)
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail:{exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

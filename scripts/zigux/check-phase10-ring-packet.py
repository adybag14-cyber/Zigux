#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path(__file__).resolve().parent
)

DIRECT_PACKET_FILES = [
    "drivers/virtio/virtio_ring.zig",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
]

MARKERS = {
    "drivers/virtio/virtio_ring.zig": [
        "pub fn defineQueue(",
        "pub fn publishDescriptorChain(self: *Self, queue_index: u16) !void {",
        "pub fn prepareKick(self: *Self, queue_index: u16) !QueueNotificationSummary {",
        "pub fn pollUsedBuffers(self: *Self, queue_index: u16) !UsedBufferPollSummary {",
        "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
        "pub fn enableCallbackDelayed(self: *Self, queue_index: u16) !DelayedCallbackSummary {",
        "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
        "pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary {",
        "pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
        "pub fn clearBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
        "if (slot.broken) return error.QueueBroken;",
        "if (slot.broken) return error.QueueResetWhileBroken;",
    ],
    "zigux/tests/phase10_build.zig": [
        '.root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_prepare_kick_idempotent.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_broken_queue_queue_discipline.zig"),',
        '.name = "phase10-virtio-ring-prepare-kick-idempotent-tests",',
        '.name = "phase10-virtio-ring-broken-queue-queue-discipline-tests",',
        "test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);",
    ],
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig": [
        'test "phase10 virtio ring repeated prepareKick stays idle until new descriptors are published" {',
        "const virtio_ring = @import(\"virtio_ring\");",
        "kick_summary = try ring.prepareKick(1);",
        "try std.testing.expect(!kick_summary.needs_kick);",
    ],
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig": [
        'test "phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible" {',
        "const broken_summary = try ring.markBroken(3);",
        "try std.testing.expectError(error.QueueBroken, ring.publishDescriptorChain(3));",
        "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
        "const cleared_summary = try ring.clearBroken(3);",
        "const second_kick = try ring.prepareKick(3);",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in DIRECT_PACKET_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in MARKERS.items():
        text = read_text(root, rel_path)
        label = Path(rel_path).name
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{label}:{marker}")

    return [], missing_markers


def write_fixture(root: Path) -> None:
    fixture = {
        "drivers/virtio/virtio_ring.zig": "\n".join(MARKERS["drivers/virtio/virtio_ring.zig"]) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(MARKERS["zigux/tests/phase10_build.zig"]) + "\n",
        "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig": "\n".join(
            MARKERS["zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig"]
        )
        + "\n",
        "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig": "\n".join(
            MARKERS["zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig"]
        )
        + "\n",
    }
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

        def expect_missing_marker(rel_path: str, marker: str) -> None:
            nonlocal case_count
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace(marker, "__drift_marker_removed__", 1), encoding="utf-8")
            _, missing = validate(root)
            expected = f"{Path(rel_path).name}:{marker}"
            if expected not in missing:
                raise SystemExit(f"phase10-ring-self-test:expected_marker_missing:{expected}")
            path.write_text(original, encoding="utf-8")
            case_count += 1

        def expect_missing_file(rel_path: str) -> None:
            nonlocal case_count
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.unlink()
            files, _ = validate(root)
            if rel_path not in files:
                raise SystemExit(f"phase10-ring-self-test:expected_file_missing:{rel_path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(original, encoding="utf-8")
            case_count += 1

        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn clearBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            '.name = "phase10-virtio-ring-broken-queue-queue-discipline-tests",',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
            'test "phase10 virtio ring repeated prepareKick stays idle until new descriptors are published" {',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
            "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
        )
        expect_missing_file("zigux/tests/phase10_build.zig")

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print(f"PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the directly readable Phase 10 virtio ring queue-discipline packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in drift checks against a synthetic fixture tree.")
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root to validate. Defaults to the checker's inferred repo root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root)
    missing_files, missing_markers = validate(root)
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
    print(f"PHASE10_RING_REQUIRED_FILE_COUNT={len(DIRECT_PACKET_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

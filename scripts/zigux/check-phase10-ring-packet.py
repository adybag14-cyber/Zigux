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

CURRENT_RING_PACKET_FILES = [
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
]

MARKERS = {
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "`Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`",
        "`zigux/tests/phase10_virtio_ring_manifest.json`",
        "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        "`phase10-virtio-ring-survey-gate`",
        "`phase10-virtqueue-shape-helper`",
        "the ring lane still stays below transport-backed work: the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
    ],
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "drivers/virtio/virtio_ring_verify.zig",
        "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
        "while `zigux/tests/phase10_virtio_ring.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` still return missing.",
        "Keep the queue-local ring helper ladder, the wrapper-facing verify replay, and the focused replays framed as direct current-head evidence",
        "the remaining direct ring gap is the dedicated survey replay",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "Fresh direct readback on current `master` now materializes `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, and `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, while `zigux/tests/phase10_virtio_ring.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` still do not materialize through direct contents readback.",
        "The shared ring packet therefore keeps the restored helper, the wrapper-facing verify replay, and the focused replays as current direct evidence",
        "while the dedicated survey gate remains the only direct ring packet gap in this slice.",
    ],
    "drivers/virtio/virtio_ring.zig": [
        "pub fn defineQueue(",
        "pub fn publishDescriptorChain(self: *Self, queue_index: u16) !void {",
        "pub fn prepareKick(self: *Self, queue_index: u16) !QueueNotificationSummary {",
        "pub fn pollUsedBuffers(self: *Self, queue_index: u16) !UsedBufferPollSummary {",
        "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
        "pub fn enableCallbackDelayed(self: *Self, queue_index: u16) !DelayedCallbackSummary {",
        "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
        "pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
        "pub fn clearBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
        "pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary {",
        "if (slot.broken) return error.QueueBroken;",
        "if (slot.broken) return error.QueueResetWhileBroken;",
    ],
    "drivers/virtio/virtio_ring_verify.zig": [
        "pub fn summarizeDelayedCallback(",
        "pub fn summarizeResetReadiness(",
        'test "phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit" {',
        'test "phase10 virtio ring verify keeps broken queue fences visible until clear" {',
        'test "phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay" {',
    ],
    "zigux/tests/phase10_build.zig": [
        '.root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_prepare_kick_idempotent.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_reset_reuse.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_broken_queue_queue_discipline.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_delayed_callback_budget.zig"),',
        '.name = "phase10-virtio-ring-prepare-kick-idempotent-tests",',
        '.name = "phase10-virtio-ring-reset-reuse-tests",',
        '.name = "phase10-virtio-ring-broken-queue-queue-discipline-tests",',
        '.name = "phase10-virtio-ring-delayed-callback-budget-tests",',
        "test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);",
        "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
    ],
    "zigux/tests/phase10_virtio_ring_manifest.json": [
        '"lane_key": "P10-L10"',
        '"id": "phase10-virtio-ring-survey-gate"',
        '"status": "repo_reality_gap"',
        '"id": "phase10-virtqueue-shape-helper"',
        '"id": "phase10-ring-lab-driver-bridge"',
        '"freeze_status_change_claimed": false',
        '"risky_transport_posture": "blocked_on_risky_transport"',
        '"allowed_evidence_kinds": [',
        '"forbidden_transport_claims": [',
        '"architecture_council_reopen_required": true',
        '"architecture_council_reopen_attached": false',
    ],
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig": [
        'test "phase10 virtio ring repeated prepareKick stays idle until new descriptors are published" {',
        'const virtio_ring = @import("virtio_ring");',
        "kick_summary = try ring.prepareKick(1);",
        "try std.testing.expect(!kick_summary.needs_kick);",
    ],
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        'test "phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state" {',
        "var readiness = try ring.queueResetReadinessSummary(2);",
        'try std.testing.expectEqualStrings("unpublished_chains", @tagName(readiness.blocker.?));',
        "const reset = try ring.resetQueue(2);",
        "const kick_after_reset = try ring.prepareKick(2);",
    ],
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig": [
        'test "phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible" {',
        "const broken_summary = try ring.markBroken(3);",
        "try std.testing.expectError(error.QueueBroken, ring.publishDescriptorChain(3));",
        "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
        "const cleared_summary = try ring.clearBroken(3);",
        "const second_kick = try ring.prepareKick(3);",
    ],
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig": [
        'test "phase10 virtio ring delayed callback budget stays bounded to queue-local replay state" {',
        'const virtio_ring = @import("virtio_ring");',
        "var summary = try ring.enableCallbackDelayed(7);",
        "try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);",
        "try std.testing.expectEqual(@as(u16, 2), summary.pending_used_chain_count);",
        "try std.testing.expect(summary.should_poll);",
        "summary = try ring.enableCallbackDelayed(7);",
        "try std.testing.expect(!summary.should_poll);",
        "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in CURRENT_RING_PACKET_FILES if not (root / path).exists()]
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
    for rel_path, markers in MARKERS.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(markers) + "\n", encoding="utf-8")


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
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "`Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "`phase10-virtio-ring-survey-gate`",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "the ring lane still stays below transport-backed work: the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
            "drivers/virtio/virtio_ring_verify.zig",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
            "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
            "Keep the queue-local ring helper ladder, the wrapper-facing verify replay, and the focused replays framed as direct current-head evidence",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
            "the remaining direct ring gap is the dedicated survey replay",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-slice.md",
            "Fresh direct readback on current `master` now materializes `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, and `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, while `zigux/tests/phase10_virtio_ring.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` still do not materialize through direct contents readback.",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-slice.md",
            "The shared ring packet therefore keeps the restored helper, the wrapper-facing verify replay, and the focused replays as current direct evidence",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-slice.md",
            "while the dedicated survey gate remains the only direct ring packet gap in this slice.",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn prepareKick(self: *Self, queue_index: u16) !QueueNotificationSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn enableCallbackDelayed(self: *Self, queue_index: u16) !DelayedCallbackSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring_verify.zig",
            'test "phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit" {',
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring_verify.zig",
            'test "phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay" {',
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            '.name = "phase10-virtio-ring-broken-queue-queue-discipline-tests",',
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            '.name = "phase10-virtio-ring-reset-reuse-tests",',
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            '.name = "phase10-virtio-ring-delayed-callback-budget-tests",',
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            "test_step.dependOn(&run_phase10_virtio_ring_prepare_kick_idempotent_tests.step);",
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            "test_step.dependOn(&run_phase10_virtio_ring_reset_reuse_tests.step);",
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            "test_step.dependOn(&run_phase10_virtio_ring_broken_queue_queue_discipline_tests.step);",
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            "test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);",
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"id": "phase10-virtio-ring-survey-gate"',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"id": "phase10-virtqueue-shape-helper"',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"id": "phase10-ring-lab-driver-bridge"',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"freeze_status_change_claimed": false',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"risky_transport_posture": "blocked_on_risky_transport"',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"allowed_evidence_kinds": [',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"forbidden_transport_claims": [',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"architecture_council_reopen_required": true',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"architecture_council_reopen_attached": false',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
            'test "phase10 virtio ring repeated prepareKick stays idle until new descriptors are published" {',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "const reset = try ring.resetQueue(2);",
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "const kick_after_reset = try ring.prepareKick(2);",
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
            "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
            "try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);",
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
            "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
        )
        expect_missing_marker(
            "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
            "while `zigux/tests/phase10_virtio_ring.zig` and `zigux/tests/phase10_virtio_ring_survey.zig` still return missing.",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn publishDescriptorChain(self: *Self, queue_index: u16) !void {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn pollUsedBuffers(self: *Self, queue_index: u16) !UsedBufferPollSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn markBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn clearBroken(self: *Self, queue_index: u16) !BrokenQueueSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "pub fn resetQueue(self: *Self, queue_index: u16) !QueueResetSummary {",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "if (slot.broken) return error.QueueBroken;",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring.zig",
            "if (slot.broken) return error.QueueResetWhileBroken;",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring_verify.zig",
            "pub fn summarizeDelayedCallback(",
        )
        expect_missing_marker(
            "drivers/virtio/virtio_ring_verify.zig",
            "pub fn summarizeResetReadiness(",
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            '.root_source_file = b.path("../../drivers/virtio/virtio_ring.zig"),',
        )
        expect_missing_marker(
            "zigux/tests/phase10_build.zig",
            '.root_source_file = b.path("phase10_virtio_ring_delayed_callback_budget.zig"),',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"lane_key": "P10-L10"',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_manifest.json",
            '"status": "repo_reality_gap"',
        )
        expect_missing_marker(
            "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
            "try std.testing.expect(summary.should_poll);",
        )
        expect_missing_file("Documentation/zigux/phase10-virtio-ring-survey.md")
        expect_missing_file("Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md")
        expect_missing_file("Documentation/zigux/phase10-virtio-ring-slice.md")
        expect_missing_file("drivers/virtio/virtio_ring.zig")
        expect_missing_file("drivers/virtio/virtio_ring_verify.zig")
        expect_missing_file("zigux/tests/phase10_build.zig")
        expect_missing_file("zigux/tests/phase10_virtio_ring_manifest.json")
        expect_missing_file("zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig")
        expect_missing_file("zigux/tests/phase10_virtio_ring_reset_reuse.zig")
        expect_missing_file("zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig")
        expect_missing_file("zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig")

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print(f"PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current directly materialized Phase 10 virtio ring helper-and-verify packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a synthetic fixture tree.",
    )
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
    print(f"PHASE10_RING_REQUIRED_FILE_COUNT={len(CURRENT_RING_PACKET_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
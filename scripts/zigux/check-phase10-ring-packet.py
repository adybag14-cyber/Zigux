#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_MARKERS = {
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "`phase10-virtio-ring-survey-gate`",
        "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
        "`zigux/tests/phase10_virtio_ring_survey.zig`",
        "the broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize on current `master`",
        "the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet",
    ],
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "current packet lane on master: `P10-L05`",
        "adjacent freeze-boundary owner: `P10-L11`",
        "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` still remains a direct-readback gap beside the queue-local helper ladder",
        "the dedicated ring survey replay `zigux/tests/phase10_virtio_ring_survey.zig` stays part of the same directly readable ring packet",
        "the smallest same-lane follow-through is reminder-surface, checker, or manifest truthfulness work",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "`zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`",
        "`zigux/tests/phase10_virtio_ring_survey.zig`",
        "the broader ring replay still remains outside direct current-head evidence in this slice",
        "the dedicated survey gate is now a landed review surface inside this slice",
    ],
    "drivers/virtio/virtio_ring.zig": [
        "pub const QueueShapeSummary = struct {",
        "pub const NotificationDataSummary = struct {",
        "pub fn notificationSummary(self: *const Self, queue_index: u16) !QueueNotificationSummary {",
        "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
        "pub fn enableCallbackDelayed(self: *Self, queue_index: u16) !DelayedCallbackSummary {",
        "pub fn queueResetReadinessSummary(self: *const Self, queue_index: u16) !QueueResetReadinessSummary {",
    ],
    "drivers/virtio/virtio_ring_verify.zig": [
        "pub fn summarizeNotificationState(",
        "pub fn summarizeNotificationData(",
        "pub fn summarizeDelayedCallback(",
        "pub fn summarizeResetReadiness(",
        'test "phase10 virtio ring verify keeps notification-state wrapper explicit across publish kick and used replay" {',
        'test "phase10 virtio ring verify keeps notification-data next-avail state reviewable across split packed and reset replay" {',
        'test "phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay" {',
    ],
    "zigux/tests/phase10_build.zig": [
        '.root_source_file = b.path("phase10_virtio_ring_notification_data_readiness.zig"),',
        '.root_source_file = b.path("phase10_virtio_ring_survey.zig"),',
        '.name = "phase10-virtio-ring-notification-data-readiness-tests",',
        '.name = "phase10-virtio-ring-verify-tests",',
        '.name = "phase10-virtio-ring-prepare-kick-idempotent-tests",',
        '.name = "phase10-virtio-ring-reset-reuse-tests",',
        '.name = "phase10-virtio-ring-broken-queue-queue-discipline-tests",',
        '.name = "phase10-virtio-ring-delayed-callback-budget-tests",',
        '.name = "phase10-virtio-ring-survey-tests",',
        "test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);",
        "test_step.dependOn(&run_phase10_virtio_ring_survey_tests.step);",
        "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests",
    ],
    "zigux/tests/phase10_virtio_ring_manifest.json": [
        '"lane_key": "P10-L05"',
        '"preexisting_phase10_test_files": 3,',
        '"id": "phase10-virtio-ring-survey-gate"',
        '"status": "starter_landed"',
        '"id": "phase10-ring-verify-replay"',
        '"id": "phase10-ring-lab-driver-bridge"',
        '"status": "blocked_on_risky_transport"',
    ],
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig": [
        'test "phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit" {',
        "const split_summary = try ring.notificationDataSummary(1);",
        "const packed_summary = try ring.notificationDataSummary(2);",
        'test "phase10 virtio ring reset-readiness replay orders blockers before a clean queue reset" {',
        "const reset = try ring.resetQueue(5);",
    ],
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig": [
        'test "phase10 virtio ring repeated prepareKick stays idle until new descriptors are published" {',
        "kick_summary = try ring.prepareKick(1);",
        "try std.testing.expect(!kick_summary.needs_kick);",
    ],
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        'test "phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state" {',
        "const reset = try ring.resetQueue(2);",
        "const kick_after_reset = try ring.prepareKick(2);",
    ],
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig": [
        'test "phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible" {',
        "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
        "const cleared_summary = try ring.clearBroken(3);",
    ],
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig": [
        'test "phase10 virtio ring delayed callback budget stays bounded to queue-local replay state" {',
        "try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);",
        "try std.testing.expect(summary.should_poll);",
        "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
    ],
    "zigux/tests/phase10_virtio_ring_survey.zig": [
        'test "phase10 virtio ring survey note keeps the missing broader replay explicit beside the queue-local helper packet" {',
        'try expectContains(survey_note, "broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize");',
        'try expectContains(build_file, "\\\\\\\"phase10-virtio-ring-survey-tests\\\\\\\"");',
        'test "phase10 virtio ring freeze-boundary note keeps risky transport work blocked" {',
    ],
}

FORBIDDEN_MARKERS = {
    "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md": [
        "the broader ring replay now rematerializes",
        "`zigux/tests/phase10_virtio_ring.zig` joins direct current-head evidence beside the queue-local helper ladder",
    ],
    "Documentation/zigux/phase10-virtio-ring-slice.md": [
        "the broader ring replay and the dedicated survey gate are now landed review surfaces inside this slice",
        "Fresh direct readback on current `master` now materializes `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`",
    ],
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "the broader replay `zigux/tests/phase10_virtio_ring.zig`, the focused queue-local replays",
        "the broader ring replay, the queue-local ring helper ladder, the wrapper-facing verify replay",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_MARKERS if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    problems: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                problems.append(f"{rel_path}:forbidden:{marker}")

    return [], problems


def write_fixture(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(markers) + "\n", encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, marker: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "__removed__", 1), encoding="utf-8")
    _, problems = validate(root)
    expected = f"{rel_path}:{marker}"
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_forbidden_marker(root: Path, rel_path: str, marker: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original + marker + "\n", encoding="utf-8")
    _, problems = validate(root)
    expected = f"{rel_path}:forbidden:{marker}"
    if expected not in problems:
        actual = ",".join(problems) if problems else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, rel_path: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.unlink()
    missing_files, problems = validate(root)
    if problems:
        actual = ",".join(problems)
        raise SystemExit(f"phase10-ring-self-test:unexpected_problems={actual}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"phase10-ring-self-test:expected={rel_path}:actual={actual}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, problems = validate(root)
        if missing_files or problems:
            raise SystemExit(
                "phase10-ring-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"problems={','.join(problems) or 'none'}"
            )

        cases = [
            (
                "Documentation/zigux/phase10-virtio-ring-survey.md",
                "`zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`",
            ),
            (
                "Documentation/zigux/phase10-virtio-ring-survey.md",
                "the broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize on current `master`",
            ),
            (
                "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
                "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` still remains a direct-readback gap beside the queue-local helper ladder",
            ),
            (
                "Documentation/zigux/phase10-virtio-ring-slice.md",
                "the broader ring replay still remains outside direct current-head evidence in this slice",
            ),
            (
                "drivers/virtio/virtio_ring.zig",
                "pub fn enableCallback(self: *Self, queue_index: u16) !CallbackEnableSummary {",
            ),
            (
                "drivers/virtio/virtio_ring_verify.zig",
                "pub fn summarizeNotificationState(",
            ),
            (
                "drivers/virtio/virtio_ring_verify.zig",
                'test "phase10 virtio ring verify keeps notification-state wrapper explicit across publish kick and used replay" {',
            ),
            (
                "zigux/tests/phase10_build.zig",
                '.name = "phase10-virtio-ring-notification-data-readiness-tests",',
            ),
            (
                "zigux/tests/phase10_build.zig",
                "test_step.dependOn(&run_phase10_virtio_ring_notification_data_readiness_tests.step);",
            ),
            (
                "zigux/tests/phase10_virtio_ring_manifest.json",
                '"id": "phase10-virtio-ring-survey-gate"',
            ),
            (
                "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
                "const packed_summary = try ring.notificationDataSummary(2);",
            ),
            (
                "zigux/tests/phase10_virtio_ring_survey.zig",
                'try expectContains(survey_note, "broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize");',
            ),
            (
                "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
                "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
            ),
        ]
        for rel_path, marker in cases:
            expect_missing_marker(root, rel_path, marker)

        expect_forbidden_marker(
            root,
            "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
            "the broader ring replay now rematerializes",
        )
        expect_forbidden_marker(
            root,
            "Documentation/zigux/phase10-virtio-ring-slice.md",
            "the broader ring replay and the dedicated survey gate are now landed review surfaces inside this slice",
        )
        expect_missing_file(root, "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig")

    print("PHASE10_RING_PACKET_SELF_TEST=pass")
    print("PHASE10_RING_PACKET_SELF_TEST_CASE_COUNT=15")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current directly re-readable Phase 10 virtio ring packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, problems = validate(Path(args.root))
    if missing_files:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_RING_FILES_END")
        return 1

    if problems:
        print("PHASE10_RING_PACKET=fail")
        print("MISSING_PHASE10_RING_MARKERS_START")
        for item in problems:
            print(item)
        print("MISSING_PHASE10_RING_MARKERS_END")
        return 1

    required_marker_count = sum(len(markers) for markers in REQUIRED_MARKERS.values())
    forbidden_marker_count = sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
    print("PHASE10_RING_PACKET=pass")
    print(f"PHASE10_RING_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE10_RING_REQUIRED_MARKER_COUNT={required_marker_count}")
    print(f"PHASE10_RING_FORBIDDEN_MARKER_COUNT={forbidden_marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

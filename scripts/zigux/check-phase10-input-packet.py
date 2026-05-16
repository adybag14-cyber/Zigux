#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

FILES = [
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_build.zig",
]

MODULE_MARKERS = [
    "# Phase 10 Virtio Input Module Slice",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "queued status completions are still reclaimed in memory",
    "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
]

INPUT_HELPER_MARKERS = [
    "pub const QueuePlanSummary = struct {",
    "pub const StatusDrainSummary = struct {",
    "pub const RegistrationPreflightSummary = struct {",
    "pub const QueueCallbackPreflightSummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub const TeardownObservationSummary = struct {",
    "pub fn fillEventBuffers(self: *Self) !QueuePlanSummary {",
    "pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
    "pub fn registrationPreflightSummary(self: *const Self) RegistrationPreflightSummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
    "pub fn teardownObservationSummary(self: *const Self) TeardownObservationSummary {",
    "pub fn drainStatusQueue(self: *Self, completed_count: usize) !StatusDrainSummary {",
]

REGISTRATION_HELPER_MARKERS = [
    "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
    "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
    "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
]

BUILD_MARKERS = [
    "phase10_virtio_input_module",
    "phase10_virtio_input_probe_preflight_module",
    "phase10_virtio_input_queue_callback_preflight_module",
    "phase10_virtio_input_registration_preflight_module",
    "phase10_virtio_input_status_drain_module",
    "phase10_virtio_input_teardown_observation_module",
    '"phase10-virtio-input-tests"',
    '"phase10-virtio-input-probe-preflight-tests"',
    '"phase10-virtio-input-queue-callback-preflight-tests"',
    '"phase10-virtio-input-registration-preflight-tests"',
    '"phase10-virtio-input-status-drain-tests"',
    '"phase10-virtio-input-teardown-observation-tests"',
]

TEST_MARKERS = {
    "zigux/tests/phase10_virtio_input.zig": [
        'test "phase10 virtio input descriptor and identity snapshot stay lab-only and bounded" {',
        'test "phase10 virtio input queue planning caps and refills event buffers" {',
    ],
    "zigux/tests/phase10_virtio_input_probe_preflight.zig": [
        'test "phase10 virtio input probe preflight stays blocked until queue, capability, and slot planning are staged" {',
    ],
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig": [
        'test "phase10 virtio input queue callback preflight tracks queue and ready-state gating" {',
    ],
    "zigux/tests/phase10_virtio_input_registration_preflight.zig": [
        'test "phase10 virtio input registration preflight helper exposes blocker tags and ready transition" {',
    ],
    "zigux/tests/phase10_virtio_input_status_drain.zig": [
        'test "phase10 virtio input status drain preserves suppressed timestamp counts while draining queued statuses" {',
    ],
    "zigux/tests/phase10_virtio_input_teardown_observation.zig": [
        'test "phase10 virtio input teardown observation keeps identity while resettable runtime state stays explicit" {',
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    check_markers(
        missing_markers,
        "module_note",
        read_text(root, "Documentation/zigux/phase10-virtio-input-module-slice.md"),
        MODULE_MARKERS,
    )
    check_markers(
        missing_markers,
        "input_helper",
        read_text(root, "drivers/virtio/virtio_input.zig"),
        INPUT_HELPER_MARKERS,
    )
    check_markers(
        missing_markers,
        "registration_helper",
        read_text(root, "drivers/virtio/virtio_input_registration_preflight.zig"),
        REGISTRATION_HELPER_MARKERS,
    )
    check_markers(
        missing_markers,
        "phase10_build",
        read_text(root, "zigux/tests/phase10_build.zig"),
        BUILD_MARKERS,
    )
    for rel_path, markers in TEST_MARKERS.items():
        check_markers(missing_markers, Path(rel_path).name, read_text(root, rel_path), markers)

    return [], missing_markers


def write_fixture(root: Path) -> None:
    fixture_contents = {
        "Documentation/zigux/phase10-virtio-input-module-slice.md": "\n".join(MODULE_MARKERS) + "\n",
        "drivers/virtio/virtio_input.zig": "\n".join(INPUT_HELPER_MARKERS) + "\n",
        "drivers/virtio/virtio_input_registration_preflight.zig": "\n".join(REGISTRATION_HELPER_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
    }
    for rel_path, markers in TEST_MARKERS.items():
        fixture_contents[rel_path] = "\n".join(markers) + "\n"

    for rel_path, content in fixture_contents.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def expect_missing_file(root: Path, expected: str, label: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"{label}:unexpected_missing_markers:{','.join(missing_markers)}")
    if expected not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_input_live_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-input-live-packet-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        case_count = 0

        module_note_path = root / "Documentation/zigux/phase10-virtio-input-module-slice.md"
        original_module_note = module_note_path.read_text(encoding="utf-8")
        module_note_path.write_text(
            original_module_note.replace(
                "zigux/tests/phase10_virtio_input_status_drain.zig",
                "zigux/tests/phase10_virtio_input_status_drain_missing.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "module_note:zigux/tests/phase10_virtio_input_status_drain.zig",
            "phase10-input-live-packet-self-test:module_note_status_path",
        )
        module_note_path.write_text(original_module_note, encoding="utf-8")
        case_count += 1

        input_helper_path = root / "drivers/virtio/virtio_input.zig"
        original_input_helper = input_helper_path.read_text(encoding="utf-8")
        input_helper_path.write_text(
            original_input_helper.replace(
                "pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
                "pub fn queueCallbackPreflightStatus(self: *const Self) QueueCallbackPreflightSummary {",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "input_helper:pub fn queueCallbackPreflightSummary(self: *const Self) QueueCallbackPreflightSummary {",
            "phase10-input-live-packet-self-test:helper_queue_callback",
        )
        input_helper_path.write_text(original_input_helper, encoding="utf-8")
        case_count += 1

        registration_helper_path = root / "drivers/virtio/virtio_input_registration_preflight.zig"
        original_registration_helper = registration_helper_path.read_text(encoding="utf-8")
        registration_helper_path.write_text(
            original_registration_helper.replace(
                "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
                "pub fn blockerName(blocker: RegistrationBlocker) []const u8 {",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "registration_helper:pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
            "phase10-input-live-packet-self-test:registration_helper_blocker_tag",
        )
        registration_helper_path.write_text(original_registration_helper, encoding="utf-8")
        case_count += 1

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                '"phase10-virtio-input-teardown-observation-tests"',
                '"phase10-virtio-input-teardown-observation-drift"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'phase10_build:"phase10-virtio-input-teardown-observation-tests"',
            "phase10-input-live-packet-self-test:build_teardown_test",
        )
        build_path.write_text(original_build, encoding="utf-8")
        case_count += 1

        direct_test_path = root / "zigux/tests/phase10_virtio_input.zig"
        original_direct_test = direct_test_path.read_text(encoding="utf-8")
        direct_test_path.write_text(
            original_direct_test.replace(
                'test "phase10 virtio input queue planning caps and refills event buffers" {',
                'test "phase10 virtio input queue planning drift" {',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            'phase10_virtio_input.zig:test "phase10 virtio input queue planning caps and refills event buffers" {',
            "phase10-input-live-packet-self-test:direct_test_title",
        )
        direct_test_path.write_text(original_direct_test, encoding="utf-8")
        case_count += 1

        (root / "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig").unlink()
        expect_missing_file(
            root,
            "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
            "phase10-input-live-packet-self-test:missing_queue_callback_test",
        )
        write_fixture(root)
        case_count += 1

    print("PHASE10_INPUT_LIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE10_INPUT_LIVE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the live Phase 10 virtio input queue-handling packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the checker's built-in synthetic drift tests",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_INPUT_LIVE_PACKET=fail")
        print("MISSING_PHASE10_INPUT_LIVE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_INPUT_LIVE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_INPUT_LIVE_PACKET=fail")
        print("MISSING_PHASE10_INPUT_LIVE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_INPUT_LIVE_MARKERS_END")
        return 1

    print("PHASE10_INPUT_LIVE_PACKET=pass")
    print(f"PHASE10_INPUT_LIVE_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE10_INPUT_LIVE_REQUIRED_MARKER_COUNT="
        f"{len(MODULE_MARKERS) + len(INPUT_HELPER_MARKERS) + len(REGISTRATION_HELPER_MARKERS) + len(BUILD_MARKERS) + sum(len(markers) for markers in TEST_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

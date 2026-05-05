#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase10-virtio-core-slice.md": [
        "drivers/virtio/virtio.c",
        "current `master` carries no standalone `zigux/tests/phase10_virtio_core_manifest.json` or `zigux/tests/phase10_virtio_core_survey.zig`",
        "queue callback bookkeeping, config-change bookkeeping, config-generation bookkeeping, interrupt-ack bookkeeping, lifecycle guard bookkeeping, reset replay bookkeeping",
        "make -C zigux phase10",
    ],
    "drivers/virtio/virtio.zig": [
        "pub const LifecycleGuardSummary = struct",
        "pub const ResetReplaySummary = struct",
        "pub fn lifecycleGuardSummary",
        "pub fn resetReplaySummary",
    ],
    "drivers/virtio/virtio_driver_id.zig": [
        "pub const any_id: u32 = 0xffff_ffff;",
        "pub fn registrationSummary",
        "pub fn driverIdMatchSummary",
    ],
    "scripts/zigux/check-phase10-core-packet.py": [
        "--self-test",
        "PHASE10_CORE_PACKET_SELF_TEST=pass",
    ],
    "zigux/Makefile": [
        "phase10-validate:",
        "scripts/zigux/check-phase10-core-packet.py",
        "phase10-test:",
        "zigux/tests/phase10_build.zig",
    ],
    "zigux/tests/phase10_build.zig": [
        "phase10-virtio-core-tests",
        "phase10-virtio-core-reset-queue-tests",
        "phase10-virtio-driver-id-tests",
        '"phase10_virtio_core_reset_queue.zig"',
        "test_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);",
    ],
    "zigux/tests/phase10_virtio_core.zig": [
        'test "phase10 virtio core tracks lifecycle guard bookkeeping across driver model milestones"',
        'test "phase10 virtio core exposes reset replay bookkeeping before reset clears state"',
        'test "phase10 virtio core keeps pending config generations visible in reset replay bookkeeping"',
    ],
    "zigux/tests/phase10_virtio_core_reset_queue.zig": [
        'test "phase10 virtio core blocks fresh queue registration once reset is required"',
        'test "phase10 virtio core blocks queue teardown and reshaping once reset is required but keeps replay summaries visible"',
        'test "phase10 virtio core blocks fresh driver attachment once reset is required"',
    ],
    "zigux/tests/phase10_virtio_driver_id.zig": [
        'test "phase10 virtio driver id helper records bounded registration identity strings"',
        'test "phase10 virtio driver id helper models wildcard and unmatched paths"',
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = "\n".join(REQUIRED_MARKERS.get(rel, ["// fixture"])) + "\n"
        path.write_text(text, encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_core_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase10-core-packet.py"
        checker_path.unlink()
        expect_missing_file(
            "missing_phase10_core_packet_checker",
            tmp_root,
            "scripts/zigux/check-phase10-core-packet.py",
        )
        write_fixture_root(tmp_root)

        reset_queue_path = tmp_root / "zigux" / "tests" / "phase10_virtio_core_reset_queue.zig"
        reset_queue_path.unlink()
        expect_missing_file(
            "missing_phase10_core_reset_queue_tests",
            tmp_root,
            "zigux/tests/phase10_virtio_core_reset_queue.zig",
        )
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase10-virtio-core-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace(
                "current `master` carries no standalone `zigux/tests/phase10_virtio_core_manifest.json` or `zigux/tests/phase10_virtio_core_survey.zig`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase10_core_slice_compact_packet_marker",
            tmp_root,
            "Documentation/zigux/phase10-virtio-core-slice.md: current `master` carries no standalone `zigux/tests/phase10_virtio_core_manifest.json` or `zigux/tests/phase10_virtio_core_survey.zig`",
        )
        slice_path.write_text(original_slice, encoding="utf-8")

        build_path = tmp_root / "zigux" / "tests" / "phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase10-virtio-core-reset-queue-tests", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase10_core_build_reset_queue_gate_marker",
            tmp_root,
            "zigux/tests/phase10_build.zig: phase10-virtio-core-reset-queue-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        makefile_path = tmp_root / "zigux" / "Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase10-core-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase10_core_makefile_checker_route_marker",
            tmp_root,
            "zigux/Makefile: scripts/zigux/check-phase10-core-packet.py",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        core_tests_path = tmp_root / "zigux" / "tests" / "phase10_virtio_core.zig"
        original_core_tests = core_tests_path.read_text(encoding="utf-8")
        core_tests_path.write_text(
            original_core_tests.replace(
                'test "phase10 virtio core exposes reset replay bookkeeping before reset clears state"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase10_core_reset_replay_test_marker",
            tmp_root,
            'zigux/tests/phase10_virtio_core.zig: test "phase10 virtio core exposes reset replay bookkeeping before reset clears state"',
        )

    case_count = 5
    print("PHASE10_CORE_PACKET_SELF_TEST=pass")
    print(f"PHASE10_CORE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current compact Phase 10 virtio core packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run packet checker self-tests without reading repository files.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CORE_PACKET_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_CORE_PACKET=fail")
        print("MISSING_PHASE10_CORE_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CORE_PACKET_MARKERS_END")
        return 1

    print("PHASE10_CORE_PACKET=pass")
    print(f"PHASE10_CORE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE10_CORE_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

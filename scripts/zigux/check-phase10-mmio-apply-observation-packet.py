#!/usr/bin/env python3
"""Validate the bounded Phase 10 virtio MMIO apply-observation packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FILES = [
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "drivers/virtio/virtio_mmio_apply_observation.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_build.zig",
]

SURVEY_NOTE_MARKERS = [
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
    "changed-byte coverage, no-op planning, and stale-plan rejection explicit",
    "zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all",
    "The shared gate should still be read as helper-local MMIO coverage plus one direct lab replay, one wrapper-facing verify replay, and one survey replay rather than a broader transport-backed replay.",
]

CLOSURE_NOTE_MARKERS = [
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig, `zigux/tests/phase10_virtio_mmio_survey.zig`",
    "phase10-mmio-config-write-apply-observation-helper",
]

HELPER_MARKERS = [
    "pub const ConfigWriteApplyObservationSummary = struct {",
    "pub fn summarizeConfigWriteApplyObservation(",
    "pub fn touchedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {",
    "pub fn changedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {",
    "pub fn changedBytesStayWithinTouchedMask(summary: ConfigWriteApplyObservationSummary) bool {",
    "pub fn appliesByteChanges(summary: ConfigWriteApplyObservationSummary) bool {",
]

MANIFEST_MARKERS = [
    '"id": "phase10-mmio-config-write-apply-observation-helper"',
    '"id": "phase10-mmio-config-write-apply-observation-replay"',
    '"zigux_destination": "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig"',
]

REPLAY_MARKERS = [
    'test "phase10 virtio mmio apply-observation replay keeps changed bytes explicit" {',
    "const summary = try apply_observation.summarizeConfigWriteApplyObservation(&device);",
    "try std.testing.expectEqual(@as(u4, 0b1111), summary.touched_byte_mask);",
    "try std.testing.expectEqual(@as(u3, 2), apply_observation.changedByteCount(summary));",
    'test "phase10 virtio mmio apply-observation replay keeps no-op and stale plans distinct" {',
    "try std.testing.expectError(",
    "error.ConfigWritePlanUnavailable,",
]

BUILD_SHARD_MARKERS = [
    '../../drivers/virtio/virtio_mmio_apply_observation.zig',
    'b.path("phase10_virtio_mmio_apply_observation_replay.zig")',
    '.name = "phase10-virtio-mmio-apply-observation-replay"',
    '"phase10-virtio-mmio-apply-observation-replay"',
    "Run the bounded Phase 10 virtio MMIO apply-observation replay",
]

SURVEY_GATE_MARKERS = [
    'try expectContains(survey_note, "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig");',
    'try expectContains(survey_note, "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig");',
    'try expectContains(',
    '        "zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all",',
    '    const replay_build_file = try readRepoRelative(',
    '        "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",',
    '    try expectContains(replay_build_file, "phase10_virtio_mmio_apply_observation_replay.zig");',
    '    try expectContains(replay_build_file, "\\\"phase10-virtio-mmio-apply-observation-replay\\\"");',
]

SHARED_BUILD_MARKERS = [
    "const virtio_mmio_apply_observation_module = b.createModule(.{",
    '.name = "phase10-virtio-mmio-apply-observation-tests"',
    "const run_phase10_virtio_mmio_apply_observation_tests = b.addRunArtifact(",
    '        "phase10-virtio-mmio-apply-observation-tests",',
    "phase10_virtio_mmio_apply_observation_step.dependOn(",
    "test_step.dependOn(&run_phase10_virtio_mmio_apply_observation_tests.step);",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path):
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    check_markers(
        missing_markers,
        "survey_note",
        read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md"),
        SURVEY_NOTE_MARKERS,
    )
    check_markers(
        missing_markers,
        "closure_note",
        read_text(root, "Documentation/zigux/phase10-closure-evidence.md"),
        CLOSURE_NOTE_MARKERS,
    )
    check_markers(
        missing_markers,
        "helper",
        read_text(root, "drivers/virtio/virtio_mmio_apply_observation.zig"),
        HELPER_MARKERS,
    )
    check_markers(
        missing_markers,
        "manifest",
        read_text(root, "zigux/tests/phase10_virtio_mmio_manifest.json"),
        MANIFEST_MARKERS,
    )
    check_markers(
        missing_markers,
        "replay",
        read_text(root, "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig"),
        REPLAY_MARKERS,
    )
    check_markers(
        missing_markers,
        "build_shard",
        read_text(root, "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig"),
        BUILD_SHARD_MARKERS,
    )
    check_markers(
        missing_markers,
        "survey_gate",
        read_text(root, "zigux/tests/phase10_virtio_mmio_survey.zig"),
        SURVEY_GATE_MARKERS,
    )
    check_markers(
        missing_markers,
        "shared_build",
        read_text(root, "zigux/tests/phase10_build.zig"),
        SHARED_BUILD_MARKERS,
    )
    return [], missing_markers


def write_fixture_files(root: Path) -> None:
    nl = "\n"
    files = {
        "Documentation/zigux/phase10-virtio-mmio-survey.md": nl.join(SURVEY_NOTE_MARKERS) + nl,
        "Documentation/zigux/phase10-closure-evidence.md": nl.join(CLOSURE_NOTE_MARKERS) + nl,
        "drivers/virtio/virtio_mmio_apply_observation.zig": nl.join(HELPER_MARKERS) + nl,
        "zigux/tests/phase10_virtio_mmio_manifest.json": nl.join(MANIFEST_MARKERS) + nl,
        "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig": nl.join(REPLAY_MARKERS) + nl,
        "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig": nl.join(BUILD_SHARD_MARKERS) + nl,
        "zigux/tests/phase10_virtio_mmio_survey.zig": nl.join(SURVEY_GATE_MARKERS) + nl,
        "zigux/tests/phase10_build.zig": nl.join(SHARED_BUILD_MARKERS) + nl,
    }
    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            "phase10-mmio-apply-observation-self-test:unexpected_missing_files:"
            + ",".join(missing_files)
        )
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            "phase10-mmio-apply-observation-self-test:expected="
            + expected
            + ":actual="
            + actual
        )
    path.write_text(original, encoding="utf-8")


def expect_missing_file(root: Path, rel_path: str) -> None:
    target = root / rel_path
    original = target.read_text(encoding="utf-8")
    target.unlink()
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            "phase10-mmio-apply-observation-self-test:unexpected_missing_markers:"
            + ",".join(missing_markers)
        )
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(
            "phase10-mmio-apply-observation-self-test:expected="
            + rel_path
            + ":actual="
            + actual
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_apply_observation_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_files(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit("baseline_failed")

        expect_missing_marker(
            root,
            "Documentation/zigux/phase10-virtio-mmio-survey.md",
            "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
            "zigux/tests/phase10_virtio_mmio_apply_observation_replay_missing.zig",
            "survey_note:zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
        )
        expect_missing_marker(
            root,
            "Documentation/zigux/phase10-virtio-mmio-survey.md",
            "zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all",
            "zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay_missing.zig --summary all",
            "survey_note:zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all",
        )
        expect_missing_marker(
            root,
            "Documentation/zigux/phase10-closure-evidence.md",
            "phase10-mmio-config-write-apply-observation-helper",
            "phase10-mmio-config-write-apply-observation-gap",
            "closure_note:phase10-mmio-config-write-apply-observation-helper",
        )
        expect_missing_marker(
            root,
            "drivers/virtio/virtio_mmio_apply_observation.zig",
            "pub fn summarizeConfigWriteApplyObservation(",
            "pub fn summarizeConfigWriteApplyObservationMissing(",
            "helper:pub fn summarizeConfigWriteApplyObservation(",
        )
        expect_missing_marker(
            root,
            "zigux/tests/phase10_virtio_mmio_manifest.json",
            '"id": "phase10-mmio-config-write-apply-observation-replay"',
            '"id": "phase10-mmio-config-write-apply-observation-replay-missing"',
            'manifest:"id": "phase10-mmio-config-write-apply-observation-replay"',
        )
        expect_missing_marker(
            root,
            "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
            'test "phase10 virtio mmio apply-observation replay keeps changed bytes explicit" {',
            'test "phase10 virtio mmio apply-observation replay drifts" {',
            'replay:test "phase10 virtio mmio apply-observation replay keeps changed bytes explicit" {',
        )
        expect_missing_marker(
            root,
            "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
            '.name = "phase10-virtio-mmio-apply-observation-replay"',
            '.name = "phase10-virtio-mmio-apply-observation-replay-gap"',
            'build_shard:.name = "phase10-virtio-mmio-apply-observation-replay"',
        )
        expect_missing_marker(
            root,
            "zigux/tests/phase10_virtio_mmio_survey.zig",
            '    try expectContains(replay_build_file, "\\"phase10-virtio-mmio-apply-observation-replay\\"");',
            '    try expectContains(replay_build_file, "\\"phase10-virtio-mmio-apply-observation-replay-missing\\"");',
            'survey_gate:    try expectContains(replay_build_file, "\\"phase10-virtio-mmio-apply-observation-replay\\"");',
        )
        expect_missing_marker(
            root,
            "zigux/tests/phase10_build.zig",
            '.name = "phase10-virtio-mmio-apply-observation-tests"',
            '.name = "phase10-virtio-mmio-apply-observation-tests-missing"',
            'shared_build:.name = "phase10-virtio-mmio-apply-observation-tests"',
        )
        expect_missing_file(
            root,
            "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
        )
        expect_missing_file(
            root,
            "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
        )

    print("PHASE10_MMIO_APPLY_OBSERVATION_PACKET_SELF_TEST=pass")
    print("PHASE10_MMIO_APPLY_OBSERVATION_PACKET_SELF_TEST_CASE_COUNT=11")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 10 virtio MMIO apply-observation packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in synthetic drift tests for the packet checker.",
    )
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root to validate. Defaults to the checker's inferred repo root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(Path(args.root))
    if missing_files:
        print("PHASE10_MMIO_APPLY_OBSERVATION_PACKET=fail")
        print("MISSING_PHASE10_MMIO_APPLY_OBSERVATION_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_MMIO_APPLY_OBSERVATION_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_MMIO_APPLY_OBSERVATION_PACKET=fail")
        print("MISSING_PHASE10_MMIO_APPLY_OBSERVATION_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MMIO_APPLY_OBSERVATION_MARKERS_END")
        return 1

    print("PHASE10_MMIO_APPLY_OBSERVATION_PACKET=pass")
    print(f"PHASE10_MMIO_APPLY_OBSERVATION_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "PHASE10_MMIO_APPLY_OBSERVATION_REQUIRED_MARKER_COUNT="
        + str(
            len(SURVEY_NOTE_MARKERS)
            + len(CLOSURE_NOTE_MARKERS)
            + len(HELPER_MARKERS)
            + len(MANIFEST_MARKERS)
            + len(REPLAY_MARKERS)
            + len(BUILD_SHARD_MARKERS)
            + len(SURVEY_GATE_MARKERS)
            + len(SHARED_BUILD_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

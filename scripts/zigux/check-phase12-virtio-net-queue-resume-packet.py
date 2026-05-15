#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/tests/phase12_build.zig").exists() and (
            candidate / "Documentation/zigux/phase12-virtio-net-survey.md"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

BUILD_PATH = "zigux/tests/phase12_build.zig"
SURVEY_NOTE_PATH = "Documentation/zigux/phase12-virtio-net-survey.md"
MANIFEST_PATH = "zigux/tests/phase12_virtio_net_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_net_survey.zig"
DRIVER_PATH = "drivers/net/virtio_net_queue_resume.zig"
TEST_PATH = "zigux/tests/phase12_virtio_net_queue_resume.zig"

REQUIRED_FILES = [
    BUILD_PATH,
    SURVEY_NOTE_PATH,
    MANIFEST_PATH,
    SURVEY_GATE_PATH,
    DRIVER_PATH,
    TEST_PATH,
]

BUILD_MARKERS = [
    '../../drivers/net/virtio_net_queue_resume.zig',
    '"phase12_virtio_net_queue_resume.zig"',
    '"virtio_net_queue_resume"',
    '.name = "phase12-virtio-net-queue-resume-tests"',
    'run_virtio_net_queue_resume_tests.setCwd(b.path("../.."));',
    'smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);',
    'test_step.dependOn(&run_virtio_net_queue_resume_tests.step);',
]

SURVEY_NOTE_MARKERS = [
    "PHASE12_STATUS=starter-present-queue-resume-transmit-recycle-followup",
    "`drivers/net/virtio_net_queue_resume.zig`",
    "`zigux/tests/phase12_virtio_net_queue_resume.zig`",
    "`summarizeQueueResume()`",
    "the current bounded queue-resume follow-up now also exposes `summarizeQueueResume()`",
    "the shared build route now carries the direct `virtio_net` syntax-lab smoke shard plus the dedicated `virtio_net_queue_resume` and `virtio_net_transmit_recycle` replays",
]

MANIFEST_MARKERS = [
    '"phase12-virtio-net-queue-resume-followup"',
    '"drivers/net/virtio_net_queue_resume.zig"',
    '"The shared Phase 12 build route now carries the direct `virtio_net` syntax-lab smoke shard plus the dedicated `virtio_net_transmit_recycle` and `virtio_net_queue_resume` replays alongside the shipped `virtio_scsi` packet."',
]

SURVEY_GATE_MARKERS = [
    "phase12 virtio net survey gate keeps the bounded transmit-recycle and queue-resume packet truthful",
    "drivers/net/virtio_net_queue_resume.zig",
    "zigux/tests/phase12_virtio_net_queue_resume.zig",
    "phase12 virtio net survey gate keeps queue resume replay wired into shared smoke route",
    "phase12-virtio-net-queue-resume-tests",
    "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
]

BUILD_EXACT_COUNTS = {
    "const virtio_net_queue_resume_tests = b.addTest(.{": 1,
    "run_virtio_net_queue_resume_tests.setCwd(": 1,
    "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);": 1,
    "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);": 1,
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def ensure_exact_counts(
    failures: list[str], label: str, text: str, expected_counts: dict[str, int]
) -> None:
    for marker, expected in expected_counts.items():
        actual = text.count(marker)
        if actual != expected:
            failures.append(
                f"{label}_exact_count:{marker}:expected={expected}:actual={actual}"
            )


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    ensure_contains(failures, "build", read_text(root, BUILD_PATH), BUILD_MARKERS)
    ensure_contains(
        failures, "survey_note", read_text(root, SURVEY_NOTE_PATH), SURVEY_NOTE_MARKERS
    )
    ensure_contains(
        failures, "manifest", read_text(root, MANIFEST_PATH), MANIFEST_MARKERS
    )
    ensure_contains(
        failures, "survey_gate", read_text(root, SURVEY_GATE_PATH), SURVEY_GATE_MARKERS
    )
    ensure_exact_counts(
        failures, "build", read_text(root, BUILD_PATH), BUILD_EXACT_COUNTS
    )
    return failures


def minimal_build() -> str:
    return """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_queue_resume_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });

    const virtio_net_queue_resume_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_queue_resume.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_queue_resume_root_module.addImport(
        "virtio_net_queue_resume",
        virtio_net_queue_resume_module,
    );

    const virtio_net_queue_resume_tests = b.addTest(.{
        .name = "phase12-virtio-net-queue-resume-tests",
        .root_module = virtio_net_queue_resume_root_module,
    });
    const run_virtio_net_queue_resume_tests = b.addRunArtifact(virtio_net_queue_resume_tests);
    run_virtio_net_queue_resume_tests.setCwd(b.path("../.."));

    const smoke_step = b.step("smoke", "Run Phase 12 virtio syntax smoke");
    smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);

    const test_step = b.step("test", "Run Phase 12 virtio packet tests");
    test_step.dependOn(&run_virtio_net_queue_resume_tests.step);
}
"""


def placeholder_for(rel_path: str) -> str:
    mapping = {
        BUILD_PATH: minimal_build(),
        SURVEY_NOTE_PATH: "\n".join(SURVEY_NOTE_MARKERS) + "\n",
        MANIFEST_PATH: "\n".join(MANIFEST_MARKERS) + "\n",
        SURVEY_GATE_PATH: "\n".join(SURVEY_GATE_MARKERS) + "\n",
        DRIVER_PATH: "// phase12 queue-resume placeholder\n",
        TEST_PATH: "// phase12 queue-resume test placeholder\n",
    }
    return mapping[rel_path]


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, placeholder_for(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-queue-resume-packet-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / DRIVER_PATH).unlink()
        expect_failure(base, f"missing_file:{DRIVER_PATH}")

        write_fixture_tree(base)
        (base / TEST_PATH).unlink()
        expect_failure(base, f"missing_file:{TEST_PATH}")

        write_fixture_tree(base)
        survey_note_path = base / SURVEY_NOTE_PATH
        survey_note_path.write_text(
            survey_note_path.read_text(encoding="utf-8").replace(
                SURVEY_NOTE_MARKERS[3],
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"survey_note:{SURVEY_NOTE_MARKERS[3]}")

        write_fixture_tree(base)
        manifest_path = base / MANIFEST_PATH
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8").replace(
                MANIFEST_MARKERS[0],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"manifest:{MANIFEST_MARKERS[0]}")

        write_fixture_tree(base)
        survey_gate_path = base / SURVEY_GATE_PATH
        survey_gate_path.write_text(
            survey_gate_path.read_text(encoding="utf-8").replace(
                SURVEY_GATE_MARKERS[3],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"survey_gate:{SURVEY_GATE_MARKERS[3]}")

        write_fixture_tree(base)
        build_path = base / BUILD_PATH
        build_path.write_text(
            build_path.read_text(encoding="utf-8").replace(
                'smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "build:smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);")

        write_fixture_tree(base)
        build_path = base / BUILD_PATH
        build_path.write_text(
            build_path.read_text(encoding="utf-8").replace(
                "const virtio_net_queue_resume_tests = b.addTest(.{",
                "const virtio_net_queue_resume_tests = b.addExecutable(.{",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "build_exact_count:const virtio_net_queue_resume_tests = b.addTest(.{:expected=1:actual=0",
        )

        print("PHASE12_QUEUE_RESUME_PACKET_SELF_TEST=pass")
        print("PHASE12_QUEUE_RESUME_PACKET_SELF_TEST_CASE_COUNT=7")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the shipped Phase 12 virtio-net queue-resume packet across the "
            "shared build route, the survey note, the survey gate, and the manifest."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_QUEUE_RESUME_PACKET=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_QUEUE_RESUME_PACKET=pass")
    print(f"PHASE12_QUEUE_RESUME_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

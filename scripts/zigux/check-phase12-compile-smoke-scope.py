#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/tests/phase12_build.zig").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"

REQUIRED_MARKERS = {
    PHASE12_BUILD_PATH: [
        'const virtio_net_survey_root_module = b.createModule(.{',
        '.root_source_file = b.path("phase12_virtio_net_survey.zig"),',
        'const phase12_virtio_net_survey_tests = b.addTest(.{',
        '.name = "phase12-virtio-net-survey-tests",',
        "const run_virtio_net_survey_tests = b.addRunArtifact(",
        "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
        "test_step.dependOn(&run_virtio_net_survey_tests.step);",
        "survey-gate smoke tests",
        "survey-gate tests",
    ],
}

EXACT_COUNT_MARKERS = {
    PHASE12_BUILD_PATH: {
        "b.createModule(.{": 11,
        ".addImport(": 5,
        "b.addTest(.{": 6,
        "b.addRunArtifact(": 6,
        "smoke_step.dependOn(": 6,
        "test_step.dependOn(": 6,
        "b.step(": 2,
    },
}

FORBIDDEN_MARKERS = {
    PHASE12_BUILD_PATH: [
        '"phase12_virtio_net_syntax_lab.zig"',
        '"phase12_virtio_scsi_syntax_lab.zig"',
        '"phase12_virtio_scsi_survey.zig"',
        '"phase12_nvme_pci.zig"',
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    build_path = root / PHASE12_BUILD_PATH
    if not build_path.exists():
        return [f"missing_file:{PHASE12_BUILD_PATH}"]

    text = build_path.read_text(encoding="utf-8")

    for marker in REQUIRED_MARKERS[PHASE12_BUILD_PATH]:
        if marker not in text:
            failures.append(f"missing_marker:{PHASE12_BUILD_PATH}:{marker}")

    for marker, expected in EXACT_COUNT_MARKERS[PHASE12_BUILD_PATH].items():
        actual = text.count(marker)
        if actual != expected:
            failures.append(
                f"wrong_count:{PHASE12_BUILD_PATH}:{marker}:expected={expected}:actual={actual}"
            )

    for marker in FORBIDDEN_MARKERS[PHASE12_BUILD_PATH]:
        if marker in text:
            failures.append(f"forbidden_marker:{PHASE12_BUILD_PATH}:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_phase12_build() -> str:
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

    const virtio_net_transmit_recycle_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_transmit_recycle_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_transmit_recycle.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_transmit_recycle_root_module.addImport(
        "virtio_net_transmit_recycle",
        virtio_net_transmit_recycle_module,
    );

    const virtio_net_receive_refill_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_receive_refill_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_receive_refill_replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_receive_refill_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_receive_refill_replay_root_module.addImport(
        "virtio_net_receive_refill_replay",
        virtio_net_receive_refill_replay_module,
    );

    const virtio_net_post_reset_replay_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_post_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_post_reset_replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_post_reset_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_post_reset_replay_root_module.addImport(
        "virtio_net_post_reset_replay",
        virtio_net_post_reset_replay_module,
    );

    const virtio_net_throughput_parity_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/net/virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_throughput_parity_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_throughput_parity.zig"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_throughput_parity_root_module.addImport(
        "virtio_net_throughput_parity",
        virtio_net_throughput_parity_module,
    );

    const virtio_net_survey_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_net_survey.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_virtio_net_queue_resume_tests = b.addTest(.{
        .name = "phase12-virtio-net-queue-resume-tests",
        .root_module = virtio_net_queue_resume_root_module,
    });
    const run_virtio_net_queue_resume_tests = b.addRunArtifact(
        phase12_virtio_net_queue_resume_tests,
    );

    const phase12_virtio_net_transmit_recycle_tests = b.addTest(.{
        .name = "phase12-virtio-net-transmit-recycle-tests",
        .root_module = virtio_net_transmit_recycle_root_module,
    });
    const run_virtio_net_transmit_recycle_tests = b.addRunArtifact(
        phase12_virtio_net_transmit_recycle_tests,
    );

    const phase12_virtio_net_receive_refill_replay_tests = b.addTest(.{
        .name = "phase12-virtio-net-receive-refill-replay-tests",
        .root_module = virtio_net_receive_refill_replay_root_module,
    });
    const run_virtio_net_receive_refill_replay_tests = b.addRunArtifact(
        phase12_virtio_net_receive_refill_replay_tests,
    );

    const phase12_virtio_net_post_reset_replay_tests = b.addTest(.{
        .name = "phase12-virtio-net-post-reset-replay-tests",
        .root_module = virtio_net_post_reset_replay_root_module,
    });
    const run_virtio_net_post_reset_replay_tests = b.addRunArtifact(
        phase12_virtio_net_post_reset_replay_tests,
    );

    const phase12_virtio_net_throughput_parity_tests = b.addTest(.{
        .name = "phase12-virtio-net-throughput-parity-tests",
        .root_module = virtio_net_throughput_parity_root_module,
    });
    const run_virtio_net_throughput_parity_tests = b.addRunArtifact(
        phase12_virtio_net_throughput_parity_tests,
    );

    const phase12_virtio_net_survey_tests = b.addTest(.{
        .name = "phase12-virtio-net-survey-tests",
        .root_module = virtio_net_survey_root_module,
    });
    const run_virtio_net_survey_tests = b.addRunArtifact(
        phase12_virtio_net_survey_tests,
    );

    const smoke_step = b.step(
        "smoke",
        "Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate smoke tests",
    );
    smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    smoke_step.dependOn(&run_virtio_net_survey_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate tests",
    );
    test_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    test_step.dependOn(&run_virtio_net_survey_tests.step);
}
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root / PHASE12_BUILD_PATH, minimal_phase12_build())


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-compile-smoke-scope-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / PHASE12_BUILD_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE12_BUILD_PATH}")

        for marker in REQUIRED_MARKERS[PHASE12_BUILD_PATH]:
            write_fixture_tree(base)
            path = base / PHASE12_BUILD_PATH
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(marker, "__REMOVED_PHASE12_MARKER__", 1), encoding="utf-8")
            expect_failure(base, f"missing_marker:{PHASE12_BUILD_PATH}:{marker}")

        replacement_map = {
            "b.createModule(.{": "b.createExecutable(.{",
            ".addImport(": ".addAnonymousImport(",
            "b.addTest(.{": "b.addExecutable(.{",
            "b.addRunArtifact(": "b.addInstallArtifact(",
            "smoke_step.dependOn(": "smoke_step.addError(",
            "test_step.dependOn(": "test_step.addError(",
            "b.step(": "b.option(",
        }
        for marker, expected in EXACT_COUNT_MARKERS[PHASE12_BUILD_PATH].items():
            write_fixture_tree(base)
            path = base / PHASE12_BUILD_PATH
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(marker, replacement_map[marker], 1), encoding="utf-8")
            expect_failure(
                base,
                f"wrong_count:{PHASE12_BUILD_PATH}:{marker}:expected={expected}:actual={expected - 1}",
            )

        for marker in FORBIDDEN_MARKERS[PHASE12_BUILD_PATH]:
            write_fixture_tree(base)
            path = base / PHASE12_BUILD_PATH
            path.write_text(path.read_text(encoding="utf-8") + f"\n{marker}\n", encoding="utf-8")
            expect_failure(base, f"forbidden_marker:{PHASE12_BUILD_PATH}:{marker}")

        case_count = (
            1
            + len(REQUIRED_MARKERS[PHASE12_BUILD_PATH])
            + len(EXACT_COUNT_MARKERS[PHASE12_BUILD_PATH])
            + len(FORBIDDEN_MARKERS[PHASE12_BUILD_PATH])
        )
        print("PHASE12_COMPILE_SMOKE_SCOPE_SELF_TEST=pass")
        print(f"PHASE12_COMPILE_SMOKE_SCOPE_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the current Phase 12 shared compile-smoke build remains "
            "aligned with the survey-gate-enabled virtio_net packet while keeping "
            "syntax-lab and driver-local shards out of the shared build."
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
            print(f"PHASE12_COMPILE_SMOKE_SCOPE=fail:{failure}")
        return 1

    print("PHASE12_COMPILE_SMOKE_SCOPE=pass")
    print("PHASE12_COMPILE_SMOKE_SCOPE_REQUIRED_FILE_COUNT=1")
    print(
        "PHASE12_COMPILE_SMOKE_SCOPE_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_MARKERS[PHASE12_BUILD_PATH])}"
    )
    print(
        "PHASE12_COMPILE_SMOKE_SCOPE_FORBIDDEN_MARKER_COUNT="
        f"{len(FORBIDDEN_MARKERS[PHASE12_BUILD_PATH])}"
    )
    print(
        "PHASE12_COMPILE_SMOKE_SCOPE_EXACT_COUNT_MARKER_COUNT="
        f"{len(EXACT_COUNT_MARKERS[PHASE12_BUILD_PATH])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

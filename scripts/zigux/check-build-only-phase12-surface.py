#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/tests/phase12_build.zig").exists() and (
            candidate / "zigux/Makefile"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH = (
    "drivers/net/virtio_net_queue_resume.zig"
)
PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH = (
    "drivers/net/virtio_net_transmit_recycle.zig"
)
PHASE12_VIRTIO_NET_POST_RESET_REPLAY_DRIVER_PATH = (
    "drivers/net/virtio_net_post_reset_replay.zig"
)
PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_DRIVER_PATH = (
    "drivers/net/virtio_net_throughput_parity.zig"
)
PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_queue_resume.zig"
)
PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig"
)
PHASE12_VIRTIO_NET_POST_RESET_REPLAY_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig"
)
PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_throughput_parity.zig"
)

REQUIRED_FILES = [
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
    PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH,
    PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH,
    PHASE12_VIRTIO_NET_POST_RESET_REPLAY_DRIVER_PATH,
    PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_DRIVER_PATH,
    PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH,
    PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH,
    PHASE12_VIRTIO_NET_POST_RESET_REPLAY_TEST_PATH,
    PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_TEST_PATH,
]

REQUIRED_MARKERS = {
    VALIDATOR_PATH: [
        BUILD_ONLY_CHECKER_PATH,
        RELEASE_READINESS_CHECKER_PATH,
        "make -C zigux phase12-validate",
        "stale reminder vocabulary",
    ],
    MAKEFILE_PATH: [
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
    PHASE12_BUILD_PATH: [
        '"phase12_virtio_net_queue_resume.zig"',
        '"phase12_virtio_net_transmit_recycle.zig"',
        '"phase12_virtio_net_post_reset_replay.zig"',
        '"phase12_virtio_net_throughput_parity.zig"',
        "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
        "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
        "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 build-only surface checker",
        "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Check current Phase 12 build-only surface",
        "        run: python3 scripts/zigux/check-build-only-phase12-surface.py",
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Check current Phase 12 release-readiness packet",
        "        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
        "- name: Validate current Phase 12 support bundle",
        "        run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 smoke packet",
        "        run: make -C zigux phase12-smoke",
        "- name: Run current Phase 12 shared test packet",
        "        run: make -C zigux phase12-test",
    ],
}

PHASE12_BUILD_EXACT_COUNTS = {
    "b.createModule(.{": 8,
    ".addImport(": 4,
    "b.addTest(.{": 4,
    "b.addRunArtifact(": 4,
    "smoke_step.dependOn(": 4,
    "test_step.dependOn(": 4,
    "b.step(": 2,
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    PHASE12_BUILD_PATH: [
        '"phase12_virtio_net.zig"',
        '"phase12_virtio_net_syntax_lab.zig"',
        '"phase12_virtio_scsi.zig"',
        '"phase12_virtio_scsi_syntax_lab.zig"',
        '"phase12_virtio_scsi_repeated_replan_gate.zig"',
        '"phase12_virtio_scsi_repeated_rollback_gate.zig"',
        '"phase12_virtio_scsi_packet.zig"',
    ],
}

EXACT_LINE_MARKER_PATHS = {WORKFLOW_PATH}


def has_required_marker(rel_path: str, text: str, marker: str) -> bool:
    if rel_path in EXACT_LINE_MARKER_PATHS:
        return marker in text.splitlines()
    return marker in text


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if not has_required_marker(rel_path, text, marker):
                failures.append(f"missing_marker:{rel_path}:{marker}")

    build_text = (root / PHASE12_BUILD_PATH).read_text(encoding="utf-8")
    for marker, expected in PHASE12_BUILD_EXACT_COUNTS.items():
        actual = build_text.count(marker)
        if actual != expected:
            failures.append(
                f"exact_count:{PHASE12_BUILD_PATH}:{marker}:expected={expected}:actual={actual}"
            )

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


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

    const smoke_step = b.step(
        "smoke",
        "Run the Phase 12 virtio_net queue-resume, transmit-recycle, post-reset replay, and throughput-parity smoke tests",
    );
    smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 12 virtio_net queue-resume, transmit-recycle, post-reset replay, and throughput-parity tests",
    );
    test_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
}
"""


def fixture_text(rel_path: str) -> str:
    if rel_path in REQUIRED_MARKERS:
        title = {
            VALIDATOR_PATH: "# Phase 12 Support Validator",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path == PHASE12_BUILD_PATH:
            return minimal_phase12_build()
        if rel_path in {VALIDATOR_PATH, MAKEFILE_PATH, WORKFLOW_PATH}:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    return "fixture\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def corrupt_exact_count(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    replacement = {
        "b.createModule(.{": "b.createExecutable(.{",
        ".addImport(": ".addAnonymousImport(",
        "b.addTest(.{": "b.addExecutable(.{",
        "b.addRunArtifact(": "b.addInstallArtifact(",
        "smoke_step.dependOn(": "smoke_step.addError(",
        "test_step.dependOn(": "test_step.addError(",
        "b.step(": "b.option(",
    }[marker]
    updated = text.replace(marker, replacement, 1)
    if updated == text:
        raise SystemExit(f"exact-count marker not corruptible: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path, markers in FORBIDDEN_MARKERS.items():
            for marker in markers:
                write_fixture_tree(base)
                write_text(
                    base / rel_path,
                    (base / rel_path).read_text(encoding="utf-8") + f"{marker}\n",
                )
                expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        for marker, expected in PHASE12_BUILD_EXACT_COUNTS.items():
            write_fixture_tree(base)
            corrupt_exact_count(base / PHASE12_BUILD_PATH, marker)
            expect_failure(
                base,
                f"exact_count:{PHASE12_BUILD_PATH}:{marker}:expected={expected}:actual={expected - 1}",
            )

        case_count = (
            len(REQUIRED_FILES)
            + len(marker_cases)
            + sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
            + len(PHASE12_BUILD_EXACT_COUNTS)
        )
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print(f"PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 12 build-only contract around the "
            "returned smoke-and-test wrappers and the split-helper virtio_net packet."
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
            print(f"PHASE12_BUILD_ONLY_SURFACE=fail:{failure}")
        return 1

    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(f"PHASE12_BUILD_ONLY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE12_BUILD_ONLY_REQUIRED_MARKER_COUNT={sum(len(m) for m in REQUIRED_MARKERS.values())}")
    print(f"PHASE12_BUILD_ONLY_EXACT_COUNT_MARKER_COUNT={len(PHASE12_BUILD_EXACT_COUNTS)}")
    print(f"PHASE12_BUILD_ONLY_FORBIDDEN_MARKER_COUNT={sum(len(m) for m in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
        if (candidate / "zigux/tests/phase12_build.zig").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH = "zigux/tests/phase12_virtio_net_syntax_lab.zig"
PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH = "zigux/tests/phase12_virtio_scsi_syntax_lab.zig"

REQUIRED_FILES = [
    PHASE12_BUILD_PATH,
    PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH,
    PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH,
]

BUILD_MARKERS = [
    '"phase12_virtio_net_syntax_lab.zig"',
    '"phase12_virtio_scsi_syntax_lab.zig"',
    '.name = "phase12-virtio-net-syntax-lab-tests"',
    '.name = "phase12-virtio-scsi-syntax-lab-tests"',
    'smoke_step.dependOn(&run_virtio_net_syntax_tests.step);',
    'smoke_step.dependOn(&run_syntax_tests.step);',
    'test_step.dependOn(&run_virtio_net_syntax_tests.step);',
    'test_step.dependOn(&run_syntax_tests.step);',
]

VIRTIO_NET_MARKERS = [
    'test "phase12 virtio net syntax lab keeps queue-topology, refill, recovery, control recovery, and payload shape exports reachable"',
    'test "phase12 virtio net syntax lab keeps control queue payload shaping separate from runtime commands"',
    'test "phase12 virtio net syntax lab keeps mergeable path and recycled room distinct through refill and recovery"',
    'test "phase12 virtio net syntax lab clears stale control queue and mergeable refill state across a second recovery cycle"',
    'test "phase12 virtio net syntax lab keeps rss payload shaping aligned with tunnel-header recovery"',
]

VIRTIO_SCSI_MARKERS = [
    'test "phase12 virtio scsi syntax lab keeps current queue-planning exports reachable"',
    'test "phase12 virtio scsi syntax lab keeps transport-reset recovery exports reachable"',
]

EXACT_COUNTS = {
    ("phase12_build", "smoke_step.dependOn("): 4,
    ("phase12_build", "test_step.dependOn("): 6,
    (
        "phase12_virtio_net_syntax_lab",
        'test "phase12 virtio net syntax lab ',
    ): 5,
    (
        "phase12_virtio_scsi_syntax_lab",
        'test "phase12 virtio scsi syntax lab ',
    ): 2,
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
    failures: list[str], label: str, text: str, marker: str, expected: int
) -> None:
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

    build_text = read_text(root, PHASE12_BUILD_PATH)
    virtio_net_text = read_text(root, PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH)
    virtio_scsi_text = read_text(root, PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH)

    ensure_contains(failures, "phase12_build", build_text, BUILD_MARKERS)
    ensure_contains(
        failures, "phase12_virtio_net_syntax_lab", virtio_net_text, VIRTIO_NET_MARKERS
    )
    ensure_contains(
        failures,
        "phase12_virtio_scsi_syntax_lab",
        virtio_scsi_text,
        VIRTIO_SCSI_MARKERS,
    )

    ensure_exact_counts(
        failures,
        "phase12_build",
        build_text,
        "smoke_step.dependOn(",
        EXACT_COUNTS[("phase12_build", "smoke_step.dependOn(")],
    )
    ensure_exact_counts(
        failures,
        "phase12_build",
        build_text,
        "test_step.dependOn(",
        EXACT_COUNTS[("phase12_build", "test_step.dependOn(")],
    )
    ensure_exact_counts(
        failures,
        "phase12_virtio_net_syntax_lab",
        virtio_net_text,
        'test "phase12 virtio net syntax lab ',
        EXACT_COUNTS[
            ("phase12_virtio_net_syntax_lab", 'test "phase12 virtio net syntax lab ')
        ],
    )
    ensure_exact_counts(
        failures,
        "phase12_virtio_scsi_syntax_lab",
        virtio_scsi_text,
        'test "phase12 virtio scsi syntax lab ',
        EXACT_COUNTS[
            ("phase12_virtio_scsi_syntax_lab", 'test "phase12 virtio scsi syntax lab ')
        ],
    )

    return failures


def placeholder_build() -> str:
    return """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_syntax_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_syntax_lab.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const syntax_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi_syntax_lab.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const repeated_replan_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi_repeated_replan_gate.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const packet_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi_packet.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const virtio_net_syntax_tests = b.addTest(.{
        .name = \"phase12-virtio-net-syntax-lab-tests\",
        .root_module = virtio_net_syntax_root_module,
    });
    const run_virtio_net_syntax_tests = b.addRunArtifact(virtio_net_syntax_tests);

    const syntax_tests = b.addTest(.{
        .name = \"phase12-virtio-scsi-syntax-lab-tests\",
        .root_module = syntax_root_module,
    });
    const run_syntax_tests = b.addRunArtifact(syntax_tests);

    const repeated_replan_tests = b.addTest(.{
        .name = \"phase12-virtio-scsi-repeated-replan-gate-tests\",
        .root_module = repeated_replan_root_module,
    });
    const run_repeated_replan_tests = b.addRunArtifact(repeated_replan_tests);

    const packet_tests = b.addTest(.{
        .name = \"phase12-virtio-scsi-packet-tests\",
        .root_module = packet_root_module,
    });
    const run_packet_tests = b.addRunArtifact(packet_tests);

    const smoke_step = b.step(\"smoke\", \"Run Phase 12 virtio syntax smoke\");
    smoke_step.dependOn(&run_virtio_net_syntax_tests.step);
    smoke_step.dependOn(&run_syntax_tests.step);
    smoke_step.dependOn(&run_repeated_replan_tests.step);
    smoke_step.dependOn(&run_packet_tests.step);

    const test_step = b.step(\"test\", \"Run Phase 12 virtio packet tests\");
    test_step.dependOn(&run_virtio_net_syntax_tests.step);
    test_step.dependOn(&run_syntax_tests.step);
    test_step.dependOn(&run_repeated_replan_tests.step);
    test_step.dependOn(&run_packet_tests.step);
    test_step.dependOn(&run_packet_tests.step);
    test_step.dependOn(&run_packet_tests.step);
}
"""


def placeholder_virtio_net() -> str:
    return "\n".join(VIRTIO_NET_MARKERS) + "\n"


def placeholder_virtio_scsi() -> str:
    return "\n".join(VIRTIO_SCSI_MARKERS) + "\n"


def placeholder_for(rel_path: str) -> str:
    mapping = {
        PHASE12_BUILD_PATH: placeholder_build(),
        PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH: placeholder_virtio_net(),
        PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH: placeholder_virtio_scsi(),
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
    base = Path(tempfile.mkdtemp(prefix="phase12-syntax-lab-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH}")

        write_fixture_tree(base)
        build_path = base / PHASE12_BUILD_PATH
        build_path.write_text(
            build_path.read_text(encoding="utf-8").replace(BUILD_MARKERS[4], "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_build:{BUILD_MARKERS[4]}")

        write_fixture_tree(base)
        virtio_net_path = base / PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH
        virtio_net_path.write_text(
            virtio_net_path.read_text(encoding="utf-8").replace(
                VIRTIO_NET_MARKERS[-1] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base, f"phase12_virtio_net_syntax_lab:{VIRTIO_NET_MARKERS[-1]}"
        )

        write_fixture_tree(base)
        virtio_net_path = base / PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH
        virtio_net_path.write_text(
            virtio_net_path.read_text(encoding="utf-8").replace(
                'test "phase12 virtio net syntax lab ',
                'note "phase12 virtio net syntax lab ',
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            'phase12_virtio_net_syntax_lab_exact_count:test "phase12 virtio net syntax lab :expected=5:actual=4',
        )

        write_fixture_tree(base)
        virtio_scsi_path = base / PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH
        virtio_scsi_path.write_text(
            virtio_scsi_path.read_text(encoding="utf-8").replace(
                VIRTIO_SCSI_MARKERS[-1] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base, f"phase12_virtio_scsi_syntax_lab:{VIRTIO_SCSI_MARKERS[-1]}"
        )

        print("PHASE12_SYNTAX_LAB_SURFACE_SELF_TEST=pass")
        print("PHASE12_SYNTAX_LAB_SURFACE_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 syntax-lab surface so the shared smoke "
            "wiring and the shipped virtio syntax-lab inventories stay explicit."
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
        print("PHASE12_SYNTAX_LAB_SURFACE=fail")
        print("PHASE12_SYNTAX_LAB_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_SYNTAX_LAB_SURFACE_FAILURES_END")
        return 1

    marker_count = (
        len(REQUIRED_FILES)
        + len(BUILD_MARKERS)
        + len(VIRTIO_NET_MARKERS)
        + len(VIRTIO_SCSI_MARKERS)
        + len(EXACT_COUNTS)
    )
    print("PHASE12_SYNTAX_LAB_SURFACE=pass")
    print(f"PHASE12_SYNTAX_LAB_SURFACE_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 12 cross-compile packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_CROSS_PACKET"

NOTE_PATH = Path("Documentation/zigux/phase12-cross-compile-smoke.md")
BUILD_PATH = Path("zigux/tests/phase12_cross_build.zig")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase12_cross_targets.json")
VIRTIO_NET_SYNTAX_PATH = Path("zigux/tests/phase12_virtio_net_syntax_lab.zig")
VIRTIO_SCSI_SYNTAX_PATH = Path("zigux/tests/phase12_virtio_scsi_syntax_lab.zig")
RAW_GITHUB_COVERAGE_PATH = Path("zigux/tests/phase12_raw_github_coverage_survey.zig")

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

NOTE_MARKERS = (
    "roadmap scope: keep existing Phase 12 `virtio_net`, `nvme_pci`, `virtio_scsi`, and bounded libbpf reviewability surfaces parse-valid across approved non-native musl targets without claiming new runtime parity",
    "compile entrypoint: `python3 scripts/zigux/check-phase12-cross.py --zig `",
    "build file: `zigux/tests/phase12_cross_build.zig`",
    "approved targets: `x86_64-linux-musl`, `aarch64-linux-musl`, `riscv64-linux-musl`",
    "phase12_virtio_net_syntax_lab.zig",
    "phase12_virtio_scsi_syntax_lab.zig",
    "phase12_raw_github_coverage_survey.zig",
    "rollback posture: if this packet drifts, repair the cross-build wiring or remove the stale claim before widening any Phase 12 driver implementation work",
)

BUILD_MARKERS = (
    'const cross_step = b.step("cross", "Compile the bounded Phase 12 packet for approved non-native musl targets");',
    '.root_source_file = b.path("phase12_virtio_net_syntax_lab.zig")',
    '.name = "phase12-cross-virtio-net-syntax-lab-tests"',
    '.root_source_file = b.path("phase12_virtio_scsi_syntax_lab.zig")',
    '.name = "phase12-cross-virtio-scsi-syntax-lab-tests"',
    '.root_source_file = b.path("phase12_raw_github_coverage_survey.zig")',
    '.name = "phase12-cross-raw-github-coverage-survey-tests"',
    '.name = "phase12-cross-libbpf-reviewability-tests"',
    "cross_step.dependOn(&phase12_virtio_net_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_virtio_scsi_syntax_lab_tests.step);",
    "cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);",
    "cross_step.dependOn(&phase12_libbpf_reviewability_tests.step);",
)

VIRTIO_NET_SYNTAX_MARKERS = (
    'test "phase12 virtio net syntax lab keeps queue-topology, refill, recovery, control recovery, and payload shape exports reachable"',
    'test "phase12 virtio net syntax lab keeps control queue payload shaping separate from runtime commands"',
    'test "phase12 virtio net syntax lab clears stale control queue and mergeable refill state across a second recovery cycle"',
)

VIRTIO_SCSI_SYNTAX_MARKERS = (
    'test "phase12 virtio scsi syntax lab keeps transport-reset recovery exports reachable"',
    "freezeForTransportReset",
)

RAW_GITHUB_COVERAGE_MARKERS = (
    'test "phase12 raw GitHub coverage manifest keeps the shared fallback split reviewable"',
    'Documentation/zigux/phase12-raw-github-coverage-survey.md',
    'Documentation/zigux/phase12-release-coordination-matrix.md',
)


class CheckFailure(RuntimeError):
    """Raised when the checker finds packet drift."""


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path.as_posix()}") from exc


def require_markers(text: str, relative_path: Path, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{relative_path.as_posix()} missing marker: {marker}")


def check_fixture(root: Path) -> None:
    fixture_text = read_text(root, FIXTURE_PATH)
    try:
        fixture = json.loads(fixture_text)
    except json.JSONDecodeError as exc:
        raise CheckFailure(f"{FIXTURE_PATH.as_posix()} is not valid JSON") from exc

    if fixture.get("phase") != "Phase 12":
        raise CheckFailure("phase12 cross fixture phase drifted")
    if fixture.get("build_file") != BUILD_PATH.as_posix():
        raise CheckFailure("phase12 cross fixture build_file drifted")
    if fixture.get("build_step") != "cross":
        raise CheckFailure("phase12 cross fixture build_step drifted")
    if fixture.get("target_count") != len(EXPECTED_TARGETS):
        raise CheckFailure("phase12 cross fixture target_count drifted")

    targets = fixture.get("targets")
    if targets != EXPECTED_TARGETS:
        raise CheckFailure("phase12 cross fixture approved targets drifted")

    lane_key = fixture.get("lane_key")
    if not isinstance(lane_key, str) or not lane_key.startswith("P12-L"):
        raise CheckFailure("phase12 cross fixture lane_key is not a Phase 12 lane tag")


def check_packet(root: Path) -> None:
    check_fixture(root)
    require_markers(read_text(root, NOTE_PATH), NOTE_PATH, NOTE_MARKERS)
    require_markers(read_text(root, BUILD_PATH), BUILD_PATH, BUILD_MARKERS)
    require_markers(
        read_text(root, VIRTIO_NET_SYNTAX_PATH),
        VIRTIO_NET_SYNTAX_PATH,
        VIRTIO_NET_SYNTAX_MARKERS,
    )
    require_markers(
        read_text(root, VIRTIO_SCSI_SYNTAX_PATH),
        VIRTIO_SCSI_SYNTAX_PATH,
        VIRTIO_SCSI_SYNTAX_MARKERS,
    )
    require_markers(
        read_text(root, RAW_GITHUB_COVERAGE_PATH),
        RAW_GITHUB_COVERAGE_PATH,
        RAW_GITHUB_COVERAGE_MARKERS,
    )


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    write_text(
        root,
        NOTE_PATH,
        "# Phase 12 Cross Compile Smoke\n"
        "This note records the bounded non-native compile-smoke packet for the current Phase 12 driver tranche.\n"
        "\n"
        "- roadmap scope: keep existing Phase 12 `virtio_net`, `nvme_pci`, `virtio_scsi`, and bounded libbpf reviewability surfaces parse-valid across approved non-native musl targets without claiming new runtime parity\n"
        "- compile entrypoint: `python3 scripts/zigux/check-phase12-cross.py --zig `\n"
        "- build file: `zigux/tests/phase12_cross_build.zig`\n"
        "- approved targets: `x86_64-linux-musl`, `aarch64-linux-musl`, `riscv64-linux-musl`\n"
        "- current packet now includes the landed `phase12_virtio_net_syntax_lab.zig`, `phase12_virtio_scsi_syntax_lab.zig`, and `phase12_raw_github_coverage_survey.zig` gates in addition to the existing driver and libbpf survey modules\n"
        "- rollback posture: if this packet drifts, repair the cross-build wiring or remove the stale claim before widening any Phase 12 driver implementation work\n",
    )
    write_text(
        root,
        BUILD_PATH,
        """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const cross_step = b.step(\"cross\", \"Compile the bounded Phase 12 packet for approved non-native musl targets\");
    const phase12_virtio_net_syntax_lab_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_syntax_lab.zig\"),
    });
    const phase12_virtio_net_syntax_lab_tests = b.addTest(.{
        .name = \"phase12-cross-virtio-net-syntax-lab-tests\",
        .root_module = phase12_virtio_net_syntax_lab_module,
    });
    const phase12_virtio_scsi_syntax_lab_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi_syntax_lab.zig\"),
    });
    const phase12_virtio_scsi_syntax_lab_tests = b.addTest(.{
        .name = \"phase12-cross-virtio-scsi-syntax-lab-tests\",
        .root_module = phase12_virtio_scsi_syntax_lab_module,
    });
    const phase12_raw_github_coverage_survey_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_raw_github_coverage_survey.zig\"),
    });
    const phase12_raw_github_coverage_survey_tests = b.addTest(.{
        .name = \"phase12-cross-raw-github-coverage-survey-tests\",
        .root_module = phase12_raw_github_coverage_survey_module,
    });
    const phase12_libbpf_reviewability_tests = b.addTest(.{
        .name = \"phase12-cross-libbpf-reviewability-tests\",
        .root_module = phase12_raw_github_coverage_survey_module,
    });
    cross_step.dependOn(&phase12_virtio_net_syntax_lab_tests.step);
    cross_step.dependOn(&phase12_virtio_scsi_syntax_lab_tests.step);
    cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);
    cross_step.dependOn(&phase12_libbpf_reviewability_tests.step);
}
""",
    )
    write_text(
        root,
        FIXTURE_PATH,
        json.dumps(
            {
                "phase": "Phase 12",
                "lane_key": "P12-L05",
                "build_file": "zigux/tests/phase12_cross_build.zig",
                "build_step": "cross",
                "target_count": 3,
                "targets": EXPECTED_TARGETS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        VIRTIO_NET_SYNTAX_PATH,
        "\n".join(VIRTIO_NET_SYNTAX_MARKERS) + "\n",
    )
    write_text(
        root,
        VIRTIO_SCSI_SYNTAX_PATH,
        "\n".join(VIRTIO_SCSI_SYNTAX_MARKERS) + "\n",
    )
    write_text(
        root,
        RAW_GITHUB_COVERAGE_PATH,
        "\n".join(RAW_GITHUB_COVERAGE_MARKERS) + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_fixture_tree(root)

        check_packet(root)
        cases += 1

        bad_targets = json.loads((root / FIXTURE_PATH).read_text(encoding="utf-8"))
        bad_targets["target_count"] = 4
        write_text(root, FIXTURE_PATH, json.dumps(bad_targets, indent=2) + "\n")
        try:
            check_packet(root)
        except CheckFailure as exc:
            if "target_count" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected target_count drift to fail")

        write_fixture_tree(root)
        write_text(root, NOTE_PATH, "# note missing compile packet markers\n")
        try:
            check_packet(root)
        except CheckFailure as exc:
            if NOTE_PATH.as_posix() not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected note drift to fail")

        write_fixture_tree(root)
        build_text = (root / BUILD_PATH).read_text(encoding="utf-8")
        build_text = build_text.replace(
            "cross_step.dependOn(&phase12_raw_github_coverage_survey_tests.step);\n",
            "",
        )
        write_text(root, BUILD_PATH, build_text)
        try:
            check_packet(root)
        except CheckFailure as exc:
            if "phase12_raw_github_coverage_survey_tests" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected build drift to fail")

        write_fixture_tree(root)
        write_text(root, RAW_GITHUB_COVERAGE_PATH, "placeholder\n")
        try:
            check_packet(root)
        except CheckFailure as exc:
            if RAW_GITHUB_COVERAGE_PATH.as_posix() not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected raw coverage drift to fail")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the current Phase 12 cross-compile packet."
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        check_packet(Path(args.root))
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail")
        print(f"{CHECK_NAME}_ERROR={exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_TARGET_COUNT={len(EXPECTED_TARGETS)}")
    print(f"{CHECK_NAME}_NOTE={NOTE_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

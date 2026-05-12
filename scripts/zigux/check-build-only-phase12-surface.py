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
        if (candidate / "scripts/zigux/README.md").exists() and (
            candidate / ".github/workflows/zigux-bootstrap.yml"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
LIBBPF_VERIFY_SHARD_NOTE_PATH = (
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
)
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
PHASE12_DRIVER_PATH = "drivers/scsi/virtio_scsi.zig"
PHASE12_TEST_PATH = "zigux/tests/phase12_virtio_scsi.zig"
PHASE12_SYNTAX_LAB_PATH = "zigux/tests/phase12_virtio_scsi_syntax_lab.zig"
PHASE12_REPEATED_REPLAN_PATH = "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig"

REQUIRED_FILES = [
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    LIBBPF_VERIFY_SHARD_NOTE_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    PHASE12_DRIVER_PATH,
    PHASE12_TEST_PATH,
    PHASE12_SYNTAX_LAB_PATH,
    PHASE12_REPEATED_REPLAN_PATH,
]

FORBIDDEN_FILES = [
    "scripts/zigux/validate-phase12.py",
]

SCRIPTS_README_MARKERS = [
    "Phase 12 flow -",
    "`check-build-only-phase12-surface.py`",
    "`zigux/tests/phase12_build.zig`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12`",
    "without implying removed `validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build, or `phase12-validate` surfaces that are not on `master`.",
]

TESTS_README_MARKERS = [
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zigux/tests/phase12_build.zig`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12`",
    "without implying removed `validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build, or `phase12-validate` surfaces that are not on `master`",
]

RELEASE_READINESS_SURVEY_MARKERS = [
    "`PHASE12_STATUS=active`",
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "the parked verify-shard note still governs the shared libbpf packet",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py`",
]

RELEASE_SEQUENCING_MARKERS = [
    "`PHASE12_STATUS=active`",
    "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
    "shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py`",
    "Current `master` already keeps the compact release-coordination matrix explicit",
]

RELEASE_COORDINATION_MATRIX_MARKERS = [
    "`PHASE12_STATUS=active`",
    "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
    "Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packet and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs;",
    "rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO wording",
]

RELEASE_CLOSURE_CHECKLIST_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "The bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill must remain described as lab-only reversible-delivery evidence rather than closure-ready runtime recovery.",
    "Until then, release planning should name only the shipped smoke preflight routes, the shared build-and-make replay path, the narrow build-only contract checker, the shared fallback overview note, the shared libbpf anti-overlap companion, and the bounded storage rollback drill.",
    "During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain shared-tree raw-read anchors for the smoke-first packet rather than extra commit-pinned fallback artifacts.",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 12 build-only surface checker",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "Check Phase 12 build-only surface",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "Run focused Phase 12 smoke shard",
    "make -C zigux phase12-smoke",
    "Run Phase 12 complex driver and libbpf tests",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
]

MAKEFILE_MARKERS = [
    "phase12-smoke:",
    "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-smoke phase12-test",
]

PHASE12_BUILD_MARKERS = [
    '../../drivers/scsi/virtio_scsi.zig',
    '"phase12_virtio_scsi.zig"',
    '"phase12_virtio_scsi_syntax_lab.zig"',
    '"phase12_virtio_scsi_repeated_replan_gate.zig"',
    '.name = "phase12-virtio-scsi-tests"',
    '.name = "phase12-virtio-scsi-syntax-lab-tests"',
    '.name = "phase12-virtio-scsi-repeated-replan-gate-tests"',
    'run_contract_tests.setCwd(b.path("../.."));',
    'run_syntax_tests.setCwd(b.path("../.."));',
    'run_repeated_replan_tests.setCwd(b.path("../.."));',
    'const smoke_step = b.step("smoke", "Run Phase 12 virtio-scsi syntax smoke");',
    'smoke_step.dependOn(&run_syntax_tests.step);',
    'smoke_step.dependOn(&run_repeated_replan_tests.step);',
    'const test_step = b.step("test", "Run Phase 12 virtio-scsi tranche tests");',
    'test_step.dependOn(&run_contract_tests.step);',
    'test_step.dependOn(&run_syntax_tests.step);',
    'test_step.dependOn(&run_repeated_replan_tests.step);',
]

PHASE12_BUILD_EXACT_COUNTS = {
    "b.addTest(.{": 3,
    "setCwd(": 3,
    "smoke_step.dependOn(": 2,
    "test_step.dependOn(": 3,
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

    for rel_path in FORBIDDEN_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    if failures:
        return failures

    ensure_contains(
        failures,
        "scripts_readme",
        read_text(root, SCRIPTS_README_PATH),
        SCRIPTS_README_MARKERS,
    )
    ensure_contains(
        failures,
        "tests_readme",
        read_text(root, TESTS_README_PATH),
        TESTS_README_MARKERS,
    )
    ensure_contains(
        failures,
        "release_readiness_survey",
        read_text(root, RELEASE_READINESS_SURVEY_PATH),
        RELEASE_READINESS_SURVEY_MARKERS,
    )
    ensure_contains(
        failures,
        "release_sequencing",
        read_text(root, RELEASE_SEQUENCING_PATH),
        RELEASE_SEQUENCING_MARKERS,
    )
    ensure_contains(
        failures,
        "release_coordination_matrix",
        read_text(root, RELEASE_COORDINATION_MATRIX_PATH),
        RELEASE_COORDINATION_MATRIX_MARKERS,
    )
    ensure_contains(
        failures,
        "release_closure_checklist",
        read_text(root, RELEASE_CLOSURE_CHECKLIST_PATH),
        RELEASE_CLOSURE_CHECKLIST_MARKERS,
    )
    ensure_contains(
        failures, "workflow", read_text(root, WORKFLOW_PATH), WORKFLOW_MARKERS
    )
    ensure_contains(
        failures, "makefile", read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS
    )

    phase12_build = read_text(root, PHASE12_BUILD_PATH)
    ensure_contains(failures, "phase12_build", phase12_build, PHASE12_BUILD_MARKERS)
    ensure_exact_counts(
        failures, "phase12_build", phase12_build, PHASE12_BUILD_EXACT_COUNTS
    )

    return failures


def minimal_scripts_readme() -> str:
    return "\n".join(["# scripts/zigux", *SCRIPTS_README_MARKERS, ""])


def minimal_tests_readme() -> str:
    return "\n".join(["# zigux/tests", *TESTS_README_MARKERS, ""])


def minimal_release_readiness_survey() -> str:
    return "\n".join(
        ["# Phase 12 Release Readiness Survey", *RELEASE_READINESS_SURVEY_MARKERS, ""]
    )


def minimal_release_sequencing() -> str:
    return "\n".join(["# Phase 12 Release Sequencing", *RELEASE_SEQUENCING_MARKERS, ""])


def minimal_release_coordination_matrix() -> str:
    return "\n".join(
        ["# Phase 12 Release Coordination Matrix", *RELEASE_COORDINATION_MATRIX_MARKERS, ""]
    )


def minimal_release_closure_checklist() -> str:
    return "\n".join(
        ["# Phase 12 Release Closure Checklist", *RELEASE_CLOSURE_CHECKLIST_MARKERS, ""]
    )


def minimal_workflow() -> str:
    return "\n".join(WORKFLOW_MARKERS) + "\n"


def minimal_makefile() -> str:
    return "\n".join(MAKEFILE_MARKERS) + "\n"


def minimal_phase12_build() -> str:
    return """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_scsi_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/scsi/virtio_scsi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_root_module.addImport("virtio_scsi", virtio_scsi_module);

    const syntax_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_syntax_lab.zig"),
        .target = target,
        .optimize = optimize,
    });
    syntax_root_module.addImport("virtio_scsi", virtio_scsi_module);

    const repeated_replan_root_module = b.createModule(.{
        .root_source_file = b.path("phase12_virtio_scsi_repeated_replan_gate.zig"),
        .target = target,
        .optimize = optimize,
    });
    repeated_replan_root_module.addImport("virtio_scsi", virtio_scsi_module);

    const contract_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-tests",
        .root_module = contract_root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const syntax_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-syntax-lab-tests",
        .root_module = syntax_root_module,
    });
    const run_syntax_tests = b.addRunArtifact(syntax_tests);
    run_syntax_tests.setCwd(b.path("../.."));

    const repeated_replan_tests = b.addTest(.{
        .name = "phase12-virtio-scsi-repeated-replan-gate-tests",
        .root_module = repeated_replan_root_module,
    });
    const run_repeated_replan_tests = b.addRunArtifact(repeated_replan_tests);
    run_repeated_replan_tests.setCwd(b.path("../.."));

    const smoke_step = b.step("smoke", "Run Phase 12 virtio-scsi syntax smoke");
    smoke_step.dependOn(&run_syntax_tests.step);
    smoke_step.dependOn(&run_repeated_replan_tests.step);

    const test_step = b.step("test", "Run Phase 12 virtio-scsi tranche tests");
    test_step.dependOn(&run_contract_tests.step);
    test_step.dependOn(&run_syntax_tests.step);
    test_step.dependOn(&run_repeated_replan_tests.step);
}
"""


def placeholder_for(rel_path: str) -> str:
    if rel_path == SCRIPTS_README_PATH:
        return minimal_scripts_readme()
    if rel_path == TESTS_README_PATH:
        return minimal_tests_readme()
    if rel_path == RELEASE_READINESS_SURVEY_PATH:
        return minimal_release_readiness_survey()
    if rel_path == RELEASE_SEQUENCING_PATH:
        return minimal_release_sequencing()
    if rel_path == RELEASE_COORDINATION_MATRIX_PATH:
        return minimal_release_coordination_matrix()
    if rel_path == RELEASE_CLOSURE_CHECKLIST_PATH:
        return minimal_release_closure_checklist()
    if rel_path == WORKFLOW_PATH:
        return minimal_workflow()
    if rel_path == MAKEFILE_PATH:
        return minimal_makefile()
    if rel_path == PHASE12_BUILD_PATH:
        return minimal_phase12_build()
    if rel_path.endswith(".zig"):
        return "// phase12 placeholder\n"
    return ""


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
    base = Path(tempfile.mkdtemp(prefix="phase12-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        tests_readme_path = base / TESTS_README_PATH
        release_readiness_survey_path = base / RELEASE_READINESS_SURVEY_PATH
        release_sequencing_path = base / RELEASE_SEQUENCING_PATH
        release_coordination_matrix_path = base / RELEASE_COORDINATION_MATRIX_PATH
        release_closure_checklist_path = base / RELEASE_CLOSURE_CHECKLIST_PATH
        libbpf_verify_shard_note_path = base / LIBBPF_VERIFY_SHARD_NOTE_PATH
        workflow_path = base / WORKFLOW_PATH
        makefile_path = base / MAKEFILE_PATH
        phase12_build_path = base / PHASE12_BUILD_PATH

        libbpf_verify_shard_note_path.unlink()
        expect_failure(
            base,
            f"missing_file:{LIBBPF_VERIFY_SHARD_NOTE_PATH}",
        )

        write_fixture_tree(base)
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(
                TESTS_README_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"tests_readme:{TESTS_README_MARKERS[2]}",
        )

        write_fixture_tree(base)
        release_readiness_survey_path.write_text(
            release_readiness_survey_path.read_text(encoding="utf-8").replace(
                RELEASE_READINESS_SURVEY_MARKERS[3], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_readiness_survey:{RELEASE_READINESS_SURVEY_MARKERS[3]}",
        )

        write_fixture_tree(base)
        release_sequencing_path.write_text(
            release_sequencing_path.read_text(encoding="utf-8").replace(
                RELEASE_SEQUENCING_MARKERS[4], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_sequencing:{RELEASE_SEQUENCING_MARKERS[4]}",
        )

        write_fixture_tree(base)
        release_coordination_matrix_path.write_text(
            release_coordination_matrix_path.read_text(encoding="utf-8").replace(
                RELEASE_COORDINATION_MATRIX_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_coordination_matrix:{RELEASE_COORDINATION_MATRIX_MARKERS[2]}",
        )

        write_fixture_tree(base)
        release_closure_checklist_path.writeText(
            release_closure_checklist_path.read_text(encoding="utf-8").replace(
                RELEASE_CLOSURE_CHECKLIST_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_closure_checklist:{RELEASE_CLOSURE_CHECKLIST_MARKERS[2]}",
        )

        write_fixture_tree(base)
        release_closure_checklist_path.write_text(
            release_closure_checklist_path.read_text(encoding="utf-8").replace(
                RELEASE_CLOSURE_CHECKLIST_MARKERS[4], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_closure_checklist:{RELEASE_CLOSURE_CHECKLIST_MARKERS[4]}",
        )

        write_fixture_tree(base)
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "make -C zigux phase12-smoke", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, "workflow:make -C zigux phase12-smoke")

        write_fixture_tree(base)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(
                "phase12: phase12-smoke phase12-test", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, "makefile:phase12: phase12-smoke phase12-test")

        write_fixture_tree(base)
        phase12_build_path.write_text(
            phase12_build_path.read_text(encoding="utf-8").replace(
                'test_step.dependOn(&run_contract_tests.step);\n', "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "phase12_build:test_step.dependOn(&run_contract_tests.step);",
        )

        write_fixture_tree(base)
        phase12_build_path.write_text(
            phase12_build_path.read_text(encoding="utf-8").replace(
                'smoke_step.dependOn(&run_repeated_replan_tests.step);\n', "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "phase12_build:smoke_step.dependOn(&run_repeated_replan_tests.step);",
        )

        write_fixture_tree(base)
        phase12_build_path.write_text(
            phase12_build_path.read_text(encoding="utf-8").replace(
                'const repeated_replan_tests = b.addTest(.{',
                'const repeated_replan_tests = b.addExecutable(.{',
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "phase12_build_exact_count:b.addTest(.{:expected=3:actual=2",
        )

        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=12")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 12 build-only contract around the "
            "shipped virtio-scsi smoke and tranche replay."
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
        print("PHASE12_BUILD_ONLY_SURFACE=fail")
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_END")
        return 1

    marker_count = (
        len(REQUIRED_FILES)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(RELEASE_READINESS_SURVEY_MARKERS)
        + len(RELEASE_SEQUENCING_MARKERS)
        + len(RELEASE_COORDINATION_MATRIX_MARKERS)
        + len(RELEASE_CLOSURE_CHECKLIST_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(MAKEFILE_MARKERS)
        + len(PHASE12_BUILD_MARKERS)
        + len(PHASE12_BUILD_EXACT_COUNTS)
    )
    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(f"PHASE12_BUILD_ONLY_SURFACE_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
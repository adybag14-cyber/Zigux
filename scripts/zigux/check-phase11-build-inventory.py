#!/usr/bin/env python3
"""Fail-closed checker for the current-head Phase 11 build inventory packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[3]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)

REQUIRED_PROOF_ROUTE = {
    "proof_build_file": "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_replay_command": "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_step_name": "test",
    "proof_step_description": "Run the focused Phase 11 HVC cleanup packet proof",
    "proof_test_artifact_name": "phase11-hvc-cleanup-packet-proof",
    "proof_root_source_file": "phase11_hvc_cleanup_packet_proof.zig",
}

EXACT_CURRENT_CHECKS = (
    "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    "python3 scripts/zigux/check-phase11-build-inventory.py",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

BUILD_FILE_PATH = Path(REQUIRED_PROOF_ROUTE["proof_build_file"])
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
HVC_VALIDATION_MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
HV_OPS_BUILD_PATH = Path("zigux/tests/phase11_hvc_hv_ops_layout_build.zig")
EXPORT_BUILD_PATH = Path("zigux/tests/phase11_hvc_export_surface_layout_build.zig")

REQUIRED_BUILD_TEXT_MARKERS = (
    "phase11_hvc_cleanup_packet_proof.zig",
    "phase11-hvc-cleanup-packet-proof",
    "Run the focused Phase 11 HVC cleanup packet proof",
)

FORBIDDEN_BUILD_TEXT_MARKERS = (
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
)

REQUIRED_BUILD_TEST_NAMES = (
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
)

REQUIRED_SHARED_DEPEND_STEPS: tuple[str, ...] = ()

REQUIRED_MODULE_PATHS = {
    "hv_ops_proof_module": "phase11_hvc_hv_ops_layout_proof.zig",
    "export_surface_proof_module": "phase11_hvc_export_surface_layout_proof.zig",
    "proof_module": "phase11_hvc_cleanup_packet_proof.zig",
}

REQUIRED_TEST_ROOT_MODULES = {
    "phase11-hvc-hv-ops-layout-proof-tests": "hv_ops_proof_module",
    "phase11-hvc-export-surface-layout-proof-tests": "export_surface_proof_module",
    "phase11-hvc-cleanup-packet-proof": "proof_module",
}

REQUIRED_DEDICATED_SURVEY_REPLAYS: tuple[str, ...] = ()

REQUIRED_SHARED_ADJUNCT_REPLAYS = (
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
)

REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS = (
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
)

REQUIRED_REPLAY_MARKERS: set[tuple[str, str]] = set()

REQUIRED_HVC_VALIDATION_MATRIX_MARKERS = (
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "current-head HVC continuity packet rather than a whole-Phase-11 replay roster",
)

REQUIRED_SCRIPTS_ROOT_MARKERS = (
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`make -C zigux phase11-validate`",
)

REQUIRED_HV_OPS_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig")',
    '.name = "phase11-hvc-hv-ops-layout-proof-tests"',
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig")',
    '.name = "phase11-hvc-export-surface-layout-proof-tests"',
    'const test_step = b.step("test", "Run the focused Phase 11 exported-header proofs");',
)

REQUIRED_EXPORT_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig")',
    '.name = "phase11-hvc-export-surface-layout-proof"',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
)

REQUIRED_WORKFLOW_PHASE11_STEPS = (
    (
        "Self-test current Phase 11 build inventory checker",
        "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    ),
    (
        "Check current Phase 11 build inventory packet",
        "python3 scripts/zigux/check-phase11-build-inventory.py",
    ),
    (
        "Self-test current Phase 11 HVC cleanup current-head checker",
        "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    ),
    (
        "Check current Phase 11 HVC cleanup current-head packet",
        "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    ),
    (
        "Run current Phase 11 HVC hv_ops layout proof",
        "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    ),
    (
        "Run current Phase 11 HVC export surface layout proof",
        "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    ),
    (
        "Run current Phase 11 HVC cleanup packet proof",
        "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    ),
    (
        "Run current Phase 11 HVC targetless-unregister gap witness",
        "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    ),
)

REQUIRED_MAKEFILE_ROUTE_MARKERS = (
    "phase11-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {path}")
    return value


def expect_string(label: str, value: object) -> str:
    if not isinstance(value, str):
        raise CheckError(f"expected string for {label}")
    return value


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def expect_object_list(label: str, value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise CheckError(f"expected object list for {label}")
    return list(value)


def mapping_from_entries(
    entries: object,
    key_field: str,
    value_field: str,
    label: str,
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in expect_object_list(label, entries):
        key = entry.get(key_field)
        value = entry.get(value_field)
        if not isinstance(key, str) or not isinstance(value, str):
            raise CheckError(f"invalid entry in {label}")
        mapping[key] = value
    return mapping


def workflow_steps_from_entries(
    entries: object,
    label: str,
) -> list[tuple[str, str]]:
    steps: list[tuple[str, str]] = []
    for entry in expect_object_list(label, entries):
        name = entry.get("name")
        run = entry.get("run")
        if not isinstance(name, str) or not isinstance(run, str):
            raise CheckError(f"invalid entry in {label}")
        steps.append((name, run))
    return steps


def expect_exact_string(label: str, actual: object, expected: str) -> str:
    value = expect_string(label, actual)
    if value != expected:
        raise CheckError(f"{label} does not match the current-head Phase 11 packet")
    return value


def expect_exact_string_list(label: str, actual: object, expected: tuple[str, ...]) -> None:
    if expect_string_list(label, actual) != list(expected):
        raise CheckError(f"{label} does not match the current-head Phase 11 packet")


def require_text_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = normalize_whitespace(read_text(path))
    for marker in markers:
        if normalize_whitespace(marker) not in text:
            raise CheckError(f"missing marker in {path}: {marker}")


def build_route_markers_from_inventory(inventory: dict[str, object]) -> tuple[str, ...]:
    root_source_file = expect_exact_string(
        "proof_root_source_file",
        inventory.get("proof_root_source_file"),
        REQUIRED_PROOF_ROUTE["proof_root_source_file"],
    )
    test_artifact_name = expect_exact_string(
        "proof_test_artifact_name",
        inventory.get("proof_test_artifact_name"),
        REQUIRED_PROOF_ROUTE["proof_test_artifact_name"],
    )
    step_name = expect_exact_string(
        "proof_step_name",
        inventory.get("proof_step_name"),
        REQUIRED_PROOF_ROUTE["proof_step_name"],
    )
    step_description = expect_exact_string(
        "proof_step_description",
        inventory.get("proof_step_description"),
        REQUIRED_PROOF_ROUTE["proof_step_description"],
    )
    proof_build_file = expect_exact_string(
        "proof_build_file",
        inventory.get("proof_build_file"),
        REQUIRED_PROOF_ROUTE["proof_build_file"],
    )
    proof_replay_command = expect_exact_string(
        "proof_replay_command",
        inventory.get("proof_replay_command"),
        REQUIRED_PROOF_ROUTE["proof_replay_command"],
    )
    if proof_replay_command != f"zig build test --build-file {proof_build_file}":
        raise CheckError("proof_replay_command does not match proof_build_file")
    return (
        f'.root_source_file = b.path("{root_source_file}")',
        f'.name = "{test_artifact_name}"',
        f'const test_step = b.step("{step_name}", "{step_description}");',
    )


def run_check(root: Path) -> None:
    inventory = read_json(root / INVENTORY_PATH)
    build_text = read_text(root / BUILD_FILE_PATH)
    workflow_text = read_text(root / WORKFLOW_PATH)
    makefile_text = read_text(root / MAKEFILE_PATH)
    for marker in REQUIRED_BUILD_TEXT_MARKERS:
        if marker not in build_text:
            raise CheckError(f"missing marker in {BUILD_FILE_PATH}: {marker}")
    for marker in build_route_markers_from_inventory(inventory):
        if marker not in build_text:
            raise CheckError(f"missing marker in {BUILD_FILE_PATH}: {marker}")
    for marker in FORBIDDEN_BUILD_TEXT_MARKERS:
        if marker in build_text:
            raise CheckError(f"forbidden marker present in {BUILD_FILE_PATH}: {marker}")

    expect_exact_string_list(
        "build_test_names",
        inventory.get("build_test_names"),
        REQUIRED_BUILD_TEST_NAMES,
    )
    expect_exact_string_list(
        "shared_test_depend_steps",
        inventory.get("shared_test_depend_steps"),
        REQUIRED_SHARED_DEPEND_STEPS,
    )

    module_paths = mapping_from_entries(
        inventory.get("module_root_source_files"),
        "module",
        "path",
        "module_root_source_files",
    )
    if module_paths != REQUIRED_MODULE_PATHS:
        raise CheckError("module_root_source_files does not match the current-head HVC packet")

    test_root_modules = mapping_from_entries(
        inventory.get("test_root_modules"),
        "test",
        "root_module",
        "test_root_modules",
    )
    if test_root_modules != REQUIRED_TEST_ROOT_MODULES:
        raise CheckError("test_root_modules does not match the current-head HVC packet")

    expect_exact_string_list(
        "forbidden_markers",
        inventory.get("forbidden_markers"),
        FORBIDDEN_BUILD_TEXT_MARKERS,
    )
    expect_exact_string_list(
        "exact_current_checks",
        inventory.get("exact_current_checks"),
        EXACT_CURRENT_CHECKS,
    )
    workflow_steps = workflow_steps_from_entries(
        inventory.get("workflow_phase11_steps"),
        "workflow_phase11_steps",
    )
    if workflow_steps != list(REQUIRED_WORKFLOW_PHASE11_STEPS):
        raise CheckError("workflow_phase11_steps does not match the current-head Phase 11 packet")
    normalized_workflow_text = normalize_whitespace(workflow_text)
    for name, run in workflow_steps:
        if normalize_whitespace(f"- name: {name}") not in normalized_workflow_text:
            raise CheckError(f"missing workflow step in {WORKFLOW_PATH}: {name}")
        if normalize_whitespace(f"run: {run}") not in normalized_workflow_text:
            raise CheckError(f"missing workflow run in {WORKFLOW_PATH}: {run}")
    require_text_markers(root / MAKEFILE_PATH, REQUIRED_MAKEFILE_ROUTE_MARKERS)
    require_text_markers(root / HV_OPS_BUILD_PATH, REQUIRED_HV_OPS_BUILD_MARKERS)
    require_text_markers(root / EXPORT_BUILD_PATH, REQUIRED_EXPORT_BUILD_MARKERS)
    require_text_markers(root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_ROOT_MARKERS)
    expect_exact_string_list(
        "dedicated_survey_replays",
        inventory.get("dedicated_survey_replays"),
        REQUIRED_DEDICATED_SURVEY_REPLAYS,
    )
    expect_exact_string_list(
        "shared_split_replays",
        inventory.get("shared_split_replays"),
        (),
    )
    expect_exact_string_list(
        "shared_adjunct_replays",
        inventory.get("shared_adjunct_replays"),
        REQUIRED_SHARED_ADJUNCT_REPLAYS,
    )
    expect_exact_string_list(
        "shared_adjunct_build_replays",
        inventory.get("shared_adjunct_build_replays"),
        REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS,
    )

    replay_pairs = {
        (entry.get("path"), entry.get("marker"))
        for entry in expect_object_list(
            "shared_replay_markers",
            inventory.get("shared_replay_markers"),
        )
    }
    if replay_pairs != REQUIRED_REPLAY_MARKERS:
        raise CheckError("shared_replay_markers does not match the current-head Phase 11 packet")

    require_text_markers(root / HVC_VALIDATION_MATRIX_PATH, REQUIRED_HVC_VALIDATION_MATRIX_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_inventory() -> dict[str, object]:
    return {
        **REQUIRED_PROOF_ROUTE,
        "build_test_names": list(REQUIRED_BUILD_TEST_NAMES),
        "shared_test_depend_steps": list(REQUIRED_SHARED_DEPEND_STEPS),
        "module_root_source_files": [
            {"module": module, "path": path}
            for module, path in REQUIRED_MODULE_PATHS.items()
        ],
        "test_root_modules": [
            {"test": test_name, "root_module": module}
            for test_name, module in REQUIRED_TEST_ROOT_MODULES.items()
        ],
        "forbidden_markers": list(FORBIDDEN_BUILD_TEXT_MARKERS),
        "exact_current_checks": list(EXACT_CURRENT_CHECKS),
        "workflow_phase11_steps": [
            {"name": name, "run": run}
            for name, run in REQUIRED_WORKFLOW_PHASE11_STEPS
        ],
        "dedicated_survey_replays": list(REQUIRED_DEDICATED_SURVEY_REPLAYS),
        "shared_split_replays": [],
        "shared_adjunct_replays": list(REQUIRED_SHARED_ADJUNCT_REPLAYS),
        "shared_adjunct_build_replays": list(REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS),
        "shared_replay_markers": [],
    }


FIXTURE_BUILD_TEXT = """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const proof_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_cleanup_packet_proof.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const proof_tests = b.addTest(.{
        .name = \"phase11-hvc-cleanup-packet-proof\",
        .root_module = proof_module,
    });
    const run_proof_tests = b.addRunArtifact(proof_tests);

    const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC cleanup packet proof\");
    test_step.dependOn(&run_proof_tests.step);
}
"""


FIXTURE_HV_OPS_BUILD_TEXT = """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const hv_ops_proof_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_hv_ops_layout_proof.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const hv_ops_proof_tests = b.addTest(.{
        .name = \"phase11-hvc-hv-ops-layout-proof-tests\",
        .root_module = hv_ops_proof_module,
    });
    const run_hv_ops_proof_tests = b.addRunArtifact(hv_ops_proof_tests);

    const export_surface_proof_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const export_surface_proof_tests = b.addTest(.{
        .name = \"phase11-hvc-export-surface-layout-proof-tests\",
        .root_module = export_surface_proof_module,
    });
    const run_export_surface_proof_tests = b.addRunArtifact(export_surface_proof_tests);

    const test_step = b.step(\"test\", \"Run the focused Phase 11 exported-header proofs\");
    test_step.dependOn(&run_hv_ops_proof_tests.step);
    test_step.dependOn(&run_export_surface_proof_tests.step);
}
"""


FIXTURE_EXPORT_BUILD_TEXT = """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const proof_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_export_surface_layout_proof.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const proof_tests = b.addTest(.{
        .name = \"phase11-hvc-export-surface-layout-proof\",
        .root_module = proof_module,
    });
    const run_proof_tests = b.addRunArtifact(proof_tests);

    const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC exported-helper ABI proof\");
    test_step.dependOn(&run_proof_tests.step);
}
"""


FIXTURE_HVC_VALIDATION_MATRIX_TEXT = """# Phase 11 HVC Console Validation Matrix

- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- current-head HVC continuity packet rather than a whole-Phase-11 replay roster
"""

FIXTURE_SCRIPTS_README_TEXT = """# scripts/zigux

## Phase 11

- `scripts/zigux/check-phase11-build-inventory.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `make -C zigux phase11-validate`
"""

FIXTURE_WORKFLOW_TEXT = """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 11 build inventory checker
        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test
      - name: Check current Phase 11 build inventory packet
        run: python3 scripts/zigux/check-phase11-build-inventory.py
      - name: Self-test current Phase 11 HVC cleanup current-head checker
        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test
      - name: Check current Phase 11 HVC cleanup current-head packet
        run: python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py
      - name: Run current Phase 11 HVC hv_ops layout proof
        run: zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig
      - name: Run current Phase 11 HVC export surface layout proof
        run: zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig
      - name: Run current Phase 11 HVC cleanup packet proof
        run: zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig
      - name: Run current Phase 11 HVC targetless-unregister gap witness
        run: zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig
"""

FIXTURE_MAKEFILE_TEXT = """phase11-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig
\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig
"""


def build_fixture(root: Path) -> None:
    write(root / BUILD_FILE_PATH, FIXTURE_BUILD_TEXT)
    write(root / HV_OPS_BUILD_PATH, FIXTURE_HV_OPS_BUILD_TEXT)
    write(root / EXPORT_BUILD_PATH, FIXTURE_EXPORT_BUILD_TEXT)
    write(root / INVENTORY_PATH, json.dumps(fixture_inventory(), indent=2) + "\n")
    write(root / HVC_VALIDATION_MATRIX_PATH, FIXTURE_HVC_VALIDATION_MATRIX_TEXT)
    write(root / SCRIPTS_README_PATH, FIXTURE_SCRIPTS_README_TEXT)
    write(root / WORKFLOW_PATH, FIXTURE_WORKFLOW_TEXT)
    write(root / MAKEFILE_PATH, FIXTURE_MAKEFILE_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_build_inventory_current_head_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_build_marker = tmpdir / "missing_build_marker"
        shutil.copytree(fixture, missing_build_marker, dirs_exist_ok=True)
        write(
            missing_build_marker / BUILD_FILE_PATH,
            read_text(missing_build_marker / BUILD_FILE_PATH).replace(
                "phase11-hvc-cleanup-packet-proof",
                "",
                1,
            ),
        )
        expect_failure(missing_build_marker, "phase11-hvc-cleanup-packet-proof")
        case_count += 1

        missing_hv_ops_build_marker = tmpdir / "missing_hv_ops_build_marker"
        shutil.copytree(fixture, missing_hv_ops_build_marker, dirs_exist_ok=True)
        write(
            missing_hv_ops_build_marker / HV_OPS_BUILD_PATH,
            read_text(missing_hv_ops_build_marker / HV_OPS_BUILD_PATH).replace(
                "phase11-hvc-export-surface-layout-proof-tests",
                "",
                1,
            ),
        )
        expect_failure(missing_hv_ops_build_marker, "phase11-hvc-export-surface-layout-proof-tests")
        case_count += 1

        missing_export_build_marker = tmpdir / "missing_export_build_marker"
        shutil.copytree(fixture, missing_export_build_marker, dirs_exist_ok=True)
        write(
            missing_export_build_marker / EXPORT_BUILD_PATH,
            read_text(missing_export_build_marker / EXPORT_BUILD_PATH).replace(
                "phase11-hvc-export-surface-layout-proof",
                "",
                1,
            ),
        )
        expect_failure(missing_export_build_marker, "phase11-hvc-export-surface-layout-proof")
        case_count += 1

        wrong_proof_command = tmpdir / "wrong_proof_command"
        shutil.copytree(fixture, wrong_proof_command, dirs_exist_ok=True)
        inventory = read_json(wrong_proof_command / INVENTORY_PATH)
        inventory["proof_replay_command"] = "zig build test --build-file zigux/tests/phase11_build.zig"
        write(wrong_proof_command / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_proof_command, "proof_replay_command does not match")
        case_count += 1

        wrong_build_names = tmpdir / "wrong_build_names"
        shutil.copytree(fixture, wrong_build_names, dirs_exist_ok=True)
        inventory = read_json(wrong_build_names / INVENTORY_PATH)
        inventory["build_test_names"] = inventory["build_test_names"][:-1]
        write(wrong_build_names / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_build_names, "build_test_names does not match")
        case_count += 1

        wrong_exact_checks = tmpdir / "wrong_exact_checks"
        shutil.copytree(fixture, wrong_exact_checks, dirs_exist_ok=True)
        inventory = read_json(wrong_exact_checks / INVENTORY_PATH)
        inventory["exact_current_checks"] = inventory["exact_current_checks"][:-1]
        write(wrong_exact_checks / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_exact_checks, "exact_current_checks does not match")
        case_count += 1

        wrong_workflow_steps = tmpdir / "wrong_workflow_steps"
        shutil.copytree(fixture, wrong_workflow_steps, dirs_exist_ok=True)
        inventory = read_json(wrong_workflow_steps / INVENTORY_PATH)
        inventory["workflow_phase11_steps"] = inventory["workflow_phase11_steps"][:-1]
        write(wrong_workflow_steps / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_workflow_steps, "workflow_phase11_steps does not match")
        case_count += 1

        missing_workflow_step = tmpdir / "missing_workflow_step"
        shutil.copytree(fixture, missing_workflow_step, dirs_exist_ok=True)
        write(
            missing_workflow_step / WORKFLOW_PATH,
            read_text(missing_workflow_step / WORKFLOW_PATH).replace(
                "      - name: Run current Phase 11 HVC cleanup packet proof\n        run: zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig\n",
                "",
                1,
            ),
        )
        expect_failure(missing_workflow_step, "Run current Phase 11 HVC cleanup packet proof")
        case_count += 1

        missing_hv_ops_workflow_step = tmpdir / "missing_hv_ops_workflow_step"
        shutil.copytree(fixture, missing_hv_ops_workflow_step, dirs_exist_ok=True)
        write(
            missing_hv_ops_workflow_step / WORKFLOW_PATH,
            read_text(missing_hv_ops_workflow_step / WORKFLOW_PATH).replace(
                "      - name: Run current Phase 11 HVC hv_ops layout proof\n        run: zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig\n",
                "",
                1,
            ),
        )
        expect_failure(missing_hv_ops_workflow_step, "Run current Phase 11 HVC hv_ops layout proof")
        case_count += 1

        missing_targetless_workflow_step = tmpdir / "missing_targetless_workflow_step"
        shutil.copytree(fixture, missing_targetless_workflow_step, dirs_exist_ok=True)
        write(
            missing_targetless_workflow_step / WORKFLOW_PATH,
            read_text(missing_targetless_workflow_step / WORKFLOW_PATH).replace(
                "      - name: Run current Phase 11 HVC targetless-unregister gap witness\n        run: zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig\n",
                "",
                1,
            ),
        )
        expect_failure(missing_targetless_workflow_step, "Run current Phase 11 HVC targetless-unregister gap witness")
        case_count += 1

        missing_makefile_marker = tmpdir / "missing_makefile_marker"
        shutil.copytree(fixture, missing_makefile_marker, dirs_exist_ok=True)
        write(
            missing_makefile_marker / MAKEFILE_PATH,
            read_text(missing_makefile_marker / MAKEFILE_PATH).replace(
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig\n",
                "",
                1,
            ),
        )
        expect_failure(
            missing_makefile_marker,
            "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
        )
        case_count += 1

        missing_scripts_readme_marker = tmpdir / "missing_scripts_readme_marker"
        shutil.copytree(fixture, missing_scripts_readme_marker, dirs_exist_ok=True)
        write(
            missing_scripts_readme_marker / SCRIPTS_README_PATH,
            read_text(missing_scripts_readme_marker / SCRIPTS_README_PATH).replace(
                "- `make -C zigux phase11-validate`\n",
                "",
                1,
            ),
        )
        expect_failure(
            missing_scripts_readme_marker,
            "`make -C zigux phase11-validate`",
        )
        case_count += 1

        wrong_adjunct_replays = tmpdir / "wrong_adjunct_replays"
        shutil.copytree(fixture, wrong_adjunct_replays, dirs_exist_ok=True)
        inventory = read_json(wrong_adjunct_replays / INVENTORY_PATH)
        inventory["shared_adjunct_replays"] = inventory["shared_adjunct_replays"][:-1]
        write(wrong_adjunct_replays / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_adjunct_replays, "shared_adjunct_replays does not match")
        case_count += 1

        wrong_adjunct_build_replays = tmpdir / "wrong_adjunct_build_replays"
        shutil.copytree(fixture, wrong_adjunct_build_replays, dirs_exist_ok=True)
        inventory = read_json(wrong_adjunct_build_replays / INVENTORY_PATH)
        inventory["shared_adjunct_build_replays"] = inventory["shared_adjunct_build_replays"][:-1]
        write(
            wrong_adjunct_build_replays / INVENTORY_PATH,
            json.dumps(inventory, indent=2) + "\n",
        )
        expect_failure(
            wrong_adjunct_build_replays,
            "shared_adjunct_build_replays does not match",
        )
        case_count += 1

        wrong_replay_marker = tmpdir / "wrong_replay_marker"
        shutil.copytree(fixture, wrong_replay_marker, dirs_exist_ok=True)
        inventory = read_json(wrong_replay_marker / INVENTORY_PATH)
        inventory["shared_replay_markers"] = [{"path": "x", "marker": "y"}]
        write(wrong_replay_marker / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_replay_marker, "shared_replay_markers does not match")
        case_count += 1

        missing_matrix_marker = tmpdir / "missing_matrix_marker"
        shutil.copytree(fixture, missing_matrix_marker, dirs_exist_ok=True)
        write(
            missing_matrix_marker / HVC_VALIDATION_MATRIX_PATH,
            read_text(missing_matrix_marker / HVC_VALIDATION_MATRIX_PATH).replace(
                "- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`\n",
                "",
                1,
            ),
        )
        expect_failure(
            missing_matrix_marker,
            "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
        )
        case_count += 1

        print("PHASE11_BUILD_INVENTORY_SELF_TEST=pass")
        print(f"PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_BUILD_INVENTORY=fail: {exc}")
        return 1

    print("PHASE11_BUILD_INVENTORY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

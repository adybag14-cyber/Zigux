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

BUILD_FILE_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
DRIVER_LANE_SEQUENCING_PATH = Path("Documentation/zigux/phase11-driver-lane-sequencing.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

REQUIRED_DRIVER_LANE_MARKERS = (
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "must not recreate missing shared-contract or make-route claims from historical wording alone",
    "did not rematerialize `Documentation/zigux/phase11-shared-replay-contract.md`",
)

REQUIRED_SCRIPTS_ROOT_MARKERS = (
    "## Phase 11",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
)

REQUIRED_BUILD_TEXT_MARKERS = (
    "phase11_hvc_cleanup_packet_proof.zig",
    "phase11-hvc-cleanup-packet-proof",
    "Run the focused Phase 11 HVC cleanup packet proof",
)

FORBIDDEN_BUILD_TEXT_MARKERS = (
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
)

REQUIRED_BUILD_TEST_NAMES = (
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
)

REQUIRED_SHARED_DEPEND_STEPS = (
    "run_phase11_hvc_console_tests",
    "run_hvc_console_verify_tests",
    "run_phase11_hvc_cleanup_tests",
)

REQUIRED_MODULE_PATHS = {
    "hvc_console_module": "../../drivers/tty/hvc/hvc_console.zig",
    "hvc_console_verify_module": "../../drivers/tty/hvc/hvc_console_verify.zig",
    "phase11_hvc_console_module": "phase11_hvc_console.zig",
    "phase11_hvc_cleanup_module": "phase11_hvc_cleanup.zig",
    "phase11_hvc_console_survey_module": "phase11_hvc_console_survey.zig",
}

REQUIRED_TEST_ROOT_MODULES = {
    "phase11-hvc-console-tests": "phase11_hvc_console_module",
    "phase11-hvc-console-verify-tests": "hvc_console_verify_module",
    "phase11-hvc-cleanup-tests": "phase11_hvc_cleanup_module",
    "phase11-hvc-console-survey-tests": "phase11_hvc_console_survey_module",
}

REQUIRED_DEDICATED_SURVEY_REPLAYS = (
    "zigux/tests/phase11_hvc_console_survey.zig",
)

REQUIRED_SHARED_ADJUNCT_REPLAYS = (
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
)

REQUIRED_REPLAY_MARKERS = {
    (
        "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        " try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    ),
    (
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        " try std.testing.expect(dispatch.invokes_sysrq_handler);",
    ),
}


class CheckError(RuntimeError):
    pass


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


def expect_exact_string_list(label: str, actual: object, expected: tuple[str, ...]) -> None:
    if expect_string_list(label, actual) != list(expected):
        raise CheckError(f"{label} does not match the current-head Phase 11 packet")


def require_text_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path}: {marker}")


def run_check(root: Path) -> None:
    build_text = read_text(root / BUILD_FILE_PATH)
    for marker in REQUIRED_BUILD_TEXT_MARKERS:
        if marker not in build_text:
            raise CheckError(f"missing marker in {BUILD_FILE_PATH}: {marker}")
    for marker in FORBIDDEN_BUILD_TEXT_MARKERS:
        if marker in build_text:
            raise CheckError(f"forbidden marker present in {BUILD_FILE_PATH}: {marker}")

    inventory = read_json(root / INVENTORY_PATH)

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

    replay_pairs = {
        (entry.get("path"), entry.get("marker"))
        for entry in expect_object_list("shared_replay_markers", inventory.get("shared_replay_markers"))
    }
    if replay_pairs != REQUIRED_REPLAY_MARKERS:
        raise CheckError("shared_replay_markers does not match the current-head HVC packet")

    require_text_markers(root / DRIVER_LANE_SEQUENCING_PATH, REQUIRED_DRIVER_LANE_MARKERS)
    require_text_markers(root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_ROOT_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_inventory() -> dict[str, object]:
    return {
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
        "dedicated_survey_replays": list(REQUIRED_DEDICATED_SURVEY_REPLAYS),
        "shared_split_replays": [],
        "shared_adjunct_replays": list(REQUIRED_SHARED_ADJUNCT_REPLAYS),
        "shared_replay_markers": [
            {"path": path, "marker": marker}
            for path, marker in sorted(REQUIRED_REPLAY_MARKERS)
        ],
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


FIXTURE_DRIVER_LANE_TEXT = """# Phase 11 Driver Lane Sequencing

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- must not recreate missing shared-contract or make-route claims from historical wording alone
- did not rematerialize `Documentation/zigux/phase11-shared-replay-contract.md`
"""


FIXTURE_SCRIPTS_README_TEXT = """# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 11

- Phase 11 flow - the current scripts-root reminder packet stays reviewable through the shared build-inventory checker and fixture roster.
- `scripts/zigux/check-phase11-build-inventory.py` and `zigux/tests/fixtures/phase11_build_inventory.json` keep the shipped manifest-backed review surface explicit from the scripts root.
"""


def build_fixture(root: Path) -> None:
    write(root / BUILD_FILE_PATH, FIXTURE_BUILD_TEXT)
    write(root / INVENTORY_PATH, json.dumps(fixture_inventory(), indent=2) + "\n")
    write(root / DRIVER_LANE_SEQUENCING_PATH, FIXTURE_DRIVER_LANE_TEXT)
    write(root / SCRIPTS_README_PATH, FIXTURE_SCRIPTS_README_TEXT)


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
                "phase11_hvc_cleanup_packet_proof.zig",
                "",
                1,
            ),
        )
        expect_failure(missing_build_marker, "phase11_hvc_cleanup_packet_proof.zig")
        case_count += 1

        forbidden_marker_present = tmpdir / "forbidden_marker_present"
        shutil.copytree(fixture, forbidden_marker_present, dirs_exist_ok=True)
        write(
            forbidden_marker_present / BUILD_FILE_PATH,
            read_text(forbidden_marker_present / BUILD_FILE_PATH).replace(
                "test_step.dependOn(&run_proof_tests.step);",
                "test_step.dependOn(&run_proof_tests.step);\n    test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
                1,
            ),
        )
        expect_failure(
            forbidden_marker_present,
            "forbidden marker present in zigux/tests/phase11_hvc_cleanup_packet_build.zig",
        )
        case_count += 1

        wrong_build_names = tmpdir / "wrong_build_names"
        shutil.copytree(fixture, wrong_build_names, dirs_exist_ok=True)
        inventory = read_json(wrong_build_names / INVENTORY_PATH)
        inventory["build_test_names"].remove("phase11-hvc-cleanup-tests")
        write(wrong_build_names / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_build_names, "build_test_names does not match")
        case_count += 1

        wrong_adjunct_replays = tmpdir / "wrong_adjunct_replays"
        shutil.copytree(fixture, wrong_adjunct_replays, dirs_exist_ok=True)
        inventory = read_json(wrong_adjunct_replays / INVENTORY_PATH)
        inventory["shared_adjunct_replays"] = inventory["shared_adjunct_replays"][:-1]
        write(wrong_adjunct_replays / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_adjunct_replays, "shared_adjunct_replays does not match")
        case_count += 1

        wrong_replay_marker = tmpdir / "wrong_replay_marker"
        shutil.copytree(fixture, wrong_replay_marker, dirs_exist_ok=True)
        inventory = read_json(wrong_replay_marker / INVENTORY_PATH)
        inventory["shared_replay_markers"] = inventory["shared_replay_markers"][:-1]
        write(wrong_replay_marker / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_replay_marker, "shared_replay_markers does not match")
        case_count += 1

        missing_driver_marker = tmpdir / "missing_driver_marker"
        shutil.copytree(fixture, missing_driver_marker, dirs_exist_ok=True)
        write(
            missing_driver_marker / DRIVER_LANE_SEQUENCING_PATH,
            read_text(missing_driver_marker / DRIVER_LANE_SEQUENCING_PATH).replace(
                "- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`\n",
                "",
                1,
            ),
        )
        expect_failure(missing_driver_marker, "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`")
        case_count += 1

        missing_scripts_marker = tmpdir / "missing_scripts_marker"
        shutil.copytree(fixture, missing_scripts_marker, dirs_exist_ok=True)
        write(
            missing_scripts_marker / SCRIPTS_README_PATH,
            read_text(missing_scripts_marker / SCRIPTS_README_PATH).replace(
                "`zigux/tests/fixtures/phase11_build_inventory.json`",
                "",
                1,
            ),
        )
        expect_failure(missing_scripts_marker, "`zigux/tests/fixtures/phase11_build_inventory.json`")
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
#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare build packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[3] if len(SELF_PATH.parents) > 3 else Path.cwd()

BUILD_PATH = Path("zigux/tests/phase11_dw_wdt_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json")
REGISTRATION_SCAFFOLD_PATH = Path("zigux/tests/phase11_dw_wdt_registration_scaffold.zig")
LIVE_MMIO_REVIEW_PATH = Path("zigux/tests/phase11_dw_wdt_live_mmio_review.zig")
DIRECT_REPLAY_PATH = Path("zigux/tests/phase11_dw_wdt.zig")
PM_PATH = Path("drivers/watchdog/dw_wdt_pm.zig")
RESTART_PATH = Path("drivers/watchdog/dw_wdt_restart.zig")
VERIFY_PATH = Path("drivers/watchdog/dw_wdt_verify.zig")

REQUIRED_BUILD_TEXT_MARKERS = (
    '.root_source_file = b.path("../../drivers/watchdog/dw_wdt.zig")',
    '.root_source_file = b.path("../../drivers/watchdog/dw_wdt_pm.zig")',
    '.root_source_file = b.path("phase11_dw_wdt_registration_scaffold.zig")',
    '.root_source_file = b.path("phase11_dw_wdt_live_mmio_review.zig")',
    '.root_source_file = b.path("../../drivers/watchdog/dw_wdt_restart.zig")',
    '.root_source_file = b.path("../../drivers/watchdog/dw_wdt_verify.zig")',
    '.root_source_file = b.path("phase11_dw_wdt.zig")',
    'registration_scaffold_module.addImport("dw_wdt", dw_wdt_module);',
    'live_mmio_review_module.addImport("dw_wdt", dw_wdt_module);',
    'live_mmio_review_module.addImport("dw_wdt_pm", dw_wdt_pm_module);',
    'direct_replay_module.addImport("dw_wdt", dw_wdt_module);',
    'direct_replay_module.addImport("dw_wdt_pm", dw_wdt_pm_module);',
    'direct_replay_module.addImport("dw_wdt_restart", restart_module);',
    '.name = "phase11-dw-wdt-registration-scaffold-tests"',
    '.name = "phase11-dw-wdt-live-mmio-review-tests"',
    '.name = "phase11-dw-wdt-pm-tests"',
    '.name = "phase11-dw-wdt-restart-tests"',
    '.name = "phase11-dw-wdt-verify-tests"',
    '.name = "phase11-dw-wdt-direct-replay-tests"',
    '"Run the focused Phase 11 DesignWare watchdog scaffold, direct replay, and verify packet"',
    'test_step.dependOn(&run_registration_scaffold_tests.step);',
    'test_step.dependOn(&run_live_mmio_review_tests.step);',
    'test_step.dependOn(&run_pm_tests.step);',
    'test_step.dependOn(&run_restart_tests.step);',
    'test_step.dependOn(&run_verify_tests.step);',
    'test_step.dependOn(&run_direct_replay_tests.step);',
)

REQUIRED_BUILD_TEST_NAMES = (
    "phase11-dw-wdt-registration-scaffold-tests",
    "phase11-dw-wdt-live-mmio-review-tests",
    "phase11-dw-wdt-pm-tests",
    "phase11-dw-wdt-restart-tests",
    "phase11-dw-wdt-verify-tests",
    "phase11-dw-wdt-direct-replay-tests",
)

REQUIRED_MODULE_PATHS = {
    "dw_wdt_module": "../../drivers/watchdog/dw_wdt.zig",
    "dw_wdt_pm_module": "../../drivers/watchdog/dw_wdt_pm.zig",
    "registration_scaffold_module": "phase11_dw_wdt_registration_scaffold.zig",
    "live_mmio_review_module": "phase11_dw_wdt_live_mmio_review.zig",
    "restart_module": "../../drivers/watchdog/dw_wdt_restart.zig",
    "verify_module": "../../drivers/watchdog/dw_wdt_verify.zig",
    "direct_replay_module": "phase11_dw_wdt.zig",
}

REQUIRED_TEST_ROOT_MODULES = {
    "phase11-dw-wdt-registration-scaffold-tests": "registration_scaffold_module",
    "phase11-dw-wdt-live-mmio-review-tests": "live_mmio_review_module",
    "phase11-dw-wdt-pm-tests": "dw_wdt_pm_module",
    "phase11-dw-wdt-restart-tests": "restart_module",
    "phase11-dw-wdt-verify-tests": "verify_module",
    "phase11-dw-wdt-direct-replay-tests": "direct_replay_module",
}

EXACT_CURRENT_CHECKS = (
    "python3 scripts/zigux/check-phase11-dw-wdt-build-route.py --self-test",
    "python3 scripts/zigux/check-phase11-dw-wdt-build-route.py",
    "zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
)

REQUIRED_REGISTRATION_SCAFFOLD_MARKERS = (
    'test "platform registration scaffold summary keeps imported-running resetless registration explicit" {',
    'test "platform registration scaffold summary keeps ready reset-release branch explicit" {',
)

REQUIRED_LIVE_MMIO_REVIEW_MARKERS = (
    'test "phase11 dw_wdt keeps live mmio timeout barriers aligned across probe and resume" {',
    'test "phase11 dw_wdt keeps imported-running handoff free of fabricated live mmio blockers" {',
    'test "phase11 dw_wdt keeps remove-time live mmio stop boundaries explicit" {',
)

REQUIRED_DIRECT_REPLAY_MARKERS = (
    'test "phase11 dw_wdt direct replay keeps probe and PM timeout blockers aligned" {',
    'test "phase11 dw_wdt direct replay keeps imported-running registration and resume handoff aligned" {',
    'test "phase11 dw_wdt direct replay keeps restart and remove boundaries distinct" {',
)

REQUIRED_PM_MARKERS = (
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt pm suspend keeps missing drvdata explicit" {',
    'test "phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit" {',
)

REQUIRED_RESTART_MARKERS = (
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt restart summary keeps missing drvdata explicit" {',
    'test "phase11 dw_wdt restart summary keeps restart register writes explicit" {',
)

REQUIRED_VERIFY_MARKERS = (
    'test "dw_wdt verify keeps restart blockers and register-write readiness aligned" {',
    'test "dw_wdt verify keeps PM helper ordering and blocker branches explicit" {',
    'test "dw_wdt verify keeps PM scaffold dispositions aligned with the stronger helper packet" {',
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {path}")
    return payload


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


def mapping_from_entries(entries: object, key_field: str, value_field: str, label: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in expect_object_list(label, entries):
        key = entry.get(key_field)
        value = entry.get(value_field)
        if not isinstance(key, str) or not isinstance(value, str):
            raise CheckError(f"invalid entry in {label}")
        mapping[key] = value
    return mapping


def require_text_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path}: {marker}")


def run_check(root: Path) -> None:
    inventory = read_json(root / INVENTORY_PATH)
    build_text = read_text(root / BUILD_PATH)

    for marker in REQUIRED_BUILD_TEXT_MARKERS:
        if marker not in build_text:
            raise CheckError(f"missing marker in {BUILD_PATH}: {marker}")

    if expect_string("shared_build_file", inventory.get("shared_build_file")) != BUILD_PATH.as_posix():
        raise CheckError("shared_build_file does not match the current Phase 11 DesignWare packet")
    replay_command = expect_string("shared_replay_command", inventory.get("shared_replay_command"))
    if replay_command != f"zig build test --build-file {BUILD_PATH.as_posix()}":
        raise CheckError("shared_replay_command does not match shared_build_file")
    if expect_string("shared_step_name", inventory.get("shared_step_name")) != "test":
        raise CheckError("shared_step_name does not match the current Phase 11 DesignWare packet")
    if expect_string("shared_step_description", inventory.get("shared_step_description")) != "Run the focused Phase 11 DesignWare watchdog scaffold, direct replay, and verify packet":
        raise CheckError("shared_step_description does not match the current Phase 11 DesignWare packet")
    if expect_string_list("build_test_names", inventory.get("build_test_names")) != list(REQUIRED_BUILD_TEST_NAMES):
        raise CheckError("build_test_names does not match the current Phase 11 DesignWare packet")
    if expect_string_list("exact_current_checks", inventory.get("exact_current_checks")) != list(EXACT_CURRENT_CHECKS):
        raise CheckError("exact_current_checks does not match the current Phase 11 DesignWare packet")

    module_paths = mapping_from_entries(
        inventory.get("module_root_source_files"),
        "module",
        "path",
        "module_root_source_files",
    )
    if module_paths != REQUIRED_MODULE_PATHS:
        raise CheckError("module_root_source_files does not match the current Phase 11 DesignWare packet")

    test_root_modules = mapping_from_entries(
        inventory.get("test_root_modules"),
        "test",
        "root_module",
        "test_root_modules",
    )
    if test_root_modules != REQUIRED_TEST_ROOT_MODULES:
        raise CheckError("test_root_modules does not match the current Phase 11 DesignWare packet")

    require_text_markers(root / REGISTRATION_SCAFFOLD_PATH, REQUIRED_REGISTRATION_SCAFFOLD_MARKERS)
    require_text_markers(root / LIVE_MMIO_REVIEW_PATH, REQUIRED_LIVE_MMIO_REVIEW_MARKERS)
    require_text_markers(root / DIRECT_REPLAY_PATH, REQUIRED_DIRECT_REPLAY_MARKERS)
    require_text_markers(root / PM_PATH, REQUIRED_PM_MARKERS)
    require_text_markers(root / RESTART_PATH, REQUIRED_RESTART_MARKERS)
    require_text_markers(root / VERIFY_PATH, REQUIRED_VERIFY_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_inventory() -> dict[str, object]:
    return {
        "shared_build_file": BUILD_PATH.as_posix(),
        "shared_replay_command": f"zig build test --build-file {BUILD_PATH.as_posix()}",
        "shared_step_name": "test",
        "shared_step_description": "Run the focused Phase 11 DesignWare watchdog scaffold, direct replay, and verify packet",
        "build_test_names": list(REQUIRED_BUILD_TEST_NAMES),
        "module_root_source_files": [
            {"module": module, "path": path}
            for module, path in REQUIRED_MODULE_PATHS.items()
        ],
        "test_root_modules": [
            {"test": test_name, "root_module": module}
            for test_name, module in REQUIRED_TEST_ROOT_MODULES.items()
        ],
        "exact_current_checks": list(EXACT_CURRENT_CHECKS),
    }


FIXTURE_BUILD_TEXT = """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const dw_wdt_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/watchdog/dw_wdt.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const dw_wdt_pm_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_pm.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const registration_scaffold_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_dw_wdt_registration_scaffold.zig\"),
        .target = target,
        .optimize = optimize,
    });
    registration_scaffold_module.addImport(\"dw_wdt\", dw_wdt_module);
    const live_mmio_review_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_dw_wdt_live_mmio_review.zig\"),
        .target = target,
        .optimize = optimize,
    });
    live_mmio_review_module.addImport(\"dw_wdt\", dw_wdt_module);
    live_mmio_review_module.addImport(\"dw_wdt_pm\", dw_wdt_pm_module);
    const restart_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_restart.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const verify_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_verify.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const direct_replay_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_dw_wdt.zig\"),
        .target = target,
        .optimize = optimize,
    });
    direct_replay_module.addImport(\"dw_wdt\", dw_wdt_module);
    direct_replay_module.addImport(\"dw_wdt_pm\", dw_wdt_pm_module);
    direct_replay_module.addImport(\"dw_wdt_restart\", restart_module);

    const registration_scaffold_tests = b.addTest(.{ .name = \"phase11-dw-wdt-registration-scaffold-tests\", .root_module = registration_scaffold_module });
    const run_registration_scaffold_tests = b.addRunArtifact(registration_scaffold_tests);
    const live_mmio_review_tests = b.addTest(.{ .name = \"phase11-dw-wdt-live-mmio-review-tests\", .root_module = live_mmio_review_module });
    const run_live_mmio_review_tests = b.addRunArtifact(live_mmio_review_tests);
    const pm_tests = b.addTest(.{ .name = \"phase11-dw-wdt-pm-tests\", .root_module = dw_wdt_pm_module });
    const run_pm_tests = b.addRunArtifact(pm_tests);
    const restart_tests = b.addTest(.{ .name = \"phase11-dw-wdt-restart-tests\", .root_module = restart_module });
    const run_restart_tests = b.addRunArtifact(restart_tests);
    const verify_tests = b.addTest(.{ .name = \"phase11-dw-wdt-verify-tests\", .root_module = verify_module });
    const run_verify_tests = b.addRunArtifact(verify_tests);
    const direct_replay_tests = b.addTest(.{ .name = \"phase11-dw-wdt-direct-replay-tests\", .root_module = direct_replay_module });
    const run_direct_replay_tests = b.addRunArtifact(direct_replay_tests);

    const test_step = b.step(\"test\", \"Run the focused Phase 11 DesignWare watchdog scaffold, direct replay, and verify packet\");
    test_step.dependOn(&run_registration_scaffold_tests.step);
    test_step.dependOn(&run_live_mmio_review_tests.step);
    test_step.dependOn(&run_pm_tests.step);
    test_step.dependOn(&run_restart_tests.step);
    test_step.dependOn(&run_verify_tests.step);
    test_step.dependOn(&run_direct_replay_tests.step);
}
"""

FIXTURE_REGISTRATION_SCAFFOLD_TEXT = """
test \"platform registration scaffold summary keeps imported-running resetless registration explicit\" {
}
test \"platform registration scaffold summary keeps ready reset-release branch explicit\" {
}
"""

FIXTURE_LIVE_MMIO_REVIEW_TEXT = """
test \"phase11 dw_wdt keeps live mmio timeout barriers aligned across probe and resume\" {
}
test \"phase11 dw_wdt keeps imported-running handoff free of fabricated live mmio blockers\" {
}
test \"phase11 dw_wdt keeps remove-time live mmio stop boundaries explicit\" {
}
"""

FIXTURE_DIRECT_REPLAY_TEXT = """
test \"phase11 dw_wdt direct replay keeps probe and PM timeout blockers aligned\" {
}
test \"phase11 dw_wdt direct replay keeps imported-running registration and resume handoff aligned\" {
}
test \"phase11 dw_wdt direct replay keeps restart and remove boundaries distinct\" {
}
"""

FIXTURE_PM_TEXT = """
pub const anchor_path = \"drivers/watchdog/dw_wdt.c\";
test \"phase11 dw_wdt pm suspend keeps missing drvdata explicit\" {
}
test \"phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit\" {
}
"""

FIXTURE_RESTART_TEXT = """
pub const anchor_path = \"drivers/watchdog/dw_wdt.c\";
test \"phase11 dw_wdt restart summary keeps missing drvdata explicit\" {
}
test \"phase11 dw_wdt restart summary keeps restart register writes explicit\" {
}
"""

FIXTURE_VERIFY_TEXT = """
test \"dw_wdt verify keeps restart blockers and register-write readiness aligned\" {
}
test \"dw_wdt verify keeps PM helper ordering and blocker branches explicit\" {
}
test \"dw_wdt verify keeps PM scaffold dispositions aligned with the stronger helper packet\" {
}
"""


def build_fixture(root: Path) -> None:
    write(root / BUILD_PATH, FIXTURE_BUILD_TEXT)
    write(root / REGISTRATION_SCAFFOLD_PATH, FIXTURE_REGISTRATION_SCAFFOLD_TEXT)
    write(root / LIVE_MMIO_REVIEW_PATH, FIXTURE_LIVE_MMIO_REVIEW_TEXT)
    write(root / DIRECT_REPLAY_PATH, FIXTURE_DIRECT_REPLAY_TEXT)
    write(root / PM_PATH, FIXTURE_PM_TEXT)
    write(root / RESTART_PATH, FIXTURE_RESTART_TEXT)
    write(root / VERIFY_PATH, FIXTURE_VERIFY_TEXT)
    write(root / INVENTORY_PATH, json.dumps(fixture_inventory(), indent=2) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_build_route_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_live_mmio_marker = tmpdir / "missing_live_mmio_marker"
        shutil.copytree(fixture, missing_live_mmio_marker, dirs_exist_ok=True)
        write(
            missing_live_mmio_marker / BUILD_PATH,
            read_text(missing_live_mmio_marker / BUILD_PATH).replace(
                'phase11-dw-wdt-live-mmio-review-tests',
                '',
                1,
            ),
        )
        expect_failure(missing_live_mmio_marker, 'phase11-dw-wdt-live-mmio-review-tests')
        case_count += 1

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        inventory = read_json(wrong_inventory / INVENTORY_PATH)
        inventory["build_test_names"] = inventory["build_test_names"][:-1]
        write(wrong_inventory / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_inventory, 'build_test_names does not match')
        case_count += 1

        missing_direct_replay_marker = tmpdir / "missing_direct_replay_marker"
        shutil.copytree(fixture, missing_direct_replay_marker, dirs_exist_ok=True)
        write(
            missing_direct_replay_marker / DIRECT_REPLAY_PATH,
            read_text(missing_direct_replay_marker / DIRECT_REPLAY_PATH).replace(
                'test \"phase11 dw_wdt direct replay keeps restart and remove boundaries distinct\" {',
                '',
                1,
            ),
        )
        expect_failure(missing_direct_replay_marker, 'phase11 dw_wdt direct replay keeps restart and remove boundaries distinct')
        case_count += 1

        wrong_checks = tmpdir / "wrong_checks"
        shutil.copytree(fixture, wrong_checks, dirs_exist_ok=True)
        inventory = read_json(wrong_checks / INVENTORY_PATH)
        inventory["exact_current_checks"] = inventory["exact_current_checks"][:-1]
        write(wrong_checks / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_checks, 'exact_current_checks does not match')
        case_count += 1

        print("PHASE11_DW_WDT_BUILD_ROUTE_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_BUILD_ROUTE_SELF_TEST_CASE_COUNT={case_count}")
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
        print(f"PHASE11_DW_WDT_BUILD_ROUTE=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_BUILD_ROUTE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

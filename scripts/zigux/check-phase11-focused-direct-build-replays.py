#!/usr/bin/env python3
"""Fail-closed checker for Phase 11 focused direct build replays."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)

INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
MODEM_BUILD_PATH = Path("zigux/tests/phase11_hvc_modem_control_proof_build.zig")
TARGETLESS_BUILD_PATH = Path("zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")
VALIDATE_PHASE11_PATH = Path("scripts/zigux/validate-phase11.py")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS = (
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

REQUIRED_FOCUSED_DIRECT_BUILD_CHECKS = (
    "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test",
    "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py",
)

REQUIRED_VALIDATE_PHASE11_MARKERS = (
    '("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")',
)

REQUIRED_MAKEFILE_MARKERS = (
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

REQUIRED_MODEM_BUILD_MARKERS = (
    '.root_source_file = b.path("../../drivers/tty/hvc/hvc_console.zig")',
    '.root_source_file = b.path("phase11_hvc_modem_control_proof.zig")',
    'root_module.addImport("hvc_console", hvc_console_module);',
    '.name = "phase11-hvc-modem-control-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC modem-control proof.");',
)

REQUIRED_TARGETLESS_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_targetless_unregister_gap.zig")',
    '.name = "phase11-hvc-targetless-unregister-gap",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC targetless-unregister gap witness.");',
)


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


def require_text_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path}: {marker}")


def run_check(root: Path) -> None:
    inventory = read_json(root / INVENTORY_PATH)
    if expect_string_list(
        "focused_direct_build_replays",
        inventory.get("focused_direct_build_replays"),
    ) != list(REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS):
        raise CheckError(
            "focused_direct_build_replays does not match the current-head Phase 11 packet"
        )
    if expect_string_list(
        "focused_direct_build_checks",
        inventory.get("focused_direct_build_checks"),
    ) != list(REQUIRED_FOCUSED_DIRECT_BUILD_CHECKS):
        raise CheckError(
            "focused_direct_build_checks does not match the current-head Phase 11 packet"
        )
    require_text_markers(root / MODEM_BUILD_PATH, REQUIRED_MODEM_BUILD_MARKERS)
    require_text_markers(root / TARGETLESS_BUILD_PATH, REQUIRED_TARGETLESS_BUILD_MARKERS)
    require_text_markers(root / VALIDATE_PHASE11_PATH, REQUIRED_VALIDATE_PHASE11_MARKERS)
    require_text_markers(root / MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_inventory() -> dict[str, object]:
    return {
        "focused_direct_build_replays": list(REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS),
        "focused_direct_build_checks": list(REQUIRED_FOCUSED_DIRECT_BUILD_CHECKS),
    }


FIXTURE_MODEM_BUILD_TEXT = """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const hvc_console_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/tty/hvc/hvc_console.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_modem_control_proof.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("hvc_console", hvc_console_module);

    const unit_tests = b.addTest(.{
        .name = "phase11-hvc-modem-control-proof",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run the focused Phase 11 HVC modem-control proof.");
    test_step.dependOn(&run_unit_tests.step);
}
"""


FIXTURE_TARGETLESS_BUILD_TEXT = """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_targetless_unregister_gap.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase11-hvc-targetless-unregister-gap",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run the focused Phase 11 HVC targetless-unregister gap witness.");
    test_step.dependOn(&run_unit_tests.step);
}
"""

FIXTURE_VALIDATE_PHASE11_TEXT = """CHECKS = (
    ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py", "--self-test"),
    ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py"),
    ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig"),
    ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"),
)
"""

FIXTURE_MAKEFILE_TEXT = """phase11-validate:
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig
	cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig
"""


def build_fixture(root: Path) -> None:
    write(root / INVENTORY_PATH, json.dumps(fixture_inventory(), indent=2) + "\n")
    write(root / MODEM_BUILD_PATH, FIXTURE_MODEM_BUILD_TEXT)
    write(root / TARGETLESS_BUILD_PATH, FIXTURE_TARGETLESS_BUILD_TEXT)
    write(root / VALIDATE_PHASE11_PATH, FIXTURE_VALIDATE_PHASE11_TEXT)
    write(root / MAKEFILE_PATH, FIXTURE_MAKEFILE_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def remove_marker(root: Path, path: Path, marker: str) -> None:
    full_path = root / path
    write(full_path, read_text(full_path).replace(marker, "", 1))


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_focused_direct_build_replays_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        wrong_replays = tmpdir / "wrong_replays"
        shutil.copytree(fixture, wrong_replays, dirs_exist_ok=True)
        inventory = read_json(wrong_replays / INVENTORY_PATH)
        inventory["focused_direct_build_replays"] = inventory["focused_direct_build_replays"][:-1]
        write(wrong_replays / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_replays, "focused_direct_build_replays does not match")
        case_count += 1

        wrong_checks = tmpdir / "wrong_checks"
        shutil.copytree(fixture, wrong_checks, dirs_exist_ok=True)
        inventory = read_json(wrong_checks / INVENTORY_PATH)
        inventory["focused_direct_build_checks"] = inventory["focused_direct_build_checks"][:-1]
        write(wrong_checks / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_checks, "focused_direct_build_checks does not match")
        case_count += 1

        marker_cases = (
            (MODEM_BUILD_PATH, REQUIRED_MODEM_BUILD_MARKERS),
            (TARGETLESS_BUILD_PATH, REQUIRED_TARGETLESS_BUILD_MARKERS),
            (VALIDATE_PHASE11_PATH, REQUIRED_VALIDATE_PHASE11_MARKERS),
            (MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS),
        )
        for path, markers in marker_cases:
            for marker in markers:
                case_root = tmpdir / f"missing_{case_count}"
                shutil.copytree(fixture, case_root, dirs_exist_ok=True)
                remove_marker(case_root, path, marker)
                expect_failure(case_root, marker)
                case_count += 1

        print("PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS_SELF_TEST=pass")
        print(f"PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS_SELF_TEST_CASE_COUNT={case_count}")
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
        print(f"PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS=fail: {exc}")
        return 1

    print("PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

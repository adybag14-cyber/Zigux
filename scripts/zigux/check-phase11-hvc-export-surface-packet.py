#!/usr/bin/env python3
"""Fail-closed checker for the dedicated Phase 11 HVC export-surface proof packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

FILES = {
    "proof": "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "build": "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
}

PROOF_MARKERS = [
    'const layout_assert = @import("layout_assert");',
    "const WinsizeLayout = extern struct {",
    "const HvcStruct = opaque {};",
    "const HvOpsLayout = extern struct {",
    "const HvcExportSurface = extern struct {",
    'layout_assert.assertSize(HvcExportSurface, 72);',
    'layout_assert.assertAlign(HvcExportSurface, 8);',
    'layout_assert.assertOffset(HvcExportSurface, "hvc_instantiate", 0);',
    'layout_assert.assertOffset(HvcExportSurface, "hvc_alloc", 8);',
    'layout_assert.assertOffset(HvcExportSurface, "hvc_remove", 16);',
    'layout_assert.assertOffset(HvcExportSurface, "hvc_poll", 24);',
    'layout_assert.assertOffset(HvcExportSurface, "hvc_kick", 32);',
    'layout_assert.assertOffset(HvcExportSurface, "__hvc_resize", 40);',
    'layout_assert.assertOffset(HvcExportSurface, "notifier_add_irq", 48);',
    'layout_assert.assertOffset(HvcExportSurface, "notifier_del_irq", 56);',
    'layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
    'test "phase11 HVC exported helper proof keeps the exported helper surface layout explicit" {',
    'test "phase11 HVC exported helper proof keeps exported helper signatures exact" {',
    'assertExactType(@FieldType(HvcExportSurface, "hvc_instantiate"), HvcInstantiateFn);',
    'assertExactType(@FieldType(HvcExportSurface, "hvc_alloc"), HvcAllocFn);',
    'assertExactType(@FieldType(HvcExportSurface, "hvc_remove"), HvcRemoveFn);',
    'assertExactType(@FieldType(HvcExportSurface, "hvc_poll"), HvcPollFn);',
    'assertExactType(@FieldType(HvcExportSurface, "hvc_kick"), HvcKickFn);',
    'assertExactType(@FieldType(HvcExportSurface, "__hvc_resize"), HvcResizeFn);',
    'assertExactType(@FieldType(HvcExportSurface, "notifier_add_irq"), HvcNotifierAddIrqFn);',
    'assertExactType(@FieldType(HvcExportSurface, "notifier_del_irq"), HvcNotifierDelIrqFn);',
    'assertExactType(@FieldType(HvcExportSurface, "notifier_hangup_irq"), HvcNotifierHangupIrqFn);',
]

BUILD_MARKERS = [
    'const std = @import("std");',
    'const abi_bindings_module = b.createModule(.{',
    '.root_source_file = b.path("../bindings/abi.zig"),',
    'const layout_assert_module = b.createModule(.{',
    '.root_source_file = b.path("../helpers/layout_assert.zig"),',
    'layout_assert_module.addImport("abi_bindings", abi_bindings_module);',
    'const proof_module = b.createModule(.{',
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
    'proof_module.addImport("layout_assert", layout_assert_module);',
    '.name = "phase11-hvc-export-surface-layout-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
    "test_step.dependOn(&run_proof_tests.step);",
]

FORBIDDEN_BUILD_MARKERS = [
    'proof_module.addImport("abi_bindings", abi_bindings_module);',
    'b.path("phase11_build.zig")',
]


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_absent(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    proof_text = read_text(root, FILES["proof"])
    build_text = read_text(root, FILES["build"])

    expect_markers("proof", proof_text, PROOF_MARKERS)
    expect_markers("build", build_text, BUILD_MARKERS)
    expect_absent("build", build_text, FORBIDDEN_BUILD_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / FILES["proof"],
        "\n".join(PROOF_MARKERS) + "\n",
    )
    write(
        root / FILES["build"],
        "\n".join(BUILD_MARKERS) + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_export_surface_packet_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        text_cases = [
            ("missing_proof_marker", "proof", PROOF_MARKERS[5]),
            ("missing_build_marker", "build", BUILD_MARKERS[7]),
        ]
        for case_name, label, marker in text_cases:
            root = tmpdir / case_name
            shutil.copytree(fixture, root, dirs_exist_ok=True)
            path = root / FILES[label]
            write(path, path.read_text(encoding="utf-8").replace(marker, "", 1))
            expect_failure(root, marker)

        forbidden_case = tmpdir / "forbidden_build_marker"
        shutil.copytree(fixture, forbidden_case, dirs_exist_ok=True)
        path = forbidden_case / FILES["build"]
        write(path, path.read_text(encoding="utf-8") + FORBIDDEN_BUILD_MARKERS[0] + "\n")
        expect_failure(forbidden_case, FORBIDDEN_BUILD_MARKERS[0])

        missing_case = tmpdir / "missing_build_file"
        shutil.copytree(fixture, missing_case, dirs_exist_ok=True)
        (missing_case / FILES["build"]).unlink()
        expect_failure(missing_case, FILES["build"])

        print("PHASE11_HVC_EXPORT_SURFACE_PACKET_SELF_TEST=pass")
        print("PHASE11_HVC_EXPORT_SURFACE_PACKET_SELF_TEST_CASE_COUNT=4")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_HVC_EXPORT_SURFACE_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_EXPORT_SURFACE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

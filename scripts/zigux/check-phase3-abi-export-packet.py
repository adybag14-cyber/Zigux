#!/usr/bin/env python3
"""Fail-close the current shared Phase 3 ABI-plus-export packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase3.py")
BUILD_PATH = Path("zigux/tests/build.zig")
ABI_REPLAY_PATH = Path("zigux/tests/phase3_abi.zig")
EXPORT_LAYOUT_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
EXPORT_LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
EXPORT_SHIM_BUILD_PATH = Path("zigux/tests/phase3_export_shim_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_PATHS = (
    SURVEY_PATH,
    VALIDATOR_PATH,
    BUILD_PATH,
    ABI_REPLAY_PATH,
    EXPORT_LAYOUT_PATH,
    EXPORT_LAYOUT_BUILD_PATH,
    EXPORT_SHIM_BUILD_PATH,
    MAKEFILE_PATH,
    MANIFEST_PATH,
)

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_EXPORT_UAPI_VALIDATOR_PATH=scripts/zigux/validate-phase3-export-uapi-survey.py",
    "PHASE3_SHARED_VALIDATE_MAKE_ROUTE=make -C zigux phase3-validate",
    "PHASE3_SHARED_PHASE_MAKE_ROUTE=make -C zigux phase3",
    "PHASE3_EXPORT_SHIM_BUILD_PATH=zigux/tests/phase3_export_shim_build.zig",
    "PHASE3_EXPORT_SHIM_DEDICATED_GATE=zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "PHASE3_EXPORT_SHIM_DEDICATED_MAKE_ROUTE=make -C zigux phase3-export-shim-test",
    "PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig",
    "PHASE3_LAYOUT_SHARED_GATE=zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "PHASE3_LAYOUT_BUILD_PATH=zigux/tests/phase3_export_uapi_layout_build.zig",
    "PHASE3_LAYOUT_DEDICATED_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "PHASE3_LAYOUT_MAKE_ROUTE=make -C zigux phase3-export-uapi-layout",
    "PHASE3_LAYOUT_DEDICATED_MAKE_ROUTE=make -C zigux phase3-export-uapi-layout-test",
    "PHASE3_C_HEADER_SMOKE_CHECK=scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "PHASE3_EXPORT_UAPI_CATALOG_HELPER=scripts/zigux/phase3_catalog.py",
    "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts/zigux/check-phase3-catalog-selftest.py",
    "There is no remaining packet-local missing companion, missing focused export-shim replay handoff, missing dedicated layout-build handoff, or missing aggregate replay entrypoint left to close inside this survey.",
)

REQUIRED_VALIDATOR_MARKERS = (
    'TESTS_BUILD_PATH = Path("zigux/tests/build.zig")',
    'ABI_TEST_PATH = Path("zigux/tests/phase3_abi.zig")',
    'EXPORT_UAPI_LAYOUT_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")',
    'EXPORT_UAPI_LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")',
    'EXPORT_SHIM_BUILD_PATH = Path("zigux/tests/phase3_export_shim_build.zig")',
    '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
    '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
    '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
    '"make -C zigux phase3-export-shim-test"',
    '"make -C zigux phase3-export-uapi-layout"',
    '"make -C zigux phase3-export-uapi-layout-test"',
)

REQUIRED_BUILD_MARKERS = (
    "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
    'root_source_file = b.path("phase3_abi.zig"),',
    'root_source_file = b.path("phase3_export_uapi_layout.zig"),',
    'root_module.addImport("header_family_binding", header_family_binding);',
    'root_module.addImport("export_shim", export_shim);',
    '"phase3-abi-export"',
    "phase3_abi_export_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_abi_export_step.dependOn(&phase3_export_uapi_layout.step);",
)

REQUIRED_ABI_REPLAY_MARKERS = (
    'test "phase3 abi keeps shared layout assertions wired into the replay" {',
    'test "phase3 abi keeps export shim compatibility and status helpers reviewable" {',
    'test "phase3 abi keeps version and dev_t relays explicit" {',
    'test "phase3 abi keeps export-shim version validation and dev_t roundtrip relays explicit" {',
    'test "phase3 abi keeps Linux-facing header-family relays aligned with the shared ABI helpers" {',
)

REQUIRED_EXPORT_LAYOUT_MARKERS = (
    'test "export and uapi dev_t layouts stay aligned" {',
    'test "export and uapi version layouts stay aligned" {',
    'test "header-family binding keeps the bounded relay surface explicit" {',
    'test "export shim relays version compatibility without widening the boundary" {',
    'test "export shim relays starter boundary-header validation through the focused replay" {',
)

REQUIRED_EXPORT_LAYOUT_BUILD_MARKERS = (
    '.root_source_file = b.path("../uapi/dev_t.zig"),',
    '.root_source_file = b.path("../uapi/version.zig"),',
    '.root_source_file = b.path("../kernel/export_shim.zig"),',
    '.root_source_file = b.path("../bindings/header_family.zig"),',
    '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
    'root_module.addImport("header_family_binding", header_family_binding);',
    'root_module.addImport("export_shim", export_shim);',
    '"phase3-export-uapi-layout-test",',
)

REQUIRED_EXPORT_SHIM_BUILD_MARKERS = (
    '.root_source_file = b.path("../bindings/abi.zig"),',
    '.root_source_file = b.path("../uapi/dev_t.zig"),',
    '.root_source_file = b.path("../uapi/version.zig"),',
    '.root_source_file = b.path("../bindings/dev_t.zig"),',
    '.root_source_file = b.path("../bindings/version.zig"),',
    '.root_source_file = b.path("../kernel/export_shim.zig"),',
    'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
    'export_shim_module.addImport("dev_t_binding", dev_t_binding_module);',
    'export_shim_module.addImport("version_binding", version_binding_module);',
    '.name = "phase3-export-shim-test",',
    '"Run the focused Phase 3 export shim replay"',
)

REQUIRED_MAKEFILE_LINES = (
    "phase3-validate:",
    "phase3-export-uapi-layout:",
    "phase3-export-uapi-layout-test:",
    "phase3-export-shim-test:",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
)

REQUIRED_MANIFEST_PACKET_FILES = (
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/Makefile",
)

REQUIRED_MANIFEST_REPLAY_ROUTES = (
    "python3 scripts/zigux/validate-phase3.py --self-test",
    "python3 scripts/zigux/validate-phase3.py",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-validate",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "make -C zigux phase3-export-shim-test",
    "make -C zigux phase3",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _check_markers(root: Path, rel_path: Path, markers: tuple[str, ...], issues: list[str]) -> None:
    try:
        text = _read(root / rel_path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {rel_path.as_posix()}")
        return
    for marker in markers:
        if marker not in text:
            issues.append(f"missing {rel_path.as_posix()} marker: {marker}")


def _check_exact_lines(root: Path, rel_path: Path, lines: tuple[str, ...], issues: list[str]) -> None:
    try:
        present = _read(root / rel_path).splitlines()
    except FileNotFoundError:
        issues.append(f"missing repo file: {rel_path.as_posix()}")
        return
    for line in lines:
        if line not in present:
            issues.append(f"missing {rel_path.as_posix()} marker: {line}")


def validate_repo(root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_PATHS:
        if not (root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    _check_markers(root, SURVEY_PATH, REQUIRED_SURVEY_MARKERS, issues)
    _check_markers(root, VALIDATOR_PATH, REQUIRED_VALIDATOR_MARKERS, issues)
    _check_markers(root, BUILD_PATH, REQUIRED_BUILD_MARKERS, issues)
    _check_markers(root, ABI_REPLAY_PATH, REQUIRED_ABI_REPLAY_MARKERS, issues)
    _check_markers(root, EXPORT_LAYOUT_PATH, REQUIRED_EXPORT_LAYOUT_MARKERS, issues)
    _check_markers(root, EXPORT_LAYOUT_BUILD_PATH, REQUIRED_EXPORT_LAYOUT_BUILD_MARKERS, issues)
    _check_markers(root, EXPORT_SHIM_BUILD_PATH, REQUIRED_EXPORT_SHIM_BUILD_MARKERS, issues)
    _check_exact_lines(root, MAKEFILE_PATH, REQUIRED_MAKEFILE_LINES, issues)

    manifest_path = root / MANIFEST_PATH
    try:
        manifest = json.loads(_read(manifest_path))
    except FileNotFoundError:
        return issues
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        for entry in REQUIRED_MANIFEST_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {entry}")
    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        for entry in REQUIRED_MANIFEST_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(f"phase3_abi_manifest.json missing replay route: {entry}")

    return issues


def _sample_manifest() -> str:
    payload = {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "status": "shared_abi_and_header_family_binding_surface_present",
        "scope": "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
        "packet_files": list(REQUIRED_MANIFEST_PACKET_FILES),
        "replay_routes": list(REQUIRED_MANIFEST_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
    }
    return json.dumps(payload, indent=2) + "\n"


def write_sample_root(root: Path) -> None:
    _write(root / SURVEY_PATH, "\n".join(REQUIRED_SURVEY_MARKERS) + "\n")
    _write(root / VALIDATOR_PATH, "\n".join(REQUIRED_VALIDATOR_MARKERS) + "\n")
    _write(root / BUILD_PATH, "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
    _write(root / ABI_REPLAY_PATH, "\n".join(REQUIRED_ABI_REPLAY_MARKERS) + "\n")
    _write(root / EXPORT_LAYOUT_PATH, "\n".join(REQUIRED_EXPORT_LAYOUT_MARKERS) + "\n")
    _write(root / EXPORT_LAYOUT_BUILD_PATH, "\n".join(REQUIRED_EXPORT_LAYOUT_BUILD_MARKERS) + "\n")
    _write(root / EXPORT_SHIM_BUILD_PATH, "\n".join(REQUIRED_EXPORT_SHIM_BUILD_MARKERS) + "\n")
    _write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    _write(root / MANIFEST_PATH, _sample_manifest())


def _remove_once(path: Path, marker: str) -> None:
    path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")


def run_self_test() -> int:
    cases = (
        (SURVEY_PATH, REQUIRED_SURVEY_MARKERS[0], f"missing {SURVEY_PATH.as_posix()} marker: {REQUIRED_SURVEY_MARKERS[0]}"),
        (SURVEY_PATH, REQUIRED_SURVEY_MARKERS[-1], f"missing {SURVEY_PATH.as_posix()} marker: {REQUIRED_SURVEY_MARKERS[-1]}"),
        (VALIDATOR_PATH, REQUIRED_VALIDATOR_MARKERS[-1], f"missing {VALIDATOR_PATH.as_posix()} marker: {REQUIRED_VALIDATOR_MARKERS[-1]}"),
        (BUILD_PATH, REQUIRED_BUILD_MARKERS[-1], f"missing {BUILD_PATH.as_posix()} marker: {REQUIRED_BUILD_MARKERS[-1]}"),
        (ABI_REPLAY_PATH, REQUIRED_ABI_REPLAY_MARKERS[0], f"missing {ABI_REPLAY_PATH.as_posix()} marker: {REQUIRED_ABI_REPLAY_MARKERS[0]}"),
        (EXPORT_LAYOUT_PATH, REQUIRED_EXPORT_LAYOUT_MARKERS[-1], f"missing {EXPORT_LAYOUT_PATH.as_posix()} marker: {REQUIRED_EXPORT_LAYOUT_MARKERS[-1]}"),
        (
            EXPORT_LAYOUT_BUILD_PATH,
            REQUIRED_EXPORT_LAYOUT_BUILD_MARKERS[-1],
            f"missing {EXPORT_LAYOUT_BUILD_PATH.as_posix()} marker: {REQUIRED_EXPORT_LAYOUT_BUILD_MARKERS[-1]}",
        ),
        (
            EXPORT_SHIM_BUILD_PATH,
            REQUIRED_EXPORT_SHIM_BUILD_MARKERS[-1],
            f"missing {EXPORT_SHIM_BUILD_PATH.as_posix()} marker: {REQUIRED_EXPORT_SHIM_BUILD_MARKERS[-1]}",
        ),
        (MAKEFILE_PATH, REQUIRED_MAKEFILE_LINES[-1], f"missing {MAKEFILE_PATH.as_posix()} marker: {REQUIRED_MAKEFILE_LINES[-1]}"),
        (
            MANIFEST_PATH,
            REQUIRED_MANIFEST_PACKET_FILES[-1],
            f"phase3_abi_manifest.json missing packet_files entry: {REQUIRED_MANIFEST_PACKET_FILES[-1]}",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_export_packet_") as temp_dir:
        root = Path(temp_dir)
        write_sample_root(root)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_EXPORT_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for rel_path, marker, expected in cases:
            write_sample_root(root)
            _remove_once(root / rel_path, marker)
            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE3_ABI_EXPORT_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_ABI_EXPORT_PACKET_SELF_TEST=pass")
    print(f"PHASE3_ABI_EXPORT_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the current shared Phase 3 ABI-plus-export packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like packet fixture rooted at the given path",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"wrote sample root to {args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.root)
    if issues:
        print("PHASE3_ABI_EXPORT_PACKET=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_ABI_EXPORT_PACKET=pass")
    print(f"PHASE3_ABI_EXPORT_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print("PHASE3_ABI_EXPORT_PACKET_SCOPE=shared_phase3_abi_plus_export_replay_surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

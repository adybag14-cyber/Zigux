#!/usr/bin/env python3
"""Fail-close the current Phase 3 dev_t starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
UAPI_DEV_T_PATH = Path("zigux/uapi/dev_t.zig")
UAPI_VERSION_PATH = Path("zigux/uapi/version.zig")
BINDING_PATH = Path("zigux/bindings/dev_t.zig")
TEST_PATH = Path("zigux/tests/phase3_dev_t_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_dev_t_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_dev_t_starter_packet_manifest.json")

REQUIRED_MARKERS = {
    ABI_SLICE_PATH: (
        "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
        "scripts/zigux/check-phase3-dev-t-starter-packet.py",
        "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
        "`zigux/tests/README.md` is still the next shared reminder surface to narrow so it matches this note and `Documentation/zigux/phase3-validator-support-surface.md` without implying the broader Phase 3 packet has already returned",
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "zigux/kernel/export_shim.zig",
    ),
    VALIDATOR_NOTE_PATH: (
        "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
        "scripts/zigux/check-phase3-dev-t-starter-packet.py",
        "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
        "the new manifest-backed starter packet",
    ),
    LINUX_HEADER_PATH: (
        "#define ZIGUX_UAPI_ABI_MAJOR 0u",
        "#define ZIGUX_UAPI_ABI_MINOR 1u",
        "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
        "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
        "struct zigux_uapi_version {",
        "static inline struct zigux_uapi_version zigux_uapi_version_current(void) {",
    ),
    DEV_T_HEADER_PATH: (
        "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
        "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
        "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
        "struct zigux_dev_t_fields {",
        "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
    ),
    UAPI_DEV_T_PATH: (
        "pub const abi_version: u32 = 1;",
        "pub const Fields = extern struct {",
        "pub fn init(major: u32, minor: u32) Fields {",
        "std.debug.assert(@sizeOf(Fields) == 8);",
        "std.debug.assert(@alignOf(Fields) == 4);",
    ),
    UAPI_VERSION_PATH: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const header_family_revision: u32 = 1;",
        "pub const Version = extern struct {",
        "pub fn current() Version {",
        "std.debug.assert(@sizeOf(Version) == 12);",
        "std.debug.assert(@alignOf(Version) == 4);",
    ),
    BINDING_PATH: (
        "pub const abi_version = uapi.abi_version;",
        "pub const fields_size: usize = @sizeOf(uapi.Fields);",
        "pub const fields_align: usize = @alignOf(uapi.Fields);",
        'pub const major_offset: usize = @offsetOf(uapi.Fields, "major");',
        'pub const minor_offset: usize = @offsetOf(uapi.Fields, "minor");',
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn eql(left: Fields, right: Fields) bool {",
        "std.debug.assert(major_offset == 0);",
        "std.debug.assert(minor_offset == 4);",
    ),
    TEST_PATH: (
        'test "dev_t starter binding preserves the current ABI layout" {',
        'test "starter packet version stays aligned with the Linux-facing header family" {',
        'test "dev_t binding equality stays field based" {',
        "try testing.expectEqual(@as(u32, 1), dev_t.abi_version);",
        "try testing.expectEqual(@as(u32, 1), version.header_family_revision);",
        "try testing.expect(dev_t.eql(left, same));",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../bindings/dev_t.zig"),',
        '.root_source_file = b.path("phase3_dev_t_starter_packet.zig"),',
        'dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);',
        'root_module.addImport("dev_t_binding", dev_t_binding);',
        '"phase3-dev-t-starter-packet-test"',
        '"Run the Phase 3 dev_t starter-packet ABI self-check"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-dev-t-starter-packet"',
        '"status": "starter_packet_present"',
        '"Documentation/zigux/phase3-abi-slice.md"',
        '"Documentation/zigux/phase3-validator-support-surface.md"',
        '"zigux/tests/phase3_dev_t_starter_packet_manifest.json"',
        '"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-dev-t-starter-packet.py"',
        '"next_safe_step": "keep the live starter packet honest with bounded manifest-backed validator work before widening the broader Phase 3 ABI substrate"',
    ),
}

SAMPLE_FILES = {
    ABI_SLICE_PATH: """# Phase 3 ABI Slice

zigux/tests/phase3_dev_t_starter_packet_manifest.json
scripts/zigux/check-phase3-dev-t-starter-packet.py
python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test
python3 scripts/zigux/check-phase3-dev-t-starter-packet.py
`zigux/tests/README.md` is still the next shared reminder surface to narrow so it matches this note and `Documentation/zigux/phase3-validator-support-surface.md` without implying the broader Phase 3 packet has already returned
scripts/zigux/validate-phase3-export-uapi-survey.py
zigux/kernel/export_shim.zig
""",
    VALIDATOR_NOTE_PATH: """# Phase 3 Validator Support Surface

zigux/tests/phase3_dev_t_starter_packet_manifest.json
scripts/zigux/check-phase3-dev-t-starter-packet.py
python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test
python3 scripts/zigux/check-phase3-dev-t-starter-packet.py
the new manifest-backed starter packet
""",
    LINUX_HEADER_PATH: "\n".join(REQUIRED_MARKERS[LINUX_HEADER_PATH]) + "\n",
    DEV_T_HEADER_PATH: "\n".join(REQUIRED_MARKERS[DEV_T_HEADER_PATH]) + "\n",
    UAPI_DEV_T_PATH: "\n".join(REQUIRED_MARKERS[UAPI_DEV_T_PATH]) + "\n",
    UAPI_VERSION_PATH: "\n".join(REQUIRED_MARKERS[UAPI_VERSION_PATH]) + "\n",
    BINDING_PATH: "\n".join(REQUIRED_MARKERS[BINDING_PATH]) + "\n",
    TEST_PATH: "\n".join(REQUIRED_MARKERS[TEST_PATH]) + "\n",
    BUILD_PATH: "\n".join(REQUIRED_MARKERS[BUILD_PATH]) + "\n",
    MANIFEST_PATH: """{
  "slug": "phase3-dev-t-starter-packet",
  "status": "starter_packet_present",
  "packet_files": [
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-dev-t-starter-packet.py"
  ],
  "replay_routes": [
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py"
  ],
  "next_safe_step": "keep the live starter packet honest with bounded manifest-backed validator work before widening the broader Phase 3 ABI substrate"
}
""",
}

SELF_TEST_CASES = (
    (ABI_SLICE_PATH, "zigux/tests/phase3_dev_t_starter_packet_manifest.json"),
    (VALIDATOR_NOTE_PATH, "the new manifest-backed starter packet"),
    (LINUX_HEADER_PATH, "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u"),
    (DEV_T_HEADER_PATH, "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u"),
    (UAPI_DEV_T_PATH, "std.debug.assert(@sizeOf(Fields) == 8);"),
    (UAPI_VERSION_PATH, "pub const header_family_revision: u32 = 1;"),
    (BINDING_PATH, 'pub const major_offset: usize = @offsetOf(uapi.Fields, "major");'),
    (TEST_PATH, 'test "starter packet version stays aligned with the Linux-facing header family" {'),
    (BUILD_PATH, '"phase3-dev-t-starter-packet-test"'),
    (MANIFEST_PATH, '"status": "starter_packet_present"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            if not isinstance(packet_files, list):
                issues.append("phase3_dev_t_starter_packet_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_dev_t_starter_packet_manifest.json replay_routes is not a list")
            if isinstance(packet_files, list):
                for required_path in (
                    "Documentation/zigux/phase3-abi-slice.md",
                    "Documentation/zigux/phase3-validator-support-surface.md",
                    "include/linux/zigux.h",
                    "include/zigux/dev_t.h",
                    "zigux/uapi/version.zig",
                    "zigux/uapi/dev_t.zig",
                    "zigux/bindings/dev_t.zig",
                    "zigux/tests/phase3_dev_t_starter_packet.zig",
                    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
                    "zigux/tests/phase3_dev_t_starter_packet_manifest.json",
                    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
                ):
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_dev_t_starter_packet_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in (
                    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test",
                    "python3 scripts/zigux/check-phase3-dev-t-starter-packet.py",
                ):
                    if route not in replay_routes:
                        issues.append(
                            "phase3_dev_t_starter_packet_manifest.json missing replay route: "
                            f"{route}"
                        )
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_dev_t_starter_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_DEV_T_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_DEV_T_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 dev_t starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 dev_t starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_DEV_T_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
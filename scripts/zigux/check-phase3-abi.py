#!/usr/bin/env python3
"""Fail-close the current bounded Phase 3 shared ABI packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ABI_SLICE_NOTE = Path("Documentation/zigux/phase3-abi-slice.md")
ABI_HEADER = Path("include/zigux/abi.h")
LINUX_ZIGUX_HEADER = Path("include/linux/zigux.h")
DEV_T_HEADER = Path("include/zigux/dev_t.h")
UAPI_DEV_T = Path("zigux/uapi/dev_t.zig")
UAPI_VERSION = Path("zigux/uapi/version.zig")
BINDING_ABI = Path("zigux/bindings/abi.zig")
BINDING_DEV_T = Path("zigux/bindings/dev_t.zig")
BINDING_VERSION = Path("zigux/bindings/version.zig")
BINDING_NOTIFIER = Path("zigux/bindings/notifier_abi.zig")
EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")
PHASE3_CATALOG = Path("scripts/zigux/phase3_catalog.py")
EXPORT_UAPI_SURVEY_VALIDATOR = Path("scripts/zigux/validate-phase3-export-uapi-survey.py")
ABI_TEST = Path("zigux/tests/phase3_abi.zig")
TESTS_BUILD = Path("zigux/tests/build.zig")
ABI_DUMP = Path("zigux/tests/phase3_abi_dump_current.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_MARKERS = {
    ABI_SLICE_NOTE: (
        "PHASE3_CURRENT_INTEROP_GAP=",
        "PHASE3_CURRENT_INTEROP_GAP_DETAIL=",
        "include/linux/zigux.h",
        "include/zigux/dev_t.h",
        "include/zigux/abi.h",
        "zigux/uapi/dev_t.zig",
        "zigux/uapi/version.zig",
        "zigux/bindings/dev_t.zig",
        "zigux/bindings/version.zig",
        "zigux/bindings/abi.zig",
        "zigux/bindings/notifier_abi.zig",
        "zigux/kernel/export_shim.zig",
        "scripts/zigux/check-phase3-abi.py",
        "scripts/zigux/validate-phase3.py",
        "scripts/zigux/phase3_catalog.py",
        "scripts/zigux/validate-phase3-export-uapi-survey.py",
        "zigux/tests/phase3_abi.zig",
        "zigux/tests/build.zig",
        "zigux/tests/phase3_abi_dump_current.zig",
        "scripts/zigux/check-phase3-catalog-selftest.py",
        "Documentation/zigux/phase3-linux-zigux-header-governance.md",
        "zigux/tests/fixtures/phase3_abi_manifest.json",
    ),
    ABI_HEADER: (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_FACILITY_KERNEL 1U",
        "#define ZIGUX_FACILITY_HELPERS 2U",
        "#define ZIGUX_FACILITY_DRIVERS 3U",
        "#define ZIGUX_STATUS_FLAG_ERROR 1U",
        "#define ZIGUX_PANIC_ABORT 0U",
        "#define ZIGUX_ALLOC_KERNEL_HEAP 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "typedef struct zigux_boundary_header {",
        "struct zigux_export_status {",
        "struct zigux_interop_policy {",
        "struct zigux_notifier_block {",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline int zigux_export_status_ok(struct zigux_export_status status)",
    ),
    LINUX_ZIGUX_HEADER: (
        "#define ZIGUX_UAPI_ABI_MAJOR 0u",
        "#define ZIGUX_UAPI_ABI_MINOR 1u",
        "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u",
        "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u",
        "struct zigux_uapi_version {",
        "static inline struct zigux_uapi_version zigux_uapi_version_current(void)",
        "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)",
        "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
        "static inline int zigux_uapi_dev_t_fields_range_is_valid(",
    ),
    DEV_T_HEADER: (
        "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
        "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
        "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
        "#define ZIGUX_DEV_T_MAJOR_OFFSET 0u",
        "#define ZIGUX_DEV_T_MINOR_OFFSET 4u",
        "#define ZIGUX_DEV_MINOR_BITS 20u",
        "struct zigux_dev_t_fields {",
        "static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)",
        "static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    ),
    UAPI_DEV_T: (
        "pub const abi_version: u32 = 1;",
        "pub const major_bits: u6 = 12;",
        "pub const minor_bits: u6 = 20;",
        "pub const Fields = extern struct {",
        "pub const fields_size: usize = @sizeOf(Fields);",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    UAPI_VERSION: (
        "pub const abi_major: u32 = 0;",
        "pub const abi_minor: u32 = 1;",
        "pub const header_family_revision: u32 = 1;",
        "pub const Version = extern struct {",
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    BINDING_DEV_T: (
        "pub const abi_version = uapi.abi_version;",
        "pub const Fields = uapi.Fields;",
        "pub fn init(major: u32, minor: u32) Fields {",
        "pub fn validate(fields: Fields) bool {",
        "pub fn validateRange(start: Fields, end: Fields) bool {",
    ),
    BINDING_VERSION: (
        "pub const abi_major = uapi.abi_major;",
        "pub const abi_minor = uapi.abi_minor;",
        "pub const header_family_revision = uapi.header_family_revision;",
        "pub const Version = uapi.Version;",
        "pub fn current() Version {",
        "pub fn matchesCurrent(version: Version) bool {",
    ),
    BINDING_NOTIFIER: (
        "pub const NotifierResult = enum(u32) {",
        "done = 0,",
        "ok = 1,",
        "stop = 2,",
        "pub const NotifierBlock = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {",
        "pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {",
        "pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {",
    ),
    BINDING_ABI: (
        'const notifier_abi = @import("notifier_abi.zig");',
        "pub const ABI_VERSION: u16 = 1;",
        "pub const FACILITY_KERNEL: u16 = 1;",
        "pub const FACILITY_HELPERS: u16 = 2;",
        "pub const FACILITY_DRIVERS: u16 = 3;",
        "pub const STATUS_FLAG_ERROR: u16 = 1;",
        "pub const PANIC_ABORT: u8 = 0;",
        "pub const PANIC_BUG: u8 = 1;",
        "pub const PANIC_WARN: u8 = 2;",
        "pub const ALLOC_CALLER_PROVIDED: u8 = 0;",
        "pub const ALLOC_KERNEL_HEAP: u8 = 1;",
        "pub const ALLOC_ARENA: u8 = 2;",
        "pub const UNSAFE_NONE: u8 = 0;",
        "pub const UNSAFE_VOLATILE_MMIO: u8 = 1;",
        "pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;",
        "pub const NOTIFIER_DONE: u32 = 0;",
        "pub const NOTIFIER_OK: u32 = 1;",
        "pub const NOTIFIER_STOP: u32 = 2;",
        "pub const PanicMode = enum(u8) {",
        "pub const AllocatorMode = enum(u8) {",
        "pub const UnsafeScope = enum(u8) {",
        "pub const BoundaryHeader = extern struct {",
        "pub const ExportStatus = extern struct {",
        "pub const InteropPolicy = extern struct {",
        "pub const NotifierResult = notifier_abi.NotifierResult;",
        "pub const NotifierBlock = notifier_abi.NotifierBlock;",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
        "pub fn defaultInteropPolicy() InteropPolicy {",
        "pub fn headerIsCanonical(header: BoundaryHeader) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {",
    ),
    EXPORT_SHIM: (
        'const abi = @import("abi_bindings");',
        'const dev_t = @import("dev_t_binding");',
        'const version = @import("version_binding");',
        "pub const BoundaryHeader = abi.BoundaryHeader;",
        "pub const ExportStatus = abi.ExportStatus;",
        "pub const Facility = abi.Facility;",
        "pub fn canonicalHeader(flags: u16) BoundaryHeader {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
        "pub fn errorStatus(code: i32, facility: Facility) ExportStatus {",
        "pub fn statusIsOk(status: ExportStatus) bool {",
        "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {",
    ),
    PHASE3_CATALOG: (
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        'Path("scripts/zigux/phase3_catalog.py")',
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    EXPORT_UAPI_SURVEY_VALIDATOR: (
        'SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")',
        'CATALOG_HELPER_PATH = Path("scripts/zigux/phase3_catalog.py")',
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
    ),
    ABI_TEST: (
        'test "phase3 abi keeps shared layout assertions wired into the replay" {',
        "layout_assert.assertBoundaryHeaderLayout();",
        "layout_assert.assertNotifierChainPriorityIncreaseLayout();",
        'test "phase3 abi keeps export shim compatibility and status helpers reviewable" {',
        'test "phase3 abi keeps version and dev_t relays explicit" {',
        'test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {',
    ),
    TESTS_BUILD: (
        "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
        "const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);",
        '"phase3-abi-core-packet"',
        '"phase3-dump"',
        "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
    ),
    ABI_DUMP: (
        'const abi = @import("abi_bindings");',
        "pub fn main(init: std.process.Init) !void {",
        "const default_header = abi.defaultHeader(0);",
        "const policy = abi.defaultInteropPolicy();",
        "const header_is_canonical = abi.headerIsCanonical(default_header);",
        "abi.STATUS_FLAG_ERROR,",
        "abi.NOTIFIER_DONE,",
        '@offsetOf(abi.NotifierBlock, \\\"priority\\\"),',
        '"  \\\"abi_version\\\": {},\\n"',
        '"  \\\"notifier\\\": {{\\n',
    ),
    MANIFEST_PATH: (
        '"phase": "Phase 3"',
        '"lane": "abi-runtime"',
        '"slug": "phase3-abi-packet"',
        '"status": "shared_abi_binding_surface_present"',
        '"scope": "shared ABI bindings, notifier layouts, export-status layout, and header-compatibility replay"',
        '"Documentation/zigux/phase3-abi-slice.md"',
        '"zigux/bindings/abi.zig"',
        '"zigux/bindings/notifier_abi.zig"',
        '"scripts/zigux/validate-phase3.py"',
        '"scripts/zigux/phase3_catalog.py"',
        '"scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"zigux/tests/phase3_abi.zig"',
        '"zigux/tests/phase3_abi_dump_current.zig"',
        '"python3 scripts/zigux/check-phase3-abi.py --self-test"',
        '"zig build phase3-abi-core-packet --build-file zigux/tests/build.zig"',
        '"zig build phase3-dump --build-file zigux/tests/build.zig"',
        '"scripts/zigux/check-phase3-catalog-selftest.py"',
        '"Documentation/zigux/phase3-linux-zigux-header-governance.md"',
        '"next_safe_step": "keep the shared ABI packet bounded to manifest-backed binding parity, dump-route reviewability, and directly coupled header-to-binding checks before widening into broader Phase 3 catalog or export/UAPI survey work"',
    ),
}

SELF_TEST_CASES = (
    (ABI_SLICE_NOTE, "scripts/zigux/check-phase3-abi.py"),
    (ABI_SLICE_NOTE, "scripts/zigux/phase3_catalog.py"),
    (ABI_SLICE_NOTE, "zigux/tests/phase3_abi.zig"),
    (ABI_SLICE_NOTE, "zigux/tests/phase3_abi_dump_current.zig"),
    (BINDING_ABI, "pub const NotifierResult = notifier_abi.NotifierResult;"),
    (BINDING_ABI, "pub const ABI_VERSION: u16 = 1;"),
    (EXPORT_SHIM, "pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {"),
    (ABI_TEST, 'test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {'),
    (ABI_DUMP, "abi.NOTIFIER_DONE,"),
    (PHASE3_CATALOG, 'print("PHASE3_CATALOG_SELF_TEST=pass")'),
    (MANIFEST_PATH, '"slug": "phase3-abi-packet"'),
)

HEADER_DEFINE_RE = re.compile(r"^\s*#define\s+ZIGUX_([A-Z0-9_]+)\b", re.MULTILINE)
BINDING_CONST_RE = re.compile(r"^\s*pub const\s+([A-Z0-9_]+)\s*:", re.MULTILINE)

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_binding_surface_present",
    "scope": "shared ABI bindings, notifier layouts, export-status layout, and header-compatibility replay",
    "next_safe_step": "keep the shared ABI packet bounded to manifest-backed binding parity, dump-route reviewability, and directly coupled header-to-binding checks before widening into broader Phase 3 catalog or export/UAPI survey work",
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/kernel/export_shim.zig",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/check-phase3-abi.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
)

REQUIRED_REPO_REALITY_GAPS = (
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
)

SAMPLE_MANIFEST = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_binding_surface_present",
    "scope": "shared ABI bindings, notifier layouts, export-status layout, and header-compatibility replay",
    "packet_files": list(REQUIRED_PACKET_FILES),
    "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    "repo_reality_gaps": list(REQUIRED_REPO_REALITY_GAPS),
    "next_safe_step": "keep the shared ABI packet bounded to manifest-backed binding parity, dump-route reviewability, and directly coupled header-to-binding checks before widening into broader Phase 3 catalog or export/UAPI survey work",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _header_names(text: str) -> set[str]:
    return set(HEADER_DEFINE_RE.findall(text))


def _binding_names(text: str) -> set[str]:
    return set(BINDING_CONST_RE.findall(text))


def _append_duplicate_list_entry_issues(
    manifest_name: str,
    field_name: str,
    values: list[object],
    issues: list[str],
) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{manifest_name} duplicate {field_name} entry: "
            f"{value!r} (first index {first_index}, duplicate index {index})"
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    texts: dict[Path, str] = {}

    for rel_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        texts[rel_path] = text
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    header_text = texts.get(ABI_HEADER)
    binding_text = texts.get(BINDING_ABI)
    if header_text is not None and binding_text is not None:
        missing_binding_constants = sorted(_header_names(header_text) - _binding_names(binding_text))
        for name in missing_binding_constants:
            issues.append(
                "missing ABI binding constant for header define: "
                f"ZIGUX_{name} -> {name}"
            )

    notifier_text = texts.get(BINDING_NOTIFIER)
    if binding_text is not None and notifier_text is not None:
        for marker in (
            "pub const NotifierResult = notifier_abi.NotifierResult;",
            "pub const NotifierBlock = notifier_abi.NotifierBlock;",
        ):
            if marker not in binding_text:
                issues.append(f"missing {BINDING_ABI.as_posix()} marker: {marker}")
        for marker in ("done = 0,", "ok = 1,", "stop = 2,"):
            if marker not in notifier_text:
                issues.append(f"missing {BINDING_NOTIFIER.as_posix()} marker: {marker}")

    manifest_text = texts.get(MANIFEST_PATH)
    if manifest_text is not None:
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            for field, expected in REQUIRED_MANIFEST_FIELDS.items():
                actual = manifest.get(field)
                if actual != expected:
                    issues.append(
                        "phase3_abi_manifest.json wrong "
                        f"{field}: {actual!r} != {expected!r}"
                    )

            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")
            if not isinstance(packet_files, list):
                issues.append("phase3_abi_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_abi_manifest.json replay_routes is not a list")
            if not isinstance(repo_reality_gaps, list):
                issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
            if isinstance(packet_files, list):
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json",
                    "packet_files",
                    packet_files,
                    issues,
                )
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_abi_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json",
                    "replay_routes",
                    replay_routes,
                    issues,
                )
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_abi_manifest.json missing replay route: "
                            f"{route}"
                        )
            if isinstance(repo_reality_gaps, list):
                _append_duplicate_list_entry_issues(
                    "phase3_abi_manifest.json",
                    "repo_reality_gaps",
                    repo_reality_gaps,
                    issues,
                )
                for gap in repo_reality_gaps:
                    if (repo_root / gap).exists():
                        issues.append(
                            "phase3_abi_manifest.json repo_reality_gaps entry is present on disk: "
                            f"{gap}"
                        )
                for gap in REQUIRED_REPO_REALITY_GAPS:
                    if gap not in repo_reality_gaps:
                        issues.append(
                            "phase3_abi_manifest.json missing repo_reality_gaps entry: "
                            f"{gap}"
                        )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_check_") as temp_dir:
        root = Path(temp_dir)

        for rel_path, markers in REQUIRED_MARKERS.items():
            _write(root / rel_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for rel_path, marker in SELF_TEST_CASES:
            for populate_path, markers in REQUIRED_MARKERS.items():
                _write(root / populate_path, "\n".join(markers) + "\n")
            _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
            _write(root / rel_path, _read(root / rel_path).replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {rel_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ABI_CHECK_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        for populate_path, markers in REQUIRED_MARKERS.items():
            _write(root / populate_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_duplicate = (
            "phase3_abi_manifest.json duplicate replay_routes entry: "
            "'python3 scripts/zigux/check-phase3-abi.py --self-test' "
        )
        if not any(issue.startswith(expected_duplicate) for issue in issues):
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected duplicate replay route was not reported")
            return 1

        for populate_path, markers in REQUIRED_MARKERS.items():
            _write(root / populate_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove(REQUIRED_REPLAY_ROUTES[-1])
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_missing_route = (
            "phase3_abi_manifest.json missing replay route: "
            f"{REQUIRED_REPLAY_ROUTES[-1]}"
        )
        if expected_missing_route not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected missing export/uapi layout replay route was not reported")
            return 1

        for populate_path, markers in REQUIRED_MARKERS.items():
            _write(root / populate_path, "\n".join(markers) + "\n")
        _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["repo_reality_gaps"].append(BINDING_ABI.as_posix())
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_present_gap = (
            "phase3_abi_manifest.json repo_reality_gaps entry is present on disk: "
            f"{BINDING_ABI.as_posix()}"
        )
        if expected_present_gap not in issues:
            print("PHASE3_ABI_CHECK_SELF_TEST=fail")
            print("expected present-on-disk repo-reality gap was not reported")
            return 1

    print("PHASE3_ABI_CHECK_SELF_TEST=pass")
    print(f"PHASE3_ABI_CHECK_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 4}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 shared ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 shared ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_CHECK=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_ABI_CHECK=pass")
    print("PHASE3_ABI_SCOPE=shared-abi-packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

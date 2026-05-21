#!/usr/bin/env python3
"""Validate the current bounded Phase 3 shared ABI packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")
NOTIFIER_BINDINGS_PATH = Path("zigux/bindings/notifier_abi.zig")
ABI_CHECKER_PATH = Path("scripts/zigux/check-phase3-abi.py")
PHASE3_CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")
HEADER_GOVERNANCE_VALIDATOR_PATH = Path(
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
)
TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
ABI_TEST_PATH = Path("zigux/tests/phase3_abi.zig")
ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
EXPORT_UAPI_LAYOUT_PATH = Path("zigux/tests/phase3_export_uapi_layout.zig")
EXPORT_UAPI_LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")

CURRENT_REPO_REALITY_GAP = (
    "zigux/bindings/abi.zig still duplicates notifier result, notifier layout, and "
    "list-helper ownership that current master already materializes in "
    "zigux/bindings/notifier_abi.zig, so the shared ABI packet is not yet on a "
    "single notifier-binding ownership path"
)
CURRENT_NEXT_SAFE_STEP = (
    "relay the shared notifier result, notifier layout, and list-helper surface in "
    "zigux/bindings/abi.zig through explicit aliases and wrappers over "
    "zigux/bindings/notifier_abi.zig, then rerun the dedicated phase3 ABI checker "
    "plus the narrowest honest Zig replay before treating the packet as ownership-clean"
)

REQUIRED_SOURCE_MARKERS = {
    ABI_HEADER_PATH: (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_FACILITY_KERNEL 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_boundary_header {",
        "struct zigux_interop_policy {",
        "struct zigux_export_status {",
        "struct zigux_notifier_block {",
        "struct zigux_list_head {",
        "struct zigux_hlist_head {",
        "struct zigux_hlist_node {",
        "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
        "static inline int zigux_notifier_first_chain_priority_increase(",
        "static inline int zigux_list_has_consistent_backlinks(",
        "static inline int zigux_hlist_has_consistent_prev_links(",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline zigux_boundary_header zigux_compatible_header(",
        "static inline int zigux_abi_version_is_current(uint16_t abi_version)",
        "static inline int zigux_header_is_canonical(zigux_boundary_header header)",
        "static inline int zigux_header_is_compatible(zigux_boundary_header header)",
        "static inline int zigux_header_extends_boundary(zigux_boundary_header header)",
        "static inline uint32_t zigux_header_requested_extra_bytes(",
        "static inline zigux_boundary_header zigux_header_canonicalize(",
        "static inline struct zigux_interop_policy zigux_default_interop_policy(void)",
        "static inline struct zigux_export_status zigux_make_status(",
        "static inline struct zigux_export_status zigux_ok_status(uint16_t facility)",
        "static inline int zigux_export_status_ok(struct zigux_export_status status)",
    ),
    ABI_BINDINGS_PATH: (
        "pub const ABI_VERSION: u16 = 1;",
        "pub const FACILITY_KERNEL: u16 = 1;",
        "pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;",
        "pub const BoundaryHeader = extern struct {",
        "pub const InteropPolicy = extern struct {",
        "pub const ExportStatus = extern struct {",
        "pub const NotifierResult = enum(u32) {",
        "pub const NotifierBlock = extern struct {",
        "pub const ListHead = extern struct {",
        "pub const HListHead = extern struct {",
        "pub const HListNode = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {",
        "pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {",
        "pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {",
        "pub fn defaultHeader(flags: u16) BoundaryHeader {",
        "pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {",
        "pub fn headerHasCurrentAbiVersion(abi_version: u16) bool {",
        "pub fn headerIsCanonical(header: BoundaryHeader) bool {",
        "pub fn headerIsCompatible(header: BoundaryHeader) bool {",
        "pub fn extendsBoundary(header: BoundaryHeader) bool {",
        "pub fn requestedExtraBytes(header: BoundaryHeader) u32 {",
        "pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {",
        "pub fn defaultInteropPolicy() InteropPolicy {",
        "pub fn makeStatus(code: i32, facility: Facility) ExportStatus {",
        "pub fn okStatus(facility: Facility) ExportStatus {",
        "pub fn statusIsOk(status: ExportStatus) bool {",
    ),
    NOTIFIER_BINDINGS_PATH: (
        "pub const NotifierResult = enum(u32) {",
        "pub const NotifierBlock = extern struct {",
        "pub const NotifierChainPriorityIncrease = extern struct {",
        "pub const ListHead = extern struct {",
        "pub const HListHead = extern struct {",
        "pub const HListNode = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {",
        "pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {",
        "pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {",
    ),
    ABI_CHECKER_PATH: (
        'ABI_SLICE_NOTE = Path("Documentation/zigux/phase3-abi-slice.md")',
        'ABI_HEADER = Path("include/zigux/abi.h")',
        'BINDING_ABI = Path("zigux/bindings/abi.zig")',
        'EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")',
        'MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
        "def validate_repo(repo_root: Path) -> list[str]:",
        'print("PHASE3_ABI_CHECK_SELF_TEST=pass")',
    ),
    PHASE3_CATALOG_PATH: (
        'PHASE3_CATALOG_PHASE = "Phase 3"',
        'PHASE3_CATALOG_SCOPE = "abi-runtime"',
        "def build_catalog(repo_root: Path) -> dict[str, object]:",
        'print("PHASE3_CATALOG_SELF_TEST=pass")',
    ),
    RUNNER_PATH: (
        'Path("scripts/zigux/validate-phase3.py")',
        'Path("scripts/zigux/validate-phase3-export-uapi-survey.py")',
        'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
        '"phase3-validate"',
    ),
    HEADER_GOVERNANCE_VALIDATOR_PATH: (
        'HEADER_PATH = Path("include/linux/zigux.h")',
        'NOTE_PATH = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
        'print("PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass")',
    ),
    TESTS_BUILD_PATH: (
        "const phase3_policy_starter_packet = addPhase3PolicyStarterPacket(b, target, optimize);",
        "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
        "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);",
        "const phase3_abi_dump = addPhase3AbiDump(b, target, optimize);",
        'root_source_file = b.path("phase3_policy_starter_packet.zig"),',
        'root_source_file = b.path("phase3_abi.zig"),',
        'root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'root_source_file = b.path("phase3_abi_dump_current.zig"),',
        'root_module.addImport("header_family_binding", header_family_binding);',
        '"phase3-policy-starter-packet"',
        '"phase3-abi-core-packet"',
        '"phase3-export-uapi-layout"',
        '"phase3-dump"',
        "phase3_test_step.dependOn(&phase3_policy_starter_packet.step);",
        "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
        "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
        "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    ),
    ABI_TEST_PATH: (
        'test "phase3 abi keeps shared layout assertions wired into the replay" {',
        "try layout_assert.assertPublishedAbiLayouts();",
        'test "phase3 abi keeps export shim compatibility and status helpers reviewable" {',
        'test "phase3 abi keeps version and dev_t relays explicit" {',
        'test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {',
        'test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {',
    ),
    EXPORT_UAPI_LAYOUT_PATH: (
        'const header_family = @import("header_family_binding");',
        'test "export and uapi dev_t layouts stay aligned" {',
        'test "export and uapi version layouts stay aligned" {',
        'test "header-family binding keeps the bounded relay surface explicit" {',
        'test "header-family status wrappers stay aligned with export shim validation" {',
        'test "export shim relays version compatibility without widening the boundary" {',
        'test "export shim reuses the canonical boundary header contract" {',
        'test "export shim mirrors boundary header predicate helpers" {',
        'test "export shim keeps facility tagged statuses explicit" {',
        'test "export shim relays starter dev_t validation and range checks through the focused replay" {',
    ),
    EXPORT_UAPI_LAYOUT_BUILD_PATH: (
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        '.root_source_file = b.path("../bindings/header_family.zig"),',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'root_module.addImport("header_family_binding", header_family_binding);',
        '"phase3-export-uapi-layout-test"',
    ),
    ABI_MANIFEST_PATH: (
        '"phase": "Phase 3"',
        '"lane": "abi-runtime"',
        '"slug": "phase3-abi-packet"',
        '"status": "shared_abi_and_header_family_binding_surface_present"',
        '"zigux/tests/phase3_policy_starter_packet.zig"',
        '"zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zigux/tests/phase3_policy_starter_packet_manifest.json"',
        '"scripts/zigux/check-phase3-policy-starter-packet.py"',
        '"zigux/tests/phase3_export_uapi_layout.zig"',
        '"Documentation/zigux/phase3-export-uapi-boundary-survey.md"',
        '"Documentation/zigux/phase3-linux-zigux-header-governance.md"',
        '"scripts/zigux/validate-phase3-export-uapi-survey.py"',
        '"scripts/zigux/validate-phase3-linux-zigux-header-governance.py"',
        '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
        '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test"',
        '"python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"',
        CURRENT_REPO_REALITY_GAP,
        CURRENT_NEXT_SAFE_STEP,
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": (
        "shared ABI bindings, directly coupled helper decoding, header-family "
        "follow-through, notifier layouts, export-status layout, and "
        "header-compatibility replay"
    ),
    "next_safe_step": CURRENT_NEXT_SAFE_STEP,
}

REQUIRED_MANIFEST_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/header_family.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/unsafe/narrow.zig",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
)

REQUIRED_MANIFEST_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi.py --self-test",
    "python3 scripts/zigux/check-phase3-abi.py",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
)

REQUIRED_MANIFEST_REPO_REALITY_GAPS = (CURRENT_REPO_REALITY_GAP,)

HEADER_TYPEDEF_ALIAS_RE = re.compile(r"^\s*}\s*([A-Za-z_][A-Za-z0-9_]*)\s*;")
ZIG_PUB_FN_RE = re.compile(r"^\s*pub fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_missing_markers(
    repo_root: Path, issues: list[str], texts: dict[Path, str]
) -> None:
    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        texts[rel_path] = text
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")


def _validate_manifest(manifest_text: str) -> list[str]:
    issues: list[str] = []
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON in {ABI_MANIFEST_PATH.as_posix()}: {exc}"]

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        for required in REQUIRED_MANIFEST_PACKET_FILES:
            if required not in packet_files:
                issues.append(
                    f"phase3_abi_manifest.json missing packet_files entry: {required}"
                )

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        for required in REQUIRED_MANIFEST_REPLAY_ROUTES:
            if required not in replay_routes:
                issues.append(
                    f"phase3_abi_manifest.json missing replay route: {required}"
                )

    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    else:
        if repo_reality_gaps != list(REQUIRED_MANIFEST_REPO_REALITY_GAPS):
            issues.append(
                "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation"
            )

    return issues


def _append_duplicate_name_issues(
    rel_path: Path,
    text: str,
    pattern: re.Pattern[str],
    label: str,
    issues: list[str],
) -> None:
    first_lines: dict[str, int] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = pattern.match(line)
        if match is None:
            continue
        name = match.group(1)
        first_line = first_lines.get(name)
        if first_line is None:
            first_lines[name] = line_no
            continue
        issues.append(
            f"duplicate {label}: {name} (first line {first_line}, duplicate line {line_no})"
        )


def _append_duplicate_issues(texts: dict[Path, str], issues: list[str]) -> None:
    header_text = texts.get(ABI_HEADER_PATH)
    if header_text is not None:
        _append_duplicate_name_issues(
            ABI_HEADER_PATH,
            header_text,
            HEADER_TYPEDEF_ALIAS_RE,
            "ABI header typedef alias",
            issues,
        )

    bindings_text = texts.get(ABI_BINDINGS_PATH)
    if bindings_text is not None:
        _append_duplicate_name_issues(
            ABI_BINDINGS_PATH,
            bindings_text,
            ZIG_PUB_FN_RE,
            "ABI binding pub fn",
            issues,
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    texts: dict[Path, str] = {}
    _append_missing_markers(repo_root, issues, texts)

    manifest_text = texts.get(ABI_MANIFEST_PATH)
    if manifest_text is not None:
        issues.extend(_validate_manifest(manifest_text))

    _append_duplicate_issues(texts, issues)
    return issues


def _populate_repo(root: Path) -> None:
    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        suffix = "\n} zigux_boundary_header;\n" if rel_path == ABI_HEADER_PATH else "\n"
        _write(root / rel_path, "\n".join(markers) + suffix)

    manifest = {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "status": "shared_abi_and_header_family_binding_surface_present",
        "scope": REQUIRED_MANIFEST_FIELDS["scope"],
        "packet_files": list(REQUIRED_MANIFEST_PACKET_FILES),
        "replay_routes": list(REQUIRED_MANIFEST_REPLAY_ROUTES),
        "repo_reality_gaps": list(REQUIRED_MANIFEST_REPO_REALITY_GAPS),
        "next_safe_step": CURRENT_NEXT_SAFE_STEP,
    }
    _write(root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_") as temp_dir:
        repo_root = Path(temp_dir)
        _populate_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                TESTS_BUILD_PATH,
                "const phase3_policy_starter_packet = addPhase3PolicyStarterPacket(b, target, optimize);\n",
                "missing zigux/tests/build.zig marker: const phase3_policy_starter_packet = addPhase3PolicyStarterPacket(b, target, optimize);",
            ),
            (
                TESTS_BUILD_PATH,
                'root_source_file = b.path("phase3_policy_starter_packet.zig"),\n',
                'missing zigux/tests/build.zig marker: root_source_file = b.path("phase3_policy_starter_packet.zig"),',
            ),
            (
                TESTS_BUILD_PATH,
                "phase3_test_step.dependOn(&phase3_policy_starter_packet.step);\n",
                "missing zigux/tests/build.zig marker: phase3_test_step.dependOn(&phase3_policy_starter_packet.step);",
            ),
            (
                ABI_MANIFEST_PATH,
                '"zigux/tests/phase3_policy_starter_packet_manifest.json",\n',
                'missing zigux/tests/fixtures/phase3_abi_manifest.json marker: "zigux/tests/phase3_policy_starter_packet_manifest.json"',
            ),
            (
                ABI_MANIFEST_PATH,
                '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",\n',
                'missing zigux/tests/fixtures/phase3_abi_manifest.json marker: "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
            ),
            (
                TESTS_BUILD_PATH,
                'root_module.addImport("header_family_binding", header_family_binding);\n',
                'missing zigux/tests/build.zig marker: root_module.addImport("header_family_binding", header_family_binding);',
            ),
            (
                EXPORT_UAPI_LAYOUT_BUILD_PATH,
                '.root_source_file = b.path("../bindings/header_family.zig"),\n',
                'missing zigux/tests/phase3_export_uapi_layout_build.zig marker: .root_source_file = b.path("../bindings/header_family.zig"),',
            ),
            (
                HEADER_GOVERNANCE_VALIDATOR_PATH,
                'NOTE_PATH = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")\n',
                'missing scripts/zigux/validate-phase3-linux-zigux-header-governance.py marker: NOTE_PATH = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")',
            ),
            (
                ABI_CHECKER_PATH,
                'MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")\n',
                'missing scripts/zigux/check-phase3-abi.py marker: MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")',
            ),
        )

        for rel_path, needle, expected in cases:
            current = _read(repo_root / rel_path)
            _write(repo_root / rel_path, current.replace(needle, "", 1))
            issues = validate_repo(repo_root)
            if expected not in issues:
                print("PHASE3_VALIDATION_SELF_TEST=fail")
                print(f"expected issue was not reported: {expected}")
                return 1
            _write(repo_root / rel_path, current)

        manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
        manifest["replay_routes"].remove(
            "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
        )
        _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
        )
        if expected not in issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print(f"expected issue was not reported: {expected}")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
        manifest["repo_reality_gaps"] = ["stale gap text"]
        _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared packet expectation"
        )
        if expected not in issues:
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print(f"expected issue was not reported: {expected}")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(repo_root / ABI_MANIFEST_PATH))
        manifest["next_safe_step"] = "old export/uapi next step"
        _write(repo_root / ABI_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = "phase3_abi_manifest.json wrong next_safe_step:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print(f"expected issue was not reported: {expected}")
            return 1

        _populate_repo(repo_root)
        current_header = _read(repo_root / ABI_HEADER_PATH)
        _write(
            repo_root / ABI_HEADER_PATH,
            current_header
            + "\ntypedef struct zigux_layout_alias {\n"
            + "    int value;\n"
            + "} zigux_boundary_header;\n",
        )
        issues = validate_repo(repo_root)
        if not any(
            issue.startswith("duplicate ABI header typedef alias: zigux_boundary_header ")
            for issue in issues
        ):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected duplicate typedef issue was not reported")
            return 1

        _populate_repo(repo_root)
        current_bindings = _read(repo_root / ABI_BINDINGS_PATH)
        _write(
            repo_root / ABI_BINDINGS_PATH,
            current_bindings
            + "\npub fn defaultHeader(flags: u16) BoundaryHeader {\n"
            + "    _ = flags;\n"
            + "    return undefined;\n"
            + "}\n",
        )
        issues = validate_repo(repo_root)
        if not any(
            issue.startswith("duplicate ABI binding pub fn: defaultHeader ")
            for issue in issues
        ):
            print("PHASE3_VALIDATION_SELF_TEST=fail")
            print("expected duplicate pub fn issue was not reported")
            return 1

    print("PHASE3_VALIDATION_SELF_TEST=pass")
    print("PHASE3_VALIDATION_SELF_TEST_CASE_COUNT=13")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 3 shared ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help=(
            "repository root that contains include/zigux/, zigux/bindings/, "
            "scripts/zigux/, and zigux/tests/"
        ),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_VALIDATION=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_VALIDATION=pass")
    print(
        "PHASE3_SCOPE=shared-abi-binding-layout-catalog-dump-export-uapi-and-low-level-wrapper-route-surface"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
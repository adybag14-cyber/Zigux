#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
DOCS_ROOT_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"
LINUX_HEADER_REL = "include/linux/zigux.h"
ABI_HEADER_REL = "include/zigux/abi.h"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
BUILD_FILE_REL = "zigux/tests/build.zig"
EXPORT_UAPI_LAYOUT_REL = "zigux/tests/phase3_export_uapi_layout.zig"
LINUX_HEADER_GOVERNANCE_REL = "Documentation/zigux/phase3-linux-zigux-header-governance.md"
VALIDATOR_REL = "scripts/zigux/validate-phase3-export-uapi-survey.py"
SELF_TEST_CASE_COUNT = 12

REQUIRED_FILES = (
    SURVEY_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    LINUX_HEADER_REL,
    ABI_HEADER_REL,
    ABI_MANIFEST_REL,
    BUILD_FILE_REL,
    EXPORT_UAPI_LAYOUT_REL,
    LINUX_HEADER_GOVERNANCE_REL,
    WORKFLOW_REL,
)

MANIFEST_REQUIRED_FILES = (
    SURVEY_REL,
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    LINUX_HEADER_REL,
    ABI_HEADER_REL,
    BUILD_FILE_REL,
    EXPORT_UAPI_LAYOUT_REL,
    LINUX_HEADER_GOVERNANCE_REL,
    VALIDATOR_REL,
)

SURVEY_PROVENANCE_MARKERS = (
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`",
)

SURVEY_EXACT_MARKERS = (
    "`PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=shared-abi-slice-owns-linux-header-governance-export-uapi-packet-owns-starter-boundary-wording-only`",
    "`PHASE3_C_HEADER_GROWTH_RULE=shared-abi-resurvey-for-linux-header-growth-packet-local-resurvey-for-starter-entry-point-growth`",
    "`PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-layout-replay-plus-shared-review-surface-refresh`",
    "`PHASE3_LAYOUT_REPLAY_OWNERSHIP=export-uapi-packet-owns-focused-starter-boundary-layout-replay`",
    f"`PHASE3_EXPORT_SHIM_PATH={EXPORT_SHIM_REL}`",
    f"`PHASE3_UAPI_VERSION_PATH={UAPI_VERSION_REL}`",
    f"`PHASE3_LINUX_HEADER_PATH={LINUX_HEADER_REL}`",
    f"`PHASE3_ABI_HEADER_PATH={ABI_HEADER_REL}`",
    f"`PHASE3_EXPORT_UAPI_LAYOUT_PATH={EXPORT_UAPI_LAYOUT_REL}`",
)

SURVEY_BLOB_MARKERS = (
    ("PHASE3_EXPORT_SHIM_BLOB_SHA", EXPORT_SHIM_REL),
    ("PHASE3_UAPI_VERSION_BLOB_SHA", UAPI_VERSION_REL),
    ("PHASE3_LINUX_HEADER_BLOB_SHA", LINUX_HEADER_REL),
    ("PHASE3_ABI_HEADER_BLOB_SHA", ABI_HEADER_REL),
    ("PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA", EXPORT_UAPI_LAYOUT_REL),
)

REQUIRED_MARKERS = {
    EXPORT_SHIM_REL: (
        "pub const Header = uapi_version.Header;",
        "pub const abi_version: u16 = uapi_version.abi_version;",
        "pub const header_size: u32 = uapi_version.header_size;",
        "pub const HeaderCompatibility = uapi_version.Compatibility;",
        "pub const HeaderAcceptance = uapi_version.AcceptedHeader;",
        "pub fn versionedHeader(size: u32, version: u16, flags: u16) Header {",
        "return uapi_version.versionedHeader(size, version, flags);",
        "pub fn canonicalHeader(flags: u16) Header {",
        "return uapi_version.canonicalHeader(flags);",
        "pub fn boundaryHeader(flags: u16) Header {",
        "return uapi_version.boundaryHeader(flags);",
        "pub fn compatibleHeader(size: u32, flags: u16) Header {",
        "return uapi_version.compatibleHeader(size, flags);",
        "pub fn header(flags: u16) Header {",
        "return canonicalHeader(flags);",
        "pub fn isCurrentAbiVersion(version: u16) bool {",
        "return uapi_version.isCurrentAbiVersion(version);",
        "pub fn isCompatibleSize(size: u32) bool {",
        "return uapi_version.isCompatibleSize(size);",
        "pub fn isCanonicalSize(size: u32) bool {",
        "return uapi_version.isCanonicalSize(size);",
        "pub fn acceptHeader(header_value: Header) ?HeaderAcceptance {",
        "return uapi_version.acceptHeader(header_value);",
        "pub fn headerCompatibility(header_value: Header) ?HeaderCompatibility {",
        "return uapi_version.compatibility(header_value);",
        "pub fn isCompatibleHeader(header_value: Header) bool {",
        "return uapi_version.isCompatible(header_value);",
        "pub fn isCanonicalHeader(header_value: Header) bool {",
        "return uapi_version.isCanonical(header_value);",
        "pub fn canonicalizeHeader(header_value: Header) ?Header {",
        "return uapi_version.canonicalizeHeader(header_value);",
        "pub fn compatibilityStatus(",
        "return if (isCompatibleHeader(header_value)) ok(facility) else errno(incompatible_code, facility);",
        "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {",
        'test "phase3 export shim keeps failure encoding explicit" {',
        'test "phase3 export shim reuses the shared boundary-header compatibility rules" {',
        "const accepted_canonical = acceptHeader(canonical).?;",
        "const accepted_future = acceptHeader(future_compatible).?;",
        'test "phase3 export shim relays compatibility through explicit status packets" {',
    ),
    UAPI_VERSION_REL: (
        "pub const Compatibility = enum {",
        "canonical,",
        "future_compatible,",
        "pub const AcceptedHeader = struct {",
        "compatibility: Compatibility,",
        "canonical: Header,",
        "pub fn canonicalHeader(flags: u16) Header {",
        "pub fn boundaryHeader(flags: u16) Header {",
        "return canonicalHeader(flags);",
        "pub fn compatibleHeader(size: u32, flags: u16) Header {",
        "pub fn acceptHeader(header: Header) ?AcceptedHeader {",
        "const mode = compatibility(header) orelse return null;",
        "pub fn canonicalizeHeader(header: Header) ?Header {",
        "return (acceptHeader(header) orelse return null).canonical;",
        'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {',
        "const accepted_canonical = acceptHeader(canonical).?;",
        "const accepted_future = acceptHeader(future_compatible).?;",
        'test "phase3 uapi canonicalizes compatible headers without widening the boundary" {',
        "const accepted = acceptHeader(future_compatible).?;",
    ),
    LINUX_HEADER_REL: (
        "#include <zigux/abi.h>",
        "static inline struct zigux_export_status zigux_status_ok(",
        "static inline struct zigux_export_status zigux_status_err(",
    ),
    ABI_HEADER_REL: (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_STATUS_FLAG_ERROR 1U",
        "struct zigux_boundary_header {",
        "struct zigux_export_status {",
    ),
    EXPORT_UAPI_LAYOUT_REL: (
        'const export_shim = @import("export_shim");',
        'const uapi_version = @import("uapi_version");',
        'test "phase3 export shim and uapi keep canonical boundary layout" {',
        'const header: export_shim.Header = export_shim.header(0x55);',
        'const uapi_header: uapi_version.Header = uapi_version.boundaryHeader(0x55);',
        "const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x55);",
        "const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);",
        "const uapi_undersized = uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x55);",
        "const accepted_canonical = export_shim.acceptHeader(header).?;",
        "const accepted_future = export_shim.acceptHeader(future_compatible).?;",
        "const uapi_accepted_canonical = uapi_version.acceptHeader(uapi_header).?;",
        "const uapi_accepted_future = uapi_version.acceptHeader(future_compatible).?;",
        "try std.testing.expectEqual(header, uapi_header);",
        "try std.testing.expectEqual(export_shim.HeaderCompatibility.canonical, accepted_canonical.compatibility);",
        "try std.testing.expectEqual(header, accepted_future.canonical);",
        "try std.testing.expectEqual(uapi_header, uapi_accepted_future.canonical);",
        "try std.testing.expectEqual(undersized, uapi_undersized);",
        "try std.testing.expect(export_shim.headerCompatibility(undersized) == null);",
        "try std.testing.expect(uapi_version.compatibility(uapi_undersized) == null);",
        "try std.testing.expect(export_shim.acceptHeader(undersized) == null);",
        "try std.testing.expect(uapi_version.acceptHeader(uapi_undersized) == null);",
        "try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);",
        "try std.testing.expect(uapi_version.canonicalizeHeader(uapi_undersized) == null);",
        "try std.testing.expect(export_shim.headerCompatibility(version_mismatch) == null);",
        "try std.testing.expect(uapi_version.compatibility(version_mismatch) == null);",
        "try std.testing.expect(export_shim.acceptHeader(version_mismatch) == null);",
        "try std.testing.expect(uapi_version.acceptHeader(version_mismatch) == null);",
        'test "phase3 export shim keeps compatibility status relays explicit" {',
        "const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);",
    ),
}

DOCS_ROOT_REQUIRED_MARKERS = (
    "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `Documentation/zigux/phase3-export-uapi-boundary-survey.md` - `Documentation/zigux/phase3-linux-zigux-header-governance.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/check-phase3-policy-byte-guards.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py` - `scripts/zigux/survey-phase3-abi-constant-parity.py` - `scripts/zigux/check-phase3-catalog-selftest.py` - `scripts/zigux/check-phase3-readme-tooling-inventory.py` - `scripts/zigux/check-phase3-abi-dump-gate.py` - `scripts/zigux/check-phase3-selftest-surface.py` - `scripts/zigux/phase3_catalog.py` - `scripts/zigux/phase3_check_lib.py` - `scripts/zigux/generate-phase3-check-wrappers.py` - `scripts/zigux/run-phase3-checks.py` - `scripts/zigux/validate_phase3_selftest.py` - `zigux/tests/README.md` - `zigux/Makefile` - `python3 scripts/zigux/validate-phase3.py`, `python3 scripts/zigux/validate-phase3.py --slug abi`, `python3 scripts/zigux/run-phase3-checks.py --slug abi`, `python3 scripts/zigux/phase3_catalog.py --audit-doc-sync`, `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-validate`, and `make -C zigux phase3` now keep the current ABI substrate reviewable through the shared `abi` slice, the policy-and-unsafe survey, the dedicated policy-byte guard, the low-level-wrapper survey, the export/UAPI boundary survey, the dedicated Linux `zigux.h` header-governance note, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.",
    "the export/UAPI boundary survey, the dedicated Linux `zigux.h` header-governance note, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.",
)

SCRIPTS_README_REQUIRED_MARKERS = (
    "`validate-phase3-export-uapi-survey.py`",
    "`validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `include/linux/zigux.h`, `include/zigux/abi.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and the workflow hooks that rerun that same survey surface.",
)

WORKFLOW_REQUIRED_MARKERS = (
    "- name: Validate Phase 3 export/UAPI survey",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "- name: Self-test Phase 3 export/UAPI survey",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def normalized_lines(text: str) -> list[str]:
    values: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        values.append(line)
    return values


def require_exact_line_count(issues: list[str], text: str, prefix: str, line: str) -> None:
    count = normalized_lines(text).count(line)
    if count == 1:
        return
    if count == 0:
        issues.append(f"missing_{prefix}:{line}")
        return
    issues.append(f"duplicate_{prefix}:{count}:{line}")


def require_one_of_exact_lines(issues: list[str], text: str, prefix: str, lines: tuple[str, ...]) -> None:
    normalized = normalized_lines(text)
    matching = [(line, normalized.count(line)) for line in lines if normalized.count(line) > 0]
    if not matching:
        issues.append(f"missing_{prefix}:{'|'.join(lines)}")
        return
    total = sum(count for _, count in matching)
    if total != 1:
        issues.append(f"duplicate_{prefix}:{total}:{'|'.join(lines)}")


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def extract_backticked_values(text: str, key: str) -> list[str]:
    prefix = f"`{key}="
    values: list[str] = []
    for line in normalized_lines(text):
        if line.startswith(prefix) and line.endswith("`"):
            values.append(line[len(prefix) : -1])
    return values


def validate_manifest(root: Path, issues: list[str]) -> None:
    manifest_path = root / ABI_MANIFEST_REL
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"missing_manifest:{ABI_MANIFEST_REL}")
        return
    except json.JSONDecodeError as exc:
        issues.append(f"invalid_manifest:{ABI_MANIFEST_REL}:{exc.msg}")
        return

    files = manifest.get("files")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        issues.append(f"invalid_manifest_files:{ABI_MANIFEST_REL}")
        return

    file_count = manifest.get("file_count")
    if file_count != len(files):
        issues.append(f"stale_manifest_file_count:{ABI_MANIFEST_REL}:{file_count}!={len(files)}")

    for rel in MANIFEST_REQUIRED_FILES:
        if rel not in files:
            issues.append(f"manifest_missing_required_file:{rel}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    survey_path = root / SURVEY_REL
    if not survey_path.exists():
        return issues
    survey = survey_path.read_text(encoding="utf-8")

    require_one_of_exact_lines(issues, survey, "survey_provenance", SURVEY_PROVENANCE_MARKERS)
    for marker in SURVEY_EXACT_MARKERS:
        require_exact_line_count(issues, survey, "survey_marker", marker)

    for key, rel in SURVEY_BLOB_MARKERS:
        values = extract_backticked_values(survey, key)
        if not values:
            issues.append(f"missing_survey_marker:`{key}=<sha>`")
            continue
        if len(values) != 1:
            issues.append(f"duplicate_survey_marker:{len(values)}:`{key}=<sha>`")
            continue
        expected = blob_sha(root / rel)
        if values[0] != expected:
            issues.append(f"stale_survey_blob:{key}:{values[0]}!={expected}")

    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{rel}:{marker}")

    validate_manifest(root, issues)

    docs_root_path = root / DOCS_ROOT_REL
    if docs_root_path.exists():
        docs_root = docs_root_path.read_text(encoding="utf-8")
        for marker in DOCS_ROOT_REQUIRED_MARKERS:
            require_exact_line_count(issues, docs_root, "docs_root_marker", marker)

    scripts_readme_path = root / SCRIPTS_README_REL
    if scripts_readme_path.exists():
        scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        for marker in SCRIPTS_README_REQUIRED_MARKERS:
            require_exact_line_count(issues, scripts_readme, "scripts_readme_marker", marker)

    workflow_path = root / WORKFLOW_REL
    if workflow_path.exists():
        workflow_lines = [line.strip() for line in workflow_path.read_text(encoding="utf-8").splitlines()]
        for marker in WORKFLOW_REQUIRED_MARKERS:
            count = workflow_lines.count(marker)
            if count == 0:
                issues.append(f"missing_workflow_marker:{marker}")
            elif count != 1:
                issues.append(f"duplicate_workflow_marker:{count}:{marker}")

    return issues


def export_shim_text() -> str:
    return "\n".join(
        (
            "pub const Header = uapi_version.Header;",
            "pub const abi_version: u16 = uapi_version.abi_version;",
            "pub const header_size: u32 = uapi_version.header_size;",
            "pub const HeaderCompatibility = uapi_version.Compatibility;",
            "pub const HeaderAcceptance = uapi_version.AcceptedHeader;",
            "pub fn versionedHeader(size: u32, version: u16, flags: u16) Header {",
            "    return uapi_version.versionedHeader(size, version, flags);",
            "}",
            "pub fn canonicalHeader(flags: u16) Header {",
            "    return uapi_version.canonicalHeader(flags);",
            "}",
            "pub fn boundaryHeader(flags: u16) Header {",
            "    return uapi_version.boundaryHeader(flags);",
            "}",
            "pub fn compatibleHeader(size: u32, flags: u16) Header {",
            "    return uapi_version.compatibleHeader(size, flags);",
            "}",
            "pub fn header(flags: u16) Header {",
            "    return canonicalHeader(flags);",
            "}",
            "pub fn isCurrentAbiVersion(version: u16) bool {",
            "    return uapi_version.isCurrentAbiVersion(version);",
            "}",
            "pub fn isCompatibleSize(size: u32) bool {",
            "    return uapi_version.isCompatibleSize(size);",
            "}",
            "pub fn isCanonicalSize(size: u32) bool {",
            "    return uapi_version.isCanonicalSize(size);",
            "}",
            "pub fn acceptHeader(header_value: Header) ?HeaderAcceptance {",
            "    return uapi_version.acceptHeader(header_value);",
            "}",
            "pub fn headerCompatibility(header_value: Header) ?HeaderCompatibility {",
            "    return uapi_version.compatibility(header_value);",
            "}",
            "pub fn isCompatibleHeader(header_value: Header) bool {",
            "    return uapi_version.isCompatible(header_value);",
            "}",
            "pub fn isCanonicalHeader(header_value: Header) bool {",
            "    return uapi_version.isCanonical(header_value);",
            "}",
            "pub fn canonicalizeHeader(header_value: Header) ?Header {",
            "    return uapi_version.canonicalizeHeader(header_value);",
            "}",
            "pub fn compatibilityStatus(",
            "    header_value: Header,",
            "    incompatible_code: i32,",
            "    facility: abi.Facility,",
            ") abi.ExportStatus {",
            "    return if (isCompatibleHeader(header_value)) ok(facility) else errno(incompatible_code, facility);",
            "}",
            "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {",
            "    return status;",
            "}",
            'test "phase3 export shim keeps failure encoding explicit" {',
            "    _ = .{};",
            "}",
            'test "phase3 export shim reuses the shared boundary-header compatibility rules" {',
            "    const canonical = header(0);",
            "    const future_compatible = compatibleHeader(header_size + 16, 0);",
            "    const accepted_canonical = acceptHeader(canonical).?;",
            "    const accepted_future = acceptHeader(future_compatible).?;",
            "    _ = accepted_canonical;",
            "    _ = accepted_future;",
            "}",
            'test "phase3 export shim relays compatibility through explicit status packets" {',
            "    _ = .{};",
            "}",
            "",
        )
    )


def uapi_version_text() -> str:
    return "\n".join(
        (
            "pub const Compatibility = enum {",
            "    canonical,",
            "    future_compatible,",
            "};",
            "pub const AcceptedHeader = struct {",
            "    compatibility: Compatibility,",
            "    canonical: Header,",
            "};",
            "pub fn canonicalHeader(flags: u16) Header {",
            "    _ = flags;",
            "    return undefined;",
            "}",
            "pub fn boundaryHeader(flags: u16) Header {",
            "    return canonicalHeader(flags);",
            "}",
            "pub fn compatibleHeader(size: u32, flags: u16) Header {",
            "    _ = size;",
            "    _ = flags;",
            "    return undefined;",
            "}",
            "pub fn acceptHeader(header: Header) ?AcceptedHeader {",
            "    const mode = compatibility(header) orelse return null;",
            "    _ = mode;",
            "    return undefined;",
            "}",
            "pub fn canonicalizeHeader(header: Header) ?Header {",
            "    return (acceptHeader(header) orelse return null).canonical;",
            "}",
            'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {',
            "    const canonical = canonicalHeader(0);",
            "    const future_compatible = compatibleHeader(32, 0);",
            "    const accepted_canonical = acceptHeader(canonical).?;",
            "    const accepted_future = acceptHeader(future_compatible).?;",
            "    _ = accepted_canonical;",
            "    _ = accepted_future;",
            "}",
            'test "phase3 uapi canonicalizes compatible headers without widening the boundary" {',
            "    const future_compatible = compatibleHeader(32, 0);",
            "    const accepted = acceptHeader(future_compatible).?;",
            "    _ = accepted;",
            "}",
            "",
        )
    )


def linux_header_text() -> str:
    return "\n".join(
        (
            "#include <zigux/abi.h>",
            "static inline struct zigux_export_status zigux_status_ok(",
            "    zigux_u16 facility)",
            "{",
            "    return (struct zigux_export_status){ .facility = facility };",
            "}",
            "static inline struct zigux_export_status zigux_status_err(",
            "    zigux_s32 code, zigux_u16 facility)",
            "{",
            "    return (struct zigux_export_status){ .code = code, .facility = facility };",
            "}",
            "",
        )
    )


def abi_header_text() -> str:
    return "\n".join(
        (
            "#define ZIGUX_ABI_VERSION 1U",
            "#define ZIGUX_STATUS_FLAG_ERROR 1U",
            "struct zigux_boundary_header {",
            "    unsigned int size;",
            "};",
            "struct zigux_export_status {",
            "    int code;",
            "};",
            "",
        )
    )


def export_uapi_layout_text() -> str:
    return "\n".join(
        (
            'const std = @import("std");',
            'const abi = @import("abi_bindings");',
            'const export_shim = @import("export_shim");',
            'const uapi_version = @import("uapi_version");',
            "",
            'test "phase3 export shim and uapi keep canonical boundary layout" {',
            '    const header: export_shim.Header = export_shim.header(0x55);',
            '    const uapi_header: uapi_version.Header = uapi_version.boundaryHeader(0x55);',
            '    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x55);',
            '    const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);',
            '    const uapi_undersized = uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x55);',
            '    const accepted_canonical = export_shim.acceptHeader(header).?;',
            '    const accepted_future = export_shim.acceptHeader(future_compatible).?;',
            '    const uapi_accepted_canonical = uapi_version.acceptHeader(uapi_header).?;',
            '    const uapi_accepted_future = uapi_version.acceptHeader(future_compatible).?;',
            '    try std.testing.expectEqual(header, uapi_header);',
            '    try std.testing.expectEqual(export_shim.HeaderCompatibility.canonical, accepted_canonical.compatibility);',
            '    try std.testing.expectEqual(header, accepted_future.canonical);',
            '    try std.testing.expectEqual(uapi_header, uapi_accepted_future.canonical);',
            '    try std.testing.expectEqual(undersized, uapi_undersized);',
            '    try std.testing.expect(export_shim.headerCompatibility(undersized) == null);',
            '    try std.testing.expect(uapi_version.compatibility(uapi_undersized) == null);',
            '    try std.testing.expect(export_shim.acceptHeader(undersized) == null);',
            '    try std.testing.expect(uapi_version.acceptHeader(uapi_undersized) == null);',
            '    try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);',
            '    try std.testing.expect(uapi_version.canonicalizeHeader(uapi_undersized) == null);',
            '    const version_mismatch = export_shim.versionedHeader(export_shim.header_size, export_shim.abi_version + 1, 0x55);',
            '    try std.testing.expect(export_shim.headerCompatibility(version_mismatch) == null);',
            '    try std.testing.expect(uapi_version.compatibility(version_mismatch) == null);',
            '    try std.testing.expect(export_shim.acceptHeader(version_mismatch) == null);',
            '    try std.testing.expect(uapi_version.acceptHeader(version_mismatch) == null);',
            '    _ = abi;',
            '}',
            "",
            'test "phase3 export shim keeps compatibility status relays explicit" {',
            '    const canonical = export_shim.header(0x55);',
            '    const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);',
            '    _ = canonical_status;',
            '    _ = .{};',
            '}',
            "",
        )
    )


def baseline_survey(root: Path) -> str:
    return "\n".join(
        (
            "# Phase 3 Export Shim and UAPI Boundary Survey",
            "",
            "This note records the current export-shim and starter UAPI boundary that still sits inside the bounded Phase 3 ABI substrate packet on live `master`.",
            "",
            "## Status",
            "",
            "- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
            "- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=shared-abi-slice-owns-linux-header-governance-export-uapi-packet-owns-starter-boundary-wording-only`",
            "- `PHASE3_C_HEADER_GROWTH_RULE=shared-abi-resurvey-for-linux-header-growth-packet-local-resurvey-for-starter-entry-point-growth`",
            "- `PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-layout-replay-plus-shared-review-surface-refresh`",
            "- `PHASE3_LAYOUT_REPLAY_OWNERSHIP=export-uapi-packet-owns-focused-starter-boundary-layout-replay`",
            f"- `PHASE3_EXPORT_SHIM_PATH={EXPORT_SHIM_REL}`",
            f"- `PHASE3_EXPORT_SHIM_BLOB_SHA={blob_sha(root / EXPORT_SHIM_REL)}`",
            f"- `PHASE3_UAPI_VERSION_PATH={UAPI_VERSION_REL}`",
            f"- `PHASE3_UAPI_VERSION_BLOB_SHA={blob_sha(root / UAPI_VERSION_REL)}`",
            f"- `PHASE3_LINUX_HEADER_PATH={LINUX_HEADER_REL}`",
            f"- `PHASE3_LINUX_HEADER_BLOB_SHA={blob_sha(root / LINUX_HEADER_REL)}`",
            f"- `PHASE3_ABI_HEADER_PATH={ABI_HEADER_REL}`",
            f"- `PHASE3_ABI_HEADER_BLOB_SHA={blob_sha(root / ABI_HEADER_REL)}`",
            f"- `PHASE3_EXPORT_UAPI_LAYOUT_PATH={EXPORT_UAPI_LAYOUT_REL}`",
            f"- `PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA={blob_sha(root / EXPORT_UAPI_LAYOUT_REL)}`",
            "",
            "## Scope",
            "",
            "This survey stays packet-local to the shipped export-shim and starter UAPI boundary. It does not claim broader header governance, generated bindings growth, or new helper families outside the bounded Phase 3 ABI packet.",
            "",
        )
    )


def build_valid_workspace(root: Path) -> None:
    _write(root / EXPORT_SHIM_REL, export_shim_text())
    _write(root / UAPI_VERSION_REL, uapi_version_text())
    _write(root / LINUX_HEADER_REL, linux_header_text())
    _write(root / ABI_HEADER_REL, abi_header_text())
    _write(root / BUILD_FILE_REL, "// build step placeholder\n")
    _write(root / EXPORT_UAPI_LAYOUT_REL, export_uapi_layout_text())
    _write(root / LINUX_HEADER_GOVERNANCE_REL, "# Phase 3 Linux zigux.h Header Governance\n")
    _write(root / VALIDATOR_REL, "# self-reference\n")
    _write(root / SURVEY_REL, baseline_survey(root))
    _write(
        root / DOCS_ROOT_REL,
        "\n".join(
            (
                "# Zigux Documentation",
                "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `Documentation/zigux/phase3-export-uapi-boundary-survey.md` - `Documentation/zigux/phase3-linux-zigux-header-governance.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/check-phase3-policy-byte-guards.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py` - `scripts/zigux/survey-phase3-abi-constant-parity.py` - `scripts/zigux/check-phase3-catalog-selftest.py` - `scripts/zigux/check-phase3-readme-tooling-inventory.py` - `scripts/zigux/check-phase3-abi-dump-gate.py` - `scripts/zigux/check-phase3-selftest-surface.py` - `scripts/zigux/phase3_catalog.py` - `scripts/zigux/phase3_check_lib.py` - `scripts/zigux/generate-phase3-check-wrappers.py` - `scripts/zigux/run-phase3-checks.py` - `scripts/zigux/validate_phase3_selftest.py` - `zigux/tests/README.md` - `zigux/Makefile` - `python3 scripts/zigux/validate-phase3.py`, `python3 scripts/zigux/validate-phase3.py --slug abi`, `python3 scripts/zigux/run-phase3-checks.py --slug abi`, `python3 scripts/zigux/phase3_catalog.py --audit-doc-sync`, `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-validate`, and `make -C zigux phase3` now keep the current ABI substrate reviewable through the shared `abi` slice, the policy-and-unsafe survey, the dedicated policy-byte guard, the low-level-wrapper survey, the export/UAPI boundary survey, the dedicated Linux `zigux.h` header-governance note, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.",
                "- the export/UAPI boundary survey, the dedicated Linux `zigux.h` header-governance note, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.",
                "",
            )
        ),
    )
    _write(
        root / SCRIPTS_README_REL,
        "\n".join(
            (
                "# scripts/zigux",
                "- `validate-phase3-export-uapi-survey.py`",
                "- `validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `include/linux/zigux.h`, `include/zigux/abi.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and the workflow hooks that rerun that same survey surface.",
                "",
            )
        ),
    )
    _write(
        root / WORKFLOW_REL,
        "\n".join(
            (
                "- name: Validate Phase 3 export/UAPI survey",
                "  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
                "- name: Self-test Phase 3 export/UAPI survey",
                "  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
                "",
            )
        ),
    )
    _write(
        root / ABI_MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 3",
                "status": "active",
                "slice": "abi-substrate-skeleton",
                "file_count": len(MANIFEST_REQUIRED_FILES),
                "files": list(MANIFEST_REQUIRED_FILES),
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        baseline = validate(root)
        assert baseline == [], baseline

        survey_path = root / SURVEY_REL
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
                "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [], validate(root)
        build_valid_workspace(root)

        survey_path = root / SURVEY_REL
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
                "`PHASE3_SURVEY_PROVENANCE_MISSING=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            "missing_survey_provenance:`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`|`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`"
        ]
        build_valid_workspace(root)

        survey_path = root / SURVEY_REL
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "`PHASE3_C_HEADER_GROWTH_RULE=shared-abi-resurvey-for-linux-header-growth-packet-local-resurvey-for-starter-entry-point-growth`",
                "`PHASE3_C_HEADER_GROWTH_RULE_MISSING=shared-abi-resurvey-for-linux-header-growth-packet-local-resurvey-for-starter-entry-point-growth`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            "missing_survey_marker:`PHASE3_C_HEADER_GROWTH_RULE=shared-abi-resurvey-for-linux-header-growth-packet-local-resurvey-for-starter-entry-point-growth`"
        ]
        build_valid_workspace(root)

        _write(root / EXPORT_SHIM_REL, export_shim_text() + "// drift\n")
        issues = validate(root)
        assert len(issues) == 1 and issues[0].startswith("stale_survey_blob:PHASE3_EXPORT_SHIM_BLOB_SHA:"), issues
        build_valid_workspace(root)

        _write(
            root / EXPORT_UAPI_LAYOUT_REL,
            export_uapi_layout_text().replace('    const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);\n', "", 1),
        )
        assert validate(root) == [
            "stale_survey_blob:PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA:d869631861348c7cd47fe8cb0ba025d06ef63096!=2c288abdb67761244d7367aed915ec78d476af60",
            'missing_marker:zigux/tests/phase3_export_uapi_layout.zig:const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);',
        ]
        build_valid_workspace(root)

        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
                "run: python3 scripts/zigux/validate-phase3-export-uapi-survey-missing.py --self-test",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            "missing_workflow_marker:run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"
        ]
        build_valid_workspace(root)

        docs_root_path = root / DOCS_ROOT_REL
        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(
                " - `scripts/zigux/check-phase3-policy-byte-guards.py`",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            f"missing_docs_root_marker:{DOCS_ROOT_REQUIRED_MARKERS[0]}"
        ]
        build_valid_workspace(root)

        manifest_path = root / ABI_MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != EXPORT_UAPI_LAYOUT_REL]
        manifest["file_count"] = len(manifest["files"])
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        assert validate(root) == [f"manifest_missing_required_file:{EXPORT_UAPI_LAYOUT_REL}"]
        build_valid_workspace(root)

        governance_path = root / LINUX_HEADER_GOVERNANCE_REL
        governance_path.unlink()
        assert validate(root) == [f"missing_file:{LINUX_HEADER_GOVERNANCE_REL}"]
        build_valid_workspace(root)

        manifest_path = root / ABI_MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != LINUX_HEADER_GOVERNANCE_REL]
        manifest["file_count"] = len(manifest["files"])
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        assert validate(root) == [f"manifest_missing_required_file:{LINUX_HEADER_GOVERNANCE_REL}"]
        build_valid_workspace(root)

        survey_path = root / SURVEY_REL
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                f"`PHASE3_LINUX_HEADER_PATH={LINUX_HEADER_REL}`",
                "`PHASE3_LINUX_HEADER_PATH_MISSING=include/linux/zigux.h`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [f"missing_survey_marker:`PHASE3_LINUX_HEADER_PATH={LINUX_HEADER_REL}`"]

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the shipped Phase 3 export-shim and UAPI boundary packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(repo_root)
    if issues:
        print("PHASE3_EXPORT_UAPI_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_EXPORT_UAPI_SURVEY=pass")
    print(f"PHASE3_EXPORT_UAPI_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
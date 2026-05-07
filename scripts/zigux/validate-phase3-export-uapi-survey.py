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
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
)

SURVEY_EXACT_MARKERS = (
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`",
    "`PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`",
    "`PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`",
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
)

REQUIRED_MARKERS = {
    EXPORT_SHIM_REL: (
        "pub const abi_version: u16 = uapi_version.abi_version;",
        "pub const header_size: u32 = uapi_version.header_size;",
        "pub const HeaderCompatibility = uapi_version.Compatibility;",
        "pub fn versionedHeader(size: u32, version: u16, flags: u16) abi.BoundaryHeader {",
        "return uapi_version.versionedHeader(size, version, flags);",
        "pub fn canonicalHeader(flags: u16) abi.BoundaryHeader {",
        "return uapi_version.canonicalHeader(flags);",
        "pub fn boundaryHeader(flags: u16) abi.BoundaryHeader {",
        "return uapi_version.boundaryHeader(flags);",
        "pub fn compatibleHeader(size: u32, flags: u16) abi.BoundaryHeader {",
        "return uapi_version.compatibleHeader(size, flags);",
        "pub fn header(flags: u16) abi.BoundaryHeader {",
        "return canonicalHeader(flags);",
        "pub fn isCurrentAbiVersion(version: u16) bool {",
        "return uapi_version.isCurrentAbiVersion(version);",
        "pub fn isCompatibleSize(size: u32) bool {",
        "return uapi_version.isCompatibleSize(size);",
        "pub fn isCanonicalSize(size: u32) bool {",
        "return uapi_version.isCanonicalSize(size);",
        "pub fn headerCompatibility(header_value: abi.BoundaryHeader) ?HeaderCompatibility {",
        "return uapi_version.compatibility(header_value);",
        "pub fn isCompatibleHeader(header_value: abi.BoundaryHeader) bool {",
        "return uapi_version.isCompatible(header_value);",
        "pub fn isCanonicalHeader(header_value: abi.BoundaryHeader) bool {",
        "return uapi_version.isCanonical(header_value);",
        "pub fn canonicalizeHeader(header_value: abi.BoundaryHeader) ?abi.BoundaryHeader {",
        "return uapi_version.canonicalizeHeader(header_value);",
        "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {",
        "test \"phase3 export shim keeps failure encoding explicit\" {",
        "test \"phase3 export shim reuses the shared boundary-header compatibility rules\" {",
    ),
    UAPI_VERSION_REL: (
        "pub const Compatibility = enum {",
        "canonical,",
        "future_compatible,",
        "pub fn canonicalHeader(flags: u16) Header {",
        "pub fn boundaryHeader(flags: u16) Header {",
        "return canonicalHeader(flags);",
        "pub fn compatibleHeader(size: u32, flags: u16) Header {",
        "pub fn canonicalizeHeader(header: Header) ?Header {",
        "test \"phase3 uapi boundary header distinguishes canonical and future-compatible shapes\" {",
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
        "const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x55);",
        "const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);",
        "const uapi_undersized = uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x55);",
        "try std.testing.expectEqual(header, uapi_header);",
        "try std.testing.expectEqual(undersized, uapi_undersized);",
        "try std.testing.expect(export_shim.headerCompatibility(undersized) == null);",
        "try std.testing.expect(uapi_version.compatibility(uapi_undersized) == null);",
        "try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);",
        "try std.testing.expect(uapi_version.canonicalizeHeader(uapi_undersized) == null);",
        "try std.testing.expect(export_shim.headerCompatibility(version_mismatch) == null);",
        "try std.testing.expect(uapi_version.compatibility(version_mismatch) == null);",
    ),
}

DOCS_ROOT_REQUIRED_MARKERS = (
    "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`",
    "the export/UAPI boundary survey, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.",
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


def require_exact_line_count(
    issues: list[str],
    text: str,
    prefix: str,
    line: str,
    *,
    expected_count: int = 1,
) -> None:
    count = normalized_lines(text).count(line)
    if count == expected_count:
        return
    if count == 0:
        issues.append(f"missing_{prefix}:{line}")
        return
    issues.append(f"duplicate_{prefix}:{count}:{line}")


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
        path = root / rel
        if not path.exists():
            issues.append(f"missing_file:{rel}")

    survey_path = root / SURVEY_REL
    if not survey_path.exists():
        return issues
    survey = survey_path.read_text(encoding="utf-8")

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


def run_self_test() -> int:
    export_shim_text = "\n".join(
        (
            "pub const abi_version: u16 = uapi_version.abi_version;",
            "pub const header_size: u32 = uapi_version.header_size;",
            "pub const HeaderCompatibility = uapi_version.Compatibility;",
            "pub fn versionedHeader(size: u32, version: u16, flags: u16) abi.BoundaryHeader {",
            "    return uapi_version.versionedHeader(size, version, flags);",
            "}",
            "pub fn canonicalHeader(flags: u16) abi.BoundaryHeader {",
            "    return uapi_version.canonicalHeader(flags);",
            "}",
            "pub fn boundaryHeader(flags: u16) abi.BoundaryHeader {",
            "    return uapi_version.boundaryHeader(flags);",
            "}",
            "pub fn compatibleHeader(size: u32, flags: u16) abi.BoundaryHeader {",
            "    return uapi_version.compatibleHeader(size, flags);",
            "}",
            "pub fn header(flags: u16) abi.BoundaryHeader {",
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
            "pub fn headerCompatibility(header_value: abi.BoundaryHeader) ?HeaderCompatibility {",
            "    return uapi_version.compatibility(header_value);",
            "}",
            "pub fn isCompatibleHeader(header_value: abi.BoundaryHeader) bool {",
            "    return uapi_version.isCompatible(header_value);",
            "}",
            "pub fn isCanonicalHeader(header_value: abi.BoundaryHeader) bool {",
            "    return uapi_version.isCanonical(header_value);",
            "}",
            "pub fn canonicalizeHeader(header_value: abi.BoundaryHeader) ?abi.BoundaryHeader {",
            "    return uapi_version.canonicalizeHeader(header_value);",
            "}",
            "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {",
            "    return status;",
            "}",
            'test "phase3 export shim keeps failure encoding explicit" {',
            "    _ = .{};",
            "}",
            'test "phase3 export shim reuses the shared boundary-header compatibility rules" {',
            "    _ = .{};",
            "}",
            "",
        )
    )
    uapi_version_text = "\n".join(
        (
            "pub const Compatibility = enum {",
            "    canonical,",
            "    future_compatible,",
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
            "pub fn canonicalizeHeader(header: Header) ?Header {",
            "    return header;",
            "}",
            'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {',
            "    _ = .{};",
            "}",
            "",
        )
    )
    linux_header_text = "\n".join(
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
    abi_header_text = "\n".join(
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
    export_uapi_layout_text = "\n".join(
        (
            'const std = @import("std");',
            'const abi = @import("abi_bindings");',
            'const export_shim = @import("export_shim");',
            'const uapi_version = @import("uapi_version");',
            "",
            'test "phase3 export shim and uapi keep canonical boundary layout" {',
            '    const header = export_shim.header(0x55);',
            '    const uapi_header = uapi_version.boundaryHeader(0x55);',
            '    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x55);',
            '    const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);',
            '    const uapi_undersized = uapi_version.compatibleHeader(uapi_version.header_size - 1, 0x55);',
            '    const version_mismatch = export_shim.versionedHeader(',
            '        export_shim.header_size,',
            '        export_shim.abi_version + 1,',
            '        0x55,',
            '    );',
            "",
            '    try std.testing.expectEqual(header, uapi_header);',
            '    try std.testing.expectEqual(undersized, uapi_undersized);',
            '    try std.testing.expect(export_shim.headerCompatibility(undersized) == null);',
            '    try std.testing.expect(uapi_version.compatibility(uapi_undersized) == null);',
            '    try std.testing.expect(export_shim.canonicalizeHeader(undersized) == null);',
            '    try std.testing.expect(uapi_version.canonicalizeHeader(uapi_undersized) == null);',
            '    try std.testing.expect(export_shim.headerCompatibility(version_mismatch) == null);',
            '    try std.testing.expect(uapi_version.compatibility(version_mismatch) == null);',
            '    _ = abi;',
            '    _ = future_compatible;',
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
                "- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`",
                "- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`",
                "- `PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`",
                f"- `PHASE3_EXPORT_SHIM_PATH={EXPORT_SHIM_REL}`",
                f"- `PHASE3_EXPORT_SHIM_BLOB_SHA={blob_sha(root / EXPORT_SHIM_REL)}`",
                f"- `PHASE3_UAPI_VERSION_PATH={UAPI_VERSION_REL}`",
                f"- `PHASE3_UAPI_VERSION_BLOB_SHA={blob_sha(root / UAPI_VERSION_REL)}`",
                f"- `PHASE3_LINUX_HEADER_PATH={LINUX_HEADER_REL}`",
                f"- `PHASE3_LINUX_HEADER_BLOB_SHA={blob_sha(root / LINUX_HEADER_REL)}`",
                f"- `PHASE3_ABI_HEADER_PATH={ABI_HEADER_REL}`",
                f"- `PHASE3_ABI_HEADER_BLOB_SHA={blob_sha(root / ABI_HEADER_REL)}`",
                f"- `PHASE3_EXPORT_UAPI_LAYOUT_PATH={EXPORT_UAPI_LAYOUT_REL}`",
                "",
                "## Live Boundary",
                "",
                "The blob markers above are the authoritative packet-local evidence for the currently shipped export shim, starter UAPI helper, Linux-facing aggregation header, canonical ABI header, and focused layout replay in this connector-only run.",
                "",
                "- `zigux/kernel/export_shim.zig` keeps the starter export boundary narrow by relaying the shared boundary-header helpers from `zigux/uapi/version.zig` and by normalizing explicit success or errno-style export status values.",
                "- `zigux/uapi/version.zig` keeps the starter UAPI version contract reviewable through canonical versus future-compatible boundary-header helpers without widening into a broader UAPI packet.",
                "- `zigux/tests/phase3_export_uapi_layout.zig` keeps the focused layout replay explicit by pinning canonical boundary-header size, field offsets, compatibility, and canonicalization behavior across the export shim and starter UAPI helper.",
                "- `include/linux/zigux.h` remains the Linux-facing aggregation header for already-landed Phase 3 boundary helpers, including the explicit `zigux_status_ok()` and `zigux_status_err()` relay surface.",
                "- `include/zigux/abi.h` remains the canonical ABI layout source of truth for `struct zigux_boundary_header`, `struct zigux_export_status`, and the shared version and status flags those starter helpers depend on.",
                "",
                "## Scope",
                "",
                "This survey stays packet-local to the shipped export-shim and starter UAPI boundary. It does not claim broader header governance, generated bindings growth, or new helper families outside the bounded Phase 3 ABI packet.",
                "",
            )
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / SURVEY_REL, "placeholder\n")
        _write(
            root / DOCS_ROOT_REL,
            "\n".join(
                (
                    "# Zigux Documentation",
                    "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`",
                    "- the export/UAPI boundary survey, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.",
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
        _write(root / EXPORT_SHIM_REL, export_shim_text)
        _write(root / UAPI_VERSION_REL, uapi_version_text)
        _write(root / LINUX_HEADER_REL, linux_header_text)
        _write(root / ABI_HEADER_REL, abi_header_text)
        _write(root / BUILD_FILE_REL, '// build step placeholder\n')
        _write(root / EXPORT_UAPI_LAYOUT_REL, export_uapi_layout_text)
        _write(root / "scripts/zigux/validate-phase3-export-uapi-survey.py", "# self-reference\n")
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
        _write(root / SURVEY_REL, baseline_survey(root))

        baseline = validate(root)
        if baseline:
            raise SystemExit(f"phase3-export-uapi-self-test:baseline_failed:{baseline}")

        survey_path = root / SURVEY_REL
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "`PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`",
                "`PHASE3_C_HEADER_GROWTH_RULE_MISSING=explicit-resurvey-required-before-new-c-header-entry-points`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = [
            "missing_survey_marker:`PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`"
        ]
        if issues != expected:
            raise SystemExit(f"phase3-export-uapi-self-test:survey_growth_rule_guard_failed:{issues}")
        _write(root / SURVEY_REL, baseline_survey(root))

        _write(root / EXPORT_SHIM_REL, export_shim_text + "// drift\n")
        issues = validate(root)
        if len(issues) != 1 or not issues[0].startswith("stale_survey_blob:PHASE3_EXPORT_SHIM_BLOB_SHA:"):
            raise SystemExit(f"phase3-export-uapi-self-test:survey_blob_guard_failed:{issues}")
        _write(root / EXPORT_SHIM_REL, export_shim_text)

        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                f"`PHASE3_LINUX_HEADER_PATH={LINUX_HEADER_REL}`",
                "`PHASE3_LINUX_HEADER_PATH_MISSING=include/linux/zigux.h`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = [f"missing_survey_marker:`PHASE3_LINUX_HEADER_PATH={LINUX_HEADER_REL}`"]
        if issues != expected:
            raise SystemExit(f"phase3-export-uapi-self-test:survey_path_guard_failed:{issues}")
        _write(root / SURVEY_REL, baseline_survey(root))

        _write(
            root / EXPORT_UAPI_LAYOUT_REL,
            export_uapi_layout_text.replace('const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);\n', "", 1),
        )
        issues = validate(root)
        expected = [
            'missing_marker:zigux/tests/phase3_export_uapi_layout.zig:const undersized = export_shim.compatibleHeader(export_shim.header_size - 1, 0x55);'
        ]
        if issues != expected:
            raise SystemExit(f"phase3-export-uapi-self-test:replay_marker_guard_failed:{issues}")
        _write(root / EXPORT_UAPI_LAYOUT_REL, export_uapi_layout_text)

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
        issues = validate(root)
        expected = [
            "missing_workflow_marker:run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"
        ]
        if issues != expected:
            raise SystemExit(f"phase3-export-uapi-self-test:workflow_guard_failed:{issues}")
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

        manifest_path = root / ABI_MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != EXPORT_UAPI_LAYOUT_REL]
        manifest["file_count"] = len(manifest["files"])
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        issues = validate(root)
        expected = [f"manifest_missing_required_file:{EXPORT_UAPI_LAYOUT_REL}"]
        if issues != expected:
            raise SystemExit(f"phase3-export-uapi-self-test:manifest_required_file_guard_failed:{issues}")

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shipped Phase 3 export-shim and UAPI boundary packet."
    )
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

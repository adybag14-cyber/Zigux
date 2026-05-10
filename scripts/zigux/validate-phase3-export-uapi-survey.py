#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]

SURVEY_REL = "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
ABI_SLICE_REL = "Documentation/zigux/phase3-abi-slice.md"
DOCS_ROOT_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"
LINUX_HEADER_REL = "include/linux/zigux.h"
ABI_HEADER_REL = "include/zigux/abi.h"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
BUILD_FILE_REL = "zigux/tests/build.zig"
EXPORT_UAPI_TEST_REL = "zigux/tests/phase3_export_uapi.zig"
EXPORT_UAPI_BUILD_REL = "zigux/tests/phase3_export_uapi_build.zig"
EXPORT_UAPI_LAYOUT_REL = "zigux/tests/phase3_export_uapi_layout.zig"
EXPORT_UAPI_LAYOUT_BUILD_REL = "zigux/tests/phase3_export_uapi_layout_build.zig"
LINUX_HEADER_GOVERNANCE_REL = "Documentation/zigux/phase3-linux-zigux-header-governance.md"
VALIDATOR_REL = "scripts/zigux/validate-phase3-export-uapi-survey.py"

SELF_TEST_CASE_COUNT = 10

REQUIRED_FILES = (
    SURVEY_REL,
    ABI_SLICE_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    LINUX_HEADER_REL,
    ABI_HEADER_REL,
    ABI_MANIFEST_REL,
    BUILD_FILE_REL,
    EXPORT_UAPI_TEST_REL,
    EXPORT_UAPI_BUILD_REL,
    EXPORT_UAPI_LAYOUT_REL,
    EXPORT_UAPI_LAYOUT_BUILD_REL,
    LINUX_HEADER_GOVERNANCE_REL,
    VALIDATOR_REL,
    WORKFLOW_REL,
)

MANIFEST_REQUIRED_FILES = (
    SURVEY_REL,
    ABI_SLICE_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    LINUX_HEADER_REL,
    ABI_HEADER_REL,
    BUILD_FILE_REL,
    EXPORT_UAPI_TEST_REL,
    EXPORT_UAPI_BUILD_REL,
    EXPORT_UAPI_LAYOUT_REL,
    EXPORT_UAPI_LAYOUT_BUILD_REL,
    LINUX_HEADER_GOVERNANCE_REL,
    VALIDATOR_REL,
    WORKFLOW_REL,
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
    f"`PHASE3_EXPORT_UAPI_BEHAVIOR_PATH={EXPORT_UAPI_TEST_REL}`",
    f"`PHASE3_EXPORT_UAPI_BUILD_PATH={EXPORT_UAPI_BUILD_REL}`",
    f"`PHASE3_EXPORT_UAPI_LAYOUT_PATH={EXPORT_UAPI_LAYOUT_REL}`",
    f"`PHASE3_EXPORT_UAPI_LAYOUT_BUILD_PATH={EXPORT_UAPI_LAYOUT_BUILD_REL}`",
    f"`PHASE3_EXPORT_UAPI_VALIDATOR_PATH={VALIDATOR_REL}`",
)

SURVEY_BLOB_MARKERS = (
    ("PHASE3_EXPORT_SHIM_BLOB_SHA", EXPORT_SHIM_REL),
    ("PHASE3_UAPI_VERSION_BLOB_SHA", UAPI_VERSION_REL),
    ("PHASE3_LINUX_HEADER_BLOB_SHA", LINUX_HEADER_REL),
    ("PHASE3_ABI_HEADER_BLOB_SHA", ABI_HEADER_REL),
    ("PHASE3_EXPORT_UAPI_BEHAVIOR_BLOB_SHA", EXPORT_UAPI_TEST_REL),
    ("PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA", EXPORT_UAPI_BUILD_REL),
    ("PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA", EXPORT_UAPI_LAYOUT_REL),
    ("PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA", EXPORT_UAPI_LAYOUT_BUILD_REL),
    ("PHASE3_EXPORT_UAPI_VALIDATOR_BLOB_SHA", VALIDATOR_REL),
)

ABI_SLICE_MARKERS = (
    "`PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof`",
    "current boundary evidence therefore lives in this shared ABI slice plus the packet-local export/UAPI survey note, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, the focused `phase3_export_uapi_layout` replay, `include/linux/zigux.h`, `zigux/kernel/export_shim.zig`, and `zigux/uapi/version.zig`",
    "the current shared ABI packet also keeps the focused export/UAPI boundary replay explicit across `zigux/tests/phase3_export_uapi_layout.zig`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, and `Documentation/zigux/phase3-linux-zigux-header-governance.md` so the manifest-backed replay surface matches the shipped packet-local starter proof, including accepted-header canonicalization, requested-header evaluation, and compatibility-status relays",
)

HEADER_GOVERNANCE_MARKERS = (
    f"`PHASE3_ZIGUX_H_PATH={LINUX_HEADER_REL}`",
    f"`PHASE3_ZIGUX_H_SHARED_SLICE_NOTE={ABI_SLICE_REL}`",
    f"`PHASE3_ZIGUX_H_MANIFEST_PATH={ABI_MANIFEST_REL}`",
    "`PHASE3_ZIGUX_H_GROWTH_RULE=new top-level helper families may land in include/linux/zigux.h, and already-landed top-level review surfaces may be rehomed there, only when the same bounded change also lands packet-local proof and updates this note.`",
    "export/UAPI starter work may reference this header, but the dedicated export/UAPI survey still owns the narrower starter-boundary claims it proves directly",
)

REQUIRED_MARKERS = {
    EXPORT_SHIM_REL: (
        'pub const Header = uapi_version.Header;',
        'pub const abi_version: u16 = uapi_version.abi_version;',
        'pub const header_size: u32 = uapi_version.header_size;',
        'pub const HeaderCompatibility = uapi_version.Compatibility;',
        'pub const HeaderAcceptance = uapi_version.AcceptedHeader;',
        'pub const HeaderEvaluation = uapi_version.HeaderEvaluation;',
        'pub const CompatibilityDecision = struct {',
        'pub fn boundaryHeader(flags: u16) Header {',
        'return uapi_version.boundaryHeader(flags);',
        'pub fn evaluateHeader(',
        'const evaluation = uapi_version.evaluateHeader(header_value);',
        '.status = if (evaluation.isAccepted()) ok(facility) else errno(incompatible_code, facility),',
        'pub fn compatibilityStatus(',
        'return evaluateHeader(header_value, incompatible_code, facility).status;',
        'pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {',
        'flags = if (status.code < 0) abi.STATUS_FLAG_ERROR else 0,',
        'test "phase3 export shim reuses the shared boundary-header compatibility rules" {',
        'test "phase3 export shim relays compatibility through explicit status packets" {',
        'test "phase3 export shim evaluation keeps compatibility evidence and status together" {',
    ),
    UAPI_VERSION_REL: (
        'pub const Compatibility = enum {',
        'future_compatible,',
        'pub const AcceptedHeader = struct {',
        'pub const HeaderEvaluation = struct {',
        'pub fn boundaryHeader(flags: u16) Header {',
        'pub fn compatibleHeader(size: u32, flags: u16) Header {',
        'pub fn compatibility(header: Header) ?Compatibility {',
        'pub fn acceptHeader(header: Header) ?AcceptedHeader {',
        'pub fn canonicalizeHeader(header: Header) ?Header {',
        'pub fn evaluateHeader(header: Header) HeaderEvaluation {',
        'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {',
        'test "phase3 uapi canonicalizes compatible headers without widening the boundary" {',
        'test "phase3 uapi evaluation keeps requested boundary shape explicit" {',
    ),
    LINUX_HEADER_REL: (
        '#include <zigux/abi.h>',
        'static inline struct zigux_export_status zigux_status_ok(',
        'static inline struct zigux_export_status zigux_status_err(',
    ),
    ABI_HEADER_REL: (
        '#define ZIGUX_ABI_VERSION 1U',
        '#define ZIGUX_STATUS_FLAG_ERROR 1U',
        'struct zigux_boundary_header {',
        'struct zigux_export_status {',
    ),
    EXPORT_UAPI_TEST_REL: (
        'const export_shim = @import("export_shim");',
        'const uapi_version = @import("uapi_version");',
        'test "phase3 export shim and uapi share the bounded boundary-header contract" {',
        'const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x44);',
        'try std.testing.expectEqual(canonical, export_shim.canonicalizeHeader(future_compatible).?);',
        'try std.testing.expectEqual(canonical, uapi_version.canonicalizeHeader(future_compatible).?);',
        'test "phase3 export shim keeps compatibility-status relays explicit" {',
        'const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);',
        'try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), mismatch_status.flags);',
    ),
    EXPORT_UAPI_BUILD_REL: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
        'export_shim_module.addImport("uapi_version", uapi_version_module);',
        '.root_source_file = b.path("phase3_export_uapi.zig"),',
        'root_module.addImport("export_shim", export_shim_module);',
        'root_module.addImport("uapi_version", uapi_version_module);',
        'const test_step = b.step("test", "Run Phase 3 export/UAPI behavior tests");',
    ),
    EXPORT_UAPI_LAYOUT_REL: (
        'const export_shim = @import("export_shim");',
        'const uapi_version = @import("uapi_version");',
        'test "phase3 export shim and uapi keep canonical boundary layout" {',
        'const accepted_future = export_shim.acceptHeader(future_compatible).?;',
        'const uapi_accepted_future = uapi_version.acceptHeader(future_compatible).?;',
        'try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible).?);',
        'try std.testing.expectEqual(uapi_header, uapi_version.canonicalizeHeader(future_compatible).?);',
        'test "phase3 export shim keeps compatibility status relays explicit" {',
        'const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);',
        'test "phase3 export shim evaluation mirrors the uapi boundary classification" {',
        'const export_future = export_shim.evaluateHeader(future_compatible, -75, .helpers);',
        'const uapi_future = uapi_version.evaluateHeader(future_compatible);',
        'const export_mismatch = export_shim.evaluateHeader(version_mismatch, -71, .kernel);',
        'const uapi_mismatch = uapi_version.evaluateHeader(version_mismatch);',
    ),
    EXPORT_UAPI_LAYOUT_BUILD_REL: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../uapi/version.zig"),',
        'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
        'export_shim_module.addImport("uapi_version", uapi_version_module);',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'root_module.addImport("export_shim", export_shim_module);',
        'root_module.addImport("uapi_version", uapi_version_module);',
        'const test_step = b.step("test", "Run Phase 3 export/UAPI layout tests");',
    ),
}

DOCS_ROOT_MARKERS = (
    '`Documentation/zigux/phase3-export-uapi-boundary-survey.md`',
    '`Documentation/zigux/phase3-linux-zigux-header-governance.md`',
    '`scripts/zigux/validate-phase3-export-uapi-survey.py`',
    '`zig build phase3-test --build-file zigux/tests/build.zig`',
    '`make -C zigux phase3`',
)

SCRIPTS_README_MARKERS = (
    '`validate-phase3-export-uapi-survey.py`',
    '`validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `include/linux/zigux.h`, `include/zigux/abi.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and the workflow hooks that rerun that same survey surface.`',
)

WORKFLOW_MARKERS = (
    "- name: Validate Phase 3 export/UAPI survey",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "- name: Self-test Phase 3 export/UAPI survey",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def normalized_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()
        lines.append(line)
    return lines


def require_exact_line_count(issues: list[str], text: str, prefix: str, line: str) -> None:
    count = normalized_lines(text).count(line)
    if count == 1:
        return
    if count == 0:
        issues.append(f"missing_{prefix}:{line}")
    else:
        issues.append(f"duplicate_{prefix}:{count}:{line}")


def require_one_of_exact_lines(issues: list[str], text: str, prefix: str, lines: tuple[str, ...]) -> None:
    normalized = normalized_lines(text)
    total = sum(normalized.count(line) for line in lines)
    if total == 1:
        return
    if total == 0:
        issues.append(f"missing_{prefix}:{'|'.join(lines)}")
    else:
        issues.append(f"duplicate_{prefix}:{total}:{'|'.join(lines)}")


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


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
        blob_path = root / rel
        if not blob_path.exists():
            continue
        values = extract_backticked_values(survey, key)
        if not values:
            issues.append(f"missing_survey_marker:`{key}=<sha>`")
            continue
        if len(values) != 1:
            issues.append(f"duplicate_survey_marker:{len(values)}:`{key}=<sha>`")
            continue
        expected = blob_sha(blob_path)
        if values[0] != expected:
            issues.append(f"stale_survey_blob:{key}:{values[0]}!={expected}")

    abi_slice_path = root / ABI_SLICE_REL
    if abi_slice_path.exists():
        abi_slice = abi_slice_path.read_text(encoding="utf-8")
        for marker in ABI_SLICE_MARKERS:
            require_exact_line_count(issues, abi_slice, "abi_slice_marker", marker)

    governance_path = root / LINUX_HEADER_GOVERNANCE_REL
    if governance_path.exists():
        governance = governance_path.read_text(encoding="utf-8")
        for marker in HEADER_GOVERNANCE_MARKERS:
            require_exact_line_count(issues, governance, "governance_marker", marker)

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
        for marker in DOCS_ROOT_MARKERS:
            require_exact_line_count(issues, docs_root, "docs_root_marker", marker)

    scripts_readme_path = root / SCRIPTS_README_REL
    if scripts_readme_path.exists():
        scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        for marker in SCRIPTS_README_MARKERS:
            require_exact_line_count(issues, scripts_readme, "scripts_readme_marker", marker)

    workflow_path = root / WORKFLOW_REL
    if workflow_path.exists():
        workflow_lines = [line.strip() for line in workflow_path.read_text(encoding="utf-8").splitlines()]
        for marker in WORKFLOW_MARKERS:
            count = workflow_lines.count(marker)
            if count == 0:
                issues.append(f"missing_workflow_marker:{marker}")
            elif count != 1:
                issues.append(f"duplicate_workflow_marker:{count}:{marker}")

    return issues


def minimal_export_shim_text() -> str:
    return "\n".join(
        (
            'const abi = @import("abi_bindings");',
            'const uapi_version = @import("uapi_version");',
            'pub const Header = uapi_version.Header;',
            'pub const abi_version: u16 = uapi_version.abi_version;',
            'pub const header_size: u32 = uapi_version.header_size;',
            'pub const HeaderCompatibility = uapi_version.Compatibility;',
            'pub const HeaderAcceptance = uapi_version.AcceptedHeader;',
            'pub const HeaderEvaluation = uapi_version.HeaderEvaluation;',
            'pub const CompatibilityDecision = struct {',
            '    evaluation: HeaderEvaluation,',
            '    status: abi.ExportStatus,',
            '};',
            'pub fn boundaryHeader(flags: u16) Header {',
            '    return uapi_version.boundaryHeader(flags);',
            '}',
            'pub fn evaluateHeader(',
            '    header_value: Header,',
            '    incompatible_code: i32,',
            '    facility: abi.Facility,',
            ') CompatibilityDecision {',
            '    const evaluation = uapi_version.evaluateHeader(header_value);',
            '    return .{',
            '        .evaluation = evaluation,',
            '        .status = if (evaluation.isAccepted()) ok(facility) else errno(incompatible_code, facility),',
            '    };',
            '}',
            'pub fn compatibilityStatus(',
            '    header_value: Header,',
            '    incompatible_code: i32,',
            '    facility: abi.Facility,',
            ') abi.ExportStatus {',
            '    return evaluateHeader(header_value, incompatible_code, facility).status;',
            '}',
            'pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {',
            '    return .{',
            '        .code = status.code,',
            '        .facility = status.facility,',
            '        .flags = if (status.code < 0) abi.STATUS_FLAG_ERROR else 0,',
            '    };',
            '}',
            'test "phase3 export shim reuses the shared boundary-header compatibility rules" {',
            '    _ = .{};',
            '}',
            'test "phase3 export shim relays compatibility through explicit status packets" {',
            '    _ = .{};',
            '}',
            'test "phase3 export shim evaluation keeps compatibility evidence and status together" {',
            '    _ = .{};',
            '}',
            '',
        )
    )


def minimal_uapi_text() -> str:
    return "\n".join(
        (
            'pub const Header = extern struct {};',
            'pub const Compatibility = enum {',
            '    canonical,',
            '    future_compatible,',
            '};',
            'pub const AcceptedHeader = struct {',
            '    compatibility: Compatibility,',
            '    canonical: Header,',
            '};',
            'pub const HeaderEvaluation = struct {',
            '    requested: Header,',
            '    acceptance: ?AcceptedHeader,',
            '};',
            'pub fn boundaryHeader(flags: u16) Header { _ = flags; return undefined; }',
            'pub fn compatibleHeader(size: u32, flags: u16) Header { _ = size; _ = flags; return undefined; }',
            'pub fn compatibility(header: Header) ?Compatibility { _ = header; return null; }',
            'pub fn acceptHeader(header: Header) ?AcceptedHeader { _ = header; return null; }',
            'pub fn canonicalizeHeader(header: Header) ?Header { _ = header; return null; }',
            'pub fn evaluateHeader(header: Header) HeaderEvaluation { _ = header; return undefined; }',
            'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" { _ = .{}; }',
            'test "phase3 uapi canonicalizes compatible headers without widening the boundary" { _ = .{}; }',
            'test "phase3 uapi evaluation keeps requested boundary shape explicit" { _ = .{}; }',
            '',
        )
    )


def minimal_export_uapi_test_text() -> str:
    return "\n".join(
        (
            'const abi = @import("abi_bindings");',
            'const export_shim = @import("export_shim");',
            'const uapi_version = @import("uapi_version");',
            'test "phase3 export shim and uapi share the bounded boundary-header contract" {',
            '    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x44);',
            '    try std.testing.expectEqual(canonical, export_shim.canonicalizeHeader(future_compatible).?);',
            '    try std.testing.expectEqual(canonical, uapi_version.canonicalizeHeader(future_compatible).?);',
            '}',
            'test "phase3 export shim keeps compatibility-status relays explicit" {',
            '    const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);',
            '    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), mismatch_status.flags);',
            '}',
            '',
        )
    )


def minimal_export_uapi_build_text() -> str:
    return "\n".join(
        (
            '.root_source_file = b.path("../bindings/abi.zig"),',
            '.root_source_file = b.path("../uapi/version.zig"),',
            'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
            '.root_source_file = b.path("../kernel/export_shim.zig"),',
            'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
            'export_shim_module.addImport("uapi_version", uapi_version_module);',
            '.root_source_file = b.path("phase3_export_uapi.zig"),',
            'root_module.addImport("export_shim", export_shim_module);',
            'root_module.addImport("uapi_version", uapi_version_module);',
            'const test_step = b.step("test", "Run Phase 3 export/UAPI behavior tests");',
            '',
        )
    )


def minimal_layout_text() -> str:
    return "\n".join(
        (
            'const export_shim = @import("export_shim");',
            'const uapi_version = @import("uapi_version");',
            'test "phase3 export shim and uapi keep canonical boundary layout" {',
            '    const accepted_future = export_shim.acceptHeader(future_compatible).?;',
            '    const uapi_accepted_future = uapi_version.acceptHeader(future_compatible).?;',
            '    try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible).?);',
            '    try std.testing.expectEqual(uapi_header, uapi_version.canonicalizeHeader(future_compatible).?);',
            '}',
            'test "phase3 export shim keeps compatibility status relays explicit" {',
            '    const canonical_status = export_shim.compatibilityStatus(canonical, -22, .kernel);',
            '}',
            'test "phase3 export shim evaluation mirrors the uapi boundary classification" {',
            '    const export_future = export_shim.evaluateHeader(future_compatible, -75, .helpers);',
            '    const uapi_future = uapi_version.evaluateHeader(future_compatible);',
            '    const export_mismatch = export_shim.evaluateHeader(version_mismatch, -71, .kernel);',
            '    const uapi_mismatch = uapi_version.evaluateHeader(version_mismatch);',
            '}',
            '',
        )
    )


def minimal_export_uapi_layout_build_text() -> str:
    return "\n".join(
        (
            '.root_source_file = b.path("../bindings/abi.zig"),',
            '.root_source_file = b.path("../uapi/version.zig"),',
            'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
            '.root_source_file = b.path("../kernel/export_shim.zig"),',
            'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
            'export_shim_module.addImport("uapi_version", uapi_version_module);',
            '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
            'root_module.addImport("export_shim", export_shim_module);',
            'root_module.addImport("uapi_version", uapi_version_module);',
            'const test_step = b.step("test", "Run Phase 3 export/UAPI layout tests");',
            '',
        )
    )


def baseline_survey(root: Path) -> str:
    export_sha = blob_sha(root / EXPORT_SHIM_REL)
    uapi_sha = blob_sha(root / UAPI_VERSION_REL)
    linux_sha = blob_sha(root / LINUX_HEADER_REL)
    abi_sha = blob_sha(root / ABI_HEADER_REL)
    behavior_sha = blob_sha(root / EXPORT_UAPI_TEST_REL)
    build_sha = blob_sha(root / EXPORT_UAPI_BUILD_REL)
    layout_sha = blob_sha(root / EXPORT_UAPI_LAYOUT_REL)
    layout_build_sha = blob_sha(root / EXPORT_UAPI_LAYOUT_BUILD_REL)
    validator_sha = blob_sha(root / VALIDATOR_REL)
    return "\n".join(
        (
            "# Phase 3 Export Shim and UAPI Boundary Survey",
            "",
            "## Status",
            "",
            SURVEY_PROVENANCE_MARKERS[0],
            SURVEY_EXACT_MARKERS[0],
            SURVEY_EXACT_MARKERS[1],
            SURVEY_EXACT_MARKERS[2],
            SURVEY_EXACT_MARKERS[3],
            SURVEY_EXACT_MARKERS[4],
            f"`PHASE3_EXPORT_SHIM_BLOB_SHA={export_sha}`",
            SURVEY_EXACT_MARKERS[5],
            f"`PHASE3_UAPI_VERSION_BLOB_SHA={uapi_sha}`",
            SURVEY_EXACT_MARKERS[6],
            f"`PHASE3_LINUX_HEADER_BLOB_SHA={linux_sha}`",
            SURVEY_EXACT_MARKERS[7],
            f"`PHASE3_ABI_HEADER_BLOB_SHA={abi_sha}`",
            SURVEY_EXACT_MARKERS[8],
            f"`PHASE3_EXPORT_UAPI_BEHAVIOR_BLOB_SHA={behavior_sha}`",
            SURVEY_EXACT_MARKERS[9],
            f"`PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA={build_sha}`",
            SURVEY_EXACT_MARKERS[10],
            f"`PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA={layout_sha}`",
            SURVEY_EXACT_MARKERS[11],
            f"`PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA={layout_build_sha}`",
            SURVEY_EXACT_MARKERS[12],
            f"`PHASE3_EXPORT_UAPI_VALIDATOR_BLOB_SHA={validator_sha}`",
            "",
        )
    )


def build_valid_workspace(root: Path) -> None:
    _write(root / EXPORT_SHIM_REL, minimal_export_shim_text())
    _write(root / UAPI_VERSION_REL, minimal_uapi_text())
    _write(root / EXPORT_UAPI_TEST_REL, minimal_export_uapi_test_text())
    _write(root / EXPORT_UAPI_BUILD_REL, minimal_export_uapi_build_text())
    _write(root / EXPORT_UAPI_LAYOUT_REL, minimal_layout_text())
    _write(root / EXPORT_UAPI_LAYOUT_BUILD_REL, minimal_export_uapi_layout_build_text())
    _write(root / ABI_SLICE_REL, "# Phase 3 ABI Substrate Slice\n\n- " + ABI_SLICE_MARKERS[0] + "\n- " + ABI_SLICE_MARKERS[1] + "\n- " + ABI_SLICE_MARKERS[2] + "\n")
    _write(root / LINUX_HEADER_REL, "#include <zigux/abi.h>\nstatic inline struct zigux_export_status zigux_status_ok(\n    zigux_u16 facility) {}\nstatic inline struct zigux_export_status zigux_status_err(\n    zigux_s32 code, zigux_u16 facility) {}\n")
    _write(root / ABI_HEADER_REL, "#define ZIGUX_ABI_VERSION 1U\n#define ZIGUX_STATUS_FLAG_ERROR 1U\nstruct zigux_boundary_header {\n};\nstruct zigux_export_status {\n};\n")
    _write(root / BUILD_FILE_REL, "// build placeholder\n")
    _write(root / LINUX_HEADER_GOVERNANCE_REL, "# Phase 3 Linux zigux.h Header Governance\n- " + HEADER_GOVERNANCE_MARKERS[0] + "\n- " + HEADER_GOVERNANCE_MARKERS[1] + "\n- " + HEADER_GOVERNANCE_MARKERS[2] + "\n- " + HEADER_GOVERNANCE_MARKERS[3] + "\n- " + HEADER_GOVERNANCE_MARKERS[4] + "\n")
    _write(root / VALIDATOR_REL, Path(__file__).read_text(encoding="utf-8"))
    _write(root / DOCS_ROOT_REL, "# docs root\n- " + DOCS_ROOT_MARKERS[0] + "\n- " + DOCS_ROOT_MARKERS[1] + "\n- " + DOCS_ROOT_MARKERS[2] + "\n- " + DOCS_ROOT_MARKERS[3] + "\n- " + DOCS_ROOT_MARKERS[4] + "\n")
    _write(root / SCRIPTS_README_REL, "# scripts\n- " + SCRIPTS_README_MARKERS[0] + "\n- " + SCRIPTS_README_MARKERS[1] + "\n")
    _write(root / WORKFLOW_REL, "- name: Validate Phase 3 export/UAPI survey\n  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py\n- name: Self-test Phase 3 export/UAPI survey\n  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test\n")
    manifest_files = list(MANIFEST_REQUIRED_FILES)
    _write(
        root / ABI_MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 3",
                "status": "active",
                "slice": "abi-substrate-skeleton",
                "file_count": len(manifest_files),
                "files": manifest_files,
            },
            indent=2,
        )
        + "\n",
    )
    _write(root / SURVEY_REL, baseline_survey(root))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)

        assert validate(root) == []
        case_count += 1

        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"].remove(EXPORT_UAPI_TEST_REL)
        manifest["file_count"] = len(manifest["files"])
        _write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert f"manifest_missing_required_file:{EXPORT_UAPI_TEST_REL}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"].remove(DOCS_ROOT_REL)
        manifest["file_count"] = len(manifest["files"])
        _write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert f"manifest_missing_required_file:{DOCS_ROOT_REL}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"].remove(SCRIPTS_README_REL)
        manifest["file_count"] = len(manifest["files"])
        _write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert f"manifest_missing_required_file:{SCRIPTS_README_REL}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"].remove(WORKFLOW_REL)
        manifest["file_count"] = len(manifest["files"])
        _write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert f"manifest_missing_required_file:{WORKFLOW_REL}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        test_path = root / EXPORT_UAPI_TEST_REL
        test_text = test_path.read_text(encoding="utf-8").replace(
            'const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);',
            'const stripped = true;',
        )
        _write(test_path, test_text)
        issues = validate(root)
        assert (
            f'missing_marker:{EXPORT_UAPI_TEST_REL}:const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);'
            in issues
        ), issues
        build_valid_workspace(root)
        case_count += 1

        survey_text = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            SURVEY_EXACT_MARKERS[8],
            "",
        )
        _write(root / SURVEY_REL, survey_text)
        issues = validate(root)
        assert f"missing_survey_marker:{SURVEY_EXACT_MARKERS[8]}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        build_blob = blob_sha(root / EXPORT_UAPI_BUILD_REL)
        survey_text = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            f"`PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA={build_blob}`",
            "",
        )
        _write(root / SURVEY_REL, survey_text)
        issues = validate(root)
        assert "missing_survey_marker:`PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA=<sha>`" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        layout_build_blob = blob_sha(root / EXPORT_UAPI_LAYOUT_BUILD_REL)
        survey_text = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            f"`PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA={layout_build_blob}`",
            "`PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA=deadbeef`",
        )
        _write(root / SURVEY_REL, survey_text)
        issues = validate(root)
        assert (
            f"stale_survey_blob:PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA:deadbeef!={layout_build_blob}"
            in issues
        ), issues
        case_count += 1

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the shipped Phase 3 export/UAPI boundary packet.")
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

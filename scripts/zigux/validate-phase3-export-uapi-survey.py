#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
DOCS_ROOT_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    SURVEY_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "include/linux/zigux.h",
    "include/zigux/abi.h",
    WORKFLOW_REL,
)

REQUIRED_MARKERS = {
    SURVEY_REL: (
        "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-with-legacy-head-anchor`",
        "`PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`",
        "`PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`",
    ),
    "zigux/kernel/export_shim.zig": (
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
    "zigux/uapi/version.zig": (
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
    "include/linux/zigux.h": (
        "#include <zigux/abi.h>",
        "static inline struct zigux_export_status zigux_status_ok(",
        "static inline struct zigux_export_status zigux_status_err(",
    ),
    "include/zigux/abi.h": (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_STATUS_FLAG_ERROR 1U",
        "struct zigux_boundary_header {",
        "struct zigux_export_status {",
    ),
}

DOCS_ROOT_REQUIRED_MARKERS = (
    "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`",
    "the export/UAPI boundary survey, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.",
)

SCRIPTS_README_REQUIRED_MARKERS = (
    "`validate-phase3-export-uapi-survey.py`",
    "`validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, the canonical ABI headers, and the workflow hooks that rerun that same survey surface.",
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


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            issues.append(f"missing_file:{rel}")
            continue
        if rel in REQUIRED_MARKERS:
            text = path.read_text(encoding="utf-8")
            for marker in REQUIRED_MARKERS[rel]:
                if marker not in text:
                    issues.append(f"missing_marker:{rel}:{marker}")

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
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp_dir:
        root = Path(tmp_dir)
        _write(
            root / SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Export Shim and UAPI Boundary Survey",
                    "## Status",
                    "- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-with-legacy-head-anchor`",
                    "- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`",
                    "- `PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`",
                    "",
                )
            ),
        )
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
                    "- `validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, the canonical ABI headers, and the workflow hooks that rerun that same survey surface.",
                    "",
                )
            ),
        )
        _write(
            root / "zigux/kernel/export_shim.zig",
            "\n".join(
                (
                    "pub const abi_version: u16 = uapi_version.abi_version;",
                    "pub const header_size: u32 = uapi_version.header_size;",
                    "pub const HeaderCompatibility = uapi_version.Compatibility;",
                    "pub fn versionedHeader(size: u32, version: u16, flags: u16) abi.BoundaryHeader {",
                    "    _ = version;",
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
                    "test \"phase3 export shim keeps failure encoding explicit\" {",
                    "    _ = .{};",
                    "}",
                    "test \"phase3 export shim reuses the shared boundary-header compatibility rules\" {",
                    "    _ = .{};",
                    "}",
                    "",
                )
            ),
        )
        _write(
            root / "zigux/uapi/version.zig",
            "\n".join(
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
                    "test \"phase3 uapi boundary header distinguishes canonical and future-compatible shapes\" {",
                    "    _ = .{};",
                    "}",
                    "",
                )
            ),
        )
        _write(
            root / "include/linux/zigux.h",
            "\n".join(
                (
                    "#include <zigux/abi.h>",
                    "static inline struct zigux_export_status zigux_status_ok(zigux_u16 facility)",
                    "{",
                    "    return (struct zigux_export_status){ .facility = facility };",
                    "}",
                    "static inline struct zigux_export_status zigux_status_err(zigux_s32 code, zigux_u16 facility)",
                    "{",
                    "    return (struct zigux_export_status){ .code = code, .facility = facility };",
                    "}",
                    "",
                )
            ),
        )
        _write(
            root / "include/zigux/abi.h",
            "\n".join(
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
        expected = (
            "missing_marker:Documentation/zigux/phase3-export-uapi-boundary-survey.md:`PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`"
        )
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:survey_growth_rule_guard_failed:{issues}")

        _write(
            root / SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Export Shim and UAPI Boundary Survey",
                    "## Status",
                    "- `PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-with-legacy-head-anchor`",
                    "- `PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth`",
                    "- `PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points`",
                    "",
                )
            ),
        )

        docs_root_path = root / DOCS_ROOT_REL
        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(
                "the export/UAPI boundary survey, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone.\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = (
            "missing_docs_root_marker:the export/UAPI boundary survey, the ABI-bindings syntax guard, the catalog-backed validator-support packet, the selftest review surface, and the Linux-style replay route instead of leaving the active Phase 3 packet implicit across the scripts root, tests root, and helper tree alone."
        )
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:docs_root_missing_guard_failed:{issues}")

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

        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(
                "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`\n",
                "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`\n"
                "Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`\n",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = (
            "duplicate_docs_root_marker:2:Phase 3 notes - `Documentation/zigux/phase3-abi-slice.md` - `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` - `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md` - `scripts/zigux/validate-phase3.py` - `scripts/zigux/validate-phase3-policy-unsafe-survey.py` - `scripts/zigux/validate-phase3-low-level-wrapper-survey.py` - `scripts/zigux/validate-phase3-export-uapi-survey.py` - `scripts/zigux/validate-phase3-abi-bindings-syntax.py`"
        )
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:docs_root_duplicate_guard_failed:{issues}")

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

        scripts_readme_path = root / SCRIPTS_README_REL
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                "- `validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, the canonical ABI headers, and the workflow hooks that rerun that same survey surface.\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = (
            "missing_scripts_readme_marker:`validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, the canonical ABI headers, and the workflow hooks that rerun that same survey surface."
        )
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:scripts_readme_missing_guard_failed:{issues}")

        _write(
            root / SCRIPTS_README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "- `validate-phase3-export-uapi-survey.py`",
                    "- `validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, the canonical ABI headers, and the workflow hooks that rerun that same survey surface.",
                    "",
                )
            ),
        )

        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                "- `validate-phase3-export-uapi-survey.py`\n",
                "- `validate-phase3-export-uapi-survey.py`\n- `validate-phase3-export-uapi-survey.py`\n",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = "duplicate_scripts_readme_marker:2:`validate-phase3-export-uapi-survey.py`"
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:scripts_readme_duplicate_guard_failed:{issues}")

        _write(
            root / SCRIPTS_README_REL,
            "\n".join(
                (
                    "# scripts/zigux",
                    "- `validate-phase3-export-uapi-survey.py`",
                    "- `validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, the canonical ABI headers, and the workflow hooks that rerun that same survey surface.",
                    "",
                )
            ),
        )

        broken_root = root / "zigux/uapi/version.zig"
        broken_root.write_text(
            broken_root.read_text(encoding="utf-8").replace(
                "pub fn boundaryHeader(flags: u16) Header {",
                "pub fn boundaryHeaderMissing(flags: u16) Header {",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = "missing_marker:zigux/uapi/version.zig:pub fn boundaryHeader(flags: u16) Header {"
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:boundary_header_guard_failed:{issues}")

        _write(
            root / "zigux/uapi/version.zig",
            "\n".join(
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
                    "test \"phase3 uapi boundary header distinguishes canonical and future-compatible shapes\" {",
                    "    _ = .{};",
                    "}",
                    "",
                )
            ),
        )

        export_shim_path = root / "zigux/kernel/export_shim.zig"
        export_shim_path.write_text(
            export_shim_path.read_text(encoding="utf-8").replace(
                "pub fn canonicalizeHeader(header_value: abi.BoundaryHeader) ?abi.BoundaryHeader {",
                "pub fn canonicalizeHeaderMissing(header_value: abi.BoundaryHeader) ?abi.BoundaryHeader {",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        expected = (
            "missing_marker:zigux/kernel/export_shim.zig:pub fn canonicalizeHeader(header_value: abi.BoundaryHeader) ?abi.BoundaryHeader {"
        )
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:export_shim_guard_failed:{issues}")

        _write(
            root / "zigux/kernel/export_shim.zig",
            "\n".join(
                (
                    "pub const abi_version: u16 = uapi_version.abi_version;",
                    "pub const header_size: u32 = uapi_version.header_size;",
                    "pub const HeaderCompatibility = uapi_version.Compatibility;",
                    "pub fn versionedHeader(size: u32, version: u16, flags: u16) abi.BoundaryHeader {",
                    "    _ = version;",
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
                    "test \"phase3 export shim keeps failure encoding explicit\" {",
                    "    _ = .{};",
                    "}",
                    "test \"phase3 export shim reuses the shared boundary-header compatibility rules\" {",
                    "    _ = .{};",
                    "}",
                    "",
                )
            ),
        )

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
        expected = (
            "missing_workflow_marker:run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"
        )
        if issues != [expected]:
            raise SystemExit(f"phase3-export-uapi-self-test:workflow_guard_failed:{issues}")

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=9")
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
    print("PHASE3_EXPORT_UAPI_REQUIRED_FILE_COUNT=8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

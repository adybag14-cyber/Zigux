#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
DOCS_README_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"
UAPI_ROOT_REL = "zigux/uapi"
ABI_SLICE_REL = "Documentation/zigux/phase3-abi-slice.md"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
EXPORT_UAPI_TEST_REL = "zigux/tests/phase3_export_uapi.zig"
EXPORT_UAPI_LAYOUT_BUILD_REL = "zigux/tests/phase3_export_uapi_layout_build.zig"
EXPORT_UAPI_LAYOUT_TEST_REL = "zigux/tests/phase3_export_uapi_layout.zig"
LINUX_HEADER_REL = "include/linux/zigux.h"
ABI_HEADER_REL = "include/zigux/abi.h"
VALIDATE_PHASE3_CORE_REL = "scripts/zigux/validate_phase3_core.py"
HEX40 = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-with-legacy-head-anchor",
    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
    "PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_EXPORT_SHIM_STATUS=normalize-and-compatibility-helpers-landed",
    "PHASE3_C_HEADER_PATH=include/linux/zigux.h",
    "PHASE3_C_HEADER_STATUS=shared-abi-relay-status-and-interop-helper-aggregation-landed",
    "PHASE3_C_HEADER_BOUNDARY_OWNERSHIP=export-uapi-packet-owns-boundary-wording-helper-slices-own-semantic-growth",
    "PHASE3_C_HEADER_GROWTH_RULE=explicit-resurvey-required-before-new-c-header-entry-points",
    "PHASE3_UAPI_ROOT=zigux/uapi",
    "PHASE3_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_UAPI_STATUS=version-header-and-compatibility-surface-landed",
    "PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig",
    "PHASE3_EXPORT_UAPI_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "PHASE3_ABI_BUILD_SMOKE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi --check-build-smoke",
    "PHASE3_ABI_BUILD_SMOKE_STATUS=shared-validator-replays-export-uapi-boundary-and-layout",
    "PHASE3_BOUNDARY_GAP=broader-curated-uapi-shims-still-deferred",
    "PHASE3_NEXT_BOUNDED_STEP=keep-boundary-header-surface-narrow-until-one-roadmap-backed-interop-slice-needs-another-curated-uapi-or-export-entry",
)

REQUIRED_SURVEY_SNIPPETS = (
    "zigux/tests/phase3_export_uapi_build.zig",
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "python3 scripts/zigux/validate-phase3.py --slug abi --check-build-smoke",
    "phase3-dump`, `phase3-low-level-wrappers-test`, `phase3-export-uapi-test`, `phase3-export-uapi-layout-test`, and `phase3-policy-unsafe-test`",
    "part of the shared ABI build-smoke proof rather than only a boundary-local survey gate",
    "named version and size predicates",
    "keep canonical-size header checks separate from broader future-compatible header acceptance",
    "last fully resurveyed shared-head anchor",
    "packet-local blob IDs are now the authoritative current boundary evidence",
    "The live repo already carries the C-facing boundary headers in `include/zigux/abi.h` and `include/linux/zigux.h`.",
    "compiles and runs a tiny C relay check against `include/linux/zigux.h`",
    "the C-facing `zigux_status_ok()` and `zigux_status_err()` helpers plus raw `zigux_boundary_header` field values still agree",
    "canonical boundary-header and export-status size and field-offset contract on its own focused layout replay",
    "phase3-export-uapi-layout-test",
)

REQUIRED_SURVEY_PATHS = (
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    ABI_SLICE_REL,
    ABI_HEADER_REL,
    LINUX_HEADER_REL,
    "zigux/tests/phase3_export_uapi_build.zig",
    EXPORT_UAPI_TEST_REL,
    EXPORT_UAPI_LAYOUT_BUILD_REL,
    EXPORT_UAPI_LAYOUT_TEST_REL,
    ABI_MANIFEST_REL,
    "scripts/zigux/validate-phase3.py",
    VALIDATE_PHASE3_CORE_REL,
)

REQUIRED_DOCS_README_SNIPPETS = (
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
    "`make -C zigux phase3-validate`",
)

REQUIRED_SCRIPTS_README_SNIPPETS = (
    "`validate-phase3-export-uapi-survey.py`",
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
)

REQUIRED_MAKEFILE_SNIPPETS = (
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
)

REQUIRED_EXPORT_SHIM_SNIPPETS = (
    "pub fn canonicalHeader(flags: u16) abi.BoundaryHeader {",
    "pub fn header(flags: u16) abi.BoundaryHeader {",
    "pub fn canonicalizeHeader(boundary_header: abi.BoundaryHeader) ?abi.BoundaryHeader {",
    "pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {",
    "pub fn isCanonicalHeader(boundary_header: abi.BoundaryHeader) bool {",
    "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {",
    "pub fn ok(facility: abi.Facility) abi.ExportStatus {",
    "pub fn errno(code: i32, facility: abi.Facility) abi.ExportStatus {",
    "pub fn isOk(status: abi.ExportStatus) bool {",
    'test "phase3 export shim separates canonical headers from broader compatibility"',
    'test "phase3 export shim canonicalizes compatible headers back to the current shape"',
)

REQUIRED_UAPI_VERSION_SNIPPETS = (
    "pub const Header = abi.BoundaryHeader;",
    "pub fn canonicalHeader(flags: u16) Header {",
    "pub fn boundaryHeader(flags: u16) Header {",
    "pub fn compatibleHeader(size: u32, flags: u16) Header {",
    "pub fn canonicalizeHeader(header: Header) ?Header {",
    "pub fn isCurrentAbiVersion(version: u16) bool {",
    "pub fn isCompatibleSize(size: u32) bool {",
    "pub fn isCanonicalSize(size: u32) bool {",
    "pub fn isCompatible(header: Header) bool {",
    "pub fn isCanonical(header: Header) bool {",
    'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes"',
    'test "phase3 uapi canonicalizes compatible headers without widening the boundary"',
)

REQUIRED_ABI_SLICE_SNIPPETS = (
    "export shim reality today: `zigux/kernel/export_shim.zig` stays a narrow explicit-status helper, and it now exposes a small local boundary-header surface that keeps exact canonical-size replay separate from broader future-compatible header acceptance without widening the public export namespace further",
    "UAPI reality today: `zigux/uapi/version.zig` now exposes the ABI version plus an explicit boundary-header constructor whose exact canonical-size replay stays separate from broader future-compatible compatibility, which is still bounded but makes the public boundary less ad hoc than a version constant alone",
)

REQUIRED_EXPORT_UAPI_TEST_SNIPPETS = (
    "try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));",
    "try std.testing.expect(export_shim.isCurrentAbiVersion(header.abi_version));",
    "try std.testing.expect(export_shim.isCanonicalSize(header.size));",
    "try std.testing.expect(export_shim.isCanonicalHeader(header));",
    "try std.testing.expect(uapi_version.isCanonical(header));",
    "try std.testing.expectEqual(header, export_shim.canonicalizeHeader(header).?);",
    "try std.testing.expectEqual(header, uapi_version.canonicalizeHeader(header).?);",
    "const undersized_header = export_shim.compatibleHeader(export_shim.header_size - 1, 0x11);",
    "try std.testing.expect(!uapi_version.isCompatibleSize(undersized_header.size));",
    "try std.testing.expect(!export_shim.isCurrentAbiVersion(mismatched_version_header.abi_version));",
    "const future_compatible_header = export_shim.compatibleHeader(export_shim.header_size + 8, 0x44);",
    "try std.testing.expect(uapi_version.isCompatibleSize(future_compatible_header.size));",
    "try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible_header));",
    "try std.testing.expect(!uapi_version.isCanonical(future_compatible_header));",
    "try std.testing.expect(export_shim.isCompatibleHeader(future_compatible_header));",
    "try std.testing.expect(uapi_version.isCompatible(future_compatible_header));",
    "try std.testing.expectEqual(header, export_shim.canonicalizeHeader(future_compatible_header).?);",
    "try std.testing.expectEqual(header, uapi_version.canonicalizeHeader(future_compatible_header).?);",
)

REQUIRED_EXPORT_UAPI_LAYOUT_BUILD_SNIPPETS = (
    '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
    'root_module.addImport("abi_bindings", abi_bindings_module);',
    'root_module.addImport("export_shim", export_shim_module);',
    'root_module.addImport("uapi_version", uapi_version_module);',
    '"phase3-export-uapi-layout-test",',
)

REQUIRED_EXPORT_UAPI_LAYOUT_TEST_SNIPPETS = (
    'test "phase3 export shim and uapi keep canonical boundary layout" {',
    'try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));',
    'try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));',
    'try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));',
    'try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));',
    'try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), @as(usize, header.size));',
    'try std.testing.expectEqual(header, uapi_header);',
    'try std.testing.expect(export_shim.isCanonicalHeader(header));',
    'try std.testing.expect(uapi_version.isCanonical(uapi_header));',
)

REQUIRED_VALIDATE_PHASE3_CORE_SNIPPETS = (
    "ABI_EXPORT_UAPI_BUILD_FILE_REL,",
    "ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL,",
    "ABI_EXPORT_UAPI_LAYOUT_TEST_REL,",
    '("phase3-export-uapi-test", ABI_EXPORT_UAPI_BUILD_FILE_REL),',
    '("phase3-export-uapi-layout-test", ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL),',
)

REQUIRED_UAPI_FILES = (
    UAPI_VERSION_REL,
)

REQUIRED_EXPORT_UAPI_MANIFEST_FILES = (
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    "zigux/tests/phase3_export_uapi_build.zig",
    EXPORT_UAPI_TEST_REL,
    EXPORT_UAPI_LAYOUT_BUILD_REL,
    EXPORT_UAPI_LAYOUT_TEST_REL,
    SURVEY_REL,
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
)

SURVEYED_PACKET_PATHS = (
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    LINUX_HEADER_REL,
    ABI_HEADER_REL,
    ABI_SLICE_REL,
    "zigux/tests/phase3_export_uapi_build.zig",
    EXPORT_UAPI_TEST_REL,
    EXPORT_UAPI_LAYOUT_BUILD_REL,
    EXPORT_UAPI_LAYOUT_TEST_REL,
    ABI_MANIFEST_REL,
)
SURVEYED_PACKET_BLOB_MARKERS = {
    "PHASE3_EXPORT_SHIM_BLOB_SHA": EXPORT_SHIM_REL,
    "PHASE3_UAPI_VERSION_BLOB_SHA": UAPI_VERSION_REL,
    "PHASE3_LINUX_HEADER_BLOB_SHA": LINUX_HEADER_REL,
    "PHASE3_ABI_HEADER_BLOB_SHA": ABI_HEADER_REL,
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA": ABI_SLICE_REL,
    "PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA": "zigux/tests/phase3_export_uapi_build.zig",
    "PHASE3_EXPORT_UAPI_TEST_BLOB_SHA": EXPORT_UAPI_TEST_REL,
    "PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA": EXPORT_UAPI_LAYOUT_BUILD_REL,
    "PHASE3_EXPORT_UAPI_LAYOUT_TEST_BLOB_SHA": EXPORT_UAPI_LAYOUT_TEST_REL,
    "PHASE3_ABI_MANIFEST_BLOB_SHA": ABI_MANIFEST_REL,
}
REQUIRED_SURVEY_BLOB_MARKERS = tuple(SURVEYED_PACKET_BLOB_MARKERS)
PLACEHOLDER_SHA = "0123456789abcdef0123456789abcdef01234567"
PLACEHOLDER_COMMIT = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _collect_relative_files(root: Path, rel: str) -> list[str]:
    base = root / rel
    if not base.exists():
        return []
    return sorted(path.relative_to(root).as_posix() for path in base.rglob("*") if path.is_file())


def _surveyed_commit_from_text(text: str) -> str | None:
    return _marker_value_from_text(text, "PHASE3_SURVEYED_COMMIT")


def _marker_value_from_text(text: str, marker: str) -> str | None:
    prefix = f"{marker}="
    for line in text.splitlines():
        stripped = line.strip().strip("- ").strip("`")
        if stripped.startswith(prefix):
            return stripped[len(prefix) :]
    return None


def _has_local_commit(root: Path, commit: str) -> bool:
    git_dir = root / ".git"
    if not git_dir.exists():
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _packet_drift_since_commit(root: Path, commit: str) -> list[str]:
    git_dir = root / ".git"
    if not git_dir.exists():
        return []
    if not _has_local_commit(root, commit):
        return [f"surveyed_commit_unavailable_locally:{commit}"]
    result = subprocess.run(
        ["git", "diff", "--name-only", commit, "HEAD", "--", *SURVEYED_PACKET_PATHS],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"surveyed_commit_diff_error:{commit}"]
    return [
        f"surveyed_commit_packet_drift:{rel}"
        for rel in result.stdout.splitlines()
        if rel.strip()
    ]


def _packet_drift_by_blob_sha(root: Path, survey: str) -> list[str]:
    git_dir = root / ".git"
    if not git_dir.exists():
        return []

    issues: list[str] = []
    saw_blob_marker = False
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        expected_blob = _marker_value_from_text(survey, marker)
        if expected_blob is None:
            continue
        saw_blob_marker = True
        path = root / rel
        if not path.exists():
            issues.append(f"current_blob_unavailable:{rel}")
            continue
        result = subprocess.run(
            ["git", "hash-object", "--no-filters", str(path)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            issues.append(f"current_blob_unavailable:{rel}")
            continue
        current_blob = result.stdout.strip()
        if not HEX40.fullmatch(current_blob):
            issues.append(f"invalid_current_blob_sha:{rel}:{current_blob}")
            continue
        if current_blob != expected_blob:
            issues.append(f"surveyed_blob_drift:{rel}")

    return issues if saw_blob_marker else []


def _blob_marker_lines() -> tuple[str, ...]:
    return tuple(f"{marker}={PLACEHOLDER_SHA}" for marker in REQUIRED_SURVEY_BLOB_MARKERS)


def _replace_blob_markers_with_head(root: Path, survey_path: Path) -> None:
    survey_text = survey_path.read_text(encoding="utf-8")
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        path = root / rel
        blob_sha = subprocess.run(
            ["git", "hash-object", "--no-filters", str(path)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        survey_text = survey_text.replace(f"{marker}={PLACEHOLDER_SHA}", f"{marker}={blob_sha}")
    survey_path.write_text(survey_text, encoding="utf-8")


def _validate_export_uapi_manifest(root: Path) -> list[str]:
    manifest_path = root / ABI_MANIFEST_REL
    if not manifest_path.exists():
        return []

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"export-uapi-manifest-json:{exc}"]

    issues: list[str] = []
    if manifest.get("phase") != "Phase 3":
        issues.append(f"export-uapi-manifest-phase:{manifest.get('phase')!r}")
    if manifest.get("slice") != "abi-substrate-skeleton":
        issues.append(f"export-uapi-manifest-slice:{manifest.get('slice')!r}")

    files = manifest.get("files")
    if not isinstance(files, list):
        return [*issues, "export-uapi-manifest-files-missing"]

    file_set = set(files)
    for rel in REQUIRED_EXPORT_UAPI_MANIFEST_FILES:
        if rel not in file_set:
            issues.append(f"export-uapi-manifest-missing:{rel}")

    file_count = manifest.get("file_count")
    if file_count != len(files):
        issues.append(f"export-uapi-manifest-file-count:{file_count!r}!={len(files)}")

    return issues


def validate_c_header_relay(root: Path) -> list[str]:
    linux_header = root / LINUX_HEADER_REL
    abi_header = root / ABI_HEADER_REL
    if not linux_header.exists() or not abi_header.exists():
        return []

    cc = os.environ.get("CC", "cc")
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_c_header_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        source_path = tmp_dir / "relay_check.c"
        binary_path = tmp_dir / "relay_check"
        source_path.write_text(
            "\n".join(
                (
                    "#include <linux/zigux.h>",
                    "int main(void)",
                    "{",
                    "    struct zigux_export_status ok = zigux_status_ok(ZIGUX_FACILITY_KERNEL);",
                    "    struct zigux_export_status err = zigux_status_err(-22, ZIGUX_FACILITY_HELPERS);",
                    "    struct zigux_boundary_header hdr = {",
                    "        .size = sizeof(struct zigux_boundary_header),",
                    "        .abi_version = ZIGUX_ABI_VERSION,",
                    "        .flags = 0x44,",
                    "    };",
                    "    if (ok.code != 0 || ok.facility != ZIGUX_FACILITY_KERNEL || ok.flags != 0)",
                    "        return 10;",
                    "    if (err.code != -22 || err.facility != ZIGUX_FACILITY_HELPERS || (err.flags & ZIGUX_STATUS_FLAG_ERROR) == 0)",
                    "        return 11;",
                    "    if (hdr.size != sizeof(struct zigux_boundary_header) || hdr.abi_version != ZIGUX_ABI_VERSION || hdr.flags != 0x44)",
                    "        return 12;",
                    "    return 0;",
                    "}",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        compile_result = subprocess.run(
            [cc, "-std=c11", "-Wall", "-Werror", "-I", str(root / "include"), str(source_path), "-o", str(binary_path)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if compile_result.returncode != 0:
            tail = compile_result.stderr.strip().splitlines()
            detail = tail[-1] if tail else f"exit {compile_result.returncode}"
            return [f"c-header-relay-compile:{detail}"]
        run_result = subprocess.run(
            [str(binary_path)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if run_result.returncode != 0:
            detail = run_result.stderr.strip() or run_result.stdout.strip() or f"exit {run_result.returncode}"
            return [f"c-header-relay-run:{detail}"]
    return []


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    survey = _read_text(root, SURVEY_REL, issues)
    docs_readme = _read_text(root, DOCS_README_REL, issues)
    scripts_readme = _read_text(root, SCRIPTS_README_REL, issues)
    makefile = _read_text(root, MAKEFILE_REL, issues)
    export_shim = _read_text(root, EXPORT_SHIM_REL, issues)
    uapi_version = _read_text(root, UAPI_VERSION_REL, issues)
    abi_slice = _read_text(root, ABI_SLICE_REL, issues)
    export_uapi_test = _read_text(root, EXPORT_UAPI_TEST_REL, issues)
    export_uapi_layout_build = _read_text(root, EXPORT_UAPI_LAYOUT_BUILD_REL, issues)
    export_uapi_layout_test = _read_text(root, EXPORT_UAPI_LAYOUT_TEST_REL, issues)
    validate_phase3_core = _read_text(root, VALIDATE_PHASE3_CORE_REL, issues)

    if survey:
        for marker in REQUIRED_SURVEY_MARKERS:
            if marker not in survey:
                issues.append(f"missing_survey_marker:{marker}")
        for marker in REQUIRED_SURVEY_BLOB_MARKERS:
            value = _marker_value_from_text(survey, marker)
            if value is None:
                issues.append(f"missing_survey_marker:{marker}=")
            elif not HEX40.fullmatch(value):
                issues.append(f"invalid_survey_blob_sha:{marker}:{value}")
        for snippet in REQUIRED_SURVEY_SNIPPETS:
            if snippet not in survey:
                issues.append(f"missing_survey_snippet:{snippet}")
        surveyed_commit = _surveyed_commit_from_text(survey)
        if surveyed_commit is None:
            issues.append("missing_surveyed_commit")
        elif not HEX40.fullmatch(surveyed_commit):
            issues.append(f"invalid_surveyed_commit:{surveyed_commit}")
        else:
            blob_issues = _packet_drift_by_blob_sha(root, survey)
            if blob_issues:
                issues.extend(blob_issues)
            elif all(_marker_value_from_text(survey, marker) is not None for marker in SURVEYED_PACKET_BLOB_MARKERS):
                pass
            else:
                issues.extend(_packet_drift_since_commit(root, surveyed_commit))

    for rel in REQUIRED_SURVEY_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_repo_path:{rel}")

    if docs_readme:
        for snippet in REQUIRED_DOCS_README_SNIPPETS:
            if snippet not in docs_readme:
                issues.append(f"missing_docs_readme_snippet:{snippet}")

    if scripts_readme:
        for snippet in REQUIRED_SCRIPTS_README_SNIPPETS:
            if snippet not in scripts_readme:
                issues.append(f"missing_scripts_readme_snippet:{snippet}")

    if makefile:
        for snippet in REQUIRED_MAKEFILE_SNIPPETS:
            if snippet not in makefile:
                issues.append(f"missing_makefile_snippet:{snippet}")

    if export_shim:
        for snippet in REQUIRED_EXPORT_SHIM_SNIPPETS:
            if snippet not in export_shim:
                issues.append(f"missing_export_shim_snippet:{snippet}")

    if uapi_version:
        for snippet in REQUIRED_UAPI_VERSION_SNIPPETS:
            if snippet not in uapi_version:
                issues.append(f"missing_uapi_version_snippet:{snippet}")

    if abi_slice:
        for snippet in REQUIRED_ABI_SLICE_SNIPPETS:
            if snippet not in abi_slice:
                issues.append(f"missing_abi_slice_snippet:{snippet}")

    if export_uapi_test:
        for snippet in REQUIRED_EXPORT_UAPI_TEST_SNIPPETS:
            if snippet not in export_uapi_test:
                issues.append(f"missing_export_uapi_test_snippet:{snippet}")

    if export_uapi_layout_build:
        for snippet in REQUIRED_EXPORT_UAPI_LAYOUT_BUILD_SNIPPETS:
            if snippet not in export_uapi_layout_build:
                issues.append(f"missing_export_uapi_layout_build_snippet:{snippet}")

    if export_uapi_layout_test:
        for snippet in REQUIRED_EXPORT_UAPI_LAYOUT_TEST_SNIPPETS:
            if snippet not in export_uapi_layout_test:
                issues.append(f"missing_export_uapi_layout_test_snippet:{snippet}")

    if validate_phase3_core:
        for snippet in REQUIRED_VALIDATE_PHASE3_CORE_SNIPPETS:
            if snippet not in validate_phase3_core:
                issues.append(f"missing_validate_phase3_core_snippet:{snippet}")

    issues.extend(_validate_export_uapi_manifest(root))
    issues.extend(validate_c_header_relay(root))

    uapi_files = _collect_relative_files(root, UAPI_ROOT_REL)
    expected_uapi_files = sorted(REQUIRED_UAPI_FILES)
    for rel in expected_uapi_files:
        if rel not in uapi_files:
            issues.append(f"missing_uapi_file:{rel}")
    for rel in uapi_files:
        if rel not in expected_uapi_files:
            issues.append(f"unexpected_uapi_file:{rel}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_survey_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "include/linux").mkdir(parents=True, exist_ok=True)
        (root / "include/zigux").mkdir(parents=True, exist_ok=True)

        for rel in REQUIRED_SURVEY_PATHS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel == EXPORT_SHIM_REL:
                path.write_text("\n".join(REQUIRED_EXPORT_SHIM_SNIPPETS) + "\n", encoding="utf-8")
            elif rel == UAPI_VERSION_REL:
                path.write_text("\n".join(REQUIRED_UAPI_VERSION_SNIPPETS) + "\n", encoding="utf-8")
            elif rel == ABI_HEADER_REL:
                path.write_text(
                    "\n".join(
                        (
                            "#ifndef _ZIGUX_ABI_H",
                            "#define _ZIGUX_ABI_H",
                            "#include <stdint.h>",
                            "typedef uint16_t zigux_u16;",
                            "typedef uint32_t zigux_u32;",
                            "typedef int32_t zigux_s32;",
                            "#define ZIGUX_ABI_VERSION 1U",
                            "#define ZIGUX_FACILITY_KERNEL 1U",
                            "#define ZIGUX_FACILITY_HELPERS 2U",
                            "#define ZIGUX_FACILITY_DRIVERS 3U",
                            "#define ZIGUX_STATUS_FLAG_ERROR 1U",
                            "struct zigux_boundary_header { zigux_u32 size; zigux_u16 abi_version; zigux_u16 flags; };",
                            "struct zigux_export_status { zigux_s32 code; zigux_u16 facility; zigux_u16 flags; };",
                            "#endif",
                        )
                    )
                    + "\n",
                    encoding="utf-8",
                )
            elif rel == LINUX_HEADER_REL:
                path.write_text(
                    "\n".join(
                        (
                            "#ifndef _LINUX_ZIGUX_H",
                            "#define _LINUX_ZIGUX_H",
                            "#include <stdbool.h>",
                            "#include <stdint.h>",
                            "#include <zigux/abi.h>",
                            "static inline struct zigux_export_status zigux_status_ok(zigux_u16 facility) {",
                            "    return (struct zigux_export_status){ .code = 0, .facility = facility, .flags = 0 };",
                            "}",
                            "static inline struct zigux_export_status zigux_status_err(zigux_s32 code, zigux_u16 facility) {",
                            "    return (struct zigux_export_status){ .code = code, .facility = facility, .flags = code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0 };",
                            "}",
                            "#endif",
                        )
                    )
                    + "\n",
                    encoding="utf-8",
                )
            elif rel == EXPORT_UAPI_LAYOUT_BUILD_REL:
                path.write_text("\n".join(REQUIRED_EXPORT_UAPI_LAYOUT_BUILD_SNIPPETS) + "\n", encoding="utf-8")
            elif rel == EXPORT_UAPI_LAYOUT_TEST_REL:
                path.write_text("\n".join(REQUIRED_EXPORT_UAPI_LAYOUT_TEST_SNIPPETS) + "\n", encoding="utf-8")
            elif rel == VALIDATE_PHASE3_CORE_REL:
                path.write_text("\n".join(REQUIRED_VALIDATE_PHASE3_CORE_SNIPPETS) + "\n", encoding="utf-8")
            elif rel == ABI_MANIFEST_REL:
                manifest_files = [
                    *REQUIRED_EXPORT_UAPI_MANIFEST_FILES,
                    ABI_MANIFEST_REL,
                ]
                path.write_text(
                    json.dumps(
                        {
                            "phase": "Phase 3",
                            "status": "active",
                            "slice": "abi-substrate-skeleton",
                            "files": manifest_files,
                            "file_count": len(manifest_files),
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
            else:
                path.write_text("// ok\n", encoding="utf-8")

        (root / ABI_SLICE_REL).write_text("\n".join(REQUIRED_ABI_SLICE_SNIPPETS) + "\n", encoding="utf-8")
        (root / EXPORT_UAPI_TEST_REL).write_text(
            "\n".join(REQUIRED_EXPORT_UAPI_TEST_SNIPPETS) + "\n",
            encoding="utf-8",
        )
        survey_path = root / SURVEY_REL
        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    f"PHASE3_SURVEYED_COMMIT={PLACEHOLDER_COMMIT}",
                    *_blob_marker_lines(),
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        (root / DOCS_README_REL).write_text("\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n", encoding="utf-8")
        (root / SCRIPTS_README_REL).write_text("\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n", encoding="utf-8")
        (root / MAKEFILE_REL).write_text("\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n", encoding="utf-8")

        assert validate(root) == []

        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Codex",
            "GIT_AUTHOR_EMAIL": "codex@example.com",
            "GIT_COMMITTER_NAME": "Codex",
            "GIT_COMMITTER_EMAIL": "codex@example.com",
        }
        subprocess.run(
            ["git", "commit", "-m", "self-test snapshot"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                f"PHASE3_SURVEYED_COMMIT={PLACEHOLDER_COMMIT}",
                f"PHASE3_SURVEYED_COMMIT={head}",
            ),
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        assert validate(root) == []

        export_shim_path = root / EXPORT_SHIM_REL
        original_export_shim = export_shim_path.read_text(encoding="utf-8")
        export_shim_path.write_text(original_export_shim + "// drift\n", encoding="utf-8")
        issues = validate(root)
        assert f"surveyed_blob_drift:{EXPORT_SHIM_REL}" in issues
        export_shim_path.write_text(original_export_shim, encoding="utf-8")

        survey_path.write_text(REQUIRED_SURVEY_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_survey_marker:") for issue in issues)
        assert any(issue.startswith("missing_survey_snippet:") for issue in issues)

        survey_path.write_text(
            "\n".join(
                (
                    *(marker for marker in REQUIRED_SURVEY_MARKERS if marker != "PHASE3_C_HEADER_STATUS=shared-abi-relay-status-and-interop-helper-aggregation-landed"),
                    f"PHASE3_SURVEYED_COMMIT={head}",
                    *_blob_marker_lines(),
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        issues = validate(root)
        assert "missing_survey_marker:PHASE3_C_HEADER_STATUS=shared-abi-relay-status-and-interop-helper-aggregation-landed" in issues

        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    f"PHASE3_SURVEYED_COMMIT={head}",
                    *_blob_marker_lines(),
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                f"PHASE3_SURVEYED_COMMIT={head}",
                "PHASE3_SURVEYED_COMMIT=not-a-sha",
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "invalid_surveyed_commit:not-a-sha" in issues

        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    f"PHASE3_SURVEYED_COMMIT={head}",
                    *_blob_marker_lines(),
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        current_survey = survey_path.read_text(encoding="utf-8")
        export_blob = _marker_value_from_text(current_survey, "PHASE3_EXPORT_SHIM_BLOB_SHA")
        assert export_blob is not None
        survey_path.write_text(
            current_survey.replace(
                f"PHASE3_EXPORT_SHIM_BLOB_SHA={export_blob}",
                "PHASE3_EXPORT_SHIM_BLOB_SHA=not-a-sha",
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "invalid_survey_blob_sha:PHASE3_EXPORT_SHIM_BLOB_SHA:not-a-sha" in issues

        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    f"PHASE3_SURVEYED_COMMIT={head}",
                    *_blob_marker_lines(),
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        extra_uapi = root / UAPI_ROOT_REL / "extra.zig"
        extra_uapi.write_text("// drift\n", encoding="utf-8")
        issues = validate(root)
        assert f"unexpected_uapi_file:{UAPI_ROOT_REL}/extra.zig" in issues

        extra_uapi.unlink()
        missing_snippet = "canonical boundary-header and export-status size and field-offset contract on its own focused layout replay"
        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    f"PHASE3_SURVEYED_COMMIT={head}",
                    *_blob_marker_lines(),
                    *(snippet for snippet in REQUIRED_SURVEY_SNIPPETS if snippet != missing_snippet),
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        issues = validate(root)
        assert any(issue == f"missing_survey_snippet:{missing_snippet}" for issue in issues)

        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    f"PHASE3_SURVEYED_COMMIT={head}",
                    *_blob_marker_lines(),
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        validate_phase3_core_path = root / VALIDATE_PHASE3_CORE_REL
        original_validate_phase3_core = validate_phase3_core_path.read_text(encoding="utf-8")
        validate_phase3_core_path.write_text(
            original_validate_phase3_core.replace(
                '("phase3-export-uapi-layout-test", ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL),\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert (
            'missing_validate_phase3_core_snippet:("phase3-export-uapi-layout-test", ABI_EXPORT_UAPI_LAYOUT_BUILD_FILE_REL),'
            in issues
        )
        validate_phase3_core_path.write_text(original_validate_phase3_core, encoding="utf-8")

        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    f"PHASE3_SURVEYED_COMMIT={head}",
                    *_blob_marker_lines(),
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _replace_blob_markers_with_head(root, survey_path)
        linux_header_path = root / LINUX_HEADER_REL
        linux_header_path.write_text(
            linux_header_path.read_text(encoding="utf-8").replace("zigux_status_err", "zigux_status_missing", 1),
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(issue.startswith("c-header-relay-compile:") for issue in issues)
        linux_header_path.write_text(
            linux_header_path.read_text(encoding="utf-8").replace("zigux_status_missing", "zigux_status_err", 1),
            encoding="utf-8",
        )

        manifest_path = root / ABI_MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"].remove(EXPORT_UAPI_LAYOUT_TEST_REL)
        manifest["file_count"] = len(manifest["files"])
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        issues = validate(root)
        assert f"export-uapi-manifest-missing:{EXPORT_UAPI_LAYOUT_TEST_REL}" in issues

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the published Phase 3 export-shim and UAPI boundary survey stays aligned with the live repo.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker tests without reading the repo.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate(ROOT)
    if issues:
        print("PHASE3_EXPORT_UAPI_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE3_EXPORT_UAPI_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

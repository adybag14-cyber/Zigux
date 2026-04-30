#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re
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
EXPORT_UAPI_TEST_REL = "zigux/tests/phase3_export_uapi.zig"
HEX40 = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
    "PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_EXPORT_SHIM_STATUS=normalize-and-compatibility-helpers-landed",
    "PHASE3_UAPI_ROOT=zigux/uapi",
    "PHASE3_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_UAPI_STATUS=version-header-and-compatibility-surface-landed",
    "PHASE3_EXPORT_UAPI_GATE=zig build phase3-export-uapi-test --build-file zigux/tests/phase3_export_uapi_build.zig",
    "PHASE3_BOUNDARY_GAP=broader-curated-uapi-shims-still-deferred",
    "PHASE3_NEXT_BOUNDED_STEP=keep-boundary-header-surface-narrow-until-one-roadmap-backed-interop-slice-needs-another-curated-uapi-or-export-entry",
)

REQUIRED_SURVEY_SNIPPETS = (
    "zigux/tests/phase3_export_uapi_build.zig",
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "keep canonical-size header checks separate from broader future-compatible header acceptance",
    "verified `master` head",
)

REQUIRED_SURVEY_PATHS = (
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    "Documentation/zigux/phase3-abi-slice.md",
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "zigux/tests/phase3_export_uapi_build.zig",
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
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
)

REQUIRED_EXPORT_SHIM_SNIPPETS = (
    "pub fn header(flags: u16) abi.BoundaryHeader {",
    "pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {",
    "pub fn isCanonicalHeader(boundary_header: abi.BoundaryHeader) bool {",
    "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {",
    "pub fn ok(facility: abi.Facility) abi.ExportStatus {",
    "pub fn errno(code: i32, facility: abi.Facility) abi.ExportStatus {",
    "pub fn isOk(status: abi.ExportStatus) bool {",
    'test "phase3 export shim separates canonical headers from broader compatibility"',
)

REQUIRED_UAPI_VERSION_SNIPPETS = (
    "pub const Header = abi.BoundaryHeader;",
    "pub fn boundaryHeader(flags: u16) Header {",
    "pub fn isCompatible(header: Header) bool {",
    "pub fn isCanonical(header: Header) bool {",
    'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes"',
)

REQUIRED_ABI_SLICE_SNIPPETS = (
    "export shim reality today: `zigux/kernel/export_shim.zig` stays a narrow explicit-status helper, and it now exposes a small local boundary-header surface that keeps exact canonical-size replay separate from broader future-compatible header acceptance without widening the public export namespace further",
    "UAPI reality today: `zigux/uapi/version.zig` now exposes the ABI version plus an explicit boundary-header constructor whose exact canonical-size replay stays separate from broader future-compatible compatibility, which is still bounded but makes the public boundary less ad hoc than a version constant alone",
)

REQUIRED_EXPORT_UAPI_TEST_SNIPPETS = (
    "try std.testing.expect(export_shim.isCanonicalHeader(header));",
    "try std.testing.expect(uapi_version.isCanonical(header));",
    "const future_compatible_header: abi.BoundaryHeader = .{",
    "try std.testing.expect(!export_shim.isCanonicalHeader(future_compatible_header));",
    "try std.testing.expect(!uapi_version.isCanonical(future_compatible_header));",
    "try std.testing.expect(export_shim.isCompatibleHeader(future_compatible_header));",
    "try std.testing.expect(uapi_version.isCompatible(future_compatible_header));",
)

REQUIRED_UAPI_FILES = (
    UAPI_VERSION_REL,
)


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
    prefix = "PHASE3_SURVEYED_COMMIT="
    for line in text.splitlines():
        stripped = line.strip().strip("- ").strip("`")
        if stripped.startswith(prefix):
            return stripped[len(prefix) :]
    return None


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

    if survey:
        for marker in REQUIRED_SURVEY_MARKERS:
            if marker not in survey:
                issues.append(f"missing_survey_marker:{marker}")
        for snippet in REQUIRED_SURVEY_SNIPPETS:
            if snippet not in survey:
                issues.append(f"missing_survey_snippet:{snippet}")
        surveyed_commit = _surveyed_commit_from_text(survey)
        if surveyed_commit is None:
            issues.append("missing_surveyed_commit")
        elif not HEX40.fullmatch(surveyed_commit):
            issues.append(f"invalid_surveyed_commit:{surveyed_commit}")

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

        for rel in REQUIRED_SURVEY_PATHS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel == EXPORT_SHIM_REL:
                path.write_text("\n".join(REQUIRED_EXPORT_SHIM_SNIPPETS) + "\n", encoding="utf-8")
            elif rel == UAPI_VERSION_REL:
                path.write_text("\n".join(REQUIRED_UAPI_VERSION_SNIPPETS) + "\n", encoding="utf-8")
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
                    "PHASE3_SURVEYED_COMMIT=0123456789abcdef0123456789abcdef01234567",
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

        survey_path.write_text(REQUIRED_SURVEY_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_survey_marker:") for issue in issues)
        assert any(issue.startswith("missing_survey_snippet:") for issue in issues)

        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    "PHASE3_SURVEYED_COMMIT=0123456789abcdef0123456789abcdef01234567",
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "PHASE3_SURVEYED_COMMIT=0123456789abcdef0123456789abcdef01234567",
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
                    "PHASE3_SURVEYED_COMMIT=0123456789abcdef0123456789abcdef01234567",
                    *REQUIRED_SURVEY_SNIPPETS,
                )
            )
            + "\n",
            encoding="utf-8",
        )
        extra_uapi = root / UAPI_ROOT_REL / "extra.zig"
        extra_uapi.write_text("// drift\n", encoding="utf-8")
        issues = validate(root)
        assert f"unexpected_uapi_file:{UAPI_ROOT_REL}/extra.zig" in issues

        extra_uapi.unlink()
        survey_path.write_text(
            "\n".join(
                (
                    *REQUIRED_SURVEY_MARKERS,
                    "PHASE3_SURVEYED_COMMIT=0123456789abcdef0123456789abcdef01234567",
                    *REQUIRED_SURVEY_SNIPPETS[:-1],
                )
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(
            issue == f"missing_survey_snippet:{REQUIRED_SURVEY_SNIPPETS[-1]}"
            for issue in issues
        )

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

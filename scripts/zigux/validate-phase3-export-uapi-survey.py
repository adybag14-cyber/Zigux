#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
DOCS_ROOT_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"
EXPORT_UAPI_TEST_REL = "zigux/tests/phase3_export_uapi.zig"
EXPORT_UAPI_BUILD_REL = "zigux/tests/phase3_export_uapi_build.zig"
EXPORT_UAPI_LAYOUT_TEST_REL = "zigux/tests/phase3_export_uapi_layout.zig"
EXPORT_UAPI_LAYOUT_BUILD_REL = "zigux/tests/phase3_export_uapi_layout_build.zig"
BUILD_FILE_REL = "zigux/tests/build.zig"
MAKEFILE_REL = "zigux/Makefile"
VALIDATOR_REL = "scripts/zigux/validate-phase3-export-uapi-survey.py"
SELF_TEST_CASE_COUNT = 12

REQUIRED_FILES = (
    SURVEY_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    EXPORT_UAPI_TEST_REL,
    EXPORT_UAPI_BUILD_REL,
    EXPORT_UAPI_LAYOUT_TEST_REL,
    EXPORT_UAPI_LAYOUT_BUILD_REL,
    BUILD_FILE_REL,
    MAKEFILE_REL,
    VALIDATOR_REL,
    WORKFLOW_REL,
)

SURVEY_PROVENANCE_MARKERS = (
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`",
)

SURVEY_EXACT_MARKERS = (
    "`PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-build-route-readback-plus-shared-review-surface-refresh`",
    "`PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`",
    f"`PHASE3_EXPORT_SHIM_PATH={EXPORT_SHIM_REL}`",
    f"`PHASE3_UAPI_VERSION_PATH={UAPI_VERSION_REL}`",
    f"`PHASE3_SHARED_BUILD_PATH={BUILD_FILE_REL}`",
    f"`PHASE3_SHARED_MAKEFILE_PATH={MAKEFILE_REL}`",
    f"`PHASE3_EXPORT_UAPI_VALIDATOR_PATH={VALIDATOR_REL}`",
    f"`PHASE3_EXPORT_UAPI_WORKFLOW_PATH={WORKFLOW_REL}`",
)

SURVEY_BLOB_MARKERS = (
    ("PHASE3_EXPORT_SHIM_BLOB_SHA", EXPORT_SHIM_REL),
    ("PHASE3_UAPI_VERSION_BLOB_SHA", UAPI_VERSION_REL),
)

REQUIRED_MARKERS = {
    EXPORT_SHIM_REL: (
        "pub const Header = uapi_version.Header;",
        "pub const abi_version: u16 = uapi_version.abi_version;",
        "pub const header_size: u32 = uapi_version.header_size;",
        "pub const HeaderCompatibility = uapi_version.Compatibility;",
        "pub const HeaderAcceptance = uapi_version.AcceptedHeader;",
        "pub const HeaderEvaluation = uapi_version.HeaderEvaluation;",
        "pub fn compatibilityStatus(",
        'test "phase3 export shim relays compatibility through explicit status packets" {',
    ),
    UAPI_VERSION_REL: (
        "pub const Compatibility = enum {",
        "future_compatible,",
        "pub const AcceptedHeader = struct {",
        "pub const HeaderEvaluation = struct {",
        "pub fn compatibility(header: Header) ?Compatibility {",
        'test "phase3 uapi evaluation keeps requested boundary shape explicit" {',
    ),
    MAKEFILE_REL: (
        "phase3-validate:",
        "phase3-abi:",
        "$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
        "phase3: phase3-validate phase3-abi phase3-interop",
    ),
}

DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
    "`zig build phase3-test --build-file zigux/tests/build.zig`",
    "`make -C zigux phase3`",
)

SCRIPTS_README_MARKERS = (
    "`validate-phase3-export-uapi-survey.py`",
)

WORKFLOW_MARKERS = (
    "- name: Validate Phase 3 export/UAPI survey",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "- name: Self-test Phase 3 export/UAPI survey",
    "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "- name: Run Phase 3 ABI/interp substrate tests",
    "run: zig build phase3-test --build-file zigux/tests/build.zig",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def normalized_lines(text: str) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        elif line.startswith("* "):
            line = line[2:].strip()
        out.append(line)
    return out


def require_exact_line_count(issues: list[str], text: str, prefix: str, line: str) -> None:
    count = normalized_lines(text).count(line)
    if count == 1:
        return
    if count == 0:
        issues.append(f"missing_{prefix}:{line}")
    else:
        issues.append(f"duplicate_{prefix}:{count}:{line}")


def require_one_of_exact_lines(
    issues: list[str], text: str, prefix: str, lines: tuple[str, ...]
) -> None:
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
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def extract_backticked_values(text: str, key: str) -> list[str]:
    prefix = f"`{key}="
    values: list[str] = []
    for line in normalized_lines(text):
        if line.startswith(prefix) and line.endswith("`"):
            values.append(line[len(prefix) : -1])
    return values


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
        path = root / rel
        if not path.exists():
            continue
        values = extract_backticked_values(survey, key)
        if not values:
            issues.append(f"missing_survey_marker:`{key}=<sha>`")
            continue
        if len(values) != 1:
            issues.append(f"duplicate_survey_marker:{len(values)}:`{key}=<sha>`")
            continue
        expected = blob_sha(path)
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


def build_valid_workspace(root: Path) -> None:
    export_shim_text = "\n".join(
        (
            'const abi = @import("abi_bindings");',
            'const uapi_version = @import("uapi_version");',
            "pub const Header = uapi_version.Header;",
            "pub const abi_version: u16 = uapi_version.abi_version;",
            "pub const header_size: u32 = uapi_version.header_size;",
            "pub const HeaderCompatibility = uapi_version.Compatibility;",
            "pub const HeaderAcceptance = uapi_version.AcceptedHeader;",
            "pub const HeaderEvaluation = uapi_version.HeaderEvaluation;",
            "pub fn compatibilityStatus(",
            "    header_value: Header,",
            "    incompatible_code: i32,",
            "    facility: abi.Facility,",
            ") abi.ExportStatus {",
            "    _ = header_value;",
            "    _ = incompatible_code;",
            "    _ = facility;",
            "    return undefined;",
            "}",
            'test "phase3 export shim relays compatibility through explicit status packets" {',
            "    _ = .{};",
            "}",
            "",
        )
    )
    _write(root / EXPORT_SHIM_REL, export_shim_text)

    uapi_text = "\n".join(
        (
            "pub const Header = extern struct {};",
            "pub const Compatibility = enum {",
            "    canonical,",
            "    future_compatible,",
            "};",
            "pub const AcceptedHeader = struct {",
            "    compatibility: Compatibility,",
            "    canonical: Header,",
            "};",
            "pub const HeaderEvaluation = struct {",
            "    requested: Header,",
            "    acceptance: ?AcceptedHeader,",
            "};",
            "pub fn compatibility(header: Header) ?Compatibility {",
            "    _ = header;",
            "    return null;",
            "}",
            'test "phase3 uapi evaluation keeps requested boundary shape explicit" {',
            "    _ = .{};",
            "}",
            "",
        )
    )
    _write(root / UAPI_VERSION_REL, uapi_text)

    _write(root / EXPORT_UAPI_TEST_REL, "// export/uapi replay placeholder\n")
    _write(root / EXPORT_UAPI_BUILD_REL, "// export/uapi build placeholder\n")
    _write(root / EXPORT_UAPI_LAYOUT_TEST_REL, "// export/uapi layout replay placeholder\n")
    _write(root / EXPORT_UAPI_LAYOUT_BUILD_REL, "// export/uapi layout build placeholder\n")
    _write(root / BUILD_FILE_REL, "// shared phase3 build route placeholder\n")
    _write(
        root / MAKEFILE_REL,
        "\n".join(
            (
                "phase3-validate:",
                "phase3-abi:",
                "\t$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
                "phase3: phase3-validate phase3-abi phase3-interop",
                "",
            )
        ),
    )
    _write(root / VALIDATOR_REL, "# validator placeholder\n")
    _write(
        root / DOCS_ROOT_REL,
        "\n".join(
            (
                "# docs root",
                "- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
                "- `scripts/zigux/validate-phase3-export-uapi-survey.py`",
                "- `zig build phase3-test --build-file zigux/tests/build.zig`",
                "- `make -C zigux phase3`",
                "",
            )
        ),
    )
    _write(
        root / SCRIPTS_README_REL,
        "\n".join(
            (
                "# scripts",
                "- `validate-phase3-export-uapi-survey.py`",
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
                "- name: Run Phase 3 ABI/interp substrate tests",
                "  run: zig build phase3-test --build-file zigux/tests/build.zig",
                "",
            )
        ),
    )
    survey_text = "\n".join(
        (
            "# Phase 3 Export Shim and UAPI Boundary Survey",
            "",
            "## Status",
            "",
            f"- {SURVEY_PROVENANCE_MARKERS[0]}",
            f"- {SURVEY_EXACT_MARKERS[0]}",
            f"- {SURVEY_EXACT_MARKERS[1]}",
            f"- {SURVEY_EXACT_MARKERS[2]}",
            f"- `PHASE3_EXPORT_SHIM_BLOB_SHA={blob_sha(root / EXPORT_SHIM_REL)}`",
            f"- {SURVEY_EXACT_MARKERS[3]}",
            f"- `PHASE3_UAPI_VERSION_BLOB_SHA={blob_sha(root / UAPI_VERSION_REL)}`",
            f"- {SURVEY_EXACT_MARKERS[4]}",
            f"- {SURVEY_EXACT_MARKERS[5]}",
            f"- {SURVEY_EXACT_MARKERS[6]}",
            f"- {SURVEY_EXACT_MARKERS[7]}",
            "",
        )
    )
    _write(root / SURVEY_REL, survey_text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == [], validate(root)

        survey_path = root / SURVEY_REL
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                SURVEY_PROVENANCE_MARKERS[0],
                SURVEY_PROVENANCE_MARKERS[1],
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [], validate(root)
        build_valid_workspace(root)

        _write(root / EXPORT_SHIM_REL, (root / EXPORT_SHIM_REL).read_text(encoding="utf-8") + "// drift\n")
        issues = validate(root)
        assert len(issues) == 1 and issues[0].startswith("stale_survey_blob:PHASE3_EXPORT_SHIM_BLOB_SHA:"), issues
        build_valid_workspace(root)

        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                SURVEY_EXACT_MARKERS[1],
                "`PHASE3_BUILD_ROUTE_OWNERSHIP=broken`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [f"missing_survey_marker:{SURVEY_EXACT_MARKERS[1]}"]
        build_valid_workspace(root)

        export_uapi_test_path = root / EXPORT_UAPI_TEST_REL
        export_uapi_test_path.unlink()
        assert validate(root) == [f"missing_file:{EXPORT_UAPI_TEST_REL}"]
        build_valid_workspace(root)

        export_uapi_build_path = root / EXPORT_UAPI_BUILD_REL
        export_uapi_build_path.unlink()
        assert validate(root) == [f"missing_file:{EXPORT_UAPI_BUILD_REL}"]
        build_valid_workspace(root)

        export_uapi_layout_test_path = root / EXPORT_UAPI_LAYOUT_TEST_REL
        export_uapi_layout_test_path.unlink()
        assert validate(root) == [f"missing_file:{EXPORT_UAPI_LAYOUT_TEST_REL}"]
        build_valid_workspace(root)

        export_uapi_layout_build_path = root / EXPORT_UAPI_LAYOUT_BUILD_REL
        export_uapi_layout_build_path.unlink()
        assert validate(root) == [f"missing_file:{EXPORT_UAPI_LAYOUT_BUILD_REL}"]
        build_valid_workspace(root)

        scripts_readme_path = root / SCRIPTS_README_REL
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                "- `validate-phase3-export-uapi-survey.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            "missing_scripts_readme_marker:`validate-phase3-export-uapi-survey.py`"
        ]
        build_valid_workspace(root)

        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
                "run: python3 scripts/zigux/not-the-validator.py --self-test",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            "missing_workflow_marker:run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"
        ]
        build_valid_workspace(root)

        makefile_path = root / MAKEFILE_REL
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(
                "\t$(ZIG) build phase3-test --build-file zigux/tests/build.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            "missing_marker:zigux/Makefile:$(ZIG) build phase3-test --build-file zigux/tests/build.zig"
        ]
        build_valid_workspace(root)

        docs_root_path = root / DOCS_ROOT_REL
        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(
                "- `make -C zigux phase3`\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == ["missing_docs_root_marker:`make -C zigux phase3`"]
        build_valid_workspace(root)

        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                f"`PHASE3_UAPI_VERSION_PATH={UAPI_VERSION_REL}`",
                "`PHASE3_UAPI_VERSION_PATH=broken`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate(root) == [
            f"missing_survey_marker:`PHASE3_UAPI_VERSION_PATH={UAPI_VERSION_REL}`"
        ]

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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

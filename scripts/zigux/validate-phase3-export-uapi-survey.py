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
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"
UAPI_DEV_T_REL = "zigux/uapi/dev_t.zig"
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

REQUIRED_FILES = (
    SURVEY_REL,
    ABI_SLICE_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    MAKEFILE_REL,
    EXPORT_SHIM_REL,
    UAPI_VERSION_REL,
    UAPI_DEV_T_REL,
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
    UAPI_DEV_T_REL,
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
    f"`PHASE3_UAPI_DEV_T_PATH={UAPI_DEV_T_REL}`",
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
    ("PHASE3_UAPI_DEV_T_BLOB_SHA", UAPI_DEV_T_REL),
    ("PHASE3_LINUX_HEADER_BLOB_SHA", LINUX_HEADER_REL),
    ("PHASE3_ABI_HEADER_BLOB_SHA", ABI_HEADER_REL),
    ("PHASE3_EXPORT_UAPI_BEHAVIOR_BLOB_SHA", EXPORT_UAPI_TEST_REL),
    ("PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA", EXPORT_UAPI_BUILD_REL),
    ("PHASE3_EXPORT_UAPI_LAYOUT_BLOB_SHA", EXPORT_UAPI_LAYOUT_REL),
    ("PHASE3_EXPORT_UAPI_LAYOUT_BUILD_BLOB_SHA", EXPORT_UAPI_LAYOUT_BUILD_REL),
    ("PHASE3_EXPORT_UAPI_VALIDATOR_BLOB_SHA", VALIDATOR_REL),
)

ABI_SLICE_SUBSTRINGS = (
    "`PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof`",
    "current `master` keeps the packet-local `phase3-export-uapi-boundary-survey.md` note",
    "the current shared ABI packet also keeps the focused export/UAPI boundary replay explicit across `zigux/tests/phase3_export_uapi_layout.zig`",
    "the current shared ABI packet also keeps the direct export/UAPI behavior replay explicit across `zigux/tests/phase3_export_uapi.zig` and `zigux/tests/phase3_export_uapi_build.zig`",
)

HEADER_GOVERNANCE_SUBSTRINGS = (
    f"`PHASE3_ZIGUX_H_PATH={LINUX_HEADER_REL}`",
    f"`PHASE3_ZIGUX_H_SHARED_SLICE_NOTE={ABI_SLICE_REL}`",
    f"`PHASE3_ZIGUX_H_MANIFEST_PATH={ABI_MANIFEST_REL}`",
    "export/UAPI starter work may reference this header, but the dedicated export/UAPI survey still owns the narrower starter-boundary claims it proves directly",
)

MAKEFILE_MARKERS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
)

REQUIRED_MARKERS = {
    EXPORT_SHIM_REL: (
        "pub const Header = uapi_version.Header;",
        "pub const HeaderCompatibility = uapi_version.Compatibility;",
        "pub const HeaderEvaluation = uapi_version.HeaderEvaluation;",
        "pub fn compatibilityStatus(",
        "return evaluateHeader(header_value, incompatible_code, facility).status;",
        'test "phase3 export shim reuses the shared boundary-header compatibility rules" {',
        'test "phase3 export shim relays compatibility through explicit status packets" {',
        'test "phase3 export shim evaluation keeps compatibility evidence and status together" {',
    ),
    UAPI_VERSION_REL: (
        "pub const Compatibility = enum(u32) {",
        "future_compatible = 2,",
        "pub fn compatibilityTag(header: Header) u32 {",
        'test "phase3 uapi exports explicit compatibility tags for the starter boundary" {',
    ),
    UAPI_DEV_T_REL: (
        "pub const minor_bits: u5 = dev_t_bindings.minor_bits;",
        "pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {",
        "pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {",
        'test "phase3 uapi dev_t starter mirrors the curated codec" {',
        'test "phase3 uapi dev_t starter keeps bounded range helpers explicit" {',
        'test "phase3 uapi dev_t starter rejects out-of-range inputs" {',
    ),
    EXPORT_UAPI_TEST_REL: (
        'const dev_t_bindings = @import("dev_t_bindings");',
        'const uapi_dev_t = @import("uapi_dev_t");',
        'test "phase3 export shim and uapi share the bounded boundary-header contract" {',
        'test "phase3 export shim keeps compatibility-status relays explicit" {',
        'test "phase3 uapi dev_t starter keeps encode and range parity explicit" {',
    ),
    EXPORT_UAPI_BUILD_REL: (
        '.root_source_file = b.path("../bindings/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        'uapi_dev_t_module.addImport("dev_t_bindings", dev_t_bindings_module);',
        'root_module.addImport("dev_t_bindings", dev_t_bindings_module);',
        'root_module.addImport("uapi_dev_t", uapi_dev_t_module);',
    ),
    EXPORT_UAPI_LAYOUT_REL: (
        'const dev_t_bindings = @import("dev_t_bindings");',
        'const uapi_dev_t = @import("uapi_dev_t");',
        'test "phase3 export shim and uapi keep canonical boundary layout" {',
        'test "phase3 export shim evaluation mirrors the uapi boundary classification" {',
        'test "phase3 uapi dev_t starter keeps curated boundary parity explicit" {',
    ),
    EXPORT_UAPI_LAYOUT_BUILD_REL: (
        '.root_source_file = b.path("../bindings/dev_t.zig"),',
        '.root_source_file = b.path("../uapi/dev_t.zig"),',
        'uapi_dev_t_module.addImport("dev_t_bindings", dev_t_bindings_module);',
        'root_module.addImport("dev_t_bindings", dev_t_bindings_module);',
        'root_module.addImport("uapi_dev_t", uapi_dev_t_module);',
    ),
}

DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`Documentation/zigux/phase3-linux-zigux-header-governance.md`",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
    "`zig build phase3-test --build-file zigux/tests/build.zig`",
    "`make -C zigux phase3`",
)

SCRIPTS_README_MARKERS = (
    "`validate-phase3-export-uapi-survey.py`",
    "`validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `include/linux/zigux.h`, `include/zigux/abi.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/tests/phase3_export_uapi.zig`, `zigux/tests/phase3_export_uapi_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and the workflow hooks that rerun that same survey surface.`",
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
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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


def require_substrings(issues: list[str], text: str, rel: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"missing_marker:{rel}:{marker}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    survey = (root / SURVEY_REL).read_text(encoding="utf-8")
    require_one_of_exact_lines(issues, survey, "survey_provenance", SURVEY_PROVENANCE_MARKERS)
    for marker in SURVEY_EXACT_MARKERS:
        require_exact_line_count(issues, survey, "survey_marker", marker)
    for key, rel in SURVEY_BLOB_MARKERS:
        values = extract_backticked_values(survey, key)
        if len(values) != 1:
            issues.append(f"bad_survey_blob_marker:{key}:{len(values)}")
            continue
        expected = blob_sha(root / rel)
        if values[0] != expected:
            issues.append(f"stale_survey_blob:{key}:{values[0]}!={expected}")

    require_substrings(issues, (root / ABI_SLICE_REL).read_text(encoding="utf-8"), ABI_SLICE_REL, ABI_SLICE_SUBSTRINGS)
    require_substrings(
        issues,
        (root / LINUX_HEADER_GOVERNANCE_REL).read_text(encoding="utf-8"),
        LINUX_HEADER_GOVERNANCE_REL,
        HEADER_GOVERNANCE_SUBSTRINGS,
    )

    for rel, markers in REQUIRED_MARKERS.items():
        require_substrings(issues, (root / rel).read_text(encoding="utf-8"), rel, markers)

    validate_manifest(root, issues)

    docs_root = (root / DOCS_ROOT_REL).read_text(encoding="utf-8")
    for marker in DOCS_ROOT_MARKERS:
        require_exact_line_count(issues, docs_root, "docs_root_marker", marker)

    scripts_readme = (root / SCRIPTS_README_REL).read_text(encoding="utf-8")
    for marker in SCRIPTS_README_MARKERS:
        require_exact_line_count(issues, scripts_readme, "scripts_readme_marker", marker)

    makefile = (root / MAKEFILE_REL).read_text(encoding="utf-8")
    for marker in MAKEFILE_MARKERS:
        require_exact_line_count(issues, makefile, "makefile_marker", marker)

    workflow_lines = [line.strip() for line in (root / WORKFLOW_REL).read_text(encoding="utf-8").splitlines()]
    for marker in WORKFLOW_MARKERS:
        count = workflow_lines.count(marker)
        if count != 1:
            issues.append(f"bad_workflow_marker:{count}:{marker}")

    return issues


def build_valid_workspace(root: Path) -> None:
    minimal_files = {
        EXPORT_SHIM_REL: "\n".join(REQUIRED_MARKERS[EXPORT_SHIM_REL]) + "\n",
        UAPI_VERSION_REL: "\n".join(REQUIRED_MARKERS[UAPI_VERSION_REL]) + "\n",
        UAPI_DEV_T_REL: "\n".join(REQUIRED_MARKERS[UAPI_DEV_T_REL]) + "\n",
        EXPORT_UAPI_TEST_REL: "\n".join(REQUIRED_MARKERS[EXPORT_UAPI_TEST_REL]) + "\n",
        EXPORT_UAPI_BUILD_REL: "\n".join(REQUIRED_MARKERS[EXPORT_UAPI_BUILD_REL]) + "\n",
        EXPORT_UAPI_LAYOUT_REL: "\n".join(REQUIRED_MARKERS[EXPORT_UAPI_LAYOUT_REL]) + "\n",
        EXPORT_UAPI_LAYOUT_BUILD_REL: "\n".join(REQUIRED_MARKERS[EXPORT_UAPI_LAYOUT_BUILD_REL]) + "\n",
        ABI_SLICE_REL: "\n".join(ABI_SLICE_SUBSTRINGS) + "\n",
        LINUX_HEADER_GOVERNANCE_REL: "\n".join(HEADER_GOVERNANCE_SUBSTRINGS) + "\n",
        LINUX_HEADER_REL: "#include <zigux/abi.h>\nstatic inline struct zigux_export_status zigux_status_ok(\nstatic inline struct zigux_export_status zigux_status_err(\n",
        ABI_HEADER_REL: "#define ZIGUX_ABI_VERSION 1U\n#define ZIGUX_STATUS_FLAG_ERROR 1U\nstruct zigux_boundary_header {\nstruct zigux_export_status {\n",
        BUILD_FILE_REL: "// build placeholder\n",
        DOCS_ROOT_REL: "\n".join(f"- {marker}" for marker in DOCS_ROOT_MARKERS) + "\n",
        SCRIPTS_README_REL: "\n".join(f"- {marker}" for marker in SCRIPTS_README_MARKERS) + "\n",
        MAKEFILE_REL: "\n".join(MAKEFILE_MARKERS) + "\n",
        WORKFLOW_REL: "\n".join(WORKFLOW_MARKERS) + "\n",
    }
    for rel, text in minimal_files.items():
        _write(root / rel, text)

    _write(root / VALIDATOR_REL, Path(__file__).read_text(encoding="utf-8"))

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

    survey_lines = [
        "# Phase 3 Export Shim and UAPI Boundary Survey",
        "",
        "## Status",
        "",
        SURVEY_PROVENANCE_MARKERS[0],
        *SURVEY_EXACT_MARKERS,
    ]
    for key, rel in SURVEY_BLOB_MARKERS:
        survey_lines.append(f"`{key}={blob_sha(root / rel)}`")
    _write(root / SURVEY_REL, "\n".join(survey_lines) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == []

        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"].remove(UAPI_DEV_T_REL)
        manifest["file_count"] = len(manifest["files"])
        _write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert f"manifest_missing_required_file:{UAPI_DEV_T_REL}" in issues, issues
        build_valid_workspace(root)

        survey = (root / SURVEY_REL).read_text(encoding="utf-8").replace(SURVEY_EXACT_MARKERS[6] + "\n", "")
        _write(root / SURVEY_REL, survey)
        issues = validate(root)
        assert f"missing_survey_marker:{SURVEY_EXACT_MARKERS[6]}" in issues, issues
        build_valid_workspace(root)

        bad_blob = "deadbeef"
        expected = blob_sha(root / UAPI_DEV_T_REL)
        survey = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            f"`PHASE3_UAPI_DEV_T_BLOB_SHA={expected}`",
            f"`PHASE3_UAPI_DEV_T_BLOB_SHA={bad_blob}`",
        )
        _write(root / SURVEY_REL, survey)
        issues = validate(root)
        assert f"stale_survey_blob:PHASE3_UAPI_DEV_T_BLOB_SHA:{bad_blob}!={expected}" in issues, issues
        build_valid_workspace(root)

        text = (root / EXPORT_UAPI_TEST_REL).read_text(encoding="utf-8").replace(
            'test "phase3 uapi dev_t starter keeps encode and range parity explicit" {',
            "test noop {",
        )
        _write(root / EXPORT_UAPI_TEST_REL, text)
        issues = validate(root)
        assert (
            'missing_marker:zigux/tests/phase3_export_uapi.zig:test "phase3 uapi dev_t starter keeps encode and range parity explicit" {'
            in issues
        ), issues
        build_valid_workspace(root)

        makefile = (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(MAKEFILE_MARKERS[1] + "\n", "", 1)
        _write(root / MAKEFILE_REL, makefile)
        issues = validate(root)
        assert f"missing_makefile_marker:{MAKEFILE_MARKERS[1]}" in issues, issues

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT=5")
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

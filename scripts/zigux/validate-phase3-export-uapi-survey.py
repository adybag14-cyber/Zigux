#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
DOCS_README = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
HEADER_GOVERNANCE = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")
LINUX_HEADER = Path("include/linux/zigux.h")
ABI_HEADER = Path("include/zigux/abi.h")
EXPORT_SHIM = Path("zigux/kernel/export_shim.zig")
UAPI_VERSION = Path("zigux/uapi/version.zig")
UAPI_DEV_T = Path("zigux/uapi/dev_t.zig")
ABI_SLICE = Path("Documentation/zigux/phase3-abi-slice.md")
ABI_NEXT_STEP = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
BUILD_FILE = Path("zigux/tests/build.zig")
ABI_DUMP = Path("zigux/tests/phase3_abi_dump.zig")
MAKEFILE = Path("zigux/Makefile")
VALIDATOR = Path("scripts/zigux/validate-phase3-export-uapi-survey.py")
DUMP_GATE = "zig build phase3-dump --build-file zigux/tests/build.zig"
INTEROP_ROUTE = "python3 scripts/zigux/run-phase3-checks.py --slug abi"
INTEROP_MAKE = "make -C zigux phase3-interop"

PROVENANCE = (
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`",
)
SURVEY_LINES = (
    "`PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-review-surface-refresh`",
    "`PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`",
    f"`PHASE3_EXPORT_SHIM_PATH={EXPORT_SHIM.as_posix()}`",
    f"`PHASE3_UAPI_VERSION_PATH={UAPI_VERSION.as_posix()}`",
    f"`PHASE3_UAPI_DEV_T_PATH={UAPI_DEV_T.as_posix()}`",
    f"`PHASE3_SHARED_BUILD_PATH={BUILD_FILE.as_posix()}`",
    f"`PHASE3_SHARED_DUMP_PATH={ABI_DUMP.as_posix()}`",
    f"`PHASE3_SHARED_DUMP_GATE={DUMP_GATE}`",
    f"`PHASE3_SHARED_INTEROP_ROUTE={INTEROP_ROUTE}`",
    f"`PHASE3_SHARED_INTEROP_MAKE={INTEROP_MAKE}`",
    f"`PHASE3_SHARED_MAKEFILE_PATH={MAKEFILE.as_posix()}`",
    f"`PHASE3_EXPORT_UAPI_VALIDATOR_PATH={VALIDATOR.as_posix()}`",
    f"`PHASE3_EXPORT_UAPI_WORKFLOW_PATH={WORKFLOW.as_posix()}`",
)
ABI_SLICE_LINES = (
    f"`{SURVEY.as_posix()}`",
    f"`{ABI_NEXT_STEP.as_posix()}`",
    f"`{EXPORT_SHIM.as_posix()}`",
    f"`{UAPI_VERSION.as_posix()}`",
    f"`{UAPI_DEV_T.as_posix()}`",
    f"`{ABI_DUMP.as_posix()}`",
)
ABI_NEXT_STEP_LINES = (
    f"`{SURVEY.as_posix()}`",
    f"`{EXPORT_SHIM.as_posix()}`",
    f"`{UAPI_VERSION.as_posix()}`",
    f"`{UAPI_DEV_T.as_posix()}`",
    f"`{ABI_DUMP.as_posix()}`",
    f"`{VALIDATOR.as_posix()}`",
)
FORBIDDEN_SURVEY_MARKERS = (
    "PHASE3_EXPORT_UAPI_TEST_PATH=",
    "PHASE3_EXPORT_UAPI_BUILD_PATH=",
    "PHASE3_EXPORT_UAPI_LAYOUT_PATH=",
    "PHASE3_EXPORT_UAPI_LAYOUT_BUILD_PATH=",
    "phase3_export_uapi.zig",
    "phase3_export_uapi_build.zig",
    "phase3_export_uapi_layout.zig",
    "phase3_export_uapi_layout_build.zig",
)
FORBIDDEN_SCRIPTS_README_MARKERS = (
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_export_uapi_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
)
DOCS_README_LINES = (
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`Documentation/zigux/phase3-linux-zigux-header-governance.md`",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
    f"`{UAPI_DEV_T.as_posix()}`",
    "`zig build phase3-test --build-file zigux/tests/build.zig`",
    "`make -C zigux phase3`",
)
SCRIPTS_README_LINES = (
    "`validate-phase3-export-uapi-survey.py`",
    f"`{HEADER_GOVERNANCE.as_posix()}`",
    f"`{LINUX_HEADER.as_posix()}`",
    f"`{ABI_HEADER.as_posix()}`",
    f"`{DUMP_GATE}`",
)
REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`Documentation/zigux/phase3-linux-zigux-header-governance.md`",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
    "`include/linux/zigux.h`",
    "`include/zigux/abi.h`",
)
HEADER_GOVERNANCE_MARKERS = (
    "`PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`",
    "`PHASE3_ZIGUX_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md`",
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`include/zigux/abi.h`",
)


def norm_lines(text: str) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- ") or line.startswith("* "):
            line = line[2:].strip()
        out.append(line)
    return out


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def require_exact(issues: list[str], text: str, prefix: str, marker: str) -> None:
    count = norm_lines(text).count(marker)
    if count == 1:
        return
    if count == 0:
        issues.append(f"missing_{prefix}:{marker}")
    else:
        issues.append(f"duplicate_{prefix}:{count}:{marker}")


def require_one_of(issues: list[str], text: str, prefix: str, markers: tuple[str, ...]) -> None:
    matches = [m for m in markers if norm_lines(text).count(m) > 0]
    if len(matches) == 1:
        return
    if not matches:
        issues.append(f"missing_{prefix}:{'|'.join(markers)}")
    else:
        issues.append(f"duplicate_{prefix}:{len(matches)}:{'|'.join(markers)}")


def require_contains(issues: list[str], text: str, prefix: str, marker: str) -> None:
    if marker not in text:
        issues.append(f"missing_{prefix}:{marker}")


def backtick_value(text: str, key: str) -> list[str]:
    prefix = f"`{key}="
    return [line[len(prefix):-1] for line in norm_lines(text) if line.startswith(prefix) and line.endswith("`")]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in (
        SURVEY,
        DOCS_README,
        REVIEW_CHECKLIST,
        SCRIPTS_README,
        WORKFLOW,
        HEADER_GOVERNANCE,
        LINUX_HEADER,
        ABI_HEADER,
        EXPORT_SHIM,
        UAPI_VERSION,
        UAPI_DEV_T,
        ABI_SLICE,
        ABI_NEXT_STEP,
        BUILD_FILE,
        ABI_DUMP,
        MAKEFILE,
        VALIDATOR,
    ):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")

    survey_path = root / SURVEY
    if not survey_path.exists():
        return issues
    survey_text = survey_path.read_text(encoding="utf-8")

    require_one_of(issues, survey_text, "survey_provenance", PROVENANCE)
    for marker in SURVEY_LINES:
        require_exact(issues, survey_text, "survey_marker", marker)
    for marker in FORBIDDEN_SURVEY_MARKERS:
        if marker in survey_text:
            issues.append(f"forbidden_survey_marker:{marker}")

    for key, rel in (
        ("PHASE3_EXPORT_SHIM_BLOB_SHA", EXPORT_SHIM),
        ("PHASE3_UAPI_VERSION_BLOB_SHA", UAPI_VERSION),
        ("PHASE3_UAPI_DEV_T_BLOB_SHA", UAPI_DEV_T),
    ):
        values = backtick_value(survey_text, key)
        if len(values) != 1:
            issues.append(f"missing_survey_marker:`{key}=<sha>`")
            continue
        expected = blob_sha(root / rel)
        if values[0] != expected:
            issues.append(f"stale_survey_blob:{key}:{values[0]}!={expected}")

    for rel, markers in {
        EXPORT_SHIM: (
            "pub const Header = uapi_version.Header;",
            "pub const HeaderCompatibility = uapi_version.Compatibility;",
            "pub const HeaderAcceptance = uapi_version.AcceptedHeader;",
            "pub const HeaderEvaluation = uapi_version.HeaderEvaluation;",
            "pub fn compatibilityStatus(",
            "pub fn evaluateHeader(",
            "pub fn extendsBoundary(header_value: Header) bool {",
            "pub fn requestedExtraBytes(header_value: Header) ?u32 {",
            'test "phase3 export shim relays compatibility through explicit status packets" {',
            'test "phase3 export shim evaluation keeps compatibility evidence and status together" {',
        ),
        UAPI_VERSION: (
            "pub const Compatibility = enum {",
            "future_compatible",
            "pub const AcceptedHeader = struct {",
            "pub const HeaderEvaluation = struct {",
            "pub fn compatibility(header: Header) ?Compatibility {",
            "pub fn acceptHeader(header: Header) ?AcceptedHeader {",
            "pub fn evaluateHeader(header: Header) HeaderEvaluation {",
            "pub fn requestedExtraBytes(self: @This()) ?u32 {",
            'test "phase3 uapi evaluation keeps requested boundary shape explicit" {',
        ),
        UAPI_DEV_T: (
            "pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {",
            "pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {",
            'test "phase3 uapi dev_t starter keeps encode and range parity explicit" {',
        ),
        ABI_DUMP: (
            'try writer.writeAll("{\\\"abi_version\\\":");',
            'try writer.writeAll(",\\\"constants\\\":{");',
            'try writer.writeAll("},\\\"structs\\\":{");',
            "try writeStruct(writer, decl.name, value);",
        ),
        HEADER_GOVERNANCE: (
            "`PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`",
            "`PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`",
            "live `zigux/uapi/` now ships both `version.zig` and `dev_t.zig`",
            "the dedicated export/UAPI survey still owns the narrower starter-boundary claims it proves directly",
        ),
        LINUX_HEADER: (
            "#ifndef _LINUX_ZIGUX_H",
            '#include "../zigux/abi.h"',
            '#include "../zigux/dev_t.h"',
            "zigux_export_status_ok",
        ),
        ABI_HEADER: (
            "#ifndef _ZIGUX_ABI_H",
            "#define ZIGUX_ABI_VERSION",
            "struct zigux_boundary_header {",
            "struct zigux_export_status {",
        ),
        MAKEFILE: (
            "phase3-validate:",
            "phase3-interop:",
            "$(PYTHON) scripts/zigux/run-phase3-checks.py",
            "phase3-abi:",
            "$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
            DUMP_GATE,
            "phase3: phase3-validate phase3-abi phase3-interop",
        ),
    }.items():
        if not (root / rel).exists():
            continue
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{rel.as_posix()}:{marker}")

    docs_text = (root / DOCS_README).read_text(encoding="utf-8")
    for marker in DOCS_README_LINES:
        require_exact(issues, docs_text, "docs_root_marker", marker)

    review_checklist_text = (root / REVIEW_CHECKLIST).read_text(encoding="utf-8")
    for marker in REVIEW_CHECKLIST_MARKERS:
        require_contains(issues, review_checklist_text, "review_checklist_marker", marker)

    abi_slice_text = (root / ABI_SLICE).read_text(encoding="utf-8")
    for marker in ABI_SLICE_LINES:
        require_exact(issues, abi_slice_text, "abi_slice_marker", marker)

    abi_next_step_text = (root / ABI_NEXT_STEP).read_text(encoding="utf-8")
    for marker in ABI_NEXT_STEP_LINES:
        require_exact(issues, abi_next_step_text, "abi_next_step_marker", marker)

    scripts_readme_text = (root / SCRIPTS_README).read_text(encoding="utf-8")
    for marker in SCRIPTS_README_LINES:
        require_exact(issues, scripts_readme_text, "scripts_readme_marker", marker)
    for marker in FORBIDDEN_SCRIPTS_README_MARKERS:
        if marker in scripts_readme_text:
            issues.append(f"forbidden_scripts_readme_marker:{marker}")

    workflow_lines = [line.strip() for line in (root / WORKFLOW).read_text(encoding="utf-8").splitlines()]
    for marker in (
        "- name: Validate Phase 3 export/UAPI survey",
        "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
        "- name: Self-test Phase 3 export/UAPI survey",
        "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
        "- name: Check discovered Phase 3 parity",
        "run: python3 scripts/zigux/run-phase3-checks.py",
        "- name: Run Phase 3 ABI/interp substrate tests",
        "run: zig build phase3-test --build-file zigux/tests/build.zig",
    ):
        count = workflow_lines.count(marker)
        if count == 0:
            issues.append(f"missing_workflow_marker:{marker}")
        elif count != 1:
            issues.append(f"duplicate_workflow_marker:{count}:{marker}")

    return issues


def build_valid_workspace(root: Path) -> None:
    write(root / EXPORT_SHIM, "\n".join((
        'const uapi_version = @import("uapi_version");',
        "pub const Header = uapi_version.Header;",
        "pub const HeaderCompatibility = uapi_version.Compatibility;",
        "pub const HeaderAcceptance = uapi_version.AcceptedHeader;",
        "pub const HeaderEvaluation = uapi_version.HeaderEvaluation;",
        "pub fn compatibilityStatus() void {}",
        "pub fn evaluateHeader() void {}",
        "pub fn extendsBoundary(header_value: Header) bool { _ = header_value; return false; }",
        "pub fn requestedExtraBytes(header_value: Header) ?u32 { _ = header_value; return null; }",
        'test "phase3 export shim relays compatibility through explicit status packets" {}',
        'test "phase3 export shim evaluation keeps compatibility evidence and status together" {}',
        "",
    )))
    write(root / UAPI_VERSION, "\n".join((
        "pub const Header = extern struct {};",
        "pub const Compatibility = enum { canonical, future_compatible };",
        "pub const AcceptedHeader = struct {};",
        "pub const HeaderEvaluation = struct {",
        "    pub fn requestedExtraBytes(self: @This()) ?u32 { _ = self; return null; }",
        "};",
        "pub fn compatibility(header: Header) ?Compatibility { _ = header; return null; }",
        "pub fn acceptHeader(header: Header) ?AcceptedHeader { _ = header; return null; }",
        "pub fn evaluateHeader(header: Header) HeaderEvaluation { _ = header; return .{}; }",
        'test "phase3 uapi evaluation keeps requested boundary shape explicit" {}',
        "",
    )))
    write(root / UAPI_DEV_T, "\n".join((
        "pub const EncodeError = error{};",
        "pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 { _ = major_id; _ = minor_id; return 0; }",
        "pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 { _ = major_id; _ = first_minor; _ = count; return 0; }",
        'test "phase3 uapi dev_t starter keeps encode and range parity explicit" {}',
        "",
    )))
    write(root / BUILD_FILE, "// shared phase3 build route\n")
    write(root / ABI_DUMP, "\n".join((
        'try writer.writeAll("{\\\"abi_version\\\":");',
        'try writer.writeAll(",\\\"constants\\\":{");',
        'try writer.writeAll("},\\\"structs\\\":{");',
        "try writeStruct(writer, decl.name, value);",
        "",
    )))
    write(root / MAKEFILE, "\n".join((
        "phase3-validate:",
        "phase3-interop:",
        "\t$(PYTHON) scripts/zigux/run-phase3-checks.py",
        "phase3-abi:",
        "\t$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
        f"\t{DUMP_GATE}",
        "phase3: phase3-validate phase3-abi phase3-interop",
        "",
    )))
    write(root / VALIDATOR, "# validator placeholder\n")
    write(root / HEADER_GOVERNANCE, "\n".join((
        "# Phase 3 Linux `zigux.h` Header Governance",
        "`PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`",
        "`PHASE3_ZIGUX_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`",
        "live `zigux/uapi/` now ships both `version.zig` and `dev_t.zig`",
        "the dedicated export/UAPI survey still owns the narrower starter-boundary claims it proves directly",
        "",
    )))
    write(root / LINUX_HEADER, "\n".join((
        "#ifndef _LINUX_ZIGUX_H",
        '#include "../zigux/abi.h"',
        '#include "../zigux/dev_t.h"',
        "static inline int zigux_export_status_ok(void) { return 1; }",
        "",
    )))
    write(root / ABI_HEADER, "\n".join((
        "#ifndef _ZIGUX_ABI_H",
        "#define ZIGUX_ABI_VERSION 1",
        "struct zigux_boundary_header { int size; };",
        "struct zigux_export_status { int code; };",
        "",
    )))
    write(root / DOCS_README, "\n".join((
        "- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
        "- `Documentation/zigux/phase3-linux-zigux-header-governance.md`",
        "- `scripts/zigux/validate-phase3-export-uapi-survey.py`",
        f"- `{UAPI_DEV_T.as_posix()}`",
        "- `zig build phase3-test --build-file zigux/tests/build.zig`",
        "- `make -C zigux phase3`",
        "",
    )))
    write(root / REVIEW_CHECKLIST, "\n".join((
        "- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
        "- `Documentation/zigux/phase3-linux-zigux-header-governance.md`",
        "- `scripts/zigux/validate-phase3-export-uapi-survey.py`",
        "- `include/linux/zigux.h`",
        "- `include/zigux/abi.h`",
        "",
    )))
    write(root / ABI_SLICE, "\n".join((
        f"- `{SURVEY.as_posix()}`",
        f"- `{ABI_NEXT_STEP.as_posix()}`",
        f"- `{EXPORT_SHIM.as_posix()}`",
        f"- `{UAPI_VERSION.as_posix()}`",
        f"- `{UAPI_DEV_T.as_posix()}`",
        f"- `{ABI_DUMP.as_posix()}`",
        "",
    )))
    write(root / ABI_NEXT_STEP, "\n".join((
        f"- `{SURVEY.as_posix()}`",
        f"- `{EXPORT_SHIM.as_posix()}`",
        f"- `{UAPI_VERSION.as_posix()}`",
        f"- `{UAPI_DEV_T.as_posix()}`",
        f"- `{ABI_DUMP.as_posix()}`",
        f"- `{VALIDATOR.as_posix()}`",
        "",
    )))
    write(root / SCRIPTS_README, "\n".join((
        "- `validate-phase3-export-uapi-survey.py`",
        f"- `{HEADER_GOVERNANCE.as_posix()}`",
        f"- `{LINUX_HEADER.as_posix()}`",
        f"- `{ABI_HEADER.as_posix()}`",
        f"- `{DUMP_GATE}`",
        "",
    )))
    write(root / WORKFLOW, "\n".join((
        "- name: Validate Phase 3 export/UAPI survey",
        "  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
        "- name: Self-test Phase 3 export/UAPI survey",
        "  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
        "- name: Check discovered Phase 3 parity",
        "  run: python3 scripts/zigux/run-phase3-checks.py",
        "- name: Run Phase 3 ABI/interp substrate tests",
        "  run: zig build phase3-test --build-file zigux/tests/build.zig",
        "",
    )))
    write(root / SURVEY, "\n".join((
        "# Phase 3 Export Shim and UAPI Boundary Survey",
        "",
        "## Status",
        "",
        f"- {PROVENANCE[0]}",
        *(f"- {line}" for line in SURVEY_LINES),
        f"- `PHASE3_EXPORT_SHIM_BLOB_SHA={blob_sha(root / EXPORT_SHIM)}`",
        f"- `PHASE3_UAPI_VERSION_BLOB_SHA={blob_sha(root / UAPI_VERSION)}`",
        f"- `PHASE3_UAPI_DEV_T_BLOB_SHA={blob_sha(root / UAPI_DEV_T)}`",
        "",
        "## Live Boundary",
        "",
        "The starter export shim and starter UAPI companions stay on the shared Phase 3 route.",
        "",
    )))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp:
        root = Path(tmp)
        build_valid_workspace(root)
        assert validate(root) == [], validate(root)
        case_count += 1

        write(root / UAPI_DEV_T, (root / UAPI_DEV_T).read_text(encoding="utf-8") + "// drift\n")
        issues = validate(root)
        assert len(issues) == 1 and issues[0].startswith("stale_survey_blob:PHASE3_UAPI_DEV_T_BLOB_SHA:"), issues
        build_valid_workspace(root)
        case_count += 1

        write(root / DOCS_README, (root / DOCS_README).read_text(encoding="utf-8").replace(
            "`Documentation/zigux/phase3-linux-zigux-header-governance.md`",
            "`broken`",
            1,
        ))
        assert validate(root) == ["missing_docs_root_marker:`Documentation/zigux/phase3-linux-zigux-header-governance.md`"]
        build_valid_workspace(root)
        case_count += 1

        write(root / ABI_SLICE, (root / ABI_SLICE).read_text(encoding="utf-8").replace(
            f"`{SURVEY.as_posix()}`",
            "`broken`",
            1,
        ))
        assert validate(root) == [f"missing_abi_slice_marker:`{SURVEY.as_posix()}`"]
        build_valid_workspace(root)
        case_count += 1

        write(root / ABI_SLICE, (root / ABI_SLICE).read_text(encoding="utf-8").replace(
            f"`{ABI_DUMP.as_posix()}`",
            "`broken`",
            1,
        ))
        assert validate(root) == [f"missing_abi_slice_marker:`{ABI_DUMP.as_posix()}`"]
        build_valid_workspace(root)
        case_count += 1

        write(root / ABI_NEXT_STEP, (root / ABI_NEXT_STEP).read_text(encoding="utf-8").replace(
            f"`{VALIDATOR.as_posix()}`",
            "`broken`",
            1,
        ))
        assert validate(root) == [f"missing_abi_next_step_marker:`{VALIDATOR.as_posix()}`"]
        build_valid_workspace(root)
        case_count += 1

        write(root / ABI_NEXT_STEP, (root / ABI_NEXT_STEP).read_text(encoding="utf-8").replace(
            f"`{ABI_DUMP.as_posix()}`",
            "`broken`",
            1,
        ))
        assert validate(root) == [f"missing_abi_next_step_marker:`{ABI_DUMP.as_posix()}`"]
        build_valid_workspace(root)
        case_count += 1

        write(root / REVIEW_CHECKLIST, "")
        assert validate(root) == [
            "missing_review_checklist_marker:`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
            "missing_review_checklist_marker:`Documentation/zigux/phase3-linux-zigux-header-governance.md`",
            "missing_review_checklist_marker:`scripts/zigux/validate-phase3-export-uapi-survey.py`",
            "missing_review_checklist_marker:`include/linux/zigux.h`",
            "missing_review_checklist_marker:`include/zigux/abi.h`",
        ]
        build_valid_workspace(root)
        case_count += 1

        write(root / SCRIPTS_README, "")
        issues = validate(root)
        assert "missing_scripts_readme_marker:`validate-phase3-export-uapi-survey.py`" in issues, issues
        assert f"missing_scripts_readme_marker:`{HEADER_GOVERNANCE.as_posix()}`" in issues, issues
        assert f"missing_scripts_readme_marker:`{LINUX_HEADER.as_posix()}`" in issues, issues
        assert f"missing_scripts_readme_marker:`{ABI_HEADER.as_posix()}`" in issues, issues
        assert f"missing_scripts_readme_marker:`{DUMP_GATE}`" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        (root / HEADER_GOVERNANCE).unlink()
        assert validate(root) == [f"missing_file:{HEADER_GOVERNANCE.as_posix()}"]
        build_valid_workspace(root)
        case_count += 1

        write(root / WORKFLOW, (root / WORKFLOW).read_text(encoding="utf-8").replace(
            "run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
            "run: python3 broken.py --self-test",
            1,
        ))
        assert validate(root) == ["missing_workflow_marker:run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"]
        build_valid_workspace(root)
        case_count += 1

        write(root / WORKFLOW, (root / WORKFLOW).read_text(encoding="utf-8").replace(
            "run: python3 scripts/zigux/run-phase3-checks.py",
            "run: python3 broken.py",
            1,
        ))
        assert validate(root) == ["missing_workflow_marker:run: python3 scripts/zigux/run-phase3-checks.py"]
        build_valid_workspace(root)
        case_count += 1

        write(root / SURVEY, (root / SURVEY).read_text(encoding="utf-8") + "phase3_export_uapi.zig\n")
        assert validate(root) == ["forbidden_survey_marker:phase3_export_uapi.zig"]
        build_valid_workspace(root)
        case_count += 1

        write(root / SCRIPTS_README, (root / SCRIPTS_README).read_text(encoding="utf-8") + "zigux/tests/phase3_export_uapi.zig\n")
        assert validate(root) == ["forbidden_scripts_readme_marker:zigux/tests/phase3_export_uapi.zig"]
        build_valid_workspace(root)
        case_count += 1

        write(root / MAKEFILE, "phase3-validate:\n")
        issues = validate(root)
        assert "missing_marker:zigux/Makefile:$(ZIG) build phase3-test --build-file zigux/tests/build.zig" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write(root / MAKEFILE, (root / MAKEFILE).read_text(encoding="utf-8").replace(
            "$(PYTHON) scripts/zigux/run-phase3-checks.py",
            "$(PYTHON) broken.py",
            1,
        ))
        assert validate(root) == ["missing_marker:zigux/Makefile:$(PYTHON) scripts/zigux/run-phase3-checks.py"]
        build_valid_workspace(root)
        case_count += 1

        write(root / MAKEFILE, (root / MAKEFILE).read_text(encoding="utf-8").replace(DUMP_GATE, "zig build broken --build-file zigux/tests/build.zig", 1))
        assert validate(root) == [f"missing_marker:{MAKEFILE.as_posix()}:{DUMP_GATE}"]
        build_valid_workspace(root)
        case_count += 1

        write(root / SURVEY, (root / SURVEY).read_text(encoding="utf-8").replace(
            f"`PHASE3_SHARED_DUMP_GATE={DUMP_GATE}`",
            "`PHASE3_SHARED_DUMP_GATE=broken`",
            1,
        ))
        assert validate(root) == [f"missing_survey_marker:`PHASE3_SHARED_DUMP_GATE={DUMP_GATE}`"]
        build_valid_workspace(root)
        case_count += 1

        write(root / SURVEY, (root / SURVEY).read_text(encoding="utf-8").replace(
            f"`PHASE3_SHARED_INTEROP_ROUTE={INTEROP_ROUTE}`",
            "`PHASE3_SHARED_INTEROP_ROUTE=broken`",
            1,
        ))
        assert validate(root) == [f"missing_survey_marker:`PHASE3_SHARED_INTEROP_ROUTE={INTEROP_ROUTE}`"]
        build_valid_workspace(root)
        case_count += 1

        (root / ABI_DUMP).unlink()
        assert validate(root) == [f"missing_file:{ABI_DUMP.as_posix()}"]
        build_valid_workspace(root)
        case_count += 1

        (root / LINUX_HEADER).unlink()
        assert validate(root) == [f"missing_file:{LINUX_HEADER.as_posix()}"]
        build_valid_workspace(root)
        case_count += 1

        write(root / EXPORT_SHIM, (root / EXPORT_SHIM).read_text(encoding="utf-8").replace(
            "pub fn requestedExtraBytes(header_value: Header) ?u32 { _ = header_value; return null; }\n",
            "",
            1,
        ))
        assert validate(root) == [
            "stale_survey_blob:PHASE3_EXPORT_SHIM_BLOB_SHA:"
            + backtick_value((root / SURVEY).read_text(encoding="utf-8"), "PHASE3_EXPORT_SHIM_BLOB_SHA")[0]
            + "!="
            + blob_sha(root / EXPORT_SHIM),
            "missing_marker:zigux/kernel/export_shim.zig:pub fn requestedExtraBytes(header_value: Header) ?u32 {",
        ]
        build_valid_workspace(root)
        case_count += 1

        write(root / UAPI_VERSION, (root / UAPI_VERSION).read_text(encoding="utf-8").replace(
            "pub const HeaderEvaluation = struct {\n",
            "",
            1,
        ).replace(
            "    pub fn requestedExtraBytes(self: @This()) ?u32 { _ = self; return null; }\n",
            "",
            1,
        ).replace(
            "};\n",
            "",
            1,
        ))
        issues = validate(root)
        assert issues[0].startswith("stale_survey_blob:PHASE3_UAPI_VERSION_BLOB_SHA:"), issues
        assert "missing_marker:zigux/uapi/version.zig:pub const HeaderEvaluation = struct {" in issues, issues
        assert "missing_marker:zigux/uapi/version.zig:pub fn requestedExtraBytes(self: @This()) ?u32 {" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write(root / ABI_HEADER, (root / ABI_HEADER).read_text(encoding="utf-8").replace(
            "struct zigux_export_status { int code; };",
            "",
            1,
        ))
        assert validate(root) == ["missing_marker:include/zigux/abi.h:struct zigux_export_status {"]
        case_count += 1

    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the shipped Phase 3 export/UAPI boundary packet.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("root", nargs="?")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(root)
    if issues:
        print("PHASE3_EXPORT_UAPI_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE3_EXPORT_UAPI_SURVEY=pass")
    print("PHASE3_EXPORT_UAPI_REQUIRED_FILE_COUNT=17")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SURVEY = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
KERNEL_EXPORT_GOVERNANCE = Path("Documentation/zigux/phase3-kernel-export-shim-governance.md")
HEADER_GOVERNANCE = Path("Documentation/zigux/phase3-linux-zigux-header-governance.md")
LINUX_HEADER = Path("include/linux/zigux.h")
ABI_HEADER = Path("include/zigux/abi.h")
DEV_T_HEADER = Path("include/zigux/dev_t.h")
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

REQUIRED_FILES = (
    SURVEY,
    SCRIPTS_README,
    WORKFLOW,
    KERNEL_EXPORT_GOVERNANCE,
    HEADER_GOVERNANCE,
    LINUX_HEADER,
    ABI_HEADER,
    DEV_T_HEADER,
    EXPORT_SHIM,
    UAPI_VERSION,
    UAPI_DEV_T,
    ABI_SLICE,
    ABI_NEXT_STEP,
    BUILD_FILE,
    ABI_DUMP,
    MAKEFILE,
    VALIDATOR,
)

SURVEY_ONE_OF = (
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-readback-from-public-github-fallback`",
    "`PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run`",
)
SURVEY_EXACT = (
    "`PHASE3_REVIEW_ROOT_RULE=export-uapi-growth-requires-survey-plus-shared-review-surface-refresh`",
    "`PHASE3_BUILD_ROUTE_OWNERSHIP=export-uapi-packet-owns-current-shared-phase3-build-route-wording-for-the-starter-surface`",
    f"`PHASE3_EXPORT_SHIM_PATH={EXPORT_SHIM.as_posix()}`",
    f"`PHASE3_UAPI_VERSION_PATH={UAPI_VERSION.as_posix()}`",
    f"`PHASE3_UAPI_DEV_T_PATH={UAPI_DEV_T.as_posix()}`",
    f"`PHASE3_DEV_T_HEADER_PATH={DEV_T_HEADER.as_posix()}`",
    f"`PHASE3_SHARED_BUILD_PATH={BUILD_FILE.as_posix()}`",
    f"`PHASE3_SHARED_DUMP_PATH={ABI_DUMP.as_posix()}`",
    f"`PHASE3_SHARED_DUMP_GATE={DUMP_GATE}`",
    f"`PHASE3_SHARED_INTEROP_ROUTE={INTEROP_ROUTE}`",
    f"`PHASE3_SHARED_INTEROP_MAKE={INTEROP_MAKE}`",
    f"`PHASE3_SHARED_MAKEFILE_PATH={MAKEFILE.as_posix()}`",
    f"`PHASE3_EXPORT_UAPI_VALIDATOR_PATH={VALIDATOR.as_posix()}`",
    f"`PHASE3_EXPORT_UAPI_WORKFLOW_PATH={WORKFLOW.as_posix()}`",
)
REVIEW_OWNERSHIP_LINES = (
    "`Documentation/zigux/phase3-kernel-export-shim-governance.md` owns the kernel-facing relay ownership for `zigux/kernel/export_shim.zig`, while this survey owns its own wording, its packet-local validator, and the shared `phase3-interop`, `phase3-test`, and `phase3-dump` route reminders that prove the currently shipped starter surface.",
    "`Documentation/zigux/phase3-linux-zigux-header-governance.md` still owns the Linux-facing aggregation-header growth rules for `include/linux/zigux.h`, whose starter boundary-header relays now expose both the canonical and forward-compatible constructor names needed to keep the C-facing side aligned with the shipped UAPI contract.",
    "the broader shared ABI slice and shared Phase 3 validator still own the wider interop packet; this survey only records the export shim, the starter UAPI companions, `include/linux/zigux.h`, the paired `include/zigux/dev_t.h` contract, the shared manifest marker, the shared dump anchor, and the shared replay routes that are readable in the current export/UAPI lane.",
    "any future top-level export or UAPI growth should land with a refreshed survey, the kernel-facing governance note when `zigux/kernel/export_shim.zig` changes, and one shared review-surface refresh instead of being implied by broader Phase 3 wording alone.",
)


def normalized_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- ") or line.startswith("* "):
            line = line[2:].strip()
        lines.append(line)
    return lines


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def require_exact(issues: list[str], text: str, prefix: str, marker: str) -> None:
    count = normalized_lines(text).count(marker)
    if count == 0:
        issues.append(f"missing_{prefix}:{marker}")
    elif count != 1:
        issues.append(f"duplicate_{prefix}:{count}:{marker}")


def require_contains(issues: list[str], text: str, prefix: str, marker: str) -> None:
    if marker not in text:
        issues.append(f"missing_{prefix}:{marker}")


def require_one_of(issues: list[str], text: str, prefix: str, markers: tuple[str, ...]) -> None:
    hits = [marker for marker in markers if normalized_lines(text).count(marker)]
    if not hits:
        issues.append(f"missing_{prefix}:{'|'.join(markers)}")
    elif len(hits) != 1:
        issues.append(f"duplicate_{prefix}:{len(hits)}:{'|'.join(markers)}")


def extract_section(text: str, heading: str, next_heading: str) -> str | None:
    start = text.find(f"\n{heading}\n")
    if start == -1 and text.startswith(f"{heading}\n"):
        start = 0
    if start == -1:
        return None
    if start == 0:
        section = text[len(f"{heading}\n"):]
    else:
        section = text[start + len(f"\n{heading}\n"):]
    stop = section.find(f"\n{next_heading}\n")
    return section if stop == -1 else section[:stop]


def backtick_value(text: str, key: str) -> list[str]:
    prefix = f"`{key}="
    return [line[len(prefix):-1] for line in normalized_lines(text) if line.startswith(prefix) and line.endswith("`")]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    survey_text = (root / SURVEY).read_text(encoding="utf-8")
    require_one_of(issues, survey_text, "survey_provenance", SURVEY_ONE_OF)
    for marker in SURVEY_EXACT:
        require_exact(issues, survey_text, "survey_marker", marker)

    review_ownership = extract_section(survey_text, "## Review Ownership", "## Current Gap")
    if review_ownership is None:
        issues.append("missing_survey_section:## Review Ownership")
    else:
        for marker in REVIEW_OWNERSHIP_LINES:
            require_contains(issues, review_ownership, "review_ownership_rule", marker)

    for key, rel in (
        ("PHASE3_EXPORT_SHIM_BLOB_SHA", EXPORT_SHIM),
        ("PHASE3_UAPI_VERSION_BLOB_SHA", UAPI_VERSION),
        ("PHASE3_UAPI_DEV_T_BLOB_SHA", UAPI_DEV_T),
        ("PHASE3_DEV_T_HEADER_BLOB_SHA", DEV_T_HEADER),
    ):
        values = backtick_value(survey_text, key)
        if len(values) != 1:
            issues.append(f"missing_survey_marker:`{key}=<sha>`")
        elif values[0] != blob_sha(root / rel):
            issues.append(f"stale_survey_blob:{key}:{values[0]}!={blob_sha(root / rel)}")

    exact_lists = {
        SCRIPTS_README: (
            "`validate-phase3-export-uapi-survey.py`",
            "`Documentation/zigux/phase3-linux-zigux-header-governance.md`",
            "`include/linux/zigux.h`",
            "`include/zigux/abi.h`",
            f"`{DUMP_GATE}`",
        ),
        ABI_SLICE: (
            "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
            "`Documentation/zigux/phase3-abi-h-boundary-next-step.md`",
            "`zigux/kernel/export_shim.zig`",
            "`zigux/uapi/version.zig`",
            "`zigux/uapi/dev_t.zig`",
            "`zigux/tests/phase3_abi_dump.zig`",
        ),
        ABI_NEXT_STEP: (
            "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
            "`zigux/kernel/export_shim.zig`",
            "`zigux/uapi/version.zig`",
            "`zigux/uapi/dev_t.zig`",
            "`zigux/tests/phase3_abi_dump.zig`",
            "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
        ),
        MAKEFILE: (
            "phase3-validate:",
            "$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
            "$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py",
            "phase3-interop:",
            "$(PYTHON) scripts/zigux/run-phase3-checks.py",
            "phase3-abi:",
            "$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
            DUMP_GATE,
            "phase3: phase3-validate phase3-abi phase3-interop",
        ),
    }
    for rel, markers in exact_lists.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            require_exact(issues, text, rel.stem, marker)

    contains_lists = {
        KERNEL_EXPORT_GOVERNANCE: (
            "starter `dev_t` companion ownership stays in `zigux/uapi/dev_t.zig` and `include/zigux/dev_t.h`",
            "new kernel-facing wrapper names without matching shared replay or manifest-backed evidence should be treated as churn, not Phase 3 closure",
        ),
        HEADER_GOVERNANCE: (
            "`PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`",
            "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
            "`include/zigux/abi.h`",
        ),
        LINUX_HEADER: (
            '#include "../zigux/dev_t.h"',
            "zigux_export_status_ok",
        ),
        ABI_HEADER: (
            "#define ZIGUX_ABI_VERSION",
            "struct zigux_export_status {",
        ),
        DEV_T_HEADER: (
            "#define ZIGUX_DEV_MINOR_BITS 20U",
            "static inline uint32_t zigux_mkdev(uint32_t major_id, uint32_t minor_id)",
            "static inline uint32_t zigux_minor(uint32_t dev)",
        ),
        EXPORT_SHIM: (
            "pub fn compatibilityStatus(",
            "pub fn requestedExtraBytes(header_value: Header) ?u32 {",
        ),
        UAPI_VERSION: (
            "pub const HeaderEvaluation = struct {",
            "pub fn requestedExtraBytes(self: @This()) ?u32 {",
        ),
        UAPI_DEV_T: (
            "pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {",
            "pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {",
        ),
        ABI_DUMP: (
            'try writer.writeAll("{\\\"abi_version\\\":");',
            "try writeStruct(writer, decl.name, value);",
        ),
    }
    for rel, markers in contains_lists.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            require_contains(issues, text, f"marker:{rel.as_posix()}", marker)

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
    write(root / EXPORT_SHIM, "pub fn compatibilityStatus() void {}\npub fn requestedExtraBytes(header_value: Header) ?u32 { _ = header_value; return null; }\n")
    write(root / UAPI_VERSION, "pub const HeaderEvaluation = struct {\n    pub fn requestedExtraBytes(self: @This()) ?u32 { _ = self; return null; }\n};\n")
    write(root / UAPI_DEV_T, "pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 { _ = major_id; _ = minor_id; return 0; }\npub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 { _ = major_id; _ = first_minor; _ = count; return 0; }\n")
    write(root / DEV_T_HEADER, "#define ZIGUX_DEV_MINOR_BITS 20U\nstatic inline uint32_t zigux_mkdev(uint32_t major_id, uint32_t minor_id) { return major_id + minor_id; }\nstatic inline uint32_t zigux_minor(uint32_t dev) { return dev; }\n")
    write(root / KERNEL_EXPORT_GOVERNANCE, "starter `dev_t` companion ownership stays in `zigux/uapi/dev_t.zig` and `include/zigux/dev_t.h`\nnew kernel-facing wrapper names without matching shared replay or manifest-backed evidence should be treated as churn, not Phase 3 closure\n")
    write(root / HEADER_GOVERNANCE, "`PHASE3_ZIGUX_H_PATH=include/linux/zigux.h`\n`Documentation/zigux/phase3-export-uapi-boundary-survey.md`\n`include/zigux/abi.h`\n")
    write(root / LINUX_HEADER, '#include "../zigux/dev_t.h"\nstatic inline int zigux_export_status_ok(void) { return 1; }\n')
    write(root / ABI_HEADER, "#define ZIGUX_ABI_VERSION 1\nstruct zigux_export_status { int code; };\n")
    write(root / BUILD_FILE, "// build\n")
    write(root / ABI_DUMP, 'try writer.writeAll("{\\\"abi_version\\\":");\ntry writeStruct(writer, decl.name, value);\n')
    write(root / SCRIPTS_README, f"- `validate-phase3-export-uapi-survey.py`\n- `Documentation/zigux/phase3-linux-zigux-header-governance.md`\n- `include/linux/zigux.h`\n- `include/zigux/abi.h`\n- `{DUMP_GATE}`\n")
    write(root / ABI_SLICE, "- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`\n- `Documentation/zigux/phase3-abi-h-boundary-next-step.md`\n- `zigux/kernel/export_shim.zig`\n- `zigux/uapi/version.zig`\n- `zigux/uapi/dev_t.zig`\n- `zigux/tests/phase3_abi_dump.zig`\n")
    write(root / ABI_NEXT_STEP, "- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`\n- `zigux/kernel/export_shim.zig`\n- `zigux/uapi/version.zig`\n- `zigux/uapi/dev_t.zig`\n- `zigux/tests/phase3_abi_dump.zig`\n- `scripts/zigux/validate-phase3-export-uapi-survey.py`\n")
    write(root / MAKEFILE, f"phase3-validate:\n\t$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test\n\t$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py\nphase3-interop:\n\t$(PYTHON) scripts/zigux/run-phase3-checks.py\nphase3-abi:\n\t$(ZIG) build phase3-test --build-file zigux/tests/build.zig\n\t{DUMP_GATE}\nphase3: phase3-validate phase3-abi phase3-interop\n")
    write(root / WORKFLOW, "- name: Validate Phase 3 export/UAPI survey\n  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py\n- name: Self-test Phase 3 export/UAPI survey\n  run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test\n- name: Check discovered Phase 3 parity\n  run: python3 scripts/zigux/run-phase3-checks.py\n- name: Run Phase 3 ABI/interp substrate tests\n  run: zig build phase3-test --build-file zigux/tests/build.zig\n")
    write(root / VALIDATOR, "# placeholder\n")

    write(
        root / SURVEY,
        "\n".join(
            [
                "# Phase 3 Export Shim and UAPI Boundary Survey",
                "",
                "## Status",
                "",
                f"- {SURVEY_ONE_OF[0]}",
                *(f"- {marker}" for marker in SURVEY_EXACT),
                f"- `PHASE3_EXPORT_SHIM_BLOB_SHA={blob_sha(root / EXPORT_SHIM)}`",
                f"- `PHASE3_UAPI_VERSION_BLOB_SHA={blob_sha(root / UAPI_VERSION)}`",
                f"- `PHASE3_UAPI_DEV_T_BLOB_SHA={blob_sha(root / UAPI_DEV_T)}`",
                f"- `PHASE3_DEV_T_HEADER_BLOB_SHA={blob_sha(root / DEV_T_HEADER)}`",
                "",
                "## Review Ownership",
                "",
                *(f"- {line}" for line in REVIEW_OWNERSHIP_LINES),
                "",
                "## Current Gap",
                "",
                "- current gap placeholder",
                "",
            ]
        ),
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_") as tmp:
        root = Path(tmp)
        build_valid_workspace(root)
        assert validate(root) == [], validate(root)
        case_count += 1

        write(root / SURVEY, (root / SURVEY).read_text(encoding="utf-8").replace(f"- `PHASE3_DEV_T_HEADER_PATH={DEV_T_HEADER.as_posix()}`\n", "", 1))
        assert validate(root) == [f"missing_survey_marker:`PHASE3_DEV_T_HEADER_PATH={DEV_T_HEADER.as_posix()}`"]
        build_valid_workspace(root)
        case_count += 1

        write(root / DEV_T_HEADER, (root / DEV_T_HEADER).read_text(encoding="utf-8") + "/* drift */\n")
        issues = validate(root)
        assert len(issues) == 1 and issues[0].startswith("stale_survey_blob:PHASE3_DEV_T_HEADER_BLOB_SHA:"), issues
        build_valid_workspace(root)
        case_count += 1

        write(root / SCRIPTS_README, "")
        issues = validate(root)
        assert "missing_README:`validate-phase3-export-uapi-survey.py`" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write(root / MAKEFILE, "phase3-validate:\n")
        issues = validate(root)
        assert "missing_Makefile:$(PYTHON) scripts/zigux/validate-phase3-export-uapi-survey.py --self-test" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write(root / WORKFLOW, "")
        issues = validate(root)
        assert "missing_workflow_marker:run: python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write(root / KERNEL_EXPORT_GOVERNANCE, "")
        issues = validate(root)
        assert "missing_marker:Documentation/zigux/phase3-kernel-export-shim-governance.md:starter `dev_t` companion ownership stays in `zigux/uapi/dev_t.zig` and `include/zigux/dev_t.h`" in issues, issues
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
    print(f"PHASE3_EXPORT_UAPI_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

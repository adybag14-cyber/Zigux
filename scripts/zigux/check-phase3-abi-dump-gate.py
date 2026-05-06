#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
DOC_REL = "Documentation/zigux/phase3-abi-slice.md"
BUILD_REL = "zigux/tests/build.zig"
MAKEFILE_REL = "zigux/Makefile"
DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
DUMP_GATE = "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig"
BUILD_STEP = 'b.step("phase3-dump"'
MAKEFILE_TARGET = "phase3-validate"
MAKEFILE_SELFTEST_CMD = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test"
)
MAKEFILE_LIVE_CMD = "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py"
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"
DOC_EXACT_MARKERS = (
    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice",
)
DOC_PREFIX_MARKERS = (
    "PHASE3_EXPORT_SCOPE=",
    "PHASE3_EXPORT_SHIM_BLOB_SHA=",
    "PHASE3_UAPI_SCOPE=",
    "PHASE3_UAPI_VERSION_BLOB_SHA=",
)


def _normalized_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()
        if line.startswith("`") and line.endswith("`") and len(line) >= 2:
            line = line[1:-1]
        lines.append(line)
    return lines


def _line_count(text: str, needle: str) -> int:
    return sum(1 for line in _normalized_lines(text) if line == needle)


def _prefix_count(text: str, prefix: str) -> int:
    return sum(1 for line in _normalized_lines(text) if line.startswith(prefix))


def _collect_makefile_target_lines(text: str, target: str) -> list[str] | None:
    in_target = False
    lines: list[str] = []
    target_header = f"{target}:"
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not in_target:
            if stripped == target_header:
                in_target = True
            continue
        if stripped.endswith(":") and not raw_line.startswith((" ", "\t")):
            break
        lines.append(stripped)
    return lines if in_target else None


def _command_count(lines: list[str], command: str) -> int:
    return sum(1 for line in lines if line == command)


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    doc_path = root / DOC_REL
    build_path = root / BUILD_REL
    makefile_path = root / MAKEFILE_REL
    dump_path = root / DUMP_REL
    manifest_path = root / MANIFEST_REL

    try:
        doc_text = doc_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_doc:{DOC_REL}"]

    marker_count = _line_count(doc_text, DUMP_GATE)
    if marker_count == 0:
        issues.append(f"missing_doc_marker:{DUMP_GATE}")
    elif marker_count != 1:
        issues.append(f"duplicate_doc_marker:{DUMP_GATE}")

    for marker in DOC_EXACT_MARKERS:
        exact_count = _line_count(doc_text, marker)
        if exact_count == 0:
            issues.append(f"missing_doc_marker:{marker}")
        elif exact_count != 1:
            issues.append(f"duplicate_doc_marker:{marker}")

    for prefix in DOC_PREFIX_MARKERS:
        prefix_count = _prefix_count(doc_text, prefix)
        if prefix_count == 0:
            issues.append(f"missing_doc_prefix:{prefix}")
        elif prefix_count != 1:
            issues.append(f"duplicate_doc_prefix:{prefix}")

    try:
        build_text = build_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_build:{BUILD_REL}")
    else:
        if BUILD_STEP not in build_text:
            issues.append(f"missing_build_step:{BUILD_REL}:phase3-dump")

    try:
        makefile_text = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_makefile:{MAKEFILE_REL}")
    else:
        target_lines = _collect_makefile_target_lines(makefile_text, MAKEFILE_TARGET)
        if target_lines is None:
            issues.append(f"missing_makefile_target:{MAKEFILE_TARGET}")
        else:
            selftest_count = _command_count(target_lines, MAKEFILE_SELFTEST_CMD)
            if selftest_count == 0:
                issues.append(f"missing_makefile_command:{MAKEFILE_TARGET}:{MAKEFILE_SELFTEST_CMD}")
            elif selftest_count != 1:
                issues.append(
                    f"duplicate_makefile_command:{MAKEFILE_TARGET}:{selftest_count}:{MAKEFILE_SELFTEST_CMD}"
                )

            live_count = _command_count(target_lines, MAKEFILE_LIVE_CMD)
            if live_count == 0:
                issues.append(f"missing_makefile_command:{MAKEFILE_TARGET}:{MAKEFILE_LIVE_CMD}")
            elif live_count != 1:
                issues.append(
                    f"duplicate_makefile_command:{MAKEFILE_TARGET}:{live_count}:{MAKEFILE_LIVE_CMD}"
                )

    if not dump_path.exists():
        issues.append(f"missing_dump:{DUMP_REL}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"missing_manifest:{MANIFEST_REL}")
    else:
        files = manifest.get("files")
        if not isinstance(files, list) or DUMP_REL not in files:
            issues.append(f"manifest_missing_file:{DUMP_REL}")
        if not isinstance(files, list) or EXPORT_SHIM_REL not in files:
            issues.append(f"manifest_missing_file:{EXPORT_SHIM_REL}")
        if not isinstance(files, list) or UAPI_VERSION_REL not in files:
            issues.append(f"manifest_missing_file:{UAPI_VERSION_REL}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_dump_gate_") as tmp:
        root = Path(tmp)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests/fixtures").mkdir(parents=True, exist_ok=True)
        (root / "zigux/kernel").mkdir(parents=True, exist_ok=True)
        (root / "zigux/uapi").mkdir(parents=True, exist_ok=True)

        (root / DOC_REL).write_text(
            "\n".join(
                [
                    "# Phase 3 ABI Substrate Slice",
                    "PHASE3_EXPORT_SCOPE=shim-only starter nested inside the ABI substrate slice",
                    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
                    "PHASE3_EXPORT_SHIM_BLOB_SHA=deadbeef",
                    "PHASE3_UAPI_SCOPE=version-and-boundary-header starter nested inside the ABI substrate slice",
                    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
                    "PHASE3_UAPI_VERSION_BLOB_SHA=cafebabe",
                    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice",
                    DUMP_GATE,
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / BUILD_REL).write_text(
            '\n'.join(['const dump = b.step("phase3-dump", "Run dump");', ""]),
            encoding="utf-8",
            newline="\n",
        )
        (root / MAKEFILE_REL).write_text(
            "\n".join(
                [
                    "phase3-validate:",
                    f"\t{MAKEFILE_SELFTEST_CMD}",
                    f"\t{MAKEFILE_LIVE_CMD}",
                    "phase3-abi:",
                    "\t@true",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / DUMP_REL).write_text("// dump\n", encoding="utf-8", newline="\n")
        (root / EXPORT_SHIM_REL).write_text("// export shim\n", encoding="utf-8", newline="\n")
        (root / UAPI_VERSION_REL).write_text("// uapi version\n", encoding="utf-8", newline="\n")
        (root / MANIFEST_REL).write_text(
            json.dumps({"files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL]}),
            encoding="utf-8",
            newline="\n",
        )

        assert validate(root) == []

        (root / DOC_REL).write_text("# Phase 3 ABI Substrate Slice\n", encoding="utf-8", newline="\n")
        (root / MAKEFILE_REL).write_text(
            "\n".join(
                [
                    "phase3-validate:",
                    f"\t{MAKEFILE_LIVE_CMD}",
                    "phase3-abi:",
                    "\t@true",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"missing_doc_marker:{DUMP_GATE}" in issues
        assert "missing_doc_marker:PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig" in issues
        assert "missing_doc_prefix:PHASE3_EXPORT_SHIM_BLOB_SHA=" in issues
        assert "missing_doc_marker:PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig" in issues
        assert "missing_doc_prefix:PHASE3_UAPI_VERSION_BLOB_SHA=" in issues
        assert "missing_doc_marker:PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice" in issues
        assert (
            f"missing_makefile_command:{MAKEFILE_TARGET}:{MAKEFILE_SELFTEST_CMD}" in issues
        )

        (root / DOC_REL).write_text(
            "\n".join(
                [
                    "PHASE3_EXPORT_SCOPE=shim-only starter nested inside the ABI substrate slice",
                    "PHASE3_EXPORT_SCOPE=shim-only starter nested inside the ABI substrate slice",
                    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
                    "PHASE3_EXPORT_SHIM_BLOB_SHA=deadbeef",
                    "PHASE3_UAPI_SCOPE=version-and-boundary-header starter nested inside the ABI substrate slice",
                    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
                    "PHASE3_UAPI_VERSION_BLOB_SHA=cafebabe",
                    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice",
                    DUMP_GATE,
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / MAKEFILE_REL).write_text(
            "\n".join(
                [
                    "phase3-validate:",
                    f"\t{MAKEFILE_SELFTEST_CMD}",
                    f"\t{MAKEFILE_LIVE_CMD}",
                    f"\t{MAKEFILE_LIVE_CMD}",
                    "phase3-abi:",
                    "\t@true",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert "duplicate_doc_prefix:PHASE3_EXPORT_SCOPE=" in issues
        assert (
            f"duplicate_makefile_command:{MAKEFILE_TARGET}:2:{MAKEFILE_LIVE_CMD}" in issues
        )

        (root / DOC_REL).write_text(
            "\n".join(
                [
                    "# Phase 3 ABI Substrate Slice",
                    "PHASE3_EXPORT_SCOPE=shim-only starter nested inside the ABI substrate slice",
                    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
                    "PHASE3_EXPORT_SHIM_BLOB_SHA=deadbeef",
                    "PHASE3_UAPI_SCOPE=version-and-boundary-header starter nested inside the ABI substrate slice",
                    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
                    "PHASE3_UAPI_VERSION_BLOB_SHA=cafebabe",
                    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice",
                    DUMP_GATE,
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / MAKEFILE_REL).write_text(
            "\n".join(
                [
                    "phase3-validate:",
                    f"\t{MAKEFILE_SELFTEST_CMD}",
                    "phase3-abi:",
                    "\t@true",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / MANIFEST_REL).write_text(
            json.dumps({"files": [DUMP_REL, EXPORT_SHIM_REL]}),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"manifest_missing_file:{UAPI_VERSION_REL}" in issues
        assert f"missing_makefile_command:{MAKEFILE_TARGET}:{MAKEFILE_LIVE_CMD}" in issues

    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")
    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the published Phase 3 ABI dump gate markers.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated self-test coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_ABI_DUMP_GATE=fail")
        print("PHASE3_ABI_DUMP_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_ABI_DUMP_GATE_ISSUES_END")
        return 1

    print("PHASE3_ABI_DUMP_GATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

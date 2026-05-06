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
DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
DUMP_GATE = "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig"
BUILD_STEP = 'b.step("phase3-dump"'
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


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    doc_path = root / DOC_REL
    build_path = root / BUILD_REL
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
        issues = validate(root)
        assert f"missing_doc_marker:{DUMP_GATE}" in issues
        assert "missing_doc_marker:PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig" in issues
        assert "missing_doc_prefix:PHASE3_EXPORT_SHIM_BLOB_SHA=" in issues
        assert "missing_doc_marker:PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig" in issues
        assert "missing_doc_prefix:PHASE3_UAPI_VERSION_BLOB_SHA=" in issues
        assert "missing_doc_marker:PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice" in issues

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
        issues = validate(root)
        assert "duplicate_doc_prefix:PHASE3_EXPORT_SCOPE=" in issues

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
        (root / MANIFEST_REL).write_text(
            json.dumps({"files": [DUMP_REL, EXPORT_SHIM_REL]}),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"manifest_missing_file:{UAPI_VERSION_REL}" in issues

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

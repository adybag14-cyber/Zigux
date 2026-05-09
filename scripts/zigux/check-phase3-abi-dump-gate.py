#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
DOCS_ROOT_REL = "Documentation/zigux/README.md"
DOC_REL = "Documentation/zigux/phase3-abi-slice.md"
BUILD_REL = "zigux/tests/build.zig"
MAKEFILE_REL = "zigux/Makefile"
DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
SELF_REL = "scripts/zigux/check-phase3-abi-dump-gate.py"
ABI_WRAPPER_REL = "scripts/zigux/check-phase3-abi.py"
DOCS_ROOT_ABI_TEST_GATE = "zig build phase3-test --build-file zigux/tests/build.zig"
DUMP_GATE = "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig"
BUILD_STEP = 'b.step("phase3-dump"'
MAKEFILE_TARGET = "phase3-validate"
MAKEFILE_SELFTEST_CMD = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test"
)
MAKEFILE_LIVE_CMD = "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py"
ABI_TARGET = "phase3-abi"
ABI_WRAPPER_CMD = "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase3-abi.py"
ABI_BUILD_CMD = "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-test --build-file zigux/tests/build.zig"
ABI_WRAPPER_MARKERS = (
    "validate-phase3-abi-bindings-syntax.py",
    "run_from_wrapper(__file__)",
)
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"
DOC_EXACT_MARKERS = (
    "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof",
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


def _backticked_or_plain_line_count(text: str, needle: str) -> int:
    return text.count(f"`{needle}`") + sum(1 for raw_line in text.splitlines() if raw_line.strip() == needle)


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

    docs_root_path = root / DOCS_ROOT_REL
    doc_path = root / DOC_REL
    build_path = root / BUILD_REL
    makefile_path = root / MAKEFILE_REL
    dump_path = root / DUMP_REL
    manifest_path = root / MANIFEST_REL
    abi_wrapper_path = root / ABI_WRAPPER_REL

    try:
        docs_root_text = docs_root_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_docs_root:{DOCS_ROOT_REL}")
    else:
        docs_root_count = _backticked_or_plain_line_count(docs_root_text, DOCS_ROOT_ABI_TEST_GATE)
        if docs_root_count == 0:
            issues.append(f"missing_docs_root_marker:{DOCS_ROOT_ABI_TEST_GATE}")
        elif docs_root_count != 1:
            issues.append(f"duplicate_docs_root_marker:{DOCS_ROOT_ABI_TEST_GATE}")

    try:
        doc_text = doc_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_doc:{DOC_REL}", *issues]

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

        abi_target_lines = _collect_makefile_target_lines(makefile_text, ABI_TARGET)
        if abi_target_lines is None:
            issues.append(f"missing_makefile_target:{ABI_TARGET}")
        else:
            wrapper_count = _command_count(abi_target_lines, ABI_WRAPPER_CMD)
            if wrapper_count == 0:
                issues.append(f"missing_makefile_command:{ABI_TARGET}:{ABI_WRAPPER_CMD}")
            elif wrapper_count != 1:
                issues.append(
                    f"duplicate_makefile_command:{ABI_TARGET}:{wrapper_count}:{ABI_WRAPPER_CMD}"
                )

            build_count = _command_count(abi_target_lines, ABI_BUILD_CMD)
            if build_count == 0:
                issues.append(f"missing_makefile_command:{ABI_TARGET}:{ABI_BUILD_CMD}")
            elif build_count != 1:
                issues.append(
                    f"duplicate_makefile_command:{ABI_TARGET}:{build_count}:{ABI_BUILD_CMD}"
                )

    if not dump_path.exists():
        issues.append(f"missing_dump:{DUMP_REL}")

    try:
        abi_wrapper_text = abi_wrapper_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_wrapper:{ABI_WRAPPER_REL}")
    else:
        for marker in ABI_WRAPPER_MARKERS:
            if marker not in abi_wrapper_text:
                issues.append(f"missing_wrapper_marker:{ABI_WRAPPER_REL}:{marker}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"missing_manifest:{MANIFEST_REL}")
    else:
        files = manifest.get("files")
        if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
            issues.append(f"invalid_manifest_files:{MANIFEST_REL}")
        else:
            if manifest.get("file_count") != len(files):
                issues.append(
                    f"stale_manifest_file_count:{MANIFEST_REL}:{manifest.get('file_count')}!={len(files)}"
                )
            counts = Counter(files)
            for rel, count in sorted(counts.items()):
                if count > 1:
                    issues.append(f"manifest_duplicate_file:{rel}:{count}")
            for rel in (DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL, SELF_REL):
                if rel not in counts:
                    issues.append(f"manifest_missing_file:{rel}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_dump_gate_") as tmp:
        root = Path(tmp)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests/fixtures").mkdir(parents=True, exist_ok=True)
        (root / "zigux/kernel").mkdir(parents=True, exist_ok=True)
        (root / "zigux/uapi").mkdir(parents=True, exist_ok=True)
        (root / ABI_WRAPPER_REL).parent.mkdir(parents=True, exist_ok=True)

        (root / DOCS_ROOT_REL).write_text(
            "\n".join(
                [
                    "# Zigux Documentation",
                    "- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-validate`, and `make -C zigux phase3` now keep the current ABI substrate reviewable.",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
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
                    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof",
                    DUMP_GATE,
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / BUILD_REL).write_text(
            "\n".join(['const dump = b.step("phase3-dump", "Run dump");', ""]),
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
                    f"\t{ABI_WRAPPER_CMD}",
                    f"\t{ABI_BUILD_CMD}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / DUMP_REL).write_text("// dump\n", encoding="utf-8", newline="\n")
        (root / ABI_WRAPPER_REL).write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "from phase3_check_lib import run_from_wrapper",
                    "",
                    'SYNTAX_CHECKER = ROOT / "scripts" / "zigux" / "validate-phase3-abi-bindings-syntax.py"',
                    'raise SystemExit(run_from_wrapper(__file__))',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / EXPORT_SHIM_REL).write_text("// export shim\n", encoding="utf-8", newline="\n")
        (root / UAPI_VERSION_REL).write_text("// uapi version\n", encoding="utf-8", newline="\n")
        (root / SELF_REL).write_text("# self\n", encoding="utf-8", newline="\n")
        (root / MANIFEST_REL).write_text(
            json.dumps({"file_count": 4, "files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL, SELF_REL]}),
            encoding="utf-8",
            newline="\n",
        )

        assert validate(root) == []

        (root / DOCS_ROOT_REL).unlink()
        issues = validate(root)
        assert f"missing_docs_root:{DOCS_ROOT_REL}" in issues
        (root / DOCS_ROOT_REL).write_text(
            "\n".join(
                [
                    "# Zigux Documentation",
                    "- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-validate`, and `make -C zigux phase3` now keep the current ABI substrate reviewable.",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        (root / DOCS_ROOT_REL).write_text(
            "\n".join(
                [
                    "# Zigux Documentation",
                    "- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-validate`, and `make -C zigux phase3` now keep the current ABI substrate reviewable.",
                    "- `zig build phase3-test --build-file zigux/tests/build.zig` stays explicit beside the Linux-style replay route.",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"duplicate_docs_root_marker:{DOCS_ROOT_ABI_TEST_GATE}" in issues
        (root / DOCS_ROOT_REL).write_text(
            "\n".join(
                [
                    "# Zigux Documentation",
                    "- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-validate`, and `make -C zigux phase3` now keep the current ABI substrate reviewable.",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )

        (root / DOC_REL).write_text("# Phase 3 ABI Substrate Slice\n", encoding="utf-8", newline="\n")
        (root / MAKEFILE_REL).write_text(
            "\n".join(
                [
                    "phase3-validate:",
                    f"\t{MAKEFILE_LIVE_CMD}",
                    "phase3-abi:",
                    f"\t{ABI_WRAPPER_CMD}",
                    f"\t{ABI_BUILD_CMD}",
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
        assert (
            "missing_doc_marker:"
            "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof"
            in issues
        )
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
                    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof",
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
                    f"\t{ABI_WRAPPER_CMD}",
                    f"\t{ABI_BUILD_CMD}",
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
                    f"\t{ABI_WRAPPER_CMD}",
                    f"\t{ABI_BUILD_CMD}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / MANIFEST_REL).write_text(
            json.dumps({"file_count": 3, "files": [DUMP_REL, EXPORT_SHIM_REL, SELF_REL]}),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"manifest_missing_file:{UAPI_VERSION_REL}" in issues
        assert f"missing_makefile_command:{MAKEFILE_TARGET}:{MAKEFILE_LIVE_CMD}" in issues
        assert (
            "missing_doc_marker:"
            "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof"
            in issues
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
                    "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof",
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
                    "phase3-abi:",
                    f"\t{ABI_WRAPPER_CMD}",
                    f"\t{ABI_BUILD_CMD}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / BUILD_REL).write_text(
            "\n".join(['const test = b.step("phase3-test", "Run test");', ""]),
            encoding="utf-8",
            newline="\n",
        )
        (root / MANIFEST_REL).write_text(
            json.dumps({"file_count": 4, "files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL, SELF_REL]}),
            encoding="utf-8",
            newline="\n",
        )
        (root / DUMP_REL).unlink()
        issues = validate(root)
        assert f"missing_build_step:{BUILD_REL}:phase3-dump" in issues
        assert f"missing_dump:{DUMP_REL}" in issues

        (root / BUILD_REL).write_text(
            "\n".join(['const dump = b.step("phase3-dump", "Run dump");', ""]),
            encoding="utf-8",
            newline="\n",
        )
        (root / DUMP_REL).write_text("// dump\n", encoding="utf-8", newline="\n")
        (root / ABI_WRAPPER_REL).write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "from phase3_check_lib import run_from_wrapper",
                    "",
                    'raise SystemExit(run_from_wrapper(__file__))',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert (
            f"missing_wrapper_marker:{ABI_WRAPPER_REL}:validate-phase3-abi-bindings-syntax.py" in issues
        )

        (root / ABI_WRAPPER_REL).write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "",
                    "from phase3_check_lib import run_from_wrapper",
                    "",
                    'SYNTAX_CHECKER = ROOT / "scripts" / "zigux" / "validate-phase3-abi-bindings-syntax.py"',
                    'raise SystemExit(run_from_wrapper(__file__))',
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / MANIFEST_REL).write_text(
            json.dumps(
                {
                    "file_count": 3,
                    "files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL],
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"manifest_missing_file:{SELF_REL}" in issues

        (root / MANIFEST_REL).write_text(
            json.dumps(
                {
                    "file_count": 3,
                    "files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL, SELF_REL],
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"stale_manifest_file_count:{MANIFEST_REL}:3!=4" in issues

        (root / MANIFEST_REL).write_text(
            json.dumps(
                {
                    "file_count": 5,
                    "files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL, SELF_REL, DUMP_REL],
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"manifest_duplicate_file:{DUMP_REL}:2" in issues

    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")
    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=11")
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
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path


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
EXPORT_SHIM_REL = "zigux/kernel/export_shim.zig"
UAPI_VERSION_REL = "zigux/uapi/version.zig"

DOCS_ROOT_ABI_TEST_GATE = "zig build phase3-test --build-file zigux/tests/build.zig"
DOC_ABI_WRAPPER_GATE = "python3 scripts/zigux/check-phase3-abi.py"
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
MANIFEST_REQUIRED_FILES = (DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL, SELF_REL)


def _normalized_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
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
    return text.count(f"`{needle}`") + sum(1 for raw in text.splitlines() if raw.strip() == needle)


def _collect_makefile_target_lines(text: str, target: str) -> list[str] | None:
    lines: list[str] = []
    in_target = False
    header = f"{target}:"
    for raw in text.splitlines():
        stripped = raw.strip()
        if not in_target:
            if stripped == header:
                in_target = True
            continue
        if stripped.endswith(":") and not raw.startswith((" ", "\t")):
            break
        if stripped:
            lines.append(stripped)
    return lines if in_target else None


def _check_line_count(issues: list[str], text: str, marker: str, prefix: str, fn) -> None:
    count = fn(text, marker)
    if count == 0:
        issues.append(f"missing_{prefix}:{marker}")
    elif count != 1:
        issues.append(f"duplicate_{prefix}:{marker}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    docs_root = root / DOCS_ROOT_REL
    doc = root / DOC_REL
    build = root / BUILD_REL
    makefile = root / MAKEFILE_REL
    dump = root / DUMP_REL
    manifest_path = root / MANIFEST_REL
    wrapper = root / ABI_WRAPPER_REL

    try:
        docs_root_text = docs_root.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_docs_root:{DOCS_ROOT_REL}")
    else:
        _check_line_count(
            issues,
            docs_root_text,
            DOCS_ROOT_ABI_TEST_GATE,
            "docs_root_marker",
            _backticked_or_plain_line_count,
        )

    try:
        doc_text = doc.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_doc:{DOC_REL}", *issues]

    _check_line_count(issues, doc_text, DUMP_GATE, "doc_marker", _line_count)
    _check_line_count(
        issues,
        doc_text,
        DOC_ABI_WRAPPER_GATE,
        "doc_marker",
        _backticked_or_plain_line_count,
    )
    for marker in DOC_EXACT_MARKERS:
        _check_line_count(issues, doc_text, marker, "doc_marker", _line_count)
    for prefix in DOC_PREFIX_MARKERS:
        count = _prefix_count(doc_text, prefix)
        if count == 0:
            issues.append(f"missing_doc_prefix:{prefix}")
        elif count != 1:
            issues.append(f"duplicate_doc_prefix:{prefix}")

    try:
        if BUILD_STEP not in build.read_text(encoding="utf-8"):
            issues.append(f"missing_build_step:{BUILD_REL}:phase3-dump")
    except FileNotFoundError:
        issues.append(f"missing_build:{BUILD_REL}")

    try:
        makefile_text = makefile.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_makefile:{MAKEFILE_REL}")
    else:
        phase3_validate = _collect_makefile_target_lines(makefile_text, MAKEFILE_TARGET)
        if phase3_validate is None:
            issues.append(f"missing_makefile_target:{MAKEFILE_TARGET}")
        else:
            for cmd in (MAKEFILE_SELFTEST_CMD, MAKEFILE_LIVE_CMD):
                count = phase3_validate.count(cmd)
                if count == 0:
                    issues.append(f"missing_makefile_command:{MAKEFILE_TARGET}:{cmd}")
                elif count != 1:
                    issues.append(f"duplicate_makefile_command:{MAKEFILE_TARGET}:{count}:{cmd}")

        phase3_abi = _collect_makefile_target_lines(makefile_text, ABI_TARGET)
        if phase3_abi is None:
            issues.append(f"missing_makefile_target:{ABI_TARGET}")
        else:
            for cmd in (ABI_WRAPPER_CMD, ABI_BUILD_CMD):
                count = phase3_abi.count(cmd)
                if count == 0:
                    issues.append(f"missing_makefile_command:{ABI_TARGET}:{cmd}")
                elif count != 1:
                    issues.append(f"duplicate_makefile_command:{ABI_TARGET}:{count}:{cmd}")

    if not dump.exists():
        issues.append(f"missing_dump:{DUMP_REL}")

    try:
        wrapper_text = wrapper.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_wrapper:{ABI_WRAPPER_REL}")
    else:
        for marker in ABI_WRAPPER_MARKERS:
            if marker not in wrapper_text:
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
            for rel in MANIFEST_REQUIRED_FILES:
                if rel not in counts:
                    issues.append(f"manifest_missing_file:{rel}")

    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _baseline_doc() -> str:
    return "\n".join(
        [
            "# Phase 3 ABI Substrate Slice",
            "PHASE3_EXPORT_SCOPE=shim-only starter nested inside the ABI substrate slice",
            "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig",
            "PHASE3_EXPORT_SHIM_BLOB_SHA=deadbeef",
            "PHASE3_UAPI_SCOPE=version-and-boundary-header starter nested inside the ABI substrate slice",
            "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
            "PHASE3_UAPI_VERSION_BLOB_SHA=cafebabe",
            "PHASE3_EXPORT_UAPI_SURVEY_MODE=shared-abi-slice-plus-packet-local-starter-proof",
            f"- `{DOC_ABI_WRAPPER_GATE}`",
            DUMP_GATE,
            "",
        ]
    )


def _baseline_repo(root: Path) -> None:
    _write(
        root / DOCS_ROOT_REL,
        "\n".join(
            [
                "# Zigux Documentation",
                "- `zig build phase3-test --build-file zigux/tests/build.zig`, `make -C zigux phase3-validate`, and `make -C zigux phase3` now keep the current ABI substrate reviewable.",
                "",
            ]
        ),
    )
    _write(root / DOC_REL, _baseline_doc())
    _write(root / BUILD_REL, "\n".join(['const dump = b.step("phase3-dump", "Run dump");', ""]))
    _write(
        root / MAKEFILE_REL,
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
    )
    _write(root / DUMP_REL, "// dump\n")
    _write(
        root / ABI_WRAPPER_REL,
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
    )
    _write(root / EXPORT_SHIM_REL, "// export shim\n")
    _write(root / UAPI_VERSION_REL, "// uapi version\n")
    _write(root / SELF_REL, "# self\n")
    _write(
        root / MANIFEST_REL,
        json.dumps({"file_count": 4, "files": list(MANIFEST_REQUIRED_FILES)}),
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase3_abi_dump_gate_") as tmp:
        root = Path(tmp)
        _baseline_repo(root)
        assert validate(root) == []
        case_count += 1

        _write(root / DOC_REL, "# Phase 3 ABI Substrate Slice\n")
        issues = validate(root)
        assert f"missing_doc_marker:{DUMP_GATE}" in issues
        assert f"missing_doc_marker:{DOC_ABI_WRAPPER_GATE}" in issues
        case_count += 1

        _write(
            root / DOC_REL,
            _baseline_doc().replace(
                f"- `{DOC_ABI_WRAPPER_GATE}`\n",
                f"- `{DOC_ABI_WRAPPER_GATE}`\n- `{DOC_ABI_WRAPPER_GATE}`\n",
                1,
            ),
        )
        issues = validate(root)
        assert f"duplicate_doc_marker:{DOC_ABI_WRAPPER_GATE}" in issues
        case_count += 1

        _baseline_repo(root)
        _write(root / MAKEFILE_REL, "phase3-validate:\n\t%s\nphase3-abi:\n\t%s\n\t%s\n" % (MAKEFILE_LIVE_CMD, ABI_WRAPPER_CMD, ABI_BUILD_CMD))
        issues = validate(root)
        assert f"missing_makefile_command:{MAKEFILE_TARGET}:{MAKEFILE_SELFTEST_CMD}" in issues
        case_count += 1

        _baseline_repo(root)
        _write(root / BUILD_REL, 'const test = b.step("phase3-test", "Run test");\n')
        issues = validate(root)
        assert f"missing_build_step:{BUILD_REL}:phase3-dump" in issues
        case_count += 1

        _baseline_repo(root)
        _write(root / ABI_WRAPPER_REL, "from phase3_check_lib import run_from_wrapper\nraise SystemExit(run_from_wrapper(__file__))\n")
        issues = validate(root)
        assert (
            f"missing_wrapper_marker:{ABI_WRAPPER_REL}:validate-phase3-abi-bindings-syntax.py" in issues
        )
        case_count += 1

        _baseline_repo(root)
        _write(root / MANIFEST_REL, json.dumps({"file_count": 3, "files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL]}))
        issues = validate(root)
        assert f"manifest_missing_file:{SELF_REL}" in issues
        assert f"stale_manifest_file_count:{MANIFEST_REL}:3!=3" not in issues
        case_count += 1

        _baseline_repo(root)
        _write(root / MANIFEST_REL, json.dumps({"file_count": 5, "files": [DUMP_REL, EXPORT_SHIM_REL, UAPI_VERSION_REL, SELF_REL, DUMP_REL]}))
        issues = validate(root)
        assert f"manifest_duplicate_file:{DUMP_REL}:2" in issues
        assert f"stale_manifest_file_count:{MANIFEST_REL}:5!=5" not in issues
        case_count += 1

    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")
    print(f"PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT={case_count}")
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
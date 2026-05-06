#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DOC_REL = "Documentation/zigux/phase3-abi-slice.md"
BUILD_REL = "zigux/tests/build.zig"
DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
DUMP_GATE = "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig"
BUILD_STEP = 'b.step("phase3-dump"'


def _line_count(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().strip("`") == needle)


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

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_dump_gate_") as tmp:
        root = Path(tmp)
        (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux/tests/fixtures").mkdir(parents=True, exist_ok=True)

        (root / DOC_REL).write_text(
            "\n".join(
                [
                    "# Phase 3 ABI Substrate Slice",
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
        (root / MANIFEST_REL).write_text(
            json.dumps({"files": [DUMP_REL]}),
            encoding="utf-8",
            newline="\n",
        )

        assert validate(root) == []

        (root / DOC_REL).write_text("# Phase 3 ABI Substrate Slice\n", encoding="utf-8", newline="\n")
        issues = validate(root)
        assert f"missing_doc_marker:{DUMP_GATE}" in issues

        (root / DOC_REL).write_text(
            "\n".join([DUMP_GATE, DUMP_GATE, ""]),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate(root)
        assert f"duplicate_doc_marker:{DUMP_GATE}" in issues

    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")
    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=3")
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

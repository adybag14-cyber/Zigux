#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = "Documentation/zigux/phase2-closure.md"
PHASE2_TOOL_MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"
PHASE2_VALIDATE = "scripts/zigux/validate-phase2.py"
PHASE2_VALIDATE_CLOSURE = "scripts/zigux/validate-phase2-closure.py"
BRIDGE_CHECKER = "scripts/zigux/check-genksyms-bridge.py"
BRIDGE_CASES = "zigux/tests/fixtures/genksyms_bridge/cases.json"
INLINE_SHORT_TEST = "scripts/zigux/genksyms_inline_short_option_argument_test.zig"
INLINE_SHORT_EXPECTED = "zigux/tests/fixtures/genksyms_bridge/inline_short_option_arguments_expected.json"

SHARED_STANDALONE_PROOF_PACKET = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)
EXPECTED_INLINE_SHORT_PAYLOAD = {
    "tool": "scripts/genksyms/genksyms",
    "stdin": "cpp-stream",
    "stdout": "symversions",
    "argv": [
        "scripts/genksyms/genksyms",
        "-d",
        "-rfoo.symref",
        "-Ttypes.symtypes",
    ],
    "options": {
        "debug_level": 1,
        "warnings": False,
        "dump_defs": False,
        "preserve": False,
        "reference_files": ["foo.symref"],
        "dump_types_file": "types.symtypes",
    },
}
EXPECTED_SELF_TEST_CASE_COUNT = 9


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(root: Path, rel: str, issue_code: str) -> tuple[object | None, tuple[str, str] | None]:
    try:
        return json.loads(read_text(root, rel)), None
    except json.JSONDecodeError:
        return None, (issue_code, rel)


def count_exact(values: list[str], target: str) -> int:
    return sum(1 for value in values if value == target)


def parse_python_module(root: Path, rel: str) -> ast.Module:
    path = root / rel
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=rel)
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except SyntaxError as exc:
        raise SystemExit(f"invalid python in required file: {path}:{exc.lineno}:{exc.offset}") from exc


def extract_assign_literal(module: ast.Module, const_name: str) -> object:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == const_name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"missing constant {const_name}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in (
        PHASE2_CLOSURE,
        PHASE2_TOOL_MANIFEST,
        PHASE2_VALIDATE,
        PHASE2_VALIDATE_CLOSURE,
        BRIDGE_CHECKER,
        BRIDGE_CASES,
        INLINE_SHORT_TEST,
        INLINE_SHORT_EXPECTED,
    ):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    closure_text = read_text(root, PHASE2_CLOSURE)
    tool_manifest_payload, tool_manifest_issue = read_json(root, PHASE2_TOOL_MANIFEST, "INVALID_TOOL_MANIFEST_JSON")
    bridge_cases_payload, bridge_cases_issue = read_json(root, BRIDGE_CASES, "INVALID_BRIDGE_CASES_JSON")
    inline_short_payload, inline_short_issue = read_json(root, INLINE_SHORT_EXPECTED, "INVALID_INLINE_SHORT_EXPECTED_JSON")
    if tool_manifest_issue is not None:
        issues.append(tool_manifest_issue)
    if bridge_cases_issue is not None:
        issues.append(bridge_cases_issue)
    if inline_short_issue is not None:
        issues.append(inline_short_issue)
    if issues:
        return issues

    validate_phase2 = parse_python_module(root, PHASE2_VALIDATE)
    validate_phase2_closure = parse_python_module(root, PHASE2_VALIDATE_CLOSURE)
    bridge_checker_text = read_text(root, BRIDGE_CHECKER)
    inline_short_test_text = read_text(root, INLINE_SHORT_TEST)

    if not isinstance(tool_manifest_payload, dict):
        issues.append(("INVALID_TOOL_MANIFEST_PAYLOAD", type(tool_manifest_payload).__name__))
        return issues
    present_surfaces = tool_manifest_payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_TOOL_MANIFEST_FIELD", "present_surfaces"))
        return issues
    bridge_helpers = present_surfaces.get("bridge_helpers")
    if not isinstance(bridge_helpers, list) or not all(isinstance(item, str) for item in bridge_helpers):
        issues.append(("INVALID_TOOL_MANIFEST_FIELD", "bridge_helpers"))
    else:
        for marker in SHARED_STANDALONE_PROOF_PACKET:
            if count_exact(bridge_helpers, marker) != 1:
                issues.append(("TOOL_MANIFEST_BRIDGE_HELPER_MISMATCH", marker))
        if INLINE_SHORT_TEST in bridge_helpers:
            issues.append(("INLINE_SHORT_LEAKED_TO_TOOL_MANIFEST", INLINE_SHORT_TEST))

    for marker in SHARED_STANDALONE_PROOF_PACKET:
        if f"`{marker}`" not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
    if INLINE_SHORT_TEST in closure_text:
        issues.append(("INLINE_SHORT_LEAKED_TO_CLOSURE", INLINE_SHORT_TEST))

    try:
        validate_phase2_bridge_helpers = extract_assign_literal(validate_phase2, "BASE_REQUIRED_PRESENT_SURFACES")[
            "bridge_helpers"
        ]
    except (ValueError, KeyError, TypeError):
        issues.append(("INVALID_VALIDATE_PHASE2_CONSTANT", "BASE_REQUIRED_PRESENT_SURFACES.bridge_helpers"))
        validate_phase2_bridge_helpers = []
    if isinstance(validate_phase2_bridge_helpers, (list, tuple)):
        helpers = list(validate_phase2_bridge_helpers)
        for marker in SHARED_STANDALONE_PROOF_PACKET:
            if count_exact(helpers, marker) != 1:
                issues.append(("VALIDATE_PHASE2_BRIDGE_HELPER_MISMATCH", marker))
        if INLINE_SHORT_TEST in helpers:
            issues.append(("INLINE_SHORT_LEAKED_TO_VALIDATE_PHASE2", INLINE_SHORT_TEST))
    else:
        issues.append(("INVALID_VALIDATE_PHASE2_CONSTANT", "BASE_REQUIRED_PRESENT_SURFACES.bridge_helpers"))

    try:
        build_self_test_root = extract_assign_literal(validate_phase2_closure, "GENKSYMS_REQUIRED_NOTE_MARKERS")
    except ValueError:
        build_self_test_root = []
        issues.append(("INVALID_VALIDATE_PHASE2_CLOSURE_CONSTANT", "GENKSYMS_REQUIRED_NOTE_MARKERS"))
    if isinstance(build_self_test_root, (list, tuple)):
        markers = list(build_self_test_root)
        for marker in SHARED_STANDALONE_PROOF_PACKET:
            if count_exact(markers, marker) != 1:
                issues.append(("VALIDATE_PHASE2_CLOSURE_MARKER_MISMATCH", marker))
        if INLINE_SHORT_TEST in markers:
            issues.append(("INLINE_SHORT_LEAKED_TO_VALIDATE_PHASE2_CLOSURE", INLINE_SHORT_TEST))
    else:
        issues.append(("INVALID_VALIDATE_PHASE2_CLOSURE_CONSTANT", "GENKSYMS_REQUIRED_NOTE_MARKERS"))

    if not isinstance(bridge_cases_payload, list):
        issues.append(("INVALID_BRIDGE_CASES_PAYLOAD", type(bridge_cases_payload).__name__))
        return issues
    inline_short_cases = [
        item for item in bridge_cases_payload if isinstance(item, dict) and item.get("name") == "inline_short_option_arguments"
    ]
    if len(inline_short_cases) != 1:
        issues.append(("INLINE_SHORT_CASE_COUNT_MISMATCH", str(len(inline_short_cases))))
    elif inline_short_cases[0].get("expected_file") != "inline_short_option_arguments_expected.json":
        issues.append(("INLINE_SHORT_CASE_EXPECTED_FILE_MISMATCH", repr(inline_short_cases[0].get("expected_file"))))

    if "inline_short_option_arguments" not in bridge_checker_text:
        issues.append(("MISSING_BRIDGE_CHECKER_MARKER", "inline_short_option_arguments"))
    if "inline_short_option_arguments_expected.json" not in bridge_checker_text:
        issues.append(("MISSING_BRIDGE_CHECKER_MARKER", "inline_short_option_arguments_expected.json"))
    if INLINE_SHORT_TEST not in bridge_checker_text:
        issues.append(("MISSING_BRIDGE_CHECKER_MARKER", INLINE_SHORT_TEST))
    if inline_short_test_text.count('test "genksyms bridge accepts inline short option arguments" {') != 1:
        issues.append(("INLINE_SHORT_TEST_MARKER_MISMATCH", INLINE_SHORT_TEST))
    if inline_short_payload != EXPECTED_INLINE_SHORT_PAYLOAD:
        issues.append(("INLINE_SHORT_EXPECTED_PAYLOAD_MISMATCH", INLINE_SHORT_EXPECTED))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_SHARED_GENKSYMS_PROOF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                f"- `{SHARED_STANDALONE_PROOF_PACKET[0]}`",
                f"- `{SHARED_STANDALONE_PROOF_PACKET[1]}`",
                "",
            )
        ),
    )
    write_text(
        root,
        PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "present_surfaces": {
                    "bridge_helpers": [
                        "scripts/zigux/kconfig/conf_bridge.zig",
                        "scripts/zigux/kconfig/confdata_bridge.zig",
                        "scripts/zigux/genksyms.zig",
                        *SHARED_STANDALONE_PROOF_PACKET,
                    ]
                }
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        PHASE2_VALIDATE,
        "\n".join(
            (
                "BASE_REQUIRED_PRESENT_SURFACES = {",
                '    "bridge_helpers": (',
                '        "scripts/zigux/kconfig/conf_bridge.zig",',
                '        "scripts/zigux/kconfig/confdata_bridge.zig",',
                '        "scripts/zigux/genksyms.zig",',
                f'        "{SHARED_STANDALONE_PROOF_PACKET[0]}",',
                f'        "{SHARED_STANDALONE_PROOF_PACKET[1]}",',
                "    ),",
                "}",
                "",
            )
        ),
    )
    write_text(
        root,
        PHASE2_VALIDATE_CLOSURE,
        "\n".join(
            (
                "GENKSYMS_REQUIRED_NOTE_MARKERS = (",
                f'    "{SHARED_STANDALONE_PROOF_PACKET[0]}",',
                f'    "{SHARED_STANDALONE_PROOF_PACKET[1]}",',
                ")",
                "",
            )
        ),
    )
    write_text(
        root,
        BRIDGE_CHECKER,
        "\n".join(
            (
                'CASE_FIXTURE = "inline_short_option_arguments"',
                'EXPECTED_FILE = "inline_short_option_arguments_expected.json"',
                f'INLINE_SHORT_ARGUMENT_TEST = "{INLINE_SHORT_TEST}"',
                "",
            )
        ),
    )
    write_text(
        root,
        BRIDGE_CASES,
        json.dumps(
            [
                {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
                {
                    "name": "inline_short_option_arguments",
                    "args": ["-d", "-rfoo.symref", "-Ttypes.symtypes"],
                    "expected_file": "inline_short_option_arguments_expected.json",
                },
            ],
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        INLINE_SHORT_TEST,
        'test "genksyms bridge accepts inline short option arguments" {\n}\n',
    )
    write_text(root, INLINE_SHORT_EXPECTED, json.dumps(EXPECTED_INLINE_SHORT_PAYLOAD, indent=2) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane22_shared_genksyms_proof_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, PHASE2_TOOL_MANIFEST))
        payload["present_surfaces"]["bridge_helpers"].append(INLINE_SHORT_TEST)
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(payload, indent=2) + "\n")
        assert ("INLINE_SHORT_LEAKED_TO_TOOL_MANIFEST", INLINE_SHORT_TEST) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, PHASE2_CLOSURE, read_text(root, PHASE2_CLOSURE) + f"- `{INLINE_SHORT_TEST}`\n")
        assert ("INLINE_SHORT_LEAKED_TO_CLOSURE", INLINE_SHORT_TEST) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, PHASE2_VALIDATE, read_text(root, PHASE2_VALIDATE).replace(SHARED_STANDALONE_PROOF_PACKET[1], INLINE_SHORT_TEST))
        assert ("VALIDATE_PHASE2_BRIDGE_HELPER_MISMATCH", SHARED_STANDALONE_PROOF_PACKET[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            PHASE2_VALIDATE_CLOSURE,
            read_text(root, PHASE2_VALIDATE_CLOSURE).replace(SHARED_STANDALONE_PROOF_PACKET[0], INLINE_SHORT_TEST),
        )
        assert ("VALIDATE_PHASE2_CLOSURE_MARKER_MISMATCH", SHARED_STANDALONE_PROOF_PACKET[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        cases = json.loads(read_text(root, BRIDGE_CASES))
        cases[1]["expected_file"] = "drifted.json"
        write_text(root, BRIDGE_CASES, json.dumps(cases, indent=2) + "\n")
        assert ("INLINE_SHORT_CASE_EXPECTED_FILE_MISMATCH", "'drifted.json'") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, INLINE_SHORT_EXPECTED, "{}\n")
        assert ("INLINE_SHORT_EXPECTED_PAYLOAD_MISMATCH", INLINE_SHORT_EXPECTED) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, BRIDGE_CHECKER, "")
        assert ("MISSING_BRIDGE_CHECKER_MARKER", "inline_short_option_arguments") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, PHASE2_TOOL_MANIFEST, "{broken\n")
        assert ("INVALID_TOOL_MANIFEST_JSON", PHASE2_TOOL_MANIFEST) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_SHARED_GENKSYMS_PROOF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SHARED_GENKSYMS_PROOF_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 2 genksyms proof packet drifts from the live closure tranche."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_SHARED_GENKSYMS_PROOF_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    tool_manifest_payload = json.loads(read_text(args.root, PHASE2_TOOL_MANIFEST))
    bridge_helpers = tool_manifest_payload["present_surfaces"]["bridge_helpers"]
    bridge_cases_payload = json.loads(read_text(args.root, BRIDGE_CASES))
    inline_short_case_count = sum(
        1 for item in bridge_cases_payload if isinstance(item, dict) and item.get("name") == "inline_short_option_arguments"
    )

    print("PHASE2_SHARED_GENKSYMS_PROOF_PACKET=pass")
    print(f"PHASE2_SHARED_GENKSYMS_PROOF_PACKET_SHARED_PROOF_COUNT={len(SHARED_STANDALONE_PROOF_PACKET)}")
    print(f"PHASE2_SHARED_GENKSYMS_PROOF_PACKET_TOOL_MANIFEST_BRIDGE_HELPER_COUNT={len(bridge_helpers)}")
    print(f"PHASE2_SHARED_GENKSYMS_PROOF_PACKET_INLINE_SHORT_CASE_COUNT={inline_short_case_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

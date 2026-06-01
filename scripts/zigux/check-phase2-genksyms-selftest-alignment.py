#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py"
GENKSYMS_ZIG = ROOT / "scripts" / "zigux" / "genksyms.zig"
VERSION_SIDE_EFFECT_TEST = ROOT / "scripts" / "zigux" / "genksyms_version_before_invalid_long_option_test.zig"
AMBIGUOUS_VERSION_SIDE_EFFECT_TEST = ROOT / "scripts" / "zigux" / "genksyms_version_before_ambiguous_long_option_test.zig"
INLINE_SHORT_ARGUMENT_TEST = ROOT / "scripts" / "zigux" / "genksyms_inline_short_option_argument_test.zig"
CASES_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json"
MANIFEST_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "manifest.json"
HELP_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "help_expected.json"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: make -C zigux phase2-genksyms",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
)

MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
)

HELP_USAGE = (
    "Usage:\n"
    "genksyms [-dDpwqhV] [-r file] [-T file] > /path/to/.tmp_obj.ver\n"
    "\n"
    " -d, --debug Increment the debug level (repeatable)\n"
    " -D, --dump Dump expanded symbol defs (for debugging only)\n"
    " -r, --reference file Read reference symbols from a file\n"
    " -T, --dump-types file Dump expanded types into file\n"
    " -p, --preserve Preserve reference modversions or fail\n"
    " -w, --warnings Enable warnings\n"
    " -q, --quiet Disable warnings (default)\n"
    " -h, --help Print this message\n"
    " -V, --version Print the release version\n"
)

EXPECTED_HELP_PAYLOAD = {"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}

EXPECTED_PROCESS_OUTPUT_PAYLOADS = {
    "abbreviated_version_expected.json": {"stdout": "", "stderr": "genksyms version 2.5.60\n", "exit_code": 0},
    "ambiguous_long_option_expected.json": {
        "stdout": "",
        "stderr": "option '--du' is ambiguous; possibilities: '--dump' '--dump-types'\n" + HELP_USAGE,
        "exit_code": 1,
    },
    "invalid_option_expected.json": {"stdout": "", "stderr": "invalid option -- 'x'\n" + HELP_USAGE, "exit_code": 1},
    "missing_long_dump_types_argument_expected.json": {
        "stdout": "",
        "stderr": "option '--dump-types' requires an argument\n" + HELP_USAGE,
        "exit_code": 1,
    },
    "missing_long_reference_argument_expected.json": {
        "stdout": "",
        "stderr": "option '--reference' requires an argument\n" + HELP_USAGE,
        "exit_code": 1,
    },
    "missing_reference_argument_expected.json": {
        "stdout": "",
        "stderr": "option requires an argument -- 'r'\n" + HELP_USAGE,
        "exit_code": 1,
    },
    "too_many_reference_files_expected.json": {"stdout": "", "stderr": "too many reference files\n", "exit_code": 1},
    "unsupported_long_option_expected.json": {
        "stdout": "",
        "stderr": "unrecognized option '--unknown'\n" + HELP_USAGE,
        "exit_code": 1,
    },
    "unexpected_long_help_argument_expected.json": {
        "stdout": "",
        "stderr": "option '--help' doesn't allow an argument\n" + HELP_USAGE,
        "exit_code": 1,
    },
    "abbreviated_unexpected_long_help_argument_expected.json": {
        "stdout": "",
        "stderr": "option '--help' doesn't allow an argument\n" + HELP_USAGE,
        "exit_code": 1,
    },
}

STANDALONE_PROOF_PATHS = (
    VERSION_SIDE_EFFECT_TEST.relative_to(ROOT).as_posix(),
    AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT).as_posix(),
    INLINE_SHORT_ARGUMENT_TEST.relative_to(ROOT).as_posix(),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path, issue_code: str) -> tuple[object | None, tuple[str, str] | None]:
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError:
        return None, (issue_code, path.name)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def helper_anchor_test_marker(anchor: str) -> str:
    return f'test "{anchor}" {{'


def extract_literal_from_module(module: ast.Module, const_name: str, *, source_path: Path) -> object:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == const_name:
                    try:
                        return ast.literal_eval(node.value)
                    except (SyntaxError, ValueError) as exc:
                        raise ValueError(f"{source_path.relative_to(ROOT).as_posix()}:{const_name}:invalid_literal:{exc}") from exc
    raise ValueError(f"{source_path.relative_to(ROOT).as_posix()}:missing constant {const_name}")


def extract_string_sequence(module: ast.Module, const_name: str, *, source_path: Path) -> tuple[str, ...]:
    value = extract_literal_from_module(module, const_name, source_path=source_path)
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{source_path.relative_to(ROOT).as_posix()}:{const_name}:expected_string_sequence")
    return tuple(value)


def extract_case_fixtures(module: ast.Module, *, source_path: Path) -> list[dict[str, object]]:
    value = extract_literal_from_module(module, "CASE_FIXTURES", source_path=source_path)
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{source_path.relative_to(ROOT).as_posix()}:CASE_FIXTURES:expected_case_fixture_sequence")
    return [dict(item) for item in value]


def extract_bridge_packets(
    bridge_checker_text: str, *, source_path: Path
) -> tuple[list[dict[str, object]], tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    try:
        module = ast.parse(bridge_checker_text, filename=source_path.as_posix())
    except SyntaxError as exc:
        raise ValueError(f"{source_path.relative_to(ROOT).as_posix()}:invalid_python:{exc.lineno}:{exc.offset}") from exc
    return (
        extract_case_fixtures(module, source_path=source_path),
        extract_string_sequence(module, "EXPECTED_PROCESS_OUTPUT_PACKET", source_path=source_path),
        extract_string_sequence(module, "EXPECTED_HELPER_LOCAL_ANCHORS", source_path=source_path),
        extract_string_sequence(module, "REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES", source_path=source_path),
        extract_string_sequence(module, "REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES", source_path=source_path),
        extract_string_sequence(module, "REQUIRED_INLINE_SHORT_ARGUMENT_TEST_LINES", source_path=source_path),
    )


def build_expected_manifest(
    case_fixtures: list[dict[str, object]],
    process_output_packet: tuple[str, ...],
    helper_local_anchors: tuple[str, ...],
) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/genksyms.zig",
        "status": "closed",
        "mode": "bounded wrapper-first dual-implementation bridge",
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
        "case_count": len(case_fixtures),
        "cases": [str(case["name"]) for case in case_fixtures],
        "bridge_expected_packet": [str(case["expected_file"]) for case in case_fixtures],
        "help_packet": ["help_expected.json"],
        "standalone_proof_packet": list(STANDALONE_PROOF_PATHS),
        "process_output_packet": list(process_output_packet),
        "helper_local_anchors": list(helper_local_anchors),
    }


def collect_manifest_field_issues(manifest: object, expected: dict[str, object]) -> list[tuple[str, str]]:
    if not isinstance(manifest, dict):
        return [("INVALID_MANIFEST_PAYLOAD", type(manifest).__name__)]
    issues: list[tuple[str, str]] = []
    for key, expected_value in expected.items():
        actual_value = manifest.get(key)
        if actual_value != expected_value:
            issues.append(("MANIFEST_FIELD_MISMATCH", f"{key}:actual={actual_value!r}:expected={expected_value!r}"))
    return issues


def collect_process_output_issues(root: Path, process_output_packet: tuple[str, ...]) -> list[tuple[str, str]]:
    expected_packet = tuple(EXPECTED_PROCESS_OUTPUT_PAYLOADS.keys())
    if process_output_packet != expected_packet:
        return [("PROCESS_OUTPUT_PACKET_ROSTER_MISMATCH", MANIFEST_FIXTURE.name)]

    issues: list[tuple[str, str]] = []
    for rel in process_output_packet:
        payload, issue = read_json(root / f"zigux/tests/fixtures/genksyms_bridge/{rel}", "INVALID_PROCESS_OUTPUT_JSON")
        if issue is not None:
            issues.append(issue)
        elif payload != EXPECTED_PROCESS_OUTPUT_PAYLOADS[rel]:
            issues.append(("PROCESS_OUTPUT_PACKET_MISMATCH", rel))
    return issues


def collect_marker_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))

    early_required_paths = (
        BRIDGE_CHECKER,
        GENKSYMS_ZIG,
        VERSION_SIDE_EFFECT_TEST,
        AMBIGUOUS_VERSION_SIDE_EFFECT_TEST,
        INLINE_SHORT_ARGUMENT_TEST,
        CASES_FIXTURE,
        MANIFEST_FIXTURE,
        HELP_FIXTURE,
    )
    for path in early_required_paths:
        candidate = root / path.relative_to(ROOT)
        if not candidate.exists():
            issues.append(("MISSING_REQUIRED_PATHS", path.relative_to(ROOT).as_posix()))
    if issues:
        return issues

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    bridge_checker_text = read_text(root / BRIDGE_CHECKER.relative_to(ROOT))
    try:
        (
            case_fixtures,
            process_output_packet,
            helper_local_anchors,
            version_side_effect_lines,
            ambiguous_version_side_effect_lines,
            inline_short_argument_lines,
        ) = extract_bridge_packets(bridge_checker_text, source_path=BRIDGE_CHECKER)
    except ValueError as exc:
        return [*issues, ("INVALID_BRIDGE_CHECKER_PACKET", str(exc))]

    for path in [
        *(root / f"zigux/tests/fixtures/genksyms_bridge/{case['expected_file']}" for case in case_fixtures),
        *(root / f"zigux/tests/fixtures/genksyms_bridge/{name}" for name in process_output_packet),
    ]:
        if not path.exists():
            issues.append(("MISSING_REQUIRED_PATHS", path.relative_to(root).as_posix()))
    if issues:
        return issues

    genksyms_text = read_text(root / GENKSYMS_ZIG.relative_to(ROOT))
    version_text = read_text(root / VERSION_SIDE_EFFECT_TEST.relative_to(ROOT))
    ambiguous_text = read_text(root / AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT))
    inline_text = read_text(root / INLINE_SHORT_ARGUMENT_TEST.relative_to(ROOT))

    issues.extend(collect_marker_issues(version_text, version_side_effect_lines, "MISSING_VERSION_SIDE_EFFECT_TEST_LINE", "DUPLICATE_VERSION_SIDE_EFFECT_TEST_LINE"))
    issues.extend(collect_marker_issues(ambiguous_text, ambiguous_version_side_effect_lines, "MISSING_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINE", "DUPLICATE_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINE"))
    issues.extend(collect_marker_issues(inline_text, inline_short_argument_lines, "MISSING_INLINE_SHORT_ARGUMENT_TEST_LINE", "DUPLICATE_INLINE_SHORT_ARGUMENT_TEST_LINE"))
    issues.extend(collect_marker_issues(genksyms_text, tuple(helper_anchor_test_marker(anchor) for anchor in helper_local_anchors), "MISSING_HELPER_LOCAL_ANCHOR", "DUPLICATE_HELPER_LOCAL_ANCHOR"))

    cases_payload, cases_issue = read_json(root / CASES_FIXTURE.relative_to(ROOT), "INVALID_CASES_JSON")
    if cases_issue is not None:
        return [*issues, cases_issue]
    expected_cases = [{"name": case["name"], "args": case["args"], "expected_file": case["expected_file"]} for case in case_fixtures]
    if cases_payload != expected_cases:
        issues.append(("CASE_PACKET_MISMATCH", CASES_FIXTURE.name))

    manifest_payload, manifest_issue = read_json(root / MANIFEST_FIXTURE.relative_to(ROOT), "INVALID_MANIFEST_JSON")
    if manifest_issue is not None:
        return [*issues, manifest_issue]
    issues.extend(collect_manifest_field_issues(manifest_payload, build_expected_manifest(case_fixtures, process_output_packet, helper_local_anchors)))

    help_payload, help_issue = read_json(root / HELP_FIXTURE.relative_to(ROOT), "INVALID_HELP_JSON")
    if help_issue is not None:
        return [*issues, help_issue]
    if help_payload != EXPECTED_HELP_PAYLOAD:
        issues.append(("HELP_PACKET_MISMATCH", HELP_FIXTURE.name))

    issues.extend(collect_process_output_issues(root, process_output_packet))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def render_bridge_checker_stub() -> str:
    return (
        "CASE_FIXTURES = ["
        "{'name': 'minimal', 'args': [], 'expected_file': 'minimal_expected.json'}, "
        "{'name': 'inline_short_option_arguments', 'args': ['-d', '-rfoo.symref', '-Ttypes.symtypes'], 'expected_file': 'inline_short_option_arguments_expected.json'}]\n"
        f"EXPECTED_PROCESS_OUTPUT_PACKET = {tuple(EXPECTED_PROCESS_OUTPUT_PAYLOADS.keys())!r}\n"
        "EXPECTED_HELPER_LOCAL_ANCHORS = ('genksyms bridge treats pure version requests as version command', 'genksyms bridge preserves repeated pure version invocations')\n"
        "REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES = ('test \\\"genksyms bridge preserves version side effect before invalid long option\\\" {', 'test \\\"genksyms bridge preserves abbreviated version side effect before invalid long option\\\" {')\n"
        "REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES = ('test \\\"genksyms bridge preserves version side effect before ambiguous long option\\\" {', 'test \\\"genksyms bridge preserves abbreviated version side effect before ambiguous long option\\\" {')\n"
        "REQUIRED_INLINE_SHORT_ARGUMENT_TEST_LINES = ('test \\\"genksyms bridge accepts inline short option arguments\\\" {',)\n"
    )


def build_self_test_root(root: Path) -> None:
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(root / MAKEFILE.relative_to(ROOT), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(root / BRIDGE_CHECKER.relative_to(ROOT), render_bridge_checker_stub())
    write_text(root / GENKSYMS_ZIG.relative_to(ROOT), "\n".join((
        helper_anchor_test_marker("genksyms bridge treats pure version requests as version command"),
        "}",
        helper_anchor_test_marker("genksyms bridge preserves repeated pure version invocations"),
        "}",
        "",
    )))
    write_text(root / VERSION_SIDE_EFFECT_TEST.relative_to(ROOT),
        'test "genksyms bridge preserves version side effect before invalid long option" {\n}\n'
        'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {\n}\n')
    write_text(root / AMBIGUOUS_VERSION_SIDE_EFFECT_TEST.relative_to(ROOT),
        'test "genksyms bridge preserves version side effect before ambiguous long option" {\n}\n'
        'test "genksyms bridge preserves abbreviated version side effect before ambiguous long option" {\n}\n')
    write_text(root / INLINE_SHORT_ARGUMENT_TEST.relative_to(ROOT), 'test "genksyms bridge accepts inline short option arguments" {\n}\n')

    bridge_checker_text = read_text(root / BRIDGE_CHECKER.relative_to(ROOT))
    case_fixtures, process_output_packet, helper_local_anchors, _, _, _ = extract_bridge_packets(bridge_checker_text, source_path=BRIDGE_CHECKER)
    write_text(root / CASES_FIXTURE.relative_to(ROOT), json.dumps(expected_cases(case_fixtures), indent=2) + "\n")
    write_text(root / MANIFEST_FIXTURE.relative_to(ROOT), json.dumps(build_expected_manifest(case_fixtures, process_output_packet, helper_local_anchors), indent=2) + "\n")
    write_text(root / HELP_FIXTURE.relative_to(ROOT), json.dumps(EXPECTED_HELP_PAYLOAD, indent=2) + "\n")
    for case in case_fixtures:
        write_text(root / f"zigux/tests/fixtures/genksyms_bridge/{case['expected_file']}", "{}\n")
    for rel, payload in EXPECTED_PROCESS_OUTPUT_PAYLOADS.items():
        write_text(root / f"zigux/tests/fixtures/genksyms_bridge/{rel}", json.dumps(payload, indent=2) + "\n")


def expected_cases(case_fixtures: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"name": case["name"], "args": case["args"], "expected_file": case["expected_file"]} for case in case_fixtures]


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 broken.py"), encoding="utf-8")
            assert ("MISSING_WORKFLOW_HOOKS", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE.relative_to(ROOT)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "$(PYTHON) broken.py"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_HOOKS", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        bridge_path = root / BRIDGE_CHECKER.relative_to(ROOT)
        bridge_path.write_text(bridge_path.read_text(encoding="utf-8").replace("REQUIRED_INLINE_SHORT_ARGUMENT_TEST_LINES = ", "MISSING_REQUIRED_INLINE_SHORT_ARGUMENT_TEST_LINES = ", 1), encoding="utf-8")
        assert ("INVALID_BRIDGE_CHECKER_PACKET", "scripts/zigux/check-genksyms-bridge.py:missing constant REQUIRED_INLINE_SHORT_ARGUMENT_TEST_LINES") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        inline_path = root / INLINE_SHORT_ARGUMENT_TEST.relative_to(ROOT)
        inline_path.write_text("", encoding="utf-8")
        assert ("MISSING_INLINE_SHORT_ARGUMENT_TEST_LINE", 'test "genksyms bridge accepts inline short option arguments" {') in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        inline_path = root / INLINE_SHORT_ARGUMENT_TEST.relative_to(ROOT)
        inline_path.write_text(duplicate_exact_line(inline_path.read_text(encoding="utf-8"), 'test "genksyms bridge accepts inline short option arguments" {'), encoding="utf-8")
        assert ("DUPLICATE_INLINE_SHORT_ARGUMENT_TEST_LINE", 'test "genksyms bridge accepts inline short option arguments" {:count=2') in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / INLINE_SHORT_ARGUMENT_TEST.relative_to(ROOT)).unlink()
        assert ("MISSING_REQUIRED_PATHS", INLINE_SHORT_ARGUMENT_TEST.relative_to(ROOT).as_posix()) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / MANIFEST_FIXTURE.relative_to(ROOT)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["standalone_proof_packet"] = manifest["standalone_proof_packet"][:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert any(code == "MANIFEST_FIELD_MISMATCH" and value.startswith("standalone_proof_packet:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        cases_path = root / CASES_FIXTURE.relative_to(ROOT)
        cases_path.write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_CASES_JSON", CASES_FIXTURE.name) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        help_path = root / HELP_FIXTURE.relative_to(ROOT)
        help_path.write_text("{}\n", encoding="utf-8")
        assert ("HELP_PACKET_MISMATCH", HELP_FIXTURE.name) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        process_output_path = root / "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json"
        process_output_path.write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_PROCESS_OUTPUT_JSON", process_output_path.name) in collect_issues(root)
        checks_run += 1

    print("PHASE2_GENKSYMS_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current Phase 2 genksyms bridge packet stays aligned with its shared reminder and replay surfaces.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_GENKSYMS_ALIGNMENT=pass")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(MAKEFILE_LINES)}")
    print("PHASE2_GENKSYMS_ALIGNMENT_CASE_COUNT=derived")
    print("PHASE2_GENKSYMS_ALIGNMENT_HELPER_ANCHOR_COUNT=derived")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_STANDALONE_PROOF_COUNT={len(STANDALONE_PROOF_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MAKEFILE = "zigux/Makefile"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
GENKSYMS_ZIG = "scripts/zigux/genksyms.zig"
VERSION_SIDE_EFFECT_TEST = "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"
AMBIGUOUS_VERSION_SIDE_EFFECT_TEST = "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"
HELP_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/help_expected.json"
CASES_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/cases.json"
MANIFEST_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/manifest.json"

CASE_FIXTURES = (
    {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
    {
        "name": "debug_reference_types",
        "args": ["-d", "-r", "ref.symvers", "-T", "types.symtypes"],
        "expected_file": "debug_reference_types_expected.json",
    },
    {
        "name": "long_options",
        "args": [
            "--debug",
            "--dump",
            "--reference=foo.symref",
            "--dump-types",
            "types.symtypes",
            "--preserve",
        ],
        "expected_file": "long_options_expected.json",
    },
    {
        "name": "abbreviated_long_options",
        "args": [
            "--deb",
            "--warn",
            "--qui",
            "--ref=foo.symref",
            "--dump-t",
            "types.symtypes",
            "--pres",
        ],
        "expected_file": "abbreviated_long_options_expected.json",
    },
    {
        "name": "quiet_overrides_warning",
        "args": ["--warnings", "--quiet", "--reference", "bar.symref"],
        "expected_file": "quiet_overrides_warning_expected.json",
    },
    {
        "name": "explicit_option_terminator",
        "args": ["-d", "leftover.c", "--", "--leftover", "positional"],
        "expected_file": "explicit_option_terminator_expected.json",
    },
    {
        "name": "positional_passthrough",
        "args": ["leftover.c", "-d", "rightover.h", "-r", "foo.symref"],
        "expected_file": "positional_passthrough_expected.json",
    },
    {
        "name": "lone_dash_passthrough",
        "args": ["-", "-d"],
        "expected_file": "lone_dash_passthrough_expected.json",
    },
    {
        "name": "dash_prefixed_long_option_arguments_as_data",
        "args": ["--reference", "--debug", "--dump-types", "--types"],
        "expected_file": "dash_prefixed_long_option_arguments_as_data_expected.json",
    },
    {
        "name": "dash_prefixed_short_option_arguments_as_data",
        "args": ["-r", "-d", "-T", "--symtypes"],
        "expected_file": "dash_prefixed_short_option_arguments_as_data_expected.json",
    },
)

EXPECTED_PROCESS_OUTPUT_PACKET = (
    "abbreviated_unexpected_long_help_argument_expected.json",
    "abbreviated_version_expected.json",
    "ambiguous_long_option_expected.json",
    "invalid_option_expected.json",
    "missing_long_dump_types_argument_expected.json",
    "missing_long_reference_argument_expected.json",
    "missing_reference_argument_expected.json",
    "repeated_version_expected.json",
    "too_many_reference_files_expected.json",
    "unexpected_help_argument_expected.json",
    "unexpected_long_help_argument_expected.json",
    "unsupported_long_option_expected.json",
    "version_expected.json",
    "version_then_help_expected.json",
)

EXPECTED_HELPER_LOCAL_ANCHORS = (
    "genksyms bridge treats pure version requests as version command",
    "genksyms bridge preserves repeated pure version invocations",
    "genksyms bridge preserves empty inline long reference argument",
    "genksyms bridge preserves empty inline abbreviated dump-types argument",
    "parseArgs reports ambiguous abbreviated long options",
    "genksyms bridge renders ambiguous long option failure like the fixture",
    "genksyms bridge renders invalid short option failure like the fixture",
    "genksyms bridge renders missing long option argument like the fixture",
    "genksyms bridge renders missing short option argument like the fixture",
    "genksyms bridge renders unexpected long option argument like the fixture",
    "genksyms bridge appends usage after getopt-style parse failures",
    "genksyms bridge leaves tool-local reference-limit failure message unchanged",
    "genksyms bridge keeps dash-prefixed long option arguments as data",
    "genksyms bridge keeps dash-prefixed short option arguments as data",
    "genksyms bridge rejects more than sixteen reference files like the C harness",
)

REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES = (
    'test "genksyms bridge preserves version side effect before invalid long option" {',
    'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {',
)

REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES = (
    'test "genksyms bridge preserves version side effect before ambiguous long option" {',
    'test "genksyms bridge preserves abbreviated version side effect before ambiguous long option" {',
)

STANDALONE_PROOF_PACKET = (
    VERSION_SIDE_EFFECT_TEST,
    AMBIGUOUS_VERSION_SIDE_EFFECT_TEST,
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

REQUIRED_MAKEFILE_LINES = (
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: make -C zigux phase2-genksyms",
)

LONG_OPTION_SPECS = (
    ("help", "help", False),
    ("version", "version", False),
    ("debug", "debug", False),
    ("warnings", "warnings", False),
    ("quiet", "quiet", False),
    ("dump", "dump", False),
    ("reference", "reference", True),
    ("dump-types", "dump-types", True),
    ("preserve", "preserve", False),
)

EXPECTED_SELF_TEST_CASE_COUNT = 23


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(root: Path, rel: str, issue_code: str):
    try:
        return json.loads(read_text(root, rel)), None
    except json.JSONDecodeError:
        return None, (issue_code, rel)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_duplicate_strings(values: list[str]) -> list[str]:
    duplicates: list[str] = []
    seen: set[str] = set()
    recorded: set[str] = set()
    for value in values:
        if value in seen and value not in recorded:
            duplicates.append(value)
            recorded.add(value)
        seen.add(value)
    return duplicates


def extract_case_field_strings(payload: object, field: str):
    if not isinstance(payload, list):
        return None
    values: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            return None
        value = item.get(field)
        if not isinstance(value, str):
            return None
        values.append(value)
    return values


def resolve_long_option(name: str):
    exact_match = None
    prefix_matches = []
    for spec_name, canonical_name, takes_argument in LONG_OPTION_SPECS:
        if name == spec_name:
            exact_match = (canonical_name, takes_argument)
            break
        if spec_name.startswith(name):
            prefix_matches.append((canonical_name, takes_argument))
    if exact_match is not None:
        return exact_match
    if len(prefix_matches) == 1:
        return prefix_matches[0]
    raise ValueError(f"unsupported fixture arg: --{name}")


def parse_args(argv: list[str]) -> dict[str, object]:
    rendered: list[str] = []
    positional_args: list[str] = []
    debug_level = 0
    warnings = False
    dump_defs = False
    preserve = False
    reference_files: list[str] = []
    dump_types_file: str | None = None
    idx = 0
    while idx < len(argv):
        arg = argv[idx]
        if arg == "--":
            rendered.extend(positional_args)
            rendered.append(arg)
            rendered.extend(argv[idx + 1 :])
            break
        if not arg or arg[0] != "-" or arg == "-":
            positional_args.append(arg)
            idx += 1
            continue
        if arg == "-d":
            debug_level += 1
            rendered.append(arg)
        elif arg == "-D":
            dump_defs = True
            rendered.append(arg)
        elif arg == "-p":
            preserve = True
            rendered.append(arg)
        elif arg == "-w":
            warnings = True
            rendered.append(arg)
        elif arg == "-q":
            warnings = False
            rendered.append(arg)
        elif arg == "-r":
            idx += 1
            reference_files.append(argv[idx])
            rendered.extend((arg, argv[idx]))
        elif arg == "-T":
            idx += 1
            dump_types_file = argv[idx]
            rendered.extend((arg, argv[idx]))
        elif arg.startswith("--"):
            option, separator, inline_value = arg[2:].partition("=")
            canonical_name, takes_argument = resolve_long_option(option)
            if takes_argument:
                if separator:
                    value = inline_value
                    rendered.append(arg)
                else:
                    idx += 1
                    value = argv[idx]
                    rendered.extend((arg, argv[idx]))
                if canonical_name == "reference":
                    reference_files.append(value)
                else:
                    dump_types_file = value
            else:
                rendered.append(arg)
                if canonical_name == "debug":
                    debug_level += 1
                elif canonical_name == "dump":
                    dump_defs = True
                elif canonical_name == "preserve":
                    preserve = True
                elif canonical_name == "warnings":
                    warnings = True
                elif canonical_name == "quiet":
                    warnings = False
        else:
            raise ValueError(f"unsupported fixture arg: {arg}")
        idx += 1
    else:
        rendered.extend(positional_args)

    return {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": ["scripts/genksyms/genksyms", *rendered],
        "options": {
            "debug_level": debug_level,
            "warnings": warnings,
            "dump_defs": dump_defs,
            "preserve": preserve,
            "reference_files": reference_files,
            "dump_types_file": dump_types_file,
        },
    }


def build_expected_manifest() -> dict[str, object]:
    return {
        "tool": "scripts/zigux/genksyms.zig",
        "status": "closed",
        "mode": "bounded wrapper-first dual-implementation bridge",
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "fixture_case_source": CASES_FIXTURE,
        "case_count": len(CASE_FIXTURES),
        "cases": [case["name"] for case in CASE_FIXTURES],
        "bridge_expected_packet": [case["expected_file"] for case in CASE_FIXTURES],
        "help_packet": ["help_expected.json"],
        "standalone_proof_packet": list(STANDALONE_PROOF_PACKET),
        "process_output_packet": list(EXPECTED_PROCESS_OUTPUT_PACKET),
        "helper_local_anchors": list(EXPECTED_HELPER_LOCAL_ANCHORS),
    }


def expected_process_output_payloads() -> dict[str, dict[str, object]]:
    return {
        "abbreviated_unexpected_long_help_argument_expected.json": {
            "stdout": "",
            "stderr": "option '--help' doesn't allow an argument\n" + HELP_USAGE,
            "exit_code": 1,
        },
        "abbreviated_version_expected.json": {
            "stdout": "",
            "stderr": "genksyms version 2.5.60\n",
            "exit_code": 0,
        },
        "ambiguous_long_option_expected.json": {
            "stdout": "",
            "stderr": "option '--du' is ambiguous; possibilities: '--dump' '--dump-types'\n" + HELP_USAGE,
            "exit_code": 1,
        },
        "invalid_option_expected.json": {
            "stdout": "",
            "stderr": "invalid option -- 'x'\n" + HELP_USAGE,
            "exit_code": 1,
        },
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
        "repeated_version_expected.json": {
            "stdout": "",
            "stderr": "genksyms version 2.5.60\ngenksyms version 2.5.60\n",
            "exit_code": 0,
        },
        "too_many_reference_files_expected.json": {
            "stdout": "",
            "stderr": "too many reference files\n",
            "exit_code": 1,
        },
        "unexpected_help_argument_expected.json": {
            "stdout": "",
            "stderr": "option '--help' doesn't allow an argument\n",
            "exit_code": 1,
        },
        "unexpected_long_help_argument_expected.json": {
            "stdout": "",
            "stderr": "option '--help' doesn't allow an argument\n" + HELP_USAGE,
            "exit_code": 1,
        },
        "unsupported_long_option_expected.json": {
            "stdout": "",
            "stderr": "unrecognized option '--unknown'\n" + HELP_USAGE,
            "exit_code": 1,
        },
        "version_expected.json": {
            "stdout": "",
            "stderr": "genksyms version 2.5.60\n",
            "exit_code": 0,
        },
        "version_then_help_expected.json": {
            "stdout": "",
            "stderr": "genksyms version 2.5.60\n" + HELP_USAGE,
            "exit_code": 0,
        },
    }


def expected_fixture_packet() -> tuple[str, ...]:
    return (
        Path(HELP_FIXTURE).name,
        Path(CASES_FIXTURE).name,
        Path(MANIFEST_FIXTURE).name,
        *[case["expected_file"] for case in CASE_FIXTURES],
        *EXPECTED_PROCESS_OUTPUT_PACKET,
    )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    required_paths = [
        GENKSYMS_ZIG,
        *STANDALONE_PROOF_PACKET,
        HELP_FIXTURE,
        CASES_FIXTURE,
        MANIFEST_FIXTURE,
        MAKEFILE,
        WORKFLOW,
        *[f"zigux/tests/fixtures/genksyms_bridge/{case['expected_file']}" for case in CASE_FIXTURES],
        *[f"zigux/tests/fixtures/genksyms_bridge/{name}" for name in EXPECTED_PROCESS_OUTPUT_PACKET],
    ]
    for rel in required_paths:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    makefile_text = read_text(root, MAKEFILE)
    workflow_text = read_text(root, WORKFLOW)
    genksyms_text = read_text(root, GENKSYMS_ZIG)
    version_side_effect_text = read_text(root, VERSION_SIDE_EFFECT_TEST)
    ambiguous_version_side_effect_text = read_text(root, AMBIGUOUS_VERSION_SIDE_EFFECT_TEST)

    for marker in REQUIRED_MAKEFILE_LINES:
        if count_exact_lines(makefile_text, marker) != 1:
            issues.append(("MAKEFILE_LINE_MISMATCH", marker))
    for marker in REQUIRED_WORKFLOW_LINES:
        if count_exact_lines(workflow_text, marker) != 1:
            issues.append(("WORKFLOW_LINE_MISMATCH", marker))
    for marker in REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES:
        if count_exact_lines(version_side_effect_text, marker) != 1:
            issues.append(("VERSION_SIDE_EFFECT_TEST_LINE_MISMATCH", marker))
    for marker in REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES:
        if count_exact_lines(ambiguous_version_side_effect_text, marker) != 1:
            issues.append(("AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINE_MISMATCH", marker))
    for anchor in EXPECTED_HELPER_LOCAL_ANCHORS:
        marker = f'test "{anchor}" {{'
        if count_exact_lines(genksyms_text, marker) != 1:
            issues.append(("HELPER_LOCAL_ANCHOR_MISMATCH", marker))

    if '@embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json")' not in genksyms_text:
        issues.append(("MISSING_HELP_FIXTURE_EMBED", HELP_FIXTURE))

    help_payload, help_issue = read_json(root, HELP_FIXTURE, "INVALID_HELP_FIXTURE_JSON")
    if help_issue is not None:
        issues.append(help_issue)
        return issues
    if help_payload != {"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}:
        issues.append(("HELP_FIXTURE_MISMATCH", HELP_FIXTURE))

    cases_payload, cases_issue = read_json(root, CASES_FIXTURE, "INVALID_CASES_FIXTURE_JSON")
    if cases_issue is not None:
        issues.append(cases_issue)
        return issues
    case_names = extract_case_field_strings(cases_payload, "name")
    if case_names is not None:
        for value in find_duplicate_strings(case_names):
            issues.append(("DUPLICATE_CASE_NAME", value))
    expected_files = extract_case_field_strings(cases_payload, "expected_file")
    if expected_files is not None:
        for value in find_duplicate_strings(expected_files):
            issues.append(("DUPLICATE_EXPECTED_FILE", value))
    if cases_payload != [dict(case) for case in CASE_FIXTURES]:
        issues.append(("CASE_ROSTER_MISMATCH", CASES_FIXTURE))

    manifest_payload, manifest_issue = read_json(root, MANIFEST_FIXTURE, "INVALID_MANIFEST_JSON")
    if manifest_issue is not None:
        issues.append(manifest_issue)
        return issues
    expected_manifest = build_expected_manifest()
    if not isinstance(manifest_payload, dict):
        issues.append(("INVALID_MANIFEST_PAYLOAD", type(manifest_payload).__name__))
        return issues
    if manifest_payload.get("standalone_proof_packet") != expected_manifest["standalone_proof_packet"]:
        issues.append(("MANIFEST_FIELD_MISMATCH", "standalone_proof_packet"))
    for key, expected_value in expected_manifest.items():
        if manifest_payload.get(key) != expected_value:
            issues.append(("MANIFEST_FIELD_MISMATCH", key))

    for case in CASE_FIXTURES:
        rel = f"zigux/tests/fixtures/genksyms_bridge/{case['expected_file']}"
        payload, payload_issue = read_json(root, rel, "INVALID_EXPECTED_FIXTURE_JSON")
        if payload_issue is not None:
            issues.append(payload_issue)
            continue
        if payload != parse_args(list(case["args"])):
            issues.append(("CASE_MISMATCH", case["name"]))

    for rel, expected_payload in expected_process_output_payloads().items():
        payload, payload_issue = read_json(root, f"zigux/tests/fixtures/genksyms_bridge/{rel}", "INVALID_PROCESS_OUTPUT_FIXTURE_JSON")
        if payload_issue is not None:
            issues.append(payload_issue)
            continue
        if payload != expected_payload:
            issues.append(("PROCESS_OUTPUT_FIXTURE_MISMATCH", rel))

    fixture_root = root / "zigux/tests/fixtures/genksyms_bridge"
    actual_fixture_packet = sorted(path.name for path in fixture_root.iterdir() if path.is_file())
    expected_packet = sorted(expected_fixture_packet())
    if actual_fixture_packet != expected_packet:
        issues.append(("FIXTURE_PACKET_MISMATCH", "zigux/tests/fixtures/genksyms_bridge"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("GENKSYMS_BRIDGE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        MAKEFILE,
        "phase2-genksyms:\n"
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test\n"
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py\n"
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig\n",
    )
    write_text(
        root,
        WORKFLOW,
        "      - name: Self-test current Phase 2 genksyms bridge checker\n"
        "        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test\n"
        "      - name: Check current Phase 2 genksyms bridge packet\n"
        "        run: python3 scripts/zigux/check-genksyms-bridge.py\n"
        "      - name: Run current Phase 2 genksyms unit replay\n"
        "        run: zig test scripts/zigux/genksyms.zig\n"
        "      - name: Run current Phase 2 genksyms make route\n"
        "        run: make -C zigux phase2-genksyms\n",
    )
    helper_tests = "\n".join(f'test "{anchor}" {{\n}}' for anchor in EXPECTED_HELPER_LOCAL_ANCHORS)
    write_text(
        root,
        GENKSYMS_ZIG,
        'const help_expected_json = @embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json");\n\n' + helper_tests + "\n",
    )
    write_text(
        root,
        VERSION_SIDE_EFFECT_TEST,
        'test "genksyms bridge preserves version side effect before invalid long option" {\n}\n'
        'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {\n}\n',
    )
    write_text(
        root,
        AMBIGUOUS_VERSION_SIDE_EFFECT_TEST,
        'test "genksyms bridge preserves version side effect before ambiguous long option" {\n}\n'
        'test "genksyms bridge preserves abbreviated version side effect before ambiguous long option" {\n}\n',
    )
    write_text(root, HELP_FIXTURE, json.dumps({"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}, indent=2) + "\n")
    write_text(root, CASES_FIXTURE, json.dumps([dict(case) for case in CASE_FIXTURES], indent=2) + "\n")
    write_text(root, MANIFEST_FIXTURE, json.dumps(build_expected_manifest(), indent=2) + "\n")
    for case in CASE_FIXTURES:
        write_text(
            root,
            f"zigux/tests/fixtures/genksyms_bridge/{case['expected_file']}",
            json.dumps(parse_args(list(case["args"])), indent=2) + "\n",
        )
    for rel, payload in expected_process_output_payloads().items():
        write_text(root, f"zigux/tests/fixtures/genksyms_bridge/{rel}", json.dumps(payload, indent=2) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_genksyms_bridge_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, HELP_FIXTURE, "{}\n")
        assert ("HELP_FIXTURE_MISMATCH", HELP_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, HELP_FIXTURE, "{broken\n")
        assert ("INVALID_HELP_FIXTURE_JSON", HELP_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, CASES_FIXTURE, "{broken\n")
        assert ("INVALID_CASES_FIXTURE_JSON", CASES_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        duplicate_name_cases = [dict(case) for case in CASE_FIXTURES]
        duplicate_name_cases[1]["name"] = duplicate_name_cases[0]["name"]
        write_text(root, CASES_FIXTURE, json.dumps(duplicate_name_cases, indent=2) + "\n")
        assert ("DUPLICATE_CASE_NAME", "minimal") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        duplicate_expected_cases = [dict(case) for case in CASE_FIXTURES]
        duplicate_expected_cases[1]["expected_file"] = duplicate_expected_cases[0]["expected_file"]
        write_text(root, CASES_FIXTURE, json.dumps(duplicate_expected_cases, indent=2) + "\n")
        assert ("DUPLICATE_EXPECTED_FILE", "minimal_expected.json") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, CASES_FIXTURE, json.dumps([dict(CASE_FIXTURES[0])], indent=2) + "\n")
        assert ("CASE_ROSTER_MISMATCH", CASES_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MANIFEST_FIXTURE, "{broken\n")
        assert ("INVALID_MANIFEST_JSON", MANIFEST_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MANIFEST_FIXTURE, "[]\n")
        assert ("INVALID_MANIFEST_PAYLOAD", "list") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest = build_expected_manifest()
        manifest["standalone_proof_packet"] = []
        write_text(root, MANIFEST_FIXTURE, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_FIELD_MISMATCH", "standalone_proof_packet") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json", "{broken\n")
        assert ("INVALID_EXPECTED_FIXTURE_JSON", "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        bad_payload = parse_args(["leftover.c", "-d", "rightover.h", "-r", "foo.symref"])
        bad_payload["options"]["warnings"] = True
        write_text(root, "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json", json.dumps(bad_payload, indent=2) + "\n")
        assert ("CASE_MISMATCH", "positional_passthrough") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json", "{broken\n")
        assert ("INVALID_PROCESS_OUTPUT_FIXTURE_JSON", "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json").unlink()
        assert ("MISSING_REQUIRED_PATH", "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, "zigux/tests/fixtures/genksyms_bridge/stale_expected.json", "{}\n")
        assert ("FIXTURE_PACKET_MISMATCH", "zigux/tests/fixtures/genksyms_bridge") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        payload = expected_process_output_payloads()["unexpected_long_help_argument_expected.json"].copy()
        payload["exit_code"] = 7
        write_text(root, "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json", json.dumps(payload, indent=2) + "\n")
        assert ("PROCESS_OUTPUT_FIXTURE_MISMATCH", "unexpected_long_help_argument_expected.json") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, "phase2-genksyms:\n")
        assert ("MAKEFILE_LINE_MISMATCH", REQUIRED_MAKEFILE_LINES[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, "      - name: Self-test current Phase 2 genksyms bridge checker\n")
        assert ("WORKFLOW_LINE_MISMATCH", REQUIRED_WORKFLOW_LINES[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, VERSION_SIDE_EFFECT_TEST, 'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {\n}\n')
        assert ("VERSION_SIDE_EFFECT_TEST_LINE_MISMATCH", REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, AMBIGUOUS_VERSION_SIDE_EFFECT_TEST, 'test "genksyms bridge preserves abbreviated version side effect before ambiguous long option" {\n}\n')
        assert ("AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINE_MISMATCH", REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, GENKSYMS_ZIG, 'const help_expected_json = @embedFile("missing.json");\n')
        assert ("MISSING_HELP_FIXTURE_EMBED", HELP_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, GENKSYMS_ZIG, 'const help_expected_json = @embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json");\n')
        assert ("HELPER_LOCAL_ANCHOR_MISMATCH", f'test "{EXPECTED_HELPER_LOCAL_ANCHORS[0]}" {{') in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / HELP_FIXTURE).unlink()
        assert ("MISSING_REQUIRED_PATH", HELP_FIXTURE) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("GENKSYMS_BRIDGE_SELF_TEST=pass")
    print(f"GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={checks}")
    print(f"GENKSYMS_BRIDGE_EXPECTED_CASE_COUNT={len(CASE_FIXTURES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 2 genksyms bridge packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("GENKSYMS_BRIDGE=pass")
    print(f"GENKSYMS_BRIDGE_CASE_COUNT={len(CASE_FIXTURES)}")
    print(f"GENKSYMS_BRIDGE_EXPECTED_CASE_COUNT={len(CASE_FIXTURES)}")
    print(f"GENKSYMS_BRIDGE_REQUIRED_PATH_COUNT={9 + len(CASE_FIXTURES) + len(EXPECTED_PROCESS_OUTPUT_PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

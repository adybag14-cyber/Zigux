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
HELP_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/help_expected.json"
CASES_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/cases.json"
MANIFEST_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/manifest.json"

CASE_FIXTURES = (
    {
        "name": "minimal",
        "args": [],
        "expected_file": "minimal_expected.json",
    },
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
)

EXPECTED_FIXTURES = tuple(
    f'zigux/tests/fixtures/genksyms_bridge/{case["expected_file"]}'
    for case in CASE_FIXTURES
)
EXPECTED_CASE_KEYS = tuple(
    (case["name"], case["expected_file"])
    for case in CASE_FIXTURES
)
EXPECTED_BRIDGE_EXPECTED_PACKET = tuple(case["expected_file"] for case in CASE_FIXTURES)
EXPECTED_PROCESS_OUTPUT_PACKET = (
    "abbreviated_version_expected.json",
    "ambiguous_long_option_expected.json",
    "invalid_option_expected.json",
    "missing_long_dump_types_argument_expected.json",
    "missing_long_reference_argument_expected.json",
    "missing_reference_argument_expected.json",
    "too_many_reference_files_expected.json",
    "unsupported_long_option_expected.json",
    "unexpected_long_help_argument_expected.json",
)
PROCESS_OUTPUT_FIXTURES = tuple(
    f"zigux/tests/fixtures/genksyms_bridge/{name}"
    for name in EXPECTED_PROCESS_OUTPUT_PACKET
)
EXPECTED_HELP_PACKET = ("help_expected.json",)
EXPECTED_STANDALONE_PROOF_PACKET = (VERSION_SIDE_EFFECT_TEST,)
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
    "genksyms bridge rejects more than sixteen reference files like the C harness",
)
REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES = (
    'test "genksyms bridge preserves version side effect before invalid long option" {',
    'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {',
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
    ("debug", "debug", False),
    ("dump", "dump", False),
    ("dump-types", "dump-types", True),
    ("preserve", "preserve", False),
    ("quiet", "quiet", False),
    ("reference", "reference", True),
    ("warnings", "warnings", False),
)

EXPECTED_SELF_TEST_CASE_COUNT = 26


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def read_json(root: Path, rel: str, issue_code: str) -> tuple[object | None, tuple[str, str] | None]:
    try:
        return json.loads(read_text(root, rel)), None
    except json.JSONDecodeError:
        return None, (issue_code, rel)


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def resolve_long_option(name: str) -> tuple[str, bool]:
    exact_match: tuple[str, bool] | None = None
    prefix_matches: list[tuple[str, bool]] = []
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
        "bridge_expected_packet": list(EXPECTED_BRIDGE_EXPECTED_PACKET),
        "help_packet": list(EXPECTED_HELP_PACKET),
        "standalone_proof_packet": list(EXPECTED_STANDALONE_PROOF_PACKET),
        "process_output_packet": list(EXPECTED_PROCESS_OUTPUT_PACKET),
        "helper_local_anchors": list(EXPECTED_HELPER_LOCAL_ANCHORS),
    }


def is_valid_process_output_payload(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    if set(payload.keys()) != {"stdout", "stderr", "exit_code"}:
        return False
    return (
        isinstance(payload.get("stdout"), str)
        and isinstance(payload.get("stderr"), str)
        and isinstance(payload.get("exit_code"), int)
    )


def load_cases_payload(root: Path) -> tuple[list[dict[str, object]] | None, list[tuple[str, str]]]:
    raw_cases, read_issue = read_json(root, CASES_FIXTURE, "INVALID_CASES_FIXTURE_JSON")
    if read_issue is not None:
        return None, [read_issue]

    if not isinstance(raw_cases, list):
        return None, [("INVALID_CASES_FIXTURE_PAYLOAD", type(raw_cases).__name__)]

    issues: list[tuple[str, str]] = []
    validated_cases: list[dict[str, object]] = []
    for index, case in enumerate(raw_cases):
        if not isinstance(case, dict):
            issues.append(("INVALID_CASE_ENTRY", f"index={index}:type={type(case).__name__}"))
            continue

        name = case.get("name")
        expected_file = case.get("expected_file")
        args = case.get("args")

        if not isinstance(name, str) or not name:
            issues.append(("INVALID_CASE_FIELD", f"index={index}:name"))
        if not isinstance(expected_file, str) or not expected_file:
            issues.append(("INVALID_CASE_FIELD", f"index={index}:expected_file"))
        if not isinstance(args, list):
            issues.append(("INVALID_CASE_FIELD", f"index={index}:args"))
            continue
        if any(not isinstance(arg, str) for arg in args):
            issues.append(("INVALID_CASE_ARGS_ENTRY", f"index={index}"))
            continue

        if (
            isinstance(name, str)
            and name
            and isinstance(expected_file, str)
            and expected_file
        ):
            validated_cases.append(
                {
                    "name": name,
                    "expected_file": expected_file,
                    "args": list(args),
                }
            )

    if issues:
        return None, issues
    return validated_cases, []


def validate_manifest_payload(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_PAYLOAD", type(payload).__name__)]

    expected = build_expected_manifest()
    issues: list[tuple[str, str]] = []
    for key in ("tool", "status", "mode", "fixture_root", "fixture_case_source", "case_count"):
        if payload.get(key) != expected[key]:
            issues.append(("MANIFEST_FIELD_MISMATCH", key))
    if payload.get("cases") != expected["cases"]:
        issues.append(("MANIFEST_CASE_PACKET_MISMATCH", MANIFEST_FIXTURE))
    if payload.get("bridge_expected_packet") != expected["bridge_expected_packet"]:
        issues.append(("MANIFEST_BRIDGE_EXPECTED_PACKET_MISMATCH", MANIFEST_FIXTURE))
    if payload.get("help_packet") != expected["help_packet"]:
        issues.append(("MANIFEST_HELP_PACKET_MISMATCH", MANIFEST_FIXTURE))
    if payload.get("standalone_proof_packet") != expected["standalone_proof_packet"]:
        issues.append(("MANIFEST_STANDALONE_PROOF_PACKET_MISMATCH", MANIFEST_FIXTURE))
    if payload.get("process_output_packet") != expected["process_output_packet"]:
        issues.append(("MANIFEST_PROCESS_OUTPUT_PACKET_MISMATCH", MANIFEST_FIXTURE))
    if payload.get("helper_local_anchors") != expected["helper_local_anchors"]:
        issues.append(("MANIFEST_HELPER_LOCAL_ANCHORS_MISMATCH", MANIFEST_FIXTURE))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in (
        GENKSYMS_ZIG,
        VERSION_SIDE_EFFECT_TEST,
        HELP_FIXTURE,
        CASES_FIXTURE,
        MANIFEST_FIXTURE,
        *EXPECTED_FIXTURES,
        *PROCESS_OUTPUT_FIXTURES,
        MAKEFILE,
        WORKFLOW,
    ):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    makefile_text = read_text(root, MAKEFILE)
    workflow_text = read_text(root, WORKFLOW)
    genksyms_text = read_text(root, GENKSYMS_ZIG)
    version_side_effect_text = read_text(root, VERSION_SIDE_EFFECT_TEST)

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES:
        count = count_exact_lines(version_side_effect_text, marker)
        if count == 0:
            issues.append(("MISSING_VERSION_SIDE_EFFECT_TEST_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VERSION_SIDE_EFFECT_TEST_LINE", f"{marker}:count={count}"))

    if '@embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json")' not in genksyms_text:
        issues.append(("MISSING_HELP_FIXTURE_EMBED", HELP_FIXTURE))

    help_payload, help_issue = read_json(root, HELP_FIXTURE, "INVALID_HELP_FIXTURE_JSON")
    if help_issue is not None:
        issues.append(help_issue)
        return issues
    if help_payload != {"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}:
        issues.append(("HELP_FIXTURE_MISMATCH", HELP_FIXTURE))

    manifest_payload, manifest_issue = read_json(root, MANIFEST_FIXTURE, "INVALID_MANIFEST_JSON")
    if manifest_issue is not None:
        issues.append(manifest_issue)
        return issues
    issues.extend(validate_manifest_payload(manifest_payload))
    if issues:
        return issues

    cases, case_issues = load_cases_payload(root)
    issues.extend(case_issues)
    if issues:
        return issues
    assert cases is not None

    actual_case_keys = tuple((case["name"], case["expected_file"]) for case in cases)
    if actual_case_keys != EXPECTED_CASE_KEYS:
        issues.append(("CASE_ROSTER_MISMATCH", CASES_FIXTURE))

    for case in cases:
        expected_rel = f'zigux/tests/fixtures/genksyms_bridge/{case["expected_file"]}'
        expected_payload, expected_issue = read_json(root, expected_rel, "INVALID_EXPECTED_FIXTURE_JSON")
        if expected_issue is not None:
            issues.append(expected_issue)
            continue
        actual_payload = parse_args(case["args"])
        if expected_payload != actual_payload:
            issues.append(("CASE_MISMATCH", case["name"]))

    for rel in PROCESS_OUTPUT_FIXTURES:
        payload, issue = read_json(root, rel, "INVALID_PROCESS_OUTPUT_FIXTURE_JSON")
        if issue is not None:
            issues.append(issue)
            continue
        if not is_valid_process_output_payload(payload):
            issues.append(("PROCESS_OUTPUT_FIXTURE_PAYLOAD_MISMATCH", rel))

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
    write_text(
        root,
        GENKSYMS_ZIG,
        'const help_expected_json = @embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json");\n',
    )
    write_text(
        root,
        VERSION_SIDE_EFFECT_TEST,
        'test "genksyms bridge preserves version side effect before invalid long option" {}\n'
        'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {}\n',
    )
    write_text(root, HELP_FIXTURE, json.dumps({"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}, indent=2) + "\n")
    write_text(root, CASES_FIXTURE, json.dumps(list(CASE_FIXTURES), indent=2) + "\n")
    write_text(root, MANIFEST_FIXTURE, json.dumps(build_expected_manifest(), indent=2) + "\n")
    for case in CASE_FIXTURES:
        rel = f'zigux/tests/fixtures/genksyms_bridge/{case["expected_file"]}'
        write_text(root, rel, json.dumps(parse_args(case["args"]), indent=2) + "\n")
    for rel in PROCESS_OUTPUT_FIXTURES:
        exit_code = 0 if rel.endswith("abbreviated_version_expected.json") else 1
        payload = {
            "stdout": "",
            "stderr": f"{Path(rel).name}\n",
            "exit_code": exit_code,
        }
        write_text(root, rel, json.dumps(payload, indent=2) + "\n")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_genksyms_bridge_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

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
        write_text(root, MAKEFILE, "phase2-genksyms:\n")
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[1]) in collect_issues(root)
        checks += 1

        for marker in REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES:
            build_self_test_root(root)
            write_text(
                root,
                VERSION_SIDE_EFFECT_TEST,
                read_text(root, VERSION_SIDE_EFFECT_TEST).replace(f"{marker}\n", "", 1),
            )
            assert ("MISSING_VERSION_SIDE_EFFECT_TEST_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES:
            build_self_test_root(root)
            write_text(
                root,
                VERSION_SIDE_EFFECT_TEST,
                duplicate_exact_line(read_text(root, VERSION_SIDE_EFFECT_TEST), marker),
            )
            assert (
                "DUPLICATE_VERSION_SIDE_EFFECT_TEST_LINE",
                f"{marker}:count=2",
            ) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        write_text(
            root,
            CASES_FIXTURE,
            json.dumps(list(CASE_FIXTURES[:5]), indent=2) + "\n",
        )
        assert ("CASE_ROSTER_MISMATCH", CASES_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
            json.dumps(
                {
                    "tool": "scripts/genksyms/genksyms",
                    "stdin": "cpp-stream",
                    "stdout": "symversions",
                    "argv": [
                        "scripts/genksyms/genksyms",
                        "leftover.c",
                        "-d",
                        "rightover.h",
                        "-r",
                        "foo.symref",
                    ],
                    "options": {
                        "debug_level": 1,
                        "warnings": True,
                        "dump_defs": False,
                        "preserve": False,
                        "reference_files": ["foo.symref"],
                        "dump_types_file": None,
                    },
                },
                indent=2,
            )
            + "\n",
        )
        assert ("CASE_MISMATCH", "positional_passthrough") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
            "{broken\n",
        )
        assert (
            "INVALID_EXPECTED_FIXTURE_JSON",
            "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, CASES_FIXTURE, "{}\n")
        assert ("INVALID_CASES_FIXTURE_PAYLOAD", "dict") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, CASES_FIXTURE, json.dumps(["broken"], indent=2) + "\n")
        assert ("INVALID_CASE_ENTRY", "index=0:type=str") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        broken_cases = list(CASE_FIXTURES)
        broken_cases[0] = {
            "name": "minimal",
            "args": ["-d", 7],
            "expected_file": "minimal_expected.json",
        }
        write_text(root, CASES_FIXTURE, json.dumps(broken_cases, indent=2) + "\n")
        assert ("INVALID_CASE_ARGS_ENTRY", "index=0") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        broken_cases = list(CASE_FIXTURES)
        broken_cases[0] = {
            "name": "minimal",
            "args": [],
            "expected_file": "",
        }
        write_text(root, CASES_FIXTURE, json.dumps(broken_cases, indent=2) + "\n")
        assert ("INVALID_CASE_FIELD", "index=0:expected_file") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, "      - name: Self-test current Phase 2 genksyms bridge checker\n")
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
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
            "        run: make -C zigux phase2-genksyms\n"
            "        run: make -C zigux phase2-genksyms\n",
        )
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[3]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            MAKEFILE,
            duplicate_exact_line(read_text(root, MAKEFILE), REQUIRED_MAKEFILE_LINES[2]),
        )
        assert ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[2]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, GENKSYMS_ZIG, 'const help_expected_json = @embedFile("missing.json");\n')
        assert ("MISSING_HELP_FIXTURE_EMBED", HELP_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MANIFEST_FIXTURE, "{broken\n")
        assert ("INVALID_MANIFEST_JSON", MANIFEST_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest = build_expected_manifest()
        manifest["standalone_proof_packet"] = []
        write_text(root, MANIFEST_FIXTURE, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_STANDALONE_PROOF_PACKET_MISMATCH", MANIFEST_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest = build_expected_manifest()
        manifest["process_output_packet"] = manifest["process_output_packet"][:-1]
        write_text(root, MANIFEST_FIXTURE, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_PROCESS_OUTPUT_PACKET_MISMATCH", MANIFEST_FIXTURE) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, PROCESS_OUTPUT_FIXTURES[0], "{broken\n")
        assert ("INVALID_PROCESS_OUTPUT_FIXTURE_JSON", PROCESS_OUTPUT_FIXTURES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, PROCESS_OUTPUT_FIXTURES[1], json.dumps({"stdout": "", "stderr": 7, "exit_code": 1}, indent=2) + "\n")
        assert ("PROCESS_OUTPUT_FIXTURE_PAYLOAD_MISMATCH", PROCESS_OUTPUT_FIXTURES[1]) in collect_issues(root)
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

    cases, case_issues = load_cases_payload(args.root.resolve())
    assert not case_issues
    assert cases is not None
    case_count = len(cases)
    print("GENKSYMS_BRIDGE=pass")
    print(f"GENKSYMS_BRIDGE_CASE_COUNT={case_count}")
    print(f"GENKSYMS_BRIDGE_EXPECTED_CASE_COUNT={len(CASE_FIXTURES)}")
    print(f"GENKSYMS_BRIDGE_REQUIRED_PATH_COUNT={len(EXPECTED_FIXTURES) + len(PROCESS_OUTPUT_FIXTURES) + 7}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = "zigux/Makefile"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
GENKSYMS_ZIG = "scripts/zigux/genksyms.zig"
HELP_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/help_expected.json"
CASES_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/cases.json"

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


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in (GENKSYMS_ZIG, HELP_FIXTURE, CASES_FIXTURE, *EXPECTED_FIXTURES, MAKEFILE, WORKFLOW):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    makefile_text = read_text(root, MAKEFILE)
    workflow_text = read_text(root, WORKFLOW)
    genksyms_text = read_text(root, GENKSYMS_ZIG)

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

    if '@embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json")' not in genksyms_text:
        issues.append(("MISSING_HELP_FIXTURE_EMBED", HELP_FIXTURE))

    help_payload = json.loads(read_text(root, HELP_FIXTURE))
    if help_payload != {"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}:
        issues.append(("HELP_FIXTURE_MISMATCH", HELP_FIXTURE))

    cases = json.loads(read_text(root, CASES_FIXTURE))
    actual_case_keys = tuple((case["name"], case["expected_file"]) for case in cases)
    if actual_case_keys != EXPECTED_CASE_KEYS:
        issues.append(("CASE_ROSTER_MISMATCH", CASES_FIXTURE))

    for case in cases:
        expected_rel = f'zigux/tests/fixtures/genksyms_bridge/{case["expected_file"]}'
        expected_payload = json.loads(read_text(root, expected_rel))
        actual_payload = parse_args(case["args"])
        if expected_payload != actual_payload:
            issues.append(("CASE_MISMATCH", case["name"]))

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
        "        run: zig test scripts/zigux/genksyms.zig\n",
    )
    write_text(
        root,
        GENKSYMS_ZIG,
        'const help_expected_json = @embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json");\n',
    )
    write_text(root, HELP_FIXTURE, json.dumps({"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}, indent=2) + "\n")
    write_text(root, CASES_FIXTURE, json.dumps(list(CASE_FIXTURES), indent=2) + "\n")
    for case in CASE_FIXTURES:
        rel = f'zigux/tests/fixtures/genksyms_bridge/{case["expected_file"]}'
        write_text(root, rel, json.dumps(parse_args(case["args"]), indent=2) + "\n")


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
        write_text(root, MAKEFILE, "phase2-genksyms:\n")
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[1]) in collect_issues(root)
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
            "        run: zig test scripts/zigux/genksyms.zig\n",
        )
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[2]}:count=2") in collect_issues(root)
        checks += 1

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

    case_count = len(json.loads(read_text(args.root.resolve(), CASES_FIXTURE)))
    print("GENKSYMS_BRIDGE=pass")
    print(f"GENKSYMS_BRIDGE_CASE_COUNT={case_count}")
    print(f"GENKSYMS_BRIDGE_EXPECTED_CASE_COUNT={len(CASE_FIXTURES)}")
    print(f"GENKSYMS_BRIDGE_REQUIRED_PATH_COUNT={len(EXPECTED_FIXTURES) + 5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

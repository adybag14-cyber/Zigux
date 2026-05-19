#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = "zigux/Makefile"
GENKSYMS_ZIG = "scripts/zigux/genksyms.zig"
HELP_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/help_expected.json"
CASES_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/cases.json"

EXPECTED_FIXTURES = (
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
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


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def parse_args(argv: list[str]) -> dict[str, object]:
    rendered = list(argv)
    debug_level = 0
    warnings = False
    dump_defs = False
    preserve = False
    reference_files: list[str] = []
    dump_types_file: str | None = None
    idx = 0
    while idx < len(argv):
        arg = argv[idx]
        if arg == "-d":
            debug_level += 1
        elif arg == "-D":
            dump_defs = True
        elif arg == "-p":
            preserve = True
        elif arg == "-w":
            warnings = True
        elif arg == "-q":
            warnings = False
        elif arg == "-r":
            idx += 1
            reference_files.append(argv[idx])
        elif arg == "-T":
            idx += 1
            dump_types_file = argv[idx]
        elif arg == "--debug":
            debug_level += 1
        elif arg == "--dump":
            dump_defs = True
        elif arg == "--preserve":
            preserve = True
        elif arg == "--warnings":
            warnings = True
        elif arg == "--quiet":
            warnings = False
        elif arg.startswith("--reference="):
            reference_files.append(arg.split("=", 1)[1])
        elif arg == "--reference":
            idx += 1
            reference_files.append(argv[idx])
        elif arg.startswith("--dump-types="):
            dump_types_file = arg.split("=", 1)[1]
        elif arg == "--dump-types":
            idx += 1
            dump_types_file = argv[idx]
        else:
            raise ValueError(f"unsupported fixture arg: {arg}")
        idx += 1

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

    for rel in (GENKSYMS_ZIG, HELP_FIXTURE, CASES_FIXTURE, *EXPECTED_FIXTURES, MAKEFILE):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    makefile_text = read_text(root, MAKEFILE)
    genksyms_text = read_text(root, GENKSYMS_ZIG)

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if '@embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json")' not in genksyms_text:
        issues.append(("MISSING_HELP_FIXTURE_EMBED", HELP_FIXTURE))

    help_payload = json.loads(read_text(root, HELP_FIXTURE))
    if help_payload != {"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}:
        issues.append(("HELP_FIXTURE_MISMATCH", HELP_FIXTURE))

    cases = json.loads(read_text(root, CASES_FIXTURE))
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
        GENKSYMS_ZIG,
        'const help_expected_json = @embedFile("../../zigux/tests/fixtures/genksyms_bridge/help_expected.json");\n',
    )
    write_text(root, HELP_FIXTURE, json.dumps({"stdout": "", "stderr": HELP_USAGE, "exit_code": 0}, indent=2) + "\n")
    write_text(
        root,
        CASES_FIXTURE,
        json.dumps(
            [
                {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
                {
                    "name": "debug_reference_types",
                    "args": ["-d", "-r", "ref.symvers", "-T", "types.symtypes"],
                    "expected_file": "debug_reference_types_expected.json",
                },
                {
                    "name": "long_options",
                    "args": ["--debug", "--dump", "--reference=foo.symref", "--dump-types", "types.symtypes", "--preserve"],
                    "expected_file": "long_options_expected.json",
                },
                {
                    "name": "quiet_overrides_warning",
                    "args": ["--warnings", "--quiet", "--reference", "bar.symref"],
                    "expected_file": "quiet_overrides_warning_expected.json",
                },
            ],
            indent=2,
        )
        + "\n",
    )
    for rel, argv in {
        "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json": [],
        "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json": ["-d", "-r", "ref.symvers", "-T", "types.symtypes"],
        "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json": ["--debug", "--dump", "--reference=foo.symref", "--dump-types", "types.symtypes", "--preserve"],
        "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json": ["--warnings", "--quiet", "--reference", "bar.symref"],
    }.items():
        write_text(root, rel, json.dumps(parse_args(argv), indent=2) + "\n")


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

    print("GENKSYMS_BRIDGE_SELF_TEST=pass")
    print(f"GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={checks}")
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
    print(f"GENKSYMS_BRIDGE_REQUIRED_PATH_COUNT={2 + len(EXPECTED_FIXTURES) + 2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
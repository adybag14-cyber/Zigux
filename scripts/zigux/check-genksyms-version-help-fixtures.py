#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
GENKSYMS_ZIG = "scripts/zigux/genksyms.zig"
HELP_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/help_expected.json"
VERSION_BEFORE_SHORT_HELP_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/version_before_short_help_expected.json"
VERSION_BEFORE_LONG_HELP_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/version_before_long_help_expected.json"

USAGE = (
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
VERSION_TEXT = "genksyms version 2.5.60\n"

EXPECTED_HELP = {
    "stdout": "",
    "stderr": USAGE,
    "exit_code": 0,
}
EXPECTED_VERSION_BEFORE_HELP = {
    "stdout": "",
    "stderr": VERSION_TEXT + USAGE,
    "exit_code": 0,
}

EXPECTED_SELF_TEST_CASE_COUNT = 8


def read_json(root: Path, rel: str) -> object:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    genksyms_path = root / GENKSYMS_ZIG
    if not genksyms_path.exists():
        issues.append(("MISSING_REQUIRED_PATH", GENKSYMS_ZIG))
    else:
        genksyms_text = genksyms_path.read_text(encoding="utf-8")
        if "genksyms [-dDpwqhV] [-r file] [-T file] > /path/to/.tmp_obj.ver" not in genksyms_text:
            issues.append(("USAGE_LINE_MISMATCH", GENKSYMS_ZIG))

    for rel in (HELP_FIXTURE, VERSION_BEFORE_SHORT_HELP_FIXTURE, VERSION_BEFORE_LONG_HELP_FIXTURE):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    help_payload = read_json(root, HELP_FIXTURE)
    if help_payload != EXPECTED_HELP:
        issues.append(("HELP_FIXTURE_MISMATCH", HELP_FIXTURE))

    short_help_payload = read_json(root, VERSION_BEFORE_SHORT_HELP_FIXTURE)
    if short_help_payload != EXPECTED_VERSION_BEFORE_HELP:
        issues.append(("VERSION_BEFORE_SHORT_HELP_FIXTURE_MISMATCH", VERSION_BEFORE_SHORT_HELP_FIXTURE))

    long_help_payload = read_json(root, VERSION_BEFORE_LONG_HELP_FIXTURE)
    if long_help_payload != EXPECTED_VERSION_BEFORE_HELP:
        issues.append(("VERSION_BEFORE_LONG_HELP_FIXTURE_MISMATCH", VERSION_BEFORE_LONG_HELP_FIXTURE))

    if short_help_payload != long_help_payload:
        issues.append(("VERSION_BEFORE_HELP_FIXTURES_DIVERGED", "short_vs_long"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_VERSION_HELP_FIXTURES=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        GENKSYMS_ZIG,
        "const usage_text =\n"
        '    "Usage:\\n" ++\n'
        '    "genksyms [-dDpwqhV] [-r file] [-T file] > /path/to/.tmp_obj.ver\\n";\n',
    )
    write_text(root, HELP_FIXTURE, json.dumps(EXPECTED_HELP, indent=2) + "\n")
    write_text(root, VERSION_BEFORE_SHORT_HELP_FIXTURE, json.dumps(EXPECTED_VERSION_BEFORE_HELP, indent=2) + "\n")
    write_text(root, VERSION_BEFORE_LONG_HELP_FIXTURE, json.dumps(EXPECTED_VERSION_BEFORE_HELP, indent=2) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_genksyms_version_help_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, HELP_FIXTURE, "{}\n")
        assert ("HELP_FIXTURE_MISMATCH", HELP_FIXTURE) in validate(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, VERSION_BEFORE_SHORT_HELP_FIXTURE, "{}\n")
        assert ("VERSION_BEFORE_SHORT_HELP_FIXTURE_MISMATCH", VERSION_BEFORE_SHORT_HELP_FIXTURE) in validate(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, VERSION_BEFORE_LONG_HELP_FIXTURE, "{}\n")
        assert ("VERSION_BEFORE_LONG_HELP_FIXTURE_MISMATCH", VERSION_BEFORE_LONG_HELP_FIXTURE) in validate(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            VERSION_BEFORE_LONG_HELP_FIXTURE,
            json.dumps(EXPECTED_HELP, indent=2) + "\n",
        )
        assert ("VERSION_BEFORE_HELP_FIXTURES_DIVERGED", "short_vs_long") in validate(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, GENKSYMS_ZIG, "const usage_text = \"Usage:\\nlegacy\\n\";\n")
        assert ("USAGE_LINE_MISMATCH", GENKSYMS_ZIG) in validate(root)
        checks += 1

        build_self_test_root(root)
        (root / VERSION_BEFORE_SHORT_HELP_FIXTURE).unlink()
        assert ("MISSING_REQUIRED_PATH", VERSION_BEFORE_SHORT_HELP_FIXTURE) in validate(root)
        checks += 1

        build_self_test_root(root)
        (root / HELP_FIXTURE).unlink()
        assert ("MISSING_REQUIRED_PATH", HELP_FIXTURE) in validate(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_VERSION_HELP_FIXTURES_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_VERSION_HELP_FIXTURES_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current genksyms version-before-help fixture packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_VERSION_HELP_FIXTURES=pass")
    print("PHASE2_GENKSYMS_VERSION_HELP_FIXTURE_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
GENKSYMS_ZIG = ROOT / "scripts" / "zigux" / "genksyms.zig"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "unexpected_abbreviated_version_argument_expected.json"

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

ANCHOR = 'test "genksyms bridge canonicalizes unexpected abbreviated version argument failures" {'

EXPECTED_PAYLOAD = {
    "stdout": "",
    "stderr": "option '--version' doesn't allow an argument\n" + HELP_USAGE,
    "exit_code": 1,
}

EXPECTED_SELF_TEST_CASE_COUNT = 6


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> tuple[object | None, tuple[str, str] | None]:
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError:
        return None, ("INVALID_FIXTURE_JSON", path.name)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    genksyms_path = root / GENKSYMS_ZIG.relative_to(ROOT)
    fixture_path = root / FIXTURE.relative_to(ROOT)

    for path in (genksyms_path, fixture_path):
        if not path.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(root).as_posix()))
    if issues:
        return issues

    anchor_count = count_exact_lines(read_text(genksyms_path), ANCHOR)
    if anchor_count == 0:
        issues.append(("MISSING_ANCHOR", ANCHOR))
    elif anchor_count != 1:
        issues.append(("DUPLICATE_ANCHOR", f"{ANCHOR}:count={anchor_count}"))

    payload, payload_issue = read_json(fixture_path)
    if payload_issue is not None:
        issues.append(payload_issue)
        return issues
    if payload != EXPECTED_PAYLOAD:
        issues.append(("FIXTURE_MISMATCH", fixture_path.name))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("GENKSYMS_ABBREVIATED_VERSION_OUTPUT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root / GENKSYMS_ZIG.relative_to(ROOT),
        "const std = @import(\"std\");\n\n" + ANCHOR + "\n}\n",
    )
    write_text(root / FIXTURE.relative_to(ROOT), json.dumps(EXPECTED_PAYLOAD, indent=2) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_genksyms_abbrev_version_output_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        (root / FIXTURE.relative_to(ROOT)).unlink()
        assert ("MISSING_REQUIRED_PATH", FIXTURE.relative_to(ROOT).as_posix()) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        fixture_path = root / FIXTURE.relative_to(ROOT)
        fixture_path.write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_JSON", fixture_path.name) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        fixture_path = root / FIXTURE.relative_to(ROOT)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["exit_code"] = 0
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("FIXTURE_MISMATCH", fixture_path.name) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        genksyms_path = root / GENKSYMS_ZIG.relative_to(ROOT)
        genksyms_path.write_text("const std = @import(\"std\");\n", encoding="utf-8")
        assert ("MISSING_ANCHOR", ANCHOR) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        genksyms_path = root / GENKSYMS_ZIG.relative_to(ROOT)
        genksyms_path.write_text(
            "const std = @import(\"std\");\n\n" + ANCHOR + "\n}\n" + ANCHOR + "\n}\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_ANCHOR", f"{ANCHOR}:count=2") in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("GENKSYMS_ABBREVIATED_VERSION_OUTPUT_SELF_TEST=pass")
    print(f"GENKSYMS_ABBREVIATED_VERSION_OUTPUT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the abbreviated --version expected-output packet for scripts/zigux/genksyms.zig."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("GENKSYMS_ABBREVIATED_VERSION_OUTPUT=pass")
    print(f"GENKSYMS_ABBREVIATED_VERSION_OUTPUT_FIXTURE={FIXTURE.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

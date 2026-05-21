#!/usr/bin/env python3
"""Guard the current malformed-JSON Phase 1 bench failure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path.cwd()
)

BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_LINES = (
    'except json.JSONDecodeError as exc:',
    'return ("expectations_json_error", exc)',
)

EXPECTED_JSON_ERROR_SECTION = (
    'if kind == "expectations_json_error":',
    "exc = payload",
    "assert isinstance(exc, json.JSONDecodeError)",
    'print("PHASE1_BENCH_CHECK=fail")',
    'print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
    'print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
    'print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
    "return 1",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def extract_section(text: str, first_line: str) -> list[str]:
    section: list[str] = []
    capturing = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not capturing:
            if line == first_line:
                capturing = True
                section.append(line)
            continue
        if not line:
            return section
        section.append(line)
    return section


def section_contains_expected_lines(section: list[str], expected_lines: tuple[str, ...]) -> bool:
    expected_index = 0
    for line in section:
        if expected_index == len(expected_lines):
            return True
        if line == expected_lines[expected_index]:
            expected_index += 1
    return expected_index == len(expected_lines)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    bench_checker = root / BENCH_CHECKER_REL
    if not bench_checker.is_file():
        return [f"missing_file:{BENCH_CHECKER_REL}"]

    text = read_text(root, BENCH_CHECKER_REL)
    stripped_lines = [line.strip() for line in text.splitlines()]

    for required_line in REQUIRED_LINES:
        count = sum(1 for line in stripped_lines if line == required_line)
        if count != 1:
            issues.append(
                f"{BENCH_CHECKER_REL}:marker_count:{required_line}:expected=1:actual={count}"
            )

    first_line = EXPECTED_JSON_ERROR_SECTION[0]
    first_line_count = sum(1 for line in stripped_lines if line == first_line)
    if first_line_count != 1:
        issues.append(
            f"{BENCH_CHECKER_REL}:marker_count:{first_line}:expected=1:actual={first_line_count}"
        )
        return issues

    actual_section = extract_section(text, first_line)
    if not section_contains_expected_lines(actual_section, EXPECTED_JSON_ERROR_SECTION):
        issues.append(f"{BENCH_CHECKER_REL}:json_error_section:{actual_section!r}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(
        root,
        BENCH_CHECKER_REL,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "",
                "def load_runtime_expectations(path):",
                "    try:",
                "        expectations = load_expectations(path)",
                "    except json.JSONDecodeError as exc:",
                '        return ("expectations_json_error", exc)',
                "",
                "def main(kind, payload):",
                '    if kind == "expectations_json_error":',
                "        exc = payload",
                "        assert isinstance(exc, json.JSONDecodeError)",
                '        print("PHASE1_BENCH_CHECK=fail")',
                '        print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
                '        print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
                '        print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
                "        return 1",
                "",
            ]
        )
        + "\n",
    )


def mutate_remove_line(root: Path, line: str) -> None:
    path = root / BENCH_CHECKER_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(f"{line}\n", "", 1), encoding="utf-8")


def mutate_duplicate_line(root: Path, line: str) -> None:
    path = root / BENCH_CHECKER_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(line, f"{line}\n{line}", 1), encoding="utf-8")


def mutate_insert_reason_line(root: Path) -> None:
    path = root / BENCH_CHECKER_REL
    text = path.read_text(encoding="utf-8")
    old = '        print("PHASE1_BENCH_CHECK=fail")\n'
    new = (
        '        print("PHASE1_BENCH_CHECK=fail")\n'
        '        print("PHASE1_BENCH_CHECK_REASON=expectations_json_error")\n'
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_wrong_reason_payload(root: Path) -> list[str]:
    path = root / BENCH_CHECKER_REL
    text = path.read_text(encoding="utf-8")
    old = '        print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))\n'
    new = '        print("EXPECTATIONS_JSON_ERROR={}".format(exc.colno))\n'
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return extract_section(path.read_text(encoding="utf-8"), EXPECTED_JSON_ERROR_SECTION[0])


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-json-error-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST=fail")
            print(f"case=baseline:actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-json-error-packet-reason-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        mutate_insert_reason_line(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST=fail")
            print(f"case=optional_reason_line:actual={issues!r}")
            return 1

    negative_cases = (
        (
            "missing_decode_return",
            lambda root: mutate_remove_line(root, '        return ("expectations_json_error", exc)'),
            f"{BENCH_CHECKER_REL}:marker_count:return (\"expectations_json_error\", exc):expected=1:actual=0",
        ),
        (
            "duplicate_decode_return",
            lambda root: mutate_duplicate_line(root, '        return ("expectations_json_error", exc)'),
            f"{BENCH_CHECKER_REL}:marker_count:return (\"expectations_json_error\", exc):expected=1:actual=2",
        ),
        (
            "missing_column_print",
            lambda root: mutate_remove_line(root, '        print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))'),
            f"{BENCH_CHECKER_REL}:json_error_section:{['if kind == \"expectations_json_error\":', 'exc = payload', 'assert isinstance(exc, json.JSONDecodeError)', 'print(\"PHASE1_BENCH_CHECK=fail\")', 'print(\"EXPECTATIONS_JSON_ERROR={}\".format(exc.msg))', 'print(\"EXPECTATIONS_JSON_LINE={}\".format(exc.lineno))', 'return 1']!r}",
        ),
        (
            "wrong_reason_payload",
            mutate_wrong_reason_payload,
            None,
        ),
    )

    for label, mutate, expected in negative_cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-json-error-packet-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            result = mutate(root)
            issues = collect_issues(root)
            if label == "wrong_reason_payload":
                expected = f"{BENCH_CHECKER_REL}:json_error_section:{result!r}"
            if issues != [expected]:
                print("PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST=fail")
                print(f"case={label}")
                print(f"expected={[expected]!r}")
                print(f"actual={issues!r}")
                return 1

    print("PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST=pass")
    print("PHASE1_BENCH_JSON_ERROR_PACKET_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_JSON_ERROR_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_JSON_ERROR_PACKET=pass")
    print("PHASE1_BENCH_JSON_ERROR_PACKET_REQUIRED_FILE_COUNT=1")
    print(f"PHASE1_BENCH_JSON_ERROR_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_LINES) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

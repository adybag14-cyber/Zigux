#!/usr/bin/env python3
"""Guard the live Lane 16 bench checker runtime-failure packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_FILES = (
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
)

MARKERS = {
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        "def load_runtime_expectations(path: Path) -> tuple[str, object]:",
        "def load_runtime_bench_source(path: Path) -> tuple[str, object]:",
        "def validate_find_bit_bench_source(text: str) -> tuple[str, object]:",
        '[zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],',
        'print("PHASE1_BENCH_CHECK=pass")',
        'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
        'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
        'print(f"PHASE1_BENCH_ZIG={zig}")',
    ),
}

EXPECTED_SECTIONS = {
    BENCH_CHECKER_REL: (
        (
            'if kind == "missing_expectations_file":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            'print(f"EXPECTATIONS_PATH={payload}")',
            "return 1",
        ),
        (
            'if kind == "expectations_json_error":',
            "exc = payload",
            "assert isinstance(exc, json.JSONDecodeError)",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
            'print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
            'print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
            "return 1",
        ),
        (
            "kind, payload = load_runtime_bench_source(PHASE1_BENCH)",
            'if kind != "pass":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            "print(payload)",
            "return 1",
        ),
        (
            "if result.returncode != 0:",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"BENCH_COMMAND_EXIT={result.returncode}")',
            "if result.stdout:",
            'print(result.stdout.rstrip("\\n"))',
            "if result.stderr:",
            'print(result.stderr.rstrip("\\n"))',
            "return 1",
        ),
    ),
}

FORBIDDEN_FRAGMENTS = {
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py",
    ),
}


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


def replace_section(text: str, first_line: str, replacement: list[str]) -> str:
    lines = text.splitlines()
    start_index: int | None = None
    end_index = len(lines)
    for index, raw_line in enumerate(lines):
        if raw_line.strip() == first_line:
            start_index = index
            break
    if start_index is None:
        raise ValueError(f"section not found: {first_line}")
    for index in range(start_index + 1, len(lines)):
        if not lines[index].strip():
            end_index = index
            break
    new_lines = lines[:start_index] + replacement + lines[end_index:]
    return "\n".join(new_lines) + "\n"


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
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        lines = text.splitlines()
        for marker in markers:
            if relative_path == WORKFLOW_REL:
                count = sum(1 for line in lines if line.strip() == marker)
            else:
                count = text.count(marker)
            if count != 1:
                issues.append(f"{relative_path}:marker_count:{marker}:expected=1:actual={count}")

        for fragment in FORBIDDEN_FRAGMENTS.get(relative_path, ()): 
            if relative_path == WORKFLOW_REL:
                count = sum(1 for line in lines if line.strip() == fragment)
            else:
                count = text.count(fragment)
            if count != 0:
                issues.append(f"{relative_path}:forbidden:{fragment}:actual={count}")

        stripped_lines = [line.strip() for line in lines]
        for expected_section in EXPECTED_SECTIONS.get(relative_path, ()): 
            first_line = expected_section[0]
            first_line_count = sum(1 for line in stripped_lines if line == first_line)
            if first_line_count != 1:
                issues.append(
                    f"{relative_path}:marker_count:{first_line}:expected=1:actual={first_line_count}"
                )
                continue
            actual_section = extract_section(text, first_line)
            if not section_contains_expected_lines(actual_section, expected_section):
                issues.append(f"{relative_path}:section:{first_line}:{actual_section!r}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_workflow_file() -> str:
    return "\n".join(
        (
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Self-test current Phase 1 bench checker",
            "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            "",
        )
    )


def build_bench_checker_file() -> str:
    lines = [
        "import json",
        "from pathlib import Path",
        "",
        "EXPECTATIONS = Path('zigux/tests/fixtures/phase1_bench_expectations.json')",
        "PHASE1_BENCH = Path('zigux/tests/phase1_bench.zig')",
        "",
        "def validate_find_bit_bench_source(text: str) -> tuple[str, object]:",
        '    return ("pass", text)',
        "",
        "def load_runtime_expectations(path: Path) -> tuple[str, object]:",
        "    pass",
        "",
        'if kind == "missing_expectations_file":',
        '    print("PHASE1_BENCH_CHECK=fail")',
        '    print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
        '    print(f"EXPECTATIONS_PATH={payload}")',
        "    return 1",
        "",
        'if kind == "expectations_json_error":',
        "    exc = payload",
        "    assert isinstance(exc, json.JSONDecodeError)",
        '    print("PHASE1_BENCH_CHECK=fail")',
        '    print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
        '    print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
        '    print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
        "    return 1",
        "",
        "def load_runtime_bench_source(path: Path) -> tuple[str, object]:",
        "    pass",
        "",
        "kind, payload = load_runtime_bench_source(PHASE1_BENCH)",
        'if kind != "pass":',
        '    print("PHASE1_BENCH_CHECK=fail")',
        '    print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
        "    print(payload)",
        "    return 1",
        "",
        "result = type('Result', (), {'returncode': 1, 'stdout': 'oops', 'stderr': 'bad'})()",
        "if result.returncode != 0:",
        '    print("PHASE1_BENCH_CHECK=fail")',
        '    print(f"BENCH_COMMAND_EXIT={result.returncode}")',
        "    if result.stdout:",
        '        print(result.stdout.rstrip("\\n"))',
        "    if result.stderr:",
        '        print(result.stderr.rstrip("\\n"))',
        "    return 1",
        "",
        "zig = 'zig'",
        "result = None",
        '[zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],',
        'print("PHASE1_BENCH_CHECK=pass")',
        'print(f"PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}")',
        'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
        'print(f"PHASE1_BENCH_ZIG={zig}")',
        "",
    ]
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_text(root, WORKFLOW_REL, build_workflow_file())
    write_text(root, BENCH_CHECKER_REL, build_bench_checker_file())


def mutate_remove_line(root: Path, relative_path: str, needle: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(needle + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_line(root: Path, relative_path: str, needle: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")


def mutate_append_line(root: Path, relative_path: str, needle: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + needle + "\n", encoding="utf-8")


def mutate_section_insert_after(
    root: Path,
    relative_path: str,
    first_line: str,
    anchor_line: str,
    inserted_lines: tuple[str, ...],
) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    anchor_index = actual_section.index(anchor_line)
    updated_section = (
        actual_section[: anchor_index + 1]
        + list(inserted_lines)
        + actual_section[anchor_index + 1 :]
    )
    path.write_text(replace_section(text, first_line, updated_section), encoding="utf-8")
    return updated_section


def mutate_section_remove_line(root: Path, relative_path: str, first_line: str, line_index: int) -> list[str]:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    updated_section = actual_section[:line_index] + actual_section[line_index + 1 :]
    path.write_text(replace_section(text, first_line, updated_section), encoding="utf-8")
    return updated_section


def run_self_test() -> int:
    expected_missing_expectations_section = (
        f'{BENCH_CHECKER_REL}:section:if kind == "missing_expectations_file"::'
        + repr(
            [
                'if kind == "missing_expectations_file":',
                'print("PHASE1_BENCH_CHECK=fail")',
                'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
                "return 1",
            ]
        )
    )
    expected_json_error_section = (
        f'{BENCH_CHECKER_REL}:section:if kind == "expectations_json_error"::'
        + repr(
            [
                'if kind == "expectations_json_error":',
                "exc = payload",
                "assert isinstance(exc, json.JSONDecodeError)",
                'print("PHASE1_BENCH_CHECK=fail")',
                'print("EXPECTATIONS_JSON_ERROR={}".format(exc.msg))',
                'print("EXPECTATIONS_JSON_LINE={}".format(exc.lineno))',
                "return 1",
            ]
        )
    )
    expected_bench_source_section_missing_reason = (
        f"{BENCH_CHECKER_REL}:section:kind, payload = load_runtime_bench_source(PHASE1_BENCH):"
        + repr(
            [
                "kind, payload = load_runtime_bench_source(PHASE1_BENCH)",
                'if kind != "pass":',
                'print("PHASE1_BENCH_CHECK=fail")',
                "print(payload)",
                "return 1",
            ]
        )
    )
    expected_command_exit_section = (
        f"{BENCH_CHECKER_REL}:section:if result.returncode != 0::"
        + repr(
            [
                "if result.returncode != 0:",
                'print("PHASE1_BENCH_CHECK=fail")',
                "if result.stdout:",
                'print(result.stdout.rstrip("\\n"))',
                "if result.stderr:",
                'print(result.stderr.rstrip("\\n"))',
                "return 1",
            ]
        )
    )

    with tempfile.TemporaryDirectory(prefix="phase1-bench-runtime-fail-packets-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SELF_TEST=fail")
            print(f"actual={issues!r}")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-runtime-fail-packets-interleaved-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        mutate_section_insert_after(
            root,
            BENCH_CHECKER_REL,
            'if kind == "expectations_json_error":',
            'print("PHASE1_BENCH_CHECK=fail")',
            ('print(f"PHASE1_BENCH_CHECK_REASON={kind}")',),
        )
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SELF_TEST=fail")
            print("case=json_error_reason_line_allowed")
            print(f"actual={issues!r}")
            return 1

    cases = [
        (
            "remove_workflow_selftest",
            WORKFLOW_REL,
            "remove",
            "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            f"{WORKFLOW_REL}:marker_count:run: python3 scripts/zigux/check-phase1-bench.py --self-test:expected=1:actual=0",
        ),
        (
            "duplicate_workflow_selftest",
            WORKFLOW_REL,
            "duplicate",
            "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            f"{WORKFLOW_REL}:marker_count:run: python3 scripts/zigux/check-phase1-bench.py --self-test:expected=1:actual=2",
        ),
        (
            "forbidden_direct_workflow_run",
            WORKFLOW_REL,
            "append",
            "run: python3 scripts/zigux/check-phase1-bench.py",
            f"{WORKFLOW_REL}:forbidden:run: python3 scripts/zigux/check-phase1-bench.py:actual=1",
        ),
        (
            "remove_missing_expectations_path",
            BENCH_CHECKER_REL,
            "remove",
            'print(f"EXPECTATIONS_PATH={payload}")',
            expected_missing_expectations_section,
        ),
        (
            "remove_json_error_column",
            BENCH_CHECKER_REL,
            "remove",
            'print("EXPECTATIONS_JSON_COLUMN={}".format(exc.colno))',
            expected_json_error_section,
        ),
        (
            "remove_bench_source_reason",
            BENCH_CHECKER_REL,
            "remove_section_line",
            'kind, payload = load_runtime_bench_source(PHASE1_BENCH)',
            expected_bench_source_section_missing_reason,
        ),
        (
            "remove_bench_command_exit",
            BENCH_CHECKER_REL,
            "remove",
            'print(f"BENCH_COMMAND_EXIT={result.returncode}")',
            expected_command_exit_section,
        ),
    ]

    for label, relative_path, operation, needle, expected in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-runtime-fail-packets-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if operation == "remove":
                mutate_remove_line(root, relative_path, needle)
            elif operation == "duplicate":
                mutate_duplicate_line(root, relative_path, needle)
            elif operation == "remove_section_line":
                mutate_section_remove_line(root, relative_path, needle, 3)
            else:
                mutate_append_line(root, relative_path, needle)
            issues = collect_issues(root)
            if issues != [expected]:
                print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SELF_TEST=fail")
                print(f"case={label}")
                print(f"expected={expected}")
                print(f"actual={issues!r}")
                return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-runtime-fail-packets-section-remove-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        actual_section = mutate_section_remove_line(
            root,
            BENCH_CHECKER_REL,
            "if result.returncode != 0:",
            3,
        )
        expected = f'{BENCH_CHECKER_REL}:section:if result.returncode != 0::{actual_section!r}'
        issues = collect_issues(root)
        if issues != [expected]:
            print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SELF_TEST=fail")
            print("case=remove_command_stdout_line")
            print(f"expected={expected}")
            print(f"actual={issues!r}")
            return 1

    print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SELF_TEST=pass")
    print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument("--write-sample-root", help="write a sample repository root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        build_sample_repo(root)
        print(f"PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SAMPLE_ROOT={root}")
        return 0

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_RUNTIME_FAIL_PACKETS=pass")
    print(f"PHASE1_BENCH_RUNTIME_FAIL_PACKETS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_RUNTIME_FAIL_PACKETS_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    print(
        "PHASE1_BENCH_RUNTIME_FAIL_PACKETS_SECTION_COUNT="
        f"{sum(len(sections) for sections in EXPECTED_SECTIONS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

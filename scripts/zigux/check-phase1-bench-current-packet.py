#!/usr/bin/env python3
"""Guard the current Lane 16 Phase 1 bench packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path.cwd()
)

PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
    ),
    SCRIPTS_README_REL: (
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "That shared smoke route should stay paired with the restored closure-side validator, the direct owner-map and string-review guards, the shipped bench checker, and the committed helper manifest so the tests-root note matches the same bounded Phase 1 packet already named by the docs root, lane-sequencing note, and scripts-root reminder.",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        'class DuplicateTrackingDict(dict[str, object]):',
        'def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:',
        'def load_runtime_expectations(path: Path) -> tuple[str, object]:',
        'return ("missing_expectations_file", path)',
        'return ("expectations_json_error", exc)',
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
    ),
}

ORDERED_SECTIONS = {
    BENCH_CHECKER_REL: (
        (
            "for key, value, expected_kind in (",
            '("PHASE1_BENCH_STRING_CHECKSUM", "5", "missing_string_exact_checksums"),',
            '("PHASE1_BENCH_HWEIGHT_CHECKSUM", "6", "missing_hweight_exact_checksums"),',
            '("PHASE1_BENCH_LIST_SORT_CHECKSUM", "7", "missing_list_sort_exact_checksums"),',
            "):",
            'missing_output = ok_output.replace(f"\\n{key}={value}", "")',
            "kind, payload = validate_output(base_expectations(), missing_output)",
            'assert_case(kind == reason, "missing exact category", (reason, kind, payload))',
            'assert_case(payload == [key], "missing exact payload", payload)',
            "case_count += 1",
        ),
        (
            "status_mismatch_output = ok_output.replace(",
            '"PHASE1_BENCH=pass",',
            '"PHASE1_BENCH=fail",',
            "1,",
            ")",
            "kind, payload = validate_output(expectations, status_mismatch_output)",
            'assert kind == "status"',
            'assert payload == ("pass", "fail")',
            "case_count += 1",
        ),
        (
            'if kind == "expectations_json_error":',
            "exc = payload",
            "assert isinstance(exc, json.JSONDecodeError)",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")',
            'print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")',
            'print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")',
            "return 1",
        ),
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


def contains_subsequence(section: list[str], expected_lines: tuple[str, ...]) -> bool:
    index = 0
    for line in section:
        if index == len(expected_lines):
            return True
        if line == expected_lines[index]:
            index += 1
    return index == len(expected_lines)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = sum(1 for line in text.splitlines() if marker in line)
            if count != 1:
                issues.append(
                    f"{relative_path}:marker_count:{marker}:expected=1:actual={count}"
                )
        for expected_lines in ORDERED_SECTIONS.get(relative_path, ()):
            first_line = expected_lines[0]
            stripped_lines = [line.strip() for line in text.splitlines()]
            first_line_count = sum(1 for line in stripped_lines if line == first_line)
            if first_line_count != 1:
                issues.append(
                    f"{relative_path}:marker_count:{first_line}:expected=1:actual={first_line_count}"
                )
                continue
            actual_section = extract_section(text, first_line)
            if not contains_subsequence(actual_section, expected_lines):
                issues.append(
                    f"{relative_path}:ordered_section:{first_line}:{actual_section!r}"
                )
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_file(relative_path: str) -> str:
    lines = list(REQUIRED_MARKERS[relative_path])
    for section in ORDERED_SECTIONS.get(relative_path, ()):
        lines.extend(section)
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, build_sample_file(relative_path))


def replace_section(
    root: Path,
    relative_path: str,
    first_line: str,
    updated_section: list[str],
) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    actual_section = extract_section(text, first_line)
    original = "\n".join(actual_section)
    updated = "\n".join(updated_section)
    path.write_text(text.replace(original, updated, 1), encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        assert collect_issues(root) == []
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-interleaved-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            "for key, value, expected_kind in (",
        )
        updated = (
            section[:1]
            + ['("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM", "1", "ignored_extra"),']
            + section[1:]
        )
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        assert collect_issues(root) == []
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-multiline-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            "status_mismatch_output = ok_output.replace(",
        )
        updated = section[:4] + ["helper_line = status_mismatch_output"] + section[4:]
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        assert collect_issues(root) == []
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-json-gap-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            'if kind == "expectations_json_error":',
        )
        updated = section[:4] + ["helper_line = exc.msg"] + section[4:]
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        assert collect_issues(root) == []
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-missing-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            "status_mismatch_output = ok_output.replace(",
        )
        updated = [line for line in section if line != 'assert payload == ("pass", "fail")']
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        issues = collect_issues(root)
        assert len(issues) == 1
        assert issues[0].startswith(
            "scripts/zigux/check-phase1-bench.py:ordered_section:status_mismatch_output = ok_output.replace("
        )
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-json-missing-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            'if kind == "expectations_json_error":',
        )
        updated = [line for line in section if line != 'print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")']
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        issues = collect_issues(root)
        assert len(issues) == 1
        assert issues[0].startswith(
            'scripts/zigux/check-phase1-bench.py:ordered_section:if kind == "expectations_json_error":'
        )
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-file-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        (root / WORKFLOW_REL).unlink()
        assert collect_issues(root) == [f"missing_file:{WORKFLOW_REL}"]
        case_count += 1

    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_CURRENT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_CURRENT_PACKET=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_CURRENT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
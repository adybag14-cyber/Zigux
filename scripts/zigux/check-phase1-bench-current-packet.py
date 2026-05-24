#!/usr/bin/env python3
"""Guard the current Lane 16 Phase 1 bench packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

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
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    ),
    WORKFLOW_REL: (
        "- name: Self-test current Phase 1 bench checker",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        "def repo_root(root: str | None) -> Path:",
        "def expectations_path(root: Path) -> Path:",
        "def bench_source_path(root: Path) -> Path:",
        'return ("missing_expectations_file", path)',
        'return ("expectations_json_error", exc)',
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
        'parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")',
    ),
}

ORDERED_SECTIONS = {
    BENCH_CHECKER_REL: (
        (
            'with tempfile.TemporaryDirectory(prefix="phase1-bench-root-") as tmp:',
            "root = Path(tmp)",
            "source_path = bench_source_path(root)",
            "source_path.parent.mkdir(parents=True, exist_ok=True)",
            'source_path.write_text(build_full_bench_source(), encoding="utf-8")',
            "expectations_file = expectations_path(root)",
            "expectations_file.parent.mkdir(parents=True, exist_ok=True)",
            'expectations_file.write_text(json.dumps(base_expectations(), indent=2) + "\\n", encoding="utf-8")',
            'assert_case(repo_root(str(root)) == root.resolve(), "repo root override")',
            "kind, payload = load_runtime_bench_source(bench_source_path(root))",
            'assert_case(kind == "pass", "bench source root override", (kind, payload))',
            "kind, payload = load_runtime_expectations(expectations_path(root))",
            'assert_case(kind == "pass", "expectations root override", (kind, payload))',
            "case_count += 3",
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
        (
            'print("PHASE1_BENCH_CHECK=pass")',
            'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
            'print(f"PHASE1_BENCH_SOURCE={phase1_bench}")',
            'print(f"PHASE1_BENCH_ZIG={zig}")',
            "return 0",
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

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-root-interleaved-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            'with tempfile.TemporaryDirectory(prefix="phase1-bench-root-") as tmp:',
        )
        updated = section[:6] + ["helper_line = expectations_file"] + section[6:]
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        assert collect_issues(root) == []
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-json-interleaved-") as tmpdir:
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

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-success-interleaved-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            'print("PHASE1_BENCH_CHECK=pass")',
        )
        updated = section[:2] + ["helper_line = zig"] + section[2:]
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        assert collect_issues(root) == []
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-root-missing-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        section = extract_section(
            read_text(root, BENCH_CHECKER_REL),
            'with tempfile.TemporaryDirectory(prefix="phase1-bench-root-") as tmp:',
        )
        updated = [line for line in section if line != 'assert_case(kind == "pass", "expectations root override", (kind, payload))']
        replace_section(root, BENCH_CHECKER_REL, section[0], updated)
        issues = collect_issues(root)
        assert len(issues) == 1
        assert issues[0].startswith(
            'scripts/zigux/check-phase1-bench.py:ordered_section:with tempfile.TemporaryDirectory(prefix="phase1-bench-root-") as tmp:'
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

    with tempfile.TemporaryDirectory(prefix="lane16-current-packet-file-missing-") as tmpdir:
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
    parser.add_argument("--root", help="Override repository root")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test")
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

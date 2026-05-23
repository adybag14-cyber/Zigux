#!/usr/bin/env python3
"""Guard the live Lane 16 Phase 1 bench source-failure packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = (
    BENCH_CHECKER_REL,
    WORKFLOW_REL,
)

BENCH_MARKERS = (
    'PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"',
    "FIND_BIT_REQUIRED_SOURCE_MARKERS = {",
    '"find_bit_bench_fn": "fn findBitBench() struct { checksum: u64 } {",',
    "RBTREE_REQUIRED_SOURCE_MARKERS = {",
    '"rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",',
    "SOURCE_MARKER_SETS = (",
    'def validate_bench_source(text: str) -> tuple[str, object]:',
    'return ("bench_source_missing_markers", missing)',
    'def load_runtime_bench_source(path: Path) -> tuple[str, object]:',
    'return ("missing_bench_source_file", path)',
    "kind, payload = load_runtime_bench_source(PHASE1_BENCH)",
    'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    bench_text = read_text(root, BENCH_CHECKER_REL)
    for marker in BENCH_MARKERS:
        count = bench_text.count(marker)
        if count != 1:
            issues.append(f"{BENCH_CHECKER_REL}:marker_count:{marker}:expected=1:actual={count}")

    workflow_lines = [line.strip() for line in read_text(root, WORKFLOW_REL).splitlines()]
    for marker in WORKFLOW_MARKERS:
        count = sum(1 for line in workflow_lines if line == marker)
        if count != 1:
            issues.append(f"{WORKFLOW_REL}:marker_count:{marker}:expected=1:actual={count}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_bench_checker() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "from pathlib import Path",
            "",
            'PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"',
            "",
            "FIND_BIT_REQUIRED_SOURCE_MARKERS = {",
            '    "find_bit_bench_fn": "fn findBitBench() struct { checksum: u64 } {",',
            "}",
            "",
            "RBTREE_REQUIRED_SOURCE_MARKERS = {",
            '    "rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",',
            "}",
            "",
            "SOURCE_MARKER_SETS = (",
            "    FIND_BIT_REQUIRED_SOURCE_MARKERS,",
            "    RBTREE_REQUIRED_SOURCE_MARKERS,",
            ")",
            "",
            'def validate_bench_source(text: str) -> tuple[str, object]:',
            "    missing: list[str] = []",
            "    if missing:",
            '        return ("bench_source_missing_markers", missing)',
            '    return ("pass", text)',
            "",
            'def load_runtime_bench_source(path: Path) -> tuple[str, object]:',
            "    try:",
            '        text = path.read_text(encoding="utf-8")',
            "    except FileNotFoundError:",
            '        return ("missing_bench_source_file", path)',
            "    return validate_bench_source(text)",
            "",
            "kind, payload = load_runtime_bench_source(PHASE1_BENCH)",
            'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
            "",
        ]
    ) + "\n"


def sample_workflow() -> str:
    return "\n".join(
        [
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Self-test phase1 bench checker",
            "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        ]
    ) + "\n"


def build_sample_root(root: Path) -> None:
    write_text(root, BENCH_CHECKER_REL, sample_bench_checker())
    write_text(root, WORKFLOW_REL, sample_workflow())


def expected_marker_issue(relative_path: str, marker: str, actual: int) -> str:
    return f"{relative_path}:marker_count:{marker}:expected=1:actual={actual}"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-source-failure-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_SOURCE_FAILURE_PACKET_SELF_TEST=fail")
            print(f"case=pass_root")
            print(f"actual={issues!r}")
            return 1

    cases = [
        ("missing_workflow_marker", WORKFLOW_REL, WORKFLOW_MARKERS[0], "remove"),
        ("duplicate_workflow_marker", WORKFLOW_REL, WORKFLOW_MARKERS[0], "duplicate"),
        ("missing_source_failure_marker", BENCH_CHECKER_REL, 'return ("missing_bench_source_file", path)', "remove"),
        ("missing_source_success_path", BENCH_CHECKER_REL, 'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")', "remove"),
    ]

    for label, relative_path, marker, mode in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-source-failure-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            path = root / relative_path
            text = path.read_text(encoding="utf-8")
            if mode == "remove":
                updated = text.replace(marker + "\n", "", 1)
                expected = expected_marker_issue(relative_path, marker, 0)
            else:
                updated = text.replace(marker, marker + "\n" + marker, 1)
                expected = expected_marker_issue(relative_path, marker, 2)
            path.write_text(updated, encoding="utf-8")
            issues = collect_issues(root)
            if issues != [expected]:
                print("PHASE1_BENCH_SOURCE_FAILURE_PACKET_SELF_TEST=fail")
                print(f"case={label}")
                print(f"expected={expected}")
                print(f"actual={issues!r}")
                return 1

    print("PHASE1_BENCH_SOURCE_FAILURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_SOURCE_FAILURE_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_SOURCE_FAILURE_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_SOURCE_FAILURE_PACKET=pass")
    print(f"PHASE1_BENCH_SOURCE_FAILURE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_SOURCE_FAILURE_PACKET_MARKER_COUNT={len(BENCH_MARKERS) + len(WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

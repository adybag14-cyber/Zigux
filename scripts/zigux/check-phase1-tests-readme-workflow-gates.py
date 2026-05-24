#!/usr/bin/env python3
"""Guard the current Phase 1 tests-root reminder against its live workflow gates."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
)

README_MARKERS = (
    "## Phase 1 host-tools review packet",
    "current direct-readback Phase 1 reminder packet:",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `.github/workflows/zigux-bootstrap.yml`",
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

BENCH_MARKERS = (
    "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
    "def run_self_test() -> None:",
)

SHARED_REMINDER_MARKERS = (
    "\"\"\"Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow.\"\"\"",
    'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
    'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: str, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_stripped_line_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    issues.extend(collect_exact_markers(read_text(root, "zigux/tests/README.md"), "zigux/tests/README.md", README_MARKERS))
    issues.extend(
        collect_stripped_line_markers(
            read_text(root, ".github/workflows/zigux-bootstrap.yml"),
            ".github/workflows/zigux-bootstrap.yml",
            WORKFLOW_MARKERS,
        )
    )
    issues.extend(
        collect_exact_markers(
            read_text(root, "scripts/zigux/check-phase1-bench.py"),
            "scripts/zigux/check-phase1-bench.py",
            BENCH_MARKERS,
        )
    )
    issues.extend(
        collect_exact_markers(
            read_text(root, "scripts/zigux/check-phase1-shared-reminder-packet.py"),
            "scripts/zigux/check-phase1-shared-reminder-packet.py",
            SHARED_REMINDER_MARKERS,
        )
    )
    return issues


def build_sample_repo(root: Path) -> None:
    write_text(root, "zigux/tests/README.md", "\n".join(README_MARKERS) + "\n")
    write_text(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root, "scripts/zigux/check-phase1-bench.py", "\n".join(BENCH_MARKERS) + "\n")
    write_text(
        root,
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "\n".join(SHARED_REMINDER_MARKERS) + "\n",
    )


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-tests-readme-workflow-gates-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("self-test:success:unexpected_failures")
            for item in issues:
                print(item)
            return 1

    def make_missing_file_case(relative_path: str):
        return (
            f"missing_file_{relative_path.replace('/', '_').replace('.', '_')}",
            lambda root, relative_path=relative_path: (root / relative_path).unlink(),
        )

    def make_marker_case(relative_path: str, marker: str, mutation: str):
        mutator = mutate_remove_marker if mutation == "remove" else mutate_duplicate_marker
        return (
            f"{mutation}_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(marker))}",
            lambda root, relative_path=relative_path, marker=marker, mutator=mutator: mutator(
                root, relative_path, marker
            ),
        )

    cases: list[tuple[str, object]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append(make_missing_file_case(relative_path))
    for marker in README_MARKERS:
        cases.append(make_marker_case("zigux/tests/README.md", marker, "remove"))
    for marker in WORKFLOW_MARKERS:
        cases.append(make_marker_case(".github/workflows/zigux-bootstrap.yml", marker, "remove"))
        cases.append(make_marker_case(".github/workflows/zigux-bootstrap.yml", marker, "duplicate"))
    for marker in BENCH_MARKERS:
        cases.append(make_marker_case("scripts/zigux/check-phase1-bench.py", marker, "remove"))
    for marker in SHARED_REMINDER_MARKERS:
        cases.append(make_marker_case("scripts/zigux/check-phase1-shared-reminder-packet.py", marker, "remove"))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-tests-readme-workflow-gates-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            issues = collect_issues(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for item in issues:
                        print(item)
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_TESTS_README_WORKFLOW_GATES_SELF_TEST=pass")
    print(f"PHASE1_TESTS_README_WORKFLOW_GATES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        "--root",
        dest="repo_root",
        help="override the repository root used for checks",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the guard against synthetic positive and negative cases",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root(args.repo_root)
    issues = collect_issues(root)
    if issues:
        for item in issues:
            print(item)
        return 1

    print("PHASE1_TESTS_README_WORKFLOW_GATES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

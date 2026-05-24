#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_CHECKER_PATH = Path("scripts/zigux/check-lane05-split-helper-workflow.py")

WORKFLOW_MARKERS = (
    'CLI_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract checker"',
    'CLI_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract packet"',
    'ALIGN_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-stage alignment checker"',
    'ALIGN_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment packet"',
    'ALIGN_SELFTEST_SELF_TEST_STEP = (',
    'ALIGN_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment selftest packet"',
    "def sample_workflow_text() -> str:",
    "def run_self_test() -> int:",
    'assert check_workflow(good_workflow) == len(ORDERED_STEPS) - 1',
    "duplicate_step = good_workflow.replace(",
    "reordered_steps = good_workflow.replace(",
    'print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")',
    'print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")',
    'print("LANE05_SPLIT_HELPER_WORKFLOW=pass")',
    'print(f"LANE05_SPLIT_HELPER_WORKFLOW_STEP_COUNT={step_count}")',
)

EXACT_ONCE_MARKERS = (
    'def sample_workflow_text() -> str:',
    'def run_self_test() -> int:',
    'print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")',
    'print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")',
)

ORDERED_MARKERS = (
    (
        'CLI_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract checker"',
        'CLI_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract packet"',
    ),
    (
        'ALIGN_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-stage alignment checker"',
        'ALIGN_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment packet"',
    ),
    (
        'ALIGN_SELFTEST_SELF_TEST_STEP = (',
        'ALIGN_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment selftest packet"',
    ),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper workflow selftest checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            "lane05 split-helper workflow selftest checker expected exactly "
            f"{expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(
            f"lane05 split-helper workflow selftest checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise ValueError(
            "lane05 split-helper workflow selftest checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow_checker(root: Path) -> int:
    checker_text = read_text(root / WORKFLOW_CHECKER_PATH)

    for marker in WORKFLOW_MARKERS:
        require_marker(checker_text, marker, "workflow checker marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(checker_text, marker, 1, "workflow checker marker")
    for earlier, later in ORDERED_MARKERS:
        require_order(checker_text, earlier, later, "checker constant order")

    require_marker(
        checker_text,
        'assert check_workflow(good_workflow) == len(ORDERED_STEPS) - 1',
        "self-test baseline assertion",
    )
    require_marker(
        checker_text,
        'assert expected in str(exc), str(exc)',
        "self-test failure assertion",
    )
    require_marker(
        checker_text,
        'assert ALIGN_SELF_TEST_STEP in str(exc), str(exc)',
        "duplicate-step failure assertion",
    )
    require_marker(
        checker_text,
        'assert "lane05 step order" in str(exc), str(exc)',
        "reordered-step failure assertion",
    )
    require_marker(
        checker_text,
        'print(f"LANE05_SPLIT_HELPER_WORKFLOW_STEP_COUNT={step_count}")',
        "main pass output",
    )
    return len(WORKFLOW_MARKERS) + 5


def write_sample_root(root: Path) -> None:
    checker = root / WORKFLOW_CHECKER_PATH
    checker.parent.mkdir(parents=True, exist_ok=True)
    checker.write_text(
        "\n".join(
            (
                "from pathlib import Path",
                "",
                'CLI_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract checker"',
                'CLI_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract packet"',
                'ALIGN_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-stage alignment checker"',
                'ALIGN_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment packet"',
                'ALIGN_SELFTEST_SELF_TEST_STEP = (',
                '    "- name: Self-test current Lane 05 split-stage alignment selftest checker"',
                ")",
                'ALIGN_SELFTEST_CHECK_STEP = "- name: Check current Lane 05 split-stage alignment selftest packet"',
                "",
                "def sample_workflow_text() -> str:",
                '    return "ok"',
                "",
                "def run_self_test() -> int:",
                "    case_count = 6",
                '    assert check_workflow(good_workflow) == len(ORDERED_STEPS) - 1',
                '    assert expected in str(exc), str(exc)',
                '    assert ALIGN_SELF_TEST_STEP in str(exc), str(exc)',
                '    assert "lane05 step order" in str(exc), str(exc)',
                "    duplicate_step = good_workflow.replace(",
                "    reordered_steps = good_workflow.replace(",
                '    print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")',
                '    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")',
                "",
                'print("LANE05_SPLIT_HELPER_WORKFLOW=pass")',
                'print(f"LANE05_SPLIT_HELPER_WORKFLOW_STEP_COUNT={step_count}")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_workflow_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_workflow_checker(root) == len(WORKFLOW_MARKERS) + 5
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(
            prefix="lane05_split_helper_workflow_selftest_fail_"
        ) as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_workflow_checker(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / WORKFLOW_CHECKER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing workflow checker marker",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_CHECKER_PATH).write_text(
            (root / WORKFLOW_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_CHECKER_PATH).write_text(
            (root / WORKFLOW_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'CLI_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract checker"\n'
                'CLI_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract packet"\n',
                'CLI_CHECK_STEP = "- name: Check current Lane 05 split helper cli-contract packet"\n'
                'CLI_SELF_TEST_STEP = "- name: Self-test current Lane 05 split helper cli-contract checker"\n',
                1,
            ),
            encoding="utf-8",
        ),
        "checker constant order",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_CHECKER_PATH).write_text(
            (root / WORKFLOW_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'assert expected in str(exc), str(exc)\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "self-test failure assertion",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_CHECKER_PATH).write_text(
            (root / WORKFLOW_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print(f"LANE05_SPLIT_HELPER_WORKFLOW_STEP_COUNT={step_count}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "LANE05_SPLIT_HELPER_WORKFLOW_STEP_COUNT",
    )

    print("LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Lane 05 split-helper workflow checker keeps its own "
            "self-test surface explicit."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a compact sample root that should satisfy this checker and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    try:
        root = args.root.resolve()
        marker_count = check_workflow_checker(root)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST=fail")
        print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELFTEST_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLI_CONTRACT_CHECKER_PATH = Path("scripts/zigux/check-lane05-split-helper-cli-contract.py")

CLI_CONTRACT_MARKERS = (
    'SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")',
    "HELPER_MARKERS = (",
    "EXACT_ONCE_MARKERS = (",
    "ORDERED_MARKERS = (",
    "def check_helper(root: Path) -> int:",
    "def write_sample_root(root: Path) -> None:",
    "def run_self_test() -> int:",
    'lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\\n", encoding="utf-8")',
    '"missing helper marker",',
    '"exactly 1 occurrences",',
    '"cli/status order",',
    '"--parts-dir and --destination are required for reconstruct mode",',
    '"choose either split mode",',
    '"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION",',
    'print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")',
    'print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")',
    'print("LANE05_SPLIT_HELPER_CLI_CONTRACT=pass")',
    'print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_MARKER_COUNT={marker_count}")',
)

EXACT_ONCE_MARKERS = (
    'def run_self_test() -> int:',
    'def write_sample_root(root: Path) -> None:',
    'print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")',
    'print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")',
)

ORDERED_MARKERS = (
    ('"missing helper marker",', '"exactly 1 occurrences",'),
    ('"exactly 1 occurrences",', '"cli/status order",'),
    ('"cli/status order",', '"--parts-dir and --destination are required for reconstruct mode",'),
    ('"--parts-dir and --destination are required for reconstruct mode",', '"choose either split mode",'),
    ('"choose either split mode",', '"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION",'),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper cli-contract selftest checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            "lane05 split-helper cli-contract selftest checker expected exactly "
            f"{expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(
            f"lane05 split-helper cli-contract selftest checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise ValueError(
            "lane05 split-helper cli-contract selftest checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_cli_contract_checker(root: Path) -> int:
    checker_text = read_text(root / CLI_CONTRACT_CHECKER_PATH)

    for marker in CLI_CONTRACT_MARKERS:
        require_marker(checker_text, marker, "cli-contract checker marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(checker_text, marker, 1, "cli-contract checker marker")
    for earlier, later in ORDERED_MARKERS:
        require_order(checker_text, earlier, later, "self-test failure order")

    require_marker(
        checker_text,
        "assert check_helper(root) == len(HELPER_MARKERS)",
        "self-test baseline assertion",
    )
    require_marker(
        checker_text,
        'print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_ROOT={root}")',
        "main pass output",
    )
    return len(CLI_CONTRACT_MARKERS) + 2


def write_sample_root(root: Path) -> None:
    checker = root / CLI_CONTRACT_CHECKER_PATH
    checker.parent.mkdir(parents=True, exist_ok=True)
    checker.write_text(
        "\n".join(
            (
                "from pathlib import Path",
                "",
                'SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")',
                "HELPER_MARKERS = (",
                ")",
                "EXACT_ONCE_MARKERS = (",
                ")",
                "ORDERED_MARKERS = (",
                ")",
                "",
                "def check_helper(root: Path) -> int:",
                "    return 0",
                "",
                "def write_sample_root(root: Path) -> None:",
                "    pass",
                "",
                "def run_self_test() -> int:",
                "    case_count = 7",
                "    assert check_helper(root) == len(HELPER_MARKERS)",
                '    lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\\n", encoding="utf-8")',
                '    "missing helper marker",',
                '    "exactly 1 occurrences",',
                '    "cli/status order",',
                '    "--parts-dir and --destination are required for reconstruct mode",',
                '    "choose either split mode",',
                '    "RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION",',
                '    print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")',
                '    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")',
                "",
                'print("LANE05_SPLIT_HELPER_CLI_CONTRACT=pass")',
                'print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_MARKER_COUNT={marker_count}")',
                'print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_ROOT={root}")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_cli_contract_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_cli_contract_checker(root) == len(CLI_CONTRACT_MARKERS) + 2
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(
            prefix="lane05_split_helper_cli_contract_selftest_fail_"
        ) as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_cli_contract_checker(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / CLI_CONTRACT_CHECKER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing cli-contract checker marker",
    )
    expect_failure(
        lambda root: (root / CLI_CONTRACT_CHECKER_PATH).write_text(
            (root / CLI_CONTRACT_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass",
    )
    expect_failure(
        lambda root: (root / CLI_CONTRACT_CHECKER_PATH).write_text(
            (root / CLI_CONTRACT_CHECKER_PATH).read_text(encoding="utf-8").replace(
                '"cli/status order",\n    "--parts-dir and --destination are required for reconstruct mode",\n',
                '"--parts-dir and --destination are required for reconstruct mode",\n    "cli/status order",\n',
                1,
            ),
            encoding="utf-8",
        ),
        "self-test failure order",
    )
    expect_failure(
        lambda root: (root / CLI_CONTRACT_CHECKER_PATH).write_text(
            (root / CLI_CONTRACT_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")',
                'print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")\n'
                '    print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / CLI_CONTRACT_CHECKER_PATH).write_text(
            (root / CLI_CONTRACT_CHECKER_PATH).read_text(encoding="utf-8").replace(
                "    assert check_helper(root) == len(HELPER_MARKERS)\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "self-test baseline assertion",
    )
    expect_failure(
        lambda root: (root / CLI_CONTRACT_CHECKER_PATH).write_text(
            (root / CLI_CONTRACT_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_ROOT={root}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "main pass output",
    )

    print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Lane 05 split-helper cli-contract checker keeps its own "
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
        marker_count = check_cli_contract_checker(root)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST=fail")
        print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST=pass")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELFTEST_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

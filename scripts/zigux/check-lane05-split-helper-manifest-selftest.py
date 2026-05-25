#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST_CHECKER_PATH = Path("scripts/zigux/check-lane05-split-helper-manifest-packet.py")

MANIFEST_CHECKER_MARKERS = (
    'SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")',
    'TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")',
    "MANIFEST_MARKERS = (",
    "HELPER_MARKERS = (",
    "ORDERED_MARKERS = (",
    "def check_helper(root: Path) -> int:",
    "def write_sample_root(root: Path) -> None:",
    "def run_self_test() -> int:",
    'assert check_helper(root) == len(HELPER_MARKERS) + len(MANIFEST_MARKERS)',
    'lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\\n", encoding="utf-8")',
    '"missing helper marker",',
    '"manifest key order",',
    '"archive target scope",',
    '"self-test output order",',
    'print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")',
    'print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST_CASE_COUNT={case_count}")',
    'print("LANE05_SPLIT_HELPER_MANIFEST_PACKET=pass")',
    'print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_MARKER_COUNT={marker_count}")',
)

EXACT_ONCE_MARKERS = (
    'print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")',
    'print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST_CASE_COUNT={case_count}")',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper manifest selftest checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            "lane05 split-helper manifest selftest checker expected exactly "
            f"{expected} occurrences of {label} `{marker}`, found {actual}"
        )


def check_manifest_checker(root: Path) -> int:
    checker_text = read_text(root / MANIFEST_CHECKER_PATH)

    for marker in MANIFEST_CHECKER_MARKERS:
        require_marker(checker_text, marker, "manifest checker marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(checker_text, marker, 1, "manifest checker marker")
    return len(MANIFEST_CHECKER_MARKERS)


def write_sample_root(root: Path) -> None:
    checker = root / MANIFEST_CHECKER_PATH
    checker.parent.mkdir(parents=True, exist_ok=True)
    checker.write_text(
        "\n".join(
            (
                "from pathlib import Path",
                "",
                'SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")',
                'TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")',
                "MANIFEST_MARKERS = (",
                ")",
                "HELPER_MARKERS = (",
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
                "    case_count = 5",
                '    assert check_helper(root) == len(HELPER_MARKERS) + len(MANIFEST_MARKERS)',
                '    lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\\n", encoding="utf-8")',
                '    "missing helper marker",',
                '    "manifest key order",',
                '    "archive target scope",',
                '    "self-test output order",',
                '    print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")',
                '    print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST_CASE_COUNT={case_count}")',
                "",
                'print("LANE05_SPLIT_HELPER_MANIFEST_PACKET=pass")',
                'print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_MARKER_COUNT={marker_count}")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_manifest_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_manifest_checker(root) == len(MANIFEST_CHECKER_MARKERS)
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(
            prefix="lane05_split_helper_manifest_selftest_fail_"
        ) as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_manifest_checker(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / MANIFEST_CHECKER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing manifest checker marker",
    )
    expect_failure(
        lambda root: (root / MANIFEST_CHECKER_PATH).write_text(
            (root / MANIFEST_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass",
    )
    expect_failure(
        lambda root: (root / MANIFEST_CHECKER_PATH).write_text(
            (root / MANIFEST_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")',
                'print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")\n'
                '    print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / MANIFEST_CHECKER_PATH).write_text(
            (root / MANIFEST_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'assert check_helper(root) == len(HELPER_MARKERS) + len(MANIFEST_MARKERS)\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "assert check_helper(root) == len(HELPER_MARKERS) + len(MANIFEST_MARKERS)",
    )
    expect_failure(
        lambda root: (root / MANIFEST_CHECKER_PATH).write_text(
            (root / MANIFEST_CHECKER_PATH).read_text(encoding="utf-8").replace(
                'print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_MARKER_COUNT={marker_count}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_MARKER_COUNT={marker_count}")',
    )

    print("LANE05_SPLIT_HELPER_MANIFEST_SELFTEST_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_SELFTEST_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Lane 05 split-helper manifest packet checker keeps its own "
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
        marker_count = check_manifest_checker(root)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_MANIFEST_SELFTEST=fail")
        print(f"LANE05_SPLIT_HELPER_MANIFEST_SELFTEST_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_MANIFEST_SELFTEST_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_MANIFEST_SELFTEST=pass")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_SELFTEST_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_SELFTEST_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

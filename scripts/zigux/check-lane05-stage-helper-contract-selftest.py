#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TARGET = Path("scripts/zigux/check-lane05-stage-helper-contract.py")

REQUIRED_MARKERS = (
    'STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")',
    'README_PATH = Path("third_party/README.md")',
    'with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_") as tmp_dir:',
    'assert check_stage_helper(root, contract) == 19',
    'assert check_readme(root, contract) == 7',
    'expect_failure(',
    '"missing stage helper marker"',
    '"missing README marker"',
    '"expected exactly one archive target"',
    '"output order"',
    'print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")',
    'print(f"LANE05_STAGE_HELPER_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")',
)

EXACT_ONCE_MARKERS = (
    'print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")',
    'print(f"LANE05_STAGE_HELPER_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")',
    'with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_") as tmp_dir:',
)

ORDERED_MARKERS = (
    ('"missing stage helper marker"', '"missing README marker"'),
    ('"missing README marker"', '"expected exactly one archive target"'),
    ('"expected exactly one archive target"', '"output order"'),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str) -> None:
    if marker not in text:
        raise ValueError(f"missing checker self-test marker: {marker}")


def require_exact_count(text: str, marker: str, expected: int) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"expected exactly {expected} occurrences of `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"missing ordered markers `{earlier}` or `{later}`")
    if earlier_index >= later_index:
        raise ValueError(f"expected `{earlier}` before `{later}`")


def check_text(text: str) -> int:
    for marker in REQUIRED_MARKERS:
        require_marker(text, marker)
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(text, marker, 1)
    for earlier, later in ORDERED_MARKERS:
        require_order(text, earlier, later)
    return len(REQUIRED_MARKERS)


def sample_text() -> str:
    return "\n".join(
        (
            "from pathlib import Path",
            "import tempfile",
            "",
            'STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")',
            'README_PATH = Path("third_party/README.md")',
            "",
            "def run_self_test() -> int:",
            '    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_") as tmp_dir:',
            "        root = Path(tmp_dir)",
            "        contract = {}",
            "        assert check_stage_helper(root, contract) == 19",
            "        assert check_readme(root, contract) == 7",
            "",
            "    expect_failure(",
            '        lambda root: None,',
            '        "missing stage helper marker",',
            "    )",
            "    expect_failure(",
            '        lambda root: None,',
            '        "missing README marker",',
            "    )",
            "    expect_failure(",
            '        lambda root: None,',
            '        "expected exactly one archive target",',
            "    )",
            "    expect_failure(",
            '        lambda root: None,',
            '        "output order",',
            "    )",
            '    print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")',
            '    print(f"LANE05_STAGE_HELPER_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")',
        )
    ) + "\n"


def write_sample_root(root: Path) -> None:
    path = root / TARGET
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sample_text(), encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_text(read_text(root / TARGET)) == len(REQUIRED_MARKERS)
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_selftest_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            target_path = root / TARGET
            mutator(target_path)
            try:
                check_text(read_text(target_path))
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda path: path.write_text("missing\n", encoding="utf-8"),
        "missing checker self-test marker",
    )
    expect_failure(
        lambda path: path.write_text(
            read_text(path).replace(
                'print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")',
    )
    expect_failure(
        lambda path: path.write_text(
            read_text(path).replace(
                '"missing README marker"',
                '"different marker"',
                1,
            ),
            encoding="utf-8",
        ),
        '"missing README marker"',
    )
    expect_failure(
        lambda path: path.write_text(
            read_text(path).replace(
                'print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")',
                'print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")\n'
                '    print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")',
                1,
            ),
            encoding="utf-8",
        ),
        "expected exactly 1 occurrences",
    )
    expect_failure(
        lambda path: path.write_text(
            read_text(path).replace(
                '"missing README marker",\n'
                '    )\n'
                '    expect_failure(\n'
                '        lambda root: None,\n'
                '        "expected exactly one archive target",',
                '"expected exactly one archive target",\n'
                '    )\n'
                '    expect_failure(\n'
                '        lambda root: None,\n'
                '        "missing README marker",',
                1,
            ),
            encoding="utf-8",
        ),
        "expected `\"missing README marker\"` before `\"expected exactly one archive target\"`",
    )

    print("LANE05_STAGE_HELPER_CONTRACT_SELFTEST_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SELFTEST_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 stage-helper contract checker keeps its self-test packet explicit."
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
        marker_count = check_text(read_text(root / TARGET))
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_CONTRACT_SELFTEST=fail")
        print(f"LANE05_STAGE_HELPER_CONTRACT_SELFTEST_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_CONTRACT_SELFTEST_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_CONTRACT_SELFTEST=pass")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SELFTEST_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SELFTEST_TARGET={TARGET}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SELFTEST_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

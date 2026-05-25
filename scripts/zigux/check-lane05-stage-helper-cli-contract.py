#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")

SOURCE_ARG = 'parser.add_argument("--source", type=Path, help="Path to the candidate Zig archive payload.")'
PARTS_DIR_ARG = '        "--parts-dir",'
PARTS_DIR_FLAG = '"--parts-dir"'
CHECK_ONLY_ARG = '        "--check-only",'
SELF_TEST_ARG = 'parser.add_argument("--self-test", action="store_true", help="Run built-in coverage.")'
ONE_OF_GUARD = 'if (args.source is None) == (args.parts_dir is None):'
ONE_OF_NOTE = "exactly one of --source or --parts_dir is required unless --self-test is used"
SOURCE_RESOLVE = "source = args.source.resolve() if args.source is not None else None"
PARTS_DIR_RESOLVE = "parts_dir = args.parts_dir.resolve() if args.parts_dir is not None else None"
CHECK_ONLY_PASSTHROUGH = "check_only=args.check_only,"
PASS_INPUT_MODE = 'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")'
FAIL_SOURCE = 'print(f"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}")'
FAIL_PARTS_DIR = 'print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")'
SELF_TEST_SOURCE_ASSERT = 'assert input_mode == "source"'
SELF_TEST_PARTS_ASSERT = 'assert input_mode == "parts_dir"'
SELF_TEST_PASS = 'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass'


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 stage-helper cli contract missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            "lane05 stage-helper cli contract expected exactly "
            f"{expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage-helper cli contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            "lane05 stage-helper cli contract expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_helper(root: Path) -> int:
    helper_text = read_text(root / STAGE_HELPER_PATH)

    for marker, label in (
        (SOURCE_ARG, "source argument"),
        (PARTS_DIR_ARG, "parts-dir argument block"),
        (PARTS_DIR_FLAG, "parts-dir argument flag"),
        (CHECK_ONLY_ARG, "check-only argument"),
        (SELF_TEST_ARG, "self-test argument"),
        (ONE_OF_GUARD, "one-of guard"),
        (ONE_OF_NOTE, "one-of guard note"),
        (SOURCE_RESOLVE, "source resolve"),
        (PARTS_DIR_RESOLVE, "parts-dir resolve"),
        (CHECK_ONLY_PASSTHROUGH, "check-only passthrough"),
        (PASS_INPUT_MODE, "input-mode pass output"),
        (FAIL_SOURCE, "source status output"),
        (FAIL_PARTS_DIR, "parts-dir status output"),
        (SELF_TEST_SOURCE_ASSERT, "source self-test assertion"),
        (SELF_TEST_PARTS_ASSERT, "parts-dir self-test assertion"),
        (SELF_TEST_PASS, "self-test pass marker"),
    ):
        require_marker(helper_text, marker, label)

    require_exact_count(helper_text, SOURCE_ARG, 1, "source argument")
    require_exact_count(helper_text, PARTS_DIR_FLAG, 1, "parts-dir flag")
    require_exact_count(helper_text, CHECK_ONLY_PASSTHROUGH, 1, "check-only passthrough")
    require_exact_count(helper_text, PASS_INPUT_MODE, 1, "input-mode pass output")
    require_exact_count(helper_text, SELF_TEST_SOURCE_ASSERT, 1, "source self-test assertion")
    require_exact_count(helper_text, SELF_TEST_PARTS_ASSERT, 1, "parts-dir self-test assertion")

    require_order(helper_text, SOURCE_ARG, PARTS_DIR_ARG, "parser argument order")
    require_order(helper_text, PARTS_DIR_ARG, CHECK_ONLY_ARG, "parser argument order")
    require_order(helper_text, CHECK_ONLY_ARG, SELF_TEST_ARG, "parser argument order")
    require_order(helper_text, ONE_OF_GUARD, SOURCE_RESOLVE, "resolve order")
    require_order(helper_text, SOURCE_RESOLVE, PARTS_DIR_RESOLVE, "resolve order")
    require_order(helper_text, PARTS_DIR_RESOLVE, CHECK_ONLY_PASSTHROUGH, "stage_archive call order")
    require_order(helper_text, FAIL_SOURCE, FAIL_PARTS_DIR, "failure output order")
    require_order(helper_text, FAIL_PARTS_DIR, PASS_INPUT_MODE, "status output order")
    require_order(helper_text, SELF_TEST_SOURCE_ASSERT, SELF_TEST_PARTS_ASSERT, "self-test mode order")
    return 16


def write_fixture(root: Path) -> None:
    helper_path = root / STAGE_HELPER_PATH
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    helper_path.write_text(
        "\n".join(
            (
                "import argparse",
                "from pathlib import Path",
                "",
                "def stage_archive(root, source, *, parts_dir, check_only):",
                '    return {}, "checked", "deadbeef", root / "third_party/archive.tar.xz", "source"',
                "",
                "def run_self_test():",
                '    assert input_mode == "source"',
                '    assert input_mode == "parts_dir"',
                '    print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                "",
                "def main() -> int:",
                "    parser = argparse.ArgumentParser()",
                SOURCE_ARG,
                '    parser.add_argument(',
                '        "--parts-dir",',
                "        type=Path,",
                '        help="Directory containing manifest.json plus part-XXX.b64 shard files.",',
                "    )",
                '    parser.add_argument(',
                '        "--check-only",',
                '        action="store_true",',
                '        help="Validate the candidate archive without copying it into third_party.",',
                "    )",
                '    parser.add_argument("--self-test", action="store_true", help="Run built-in coverage.")',
                "    args = parser.parse_args()",
                ONE_OF_GUARD,
                f'        raise SystemExit("{ONE_OF_NOTE}")',
                SOURCE_RESOLVE,
                PARTS_DIR_RESOLVE,
                "    metadata, status, actual_sha, destination, input_mode = stage_archive(",
                "        root,",
                "        source,",
                "        parts_dir=parts_dir,",
                f"        {CHECK_ONLY_PASSTHROUGH}",
                "    )",
                "    if source is not None:",
                f"        {FAIL_SOURCE}",
                "    if parts_dir is not None:",
                f"        {FAIL_PARTS_DIR}",
                f"    {PASS_INPUT_MODE}",
                "    return 0",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_cli_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        assert check_helper(root) == 16
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_cli_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root / STAGE_HELPER_PATH)
            try:
                check_helper(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda path: path.write_text(path.read_text(encoding="utf-8").replace(SOURCE_ARG + "\n", "", 1), encoding="utf-8"),
        "source argument",
    )
    expect_failure(
        lambda path: path.write_text(path.read_text(encoding="utf-8").replace(PARTS_DIR_FLAG, '"--parts-dir-disabled"', 1), encoding="utf-8"),
        "parts-dir argument",
    )
    expect_failure(
        lambda path: path.write_text(path.read_text(encoding="utf-8").replace(ONE_OF_GUARD + "\n", "", 1), encoding="utf-8"),
        "one-of guard",
    )
    expect_failure(
        lambda path: path.write_text(path.read_text(encoding="utf-8").replace(CHECK_ONLY_PASSTHROUGH + "\n", "", 1), encoding="utf-8"),
        "check-only passthrough",
    )
    expect_failure(
        lambda path: path.write_text(path.read_text(encoding="utf-8").replace(PASS_INPUT_MODE + "\n", "", 1), encoding="utf-8"),
        "input-mode pass output",
    )
    expect_failure(
        lambda path: path.write_text(path.read_text(encoding="utf-8").replace(SELF_TEST_PARTS_ASSERT + "\n", "", 1), encoding="utf-8"),
        "parts-dir self-test assertion",
    )
    expect_failure(
        lambda path: path.write_text(
            path.read_text(encoding="utf-8").replace(
                SOURCE_RESOLVE + "\n" + PARTS_DIR_RESOLVE,
                PARTS_DIR_RESOLVE + "\n" + SOURCE_RESOLVE,
                1,
            ),
            encoding="utf-8",
        ),
        "resolve order",
    )

    print("LANE05_STAGE_HELPER_CLI_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_CLI_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    write_fixture(root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 staged-archive helper keeps its CLI contract explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample repo root that should pass this checker.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    root = args.root.resolve()
    try:
        marker_count = check_helper(root)
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_CLI_CONTRACT=fail")
        print(f"LANE05_STAGE_HELPER_CLI_CONTRACT_ROOT={root}")
        print(f"LANE05_STAGE_HELPER_CLI_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_CLI_CONTRACT=pass")
    print(f"LANE05_STAGE_HELPER_CLI_CONTRACT_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_CLI_CONTRACT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

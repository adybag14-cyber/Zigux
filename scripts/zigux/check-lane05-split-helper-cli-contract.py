#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")

HELPER_MARKERS = (
    'parser.add_argument("--source", type=Path, help="Path to the validated pinned Zig archive payload.")',
    'parser.add_argument(',
    '"--output-dir"',
    '"--chunk-bytes"',
    '"--parts-dir"',
    '"--destination"',
    'parser.add_argument("--self-test", action="store_true", help="Run built-in shard helper coverage.")',
    'split_mode = args.source is not None or args.output_dir is not None',
    'reconstruct_mode = args.parts_dir is not None or args.destination is not None',
    '"choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)"',
    '"--source and --output-dir are required for split mode"',
    '"--parts-dir and --destination are required for reconstruct mode"',
    '"use either split mode (--source/--output-dir), reconstruct mode (--parts-dir/--destination), or --self-test"',
    'print("SPLIT_PINNED_ZIG_ARCHIVE=fail")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_ROOT={root}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={source}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_NOTE={exc}")',
    'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={output_dir}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_CHUNK_BYTES={args.chunk_bytes}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_NOTE={exc}")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
)

EXACT_ONCE_MARKERS = (
    'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
    'print("SPLIT_PINNED_ZIG_ARCHIVE=fail")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")',
    'split_mode = args.source is not None or args.output_dir is not None',
    'reconstruct_mode = args.parts_dir is not None or args.destination is not None',
)

ORDERED_MARKERS = (
    (
        'split_mode = args.source is not None or args.output_dir is not None',
        'reconstruct_mode = args.parts_dir is not None or args.destination is not None',
    ),
    (
        '"choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)"',
        '"--source and --output-dir are required for split mode"',
    ),
    (
        '"--source and --output-dir are required for split mode"',
        '"--parts-dir and --destination are required for reconstruct mode"',
    ),
    (
        'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={output_dir}")',
    ),
    (
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={output_dir}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
    ),
    (
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
    ),
    (
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
    ),
    (
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
    ),
    (
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_CHUNK_BYTES={args.chunk_bytes}")',
    ),
    (
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_CHUNK_BYTES={args.chunk_bytes}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
    ),
    (
        'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
    ),
    (
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
    ),
    (
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
    ),
    (
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
    ),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper cli contract missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            "lane05 split-helper cli contract expected exactly "
            f"{expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-helper cli contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            "lane05 split-helper cli contract expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_helper(root: Path) -> int:
    helper_text = read_text(root / SPLIT_HELPER_PATH)

    for marker in HELPER_MARKERS:
        require_marker(helper_text, marker, "helper marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(helper_text, marker, 1, "helper marker")
    for earlier, later in ORDERED_MARKERS:
        require_order(helper_text, earlier, later, "cli/status order")
    return len(HELPER_MARKERS)


def write_sample_root(root: Path) -> None:
    helper = root / SPLIT_HELPER_PATH
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text(
        "\n".join(
            (
                "from pathlib import Path",
                "import argparse",
                "",
                "def main() -> int:",
                "    parser = argparse.ArgumentParser()",
                '    parser.add_argument("--source", type=Path, help="Path to the validated pinned Zig archive payload.")',
                "    parser.add_argument(",
                '        "--output-dir",',
                '        type=Path,',
                '    )',
                "    parser.add_argument(",
                '        "--chunk-bytes",',
                '        type=int,',
                '    )',
                "    parser.add_argument(",
                '        "--parts-dir",',
                '        type=Path,',
                '    )',
                "    parser.add_argument(",
                '        "--destination",',
                '        type=Path,',
                '    )',
                '    parser.add_argument("--self-test", action="store_true", help="Run built-in shard helper coverage.")',
                "    args = parser.parse_args()",
                "    split_mode = args.source is not None or args.output_dir is not None",
                "    reconstruct_mode = args.parts_dir is not None or args.destination is not None",
                '    raise SystemExit("choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)")',
                '    raise SystemExit("--source and --output-dir are required for split mode")',
                '    raise SystemExit("--parts-dir and --destination are required for reconstruct mode")',
                '    raise SystemExit("use either split mode (--source/--output-dir), reconstruct mode (--parts-dir/--destination), or --self-test")',
                '    print("SPLIT_PINNED_ZIG_ARCHIVE=fail")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_ROOT={root}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={source}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_NOTE={exc}")',
                '    print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={output_dir}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_CHUNK_BYTES={args.chunk_bytes}")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
                '    print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")',
                '    print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
                '    print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
                '    print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_NOTE={exc}")',
                '    print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
                '    print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
                '    print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
                '    print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
                '    print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_cli_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_helper(root) == len(HELPER_MARKERS)
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_helper_cli_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_helper(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing helper marker",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "SPLIT_PINNED_ZIG_ARCHIVE=pass",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")\n'
                '    print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")\n'
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")\n',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")\n'
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")\n',
                1,
            ),
            encoding="utf-8",
        ),
        "cli/status order",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                '--parts-dir and --destination are required for reconstruct mode',
                '--parts-dir is required for reconstruct mode',
                1,
            ),
            encoding="utf-8",
        ),
        "--parts-dir and --destination are required for reconstruct mode",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)',
                'choose split or reconstruct mode',
                1,
            ),
            encoding="utf-8",
        ),
        "choose either split mode",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION",
    )

    print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper keeps its split/reconstruct CLI contract explicit."
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
        marker_count = check_helper(root)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_CLI_CONTRACT=fail")
        print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_CLI_CONTRACT=pass")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

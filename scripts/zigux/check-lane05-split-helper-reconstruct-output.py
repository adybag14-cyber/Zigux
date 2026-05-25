#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")

REQUIRED_MARKERS = (
    "def load_manifest(parts_dir: Path) -> dict[str, object]:",
    "def reconstruct_archive(parts_dir: Path, destination: Path) -> dict[str, object]:",
    'raise ValueError(f"missing expected shard: {path.name}")',
    "base64.b64decode(encoded, validate=True)",
    'raise ValueError(f"expected reconstructed archive to be {expected_size} bytes, got {actual_size}")',
    'f"expected reconstructed archive to have sha256 {expected_sha}, got {actual_sha}"',
    'raise SystemExit("--parts-dir and --destination are required for reconstruct mode")',
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

EXACT_COUNT_MARKERS = (
    ('print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")', 1),
    ('print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")', 1),
    ('print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")', 2),
    ('print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")', 2),
    ('print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")', 1),
    ('print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")', 1),
    ('print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")', 1),
    ('print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")', 1),
)

SUCCESS_START_MARKER = 'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")'

ORDERED_MARKERS = (
    (
        SUCCESS_START_MARKER,
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
    ),
    (
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
    ),
    (
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
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
        raise ValueError(f"lane05 split-helper reconstruct-output missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    count = text.count(marker)
    if count != expected:
        raise ValueError(
            "lane05 split-helper reconstruct-output expected exactly "
            f"{expected} {label} `{marker}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(
            f"lane05 split-helper reconstruct-output missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise ValueError(
            "lane05 split-helper reconstruct-output expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_root(root: Path) -> tuple[int, int]:
    helper_text = read_text(root / SPLIT_HELPER_PATH)
    success_index = helper_text.find(SUCCESS_START_MARKER)

    for marker in REQUIRED_MARKERS:
        require_marker(helper_text, marker, "helper marker")
    for marker, expected in EXACT_COUNT_MARKERS:
        require_exact_count(helper_text, marker, expected, "helper marker")
    if success_index == -1:
        raise ValueError(
            f"lane05 split-helper reconstruct-output missing helper marker: {SUCCESS_START_MARKER}"
        )
    success_block = helper_text[success_index:]
    for earlier, later in ORDERED_MARKERS:
        require_order(success_block, earlier, later, "reconstruct output order")

    return len(REQUIRED_MARKERS), len(ORDERED_MARKERS)


def write_sample_root(root: Path) -> None:
    helper_path = root / SPLIT_HELPER_PATH
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    helper_path.write_text(
        "\n".join(
            (
                "from __future__ import annotations",
                "import argparse",
                "import base64",
                "from pathlib import Path",
                "",
                "def load_manifest(parts_dir: Path) -> dict[str, object]:",
                "    return {}",
                "",
                "def reconstruct_archive(parts_dir: Path, destination: Path) -> dict[str, object]:",
                '    raise ValueError(f"missing expected shard: {path.name}")',
                "    base64.b64decode(encoded, validate=True)",
                '    raise ValueError(f"expected reconstructed archive to be {expected_size} bytes, got {actual_size}")',
                '    raise ValueError(f"expected reconstructed archive to have sha256 {expected_sha}, got {actual_sha}")',
                "    return metadata",
                "",
                "def main() -> int:",
                "    parser = argparse.ArgumentParser()",
                "    parser.add_argument('--parts-dir', type=Path)",
                "    parser.add_argument('--destination', type=Path)",
                "    args = parser.parse_args()",
                "    reconstruct_mode = args.parts_dir is not None or args.destination is not None",
                "    if reconstruct_mode:",
                "        if args.parts_dir is None or args.destination is None:",
                '            raise SystemExit("--parts-dir and --destination are required for reconstruct mode")',
                "        parts_dir = args.parts_dir.resolve()",
                "        destination = args.destination.resolve()",
                "        try:",
                "            metadata = reconstruct_archive(parts_dir, destination)",
                "        except ValueError as exc:",
                '            print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")',
                '            print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
                '            print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
                '            print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_NOTE={exc}")',
                "            return 1",
                '        print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE={metadata[\'size\']}")',
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
                "        return 0",
                "    return 1",
                "",
                'if __name__ == "__main__":',
                "    raise SystemExit(main())",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_reconstruct_output_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_root(root) == (len(REQUIRED_MARKERS), len(ORDERED_MARKERS))
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_reconstruct_output_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            helper_path = root / SPLIT_HELPER_PATH
            mutator(helper_path)
            try:
                check_root(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda helper_path: helper_path.write_text("missing\n", encoding="utf-8"),
        "missing helper marker",
    )
    expect_failure(
        lambda helper_path: helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")',
    )
    expect_failure(
        lambda helper_path: helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")\n'
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")\n',
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")\n'
                '        print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")\n',
                1,
            ),
            encoding="utf-8",
        ),
        "reconstruct output order",
    )
    expect_failure(
        lambda helper_path: helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'raise SystemExit("--parts-dir and --destination are required for reconstruct mode")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "--parts-dir and --destination are required for reconstruct mode",
    )
    expect_failure(
        lambda helper_path: helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'raise ValueError(f"missing expected shard: {path.name}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "missing expected shard",
    )
    expect_failure(
        lambda helper_path: helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                "base64.b64decode(encoded, validate=True)\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "base64.b64decode(encoded, validate=True)",
    )
    expect_failure(
        lambda helper_path: helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'raise ValueError(f"expected reconstructed archive to have sha256 {expected_sha}, got {actual_sha}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "expected reconstructed archive to have sha256",
    )

    print("LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper keeps reconstruct-mode output explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for focused checker validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        root = args.root.resolve()
        marker_count, ordered_pair_count = check_root(root)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT=fail")
        print(f"LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT=pass")
    print(f"LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_MARKER_COUNT={marker_count}")
    print(f"LANE05_SPLIT_HELPER_RECONSTRUCT_OUTPUT_ORDERED_PAIR_COUNT={ordered_pair_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

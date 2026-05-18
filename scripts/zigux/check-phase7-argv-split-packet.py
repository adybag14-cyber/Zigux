#!/usr/bin/env python3
"""Validate the current Phase 7 argv_split helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/check-phase7-argv-split-packet.py",
    ".github/workflows/zigux-bootstrap.yml",
    "tools/lib/argv_split.zig",
]

REQUIRED_MARKERS = {
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "'scripts/zigux/**'",
        "find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort",
        'python3 -m py_compile "${scripts[@]}"',
    ],
    "tools/lib/argv_split.zig": [
        "pub fn argvSplit(allocator: std.mem.Allocator, text: []const u8) !ArgvSplitResult {",
        "allocator.dupe(u8, text[idx..end]);",
        "pub fn argvFree(result: *ArgvSplitResult) void {",
        "pub const argv_split = argvSplit;",
        "pub const argv_free = argvFree;",
        'test "argvSplit matches the phase 1 committed fixture shape" {',
        'test "argvSplit collapses repeated whitespace and blank inputs to zero arguments" {',
    ],
}

SELF_TEST_CASE_COUNT = 7


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {
        "scripts/zigux/check-phase7-argv-split-packet.py": "\n".join(REQUIRED_MARKERS["scripts/zigux/check-phase7-argv-split-packet.py"]) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(REQUIRED_MARKERS[".github/workflows/zigux-bootstrap.yml"]) + "\n",
        "tools/lib/argv_split.zig": "\n".join(REQUIRED_MARKERS["tools/lib/argv_split.zig"]) + "\n",
    }

    for rel in REQUIRED_FILES:
        write(tmp_root / rel, fixture_text[rel])


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
        checker_path.unlink()
        expect_missing_file(
            "missing_argv_split_checker",
            tmp_root,
            "scripts/zigux/check-phase7-argv-split-packet.py",
        )
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_path.unlink()
        expect_missing_file(
            "missing_bootstrap_workflow",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml",
        )
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "tools" / "lib" / "argv_split.zig"
        helper_path.unlink()
        expect_missing_file(
            "missing_argv_split_helper",
            tmp_root,
            "tools/lib/argv_split.zig",
        )
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_path.write_text(helper_text.replace("pub const argv_free = argvFree;\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_argv_free_alias",
            tmp_root,
            "tools/lib/argv_split.zig: pub const argv_free = argvFree;",
        )
        helper_path.write_text(helper_text, encoding="utf-8")

        helper_path.write_text(helper_text.replace("allocator.dupe(u8, text[idx..end]);\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_token_copy_marker",
            tmp_root,
            "tools/lib/argv_split.zig: allocator.dupe(u8, text[idx..end]);",
        )
        helper_path.write_text(helper_text, encoding="utf-8")

        workflow_text = read_text(workflow_path)
        workflow_path.write_text(
            workflow_text.replace("find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort\n", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "missing_workflow_script_compile_scan",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort",
        )
        workflow_path.write_text(workflow_text, encoding="utf-8")

        workflow_path.write_text(
            workflow_text.replace('python3 -m py_compile "${scripts[@]}"\n', "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "missing_workflow_py_compile",
            tmp_root,
            '.github/workflows/zigux-bootstrap.yml: python3 -m py_compile "${scripts[@]}"',
        )

    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to validate (default: current repository root)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-tests instead of validating the repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(args.repo_root)
    if missing_files:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_MARKERS_END")
        return 1

    print("PHASE7_ARGV_SPLIT_PACKET=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "lib/argv_split.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "null-terminated pointer-vector access through `cArgv()`",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    ],
    "zigux/Makefile": [
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-argv-split-tests",
        '"phase7_argv_split.zig"',
    ],
    "zigux/tests/phase7_argv_split.zig": [
        '@import("fixtures/phase7_argv_split_vectors.zig")',
        "split.cArgv()",
        "phase 7 argvSplit token buffer does not alias the source text",
    ],
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": [
        "repeated whitespace collapses into separators",
        "blank input stays empty",
        "first NUL stops counting and splitting",
        "quote characters stay inside returned tokens",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {
        "Documentation/zigux/phase7-argv-split-slice.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase7-argv-split-slice.md"]) + "\n",
        "scripts/zigux/check-phase7-argv-split-packet.py": "\n".join(REQUIRED_MARKERS["scripts/zigux/check-phase7-argv-split-packet.py"]) + "\n",
        "zigux/Makefile": "\n".join(REQUIRED_MARKERS["zigux/Makefile"]) + "\n",
        "zigux/tests/phase7_build.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_build.zig"]) + "\n",
        "zigux/tests/phase7_argv_split.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split.zig"]) + "\n",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/fixtures/phase7_argv_split_vectors.zig"]) + "\n",
        "lib/argv_split.zig": "// fixture\n",
    }

    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")


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
            "missing_argv_split_packet_checker",
            tmp_root,
            "scripts/zigux/check-phase7-argv-split-packet.py",
        )
        write_fixture_root(tmp_root)

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        fixture_path.unlink()
        expect_missing_file(
            "missing_argv_split_vectors_fixture",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        )
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("python3 scripts/zigux/check-phase7-argv-split-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_packet_checker_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        )
        slice_path.write_text(original_slice, encoding="utf-8")

        makefile_path = tmp_root / "zigux" / "Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase7-argv-split-packet.py --self-test", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_argv_split_packet_self_test_hook",
            tmp_root,
            "zigux/Makefile: scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        tests_path = tmp_root / "zigux" / "tests" / "phase7_argv_split.zig"
        original_tests = tests_path.read_text(encoding="utf-8")
        tests_path.write_text(original_tests.replace("split.cArgv()", "split.argv", 1), encoding="utf-8")
        expect_missing_marker(
            "argv_split_cargv_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: split.cArgv()",
        )
        tests_path.write_text(original_tests, encoding="utf-8")

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        original_fixture = fixture_path.read_text(encoding="utf-8")
        fixture_path.write_text(
            original_fixture.replace("quote characters stay inside returned tokens", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_quote_fixture_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: quote characters stay inside returned tokens",
        )

    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT=6")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the dedicated Phase 7 argv_split packet surface.")
    parser.add_argument("--self-test", action="store_true", help="Run packet checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
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

#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if SELF_PATH.parent.name == "zigux" and SELF_PATH.parent.parent.name == "scripts":
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent

TARGET = Path("tools/lib/find_bit.zig")

REQUIRED_FUNCTION_MARKERS = {
    "find_next_clump8": "pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "find_next_clump8_alias": "pub fn find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "find_next_clump8_underscore": "pub fn _find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "find_first_clump8": "pub fn findFirstClump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "find_first_clump8_alias": "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "find_first_clump8_underscore": "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
}

REQUIRED_TEST_MARKERS = {
    "byte_alignment": 'test "clump8 scans align to the containing byte and return its value" {',
    "tail_reachable": 'test "clump8 scans keep tail bytes reachable from partial final words" {',
    "tail_mask": 'test "clump8 scans mask tail bits beyond nbits" {',
    "no_match_preserves_byte": 'test "clump8 scans leave the caller byte untouched when no set bit remains" {',
}

REQUIRED_ALIAS_EXPECTATIONS = {
    "underscore_first": "try std.testing.expectEqual(@as(usize, 0), _find_first_clump8(&clump, &clump_map, 8));",
    "underscore_next": "try std.testing.expectEqual(@as(usize, 0), _find_next_clump8(&clump, &clump_map, 8, 0));",
    "linux_first": "try std.testing.expectEqual(@as(usize, 0), find_first_clump8(&clump, &[_]Word{@as(Word, 1)}, 8));",
    "linux_next": "try std.testing.expectEqual(@as(usize, 0), find_next_clump8(&clump, &[_]Word{@as(Word, 1)}, 8, 0));",
}


def validate_exact_lines(section: str, text: str, markers: dict[str, str]) -> list[str]:
    failures: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for label, marker in markers.items():
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            failures.append(f"{section}:{label}:expected=1:actual={count}")
    return failures


def validate(root: Path) -> list[str]:
    path = root / TARGET
    if not path.exists():
        return [f"missing_file:{TARGET.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    missing: list[str] = []
    missing.extend(validate_exact_lines("function", text, REQUIRED_FUNCTION_MARKERS))
    missing.extend(validate_exact_lines("test", text, REQUIRED_TEST_MARKERS))
    missing.extend(validate_exact_lines("alias", text, REQUIRED_ALIAS_EXPECTATIONS))
    return missing


def build_fixture(root: Path) -> None:
    (root / TARGET.parent).mkdir(parents=True, exist_ok=True)
    lines = [
        "pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
        "    _ = clump;",
        "    _ = addr;",
        "    _ = nbits;",
        "    _ = offset;",
        "    return 0;",
        "}",
        "",
        "pub fn find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
        "    return findNextClump8(clump, addr, nbits, offset);",
        "}",
        "",
        "pub fn _find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
        "    return findNextClump8(clump, addr, nbits, offset);",
        "}",
        "",
        "pub fn findFirstClump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
        "    return findNextClump8(clump, addr, nbits, 0);",
        "}",
        "",
        "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
        "    return findFirstClump8(clump, addr, nbits);",
        "}",
        "",
        "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
        "    return findFirstClump8(clump, addr, nbits);",
        "}",
        "",
        'test "clump8 scans align to the containing byte and return its value" {',
        "}",
        "",
        'test "clump8 scans keep tail bytes reachable from partial final words" {',
        "}",
        "",
        'test "clump8 scans mask tail bits beyond nbits" {',
        "}",
        "",
        'test "clump8 scans leave the caller byte untouched when no set bit remains" {',
        "}",
        "",
        "try std.testing.expectEqual(@as(usize, 0), _find_first_clump8(&clump, &clump_map, 8));",
        "try std.testing.expectEqual(@as(usize, 0), _find_next_clump8(&clump, &clump_map, 8, 0));",
        "try std.testing.expectEqual(@as(usize, 0), find_first_clump8(&clump, &[_]Word{@as(Word, 1)}, 8));",
        "try std.testing.expectEqual(@as(usize, 0), find_next_clump8(&clump, &[_]Word{@as(Word, 1)}, 8, 0));",
    ]
    (root / TARGET).write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("missing_file", "missing_file:tools/lib/find_bit.zig"),
        ("missing_test", "test:tail_mask:expected=1:actual=0"),
        ("missing_alias_expectation", "alias:linux_next:expected=1:actual=0"),
        ("missing_function", "function:find_first_clump8_underscore:expected=1:actual=0"),
        ("duplicate_test", "test:tail_mask:expected=1:actual=2"),
        ("duplicate_alias_expectation", "alias:linux_next:expected=1:actual=2"),
        ("duplicate_function", "function:find_first_clump8_underscore:expected=1:actual=2"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_clump_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if validate(tmp_root) != [cases[0][1]]:
            raise SystemExit("phase1-find-bit-clump:self-test:missing_file")

        build_fixture(tmp_root)
        if validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:baseline")

        text = (tmp_root / TARGET).read_text(encoding="utf-8")

        (tmp_root / TARGET).write_text(
            text.replace(REQUIRED_TEST_MARKERS["tail_mask"] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[1][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_test")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(REQUIRED_ALIAS_EXPECTATIONS["linux_next"] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[2][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_alias")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(REQUIRED_FUNCTION_MARKERS["find_first_clump8_underscore"] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[3][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:missing_function")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(
                REQUIRED_TEST_MARKERS["tail_mask"],
                REQUIRED_TEST_MARKERS["tail_mask"] + "\n" + REQUIRED_TEST_MARKERS["tail_mask"],
                1,
            ),
            encoding="utf-8",
        )
        if cases[4][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:duplicate_test")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(
                REQUIRED_ALIAS_EXPECTATIONS["linux_next"],
                REQUIRED_ALIAS_EXPECTATIONS["linux_next"] + "\n" + REQUIRED_ALIAS_EXPECTATIONS["linux_next"],
                1,
            ),
            encoding="utf-8",
        )
        if cases[5][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:duplicate_alias")

        build_fixture(tmp_root)
        text = (tmp_root / TARGET).read_text(encoding="utf-8")
        (tmp_root / TARGET).write_text(
            text.replace(
                REQUIRED_FUNCTION_MARKERS["find_first_clump8_underscore"],
                REQUIRED_FUNCTION_MARKERS["find_first_clump8_underscore"] + "\n" + REQUIRED_FUNCTION_MARKERS["find_first_clump8_underscore"],
                1,
            ),
            encoding="utf-8",
        )
        if cases[6][1] not in validate(tmp_root):
            raise SystemExit("phase1-find-bit-clump:self-test:duplicate_function")

    print("PHASE1_FIND_BIT_CLUMP_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_CLUMP_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    missing = validate(ROOT)
    if missing:
        print("PHASE1_FIND_BIT_CLUMP_VALIDATION=fail")
        print("MISSING_PHASE1_FIND_BIT_CLUMP_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_PHASE1_FIND_BIT_CLUMP_MARKERS_END")
        return 1

    print("PHASE1_FIND_BIT_CLUMP_VALIDATION=pass")
    print(f"PHASE1_FIND_BIT_CLUMP_FUNCTION_MARKER_COUNT={len(REQUIRED_FUNCTION_MARKERS)}")
    print(f"PHASE1_FIND_BIT_CLUMP_TEST_MARKER_COUNT={len(REQUIRED_TEST_MARKERS)}")
    print(f"PHASE1_FIND_BIT_CLUMP_ALIAS_MARKER_COUNT={len(REQUIRED_ALIAS_EXPECTATIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

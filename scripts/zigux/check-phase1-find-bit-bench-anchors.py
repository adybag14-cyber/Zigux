#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
FIND_BIT = ROOT / "tools" / "lib" / "find_bit.zig"

REQUIRED_TEST_MARKERS = {
    "boundary_head_test": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
    "boundary_tail_test": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
    "single_word_tail_test": 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start" {',
    "past_end_no_read_test": 'test "next scans past nbits return without reading bitmap words" {',
    "clump8_no_read_test": 'test "clump8 past-end scans return without reading bitmap words" {',
    "last_bit_tail_test": 'test "find last bit clamps tail words to nbits" {',
}

REQUIRED_SOURCE_MARKERS = {
    "find_next_boundary": "findNextBit(&set_map, nbits, boundary)",
    "find_next_and_boundary": "findNextAndBit(&and_lhs, &and_rhs, nbits, boundary)",
    "find_next_andnot_boundary": "findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)",
    "find_next_zero_boundary": "findNextZeroBit(&zero_map, nbits, boundary)",
    "find_last_tail_single_word": "findLastBit(&single_word, single_word_nbits)",
    "find_next_past_end": "findNextBit(&empty, 7, 11)",
    "find_next_zero_past_end": "findNextZeroBit(&empty, 7, 11)",
    "find_next_and_past_end": "findNextAndBit(&empty, &empty, 7, 11)",
    "find_next_andnot_past_end": "findNextAndNotBit(&empty, &empty, 7, 11)",
    "find_clump8_past_end": "findNextClump8(&clump, &empty, 8, 8)",
    "find_clump8_linux_alias_past_end": "find_next_clump8(&clump, &empty, 8, 12)",
    "find_clump8_low_level_alias_past_end": "_find_next_clump8(&clump, &empty, 8, 20)",
}


def validate_find_bit_source(text: str) -> tuple[str, object]:
    missing_tests = [
        label for label, marker in REQUIRED_TEST_MARKERS.items() if marker not in text
    ]
    if missing_tests:
        return ("missing_test_markers", missing_tests)

    missing_source = [
        label for label, marker in REQUIRED_SOURCE_MARKERS.items() if marker not in text
    ]
    if missing_source:
        return ("missing_source_markers", missing_source)

    return ("pass", None)


def load_find_bit_source(path: Path) -> tuple[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_file", path)
    return validate_find_bit_source(text)


def build_sample_source(omit_label: str | None = None) -> str:
    lines = [
        'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
        "    _ = findNextBit(&set_map, nbits, boundary);",
        "    _ = findNextAndBit(&and_lhs, &and_rhs, nbits, boundary);",
        "    _ = findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary);",
        "    _ = findNextZeroBit(&zero_map, nbits, boundary);",
        "}",
        'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
        "    _ = findNextBit(&set_map, nbits, boundary);",
        "}",
        'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start" {',
        "    _ = findNextBit(&set_map, nbits, boundary);",
        "}",
        'test "next scans past nbits return without reading bitmap words" {',
        "    _ = findNextBit(&empty, 7, 11);",
        "    _ = findNextZeroBit(&empty, 7, 11);",
        "    _ = findNextAndBit(&empty, &empty, 7, 11);",
        "    _ = findNextAndNotBit(&empty, &empty, 7, 11);",
        "}",
        'test "clump8 past-end scans return without reading bitmap words" {',
        "    _ = findNextClump8(&clump, &empty, 8, 8);",
        "    _ = find_next_clump8(&clump, &empty, 8, 12);",
        "    _ = _find_next_clump8(&clump, &empty, 8, 20);",
        "}",
        'test "find last bit clamps tail words to nbits" {',
        "    _ = findLastBit(&single_word, single_word_nbits);",
        "}",
    ]
    if omit_label is not None:
        marker = REQUIRED_TEST_MARKERS.get(omit_label, REQUIRED_SOURCE_MARKERS.get(omit_label))
        assert marker is not None
        lines = [line for line in lines if marker not in line]
    return "\n".join(lines) + "\n"


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_find_bit_source(build_sample_source())
    assert kind == "pass", (kind, payload)
    case_count += 1

    kind, payload = validate_find_bit_source(build_sample_source("boundary_tail_test"))
    assert kind == "missing_test_markers", (kind, payload)
    assert payload == ["boundary_tail_test"]
    case_count += 1

    kind, payload = validate_find_bit_source(build_sample_source("find_clump8_low_level_alias_past_end"))
    assert kind == "missing_source_markers", (kind, payload)
    assert payload == ["find_clump8_low_level_alias_past_end"]
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-find-bit-bench-anchors-") as tmp:
        source_path = Path(tmp) / "find_bit.zig"
        kind, payload = load_find_bit_source(source_path)
        assert kind == "missing_file", (kind, payload)
        assert payload == source_path
        case_count += 1

        source_path.write_text(build_sample_source(), encoding="utf-8")
        kind, payload = load_find_bit_source(source_path)
        assert kind == "pass", (kind, payload)
        case_count += 1

    print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the live find_bit helper still carries the current bench-adjacent edge anchors."
    )
    parser.add_argument("--self-test", action="store_true", help="Run self-test cases only.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = load_find_bit_source(FIND_BIT)
    if kind != "pass":
        print("PHASE1_FIND_BIT_BENCH_ANCHORS=fail")
        print(f"PHASE1_FIND_BIT_BENCH_ANCHORS_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_FIND_BIT_BENCH_ANCHORS=pass")
    print(f"PHASE1_FIND_BIT_BENCH_ANCHORS_SOURCE={FIND_BIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

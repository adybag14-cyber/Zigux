#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path("/workspace/direct-anchor-selftest-root")

EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_REVIEW_FIELDS = {
    "tools/lib/bitmap.zig": {
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
        "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
        "partial_xor_review_fields": [
            "partial_xor_nbits",
            "partial_xor_masked_values",
        ],
    },
    "tools/lib/find_bit.zig": {
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
        "tail_clamp_fixture_keys": [
            "tail_clamped_first",
            "tail_clamped_next",
            "tail_zero_clamped_first",
            "tail_zero_clamped_next",
            "tail_and_clamped_first",
            "tail_and_clamped_next",
            "tail_clamped_last",
            "tail_clamped_empty_last",
        ],
    },
    "tools/lib/rbtree.zig": {
        "duplicate_search_anchors": [
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
        ],
        "cached_root_followup_anchors": [
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "parity_fixture_keys": [
            "find_found_key",
            "find_missing",
            "find_first_serial",
            "next_match_serials",
            "next_match_terminal_null",
        ],
    },
    "tools/lib/string.zig": {
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
        "helper_test_anchors": [
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "memchrInv follows the earliest dirty byte as long buffers change"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ],
        "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
        "parity_fixture_keys": [
            "replace_char",
            "replace_char_end",
            "replace_char_cstr_end",
            "replace_char_cstr_bytes",
            "memchr_inv_index",
            "memchr_inv_none",
        ],
    },
}

HELPER_TEST_MARKERS = {
    "tools/lib/bitmap.zig": [
        'test "bitmap range helpers honor exact first-word boundaries"',
        'test "bitmap predicates ignore out-of-range tail bits"',
        'test "bitmap scnprintf reports full length while truncating the buffer"',
        'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        'test "bitmap copy alias preserves raw source words without tail clearing"',
        'test "bitmap zero-bit helpers stay explicit no-ops"',
    ],
    "tools/lib/find_bit.zig": [
        'test "single-word next scans honor start masks"',
        'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        'test "zero-bit windows return without reading bitmap words"',
        'test "next scans past nbits return without reading bitmap words"',
        'test "low-level underscore aliases mirror the primary find helpers"',
    ],
    "tools/lib/rbtree.zig": [
        'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
        'test "rbtree nextMatch walks the duplicate range in order"',
        'test "rbtree matchIterator walks the duplicate range in order"',
        'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
        'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
        'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
        'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
        'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
    ],
    "tools/lib/string.zig": [
        'test "memparse applies suffixes before signed clamping"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "memchrInv follows the earliest dirty byte as long buffers change"',
        'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    ],
}

PHASE1_HELPERS_MARKERS = [
    "fixture.find_bit.inclusive_boundary_next",
    "fixture.find_bit.inclusive_boundary_zero",
    "fixture.find_bit.inclusive_boundary_and",
    "fixture.find_bit.tail_clamped_first",
    "fixture.find_bit.tail_clamped_next",
    "fixture.find_bit.tail_zero_clamped_first",
    "fixture.find_bit.tail_zero_clamped_next",
    "fixture.find_bit.tail_and_clamped_first",
    "fixture.find_bit.tail_and_clamped_next",
    "fixture.find_bit.tail_clamped_last",
    "fixture.find_bit.tail_clamped_empty_last",
    "fixture.bitmap.partial_xor_nbits",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.rbtree.find_found_key",
    "fixture.rbtree.find_missing",
    "fixture.rbtree.find_first_serial",
    "fixture.rbtree.next_match_serials",
    "fixture.rbtree.next_match_terminal_null",
    'test "phase 1 string replaceChar stops at embedded NUL"',
]


def collect_mismatches(root: Path) -> list[str]:
    manifest_path = root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mismatches: list[str] = []

    lane = manifest.get("lane_sequencing", {})
    if lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        mismatches.append("lane_sequencing:direct_anchor_followup_helpers")

    review_anchors = manifest.get("review_anchors", {})
    for helper, expected_fields in EXPECTED_REVIEW_FIELDS.items():
        actual_helper = review_anchors.get(helper)
        if not isinstance(actual_helper, dict):
            mismatches.append(f"review_anchors:missing:{helper}")
            continue
        for field, expected in expected_fields.items():
            actual = actual_helper.get(field)
            if actual != expected:
                mismatches.append(f"review_anchors:{helper}:{field}")

    for helper, markers in HELPER_TEST_MARKERS.items():
        text = (root / helper).read_text(encoding="utf-8")
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                mismatches.append(f"helper_anchor:{helper}:{marker}:expected=1:actual={count}")

    phase1_helpers = (root / "zigux" / "tests" / "phase1_helpers.zig").read_text(encoding="utf-8")
    for marker in PHASE1_HELPERS_MARKERS:
        count = phase1_helpers.count(marker)
        if count < 1:
            mismatches.append(f"phase1_helpers:{marker}:expected>=1:actual={count}")

    return mismatches


def seed_fixture_root(root: Path) -> None:
    manifest_path = root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "lane_sequencing": {
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
                },
                "review_anchors": EXPECTED_REVIEW_FIELDS,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for helper, markers in HELPER_TEST_MARKERS.items():
        path = root / helper
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")

    phase1_helpers = root / "zigux" / "tests" / "phase1_helpers.zig"
    phase1_helpers.parent.mkdir(parents=True, exist_ok=True)
    phase1_helpers.write_text("\n".join(PHASE1_HELPERS_MARKERS) + "\n", encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        seed_fixture_root(tmp_root)
        assert not collect_mismatches(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = EXPECTED_DIRECT_HELPERS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        mismatches = collect_mismatches(tmp_root)
        assert "lane_sequencing:direct_anchor_followup_helpers" in mismatches

        seed_fixture_root(tmp_root)
        string_path = tmp_root / "tools" / "lib" / "string.zig"
        string_path.write_text(
            string_path.read_text(encoding="utf-8").replace(
                'test "memparse applies suffixes before signed clamping"\n',
                "",
            ),
            encoding="utf-8",
        )
        mismatches = collect_mismatches(tmp_root)
        assert any("memparse applies suffixes before signed clamping" in item for item in mismatches)

        seed_fixture_root(tmp_root)
        phase1_helpers = tmp_root / "zigux" / "tests" / "phase1_helpers.zig"
        phase1_helpers.write_text(
            phase1_helpers.read_text(encoding="utf-8").replace("fixture.rbtree.next_match_serials\n", ""),
            encoding="utf-8",
        )
        mismatches = collect_mismatches(tmp_root)
        assert any("fixture.rbtree.next_match_serials" in item for item in mismatches)

    print("PHASE1_DIRECT_ANCHOR_SELF_TEST=pass")
    print("PHASE1_DIRECT_ANCHOR_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 1 direct-anchor helper follow-up packet."
    )
    parser.add_argument("--self-test", action="store_true", help="run isolated checker self-tests")
    parser.add_argument("root", nargs="?", default=".", help="repository root to inspect")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    mismatches = collect_mismatches(Path(args.root).resolve())
    if mismatches:
        print("PHASE1_DIRECT_ANCHOR_PACKET=fail")
        print("PHASE1_DIRECT_ANCHOR_MISMATCHES_START")
        for item in mismatches:
            print(item)
        print("PHASE1_DIRECT_ANCHOR_MISMATCHES_END")
        return 1

    print("PHASE1_DIRECT_ANCHOR_PACKET=pass")
    print(f"PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    print(f"PHASE1_DIRECT_ANCHOR_MARKER_COUNT={len(PHASE1_HELPERS_MARKERS) + sum(len(v) for v in HELPER_TEST_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

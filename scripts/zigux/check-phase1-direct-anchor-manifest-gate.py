#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


EXPECTED_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap set clear weight and empty full helpers"',
            'test "bitmap range helpers preserve edges across whole-word spans"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap copy helpers keep zero-sized destination views untouched"',
            'test "bitmap zero-bit logical helpers stay explicit"',
            'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
            'test "bitmap and andnot equal intersects subset"',
            'test "bitmap tail-masked helpers ignore out-of-range differences"',
            'test "bitmap full empty and weight ignore out-of-range tail bits"',
            'test "bitmap xor keeps caller-selected bit window"',
            'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
            'test "bitmap or keeps caller-selected bit window"',
            'test "bitmap or across a multiword tail still lets callers clamp the last word"',
            'test "bitmap weighted or and xor clamp counts to the declared tail window"',
            'test "bitmap weighted and andnot clamp counts to the declared tail window"',
            'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
            'test "bitmap scnprintf collapses contiguous ranges"',
            'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
            'test "bitmap scnprintf truncates and keeps a terminator slot"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
            'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
            'test "bitmap allocation helpers size zero fill and reset optionals"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
        "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
        "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
        "equal_fast_path_anchor": 'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
        "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
        "or_window_anchor": 'test "bitmap or keeps caller-selected bit window"',
        "or_multiword_tail_anchor": 'test "bitmap or across a multiword tail still lets callers clamp the last word"',
        "weighted_tail_count_anchor": 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
        "complement_tail_anchor": 'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "parity_fixture_keys": [
            "alloc_words",
            "zalloc_words",
            "zalloc_values",
            "scnprintf",
            "truncated_scnprintf_len",
            "truncated_scnprintf",
            "terminator_only_scnprintf_len",
            "terminator_only_nul",
            "zero_length_scnprintf_len",
        ],
        "partial_xor_review_fields": [
            "partial_xor_nbits",
            "partial_xor_masked_values",
        ],
        "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf truncates and keeps a terminator slot"',
        "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "copy_zero_and_aligned_anchors": [
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap copy helpers keep zero-sized destination views untouched"',
        ],
        "zero_bit_noop_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
        "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
        "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    },
    "tools/lib/find_bit.zig": {
        "helper_test_anchors": [
            'test "find first and next set bits across words, with andnot gaps explicit"',
            'test "find zero bits respects the declared bit count"',
            'test "find and bit returns the first shared set bit"',
            'test "underscore entry points reuse the public helper behavior"',
            'test "single-word next scans honor start masks"',
            'test "single-word first scans clamp to the declared bit window"',
            'test "single-word next scans clamp partial windows before returning nbits"',
            'test "word-boundary next scans start fresh on the next word"',
            'test "zero-bit windows return without reading bitmap words"',
            'test "zero-sized scans ignore populated backing words"',
            'test "next scans past nbits return without reading bitmap words"',
            'test "tail mask ignores set bits beyond nbits"',
            'test "tail mask ignores zero bits beyond nbits"',
            'test "tail mask ignores shared bits beyond nbits"',
            'test "tail-word next set scans skip earlier in-range matches before clamping"',
            'test "clump8 scans align to the containing byte and return its value"',
            'test "clump8 scans keep tail bytes reachable from partial final words"',
            'test "clump8 scans mask tail bits beyond nbits"',
            'test "clump8 scans leave the caller byte untouched when no set bit remains"',
            'test "clump8 zero-bit and past-end windows leave the caller byte untouched"',
            'test "clump8 past-end scans return without reading bitmap words"',
            'test "getValue8 reads aligned bytes from bitmap words"',
            'test "getValue8 reads the last aligned byte of a word without folding in the next word"',
            'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
            'test "find last bit scans backward across words"',
            'test "find last bit ignores storage beyond an exact word boundary"',
            'test "find last bit clamps tail words to nbits"',
            'test "find last bit returns nbits when no set bits remain"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
            'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        ],
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "single_word_tail_inclusive_boundary_anchor": 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
        "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        "andnot_scan_entrypoints": [
            "findFirstAndNotBit",
            "find_first_andnot_bit",
            "_find_first_andnot_bit",
            "findNextAndNotBit",
            "find_next_andnot_bit",
            "_find_next_andnot_bit",
        ],
        "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
        "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
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
        "tail_inclusive_boundary_fixture_keys": [
            "tail_inclusive_boundary_next",
            "tail_inclusive_boundary_zero",
            "tail_inclusive_boundary_and",
        ],
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": [
            'test "rbtree inserts and traverses in sorted order"',
            'test "rbtree erase and replace keep traversal consistent"',
            'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
            'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
            'test "rbtree eraseInit detaches erased node"',
            'test "rbtree eraseInit clears singleton roots before reseed"',
            'test "rbtree postorder and empty node helpers behave"',
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
        "parity_fixture_keys": [
            "empty_root",
            "insert_order",
            "reverse_order",
            "replace_order",
            "erase_init_order",
            "postorder_count",
            "erase_init_node_empty",
            "cleared_node_empty",
            "find_found_key",
            "find_missing",
            "find_first_serial",
            "next_match_serials",
            "match_iterator_serials",
            "next_match_terminal_null",
        ],
        "cached_leftmost_fixture_keys": [
            "cached_leftmost_return_serials",
        ],
        "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
        "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
        "duplicate_search_anchors": [
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
        ],
        "cached_root_followup_anchors": [
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
    },
    "tools/lib/string.zig": {
        "helper_test_anchors": [
            'test "strtobool accepts common Linux forms"',
            'test "strlcpy copies and returns the source length"',
            'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
            'test "strscpyPad zero-pads the tail after a short source"',
            'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
            'test "strscpyPad preserves strscpy truncation semantics"',
            'test "strscpy_pad mirrors strscpyPad padding semantics"',
            'test "strscpy and strscpyPad keep one-byte destinations terminated"',
            'test "streq matches C-string equality semantics"',
            'test "skip trim remove and replace spaces work in place"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
            'test "strreplace mirrors replaceChar C-string semantics"',
            'test "strHasPrefix returns the matched prefix length with C-string semantics"',
            'test "strHasSuffix returns the matched suffix length with C-string semantics"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
            'test "kbasename returns the final path component with C-string semantics"',
            'test "sysfsStreq treats trailing newline and NUL as equivalent"',
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
            'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
            'test "matchString finds C-string matches and preserves first-match order"',
            'test "match_string mirrors matchString for empty and matched lists"',
            'test "memdup and memchrInv preserve byte content"',
            'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
            'test "memchrInv follows the earliest dirty byte as long buffers change"',
            'test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"',
            'test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"',
            'test "memchrInv keeps the earliest dirty byte for long non-zero scans across alignments"',
            'test "memchrInv keeps the earliest dirty byte for long zero-value scans across alignments"',
            'test "memchrInv short zero-value scans stay byte-accurate"',
            'test "memchrInv keeps the earliest dirty byte across the fast-path cutoff"',
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
            'test "strchr mirrors full-length C-string searches"',
            'test "strrchr finds the last in-range match with C-string semantics"',
            'test "strchr and strrchr return the terminator index when searching for NUL"',
            'test "strpbrk finds the first accepted byte with C-string semantics"',
            'test "strspn counts the accepted prefix with C-string semantics"',
            'test "strcspn counts until the first rejected byte with C-string semantics"',
            'test "strnchr honors count and C-string boundaries"',
            'test "strnlen honors count and C-string boundaries"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
        ],
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
        "prefix_suffix_review_anchors": [
            'test "strHasPrefix returns the matched prefix length with C-string semantics"',
            'test "strHasSuffix returns the matched suffix length with C-string semantics"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
        ],
        "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
        "parity_fixture_keys": [
            "strtobool_y",
            "strtobool_on",
            "strtobool_zero",
            "strtobool_off",
            "strtobool_invalid",
            "strlcpy_len",
            "strlcpy_buffer",
            "skip_spaces",
            "trim_spaces",
            "remove_spaces",
            "replace_char",
            "replace_char_end",
            "replace_char_cstr_end",
            "replace_char_cstr_bytes",
            "memchr_inv_index",
            "memchr_inv_none",
        ],
    },
}


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return Path(__file__).resolve().parents[1]


def load_manifest(root: Path) -> dict:
    manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def collect_issues(manifest: dict) -> list[str]:
    issues: list[str] = []
    if manifest.get("phase") != "Phase 1":
        issues.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        issues.append("manifest:status=closed")
    if manifest.get("helper_count") != 13:
        issues.append("manifest:helper_count=13")

    helpers = manifest.get("helpers")
    if helpers != [
        "tools/lib/argv_split.zig",
        "tools/lib/bitmap.zig",
        "tools/lib/cmdline.zig",
        "tools/lib/ctype.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/hweight.zig",
        "tools/lib/list_sort.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/slab.zig",
        "tools/lib/str_error_r.zig",
        "tools/lib/string.zig",
        "tools/lib/vsprintf.zig",
        "tools/lib/zalloc.zig",
    ]:
        issues.append("manifest:helpers=expected_phase1_helper_list")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors=dict")
        return issues

    for helper in EXPECTED_HELPERS:
        actual_entry = review_anchors.get(helper)
        expected_entry = EXPECTED_REVIEW_ANCHORS[helper]
        if not isinstance(actual_entry, dict):
            issues.append(f"manifest:missing_review_anchor={helper}")
            continue
        for field, expected_value in expected_entry.items():
            if field not in actual_entry:
                issues.append(f"manifest:missing_review_anchor_field={helper}:{field}")
                continue
            if actual_entry[field] != expected_value:
                issues.append(f"manifest:review_anchor_value={helper}:{field}")

    return issues


def make_fixture_root(tmp_root: Path) -> None:
    manifest_path = tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": [
            "tools/lib/argv_split.zig",
            "tools/lib/bitmap.zig",
            "tools/lib/cmdline.zig",
            "tools/lib/ctype.zig",
            "tools/lib/find_bit.zig",
            "tools/lib/hweight.zig",
            "tools/lib/list_sort.zig",
            "tools/lib/rbtree.zig",
            "tools/lib/slab.zig",
            "tools/lib/str_error_r.zig",
            "tools/lib/string.zig",
            "tools/lib/vsprintf.zig",
            "tools/lib/zalloc.zig",
        ],
        "review_anchors": EXPECTED_REVIEW_ANCHORS,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def assert_issue_case(tmp_root: Path, mutate, expected_issue: str) -> None:
    mutate()
    issues = collect_issues(load_manifest(tmp_root))
    assert expected_issue in issues, issues
    make_fixture_root(tmp_root)


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_anchor_manifest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)
        assert collect_issues(load_manifest(tmp_root)) == []

        manifest_path = tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json"

        def load_current() -> dict:
            return json.loads(manifest_path.read_text(encoding="utf-8"))

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("scnprintf_cross_word_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:scnprintf_cross_word_anchor",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"].remove(
                        'test "bitmap Linux-style aliases mirror size state and allocation helpers"'
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:review_anchor_value=tools/lib/bitmap.zig:helper_test_anchors",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"].pop("tail_word_set_skip_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:tail_word_set_skip_anchor",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_clamp_fixture_keys"].remove(
                        "tail_clamped_last"
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:review_anchor_value=tools/lib/find_bit.zig:tail_clamp_fixture_keys",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/rbtree.zig"]["parity_fixture_keys"].remove(
                        "next_match_terminal_null"
                    ),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:review_anchor_value=tools/lib/rbtree.zig:parity_fixture_keys",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/string.zig"].pop("phase1_helper_replay_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:missing_review_anchor_field=tools/lib/string.zig:phase1_helper_replay_anchor",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: manifest_path.write_text(
                    json.dumps({**manifest, "helper_count": 12}, indent=2) + "\n",
                    encoding="utf-8",
                )
            )(load_current()),
            "manifest:helper_count=13",
        )
        case_count += 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the direct-anchor Phase 1 helper manifest packet for bitmap, find_bit, rbtree, and string."
    )
    parser.add_argument("--self-test", action="store_true", help="Run embedded self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux checkout root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    issues = collect_issues(load_manifest(repo_root_from_arg(args.root)))
    if issues:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail")
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUES_END")
        return 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")
    print(f"PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(
        "PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT="
        f"{sum(len(fields) for fields in EXPECTED_REVIEW_ANCHORS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
            'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            'test "bitmap allocator helpers size zero and free their buffers"',
            'test "bitmap size aliases round bit counts to full words in bytes"',
            'test "bitmap set clear weight and empty full helpers"',
            'test "bitmap range helpers honor exact first-word boundaries"',
            'test "bitmap range helpers clamp the final partial word"',
            'test "bitmap fill clamps tail bits in partial words"',
            'test "bitmap and andnot equal intersects subset"',
            'test "bitmap and andnot clamp tail bits in partial words"',
            'test "bitmap predicates ignore out-of-range tail bits"',
            'test "bitmap xor keeps caller-selected bit window"',
            'test "bitmap scnprintf collapses contiguous ranges"',
            'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
            'test "bitmap scnprintf reports full length while truncating the buffer"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap copy helpers keep zero-sized destination views untouched"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
            'test "bitmap zero-bit binary helpers stay explicit identity operations"',
            'test "bitmap Linux-style aliases mirror the primary helper surface"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
        "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
        "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "parity_fixture_keys": [
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
        "cross_word_scnprintf_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "copy_extend_zero_aligned_anchor": 'test "bitmap copy and extend handles zero and aligned counts"',
        "zero_sized_destination_view_anchor": 'test "bitmap copy helpers keep zero-sized destination views untouched"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
        "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
        "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
    },
    "tools/lib/find_bit.zig": {
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
        "tail_word_next_set_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
        "tail_word_next_zero_and_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
        "tail_word_start_mask_review_summary": "helper-local tail-word next-scan anchors stay explicit because the shared Phase 1 replay locks tail-clamped results but does not isolate same-tail-word starts that must skip earlier in-range matches before clamping",
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
        "helper_test_anchors": [
            'test "rbtree inserts and traverses in sorted order"',
            'test "rbtree erase and replace keep traversal consistent"',
            'test "rbtree eraseInit detaches erased node"',
            'test "rbtree postorder and empty node helpers behave"',
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
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
            "next_match_terminal_null",
        ],
    },
    "tools/lib/string.zig": {
        "helper_test_anchors": [
            'test "strtobool accepts common Linux forms"',
            'test "strlcpy copies and returns the source length"',
            'test "streq matches C-string equality semantics"',
            'test "skip trim remove and replace spaces work in place"',
            'test "strreplace mirrors replaceChar C-string semantics"',
            'test "strHasPrefix honors C-string boundaries"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
            'test "memdup and memchrInv preserve byte content"',
            'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ],
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
        "prefix_suffix_review_anchors": [
            'test "strHasPrefix honors C-string boundaries"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
        ],
        "prefix_suffix_review_summary": "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields",
        "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep trailing-rest splits aligned with unsigned parsing, signed overflow saturates, and suffixes are still consumed after saturation",
        "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
        "shared_replace_char_cstr_review_summary": "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership",
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
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("cross_word_scnprintf_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:cross_word_scnprintf_anchor",
        )
        case_count += 1

        assert_issue_case(
            tmp_root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"].remove(
                        'test "bitmap zero-bit binary helpers stay explicit identity operations"'
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
                    manifest["review_anchors"]["tools/lib/find_bit.zig"].pop("tail_word_next_set_anchor"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:tail_word_next_set_anchor",
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
                    manifest["review_anchors"]["tools/lib/string.zig"].pop("shared_replace_char_cstr_review_summary"),
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8"),
                )
            )(load_current()),
            "manifest:missing_review_anchor_field=tools/lib/string.zig:shared_replace_char_cstr_review_summary",
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_PHASE = "Phase 1"
EXPECTED_STATUS = "closed"
EXPECTED_HELPER_COUNT = 13
EXPECTED_HELPER_LIST = [
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
]

EXPECTED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "review_packet_summary": "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, and allocator optional-reset coverage.",
        "next_safe_step_note": "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and Linux-style alias follow-through no longer live in the helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through.",
        "partial_xor_review_fields": [
            "partial_xor_nbits",
            "partial_xor_masked_values",
        ],
    },
    "tools/lib/find_bit.zig": {
        "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "tail_word_inclusive_boundary_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.",
        "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
        "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias, or tail-word skip anchors, or committed tail-clamped replay drift; do not reopen older saved validator cues or neighboring helper families.",
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
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "review_packet_summary": "shared find, first-match, next-match, and match-iterator duplicate-search parity stays explicit through the Phase 1 fixture and replay, and current master already consumes `cached_leftmost_return_serials` as shared cached-root leftmost-return evidence, while the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed review anchors stay explicit at the helper surface for any paths the shared replay still does not cover",
        "next_safe_step_note": "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; until another committed cached-root field lands, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors.",
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
    },
    "tools/lib/string.zig": {
        "prefix_suffix_review_summary": "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields, so strHasPrefix and str_has_prefix plus strHasSuffix and str_has_suffix plus strstarts plus strEndsWith and str_ends_with plus strends remain review-visible at the helper surface",
        "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation",
        "shared_replace_char_cstr_review_summary": "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership",
        "next_safe_step_note": "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.",
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
    return ROOT


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))


def collect_issues(manifest: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if manifest.get("phase") != EXPECTED_PHASE:
        issues.append("manifest:phase")
    if manifest.get("status") != EXPECTED_STATUS:
        issues.append("manifest:status")
    if manifest.get("helper_count") != EXPECTED_HELPER_COUNT:
        issues.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPER_LIST:
        issues.append("manifest:helpers")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors")
        return issues

    for helper in EXPECTED_HELPERS:
        expected_entry = EXPECTED_REVIEW_ANCHORS[helper]
        actual_entry = review_anchors.get(helper)
        if not isinstance(actual_entry, dict):
            issues.append(f"manifest:missing_review_anchor={helper}")
            continue
        for field, expected_value in expected_entry.items():
            if actual_entry.get(field) != expected_value:
                issues.append(f"manifest:review_anchor_value={helper}:{field}")

    return issues


def write_manifest(root: Path, payload: dict[str, object]) -> None:
    path = root / MANIFEST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def good_manifest() -> dict[str, object]:
    return {
        "phase": EXPECTED_PHASE,
        "status": EXPECTED_STATUS,
        "helper_count": EXPECTED_HELPER_COUNT,
        "helpers": list(EXPECTED_HELPER_LIST),
        "review_anchors": copy.deepcopy(EXPECTED_REVIEW_ANCHORS),
    }


def assert_issue_case(root: Path, mutate, expected_issue: str) -> None:
    mutate()
    issues = collect_issues(load_manifest(root))
    assert expected_issue in issues, issues
    write_manifest(root, good_manifest())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_anchor_manifest_gate_") as tmp_dir:
        root = Path(tmp_dir)
        write_manifest(root, good_manifest())
        assert collect_issues(load_manifest(root)) == []

        manifest_path = root / MANIFEST_REL

        def load_current() -> dict[str, object]:
            return json.loads(manifest_path.read_text(encoding="utf-8"))

        assert_issue_case(
            root,
            lambda: write_manifest(root, {**load_current(), "helper_count": 12}),
            "manifest:helper_count",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: write_manifest(root, {**load_current(), "review_anchors": "drift"}),
            "manifest:review_anchors",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("review_packet_summary"),
                    write_manifest(root, manifest),
                )
            )(load_current()),
            "manifest:review_anchor_value=tools/lib/bitmap.zig:review_packet_summary",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_clamp_fixture_keys"].remove("tail_clamped_last"),
                    write_manifest(root, manifest),
                )
            )(load_current()),
            "manifest:review_anchor_value=tools/lib/find_bit.zig:tail_clamp_fixture_keys",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/rbtree.zig"].pop("next_safe_step_note"),
                    write_manifest(root, manifest),
                )
            )(load_current()),
            "manifest:review_anchor_value=tools/lib/rbtree.zig:next_safe_step_note",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/string.zig"]["parity_fixture_keys"].remove("memchr_inv_none"),
                    write_manifest(root, manifest),
                )
            )(load_current()),
            "manifest:review_anchor_value=tools/lib/string.zig:parity_fixture_keys",
        )
        case_count += 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 direct-anchor helper manifest packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run embedded checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux checkout root.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

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
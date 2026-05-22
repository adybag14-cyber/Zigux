#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

EXPECTED_HELPERS = [
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

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded "
    "direct helper-local follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

REVIEW_CHECKS = {
    "tools/lib/bitmap.zig": {
        "required_anchor_subset": [
            'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
            'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
            'test "bitmap weighted and andnot clamp counts to the declared tail window"',
            'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
            'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
            'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
        ],
        "required_exact_lists": {
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
        },
        "required_exact_scalars": {
            "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        },
        "required_summary_fragments": [
            "partial-window xor replay",
            "exact-word-boundary equality fast-path masking",
            "weighted tail-count clamping",
            "allocator optional-reset coverage",
        ],
        "required_next_step_fragments": [
            "keep bitmap parked unless a fresh reread finds new direct-anchor drift",
            "do not reopen older closure-side or validator-route cue names by default",
        ],
    },
    "tools/lib/find_bit.zig": {
        "required_anchor_subset": [
            'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
            'test "clump8 past-end scans return without reading bitmap words"',
            'test "getValue8 reads the last aligned byte of a word without folding in the next word"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        ],
        "required_exact_lists": {
            "andnot_scan_entrypoints": [
                "findFirstAndNotBit",
                "find_first_andnot_bit",
                "_find_first_andnot_bit",
                "findNextAndNotBit",
                "find_next_andnot_bit",
                "_find_next_andnot_bit",
            ],
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
        "required_exact_scalars": {
            "same_word_start_masks": 'test "single-word next scans honor start masks"',
            "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        },
        "required_summary_fragments": [
            "tail-inclusive-boundary find_bit replay",
            "zero-sized short-circuit",
            "Linux-style alias behavior",
        ],
        "required_next_step_fragments": [
            "coverage including the shipped andnot scan entry points",
            "do not reopen older saved validator cues or neighboring helper families",
        ],
    },
    "tools/lib/rbtree.zig": {
        "required_anchor_subset": [
            'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
            'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "required_exact_lists": {
            "cached_leftmost_fixture_keys": [
                "cached_leftmost_return_serials",
            ],
            "duplicate_search_replay_keys": [
                "find_found_key",
                "find_missing",
                "find_first_serial",
                "next_match_serials",
                "match_iterator_serials",
                "next_match_terminal_null",
            ],
        },
        "required_exact_scalars": {
            "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
        },
        "required_summary_fragments": [
            "cached-leftmost-return witness",
            "cached-root alias",
            "shared smoke route does not replay exactly",
        ],
        "required_next_step_fragments": [
            "cached-root insert-miss",
            "until another committed cached-root field lands",
        ],
    },
    "tools/lib/string.zig": {
        "required_anchor_subset": [
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
            'test "memparse applies suffixes before signed clamping"',
            'test "strchr and strrchr return the terminator index when searching for NUL"',
            'test "strcspn counts until the first rejected byte with C-string semantics"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
        ],
        "required_exact_lists": {
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
            "memparse_review_anchors": [
                'test "memparse handles decimal hexadecimal octal and suffixes"',
                'test "memparse keeps original rest when sign is not followed by digits"',
                'test "memparse saturates signed overflow instead of trapping"',
                'test "memparse clamps explicit positive signed overflow"',
                'test "memparse keeps signed values and their trailing rest aligned"',
                'test "memparse consumes suffix after saturation"',
                'test "memparse applies suffixes before signed clamping"',
            ],
        },
        "required_exact_scalars": {
            "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
        },
        "required_summary_fragments": [
            ("prefix_suffix_review_summary", "dedicated prefix or suffix fixture fields"),
            ("sysfs_review_summary", "dedicated sysfs fixture keys"),
            ("strnchr_review_summary", "dedicated counted-search or search-length fixture keys"),
        ],
        "required_next_step_fragments": [
            "helper-local sysfs review anchors aligned",
            "do not reopen missing closure-side validator names by default",
        ],
    },
}

EXPECTED_BLOCKERS = {
    "status": "parked",
    "lane_sequencing": {
        "manifest": str(MANIFEST_REL),
        "shared_replay_parked_helper_count": len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
        "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
        "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
        "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
        "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
    },
    "replay": {
        "path": "zigux/tests/phase1_helpers.zig",
        "state": "blocked",
    },
    "c_harness": {
        "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        "state": "blocked",
        "reason": "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
    },
}


class CheckError(Exception):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CheckError(f"duplicate_key:{key}")
        result[key] = value
    return result


def read_json_file(path: Path, label: str) -> object:
    if not path.exists():
        raise CheckError(f"{label}:missing")
    if not path.is_file():
        raise CheckError(f"{label}:not_file")
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except CheckError as exc:
        raise CheckError(f"{label}:{exc}") from exc
    except json.JSONDecodeError as exc:
        raise CheckError(
            f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"
        ) from exc


def expect(condition: bool, issues: list[str], label: str) -> None:
    if not condition:
        issues.append(label)


def expect_list_contains(
    values: object,
    required_items: list[str],
    issues: list[str],
    label: str,
) -> None:
    if not isinstance(values, list):
        issues.append(f"{label}:not_list")
        return
    for item in required_items:
        if item not in values:
            issues.append(f"{label}:missing={item}")


def expect_text_contains(
    value: object,
    required_fragments: list[str],
    issues: list[str],
    label: str,
) -> None:
    if not isinstance(value, str):
        issues.append(f"{label}:not_string")
        return
    for fragment in required_fragments:
        if fragment not in value:
            issues.append(f"{label}:missing_fragment={fragment}")


def check_manifest(payload: object, issues: list[str]) -> None:
    if not isinstance(payload, dict):
        issues.append("manifest:not_json_object")
        return

    expect(payload.get("phase") == "Phase 1", issues, "manifest:phase")
    expect(payload.get("status") == "closed", issues, "manifest:status")
    expect(payload.get("helper_count") == len(EXPECTED_HELPERS), issues, "manifest:helper_count")
    expect(payload.get("helpers") == EXPECTED_HELPERS, issues, "manifest:helpers")

    lane = payload.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("manifest:lane_sequencing:not_object")
    else:
        expect(
            lane.get("shared_replay_parked_helpers") == EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            issues,
            "manifest:shared_replay_helpers",
        )
        expect(
            lane.get("direct_anchor_followup_helpers") == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            issues,
            "manifest:direct_anchor_helpers",
        )
        expect(lane.get("rule_summary") == EXPECTED_RULE_SUMMARY, issues, "manifest:rule_summary")
        expect(
            lane.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE,
            issues,
            "manifest:anti_overlap_rule",
        )

    review_anchors = payload.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors:not_object")
        return

    for helper, helper_checks in REVIEW_CHECKS.items():
        entry = review_anchors.get(helper)
        if not isinstance(entry, dict):
            issues.append(f"manifest:{helper}:missing_entry")
            continue

        expect_list_contains(
            entry.get("helper_test_anchors"),
            helper_checks["required_anchor_subset"],
            issues,
            f"manifest:{helper}:helper_test_anchors",
        )

        for field_name, expected_value in helper_checks.get("required_exact_lists", {}).items():
            expect(
                entry.get(field_name) == expected_value,
                issues,
                f"manifest:{helper}:{field_name}",
            )

        for field_name, expected_value in helper_checks.get("required_exact_scalars", {}).items():
            expect(
                entry.get(field_name) == expected_value,
                issues,
                f"manifest:{helper}:{field_name}",
            )

        summary_fragments = helper_checks.get("required_summary_fragments", [])
        if helper == "tools/lib/string.zig":
            for field_name, fragment in summary_fragments:
                expect_text_contains(
                    entry.get(field_name),
                    [fragment],
                    issues,
                    f"manifest:{helper}:{field_name}",
                )
        else:
            expect_text_contains(
                entry.get("review_packet_summary"),
                summary_fragments,
                issues,
                f"manifest:{helper}:review_packet_summary",
            )

        expect_text_contains(
            entry.get("next_safe_step_note"),
            helper_checks["required_next_step_fragments"],
            issues,
            f"manifest:{helper}:next_safe_step_note",
        )


def check_blockers(payload: object, issues: list[str]) -> None:
    if not isinstance(payload, dict):
        issues.append("blockers:not_json_object")
        return

    expect(payload.get("status") == EXPECTED_BLOCKERS["status"], issues, "blockers:status")

    lane = payload.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("blockers:lane_sequencing:not_object")
    else:
        for field_name, expected_value in EXPECTED_BLOCKERS["lane_sequencing"].items():
            expect(
                lane.get(field_name) == expected_value,
                issues,
                f"blockers:lane_sequencing:{field_name}",
            )

    replay = payload.get("replay")
    if not isinstance(replay, dict):
        issues.append("blockers:replay:not_object")
    else:
        expect(replay.get("path") == EXPECTED_BLOCKERS["replay"]["path"], issues, "blockers:replay:path")
        expect(replay.get("state") == EXPECTED_BLOCKERS["replay"]["state"], issues, "blockers:replay:state")

    c_harness = payload.get("c_harness")
    if not isinstance(c_harness, dict):
        issues.append("blockers:c_harness:not_object")
    else:
        for field_name, expected_value in EXPECTED_BLOCKERS["c_harness"].items():
            expect(
                c_harness.get(field_name) == expected_value,
                issues,
                f"blockers:c_harness:{field_name}",
            )


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        manifest = read_json_file(root / MANIFEST_REL, "manifest")
    except CheckError as exc:
        issues.append(str(exc))
    else:
        check_manifest(manifest, issues)

    try:
        blockers = read_json_file(root / BLOCKERS_REL, "blockers")
    except CheckError as exc:
        issues.append(str(exc))
    else:
        check_blockers(blockers, issues)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=fail")
        for issue in issues:
            print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_ISSUE={issue}")
        return 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")
    print(f"PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(f"PHASE1_DIRECT_ANCHOR_REVIEW_HELPER_COUNT={len(REVIEW_CHECKS)}")
    print(f"PHASE1_DIRECT_ANCHOR_MANIFEST={MANIFEST_REL}")
    print(f"PHASE1_DIRECT_ANCHOR_BLOCKERS={BLOCKERS_REL}")
    return 0


def good_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "helper_test_anchors": [
                    'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
                    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
                    'test "bitmap weighted and andnot clamp counts to the declared tail window"',
                    'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
                    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
                    'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
                ],
                "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
                "review_packet_summary": (
                    "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation "
                    "words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, "
                    "while current master keeps the direct helper-local bitmap packet bounded to exact-word-boundary "
                    "equality fast-path masking, weighted tail-count clamping, and allocator optional-reset coverage."
                ),
                "parity_fixture_keys": list(REVIEW_CHECKS["tools/lib/bitmap.zig"]["required_exact_lists"]["parity_fixture_keys"]),
                "partial_xor_review_fields": list(REVIEW_CHECKS["tools/lib/bitmap.zig"]["required_exact_lists"]["partial_xor_review_fields"]),
                "next_safe_step_note": (
                    "keep bitmap parked unless a fresh reread finds new direct-anchor drift; "
                    "do not reopen older closure-side or validator-route cue names by default"
                ),
            },
            "tools/lib/find_bit.zig": {
                "helper_test_anchors": [
                    'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
                    'test "clump8 past-end scans return without reading bitmap words"',
                    'test "getValue8 reads the last aligned byte of a word without folding in the next word"',
                    'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
                    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
                ],
                "same_word_start_masks": 'test "single-word next scans honor start masks"',
                "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
                "andnot_scan_entrypoints": list(REVIEW_CHECKS["tools/lib/find_bit.zig"]["required_exact_lists"]["andnot_scan_entrypoints"]),
                "tail_clamp_fixture_keys": list(REVIEW_CHECKS["tools/lib/find_bit.zig"]["required_exact_lists"]["tail_clamp_fixture_keys"]),
                "tail_inclusive_boundary_fixture_keys": list(REVIEW_CHECKS["tools/lib/find_bit.zig"]["required_exact_lists"]["tail_inclusive_boundary_fixture_keys"]),
                "review_packet_summary": (
                    "shared Phase 1 fixture keys own the exact tail-inclusive-boundary find_bit replay, "
                    "while helper-local anchors keep zero-sized short-circuit and Linux-style alias behavior review-visible."
                ),
                "next_safe_step_note": (
                    "coverage including the shipped andnot scan entry points; "
                    "do not reopen older saved validator cues or neighboring helper families"
                ),
            },
            "tools/lib/rbtree.zig": {
                "helper_test_anchors": [
                    'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
                    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
                    'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
                ],
                "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
                "cached_leftmost_fixture_keys": list(REVIEW_CHECKS["tools/lib/rbtree.zig"]["required_exact_lists"]["cached_leftmost_fixture_keys"]),
                "duplicate_search_replay_keys": list(REVIEW_CHECKS["tools/lib/rbtree.zig"]["required_exact_lists"]["duplicate_search_replay_keys"]),
                "review_packet_summary": (
                    "the current shared host-tools smoke replay keeps the cached-leftmost-return witness visible for "
                    "rbtree, while direct helper-local anchors continue to own cached-root alias paths that the shared smoke route does not replay exactly"
                ),
                "next_safe_step_note": (
                    "cached-root insert-miss stays helper-local until another committed cached-root field lands"
                ),
            },
            "tools/lib/string.zig": {
                "helper_test_anchors": [
                    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
                    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
                    'test "memparse applies suffixes before signed clamping"',
                    'test "strchr and strrchr return the terminator index when searching for NUL"',
                    'test "strcspn counts until the first rejected byte with C-string semantics"',
                    'test "strnchrNul returns the first match, NUL, or count boundary"',
                ],
                "memparse_review_anchors": list(REVIEW_CHECKS["tools/lib/string.zig"]["required_exact_lists"]["memparse_review_anchors"]),
                "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
                "parity_fixture_keys": list(REVIEW_CHECKS["tools/lib/string.zig"]["required_exact_lists"]["parity_fixture_keys"]),
                "prefix_suffix_review_summary": "shared Phase 1 replay still focuses on dedicated prefix or suffix fixture fields",
                "sysfs_review_summary": "shared Phase 1 replay still carries no dedicated sysfs fixture keys",
                "strnchr_review_summary": "shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys",
                "next_safe_step_note": (
                    "keep the helper-local sysfs review anchors aligned; "
                    "do not reopen missing closure-side validator names by default"
                ),
            },
        },
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_root(root: Path) -> Path:
    write_json(root / MANIFEST_REL, good_manifest())
    write_json(root / BLOCKERS_REL, EXPECTED_BLOCKERS)
    return root


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(issue.startswith(expected_prefix) for issue in collect_issues(root))


def run_self_test() -> int:
    failed: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_anchor_manifest_gate_") as tmp_dir:
        base = Path(tmp_dir)

        good_root = build_root(base / "good")
        if run_check(good_root) != 0:
            failed.append("good")

        missing_manifest_root = build_root(base / "missing_manifest")
        (missing_manifest_root / MANIFEST_REL).unlink()
        if not expect_failure(missing_manifest_root, "manifest:missing"):
            failed.append("missing_manifest")

        manifest_not_file_root = build_root(base / "manifest_not_file")
        (manifest_not_file_root / MANIFEST_REL).unlink()
        (manifest_not_file_root / MANIFEST_REL).mkdir(parents=True)
        if not expect_failure(manifest_not_file_root, "manifest:not_file"):
            failed.append("manifest_not_file")

        manifest_bad_json_root = build_root(base / "manifest_bad_json")
        write_text(manifest_bad_json_root / MANIFEST_REL, "{\n")
        if not expect_failure(manifest_bad_json_root, "manifest:json_decode_error:"):
            failed.append("manifest_bad_json")

        manifest_dup_key_root = build_root(base / "manifest_dup_key")
        write_text(
            manifest_dup_key_root / MANIFEST_REL,
            '{\n  "phase": "Phase 1",\n  "phase": "duplicate"\n}\n',
        )
        if not expect_failure(manifest_dup_key_root, "manifest:duplicate_key:phase"):
            failed.append("manifest_dup_key")

        manifest_direct_anchor_root = build_root(base / "manifest_direct_anchor")
        payload = good_manifest()
        payload["lane_sequencing"]["direct_anchor_followup_helpers"] = ["tools/lib/bitmap.zig"]
        write_json(manifest_direct_anchor_root / MANIFEST_REL, payload)
        if not expect_failure(manifest_direct_anchor_root, "manifest:direct_anchor_helpers"):
            failed.append("manifest_direct_anchor")

        manifest_bitmap_root = build_root(base / "manifest_bitmap")
        payload = good_manifest()
        payload["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"] = []
        write_json(manifest_bitmap_root / MANIFEST_REL, payload)
        if not expect_failure(
            manifest_bitmap_root,
            'manifest:tools/lib/bitmap.zig:helper_test_anchors:missing=test "bitmap equal fast path ignores storage beyond an exact word boundary"',
        ):
            failed.append("manifest_bitmap")

        manifest_string_root = build_root(base / "manifest_string")
        payload = good_manifest()
        payload["review_anchors"]["tools/lib/string.zig"]["parity_fixture_keys"] = ["strtobool_y"]
        write_json(manifest_string_root / MANIFEST_REL, payload)
        if not expect_failure(
            manifest_string_root,
            "manifest:tools/lib/string.zig:parity_fixture_keys",
        ):
            failed.append("manifest_string")

        missing_blockers_root = build_root(base / "missing_blockers")
        (missing_blockers_root / BLOCKERS_REL).unlink()
        if not expect_failure(missing_blockers_root, "blockers:missing"):
            failed.append("missing_blockers")

        blockers_not_file_root = build_root(base / "blockers_not_file")
        (blockers_not_file_root / BLOCKERS_REL).unlink()
        (blockers_not_file_root / BLOCKERS_REL).mkdir(parents=True)
        if not expect_failure(blockers_not_file_root, "blockers:not_file"):
            failed.append("blockers_not_file")

        blockers_bad_json_root = build_root(base / "blockers_bad_json")
        write_text(blockers_bad_json_root / BLOCKERS_REL, "{\n")
        if not expect_failure(blockers_bad_json_root, "blockers:json_decode_error:"):
            failed.append("blockers_bad_json")

        blockers_dup_key_root = build_root(base / "blockers_dup_key")
        write_text(
            blockers_dup_key_root / BLOCKERS_REL,
            '{\n  "status": "parked",\n  "status": "duplicate"\n}\n',
        )
        if not expect_failure(blockers_dup_key_root, "blockers:duplicate_key:status"):
            failed.append("blockers_dup_key")

        blockers_rule_root = build_root(base / "blockers_rule")
        payload = dict(EXPECTED_BLOCKERS)
        payload["lane_sequencing"] = dict(EXPECTED_BLOCKERS["lane_sequencing"])
        payload["lane_sequencing"]["anti_overlap_rule"] = "drift"
        write_json(blockers_rule_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_rule_root, "blockers:lane_sequencing:anti_overlap_rule"):
            failed.append("blockers_rule")

        blockers_harness_root = build_root(base / "blockers_harness")
        payload = dict(EXPECTED_BLOCKERS)
        payload["c_harness"] = dict(EXPECTED_BLOCKERS["c_harness"])
        payload["c_harness"]["state"] = "open"
        write_json(blockers_harness_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_harness_root, "blockers:c_harness:state"):
            failed.append("blockers_harness")

    if failed:
        print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=fail")
        for case in failed:
            print(f"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_FAILED_CASE={case}")
        return 1

    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")
    print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST_CASE_COUNT=13")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 direct-anchor helper manifest packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_root(args.write_sample_root.resolve())
        return 0
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

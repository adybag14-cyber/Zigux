#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
REPLAY_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")

EXPECTED_SECTIONS = (
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
)

EXPECTED_HELPERS = (
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
)

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS: dict[str, dict[str, object]] = {
    "tools/lib/bitmap.zig": {
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
        "equal_fast_path_anchor": 'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
        "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
        "weighted_tail_count_anchor": 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
        "weighted_and_tail_count_anchor": 'test "bitmap weighted and andnot clamp counts to the declared tail window"',
        "parity_fixture_keys": (
            "alloc_words",
            "zalloc_words",
            "zalloc_values",
            "scnprintf",
            "truncated_scnprintf_len",
            "truncated_scnprintf",
            "terminator_only_scnprintf_len",
            "terminator_only_nul",
            "zero_length_scnprintf_len",
        ),
        "shared_logical_fixture_keys": (
            "weight",
            "and_result",
            "and_values",
            "andnot_result",
            "andnot_values",
            "or_values",
            "xor_values",
            "equal",
            "intersects",
            "subset",
        ),
        "shared_range_fixture_keys": (
            "range_after_set",
            "range_after_clear",
            "full_after_fill",
            "empty_after_zero",
        ),
        "partial_xor_review_fields": (
            "partial_xor_nbits",
            "partial_xor_masked_values",
        ),
    },
    "tools/lib/find_bit.zig": {
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "single_word_tail_inclusive_boundary_anchor": 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
        "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        "andnot_scan_entrypoints": (
            "findFirstAndNotBit",
            "find_first_andnot_bit",
            "_find_first_andnot_bit",
            "findNextAndNotBit",
            "find_next_andnot_bit",
            "_find_next_andnot_bit",
        ),
        "tail_clamp_fixture_keys": (
            "tail_clamped_first",
            "tail_clamped_next",
            "tail_zero_clamped_first",
            "tail_zero_clamped_next",
            "tail_and_clamped_first",
            "tail_and_clamped_next",
            "tail_clamped_last",
            "tail_clamped_empty_last",
        ),
        "tail_inclusive_boundary_fixture_keys": (
            "tail_inclusive_boundary_next",
            "tail_inclusive_boundary_zero",
            "tail_inclusive_boundary_and",
        ),
    },
    "tools/lib/rbtree.zig": {
        "phase1_helper_replay_anchor": 'test "phase1 host-tools smoke exercises live helper behavior"',
        "ordered_alias_anchor": 'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
        "low_level_alias_anchor": 'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
        "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
        "parity_fixture_keys": (
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
        ),
        "cached_leftmost_fixture_keys": (
            "cached_leftmost_return_serials",
        ),
        "cached_root_transition_fixture_keys": (
            "cached_root_transition_serials",
        ),
        "duplicate_search_anchors": (
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
        ),
    },
    "tools/lib/string.zig": {
        "phase1_helper_replay_anchor": 'test "strreplace mirrors replaceChar C-string semantics"',
        "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
        "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics"',
        "strnchr_review_anchor": 'test "strnchr honors count and C-string boundaries"',
        "strnchrnul_review_anchor": 'test "strnchrNul returns the first match, NUL, or count boundary"',
        "parity_fixture_keys": (
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
        ),
        "memparse_review_anchors": (
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ),
        "sysfs_review_anchors": (
            'test "sysfsStreq treats trailing newline and NUL as equivalent"',
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
            'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
        ),
    },
}

EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS: dict[str, dict[str, tuple[str, ...]]] = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": (
            'test "bitmap range helpers preserve edges across whole-word spans"',
            'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
            'test "bitmap weighted or and xor clamp counts to the declared tail window"',
            'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
        ),
    },
    "tools/lib/find_bit.zig": {
        "helper_test_anchors": (
            'test "single-word next scans honor start masks"',
            'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
            'test "Linux-style aliases mirror the primary find helpers, including andnot"',
        ),
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": (
            'test "rbtree inserts and traverses in sorted order"',
            'test "rbtree ordered Linux-style aliases mirror traversal and replacement helpers"',
            'test "rbtree low-level Linux-style aliases mirror node-state helpers"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
        ),
    },
    "tools/lib/string.zig": {
        "helper_test_anchors": (
            'test "strreplace mirrors replaceChar C-string semantics"',
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "kbasename returns the final path component with C-string semantics"',
            'test "strnchrNul returns the first match, NUL, or count boundary"',
        ),
    },
}

EXPECTED_FIXTURE_VALUES = {
    ("string", "strtobool_invalid"): 184,
    ("string", "replace_char_cstr_end"): 2,
    ("string", "replace_char_cstr_bytes"): [97, 95, 0, 45, 122],
    ("slab", "zero_after_kmalloc"): True,
    ("bitmap", "truncated_scnprintf_len"): 7,
    ("bitmap", "truncated_scnprintf"): "1-3,7,1",
    ("bitmap", "terminator_only_scnprintf_len"): 0,
    ("bitmap", "zero_length_scnprintf_len"): 0,
    ("bitmap", "copy_clear_tail_values"): [18446744073709551615, 31],
    ("bitmap", "copy_and_extend_values"): [18446744073709551615, 31, 0],
    ("find_bit", "inclusive_boundary_next"): 63,
    ("find_bit", "inclusive_boundary_zero"): 63,
    ("find_bit", "inclusive_boundary_and"): 63,
    ("find_bit", "tail_clamped_first"): 67,
    ("find_bit", "tail_clamped_last"): 67,
    ("find_bit", "tail_clamped_empty_last"): 69,
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("rbtree", "cached_root_transition_serials"): [0, 0, 4, 2],
    ("rbtree", "next_match_terminal_null"): True,
    ("list_sort", "bool_sorted_ordinals"): [1, 3, 0, 2, 4],
}

EXPECTED_REPLAY_BLOCKER_IDS = (
    "phase1_helpers_zig_slab_zero_after_kmalloc",
    "phase1_helpers_c_harness_missing_c_sources",
)

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_REPLAY_MARKERS = (
    'test "phase 1 helper ports match committed parity fixture" {',
    'const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");',
    "const Fixture = struct {",
)

EXPECTED_REPLAY_BUILD_MARKERS = (
    '.root_source_file = b.path("phase1_helpers.zig"),',
    '.name = "phase1-helpers",',
    '"Run the focused Phase 1 helper replay anchor from zigux/tests",',
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def read_json(path: Path, label: str, issues: list[str]) -> object | None:
    try:
        payload = load_json_with_duplicate_tracking(read_text(path))
    except json.JSONDecodeError as exc:
        issues.append(f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}")
        return None

    duplicate_paths = collect_duplicate_json_key_paths(payload)
    if duplicate_paths:
        issues.extend(f"{label}:duplicate_json_key:{duplicate_path}" for duplicate_path in duplicate_paths)
        return None

    return payload


def run_python(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def ensure(condition: bool, issue: str, issues: list[str]) -> None:
    if not condition:
        issues.append(issue)


def ensure_exact_occurrence(text: str, label: str, marker: str, issues: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        issues.append(f"{label}:expected=1:actual={count}")


def ensure_review_anchor_exact_fields(helper: str, helper_payload: dict[str, object], issues: list[str]) -> None:
    for key, expected_value in EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS.get(helper, {}).items():
        actual_value = helper_payload.get(key)
        issue_prefix = f"manifest:review_anchors:{helper}:{key}"
        if isinstance(expected_value, tuple):
            ensure(isinstance(actual_value, list), f"{issue_prefix}:not_list", issues)
            if isinstance(actual_value, list):
                ensure(tuple(actual_value) == expected_value, f"{issue_prefix}:{actual_value!r}!={expected_value!r}", issues)
        else:
            ensure(actual_value == expected_value, f"{issue_prefix}:{actual_value!r}!={expected_value!r}", issues)


def ensure_review_anchor_subset_fields(helper: str, helper_payload: dict[str, object], issues: list[str]) -> None:
    for key, expected_values in EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS.get(helper, {}).items():
        actual_value = helper_payload.get(key)
        issue_prefix = f"manifest:review_anchors:{helper}:{key}"
        ensure(isinstance(actual_value, list), f"{issue_prefix}:not_list", issues)
        if isinstance(actual_value, list):
            for expected_value in expected_values:
                ensure(expected_value in actual_value, f"{issue_prefix}:missing:{expected_value}", issues)


def check_artifact_diff(root: Path, issues: list[str]) -> None:
    artifact_diff = root / ARTIFACT_DIFF_REL
    result = run_python(artifact_diff, "--self-test")
    ensure(result.returncode == 0, "artifact_diff:self_test:returncode", issues)
    ensure("ARTIFACT_DIFF_SELF_TEST=pass" in result.stdout, "artifact_diff:self_test:pass", issues)
    ensure("ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23" in result.stdout, "artifact_diff:self_test:case_count", issues)

    with tempfile.TemporaryDirectory(prefix="phase1_parity_artifact_diff_") as tmp_dir:
        tmp = Path(tmp_dir)
        text_expected = tmp / "expected.txt"
        text_actual = tmp / "actual.txt"
        json_expected = tmp / "expected.json"
        json_actual = tmp / "actual.json"
        bytes_expected = tmp / "expected.bin"
        bytes_actual = tmp / "actual.bin"

        text_expected.write_text("alpha\nbeta\n", encoding="utf-8")
        text_actual.write_text("alpha\nbeta\n", encoding="utf-8")
        json_expected.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8")
        json_actual.write_text('{"beta": [2, 3], "alpha": 1}\n', encoding="utf-8")
        bytes_expected.write_bytes(b"zigux-parity")
        bytes_actual.write_bytes(b"zigux-parity")

        cases = (
            ("text", ["--mode", "text", str(text_expected), str(text_actual)]),
            ("json", ["--mode", "json", str(json_expected), str(json_actual)]),
            ("bytes", ["--mode", "bytes", str(bytes_expected), str(bytes_actual)]),
            ("sha256", ["--mode", "sha256", str(bytes_expected), str(bytes_actual)]),
        )
        for name, argv in cases:
            result = run_python(artifact_diff, *argv)
            ensure(result.returncode == 0, f"artifact_diff:{name}:returncode", issues)
            ensure("ARTIFACT_DIFF=pass" in result.stdout, f"artifact_diff:{name}:pass", issues)


def check_replay_routes(root: Path, issues: list[str]) -> None:
    replay_text = read_text(root / REPLAY_REL)
    for marker in EXPECTED_REPLAY_MARKERS:
        ensure_exact_occurrence(replay_text, f"replay:{marker}", marker, issues)

    build_text = read_text(root / REPLAY_BUILD_REL)
    for marker in EXPECTED_REPLAY_BUILD_MARKERS:
        ensure_exact_occurrence(build_text, f"replay_build:{marker}", marker, issues)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):
        ensure((root / rel).exists(), f"missing:{rel.as_posix()}", issues)
    if issues:
        return issues

    check_artifact_diff(root, issues)
    check_replay_routes(root, issues)

    fixture_payload = read_json(root / FIXTURE_REL, "fixture", issues)
    if isinstance(fixture_payload, dict):
        ensure(tuple(fixture_payload.keys()) == EXPECTED_SECTIONS, "fixture:sections", issues)
        for (section, key), expected_value in EXPECTED_FIXTURE_VALUES.items():
            section_payload = fixture_payload.get(section)
            ensure(isinstance(section_payload, dict), f"fixture:{section}:not_object", issues)
            if isinstance(section_payload, dict):
                ensure(
                    section_payload.get(key) == expected_value,
                    f"fixture:{section}.{key}:{section_payload.get(key)!r}!={expected_value!r}",
                    issues,
                )
    elif fixture_payload is not None:
        ensure(False, "fixture:not_object", issues)

    manifest_payload = read_json(root / MANIFEST_REL, "manifest", issues)
    if isinstance(manifest_payload, dict):
        ensure(manifest_payload.get("phase") == "Phase 1", "manifest:phase", issues)
        ensure(manifest_payload.get("status") == "closed", "manifest:status", issues)
        ensure(manifest_payload.get("helper_count") == len(EXPECTED_HELPERS), "manifest:helper_count", issues)
        ensure(tuple(manifest_payload.get("helpers", ())) == EXPECTED_HELPERS, "manifest:helpers", issues)
        lane = manifest_payload.get("lane_sequencing")
        ensure(isinstance(lane, dict), "manifest:lane:not_object", issues)
        if isinstance(lane, dict):
            ensure(
                tuple(lane.get("shared_replay_parked_helpers", ())) == EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                "manifest:shared_replay_parked_helpers",
                issues,
            )
            ensure(
                tuple(lane.get("direct_anchor_followup_helpers", ())) == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                "manifest:direct_anchor_followup_helpers",
                issues,
            )
            ensure(lane.get("rule_summary") == EXPECTED_RULE_SUMMARY, "manifest:rule_summary", issues)
            ensure(lane.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE, "manifest:anti_overlap_rule", issues)
        review_anchors = manifest_payload.get("review_anchors")
        ensure(isinstance(review_anchors, dict), "manifest:review_anchors:not_object", issues)
        if isinstance(review_anchors, dict):
            for helper in EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS:
                ensure(helper in review_anchors, f"manifest:review_anchors:{helper}:missing", issues)
                if helper in review_anchors:
                    ensure(
                        isinstance(review_anchors.get(helper), dict),
                        f"manifest:review_anchors:{helper}:not_object",
                        issues,
                    )
                    helper_payload = review_anchors.get(helper)
                    if isinstance(helper_payload, dict):
                        ensure_review_anchor_exact_fields(helper, helper_payload, issues)
                        ensure_review_anchor_subset_fields(helper, helper_payload, issues)
    elif manifest_payload is not None:
        ensure(False, "manifest:not_object", issues)

    blockers_payload = read_json(root / BLOCKERS_REL, "blockers", issues)
    if isinstance(blockers_payload, dict):
        ensure(blockers_payload.get("status") == "parked", "blockers:status", issues)
        replay = blockers_payload.get("replay")
        ensure(isinstance(replay, dict), "blockers:replay:not_object", issues)
        if isinstance(replay, dict):
            ensure(replay.get("path") == REPLAY_REL.as_posix(), "blockers:replay:path", issues)
            ensure(replay.get("state") == "blocked", "blockers:replay:state", issues)
            blocker_list = replay.get("blockers")
            ensure(isinstance(blocker_list, list) and len(blocker_list) == 1, "blockers:replay:list", issues)
            if isinstance(blocker_list, list) and len(blocker_list) == 1 and isinstance(blocker_list[0], dict):
                blocker = blocker_list[0]
                ensure(blocker.get("id") == EXPECTED_REPLAY_BLOCKER_IDS[0], "blockers:replay:id", issues)
                ensure(blocker.get("field") == "slab.zero_after_kmalloc", "blockers:replay:field", issues)
                ensure(blocker.get("expected") is True, "blockers:replay:expected", issues)
                ensure(blocker.get("actual") is False, "blockers:replay:actual", issues)
        harness = blockers_payload.get("c_harness")
        ensure(isinstance(harness, dict), "blockers:c_harness:not_object", issues)
        if isinstance(harness, dict):
            ensure(harness.get("path") == HARNESS_REL.as_posix(), "blockers:c_harness:path", issues)
            ensure(harness.get("state") == "blocked", "blockers:c_harness:state", issues)
            ensure(harness.get("helper_count") == len(EXPECTED_HELPERS), "blockers:c_harness:helper_count", issues)
            ensure(tuple(harness.get("helpers", ())) == EXPECTED_HELPERS, "blockers:c_harness:helpers", issues)
            ensure(harness.get("blocker_id") == EXPECTED_REPLAY_BLOCKER_IDS[1], "blockers:c_harness:blocker_id", issues)
    elif blockers_payload is not None:
        ensure(False, "blockers:not_object", issues)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_PARITY=fail")
        for issue in issues:
            print(f"PHASE1_PARITY_ISSUE={issue}")
        return 1

    print("PHASE1_PARITY=pass")
    print(f"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}")
    print(f"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print("PHASE1_PARITY_REPLAY=present")
    print(f"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}")
    print("PHASE1_PARITY_BLOCKER_IDS=" + ",".join(EXPECTED_REPLAY_BLOCKER_IDS))
    print(f"PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT={len(EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS)}")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_review_anchor_payloads() -> dict[str, dict[str, object]]:
    payloads: dict[str, dict[str, object]] = {}
    for helper in EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS:
        payload: dict[str, object] = {}
        for key, value in EXPECTED_DIRECT_REVIEW_ANCHOR_EXACT_FIELDS[helper].items():
            payload[key] = list(value) if isinstance(value, tuple) else value
        for key, value in EXPECTED_DIRECT_REVIEW_ANCHOR_SUBSET_FIELDS.get(helper, {}).items():
            payload[key] = list(value)
        payloads[helper] = payload
    return payloads


def build_sample_root(root: Path) -> None:
    artifact_diff_text = """#!/usr/bin/env python3
from __future__ import annotations

import sys

if "--self-test" in sys.argv:
    print(\"ARTIFACT_DIFF_SELF_TEST=pass\")
    print(\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23\")
else:
    print(\"ARTIFACT_DIFF=pass\")
"""
    fixture_payload = {name: {} for name in EXPECTED_SECTIONS}
    fixture_payload["string"]["strtobool_invalid"] = 184
    fixture_payload["string"]["replace_char_cstr_end"] = 2
    fixture_payload["string"]["replace_char_cstr_bytes"] = [97, 95, 0, 45, 122]
    fixture_payload["slab"]["zero_after_kmalloc"] = True
    fixture_payload["bitmap"]["truncated_scnprintf_len"] = 7
    fixture_payload["bitmap"]["truncated_scnprintf"] = "1-3,7,1"
    fixture_payload["bitmap"]["terminator_only_scnprintf_len"] = 0
    fixture_payload["bitmap"]["zero_length_scnprintf_len"] = 0
    fixture_payload["bitmap"]["copy_clear_tail_values"] = [18446744073709551615, 31]
    fixture_payload["bitmap"]["copy_and_extend_values"] = [18446744073709551615, 31, 0]
    fixture_payload["find_bit"]["inclusive_boundary_next"] = 63
    fixture_payload["find_bit"]["inclusive_boundary_zero"] = 63
    fixture_payload["find_bit"]["inclusive_boundary_and"] = 63
    fixture_payload["find_bit"]["tail_clamped_first"] = 67
    fixture_payload["find_bit"]["tail_clamped_last"] = 67
    fixture_payload["find_bit"]["tail_clamped_empty_last"] = 69
    fixture_payload["rbtree"]["cached_leftmost_return_serials"] = [0, -1, 2, -1]
    fixture_payload["rbtree"]["cached_root_transition_serials"] = [0, 0, 4, 2]
    fixture_payload["rbtree"]["next_match_terminal_null"] = True
    fixture_payload["list_sort"]["bool_sorted_ordinals"] = [1, 3, 0, 2, 4]

    manifest_payload = {
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
        "review_anchors": build_sample_review_anchor_payloads(),
    }
    blockers_payload = {
        "status": "parked",
        "replay": {
            "path": REPLAY_REL.as_posix(),
            "state": "blocked",
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_IDS[0],
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                }
            ],
        },
        "c_harness": {
            "path": HARNESS_REL.as_posix(),
            "state": "blocked",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": EXPECTED_REPLAY_BLOCKER_IDS[1],
        },
    }
    replay_text = "\n".join(EXPECTED_REPLAY_MARKERS) + "\n"
    replay_build_text = "\n".join(EXPECTED_REPLAY_BUILD_MARKERS) + "\n"

    write_text(root / ARTIFACT_DIFF_REL, artifact_diff_text)
    write_text(root / REPLAY_REL, replay_text)
    write_text(root / REPLAY_BUILD_REL, replay_build_text)
    write_text(root / FIXTURE_REL, json.dumps(fixture_payload, indent=2) + "\n")
    write_text(root / MANIFEST_REL, json.dumps(manifest_payload, indent=2) + "\n")
    write_text(root / BLOCKERS_REL, json.dumps(blockers_payload, indent=2) + "\n")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1_parity_self_test_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        ensure(collect_issues(root) == [], "self_test:baseline", [])
        case_count += 1

        manifest_payload = read_json(root / MANIFEST_REL, "manifest", [])
        assert isinstance(manifest_payload, dict)
        review_anchors = manifest_payload["review_anchors"]
        assert isinstance(review_anchors, dict)
        bitmap_payload = review_anchors["tools/lib/bitmap.zig"]
        assert isinstance(bitmap_payload, dict)
        bitmap_payload.pop("shared_range_fixture_keys")
        write_text(root / MANIFEST_REL, json.dumps(manifest_payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert "manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:not_list" in issues
        case_count += 1

        build_sample_root(root)
        manifest_payload = read_json(root / MANIFEST_REL, "manifest", [])
        assert isinstance(manifest_payload, dict)
        review_anchors = manifest_payload["review_anchors"]
        assert isinstance(review_anchors, dict)
        bitmap_payload = review_anchors["tools/lib/bitmap.zig"]
        assert isinstance(bitmap_payload, dict)
        bitmap_payload["shared_range_fixture_keys"] = ["range_after_set", "range_after_clear", "full_after_fill"]
        write_text(root / MANIFEST_REL, json.dumps(manifest_payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(issue.startswith("manifest:review_anchors:tools/lib/bitmap.zig:shared_range_fixture_keys:") for issue in issues)
        case_count += 1

    print("PHASE1_PARITY_SELF_TEST=pass")
    print(f"PHASE1_PARITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run focused parity checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(Path(args.root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())

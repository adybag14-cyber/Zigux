#!/usr/bin/env python3
"""Guard the current Phase 1 artifact/blocker alignment packet."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

REQUIRED_FILES = (
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_replay_blockers.json",
    "zigux/tests/fixtures/phase1_helpers.json",
)

EXPECTED_ARTIFACT_MARKERS = (
    'print("ARTIFACT_DIFF_SELF_TEST=pass")',
    'print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")',
    'print("ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))',
)

EXPECTED_ARTIFACT_LITERALS = {
    "MODE_CHOICES": ("text", "json", "bytes"),
    "LEGACY_MODE_ALIASES": {"sha256": "bytes"},
    "SELF_TEST_CASES": [
        "text_pass",
        "text_mismatch",
        "json_pass",
        "json_mismatch",
        "json_invalid_expected",
        "json_invalid_actual",
        "json_invalid_both",
        "json_missing_expected",
        "json_missing_actual",
        "json_missing_both",
        "bytes_pass",
        "bytes_drift",
        "text_missing_expected",
        "text_missing_actual",
        "text_missing_both",
        "bytes_missing_expected",
        "bytes_missing_actual",
        "bytes_missing_both",
        "legacy_sha256_alias",
        "missing_mode_value_rejected",
        "missing_positional_arguments_rejected",
        "invalid_mode_rejected",
        "extra_positional_rejected",
    ],
}

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

EXPECTED_FIXTURE_KEYS = (
    "argv_split",
    "bitmap",
    "cmdline",
    "ctype",
    "find_bit",
    "hweight",
    "list_sort",
    "rbtree",
    "slab",
    "str_error_r",
    "string",
    "vsprintf",
    "zalloc",
)

HELPER_TO_FIXTURE = {
    "tools/lib/argv_split.zig": "argv_split",
    "tools/lib/bitmap.zig": "bitmap",
    "tools/lib/cmdline.zig": "cmdline",
    "tools/lib/ctype.zig": "ctype",
    "tools/lib/find_bit.zig": "find_bit",
    "tools/lib/hweight.zig": "hweight",
    "tools/lib/list_sort.zig": "list_sort",
    "tools/lib/rbtree.zig": "rbtree",
    "tools/lib/slab.zig": "slab",
    "tools/lib/str_error_r.zig": "str_error_r",
    "tools/lib/string.zig": "string",
    "tools/lib/vsprintf.zig": "vsprintf",
    "tools/lib/zalloc.zig": "zalloc",
}

EXPECTED_REVIEW_ANCHOR_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_EXACT_REVIEW_FIELDS = {
    "tools/lib/bitmap.zig": {
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
        "partial_xor_review_fields": ("partial_xor_nbits", "partial_xor_masked_values"),
    },
    "tools/lib/find_bit.zig": {
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
        "cached_leftmost_fixture_keys": ("cached_leftmost_return_serials",),
    },
    "tools/lib/list_sort.zig": {
        "parity_fixture_keys": (
            "tri_sorted_keys",
            "tri_sorted_ordinals",
            "bool_sorted_keys",
            "bool_sorted_ordinals",
        ),
    },
    "tools/lib/string.zig": {
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
    },
}

EXPECTED_SHARED_HELPERS = (
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

EXPECTED_DIRECT_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

EXPECTED_MANIFEST_PATH = "zigux/tests/fixtures/phase1_helper_manifest.json"
EXPECTED_REPLAY_BLOCKED_HELPER = "tools/lib/slab.zig"
EXPECTED_REPLAY_BLOCKED_FIXTURE_PREFIX = "slab."
EXPECTED_REPLAY_BLOCKER = {
    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
    "kind": "fixture_mismatch",
    "path": EXPECTED_REPLAY_BLOCKED_HELPER,
    "field": "slab.zero_after_kmalloc",
    "expected": True,
    "actual": False,
    "evidence": (
        "Focused 2026-05-17 scratch replay of `zig build test --build-file "
        "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` because the "
        "committed fixture expects `true` while `tools/lib/slab.zig` still produced `false`."
    ),
}

EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_C_HARNESS_STATE = "blocked"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that "
    "current master no longer ships beside the Phase 1 `.zig` ports."
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def issue(label: str, expected: object, actual: object) -> str:
    return f"{label}:expected={expected!r}:actual={actual!r}"


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_json(root: Path, relative_path: str) -> object:
    return json.loads(read_text(root, relative_path))


def read_python_module(root: Path, relative_path: str) -> ast.Module:
    return ast.parse(read_text(root, relative_path), filename=relative_path)


def find_literal_assignment(module: ast.Module, name: str) -> object | None:
    for node in module.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            return ast.literal_eval(node.value)
    return None


def resolve_field(payload: dict[str, object], dotted: str) -> object | None:
    current: object = payload
    for segment in dotted.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


def validate_review_anchor(helper_path: str, review_anchor: object, fixture: dict[str, object], failures: list[str]) -> None:
    if not isinstance(review_anchor, dict):
        failures.append(issue(f"review_anchor_type:{helper_path}", "dict", type(review_anchor).__name__))
        return
    helper_fixture = fixture.get(HELPER_TO_FIXTURE[helper_path])
    if not isinstance(helper_fixture, dict):
        failures.append(issue(f"fixture_helper_type:{helper_path}", "dict", type(helper_fixture).__name__))
        return
    for field_name, expected in EXPECTED_EXACT_REVIEW_FIELDS.get(helper_path, {}).items():
        actual = tuple(review_anchor.get(field_name, []))
        if actual != expected:
            failures.append(issue(f"review_anchor_exact:{helper_path}:{field_name}", expected, actual))
    for field_name, field_value in review_anchor.items():
        if not field_name.endswith(("_keys", "_fields")):
            continue
        if not isinstance(field_value, list):
            failures.append(issue(f"review_anchor_dynamic_type:{helper_path}:{field_name}", "list", type(field_value).__name__))
            continue
        missing = tuple(item for item in field_value if item not in helper_fixture)
        if missing:
            failures.append(issue(f"review_anchor_dynamic_missing:{helper_path}:{field_name}", (), missing))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.exists():
            failures.append(f"missing_file:{relative_path}")
        elif not path.is_file():
            failures.append(f"required_file_not_regular:{relative_path}")
    if failures:
        return failures

    artifact_module = read_python_module(root, "scripts/zigux/artifact_diff.py")
    artifact_text = read_text(root, "scripts/zigux/artifact_diff.py")
    for marker in EXPECTED_ARTIFACT_MARKERS:
        count = artifact_text.count(marker)
        if count != 1:
            failures.append(issue(f"artifact_marker:{marker}", 1, count))
    for name, expected in EXPECTED_ARTIFACT_LITERALS.items():
        actual = find_literal_assignment(artifact_module, name)
        if actual != expected:
            failures.append(issue(f"artifact_literal:{name}", expected, actual))

    manifest = read_json(root, "zigux/tests/fixtures/phase1_helper_manifest.json")
    blockers = read_json(root, "zigux/tests/fixtures/phase1_replay_blockers.json")
    fixture = read_json(root, "zigux/tests/fixtures/phase1_helpers.json")
    if not isinstance(manifest, dict) or not isinstance(blockers, dict) or not isinstance(fixture, dict):
        return ["packet_type_drift"]

    if manifest.get("phase") != "Phase 1":
        failures.append(issue("manifest_phase", "Phase 1", manifest.get("phase")))
    if manifest.get("status") != "closed":
        failures.append(issue("manifest_status", "closed", manifest.get("status")))
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        failures.append(issue("manifest_helper_count", len(EXPECTED_HELPERS), manifest.get("helper_count")))
    if tuple(manifest.get("helpers", [])) != EXPECTED_HELPERS:
        failures.append(issue("manifest_helpers", EXPECTED_HELPERS, tuple(manifest.get("helpers", []))))
    if tuple(sorted(fixture.keys())) != tuple(sorted(EXPECTED_FIXTURE_KEYS)):
        failures.append(issue("fixture_keys", tuple(sorted(EXPECTED_FIXTURE_KEYS)), tuple(sorted(fixture.keys()))))
    for helper_path, fixture_key in HELPER_TO_FIXTURE.items():
        if fixture_key not in fixture:
            failures.append(f"fixture_key_missing_for_helper:{helper_path}:{fixture_key}")

    manifest_lane = manifest.get("lane_sequencing", {})
    blocker_lane = blockers.get("lane_sequencing", {})
    if tuple(manifest_lane.get("shared_replay_parked_helpers", [])) != EXPECTED_SHARED_HELPERS:
        failures.append(issue("manifest_shared_helpers", EXPECTED_SHARED_HELPERS, tuple(manifest_lane.get("shared_replay_parked_helpers", []))))
    if tuple(manifest_lane.get("direct_anchor_followup_helpers", [])) != EXPECTED_DIRECT_HELPERS:
        failures.append(issue("manifest_direct_helpers", EXPECTED_DIRECT_HELPERS, tuple(manifest_lane.get("direct_anchor_followup_helpers", []))))
    if manifest_lane.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        failures.append(issue("manifest_rule_summary", EXPECTED_RULE_SUMMARY, manifest_lane.get("rule_summary")))
    if manifest_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append(issue("manifest_anti_overlap_rule", EXPECTED_ANTI_OVERLAP_RULE, manifest_lane.get("anti_overlap_rule")))
    if blocker_lane.get("manifest") != EXPECTED_MANIFEST_PATH:
        failures.append(issue("blocker_manifest_path", EXPECTED_MANIFEST_PATH, blocker_lane.get("manifest")))
    if tuple(blocker_lane.get("shared_replay_parked_helpers", [])) != EXPECTED_SHARED_HELPERS:
        failures.append(issue("blocker_shared_helpers", EXPECTED_SHARED_HELPERS, tuple(blocker_lane.get("shared_replay_parked_helpers", []))))
    if tuple(blocker_lane.get("direct_anchor_followup_helpers", [])) != EXPECTED_DIRECT_HELPERS:
        failures.append(issue("blocker_direct_helpers", EXPECTED_DIRECT_HELPERS, tuple(blocker_lane.get("direct_anchor_followup_helpers", []))))
    if blocker_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        failures.append(issue("blocker_shared_count", len(EXPECTED_SHARED_HELPERS), blocker_lane.get("shared_replay_parked_helper_count")))
    if blocker_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        failures.append(issue("blocker_direct_count", len(EXPECTED_DIRECT_HELPERS), blocker_lane.get("direct_anchor_followup_helper_count")))
    if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append(issue("blocker_anti_overlap_rule", EXPECTED_ANTI_OVERLAP_RULE, blocker_lane.get("anti_overlap_rule")))

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        failures.append(issue("review_anchors_type", "dict", type(review_anchors).__name__))
    else:
        actual_keys = tuple(sorted(review_anchors.keys()))
        expected_keys = tuple(sorted(EXPECTED_REVIEW_ANCHOR_HELPERS))
        if actual_keys != expected_keys:
            failures.append(issue("review_anchor_keys", expected_keys, actual_keys))
        for helper_path in EXPECTED_REVIEW_ANCHOR_HELPERS:
            validate_review_anchor(helper_path, review_anchors.get(helper_path), fixture, failures)

    if blockers.get("status") != "parked":
        failures.append(issue("blockers_status", "parked", blockers.get("status")))
    replay = blockers.get("replay", {})
    replay_blockers = replay.get("blockers", [])
    if replay.get("path") != "zigux/tests/phase1_helpers.zig":
        failures.append(issue("replay_path", "zigux/tests/phase1_helpers.zig", replay.get("path")))
    if replay.get("state") != "blocked":
        failures.append(issue("replay_state", "blocked", replay.get("state")))
    if not isinstance(replay_blockers, list) or len(replay_blockers) != 1 or not isinstance(replay_blockers[0], dict):
        failures.append("replay_blocker_shape")
    else:
        first = replay_blockers[0]
        for key, expected in EXPECTED_REPLAY_BLOCKER.items():
            if first.get(key) != expected:
                failures.append(issue(f"replay_blocker:{key}", expected, first.get(key)))
        blocked_helper = first.get("path")
        if blocked_helper not in EXPECTED_SHARED_HELPERS:
            failures.append(issue("replay_blocked_helper_family", EXPECTED_SHARED_HELPERS, blocked_helper))
        blocked_field = first.get("field")
        fixture_key = HELPER_TO_FIXTURE.get(blocked_helper) if isinstance(blocked_helper, str) else None
        if fixture_key is None:
            failures.append(issue("replay_blocked_helper_mapping", "known_helper", blocked_helper))
        elif not isinstance(blocked_field, str) or not blocked_field.startswith(f"{fixture_key}."):
            failures.append(issue("replay_blocked_field_prefix", f"{fixture_key}.", blocked_field))
        if resolve_field(fixture, EXPECTED_REPLAY_BLOCKER["field"]) != EXPECTED_REPLAY_BLOCKER["expected"]:
            failures.append(issue("fixture_blocked_field_value", EXPECTED_REPLAY_BLOCKER["expected"], resolve_field(fixture, EXPECTED_REPLAY_BLOCKER["field"])))

    c_harness = blockers.get("c_harness", {})
    if c_harness.get("path") != EXPECTED_C_HARNESS_PATH:
        failures.append(issue("c_harness_path", EXPECTED_C_HARNESS_PATH, c_harness.get("path")))
    if c_harness.get("state") != EXPECTED_C_HARNESS_STATE:
        failures.append(issue("c_harness_state", EXPECTED_C_HARNESS_STATE, c_harness.get("state")))
    if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
        failures.append(issue("c_harness_reason", EXPECTED_C_HARNESS_REASON, c_harness.get("reason")))
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        failures.append(issue("c_harness_helper_count", len(EXPECTED_HELPERS), c_harness.get("helper_count")))
    if tuple(c_harness.get("helpers", [])) != EXPECTED_HELPERS:
        failures.append(issue("c_harness_helpers", EXPECTED_HELPERS, tuple(c_harness.get("helpers", []))))
    if c_harness.get("blocker_id") != EXPECTED_C_HARNESS_BLOCKER_ID:
        failures.append(issue("c_harness_blocker_id", EXPECTED_C_HARNESS_BLOCKER_ID, c_harness.get("blocker_id")))
    if (root / EXPECTED_C_HARNESS_PATH).exists():
        failures.append(issue("c_harness_present", False, True))
    return failures


def sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": {
            "tools/lib/argv_split.zig": {"next_safe_step_note": "ok"},
            "tools/lib/bitmap.zig": {
                "parity_fixture_keys": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/bitmap.zig"]["parity_fixture_keys"]),
                "partial_xor_review_fields": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/bitmap.zig"]["partial_xor_review_fields"]),
                "shared_logical_fixture_keys": ["weight", "and_result"],
                "shared_range_fixture_keys": ["range_after_set", "empty_after_zero"],
                "next_safe_step_note": "ok",
            },
            "tools/lib/find_bit.zig": {
                "tail_clamp_fixture_keys": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/find_bit.zig"]["tail_clamp_fixture_keys"]),
                "tail_inclusive_boundary_fixture_keys": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/find_bit.zig"]["tail_inclusive_boundary_fixture_keys"]),
                "next_safe_step_note": "ok",
            },
            "tools/lib/list_sort.zig": {
                "parity_fixture_keys": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/list_sort.zig"]["parity_fixture_keys"]),
                "next_safe_step_note": "ok",
            },
            "tools/lib/rbtree.zig": {
                "parity_fixture_keys": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/rbtree.zig"]["parity_fixture_keys"]),
                "cached_leftmost_fixture_keys": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/rbtree.zig"]["cached_leftmost_fixture_keys"]),
                "traversal_replay_keys": ["empty_root", "insert_order"],
                "duplicate_search_replay_keys": ["find_found_key", "next_match_terminal_null"],
                "next_safe_step_note": "ok",
            },
            "tools/lib/string.zig": {
                "parity_fixture_keys": list(EXPECTED_EXACT_REVIEW_FIELDS["tools/lib/string.zig"]["parity_fixture_keys"]),
                "next_safe_step_note": "ok",
            },
        },
    }


def sample_blockers() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": EXPECTED_MANIFEST_PATH,
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_HELPERS),
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
            "blockers": [dict(EXPECTED_REPLAY_BLOCKER)],
        },
        "c_harness": {
            "path": EXPECTED_C_HARNESS_PATH,
            "state": EXPECTED_C_HARNESS_STATE,
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }


def sample_fixture() -> dict[str, object]:
    return {
        "argv_split": {"argc": 3},
        "bitmap": {
            "alloc_words": 2,
            "zalloc_words": 2,
            "zalloc_values": [0, 0],
            "scnprintf": "x",
            "truncated_scnprintf_len": 1,
            "truncated_scnprintf": "x",
            "terminator_only_scnprintf_len": 0,
            "terminator_only_nul": 0,
            "zero_length_scnprintf_len": 0,
            "partial_xor_nbits": 4,
            "partial_xor_masked_values": [14],
            "weight": 3,
            "and_result": True,
            "range_after_set": [1],
            "empty_after_zero": True,
        },
        "cmdline": {"decimal_k": {"value": 1}},
        "ctype": {"mask_A": 65},
        "find_bit": {
            "tail_clamped_first": 1,
            "tail_clamped_next": 2,
            "tail_zero_clamped_first": 3,
            "tail_zero_clamped_next": 4,
            "tail_and_clamped_first": 5,
            "tail_and_clamped_next": 6,
            "tail_clamped_last": 7,
            "tail_clamped_empty_last": 8,
            "tail_inclusive_boundary_next": 9,
            "tail_inclusive_boundary_zero": 10,
            "tail_inclusive_boundary_and": 11,
        },
        "hweight": {"w8": 4},
        "list_sort": {
            "tri_sorted_keys": [1],
            "tri_sorted_ordinals": [0],
            "bool_sorted_keys": [1],
            "bool_sorted_ordinals": [0],
        },
        "rbtree": {
            "empty_root": True,
            "insert_order": [1],
            "reverse_order": [1],
            "replace_order": [1],
            "erase_init_order": [1],
            "postorder_count": 1,
            "erase_init_node_empty": True,
            "cleared_node_empty": True,
            "find_found_key": 1,
            "find_missing": True,
            "find_first_serial": 0,
            "next_match_serials": [0],
            "match_iterator_serials": [0],
            "next_match_terminal_null": True,
            "cached_leftmost_return_serials": [0],
        },
        "slab": {"zero_after_kmalloc": True},
        "str_error_r": {"enoent": "ok"},
        "string": {
            "strtobool_y": True,
            "strtobool_on": True,
            "strtobool_zero": False,
            "strtobool_off": False,
            "strtobool_invalid": 1,
            "strlcpy_len": 1,
            "strlcpy_buffer": "x",
            "skip_spaces": "x",
            "trim_spaces": "x",
            "remove_spaces": "x",
            "replace_char": "x",
            "replace_char_end": 1,
            "replace_char_cstr_end": 1,
            "replace_char_cstr_bytes": [0],
            "memchr_inv_index": 0,
            "memchr_inv_none": True,
        },
        "vsprintf": {"scnprintf_text": "x"},
        "zalloc": {"zeroed": True},
    }


def build_sample_root(root: Path) -> None:
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests/fixtures").mkdir(parents=True, exist_ok=True)
    artifact_lines = [
        "#!/usr/bin/env python3",
        'MODE_CHOICES = ("text", "json", "bytes")',
        'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
        "SELF_TEST_CASES = [",
    ]
    artifact_lines.extend(f'    "{case}",' for case in EXPECTED_ARTIFACT_LITERALS["SELF_TEST_CASES"])
    artifact_lines.extend(
        [
            "]",
            'print("ARTIFACT_DIFF_SELF_TEST=pass")',
            'print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")',
            'print("ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))',
            "",
        ]
    )
    (root / "scripts/zigux/artifact_diff.py").write_text("\n".join(artifact_lines), encoding="utf-8")
    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(json.dumps(sample_manifest(), indent=2) + "\n", encoding="utf-8")
    (root / "zigux/tests/fixtures/phase1_replay_blockers.json").write_text(json.dumps(sample_blockers(), indent=2) + "\n", encoding="utf-8")
    (root / "zigux/tests/fixtures/phase1_helpers.json").write_text(json.dumps(sample_fixture(), separators=(",", ":")) + "\n", encoding="utf-8")


def mutate_json(path: Path, fn) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    fn(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = (
        ("success", None),
        ("missing_file", lambda root: (root / "scripts/zigux/artifact_diff.py").unlink()),
        ("artifact_case_drift", lambda root: (root / "scripts/zigux/artifact_diff.py").write_text("#!/usr/bin/env python3\nSELF_TEST_CASES=[]\n", encoding="utf-8")),
        ("review_anchor_key_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", lambda data: data["review_anchors"].pop("tools/lib/string.zig"))),
        ("dynamic_key_type_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", lambda data: data["review_anchors"]["tools/lib/rbtree.zig"].__setitem__("traversal_replay_keys", "drift"))),
        ("dynamic_key_missing_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", lambda data: data["review_anchors"]["tools/lib/rbtree.zig"].__setitem__("duplicate_search_replay_keys", ["missing"]))),
        ("blocker_manifest_pointer_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["lane_sequencing"].__setitem__("manifest", "drift.json"))),
        ("replay_blocked_helper_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["replay"]["blockers"][0].__setitem__("path", "tools/lib/bitmap.zig"))),
        ("c_harness_blocker_id_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["c_harness"].__setitem__("blocker_id", "drift"))),
        ("fixture_key_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helpers.json", lambda data: data["slab"].__setitem__("zero_after_kmalloc", False))),
        ("blocker_reason_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["c_harness"].__setitem__("reason", "drift"))),
    )
    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="lane09_alignment_") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutation is not None:
                mutation(root)
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1
    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_FIXTURE_HELPER_COUNT={len(EXPECTED_FIXTURE_KEYS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_BLOCKED_FIELD={EXPECTED_REPLAY_BLOCKER['field']}")
    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_C_HARNESS_PRESENT=False")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_REVIEW_ANCHOR_HELPER_COUNT={len(EXPECTED_REVIEW_ANCHOR_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_ARTIFACT_SELF_TEST_CASE_COUNT={len(EXPECTED_ARTIFACT_LITERALS['SELF_TEST_CASES'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

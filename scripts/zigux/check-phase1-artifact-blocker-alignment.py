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

EXPECTED_ARTIFACT_LITERAL_ASSIGNMENTS = {
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

EXPECTED_HELPER_FIXTURE_MAP = {
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

EXPECTED_REVIEW_ANCHOR_FIXTURE_FIELDS = {
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
        "partial_xor_review_fields": (
            "partial_xor_nbits",
            "partial_xor_masked_values",
        ),
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
        "cached_leftmost_fixture_keys": (
            "cached_leftmost_return_serials",
        ),
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

EXPECTED_MANIFEST_PATH = "zigux/tests/fixtures/phase1_helper_manifest.json"
EXPECTED_FIXTURE_PATH = "zigux/tests/fixtures/phase1_helpers.json"
EXPECTED_REPLAY_PATH = "zigux/tests/phase1_helpers.zig"
EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_KIND = "fixture_mismatch"
EXPECTED_REPLAY_BLOCKER_SOURCE_PATH = "tools/lib/slab.zig"
EXPECTED_REPLAY_BLOCKER_FIELD = "slab.zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_EVIDENCE = (
    "Focused 2026-05-17 scratch replay of `zig build test --build-file "
    "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` because the "
    "committed fixture expects `true` while `tools/lib/slab.zig` still produced `false`."
)
EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that "
    "current master no longer ships beside the Phase 1 `.zig` ports."
)
EXPECTED_C_HARNESS_PRESENT = False

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


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def issue(label: str, expected: object, actual: object) -> str:
    return f"{label}:expected={expected!r}:actual={actual!r}"


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_json(root: Path, relative_path: str, *, failures: list[str], label: str) -> object | None:
    try:
        text = read_text(root, relative_path)
    except UnicodeDecodeError as exc:
        failures.append(f"{label}_invalid_utf8:{relative_path}:{exc.start + 1}:{exc.reason}")
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        failures.append(f"{label}_invalid_json:{relative_path}:{exc.lineno}:{exc.colno}:{exc.msg}")
        return None


def read_python_module(root: Path, relative_path: str, *, failures: list[str]) -> ast.Module | None:
    try:
        text = read_text(root, relative_path)
    except UnicodeDecodeError as exc:
        failures.append(f"artifact_invalid_utf8:{relative_path}:{exc.start + 1}:{exc.reason}")
        return None
    try:
        return ast.parse(text, filename=relative_path)
    except SyntaxError as exc:
        failures.append(f"artifact_invalid_python:{relative_path}:{exc.lineno}:{exc.offset}:{exc.msg}")
        return None


def find_literal_assignment(module: ast.Module, name: str) -> object | None:
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            try:
                return ast.literal_eval(node.value)
            except ValueError:
                return None
    return None


def resolve_field_path(payload: dict[str, object], field_path: str) -> object | None:
    current: object = payload
    for segment in field_path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


def validate_fixture_key_fields(
    *,
    helper_path: str,
    fixture_key: str,
    review_anchor: object,
    fixture: dict[str, object],
    failures: list[str],
) -> None:
    if not isinstance(review_anchor, dict):
        failures.append(issue(f"review_anchor_type:{helper_path}", "dict", type(review_anchor).__name__))
        return
    helper_fixture = fixture.get(fixture_key)
    if not isinstance(helper_fixture, dict):
        failures.append(issue(f"fixture_helper_type:{helper_path}", "dict", type(helper_fixture).__name__))
        return

    for field_name, expected_keys in EXPECTED_REVIEW_ANCHOR_FIXTURE_FIELDS.get(helper_path, {}).items():
        actual_keys = tuple(review_anchor.get(field_name, []))
        if actual_keys != expected_keys:
            failures.append(issue(f"review_anchor_fixture_keys:{helper_path}:{field_name}", expected_keys, actual_keys))
            continue
        missing = tuple(key for key in expected_keys if key not in helper_fixture)
        if missing:
            failures.append(
                issue(
                    f"review_anchor_fixture_field_presence:{helper_path}:{field_name}",
                    (),
                    missing,
                )
            )


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

    artifact_path = "scripts/zigux/artifact_diff.py"
    artifact_text = read_text(root, artifact_path)
    artifact_module = read_python_module(root, artifact_path, failures=failures)
    for marker in EXPECTED_ARTIFACT_MARKERS:
        count = artifact_text.count(marker)
        if count != 1:
            failures.append(issue(f"artifact_marker:{marker}", 1, count))
    if artifact_module is not None:
        for name, expected in EXPECTED_ARTIFACT_LITERAL_ASSIGNMENTS.items():
            actual = find_literal_assignment(artifact_module, name)
            if actual != expected:
                failures.append(issue(f"artifact_literal:{name}", expected, actual))

    manifest = read_json(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        failures=failures,
        label="manifest",
    )
    blockers = read_json(
        root,
        "zigux/tests/fixtures/phase1_replay_blockers.json",
        failures=failures,
        label="blockers",
    )
    fixture = read_json(
        root,
        "zigux/tests/fixtures/phase1_helpers.json",
        failures=failures,
        label="fixture",
    )
    if manifest is None or blockers is None or fixture is None:
        return failures
    if not isinstance(manifest, dict):
        failures.append(issue("manifest_type", "dict", type(manifest).__name__))
        return failures
    if not isinstance(blockers, dict):
        failures.append(issue("blockers_type", "dict", type(blockers).__name__))
        return failures
    if not isinstance(fixture, dict):
        failures.append(issue("fixture_type", "dict", type(fixture).__name__))
        return failures

    for key, expected in (
        ("phase", "Phase 1"),
        ("status", "closed"),
        ("helper_count", len(EXPECTED_HELPERS)),
    ):
        actual = manifest.get(key)
        if actual != expected:
            failures.append(issue(f"manifest:{key}", expected, actual))

    manifest_helpers = tuple(manifest.get("helpers", []))
    if manifest_helpers != EXPECTED_HELPERS:
        failures.append(issue("manifest_helpers", EXPECTED_HELPERS, manifest_helpers))

    fixture_keys = tuple(sorted(fixture.keys()))
    if fixture_keys != tuple(sorted(EXPECTED_FIXTURE_KEYS)):
        failures.append(issue("fixture_keys", tuple(sorted(EXPECTED_FIXTURE_KEYS)), fixture_keys))

    for helper_path, fixture_key in EXPECTED_HELPER_FIXTURE_MAP.items():
        if helper_path not in manifest_helpers:
            failures.append(f"helper_missing_from_manifest_for_fixture:{helper_path}")
        if fixture_key not in fixture:
            failures.append(f"fixture_key_missing_for_helper:{helper_path}:{fixture_key}")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        failures.append(issue("review_anchors_type", "dict", type(review_anchors).__name__))
        return failures
    review_anchor_keys = tuple(sorted(review_anchors.keys()))
    expected_review_anchor_keys = tuple(sorted(EXPECTED_HELPER_FIXTURE_MAP.keys()))
    if review_anchor_keys != expected_review_anchor_keys:
        failures.append(issue("review_anchor_keys", expected_review_anchor_keys, review_anchor_keys))
    for helper_path, fixture_key in EXPECTED_HELPER_FIXTURE_MAP.items():
        validate_fixture_key_fields(
            helper_path=helper_path,
            fixture_key=fixture_key,
            review_anchor=review_anchors.get(helper_path),
            fixture=fixture,
            failures=failures,
        )

    manifest_lane = manifest.get("lane_sequencing")
    blocker_lane = blockers.get("lane_sequencing")
    replay = blockers.get("replay")
    c_harness = blockers.get("c_harness")

    if not isinstance(manifest_lane, dict):
        failures.append(issue("manifest_lane_type", "dict", type(manifest_lane).__name__))
        return failures
    if not isinstance(blocker_lane, dict):
        failures.append(issue("blocker_lane_type", "dict", type(blocker_lane).__name__))
        return failures
    if not isinstance(replay, dict):
        failures.append(issue("replay_type", "dict", type(replay).__name__))
        return failures
    if not isinstance(c_harness, dict):
        failures.append(issue("c_harness_type", "dict", type(c_harness).__name__))
        return failures

    manifest_shared = tuple(manifest_lane.get("shared_replay_parked_helpers", []))
    manifest_direct = tuple(manifest_lane.get("direct_anchor_followup_helpers", []))
    blocker_shared = tuple(blocker_lane.get("shared_replay_parked_helpers", []))
    blocker_direct = tuple(blocker_lane.get("direct_anchor_followup_helpers", []))

    if manifest_shared != EXPECTED_SHARED_HELPERS:
        failures.append(issue("manifest_shared_helpers", EXPECTED_SHARED_HELPERS, manifest_shared))
    if manifest_direct != EXPECTED_DIRECT_HELPERS:
        failures.append(issue("manifest_direct_helpers", EXPECTED_DIRECT_HELPERS, manifest_direct))
    if blocker_shared != EXPECTED_SHARED_HELPERS:
        failures.append(issue("blocker_shared_helpers", EXPECTED_SHARED_HELPERS, blocker_shared))
    if blocker_direct != EXPECTED_DIRECT_HELPERS:
        failures.append(issue("blocker_direct_helpers", EXPECTED_DIRECT_HELPERS, blocker_direct))
    if manifest_lane.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        failures.append(
            issue("manifest_rule_summary", EXPECTED_RULE_SUMMARY, manifest_lane.get("rule_summary"))
        )

    if manifest_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append(
            issue(
                "manifest_anti_overlap_rule",
                EXPECTED_ANTI_OVERLAP_RULE,
                manifest_lane.get("anti_overlap_rule"),
            )
        )
    if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append(
            issue(
                "blocker_anti_overlap_rule",
                EXPECTED_ANTI_OVERLAP_RULE,
                blocker_lane.get("anti_overlap_rule"),
            )
        )

    if blocker_lane.get("manifest") != EXPECTED_MANIFEST_PATH:
        failures.append(issue("blocker_manifest_path", EXPECTED_MANIFEST_PATH, blocker_lane.get("manifest")))
    if blocker_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        failures.append(
            issue(
                "blocker_shared_count",
                len(EXPECTED_SHARED_HELPERS),
                blocker_lane.get("shared_replay_parked_helper_count"),
            )
        )
    if blocker_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        failures.append(
            issue(
                "blocker_direct_count",
                len(EXPECTED_DIRECT_HELPERS),
                blocker_lane.get("direct_anchor_followup_helper_count"),
            )
        )

    if set(manifest_shared).intersection(manifest_direct):
        failures.append("manifest_helper_sets_overlap")
    if set(blocker_shared).intersection(blocker_direct):
        failures.append("blocker_helper_sets_overlap")
    if tuple(sorted(manifest_shared + manifest_direct)) != tuple(sorted(blocker_shared + blocker_direct)):
        failures.append("manifest_and_blocker_helper_sets_differ")

    if blockers.get("status") != "parked":
        failures.append(issue("blockers_status", "parked", blockers.get("status")))

    if replay.get("path") != EXPECTED_REPLAY_PATH:
        failures.append(issue("replay_path", EXPECTED_REPLAY_PATH, replay.get("path")))
    if replay.get("state") != "blocked":
        failures.append(issue("replay_state", "blocked", replay.get("state")))
    replay_blockers = replay.get("blockers")
    if not isinstance(replay_blockers, list) or not replay_blockers:
        failures.append(issue("replay_blockers", "non-empty list", replay_blockers))
    else:
        if len(replay_blockers) != 1:
            failures.append(issue("replay_blocker_count", 1, len(replay_blockers)))
        first = replay_blockers[0]
        if not isinstance(first, dict):
            failures.append(issue("replay_first_type", "dict", type(first).__name__))
        else:
            if first.get("id") != EXPECTED_REPLAY_BLOCKER_ID:
                failures.append(issue("replay_blocker_id", EXPECTED_REPLAY_BLOCKER_ID, first.get("id")))
            if first.get("kind") != EXPECTED_REPLAY_BLOCKER_KIND:
                failures.append(issue("replay_blocker_kind", EXPECTED_REPLAY_BLOCKER_KIND, first.get("kind")))
            if first.get("path") != EXPECTED_REPLAY_BLOCKER_SOURCE_PATH:
                failures.append(
                    issue("replay_blocker_source_path", EXPECTED_REPLAY_BLOCKER_SOURCE_PATH, first.get("path"))
                )
            if first.get("field") != EXPECTED_REPLAY_BLOCKER_FIELD:
                failures.append(issue("replay_blocker_field", EXPECTED_REPLAY_BLOCKER_FIELD, first.get("field")))
            if first.get("expected") is not True:
                failures.append(issue("replay_blocker_expected", True, first.get("expected")))
            if first.get("actual") is not False:
                failures.append(issue("replay_blocker_actual", False, first.get("actual")))
            if first.get("evidence") != EXPECTED_REPLAY_BLOCKER_EVIDENCE:
                failures.append(
                    issue("replay_blocker_evidence", EXPECTED_REPLAY_BLOCKER_EVIDENCE, first.get("evidence"))
                )

            expected_fixture_value = first.get("expected")
            fixture_value = resolve_field_path(fixture, EXPECTED_REPLAY_BLOCKER_FIELD)
            if fixture_value != expected_fixture_value:
                failures.append(issue("fixture_blocked_field_value", expected_fixture_value, fixture_value))
            if replay.get("fixture") not in (None, EXPECTED_FIXTURE_PATH):
                failures.append(issue("replay_fixture_path", EXPECTED_FIXTURE_PATH, replay.get("fixture")))

    if c_harness.get("path") != EXPECTED_C_HARNESS_PATH:
        failures.append(issue("c_harness_path", EXPECTED_C_HARNESS_PATH, c_harness.get("path")))
    if c_harness.get("state") != "blocked":
        failures.append(issue("c_harness_state", "blocked", c_harness.get("state")))
    if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
        failures.append(issue("c_harness_reason", EXPECTED_C_HARNESS_REASON, c_harness.get("reason")))
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        failures.append(issue("c_harness_helper_count", len(EXPECTED_HELPERS), c_harness.get("helper_count")))
    c_harness_helpers = tuple(c_harness.get("helpers", []))
    if c_harness_helpers != EXPECTED_HELPERS:
        failures.append(issue("c_harness_helpers", EXPECTED_HELPERS, c_harness_helpers))
    if c_harness.get("blocker_id") != EXPECTED_C_HARNESS_BLOCKER_ID:
        failures.append(issue("c_harness_blocker_id", EXPECTED_C_HARNESS_BLOCKER_ID, c_harness.get("blocker_id")))

    c_harness_present = (root / EXPECTED_C_HARNESS_PATH).exists()
    if c_harness_present != EXPECTED_C_HARNESS_PRESENT:
        failures.append(issue("c_harness_present", EXPECTED_C_HARNESS_PRESENT, c_harness_present))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def sample_artifact_diff() -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            'MODE_CHOICES = ("text", "json", "bytes")',
            'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
            "SELF_TEST_CASES = [",
            '    "text_pass",',
            '    "text_mismatch",',
            '    "json_pass",',
            '    "json_mismatch",',
            '    "json_invalid_expected",',
            '    "json_invalid_actual",',
            '    "json_invalid_both",',
            '    "json_missing_expected",',
            '    "json_missing_actual",',
            '    "json_missing_both",',
            '    "bytes_pass",',
            '    "bytes_drift",',
            '    "text_missing_expected",',
            '    "text_missing_actual",',
            '    "text_missing_both",',
            '    "bytes_missing_expected",',
            '    "bytes_missing_actual",',
            '    "bytes_missing_both",',
            '    "legacy_sha256_alias",',
            '    "missing_mode_value_rejected",',
            '    "missing_positional_arguments_rejected",',
            '    "invalid_mode_rejected",',
            '    "extra_positional_rejected",',
            "]",
            'print("ARTIFACT_DIFF_SELF_TEST=pass")',
            'print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")',
            'print("ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))',
            "",
        )
    )


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
            helper_path: fields
            for helper_path, fields in sample_review_anchors().items()
        },
    }


def sample_review_anchors() -> dict[str, dict[str, object]]:
    anchors: dict[str, dict[str, object]] = {}
    for helper_path in EXPECTED_HELPERS:
        fixture_name = EXPECTED_HELPER_FIXTURE_MAP[helper_path]
        anchor = {
            "next_safe_step_note": f"Keep {fixture_name} bounded to its current manifest packet unless fixture drift appears.",
        }
        for field_name, expected_keys in EXPECTED_REVIEW_ANCHOR_FIXTURE_FIELDS.get(helper_path, {}).items():
            anchor[field_name] = list(expected_keys)
        anchors[helper_path] = anchor
    return anchors


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
            "path": EXPECTED_REPLAY_PATH,
            "state": "blocked",
            "fixture": EXPECTED_FIXTURE_PATH,
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_ID,
                    "kind": EXPECTED_REPLAY_BLOCKER_KIND,
                    "path": EXPECTED_REPLAY_BLOCKER_SOURCE_PATH,
                    "field": EXPECTED_REPLAY_BLOCKER_FIELD,
                    "expected": True,
                    "actual": False,
                    "evidence": EXPECTED_REPLAY_BLOCKER_EVIDENCE,
                }
            ],
        },
        "c_harness": {
            "path": EXPECTED_C_HARNESS_PATH,
            "state": "blocked",
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }


def sample_fixture() -> dict[str, object]:
    return {
        "find_bit": {
            "bits_per_long": 64,
            "first": 5,
            "next_after_6": 67,
            "next_after_word": 135,
            "first_zero": 3,
            "next_zero": 68,
            "first_and": 9,
            "next_and": 66,
            "last": 135,
            "inclusive_boundary_next": 63,
            "inclusive_boundary_zero": 63,
            "inclusive_boundary_and": 63,
            "tail_inclusive_boundary_next": 68,
            "tail_inclusive_boundary_zero": 68,
            "tail_inclusive_boundary_and": 68,
            "past_nbits_next": 7,
            "past_nbits_zero": 7,
            "past_nbits_and": 7,
            "tail_clamped_first": 67,
            "tail_clamped_next": 69,
            "tail_zero_clamped_first": 69,
            "tail_zero_clamped_next": 69,
            "tail_and_clamped_first": 67,
            "tail_and_clamped_next": 69,
            "tail_clamped_last": 67,
            "tail_clamped_empty_last": 69,
        },
        "bitmap": {
            "weight": 3,
            "scnprintf": "1-3,7,10-11",
            "truncated_scnprintf_len": 7,
            "truncated_scnprintf": "1-3,7,1",
            "terminator_only_scnprintf_len": 0,
            "terminator_only_nul": 0,
            "zero_length_scnprintf_len": 0,
            "alloc_words": 2,
            "zalloc_words": 2,
            "zalloc_values": [0, 0],
            "copy_values": [18446744073709551615, 18446744073709551615],
            "copy_clear_tail_values": [18446744073709551615, 31],
            "copy_and_extend_values": [18446744073709551615, 31, 0],
            "and_result": True,
            "and_values": [10, 0],
            "andnot_result": True,
            "andnot_values": [4, 0],
            "or_values": [14, 0],
            "xor_values": [4, 0],
            "partial_xor_nbits": 4,
            "partial_xor_masked_values": [14],
            "equal": True,
            "intersects": True,
            "subset": True,
            "range_after_set": [14, 12, 0],
            "range_after_clear": [0, 0, 0],
            "full_after_fill": True,
            "empty_after_zero": True,
        },
        "string": {
            "strtobool_y": True,
            "strtobool_on": True,
            "strtobool_zero": False,
            "strtobool_off": False,
            "strtobool_invalid": 184,
            "strlcpy_len": 5,
            "strlcpy_buffer": "hel",
            "skip_spaces": "hello",
            "trim_spaces": "hi",
            "remove_spaces": "abc",
            "replace_char": "a_b",
            "replace_char_end": 3,
            "replace_char_cstr_end": 2,
            "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
            "memchr_inv_index": 4,
            "memchr_inv_none": True,
        },
        "rbtree": {
            "empty_root": True,
            "insert_order": [5, 10, 15, 20, 25],
            "reverse_order": [25, 20, 15, 10, 5],
            "replace_order": [5, 10, 15, 25],
            "erase_init_order": [5, 15, 25],
            "postorder_count": 3,
            "erase_init_node_empty": True,
            "cleared_node_empty": True,
            "find_found_key": 15,
            "find_missing": True,
            "find_first_serial": 0,
            "next_match_serials": [0, 2, 4],
            "match_iterator_serials": [0, 2, 4],
            "cached_leftmost_return_serials": [0, -1, 2, -1],
            "next_match_terminal_null": True,
        },
        "argv_split": {"argc": 3, "argv": ["alpha", "beta", "gamma"], "blank_argc": 0},
        "cmdline": {
            "decimal_k": {"value": 65536, "rest": " rest"},
            "hex_m": {"value": 33554432, "rest": ""},
            "octal_k": {"value": 8192, "rest": ""},
            "invalid": {"value": 0, "rest": "xyz"},
        },
        "ctype": {
            "mask_A": 65,
            "mask_a": 66,
            "mask_space": 160,
            "isalnum_A": True,
            "isalpha_z": True,
            "isdigit_7": True,
            "isspace_tab": True,
            "isxdigit_f": True,
            "ispunct_bang": True,
            "tolower_A": 97,
            "toupper_z": 90,
            "isodigit_7": True,
            "isodigit_8": False,
        },
        "hweight": {"w8": 4, "w16": 8, "w32": 16, "w64": 32, "wlong": 8},
        "list_sort": {
            "tri_sorted_keys": [1, 1, 2, 3, 3],
            "tri_sorted_ordinals": [1, 3, 0, 2, 4],
            "bool_sorted_keys": [1, 1, 2, 3, 3],
            "bool_sorted_ordinals": [1, 3, 0, 2, 4],
        },
        "zalloc": {
            "zeroed": True,
            "freed_is_null": True,
            "value_zeroed": True,
            "value_freed_is_null": True,
        },
        "str_error_r": {
            "enoent": "No such file or directory",
            "unknown": "INTERNAL ERROR: strerror_r(4096, [buf], 64)=22",
        },
        "slab": {
            "null_without_reclaim": True,
            "alloc_count_after_kmalloc": 1,
            "zero_after_kmalloc": True,
            "alloc_count_after_kmalloc_free": 0,
            "array_zeroed": True,
            "alloc_count_after_kmalloc_array": 1,
            "alloc_count_after_kmalloc_array_free": 0,
            "slab_is_available": True,
        },
        "vsprintf": {
            "scnprintf_text": "zigux:7",
            "scnprintf_len": 7,
            "pad_text": "id=7    ",
            "pad_len": 7,
        },
    }


def build_sample_root(root: Path) -> None:
    write_text(root, "scripts/zigux/artifact_diff.py", sample_artifact_diff())
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(sample_manifest(), indent=2) + "\n",
    )
    write_text(
        root,
        "zigux/tests/fixtures/phase1_replay_blockers.json",
        json.dumps(sample_blockers(), indent=2) + "\n",
    )
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helpers.json",
        json.dumps(sample_fixture(), separators=(",", ":")) + "\n",
    )


def run_self_test() -> int:
    cases = (
        ("success", None),
        ("missing_required_file", lambda root: (root / "scripts/zigux/artifact_diff.py").unlink()),
        (
            "missing_artifact_marker",
            lambda root: write_text(root, "scripts/zigux/artifact_diff.py", "#!/usr/bin/env python3\n"),
        ),
        (
            "artifact_self_test_cases_drift",
            lambda root: write_text(
                root,
                "scripts/zigux/artifact_diff.py",
                sample_artifact_diff().replace('"extra_positional_rejected",', '"drifted_case",', 1),
            ),
        ),
        (
            "artifact_legacy_alias_drift",
            lambda root: write_text(
                root,
                "scripts/zigux/artifact_diff.py",
                sample_artifact_diff().replace('{"sha256": "bytes"}', '{"sha1": "bytes"}', 1),
            ),
        ),
        (
            "manifest_helpers_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data.__setitem__("helpers", ["drift"]),
            ),
        ),
        (
            "manifest_rule_summary_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["lane_sequencing"].__setitem__("rule_summary", "drift"),
            ),
        ),
        (
            "manifest_shared_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["lane_sequencing"].__setitem__("shared_replay_parked_helpers", ["drift"]),
            ),
        ),
        (
            "review_anchor_keys_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["review_anchors"].pop("tools/lib/string.zig"),
            ),
        ),
        (
            "review_anchor_fixture_keys_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["review_anchors"]["tools/lib/bitmap.zig"].__setitem__(
                    "parity_fixture_keys", ["drift"]
                ),
            ),
        ),
        (
            "review_anchor_missing_fixture_field",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helpers.json",
                lambda data: data["find_bit"].pop("tail_clamped_last"),
            ),
        ),
        (
            "fixture_keys_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helpers.json",
                lambda data: data.__setitem__("unexpected", True),
            ),
        ),
        (
            "fixture_blocked_field_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helpers.json",
                lambda data: data["slab"].__setitem__("zero_after_kmalloc", False),
            ),
        ),
        (
            "blocker_direct_count_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["lane_sequencing"].__setitem__("direct_anchor_followup_helper_count", 99),
            ),
        ),
        (
            "blocker_id_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["replay"]["blockers"][0].__setitem__("id", "drift"),
            ),
        ),
        (
            "replay_evidence_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["replay"]["blockers"][0].__setitem__("evidence", "drift"),
            ),
        ),
        (
            "c_harness_reason_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["c_harness"].__setitem__("reason", "drift"),
            ),
        ),
        (
            "c_harness_present_drift",
            lambda root: write_text(root, EXPECTED_C_HARNESS_PATH, "legacy harness\n"),
        ),
        (
            "helper_set_overlap",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["lane_sequencing"]["direct_anchor_followup_helpers"].__setitem__(
                    0, EXPECTED_SHARED_HELPERS[0]
                ),
            ),
        ),
        (
            "blockers_invalid_json",
            lambda root: write_text(root, "zigux/tests/fixtures/phase1_replay_blockers.json", "{\n"),
        ),
        (
            "fixture_invalid_json",
            lambda root: write_text(root, "zigux/tests/fixtures/phase1_helpers.json", "{\n"),
        ),
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="lane09_artifact_blocker_alignment_") as tmpdir:
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


def _mutate_json(path: Path, mutation) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutation(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
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
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_BLOCKED_FIELD={EXPECTED_REPLAY_BLOCKER_FIELD}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_C_HARNESS_PRESENT={EXPECTED_C_HARNESS_PRESENT}")
    print(
        "PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_REVIEW_ANCHOR_HELPER_COUNT="
        f"{len(EXPECTED_HELPER_FIXTURE_MAP)}"
    )
    print(
        "PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_ARTIFACT_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_ARTIFACT_LITERAL_ASSIGNMENTS['SELF_TEST_CASES'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

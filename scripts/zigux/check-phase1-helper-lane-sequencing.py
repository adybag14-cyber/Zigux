#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

EXPECTED_DIRECT_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

LIST_SORT_HELPER = "tools/lib/list_sort.zig"

EXPECTED_LIST_SORT_HELPER_TEST_ANCHORS = [
    'test "list sort keeps stable ordering for tri-state comparator"',
    'test "list sort accepts boolean-style comparator"',
    'test "list sort honors comparator context"',
    'test "list sort can reorder the same circular list twice"',
    'test "list sort keeps reverse links aligned after reordering"',
    'test "list sort preserves sorted unique input"',
    'test "list sort preserves stable bucket order across parity groups"',
    'test "list sort preserves stable modulo bucket order across a longer merge path"',
    'test "list sort preserves input order when every comparison ties"',
    'test "list sort handles empty and singleton lists"',
]

EXPECTED_LIST_SORT_REVIEW_PACKET_SUMMARY = (
    "keep list_sort parked in the shared-replay helper family for fixture ownership, "
    "but reread the helper-local proof packet before reopening the lane: current "
    "master already names direct witnesses for comparator-context ordering, repeat-sort "
    "circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket "
    "stability, longer modulo-bucket stability, all-ties stability, and empty-or-singleton "
    "handling beside the committed parity keys"
)

EXPECTED_LIST_SORT_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep list_sort parked unless a fresh reread finds drift "
    "in the committed `tri_sorted_*` or `bool_sorted_*` fixture keys, or in the current "
    "helper-local anchors for comparator-context ordering, repeat-sort circular integrity, "
    "reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer "
    "modulo-bucket stability, all-ties stability, or empty-or-singleton handling; do not "
    "widen into the missing shared replay stack by default."
)

EXPECTED_LIST_SORT_LANE_NOTE_LINE = (
    "- `PHASE1_LIST_SORT_NEXT_SAFE_STEP=list_sort reopens only for shared replay or "
    "reminder-surface drift in the committed tri_sorted_* or bool_sorted_* fixture keys, "
    "or for drift in the helper-local comparator-context, repeat-sort, reverse-link, "
    "sorted-input, parity-bucket, modulo-bucket, all-ties, non-unit comparator, signed "
    "subtractive comparator, repeated reorder, or empty-or-singleton anchors; do not "
    "widen into neighboring shared-replay parked helpers by default.`"
)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ensure(condition: bool, issue: str, issues: list[str]) -> None:
    if not condition:
        issues.append(issue)


def require_string(payload: dict[str, object], key: str, issue_prefix: str, issues: list[str]) -> str | None:
    value = payload.get(key)
    ensure(isinstance(value, str) and value != "", f"{issue_prefix}:{key}:missing_or_blank", issues)
    return value if isinstance(value, str) and value != "" else None


def require_list_of_strings(
    payload: dict[str, object],
    key: str,
    issue_prefix: str,
    issues: list[str],
) -> list[str] | None:
    value = payload.get(key)
    ensure(isinstance(value, list), f"{issue_prefix}:{key}:not_list", issues)
    if not isinstance(value, list):
        return None

    strings = [item for item in value if isinstance(item, str) and item != ""]
    ensure(len(strings) == len(value), f"{issue_prefix}:{key}:non_string_member", issues)
    return strings


def require_exact_occurrence(text: str, needle: str, issue: str, issues: list[str]) -> None:
    ensure(text.count(needle) == 1, issue, issues)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    manifest_path = root / MANIFEST_REL
    lane_note_path = root / LANE_NOTE_REL
    ensure(manifest_path.exists(), f"missing:{MANIFEST_REL.as_posix()}", issues)
    ensure(lane_note_path.exists(), f"missing:{LANE_NOTE_REL.as_posix()}", issues)
    if issues:
        return issues

    manifest = read_json(manifest_path)
    ensure(isinstance(manifest, dict), "manifest:not_object", issues)
    if not isinstance(manifest, dict):
        return issues

    lane_note_text = read_text(lane_note_path)
    require_exact_occurrence(
        lane_note_text,
        EXPECTED_LIST_SORT_LANE_NOTE_LINE,
        "lane_note:list_sort_next_safe_step",
        issues,
    )

    ensure(manifest.get("phase") == "Phase 1", "manifest:phase", issues)
    helpers = require_list_of_strings(manifest, "helpers", "manifest", issues)
    helper_count = manifest.get("helper_count")
    if helpers is None:
        return issues

    ensure(isinstance(helper_count, int), "manifest:helper_count:not_int", issues)
    if isinstance(helper_count, int):
        ensure(helper_count == len(helpers), "manifest:helper_count:mismatch", issues)

    helper_set = set(helpers)
    ensure(len(helper_set) == len(helpers), "manifest:helpers:duplicate", issues)

    lane = manifest.get("lane_sequencing")
    ensure(isinstance(lane, dict), "manifest:lane_sequencing:not_object", issues)
    if not isinstance(lane, dict):
        return issues

    parked = require_list_of_strings(lane, "shared_replay_parked_helpers", "manifest:lane_sequencing", issues)
    direct = require_list_of_strings(lane, "direct_anchor_followup_helpers", "manifest:lane_sequencing", issues)
    require_string(lane, "rule_summary", "manifest:lane_sequencing", issues)
    require_string(lane, "anti_overlap_rule", "manifest:lane_sequencing", issues)
    if parked is None or direct is None:
        return issues

    parked_set = set(parked)
    direct_set = set(direct)
    ensure(len(parked_set) == len(parked), "manifest:lane_sequencing:shared_replay_parked_helpers:duplicate", issues)
    ensure(len(direct_set) == len(direct), "manifest:lane_sequencing:direct_anchor_followup_helpers:duplicate", issues)
    ensure(parked_set.isdisjoint(direct_set), "manifest:lane_sequencing:helper_overlap", issues)
    ensure(parked_set | direct_set == helper_set, "manifest:lane_sequencing:helper_partition", issues)
    ensure(tuple(direct) == EXPECTED_DIRECT_HELPERS, "manifest:lane_sequencing:direct_helper_order", issues)
    ensure(LIST_SORT_HELPER in parked_set, "manifest:lane_sequencing:list_sort_not_parked", issues)

    review_anchors = manifest.get("review_anchors")
    ensure(isinstance(review_anchors, dict), "manifest:review_anchors:not_object", issues)
    if not isinstance(review_anchors, dict):
        return issues

    review_anchor_keys = set(review_anchors.keys())
    ensure(review_anchor_keys == helper_set, "manifest:review_anchors:key_partition", issues)

    for helper in helpers:
        anchor_payload = review_anchors.get(helper)
        issue_prefix = f"manifest:review_anchors:{helper}"
        ensure(isinstance(anchor_payload, dict), f"{issue_prefix}:not_object", issues)
        if not isinstance(anchor_payload, dict):
            continue

        helper_test_anchors = require_list_of_strings(anchor_payload, "helper_test_anchors", issue_prefix, issues)
        next_safe_step_note = require_string(anchor_payload, "next_safe_step_note", issue_prefix, issues)
        review_packet_summary = require_string(anchor_payload, "review_packet_summary", issue_prefix, issues)

        if helper_test_anchors is not None:
            ensure(len(helper_test_anchors) > 0, f"{issue_prefix}:helper_test_anchors:empty", issues)

        if helper in direct_set:
            ensure("helper-local" in (review_packet_summary or ""), f"{issue_prefix}:direct_missing_helper_local_summary", issues)
            ensure("direct" in (next_safe_step_note or ""), f"{issue_prefix}:direct_missing_next_step_scope", issues)
        else:
            ensure("parked" in (next_safe_step_note or ""), f"{issue_prefix}:parked_missing_next_step_scope", issues)
            ensure(
                ("shared replay" in (review_packet_summary or "")) or ("shared Phase 1 replay" in (review_packet_summary or "")),
                f"{issue_prefix}:parked_missing_shared_replay_summary",
                issues,
            )

        if helper == LIST_SORT_HELPER:
            ensure(
                helper_test_anchors == EXPECTED_LIST_SORT_HELPER_TEST_ANCHORS,
                f"{issue_prefix}:helper_test_anchors:stale_exact_packet",
                issues,
            )
            ensure(
                review_packet_summary == EXPECTED_LIST_SORT_REVIEW_PACKET_SUMMARY,
                f"{issue_prefix}:review_packet_summary:stale_exact_packet",
                issues,
            )
            ensure(
                next_safe_step_note == EXPECTED_LIST_SORT_NEXT_SAFE_STEP_NOTE,
                f"{issue_prefix}:next_safe_step_note:stale_exact_packet",
                issues,
            )

    return issues


def build_sample_manifest() -> dict[str, object]:
    helpers = [
        LIST_SORT_HELPER,
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ]
    parked = [LIST_SORT_HELPER]
    direct = [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ]

    review_anchors: dict[str, object] = {
        LIST_SORT_HELPER: {
            "helper_test_anchors": EXPECTED_LIST_SORT_HELPER_TEST_ANCHORS,
            "review_packet_summary": EXPECTED_LIST_SORT_REVIEW_PACKET_SUMMARY,
            "next_safe_step_note": EXPECTED_LIST_SORT_NEXT_SAFE_STEP_NOTE,
        }
    }
    for helper in direct:
        review_anchors[helper] = {
            "helper_test_anchors": ["test direct helper anchor"],
            "review_packet_summary": "direct helper-local packet stays visible in review",
            "next_safe_step_note": "If this direct helper lane reopens, keep the direct helper-local packet bounded.",
        }

    return {
        "phase": "Phase 1",
        "helper_count": len(helpers),
        "helpers": helpers,
        "lane_sequencing": {
            "shared_replay_parked_helpers": parked,
            "direct_anchor_followup_helpers": direct,
            "rule_summary": "Phase 1 lane routing stays split between parked shared replay helpers and direct helper-local follow-up helpers.",
            "anti_overlap_rule": "Do not batch helpers across the parked and direct Phase 1 sets in one lane.",
        },
        "review_anchors": review_anchors,
    }


def write_sample_root(root: Path, manifest: dict[str, object]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lane_note_path = root / LANE_NOTE_REL
    lane_note_path.parent.mkdir(parents=True, exist_ok=True)
    lane_note_path.write_text(
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        + EXPECTED_LIST_SORT_LANE_NOTE_LINE
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1_lane_sequencing_") as tmp_dir:
        root = Path(tmp_dir)

        baseline = build_sample_manifest()
        write_sample_root(root, baseline)
        issues = collect_issues(root)
        assert "manifest:lane_sequencing:direct_helper_order" not in issues
        assert "manifest:lane_sequencing:helper_overlap" not in issues
        assert "manifest:review_anchors:key_partition" not in issues
        assert "manifest:review_anchors:tools/lib/list_sort.zig:helper_test_anchors:stale_exact_packet" not in issues
        assert "manifest:review_anchors:tools/lib/list_sort.zig:review_packet_summary:stale_exact_packet" not in issues
        assert "manifest:review_anchors:tools/lib/list_sort.zig:next_safe_step_note:stale_exact_packet" not in issues
        assert "lane_note:list_sort_next_safe_step" not in issues
        case_count += 1

        overlap = build_sample_manifest()
        overlap_lane = overlap["lane_sequencing"]
        assert isinstance(overlap_lane, dict)
        overlap_lane["shared_replay_parked_helpers"] = [LIST_SORT_HELPER, "tools/lib/bitmap.zig"]
        write_sample_root(root, overlap)
        issues = collect_issues(root)
        assert "manifest:lane_sequencing:helper_overlap" in issues
        case_count += 1

        missing_review = build_sample_manifest()
        missing_review_anchors = missing_review["review_anchors"]
        assert isinstance(missing_review_anchors, dict)
        missing_review_anchors.pop("tools/lib/string.zig")
        write_sample_root(root, missing_review)
        issues = collect_issues(root)
        assert "manifest:review_anchors:key_partition" in issues
        case_count += 1

        stale_list_sort_review = build_sample_manifest()
        stale_list_sort_review_anchors = stale_list_sort_review["review_anchors"]
        assert isinstance(stale_list_sort_review_anchors, dict)
        list_sort_anchor = stale_list_sort_review_anchors[LIST_SORT_HELPER]
        assert isinstance(list_sort_anchor, dict)
        list_sort_anchor["review_packet_summary"] = "drifted parked summary"
        write_sample_root(root, stale_list_sort_review)
        issues = collect_issues(root)
        assert f"manifest:review_anchors:{LIST_SORT_HELPER}:review_packet_summary:stale_exact_packet" in issues
        case_count += 1

        stale_list_sort_next_step = build_sample_manifest()
        stale_list_sort_next_step_anchors = stale_list_sort_next_step["review_anchors"]
        assert isinstance(stale_list_sort_next_step_anchors, dict)
        list_sort_next_step_anchor = stale_list_sort_next_step_anchors[LIST_SORT_HELPER]
        assert isinstance(list_sort_next_step_anchor, dict)
        list_sort_next_step_anchor["next_safe_step_note"] = "drifted parked next step"
        write_sample_root(root, stale_list_sort_next_step)
        issues = collect_issues(root)
        assert f"manifest:review_anchors:{LIST_SORT_HELPER}:next_safe_step_note:stale_exact_packet" in issues
        case_count += 1

        stale_list_sort_anchor_list = build_sample_manifest()
        stale_list_sort_anchor_list_anchors = stale_list_sort_anchor_list["review_anchors"]
        assert isinstance(stale_list_sort_anchor_list_anchors, dict)
        list_sort_anchor_list = stale_list_sort_anchor_list_anchors[LIST_SORT_HELPER]
        assert isinstance(list_sort_anchor_list, dict)
        list_sort_anchor_list["helper_test_anchors"] = EXPECTED_LIST_SORT_HELPER_TEST_ANCHORS[:-1]
        write_sample_root(root, stale_list_sort_anchor_list)
        issues = collect_issues(root)
        assert f"manifest:review_anchors:{LIST_SORT_HELPER}:helper_test_anchors:stale_exact_packet" in issues
        case_count += 1

        stale_lane_note = build_sample_manifest()
        write_sample_root(root, stale_lane_note)
        lane_note_path = root / LANE_NOTE_REL
        lane_note_path.write_text("# Phase 1 Host-Helper Lane Sequencing\n\n- drifted list_sort note\n", encoding="utf-8")
        issues = collect_issues(root)
        assert "lane_note:list_sort_next_safe_step" in issues
        case_count += 1

    print("PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run focused self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(Path(args.root).resolve())
    if issues:
        print("PHASE1_HELPER_LANE_SEQUENCING=fail")
        for issue in issues:
            print(f"PHASE1_HELPER_LANE_SEQUENCING_ISSUE={issue}")
        return 1

    print("PHASE1_HELPER_LANE_SEQUENCING=pass")
    print(f"PHASE1_HELPER_LANE_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
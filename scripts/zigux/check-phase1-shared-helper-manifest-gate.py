#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[0]
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_PHASE = "Phase 1"
EXPECTED_STATUS = "closed"
EXPECTED_HELPER_COUNT = 13
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
EXPECTED_SHARED_HELPERS = [
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
EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]
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

EXPECTED_LIST_SORT_REVIEW = {
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "parity_fixture_keys": [
        "tri_sorted_keys",
        "tri_sorted_ordinals",
        "bool_sorted_keys",
        "bool_sorted_ordinals",
    ],
    "shared_replay_summary": (
        "the committed Phase 1 fixture still owns the tri-state and boolean-style comparator "
        "parity keys for list_sort, while current master keeps comparator-context handling, "
        "repeat-sort circular-list integrity, reverse-link alignment, sorted-input idempotence, "
        "parity-bucket stability, longer modulo-bucket stability, all-ties stability, and "
        "empty-or-singleton handling explicit at the helper surface until the broader shared "
        "replay packet returns"
    ),
    "comparator_context_anchor": 'test "list sort honors comparator context"',
    "repeat_sort_anchor": 'test "list sort can reorder the same circular list twice"',
    "reverse_link_anchor": 'test "list sort keeps reverse links aligned after reordering"',
    "sorted_input_anchor": 'test "list sort preserves sorted unique input"',
    "parity_bucket_anchor": 'test "list sort preserves stable bucket order across parity groups"',
    "modulo_bucket_anchor": 'test "list sort preserves stable modulo bucket order across a longer merge path"',
    "all_ties_anchor": 'test "list sort preserves input order when every comparison ties"',
    "empty_singleton_anchor": 'test "list sort handles empty and singleton lists"',
    "review_packet_summary": (
        "keep list_sort parked in the shared-replay helper family for fixture ownership, "
        "but reread the helper-local proof packet before reopening the lane: current master "
        "already names direct witnesses for comparator-context ordering, repeat-sort circular "
        "integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, "
        "longer modulo-bucket stability, all-ties stability, and empty-or-singleton handling "
        "beside the committed parity keys"
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep list_sort parked unless a fresh reread finds drift "
        "in the committed `tri_sorted_*` or `bool_sorted_*` fixture keys, or in the current "
        "helper-local anchors for comparator-context ordering, repeat-sort circular integrity, "
        "reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer "
        "modulo-bucket stability, all-ties stability, or empty-or-singleton handling; do not "
        "widen into the missing shared replay stack by default."
    ),
}


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def load_manifest(root: Path) -> dict[str, object]:
    path = root / MANIFEST_REL
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file():
        raise IsADirectoryError(path)
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
    )


def collect_issues(manifest: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if manifest.get("phase") != EXPECTED_PHASE:
        issues.append("manifest:phase")
    if manifest.get("status") != EXPECTED_STATUS:
        issues.append("manifest:status")
    if manifest.get("helper_count") != EXPECTED_HELPER_COUNT:
        issues.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        issues.append("manifest:helpers")

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        issues.append("manifest:lane_sequencing")
        return issues

    if lane_sequencing.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
        issues.append("manifest:shared_replay_parked_helpers")
    if lane_sequencing.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        issues.append("manifest:direct_anchor_followup_helpers")
    if lane_sequencing.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        issues.append("manifest:rule_summary")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append("manifest:anti_overlap_rule")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors")
        return issues

    list_sort_entry = review_anchors.get("tools/lib/list_sort.zig")
    if not isinstance(list_sort_entry, dict):
        issues.append("manifest:list_sort_review_anchor")
        return issues

    for field, expected_value in EXPECTED_LIST_SORT_REVIEW.items():
        if list_sort_entry.get(field) != expected_value:
            issues.append(f"manifest:list_sort_review={field}")

    return issues


def good_manifest() -> dict[str, object]:
    return {
        "phase": EXPECTED_PHASE,
        "status": EXPECTED_STATUS,
        "helper_count": EXPECTED_HELPER_COUNT,
        "helpers": copy.deepcopy(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": copy.deepcopy(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helpers": copy.deepcopy(EXPECTED_DIRECT_HELPERS),
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": {
            "tools/lib/list_sort.zig": copy.deepcopy(EXPECTED_LIST_SORT_REVIEW),
        },
    }


def write_manifest(root: Path, payload: dict[str, object]) -> None:
    path = root / MANIFEST_REL
    if path.exists() and path.is_dir():
        path.rmdir()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def assert_issue_case(root: Path, mutate, expected_issue: str) -> None:
    mutate()
    issues = collect_issues(load_manifest(root))
    assert expected_issue in issues, issues
    write_manifest(root, good_manifest())


def assert_load_failure(root: Path, mutate, expected_fragment: str) -> None:
    mutate()
    try:
        load_manifest(root)
    except Exception as exc:  # noqa: BLE001
        assert expected_fragment in str(exc), str(exc)
    else:
        raise AssertionError("expected load failure")
    write_manifest(root, good_manifest())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_shared_helper_manifest_gate_") as tmp_dir:
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
            lambda: (
                lambda manifest: (
                    manifest["lane_sequencing"].update({"rule_summary": "drift"}),
                    write_manifest(root, manifest),
                )
            )(load_current()),
            "manifest:rule_summary",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda manifest: (
                    manifest["lane_sequencing"]["shared_replay_parked_helpers"].pop(),
                    write_manifest(root, manifest),
                )
            )(load_current()),
            "manifest:shared_replay_parked_helpers",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda manifest: (
                    manifest["review_anchors"]["tools/lib/list_sort.zig"].pop("review_packet_summary"),
                    write_manifest(root, manifest),
                )
            )(load_current()),
            "manifest:list_sort_review=review_packet_summary",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: write_manifest(root, {**load_current(), "review_anchors": "drift"}),
            "manifest:review_anchors",
        )
        case_count += 1

        assert_load_failure(
            root,
            lambda: manifest_path.unlink(),
            str(MANIFEST_REL),
        )
        case_count += 1

        assert_load_failure(
            root,
            lambda: (
                manifest_path.unlink(),
                manifest_path.mkdir(parents=False, exist_ok=False),
            ),
            str(MANIFEST_REL),
        )
        case_count += 1

        assert_load_failure(
            root,
            lambda: manifest_path.write_text("{invalid\n", encoding="utf-8"),
            "Expecting property name enclosed in double quotes",
        )
        case_count += 1

        assert_load_failure(
            root,
            lambda: manifest_path.write_text('{"phase":"Phase 1","phase":"drift"}\n', encoding="utf-8"),
            "duplicate key: phase",
        )
        case_count += 1

    print("PHASE1_SHARED_HELPER_MANIFEST_GATE_SELF_TEST=pass")
    print(f"PHASE1_SHARED_HELPER_MANIFEST_GATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared-helper manifest packet for Phase 1 fixtures."
    )
    parser.add_argument("--self-test", action="store_true", help="Run embedded checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux checkout root.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        issues = collect_issues(load_manifest(repo_root(args.root)))
    except FileNotFoundError:
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE=fail")
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_START")
        print("manifest:path_missing")
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_END")
        return 1
    except IsADirectoryError:
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE=fail")
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_START")
        print("manifest:path_not_file")
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_END")
        return 1
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE=fail")
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_START")
        print(f"manifest:load_error={exc}")
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_END")
        return 1

    if issues:
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE=fail")
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_SHARED_HELPER_MANIFEST_GATE_ISSUES_END")
        return 1

    print("PHASE1_SHARED_HELPER_MANIFEST_GATE=pass")
    print(f"PHASE1_SHARED_HELPER_MANIFEST_GATE_HELPER_COUNT={EXPECTED_HELPER_COUNT}")
    print(f"PHASE1_SHARED_HELPER_MANIFEST_GATE_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print("PHASE1_SHARED_HELPER_MANIFEST_GATE_REVIEW_PACKET=list_sort")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

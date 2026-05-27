#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_DIRECT_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


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


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    manifest_path = root / MANIFEST_REL
    ensure(manifest_path.exists(), f"missing:{MANIFEST_REL.as_posix()}", issues)
    if issues:
        return issues

    manifest = read_json(manifest_path)
    ensure(isinstance(manifest, dict), "manifest:not_object", issues)
    if not isinstance(manifest, dict):
        return issues

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

    return issues


def build_sample_manifest() -> dict[str, object]:
    helpers = [
        "tools/lib/argv_split.zig",
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ]
    parked = ["tools/lib/argv_split.zig"]
    direct = [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ]

    review_anchors: dict[str, object] = {}
    for helper in helpers:
        if helper in direct:
            review_anchors[helper] = {
                "helper_test_anchors": ["test direct helper anchor"],
                "review_packet_summary": "direct helper-local packet stays visible in review",
                "next_safe_step_note": "If this direct helper lane reopens, keep the helper-local packet bounded.",
            }
        else:
            review_anchors[helper] = {
                "helper_test_anchors": ["test parked helper anchor"],
                "review_packet_summary": "the shared Phase 1 replay still owns this parked helper packet",
                "next_safe_step_note": "If this parked helper lane reopens, keep it parked unless shared replay drifts.",
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
    path = root / MANIFEST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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
        case_count += 1

        overlap = build_sample_manifest()
        overlap_lane = overlap["lane_sequencing"]
        assert isinstance(overlap_lane, dict)
        overlap_lane["shared_replay_parked_helpers"] = [
            "tools/lib/argv_split.zig",
            "tools/lib/bitmap.zig",
        ]
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

        missing_direct_scope = build_sample_manifest()
        missing_direct_review = missing_direct_scope["review_anchors"]
        assert isinstance(missing_direct_review, dict)
        bitmap_anchor = missing_direct_review["tools/lib/bitmap.zig"]
        assert isinstance(bitmap_anchor, dict)
        bitmap_anchor["review_packet_summary"] = "direct packet stays visible in review"
        write_sample_root(root, missing_direct_scope)
        issues = collect_issues(root)
        assert "manifest:review_anchors:tools/lib/bitmap.zig:direct_missing_helper_local_summary" in issues
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

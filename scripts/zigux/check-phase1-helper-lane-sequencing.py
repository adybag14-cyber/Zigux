#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


README_REL = Path("scripts/zigux/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
C_HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")

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

EXPECTED_PARKED_HELPERS = [
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
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded direct "
    "helper-local follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or "
    "already-committed shared fixture keys."
)

EXPECTED_PHASE1_FLOW_LINE = (
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper "
    "tranche reviewable through the live owner-map and string-review guards instead "
    "of rebuilding the broader installer-backed closure packet from older missing "
    "routes"
)

EXPECTED_DIRECT_ANCHOR_LINE = (
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, "
    "rbtree, and string reopen only inside their existing helper-local anchors or "
    "already-committed shared fixture keys, while the other nine closed helpers stay "
    "parked unless the shared replay or reminder packet drifts"
)


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return Path(__file__).resolve().parents[2]


def load_json_without_duplicates(path: Path) -> dict:
    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def add_path_issue(path: Path, rel: Path, prefix: str, issues: list[str]) -> bool:
    if path.is_dir():
        issues.append(f"{prefix}:directory={rel.as_posix()}")
        return True
    if not path.is_file():
        issues.append(f"missing:{rel.as_posix()}")
        return True
    return False


def is_nonempty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    readme_path = root / README_REL
    manifest_path = root / MANIFEST_REL
    blockers_path = root / BLOCKERS_REL

    if add_path_issue(readme_path, README_REL, "readme", issues):
        return issues
    if add_path_issue(manifest_path, MANIFEST_REL, "manifest", issues):
        return issues
    if add_path_issue(blockers_path, BLOCKERS_REL, "blockers", issues):
        return issues

    readme_lines = readme_path.read_text(encoding="utf-8").splitlines()
    if EXPECTED_PHASE1_FLOW_LINE not in readme_lines:
        issues.append("readme:phase1_flow_line")
    if EXPECTED_DIRECT_ANCHOR_LINE not in readme_lines:
        issues.append("readme:direct_anchor_line")

    try:
        manifest = load_json_without_duplicates(manifest_path)
    except Exception as exc:
        issues.append(f"manifest:parse={exc}")
        return issues

    if manifest.get("phase") != "Phase 1":
        issues.append("manifest:phase")
    if manifest.get("status") != "closed":
        issues.append("manifest:status")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        issues.append("manifest:helpers")

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        issues.append("manifest:lane_sequencing")
        return issues

    if lane_sequencing.get("shared_replay_parked_helpers") != EXPECTED_PARKED_HELPERS:
        issues.append("manifest:shared_replay_parked_helpers")
    if lane_sequencing.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        issues.append("manifest:direct_anchor_followup_helpers")
    if lane_sequencing.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        issues.append("manifest:rule_summary")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append("manifest:anti_overlap_rule")

    combined = lane_sequencing.get("shared_replay_parked_helpers", []) + lane_sequencing.get(
        "direct_anchor_followup_helpers", []
    )
    if sorted(combined) != sorted(EXPECTED_HELPERS):
        issues.append("manifest:helper_partition")
    if len(set(combined)) != len(EXPECTED_HELPERS):
        issues.append("manifest:helper_partition_duplicates")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        issues.append("manifest:review_anchors")
        return issues

    missing_review_helpers = [helper for helper in EXPECTED_HELPERS if helper not in review_anchors]
    if missing_review_helpers:
        issues.append(
            "manifest:missing_review_anchors=" + ",".join(missing_review_helpers)
        )
    unexpected_review_helpers = [helper for helper in review_anchors if helper not in EXPECTED_HELPERS]
    if unexpected_review_helpers:
        issues.append(
            "manifest:unexpected_review_anchors=" + ",".join(sorted(unexpected_review_helpers))
        )

    for helper in EXPECTED_HELPERS:
        anchor = review_anchors.get(helper)
        if not isinstance(anchor, dict):
            issues.append(f"manifest:missing_review_anchor={helper}")
            continue

        helper_tests = anchor.get("helper_test_anchors")
        if not is_nonempty_string_list(helper_tests):
            issues.append(f"manifest:helper_test_anchors={helper}")
        elif len(set(helper_tests)) != len(helper_tests):
            issues.append(f"manifest:helper_test_anchor_duplicates={helper}")

        replay_anchor = anchor.get("phase1_helper_replay_anchor")
        if not isinstance(replay_anchor, str) or not replay_anchor.strip():
            issues.append(f"manifest:phase1_helper_replay_anchor={helper}")

        next_step = anchor.get("next_safe_step_note")
        if not isinstance(next_step, str) or not next_step.strip():
            issues.append(f"manifest:next_safe_step_note={helper}")

        summary_keys = [
            key
            for key, value in anchor.items()
            if key.endswith("_summary") and isinstance(value, str) and value.strip()
        ]
        if not summary_keys:
            issues.append(f"manifest:review_summary={helper}")

    try:
        blockers = load_json_without_duplicates(blockers_path)
    except Exception as exc:
        issues.append(f"blockers:parse={exc}")
        return issues

    if blockers.get("status") != "parked":
        issues.append("blockers:status")

    blocker_lane = blockers.get("lane_sequencing")
    if not isinstance(blocker_lane, dict):
        issues.append("blockers:lane_sequencing")
        return issues

    if blocker_lane.get("manifest") != MANIFEST_REL.as_posix():
        issues.append("blockers:manifest_path")
    if blocker_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_PARKED_HELPERS):
        issues.append("blockers:shared_replay_parked_helper_count")
    if blocker_lane.get("shared_replay_parked_helpers") != EXPECTED_PARKED_HELPERS:
        issues.append("blockers:shared_replay_parked_helpers")
    if blocker_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        issues.append("blockers:direct_anchor_followup_helper_count")
    if blocker_lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        issues.append("blockers:direct_anchor_followup_helpers")
    if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append("blockers:anti_overlap_rule")

    blocked_combined = blocker_lane.get("shared_replay_parked_helpers", []) + blocker_lane.get(
        "direct_anchor_followup_helpers", []
    )
    if sorted(blocked_combined) != sorted(EXPECTED_HELPERS):
        issues.append("blockers:helper_partition")
    if len(set(blocked_combined)) != len(EXPECTED_HELPERS):
        issues.append("blockers:helper_partition_duplicates")

    replay = blockers.get("replay")
    if not isinstance(replay, dict):
        issues.append("blockers:replay")
        return issues
    if replay.get("path") != REPLAY_REL.as_posix():
        issues.append("blockers:replay_path")
    if replay.get("state") != "blocked":
        issues.append("blockers:replay_state")

    c_harness = blockers.get("c_harness")
    if not isinstance(c_harness, dict):
        issues.append("blockers:c_harness")
        return issues
    if c_harness.get("path") != C_HARNESS_REL.as_posix():
        issues.append("blockers:c_harness_path")
    if c_harness.get("state") != "blocked":
        issues.append("blockers:c_harness_state")
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append("blockers:c_harness_helper_count")
    if c_harness.get("helpers") != EXPECTED_HELPERS:
        issues.append("blockers:c_harness_helpers")
    if c_harness.get("blocker_id") != "phase1_helpers_c_harness_missing_c_sources":
        issues.append("blockers:c_harness_blocker_id")

    return issues


def make_sample_root(root: Path) -> None:
    readme_path = root / README_REL
    manifest_path = root / MANIFEST_REL
    blockers_path = root / BLOCKERS_REL
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    blockers_path.parent.mkdir(parents=True, exist_ok=True)

    readme_path.write_text(
        "\n".join(
            [
                "# scripts/zigux",
                "",
                "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
                "",
                "## Phase 1",
                "",
                EXPECTED_PHASE1_FLOW_LINE,
                EXPECTED_DIRECT_ANCHOR_LINE,
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    review_anchors = {}
    for helper in EXPECTED_HELPERS:
        anchor = {
            "helper_test_anchors": [f'test "{helper} stays review-visible"'],
            "phase1_helper_replay_anchor": f'test "{helper} sample replay anchor"',
            "next_safe_step_note": f"{helper} reopens only for bounded packet drift.",
        }
        if helper in EXPECTED_DIRECT_HELPERS:
            anchor["review_packet_summary"] = (
                f"{helper} keeps a direct helper-local review packet on current master."
            )
        else:
            anchor["shared_replay_summary"] = (
                f"{helper} stays parked on the shared replay reminder packet."
            )
        review_anchors[helper] = anchor

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "review_anchors": review_anchors,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    blockers = {
        "status": "parked",
        "lane_sequencing": {
            "manifest": MANIFEST_REL.as_posix(),
            "shared_replay_parked_helper_count": len(EXPECTED_PARKED_HELPERS),
            "shared_replay_parked_helpers": EXPECTED_PARKED_HELPERS,
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": REPLAY_REL.as_posix(),
            "state": "blocked",
        },
        "c_harness": {
            "path": C_HARNESS_REL.as_posix(),
            "state": "blocked",
            "reason": "Legacy helper .c companions are still absent on current master.",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": EXPECTED_HELPERS,
            "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
        },
    }
    blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")


def expect_failure(mutator) -> None:
    with tempfile.TemporaryDirectory(prefix="phase1-helper-lane-") as tmp_dir:
        root = Path(tmp_dir)
        make_sample_root(root)
        mutator(root)
        issues = collect_issues(root)
        if not issues:
            raise AssertionError("expected failure but checker passed")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase1-helper-lane-") as tmp_dir:
        root = Path(tmp_dir)
        make_sample_root(root)
        issues = collect_issues(root)
        if issues:
            raise AssertionError(f"sample root should pass, got {issues}")

    expect_failure(lambda root: (root / README_REL).write_text("# scripts/zigux\n", encoding="utf-8"))

    def wrong_direct_line(root: Path) -> None:
        path = root / README_REL
        path.write_text(path.read_text(encoding="utf-8").replace("the other nine", "the other eight"), encoding="utf-8")

    expect_failure(wrong_direct_line)

    def readme_directory(root: Path) -> None:
        path = root / README_REL
        path.unlink()
        path.mkdir()

    expect_failure(readme_directory)

    def wrong_partition(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["shared_replay_parked_helpers"] = EXPECTED_PARKED_HELPERS[:-1]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(wrong_partition)

    def manifest_directory(root: Path) -> None:
        path = root / MANIFEST_REL
        path.unlink()
        path.mkdir()

    expect_failure(manifest_directory)

    def invalid_json(root: Path) -> None:
        path = root / MANIFEST_REL
        path.write_text("{\n", encoding="utf-8")

    expect_failure(invalid_json)

    def duplicate_key(root: Path) -> None:
        path = root / MANIFEST_REL
        path.write_text('{"phase":"Phase 1","phase":"duplicate"}\n', encoding="utf-8")

    expect_failure(duplicate_key)

    def missing_review_summary(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/string.zig"]["review_packet_summary"]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(missing_review_summary)

    def missing_next_safe_step(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/string.zig"]["next_safe_step_note"]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(missing_next_safe_step)

    def missing_parked_review_anchor(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/argv_split.zig"]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(missing_parked_review_anchor)

    def empty_helper_test_anchors(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/argv_split.zig"]["helper_test_anchors"] = []
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(empty_helper_test_anchors)

    def missing_phase1_replay_anchor(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/argv_split.zig"]["phase1_helper_replay_anchor"]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(missing_phase1_replay_anchor)

    def wrong_helper_count(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["helper_count"] = 12
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(wrong_helper_count)

    def blockers_directory(root: Path) -> None:
        path = root / BLOCKERS_REL
        path.unlink()
        path.mkdir()

    expect_failure(blockers_directory)

    def blockers_duplicate_key(root: Path) -> None:
        path = root / BLOCKERS_REL
        path.write_text('{"status":"parked","status":"duplicate"}\n', encoding="utf-8")

    expect_failure(blockers_duplicate_key)

    def blockers_wrong_direct_count(root: Path) -> None:
        path = root / BLOCKERS_REL
        blockers = json.loads(path.read_text(encoding="utf-8"))
        blockers["lane_sequencing"]["direct_anchor_followup_helper_count"] = 3
        path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")

    expect_failure(blockers_wrong_direct_count)

    def blockers_wrong_anti_overlap(root: Path) -> None:
        path = root / BLOCKERS_REL
        blockers = json.loads(path.read_text(encoding="utf-8"))
        blockers["lane_sequencing"]["anti_overlap_rule"] = "wrong"
        path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")

    expect_failure(blockers_wrong_anti_overlap)

    def blockers_wrong_c_harness_helper_count(root: Path) -> None:
        path = root / BLOCKERS_REL
        blockers = json.loads(path.read_text(encoding="utf-8"))
        blockers["c_harness"]["helper_count"] = 12
        path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")

    expect_failure(blockers_wrong_c_harness_helper_count)

    print("PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST=pass")
    print("PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST_CASE_COUNT=18")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a current-master-shaped sample root for replay validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        make_sample_root(Path(args.write_sample_root).resolve())
        return 0

    root = repo_root_from_arg(args.root)
    issues = collect_issues(root)
    if issues:
        print("PHASE1_HELPER_LANE_SEQUENCING=fail")
        for issue in issues:
            print(f"PHASE1_HELPER_LANE_SEQUENCING_ISSUE={issue}")
        return 1

    print("PHASE1_HELPER_LANE_SEQUENCING=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_PARKED_COUNT={len(EXPECTED_PARKED_HELPERS)}")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_DIRECT_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    print("PHASE1_HELPER_LANE_SEQUENCING_README_MARKER_COUNT=2")
    print("PHASE1_HELPER_LANE_SEQUENCING_BLOCKER_PACKET_COUNT=2")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_REVIEW_ANCHOR_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_DIRECT_REVIEW_ANCHOR_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

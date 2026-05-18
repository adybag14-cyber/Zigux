#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

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

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded "
    "direct helper-local follow-up anchors on current master."
)

EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
    "that current master no longer ships beside the Phase 1 `.zig` ports."
)

EXPECTED_REPLAY_EVIDENCE = (
    "Focused 2026-05-17 scratch replay of `zig build test --build-file "
    "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` "
    "because the committed fixture expects `true` while `tools/lib/slab.zig` still "
    "produced `false`."
)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def expect(condition: bool, issues: list[str], label: str) -> None:
    if not condition:
        issues.append(label)


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
        issues.append("manifest:lane_sequencing")
        return

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


def check_blockers(payload: object, issues: list[str]) -> None:
    if not isinstance(payload, dict):
        issues.append("blockers:not_json_object")
        return

    expect(payload.get("status") == "parked", issues, "blockers:status")

    lane = payload.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("blockers:lane_sequencing")
    else:
        expect(
            lane.get("manifest") == str(MANIFEST_REL),
            issues,
            "blockers:manifest_path",
        )
        expect(
            lane.get("shared_replay_parked_helper_count") == len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            issues,
            "blockers:shared_replay_count",
        )
        expect(
            lane.get("shared_replay_parked_helpers") == EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            issues,
            "blockers:shared_replay_helpers",
        )
        expect(
            lane.get("direct_anchor_followup_helper_count") == len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            issues,
            "blockers:direct_anchor_count",
        )
        expect(
            lane.get("direct_anchor_followup_helpers") == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            issues,
            "blockers:direct_anchor_helpers",
        )
        expect(
            lane.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE,
            issues,
            "blockers:anti_overlap_rule",
        )

    replay = payload.get("replay")
    if not isinstance(replay, dict):
        issues.append("blockers:replay")
    else:
        expect(replay.get("path") == "zigux/tests/phase1_helpers.zig", issues, "blockers:replay_path")
        expect(replay.get("state") == "blocked", issues, "blockers:replay_state")
        blockers = replay.get("blockers")
        if not isinstance(blockers, list) or len(blockers) != 1:
            issues.append("blockers:replay_blockers")
        else:
            blocker = blockers[0]
            if not isinstance(blocker, dict):
                issues.append("blockers:replay_blocker_shape")
            else:
                expect(
                    blocker.get("id") == "phase1_helpers_zig_slab_zero_after_kmalloc",
                    issues,
                    "blockers:replay_blocker_id",
                )
                expect(blocker.get("kind") == "fixture_mismatch", issues, "blockers:replay_blocker_kind")
                expect(blocker.get("path") == "tools/lib/slab.zig", issues, "blockers:replay_blocker_path")
                expect(
                    blocker.get("field") == "slab.zero_after_kmalloc",
                    issues,
                    "blockers:replay_blocker_field",
                )
                expect(blocker.get("expected") is True, issues, "blockers:replay_blocker_expected")
                expect(blocker.get("actual") is False, issues, "blockers:replay_blocker_actual")
                expect(
                    blocker.get("evidence") == EXPECTED_REPLAY_EVIDENCE,
                    issues,
                    "blockers:replay_blocker_evidence",
                )

    c_harness = payload.get("c_harness")
    if not isinstance(c_harness, dict):
        issues.append("blockers:c_harness")
        return

    expect(
        c_harness.get("path") == "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        issues,
        "blockers:c_harness_path",
    )
    expect(c_harness.get("state") == "blocked", issues, "blockers:c_harness_state")
    expect(c_harness.get("reason") == EXPECTED_C_HARNESS_REASON, issues, "blockers:c_harness_reason")
    expect(c_harness.get("helper_count") == len(EXPECTED_HELPERS), issues, "blockers:c_harness_helper_count")
    expect(c_harness.get("helpers") == EXPECTED_HELPERS, issues, "blockers:c_harness_helpers")
    expect(
        c_harness.get("blocker_id") == "phase1_helpers_c_harness_missing_c_sources",
        issues,
        "blockers:c_harness_blocker_id",
    )


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    manifest_path = root / MANIFEST_REL
    blockers_path = root / BLOCKERS_REL

    if not manifest_path.exists():
        issues.append("manifest:missing")
    else:
        check_manifest(read_json(manifest_path), issues)

    if not blockers_path.exists():
        issues.append("blockers:missing")
    else:
        check_blockers(read_json(blockers_path), issues)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_REPLAY_BLOCKERS=fail")
        for issue in issues:
            print(f"PHASE1_REPLAY_BLOCKERS_ISSUE={issue}")
        return 1

    print("PHASE1_REPLAY_BLOCKERS=pass")
    print(f"PHASE1_REPLAY_BLOCKERS_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(
        "PHASE1_REPLAY_BLOCKERS_SHARED_REPLAY_COUNT="
        + str(len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS))
    )
    print(
        "PHASE1_REPLAY_BLOCKERS_DIRECT_ANCHOR_COUNT="
        + str(len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS))
    )
    print("PHASE1_REPLAY_BLOCKERS_REPLAY_STATE=blocked")
    print("PHASE1_REPLAY_BLOCKERS_C_HARNESS_STATE=blocked")
    return 0


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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
    }


def good_blockers() -> dict[str, object]:
    return {
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
            "blockers": [
                {
                    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
                    "kind": "fixture_mismatch",
                    "path": "tools/lib/slab.zig",
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                    "evidence": EXPECTED_REPLAY_EVIDENCE,
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
        },
    }


def build_root(root: Path) -> Path:
    write_json(root / MANIFEST_REL, good_manifest())
    write_json(root / BLOCKERS_REL, good_blockers())
    return root


def expect_failure(label: str, root: Path) -> str | None:
    issues = collect_issues(root)
    return None if issues else label


def run_self_test() -> int:
    failed: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_replay_blockers_") as tmp_dir:
        base = Path(tmp_dir)

        good_root = build_root(base / "good")
        if run_check(good_root) != 0:
            failed.append("good")

        missing_manifest_root = build_root(base / "missing_manifest")
        (missing_manifest_root / MANIFEST_REL).unlink()
        if expect_failure("missing_manifest", missing_manifest_root) is not None:
            failed.append("missing_manifest")

        manifest_status_root = build_root(base / "manifest_status")
        payload = good_manifest()
        payload["status"] = "open"
        write_json(manifest_status_root / MANIFEST_REL, payload)
        if expect_failure("manifest_status", manifest_status_root) is not None:
            failed.append("manifest_status")

        manifest_helpers_root = build_root(base / "manifest_helpers")
        payload = good_manifest()
        payload["helpers"] = payload["helpers"][:-1]
        payload["helper_count"] = len(payload["helpers"])
        write_json(manifest_helpers_root / MANIFEST_REL, payload)
        if expect_failure("manifest_helpers", manifest_helpers_root) is not None:
            failed.append("manifest_helpers")

        blockers_missing_root = build_root(base / "blockers_missing")
        (blockers_missing_root / BLOCKERS_REL).unlink()
        if expect_failure("blockers_missing", blockers_missing_root) is not None:
            failed.append("blockers_missing")

        blockers_status_root = build_root(base / "blockers_status")
        payload = good_blockers()
        payload["status"] = "open"
        write_json(blockers_status_root / BLOCKERS_REL, payload)
        if expect_failure("blockers_status", blockers_status_root) is not None:
            failed.append("blockers_status")

        blockers_lane_root = build_root(base / "blockers_lane")
        payload = good_blockers()
        payload["lane_sequencing"]["shared_replay_parked_helper_count"] = 8
        write_json(blockers_lane_root / BLOCKERS_REL, payload)
        if expect_failure("blockers_lane", blockers_lane_root) is not None:
            failed.append("blockers_lane")

        blockers_replay_root = build_root(base / "blockers_replay")
        payload = good_blockers()
        payload["replay"]["blockers"][0]["actual"] = True
        write_json(blockers_replay_root / BLOCKERS_REL, payload)
        if expect_failure("blockers_replay", blockers_replay_root) is not None:
            failed.append("blockers_replay")

        blockers_replay_evidence_root = build_root(base / "blockers_replay_evidence")
        payload = good_blockers()
        payload["replay"]["blockers"][0]["evidence"] = "drift"
        write_json(blockers_replay_evidence_root / BLOCKERS_REL, payload)
        if expect_failure("blockers_replay_evidence", blockers_replay_evidence_root) is not None:
            failed.append("blockers_replay_evidence")

        blockers_c_harness_root = build_root(base / "blockers_c_harness")
        payload = good_blockers()
        payload["c_harness"]["helper_count"] = 12
        write_json(blockers_c_harness_root / BLOCKERS_REL, payload)
        if expect_failure("blockers_c_harness", blockers_c_harness_root) is not None:
            failed.append("blockers_c_harness")

        blockers_c_harness_reason_root = build_root(base / "blockers_c_harness_reason")
        payload = good_blockers()
        payload["c_harness"]["reason"] = "drift"
        write_json(blockers_c_harness_reason_root / BLOCKERS_REL, payload)
        if expect_failure("blockers_c_harness_reason", blockers_c_harness_reason_root) is not None:
            failed.append("blockers_c_harness_reason")

    if failed:
        print("PHASE1_REPLAY_BLOCKERS_SELF_TEST=fail")
        for label in failed:
            print(f"PHASE1_REPLAY_BLOCKERS_SELF_TEST_FAILED_CASE={label}")
        return 1

    print("PHASE1_REPLAY_BLOCKERS_SELF_TEST=pass")
    print("PHASE1_REPLAY_BLOCKERS_SELF_TEST_CASE_COUNT=11")
    print(
        "PHASE1_REPLAY_BLOCKERS_SELF_TEST_CASES="
        + ",".join(
            [
                "good",
                "missing_manifest",
                "manifest_status",
                "manifest_helpers",
                "blockers_missing",
                "blockers_status",
                "blockers_lane",
                "blockers_replay",
                "blockers_replay_evidence",
                "blockers_c_harness",
                "blockers_c_harness_reason",
            ]
        )
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 replay blocker fixture packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

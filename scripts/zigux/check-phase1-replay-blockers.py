#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
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

EXPECTED_MANIFEST_RULE_SUMMARY = (
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

EXPECTED_REPLAY_EVIDENCE = (
    "Focused 2026-05-17 scratch replay of `zig build test --build-file "
    "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` "
    "because the committed fixture expects `true` while `tools/lib/slab.zig` still "
    "produced `false`."
)

EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
    "that current master no longer ships beside the Phase 1 `.zig` ports."
)


class CheckError(Exception):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    seen: set[str] = set()
    for key, value in pairs:
        if key in seen:
            raise CheckError(f"duplicate_key:{key}")
        seen.add(key)
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
    expect(
        lane.get("rule_summary") == EXPECTED_MANIFEST_RULE_SUMMARY,
        issues,
        "manifest:rule_summary",
    )
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
        expect(lane.get("manifest") == str(MANIFEST_REL), issues, "blockers:manifest_path")
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
        rule_summary = lane.get("rule_summary")
        if rule_summary is not None:
            expect(
                rule_summary == EXPECTED_MANIFEST_RULE_SUMMARY,
                issues,
                "blockers:rule_summary",
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
                expect(
                    blocker.get("kind") == "fixture_mismatch",
                    issues,
                    "blockers:replay_blocker_kind",
                )
                expect(
                    blocker.get("path") == "tools/lib/slab.zig",
                    issues,
                    "blockers:replay_blocker_path",
                )
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
    expect(
        c_harness.get("reason") == EXPECTED_C_HARNESS_REASON,
        issues,
        "blockers:c_harness_reason",
    )
    expect(
        c_harness.get("helper_count") == len(EXPECTED_HELPERS),
        issues,
        "blockers:c_harness_helper_count",
    )
    expect(c_harness.get("helpers") == EXPECTED_HELPERS, issues, "blockers:c_harness_helpers")
    expect(
        c_harness.get("blocker_id") == "phase1_helpers_c_harness_missing_c_sources",
        issues,
        "blockers:c_harness_blocker_id",
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
    print("PHASE1_REPLAY_BLOCKERS_MANIFEST=" + str(MANIFEST_REL))
    print("PHASE1_REPLAY_BLOCKERS_STATUS=parked")
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
            "rule_summary": EXPECTED_MANIFEST_RULE_SUMMARY,
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


def write_sample_root(root: Path) -> None:
    build_root(root)


def expect_failure(root: Path, expected_issue_prefix: str) -> bool:
    return any(issue.startswith(expected_issue_prefix) for issue in collect_issues(root))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    failed: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_replay_blockers_") as tmp_dir:
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

        manifest_status_root = build_root(base / "manifest_status")
        payload = good_manifest()
        payload["status"] = "open"
        write_json(manifest_status_root / MANIFEST_REL, payload)
        if not expect_failure(manifest_status_root, "manifest:status"):
            failed.append("manifest_status")

        blockers_missing_root = build_root(base / "blockers_missing")
        (blockers_missing_root / BLOCKERS_REL).unlink()
        if not expect_failure(blockers_missing_root, "blockers:missing"):
            failed.append("blockers_missing")

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

        blockers_status_root = build_root(base / "blockers_status")
        payload = good_blockers()
        payload["status"] = "open"
        write_json(blockers_status_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_status_root, "blockers:status"):
            failed.append("blockers_status")

        blockers_rule_summary_root = build_root(base / "blockers_rule_summary")
        payload = good_blockers()
        payload["lane_sequencing"]["rule_summary"] = "drift"
        write_json(blockers_rule_summary_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_rule_summary_root, "blockers:rule_summary"):
            failed.append("blockers_rule_summary")

        blockers_replay_root = build_root(base / "blockers_replay")
        payload = good_blockers()
        payload["replay"]["blockers"][0]["actual"] = True
        write_json(blockers_replay_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_replay_root, "blockers:replay_blocker_actual"):
            failed.append("blockers_replay")

        blockers_c_harness_root = build_root(base / "blockers_c_harness")
        payload = good_blockers()
        payload["c_harness"]["reason"] = "drift"
        write_json(blockers_c_harness_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_c_harness_root, "blockers:c_harness_reason"):
            failed.append("blockers_c_harness")

        blockers_helper_list_root = build_root(base / "blockers_helper_list")
        payload = good_blockers()
        payload["c_harness"]["helpers"] = payload["c_harness"]["helpers"][:-1]
        write_json(blockers_helper_list_root / BLOCKERS_REL, payload)
        if not expect_failure(blockers_helper_list_root, "blockers:c_harness_helpers"):
            failed.append("blockers_helper_list")

    if failed:
        print("PHASE1_REPLAY_BLOCKERS_SELF_TEST=fail")
        for label in failed:
            print(f"PHASE1_REPLAY_BLOCKERS_SELF_TEST_FAILED_CASE={label}")
        return 1

    print("PHASE1_REPLAY_BLOCKERS_SELF_TEST=pass")
    print("PHASE1_REPLAY_BLOCKERS_SELF_TEST_CASE_COUNT=15")
    print(
        "PHASE1_REPLAY_BLOCKERS_SELF_TEST_CASES="
        + ",".join(
            [
                "good",
                "missing_manifest",
                "manifest_not_file",
                "manifest_bad_json",
                "manifest_dup_key",
                "manifest_status",
                "blockers_missing",
                "blockers_not_file",
                "blockers_bad_json",
                "blockers_dup_key",
                "blockers_status",
                "blockers_rule_summary",
                "blockers_replay",
                "blockers_c_harness",
                "blockers_helper_list",
            ]
        )
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 replay-blocker fixture packet."
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
        write_sample_root(args.write_sample_root.resolve())
        return 0
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

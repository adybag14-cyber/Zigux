#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
EXPECTED_STATUS = "parked"
EXPECTED_REPLAY_PATH = "zigux/tests/phase1_helpers.zig"
EXPECTED_REPLAY_STATE = "blocked"
EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_C_HARNESS_STATE = "blocked"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
    "that current master no longer ships beside the Phase 1 `.zig` ports."
)
EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_REPLAY_BLOCKER_PATH = "tools/lib/slab.zig"
EXPECTED_REPLAY_BLOCKER_FIELD = "slab.zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_EXPECTED = True
EXPECTED_REPLAY_BLOCKER_ACTUAL = False
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
EXPECTED_C_SOURCES = [helper.replace(".zig", ".c") for helper in EXPECTED_HELPERS]
SELF_TEST_CASES = [
    "happy_path",
    "write_sample_root",
    "missing_blockers_file",
    "blockers_path_is_directory",
    "invalid_blockers_json",
    "duplicate_blockers_keys",
    "missing_manifest_file",
    "manifest_path_is_directory",
    "invalid_manifest_json",
    "duplicate_manifest_keys",
    "blocker_manifest_link_drift",
    "shared_helper_count_drift",
    "replay_blocker_payload_drift",
    "c_harness_helper_list_drift",
    "missing_zig_helper",
    "unexpected_c_source_present",
]


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def blockers_path(root: Path) -> Path:
    return root / BLOCKERS_REL


def manifest_path(root: Path) -> Path:
    return root / MANIFEST_REL


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def read_json_with_duplicates(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=DuplicateTrackingDict)


def _check_required_json_file(path: Path, rel: Path, label: str) -> tuple[list[str], object | None]:
    if not path.exists():
        return ([f"missing:{label}:{rel.as_posix()}"], None)
    if path.is_dir():
        return ([f"directory:{label}:{rel.as_posix()}"], None)
    try:
        payload = read_json_with_duplicates(path)
    except json.JSONDecodeError as exc:
        return ([f"invalid_json:{label}:{exc.msg}:line={exc.lineno}:column={exc.colno}"], None)
    if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:
        return ([f"duplicate_keys:{label}:{','.join(payload.duplicate_keys)}"], None)
    return ([], payload)


def build_manifest_payload() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }


def build_blockers_payload() -> dict[str, object]:
    return {
        "status": EXPECTED_STATUS,
        "lane_sequencing": {
            "manifest": MANIFEST_REL.as_posix(),
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_HELPERS),
            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": EXPECTED_REPLAY_PATH,
            "state": EXPECTED_REPLAY_STATE,
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_ID,
                    "kind": "fixture_mismatch",
                    "path": EXPECTED_REPLAY_BLOCKER_PATH,
                    "field": EXPECTED_REPLAY_BLOCKER_FIELD,
                    "expected": EXPECTED_REPLAY_BLOCKER_EXPECTED,
                    "actual": EXPECTED_REPLAY_BLOCKER_ACTUAL,
                    "evidence": (
                        "Focused 2026-05-17 scratch replay of `zig build test --build-file "
                        "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` "
                        "because the committed fixture expects `true` while `tools/lib/slab.zig` "
                        "still produced `false`."
                    ),
                }
            ],
        },
        "c_harness": {
            "path": EXPECTED_C_HARNESS_PATH,
            "state": EXPECTED_C_HARNESS_STATE,
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": EXPECTED_HELPERS,
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }


def write_sample_root(root: Path) -> None:
    write_json(manifest_path(root), build_manifest_payload())
    write_json(blockers_path(root), build_blockers_payload())
    for helper in EXPECTED_HELPERS:
        write_text(root / helper, "// placeholder\n")


def validate_manifest_payload(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return [f"manifest_type:{type(payload).__name__}"]

    issues: list[str] = []
    if payload.get("phase") != "Phase 1":
        issues.append(f"manifest_phase:{payload.get('phase')!r}")
    if payload.get("status") != "closed":
        issues.append(f"manifest_status:{payload.get('status')!r}")
    if payload.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append(f"manifest_helper_count:{payload.get('helper_count')!r}")
    if payload.get("helpers") != EXPECTED_HELPERS:
        issues.append("manifest_helpers")

    lane_sequencing = payload.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return issues + [f"manifest_lane_sequencing_type:{type(lane_sequencing).__name__}"]

    if lane_sequencing.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
        issues.append("manifest_shared_helpers")
    if lane_sequencing.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        issues.append("manifest_direct_helpers")
    if lane_sequencing.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        issues.append("manifest_rule_summary")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append("manifest_anti_overlap_rule")

    return issues


def validate_blockers_payload(payload: object, root: Path) -> list[str]:
    if not isinstance(payload, dict):
        return [f"blockers_type:{type(payload).__name__}"]

    issues: list[str] = []
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"status:{payload.get('status')!r}")

    lane_sequencing = payload.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return issues + [f"lane_sequencing_type:{type(lane_sequencing).__name__}"]
    if lane_sequencing.get("manifest") != MANIFEST_REL.as_posix():
        issues.append(f"lane_manifest:{lane_sequencing.get('manifest')!r}")
    if lane_sequencing.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        issues.append(
            f"shared_helper_count:{lane_sequencing.get('shared_replay_parked_helper_count')!r}"
        )
    if lane_sequencing.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
        issues.append("shared_helper_list")
    if lane_sequencing.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        issues.append(
            f"direct_helper_count:{lane_sequencing.get('direct_anchor_followup_helper_count')!r}"
        )
    if lane_sequencing.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        issues.append("direct_helper_list")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append("anti_overlap_rule")

    replay = payload.get("replay")
    if not isinstance(replay, dict):
        return issues + [f"replay_type:{type(replay).__name__}"]
    if replay.get("path") != EXPECTED_REPLAY_PATH:
        issues.append(f"replay_path:{replay.get('path')!r}")
    if replay.get("state") != EXPECTED_REPLAY_STATE:
        issues.append(f"replay_state:{replay.get('state')!r}")

    replay_blockers = replay.get("blockers")
    if not isinstance(replay_blockers, list) or len(replay_blockers) != 1:
        issues.append("replay_blockers")
    else:
        blocker = replay_blockers[0]
        if not isinstance(blocker, dict):
            issues.append(f"replay_blocker_type:{type(blocker).__name__}")
        else:
            if blocker.get("id") != EXPECTED_REPLAY_BLOCKER_ID:
                issues.append(f"replay_blocker_id:{blocker.get('id')!r}")
            if blocker.get("kind") != "fixture_mismatch":
                issues.append(f"replay_blocker_kind:{blocker.get('kind')!r}")
            if blocker.get("path") != EXPECTED_REPLAY_BLOCKER_PATH:
                issues.append(f"replay_blocker_path:{blocker.get('path')!r}")
            if blocker.get("field") != EXPECTED_REPLAY_BLOCKER_FIELD:
                issues.append(f"replay_blocker_field:{blocker.get('field')!r}")
            if blocker.get("expected") is not EXPECTED_REPLAY_BLOCKER_EXPECTED:
                issues.append(f"replay_blocker_expected:{blocker.get('expected')!r}")
            if blocker.get("actual") is not EXPECTED_REPLAY_BLOCKER_ACTUAL:
                issues.append(f"replay_blocker_actual:{blocker.get('actual')!r}")
            evidence = blocker.get("evidence")
            if not isinstance(evidence, str) or "phase1_helpers.zig:595" not in evidence:
                issues.append("replay_blocker_evidence")

    c_harness = payload.get("c_harness")
    if not isinstance(c_harness, dict):
        return issues + [f"c_harness_type:{type(c_harness).__name__}"]
    if c_harness.get("path") != EXPECTED_C_HARNESS_PATH:
        issues.append(f"c_harness_path:{c_harness.get('path')!r}")
    if c_harness.get("state") != EXPECTED_C_HARNESS_STATE:
        issues.append(f"c_harness_state:{c_harness.get('state')!r}")
    if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
        issues.append("c_harness_reason")
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append(f"c_harness_helper_count:{c_harness.get('helper_count')!r}")
    if c_harness.get("helpers") != EXPECTED_HELPERS:
        issues.append("c_harness_helpers")
    if c_harness.get("blocker_id") != EXPECTED_C_HARNESS_BLOCKER_ID:
        issues.append(f"c_harness_blocker_id:{c_harness.get('blocker_id')!r}")

    missing_zig_helpers: list[str] = []
    present_c_sources: list[str] = []
    for helper, c_source in zip(EXPECTED_HELPERS, EXPECTED_C_SOURCES):
        if not (root / helper).exists():
            missing_zig_helpers.append(helper)
        if (root / c_source).exists():
            present_c_sources.append(c_source)
    if missing_zig_helpers:
        issues.append("missing_zig_helpers:" + ",".join(missing_zig_helpers))
    if present_c_sources:
        issues.append("unexpected_c_sources:" + ",".join(present_c_sources))

    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    blockers_issues, blockers_payload = _check_required_json_file(
        blockers_path(root), BLOCKERS_REL, "blockers"
    )
    issues.extend(blockers_issues)
    manifest_issues, manifest_payload = _check_required_json_file(
        manifest_path(root), MANIFEST_REL, "manifest"
    )
    issues.extend(manifest_issues)
    if blockers_payload is None or manifest_payload is None:
        return issues

    issues.extend(validate_manifest_payload(manifest_payload))
    issues.extend(validate_blockers_payload(blockers_payload, root))
    return issues


def assert_case(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_c_harness_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        assert_case("happy_path", validate_root(root) == [])
        covered.append("happy_path")

        sample_root = root / "sample-root"
        write_sample_root(sample_root)
        assert_case("write_sample_root", validate_root(sample_root) == [])
        covered.append("write_sample_root")

        missing_blockers_root = root / "missing-blockers-root"
        write_sample_root(missing_blockers_root)
        blockers_path(missing_blockers_root).unlink()
        assert_case(
            "missing_blockers_file",
            validate_root(missing_blockers_root)
            == [f"missing:blockers:{BLOCKERS_REL.as_posix()}"],
        )
        covered.append("missing_blockers_file")

        blockers_dir_root = root / "blockers-dir-root"
        write_sample_root(blockers_dir_root)
        blockers_path(blockers_dir_root).unlink()
        blockers_path(blockers_dir_root).mkdir(parents=True)
        assert_case(
            "blockers_path_is_directory",
            validate_root(blockers_dir_root)
            == [f"directory:blockers:{BLOCKERS_REL.as_posix()}"],
        )
        covered.append("blockers_path_is_directory")

        invalid_blockers_root = root / "invalid-blockers-root"
        write_sample_root(invalid_blockers_root)
        write_text(blockers_path(invalid_blockers_root), '{"status":\n')
        invalid_blockers_issues = validate_root(invalid_blockers_root)
        assert_case(
            "invalid_blockers_json",
            len(invalid_blockers_issues) == 1
            and invalid_blockers_issues[0].startswith("invalid_json:blockers:"),
        )
        covered.append("invalid_blockers_json")

        duplicate_blockers_root = root / "duplicate-blockers-root"
        write_sample_root(duplicate_blockers_root)
        write_text(
            blockers_path(duplicate_blockers_root),
            '{\n  "status": "parked",\n  "status": "blocked"\n}\n',
        )
        assert_case(
            "duplicate_blockers_keys",
            validate_root(duplicate_blockers_root)
            == ["duplicate_keys:blockers:status"],
        )
        covered.append("duplicate_blockers_keys")

        missing_manifest_root = root / "missing-manifest-root"
        write_sample_root(missing_manifest_root)
        manifest_path(missing_manifest_root).unlink()
        assert_case(
            "missing_manifest_file",
            validate_root(missing_manifest_root)
            == [f"missing:manifest:{MANIFEST_REL.as_posix()}"],
        )
        covered.append("missing_manifest_file")

        manifest_dir_root = root / "manifest-dir-root"
        write_sample_root(manifest_dir_root)
        manifest_path(manifest_dir_root).unlink()
        manifest_path(manifest_dir_root).mkdir(parents=True)
        assert_case(
            "manifest_path_is_directory",
            validate_root(manifest_dir_root)
            == [f"directory:manifest:{MANIFEST_REL.as_posix()}"],
        )
        covered.append("manifest_path_is_directory")

        invalid_manifest_root = root / "invalid-manifest-root"
        write_sample_root(invalid_manifest_root)
        write_text(manifest_path(invalid_manifest_root), '{"phase":\n')
        invalid_manifest_issues = validate_root(invalid_manifest_root)
        assert_case(
            "invalid_manifest_json",
            len(invalid_manifest_issues) == 1
            and invalid_manifest_issues[0].startswith("invalid_json:manifest:"),
        )
        covered.append("invalid_manifest_json")

        duplicate_manifest_root = root / "duplicate-manifest-root"
        write_sample_root(duplicate_manifest_root)
        write_text(
            manifest_path(duplicate_manifest_root),
            '{\n  "phase": "Phase 1",\n  "phase": "Phase 2"\n}\n',
        )
        assert_case(
            "duplicate_manifest_keys",
            validate_root(duplicate_manifest_root)
            == ["duplicate_keys:manifest:phase"],
        )
        covered.append("duplicate_manifest_keys")

        manifest_link_root = root / "manifest-link-root"
        write_sample_root(manifest_link_root)
        blockers_payload = build_blockers_payload()
        blockers_payload["lane_sequencing"]["manifest"] = "zigux/tests/fixtures/wrong.json"  # type: ignore[index]
        write_json(blockers_path(manifest_link_root), blockers_payload)
        assert_case(
            "blocker_manifest_link_drift",
            validate_root(manifest_link_root)
            == ["lane_manifest:'zigux/tests/fixtures/wrong.json'"],
        )
        covered.append("blocker_manifest_link_drift")

        shared_count_root = root / "shared-count-root"
        write_sample_root(shared_count_root)
        blockers_payload = build_blockers_payload()
        blockers_payload["lane_sequencing"]["shared_replay_parked_helper_count"] = 8  # type: ignore[index]
        write_json(blockers_path(shared_count_root), blockers_payload)
        assert_case(
            "shared_helper_count_drift",
            validate_root(shared_count_root) == ["shared_helper_count:8"],
        )
        covered.append("shared_helper_count_drift")

        replay_drift_root = root / "replay-drift-root"
        write_sample_root(replay_drift_root)
        blockers_payload = build_blockers_payload()
        blockers_payload["replay"]["blockers"][0]["field"] = "slab.zero_after_free"  # type: ignore[index]
        write_json(blockers_path(replay_drift_root), blockers_payload)
        assert_case(
            "replay_blocker_payload_drift",
            validate_root(replay_drift_root) == ["replay_blocker_field:'slab.zero_after_free'"],
        )
        covered.append("replay_blocker_payload_drift")

        c_harness_list_root = root / "c-harness-list-root"
        write_sample_root(c_harness_list_root)
        blockers_payload = build_blockers_payload()
        blockers_payload["c_harness"]["helpers"] = EXPECTED_HELPERS[:-1]  # type: ignore[index]
        write_json(blockers_path(c_harness_list_root), blockers_payload)
        assert_case(
            "c_harness_helper_list_drift",
            validate_root(c_harness_list_root) == ["c_harness_helpers"],
        )
        covered.append("c_harness_helper_list_drift")

        missing_zig_helper_root = root / "missing-zig-helper-root"
        write_sample_root(missing_zig_helper_root)
        (missing_zig_helper_root / EXPECTED_HELPERS[0]).unlink()
        assert_case(
            "missing_zig_helper",
            validate_root(missing_zig_helper_root)
            == [f"missing_zig_helpers:{EXPECTED_HELPERS[0]}"],
        )
        covered.append("missing_zig_helper")

        unexpected_c_source_root = root / "unexpected-c-source-root"
        write_sample_root(unexpected_c_source_root)
        c_path = unexpected_c_source_root / EXPECTED_C_SOURCES[0]
        write_text(c_path, "/* unexpected */\n")
        assert_case(
            "unexpected_c_source_present",
            validate_root(unexpected_c_source_root)
            == [f"unexpected_c_sources:{EXPECTED_C_SOURCES[0]}"],
        )
        covered.append("unexpected_c_source_present")

    assert_case("self_test_case_order", covered == SELF_TEST_CASES)
    print("PHASE1_C_HARNESS_BLOCKERS_SELF_TEST=pass")
    print(f"PHASE1_C_HARNESS_BLOCKERS_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE1_C_HARNESS_BLOCKERS_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the committed Phase 1 C-harness blocker contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate (defaults to the current checkout).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in checker self-test suite.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        target = args.write_sample_root.resolve()
        write_sample_root(target)
        print(f"PHASE1_C_HARNESS_BLOCKERS_SAMPLE_ROOT={target}")
        return 0

    root = args.root.resolve()
    issues = validate_root(root)
    if issues:
        print("PHASE1_C_HARNESS_BLOCKERS=fail")
        print(f"PHASE1_C_HARNESS_BLOCKERS_ROOT={root}")
        for issue in issues:
            print(f"PHASE1_C_HARNESS_BLOCKERS_ISSUE={issue}")
        return 1

    print("PHASE1_C_HARNESS_BLOCKERS=pass")
    print(f"PHASE1_C_HARNESS_BLOCKERS_ROOT={root}")
    print(f"PHASE1_C_HARNESS_BLOCKERS_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_C_HARNESS_BLOCKERS_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_C_HARNESS_BLOCKERS_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    print(f"PHASE1_C_HARNESS_BLOCKERS_MISSING_C_SOURCE_COUNT={len(EXPECTED_C_SOURCES)}")
    print(f"PHASE1_C_HARNESS_BLOCKERS_MANIFEST={MANIFEST_REL.as_posix()}")
    print("PHASE1_C_HARNESS_BLOCKERS_STATUS=parked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the current Phase 1 replay-blocker packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_replay_blockers.json",
)

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

EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_PATH = "tools/lib/slab.zig"
EXPECTED_REPLAY_BLOCKER_FIELD = "slab.zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_EVIDENCE = (
    "Focused 2026-05-17 scratch replay of `zig build test --build-file "
    "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` "
    "because the committed fixture expects `true` while `tools/lib/slab.zig` "
    "still produced `false`."
)

EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
    "that current master no longer ships beside the Phase 1 `.zig` ports."
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "keep the live owner map, the restored closure note and closure validator, "
        "the parked shared-replay-versus-direct-anchor split, the shipped bench "
        "checker, and the current Phase 1 reminder packet explicit from the docs "
        "root without rebuilding the broader host-tools closure stack from older "
        "missing validator and replay surfaces.",
        "keep the helper-family split explicit here too: the nine shared-replay "
        "parked helpers reopen only for packet drift, while bitmap, find_bit, "
        "rbtree, and string keep the only bounded direct-anchor follow-up anchors "
        "on current master.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,"
        "scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,"
        "zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,"
        "zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "This note keeps those broader companions parked as historical "
        "closure-stack vocabulary until direct current-master rereads restore them.",
    ),
    "scripts/zigux/README.md": (
        "repeated authenticated reads on current `master` still return missing for "
        "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, "
        "`scripts/zigux/check-phase1-installer-companion-checks.py`, "
        "`scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, "
        "`zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, "
        "`zigux/tests/fixtures/phase1_bench_expectations.json`, and "
        "`zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those "
        "installer-backed, older validator-first, parity, and replay routes as "
        "historical packet members that need fresh re-materialization before they "
        "are reused as direct current-`master` reminder evidence",
        "the current direct-anchor tie-breakers stay helper-local: bitmap, "
        "find_bit, rbtree, and string reopen only inside their existing "
        "helper-local anchors or already-committed shared fixture keys, while the "
        "other nine closed helpers stay parked unless the shared replay or "
        "reminder packet drifts",
    ),
    "zigux/tests/README.md": (
        "broader Phase 1 closure companions stay outside the narrow direct-readback "
        "packet: authenticated contents reads on current `master` still return "
        "missing for `scripts/zigux/validate-phase1.py`, "
        "`scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, "
        "`zigux/tests/phase1_bench.zig`, "
        "`zigux/tests/fixtures/phase1_bench_expectations.json`, and "
        "`zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree "
        "readback does rematerialize that validator-first, bench, and replay family "
        "on `master`, so keep those paths framed as broader closure companions "
        "rather than as active tests-root proof inside this direct-readback "
        "reminder packet",
        "keep the Phase 1 tests-root reminder truthful: the thirteen helper ports "
        "remain closed through the committed manifest, the nine shared-replay parked "
        "helpers reopen only for packet or fixture drift, and only "
        "`tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, "
        "and `tools/lib/string.zig` still keep bounded direct-anchor follow-up "
        "markers on current `master`",
    ),
}

SELF_TEST_CASES = [
    "happy_path",
    "write_sample_root",
    "missing_blockers_file",
    "invalid_blockers_json",
    "duplicate_blockers_keys",
    "missing_manifest_file",
    "duplicate_manifest_keys",
    "shared_helper_count_drift",
    "direct_helper_list_drift",
    "replay_blocker_field_drift",
    "c_harness_reason_drift",
    "missing_marker_surface",
    "missing_helper_placeholder",
]


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def read_json_with_duplicates(path: Path) -> object:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=DuplicateTrackingDict,
    )


def check_required_json_file(
    path: Path,
    label: str,
) -> tuple[list[str], object | None]:
    if not path.exists():
        return ([f"missing:{label}:{path}"], None)
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
        "status": "parked",
        "lane_sequencing": {
            "manifest": MANIFEST_REL.as_posix(),
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_HELPERS),
            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_ID,
                    "kind": "fixture_mismatch",
                    "path": EXPECTED_REPLAY_BLOCKER_PATH,
                    "field": EXPECTED_REPLAY_BLOCKER_FIELD,
                    "expected": True,
                    "actual": False,
                    "evidence": EXPECTED_REPLAY_BLOCKER_EVIDENCE,
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": EXPECTED_HELPERS,
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if relative_path == MANIFEST_REL.as_posix():
            write_json(path, build_manifest_payload())
        elif relative_path == BLOCKERS_REL.as_posix():
            write_json(path, build_blockers_payload())
        else:
            write_text(path, "\n".join(MARKERS[relative_path]) + "\n")
    for helper in EXPECTED_HELPERS:
        write_text(root / helper, "// placeholder\n")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def collect_marker_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in MARKERS.items():
        text = (root / relative_path).read_text(encoding="utf-8")
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                issues.append(f"marker:{relative_path}:expected_once:actual={count}")
    return issues


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
    if payload.get("status") != "parked":
        issues.append(f"blockers_status:{payload.get('status')!r}")

    lane_sequencing = payload.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return issues + [f"blockers_lane_sequencing_type:{type(lane_sequencing).__name__}"]
    if lane_sequencing.get("manifest") != MANIFEST_REL.as_posix():
        issues.append(f"blockers_manifest:{lane_sequencing.get('manifest')!r}")
    if lane_sequencing.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        issues.append(
            f"blockers_shared_helper_count:{lane_sequencing.get('shared_replay_parked_helper_count')!r}"
        )
    if lane_sequencing.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
        issues.append("blockers_shared_helpers")
    if lane_sequencing.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        issues.append(
            f"blockers_direct_helper_count:{lane_sequencing.get('direct_anchor_followup_helper_count')!r}"
        )
    if lane_sequencing.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        issues.append("blockers_direct_helpers")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append("blockers_anti_overlap_rule")

    replay = payload.get("replay")
    if not isinstance(replay, dict):
        return issues + [f"replay_type:{type(replay).__name__}"]
    if replay.get("path") != "zigux/tests/phase1_helpers.zig":
        issues.append(f"replay_path:{replay.get('path')!r}")
    if replay.get("state") != "blocked":
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
            if blocker.get("expected") is not True:
                issues.append(f"replay_blocker_expected:{blocker.get('expected')!r}")
            if blocker.get("actual") is not False:
                issues.append(f"replay_blocker_actual:{blocker.get('actual')!r}")
            if blocker.get("evidence") != EXPECTED_REPLAY_BLOCKER_EVIDENCE:
                issues.append("replay_blocker_evidence")

    c_harness = payload.get("c_harness")
    if not isinstance(c_harness, dict):
        return issues + [f"c_harness_type:{type(c_harness).__name__}"]
    if c_harness.get("path") != "zigux/tests/fixtures/phase1_helpers_c_harness.c":
        issues.append(f"c_harness_path:{c_harness.get('path')!r}")
    if c_harness.get("state") != "blocked":
        issues.append(f"c_harness_state:{c_harness.get('state')!r}")
    if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
        issues.append("c_harness_reason")
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append(f"c_harness_helper_count:{c_harness.get('helper_count')!r}")
    if c_harness.get("helpers") != EXPECTED_HELPERS:
        issues.append("c_harness_helpers")
    if c_harness.get("blocker_id") != EXPECTED_C_HARNESS_BLOCKER_ID:
        issues.append(f"c_harness_blocker_id:{c_harness.get('blocker_id')!r}")

    missing_helpers = [helper for helper in EXPECTED_HELPERS if not (root / helper).is_file()]
    if missing_helpers:
        issues.append("missing_helpers:" + ",".join(missing_helpers))

    return issues


def validate_root(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    issues.extend(collect_marker_issues(root))

    manifest_issues, manifest_payload = check_required_json_file(root / MANIFEST_REL, "manifest")
    blockers_issues, blockers_payload = check_required_json_file(root / BLOCKERS_REL, "blockers")
    issues.extend(manifest_issues)
    issues.extend(blockers_issues)
    if manifest_payload is None or blockers_payload is None:
        return issues

    issues.extend(validate_manifest_payload(manifest_payload))
    issues.extend(validate_blockers_payload(blockers_payload, root))
    return issues


def assert_case(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_replay_blocker_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_repo(root)

        assert_case("happy_path", validate_root(root) == [])
        covered.append("happy_path")

        sample_root = root / "sample-root"
        build_sample_repo(sample_root)
        assert_case("write_sample_root", validate_root(sample_root) == [])
        covered.append("write_sample_root")

        missing_blockers_root = root / "missing-blockers-root"
        build_sample_repo(missing_blockers_root)
        (missing_blockers_root / BLOCKERS_REL).unlink()
        assert_case(
            "missing_blockers_file",
            validate_root(missing_blockers_root) == [f"missing_file:{BLOCKERS_REL.as_posix()}"],
        )
        covered.append("missing_blockers_file")

        invalid_blockers_root = root / "invalid-blockers-root"
        build_sample_repo(invalid_blockers_root)
        write_text(invalid_blockers_root / BLOCKERS_REL, '{"status":\n')
        issues = validate_root(invalid_blockers_root)
        assert_case(
            "invalid_blockers_json",
            len(issues) == 1 and issues[0].startswith("invalid_json:blockers:"),
        )
        covered.append("invalid_blockers_json")

        duplicate_blockers_root = root / "duplicate-blockers-root"
        build_sample_repo(duplicate_blockers_root)
        write_text(
            duplicate_blockers_root / BLOCKERS_REL,
            '{\n  "status": "parked",\n  "status": "blocked"\n}\n',
        )
        assert_case(
            "duplicate_blockers_keys",
            validate_root(duplicate_blockers_root) == ["duplicate_keys:blockers:status"],
        )
        covered.append("duplicate_blockers_keys")

        missing_manifest_root = root / "missing-manifest-root"
        build_sample_repo(missing_manifest_root)
        (missing_manifest_root / MANIFEST_REL).unlink()
        assert_case(
            "missing_manifest_file",
            validate_root(missing_manifest_root) == [f"missing_file:{MANIFEST_REL.as_posix()}"],
        )
        covered.append("missing_manifest_file")

        duplicate_manifest_root = root / "duplicate-manifest-root"
        build_sample_repo(duplicate_manifest_root)
        write_text(
            duplicate_manifest_root / MANIFEST_REL,
            '{\n  "phase": "Phase 1",\n  "phase": "Phase 2"\n}\n',
        )
        assert_case(
            "duplicate_manifest_keys",
            validate_root(duplicate_manifest_root) == ["duplicate_keys:manifest:phase"],
        )
        covered.append("duplicate_manifest_keys")

        shared_helper_count_root = root / "shared-helper-count-root"
        build_sample_repo(shared_helper_count_root)
        payload = build_blockers_payload()
        payload["lane_sequencing"]["shared_replay_parked_helper_count"] = 8  # type: ignore[index]
        write_json(shared_helper_count_root / BLOCKERS_REL, payload)
        assert_case(
            "shared_helper_count_drift",
            validate_root(shared_helper_count_root) == ["blockers_shared_helper_count:8"],
        )
        covered.append("shared_helper_count_drift")

        direct_helper_list_root = root / "direct-helper-list-root"
        build_sample_repo(direct_helper_list_root)
        payload = build_blockers_payload()
        payload["lane_sequencing"]["direct_anchor_followup_helpers"] = EXPECTED_DIRECT_HELPERS[:-1]  # type: ignore[index]
        write_json(direct_helper_list_root / BLOCKERS_REL, payload)
        assert_case(
            "direct_helper_list_drift",
            validate_root(direct_helper_list_root) == ["blockers_direct_helpers"],
        )
        covered.append("direct_helper_list_drift")

        replay_blocker_field_root = root / "replay-blocker-field-root"
        build_sample_repo(replay_blocker_field_root)
        payload = build_blockers_payload()
        payload["replay"]["blockers"][0]["field"] = "slab.zero_after_free"  # type: ignore[index]
        write_json(replay_blocker_field_root / BLOCKERS_REL, payload)
        assert_case(
            "replay_blocker_field_drift",
            validate_root(replay_blocker_field_root) == ["replay_blocker_field:'slab.zero_after_free'"],
        )
        covered.append("replay_blocker_field_drift")

        c_harness_reason_root = root / "c-harness-reason-root"
        build_sample_repo(c_harness_reason_root)
        payload = build_blockers_payload()
        payload["c_harness"]["reason"] = "host-side parity drift"  # type: ignore[index]
        write_json(c_harness_reason_root / BLOCKERS_REL, payload)
        assert_case(
            "c_harness_reason_drift",
            validate_root(c_harness_reason_root) == ["c_harness_reason"],
        )
        covered.append("c_harness_reason_drift")

        missing_marker_root = root / "missing-marker-root"
        build_sample_repo(missing_marker_root)
        target = missing_marker_root / "zigux/tests/README.md"
        marker = MARKERS["zigux/tests/README.md"][0]
        target.write_text(target.read_text(encoding="utf-8").replace(marker + "\n", "", 1), encoding="utf-8")
        issues = validate_root(missing_marker_root)
        assert_case(
            "missing_marker_surface",
            len(issues) == 1 and issues[0] == "marker:zigux/tests/README.md:expected_once:actual=0",
        )
        covered.append("missing_marker_surface")

        missing_helper_root = root / "missing-helper-root"
        build_sample_repo(missing_helper_root)
        (missing_helper_root / EXPECTED_HELPERS[0]).unlink()
        assert_case(
            "missing_helper_placeholder",
            validate_root(missing_helper_root) == [f"missing_helpers:{EXPECTED_HELPERS[0]}"],
        )
        covered.append("missing_helper_placeholder")

    assert_case("self_test_case_order", covered == SELF_TEST_CASES)
    print("PHASE1_REPLAY_BLOCKER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_REPLAY_BLOCKER_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE1_REPLAY_BLOCKER_PACKET_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for focused checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        build_sample_repo(sample_root)
        print(f"PHASE1_REPLAY_BLOCKER_PACKET_SAMPLE_ROOT={sample_root}")
        return 0

    root = repo_root(args.root)
    issues = validate_root(root)
    if issues:
        print("PHASE1_REPLAY_BLOCKER_PACKET=fail")
        print(f"PHASE1_REPLAY_BLOCKER_PACKET_ROOT={root}")
        for issue in issues:
            print(f"PHASE1_REPLAY_BLOCKER_PACKET_ISSUE={issue}")
        return 1

    print("PHASE1_REPLAY_BLOCKER_PACKET=pass")
    print(f"PHASE1_REPLAY_BLOCKER_PACKET_ROOT={root}")
    print(f"PHASE1_REPLAY_BLOCKER_PACKET_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_REPLAY_BLOCKER_PACKET_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_REPLAY_BLOCKER_PACKET_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
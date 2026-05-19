#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
EXPECTED_STATUS = "parked"
EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_C_HARNESS_STATE = "blocked"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
    "that current master no longer ships beside the Phase 1 `.zig` ports."
)
EXPECTED_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
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
EXPECTED_C_SOURCES = [helper.replace(".zig", ".c") for helper in EXPECTED_HELPERS]
SELF_TEST_CASES = [
    "happy_path",
    "missing_blockers_file",
    "status_drift",
    "path_drift",
    "state_drift",
    "reason_drift",
    "blocker_id_drift",
    "helper_count_drift",
    "helper_list_drift",
    "missing_zig_helper",
    "unexpected_c_source_present",
]


def blockers_path(root: Path) -> Path:
    return root / BLOCKERS_REL


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_blockers(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def build_sample_root(root: Path) -> None:
    payload = {
        "status": EXPECTED_STATUS,
        "lane_sequencing": {
            "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
            "shared_replay_parked_helper_count": 9,
            "shared_replay_parked_helpers": [
                "tools/lib/argv_split.zig",
                "tools/lib/cmdline.zig",
                "tools/lib/ctype.zig",
                "tools/lib/hweight.zig",
                "tools/lib/list_sort.zig",
                "tools/lib/slab.zig",
                "tools/lib/str_error_r.zig",
                "tools/lib/vsprintf.zig",
                "tools/lib/zalloc.zig",
            ],
            "direct_anchor_followup_helper_count": 4,
            "direct_anchor_followup_helpers": [
                "tools/lib/bitmap.zig",
                "tools/lib/find_bit.zig",
                "tools/lib/rbtree.zig",
                "tools/lib/string.zig",
            ],
            "anti_overlap_rule": (
                "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
                "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
                "helpers reopen only for their existing helper-local anchors or already-committed "
                "shared fixture keys."
            ),
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
                    "evidence": "sample",
                }
            ],
        },
        "c_harness": {
            "path": EXPECTED_C_HARNESS_PATH,
            "state": EXPECTED_C_HARNESS_STATE,
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": EXPECTED_HELPERS,
            "blocker_id": EXPECTED_BLOCKER_ID,
        },
    }
    write_json(blockers_path(root), payload)
    for helper in EXPECTED_HELPERS:
        helper_path = root / helper
        helper_path.parent.mkdir(parents=True, exist_ok=True)
        helper_path.write_text("// placeholder\n", encoding="utf-8")


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    path = blockers_path(root)
    if not path.exists():
        return [f"missing:{BLOCKERS_REL.as_posix()}"]

    try:
        payload = load_blockers(path)
    except json.JSONDecodeError as exc:
        return [f"invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(payload, dict):
        return [f"payload_type:{type(payload).__name__}"]

    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"status:{payload.get('status')!r}")

    c_harness = payload.get("c_harness")
    if not isinstance(c_harness, dict):
        return issues + [f"c_harness_type:{type(c_harness).__name__}"]

    if c_harness.get("path") != EXPECTED_C_HARNESS_PATH:
        issues.append(f"c_harness_path:{c_harness.get('path')!r}")
    if c_harness.get("state") != EXPECTED_C_HARNESS_STATE:
        issues.append(f"c_harness_state:{c_harness.get('state')!r}")
    if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
        issues.append("c_harness_reason")
    if c_harness.get("blocker_id") != EXPECTED_BLOCKER_ID:
        issues.append(f"c_harness_blocker_id:{c_harness.get('blocker_id')!r}")

    helper_count = c_harness.get("helper_count")
    if helper_count != len(EXPECTED_HELPERS):
        issues.append(f"helper_count:{helper_count!r}")

    helpers = c_harness.get("helpers")
    if helpers != EXPECTED_HELPERS:
        issues.append("helpers")
        return issues

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


def assert_case(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_c_harness_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert_case("happy_path", validate_root(root) == [])
        covered.append("happy_path")

        missing_root = root / "missing-root"
        assert_case(
            "missing_blockers_file",
            validate_root(missing_root) == [f"missing:{BLOCKERS_REL.as_posix()}"],
        )
        covered.append("missing_blockers_file")

        payload = load_blockers(blockers_path(root))
        assert isinstance(payload, dict)

        payload["status"] = "open"
        write_json(blockers_path(root), payload)
        assert_case("status_drift", validate_root(root) == ["status:'open'"])
        covered.append("status_drift")

        build_sample_root(root)
        payload = load_blockers(blockers_path(root))
        assert isinstance(payload, dict)
        payload["c_harness"]["path"] = "zigux/tests/fixtures/wrong.c"  # type: ignore[index]
        write_json(blockers_path(root), payload)
        assert_case(
            "path_drift",
            validate_root(root) == ["c_harness_path:'zigux/tests/fixtures/wrong.c'"],
        )
        covered.append("path_drift")

        build_sample_root(root)
        payload = load_blockers(blockers_path(root))
        assert isinstance(payload, dict)
        payload["c_harness"]["state"] = "open"  # type: ignore[index]
        write_json(blockers_path(root), payload)
        assert_case(
            "state_drift",
            validate_root(root) == ["c_harness_state:'open'"],
        )
        covered.append("state_drift")

        build_sample_root(root)
        payload = load_blockers(blockers_path(root))
        assert isinstance(payload, dict)
        payload["c_harness"]["reason"] = "drifted"  # type: ignore[index]
        write_json(blockers_path(root), payload)
        assert_case("reason_drift", validate_root(root) == ["c_harness_reason"])
        covered.append("reason_drift")

        build_sample_root(root)
        payload = load_blockers(blockers_path(root))
        assert isinstance(payload, dict)
        payload["c_harness"]["blocker_id"] = "wrong"  # type: ignore[index]
        write_json(blockers_path(root), payload)
        assert_case(
            "blocker_id_drift",
            validate_root(root) == ["c_harness_blocker_id:'wrong'"],
        )
        covered.append("blocker_id_drift")

        build_sample_root(root)
        payload = load_blockers(blockers_path(root))
        assert isinstance(payload, dict)
        payload["c_harness"]["helper_count"] = 12  # type: ignore[index]
        write_json(blockers_path(root), payload)
        assert_case("helper_count_drift", validate_root(root) == ["helper_count:12"])
        covered.append("helper_count_drift")

        build_sample_root(root)
        payload = load_blockers(blockers_path(root))
        assert isinstance(payload, dict)
        payload["c_harness"]["helpers"] = EXPECTED_HELPERS[:-1]  # type: ignore[index]
        write_json(blockers_path(root), payload)
        assert_case("helper_list_drift", validate_root(root) == ["helpers"])
        covered.append("helper_list_drift")

        build_sample_root(root)
        (root / EXPECTED_HELPERS[0]).unlink()
        assert_case(
            "missing_zig_helper",
            validate_root(root)
            == [f"missing_zig_helpers:{EXPECTED_HELPERS[0]}"],
        )
        covered.append("missing_zig_helper")

        build_sample_root(root)
        c_path = root / EXPECTED_C_SOURCES[0]
        c_path.parent.mkdir(parents=True, exist_ok=True)
        c_path.write_text("/* unexpected */\n", encoding="utf-8")
        assert_case(
            "unexpected_c_source_present",
            validate_root(root)
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
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(args.root.resolve())
    if issues:
        print("PHASE1_C_HARNESS_BLOCKERS=fail")
        print(f"PHASE1_C_HARNESS_BLOCKERS_ROOT={args.root.resolve()}")
        for issue in issues:
            print(f"PHASE1_C_HARNESS_BLOCKERS_ISSUE={issue}")
        return 1

    print("PHASE1_C_HARNESS_BLOCKERS=pass")
    print(f"PHASE1_C_HARNESS_BLOCKERS_ROOT={args.root.resolve()}")
    print(f"PHASE1_C_HARNESS_BLOCKERS_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_C_HARNESS_BLOCKERS_MISSING_C_SOURCE_COUNT={len(EXPECTED_C_SOURCES)}")
    print("PHASE1_C_HARNESS_BLOCKERS_STATUS=parked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

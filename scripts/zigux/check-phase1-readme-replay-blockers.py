#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README_REL = Path("scripts") / "zigux" / "README.md"
BLOCKERS_REL = Path("zigux") / "tests" / "fixtures" / "phase1_replay_blockers.json"

REQUIRED_README_GAPS = [
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
]
REQUIRED_DIRECT_README_MARKER = (
    "bitmap, find_bit, rbtree, and string reopen only inside their existing "
    "helper-local anchors or already-committed shared fixture keys"
)
ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)
SHARED_HELPERS = [
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
DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]
ALL_HELPERS = SHARED_HELPERS + DIRECT_HELPERS
SLAB_BLOCKER = {
    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
    "kind": "fixture_mismatch",
    "path": "tools/lib/slab.zig",
    "field": "slab.zero_after_kmalloc",
    "expected": True,
    "actual": False,
}
SELF_TEST_CASES = [
    "round_trip",
    "missing_gap_marker",
    "missing_direct_marker",
    "shared_count_drift",
    "shared_overlap_drift",
    "helper_union_drift",
    "replay_state_drift",
    "c_harness_reason_drift",
    "slab_blocker_drift",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check the current Phase 1 scripts-root replay-blocker reminder "
            "against the committed replay-blocker packet."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sample_readme_text() -> str:
    lines = [
        "# scripts/zigux",
        "",
        "## Phase 1",
        "",
        "- repeated authenticated reads on current `master` still return missing for "
        + ", ".join(f"`{marker}`" for marker in REQUIRED_README_GAPS)
        + ", so treat those validator, parity, replay, and C-harness routes as "
        + "historical packet members that need fresh re-materialization before they "
        + "are reused as direct current-`master` reminder evidence",
        "- the current direct-anchor tie-breakers stay helper-local: "
        + REQUIRED_DIRECT_README_MARKER,
        "",
    ]
    return "\n".join(lines)


def sample_blockers_payload() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
            "shared_replay_parked_helper_count": len(SHARED_HELPERS),
            "shared_replay_parked_helpers": SHARED_HELPERS,
            "direct_anchor_followup_helper_count": len(DIRECT_HELPERS),
            "direct_anchor_followup_helpers": DIRECT_HELPERS,
            "anti_overlap_rule": ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
            "blockers": [
                {
                    **SLAB_BLOCKER,
                    "evidence": (
                        "Focused scratch replay failed because the committed fixture "
                        "expects true while tools/lib/slab.zig still produced false."
                    ),
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": (
                "The old host-side parity route still depends on helper "
                "`tools/lib/*.c` inputs that current master no longer ships beside "
                "the Phase 1 `.zig` ports."
            ),
            "helper_count": len(ALL_HELPERS),
            "helpers": ALL_HELPERS,
            "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
        },
    }


def write_sample_root(root: Path) -> None:
    write_text(root / README_REL, sample_readme_text())
    write_text(
        root / BLOCKERS_REL,
        json.dumps(sample_blockers_payload(), indent=2, sort_keys=False) + "\n",
    )


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, object]:
    return json.loads(load_text(path))


def validate(root: Path) -> list[str]:
    readme_path = root / README_REL
    blockers_path = root / BLOCKERS_REL
    ensure(readme_path.exists(), f"missing required file: {README_REL}")
    ensure(blockers_path.exists(), f"missing required file: {BLOCKERS_REL}")

    readme_text = load_text(readme_path)
    for marker in REQUIRED_README_GAPS:
        ensure(marker in readme_text, f"missing README gap marker: {marker}")
    ensure(
        REQUIRED_DIRECT_README_MARKER in readme_text,
        "missing README direct-anchor marker",
    )

    blockers = load_json(blockers_path)
    ensure(blockers.get("status") == "parked", "status must stay parked")

    lane = blockers.get("lane_sequencing")
    ensure(isinstance(lane, dict), "lane_sequencing must be an object")
    ensure(
        lane.get("manifest") == "zigux/tests/fixtures/phase1_helper_manifest.json",
        "lane manifest path drifted",
    )
    ensure(
        lane.get("shared_replay_parked_helper_count") == len(SHARED_HELPERS),
        "shared helper count drifted",
    )
    ensure(
        lane.get("direct_anchor_followup_helper_count") == len(DIRECT_HELPERS),
        "direct helper count drifted",
    )
    ensure(
        lane.get("shared_replay_parked_helpers") == SHARED_HELPERS,
        "shared helper roster drifted",
    )
    ensure(
        lane.get("direct_anchor_followup_helpers") == DIRECT_HELPERS,
        "direct helper roster drifted",
    )
    ensure(
        lane.get("anti_overlap_rule") == ANTI_OVERLAP_RULE,
        "anti-overlap rule drifted",
    )

    shared = lane["shared_replay_parked_helpers"]
    direct = lane["direct_anchor_followup_helpers"]
    ensure(
        set(shared).isdisjoint(direct),
        "shared and direct helper rosters must stay disjoint",
    )

    replay = blockers.get("replay")
    ensure(isinstance(replay, dict), "replay must be an object")
    ensure(replay.get("path") == "zigux/tests/phase1_helpers.zig", "replay path drifted")
    ensure(replay.get("state") == "blocked", "replay state must stay blocked")
    replay_blockers = replay.get("blockers")
    ensure(isinstance(replay_blockers, list) and replay_blockers, "replay blockers missing")
    slab = replay_blockers[0]
    ensure(isinstance(slab, dict), "slab blocker must be an object")
    for key, value in SLAB_BLOCKER.items():
        ensure(slab.get(key) == value, f"slab blocker field drifted: {key}")

    c_harness = blockers.get("c_harness")
    ensure(isinstance(c_harness, dict), "c_harness must be an object")
    ensure(
        c_harness.get("path") == "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        "c_harness path drifted",
    )
    ensure(c_harness.get("state") == "blocked", "c_harness state must stay blocked")
    ensure(
        c_harness.get("reason")
        == "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.",
        "c_harness reason drifted",
    )
    ensure(c_harness.get("helper_count") == len(ALL_HELPERS), "c_harness helper count drifted")
    ensure(c_harness.get("helpers") == ALL_HELPERS, "c_harness helper roster drifted")
    ensure(
        c_harness.get("blocker_id") == "phase1_helpers_c_harness_missing_c_sources",
        "c_harness blocker id drifted",
    )

    ensure("bitmap, find_bit, rbtree, and string" in readme_text, "README direct helper names drifted")

    return [
        "PHASE1_README_REPLAY_BLOCKERS=pass",
        f"PHASE1_README_REPLAY_BLOCKERS_GAP_COUNT={len(REQUIRED_README_GAPS)}",
        f"PHASE1_README_REPLAY_BLOCKERS_SHARED_HELPER_COUNT={len(SHARED_HELPERS)}",
        f"PHASE1_README_REPLAY_BLOCKERS_DIRECT_HELPER_COUNT={len(DIRECT_HELPERS)}",
        f"PHASE1_README_REPLAY_BLOCKERS_REPLAY_STATE={replay['state']}",
        f"PHASE1_README_REPLAY_BLOCKERS_C_HARNESS_STATE={c_harness['state']}",
    ]


def expect_failure(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected failure for {label}")


def run_self_test() -> int:
    covered: list[str] = []

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_readme_replay_blockers_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        expected_lines = [
            "PHASE1_README_REPLAY_BLOCKERS=pass",
            "PHASE1_README_REPLAY_BLOCKERS_GAP_COUNT=4",
            "PHASE1_README_REPLAY_BLOCKERS_SHARED_HELPER_COUNT=9",
            "PHASE1_README_REPLAY_BLOCKERS_DIRECT_HELPER_COUNT=4",
            "PHASE1_README_REPLAY_BLOCKERS_REPLAY_STATE=blocked",
            "PHASE1_README_REPLAY_BLOCKERS_C_HARNESS_STATE=blocked",
        ]
        ensure(validate(root) == expected_lines, "round-trip validation drifted")
        covered.append("round_trip")

        readme_path = root / README_REL
        blockers_path = root / BLOCKERS_REL

        original_readme = load_text(readme_path)
        original_blockers = load_json(blockers_path)

        write_text(readme_path, original_readme.replace(REQUIRED_README_GAPS[0], "scripts/zigux/validate-phase1-old.py"))
        expect_failure("missing_gap_marker", lambda: validate(root))
        write_text(readme_path, original_readme)
        covered.append("missing_gap_marker")

        write_text(readme_path, original_readme.replace(REQUIRED_DIRECT_README_MARKER, "stale direct helper marker"))
        expect_failure("missing_direct_marker", lambda: validate(root))
        write_text(readme_path, original_readme)
        covered.append("missing_direct_marker")

        drift = json.loads(json.dumps(original_blockers))
        drift["lane_sequencing"]["shared_replay_parked_helper_count"] = 8
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("shared_count_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("shared_count_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["lane_sequencing"]["direct_anchor_followup_helpers"][0] = SHARED_HELPERS[0]
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("shared_overlap_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("shared_overlap_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["c_harness"]["helpers"] = SHARED_HELPERS
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("helper_union_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("helper_union_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["replay"]["state"] = "ready"
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("replay_state_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("replay_state_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["c_harness"]["reason"] = "stale reason"
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("c_harness_reason_drift", lambda: validate(root))
        write_text(blockers_path, json.dumps(original_blockers, indent=2) + "\n")
        covered.append("c_harness_reason_drift")

        drift = json.loads(json.dumps(original_blockers))
        drift["replay"]["blockers"][0]["actual"] = True
        write_text(blockers_path, json.dumps(drift, indent=2) + "\n")
        expect_failure("slab_blocker_drift", lambda: validate(root))
        covered.append("slab_blocker_drift")

    ensure(covered == SELF_TEST_CASES, f"self-test catalog drifted: {covered}")
    print("PHASE1_README_REPLAY_BLOCKERS_SELF_TEST=pass")
    print(f"PHASE1_README_REPLAY_BLOCKERS_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE1_README_REPLAY_BLOCKERS_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0
    if args.self_test:
        return run_self_test()
    for line in validate(args.root.resolve()):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

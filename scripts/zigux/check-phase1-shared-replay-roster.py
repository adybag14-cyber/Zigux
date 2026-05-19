#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

EXPECTED_SECTION_ORDER = [
    "argv_split",
    "bitmap",
    "cmdline",
    "ctype",
    "find_bit",
    "hweight",
    "list_sort",
    "rbtree",
    "slab",
    "str_error_r",
    "string",
    "vsprintf",
    "zalloc",
]

SECTION_TO_HELPER = {
    "argv_split": "tools/lib/argv_split.zig",
    "bitmap": "tools/lib/bitmap.zig",
    "cmdline": "tools/lib/cmdline.zig",
    "ctype": "tools/lib/ctype.zig",
    "find_bit": "tools/lib/find_bit.zig",
    "hweight": "tools/lib/hweight.zig",
    "list_sort": "tools/lib/list_sort.zig",
    "rbtree": "tools/lib/rbtree.zig",
    "slab": "tools/lib/slab.zig",
    "str_error_r": "tools/lib/str_error_r.zig",
    "string": "tools/lib/string.zig",
    "vsprintf": "tools/lib/vsprintf.zig",
    "zalloc": "tools/lib/zalloc.zig",
}

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

EXPECTED_SHARED_SECTION_ORDER = [
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "slab",
    "str_error_r",
    "vsprintf",
    "zalloc",
]

EXPECTED_DIRECT_SECTION_ORDER = [
    "bitmap",
    "find_bit",
    "rbtree",
    "string",
]

EXPECTED_BLOCKER_IDS = {
    "phase1_helpers_zig_slab_zero_after_kmalloc",
    "phase1_helpers_c_harness_missing_c_sources",
}


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_root(root: Path) -> dict[str, int]:
    fixture_path = root / FIXTURE_REL
    blockers_path = root / BLOCKERS_REL

    if not fixture_path.exists():
        raise SystemExit(f"missing fixture file: {fixture_path}")
    if not blockers_path.exists():
        raise SystemExit(f"missing replay-blocker file: {blockers_path}")

    fixture = load_json(fixture_path)
    blockers = load_json(blockers_path)
    if not isinstance(fixture, dict):
        raise SystemExit(f"fixture must be a JSON object: {fixture_path}")
    if not isinstance(blockers, dict):
        raise SystemExit(f"replay blockers must be a JSON object: {blockers_path}")

    errors: list[str] = []

    section_order = list(fixture.keys())
    require(
        section_order == EXPECTED_SECTION_ORDER,
        "phase1 fixture section order drifted from the committed helper roster",
        errors,
    )

    section_to_helper_values = [SECTION_TO_HELPER[section] for section in EXPECTED_SECTION_ORDER]
    require(
        len(set(section_order)) == len(section_order),
        "phase1 fixture sections must stay unique",
        errors,
    )

    lane_sequencing = blockers.get("lane_sequencing")
    require(isinstance(lane_sequencing, dict), "lane_sequencing must stay present", errors)
    if isinstance(lane_sequencing, dict):
        shared_helpers = lane_sequencing.get("shared_replay_parked_helpers")
        direct_helpers = lane_sequencing.get("direct_anchor_followup_helpers")
        require(
            lane_sequencing.get("manifest") == "zigux/tests/fixtures/phase1_helper_manifest.json",
            "lane_sequencing.manifest must keep pointing at phase1_helper_manifest.json",
            errors,
        )
        require(
            lane_sequencing.get("shared_replay_parked_helper_count") == len(EXPECTED_SHARED_HELPERS),
            "shared replay helper count drifted",
            errors,
        )
        require(
            lane_sequencing.get("direct_anchor_followup_helper_count") == len(EXPECTED_DIRECT_HELPERS),
            "direct helper count drifted",
            errors,
        )
        require(
            shared_helpers == EXPECTED_SHARED_HELPERS,
            "shared replay helper roster drifted",
            errors,
        )
        require(
            direct_helpers == EXPECTED_DIRECT_HELPERS,
            "direct helper roster drifted",
            errors,
        )
        anti_overlap_rule = lane_sequencing.get("anti_overlap_rule")
        require(
            isinstance(anti_overlap_rule, str)
            and "shared-replay parked helpers reopen only for packet drift" in anti_overlap_rule
            and "direct-anchor helpers reopen only for their existing helper-local anchors" in anti_overlap_rule,
            "anti-overlap rule lost the shared-versus-direct lane boundary wording",
            errors,
        )
        if isinstance(shared_helpers, list) and isinstance(direct_helpers, list):
            require(
                set(shared_helpers).isdisjoint(set(direct_helpers)),
                "shared and direct helper rosters must stay disjoint",
                errors,
            )
            shared_from_sections = [
                SECTION_TO_HELPER[section] for section in EXPECTED_SHARED_SECTION_ORDER
            ]
            direct_from_sections = [
                SECTION_TO_HELPER[section] for section in EXPECTED_DIRECT_SECTION_ORDER
            ]
            require(
                shared_helpers == shared_from_sections,
                "shared helper roster no longer matches the shared replay section order",
                errors,
            )
            require(
                direct_helpers == direct_from_sections,
                "direct helper roster no longer matches the direct helper section order",
                errors,
            )
            require(
                set(shared_helpers) | set(direct_helpers) == set(section_to_helper_values),
                "shared and direct helper rosters must still cover the full Phase 1 helper set",
                errors,
            )

    require(blockers.get("status") == "parked", "replay blocker status must stay parked", errors)

    replay = blockers.get("replay")
    require(isinstance(replay, dict), "replay metadata must stay present", errors)
    if isinstance(replay, dict):
        require(
            replay.get("path") == "zigux/tests/phase1_helpers.zig",
            "replay path drifted away from phase1_helpers.zig",
            errors,
        )
        require(replay.get("state") == "blocked", "replay state must stay blocked", errors)
        replay_blockers = replay.get("blockers")
        require(isinstance(replay_blockers, list) and len(replay_blockers) == 1, "replay blocker list drifted", errors)
        if isinstance(replay_blockers, list) and replay_blockers:
            blocker = replay_blockers[0]
            require(
                isinstance(blocker, dict) and blocker.get("id") == "phase1_helpers_zig_slab_zero_after_kmalloc",
                "slab replay blocker id drifted",
                errors,
            )
            require(
                isinstance(blocker, dict)
                and blocker.get("path") == "tools/lib/slab.zig"
                and blocker.get("field") == "slab.zero_after_kmalloc",
                "slab replay blocker path or field drifted",
                errors,
            )

    c_harness = blockers.get("c_harness")
    require(isinstance(c_harness, dict), "c_harness metadata must stay present", errors)
    if isinstance(c_harness, dict):
        helpers = c_harness.get("helpers")
        require(
            c_harness.get("path") == "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "c_harness path drifted",
            errors,
        )
        require(c_harness.get("state") == "blocked", "c_harness state must stay blocked", errors)
        require(
            c_harness.get("helper_count") == len(section_to_helper_values),
            "c_harness helper count drifted",
            errors,
        )
        require(
            helpers == section_to_helper_values,
            "c_harness helper roster no longer matches the Phase 1 fixture order",
            errors,
        )
        reason = c_harness.get("reason")
        require(
            isinstance(reason, str)
            and "tools/lib/*.c" in reason
            and "current master no longer ships" in reason,
            "c_harness reason lost the missing-C-source explanation",
            errors,
        )
        require(
            c_harness.get("blocker_id") == "phase1_helpers_c_harness_missing_c_sources",
            "c_harness blocker id drifted",
            errors,
        )

    if errors:
        raise SystemExit("\n".join(errors))

    return {
        "section_count": len(section_order),
        "helper_count": len(section_to_helper_values),
        "shared_helper_count": len(EXPECTED_SHARED_HELPERS),
        "direct_helper_count": len(EXPECTED_DIRECT_HELPERS),
        "blocked_replay_count": len(EXPECTED_BLOCKER_IDS),
    }


def build_sample_root(root: Path) -> None:
    fixture_path = root / FIXTURE_REL
    blockers_path = root / BLOCKERS_REL
    fixture_path.parent.mkdir(parents=True, exist_ok=True)

    fixture = {
        "argv_split": {"argc": 3},
        "bitmap": {"weight": 3},
        "cmdline": {"decimal_k": {"value": 65536, "rest": " rest"}},
        "ctype": {"mask_A": 65},
        "find_bit": {"bits_per_long": 64},
        "hweight": {"w8": 4},
        "list_sort": {"tri_sorted_keys": [1, 1, 2, 3, 3]},
        "rbtree": {"empty_root": True},
        "slab": {"zero_after_kmalloc": True},
        "str_error_r": {"enoent": "No such file or directory"},
        "string": {"strtobool_y": True},
        "vsprintf": {"scnprintf_text": "zigux:7"},
        "zalloc": {"zeroed": True},
    }
    blockers = {
        "status": "parked",
        "lane_sequencing": {
            "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
            "shared_replay_parked_helper_count": 9,
            "shared_replay_parked_helpers": EXPECTED_SHARED_HELPERS,
            "direct_anchor_followup_helper_count": 4,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_HELPERS,
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
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": (
                "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
                "that current master no longer ships beside the Phase 1 `.zig` ports."
            ),
            "helper_count": 13,
            "helpers": [SECTION_TO_HELPER[section] for section in EXPECTED_SECTION_ORDER],
            "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
        },
    }

    fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)

        result = check_root(root)
        cases += 1
        assert result["section_count"] == 13
        assert result["helper_count"] == 13
        assert result["shared_helper_count"] == 9
        assert result["direct_helper_count"] == 4
        assert result["blocked_replay_count"] == 2

        blockers_path = root / BLOCKERS_REL
        blockers = load_json(blockers_path)

        blockers["lane_sequencing"]["shared_replay_parked_helper_count"] = 8
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "shared replay helper count drifted" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected shared helper count failure")

        build_sample_root(root)
        blockers = load_json(blockers_path)
        blockers["lane_sequencing"]["shared_replay_parked_helpers"] = EXPECTED_SHARED_HELPERS[:-1]
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "shared replay helper roster drifted" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected shared helper roster failure")

        build_sample_root(root)
        fixture_path = root / FIXTURE_REL
        fixture = load_json(fixture_path)
        reordered_sections = ["bitmap", "argv_split"] + [
            section for section in EXPECTED_SECTION_ORDER if section not in {"bitmap", "argv_split"}
        ]
        reordered_fixture = {section: fixture[section] for section in reordered_sections}
        fixture_path.write_text(json.dumps(reordered_fixture, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "phase1 fixture section order drifted" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected fixture section order failure")

        build_sample_root(root)
        blockers = load_json(blockers_path)
        blockers["c_harness"]["helpers"] = blockers["c_harness"]["helpers"][:-1]
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "c_harness helper roster no longer matches" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected c_harness roster failure")

        build_sample_root(root)
        blockers = load_json(blockers_path)
        blockers["replay"]["blockers"][0]["field"] = "slab.other_field"
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "slab replay blocker path or field drifted" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected slab blocker field failure")

        build_sample_root(root)
        blockers = load_json(blockers_path)
        blockers["lane_sequencing"]["anti_overlap_rule"] = "shared replay stays here"
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "anti-overlap rule lost" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected anti-overlap rule failure")

    print("PHASE1_SHARED_REPLAY_ROSTER_SELF_TEST=pass")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the shared replay helper roster contract for Phase 1 fixtures."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate (default: repository containing this script).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in self-test suite.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    result = check_root(args.root.resolve())
    print("PHASE1_SHARED_REPLAY_ROSTER=pass")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_SECTION_COUNT={result['section_count']}")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_HELPER_COUNT={result['helper_count']}")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_SHARED_HELPER_COUNT={result['shared_helper_count']}")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_DIRECT_HELPER_COUNT={result['direct_helper_count']}")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_BLOCKED_REPLAY_COUNT={result['blocked_replay_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

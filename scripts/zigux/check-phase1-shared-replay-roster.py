#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

EXPECTED_SECTION_ORDER = [
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
]

SECTION_TO_HELPER = {
    "find_bit": "tools/lib/find_bit.zig",
    "bitmap": "tools/lib/bitmap.zig",
    "string": "tools/lib/string.zig",
    "rbtree": "tools/lib/rbtree.zig",
    "argv_split": "tools/lib/argv_split.zig",
    "cmdline": "tools/lib/cmdline.zig",
    "ctype": "tools/lib/ctype.zig",
    "hweight": "tools/lib/hweight.zig",
    "list_sort": "tools/lib/list_sort.zig",
    "zalloc": "tools/lib/zalloc.zig",
    "str_error_r": "tools/lib/str_error_r.zig",
    "slab": "tools/lib/slab.zig",
    "vsprintf": "tools/lib/vsprintf.zig",
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

EXPECTED_SHARED_SECTIONS = {
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
}

EXPECTED_DIRECT_SECTIONS = {
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
}

EXPECTED_LANE_MANIFEST = "zigux/tests/fixtures/phase1_helper_manifest.json"
EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)
EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_FIELD = "slab.zero_after_kmalloc"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs "
    "that current master no longer ships beside the Phase 1 `.zig` ports."
)


class ValidationError(Exception):
    pass


def repo_root_from_arg(root_arg: Path | None) -> Path:
    if root_arg is None:
        return ROOT
    return root_arg.resolve()


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_object(path: Path, label: str) -> dict[str, object]:
    if not path.exists():
        raise ValidationError(f"missing {label}: {path}")
    if not path.is_file():
        raise ValidationError(f"{label} is not a file: {path}")

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except ValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise ValidationError(f"malformed {label}: {path}: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ValidationError(f"{label} must be a JSON object: {path}")
    return payload


def require(condition: bool, message: str, issues: list[str]) -> None:
    if not condition:
        issues.append(message)


def collect_issues(root: Path) -> list[str]:
    fixture = load_json_object(root / FIXTURE_REL, "phase1 fixture")
    manifest = load_json_object(root / MANIFEST_REL, "phase1 helper manifest")
    blockers = load_json_object(root / BLOCKERS_REL, "phase1 replay blockers")

    issues: list[str] = []

    section_order = list(fixture.keys())
    require(
        section_order == EXPECTED_SECTION_ORDER,
        "phase1 fixture section order drifted from the committed helper roster",
        issues,
    )
    require(
        len(set(section_order)) == len(section_order),
        "phase1 fixture sections must stay unique",
        issues,
    )

    section_helpers = [SECTION_TO_HELPER[section] for section in EXPECTED_SECTION_ORDER]
    manifest_helpers = manifest.get("helpers")
    require(isinstance(manifest_helpers, list), "manifest helper roster must stay present", issues)
    if isinstance(manifest_helpers, list):
        require(
            manifest.get("helper_count") == len(manifest_helpers),
            "manifest helper count drifted",
            issues,
        )
        require(
            set(manifest_helpers) == set(section_helpers),
            "manifest helper roster no longer covers the committed phase1 helper set",
            issues,
        )

    require(blockers.get("status") == "parked", "replay blocker status must stay parked", issues)

    lane_sequencing = blockers.get("lane_sequencing")
    require(isinstance(lane_sequencing, dict), "lane_sequencing must stay present", issues)
    if isinstance(lane_sequencing, dict):
        shared_helpers = lane_sequencing.get("shared_replay_parked_helpers")
        direct_helpers = lane_sequencing.get("direct_anchor_followup_helpers")

        require(
            lane_sequencing.get("manifest") == EXPECTED_LANE_MANIFEST,
            "lane_sequencing.manifest drifted",
            issues,
        )
        require(
            lane_sequencing.get("shared_replay_parked_helper_count") == len(EXPECTED_SHARED_HELPERS),
            "shared replay helper count drifted",
            issues,
        )
        require(
            lane_sequencing.get("direct_anchor_followup_helper_count") == len(EXPECTED_DIRECT_HELPERS),
            "direct helper count drifted",
            issues,
        )
        require(
            shared_helpers == EXPECTED_SHARED_HELPERS,
            "shared replay helper roster drifted",
            issues,
        )
        require(
            direct_helpers == EXPECTED_DIRECT_HELPERS,
            "direct helper roster drifted",
            issues,
        )
        require(
            lane_sequencing.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE,
            "anti-overlap rule drifted",
            issues,
        )

        if isinstance(shared_helpers, list) and isinstance(direct_helpers, list):
            require(
                set(shared_helpers).isdisjoint(set(direct_helpers)),
                "shared and direct helper rosters must stay disjoint",
                issues,
            )
            require(
                EXPECTED_SHARED_SECTIONS.issubset(set(section_order)),
                "shared replay sections drifted out of the committed phase1 fixture",
                issues,
            )
            require(
                EXPECTED_DIRECT_SECTIONS.issubset(set(section_order)),
                "direct-anchor sections drifted out of the committed phase1 fixture",
                issues,
            )
            require(
                set(shared_helpers) | set(direct_helpers) == set(section_helpers),
                "shared and direct helper rosters no longer cover the full helper set",
                issues,
            )

    replay = blockers.get("replay")
    require(isinstance(replay, dict), "replay metadata must stay present", issues)
    if isinstance(replay, dict):
        require(
            replay.get("path") == "zigux/tests/phase1_helpers.zig",
            "replay path drifted away from phase1_helpers.zig",
            issues,
        )
        require(replay.get("state") == "blocked", "replay state must stay blocked", issues)
        replay_blockers = replay.get("blockers")
        require(
            isinstance(replay_blockers, list) and len(replay_blockers) == 1,
            "replay blocker list drifted",
            issues,
        )
        if isinstance(replay_blockers, list) and replay_blockers:
            blocker = replay_blockers[0]
            require(
                isinstance(blocker, dict) and blocker.get("id") == EXPECTED_REPLAY_BLOCKER_ID,
                "slab replay blocker id drifted",
                issues,
            )
            require(
                isinstance(blocker, dict)
                and blocker.get("path") == "tools/lib/slab.zig"
                and blocker.get("field") == EXPECTED_REPLAY_BLOCKER_FIELD,
                "slab replay blocker path or field drifted",
                issues,
            )

    c_harness = blockers.get("c_harness")
    require(isinstance(c_harness, dict), "c_harness metadata must stay present", issues)
    if isinstance(c_harness, dict):
        helpers = c_harness.get("helpers")
        require(
            c_harness.get("path") == "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "c_harness path drifted",
            issues,
        )
        require(c_harness.get("state") == "blocked", "c_harness state must stay blocked", issues)
        require(
            c_harness.get("helper_count") == len(section_helpers),
            "c_harness helper count drifted",
            issues,
        )
        require(
            c_harness.get("reason") == EXPECTED_C_HARNESS_REASON,
            "c_harness reason drifted",
            issues,
        )
        require(
            c_harness.get("blocker_id") == EXPECTED_C_HARNESS_BLOCKER_ID,
            "c_harness blocker id drifted",
            issues,
        )
        if isinstance(helpers, list):
            require(
                set(helpers) == set(section_helpers),
                "c_harness helper roster no longer covers the committed phase1 helper set",
                issues,
            )
            if isinstance(manifest_helpers, list):
                require(
                    helpers == manifest_helpers,
                    "c_harness helper roster no longer matches the manifest helper order",
                    issues,
                )

    return issues


def build_current_like_root(root: Path) -> None:
    fixture_path = root / FIXTURE_REL
    manifest_path = root / MANIFEST_REL
    blockers_path = root / BLOCKERS_REL
    fixture_path.parent.mkdir(parents=True, exist_ok=True)

    for path in (fixture_path, manifest_path, blockers_path):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    fixture = {section: {"present": True} for section in EXPECTED_SECTION_ORDER}
    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(section_helpers := [SECTION_TO_HELPER[section] for section in EXPECTED_SECTION_ORDER]),
        "helpers": [
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
        ],
    }
    blockers = {
        "status": "parked",
        "lane_sequencing": {
            "manifest": EXPECTED_LANE_MANIFEST,
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
                    "path": "tools/lib/slab.zig",
                    "field": EXPECTED_REPLAY_BLOCKER_FIELD,
                    "expected": True,
                    "actual": False,
                    "evidence": "current-master-shaped sample",
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_SECTION_ORDER),
            "helpers": manifest["helpers"],
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }

    fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_shared_replay_roster_") as tmp_dir:
        root = Path(tmp_dir)
        build_current_like_root(root)

        issues = collect_issues(root)
        assert issues == [], issues
        cases += 1

        blockers_path = root / BLOCKERS_REL
        fixture_path = root / FIXTURE_REL

        blockers = json.loads(blockers_path.read_text(encoding="utf-8"))
        blockers["lane_sequencing"]["shared_replay_parked_helper_count"] = 8
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        assert "shared replay helper count drifted" in collect_issues(root)
        cases += 1

        build_current_like_root(root)
        blockers = json.loads(blockers_path.read_text(encoding="utf-8"))
        blockers["lane_sequencing"]["shared_replay_parked_helpers"] = EXPECTED_SHARED_HELPERS[:-1]
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        assert "shared replay helper roster drifted" in collect_issues(root)
        cases += 1

        build_current_like_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        reordered_sections = ["bitmap", "find_bit"] + [
            section
            for section in EXPECTED_SECTION_ORDER
            if section not in {"bitmap", "find_bit"}
        ]
        reordered_fixture = {section: fixture[section] for section in reordered_sections}
        fixture_path.write_text(json.dumps(reordered_fixture, indent=2) + "\n", encoding="utf-8")
        assert "phase1 fixture section order drifted from the committed helper roster" in collect_issues(root)
        cases += 1

        build_current_like_root(root)
        blockers = json.loads(blockers_path.read_text(encoding="utf-8"))
        blockers["c_harness"]["helpers"] = blockers["c_harness"]["helpers"][:-1]
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        assert "c_harness helper roster no longer covers the committed phase1 helper set" in collect_issues(root)
        cases += 1

        build_current_like_root(root)
        blockers = json.loads(blockers_path.read_text(encoding="utf-8"))
        helpers = blockers["c_harness"]["helpers"]
        blockers["c_harness"]["helpers"] = helpers[1:] + helpers[:1]
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        assert "c_harness helper roster no longer matches the manifest helper order" in collect_issues(root)
        cases += 1

        build_current_like_root(root)
        blockers = json.loads(blockers_path.read_text(encoding="utf-8"))
        blockers["replay"]["blockers"][0]["field"] = "slab.other_field"
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        assert "slab replay blocker path or field drifted" in collect_issues(root)
        cases += 1

        build_current_like_root(root)
        blockers = json.loads(blockers_path.read_text(encoding="utf-8"))
        blockers["lane_sequencing"]["anti_overlap_rule"] = "shared replay stays here"
        blockers_path.write_text(json.dumps(blockers, indent=2) + "\n", encoding="utf-8")
        assert "anti-overlap rule drifted" in collect_issues(root)
        cases += 1

        build_current_like_root(root)
        (root / FIXTURE_REL).unlink()
        try:
            collect_issues(root)
        except ValidationError as exc:
            assert "missing phase1 fixture" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected missing fixture failure")

        build_current_like_root(root)
        (root / BLOCKERS_REL).unlink()
        (root / BLOCKERS_REL).mkdir(parents=False)
        try:
            collect_issues(root)
        except ValidationError as exc:
            assert "phase1 replay blockers is not a file" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected replay blocker directory failure")

        build_current_like_root(root)
        fixture_path.write_text("{invalid", encoding="utf-8")
        try:
            collect_issues(root)
        except ValidationError as exc:
            assert "malformed phase1 fixture" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected malformed fixture failure")

        build_current_like_root(root)
        (root / MANIFEST_REL).unlink()
        try:
            collect_issues(root)
        except ValidationError as exc:
            assert "missing phase1 helper manifest" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected missing manifest failure")

        build_current_like_root(root)
        blockers_path.write_text('{"status":"parked","status":"drift"}', encoding="utf-8")
        try:
            collect_issues(root)
        except ValidationError as exc:
            assert "duplicate JSON key: status" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected duplicate-key failure")

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
        help="Repository root to validate. Defaults to the repository containing this script.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in self-test suite.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-master-shaped sample root to the given directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_current_like_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(repo_root_from_arg(args.root))
    if issues:
        print("PHASE1_SHARED_REPLAY_ROSTER=fail")
        print("PHASE1_SHARED_REPLAY_ROSTER_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_SHARED_REPLAY_ROSTER_ISSUES_END")
        return 1

    print("PHASE1_SHARED_REPLAY_ROSTER=pass")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_SECTION_COUNT={len(EXPECTED_SECTION_ORDER)}")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_HELPER_COUNT={len(SECTION_TO_HELPER)}")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_SHARED_REPLAY_ROSTER_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    print("PHASE1_SHARED_REPLAY_ROSTER_BLOCKED_REPLAY_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
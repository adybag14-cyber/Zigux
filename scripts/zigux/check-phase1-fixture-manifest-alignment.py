#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

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
EXPECTED_SECTION_ORDER = [Path(helper).stem for helper in EXPECTED_HELPERS]
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
EXPECTED_MANIFEST_PATH = "zigux/tests/fixtures/phase1_helper_manifest.json"
EXPECTED_PHASE = "Phase 1"
EXPECTED_STATUS = "closed"


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def load_json(root: Path, rel: Path) -> dict[str, object]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def collect_issues(
    fixture: dict[str, object],
    manifest: dict[str, object],
    blockers: dict[str, object],
) -> list[str]:
    issues: list[str] = []

    if list(fixture.keys()) != EXPECTED_SECTION_ORDER:
        issues.append("fixture:section_order")

    if manifest.get("phase") != EXPECTED_PHASE:
        issues.append("manifest:phase")
    if manifest.get("status") != EXPECTED_STATUS:
        issues.append("manifest:status")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        issues.append("manifest:helpers")

    manifest_lane = manifest.get("lane_sequencing")
    if not isinstance(manifest_lane, dict):
        issues.append("manifest:lane_sequencing")
    else:
        if manifest_lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
            issues.append("manifest:shared_helpers")
        if manifest_lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
            issues.append("manifest:direct_helpers")

    blockers_lane = blockers.get("lane_sequencing")
    if not isinstance(blockers_lane, dict):
        issues.append("blockers:lane_sequencing")
    else:
        if blockers_lane.get("manifest") != EXPECTED_MANIFEST_PATH:
            issues.append("blockers:manifest_path")
        if blockers_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
            issues.append("blockers:shared_helper_count")
        if blockers_lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
            issues.append("blockers:shared_helpers")
        if blockers_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
            issues.append("blockers:direct_helper_count")
        if blockers_lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
            issues.append("blockers:direct_helpers")

    c_harness = blockers.get("c_harness")
    if not isinstance(c_harness, dict):
        issues.append("blockers:c_harness")
    else:
        if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
            issues.append("blockers:c_harness_helper_count")
        if c_harness.get("helpers") != EXPECTED_HELPERS:
            issues.append("blockers:c_harness_helpers")

    return issues


def write_json(root: Path, rel: Path, payload: dict[str, object]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def good_fixture() -> dict[str, object]:
    return {name: {} for name in EXPECTED_SECTION_ORDER}


def good_manifest() -> dict[str, object]:
    return {
        "phase": EXPECTED_PHASE,
        "status": EXPECTED_STATUS,
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": copy.deepcopy(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": copy.deepcopy(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helpers": copy.deepcopy(EXPECTED_DIRECT_HELPERS),
        },
    }


def good_blockers() -> dict[str, object]:
    return {
        "lane_sequencing": {
            "manifest": EXPECTED_MANIFEST_PATH,
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_HELPERS),
            "shared_replay_parked_helpers": copy.deepcopy(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
            "direct_anchor_followup_helpers": copy.deepcopy(EXPECTED_DIRECT_HELPERS),
        },
        "c_harness": {
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": copy.deepcopy(EXPECTED_HELPERS),
        },
    }


def write_good_repo(root: Path) -> None:
    write_json(root, FIXTURE_REL, good_fixture())
    write_json(root, MANIFEST_REL, good_manifest())
    write_json(root, BLOCKERS_REL, good_blockers())


def load_triplet(root: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    return (
        load_json(root, FIXTURE_REL),
        load_json(root, MANIFEST_REL),
        load_json(root, BLOCKERS_REL),
    )


def assert_issue_case(root: Path, mutate, expected_issue: str) -> None:
    mutate()
    issues = collect_issues(*load_triplet(root))
    assert expected_issue in issues, issues
    write_good_repo(root)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_fixture_manifest_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        write_good_repo(root)
        assert collect_issues(*load_triplet(root)) == []

        fixture_path = root / FIXTURE_REL
        manifest_path = root / MANIFEST_REL
        blockers_path = root / BLOCKERS_REL

        def load_manifest_payload() -> dict[str, object]:
            return json.loads(manifest_path.read_text(encoding="utf-8"))

        def load_blockers() -> dict[str, object]:
            return json.loads(blockers_path.read_text(encoding="utf-8"))

        assert_issue_case(
            root,
            lambda: write_json(
                root,
                FIXTURE_REL,
                {"bitmap": {}, **{name: {} for name in EXPECTED_SECTION_ORDER if name != "bitmap"}},
            ),
            "fixture:section_order",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: write_json(root, MANIFEST_REL, {**load_manifest_payload(), "helper_count": 12}),
            "manifest:helper_count",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda payload: (
                    payload["lane_sequencing"].update(
                        {"shared_replay_parked_helpers": payload["lane_sequencing"]["shared_replay_parked_helpers"][:-1]}
                    ),
                    write_json(root, MANIFEST_REL, payload),
                )
            )(load_manifest_payload()),
            "manifest:shared_helpers",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda payload: (
                    payload["lane_sequencing"].update({"direct_anchor_followup_helper_count": 3}),
                    write_json(root, BLOCKERS_REL, payload),
                )
            )(load_blockers()),
            "blockers:direct_helper_count",
        )
        case_count += 1

        assert_issue_case(
            root,
            lambda: (
                lambda payload: (
                    payload["c_harness"].update({"helpers": payload["c_harness"]["helpers"][:-1]}),
                    write_json(root, BLOCKERS_REL, payload),
                )
            )(load_blockers()),
            "blockers:c_harness_helpers",
        )
        case_count += 1

    print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate alignment across the Phase 1 fixture, helper manifest, and replay blockers."
    )
    parser.add_argument("--self-test", action="store_true", help="Run embedded checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux checkout root.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(*load_triplet(repo_root(args.root)))
    if issues:
        print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT=fail")
        print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE1_FIXTURE_MANIFEST_ALIGNMENT=pass")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SECTION_COUNT={len(EXPECTED_SECTION_ORDER)}")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_FIXTURE_MANIFEST_ALIGNMENT_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

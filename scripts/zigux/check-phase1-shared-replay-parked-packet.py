#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
REPLAY_BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
TESTS_README_REL = Path("zigux/tests/README.md")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")

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
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_FIXTURE_SECTION_KEYS = [
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

EXPECTED_SMOKE_MARKERS = [
    'const argv_split = @import("argv_split");',
    'const cmdline = @import("cmdline");',
    'const ctype = @import("ctype");',
    'const hweight = @import("hweight");',
    'const list_sort = @import("list_sort");',
    'const slab = @import("slab");',
    'const str_error_r = @import("str_error_r");',
    'const vsprintf = @import("vsprintf");',
    'const zalloc = @import("zalloc");',
    'var split = try argv_split.argv_split(std.testing.allocator, "  zigux   host\\ttools  ");',
    'const parsed = cmdline.memparse("64K tail");',
    "try std.testing.expect(ctype.isalpha('Q'));",
    "try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(0xf0f0_f0f0));",
    "list_sort.listSort(null, &list_head, list_cmp);",
    "const allocated = slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;",
    'try std.testing.expectEqualStrings("Permission denied", str_error_r.strErrorR(13, &error_buffer));',
    'const rendered_len = vsprintf.scnprintf(&render_buffer, "{s}:{d}", .{ "zigux", 9 });',
    "var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);",
]

EXPECTED_TESTS_README_MARKERS = [
    "keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    "broader Phase 1 closure companions stay outside the narrow direct-readback packet",
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
]

EXPECTED_CLOSURE_MARKERS = [
    "- `PHASE1_STATUS=parked`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
    "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
]

EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected top-level JSON object")
    return data


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_manifest() -> dict:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS + EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }


def sample_replay_blockers() -> dict:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": str(MANIFEST_REL),
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
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
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.",
            "helper_count": 13,
            "helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS + EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }


def sample_fixture() -> dict:
    return {key: {"sample": True} for key in EXPECTED_FIXTURE_SECTION_KEYS}


def sample_smoke() -> str:
    return "\n".join(EXPECTED_SMOKE_MARKERS) + "\n"


def sample_tests_readme() -> str:
    return "\n".join(["# zigux/tests", *EXPECTED_TESTS_README_MARKERS]) + "\n"


def sample_closure() -> str:
    return "\n".join(["# Phase 1 Closure", *EXPECTED_CLOSURE_MARKERS]) + "\n"


def write_sample_root(root: Path) -> None:
    write_text(root / MANIFEST_REL, json.dumps(sample_manifest(), indent=2) + "\n")
    write_text(root / REPLAY_BLOCKERS_REL, json.dumps(sample_replay_blockers(), indent=2) + "\n")
    write_text(root / FIXTURE_REL, json.dumps(sample_fixture(), indent=2) + "\n")
    write_text(root / SMOKE_REL, sample_smoke())
    write_text(root / TESTS_README_REL, sample_tests_readme())
    write_text(root / CLOSURE_REL, sample_closure())


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    manifest = load_json(root / MANIFEST_REL)
    replay_blockers = load_json(root / REPLAY_BLOCKERS_REL)
    fixture = load_json(root / FIXTURE_REL)
    smoke_text = (root / SMOKE_REL).read_text(encoding="utf-8")
    tests_readme = (root / TESTS_README_REL).read_text(encoding="utf-8")
    closure_text = (root / CLOSURE_REL).read_text(encoding="utf-8")

    lane = manifest.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("manifest:lane_sequencing=dict")
    else:
        if lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_REPLAY_PARKED_HELPERS:
            issues.append("manifest:shared_replay_parked_helpers")
        if lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS:
            issues.append("manifest:direct_anchor_followup_helpers")
        if lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
            issues.append("manifest:anti_overlap_rule")

    if replay_blockers.get("status") != "parked":
        issues.append("replay_blockers:status=parked")
    blocker_lane = replay_blockers.get("lane_sequencing")
    if not isinstance(blocker_lane, dict):
        issues.append("replay_blockers:lane_sequencing=dict")
    else:
        if blocker_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS):
            issues.append("replay_blockers:shared_replay_parked_helper_count")
        if blocker_lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_REPLAY_PARKED_HELPERS:
            issues.append("replay_blockers:shared_replay_parked_helpers")
        if blocker_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS):
            issues.append("replay_blockers:direct_anchor_followup_helper_count")
        if blocker_lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS:
            issues.append("replay_blockers:direct_anchor_followup_helpers")
        if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
            issues.append("replay_blockers:anti_overlap_rule")

    replay = replay_blockers.get("replay")
    if not isinstance(replay, dict):
        issues.append("replay_blockers:replay=dict")
    else:
        if replay.get("state") != "blocked":
            issues.append("replay_blockers:replay.state=blocked")
        blockers = replay.get("blockers")
        if not isinstance(blockers, list) or not blockers:
            issues.append("replay_blockers:replay.blockers=list")
        else:
            blocker = blockers[0]
            if not isinstance(blocker, dict) or blocker.get("id") != EXPECTED_REPLAY_BLOCKER_ID:
                issues.append("replay_blockers:replay.blockers[0].id")

    c_harness = replay_blockers.get("c_harness")
    if not isinstance(c_harness, dict):
        issues.append("replay_blockers:c_harness=dict")
    else:
        if c_harness.get("state") != "blocked":
            issues.append("replay_blockers:c_harness.state=blocked")
        if c_harness.get("helper_count") != 13:
            issues.append("replay_blockers:c_harness.helper_count=13")
        if c_harness.get("helpers") != EXPECTED_SHARED_REPLAY_PARKED_HELPERS + EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS:
            issues.append("replay_blockers:c_harness.helpers")
        if c_harness.get("blocker_id") != EXPECTED_C_HARNESS_BLOCKER_ID:
            issues.append("replay_blockers:c_harness.blocker_id")

    if sorted(fixture.keys()) != sorted(EXPECTED_FIXTURE_SECTION_KEYS):
        issues.append("fixture:section_keys")

    for marker in EXPECTED_SMOKE_MARKERS:
        if marker not in smoke_text:
            issues.append(f"smoke:missing_marker:{marker}")

    for marker in EXPECTED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            issues.append(f"tests_readme:missing_marker:{marker}")

    for marker in EXPECTED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(f"closure:missing_marker:{marker}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_shared_replay_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        manifest_path = root / MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["shared_replay_parked_helpers"].pop()
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert "manifest:shared_replay_parked_helpers" in collect_issues(root)
        write_sample_root(root)
        case_count += 1

        replay_path = root / REPLAY_BLOCKERS_REL
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        replay["replay"]["state"] = "pass"
        write_text(replay_path, json.dumps(replay, indent=2) + "\n")
        assert "replay_blockers:replay.state=blocked" in collect_issues(root)
        write_sample_root(root)
        case_count += 1

        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        replay["c_harness"]["blocker_id"] = "wrong"
        write_text(replay_path, json.dumps(replay, indent=2) + "\n")
        assert "replay_blockers:c_harness.blocker_id" in collect_issues(root)
        write_sample_root(root)
        case_count += 1

        fixture_path = root / FIXTURE_REL
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture.pop("slab")
        write_text(fixture_path, json.dumps(fixture, indent=2) + "\n")
        assert "fixture:section_keys" in collect_issues(root)
        write_sample_root(root)
        case_count += 1

        smoke_path = root / SMOKE_REL
        write_text(smoke_path, (root / SMOKE_REL).read_text(encoding="utf-8").replace("const slab = @import(\"slab\");\n", ""))
        issues = collect_issues(root)
        assert any(issue.startswith("smoke:missing_marker:const slab = @import(\"slab\");") for issue in issues), issues
        write_sample_root(root)
        case_count += 1

        tests_readme_path = root / TESTS_README_REL
        write_text(
            tests_readme_path,
            (root / TESTS_README_REL).read_text(encoding="utf-8").replace(
                "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\n",
                "",
            ),
        )
        issues = collect_issues(root)
        assert any(issue.startswith("tests_readme:missing_marker:current shared Phase 1 smoke route") for issue in issues), issues
        write_sample_root(root)
        case_count += 1

        closure_path = root / CLOSURE_REL
        write_text(
            closure_path,
            (root / CLOSURE_REL).read_text(encoding="utf-8").replace("- `PHASE1_STATUS=parked`\n", ""),
        )
        issues = collect_issues(root)
        assert any(issue.startswith("closure:missing_marker:- `PHASE1_STATUS=parked`") for issue in issues), issues
        case_count += 1

    print("PHASE1_SHARED_REPLAY_PARKED_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_REPLAY_PARKED_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 shared-replay parked-helper packet."
    )
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run embedded self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample repo root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_SHARED_REPLAY_PARKED_PACKET_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    issues = collect_issues(root)
    if issues:
        print("PHASE1_SHARED_REPLAY_PARKED_PACKET=fail")
        print("PHASE1_SHARED_REPLAY_PARKED_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_SHARED_REPLAY_PARKED_PACKET_ISSUES_END")
        return 1

    print("PHASE1_SHARED_REPLAY_PARKED_PACKET=pass")
    print(f"PHASE1_SHARED_REPLAY_PARKED_HELPER_COUNT={len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}")
    print(f"PHASE1_DIRECT_ANCHOR_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(f"PHASE1_FIXTURE_SECTION_COUNT={len(EXPECTED_FIXTURE_SECTION_KEYS)}")
    print(f"PHASE1_SMOKE_MARKER_COUNT={len(EXPECTED_SMOKE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

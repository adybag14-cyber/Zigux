#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")

EXPECTED_SECTIONS = (
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
)

EXPECTED_HELPERS = (
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
)

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_LANE_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

EXPECTED_FIXTURE_VALUES = {
    ("string", "strtobool_invalid"): 184,
    ("slab", "zero_after_kmalloc"): True,
    ("list_sort", "tri_sorted_ordinals"): [1, 3, 0, 2, 4],
}

REPLAY_IMPORTS = (
    'const argv_split = @import("argv_split");',
    'const bitmap = @import("bitmap");',
    'const cmdline = @import("cmdline");',
    'const ctype = @import("ctype");',
    'const find_bit = @import("find_bit");',
    'const hweight = @import("hweight");',
    'const list_sort = @import("list_sort");',
    'const rbtree = @import("rbtree");',
    'const slab = @import("slab");',
    'const str_error_r = @import("str_error_r");',
    'const string = @import("string");',
    'const vsprintf = @import("vsprintf");',
    'const zalloc = @import("zalloc");',
)

REPLAY_ANCHORS = (
    '@embedFile("fixtures/phase1_helpers.json")',
    ".ignore_unknown_fields = true,",
    'test "phase 1 helper modules import cleanly"',
    'test "phase 1 helper ports match committed parity fixture"',
)

ARTIFACT_DIFF_MARKERS = (
    "ARTIFACT_DIFF_SELF_TEST=pass",
    "MODE=text",
    "MODE=json",
    "MODE=sha256",
)

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> object:
    return json.loads(_read_text(path))


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    artifact_diff = root / ARTIFACT_DIFF_REL
    fixture = root / FIXTURE_REL
    manifest = root / MANIFEST_REL
    blockers = root / BLOCKERS_REL
    replay = root / REPLAY_REL

    for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL):
        if not (root / rel).exists():
            issues.append(f"missing:{rel.as_posix()}")

    if issues:
        return issues

    artifact_diff_text = _read_text(artifact_diff)
    for marker in ARTIFACT_DIFF_MARKERS:
        if marker not in artifact_diff_text:
            issues.append(f"artifact_diff_marker:{marker}")

    fixture_payload = _read_json(fixture)
    if not isinstance(fixture_payload, dict):
        issues.append("fixture:not_json_object")
    else:
        actual_sections = tuple(fixture_payload.keys())
        if actual_sections != EXPECTED_SECTIONS:
            issues.append(
                "fixture_sections:"
                + ",".join(actual_sections)
                + "!="
                + ",".join(EXPECTED_SECTIONS)
            )
        for (section, key), expected_value in EXPECTED_FIXTURE_VALUES.items():
            actual_section = fixture_payload.get(section)
            if not isinstance(actual_section, dict):
                issues.append(f"fixture_section:{section}")
                continue
            actual_value = actual_section.get(key)
            if actual_value != expected_value:
                issues.append(
                    f"fixture_value:{section}.{key}={actual_value!r}!={expected_value!r}"
                )

    manifest_payload = _read_json(manifest)
    if not isinstance(manifest_payload, dict):
        issues.append("manifest:not_json_object")
    else:
        if manifest_payload.get("phase") != "Phase 1":
            issues.append(f"manifest_phase:{manifest_payload.get('phase')!r}")
        if manifest_payload.get("status") != "closed":
            issues.append(f"manifest_status:{manifest_payload.get('status')!r}")
        if manifest_payload.get("helper_count") != len(EXPECTED_HELPERS):
            issues.append(f"manifest_helper_count:{manifest_payload.get('helper_count')!r}")
        if manifest_payload.get("helpers") != list(EXPECTED_HELPERS):
            issues.append("manifest_helpers")

        lane_sequencing = manifest_payload.get("lane_sequencing")
        if not isinstance(lane_sequencing, dict):
            issues.append("manifest_lane_sequencing:not_json_object")
        else:
            if lane_sequencing.get("shared_replay_parked_helpers") != list(
                EXPECTED_SHARED_REPLAY_PARKED_HELPERS
            ):
                issues.append("manifest_shared_replay_parked_helpers")
            if lane_sequencing.get("direct_anchor_followup_helpers") != list(
                EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS
            ):
                issues.append("manifest_direct_anchor_followup_helpers")
            if lane_sequencing.get("rule_summary") != EXPECTED_LANE_RULE_SUMMARY:
                issues.append("manifest_lane_rule_summary")
            if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
                issues.append("manifest_lane_anti_overlap_rule")

    blockers_payload = _read_json(blockers)
    if not isinstance(blockers_payload, dict):
        issues.append("blockers:not_json_object")
    else:
        if blockers_payload.get("status") != "parked":
            issues.append(f"blockers_status:{blockers_payload.get('status')!r}")
        lane_sequencing = blockers_payload.get("lane_sequencing")
        if not isinstance(lane_sequencing, dict):
            issues.append("blockers_lane_sequencing:not_json_object")
        else:
            if lane_sequencing.get("manifest") != MANIFEST_REL.as_posix():
                issues.append("blockers_manifest_pointer")
            if lane_sequencing.get("shared_replay_parked_helpers") != list(
                EXPECTED_SHARED_REPLAY_PARKED_HELPERS
            ):
                issues.append("blockers_shared_replay_parked_helpers")
            if lane_sequencing.get("direct_anchor_followup_helpers") != list(
                EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS
            ):
                issues.append("blockers_direct_anchor_followup_helpers")
            if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
                issues.append("blockers_anti_overlap_rule")

        replay_blockers = blockers_payload.get("replay")
        if not isinstance(replay_blockers, dict):
            issues.append("blockers_replay:not_json_object")
        else:
            if replay_blockers.get("path") != REPLAY_REL.as_posix():
                issues.append("blockers_replay_path")
            if replay_blockers.get("state") != "blocked":
                issues.append("blockers_replay_state")
            blocker_list = replay_blockers.get("blockers")
            if not isinstance(blocker_list, list) or len(blocker_list) != 1:
                issues.append("blockers_replay_list")
            else:
                blocker = blocker_list[0]
                if blocker.get("field") != "slab.zero_after_kmalloc":
                    issues.append("blockers_replay_field")
                if blocker.get("expected") is not True:
                    issues.append("blockers_replay_expected")
                if blocker.get("actual") is not False:
                    issues.append("blockers_replay_actual")

        harness = blockers_payload.get("c_harness")
        if not isinstance(harness, dict):
            issues.append("blockers_c_harness:not_json_object")
        else:
            if harness.get("path") != "zigux/tests/fixtures/phase1_helpers_c_harness.c":
                issues.append("blockers_c_harness_path")
            if harness.get("state") != "blocked":
                issues.append("blockers_c_harness_state")
            if harness.get("helper_count") != len(EXPECTED_HELPERS):
                issues.append("blockers_c_harness_helper_count")
            if harness.get("helpers") != list(EXPECTED_HELPERS):
                issues.append("blockers_c_harness_helpers")

    if replay.exists():
        replay_text = _read_text(replay)
        for marker in REPLAY_IMPORTS:
            if marker not in replay_text:
                issues.append(f"replay_import:{marker}")
        for marker in REPLAY_ANCHORS:
            if marker not in replay_text:
                issues.append(f"replay_anchor:{marker}")

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_PARITY=fail")
        for issue in issues:
            print(f"PHASE1_PARITY_ISSUE={issue}")
        return 1

    print("PHASE1_PARITY=pass")
    print(f"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}")
    print(f"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print("PHASE1_PARITY_BLOCKER_STATUS=parked")
    print("PHASE1_PARITY_REPLAY=" + ("present" if (root / REPLAY_REL).exists() else "parked"))
    return 0


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_artifact_diff_text() -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            'SELF_TEST = "ARTIFACT_DIFF_SELF_TEST=pass"',
            'TEXT = "MODE=text"',
            'JSON = "MODE=json"',
            'SHA = "MODE=sha256"',
        )
    ) + "\n"


def make_fixture_json() -> str:
    payload = {section: {} for section in EXPECTED_SECTIONS}
    payload["string"] = {"strtobool_invalid": 184}
    payload["slab"] = {"zero_after_kmalloc": True}
    payload["list_sort"] = {"tri_sorted_ordinals": [1, 3, 0, 2, 4]}
    return json.dumps(payload, indent=2) + "\n"


def make_manifest_json() -> str:
    payload = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def make_blockers_json() -> str:
    payload = {
        "status": "parked",
        "lane_sequencing": {
            "manifest": MANIFEST_REL.as_posix(),
            "shared_replay_parked_helper_count": len(
                EXPECTED_SHARED_REPLAY_PARKED_HELPERS
            ),
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helper_count": len(
                EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS
            ),
            "direct_anchor_followup_helpers": list(
                EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS
            ),
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": REPLAY_REL.as_posix(),
            "state": "blocked",
            "blockers": [
                {
                    "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
                    "kind": "fixture_mismatch",
                    "path": "tools/lib/slab.zig",
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                    "evidence": "Focused replay still diverges on slab.zero_after_kmalloc.",
                }
            ],
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "reason": "The old host-side parity route still depends on helper `tools/lib/*.c` inputs.",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def make_replay_text() -> str:
    imports = "\n".join(REPLAY_IMPORTS)
    anchors = "\n".join(
        (
            "fn loadFixture() void {",
            f"    _ = {REPLAY_ANCHORS[0]};",
            f"    _ = {REPLAY_ANCHORS[1]}",
            "}",
            "",
            f"{REPLAY_ANCHORS[2]} {{}}",
            f"{REPLAY_ANCHORS[3]} {{}}",
        )
    )
    return imports + "\n\n" + anchors + "\n"


def build_case_root(base: Path) -> Path:
    write_file(base / ARTIFACT_DIFF_REL, make_artifact_diff_text())
    write_file(base / FIXTURE_REL, make_fixture_json())
    write_file(base / MANIFEST_REL, make_manifest_json())
    write_file(base / BLOCKERS_REL, make_blockers_json())
    return base


def run_self_test() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        good_root = build_case_root(tmp_root / "good")
        cases.append(("good", run_check(good_root) == 0))

        missing_artifact_root = build_case_root(tmp_root / "missing_artifact")
        (missing_artifact_root / ARTIFACT_DIFF_REL).unlink()
        cases.append(("missing_artifact_diff", run_check(missing_artifact_root) != 0))

        fixture_drift_root = build_case_root(tmp_root / "fixture_drift")
        write_file(
            fixture_drift_root / FIXTURE_REL,
            json.dumps({"find_bit": {}, "bitmap": {}}, indent=2) + "\n",
        )
        cases.append(("fixture_drift", run_check(fixture_drift_root) != 0))

        fixture_value_root = build_case_root(tmp_root / "fixture_value_drift")
        payload = json.loads(make_fixture_json())
        payload["string"]["strtobool_invalid"] = 22
        write_file(fixture_value_root / FIXTURE_REL, json.dumps(payload, indent=2) + "\n")
        cases.append(("fixture_value_drift", run_check(fixture_value_root) != 0))

        manifest_drift_root = build_case_root(tmp_root / "manifest_drift")
        payload = json.loads(make_manifest_json())
        payload["helpers"] = payload["helpers"][:-1]
        write_file(manifest_drift_root / MANIFEST_REL, json.dumps(payload, indent=2) + "\n")
        cases.append(("manifest_drift", run_check(manifest_drift_root) != 0))

        manifest_rule_root = build_case_root(tmp_root / "manifest_rule_drift")
        payload = json.loads(make_manifest_json())
        payload["lane_sequencing"]["anti_overlap_rule"] = "drifted"
        write_file(manifest_rule_root / MANIFEST_REL, json.dumps(payload, indent=2) + "\n")
        cases.append(("manifest_lane_rule_drift", run_check(manifest_rule_root) != 0))

        blockers_drift_root = build_case_root(tmp_root / "blockers_drift")
        payload = json.loads(make_blockers_json())
        payload["replay"]["blockers"][0]["actual"] = True
        write_file(blockers_drift_root / BLOCKERS_REL, json.dumps(payload, indent=2) + "\n")
        cases.append(("blockers_drift", run_check(blockers_drift_root) != 0))

        replay_present_root = build_case_root(tmp_root / "replay_present")
        write_file(replay_present_root / REPLAY_REL, make_replay_text())
        cases.append(("replay_present", run_check(replay_present_root) == 0))

        replay_anchor_root = build_case_root(tmp_root / "replay_anchor_drift")
        write_file(replay_anchor_root / REPLAY_REL, "\n".join(REPLAY_IMPORTS) + "\n")
        cases.append(("replay_anchor_drift", run_check(replay_anchor_root) != 0))

    failed = [name for name, ok in cases if not ok]
    if failed:
        print("PHASE1_PARITY_SELF_TEST=fail")
        for name in failed:
            print(f"PHASE1_PARITY_SELF_TEST_FAILED_CASE={name}")
        return 1

    print("PHASE1_PARITY_SELF_TEST=pass")
    print(f"PHASE1_PARITY_SELF_TEST_CASE_COUNT={len(cases)}")
    print("PHASE1_PARITY_SELF_TEST_CASES=" + ",".join(name for name, _ in cases))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 09 Phase 1 parity packet."
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

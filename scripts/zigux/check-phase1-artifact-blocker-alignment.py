#!/usr/bin/env python3
"""Guard the Phase 1 artifact/helper-manifest/replay-blocker packet."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import tempfile
from pathlib import Path


EXPECTED_ARTIFACT_MODE_CHOICES = ("text", "json", "bytes")
EXPECTED_ARTIFACT_LEGACY_ALIASES = {"sha256": "bytes"}
EXPECTED_ARTIFACT_SELF_TEST_CASES = (
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
)
EXPECTED_ARTIFACT_MARKERS = (
    'print("ARTIFACT_DIFF_SELF_TEST=pass")',
    'print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")',
    'print("ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))',
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
EXPECTED_SHARED_HELPERS = (
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
EXPECTED_DIRECT_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)
EXPECTED_RULE_SUMMARY = (
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
EXPECTED_REVIEW_ANCHOR_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)
EXPECTED_FIXTURE_KEYS = (
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
)
EXPECTED_BLOCKED_FIELD = "slab.zero_after_kmalloc"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that "
    "current master no longer ships beside the Phase 1 `.zig` ports."
)
EXPECTED_MANIFEST_PATH = "zigux/tests/fixtures/phase1_helper_manifest.json"
EXPECTED_REPLAY_PATH = "zigux/tests/phase1_helpers.zig"
EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"

REQUIRED_FILES = (
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_replay_blockers.json",
    "zigux/tests/fixtures/phase1_helpers.json",
)


def repo_root(arg_root: str | None) -> Path:
    here = Path(__file__).resolve()
    default_root = here.parents[2] if len(here.parents) > 2 else here.parent
    return Path(arg_root).resolve() if arg_root else default_root.resolve()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    artifact = root / "scripts/zigux/artifact_diff.py"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                'MODE_CHOICES = ("text", "json", "bytes")',
                'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
                "SELF_TEST_CASES = [",
                *[f'    "{case}",' for case in EXPECTED_ARTIFACT_SELF_TEST_CASES],
                "]",
                'print("ARTIFACT_DIFF_SELF_TEST=pass")',
                'print(f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")',
                'print("ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))',
                "",
            ]
        ),
        encoding="utf-8",
    )

    write_json(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "lane_sequencing": {
                "shared_replay_parked_helpers": list(EXPECTED_SHARED_HELPERS),
                "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
                "rule_summary": EXPECTED_RULE_SUMMARY,
                "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
            },
            "review_anchors": {helper: {} for helper in EXPECTED_REVIEW_ANCHOR_HELPERS},
        },
    )
    write_json(
        root / "zigux/tests/fixtures/phase1_replay_blockers.json",
        {
            "status": "parked",
            "lane_sequencing": {
                "manifest": EXPECTED_MANIFEST_PATH,
                "shared_replay_parked_helper_count": len(EXPECTED_SHARED_HELPERS),
                "shared_replay_parked_helpers": list(EXPECTED_SHARED_HELPERS),
                "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
                "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
                "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
            },
            "replay": {
                "path": EXPECTED_REPLAY_PATH,
                "state": "blocked",
                "blockers": [
                    {
                        "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
                        "kind": "fixture_mismatch",
                        "path": "tools/lib/slab.zig",
                        "field": EXPECTED_BLOCKED_FIELD,
                        "expected": True,
                        "actual": False,
                        "evidence": "fixture mismatch witness",
                    }
                ],
            },
            "c_harness": {
                "path": EXPECTED_C_HARNESS_PATH,
                "state": "blocked",
                "reason": EXPECTED_C_HARNESS_REASON,
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": list(EXPECTED_HELPERS),
                "blocker_id": EXPECTED_BLOCKER_ID,
            },
        },
    )
    write_json(
        root / "zigux/tests/fixtures/phase1_helpers.json",
        {
            "argv_split": {},
            "bitmap": {},
            "cmdline": {},
            "ctype": {},
            "find_bit": {},
            "hweight": {},
            "list_sort": {},
            "rbtree": {},
            "slab": {"zero_after_kmalloc": True},
            "str_error_r": {},
            "string": {},
            "vsprintf": {},
            "zalloc": {},
        },
    )


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_artifact_literals(path: Path) -> dict[str, object]:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    literals: dict[str, object] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id in {"MODE_CHOICES", "LEGACY_MODE_ALIASES", "SELF_TEST_CASES"}:
            literals[target.id] = ast.literal_eval(node.value)
    return literals


def resolve_dotted(payload: dict[str, object], dotted: str) -> object | None:
    current: object = payload
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            failures.append(f"missing_file:{relative}")
        elif not path.is_file():
            failures.append(f"not_regular_file:{relative}")
    if failures:
        return failures

    artifact_path = root / "scripts/zigux/artifact_diff.py"
    artifact_text = artifact_path.read_text(encoding="utf-8")
    for marker in EXPECTED_ARTIFACT_MARKERS:
        count = artifact_text.count(marker)
        if count != 1:
            failures.append(f"artifact_marker:{marker}:count={count}")
    artifact_literals = read_artifact_literals(artifact_path)
    if tuple(artifact_literals.get("MODE_CHOICES", ())) != EXPECTED_ARTIFACT_MODE_CHOICES:
        failures.append("artifact_mode_choices_drift")
    if artifact_literals.get("LEGACY_MODE_ALIASES") != EXPECTED_ARTIFACT_LEGACY_ALIASES:
        failures.append("artifact_legacy_alias_drift")
    if tuple(artifact_literals.get("SELF_TEST_CASES", ())) != EXPECTED_ARTIFACT_SELF_TEST_CASES:
        failures.append("artifact_self_test_cases_drift")

    manifest = read_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json")
    blockers = read_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json")
    fixture = read_json(root / "zigux/tests/fixtures/phase1_helpers.json")
    if not isinstance(manifest, dict) or not isinstance(blockers, dict) or not isinstance(fixture, dict):
        return ["packet_shape_drift"]

    if manifest.get("phase") != "Phase 1":
        failures.append("manifest_phase_drift")
    if manifest.get("status") != "closed":
        failures.append("manifest_status_drift")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        failures.append("manifest_helper_count_drift")
    if tuple(manifest.get("helpers", ())) != EXPECTED_HELPERS:
        failures.append("manifest_helpers_drift")

    lane = manifest.get("lane_sequencing", {})
    if lane.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        failures.append("manifest_rule_summary_drift")
    if lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append("manifest_anti_overlap_rule_drift")
    if tuple(lane.get("shared_replay_parked_helpers", ())) != EXPECTED_SHARED_HELPERS:
        failures.append("manifest_shared_helpers_drift")
    if tuple(lane.get("direct_anchor_followup_helpers", ())) != EXPECTED_DIRECT_HELPERS:
        failures.append("manifest_direct_helpers_drift")

    review_anchors = manifest.get("review_anchors", {})
    if not isinstance(review_anchors, dict):
        failures.append("manifest_review_anchors_not_object")
    elif tuple(sorted(review_anchors.keys())) != tuple(sorted(EXPECTED_REVIEW_ANCHOR_HELPERS)):
        failures.append("manifest_review_anchor_keys_drift")

    if tuple(sorted(fixture.keys())) != tuple(sorted(EXPECTED_FIXTURE_KEYS)):
        failures.append("fixture_keys_drift")
    if resolve_dotted(fixture, EXPECTED_BLOCKED_FIELD) is not True:
        failures.append("fixture_blocked_field_drift")

    blocker_lane = blockers.get("lane_sequencing", {})
    if blockers.get("status") != "parked":
        failures.append("blocker_status_drift")
    if blocker_lane.get("manifest") != EXPECTED_MANIFEST_PATH:
        failures.append("blocker_manifest_pointer_drift")
    if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append("blocker_anti_overlap_rule_drift")
    if blocker_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        failures.append("blocker_shared_count_drift")
    if blocker_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        failures.append("blocker_direct_count_drift")
    if tuple(blocker_lane.get("shared_replay_parked_helpers", ())) != EXPECTED_SHARED_HELPERS:
        failures.append("blocker_shared_helpers_drift")
    if tuple(blocker_lane.get("direct_anchor_followup_helpers", ())) != EXPECTED_DIRECT_HELPERS:
        failures.append("blocker_direct_helpers_drift")

    replay = blockers.get("replay", {})
    if replay.get("path") != EXPECTED_REPLAY_PATH:
        failures.append("replay_path_drift")
    if replay.get("state") != "blocked":
        failures.append("replay_state_drift")
    replay_blockers = replay.get("blockers", [])
    if not isinstance(replay_blockers, list) or len(replay_blockers) != 1:
        failures.append("replay_blocker_shape_drift")
    else:
        first = replay_blockers[0]
        if first.get("path") != "tools/lib/slab.zig":
            failures.append("replay_blocked_helper_drift")
        if first.get("field") != EXPECTED_BLOCKED_FIELD:
            failures.append("replay_blocked_field_drift")
        if first.get("expected") is not True or first.get("actual") is not False:
            failures.append("replay_expected_actual_drift")

    c_harness = blockers.get("c_harness", {})
    if c_harness.get("path") != EXPECTED_C_HARNESS_PATH:
        failures.append("c_harness_path_drift")
    if c_harness.get("state") != "blocked":
        failures.append("c_harness_state_drift")
    if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
        failures.append("c_harness_reason_drift")
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        failures.append("c_harness_helper_count_drift")
    if tuple(c_harness.get("helpers", ())) != EXPECTED_HELPERS:
        failures.append("c_harness_helpers_drift")
    if c_harness.get("blocker_id") != EXPECTED_BLOCKER_ID:
        failures.append("c_harness_blocker_id_drift")
    if (root / EXPECTED_C_HARNESS_PATH).exists():
        failures.append("c_harness_unexpectedly_present")

    return failures


def mutate_json(path: Path, update) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    update(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, callable | None]] = [
        ("sample_root_pass", None),
        ("missing_required_file", lambda root: (root / "scripts/zigux/artifact_diff.py").unlink()),
        ("artifact_case_drift", lambda root: (root / "scripts/zigux/artifact_diff.py").write_text("#!/usr/bin/env python3\nSELF_TEST_CASES=[]\n", encoding="utf-8")),
        ("manifest_rule_summary_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", lambda data: data["lane_sequencing"].__setitem__("rule_summary", "drift"))),
        ("manifest_anti_overlap_rule_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", lambda data: data["lane_sequencing"].__setitem__("anti_overlap_rule", "drift"))),
        ("review_anchor_keys_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", lambda data: data["review_anchors"].pop("tools/lib/string.zig"))),
        ("fixture_blocked_field_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_helpers.json", lambda data: data["slab"].__setitem__("zero_after_kmalloc", False))),
        ("blocker_manifest_pointer_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["lane_sequencing"].__setitem__("manifest", "drift.json"))),
        ("blocker_anti_overlap_rule_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["lane_sequencing"].__setitem__("anti_overlap_rule", "drift"))),
        ("replay_blocked_helper_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["replay"]["blockers"][0].__setitem__("path", "tools/lib/bitmap.zig"))),
        ("replay_expected_actual_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["replay"]["blockers"][0].__setitem__("actual", True))),
        ("c_harness_reason_drift", lambda root: mutate_json(root / "zigux/tests/fixtures/phase1_replay_blockers.json", lambda data: data["c_harness"].__setitem__("reason", "drift"))),
        ("c_harness_unexpectedly_present", lambda root: (root / "zigux/tests/fixtures/phase1_helpers_c_harness.c").write_text("stale\n", encoding="utf-8")),
    ]

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="lane09_artifact_alignment_") as tmp_dir:
            root = Path(tmp_dir) / "sample"
            write_sample_root(root)
            if mutation is not None:
                mutation(root)
            failures = collect_failures(root)
            if name == "sample_root_pass":
                if failures:
                    print(f"SELF_TEST_FAILURE={name}")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"SELF_TEST_FAILURE={name}:expected_failure")
                return 1

    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root")
    parser.add_argument("--write-sample-root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=fail")
        for failure in failures:
            print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_ISSUE={failure}")
        return 1

    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_FIXTURE_HELPER_COUNT={len(EXPECTED_FIXTURE_KEYS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_BLOCKED_FIELD={EXPECTED_BLOCKED_FIELD}")
    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_C_HARNESS_PRESENT=False")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_REVIEW_ANCHOR_HELPER_COUNT={len(EXPECTED_REVIEW_ANCHOR_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_ARTIFACT_SELF_TEST_CASE_COUNT={len(EXPECTED_ARTIFACT_SELF_TEST_CASES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

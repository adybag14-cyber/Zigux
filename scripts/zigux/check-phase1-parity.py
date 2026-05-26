#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
REPLAY_BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")

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

EXPECTED_FIXTURE_VALUES = {
    ("string", "strtobool_invalid"): 184,
    ("string", "replace_char_cstr_end"): 2,
    ("string", "replace_char_cstr_bytes"): [97, 95, 0, 45, 122],
    ("slab", "zero_after_kmalloc"): True,
    ("bitmap", "truncated_scnprintf_len"): 7,
    ("bitmap", "truncated_scnprintf"): "1-3,7,1",
    ("bitmap", "terminator_only_scnprintf_len"): 0,
    ("bitmap", "zero_length_scnprintf_len"): 0,
    ("bitmap", "copy_clear_tail_values"): [18446744073709551615, 31],
    ("bitmap", "copy_and_extend_values"): [18446744073709551615, 31, 0],
    ("find_bit", "inclusive_boundary_next"): 63,
    ("find_bit", "inclusive_boundary_zero"): 63,
    ("find_bit", "inclusive_boundary_and"): 63,
    ("find_bit", "tail_clamped_first"): 67,
    ("find_bit", "tail_clamped_last"): 67,
    ("find_bit", "tail_clamped_empty_last"): 69,
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("rbtree", "cached_root_transition_serials"): [0, 0, 4, 2],
    ("rbtree", "next_match_terminal_null"): True,
    ("list_sort", "bool_sorted_ordinals"): [1, 3, 0, 2, 4],
}

EXPECTED_REPLAY_BLOCKER_IDS = (
    "phase1_helpers_zig_slab_zero_after_kmalloc",
    "phase1_helpers_c_harness_missing_c_sources",
)

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_REPLAY_MARKERS = (
    'test "phase 1 helper ports match committed parity fixture" {',
    'const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");',
    "const Fixture = struct {",
)

EXPECTED_REPLAY_BUILD_MARKERS = (
    '.root_source_file = b.path("phase1_helpers.zig"),',
    '.name = "phase1-helpers",',
    '"Run the focused Phase 1 helper replay anchor from zigux/tests",',
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def read_json(path: Path, label: str, issues: list[str]) -> object | None:
    try:
        payload = load_json_with_duplicate_tracking(read_text(path))
    except json.JSONDecodeError as exc:
        issues.append(f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}")
        return None

    duplicate_paths = collect_duplicate_json_key_paths(payload)
    if duplicate_paths:
        issues.extend(f"{label}:duplicate_json_key:{duplicate_path}" for duplicate_path in duplicate_paths)
        return None

    return payload


def run_python(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def ensure(condition: bool, issue: str, issues: list[str]) -> None:
    if not condition:
        issues.append(issue)


def ensure_exact_occurrence(text: str, label: str, marker: str, issues: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        issues.append(f"{label}:expected=1:actual={count}")


def check_artifact_diff(root: Path, issues: list[str]) -> None:
    artifact_diff = root / ARTIFACT_DIFF_REL
    result = run_python(artifact_diff, "--self-test")
    ensure(result.returncode == 0, "artifact_diff:self_test:returncode", issues)
    ensure("ARTIFACT_DIFF_SELF_TEST=pass" in result.stdout, "artifact_diff:self_test:pass", issues)
    ensure("ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23" in result.stdout, "artifact_diff:self_test:case_count", issues)

    with tempfile.TemporaryDirectory(prefix="phase1_parity_artifact_diff_") as tmp_dir:
        tmp = Path(tmp_dir)
        text_expected = tmp / "expected.txt"
        text_actual = tmp / "actual.txt"
        json_expected = tmp / "expected.json"
        json_actual = tmp / "actual.json"
        bytes_expected = tmp / "expected.bin"
        bytes_actual = tmp / "actual.bin"

        text_expected.write_text("alpha\nbeta\n", encoding="utf-8")
        text_actual.write_text("alpha\nbeta\n", encoding="utf-8")
        json_expected.write_text('{"alpha": 1, "beta": [2, 3]}\n', encoding="utf-8")
        json_actual.write_text('{"beta": [2, 3], "alpha": 1}\n', encoding="utf-8")
        bytes_expected.write_bytes(b"zigux-parity")
        bytes_actual.write_bytes(b"zigux-parity")

        cases = (
            ("text", ["--mode", "text", str(text_expected), str(text_actual)]),
            ("json", ["--mode", "json", str(json_expected), str(json_actual)]),
            ("bytes", ["--mode", "bytes", str(bytes_expected), str(bytes_actual)]),
            ("sha256", ["--mode", "sha256", str(bytes_expected), str(bytes_actual)]),
        )
        for name, argv in cases:
            result = run_python(artifact_diff, *argv)
            ensure(result.returncode == 0, f"artifact_diff:{name}:returncode", issues)
            ensure("ARTIFACT_DIFF=pass" in result.stdout, f"artifact_diff:{name}:pass", issues)


def check_replay_routes(root: Path, issues: list[str]) -> None:
    replay_text = read_text(root / REPLAY_REL)
    for marker in EXPECTED_REPLAY_MARKERS:
        ensure_exact_occurrence(replay_text, f"replay:{marker}", marker, issues)

    build_text = read_text(root / REPLAY_BUILD_REL)
    for marker in EXPECTED_REPLAY_BUILD_MARKERS:
        ensure_exact_occurrence(build_text, f"replay_build:{marker}", marker, issues)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):
        ensure((root / rel).exists(), f"missing:{rel.as_posix()}", issues)
    if issues:
        return issues

    check_artifact_diff(root, issues)
    check_replay_routes(root, issues)

    fixture_payload = read_json(root / FIXTURE_REL, "fixture", issues)
    if isinstance(fixture_payload, dict):
        ensure(tuple(fixture_payload.keys()) == EXPECTED_SECTIONS, "fixture:sections", issues)
        for (section, key), expected_value in EXPECTED_FIXTURE_VALUES.items():
            section_payload = fixture_payload.get(section)
            ensure(isinstance(section_payload, dict), f"fixture:{section}:not_object", issues)
            if isinstance(section_payload, dict):
                ensure(
                    section_payload.get(key) == expected_value,
                    f"fixture:{section}.{key}:{section_payload.get(key)!r}!={expected_value!r}",
                    issues,
                )
    elif fixture_payload is not None:
        ensure(False, "fixture:not_object", issues)

    manifest_payload = read_json(root / MANIFEST_REL, "manifest", issues)
    if isinstance(manifest_payload, dict):
        ensure(manifest_payload.get("phase") == "Phase 1", "manifest:phase", issues)
        ensure(manifest_payload.get("status") == "closed", "manifest:status", issues)
        ensure(manifest_payload.get("helper_count") == len(EXPECTED_HELPERS), "manifest:helper_count", issues)
        ensure(tuple(manifest_payload.get("helpers", ())) == EXPECTED_HELPERS, "manifest:helpers", issues)
        lane = manifest_payload.get("lane_sequencing")
        ensure(isinstance(lane, dict), "manifest:lane:not_object", issues)
        if isinstance(lane, dict):
            ensure(
                tuple(lane.get("shared_replay_parked_helpers", ())) == EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                "manifest:shared_replay_parked_helpers",
                issues,
            )
            ensure(
                tuple(lane.get("direct_anchor_followup_helpers", ())) == EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                "manifest:direct_anchor_followup_helpers",
                issues,
            )
            ensure(lane.get("rule_summary") == EXPECTED_RULE_SUMMARY, "manifest:rule_summary", issues)
            ensure(lane.get("anti_overlap_rule") == EXPECTED_ANTI_OVERLAP_RULE, "manifest:anti_overlap_rule", issues)
    elif manifest_payload is not None:
        ensure(False, "manifest:not_object", issues)

    blockers_payload = read_json(root / BLOCKERS_REL, "blockers", issues)
    if isinstance(blockers_payload, dict):
        ensure(blockers_payload.get("status") == "parked", "blockers:status", issues)
        replay = blockers_payload.get("replay")
        ensure(isinstance(replay, dict), "blockers:replay:not_object", issues)
        if isinstance(replay, dict):
            ensure(replay.get("path") == REPLAY_REL.as_posix(), "blockers:replay:path", issues)
            ensure(replay.get("state") == "blocked", "blockers:replay:state", issues)
            blocker_list = replay.get("blockers")
            ensure(isinstance(blocker_list, list) and len(blocker_list) == 1, "blockers:replay:list", issues)
            if isinstance(blocker_list, list) and len(blocker_list) == 1 and isinstance(blocker_list[0], dict):
                blocker = blocker_list[0]
                ensure(blocker.get("id") == EXPECTED_REPLAY_BLOCKER_IDS[0], "blockers:replay:id", issues)
                ensure(blocker.get("field") == "slab.zero_after_kmalloc", "blockers:replay:field", issues)
                ensure(blocker.get("expected") is True, "blockers:replay:expected", issues)
                ensure(blocker.get("actual") is False, "blockers:replay:actual", issues)
        harness = blockers_payload.get("c_harness")
        ensure(isinstance(harness, dict), "blockers:c_harness:not_object", issues)
        if isinstance(harness, dict):
            ensure(harness.get("path") == HARNESS_REL.as_posix(), "blockers:c_harness:path", issues)
            ensure(harness.get("state") == "blocked", "blockers:c_harness:state", issues)
            ensure(harness.get("helper_count") == len(EXPECTED_HELPERS), "blockers:c_harness:helper_count", issues)
            ensure(tuple(harness.get("helpers", ())) == EXPECTED_HELPERS, "blockers:c_harness:helpers", issues)
            ensure(harness.get("blocker_id") == EXPECTED_REPLAY_BLOCKER_IDS[1], "blockers:c_harness:blocker_id", issues)
    elif blockers_payload is not None:
        ensure(False, "blockers:not_object", issues)

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
    print("PHASE1_PARITY_REPLAY=present")
    print(f"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}")
    print("PHASE1_PARITY_BLOCKER_IDS=" + ",".join(EXPECTED_REPLAY_BLOCKER_IDS))
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    artifact_diff_text = """#!/usr/bin/env python3
from __future__ import annotations

import sys

if "--self-test" in sys.argv:
    print(\"ARTIFACT_DIFF_SELF_TEST=pass\")
    print(\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=23\")
else:
    print(\"ARTIFACT_DIFF=pass\")
"""
    fixture_payload = {name: {} for name in EXPECTED_SECTIONS}
    fixture_payload["string"]["strtobool_invalid"] = 184
    fixture_payload["string"]["replace_char_cstr_end"] = 2
    fixture_payload["string"]["replace_char_cstr_bytes"] = [97, 95, 0, 45, 122]
    fixture_payload["slab"]["zero_after_kmalloc"] = True
    fixture_payload["bitmap"]["truncated_scnprintf_len"] = 7
    fixture_payload["bitmap"]["truncated_scnprintf"] = "1-3,7,1"
    fixture_payload["bitmap"]["terminator_only_scnprintf_len"] = 0
    fixture_payload["bitmap"]["zero_length_scnprintf_len"] = 0
    fixture_payload["bitmap"]["copy_clear_tail_values"] = [18446744073709551615, 31]
    fixture_payload["bitmap"]["copy_and_extend_values"] = [18446744073709551615, 31, 0]
    fixture_payload["find_bit"]["inclusive_boundary_next"] = 63
    fixture_payload["find_bit"]["inclusive_boundary_zero"] = 63
    fixture_payload["find_bit"]["inclusive_boundary_and"] = 63
    fixture_payload["find_bit"]["tail_clamped_first"] = 67
    fixture_payload["find_bit"]["tail_clamped_last"] = 67
    fixture_payload["find_bit"]["tail_clamped_empty_last"] = 69
    fixture_payload["rbtree"]["cached_leftmost_return_serials"] = [0, -1, 2, -1]
    fixture_payload["rbtree"]["cached_root_transition_serials"] = [0, 0, 4, 2]
    fixture_payload["rbtree"]["next_match_terminal_null"] = True
    fixture_payload["list_sort"]["bool_sorted_ordinals"] = [1, 3, 0, 2, 4]

    manifest_payload = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS),
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }

    blockers_payload = {
        "status": "parked",
        "replay": {
            "path": REPLAY_REL.as_posix(),
            "state": "blocked",
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_IDS[0],
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                }
            ],
        },
        "c_harness": {
            "path": HARNESS_REL.as_posix(),
            "state": "blocked",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": EXPECTED_REPLAY_BLOCKER_IDS[1],
        },
    }

    write_text(root / ARTIFACT_DIFF_REL, artifact_diff_text)
    write_text(root / FIXTURE_REL, json.dumps(fixture_payload, indent=2) + "\n")
    write_text(root / MANIFEST_REL, json.dumps(manifest_payload, indent=2) + "\n")
    write_text(root / BLOCKERS_REL, json.dumps(blockers_payload, indent=2) + "\n")
    write_text(root / REPLAY_REL, "\n".join(EXPECTED_REPLAY_MARKERS) + "\n")
    write_text(root / REPLAY_BUILD_REL, "\n".join(EXPECTED_REPLAY_BUILD_MARKERS) + "\n")


def mutate_json(path: Path, mutate) -> None:
    payload = json.loads(read_text(path))
    assert isinstance(payload, dict)
    mutate(payload)
    write_text(path, json.dumps(payload, indent=2) + "\n")


def insert_duplicate_json_line(path: Path, needle: str, duplicate_line: str) -> None:
    text = read_text(path)
    write_text(path, text.replace(needle, duplicate_line + "\n" + needle, 1))


def replace_first(path: Path, needle: str, replacement: str) -> None:
    text = read_text(path)
    write_text(path, text.replace(needle, replacement, 1))


def run_self_test() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="phase1_parity_selftest_") as tmp_dir:
        tmp = Path(tmp_dir)

        for name, mutate in (
            ("good", lambda root: None),
            ("fixture_drift", lambda root: mutate_json(root / FIXTURE_REL, lambda payload: payload["string"].update({"strtobool_invalid": 22}))),
            ("manifest_drift", lambda root: mutate_json(root / MANIFEST_REL, lambda payload: payload.update({"status": "open"}))),
            ("blocker_drift", lambda root: mutate_json(root / BLOCKERS_REL, lambda payload: payload["replay"]["blockers"][0].update({"actual": True}))),
            ("fixture_duplicate_key", lambda root: insert_duplicate_json_line(root / FIXTURE_REL, '    "tail_clamped_last": 67', '    "tail_clamped_last": 0,')),
            ("manifest_duplicate_key", lambda root: insert_duplicate_json_line(root / MANIFEST_REL, '  "status": "closed",', '  "status": "open",')),
            ("blocker_duplicate_key", lambda root: insert_duplicate_json_line(root / BLOCKERS_REL, '  "status": "parked",', '  "status": "open",')),
            ("fixture_invalid_json", lambda root: write_text(root / FIXTURE_REL, "{\n")),
            ("manifest_invalid_json", lambda root: write_text(root / MANIFEST_REL, "{\n")),
            ("blocker_invalid_json", lambda root: write_text(root / BLOCKERS_REL, "{\n")),
            ("missing_replay", lambda root: (root / REPLAY_REL).unlink()),
            ("missing_replay_build", lambda root: (root / REPLAY_BUILD_REL).unlink()),
            ("replay_marker_drift", lambda root: replace_first(root / REPLAY_REL, EXPECTED_REPLAY_MARKERS[0], 'test "phase 1 helper ports drifted" {')),
            ("replay_build_marker_drift", lambda root: replace_first(root / REPLAY_BUILD_REL, EXPECTED_REPLAY_BUILD_MARKERS[1], '.name = "phase1-helper-drift",')),
        ):
            case_root = tmp / name
            build_sample_root(case_root)
            mutate(case_root)
            cases.append((name, run_check(case_root) == (0 if name == "good" else 1)))

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
    parser = argparse.ArgumentParser(description="Validate the bounded Lane 09 Phase 1 parity packet.")
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

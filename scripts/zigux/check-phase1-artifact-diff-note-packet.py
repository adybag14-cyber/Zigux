#!/usr/bin/env python3
"""Guard the Phase 1 artifact-diff note packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE_REL = Path("Documentation/zigux/artifact-diff.md")
ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

HELPER_TO_SECTION = {
    "tools/lib/argv_split.zig": "argv_split",
    "tools/lib/bitmap.zig": "bitmap",
    "tools/lib/cmdline.zig": "cmdline",
    "tools/lib/ctype.zig": "ctype",
    "tools/lib/find_bit.zig": "find_bit",
    "tools/lib/hweight.zig": "hweight",
    "tools/lib/list_sort.zig": "list_sort",
    "tools/lib/rbtree.zig": "rbtree",
    "tools/lib/slab.zig": "slab",
    "tools/lib/str_error_r.zig": "str_error_r",
    "tools/lib/string.zig": "string",
    "tools/lib/vsprintf.zig": "vsprintf",
    "tools/lib/zalloc.zig": "zalloc",
}
HELPERS = list(HELPER_TO_SECTION)
SECTIONS = [HELPER_TO_SECTION[path] for path in HELPERS]
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

NOTE_MARKERS = [
    "## Current Phase 1 use",
    "Phase 1 still uses `scripts/zigux/artifact_diff.py` as the shared host-side comparison helper",
    "`phase1_helpers.json`",
    "Phase 1 parity reminder packet",
]
ARTIFACT_DIFF_MARKERS = [
    'MODE_CHOICES = ("text", "json", "bytes")',
    'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
    '"json_pass"',
    '"bytes_pass"',
    '"legacy_sha256_alias"',
]
FIXTURE_SENTINELS = {
    "bitmap.partial_xor_nbits": 4,
    "find_bit.tail_clamped_last": 67,
    "list_sort.tri_sorted_keys": [1, 1, 2, 3, 3],
    "rbtree.cached_leftmost_return_serials": [0, -1, 2, -1],
    "slab.zero_after_kmalloc": True,
    "string.replace_char_cstr_bytes": [97, 95, 0, 45, 122],
}
SELF_TEST_CASES = [
    "round_trip",
    "sample_root_writer",
    "note_directory_drift",
    "artifact_diff_directory_drift",
    "note_marker_drift",
    "artifact_marker_drift",
    "manifest_invalid_json",
    "fixture_invalid_json",
    "blockers_invalid_json",
    "helper_count_drift",
    "shared_helper_drift",
    "direct_helper_drift",
    "fixture_section_drift",
    "fixture_sentinel_drift",
    "replay_state_drift",
    "c_harness_state_drift",
]

SAMPLE_FIXTURE = {
    "find_bit": {
        "bits_per_long": 64,
        "first": 5,
        "next_after_6": 67,
        "next_after_word": 135,
        "first_zero": 3,
        "next_zero": 68,
        "first_and": 9,
        "next_and": 66,
        "last": 135,
        "inclusive_boundary_next": 63,
        "inclusive_boundary_zero": 63,
        "inclusive_boundary_and": 63,
        "tail_inclusive_boundary_next": 68,
        "tail_inclusive_boundary_zero": 68,
        "tail_inclusive_boundary_and": 68,
        "past_nbits_next": 7,
        "past_nbits_zero": 7,
        "past_nbits_and": 7,
        "tail_clamped_first": 67,
        "tail_clamped_next": 69,
        "tail_zero_clamped_first": 69,
        "tail_zero_clamped_next": 69,
        "tail_and_clamped_first": 67,
        "tail_and_clamped_next": 69,
        "tail_clamped_last": 67,
        "tail_clamped_empty_last": 69,
    },
    "bitmap": {
        "weight": 3,
        "scnprintf": "1-3,7,10-11",
        "truncated_scnprintf_len": 7,
        "truncated_scnprintf": "1-3,7,1",
        "terminator_only_scnprintf_len": 0,
        "terminator_only_nul": 0,
        "zero_length_scnprintf_len": 0,
        "alloc_words": 2,
        "zalloc_words": 2,
        "zalloc_values": [0, 0],
        "copy_values": [18446744073709551615, 18446744073709551615],
        "copy_clear_tail_values": [18446744073709551615, 31],
        "copy_and_extend_values": [18446744073709551615, 31, 0],
        "and_result": True,
        "and_values": [10, 0],
        "andnot_result": True,
        "andnot_values": [4, 0],
        "or_values": [14, 0],
        "xor_values": [4, 0],
        "partial_xor_nbits": 4,
        "partial_xor_masked_values": [14],
        "equal": True,
        "intersects": True,
        "subset": True,
        "range_after_set": [14, 12, 0],
        "range_after_clear": [0, 0, 0],
        "full_after_fill": True,
        "empty_after_zero": True,
    },
    "string": {
        "strtobool_y": True,
        "strtobool_on": True,
        "strtobool_zero": False,
        "strtobool_off": False,
        "strtobool_invalid": 184,
        "strlcpy_len": 5,
        "strlcpy_buffer": "hel",
        "skip_spaces": "hello",
        "trim_spaces": "hi",
        "remove_spaces": "abc",
        "replace_char": "a_b",
        "replace_char_end": 3,
        "replace_char_cstr_end": 2,
        "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
        "memchr_inv_index": 4,
        "memchr_inv_none": True,
    },
    "rbtree": {
        "empty_root": True,
        "insert_order": [5, 10, 15, 20, 25],
        "reverse_order": [25, 20, 15, 10, 5],
        "replace_order": [5, 10, 15, 25],
        "erase_init_order": [5, 15, 25],
        "postorder_count": 3,
        "erase_init_node_empty": True,
        "cleared_node_empty": True,
        "find_found_key": 15,
        "find_missing": True,
        "find_first_serial": 0,
        "next_match_serials": [0, 2, 4],
        "match_iterator_serials": [0, 2, 4],
        "cached_leftmost_return_serials": [0, -1, 2, -1],
        "next_match_terminal_null": True,
    },
    "argv_split": {"argc": 3, "argv": ["alpha", "beta", "gamma"], "blank_argc": 0},
    "cmdline": {
        "decimal_k": {"value": 65536, "rest": " rest"},
        "hex_m": {"value": 33554432, "rest": ""},
        "octal_k": {"value": 8192, "rest": ""},
        "invalid": {"value": 0, "rest": "xyz"},
    },
    "ctype": {
        "mask_A": 65,
        "mask_a": 66,
        "mask_space": 160,
        "isalnum_A": True,
        "isalpha_z": True,
        "isdigit_7": True,
        "isspace_tab": True,
        "isxdigit_f": True,
        "ispunct_bang": True,
        "tolower_A": 97,
        "toupper_z": 90,
        "isodigit_7": True,
        "isodigit_8": False,
    },
    "hweight": {"w8": 4, "w16": 8, "w32": 16, "w64": 32, "wlong": 8},
    "list_sort": {
        "tri_sorted_keys": [1, 1, 2, 3, 3],
        "tri_sorted_ordinals": [1, 3, 0, 2, 4],
        "bool_sorted_keys": [1, 1, 2, 3, 3],
        "bool_sorted_ordinals": [1, 3, 0, 2, 4],
    },
    "zalloc": {
        "zeroed": True,
        "freed_is_null": True,
        "value_zeroed": True,
        "value_freed_is_null": True,
    },
    "str_error_r": {
        "enoent": "No such file or directory",
        "unknown": "INTERNAL ERROR: strerror_r(4096, [buf], 64)=22",
    },
    "slab": {
        "null_without_reclaim": True,
        "alloc_count_after_kmalloc": 1,
        "zero_after_kmalloc": True,
        "alloc_count_after_kmalloc_free": 0,
        "array_zeroed": True,
        "alloc_count_after_kmalloc_array": 1,
        "alloc_count_after_kmalloc_array_free": 0,
        "slab_is_available": True,
    },
    "vsprintf": {
        "scnprintf_text": "zigux:7",
        "scnprintf_len": 7,
        "pad_text": "id=7    ",
        "pad_len": 7,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the Phase 1 artifact-diff note packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=False) + "\n")


def sample_note_text() -> str:
    return "\n".join(
        [
            "# Zigux Artifact-Diff Notes",
            "",
            "## Current Phase 1 use",
            "",
            "Phase 1 still uses `scripts/zigux/artifact_diff.py` as the shared host-side comparison helper behind the committed helper parity fixtures, including `phase1_helpers.json` and the Phase 1 parity reminder packet.",
            "",
        ]
    )


def sample_artifact_diff_text() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            'MODE_CHOICES = ("text", "json", "bytes")',
            'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
            'SELF_TEST_CASES = ["json_pass", "bytes_pass", "legacy_sha256_alias"]',
            "",
        ]
    )


def sample_manifest_payload() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(HELPERS),
        "helpers": HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": SHARED_HELPERS,
            "direct_anchor_followup_helpers": DIRECT_HELPERS,
            "rule_summary": (
                "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
                "above, while bitmap, find_bit, rbtree, and string keep the only bounded "
                "direct helper-local follow-up anchors on current master."
            ),
            "anti_overlap_rule": (
                "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
                "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
                "helpers reopen only for their existing helper-local anchors or already-committed "
                "shared fixture keys."
            ),
        },
    }


def sample_blockers_payload() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
            "shared_replay_parked_helper_count": len(SHARED_HELPERS),
            "shared_replay_parked_helpers": SHARED_HELPERS,
            "direct_anchor_followup_helper_count": len(DIRECT_HELPERS),
            "direct_anchor_followup_helpers": DIRECT_HELPERS,
            "anti_overlap_rule": sample_manifest_payload()["lane_sequencing"]["anti_overlap_rule"],
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "helper_count": len(HELPERS),
            "helpers": HELPERS,
        },
    }


def write_sample_root(root: Path) -> None:
    write_text(root / NOTE_REL, sample_note_text())
    write_text(root / ARTIFACT_DIFF_REL, sample_artifact_diff_text())
    write_json(root / MANIFEST_REL, sample_manifest_payload())
    write_json(root / FIXTURE_REL, SAMPLE_FIXTURE)
    write_json(root / BLOCKERS_REL, sample_blockers_payload())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json_with_issue(path: Path, label: str) -> tuple[object | None, str | None]:
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError as exc:
        return None, f"{label}:json_decode:{exc.lineno}:{exc.colno}:{exc.msg}"


def load_json(path: Path) -> object:
    payload, issue = load_json_with_issue(path, "internal")
    if issue is not None:
        raise ValueError(issue)
    return payload


def ensure(condition: bool, issues: list[str], label: str) -> None:
    if not condition:
        issues.append(label)


def ensure_file(path: Path, root: Path, issues: list[str]) -> None:
    relative = path.relative_to(root).as_posix()
    if path.is_file():
        return
    if path.exists():
        issues.append(f"not_file:{relative}")
        return
    issues.append(f"missing:{relative}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    note_path = root / NOTE_REL
    artifact_diff_path = root / ARTIFACT_DIFF_REL
    manifest_path = root / MANIFEST_REL
    fixture_path = root / FIXTURE_REL
    blockers_path = root / BLOCKERS_REL
    for path in [note_path, artifact_diff_path, manifest_path, fixture_path, blockers_path]:
        ensure_file(path, root, issues)
    if issues:
        return issues

    note_text = read_text(note_path)
    for marker in NOTE_MARKERS:
        ensure(marker in note_text, issues, f"note:marker:{marker}")

    artifact_diff_text = read_text(artifact_diff_path)
    for marker in ARTIFACT_DIFF_MARKERS:
        ensure(marker in artifact_diff_text, issues, f"artifact_diff:marker:{marker}")

    manifest, manifest_issue = load_json_with_issue(manifest_path, "manifest")
    fixture, fixture_issue = load_json_with_issue(fixture_path, "fixture")
    blockers, blockers_issue = load_json_with_issue(blockers_path, "blockers")
    for issue in [manifest_issue, fixture_issue, blockers_issue]:
        if issue is not None:
            issues.append(issue)
    if issues:
        return issues
    ensure(isinstance(manifest, dict), issues, "manifest:not_object")
    ensure(isinstance(fixture, dict), issues, "fixture:not_object")
    ensure(isinstance(blockers, dict), issues, "blockers:not_object")
    if issues:
        return issues

    ensure(manifest.get("phase") == "Phase 1", issues, "manifest:phase")
    ensure(manifest.get("status") == "closed", issues, "manifest:status")
    ensure(manifest.get("helper_count") == len(HELPERS), issues, "manifest:helper_count")
    ensure(manifest.get("helpers") == HELPERS, issues, "manifest:helpers")
    lane = manifest.get("lane_sequencing")
    ensure(isinstance(lane, dict), issues, "manifest:lane")
    if isinstance(lane, dict):
        ensure(
            lane.get("shared_replay_parked_helpers") == SHARED_HELPERS,
            issues,
            "manifest:shared_helpers",
        )
        ensure(
            lane.get("direct_anchor_followup_helpers") == DIRECT_HELPERS,
            issues,
            "manifest:direct_helpers",
        )

    ensure(sorted(fixture.keys()) == sorted(SECTIONS), issues, "fixture:sections")
    ensure(len(fixture) == len(SECTIONS), issues, "fixture:section_count")
    for dotted_key, expected_value in FIXTURE_SENTINELS.items():
        section_name, key = dotted_key.split(".", 1)
        section_payload = fixture.get(section_name)
        ensure(isinstance(section_payload, dict), issues, f"fixture:section:{section_name}")
        if isinstance(section_payload, dict):
            ensure(
                section_payload.get(key) == expected_value,
                issues,
                f"fixture:sentinel:{dotted_key}",
            )

    ensure(blockers.get("status") == "parked", issues, "blockers:status")
    blocker_lane = blockers.get("lane_sequencing")
    ensure(isinstance(blocker_lane, dict), issues, "blockers:lane")
    if isinstance(blocker_lane, dict):
        ensure(
            blocker_lane.get("manifest") == MANIFEST_REL.as_posix(),
            issues,
            "blockers:manifest_path",
        )
        ensure(
            blocker_lane.get("shared_replay_parked_helper_count") == len(SHARED_HELPERS),
            issues,
            "blockers:shared_helper_count",
        )
        ensure(
            blocker_lane.get("direct_anchor_followup_helper_count") == len(DIRECT_HELPERS),
            issues,
            "blockers:direct_helper_count",
        )
        ensure(
            blocker_lane.get("shared_replay_parked_helpers") == SHARED_HELPERS,
            issues,
            "blockers:shared_helpers",
        )
        ensure(
            blocker_lane.get("direct_anchor_followup_helpers") == DIRECT_HELPERS,
            issues,
            "blockers:direct_helpers",
        )
    replay = blockers.get("replay")
    ensure(isinstance(replay, dict), issues, "blockers:replay")
    if isinstance(replay, dict):
        ensure(
            replay.get("path") == "zigux/tests/phase1_helpers.zig",
            issues,
            "blockers:replay_path",
        )
        ensure(replay.get("state") == "blocked", issues, "blockers:replay_state")
    c_harness = blockers.get("c_harness")
    ensure(isinstance(c_harness, dict), issues, "blockers:c_harness")
    if isinstance(c_harness, dict):
        ensure(
            c_harness.get("path") == "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            issues,
            "blockers:c_harness_path",
        )
        ensure(c_harness.get("state") == "blocked", issues, "blockers:c_harness_state")
        ensure(
            c_harness.get("helper_count") == len(HELPERS),
            issues,
            "blockers:c_harness_helper_count",
        )
        ensure(c_harness.get("helpers") == HELPERS, issues, "blockers:c_harness_helpers")

    if issues:
        return issues

    return [
        "PHASE1_ARTIFACT_DIFF_NOTE_PACKET=pass",
        f"PHASE1_ARTIFACT_DIFF_NOTE_PACKET_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}",
        "PHASE1_ARTIFACT_DIFF_NOTE_PACKET_ARTIFACT_MODE_COUNT=3",
        f"PHASE1_ARTIFACT_DIFF_NOTE_PACKET_HELPER_COUNT={len(HELPERS)}",
        f"PHASE1_ARTIFACT_DIFF_NOTE_PACKET_FIXTURE_SECTION_COUNT={len(SECTIONS)}",
        f"PHASE1_ARTIFACT_DIFF_NOTE_PACKET_SHARED_HELPER_COUNT={len(SHARED_HELPERS)}",
        f"PHASE1_ARTIFACT_DIFF_NOTE_PACKET_DIRECT_HELPER_COUNT={len(DIRECT_HELPERS)}",
        "PHASE1_ARTIFACT_DIFF_NOTE_PACKET_REPLAY_STATE=blocked",
        "PHASE1_ARTIFACT_DIFF_NOTE_PACKET_C_HARNESS_STATE=blocked",
    ]


def is_pass(lines: list[str]) -> bool:
    return bool(lines) and lines[0] == "PHASE1_ARTIFACT_DIFF_NOTE_PACKET=pass"


def assert_validation_pass(root: Path) -> None:
    assert is_pass(validate(root)), root.as_posix()


def expect_failure(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(label)


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_artifact_note_") as tmp_dir:
        root = Path(tmp_dir)
        sample_root = root / "sample"
        write_sample_root(sample_root)

        lines = validate(sample_root)
        assert is_pass(lines), "round_trip"
        covered.append("round_trip")

        writer_root = root / "writer"
        write_sample_root(writer_root)
        assert (writer_root / NOTE_REL).is_file(), "sample_root_writer"
        assert (writer_root / BLOCKERS_REL).is_file(), "sample_root_writer"
        covered.append("sample_root_writer")

        note_directory_drift = root / "note_directory_drift"
        write_sample_root(note_directory_drift)
        (note_directory_drift / NOTE_REL).unlink()
        (note_directory_drift / NOTE_REL).mkdir(parents=True)
        expect_failure("note_directory_drift", lambda: assert_validation_pass(note_directory_drift))
        covered.append("note_directory_drift")

        artifact_diff_directory_drift = root / "artifact_diff_directory_drift"
        write_sample_root(artifact_diff_directory_drift)
        (artifact_diff_directory_drift / ARTIFACT_DIFF_REL).unlink()
        (artifact_diff_directory_drift / ARTIFACT_DIFF_REL).mkdir(parents=True)
        expect_failure(
            "artifact_diff_directory_drift",
            lambda: assert_validation_pass(artifact_diff_directory_drift),
        )
        covered.append("artifact_diff_directory_drift")

        note_marker_drift = root / "note_marker_drift"
        write_sample_root(note_marker_drift)
        note_path = note_marker_drift / NOTE_REL
        note_path.write_text(
            read_text(note_path).replace("Phase 1 parity reminder packet", "Phase 1 parity reminder seam", 1),
            encoding="utf-8",
            newline="\n",
        )
        expect_failure("note_marker_drift", lambda: assert_validation_pass(note_marker_drift))
        covered.append("note_marker_drift")

        artifact_marker_drift = root / "artifact_marker_drift"
        write_sample_root(artifact_marker_drift)
        artifact_path = artifact_marker_drift / ARTIFACT_DIFF_REL
        artifact_path.write_text(
            read_text(artifact_path).replace('"bytes_pass"', '"bytes_pass_removed"', 1),
            encoding="utf-8",
            newline="\n",
        )
        expect_failure("artifact_marker_drift", lambda: assert_validation_pass(artifact_marker_drift))
        covered.append("artifact_marker_drift")

        manifest_invalid_json = root / "manifest_invalid_json"
        write_sample_root(manifest_invalid_json)
        write_text(manifest_invalid_json / MANIFEST_REL, '{"phase": "Phase 1",\n')
        expect_failure("manifest_invalid_json", lambda: assert_validation_pass(manifest_invalid_json))
        covered.append("manifest_invalid_json")

        fixture_invalid_json = root / "fixture_invalid_json"
        write_sample_root(fixture_invalid_json)
        write_text(fixture_invalid_json / FIXTURE_REL, '{"bitmap": {\n')
        expect_failure("fixture_invalid_json", lambda: assert_validation_pass(fixture_invalid_json))
        covered.append("fixture_invalid_json")

        blockers_invalid_json = root / "blockers_invalid_json"
        write_sample_root(blockers_invalid_json)
        write_text(blockers_invalid_json / BLOCKERS_REL, '{"status": "parked",\n')
        expect_failure("blockers_invalid_json", lambda: assert_validation_pass(blockers_invalid_json))
        covered.append("blockers_invalid_json")

        helper_count_drift = root / "helper_count_drift"
        write_sample_root(helper_count_drift)
        manifest = load_json(helper_count_drift / MANIFEST_REL)
        assert isinstance(manifest, dict)
        manifest["helper_count"] = len(HELPERS) - 1
        write_json(helper_count_drift / MANIFEST_REL, manifest)
        expect_failure("helper_count_drift", lambda: assert_validation_pass(helper_count_drift))
        covered.append("helper_count_drift")

        shared_helper_drift = root / "shared_helper_drift"
        write_sample_root(shared_helper_drift)
        manifest = load_json(shared_helper_drift / MANIFEST_REL)
        assert isinstance(manifest, dict)
        lane = manifest["lane_sequencing"]
        assert isinstance(lane, dict)
        lane["shared_replay_parked_helpers"] = SHARED_HELPERS[:-1]
        write_json(shared_helper_drift / MANIFEST_REL, manifest)
        expect_failure("shared_helper_drift", lambda: assert_validation_pass(shared_helper_drift))
        covered.append("shared_helper_drift")

        direct_helper_drift = root / "direct_helper_drift"
        write_sample_root(direct_helper_drift)
        blockers = load_json(direct_helper_drift / BLOCKERS_REL)
        assert isinstance(blockers, dict)
        blocker_lane = blockers["lane_sequencing"]
        assert isinstance(blocker_lane, dict)
        blocker_lane["direct_anchor_followup_helpers"] = DIRECT_HELPERS[:-1]
        write_json(direct_helper_drift / BLOCKERS_REL, blockers)
        expect_failure("direct_helper_drift", lambda: assert_validation_pass(direct_helper_drift))
        covered.append("direct_helper_drift")

        fixture_section_drift = root / "fixture_section_drift"
        write_sample_root(fixture_section_drift)
        fixture = load_json(fixture_section_drift / FIXTURE_REL)
        assert isinstance(fixture, dict)
        fixture.pop("vsprintf")
        write_json(fixture_section_drift / FIXTURE_REL, fixture)
        expect_failure("fixture_section_drift", lambda: assert_validation_pass(fixture_section_drift))
        covered.append("fixture_section_drift")

        fixture_sentinel_drift = root / "fixture_sentinel_drift"
        write_sample_root(fixture_sentinel_drift)
        fixture = load_json(fixture_sentinel_drift / FIXTURE_REL)
        assert isinstance(fixture, dict)
        slab = fixture["slab"]
        assert isinstance(slab, dict)
        slab["zero_after_kmalloc"] = False
        write_json(fixture_sentinel_drift / FIXTURE_REL, fixture)
        expect_failure("fixture_sentinel_drift", lambda: assert_validation_pass(fixture_sentinel_drift))
        covered.append("fixture_sentinel_drift")

        replay_state_drift = root / "replay_state_drift"
        write_sample_root(replay_state_drift)
        blockers = load_json(replay_state_drift / BLOCKERS_REL)
        assert isinstance(blockers, dict)
        replay = blockers["replay"]
        assert isinstance(replay, dict)
        replay["state"] = "ready"
        write_json(replay_state_drift / BLOCKERS_REL, blockers)
        expect_failure("replay_state_drift", lambda: assert_validation_pass(replay_state_drift))
        covered.append("replay_state_drift")

        c_harness_state_drift = root / "c_harness_state_drift"
        write_sample_root(c_harness_state_drift)
        blockers = load_json(c_harness_state_drift / BLOCKERS_REL)
        assert isinstance(blockers, dict)
        c_harness = blockers["c_harness"]
        assert isinstance(c_harness, dict)
        c_harness["state"] = "ready"
        write_json(c_harness_state_drift / BLOCKERS_REL, blockers)
        expect_failure("c_harness_state_drift", lambda: assert_validation_pass(c_harness_state_drift))
        covered.append("c_harness_state_drift")

    assert covered == SELF_TEST_CASES, "self_test_case_order"
    print("PHASE1_ARTIFACT_DIFF_NOTE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_ARTIFACT_DIFF_NOTE_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print(
        "PHASE1_ARTIFACT_DIFF_NOTE_PACKET_SELF_TEST_CASES="
        + ",".join(SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        if not args.self_test and args.root == ROOT:
            return 0
    if args.self_test:
        return run_self_test()

    lines = validate(args.root.resolve())
    for line in lines:
        print(line)
    return 0 if is_pass(lines) else 1


if __name__ == "__main__":
    raise SystemExit(main())

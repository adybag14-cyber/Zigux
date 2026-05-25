#!/usr/bin/env python3
"""Guard the Phase 1 parity-fixture ownership packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

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
DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]
ARTIFACT_DIFF_MARKERS = [
    'MODE_CHOICES = ("text", "json", "bytes")',
    'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
    '"json_pass"',
    '"bytes_pass"',
    '"legacy_sha256_alias"',
]
OWNERSHIP_LIST_SUFFIXES = ("_fixture_keys", "_replay_keys", "_review_fields")
FIXTURE_SENTINELS = {
    "bitmap.partial_xor_nbits": 4,
    "find_bit.tail_clamped_last": 67,
    "rbtree.cached_leftmost_return_serials": [0, -1, 2, -1],
    "slab.zero_after_kmalloc": True,
    "string.replace_char_cstr_end": 2,
}
SELF_TEST_CASES = [
    "round_trip",
    "sample_root_writer",
    "missing_artifact_marker",
    "helper_count_drift",
    "fixture_section_drift",
    "missing_review_anchor",
    "missing_owned_key",
    "direct_helper_ownership_missing",
    "sentinel_drift",
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
    "vsprintf": {"scnprintf_text": "zigux:7", "scnprintf_len": 7, "pad_text": "id=7    ", "pad_len": 7},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check the current Phase 1 helper-manifest to parity-fixture ownership packet."
        )
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


def sample_review_anchor(helper: str, section: str) -> dict[str, object]:
    keys = list(SAMPLE_FIXTURE[section].keys())
    anchor = {
        "helper_test_anchors": [f'test "{section} parity anchor stays explicit"'],
        "phase1_helper_replay_anchor": f'test "{section} shared replay stays explicit"',
        "next_safe_step_note": f"Keep {helper} parked unless the committed fixture keys drift.",
    }
    if helper in DIRECT_HELPERS:
        anchor["review_packet_summary"] = f"{section} direct-anchor ownership stays explicit."
        anchor["parity_fixture_keys"] = keys[: min(4, len(keys))]
        if section == "bitmap":
            anchor["shared_logical_fixture_keys"] = [
                "weight",
                "and_values",
                "andnot_values",
                "or_values",
                "xor_values",
                "equal",
                "intersects",
                "subset",
            ]
            anchor["shared_range_fixture_keys"] = [
                "range_after_set",
                "range_after_clear",
                "full_after_fill",
                "empty_after_zero",
            ]
            anchor["partial_xor_review_fields"] = [
                "partial_xor_nbits",
                "partial_xor_masked_values",
            ]
        elif section == "find_bit":
            anchor["tail_clamp_fixture_keys"] = [
                "tail_clamped_first",
                "tail_clamped_next",
                "tail_zero_clamped_first",
                "tail_zero_clamped_next",
                "tail_and_clamped_first",
                "tail_and_clamped_next",
                "tail_clamped_last",
                "tail_clamped_empty_last",
            ]
            anchor["tail_inclusive_boundary_fixture_keys"] = [
                "tail_inclusive_boundary_next",
                "tail_inclusive_boundary_zero",
                "tail_inclusive_boundary_and",
            ]
        elif section == "rbtree":
            anchor["traversal_replay_keys"] = [
                "empty_root",
                "insert_order",
                "reverse_order",
                "replace_order",
                "erase_init_order",
                "postorder_count",
            ]
            anchor["duplicate_search_replay_keys"] = [
                "find_found_key",
                "find_missing",
                "find_first_serial",
                "next_match_serials",
                "match_iterator_serials",
                "next_match_terminal_null",
            ]
            anchor["cached_leftmost_fixture_keys"] = ["cached_leftmost_return_serials"]
        elif section == "string":
            anchor["counted_search_review_fields"] = [
                "replace_char",
                "replace_char_end",
                "replace_char_cstr_end",
                "replace_char_cstr_bytes",
            ]
    else:
        anchor["shared_replay_summary"] = f"{section} shared fixture ownership stays explicit."
        anchor["parity_fixture_keys"] = keys[: min(3, len(keys))]
    return anchor


def sample_manifest_payload() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(HELPERS),
        "helpers": HELPERS,
        "review_anchors": {
            helper: sample_review_anchor(helper, section)
            for helper, section in HELPER_TO_SECTION.items()
        },
    }


def write_sample_root(root: Path) -> None:
    write_text(root / ARTIFACT_DIFF_REL, sample_artifact_diff_text())
    write_json(root / MANIFEST_REL, sample_manifest_payload())
    write_json(root / FIXTURE_REL, SAMPLE_FIXTURE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(read_text(path))


def ensure(condition: bool, issues: list[str], label: str) -> None:
    if not condition:
        issues.append(label)


def is_nonempty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def ownership_groups(anchor: dict[str, object]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for key, value in anchor.items():
        if not isinstance(value, list):
            continue
        if not any(key.endswith(suffix) for suffix in OWNERSHIP_LIST_SUFFIXES):
            continue
        if not all(isinstance(item, str) and item.strip() for item in value):
            continue
        groups[key] = list(value)
    return groups


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    artifact_diff_path = root / ARTIFACT_DIFF_REL
    manifest_path = root / MANIFEST_REL
    fixture_path = root / FIXTURE_REL
    ensure(artifact_diff_path.is_file(), issues, f"missing:{ARTIFACT_DIFF_REL.as_posix()}")
    ensure(manifest_path.is_file(), issues, f"missing:{MANIFEST_REL.as_posix()}")
    ensure(fixture_path.is_file(), issues, f"missing:{FIXTURE_REL.as_posix()}")
    if issues:
        return issues

    artifact_diff_text = read_text(artifact_diff_path)
    for marker in ARTIFACT_DIFF_MARKERS:
        ensure(marker in artifact_diff_text, issues, f"artifact_diff:marker:{marker}")

    manifest = load_json(manifest_path)
    fixture = load_json(fixture_path)
    ensure(isinstance(manifest, dict), issues, "manifest:not_object")
    ensure(isinstance(fixture, dict), issues, "fixture:not_object")
    if issues:
        return issues

    ensure(manifest.get("phase") == "Phase 1", issues, "manifest:phase")
    ensure(manifest.get("status") == "closed", issues, "manifest:status")
    ensure(manifest.get("helper_count") == len(HELPERS), issues, "manifest:helper_count")
    ensure(manifest.get("helpers") == HELPERS, issues, "manifest:helpers")
    ensure(sorted(fixture.keys()) == sorted(SECTIONS), issues, "fixture:sections")
    ensure(len(fixture) == len(SECTIONS), issues, "fixture:section_count")

    review_anchors = manifest.get("review_anchors")
    ensure(isinstance(review_anchors, dict), issues, "manifest:review_anchors")
    if not isinstance(review_anchors, dict):
        return issues

    helper_with_ownership = 0
    direct_ownership_helper_count = 0
    owned_key_group_count = 0
    for helper, section in HELPER_TO_SECTION.items():
        anchor = review_anchors.get(helper)
        ensure(isinstance(anchor, dict), issues, f"manifest:review_anchor:{helper}")
        section_payload = fixture.get(section)
        ensure(isinstance(section_payload, dict), issues, f"fixture:section:{section}")
        if not isinstance(anchor, dict) or not isinstance(section_payload, dict):
            continue

        helper_tests = anchor.get("helper_test_anchors")
        ensure(
            is_nonempty_string_list(helper_tests) and len(set(helper_tests)) == len(helper_tests),
            issues,
            f"manifest:helper_test_anchors:{helper}",
        )
        ensure(
            isinstance(anchor.get("phase1_helper_replay_anchor"), str)
            and bool(str(anchor.get("phase1_helper_replay_anchor")).strip()),
            issues,
            f"manifest:phase1_helper_replay_anchor:{helper}",
        )
        ensure(
            isinstance(anchor.get("next_safe_step_note"), str)
            and bool(str(anchor.get("next_safe_step_note")).strip()),
            issues,
            f"manifest:next_safe_step_note:{helper}",
        )
        summary_keys = [
            key
            for key, value in anchor.items()
            if key.endswith("_summary") and isinstance(value, str) and value.strip()
        ]
        ensure(bool(summary_keys), issues, f"manifest:summary:{helper}")

        groups = ownership_groups(anchor)
        if groups:
            helper_with_ownership += 1
        if helper in DIRECT_HELPERS:
            ensure(bool(groups), issues, f"manifest:direct_ownership:{helper}")
            if groups:
                direct_ownership_helper_count += 1

        for group_name, keys in groups.items():
            ensure(len(set(keys)) == len(keys), issues, f"manifest:group_duplicates:{helper}:{group_name}")
            owned_key_group_count += 1
            for key in keys:
                ensure(
                    key in section_payload,
                    issues,
                    f"fixture:missing_key:{helper}:{group_name}:{key}",
                )

    for dotted_key, expected_value in FIXTURE_SENTINELS.items():
        section_name, key = dotted_key.split(".", 1)
        section_payload = fixture.get(section_name)
        ensure(isinstance(section_payload, dict), issues, f"fixture:sentinel_section:{section_name}")
        if isinstance(section_payload, dict):
            ensure(
                section_payload.get(key) == expected_value,
                issues,
                f"fixture:sentinel:{dotted_key}",
            )

    if issues:
        return issues

    return [
        "PHASE1_PARITY_FIXTURE_OWNERSHIP=pass",
        "PHASE1_PARITY_FIXTURE_OWNERSHIP_ARTIFACT_MODE_COUNT=3",
        f"PHASE1_PARITY_FIXTURE_OWNERSHIP_HELPER_COUNT={len(HELPERS)}",
        f"PHASE1_PARITY_FIXTURE_OWNERSHIP_FIXTURE_SECTION_COUNT={len(SECTIONS)}",
        f"PHASE1_PARITY_FIXTURE_OWNERSHIP_DIRECT_HELPER_COUNT={len(DIRECT_HELPERS)}",
        f"PHASE1_PARITY_FIXTURE_OWNERSHIP_HELPERS_WITH_OWNED_KEYS={helper_with_ownership}",
        f"PHASE1_PARITY_FIXTURE_OWNERSHIP_DIRECT_HELPERS_WITH_OWNED_KEYS={direct_ownership_helper_count}",
        f"PHASE1_PARITY_FIXTURE_OWNERSHIP_OWNED_KEY_GROUP_COUNT={owned_key_group_count}",
        f"PHASE1_PARITY_FIXTURE_OWNERSHIP_SENTINEL_COUNT={len(FIXTURE_SENTINELS)}",
    ]


def is_pass(lines: list[str]) -> bool:
    return bool(lines) and lines[0] == "PHASE1_PARITY_FIXTURE_OWNERSHIP=pass"


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_fixture_ownership_") as tmp_dir:
        root = Path(tmp_dir)
        sample_root = root / "sample"
        write_sample_root(sample_root)

        lines = validate(sample_root)
        assert is_pass(lines), "round_trip"
        covered.append("round_trip")

        writer_root = root / "writer"
        write_sample_root(writer_root)
        assert (writer_root / MANIFEST_REL).is_file(), "sample_root_writer"
        assert (writer_root / FIXTURE_REL).is_file(), "sample_root_writer"
        covered.append("sample_root_writer")

        missing_artifact_marker = root / "missing_artifact_marker"
        write_sample_root(missing_artifact_marker)
        artifact_diff_path = missing_artifact_marker / ARTIFACT_DIFF_REL
        artifact_diff_path.write_text(
            read_text(artifact_diff_path).replace('"bytes_pass"', '"bytes_pass_removed"', 1),
            encoding="utf-8",
            newline="\n",
        )
        expect_failure(
            "missing_artifact_marker",
            lambda: assert_validation_pass(missing_artifact_marker),
        )
        covered.append("missing_artifact_marker")

        helper_count_drift = root / "helper_count_drift"
        write_sample_root(helper_count_drift)
        manifest = load_json(helper_count_drift / MANIFEST_REL)
        assert isinstance(manifest, dict)
        manifest["helper_count"] = len(HELPERS) - 1
        write_json(helper_count_drift / MANIFEST_REL, manifest)
        expect_failure(
            "helper_count_drift",
            lambda: assert_validation_pass(helper_count_drift),
        )
        covered.append("helper_count_drift")

        fixture_section_drift = root / "fixture_section_drift"
        write_sample_root(fixture_section_drift)
        fixture = load_json(fixture_section_drift / FIXTURE_REL)
        assert isinstance(fixture, dict)
        fixture.pop("slab")
        write_json(fixture_section_drift / FIXTURE_REL, fixture)
        expect_failure(
            "fixture_section_drift",
            lambda: assert_validation_pass(fixture_section_drift),
        )
        covered.append("fixture_section_drift")

        missing_review_anchor = root / "missing_review_anchor"
        write_sample_root(missing_review_anchor)
        manifest = load_json(missing_review_anchor / MANIFEST_REL)
        assert isinstance(manifest, dict)
        review_anchors = manifest["review_anchors"]
        assert isinstance(review_anchors, dict)
        review_anchors.pop("tools/lib/string.zig")
        write_json(missing_review_anchor / MANIFEST_REL, manifest)
        expect_failure(
            "missing_review_anchor",
            lambda: assert_validation_pass(missing_review_anchor),
        )
        covered.append("missing_review_anchor")

        missing_owned_key = root / "missing_owned_key"
        write_sample_root(missing_owned_key)
        manifest = load_json(missing_owned_key / MANIFEST_REL)
        assert isinstance(manifest, dict)
        review_anchors = manifest["review_anchors"]
        assert isinstance(review_anchors, dict)
        string_anchor = review_anchors["tools/lib/string.zig"]
        assert isinstance(string_anchor, dict)
        string_anchor["parity_fixture_keys"] = ["replace_char", "missing_key"]
        write_json(missing_owned_key / MANIFEST_REL, manifest)
        expect_failure(
            "missing_owned_key",
            lambda: assert_validation_pass(missing_owned_key),
        )
        covered.append("missing_owned_key")

        direct_helper_ownership_missing = root / "direct_helper_ownership_missing"
        write_sample_root(direct_helper_ownership_missing)
        manifest = load_json(direct_helper_ownership_missing / MANIFEST_REL)
        assert isinstance(manifest, dict)
        review_anchors = manifest["review_anchors"]
        assert isinstance(review_anchors, dict)
        bitmap_anchor = review_anchors["tools/lib/bitmap.zig"]
        assert isinstance(bitmap_anchor, dict)
        for key in [
            "parity_fixture_keys",
            "shared_logical_fixture_keys",
            "shared_range_fixture_keys",
            "partial_xor_review_fields",
        ]:
            bitmap_anchor.pop(key, None)
        write_json(direct_helper_ownership_missing / MANIFEST_REL, manifest)
        expect_failure(
            "direct_helper_ownership_missing",
            lambda: assert_validation_pass(direct_helper_ownership_missing),
        )
        covered.append("direct_helper_ownership_missing")

        sentinel_drift = root / "sentinel_drift"
        write_sample_root(sentinel_drift)
        fixture = load_json(sentinel_drift / FIXTURE_REL)
        assert isinstance(fixture, dict)
        bitmap = fixture["bitmap"]
        assert isinstance(bitmap, dict)
        bitmap["partial_xor_nbits"] = 5
        write_json(sentinel_drift / FIXTURE_REL, fixture)
        expect_failure(
            "sentinel_drift",
            lambda: assert_validation_pass(sentinel_drift),
        )
        covered.append("sentinel_drift")

    assert covered == SELF_TEST_CASES, "self_test_case_order"
    print("PHASE1_PARITY_FIXTURE_OWNERSHIP_SELF_TEST=pass")
    print(f"PHASE1_PARITY_FIXTURE_OWNERSHIP_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print(
        "PHASE1_PARITY_FIXTURE_OWNERSHIP_SELF_TEST_CASES="
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

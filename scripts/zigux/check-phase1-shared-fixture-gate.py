#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json"
MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json"

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

EXPECTED_SECTIONS = [
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

EXPECTED_SECTION_KEYS = {
    "find_bit": [
        "bits_per_long",
        "first",
        "next_after_6",
        "next_after_word",
        "first_zero",
        "next_zero",
        "first_and",
        "next_and",
        "last",
        "inclusive_boundary_next",
        "inclusive_boundary_zero",
        "inclusive_boundary_and",
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
        "past_nbits_next",
        "past_nbits_zero",
        "past_nbits_and",
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last",
    ],
    "bitmap": [
        "weight",
        "scnprintf",
        "truncated_scnprintf_len",
        "truncated_scnprintf",
        "terminator_only_scnprintf_len",
        "terminator_only_nul",
        "zero_length_scnprintf_len",
        "alloc_words",
        "zalloc_words",
        "zalloc_values",
        "copy_values",
        "copy_clear_tail_values",
        "copy_and_extend_values",
        "and_result",
        "and_values",
        "andnot_result",
        "andnot_values",
        "or_values",
        "xor_values",
        "partial_xor_nbits",
        "partial_xor_masked_values",
        "equal",
        "intersects",
        "subset",
        "range_after_set",
        "range_after_clear",
        "full_after_fill",
        "empty_after_zero",
    ],
    "string": [
        "strtobool_y",
        "strtobool_on",
        "strtobool_zero",
        "strtobool_off",
        "strtobool_invalid",
        "strlcpy_len",
        "strlcpy_buffer",
        "skip_spaces",
        "trim_spaces",
        "remove_spaces",
        "replace_char",
        "replace_char_end",
        "replace_char_cstr_end",
        "replace_char_cstr_bytes",
        "memchr_inv_index",
        "memchr_inv_none",
    ],
    "rbtree": [
        "empty_root",
        "insert_order",
        "reverse_order",
        "replace_order",
        "erase_init_order",
        "postorder_count",
        "erase_init_node_empty",
        "cleared_node_empty",
        "find_found_key",
        "find_missing",
        "find_first_serial",
        "next_match_serials",
        "match_iterator_serials",
        "cached_leftmost_return_serials",
        "next_match_terminal_null",
    ],
    "argv_split": ["argc", "argv", "blank_argc"],
    "cmdline": ["decimal_k", "hex_m", "octal_k", "invalid"],
    "ctype": [
        "mask_A",
        "mask_a",
        "mask_space",
        "isalnum_A",
        "isalpha_z",
        "isdigit_7",
        "isspace_tab",
        "isxdigit_f",
        "ispunct_bang",
        "tolower_A",
        "toupper_z",
        "isodigit_7",
        "isodigit_8",
    ],
    "hweight": ["w8", "w16", "w32", "w64", "wlong"],
    "list_sort": [
        "tri_sorted_keys",
        "tri_sorted_ordinals",
        "bool_sorted_keys",
        "bool_sorted_ordinals",
    ],
    "zalloc": ["zeroed", "freed_is_null", "value_zeroed", "value_freed_is_null"],
    "str_error_r": ["enoent", "unknown"],
    "slab": [
        "null_without_reclaim",
        "alloc_count_after_kmalloc",
        "zero_after_kmalloc",
        "alloc_count_after_kmalloc_free",
        "array_zeroed",
        "alloc_count_after_kmalloc_array",
        "alloc_count_after_kmalloc_array_free",
        "slab_is_available",
    ],
    "vsprintf": ["scnprintf_text", "scnprintf_len", "pad_text", "pad_len"],
}

EXPECTED_SENTINELS = {
    "find_bit.tail_inclusive_boundary_next": 68,
    "find_bit.tail_inclusive_boundary_zero": 68,
    "find_bit.tail_inclusive_boundary_and": 68,
    "find_bit.tail_clamped_first": 67,
    "find_bit.tail_clamped_next": 69,
    "bitmap.partial_xor_nbits": 4,
    "bitmap.copy_and_extend_values": [18446744073709551615, 31, 0],
    "string.strtobool_invalid": 184,
    "rbtree.cached_leftmost_return_serials": [0, -1, 2, -1],
    "cmdline.decimal_k.value": 65536,
    "cmdline.decimal_k.rest": " rest",
    "slab.zero_after_kmalloc": True,
    "vsprintf.pad_text": "id=7    ",
}

EXPECTED_FIXTURE_JSON = r"""{"find_bit":{"bits_per_long":64,"first":5,"next_after_6":67,"next_after_word":135,"first_zero":3,"next_zero":68,"first_and":9,"next_and":66,"last":135,"inclusive_boundary_next":63,"inclusive_boundary_zero":63,"inclusive_boundary_and":63,"tail_inclusive_boundary_next":68,"tail_inclusive_boundary_zero":68,"tail_inclusive_boundary_and":68,"past_nbits_next":7,"past_nbits_zero":7,"past_nbits_and":7,"tail_clamped_first":67,"tail_clamped_next":69,"tail_zero_clamped_first":69,"tail_zero_clamped_next":69,"tail_and_clamped_first":67,"tail_and_clamped_next":69,"tail_clamped_last":67,"tail_clamped_empty_last":69},"bitmap":{"weight":3,"scnprintf":"1-3,7,10-11","truncated_scnprintf_len":7,"truncated_scnprintf":"1-3,7,1","terminator_only_scnprintf_len":0,"terminator_only_nul":0,"zero_length_scnprintf_len":0,"alloc_words":2,"zalloc_words":2,"zalloc_values":[0,0],"copy_values":[18446744073709551615,18446744073709551615],"copy_clear_tail_values":[18446744073709551615,31],"copy_and_extend_values":[18446744073709551615,31,0],"and_result":true,"and_values":[10,0],"andnot_result":true,"andnot_values":[4,0],"or_values":[14,0],"xor_values":[4,0],"partial_xor_nbits":4,"partial_xor_masked_values":[14],"equal":true,"intersects":true,"subset":true,"range_after_set":[14,12,0],"range_after_clear":[0,0,0],"full_after_fill":true,"empty_after_zero":true},"string":{"strtobool_y":true,"strtobool_on":true,"strtobool_zero":false,"strtobool_off":false,"strtobool_invalid":184,"strlcpy_len":5,"strlcpy_buffer":"hel","skip_spaces":"hello","trim_spaces":"hi","remove_spaces":"abc","replace_char":"a_b","replace_char_end":3,"replace_char_cstr_end":2,"replace_char_cstr_bytes":[97,95,0,45,122],"memchr_inv_index":4,"memchr_inv_none":true},"rbtree":{"empty_root":true,"insert_order":[5,10,15,20,25],"reverse_order":[25,20,15,10,5],"replace_order":[5,10,15,25],"erase_init_order":[5,15,25],"postorder_count":3,"erase_init_node_empty":true,"cleared_node_empty":true,"find_found_key":15,"find_missing":true,"find_first_serial":0,"next_match_serials":[0,2,4],"match_iterator_serials":[0,2,4],"cached_leftmost_return_serials":[0,-1,2,-1],"next_match_terminal_null":true},"argv_split":{"argc":3,"argv":["alpha","beta","gamma"],"blank_argc":0},"cmdline":{"decimal_k":{"value":65536,"rest":" rest"},"hex_m":{"value":33554432,"rest":""},"octal_k":{"value":8192,"rest":""},"invalid":{"value":0,"rest":"xyz"}},"ctype":{"mask_A":65,"mask_a":66,"mask_space":160,"isalnum_A":true,"isalpha_z":true,"isdigit_7":true,"isspace_tab":true,"isxdigit_f":true,"ispunct_bang":true,"tolower_A":97,"toupper_z":90,"isodigit_7":true,"isodigit_8":false},"hweight":{"w8":4,"w16":8,"w32":16,"w64":32,"wlong":8},"list_sort":{"tri_sorted_keys":[1,1,2,3,3],"tri_sorted_ordinals":[1,3,0,2,4],"bool_sorted_keys":[1,1,2,3,3],"bool_sorted_ordinals":[1,3,0,2,4]},"zalloc":{"zeroed":true,"freed_is_null":true,"value_zeroed":true,"value_freed_is_null":true},"str_error_r":{"enoent":"No such file or directory","unknown":"INTERNAL ERROR: strerror_r(4096, [buf], 64)=22"},"slab":{"null_without_reclaim":true,"alloc_count_after_kmalloc":1,"zero_after_kmalloc":true,"alloc_count_after_kmalloc_free":0,"array_zeroed":true,"alloc_count_after_kmalloc_array":1,"alloc_count_after_kmalloc_array_free":0,"slab_is_available":true},"vsprintf":{"scnprintf_text":"zigux:7","scnprintf_len":7,"pad_text":"id=7    ","pad_len":7}}"""


class DuplicateKeyError(ValueError):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def get_nested(value: object, dotted_path: str) -> object:
    current = value
    for key in dotted_path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def load_json_object(root: Path, rel: str) -> tuple[dict[str, object] | None, str | None]:
    path = root / rel
    if not path.exists():
        return None, f"missing_file:{rel}"
    if not path.is_file():
        return None, f"not_a_file:{rel}"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None, f"read_error:{rel}"
    try:
        payload = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except DuplicateKeyError:
        return None, f"duplicate_key:{rel}"
    except json.JSONDecodeError:
        return None, f"invalid_json:{rel}"
    if not isinstance(payload, dict):
        return None, f"object_required:{rel}"
    return payload, None


def collect_issues(root: Path) -> list[str]:
    fixture, fixture_error = load_json_object(root, FIXTURE_REL)
    manifest, manifest_error = load_json_object(root, MANIFEST_REL)

    issues: list[str] = []
    if fixture_error:
        issues.append(fixture_error)
    if manifest_error:
        issues.append(manifest_error)
    if issues:
        return issues

    assert fixture is not None
    assert manifest is not None

    helpers = manifest.get("helpers")
    if helpers != EXPECTED_HELPERS:
        issues.append("manifest:helpers=expected_phase1_helper_list")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append(f"manifest:helper_count={len(EXPECTED_HELPERS)}")
    if manifest.get("phase") != "Phase 1":
        issues.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        issues.append("manifest:status=closed")

    section_names = list(fixture.keys())
    if section_names != EXPECTED_SECTIONS:
        issues.append("fixture:sections=expected_phase1_fixture_sections")

    for section, expected_keys in EXPECTED_SECTION_KEYS.items():
        actual_section = fixture.get(section)
        if not isinstance(actual_section, dict):
            issues.append(f"fixture:missing_section={section}")
            continue
        if list(actual_section.keys()) != expected_keys:
            issues.append(f"fixture:section_keys={section}")

    for dotted_path, expected_value in EXPECTED_SENTINELS.items():
        section_name, _, nested_path = dotted_path.partition(".")
        actual_value = get_nested(fixture.get(section_name), nested_path)
        if actual_value != expected_value:
            issues.append(f"fixture:sentinel={dotted_path}")

    if len(section_names) != len(EXPECTED_HELPERS):
        issues.append(f"fixture:section_count={len(EXPECTED_HELPERS)}")

    return issues


def expected_fixture() -> dict[str, object]:
    return json.loads(EXPECTED_FIXTURE_JSON, object_pairs_hook=reject_duplicate_keys)


def expected_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
    }


def write_json(path: Path, payload: object) -> None:
    if path.exists() and path.is_dir():
        path.rmdir()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_json(root / FIXTURE_REL, expected_fixture())
    write_json(root / MANIFEST_REL, expected_manifest())


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_shared_fixture_gate_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []

        (root / FIXTURE_REL).unlink()
        assert collect_issues(root) == [f"missing_file:{FIXTURE_REL}"]
        case_count += 1
        build_sample_root(root)

        (root / FIXTURE_REL).unlink()
        (root / FIXTURE_REL).mkdir(parents=True)
        assert collect_issues(root) == [f"not_a_file:{FIXTURE_REL}"]
        case_count += 1
        build_sample_root(root)

        (root / FIXTURE_REL).write_text("{", encoding="utf-8")
        assert collect_issues(root) == [f"invalid_json:{FIXTURE_REL}"]
        case_count += 1
        build_sample_root(root)

        (root / FIXTURE_REL).write_text('{"find_bit": {}, "find_bit": {}}', encoding="utf-8")
        assert collect_issues(root) == [f"duplicate_key:{FIXTURE_REL}"]
        case_count += 1
        build_sample_root(root)

        fixture = expected_fixture()
        assert isinstance(fixture["find_bit"], dict)
        fixture["find_bit"].pop("tail_inclusive_boundary_next")
        write_json(root / FIXTURE_REL, fixture)
        issues = collect_issues(root)
        assert "fixture:section_keys=find_bit" in issues
        assert "fixture:sentinel=find_bit.tail_inclusive_boundary_next" in issues
        case_count += 1
        build_sample_root(root)

        fixture = expected_fixture()
        assert isinstance(fixture["string"], dict)
        fixture["string"]["strtobool_invalid"] = -22
        write_json(root / FIXTURE_REL, fixture)
        assert "fixture:sentinel=string.strtobool_invalid" in collect_issues(root)
        case_count += 1
        build_sample_root(root)

        fixture = expected_fixture()
        reordered = {"bitmap": fixture["bitmap"]}
        for key, value in fixture.items():
            if key != "bitmap":
                reordered[key] = value
        write_json(root / FIXTURE_REL, reordered)
        assert "fixture:sections=expected_phase1_fixture_sections" in collect_issues(root)
        case_count += 1
        build_sample_root(root)

        manifest = expected_manifest()
        manifest["helper_count"] = 12
        write_json(root / MANIFEST_REL, manifest)
        assert f"manifest:helper_count={len(EXPECTED_HELPERS)}" in collect_issues(root)
        case_count += 1
        build_sample_root(root)

        manifest = expected_manifest()
        manifest["helpers"] = EXPECTED_HELPERS[:-1]
        write_json(root / MANIFEST_REL, manifest)
        assert "manifest:helpers=expected_phase1_helper_list" in collect_issues(root)
        case_count += 1

    print("PHASE1_SHARED_FIXTURE_GATE_SELF_TEST=pass")
    print(f"PHASE1_SHARED_FIXTURE_GATE_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the committed Phase 1 shared helper fixture surface."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a current-like sample root for focused checker replay.",
    )
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        run_self_test()
        return 0

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_SHARED_FIXTURE_GATE=fail")
        print("PHASE1_SHARED_FIXTURE_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_SHARED_FIXTURE_GATE_ISSUES_END")
        return 1

    print("PHASE1_SHARED_FIXTURE_GATE=pass")
    print(f"PHASE1_SHARED_FIXTURE_GATE_SECTION_COUNT={len(EXPECTED_SECTIONS)}")
    print(f"PHASE1_SHARED_FIXTURE_GATE_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_SHARED_FIXTURE_GATE_SENTINEL_COUNT={len(EXPECTED_SENTINELS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

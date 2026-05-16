#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
ROOT = THIS_FILE.parents[2] if len(THIS_FILE.parents) >= 3 else THIS_FILE.parent

FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")
ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
PHASE1_HELPERS_REL = Path("zigux/tests/phase1_helpers.zig")

SOURCE_RELS = [
    Path("tools/lib/argv_split.zig"),
    Path("tools/lib/bitmap.zig"),
    Path("tools/lib/cmdline.zig"),
    Path("tools/lib/ctype.zig"),
    Path("tools/lib/find_bit.zig"),
    Path("tools/lib/hweight.zig"),
    Path("tools/lib/list_sort.zig"),
    Path("tools/lib/rbtree.zig"),
    Path("tools/lib/slab.zig"),
    Path("tools/lib/str_error_r.zig"),
    Path("tools/lib/string.zig"),
    Path("tools/lib/vsprintf.zig"),
    Path("tools/lib/zalloc.zig"),
]

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

REQUIRED_PARITY_KEYS = {
    "find_bit": (
        "inclusive_boundary_next",
        "inclusive_boundary_zero",
        "inclusive_boundary_and",
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
    ),
    "bitmap": (
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
    ),
    "string": (
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
    ),
    "rbtree": (
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
    ),
    "argv_split": ("argc", "argv", "blank_argc"),
    "cmdline": ("decimal_k", "hex_m", "octal_k", "invalid"),
    "ctype": (
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
    ),
    "hweight": ("w8", "w16", "w32", "w64", "wlong"),
    "list_sort": (
        "tri_sorted_keys",
        "tri_sorted_ordinals",
        "bool_sorted_keys",
        "bool_sorted_ordinals",
    ),
    "zalloc": ("zeroed", "freed_is_null", "value_zeroed", "value_freed_is_null"),
    "str_error_r": ("enoent", "unknown"),
    "slab": (
        "null_without_reclaim",
        "alloc_count_after_kmalloc",
        "zero_after_kmalloc",
        "alloc_count_after_kmalloc_free",
        "array_zeroed",
        "alloc_count_after_kmalloc_array",
        "alloc_count_after_kmalloc_array_free",
        "slab_is_available",
    ),
    "vsprintf": ("scnprintf_text", "scnprintf_len", "pad_text", "pad_len"),
}

REQUIRED_PHASE1_HELPERS_MARKERS = (
    '@embedFile("fixtures/phase1_helpers.json")',
    'test "phase 1 helper ports match committed parity fixture"',
    "fixture.find_bit.inclusive_boundary_next",
    "fixture.find_bit.tail_clamped_empty_last",
    "fixture.bitmap.truncated_scnprintf",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.string.replace_char_cstr_bytes",
    "fixture.rbtree.cached_leftmost_return_serials",
    "fixture.argv_split.argc",
    "fixture.cmdline.decimal_k.value",
    "fixture.ctype.mask_A",
    "fixture.hweight.w64",
    "fixture.list_sort.tri_sorted_keys",
    "fixture.zalloc.value_freed_is_null",
    "fixture.str_error_r.unknown",
    "fixture.slab.alloc_count_after_kmalloc_array_free",
    "fixture.vsprintf.pad_text",
)


def collect_input_issues(root: Path, source_rels: list[Path] | None = None) -> list[str]:
    rels = source_rels or SOURCE_RELS
    issues: list[str] = []

    for rel in [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL, PHASE1_HELPERS_REL, *rels]:
        if not (root / rel).exists():
            issues.append(f"missing:{rel.as_posix()}")

    return issues


def collect_fixture_issues(path: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"fixture:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(payload, dict):
        return ["fixture:json_object"]

    issues: list[str] = []
    actual_sections = set(payload.keys())
    expected_sections = set(EXPECTED_SECTIONS)

    for section in sorted(expected_sections - actual_sections):
        issues.append(f"missing_section:{section}")
    for section in sorted(actual_sections - expected_sections):
        issues.append(f"unexpected_section:{section}")

    for section_name, required_keys in REQUIRED_PARITY_KEYS.items():
        section = payload.get(section_name)
        if not isinstance(section, dict):
            issues.append(f"invalid_section:{section_name}")
            continue
        for key in required_keys:
            if key not in section:
                issues.append(f"missing_parity_key:{section_name}.{key}")

    return issues


def collect_phase1_helpers_issues(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for marker in REQUIRED_PHASE1_HELPERS_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(f"phase1_helpers_marker:{marker}:expected=1:actual={count}")
    return issues


def make_self_test_root(root: Path) -> None:
    all_files = [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL, PHASE1_HELPERS_REL, *SOURCE_RELS]
    for rel in all_files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel == FIXTURE_REL:
            payload = {
                section: {key: 0 for key in REQUIRED_PARITY_KEYS[section]}
                for section in EXPECTED_SECTIONS
            }
            path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
        elif rel == PHASE1_HELPERS_REL:
            path.write_text("\n".join(REQUIRED_PHASE1_HELPERS_MARKERS) + "\n", encoding="utf-8")
        else:
            path.write_text("// packet\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        make_self_test_root(root)

        assert collect_input_issues(root) == []
        assert collect_fixture_issues(root / FIXTURE_REL) == []
        assert collect_phase1_helpers_issues(root / PHASE1_HELPERS_REL) == []
        case_count += 3

        (root / SOURCE_RELS[0]).unlink()
        assert f"missing:{SOURCE_RELS[0].as_posix()}" in collect_input_issues(root)
        make_self_test_root(root)
        case_count += 1

        fixture_path = root / FIXTURE_REL
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["bitmap"].pop("truncated_scnprintf")
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")) + "\n", encoding="utf-8")
        assert "missing_parity_key:bitmap.truncated_scnprintf" in collect_fixture_issues(fixture_path)
        make_self_test_root(root)
        case_count += 1

        fixture_path.write_text('{"find_bit":', encoding="utf-8")
        errors = collect_fixture_issues(fixture_path)
        assert len(errors) == 1 and errors[0].startswith("fixture:json_decode_error:")
        make_self_test_root(root)
        case_count += 1

        helpers_path = root / PHASE1_HELPERS_REL
        helpers_path.write_text(
            helpers_path.read_text(encoding="utf-8").replace(
                'test "phase 1 helper ports match committed parity fixture"\n', "", 1
            ),
            encoding="utf-8",
        )
        marker_error = (
            'phase1_helpers_marker:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0'
        )
        assert marker_error in collect_phase1_helpers_issues(helpers_path)
        case_count += 1

    print("PHASE1_PARITY_SELF_TEST=pass")
    print(f"PHASE1_PARITY_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the live Phase 1 parity packet against the current Zig helper tree."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading the live repository.",
    )
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = ROOT if args.root is None else Path(args.root).resolve()

    input_issues = collect_input_issues(root)
    if input_issues:
        print("PHASE1_PARITY=fail")
        print("PHASE1_PARITY_INPUT_ISSUES_START")
        for issue in input_issues:
            print(issue)
        print("PHASE1_PARITY_INPUT_ISSUES_END")
        return 1

    fixture_issues = collect_fixture_issues(root / FIXTURE_REL)
    if fixture_issues:
        print("PHASE1_PARITY=fail")
        print("PHASE1_PARITY_FIXTURE_ISSUES_START")
        for issue in fixture_issues:
            print(issue)
        print("PHASE1_PARITY_FIXTURE_ISSUES_END")
        return 1

    helpers_issues = collect_phase1_helpers_issues(root / PHASE1_HELPERS_REL)
    if helpers_issues:
        print("PHASE1_PARITY=fail")
        print("PHASE1_PARITY_HELPERS_ISSUES_START")
        for issue in helpers_issues:
            print(issue)
        print("PHASE1_PARITY_HELPERS_ISSUES_END")
        return 1

    print("PHASE1_PARITY=pass")
    print(f"FIXTURE={root / FIXTURE_REL}")
    print(f"HELPER_TEST={root / PHASE1_HELPERS_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else HERE.parent

FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

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

EXPECTED_FIXTURE = {
    "find_bit": {
        "bits_per_long": 64,
        "first": 5,
        "next_after_6": 9,
        "next_after_word": 66,
        "first_zero": 3,
        "next_zero": 68,
        "first_and": 9,
        "next_and": 66,
        "last": 71,
    },
    "bitmap": {
        "weight": 3,
        "scnprintf": "1-3,66-67",
        "truncated_scnprintf_len": 7,
        "truncated_scnprintf": "1-3,66-",
        "terminator_only_scnprintf_len": 0,
        "terminator_only_nul": 0,
        "zero_length_scnprintf_len": 0,
        "alloc_words": 3,
        "zalloc_words": 3,
        "zalloc_values": [0, 0, 0],
        "copy_values": [18446744073709551615, 18446744073709551615],
        "copy_clear_tail_values": [18446744073709551615, 31],
        "copy_and_extend_values": [18446744073709551615, 31, 0],
        "complement_values": [18446744073709551605, 29],
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
        "cached_root_transition_serials": [0, 0, 4, 2],
        "next_match_terminal_null": True,
    },
    "argv_split": {
        "argc": 3,
        "argv": ["alpha", "beta", "gamma"],
        "blank_argc": 0,
    },
    "cmdline": {
        "decimal_k": {"value": 65536, "rest": " rest"},
        "signed_k": {"value": 18446744073709549568, "rest": " tail"},
        "signed_hex_k": {"value": 18446744073709549568, "rest": "tail"},
        "signed_octal_m": {"value": 8388608, "rest": "more"},
        "saturated_positive_signed": {"value": 9223372036854775807, "rest": ""},
        "option_debug": True,
        "option_empty_leading": True,
        "option_empty_double_comma": True,
        "option_empty_trailing": False,
        "option_absent": False,
        "first_arg": {
            "param": "console",
            "value": "ttyS0,115200",
            "remaining": "root=\"/dev/sda1 quiet\" panic=-1",
        },
        "second_arg": {
            "param": "root",
            "value": "/dev/sda1 quiet",
            "remaining": "panic=-1",
        },
        "quoted_arg": {"param": "mode", "value": "fast path", "remaining": "tail"},
        "empty_quoted_arg": {"param": "root", "value": "", "remaining": "quiet"},
        "unterminated_arg": {"param": "mode", "value": "fast boot", "remaining": ""},
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
        "tiny_unknown": "INTERNA",
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


class DuplicateKeyError(ValueError):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def resolve_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_json_object(path: Path) -> tuple[dict[str, object] | None, str | None]:
    if not path.exists():
        return None, f"missing_file:{path.as_posix()}"
    if not path.is_file():
        return None, f"not_a_file:{path.as_posix()}"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None, f"read_error:{path.as_posix()}"
    try:
        payload = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except DuplicateKeyError:
        return None, f"duplicate_key:{path.as_posix()}"
    except json.JSONDecodeError:
        return None, f"invalid_json:{path.as_posix()}"
    if not isinstance(payload, dict):
        return None, f"object_required:{path.as_posix()}"
    return payload, None


def collect_issues(root: Path) -> list[str]:
    fixture_path = root / FIXTURE_REL
    manifest_path = root / MANIFEST_REL
    fixture, fixture_error = load_json_object(fixture_path)
    manifest, manifest_error = load_json_object(manifest_path)

    issues: list[str] = []
    if fixture_error:
        issues.append(fixture_error)
    if manifest_error:
        issues.append(manifest_error)
    if issues:
        return issues

    assert fixture is not None
    assert manifest is not None

    if fixture != EXPECTED_FIXTURE:
        issues.append("fixture:packet=expected_current_master_phase1_fixture")

    if manifest.get("phase") != "Phase 1":
        issues.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        issues.append("manifest:status=closed")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        issues.append(f"manifest:helper_count={len(EXPECTED_HELPERS)}")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        issues.append("manifest:helpers=expected_phase1_helper_list")

    return issues


def write_json(path: Path, payload: object) -> None:
    if path.exists() and path.is_dir():
        path.rmdir()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
    }


def write_sample_root(root: Path) -> None:
    write_json(root / FIXTURE_REL, EXPECTED_FIXTURE)
    write_json(root / MANIFEST_REL, sample_manifest())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_shared_fixture_gate_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        (root / FIXTURE_REL).unlink()
        assert collect_issues(root) == [f"missing_file:{(root / FIXTURE_REL).as_posix()}"]
        case_count += 1
        write_sample_root(root)

        (root / FIXTURE_REL).unlink()
        (root / FIXTURE_REL).mkdir(parents=True)
        assert collect_issues(root) == [f"not_a_file:{(root / FIXTURE_REL).as_posix()}"]
        case_count += 1
        write_sample_root(root)

        (root / FIXTURE_REL).write_text("{", encoding="utf-8")
        assert collect_issues(root) == [f"invalid_json:{(root / FIXTURE_REL).as_posix()}"]
        case_count += 1
        write_sample_root(root)

        (root / FIXTURE_REL).write_text('{"find_bit": {}, "find_bit": {}}', encoding="utf-8")
        assert collect_issues(root) == [f"duplicate_key:{(root / FIXTURE_REL).as_posix()}"]
        case_count += 1
        write_sample_root(root)

        drifted_fixture = json.loads(json.dumps(EXPECTED_FIXTURE))
        drifted_fixture["bitmap"]["truncated_scnprintf"] = "drift"
        write_json(root / FIXTURE_REL, drifted_fixture)
        assert collect_issues(root) == ["fixture:packet=expected_current_master_phase1_fixture"]
        case_count += 1
        write_sample_root(root)

        drifted_manifest = sample_manifest()
        drifted_manifest["helper_count"] = 12
        write_json(root / MANIFEST_REL, drifted_manifest)
        assert f"manifest:helper_count={len(EXPECTED_HELPERS)}" in collect_issues(root)
        case_count += 1
        write_sample_root(root)

        drifted_manifest = sample_manifest()
        drifted_manifest["helpers"] = EXPECTED_HELPERS[:-1]
        write_json(root / MANIFEST_REL, drifted_manifest)
        assert "manifest:helpers=expected_phase1_helper_list" in collect_issues(root)
        case_count += 1
        write_sample_root(root)

        drifted_manifest = sample_manifest()
        drifted_manifest["phase"] = "Phase X"
        write_json(root / MANIFEST_REL, drifted_manifest)
        assert "manifest:phase=Phase 1" in collect_issues(root)
        case_count += 1

    print("PHASE1_SHARED_FIXTURE_GATE_SELF_TEST=pass")
    print(f"PHASE1_SHARED_FIXTURE_GATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the committed Phase 1 shared helper fixture packet."
    )
    parser.add_argument("--root", help="validate an alternate repository root")
    parser.add_argument("--self-test", action="store_true", help="run embedded self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for focused checker replay",
    )
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(resolve_root(args.root))
    if issues:
        print("PHASE1_SHARED_FIXTURE_GATE=fail")
        print("PHASE1_SHARED_FIXTURE_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_SHARED_FIXTURE_GATE_ISSUES_END")
        return 1

    print("PHASE1_SHARED_FIXTURE_GATE=pass")
    print(f"PHASE1_SHARED_FIXTURE_GATE_SECTION_COUNT={len(EXPECTED_FIXTURE)}")
    print(f"PHASE1_SHARED_FIXTURE_GATE_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_SHARED_FIXTURE_GATE_SENTINEL_COUNT={sum(len(v) if isinstance(v, dict) else 1 for v in EXPECTED_FIXTURE.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

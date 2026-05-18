#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

EXPECTED_DIRECT_ANCHOR_FIXTURE = {
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
        "past_nbits_next": 7,
        "past_nbits_zero": 7,
        "past_nbits_and": 7,
        "tail_clamped_first": 69,
        "tail_clamped_next": 69,
        "tail_zero_clamped_first": 69,
        "tail_zero_clamped_next": 69,
        "tail_and_clamped_first": 69,
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
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def load_fixture_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_fixture(path: Path) -> object:
    return load_fixture_text(path.read_text(encoding="utf-8"))


def validate_fixture_payload(payload: object) -> tuple[str, object]:
    if not isinstance(payload, dict):
        return ("fixture_type", type(payload).__name__)
    if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:
        return ("fixture_duplicate_top_level_keys", payload.duplicate_keys)

    for helper, expected_block in EXPECTED_DIRECT_ANCHOR_FIXTURE.items():
        block = payload.get(helper)
        if block is None:
            return ("missing_helper_block", helper)
        if not isinstance(block, dict):
            return ("helper_block_type", (helper, type(block).__name__))
        if isinstance(block, DuplicateTrackingDict) and block.duplicate_keys:
            return ("helper_block_duplicate_keys", (helper, block.duplicate_keys))
        if block != expected_block:
            return ("helper_block_mismatch", helper)

    return ("pass", None)


def validate_fixture(root: Path) -> tuple[str, object]:
    fixture_path = root / FIXTURE_REL
    try:
        payload = load_fixture(fixture_path)
    except FileNotFoundError:
        return ("missing_fixture_file", fixture_path)
    except json.JSONDecodeError as exc:
        return ("fixture_json_error", (exc.msg, exc.lineno, exc.colno))
    return validate_fixture_payload(payload)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, separators=(",", ":")) + "\n")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-fixture-") as tmp:
        root = Path(tmp)
        write_fixture(root / FIXTURE_REL, EXPECTED_DIRECT_ANCHOR_FIXTURE)
        kind, payload = validate_fixture(root)
        assert kind == "pass", (kind, payload)
        case_count += 1

    duplicate_text = """{"bitmap":{},"bitmap":{"weight":3},"find_bit":{},"string":{},"rbtree":{}}"""
    kind, payload = validate_fixture_payload(load_fixture_text(duplicate_text))
    assert kind == "fixture_duplicate_top_level_keys", (kind, payload)
    assert payload == ["bitmap"], payload
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-fixture-") as tmp:
        root = Path(tmp)
        partial = dict(EXPECTED_DIRECT_ANCHOR_FIXTURE)
        partial.pop("string")
        write_fixture(root / FIXTURE_REL, partial)
        kind, payload = validate_fixture(root)
        assert kind == "missing_helper_block", (kind, payload)
        assert payload == "string", payload
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-fixture-") as tmp:
        root = Path(tmp)
        payload = dict(EXPECTED_DIRECT_ANCHOR_FIXTURE)
        payload["rbtree"] = list(EXPECTED_DIRECT_ANCHOR_FIXTURE["rbtree"].items())
        write_fixture(root / FIXTURE_REL, payload)
        kind, payload = validate_fixture(root)
        assert kind == "helper_block_type", (kind, payload)
        assert payload == ("rbtree", "list"), payload
        case_count += 1

    helper_duplicate_text = """{"find_bit":{"first":5,"first":6},"bitmap":{},"string":{},"rbtree":{}}"""
    kind, payload = validate_fixture_payload(load_fixture_text(helper_duplicate_text))
    assert kind == "helper_block_duplicate_keys", (kind, payload)
    assert payload == ("find_bit", ["first"]), payload
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-fixture-") as tmp:
        root = Path(tmp)
        payload = json.loads(json.dumps(EXPECTED_DIRECT_ANCHOR_FIXTURE))
        payload["bitmap"]["partial_xor_masked_values"] = [13]
        write_fixture(root / FIXTURE_REL, payload)
        kind, payload = validate_fixture(root)
        assert kind == "helper_block_mismatch", (kind, payload)
        assert payload == "bitmap", payload
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-fixture-") as tmp:
        root = Path(tmp)
        kind, payload = validate_fixture(root)
        assert kind == "missing_fixture_file", (kind, payload)
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-fixture-") as tmp:
        root = Path(tmp)
        write_text(root / FIXTURE_REL, "{not-json}\n")
        kind, payload = validate_fixture(root)
        assert kind == "fixture_json_error", (kind, payload)
        case_count += 1

    print("PHASE1_DIRECT_ANCHOR_FIXTURE_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_ANCHOR_FIXTURE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the committed Phase 1 direct-anchor helper fixture packet."
    )
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = ROOT if not args.root else Path(args.root)
    kind, payload = validate_fixture(root)
    if kind != "pass":
        print("PHASE1_DIRECT_ANCHOR_FIXTURE=fail")
        print(f"PHASE1_DIRECT_ANCHOR_FIXTURE_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_DIRECT_ANCHOR_FIXTURE=pass")
    print(f"PHASE1_DIRECT_ANCHOR_FIXTURE_PATH={root / FIXTURE_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

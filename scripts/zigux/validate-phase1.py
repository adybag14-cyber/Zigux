#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any

_SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

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

EXPECTED_MANIFEST = json.loads(
    r"""
{
  "phase": "Phase 1",
  "status": "closed",
  "helper_count": 13,
  "helpers": [
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
    "tools/lib/zalloc.zig"
  ],
  "review_anchors": {
    "tools/lib/bitmap.zig": {
      "helper_test_anchors": [
        "test \"bitmap predicates ignore out-of-range tail bits\"",
        "test \"bitmap range helpers clamp the final partial word\"",
        "test \"bitmap scnprintf collapses contiguous ranges across word boundaries\"",
        "test \"bitmap zero-bit binary helpers stay explicit identity operations\"",
        "test \"bitmap copy and extend handles zero and aligned counts\"",
        "test \"bitmap Linux-style aliases mirror the primary helper surface\""
      ],
      "first_word_boundary_anchor": "test \"bitmap range helpers honor exact first-word boundaries\"",
      "final_partial_word_anchor": "test \"bitmap range helpers clamp the final partial word\"",
      "predicate_tail_mask_anchor": "test \"bitmap predicates ignore out-of-range tail bits\"",
      "parity_fixture_keys": [
        "scnprintf",
        "truncated_scnprintf_len",
        "truncated_scnprintf",
        "terminator_only_scnprintf_len",
        "terminator_only_nul",
        "zero_length_scnprintf_len"
      ],
      "partial_xor_review_fields": [
        "partial_xor_nbits",
        "partial_xor_masked_values"
      ],
      "cross_word_scnprintf_anchor": "test \"bitmap scnprintf collapses contiguous ranges across word boundaries\"",
      "scnprintf_truncation_anchor": "test \"bitmap scnprintf reports full length while truncating the buffer\"",
      "copy_alias_anchor": "test \"bitmap copy aliases preserve tail clearing and extension semantics\"",
      "copy_raw_alias_anchor": "test \"bitmap copy alias preserves raw source words without tail clearing\"",
      "copy_extend_zero_aligned_anchor": "test \"bitmap copy and extend handles zero and aligned counts\"",
      "zero_bit_noop_anchor": "test \"bitmap zero-bit helpers stay explicit no-ops\"",
      "zero_bit_binary_identity_anchor": "test \"bitmap zero-bit binary helpers stay explicit identity operations\"",
      "linux_alias_anchor": "test \"bitmap Linux-style aliases mirror the primary helper surface\""
    },
    "tools/lib/find_bit.zig": {
      "helper_test_anchors": [
        "test \"single-word next scans honor start masks\"",
        "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
        "test \"zero-bit windows return without reading bitmap words\"",
        "test \"next scans past nbits return without reading bitmap words\"",
        "test \"tail-word next set scans skip earlier in-range matches before clamping\"",
        "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
        "test \"low-level underscore aliases mirror the primary find helpers\""
      ],
      "same_word_start_masks": "test \"single-word next scans honor start masks\"",
      "inclusive_boundary_start": "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\"",
      "zero_bit_window": "test \"zero-bit windows return without reading bitmap words\"",
      "past_nbits_short_circuit": "test \"next scans past nbits return without reading bitmap words\"",
      "underscore_alias_anchor": "test \"low-level underscore aliases mirror the primary find helpers\"",
      "tail_word_skip_anchor": "test \"tail-word next zero and shared scans skip earlier in-range matches before clamping\"",
      "tail_clamp_fixture_keys": [
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last"
      ],
      "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, inclusive-boundary, zero-window, past-nbits, tail-word set or zero or shared skip, and underscore-alias behavior review-visible on current master"
    },
    "tools/lib/rbtree.zig": {
      "helper_test_anchors": [
        "test \"rbtree inserts and traverses in sorted order\"",
        "test \"rbtree erase and replace keep traversal consistent\"",
        "test \"rbtree eraseInit detaches erased node\"",
        "test \"rbtree postorder and empty node helpers behave\"",
        "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
        "test \"rbtree nextMatch walks the duplicate range in order\"",
        "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
        "test \"rbtree cached root keeps the leftmost pointer in sync\"",
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
        "test \"rbtree eraseCached returns null for a singleton cached tree\"",
        "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
        "test \"rbtree eraseInitCached clears singleton cached roots before reseed\""
      ],
      "parity_fixture_keys": [
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
        "next_match_terminal_null"
      ],
      "duplicate_search_anchors": [
        "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
        "test \"rbtree nextMatch walks the duplicate range in order\""
      ],
      "cached_root_followup_anchors": [
        "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
        "test \"rbtree cached root keeps the leftmost pointer in sync\"",
        "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
        "test \"rbtree eraseCached returns null for a singleton cached tree\"",
        "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
        "test \"rbtree eraseInitCached clears singleton cached roots before reseed\""
      ],
      "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while cached-root leftmost-insert, leftmost-sync, replacement, singleton-erase, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared cached-root fixture keys"
    },
    "tools/lib/string.zig": {
      "helper_test_anchors": [
        "test \"strtobool accepts common Linux forms\"",
        "test \"strlcpy copies and returns the source length\"",
        "test \"streq matches C-string equality semantics\"",
        "test \"skip trim remove and replace spaces work in place\"",
        "test \"strreplace mirrors replaceChar C-string semantics\"",
        "test \"strHasPrefix honors C-string boundaries\"",
        "test \"strstarts mirrors the header-level prefix helper\"",
        "test \"strEndsWith honors C-string boundaries\"",
        "test \"sysfsStreq treats trailing newline and NUL as equivalent\"",
        "test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\"",
        "test \"memdup and memchrInv preserve byte content\"",
        "test \"memchr_inv mirrors memchrInv byte-search semantics\"",
        "test \"memchrInv keeps long-buffer first-dirty-byte results stable\"",
        "test \"memchrInv follows the earliest dirty byte as long buffers change\"",
        "test \"memchrInv dirty-word shortcut handles zero-value scans at word boundaries\"",
        "test \"memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment\"",
        "test \"memchrInv short zero-value scans stay byte-accurate\"",
        "test \"memparse handles decimal hexadecimal octal and suffixes\"",
        "test \"memparse keeps original rest when sign is not followed by digits\"",
        "test \"memparse saturates signed overflow instead of trapping\"",
        "test \"memparse clamps explicit positive signed overflow\"",
        "test \"memparse keeps signed values and their trailing rest aligned\"",
        "test \"memparse consumes suffix after saturation\"",
        "test \"memparse applies suffixes before signed clamping\"",
        "test \"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\""
      ],
      "memparse_review_anchors": [
        "test \"memparse keeps original rest when sign is not followed by digits\"",
        "test \"memparse saturates signed overflow instead of trapping\"",
        "test \"memparse clamps explicit positive signed overflow\"",
        "test \"memparse keeps signed values and their trailing rest aligned\"",
        "test \"memparse consumes suffix after saturation\"",
        "test \"memparse applies suffixes before signed clamping\""
      ],
      "prefix_suffix_review_anchors": [
        "test \"strHasPrefix honors C-string boundaries\"",
        "test \"strstarts mirrors the header-level prefix helper\"",
        "test \"strEndsWith honors C-string boundaries\""
      ],
      "prefix_suffix_review_summary": "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields",
      "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation",
      "phase1_helper_replay_anchor": "test \"phase 1 string replaceChar stops at embedded NUL\"",
      "shared_replace_char_cstr_review_summary": "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership",
      "parity_fixture_keys": [
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
        "memchr_inv_none"
      ]
    }
  }
}
"""
)

EXPECTED_LANE_SEQUENCING = {
    "shared_replay_parked_helpers": [
        "tools/lib/argv_split.zig",
        "tools/lib/cmdline.zig",
        "tools/lib/ctype.zig",
        "tools/lib/hweight.zig",
        "tools/lib/list_sort.zig",
        "tools/lib/slab.zig",
        "tools/lib/str_error_r.zig",
        "tools/lib/vsprintf.zig",
        "tools/lib/zalloc.zig",
    ],
    "direct_anchor_followup_helpers": [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ],
    "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    "anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
}

EXPECTED_FIXTURE = {
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
        "strtobool_invalid": -22,
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
        "next_match_terminal_null": True,
    },
}

EXPECTED_FIXTURE_TOP_LEVEL_KEYS = [
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

REQUIRED_FILES = [
    *EXPECTED_HELPERS,
    "scripts/zigux/artifact_diff.py",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/fixtures/phase1_helpers.json",
]

DOC_MARKERS = {
    "docs_root_phase1_packet": [
        "Phase 1 notes\n- `Documentation/zigux/phase1-closure.md`\n- `scripts/zigux/README.md`\n- `scripts/zigux/install-zig.py`\n- `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root",
    ],
    "tests_root_phase1_packet": [
        "keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
    ],
    "review_checklist_phase1_packet": [
        "if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`",
        "`scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche",
    ],
}

PHASE1_IMPORT_MARKERS = [
    '@import("argv_split")',
    '@import("bitmap")',
    '@import("cmdline")',
    '@import("ctype")',
    '@import("find_bit")',
    '@import("hweight")',
    '@import("list_sort")',
    '@import("rbtree")',
    '@import("slab")',
    '@import("str_error_r")',
    '@import("string")',
    '@import("vsprintf")',
    '@import("zalloc")',
    '@embedFile("fixtures/phase1_helpers.json")',
]

PHASE1_REPLAY_MARKERS = [
    "fixture.find_bit.inclusive_boundary_next",
    "fixture.find_bit.inclusive_boundary_zero",
    "fixture.find_bit.inclusive_boundary_and",
    "fixture.find_bit.past_nbits_next",
    "fixture.find_bit.past_nbits_zero",
    "fixture.find_bit.past_nbits_and",
    "fixture.find_bit.tail_clamped_first",
    "fixture.find_bit.tail_clamped_next",
    "fixture.find_bit.tail_zero_clamped_first",
    "fixture.find_bit.tail_zero_clamped_next",
    "fixture.find_bit.tail_and_clamped_first",
    "fixture.find_bit.tail_and_clamped_next",
    "fixture.find_bit.tail_clamped_last",
    "fixture.find_bit.tail_clamped_empty_last",
    "fixture.bitmap.scnprintf",
    "fixture.bitmap.truncated_scnprintf_len",
    "fixture.bitmap.truncated_scnprintf",
    "fixture.bitmap.terminator_only_scnprintf_len",
    "fixture.bitmap.terminator_only_nul",
    "fixture.bitmap.zero_length_scnprintf_len",
    "fixture.bitmap.partial_xor_nbits",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.string.strtobool_y",
    "fixture.string.strtobool_on",
    "fixture.string.strtobool_zero",
    "fixture.string.strtobool_off",
    "fixture.string.strtobool_invalid",
    "fixture.string.strlcpy_len",
    "fixture.string.strlcpy_buffer",
    "fixture.string.skip_spaces",
    "fixture.string.trim_spaces",
    "fixture.string.remove_spaces",
    "fixture.string.replace_char",
    "fixture.string.replace_char_end",
    "fixture.string.replace_char_cstr_end",
    "fixture.string.replace_char_cstr_bytes",
    "fixture.string.memchr_inv_index",
    "fixture.string.memchr_inv_none",
    "fixture.rbtree.empty_root",
    "fixture.rbtree.insert_order",
    "fixture.rbtree.reverse_order",
    "fixture.rbtree.replace_order",
    "fixture.rbtree.erase_init_order",
    "fixture.rbtree.postorder_count",
    "fixture.rbtree.erase_init_node_empty",
    "fixture.rbtree.cleared_node_empty",
    "fixture.rbtree.find_found_key",
    "fixture.rbtree.find_missing",
    "fixture.rbtree.find_first_serial",
    "fixture.rbtree.next_match_serials",
    "fixture.rbtree.next_match_terminal_null",
]

HELPER_FOLLOWUP_TESTS = [
    'test "phase 1 helper ports match committed parity fixture"',
    'test "phase 1 string replaceChar stops at embedded NUL"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
]


def repo_root_from_arg(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path, label: str) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_required_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def extract_test_body(text: str, title: str) -> str | None:
    anchor = f'test "{title}"'
    start = text.find(anchor)
    if start == -1:
        return None
    next_start = text.find('\ntest "', start + len(anchor))
    return text[start:] if next_start == -1 else text[start:next_start]


def source_path_for_helper(helper: str) -> str:
    return helper


def review_anchor_tests(anchor_value: Any) -> list[str]:
    if isinstance(anchor_value, str):
        return [anchor_value] if anchor_value.startswith('test "') else []
    if isinstance(anchor_value, list):
        return [item for item in anchor_value if isinstance(item, str) and item.startswith('test "')]
    return []


def fixture_key_markers(anchor_value: Any) -> list[str]:
    if not isinstance(anchor_value, list):
        return []
    return [item for item in anchor_value if isinstance(item, str) and not item.startswith('test "')]


def collect_manifest_and_source_markers(root: Path, manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["phase1_manifest:json_object"]

    missing: list[str] = []
    if manifest.get("phase") != EXPECTED_MANIFEST["phase"]:
        missing.append("phase1_manifest:phase")
    if manifest.get("status") != EXPECTED_MANIFEST["status"]:
        missing.append("phase1_manifest:status")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        missing.append("phase1_manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        missing.append("phase1_manifest:helpers")
    if manifest.get("lane_sequencing") != EXPECTED_LANE_SEQUENCING:
        missing.append("phase1_manifest:lane_sequencing")

    review_anchors = manifest.get("review_anchors")
    if review_anchors != EXPECTED_MANIFEST["review_anchors"]:
        missing.append("phase1_manifest:review_anchors")
        if not isinstance(review_anchors, dict):
            return missing

    replay_text = load_text(root / "zigux/tests/phase1_helpers.zig")
    replay_body = extract_test_body(replay_text, "phase 1 helper ports match committed parity fixture")
    if replay_body is None:
        missing.append('phase1_parity_test:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0')
        replay_body = ""

    fixture = json.loads((root / "zigux/tests/fixtures/phase1_helpers.json").read_text(encoding="utf-8"))

    for helper, anchors in EXPECTED_MANIFEST["review_anchors"].items():
        source_text = load_text(root / source_path_for_helper(helper))
        for key, value in anchors.items():
            target_text = replay_text if key == "phase1_helper_replay_anchor" else source_text
            for marker in review_anchor_tests(value):
                count = target_text.count(marker)
                if count != 1:
                    missing.append(f"phase1_anchor:{helper}:{key}:{marker}:expected=1:actual={count}")

            if key in {"parity_fixture_keys", "tail_clamp_fixture_keys", "partial_xor_review_fields"}:
                section = helper.rsplit("/", 1)[-1].replace(".zig", "")
                section_data = fixture.get(section)
                if not isinstance(section_data, dict):
                    missing.append(f"phase1_fixture_section:{section}")
                    continue
                for field in fixture_key_markers(value):
                    if field not in replay_body:
                        missing.append(f"phase1_replay_field:{helper}:{field}")
                    if field not in section_data:
                        missing.append(f"phase1_fixture_field:{helper}:{field}")
    return missing


def collect_fixture_sanity(root: Path, fixture: object) -> list[str]:
    if not isinstance(fixture, dict):
        return ["phase1_fixture:json_object"]

    missing: list[str] = []
    if sorted(fixture.keys()) != sorted(EXPECTED_FIXTURE_TOP_LEVEL_KEYS):
        missing.append("phase1_fixture:top_level_keys")

    for section, expected in EXPECTED_FIXTURE.items():
        actual = fixture.get(section)
        if actual != expected:
            missing.append(f"phase1_fixture:{section}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    docs_readme = load_text(root / "Documentation/zigux/README.md")
    tests_readme = load_text(root / "zigux/tests/README.md")
    review_checklist = load_text(root / "Documentation/zigux/review-checklist.md")
    helpers_text = load_text(root / "zigux/tests/phase1_helpers.zig")

    manifest, manifest_errors = load_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", "phase1_manifest")
    fixture, fixture_errors = load_json(root / "zigux/tests/fixtures/phase1_helpers.json", "phase1_fixture")

    missing: list[str] = []
    missing.extend(manifest_errors)
    missing.extend(fixture_errors)
    missing.extend(collect_required_markers(docs_readme, "docs_root_phase1_packet", DOC_MARKERS["docs_root_phase1_packet"]))
    missing.extend(collect_required_markers(tests_readme, "tests_root_phase1_packet", DOC_MARKERS["tests_root_phase1_packet"]))
    missing.extend(
        collect_required_markers(
            review_checklist,
            "review_checklist_phase1_packet",
            DOC_MARKERS["review_checklist_phase1_packet"],
        )
    )
    missing.extend(collect_required_markers(helpers_text, "phase1_import_marker", PHASE1_IMPORT_MARKERS))
    missing.extend(collect_required_markers(helpers_text, "phase1_helper_test", HELPER_FOLLOWUP_TESTS))

    replay_body = extract_test_body(helpers_text, "phase 1 helper ports match committed parity fixture")
    if replay_body is None:
        missing.append('phase1_parity_test:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0')
    else:
        for marker in PHASE1_REPLAY_MARKERS:
            if marker not in replay_body:
                missing.append(f"phase1_replay_marker:{marker}")

    if manifest is not None:
        missing.extend(collect_manifest_and_source_markers(root, manifest))
    if fixture is not None:
        missing.extend(collect_fixture_sanity(root, fixture))
    return missing


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("\n", encoding="utf-8")

    (root / "Documentation/zigux/README.md").write_text(
        DOC_MARKERS["docs_root_phase1_packet"][0] + "\n" + DOC_MARKERS["docs_root_phase1_packet"][1] + "\n",
        encoding="utf-8",
    )
    (root / "zigux/tests/README.md").write_text(
        DOC_MARKERS["tests_root_phase1_packet"][0] + "\n",
        encoding="utf-8",
    )
    (root / "Documentation/zigux/review-checklist.md").write_text(
        DOC_MARKERS["review_checklist_phase1_packet"][0]
        + "\n"
        + DOC_MARKERS["review_checklist_phase1_packet"][1]
        + "\n",
        encoding="utf-8",
    )

    for helper in EXPECTED_HELPERS:
        anchors = EXPECTED_MANIFEST["review_anchors"].get(helper, {})
        test_lines: list[str] = []
        for value in anchors.values():
            test_lines.extend(review_anchor_tests(value))
        unique_test_lines = list(dict.fromkeys(test_lines))
        (root / helper).write_text("\n".join(unique_test_lines) + "\n", encoding="utf-8")

    replay_block = ['test "phase 1 helper ports match committed parity fixture"'] + PHASE1_REPLAY_MARKERS
    replace_char_block = ['test "phase 1 string replaceChar stops at embedded NUL"']
    trim_block = ['test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"']
    helpers_body = "\n".join(
        PHASE1_IMPORT_MARKERS
        + replay_block
        + replace_char_block
        + trim_block
    ) + "\n"
    (root / "zigux/tests/phase1_helpers.zig").write_text(helpers_body, encoding="utf-8")
    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(
        json.dumps(
            {
                **EXPECTED_MANIFEST,
                "lane_sequencing": EXPECTED_LANE_SEQUENCING,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    fixture = {
        **{key: {} for key in EXPECTED_FIXTURE_TOP_LEVEL_KEYS},
        **EXPECTED_FIXTURE,
    }
    (root / "zigux/tests/fixtures/phase1_helpers.json").write_text(
        json.dumps(fixture, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)

        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 2

        bitmap_path = root / "tools/lib/bitmap.zig"
        bitmap_text = load_text(bitmap_path)
        bitmap_path.write_text(
            bitmap_text.replace('test "bitmap range helpers clamp the final partial word"\n', "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert any(item.startswith("phase1_anchor:tools/lib/bitmap.zig:final_partial_word_anchor:") for item in missing)
        bitmap_path.write_text(bitmap_text, encoding="utf-8")
        case_count += 1

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("linux_alias_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "phase1_manifest:review_anchors" in missing
        manifest_path.write_text(
            json.dumps({**EXPECTED_MANIFEST, "lane_sequencing": EXPECTED_LANE_SEQUENCING}, indent=2) + "\n",
            encoding="utf-8",
        )
        case_count += 1

        fixture_path = root / "zigux/tests/fixtures/phase1_helpers.json"
        fixture = json.loads(load_text(fixture_path))
        fixture["bitmap"]["truncated_scnprintf_len"] = 11
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")) + "\n", encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "phase1_fixture:bitmap" in missing
        fixture_path.write_text(
            json.dumps({**{key: {} for key in EXPECTED_FIXTURE_TOP_LEVEL_KEYS}, **EXPECTED_FIXTURE}, separators=(",", ":"))
            + "\n",
            encoding="utf-8",
        )
        case_count += 1

        helpers_path = root / "zigux/tests/phase1_helpers.zig"
        helpers_text = load_text(helpers_path)
        helpers_path.write_text(helpers_text.replace("fixture.bitmap.zero_length_scnprintf_len\n", "", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert "phase1_replay_marker:fixture.bitmap.zero_length_scnprintf_len" in missing
        helpers_path.write_text(helpers_text, encoding="utf-8")
        case_count += 1

        tests_readme = root / "zigux/tests/README.md"
        tests_text = load_text(tests_readme)
        tests_readme.write_text(tests_text.replace("make -C zigux phase1-bench", "make -C zigux phase1-bork", 1), encoding="utf-8")
        missing = collect_missing_markers(root)
        assert any(item.startswith("tests_root_phase1_packet:") for item in missing)
        tests_readme.write_text(tests_text, encoding="utf-8")
        case_count += 1

        (root / "scripts/zigux/validate-phase1.py").unlink()
        assert collect_missing_files(root) == ["scripts/zigux/validate-phase1.py"]
        case_count += 1

    print("PHASE1_VALIDATION_SELF_TEST=pass")
    print(f"PHASE1_VALIDATION_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_VALIDATION=fail")
        print("MISSING_PHASE1_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_MARKERS_END")
        return 1

    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in DOC_MARKERS.values()) + len(PHASE1_IMPORT_MARKERS) + len(HELPER_FOLLOWUP_TESTS) + len(PHASE1_REPLAY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

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
  "lane_sequencing": {
    "shared_replay_parked_helpers": [
      "tools/lib/argv_split.zig",
      "tools/lib/cmdline.zig",
      "tools/lib/ctype.zig",
      "tools/lib/hweight.zig",
      "tools/lib/list_sort.zig",
      "tools/lib/slab.zig",
      "tools/lib/str_error_r.zig",
      "tools/lib/vsprintf.zig",
      "tools/lib/zalloc.zig"
    ],
    "direct_anchor_followup_helpers": [
      "tools/lib/bitmap.zig",
      "tools/lib/find_bit.zig",
      "tools/lib/rbtree.zig",
      "tools/lib/string.zig"
    ],
    "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    "anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys."
  }
}
"""
)

EXPECTED_FIXTURE = json.loads(
    r"""
{"find_bit":{"bits_per_long":64,"first":5,"next_after_6":67,"next_after_word":135,"first_zero":3,"next_zero":68,"first_and":9,"next_and":66,"last":135,"inclusive_boundary_next":63,"inclusive_boundary_zero":63,"inclusive_boundary_and":63,"past_nbits_next":7,"past_nbits_zero":7,"past_nbits_and":7,"tail_clamped_first":69,"tail_clamped_next":69,"tail_zero_clamped_first":69,"tail_zero_clamped_next":69,"tail_and_clamped_first":69,"tail_and_clamped_next":69,"tail_clamped_last":67,"tail_clamped_empty_last":69},"bitmap":{"weight":3,"scnprintf":"1-3,7,10-11","truncated_scnprintf_len":7,"truncated_scnprintf":"1-3,7,1","terminator_only_scnprintf_len":0,"terminator_only_nul":0,"zero_length_scnprintf_len":0,"alloc_words":2,"zalloc_words":2,"zalloc_values":[0,0],"and_result":true,"and_values":[10,0],"andnot_result":true,"andnot_values":[4,0],"or_values":[14,0],"xor_values":[4,0],"partial_xor_nbits":4,"partial_xor_masked_values":[14],"equal":true,"intersects":true,"subset":true,"range_after_set":[14,12,0],"range_after_clear":[0,0,0],"full_after_fill":true,"empty_after_zero":true},"string":{"strtobool_y":true,"strtobool_on":true,"strtobool_zero":false,"strtobool_off":false,"strtobool_invalid":-22,"strlcpy_len":5,"strlcpy_buffer":"hel","skip_spaces":"hello","trim_spaces":"hi","remove_spaces":"abc","replace_char":"a_b","replace_char_end":3,"replace_char_cstr_end":2,"replace_char_cstr_bytes":[97,95,0,45,122],"memchr_inv_index":4,"memchr_inv_none":true},"rbtree":{"empty_root":true,"insert_order":[5,10,15,20,25],"reverse_order":[25,20,15,10,5],"replace_order":[5,10,15,25],"erase_init_order":[5,15,25],"postorder_count":3,"erase_init_node_empty":true,"cleared_node_empty":true,"find_found_key":15,"find_missing":true,"find_first_serial":0,"next_match_serials":[0,2,4],"next_match_terminal_null":true},"argv_split":{"argc":3,"argv":["alpha","beta","gamma"],"blank_argc":0},"cmdline":{"decimal_k":{"value":65536,"rest":" rest"},"hex_m":{"value":33554432,"rest":""},"octal_k":{"value":8192,"rest":""},"invalid":{"value":0,"rest":"xyz"}},"ctype":{"mask_A":65,"mask_a":66,"mask_space":160,"isalnum_A":true,"isalpha_z":true,"isdigit_7":true,"isspace_tab":true,"isxdigit_f":true,"ispunct_bang":true,"tolower_A":97,"toupper_z":90,"isodigit_7":true,"isodigit_8":false},"hweight":{"w8":4,"w16":8,"w32":16,"w64":32,"wlong":8},"list_sort":{"tri_sorted_keys":[1,1,2,3,3],"tri_sorted_ordinals":[1,3,0,2,4],"bool_sorted_keys":[1,1,2,3,3],"bool_sorted_ordinals":[1,3,0,2,4]},"zalloc":{"zeroed":true,"freed_is_null":true,"value_zeroed":true,"value_freed_is_null":true},"str_error_r":{"enoent":"No such file or directory","unknown":"INTERNAL ERROR: strerror_r(4096, [buf], 64)=22"},"slab":{"null_without_reclaim":true,"alloc_count_after_kmalloc":1,"zero_after_kmalloc":true,"alloc_count_after_kmalloc_free":0,"array_zeroed":true,"alloc_count_after_kmalloc_array":1,"alloc_count_after_kmalloc_array_free":0,"slab_is_available":true},"vsprintf":{"scnprintf_text":"zigux:7","scnprintf_len":7,"pad_text":"id=7    ","pad_len":7}}
"""
)

EXPECTED_FIXTURE_TOP_LEVEL_KEYS = sorted(EXPECTED_FIXTURE.keys())
EXPECTED_HELPERS = EXPECTED_MANIFEST["helpers"]
DIRECT_ANCHOR_HELPERS = set(EXPECTED_MANIFEST["lane_sequencing"]["direct_anchor_followup_helpers"])
EXPECTED_BITMAP_PHASE1_HELPER_REPLAY_ANCHOR = 'test "phase 1 helper ports match committed parity fixture"'
EXPECTED_BITMAP_REVIEW_PACKET_SUMMARY = (
    "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, tiny-buffer, and partial-window xor replay, "
    "while helper-local anchors keep zero-size allocator and free-null behavior, predicate tail-mask, first-word boundary, final-partial range boundary, fill tail-clamp, "
    "cross-word scnprintf collapse, truncation, empty-bitmap caller-buffer preservation, copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, "
    "zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master"
)
EXPECTED_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_ANCHOR = 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"'
EXPECTED_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_CONTRACT = (
    "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail."
)
EXPECTED_FIND_BIT_REVIEW_PACKET_SUMMARY = (
    "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, underscore-alias, and Linux-style alias behavior review-visible on current master"
)
EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY = (
    "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root leftmost-return, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root leftmost-return fixture keys"
)
EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, the smallest shared-replay expansion is a dedicated iterator or cached-root leftmost-return fixture key; until then, matchIterator coverage plus cached-root leftmost-return and singleton-erase behavior stay owned by direct helper-local anchors."
)
EXPECTED_STRING_PREFIX_SUFFIX_REVIEW_SUMMARY = (
    "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields, "
    "so strHasPrefix and strstarts plus strEndsWith and str_ends_with remain review-visible at the helper surface"
)
EXPECTED_STRING_MEMPARSE_REVIEW_SUMMARY = (
    "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation"
)
EXPECTED_STRING_SHARED_REPLACE_CHAR_CSTR_REVIEW_SUMMARY = (
    "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership"
)
EXPECTED_RBTREE_BENCH_ITERATIONS = 4000
EXPECTED_RBTREE_BENCH_EXACT_CHECKSUM = 3380000
EXPECTED_FIND_BIT_EDGE_BENCH_ITERATIONS = 20000
EXPECTED_FIND_BIT_EDGE_BENCH_EXACT_CHECKSUM = 37500000

REQUIRED_FILES = [
    *EXPECTED_HELPERS,
    "scripts/zigux/artifact_diff.py",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-installer-companion-checks.py",
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
        "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `scripts/zigux/install-zig.py` - `scripts/zigux/check-phase1-installer-review-surfaces.py` - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, the dedicated installer-review alignment checker, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
    ],
    "tests_root_phase1_packet": [
        "keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
    ],
    "review_checklist_phase1_packet": [
        "if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`, `python3 scripts/zigux/check-phase1-installer-review-surfaces.py`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test`, `python3 scripts/zigux/check-phase1-installer-companion-checks.py`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
    ],
}

PHASE1_SHARED_REPLAY_PARKED_HELPERS = ",".join(
    EXPECTED_MANIFEST["lane_sequencing"]["shared_replay_parked_helpers"]
)
PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS = ",".join(
    EXPECTED_MANIFEST["lane_sequencing"]["direct_anchor_followup_helpers"]
)
PHASE1_LANE_NOTE_MARKERS = [
    "Fresh repo-first inspection shows that the honest current owner map is the shared Phase 1 helper manifest plus the live helper-local anchors, not an older bitmap-only reopen guide.",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json` is the authoritative owner-map split for all thirteen closed Phase 1 helpers",
    f"- `PHASE1_SHARED_REPLAY_PARKED_HELPERS={PHASE1_SHARED_REPLAY_PARKED_HELPERS}`",
    f"- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS={PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS}`",
    f"- `PHASE1_LANE_RULE_SUMMARY={EXPECTED_MANIFEST['lane_sequencing']['rule_summary']}`",
    f"- `PHASE1_LANE_ANTI_OVERLAP_RULE={EXPECTED_MANIFEST['lane_sequencing']['anti_overlap_rule']}`",
]

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

HELPER_FOLLOWUP_TESTS = [
    'test "phase 1 helper ports match committed parity fixture"',
    'test "phase 1 string replaceChar stops at embedded NUL"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
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
    "fixture.bitmap.alloc_words",
    "fixture.bitmap.zalloc_words",
    "fixture.bitmap.zalloc_values",
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


def repo_root(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path, label: str) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(load_text(path)), []
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


def extract_test_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('test "'):
            continue
        closing_quote = stripped.find('"', len('test "'))
        if closing_quote == -1:
            continue
        titles.append(stripped[: closing_quote + 1])
    return titles


def extract_test_body(text: str, title: str) -> str | None:
    anchor = f'test "{title}"'
    start = text.find(anchor)
    if start == -1:
        return None
    next_start = text.find('\ntest "', start + len(anchor))
    return text[start:] if next_start == -1 else text[start:next_start]


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


def source_path_for_helper(helper: str) -> str:
    return helper


def collect_manifest_and_source_markers(root: Path, manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["phase1_manifest:json_object"]

    missing: list[str] = []
    for key in ("phase", "status", "helper_count", "helpers", "lane_sequencing"):
        if manifest.get(key) != EXPECTED_MANIFEST[key]:
            missing.append(f"phase1_manifest:{key}")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return [*missing, "phase1_manifest:review_anchors"]

    bitmap_review_anchors = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review_anchors, dict):
        missing.append("phase1_manifest_review_anchor:shape=tools/lib/bitmap.zig")
        bitmap_review_anchors = {}
    if bitmap_review_anchors.get("phase1_helper_replay_anchor") != EXPECTED_BITMAP_PHASE1_HELPER_REPLAY_ANCHOR:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:phase1_helper_replay_anchor")
    if bitmap_review_anchors.get("review_packet_summary") != EXPECTED_BITMAP_REVIEW_PACKET_SUMMARY:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:review_packet_summary")

    find_bit_review_anchors = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(find_bit_review_anchors, dict):
        missing.append("phase1_manifest_review_anchor:shape=tools/lib/find_bit.zig")
        find_bit_review_anchors = {}
    if find_bit_review_anchors.get("tail_word_inclusive_boundary_anchor") != EXPECTED_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_ANCHOR:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/find_bit.zig:tail_word_inclusive_boundary_anchor")
    if find_bit_review_anchors.get("tail_word_inclusive_boundary_contract") != EXPECTED_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_CONTRACT:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/find_bit.zig:tail_word_inclusive_boundary_contract")
    if find_bit_review_anchors.get("review_packet_summary") != EXPECTED_FIND_BIT_REVIEW_PACKET_SUMMARY:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/find_bit.zig:review_packet_summary")

    rbtree_review_anchors = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree_review_anchors, dict):
        missing.append("phase1_manifest_review_anchor:shape=tools/lib/rbtree.zig")
        rbtree_review_anchors = {}
    if rbtree_review_anchors.get("review_packet_summary") != EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/rbtree.zig:review_packet_summary")
    if rbtree_review_anchors.get("next_safe_step_note") != EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/rbtree.zig:next_safe_step_note")

    string_review_anchors = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_review_anchors, dict):
        missing.append("phase1_manifest_review_anchor:shape=tools/lib/string.zig")
        string_review_anchors = {}
    if string_review_anchors.get("prefix_suffix_review_summary") != EXPECTED_STRING_PREFIX_SUFFIX_REVIEW_SUMMARY:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/string.zig:prefix_suffix_review_summary")
    if string_review_anchors.get("memparse_review_summary") != EXPECTED_STRING_MEMPARSE_REVIEW_SUMMARY:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/string.zig:memparse_review_summary")
    if string_review_anchors.get("shared_replace_char_cstr_review_summary") != EXPECTED_STRING_SHARED_REPLACE_CHAR_CSTR_REVIEW_SUMMARY:
        missing.append("phase1_manifest_review_anchor:value=tools/lib/string.zig:shared_replace_char_cstr_review_summary")

    replay_text = load_text(root / "zigux/tests/phase1_helpers.zig")
    fixture = EXPECTED_FIXTURE
    replay_body = extract_test_body(replay_text, "phase 1 helper ports match committed parity fixture")
    if replay_body is None:
        missing.append('phase1_parity_test:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0')
        replay_body = ""

    for helper, anchors in review_anchors.items():
        if not isinstance(anchors, dict):
            missing.append(f"phase1_manifest:{helper}:review_anchor_shape")
            continue
        source_text = load_text(root / source_path_for_helper(helper))
        helper_test_anchors = anchors.get("helper_test_anchors")
        if helper in DIRECT_ANCHOR_HELPERS:
            if not isinstance(helper_test_anchors, list) or not all(isinstance(item, str) for item in helper_test_anchors):
                missing.append(f"phase1_manifest:{helper}:helper_test_anchors")
            elif helper_test_anchors != extract_test_titles(source_text):
                missing.append(f"phase1_helper_test_anchor_list:{helper}")
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


def collect_fixture_sanity(fixture: object) -> list[str]:
    if not isinstance(fixture, dict):
        return ["phase1_fixture:json_object"]
    missing: list[str] = []
    if sorted(fixture.keys()) != EXPECTED_FIXTURE_TOP_LEVEL_KEYS:
        missing.append("phase1_fixture:top_level_keys")
    for section, expected in EXPECTED_FIXTURE.items():
        if fixture.get(section) != expected:
            missing.append(f"phase1_fixture:{section}")
    return missing


def collect_bench_expectation_markers(expectations: object) -> list[str]:
    if not isinstance(expectations, dict):
        return ["phase1_bench_expectations:json_object"]

    missing: list[str] = []
    if expectations.get("status") != "pass":
        missing.append("phase1_bench_expectations:status")

    iterations = expectations.get("iterations")
    if not isinstance(iterations, dict):
        missing.append("phase1_bench_expectations:iterations")
    else:
        if iterations.get("PHASE1_BENCH_RBTREE_ITERATIONS") != EXPECTED_RBTREE_BENCH_ITERATIONS:
            missing.append(
                f"phase1_bench_expectations:rbtree_iterations={EXPECTED_RBTREE_BENCH_ITERATIONS}"
            )
        if iterations.get("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS") != EXPECTED_FIND_BIT_EDGE_BENCH_ITERATIONS:
            missing.append(
                f"phase1_bench_expectations:find_bit_edge_iterations={EXPECTED_FIND_BIT_EDGE_BENCH_ITERATIONS}"
            )

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        missing.append("phase1_bench_expectations:checksums")
    else:
        if "PHASE1_BENCH_RBTREE_CHECKSUM" not in checksums:
            missing.append("phase1_bench_expectations:rbtree_checksum_listed")
        if "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM" not in checksums:
            missing.append("phase1_bench_expectations:find_bit_edge_checksum_listed")

    exact_checksums = expectations.get("exact_checksums")
    if not isinstance(exact_checksums, dict):
        missing.append("phase1_bench_expectations:exact_checksums")
    else:
        if exact_checksums.get("PHASE1_BENCH_RBTREE_CHECKSUM") != EXPECTED_RBTREE_BENCH_EXACT_CHECKSUM:
            missing.append(
                f"phase1_bench_expectations:rbtree_exact_checksum={EXPECTED_RBTREE_BENCH_EXACT_CHECKSUM}"
            )
        if exact_checksums.get("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM") != EXPECTED_FIND_BIT_EDGE_BENCH_EXACT_CHECKSUM:
            missing.append(
                f"phase1_bench_expectations:find_bit_edge_exact_checksum={EXPECTED_FIND_BIT_EDGE_BENCH_EXACT_CHECKSUM}"
            )

    return missing


def collect_missing_markers(root: Path) -> list[str]:
    docs_readme = load_text(root / "Documentation/zigux/README.md")
    tests_readme = load_text(root / "zigux/tests/README.md")
    review_checklist = load_text(root / "Documentation/zigux/review-checklist.md")
    lane_note = load_text(root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md")
    helpers_text = load_text(root / "zigux/tests/phase1_helpers.zig")
    manifest, manifest_errors = load_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", "phase1_manifest")
    fixture, fixture_errors = load_json(root / "zigux/tests/fixtures/phase1_helpers.json", "phase1_fixture")
    bench_expectations, bench_expectation_errors = load_json(
        root / "zigux/tests/fixtures/phase1_bench_expectations.json",
        "phase1_bench_expectations",
    )

    missing: list[str] = []
    missing.extend(manifest_errors)
    missing.extend(fixture_errors)
    missing.extend(bench_expectation_errors)
    missing.extend(collect_required_markers(docs_readme, "docs_root_phase1_packet", DOC_MARKERS["docs_root_phase1_packet"]))
    missing.extend(collect_required_markers(tests_readme, "tests_root_phase1_packet", DOC_MARKERS["tests_root_phase1_packet"]))
    missing.extend(collect_required_markers(review_checklist, "review_checklist_phase1_packet", DOC_MARKERS["review_checklist_phase1_packet"]))
    missing.extend(collect_required_markers(lane_note, "phase1_lane_note", PHASE1_LANE_NOTE_MARKERS))
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
        missing.extend(collect_fixture_sanity(fixture))
    if bench_expectations is not None:
        missing.extend(collect_bench_expectation_markers(bench_expectations))
    return missing


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n" if path.suffix == ".json" else "\n", encoding="utf-8")

    (root / "Documentation/zigux/README.md").write_text("\n".join(DOC_MARKERS["docs_root_phase1_packet"]) + "\n", encoding="utf-8")
    (root / "zigux/tests/README.md").writeText = None
    (root / "zigux/tests/README.md").write_text(DOC_MARKERS["tests_root_phase1_packet"][0] + "\n", encoding="utf-8")
    (root / "Documentation/zigux/review-checklist.md").write_text("\n".join(DOC_MARKERS["review_checklist_phase1_packet"]) + "\n", encoding="utf-8")
    (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").write_text("\n".join(PHASE1_LANE_NOTE_MARKERS) + "\n", encoding="utf-8")

    manifest = {
        **EXPECTED_MANIFEST,
        "review_anchors": {
            helper: {"helper_test_anchors": [f'test "{helper}"']}
            for helper in EXPECTED_HELPERS
        },
    }
    manifest["review_anchors"]["tools/lib/find_bit.zig"] = {
        "helper_test_anchors": [
            'test "single-word next scans honor start masks"',
            EXPECTED_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_ANCHOR,
        ],
        "tail_word_inclusive_boundary_anchor": EXPECTED_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_ANCHOR,
        "tail_word_inclusive_boundary_contract": EXPECTED_FIND_BIT_TAIL_WORD_INCLUSIVE_BOUNDARY_CONTRACT,
        "tail_clamp_fixture_keys": ["tail_clamped_first"],
        "review_packet_summary": EXPECTED_FIND_BIT_REVIEW_PACKET_SUMMARY,
    }
    manifest["review_anchors"]["tools/lib/bitmap.zig"] = {
        "helper_test_anchors": ['test "bitmap range helpers honor exact first-word boundaries"'],
        "partial_xor_review_fields": ["partial_xor_nbits"],
        "phase1_helper_replay_anchor": EXPECTED_BITMAP_PHASE1_HELPER_REPLAY_ANCHOR,
        "review_packet_summary": EXPECTED_BITMAP_REVIEW_PACKET_SUMMARY,
    }
    manifest["review_anchors"]["tools/lib/string.zig"] = {
        "helper_test_anchors": ['test "strtobool accepts common Linux forms"'],
        "parity_fixture_keys": ["strtobool_invalid"],
        "prefix_suffix_review_summary": EXPECTED_STRING_PREFIX_SUFFIX_REVIEW_SUMMARY,
        "memparse_review_summary": EXPECTED_STRING_MEMPARSE_REVIEW_SUMMARY,
        "shared_replace_char_cstr_review_summary": EXPECTED_STRING_SHARED_REPLACE_CHAR_CSTR_REVIEW_SUMMARY,
    }
    manifest["review_anchors"]["tools/lib/rbtree.zig"] = {
        "helper_test_anchors": ['test "rbtree inserts and traverses in sorted order"'],
        "parity_fixture_keys": ["find_found_key"],
        "review_packet_summary": EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY,
        "next_safe_step_note": EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE,
    }

    for helper, anchors in manifest["review_anchors"].items():
        lines: list[str] = []
        for key, value in anchors.items():
            if key == "phase1_helper_replay_anchor":
                continue
            lines.extend(review_anchor_tests(value))
        (root / helper).write_text("\n".join(dict.fromkeys(lines)) + "\n", encoding="utf-8")

    helpers_body = "\n".join(
        PHASE1_IMPORT_MARKERS
        + ['test "phase 1 helper ports match committed parity fixture"']
        + PHASE1_REPLAY_MARKERS
        + [
            'test "phase 1 string replaceChar stops at embedded NUL"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ]
    ) + "\n"
    (root / "zigux/tests/phase1_helpers.zig").write_text(helpers_body, encoding="utf-8")
    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / "zigux/tests/fixtures/phase1_helpers.json").write_text(json.dumps(EXPECTED_FIXTURE, separators=(",", ":")) + "\n", encoding="utf-8")
    (root / "zigux/tests/fixtures/phase1_bench_expectations.json").write_text(
        json.dumps(
            {
                "status": "pass",
                "iterations": {
                    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": EXPECTED_FIND_BIT_EDGE_BENCH_ITERATIONS,
                    "PHASE1_BENCH_RBTREE_ITERATIONS": EXPECTED_RBTREE_BENCH_ITERATIONS,
                },
                "checksums": [
                    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
                    "PHASE1_BENCH_RBTREE_CHECKSUM",
                ],
                "exact_checksums": {
                    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": EXPECTED_FIND_BIT_EDGE_BENCH_EXACT_CHECKSUM,
                    "PHASE1_BENCH_RBTREE_CHECKSUM": EXPECTED_RBTREE_BENCH_EXACT_CHECKSUM,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_validator_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 2

        readme = root / "Documentation/zigux/README.md"
        original = load_text(readme)
        readme.write_text(original.replace("validator-first contract explicit from the docs root", "validator-first contract explicit from docs"), encoding="utf-8")
        assert any(item.startswith("docs_root_phase1_packet:") for item in collect_missing_markers(root))
        readme.write_text(original, encoding="utf-8")
        case_count += 1

        helpers = root / "zigux/tests/phase1_helpers.zig"
        original = load_text(helpers)
        helpers.write_text(original.replace("fixture.string.strtobool_invalid\n", "", 1), encoding="utf-8")
        assert "phase1_replay_marker:fixture.string.strtobool_invalid" in collect_missing_markers(root)
        helpers.write_text(original, encoding="utf-8")
        case_count += 1

        lane_note_path = root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md"
        lane_note_path.unlink()
        assert collect_missing_files(root) == ["Documentation/zigux/phase1-host-helper-lane-sequencing.md"]
        case_count += 1
        make_fixture_root(root)

        lane_note_path.write_text(
            load_text(lane_note_path).replace(PHASE1_LANE_NOTE_MARKERS[2] + "\n", "", 1),
            encoding="utf-8",
        )
        assert (
            f"phase1_lane_note:{PHASE1_LANE_NOTE_MARKERS[2]}:expected=1:actual=0"
            in collect_missing_markers(root)
        )
        case_count += 1
        make_fixture_root(root)

        fixture_path = root / "zigux/tests/fixtures/phase1_helpers.json"
        fixture = json.loads(load_text(fixture_path))
        fixture["string"]["strtobool_invalid"] = -1
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")) + "\n", encoding="utf-8")
        assert "phase1_fixture:string" in collect_missing_markers(root)
        fixture_path.write_text(json.dumps(EXPECTED_FIXTURE, separators=(",", ":")) + "\n", encoding="utf-8")
        case_count += 1

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(load_text(manifest_path))
        manifest["lane_sequencing"]["rule_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest:lane_sequencing" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("phase1_helper_replay_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:phase1_helper_replay_anchor" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["review_packet_summary"] = "stale bitmap summary"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:review_packet_summary" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        bitmap_path = root / "tools/lib/bitmap.zig"
        bitmap_path.write_text(load_text(bitmap_path) + 'test "bitmap drift"\n', encoding="utf-8")
        assert "phase1_helper_test_anchor_list:tools/lib/bitmap.zig" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/find_bit.zig"].pop("tail_word_inclusive_boundary_anchor")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/find_bit.zig:tail_word_inclusive_boundary_anchor" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_word_inclusive_boundary_contract"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/find_bit.zig:tail_word_inclusive_boundary_contract" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["review_packet_summary"] = "stale find_bit summary"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/find_bit.zig:review_packet_summary" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["review_packet_summary"] = "stale rbtree summary"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/rbtree.zig:review_packet_summary" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["next_safe_step_note"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/rbtree.zig:next_safe_step_note" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/string.zig"]["prefix_suffix_review_summary"] = "stale prefix summary"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/string.zig:prefix_suffix_review_summary" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/string.zig"]["memparse_review_summary"] = "stale memparse summary"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/string.zig:memparse_review_summary" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/string.zig"]["shared_replace_char_cstr_review_summary"] = "stale shared replace summary"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/string.zig:shared_replace_char_cstr_review_summary" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        bench_path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(load_text(bench_path))
        bench["exact_checksums"].pop("PHASE1_BENCH_RBTREE_CHECKSUM")
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "phase1_bench_expectations:rbtree_exact_checksum=3380000" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        bench = json.loads(load_text(bench_path))
        bench["exact_checksums"].pop("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM")
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "phase1_bench_expectations:find_bit_edge_exact_checksum=37500000" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        bench = json.loads(load_text(bench_path))
        bench["iterations"]["PHASE1_BENCH_RBTREE_ITERATIONS"] = 1
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "phase1_bench_expectations:rbtree_iterations=4000" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        bench = json.loads(load_text(bench_path))
        bench["iterations"]["PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS"] = 1
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "phase1_bench_expectations:find_bit_edge_iterations=20000" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        bench = json.loads(load_text(bench_path))
        bench["checksums"] = [
            item for item in bench["checksums"] if item != "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM"
        ]
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "phase1_bench_expectations:find_bit_edge_checksum_listed" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

    print("PHASE1_VALIDATION_SELF_TEST=pass")
    print(f"PHASE1_VALIDATION_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
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
        f'{sum(len(v) for v in DOC_MARKERS.values()) + len(PHASE1_LANE_NOTE_MARKERS) + len(PHASE1_IMPORT_MARKERS) + len(HELPER_FOLLOWUP_TESTS) + len(PHASE1_REPLAY_MARKERS) + 7}'
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
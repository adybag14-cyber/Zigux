#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

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
    "rule_summary": (
        "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
        "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
        "follow-up anchors on current master."
    ),
    "anti_overlap_rule": (
        "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
        "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
        "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
    ),
}

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/validate-phase1.py",
    "zigux/tests/README.md",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
]

DOC_MARKERS = {
    "docs_root_phase1_packet": [
        "Phase 1 notes - `Documentation/zigux/phase1-closure.md` - `scripts/zigux/README.md` - `scripts/zigux/install-zig.py` - `scripts/zigux/check-phase1-installer-review-surfaces.py` - `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "- `scripts/zigux/check-phase1-direct-owner-markers.py` also remains part of the live Phase 1 reminder packet beside `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of leaving the helper-family owner map implicit from the lane note alone.",
    ],
    "tests_root_phase1_packet": [
        "* current Phase 1 review-and-replay stack: `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`",
        "* current public-tree-backed Phase 1 parity packet: `zigux/tests/fixtures/phase1_helpers.json` and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    ],
    "review_checklist_phase1_packet": [
        "* if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`",
        "* if the change touches that same Phase 1 companion packet, does the checklist still say clearly that `python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test` replays the bounded checker logic while `python3 scripts/zigux/check-phase1-installer-companion-checks.py` guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line that `scripts/zigux/validate-phase1.py` enforces?",
    ],
}

REQUIRED_IMPORT_MARKERS = [
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

REQUIRED_REPLAY_MARKERS = [
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
    "fixture.bitmap.weight",
    "fixture.bitmap.scnprintf",
    "fixture.bitmap.truncated_scnprintf_len",
    "fixture.bitmap.truncated_scnprintf",
    "fixture.bitmap.terminator_only_scnprintf_len",
    "fixture.bitmap.terminator_only_nul",
    "fixture.bitmap.zero_length_scnprintf_len",
    "fixture.bitmap.alloc_words",
    "fixture.bitmap.zalloc_words",
    "fixture.bitmap.zalloc_values",
    "fixture.bitmap.and_result",
    "fixture.bitmap.and_values",
    "fixture.bitmap.andnot_result",
    "fixture.bitmap.andnot_values",
    "fixture.bitmap.or_values",
    "fixture.bitmap.xor_values",
    "fixture.bitmap.partial_xor_nbits",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.bitmap.equal",
    "fixture.bitmap.intersects",
    "fixture.bitmap.subset",
    "fixture.bitmap.range_after_set",
    "fixture.bitmap.range_after_clear",
    "fixture.bitmap.full_after_fill",
    "fixture.bitmap.empty_after_zero",
    "fixture.string.strtobool_invalid",
    "fixture.string.replace_char_cstr_bytes",
    "fixture.rbtree.find_first_serial",
    "fixture.rbtree.next_match_serials",
    "fixture.rbtree.match_iterator_serials",
    "fixture.rbtree.next_match_terminal_null",
]

EXPECTED_FIXTURE_SUBSETS = {
    "find_bit": {
        "bits_per_long": 64,
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
        "alloc_words": 2,
        "zalloc_words": 2,
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
        "scnprintf": "1-3,7,10-11",
        "truncated_scnprintf_len": 7,
        "truncated_scnprintf": "1-3,7,1",
        "terminator_only_scnprintf_len": 0,
        "terminator_only_nul": 0,
        "zero_length_scnprintf_len": 0,
        "zalloc_values": [0, 0],
    },
    "string": {
        "strtobool_invalid": -22,
        "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
    },
    "rbtree": {
        "find_first_serial": 0,
        "next_match_serials": [0, 2, 4],
        "match_iterator_serials": [0, 2, 4],
        "cached_leftmost_return_serials": [0, -1, 2, -1],
        "next_match_terminal_null": True,
    },
}

REQUIRED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "required_values": {
            "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
            "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
            "fill_tail_clamp_anchor": 'test "bitmap fill clamps tail bits in partial words"',
            "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
            "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
            "scnprintf_cross_word_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
            "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
            "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
            "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
            "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
            "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
        },
        "required_list_members": {
            "helper_test_anchors": [
                'test "bitmap weight and clamps tail bits and aliases mirror the primary helper"',
                'test "bitmap weight and keeps zero-bit windows empty"',
                'test "bitmap Linux-style aliases keep zero-bit windows explicit no-ops"',
            ],
            "copy_zero_and_aligned_anchors": [
                'test "bitmap copy and extend handles zero and aligned counts"',
                'test "bitmap copy helpers keep zero-sized destination views untouched"',
            ],
            "parity_fixture_keys": [
                "alloc_words",
                "zalloc_words",
                "zalloc_values",
                "scnprintf",
                "truncated_scnprintf_len",
                "truncated_scnprintf",
                "terminator_only_scnprintf_len",
                "terminator_only_nul",
                "zero_length_scnprintf_len",
            ],
            "partial_xor_review_fields": [
                "partial_xor_nbits",
                "partial_xor_masked_values",
            ],
        },
        "required_substrings": {
            "review_packet_summary": [
                "shared Phase 1 fixture keys now own bitmap allocator sizing",
                "Linux-style alias behavior review-visible on current master",
            ],
            "next_safe_step_note": [
                "keep bitmap parked unless",
                "do not reopen",
            ],
        },
        "source_markers": [
            'test "bitmap range helpers honor exact first-word boundaries"',
            'test "bitmap range helpers clamp the final partial word"',
            'test "bitmap fill clamps tail bits in partial words"',
            'test "bitmap predicates ignore out-of-range tail bits"',
            'test "bitmap weight and clamps tail bits and aliases mirror the primary helper"',
            'test "bitmap weight and keeps zero-bit windows empty"',
            'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap copy helpers keep zero-sized destination views untouched"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
            'test "bitmap zero-bit binary helpers stay explicit identity operations"',
            'test "bitmap Linux-style aliases keep zero-bit windows explicit no-ops"',
            'test "bitmap Linux-style aliases mirror the primary helper surface"',
        ],
    },
    "tools/lib/find_bit.zig": {
        "required_values": {
            "same_word_start_masks": 'test "single-word next scans honor start masks"',
            "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
            "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
            "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
            "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
            "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers"',
            "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
            "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
        },
        "required_list_members": {
            "helper_test_anchors": [
                'test "find or bit returns the next set bit from either bitmap"',
                'test "clump8 scans mask out-of-range bits from partial final bytes"',
            ],
            "tail_clamp_fixture_keys": [
                "tail_clamped_first",
                "tail_clamped_next",
                "tail_zero_clamped_first",
                "tail_zero_clamped_next",
                "tail_and_clamped_first",
                "tail_and_clamped_next",
                "tail_clamped_last",
                "tail_clamped_empty_last",
            ],
        },
        "required_substrings": {
            "tail_word_inclusive_boundary_contract": [
                "tail-clamped set, zero, and shared-bit scans aligned",
                "return nbits instead of leaking the out-of-range tail",
            ],
            "review_packet_summary": [
                "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay",
                "Linux-style alias behavior review-visible on current master",
            ],
            "next_safe_step_note": [
                "keep find_bit parked unless",
                "do not reopen older saved validator cues",
            ],
        },
        "source_markers": [
            'test "find or bit returns the next set bit from either bitmap"',
            'test "single-word next scans honor start masks"',
            'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "zero-bit windows return without reading bitmap words"',
            'test "zero-sized scans ignore populated backing words"',
            'test "next scans past nbits return without reading bitmap words"',
            'test "tail-word next set scans skip earlier in-range matches before clamping"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "clump8 scans mask out-of-range bits from partial final bytes"',
            'test "low-level underscore aliases mirror the primary find helpers"',
            'test "Linux-style aliases mirror the primary find helpers"',
        ],
    },
    "tools/lib/rbtree.zig": {
        "required_values": {},
        "required_list_members": {
            "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
            "duplicate_search_anchors": [
                'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
                'test "rbtree nextMatch walks the duplicate range in order"',
                'test "rbtree matchIterator walks the duplicate range in order"',
            ],
            "cached_root_followup_anchors": [
                'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
                'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
                'test "rbtree cached root keeps the leftmost pointer in sync"',
                'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
                'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
                'test "rbtree eraseCached returns null for a singleton cached tree"',
                'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
                'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
            ],
        },
        "required_substrings": {
            "review_packet_summary": [
                "cached_leftmost_return_serials",
                "cached-root leftmost-return, insert-miss, leftmost-sync",
            ],
            "next_safe_step_note": [
                "shared-replay promotion",
                "cached_leftmost_return_serials",
            ],
        },
    },
    "tools/lib/string.zig": {
        "required_values": {},
        "required_list_members": {
            "parity_fixture_keys": [
                "strtobool_invalid",
                "replace_char_cstr_bytes",
            ],
        },
        "required_substrings": {
            "prefix_suffix_review_summary": [
                "prefix and suffix boundary anchors stay explicit",
                "strHasPrefix",
                "strEndsWith",
            ],
            "memparse_review_summary": [
                "memparse safety anchors stay explicit",
                "suffixes are still consumed after saturation",
            ],
            "shared_replace_char_cstr_review_summary": [
                "shared Phase 1 string replay now exercises strtobool",
                "embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit",
            ],
        },
    },
}


def repo_root(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path, label: str) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(load_text(path)), []
    except json.JSONDecodeError as exc:
        return None, [f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]


def collect_required_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        actual = text.count(marker)
        if actual != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={actual}")
    return missing


def extract_test_body(text: str, test_name: str) -> str | None:
    needle = f'test "{test_name}"'
    start = text.find(needle)
    if start == -1:
        return None

    brace_start = text.find("{", start)
    if brace_start == -1:
        return None

    depth = 0
    for idx in range(brace_start, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1 : idx]
    return None


def compare_subset(actual: Any, expected: Any, prefix: str) -> list[str]:
    missing: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [prefix]
        for key, value in expected.items():
            if key not in actual:
                missing.append(f"{prefix}.{key}")
                continue
            missing.extend(compare_subset(actual[key], value, f"{prefix}.{key}"))
        return missing
    if actual != expected:
        return [prefix]
    return []


def collect_manifest_markers(root: Path, manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return ["phase1_manifest:json_object"]

    missing: list[str] = []
    if manifest.get("phase") != "Phase 1":
        missing.append("phase1_manifest:phase")
    if manifest.get("status") != "closed":
        missing.append("phase1_manifest:status")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        missing.append("phase1_manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        missing.append("phase1_manifest:helpers")
    if manifest.get("lane_sequencing") != EXPECTED_LANE_SEQUENCING:
        missing.append("phase1_manifest:lane_sequencing")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return missing + ["phase1_manifest:review_anchors"]

    for helper, expectations in REQUIRED_REVIEW_ANCHORS.items():
        helper_review = review_anchors.get(helper)
        if not isinstance(helper_review, dict):
            missing.append(f"phase1_manifest:review_anchor={helper}")
            continue

        for key, expected_value in expectations["required_values"].items():
            actual_value = helper_review.get(key)
            if actual_value != expected_value:
                missing.append(f"phase1_manifest_review_anchor:value={helper}:{key}")

        for key, expected_members in expectations["required_list_members"].items():
            actual_values = helper_review.get(key)
            if not isinstance(actual_values, list):
                missing.append(f"phase1_manifest_review_anchor:value={helper}:{key}")
                continue
            actual_set = set(actual_values)
            if not set(expected_members).issubset(actual_set):
                missing.append(f"phase1_manifest_review_anchor:value={helper}:{key}")

        for key, required_substrings in expectations["required_substrings"].items():
            actual_value = helper_review.get(key)
            if not isinstance(actual_value, str):
                missing.append(f"phase1_manifest_review_anchor:value={helper}:{key}")
                continue
            if not all(fragment in actual_value for fragment in required_substrings):
                missing.append(f"phase1_manifest_review_anchor:value={helper}:{key}")

        source_markers = expectations.get("source_markers", [])
        if source_markers:
            source_text = load_text(root / helper)
            for marker in source_markers:
                if marker not in source_text:
                    missing.append(f"phase1_helper_anchor:{helper}:{marker}")

    return missing


def collect_fixture_markers(fixture: Any) -> list[str]:
    missing: list[str] = []
    for helper, expected_subset in EXPECTED_FIXTURE_SUBSETS.items():
        if not isinstance(fixture, dict) or helper not in fixture:
            missing.append(f"phase1_fixture:{helper}")
            continue
        for item in compare_subset(fixture[helper], expected_subset, f"phase1_fixture:{helper}"):
            missing.append(item)
    return missing


def collect_phase1_helpers_markers(text: str) -> list[str]:
    missing = collect_required_markers(text, "phase1_import_marker", REQUIRED_IMPORT_MARKERS)
    replay_body = extract_test_body(text, "phase 1 helper ports match committed parity fixture")
    if replay_body is None:
        missing.append('phase1_parity_test:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0')
        return missing

    for marker in REQUIRED_REPLAY_MARKERS:
        if marker not in replay_body:
            missing.append(f"phase1_replay_marker:{marker}")
    return missing


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    docs_root = load_text(root / "Documentation/zigux/README.md")
    review_checklist = load_text(root / "Documentation/zigux/review-checklist.md")
    tests_readme = load_text(root / "zigux/tests/README.md")
    helpers_text = load_text(root / "zigux/tests/phase1_helpers.zig")
    manifest, manifest_errors = load_json(root / "zigux/tests/fixtures/phase1_helper_manifest.json", "phase1_manifest")
    fixture, fixture_errors = load_json(root / "zigux/tests/fixtures/phase1_helpers.json", "phase1_fixture")

    missing: list[str] = []
    missing.extend(manifest_errors)
    missing.extend(fixture_errors)
    missing.extend(collect_required_markers(docs_root, "docs_root_phase1_packet", DOC_MARKERS["docs_root_phase1_packet"]))
    missing.extend(collect_required_markers(tests_readme, "tests_root_phase1_packet", DOC_MARKERS["tests_root_phase1_packet"]))
    missing.extend(collect_required_markers(review_checklist, "review_checklist_phase1_packet", DOC_MARKERS["review_checklist_phase1_packet"]))
    missing.extend(collect_phase1_helpers_markers(helpers_text))
    if manifest is not None:
        missing.extend(collect_manifest_markers(root, manifest))
    if fixture is not None:
        missing.extend(collect_fixture_markers(fixture))
    return missing


def required_marker_count() -> int:
    total = 0
    total += sum(len(markers) for markers in DOC_MARKERS.values())
    total += len(REQUIRED_IMPORT_MARKERS)
    total += 1
    total += len(REQUIRED_REPLAY_MARKERS)
    total += 5
    total += sum(
        len(expectations["required_values"])
        + len(expectations["required_list_members"])
        + len(expectations["required_substrings"])
        + len(expectations.get("source_markers", []))
        for expectations in REQUIRED_REVIEW_ANCHORS.values()
    )
    total += sum(
        len(compare_subset(expected_subset, expected_subset, helper))
        + _count_subset_items(expected_subset)
        for helper, expected_subset in EXPECTED_FIXTURE_SUBSETS.items()
    )
    return total


def _count_subset_items(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_count_subset_items(item) for item in value.values())
    return 1


def make_fixture_root(root: Path) -> None:
    fixture_files = set(REQUIRED_FILES)
    fixture_files.update(EXPECTED_HELPERS)
    fixture_files.update(
        [
            "tools/lib/rbtree.zig",
            "tools/lib/string.zig",
        ]
    )
    for rel in fixture_files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n", encoding="utf-8")

    (root / "Documentation/zigux/README.md").write_text("\n".join(DOC_MARKERS["docs_root_phase1_packet"]) + "\n", encoding="utf-8")
    (root / "zigux/tests/README.md").write_text("\n".join(DOC_MARKERS["tests_root_phase1_packet"]) + "\n", encoding="utf-8")
    (root / "Documentation/zigux/review-checklist.md").write_text(
        "\n".join(DOC_MARKERS["review_checklist_phase1_packet"]) + "\n",
        encoding="utf-8",
    )

    helpers_body = "\n".join(
        REQUIRED_IMPORT_MARKERS
        + ['test "phase 1 helper ports match committed parity fixture" {']
        + [f"    _ = {marker};" for marker in REQUIRED_REPLAY_MARKERS]
        + ["}"]
    ) + "\n"
    (root / "zigux/tests/phase1_helpers.zig").write_text(helpers_body, encoding="utf-8")

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": EXPECTED_LANE_SEQUENCING,
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "helper_test_anchors": [
                    'test "bitmap weight and clamps tail bits and aliases mirror the primary helper"',
                    'test "bitmap weight and keeps zero-bit windows empty"',
                    'test "bitmap Linux-style aliases keep zero-bit windows explicit no-ops"',
                ],
                "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
                "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
                "fill_tail_clamp_anchor": 'test "bitmap fill clamps tail bits in partial words"',
                "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
                "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
                "review_packet_summary": (
                    "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
                    "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while helper-local anchors "
                    "keep zero-size allocator and free-null behavior, predicate tail-mask, first-word boundary, final-partial "
                    "range boundary, fill tail-clamp, cross-word scnprintf collapse, empty-bitmap caller-buffer preservation, "
                    "copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, zero-bit no-op, zero-bit binary "
                    "identity, and Linux-style alias behavior review-visible on current master"
                ),
                "parity_fixture_keys": [
                    "alloc_words",
                    "zalloc_words",
                    "zalloc_values",
                    "scnprintf",
                    "truncated_scnprintf_len",
                    "truncated_scnprintf",
                    "terminator_only_scnprintf_len",
                    "terminator_only_nul",
                    "zero_length_scnprintf_len",
                ],
                "partial_xor_review_fields": [
                    "partial_xor_nbits",
                    "partial_xor_masked_values",
                ],
                "scnprintf_cross_word_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
                "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
                "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
                "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
                "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
                "copy_zero_and_aligned_anchors": [
                    'test "bitmap copy and extend handles zero and aligned counts"',
                    'test "bitmap copy helpers keep zero-sized destination views untouched"',
                ],
                "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
                "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
                "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
                "next_safe_step_note": (
                    "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
                    "drift or committed shared replay drift; do not reopen the already-closed closure-validator or "
                    "validator-summary packets by default."
                ),
            },
            "tools/lib/find_bit.zig": {
                "helper_test_anchors": [
                    'test "find or bit returns the next set bit from either bitmap"',
                    'test "clump8 scans mask out-of-range bits from partial final bytes"',
                ],
                "same_word_start_masks": 'test "single-word next scans honor start masks"',
                "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
                "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
                "tail_word_inclusive_boundary_contract": (
                    "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive "
                    "start lands on the last in-range bit of the final partial word, while later starts still return nbits "
                    "instead of leaking the out-of-range tail."
                ),
                "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
                "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
                "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
                "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
                "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers"',
                "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
                "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
                "tail_clamp_fixture_keys": [
                    "tail_clamped_first",
                    "tail_clamped_next",
                    "tail_zero_clamped_first",
                    "tail_zero_clamped_next",
                    "tail_and_clamped_first",
                    "tail_and_clamped_next",
                    "tail_clamped_last",
                    "tail_clamped_empty_last",
                ],
                "review_packet_summary": (
                    "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors "
                    "keep same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized "
                    "short-circuit, past-nbits, tail-word set or zero or shared skip, underscore-alias, and "
                    "Linux-style alias behavior review-visible on current master"
                ),
                "next_safe_step_note": (
                    "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift "
                    "inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, "
                    "underscore-alias, Linux-style alias, or tail-word skip anchors, or committed tail-clamped replay drift; "
                    "do not reopen older saved validator cues or neighboring helper families."
                ),
            },
            "tools/lib/rbtree.zig": {
                "cached_leftmost_fixture_keys": ["cached_leftmost_return_serials"],
                "duplicate_search_anchors": [
                    'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
                    'test "rbtree nextMatch walks the duplicate range in order"',
                    'test "rbtree matchIterator walks the duplicate range in order"',
                ],
                "cached_root_followup_anchors": [
                    'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
                    'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
                    'test "rbtree cached root keeps the leftmost pointer in sync"',
                    'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
                    'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
                    'test "rbtree eraseCached returns null for a singleton cached tree"',
                    'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
                    'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
                ],
                "review_packet_summary": (
                    "shared find, first-match, next-match, and match-iterator duplicate-search parity stays explicit through "
                    "the Phase 1 fixture and replay, and current master already carries the parked `cached_leftmost_return_serials` "
                    "fixture key for cached-root leftmost-return evidence, while cached-root leftmost-return, insert-miss, "
                    "leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned "
                    "by direct helper-local anchors until the shared replay consumes that committed key"
                ),
                "next_safe_step_note": (
                    "If this helper lane reopens, the smallest shared-replay promotion is now wiring the already-shipped "
                    "`cached_leftmost_return_serials` fixture key into the shared replay; until then, cached-root "
                    "leftmost-return and singleton-erase behavior stay owned by direct helper-local anchors."
                ),
            },
            "tools/lib/string.zig": {
                "parity_fixture_keys": [
                    "strtobool_invalid",
                    "replace_char_cstr_bytes",
                ],
                "prefix_suffix_review_summary": (
                    "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because "
                    "the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated "
                    "prefix or suffix fixture fields, so strHasPrefix and str_has_prefix plus strstarts plus strEndsWith "
                    "and str_ends_with plus strends remain review-visible at the helper surface"
                ),
                "memparse_review_summary": (
                    "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed "
                    "invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, "
                    "implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation"
                ),
                "shared_replace_char_cstr_review_summary": (
                    "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, "
                    "replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps "
                    "the first-terminator stop rule explicit without widening helper-local memparse ownership"
                ),
            },
        },
    }
    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    fixture = {
        "find_bit": EXPECTED_FIXTURE_SUBSETS["find_bit"],
        "bitmap": EXPECTED_FIXTURE_SUBSETS["bitmap"],
        "string": EXPECTED_FIXTURE_SUBSETS["string"],
        "rbtree": EXPECTED_FIXTURE_SUBSETS["rbtree"],
    }
    (root / "zigux/tests/fixtures/phase1_helpers.json").write_text(json.dumps(fixture, separators=(",", ":")) + "\n", encoding="utf-8")

    (root / "tools/lib/bitmap.zig").write_text(
        "\n".join(REQUIRED_REVIEW_ANCHORS["tools/lib/bitmap.zig"]["source_markers"]) + "\n",
        encoding="utf-8",
    )
    (root / "tools/lib/find_bit.zig").write_text(
        "\n".join(REQUIRED_REVIEW_ANCHORS["tools/lib/find_bit.zig"]["source_markers"]) + "\n",
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

        docs_path = root / "Documentation/zigux/README.md"
        original_docs = load_text(docs_path)
        docs_path.write_text(original_docs.replace(DOC_MARKERS["docs_root_phase1_packet"][0] + "\n", "", 1), encoding="utf-8")
        assert f'docs_root_phase1_packet:{DOC_MARKERS["docs_root_phase1_packet"][0]}:expected=1:actual=0' in collect_missing_markers(root)
        docs_path.write_text(original_docs, encoding="utf-8")
        case_count += 1

        tests_readme = root / "zigux/tests/README.md"
        original_tests_readme = load_text(tests_readme)
        tests_readme.write_text(
            original_tests_readme.replace(DOC_MARKERS["tests_root_phase1_packet"][1] + "\n", "", 1),
            encoding="utf-8",
        )
        assert f'tests_root_phase1_packet:{DOC_MARKERS["tests_root_phase1_packet"][1]}:expected=1:actual=0' in collect_missing_markers(root)
        tests_readme.write_text(original_tests_readme, encoding="utf-8")
        case_count += 1

        review_checklist = root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = load_text(review_checklist)
        review_checklist.write_text(
            original_review_checklist.replace(DOC_MARKERS["review_checklist_phase1_packet"][1] + "\n", "", 1),
            encoding="utf-8",
        )
        assert f'review_checklist_phase1_packet:{DOC_MARKERS["review_checklist_phase1_packet"][1]}:expected=1:actual=0' in collect_missing_markers(root)
        review_checklist.write_text(original_review_checklist, encoding="utf-8")
        case_count += 1

        helpers_path = root / "zigux/tests/phase1_helpers.zig"
        original_helpers = load_text(helpers_path)
        helpers_path.write_text(original_helpers.replace("fixture.bitmap.weight", "fixture.bitmap_weight", 1), encoding="utf-8")
        assert "phase1_replay_marker:fixture.bitmap.weight" in collect_missing_markers(root)
        helpers_path.write_text(original_helpers, encoding="utf-8")
        case_count += 1

        helpers_path.write_text(original_helpers + 'test "extra helper stays allowed" {}\n', encoding="utf-8")
        assert collect_missing_markers(root) == []
        helpers_path.write_text(original_helpers, encoding="utf-8")
        case_count += 1

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"].append('test "extra anchor stays allowed"')
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert collect_missing_markers(root) == []
        case_count += 1

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["first_word_boundary_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:first_word_boundary_anchor" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        fixture_path = root / "zigux/tests/fixtures/phase1_helpers.json"
        fixture = json.loads(load_text(fixture_path))
        fixture["rbtree"].pop("cached_leftmost_return_serials")
        fixture_path.write_text(json.dumps(fixture, separators=(",", ":")) + "\n", encoding="utf-8")
        assert "phase1_fixture:rbtree.cached_leftmost_return_serials" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        bitmap_path = root / "tools/lib/bitmap.zig"
        original_bitmap = load_text(bitmap_path)
        bitmap_path.write_text(original_bitmap.replace('test "bitmap weight and keeps zero-bit windows empty"\n', "", 1), encoding="utf-8")
        assert 'phase1_helper_anchor:tools/lib/bitmap.zig:test "bitmap weight and keeps zero-bit windows empty"' in collect_missing_markers(root)
        bitmap_path.write_text(original_bitmap, encoding="utf-8")
        case_count += 1

        helpers_path.write_text(original_helpers.replace('test "phase 1 helper ports match committed parity fixture" {', 'test "phase 1 helper parity" {', 1), encoding="utf-8")
        assert 'phase1_parity_test:test "phase 1 helper ports match committed parity fixture":expected=1:actual=0' in collect_missing_markers(root)
        helpers_path.write_text(original_helpers, encoding="utf-8")
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
    print(f"PHASE1_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

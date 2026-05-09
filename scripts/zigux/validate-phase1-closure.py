#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


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

EXPECTED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
            'test "bitmap allocator helpers size zero and free their buffers"',
            'test "bitmap size aliases round bit counts to full words in bytes"',
            'test "bitmap set clear weight and empty full helpers"',
            'test "bitmap range helpers honor exact first-word boundaries"',
            'test "bitmap range helpers clamp the final partial word"',
            'test "bitmap fill clamps tail bits in partial words"',
            'test "bitmap and andnot equal intersects subset"',
            'test "bitmap and andnot clamp tail bits in partial words"',
            'test "bitmap predicates ignore out-of-range tail bits"',
            'test "bitmap xor keeps caller-selected bit window"',
            'test "bitmap scnprintf collapses contiguous ranges"',
            'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
            'test "bitmap scnprintf reports full length while truncating the buffer"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy and extend handles zero and aligned counts"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
            'test "bitmap zero-bit binary helpers stay explicit identity operations"',
            'test "bitmap Linux-style aliases mirror the primary helper surface"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
        "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
        "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
        "parity_fixture_keys": [
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
        "cross_word_scnprintf_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "copy_extend_zero_aligned_anchor": 'test "bitmap copy and extend handles zero and aligned counts"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
        "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
        "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
    },
    "tools/lib/find_bit.zig": {
        "helper_test_anchors": [
            'test "single-word next scans honor start masks"',
            'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
            'test "zero-bit windows return without reading bitmap words"',
            'test "zero-sized scans ignore populated backing words"',
            'test "next scans past nbits return without reading bitmap words"',
            'test "tail-word next set scans skip earlier in-range matches before clamping"',
            'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
            'test "low-level underscore aliases mirror the primary find helpers"',
        ],
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
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
        "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, and underscore-alias behavior review-visible on current master",
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": [
            'test "rbtree inserts and traverses in sorted order"',
            'test "rbtree erase and replace keep traversal consistent"',
            'test "rbtree eraseInit detaches erased node"',
            'test "rbtree postorder and empty node helpers behave"',
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
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
            "next_match_terminal_null",
        ],
        "duplicate_search_anchors": [
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree matchIterator walks the duplicate range in order"',
        ],
        "cached_root_followup_anchors": [
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree findAddCached keeps cached leftmost stable while inserting misses"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseCached returns null for a singleton cached tree"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, leftmost-sync, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys",
    },
    "tools/lib/string.zig": {
        "helper_test_anchors": [
            'test "strtobool accepts common Linux forms"',
            'test "strlcpy copies and returns the source length"',
            'test "streq matches C-string equality semantics"',
            'test "skip trim remove and replace spaces work in place"',
            'test "strreplace mirrors replaceChar C-string semantics"',
            'test "strHasPrefix honors C-string boundaries"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
            'test "sysfsStreq treats trailing newline and NUL as equivalent"',
            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
            'test "memdup and memchrInv preserve byte content"',
            'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
            'test "memchrInv follows the earliest dirty byte as long buffers change"',
            'test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"',
            'test "memchrInv short zero-value scans stay byte-accurate"',
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
            'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        ],
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
        "prefix_suffix_review_anchors": [
            'test "strHasPrefix honors C-string boundaries"',
            'test "strstarts mirrors the header-level prefix helper"',
            'test "strEndsWith honors C-string boundaries"',
        ],
        "prefix_suffix_review_summary": "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields",
        "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep trailing-rest splits aligned with unsigned parsing, signed overflow saturates, and suffixes are still consumed after saturation",
        "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
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
            "memchr_inv_none",
        ],
    },
}

EXPECTED_BENCH_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
}

EXPECTED_BENCH_CHECKSUMS = [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
]

EXPECTED_BENCH_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 23340000,
    "PHASE1_BENCH_STRING_CHECKSUM": 15980000,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 3380000,
    "PHASE1_BENCH_RBTREE_DUPLICATE_MUTATION_CHECKSUM": 1672000,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 148000,
}
REQUIRED_FIND_BIT_BENCH_ITERATIONS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
}
REQUIRED_FIND_BIT_BENCH_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 23340000,
}

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
]

WORKFLOW_MARKERS = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py",
    "run: python3 scripts/zigux/validate-bootstrap.py",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
    "run: python3 scripts/zigux/check-phase1-installer-review-surfaces.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: zig build test --build-file zigux/tests/build.zig",
    "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
]

BUILD_MARKERS = [
    'const root_module = b.createModule(.{',
    '.root_source_file = b.path("phase1_helpers.zig"),',
    'const test_step = b.step("test", "Run Phase 1 helper tests");',
    'const bench_root_module = b.createModule(.{',
    '.root_source_file = b.path("phase1_bench.zig"),',
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
]

LEDGER_MARKERS = [
    '15. `docs(zigux): close bounded phase-1 helper tranche`',
    '16. `test(zigux): harden phase-1 closure gates`',
    '17. `ci(zigux): harden phase-1 closure workflow viability`',
    '18. `build(zigux): remove node-20-bound Zig action from phase-1 closure path`',
]

MAKEFILE_MARKERS = [
    "phase1: phase1-validate phase1-test phase1-bench",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-installer-review-surfaces.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig",
]

DOCS_ROOT_MARKERS = [
    "Phase 1 notes",
    "`Documentation/zigux/phase1-closure.md`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-parity.py`",
    "`scripts/zigux/check-phase1-bench.py`",
    "`zig build test --build-file zigux/tests/build.zig`",
    "`zig build bench --build-file zigux/tests/build.zig`",
    "`.github/workflows/zigux-bootstrap.yml`",
]

SCRIPTS_README_MARKERS = [
    "Phase 1 flow",
    "`validate-phase1-closure.py`",
    "`check-phase1-parity.py`",
    "`check-phase1-bench.py`",
    "`Documentation/zigux/review-checklist.md`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zig build test --build-file zigux/tests/build.zig`",
    "`zig build bench --build-file zigux/tests/build.zig`",
]

TESTS_README_MARKERS = [
    "`zigux/tests/phase1_helpers.zig`",
    "`zigux/tests/phase1_bench.zig`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`zigux/tests/fixtures/phase1_bench_expectations.json`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`make -C zigux phase1-validate`",
    "`make -C zigux phase1-test`",
    "`make -C zigux phase1-bench`",
    "`make -C zigux phase1`",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the closed Phase 1 host-tools packet",
    "`Documentation/zigux/phase1-closure.md`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`make -C zigux phase1`",
]

CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py",
    "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior",
    "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
    "PHASE1_FIND_BIT_ZERO_WINDOW_REVIEW=helper-local zero-bit-window proof stays explicit through the direct find_bit test anchor so first-scan entrypoints return the empty-window boundary without reading bitmap words",
    "PHASE1_FIND_BIT_ZERO_SIZED_REVIEW=helper-local zero-sized short-circuit proof stays explicit through the direct find_bit test anchor so zero-sized windows ignore populated backing words and return the caller-visible boundary without dereferencing live data",
    "PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window",
    "PHASE1_FIND_BIT_TAIL_WORD_SET_SKIP_REVIEW=helper-local tail-word next-set skip proof stays explicit through the direct find_bit test anchor so tail-word next set scans skip earlier in-range matches before clamping to nbits",
    "PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers",
    "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
    "PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW=helper-local bitmap predicate tail-mask proof stays explicit through the direct bitmap test anchor so equal, intersects, and subset ignore out-of-range tail bits instead of treating tail noise as live data",
    "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
    "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
    "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
    "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
    "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
    "PHASE1_BITMAP_COPY_EXTEND_ZERO_ALIGNED_REVIEW=helper-local bitmap copy-and-extend zero-count and aligned-count proof stays explicit through the direct bitmap test anchor so zero-count copies clear the destination extension and aligned word counts preserve copied words without accidental tail masking",
    "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes",
    "PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so andBits, andNotBits, equal, intersects, and subset keep empty-window identity semantics without treating zero-bit windows as live data",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
    "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation",
    "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, singleton-erase, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships",
    "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring",
]


def repo_root_from_arg(arg_root: str | None) -> Path:
    return Path(arg_root).resolve() if arg_root else DEFAULT_ROOT


def load_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def load_json(root: Path, rel: str) -> object:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES + EXPECTED_HELPERS:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def require_substrings(text: str, markers: list[str], prefix: str) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{prefix}:{marker}")
    return missing


def run_guard(root: Path, command: list[str], required_markers: list[str]) -> list[str]:
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    issues: list[str] = []
    label = " ".join(command[1:]) if len(command) > 1 else command[0]
    if result.returncode != 0:
        issues.append(f"guard_exit:{label}:returncode={result.returncode}")
    combined_output = "\n".join(
        part for part in (result.stdout.strip(), result.stderr.strip()) if part
    )
    for marker in required_markers:
        if marker not in combined_output:
            issues.append(f"guard_marker:{label}:{marker}")
    return issues


def collect_manifest_markers(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest:type=dict"]
    missing: list[str] = []
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing.append("manifest:status=closed")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        missing.append(f"manifest:helper_count={len(EXPECTED_HELPERS)}")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        missing.append("manifest:helpers")
    if manifest.get("review_anchors") != EXPECTED_REVIEW_ANCHORS:
        missing.append("manifest:review_anchors")
    return missing


def collect_bench_markers(expectations: object) -> list[str]:
    if not isinstance(expectations, dict):
        return ["bench:type=dict"]
    missing: list[str] = []
    if expectations.get("status") != "pass":
        missing.append("bench:status=pass")

    iterations = expectations.get("iterations")
    if iterations != EXPECTED_BENCH_ITERATIONS:
        missing.append("bench:iterations")
    if isinstance(iterations, dict):
        for key, expected in REQUIRED_FIND_BIT_BENCH_ITERATIONS.items():
            if iterations.get(key) != expected:
                missing.append(f"bench:find_bit_iterations:{key}={expected}")

    if expectations.get("checksums") != EXPECTED_BENCH_CHECKSUMS:
        missing.append("bench:checksums")

    exact_checksums = expectations.get("exact_checksums")
    if not isinstance(exact_checksums, dict):
        missing.append("bench:exact_checksums")
        return missing
    for key, expected in EXPECTED_BENCH_EXACT_CHECKSUMS.items():
        if exact_checksums.get(key) != expected:
            missing.append(f"bench:exact_checksums:{key}={expected}")
    for key, expected in REQUIRED_FIND_BIT_BENCH_EXACT_CHECKSUMS.items():
        if exact_checksums.get(key) != expected:
            missing.append(f"bench:find_bit_exact_checksums:{key}={expected}")
    return missing


def collect_guard_issues(root: Path) -> list[str]:
    return run_guard(
        root,
        [
            sys.executable,
            str(root / "scripts" / "zigux" / "check-phase1-installer-review-surfaces.py"),
            "--self-test",
        ],
        [
            "PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST=pass",
            "PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST_CASE_COUNT=18",
        ],
    ) + run_guard(
        root,
        [
            sys.executable,
            str(root / "scripts" / "zigux" / "check-phase1-installer-review-surfaces.py"),
        ],
        [
            "PHASE1_INSTALLER_REVIEW_SURFACES=pass",
            "PHASE1_INSTALLER_REVIEW_SURFACES_MARKER_COUNT=17",
        ],
    )


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    missing.extend(require_substrings(load_text(root, "Documentation/zigux/phase1-closure.md"), CLOSURE_MARKERS, "closure"))
    missing.extend(require_substrings(load_text(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS, "workflow"))
    missing.extend(require_substrings(load_text(root, "zigux/tests/build.zig"), BUILD_MARKERS, "build"))
    missing.extend(require_substrings(load_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md"), LEDGER_MARKERS, "ledger"))
    missing.extend(require_substrings(load_text(root, "zigux/Makefile"), MAKEFILE_MARKERS, "makefile"))
    missing.extend(require_substrings(load_text(root, "Documentation/zigux/README.md"), DOCS_ROOT_MARKERS, "docs"))
    missing.extend(require_substrings(load_text(root, "scripts/zigux/README.md"), SCRIPTS_README_MARKERS, "scripts_readme"))
    missing.extend(require_substrings(load_text(root, "zigux/tests/README.md"), TESTS_README_MARKERS, "tests_readme"))
    missing.extend(require_substrings(load_text(root, "Documentation/zigux/review-checklist.md"), REVIEW_CHECKLIST_MARKERS, "review"))
    missing.extend(collect_manifest_markers(load_json(root, "zigux/tests/fixtures/phase1_helper_manifest.json")))
    missing.extend(collect_bench_markers(load_json(root, "zigux/tests/fixtures/phase1_bench_expectations.json")))
    return missing


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES + EXPECTED_HELPERS:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("// fixture\n", encoding="utf-8")

    (root / "Documentation/zigux/phase1-closure.md").write_text("\n".join(CLOSURE_MARKERS) + "\n", encoding="utf-8")
    (root / ".github/workflows/zigux-bootstrap.yml").write_text("\n".join(WORKFLOW_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux/tests/build.zig").write_text("\n".join(BUILD_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").write_text("\n".join(LEDGER_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux/Makefile").write_text("\n".join(MAKEFILE_MARKERS) + "\n", encoding="utf-8")
    (root / "Documentation/zigux/README.md").write_text("\n".join(DOCS_ROOT_MARKERS) + "\n", encoding="utf-8")
    (root / "scripts/zigux/README.md").write_text("\n".join(SCRIPTS_README_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux/tests/README.md").write_text("\n".join(TESTS_README_MARKERS) + "\n", encoding="utf-8")
    (root / "Documentation/zigux/review-checklist.md").write_text("\n".join(REVIEW_CHECKLIST_MARKERS) + "\n", encoding="utf-8")

    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": len(EXPECTED_HELPERS),
                "helpers": EXPECTED_HELPERS,
                "review_anchors": EXPECTED_REVIEW_ANCHORS,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "zigux/tests/fixtures/phase1_bench_expectations.json").write_text(
        json.dumps(
            {
                "status": "pass",
                "iterations": EXPECTED_BENCH_ITERATIONS,
                "checksums": EXPECTED_BENCH_CHECKSUMS,
                "exact_checksums": EXPECTED_BENCH_EXACT_CHECKSUMS,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def assert_missing_closure_marker(root: Path, marker: str) -> None:
    path = root / "Documentation/zigux/phase1-closure.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
        encoding="utf-8",
    )
    assert f"closure:{marker}" in collect_missing_markers(root)


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmpdir:
        root = Path(tmpdir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []

        path = root / ".github/workflows/zigux-bootstrap.yml"
        path.write_text(path.read_text(encoding="utf-8").replace(WORKFLOW_MARKERS[0] + "\n", "", 1), encoding="utf-8")
        assert any(item.startswith("workflow:") for item in collect_missing_markers(root))
        cases += 1
        make_fixture_root(root)

        path = root / "zigux/tests/build.zig"
        path.write_text(path.read_text(encoding="utf-8").replace(BUILD_MARKERS[2] + "\n", "", 1), encoding="utf-8")
        assert any(item.startswith("build:") for item in collect_missing_markers(root))
        cases += 1
        make_fixture_root(root)

        path = root / "zigux/Makefile"
        path.write_text(path.read_text(encoding="utf-8").replace(MAKEFILE_MARKERS[0] + "\n", "", 1), encoding="utf-8")
        assert any(item.startswith("makefile:") for item in collect_missing_markers(root))
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(root, "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig")
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(root, "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig")
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_FIND_BIT_ZERO_SIZED_REVIEW=helper-local zero-sized short-circuit proof stays explicit through the direct find_bit test anchor so zero-sized windows ignore populated backing words and return the caller-visible boundary without dereferencing live data",
        )
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window",
        )
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_FIND_BIT_TAIL_WORD_SET_SKIP_REVIEW=helper-local tail-word next-set skip proof stays explicit through the direct find_bit test anchor so tail-word next set scans skip earlier in-range matches before clamping to nbits",
        )
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
        )
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
        )
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_BITMAP_COPY_EXTEND_ZERO_ALIGNED_REVIEW=helper-local bitmap copy-and-extend zero-count and aligned-count proof stays explicit through the direct bitmap test anchor so zero-count copies clear the destination extension and aligned word counts preserve copied words without accidental tail masking",
        )
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so andBits, andNotBits, equal, intersects, and subset keep empty-window identity semantics without treating zero-bit windows as live data",
        )
        cases += 1
        make_fixture_root(root)

        assert_missing_closure_marker(
            root,
            "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
        )
        cases += 1
        make_fixture_root(root)

        path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["helpers"] = manifest["helpers"][:-1]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "manifest:helpers" in collect_missing_markers(root)
        cases += 1
        make_fixture_root(root)

        path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(path.read_text(encoding="utf-8"))
        del bench["iterations"]["PHASE1_BENCH_STRING_ITERATIONS"]
        path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "bench:iterations" in collect_missing_markers(root)
        cases += 1
        make_fixture_root(root)

        path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(path.read_text(encoding="utf-8"))
        del bench["iterations"]["PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS"]
        path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "bench:find_bit_iterations:PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000" in collect_missing_markers(root)
        cases += 1
        make_fixture_root(root)

        path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(path.read_text(encoding="utf-8"))
        del bench["exact_checksums"]["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
        path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "bench:exact_checksums:PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=148000" in collect_missing_markers(root)
        cases += 1
        make_fixture_root(root)

        path = root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(path.read_text(encoding="utf-8"))
        del bench["exact_checksums"]["PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM"]
        path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        assert "bench:find_bit_exact_checksums:PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM=23340000" in collect_missing_markers(root)
        cases += 1
        make_fixture_root(root)

        (root / "scripts/zigux/validate-phase1-closure.py").unlink()
        assert collect_missing_files(root) == ["scripts/zigux/validate-phase1-closure.py"]
        cases += 1
        make_fixture_root(root)

        checker_path = root / "phase1_installer_guard.py"
        checker_path.write_text(
            "print(\"PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST=pass\")\n"
            "print(\"PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST_CASE_COUNT=18\")\n",
            encoding="utf-8",
        )
        assert run_guard(
            root,
            [sys.executable, str(checker_path)],
            [
                "PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST=pass",
                "PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST_CASE_COUNT=18",
            ],
        ) == []
        cases += 1

        checker_path.write_text(
            "print(\"PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST=pass\")\n",
            encoding="utf-8",
        )
        issues = run_guard(
            root,
            [sys.executable, str(checker_path)],
            [
                "PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST=pass",
                "PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST_CASE_COUNT=18",
            ],
        )
        assert any(
            issue.endswith("PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST_CASE_COUNT=18")
            for issue in issues
        )
        cases += 1

        checker_path.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
        issues = run_guard(
            root,
            [sys.executable, str(checker_path)],
            ["PHASE1_INSTALLER_REVIEW_SURFACES_SELF_TEST=pass"],
        )
        assert any(":returncode=1" in issue for issue in issues)
        cases += 1

        checker_path.write_text(
            "print(\"PHASE1_INSTALLER_REVIEW_SURFACES=pass\")\n"
            "print(\"PHASE1_INSTALLER_REVIEW_SURFACES_MARKER_COUNT=17\")\n",
            encoding="utf-8",
        )
        assert run_guard(
            root,
            [sys.executable, str(checker_path)],
            [
                "PHASE1_INSTALLER_REVIEW_SURFACES=pass",
                "PHASE1_INSTALLER_REVIEW_SURFACES_MARKER_COUNT=17",
            ],
        ) == []
        cases += 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 1 closure packet.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_CLOSURE_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        return 1

    guard_issues = collect_guard_issues(root)
    if guard_issues:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("PHASE1_CLOSURE_GUARD_ISSUES_START")
        for item in guard_issues:
            print(item)
        print("PHASE1_CLOSURE_GUARD_ISSUES_END")
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(CLOSURE_MARKERS) + len(WORKFLOW_MARKERS) + len(BUILD_MARKERS) + len(LEDGER_MARKERS) + len(MAKEFILE_MARKERS) + len(DOCS_ROOT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + 5 + 3 + len(EXPECTED_BENCH_EXACT_CHECKSUMS) + len(REQUIRED_FIND_BIT_BENCH_ITERATIONS) + len(REQUIRED_FIND_BIT_BENCH_EXACT_CHECKSUMS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

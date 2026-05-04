#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_PHASE1_ROOT")
    if override:
        return Path(override)
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


ROOT = repo_root()
REQUIRED_FILE_RELS = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-bitmap-validator-anchors.py",
    "scripts/zigux/check-phase1-find-bit-validator-anchors.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-validation-route-inventory.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
]

REQUIRED_HELPERS = [
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

REQUIRED_DOCS_ROOT_MARKERS = [
    "- `Documentation/zigux/phase1-closure.md` remains the dedicated closure packet for the bounded host-side `tools/lib/*.zig` helper tranche, and `zigux/tests/fixtures/phase1_helper_manifest.json` plus `zigux/tests/phase1_helpers.zig` keep the closed helper inventory and parity-backed replay surface explicit from the docs root.",
    "- `python3 scripts/zigux/validate-phase1.py`, `python3 scripts/zigux/validate-phase1-closure.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` are the current validator-first and replay entrypoints for that bounded host-side helper packet.",
]

REQUIRED_SCRIPTS_ROOT_MARKERS = [
    "- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.",
    "- `check-phase1-bitmap-validator-anchors.py --self-test`, `check-phase1-bitmap-validator-anchors.py`, `check-phase1-find-bit-validator-anchors.py --self-test`, `check-phase1-find-bit-validator-anchors.py`, `check-phase1-route-summary-counts.py --self-test`, `check-phase1-route-summary-counts.py`, `check-phase1-validation-route-inventory.py --self-test`, `check-phase1-validation-route-inventory.py`, `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.",
]

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test",
    'bitmap tail-mask unit-test anchor: `tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"`',
    'bitmap zero-bit unit-test anchor: `tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"`',
    'bitmap empty unit-test anchor: `tools/lib/bitmap.zig:test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"`',
    "PHASE1_BITMAP_TAIL_MASK_UNIT_REVIEW=bitmap tail-masked reduction helpers ignore out-of-range differences while preserving the in-range window for andBits, andNotBits, equal, intersects, and subset",
    "PHASE1_BITMAP_ZERO_BIT_UNIT_REVIEW=bitmap zero-length helper calls stay side-effect free so zero fill copy copyClearTail orBits xorBits scans and formatting leave caller-owned buffers untouched when nbits is zero",
    "PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap bitmap_scnprintf keeps a non-empty caller buffer untouched when no bits are set, matching the committed empty-bitmap parity fixture contract",
    "PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the last in-range bit reachable from an inclusive start while later starts still return nbits instead of leaking the out-of-range tail",
    "PHASE1_FIND_BIT_TAIL_WORD_BOUNDARY_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the first in-range tail-word match reachable when the search starts exactly at the tail-word boundary instead of rereading an earlier full-word result",
    "PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit scans return 0 even when backing words are populated so declared nbits stays authoritative over caller storage",
    "PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse preserves decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract",
    "PHASE1_RBTREE_POSTORDER_ITERATOR_UNIT_REVIEW=rbtree iteratePostorder visits each node exactly once in left-right-root order and reports exhaustion cleanly after the full walk",
    "PHASE1_RBTREE_POSTORDER_SAFE_UNIT_REVIEW=rbtree iteratePostorderSafe caches exactly one step ahead so callers can invalidate the current node without truncating the remaining postorder walk",
    "PHASE1_RBTREE_POSTORDER_SAFE_REBALANCE_UNIT_REVIEW=rbtree iteratePostorderSafe stays aligned across erase-driven rebalancing so the walk still reaches each remaining node exactly once after the current node is removed",
    "PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_RBTREE_ALIAS_GAP_NOTE=the closed Phase 1 rbtree tranche still excludes Linux-style rb_* alias parity for the already-ported entry points, and that remaining surface stays explicitly out of scope until a later bounded repair lands",
    "PHASE1_RBTREE_ALIAS_GAP_GATE=phase1 closure validation fails closed if tools/lib/rbtree.zig grows Linux-style rb_* aliases before the closed helper tranche is deliberately reopened",
]

REQUIRED_WORKFLOW_MARKERS = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "run: python3 scripts/zigux/validate-phase1.py --self-test",
    "run: python3 scripts/zigux/validate-phase1.py",
    "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py --self-test",
    "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/check-phase1-parity.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
]

REQUIRED_BUILD_MARKERS = [
    '.root_source_file = b.path("phase1_bench.zig"),',
    'bench_root_module.addImport("find_bit", find_bit_module);',
    'const bench = b.addExecutable(.{',
    '.name = "phase1-bench",',
    'const run_bench = b.addRunArtifact(bench);',
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
]

REQUIRED_HELPER_TEST_MARKERS = [
    'const argv_split = @import("argv_split");',
    '@embedFile("fixtures/phase1_helpers.json")',
    'test "phase 1 helper modules import cleanly" {',
    'test "phase 1 helper ports match committed parity fixture" {',
    'test "phase 1 bitmap allocation helpers keep ownership and zeroing explicit" {',
]

REQUIRED_LEDGER_MARKERS = [
    "15. `docs(zigux): close bounded phase-1 helper tranche`",
    "16. `test(zigux): harden phase-1 closure gates`",
    "17. `ci(zigux): harden phase-1 closure workflow viability`",
    "18. `build(zigux): remove node-20-bound Zig action from phase-1 closure path`",
]

REQUIRED_BENCH_CHECKER_MARKERS = [
    "print('PHASE1_BENCH_SELF_TEST=pass')",
    "print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=19')",
    "print('DUPLICATE_PHASE1_BENCH_KEYS_START')",
    "print('MISSING_PHASE1_BENCH_KEYS_START')",
]

REQUIRED_PARITY_CHECKER_MARKERS = [
    "print('bitmap.scnprintf_empty_len')",
    "print('bitmap.scnprintf_empty_bytes')",
    "print('bitmap.scnprintf_trunc_len')",
    "print('bitmap.scnprintf_trunc')",
    "print('PHASE1_PARITY_SELF_TEST=pass')",
    "print('PHASE1_PARITY_SELF_TEST_CASE_COUNT=7')",
]

REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase1-validate phase1-test phase1-bench phase1",
    "phase1-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-validation-route-inventory.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-validation-route-inventory.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
    "phase1-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
    "phase1-bench:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
    "phase1: phase1-validate phase1-test phase1-bench",
]

REQUIRED_EXACT_COUNT_MARKERS = [
    (
        "docs_root_phase1_closure_packet_count",
        "Documentation/zigux/README.md",
        REQUIRED_DOCS_ROOT_MARKERS[0],
        1,
    ),
    (
        "docs_root_phase1_entrypoints_count",
        "Documentation/zigux/README.md",
        REQUIRED_DOCS_ROOT_MARKERS[1],
        1,
    ),
    (
        "scripts_root_phase1_validator_first_count",
        "scripts/zigux/README.md",
        REQUIRED_SCRIPTS_ROOT_MARKERS[0],
        1,
    ),
    (
        "scripts_root_phase1_review_hooks_count",
        "scripts/zigux/README.md",
        REQUIRED_SCRIPTS_ROOT_MARKERS[1],
        1,
    ),
    (
        "workflow_phase1_validate_self_test_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1.py --self-test",
        1,
    ),
    (
        "workflow_phase1_validate_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1.py",
        1,
    ),
    (
        "workflow_phase1_bitmap_self_test_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test",
        1,
    ),
    (
        "workflow_phase1_bitmap_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py",
        1,
    ),
    (
        "workflow_phase1_route_summary_self_test_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        1,
    ),
    (
        "workflow_phase1_route_summary_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        1,
    ),
    (
        "workflow_phase1_route_inventory_self_test_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py --self-test",
        1,
    ),
    (
        "workflow_phase1_route_inventory_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py",
        1,
    ),
    (
        "workflow_phase1_bench_self_test_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        1,
    ),
    (
        "workflow_phase1_bench_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bench.py",
        1,
    ),
    (
        "workflow_phase1_closure_self_test_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        1,
    ),
    (
        "workflow_phase1_closure_count",
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        1,
    ),
    (
        "makefile_phase1_validate_self_test_count",
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py --self-test",
        1,
    ),
    (
        "makefile_phase1_bench_self_test_count",
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py --self-test",
        1,
    ),
    (
        "makefile_phase1_bench_count",
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py",
        1,
    ),
    (
        "makefile_phase1_closure_self_test_count",
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py --self-test",
        1,
    ),
    (
        "makefile_phase1_closure_count",
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
        1,
    ),
]

# Keep these benchmark loop counts in a keyed map so the closure validator can compare them by name.
REQUIRED_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_COPY_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_SCNPRINTF_ITERATIONS": 12000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
}

REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 2260000,
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 620000,
    "PHASE1_BENCH_BITMAP_COPY_CHECKSUM": 22040000,
    "PHASE1_BENCH_BITMAP_SCNPRINTF_CHECKSUM": 11760000,
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 15621472,
    "PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM": 17862764,
    "PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM": 8124000,
    "PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM": 2200000,
    "PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM": 1929133,
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM": 1925492,
    "PHASE1_BENCH_STRING_CHECKSUM": 2500000,
    "PHASE1_BENCH_STRING_BOOL_TRIM_CHECKSUM": 500000,
    "PHASE1_BENCH_STRING_COMPARE_CHECKSUM": 360000,
    "PHASE1_BENCH_STRING_MEMCHR_CHECKSUM": 2400000,
    "PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM": 437855789,
    "PHASE1_BENCH_RBTREE_CHECKSUM": 1308000,
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 1188000,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 196000,
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 3484000,
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 1488000,
}

REQUIRED_MANIFEST_FIELDS = {
    "tools/lib/bitmap.zig": {
        "unit_test_contract": "Direct Zig unit coverage keeps bitmapAlloc(), bitmapZalloc(), and bitmapFree() honest by proving optional bitmap handles size through bitsToWords(), zero-filled allocation stays intact, and released optionals reset to null.",
        "allocator_alias_unit_test_contract": "Direct Zig unit coverage keeps bitmap_alloc(), bitmap_zalloc(), and bitmap_free() aligned with bitmapAlloc(), bitmapZalloc(), and bitmapFree() for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.",
        "copy_alias_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_alias_unit_test_contract": "Direct Zig unit coverage keeps bitmap_copy_clear_tail() and bitmap_copy_and_extend() aligned with copyClearTail() and copyAndExtend() by preserving tail masking in the final copied word and zero-filled extension across the remaining word window.",
        "tail_mask_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"',
        "tail_mask_unit_test_contract": "Direct Zig unit coverage keeps andBits(), andNotBits(), equal(), intersects(), and subset() aligned by masking out-of-range tail differences while preserving the declared in-range window.",
        "zero_bit_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"',
        "zero_bit_unit_test_contract": "Direct Zig unit coverage keeps zero-length helper calls explicit and side-effect free so zero(), fill(), copy(), copyClearTail(), orBits(), xorBits(), scans, and formatting all leave caller-owned buffers untouched when nbits is zero.",
        "empty_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
        "empty_unit_test_contract": "Direct Zig unit coverage keeps bitmap_scnprintf() from mutating a non-empty caller buffer when no bits are set, matching the committed empty-bitmap parity fixture contract.",
    },
    "tools/lib/find_bit.zig": {
        "tail_start_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"',
        "tail_start_unit_test_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit, while later starts still return nbits instead of leaking the out-of-range tail.",
        "tail_word_boundary_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans honor an exact tail-word boundary start"',
        "tail_word_boundary_unit_test_contract": "Direct Zig unit coverage keeps set, zero, and shared-bit tail scans aligned when the search starts exactly at the first tail-word bit index, so the first in-range tail match remains reachable without rereading an earlier full-word result.",
        "zero_sized_unit_test_anchor": 'tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"',
        "zero_sized_unit_test_contract": "Direct Zig unit coverage keeps zero-length set, zero, and shared-bit scans aligned by returning 0 even when backing words are populated, so declared nbits stays authoritative over caller storage.",
    },
    "tools/lib/rbtree.zig": {
        "shared_parity_scope_note": "The committed shared Phase 1 fixture still stops at traversal, replaceNode, eraseInit, postorder traversal, and detached-node state checks; duplicate-key search, duplicate-range iterators, and cached-root minima tracking are currently recorded as direct Zig unit coverage only in this closed tranche.",
        "alias_gap_note": "Linux-style rb_* alias surface parity is still missing for the already-ported entry points, and that remaining surface stays explicitly out of scope for the closed Phase 1 tranche until a later bounded repair lands.",
        "cached_find_add_unit_test_contract": "Direct Zig unit coverage keeps findAddCached() aligned so equal-key probes return the original resident node, distinct inserts still link into the cached tree, and RootCached continues to expose the same leftmost node as the underlying tree root.",
        "postorder_iterator_unit_test_contract": "Direct Zig unit coverage keeps iteratePostorder() aligned so the explicit iterator visits each node exactly once in left-right-root order and reports exhaustion cleanly after the full walk.",
        "postorder_safe_unit_test_contract": "Direct Zig unit coverage keeps iteratePostorderSafe() aligned by caching exactly one step ahead so callers can invalidate the current node without truncating the remaining postorder walk.",
        "postorder_safe_rebalance_unit_test_contract": "Direct Zig unit coverage keeps iteratePostorderSafe() aligned across erase-driven rebalancing so the walk still reaches each remaining node exactly once after the current node is removed.",
    },
    "tools/lib/string.zig": {
        "strscpy_unit_test_contract": "Direct Zig unit coverage keeps strscpy aligned with bounded kernel copy semantics for exact-fit, truncation, embedded-NUL, and zero-sized destination cases.",
        "sysfs_unit_test_contract": "Direct Zig unit coverage keeps sysfsStreq() and sysfs_streq() aligned by treating a single trailing newline as equivalent to C-string termination while still rejecting non-terminal newline and content mismatches.",
        "memparse_unit_test_contract": "Direct Zig unit coverage keeps memparse aligned by preserving decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract.",
    },
}

RBTREE_UNEXPECTED_ALIAS_MARKERS = ["pub fn rb_first(", "pub fn rb_next_match(", "pub fn rb_erase("]

WORKFLOW_EXACT_COUNT_PREFIXES = {
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test": "        ",
    "run: python3 scripts/zigux/check-phase1-bench.py": "        ",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test": "        ",
    "run: python3 scripts/zigux/validate-phase1-closure.py": "        ",
}

MAKEFILE_EXACT_COUNT_PREFIXES = {
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py --self-test": "\t",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py": "\t",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py --self-test": "\t",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py": "\t",
}


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def normalized_lines(rel: str) -> list[str]:
    return [line.strip() for line in read_text(rel).splitlines()]


def fail(items: list[str]) -> int:
    print("PHASE1_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE1_CLOSURE_MARKERS_START")
    for item in items:
        print(item)
    print("MISSING_PHASE1_CLOSURE_MARKERS_END")
    return 1


def check_contains(label: str, rel: str, markers: list[str], missing: list[str]) -> None:
    text = read_text(rel)
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def check_exact_count(label: str, rel: str, marker: str, expected: int, missing: list[str]) -> None:
    normalized_marker = marker.strip()
    actual = sum(1 for line in normalized_lines(rel) if line == normalized_marker)
    if actual != expected:
        missing.append(f"{label}:expected={expected}:actual={actual}")


def validate_manifest(missing: list[str]) -> None:
    manifest = json.loads(read_text("zigux/tests/fixtures/phase1_helper_manifest.json"))
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing.append("manifest:status=closed")
    if manifest.get("helper_count") != 13:
        missing.append("manifest:helper_count=13")
    if manifest.get("helpers") != REQUIRED_HELPERS:
        missing.append("manifest:helpers")
    review = manifest.get("helper_review_notes", {})
    for helper, fields in REQUIRED_MANIFEST_FIELDS.items():
        actual = review.get(helper, {})
        for key, value in fields.items():
            if actual.get(key) != value:
                missing.append(f"manifest:{helper}:{key}")


def validate_expectations(missing: list[str]) -> None:
    expectations = json.loads(read_text("zigux/tests/fixtures/phase1_bench_expectations.json"))
    if expectations.get("status") != "pass":
        missing.append("bench:status=pass")
    iterations = expectations.get("iterations", {})
    exact = expectations.get("exact_checksums", {})
    checksums = set(expectations.get("checksums", []))
    for key, value in REQUIRED_ITERATIONS.items():
        if iterations.get(key) != value:
            missing.append(f"bench:iterations.{key}={value}")
    for key, value in REQUIRED_EXACT_CHECKSUMS.items():
        if exact.get(key) != value:
            missing.append(f"bench:exact_checksums.{key}={value}")
        if key in checksums:
            missing.append(f"bench:remove_loose_exact_checksum:{key}")


def validate_rbtree_alias_gap(missing: list[str]) -> None:
    source = read_text("tools/lib/rbtree.zig")
    for marker in RBTREE_UNEXPECTED_ALIAS_MARKERS:
        if marker in source:
            missing.append(f"rbtree_source:unexpected_alias:{marker}")


def main() -> int:
    missing_files = [rel for rel in REQUIRED_FILE_RELS if not (ROOT / rel).exists()]
    if missing_files:
        return fail([f"file:{rel}" for rel in missing_files])
    missing: list[str] = []
    check_contains("docs_root", "Documentation/zigux/README.md", REQUIRED_DOCS_ROOT_MARKERS, missing)
    check_contains("scripts_root", "scripts/zigux/README.md", REQUIRED_SCRIPTS_ROOT_MARKERS, missing)
    check_contains("closure", "Documentation/zigux/phase1-closure.md", REQUIRED_CLOSURE_MARKERS, missing)
    check_contains("workflow", ".github/workflows/zigux-bootstrap.yml", REQUIRED_WORKFLOW_MARKERS, missing)
    check_contains("build", "zigux/tests/build.zig", REQUIRED_BUILD_MARKERS, missing)
    check_contains("helper_tests", "zigux/tests/phase1_helpers.zig", REQUIRED_HELPER_TEST_MARKERS, missing)
    check_contains("ledger", "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", REQUIRED_LEDGER_MARKERS, missing)
    check_contains("bench_checker", "scripts/zigux/check-phase1-bench.py", REQUIRED_BENCH_CHECKER_MARKERS, missing)
    check_contains("parity_checker", "scripts/zigux/check-phase1-parity.py", REQUIRED_PARITY_CHECKER_MARKERS, missing)
    check_contains("makefile", "zigux/Makefile", REQUIRED_MAKEFILE_MARKERS, missing)
    for label, rel, marker, expected in REQUIRED_EXACT_COUNT_MARKERS:
        check_exact_count(label, rel, marker, expected, missing)
    validate_manifest(missing)
    validate_expectations(missing)
    validate_rbtree_alias_gap(missing)
    if missing:
        return fail(missing)
    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILE_RELS)}")
    marker_count = sum(len(group) for group in [
        REQUIRED_DOCS_ROOT_MARKERS,
        REQUIRED_SCRIPTS_ROOT_MARKERS,
        REQUIRED_CLOSURE_MARKERS,
        REQUIRED_WORKFLOW_MARKERS,
        REQUIRED_BUILD_MARKERS,
        REQUIRED_HELPER_TEST_MARKERS,
        REQUIRED_LEDGER_MARKERS,
        REQUIRED_BENCH_CHECKER_MARKERS,
        REQUIRED_PARITY_CHECKER_MARKERS,
        REQUIRED_MAKEFILE_MARKERS,
    ]) + len(REQUIRED_EXACT_COUNT_MARKERS)
    print(f"PHASE1_CLOSURE_REQUIRED_MARKER_COUNT={marker_count}")
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_manifest() -> dict[str, object]:
    review = {helper: dict(fields) for helper, fields in REQUIRED_MANIFEST_FIELDS.items()}
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": REQUIRED_HELPERS,
        "helper_review_notes": review,
    }


def fixture_expectations() -> dict[str, object]:
    return {
        "status": "pass",
        "iterations": REQUIRED_ITERATIONS,
        "exact_checksums": REQUIRED_EXACT_CHECKSUMS,
        "checksums": ["PHASE1_BENCH_HWEIGHT_CHECKSUM", "PHASE1_BENCH_LIST_SORT_CHECKSUM"],
    }


def render_fixture_lines(markers: list[str], prefixes: dict[str, str] | None = None) -> str:
    prefixes = prefixes or {}
    return "\n".join(f"{prefixes.get(marker, '')}{marker}" for marker in markers) + "\n"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(root / "scripts/zigux/validate-phase1-closure.py")], cwd=root, capture_output=True, text=True, check=False)


def expect_failure(root: Path, expected: str) -> None:
    result = run_validator(root)
    if result.returncode == 0 or expected not in result.stdout:
        raise SystemExit(f"phase1-self-test:expected_failure:{expected}:actual:{result.stdout or result.stderr}")


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-closure-") as tmp:
        root = Path(tmp)
        for rel in REQUIRED_FILE_RELS:
            if rel.endswith(".json"):
                continue
            write(root / rel, "// fixture\n")
        write(root / "Documentation/zigux/README.md", "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
        write(root / "scripts/zigux/README.md", "\n".join(REQUIRED_SCRIPTS_ROOT_MARKERS) + "\n")
        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
        write(root / ".github/workflows/zigux-bootstrap.yml", render_fixture_lines(REQUIRED_WORKFLOW_MARKERS, WORKFLOW_EXACT_COUNT_PREFIXES))
        write(root / "zigux/tests/build.zig", "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
        write(root / "zigux/tests/phase1_helpers.zig", "\n".join(REQUIRED_HELPER_TEST_MARKERS) + "\n")
        write(root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", "\n".join(REQUIRED_LEDGER_MARKERS) + "\n")
        write(root / "scripts/zigux/check-phase1-bench.py", "\n".join(REQUIRED_BENCH_CHECKER_MARKERS) + "\n")
        write(root / "scripts/zigux/check-phase1-parity.py", "\n".join(REQUIRED_PARITY_CHECKER_MARKERS) + "\n")
        write(root / "scripts/zigux/check-phase1-bitmap-validator-anchors.py", "# fixture\n")
        write(root / "scripts/zigux/check-phase1-find-bit-validator-anchors.py", "# fixture\n")
        write(root / "scripts/zigux/check-phase1-route-summary-counts.py", "# fixture\n")
        write(root / "scripts/zigux/check-phase1-validation-route-inventory.py", "# fixture\n")
        write(root / "scripts/zigux/validate-phase1.py", "# fixture\n")
        write(root / "zigux/Makefile", render_fixture_lines(REQUIRED_MAKEFILE_MARKERS, MAKEFILE_EXACT_COUNT_PREFIXES))
        write(root / "scripts/zigux/artifact_diff.py", "# fixture\n")
        write(root / "scripts/zigux/install-zig.py", "# fixture\n")
        write(root / "zigux/tests/phase1_bench.zig", "// fixture\n")
        write(root / "zigux/tests/README.md", "# fixture\n")
        write(root / "zigux/tests/fixtures/phase1_helpers.json", "{}\n")
        write(root / "zigux/tests/fixtures/phase1_helpers_c_harness.c", "/* fixture */\n")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(fixture_expectations(), indent=2) + "\n")
        write(root / "tools/lib/rbtree.zig", "pub fn first() void {}\n")
        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        script_path = root / "scripts/zigux/validate-phase1-closure.py"
        script_path.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
        ok = subprocess.run([sys.executable, str(script_path)], cwd=root, env=env, capture_output=True, text=True, check=False)
        if ok.returncode != 0:
            raise SystemExit(f"phase1-self-test:baseline:{ok.stdout or ok.stderr}")

        write(root / "Documentation/zigux/README.md", "# Zigux Documentation\n")
        expect_failure(root, "docs_root:- `Documentation/zigux/phase1-closure.md` remains the dedicated closure packet for the bounded host-side `tools/lib/*.zig` helper tranche, and `zigux/tests/fixtures/phase1_helper_manifest.json` plus `zigux/tests/phase1_helpers.zig` keep the closed helper inventory and parity-backed replay surface explicit from the docs root.")
        write(root / "Documentation/zigux/README.md", "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")

        write(
            root / "Documentation/zigux/README.md",
            "\n".join(REQUIRED_DOCS_ROOT_MARKERS + [REQUIRED_DOCS_ROOT_MARKERS[0]]) + "\n",
        )
        expect_failure(root, "docs_root_phase1_closure_packet_count:expected=1:actual=2")
        write(root / "Documentation/zigux/README.md", "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")

        write(root / "scripts/zigux/README.md", "# scripts/zigux\n")
        expect_failure(root, "scripts_root:- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.")
        write(root / "scripts/zigux/README.md", "\n".join(REQUIRED_SCRIPTS_ROOT_MARKERS) + "\n")

        write(
            root / "scripts/zigux/README.md",
            "\n".join(REQUIRED_SCRIPTS_ROOT_MARKERS + [REQUIRED_SCRIPTS_ROOT_MARKERS[1]]) + "\n",
        )
        expect_failure(root, "scripts_root_phase1_review_hooks_count:expected=1:actual=2")
        write(root / "scripts/zigux/README.md", "\n".join(REQUIRED_SCRIPTS_ROOT_MARKERS) + "\n")

        write(root / "scripts/zigux/check-phase1-bench.py", "print('PHASE1_BENCH_SELF_TEST=pass')\n")
        expect_failure(root, "bench_checker:print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=19')")
        write(root / "scripts/zigux/check-phase1-bench.py", "\n".join(REQUIRED_BENCH_CHECKER_MARKERS) + "\n")

        write(root / "zigux/Makefile", "phase1-validate:\n")
        expect_failure(root, "makefile:PHONY += phase1-validate phase1-test phase1-bench phase1")
        write(root / "zigux/Makefile", render_fixture_lines(REQUIRED_MAKEFILE_MARKERS, MAKEFILE_EXACT_COUNT_PREFIXES))

        (root / "scripts/zigux/check-phase1-bitmap-validator-anchors.py").unlink()
        expect_failure(root, "file:scripts/zigux/check-phase1-bitmap-validator-anchors.py")
        write(root / "scripts/zigux/check-phase1-bitmap-validator-anchors.py", "# fixture\n")

        write(
            root / ".github/workflows/zigux-bootstrap.yml",
            render_fixture_lines(
                REQUIRED_WORKFLOW_MARKERS + ["run: python3 scripts/zigux/validate-phase1.py"],
                WORKFLOW_EXACT_COUNT_PREFIXES,
            ),
        )
        expect_failure(root, "workflow_phase1_validate_count:expected=1:actual=2")
        write(root / ".github/workflows/zigux-bootstrap.yml", render_fixture_lines(REQUIRED_WORKFLOW_MARKERS, WORKFLOW_EXACT_COUNT_PREFIXES))

        write(root / "zigux/tests/phase1_helpers.zig", "// fixture\n")
        expect_failure(root, 'helper_tests:const argv_split = @import("argv_split");')
        write(root / "zigux/tests/phase1_helpers.zig", "\n".join(REQUIRED_HELPER_TEST_MARKERS) + "\n")

        write(
            root / "zigux/Makefile",
            render_fixture_lines(
                REQUIRED_MAKEFILE_MARKERS + ["cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py --self-test"],
                MAKEFILE_EXACT_COUNT_PREFIXES,
            ),
        )
        expect_failure(root, "makefile_phase1_closure_self_test_count:expected=1:actual=2")
        write(root / "zigux/Makefile", render_fixture_lines(REQUIRED_MAKEFILE_MARKERS, MAKEFILE_EXACT_COUNT_PREFIXES))

        write(
            root / ".github/workflows/zigux-bootstrap.yml",
            render_fixture_lines(
                REQUIRED_WORKFLOW_MARKERS + ["run: python3 scripts/zigux/check-phase1-bench.py"],
                WORKFLOW_EXACT_COUNT_PREFIXES,
            ),
        )
        expect_failure(root, "workflow_phase1_bench_count:expected=1:actual=2")
        write(root / ".github/workflows/zigux-bootstrap.yml", render_fixture_lines(REQUIRED_WORKFLOW_MARKERS, WORKFLOW_EXACT_COUNT_PREFIXES))

        write(
            root / "Documentation/zigux/phase1-closure.md",
            "\n".join(marker for marker in REQUIRED_CLOSURE_MARKERS if not marker.startswith("PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=")) + "\n",
        )
        expect_failure(root, "closure:PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the last in-range bit reachable from an inclusive start while later starts still return nbits instead of leaking the out-of-range tail")
        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")

        write(
            root / "Documentation/zigux/phase1-closure.md",
            "\n".join(marker for marker in REQUIRED_CLOSURE_MARKERS if not marker.startswith("PHASE1_FIND_BIT_TAIL_WORD_BOUNDARY_UNIT_REVIEW=")) + "\n",
        )
        expect_failure(root, "closure:PHASE1_FIND_BIT_TAIL_WORD_BOUNDARY_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the first in-range tail-word match reachable when the search starts exactly at the tail-word boundary instead of rereading an earlier full-word result")
        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")

        write(
            root / "Documentation/zigux/phase1-closure.md",
            "\n".join(marker for marker in REQUIRED_CLOSURE_MARKERS if not marker.startswith("PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=")) + "\n",
        )
        expect_failure(root, "closure:PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit scans return 0 even when backing words are populated so declared nbits stays authoritative over caller storage")
        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")

        write(
            root / "Documentation/zigux/phase1-closure.md",
            "\n".join(marker for marker in REQUIRED_CLOSURE_MARKERS if not marker.startswith("PHASE1_RBTREE_ALIAS_GAP_NOTE=")) + "\n",
        )
        expect_failure(root, "closure:PHASE1_RBTREE_ALIAS_GAP_NOTE=the closed Phase 1 rbtree tranche still excludes Linux-style rb_* alias parity for the already-ported entry points, and that remaining surface stays explicitly out of scope until a later bounded repair lands")
        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")

        write(
            root / "Documentation/zigux/phase1-closure.md",
            "\n".join(marker for marker in REQUIRED_CLOSURE_MARKERS if not marker.startswith("PHASE1_RBTREE_ALIAS_GAP_GATE=")) + "\n",
        )
        expect_failure(root, "closure:PHASE1_RBTREE_ALIAS_GAP_GATE=phase1 closure validation fails closed if tools/lib/rbtree.zig grows Linux-style rb_* aliases before the closed helper tranche is deliberately reopened")
        write(root / "Documentation/zigux/phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/bitmap.zig"]["unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/bitmap.zig:unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/bitmap.zig"]["copy_alias_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/bitmap.zig:copy_alias_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/find_bit.zig"]["tail_start_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/find_bit.zig:tail_start_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/find_bit.zig"]["tail_word_boundary_unit_test_anchor"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/find_bit.zig:tail_word_boundary_unit_test_anchor")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/find_bit.zig"]["zero_sized_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/find_bit.zig:zero_sized_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/string.zig"]["memparse_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/string.zig:memparse_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["shared_parity_scope_note"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/rbtree.zig:shared_parity_scope_note")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["alias_gap_note"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/rbtree.zig:alias_gap_note")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["postorder_iterator_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/rbtree.zig:postorder_iterator_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["postorder_safe_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/rbtree.zig:postorder_safe_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helper_review_notes"]["tools/lib/rbtree.zig"]["postorder_safe_rebalance_unit_test_contract"] = "drift"
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:tools/lib/rbtree.zig:postorder_safe_rebalance_unit_test_contract")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        manifest = fixture_manifest()
        manifest["helpers"] = REQUIRED_HELPERS[:-1]
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "manifest:helpers")
        write(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(fixture_manifest(), indent=2) + "\n")

        expectations = fixture_expectations()
        expectations["exact_checksums"]["PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM"] = 1
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(expectations, indent=2) + "\n")
        expect_failure(root, "bench:exact_checksums.PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM=437855789")
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(fixture_expectations(), indent=2) + "\n")

        expectations = fixture_expectations()
        expectations["iterations"]["PHASE1_BENCH_RBTREE_ITERATIONS"] = 1
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(expectations, indent=2) + "\n")
        expect_failure(root, "bench:iterations.PHASE1_BENCH_RBTREE_ITERATIONS=4000")
        write(root / "zigux/tests/fixtures/phase1_bench_expectations.json", json.dumps(fixture_expectations(), indent=2) + "\n")

        write(root / "tools/lib/rbtree.zig", "pub fn rb_first() void {}\n")
        expect_failure(root, "rbtree_source:unexpected_alias:pub fn rb_first(")

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=32")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())

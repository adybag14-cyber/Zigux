#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
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

WORKFLOW_INSTALL_ZIG_RE = re.compile(
    r"python3 scripts/zigux/install-zig\.py --channel \S+ --dest \.zig-toolchain"
)

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
    "zigux/tests/phase1_bench.zig",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
]

REQUIRED_CLOSURE_MARKERS = [
    ("closure_status_count", "PHASE1_STATUS=closed", 1),
    ("closure_helper_count_count", "PHASE1_HELPER_COUNT=13", 1),
    ("closure_manifest_line_count", "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`", 1),
    ("closure_parity_gate_count", "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py", 1),
    ("closure_unit_gate_count", "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig", 1),
    ("closure_bench_gate_count", "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig", 1),
    ("closure_bench_check_gate_count", "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py", 1),
    ("closure_closure_gate_count", "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py", 1),
    ("closure_rollback_count", "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring", 1),
    ("closure_shared_review_workflow_count", "- `.github/workflows/zigux-bootstrap.yml`", 1),
    (
        "closure_find_bit_single_word_review_count",
        "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior",
        1,
    ),
    (
        "closure_find_bit_inclusive_boundary_review_count",
        "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
        1,
    ),
    (
        "closure_find_bit_inclusive_boundary_owner_count",
        "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay now consumes the committed inclusive_boundary_* fixture fields directly, while the direct helper-local inclusive-boundary test remains a review-visible same-word anchor for that path",
        1,
    ),
    (
        "closure_find_bit_zero_window_review_count",
        "PHASE1_FIND_BIT_ZERO_WINDOW_REVIEW=helper-local zero-bit-window proof stays explicit through the direct find_bit test anchor so first-scan entrypoints return the empty-window boundary without reading bitmap words",
        1,
    ),
    (
        "closure_find_bit_past_nbits_review_count",
        "PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window",
        1,
    ),
    (
        "closure_find_bit_tail_clamp_review_count",
        "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits",
        1,
    ),
    (
        "closure_find_bit_underscore_alias_review_count",
        "PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers",
        1,
    ),
    (
        "closure_bitmap_partial_xor_review_count",
        "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
        1,
    ),
    (
        "closure_bitmap_first_word_boundary_review_count",
        "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
        1,
    ),
    (
        "closure_bitmap_scnprintf_truncation_review_count",
        "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
        1,
    ),
    (
        "closure_bitmap_scnprintf_tiny_buffer_review_count",
        "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
        1,
    ),
    (
        "closure_bitmap_copy_alias_review_count",
        "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
        1,
    ),
    (
        "closure_bitmap_raw_copy_alias_review_count",
        "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
        1,
    ),
    (
        "closure_bitmap_zero_bit_noop_review_count",
        "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes",
        1,
    ),
    (
        "closure_rbtree_review_packet_count",
        "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while cached-root behavior keeps direct review anchors without implying a broader cached-root fixture packet than current master ships",
        1,
    ),
    (
        "closure_string_memparse_review_count",
        "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation",
        1,
    ),
    (
        "closure_string_review_packet_count",
        "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys",
        1,
    ),
]

REQUIRED_WORKFLOW_MARKERS = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "python3 scripts/zigux/check-zig-toolchain.py",
    "python3 scripts/zigux/validate-phase1-closure.py",
    "python3 scripts/zigux/check-phase1-bench.py",
    "zig build bench --build-file zigux/tests/build.zig",
]

REQUIRED_EXACT_WORKFLOW_MARKERS = [
    ("workflow_node24_count", "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true", 1),
    ("workflow_checkout_count", "uses: actions/checkout@v6.0.2", 1),
    ("workflow_setup_python_count", "uses: actions/setup-python@v6.2.0", 1),
    ("workflow_toolchain_check_count", "run: python3 scripts/zigux/check-zig-toolchain.py", 1),
    ("workflow_install_zig_count", "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain", 1),
]

REQUIRED_PHASE1_WORKFLOW_MARKERS = [
    ("workflow_phase1_validate_count", "run: python3 scripts/zigux/validate-phase1.py", 1),
    ("workflow_phase1_closure_count", "run: python3 scripts/zigux/validate-phase1-closure.py", 1),
    ("workflow_phase1_parity_count", "run: python3 scripts/zigux/check-phase1-parity.py", 1),
    ("workflow_phase1_bench_count", "run: python3 scripts/zigux/check-phase1-bench.py", 1),
    ("workflow_phase1_unit_replay_count", "run: zig build test --build-file zigux/tests/build.zig", 1),
    ("workflow_phase1_bench_replay_count", "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe", 1),
]

REQUIRED_BUILD_MARKERS = [
    ("build_phase1_bench_source_count", "phase1_bench.zig", 1),
    ("build_phase1_bench_step_count", 'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");', 1),
]

REQUIRED_LEDGER_MARKERS = [
    ("ledger_phase1_closure_commit_count", "docs(zigux): close bounded phase-1 helper tranche", 1),
]

REQUIRED_MAKEFILE_MARKERS = [
    ("makefile_phase1_validate_target", "phase1-validate:", 1),
    ("makefile_phase1_validate_inventory", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py", 1),
    ("makefile_phase1_validate_closure", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py", 1),
    ("makefile_phase1_test_target", "phase1-test:", 1),
    ("makefile_phase1_test_parity", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py", 1),
    ("makefile_phase1_test_replay", "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig", 1),
    ("makefile_phase1_bench_target", "phase1-bench:", 1),
    ("makefile_phase1_bench_check", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py", 1),
    ("makefile_phase1_bench_replay", "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig", 1),
    ("makefile_phase1_target", "phase1: phase1-validate phase1-test phase1-bench", 1),
]

REQUIRED_DOCS_ROOT_MARKERS = [
    (
        "docs_root_phase1_packet",
        "- `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, installer-backed workflow-viability replay, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
        1,
    ),
]

REQUIRED_SCRIPTS_README_MARKERS = [
    (
        "scripts_readme_phase1_packet",
        "- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep that same closed host-side helper packet reviewable through the docs-root closure record, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.",
        1,
    ),
]

REQUIRED_TESTS_README_MARKERS = [
    (
        "tests_readme_phase1_packet",
        "  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
        1,
    ),
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    (
        "review_checklist_phase1_packet",
        "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
        1,
    ),
]

EXPECTED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "helper_test_anchors": [
            'test "bitmap allocator helpers size zero and free their buffers"',
            'test "bitmap set clear weight and empty full helpers"',
            'test "bitmap fill clamps tail bits in partial words"',
            'test "bitmap and andnot equal intersects subset"',
            'test "bitmap and andnot clamp tail bits in partial words"',
            'test "bitmap xor keeps caller-selected bit window"',
            'test "bitmap scnprintf collapses contiguous ranges"',
            'test "bitmap scnprintf reports full length while truncating the buffer"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
        ],
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
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
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
    },
    "tools/lib/find_bit.zig": {
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
        "tail_clamp_fixture_keys": [
            "tail_clamped_first",
            "tail_clamped_next",
            "tail_zero_clamped_first",
            "tail_zero_clamped_next",
            "tail_and_clamped_first",
            "tail_and_clamped_next",
        ],
    },
    "tools/lib/rbtree.zig": {
        "helper_test_anchors": [
            'test "rbtree inserts and traverses in sorted order"',
            'test "rbtree erase and replace keep traversal consistent"',
            'test "rbtree eraseInit detaches erased node"',
            'test "rbtree postorder and empty node helpers behave"',
            'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
            'test "rbtree nextMatch walks the duplicate range in order"',
            'test "rbtree addCached returns the inserted node only when it becomes leftmost"',
            'test "rbtree cached root keeps the leftmost pointer in sync"',
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
            'test "memdup and memchrInv preserve byte content"',
            'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
            'test "memparse handles decimal hexadecimal octal and suffixes"',
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
        ],
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
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


def repo_root_from_arg(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def load_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def load_json_file(path: Path, label: str) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]


def collect_exact_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    missing: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return missing


def collect_exact_line_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    actual_counts: dict[str, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        actual_counts[line] = actual_counts.get(line, 0) + 1

    missing: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = actual_counts.get(marker, 0)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return missing


def extract_workflow_job(text: str, job_name: str) -> str:
    pattern = re.compile(
        rf"(?ms)^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)"
    )
    match = pattern.search(text)
    return "" if match is None else match.group(0)


def collect_workflow_markers(text: str) -> list[str]:
    missing: list[str] = []
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in text:
            missing.append(f"workflow:{marker}")
    if WORKFLOW_INSTALL_ZIG_RE.search(text) is None:
        missing.append("workflow:python3 scripts/zigux/install-zig.py --channel <explicit> --dest .zig-toolchain")
    if "mlugg/setup-zig@" in text:
        missing.append("workflow:remove mlugg/setup-zig@")
    return missing


def collect_manifest_review_anchor_markers(manifest: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors=dict"]

    expected_helpers = set(EXPECTED_REVIEW_ANCHORS)
    actual_helpers = set(review_anchors)
    for helper in sorted(expected_helpers - actual_helpers):
        missing.append(f"manifest:missing_review_anchor_helper={helper}")
    for helper in sorted(actual_helpers - expected_helpers):
        missing.append(f"manifest:unexpected_review_anchor_helper={helper}")

    for helper, expected_fields in EXPECTED_REVIEW_ANCHORS.items():
        helper_review = review_anchors.get(helper)
        if not isinstance(helper_review, dict):
            missing.append(f"manifest:review_anchor_object={helper}")
            continue
        expected_keys = set(expected_fields)
        actual_keys = set(helper_review)
        for key in sorted(expected_keys - actual_keys):
            missing.append(f"manifest:missing_review_anchor_field={helper}:{key}")
        for key in sorted(actual_keys - expected_keys):
            missing.append(f"manifest:unexpected_review_anchor_field={helper}:{key}")

        for key, expected_value in expected_fields.items():
            if key not in helper_review:
                continue
            if helper_review[key] != expected_value:
                missing.append(f"manifest:review_anchor_value={helper}:{key}")
    return missing


def collect_manifest_markers(manifest: object, root: Path) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest:json_object"]

    missing: list[str] = []
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        return ["manifest:helpers=list"]

    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing.append("manifest:status=closed")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        missing.append(f"manifest:helper_count={len(EXPECTED_HELPERS)}")
    if len(helpers) != len(EXPECTED_HELPERS):
        missing.append(f"manifest:helpers_len={len(EXPECTED_HELPERS)}")

    seen: set[str] = set()
    duplicates: set[str] = set()
    string_helpers: list[str] = []
    for rel in helpers:
        if not isinstance(rel, str):
            missing.append("manifest:helper_path_type=str")
            continue
        string_helpers.append(rel)
        if rel in seen:
            duplicates.add(rel)
        seen.add(rel)
        if not (root / rel).exists():
            missing.append(f"manifest_file:{rel}")

    expected = set(EXPECTED_HELPERS)
    actual = set(string_helpers)
    for rel in sorted(expected - actual):
        missing.append(f"manifest:missing_helper={rel}")
    for rel in sorted(actual - expected):
        missing.append(f"manifest:unexpected_helper={rel}")
    for rel in sorted(duplicates):
        missing.append(f"manifest:duplicate_helper={rel}")
    missing.extend(collect_manifest_review_anchor_markers(manifest))
    return missing


def collect_bench_expectation_markers(expectations: object) -> list[str]:
    if not isinstance(expectations, dict):
        return ["bench_expectations:json_object"]

    missing: list[str] = []
    if expectations.get("status") != "pass":
        missing.append("bench_expectations:status=pass")

    iterations = expectations.get("iterations")
    if not isinstance(iterations, dict):
        missing.append("bench_expectations:iterations=dict")
    else:
        actual_keys: set[str] = set()
        for key, value in iterations.items():
            if not isinstance(key, str):
                missing.append("bench_expectations:iteration_key_type=str")
                continue
            actual_keys.add(key)
            expected_value = EXPECTED_BENCH_ITERATIONS.get(key)
            if expected_value is None:
                missing.append(f"bench_expectations:unexpected_iteration={key}")
            elif value != expected_value:
                missing.append(f"bench_expectations:iteration_value={key}:{expected_value}")
        for key in sorted(set(EXPECTED_BENCH_ITERATIONS) - actual_keys):
            missing.append(f"bench_expectations:missing_iteration={key}")

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        missing.append("bench_expectations:checksums=list")
    else:
        actual: list[str] = []
        seen: set[str] = set()
        duplicates: set[str] = set()
        for item in checksums:
            if not isinstance(item, str):
                missing.append("bench_expectations:checksum_type=str")
                continue
            actual.append(item)
            if item in seen:
                duplicates.add(item)
            seen.add(item)
        for item in sorted(duplicates):
            missing.append(f"bench_expectations:duplicate_checksum={item}")
        expected = set(EXPECTED_BENCH_CHECKSUMS)
        actual_set = set(actual)
        for item in sorted(expected - actual_set):
            missing.append(f"bench_expectations:missing_checksum={item}")
        for item in sorted(actual_set - expected):
            missing.append(f"bench_expectations:unexpected_checksum={item}")
    return missing


def count_manifest_review_anchor_expectations() -> int:
    return 1 + len(EXPECTED_REVIEW_ANCHORS) + sum(
        len(fields) for fields in EXPECTED_REVIEW_ANCHORS.values()
    )


def count_manifest_metadata_expectations() -> int:
    return 4 + len(EXPECTED_HELPERS)


def count_bench_expectation_expectations() -> int:
    return 1 + len(EXPECTED_BENCH_ITERATIONS) + len(EXPECTED_BENCH_CHECKSUMS)


def render_marker_fixture(markers: list[tuple[str, str, int]]) -> str:
    return "\n".join(marker for _, marker, _ in markers) + "\n"


def make_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES + EXPECTED_HELPERS:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")

    (tmp_root / "Documentation/zigux/phase1-closure.md").write_text(
        render_marker_fixture(REQUIRED_CLOSURE_MARKERS),
        encoding="utf-8",
    )
    bootstrap_lines = [item[1] for item in REQUIRED_EXACT_WORKFLOW_MARKERS[1:]] + [
        item[1] for item in REQUIRED_PHASE1_WORKFLOW_MARKERS
    ]
    workflow_text = "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\njobs:\n  bootstrap:\n" + "".join(
        f"    {line}\n" for line in bootstrap_lines
    )
    (tmp_root / ".github/workflows/zigux-bootstrap.yml").write_text(workflow_text, encoding="utf-8")
    (tmp_root / "zigux/tests/build.zig").write_text(render_marker_fixture(REQUIRED_BUILD_MARKERS), encoding="utf-8")
    (tmp_root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").write_text(render_marker_fixture(REQUIRED_LEDGER_MARKERS), encoding="utf-8")
    (tmp_root / "zigux/Makefile").write_text(render_marker_fixture(REQUIRED_MAKEFILE_MARKERS), encoding="utf-8")
    (tmp_root / "Documentation/zigux/README.md").write_text(render_marker_fixture(REQUIRED_DOCS_ROOT_MARKERS), encoding="utf-8")
    (tmp_root / "scripts/zigux/README.md").write_text(render_marker_fixture(REQUIRED_SCRIPTS_README_MARKERS), encoding="utf-8")
    (tmp_root / "zigux/tests/README.md").write_text(render_marker_fixture(REQUIRED_TESTS_README_MARKERS), encoding="utf-8")
    (tmp_root / "Documentation/zigux/review-checklist.md").write_text(render_marker_fixture(REQUIRED_REVIEW_CHECKLIST_MARKERS), encoding="utf-8")

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "review_anchors": EXPECTED_REVIEW_ANCHORS,
    }
    (tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    bench = {
        "status": "pass",
        "iterations": dict(EXPECTED_BENCH_ITERATIONS),
        "checksums": list(EXPECTED_BENCH_CHECKSUMS),
    }
    (tmp_root / "zigux/tests/fixtures/phase1_bench_expectations.json").write_text(
        json.dumps(bench, indent=2) + "\n",
        encoding="utf-8",
    )


def collect_missing_markers(root: Path) -> list[str]:
    closure = load_text(root, "Documentation/zigux/phase1-closure.md")
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
    tests_build = load_text(root, "zigux/tests/build.zig")
    ledger = load_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    makefile = load_text(root, "zigux/Makefile")
    docs_root = load_text(root, "Documentation/zigux/README.md")
    scripts_readme = load_text(root, "scripts/zigux/README.md")
    tests_readme = load_text(root, "zigux/tests/README.md")
    review_checklist = load_text(root, "Documentation/zigux/review-checklist.md")
    manifest, manifest_parse_markers = load_json_file(root / "zigux/tests/fixtures/phase1_helper_manifest.json", "manifest")
    bench_expectations, bench_parse_markers = load_json_file(
        root / "zigux/tests/fixtures/phase1_bench_expectations.json",
        "bench_expectations",
    )
    bootstrap_workflow = extract_workflow_job(workflow, "bootstrap")

    missing = collect_workflow_markers(workflow)
    missing.extend(manifest_parse_markers)
    missing.extend(bench_parse_markers)
    missing.extend(collect_exact_line_count_markers(workflow, [REQUIRED_EXACT_WORKFLOW_MARKERS[0]]))
    missing.extend(collect_exact_line_count_markers(bootstrap_workflow, REQUIRED_EXACT_WORKFLOW_MARKERS[1:]))
    missing.extend(collect_exact_count_markers(closure, REQUIRED_CLOSURE_MARKERS))
    missing.extend(collect_exact_count_markers(tests_build, REQUIRED_BUILD_MARKERS))
    missing.extend(collect_exact_count_markers(ledger, REQUIRED_LEDGER_MARKERS))
    missing.extend(collect_exact_line_count_markers(bootstrap_workflow, REQUIRED_PHASE1_WORKFLOW_MARKERS))
    missing.extend(collect_exact_count_markers(makefile, REQUIRED_MAKEFILE_MARKERS))
    missing.extend(collect_exact_count_markers(docs_root, REQUIRED_DOCS_ROOT_MARKERS))
    missing.extend(collect_exact_count_markers(scripts_readme, REQUIRED_SCRIPTS_README_MARKERS))
    missing.extend(collect_exact_count_markers(tests_readme, REQUIRED_TESTS_README_MARKERS))
    missing.extend(collect_exact_count_markers(review_checklist, REQUIRED_REVIEW_CHECKLIST_MARKERS))
    if manifest is not None:
        missing.extend(collect_manifest_markers(manifest, root))
    if bench_expectations is not None:
        missing.extend(collect_bench_expectation_markers(bench_expectations))
    return missing


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)
        assert collect_missing_files(tmp_root) == []
        assert collect_missing_markers(tmp_root) == []

        closure_path = tmp_root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8")

        for label, marker, _ in [
            REQUIRED_CLOSURE_MARKERS[12],
            REQUIRED_CLOSURE_MARKERS[13],
            REQUIRED_CLOSURE_MARKERS[14],
            REQUIRED_CLOSURE_MARKERS[17],
            REQUIRED_CLOSURE_MARKERS[19],
            REQUIRED_CLOSURE_MARKERS[23],
        ]:
            closure_path.write_text(closure_text.replace(marker + "\n", "", 1), encoding="utf-8")
            missing = collect_missing_markers(tmp_root)
            assert f"{label}:expected=1:actual=0" in missing
            closure_path.write_text(closure_text, encoding="utf-8")

        manifest_path = tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["helpers"] = manifest["helpers"][:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "manifest:helpers_len=13" in missing
        make_fixture_root(tmp_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/bitmap.zig"]["first_word_boundary_anchor"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "manifest:missing_review_anchor_field=tools/lib/bitmap.zig:first_word_boundary_anchor" in missing
        make_fixture_root(tmp_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/find_bit.zig"]["zero_bit_window"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:zero_bit_window" in missing
        make_fixture_root(tmp_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/find_bit.zig"]["underscore_alias_anchor"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "manifest:missing_review_anchor_field=tools/lib/find_bit.zig:underscore_alias_anchor" in missing
        make_fixture_root(tmp_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/string.zig"]["shared_replace_char_cstr_review_summary"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "manifest:missing_review_anchor_field=tools/lib/string.zig:shared_replace_char_cstr_review_summary" in missing
        make_fixture_root(tmp_root)

        bench_path = tmp_root / "zigux/tests/fixtures/phase1_bench_expectations.json"
        bench = json.loads(bench_path.read_text(encoding="utf-8"))
        del bench["iterations"]["PHASE1_BENCH_STRING_ITERATIONS"]
        bench_path.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "bench_expectations:missing_iteration=PHASE1_BENCH_STRING_ITERATIONS" in missing
        make_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8").replace(
            "run: python3 scripts/zigux/check-phase1-bench.py\n",
            "",
            1,
        )
        workflow_path.write_text(workflow_text, encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "workflow_phase1_bench_count:expected=1:actual=0" in missing
        make_fixture_root(tmp_root)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8").replace(
            "phase1: phase1-validate phase1-test phase1-bench\n",
            "",
            1,
        )
        makefile_path.write_text(makefile_text, encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "makefile_phase1_target:expected=1:actual=0" in missing
        make_fixture_root(tmp_root)

        (tmp_root / ".github/workflows/zigux-bootstrap.yml").unlink()
        assert collect_missing_files(tmp_root) == [".github/workflows/zigux-bootstrap.yml"]

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=14")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root instead of the validator script checkout root.")
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
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_EXACT_WORKFLOW_MARKERS) + len(REQUIRED_PHASE1_WORKFLOW_MARKERS) + len(REQUIRED_BUILD_MARKERS) + len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_DOCS_ROOT_MARKERS) + len(REQUIRED_SCRIPTS_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + count_manifest_review_anchor_expectations() + count_manifest_metadata_expectations() + count_bench_expectation_expectations()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

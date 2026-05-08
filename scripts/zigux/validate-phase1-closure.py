#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
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
            'test "bitmap scnprintf reports full length while truncating the buffer"',
            'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
            'test "bitmap copy aliases preserve tail clearing and extension semantics"',
            'test "bitmap copy alias preserves raw source words without tail clearing"',
            'test "bitmap zero-bit helpers stay explicit no-ops"',
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
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
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
            'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
            'test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"',
            'test "rbtree eraseInitCached clears singleton cached roots before reseed"',
        ],
        "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys",
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
    if expectations.get("iterations") != EXPECTED_BENCH_ITERATIONS:
        missing.append("bench:iterations")
    if expectations.get("checksums") != EXPECTED_BENCH_CHECKSUMS:
        missing.append("bench:checksums")
    return missing


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
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


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

        (root / "scripts/zigux/validate-phase1-closure.py").unlink()
        assert collect_missing_files(root) == ["scripts/zigux/validate-phase1-closure.py"]
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

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(CLOSURE_MARKERS) + len(WORKFLOW_MARKERS) + len(BUILD_MARKERS) + len(LEDGER_MARKERS) + len(MAKEFILE_MARKERS) + len(DOCS_ROOT_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + 5 + 3}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

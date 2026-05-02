#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
if SELF_PATH.parent.name == "zigux" and SELF_PATH.parent.parent.name == "scripts":
    ROOT = SELF_PATH.parents[2]
else:
    ROOT = SELF_PATH.parent


REQUIRED_FILE_RELS = [
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("Documentation/zigux/phase1-closure.md"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
    Path("zigux/tests/fixtures/phase1_helpers.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
    Path("zigux/tests/phase1_bench.zig"),
]

HELPERS = [
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

RBTREE_SUMMARY = (
    "Committed C-backed parity coverage includes ordered forward and reverse traversal plus "
    "replaceNode, eraseInit, postorder traversal, and detached-node state checks, while "
    "Linux-style rb_* alias parity remains explicitly out of scope for this closed Phase 1 tranche."
)
RBTREE_ALIAS_GAP_NOTE = (
    "Linux-style rb_* alias surface parity is still missing for the already-ported entry points, "
    "and that remaining surface stays explicitly out of scope for the closed Phase 1 tranche until "
    "a later bounded repair lands."
)
RBTREE_ALIAS_GAP_GATE = (
    "PHASE1_RBTREE_ALIAS_GAP_GATE=phase1 closure validation fails closed if tools/lib/rbtree.zig "
    "grows Linux-style rb_* aliases before the closed helper tranche is deliberately reopened"
)
RBTREE_UNEXPECTED_ALIAS_MARKERS = [
    "pub fn rb_insert_color(",
    "pub fn rb_erase(",
    "pub fn rb_erase_init(",
    "pub fn rb_first(",
    "pub fn rb_last(",
    "pub fn rb_next(",
    "pub fn rb_prev(",
    "pub fn rb_first_postorder(",
    "pub fn rb_next_postorder(",
    "pub fn rb_replace_node(",
    "pub fn rb_first_cached(",
    "pub fn rb_insert_color_cached(",
    "pub fn rb_erase_cached(",
    "pub fn rb_replace_node_cached(",
    "pub fn rb_add_cached(",
    "pub fn rb_add(",
    "pub fn rb_find_add(",
    "pub fn rb_find(",
    "pub fn rb_find_first(",
    "pub fn rb_next_match(",
]

STRING_SUMMARY = (
    "string parity covers Linux-style bool parsing for true, false, and invalid forms, "
    "C-string-aware strlcpy length and truncation behavior, whitespace cleanup including "
    "embedded-NUL remove_spaces handling, replacement, and memchrInv mismatch detection"
)
STRING_CSTRING_REVIEW = (
    "string strlcpy stops at the first embedded NUL, preserves truncation behavior, and leaves "
    "zero-sized destinations untouched"
)
STRING_EQUALITY_REVIEW = (
    "string strEq and streq keep C-string equality aligned for exact, empty, length-mismatched, "
    "case-sensitive, and embedded-NUL comparisons"
)
STRING_ALIAS_REVIEW = (
    "string trimSpaces and strim trim trailing whitespace before the first embedded NUL while "
    "preserving bytes beyond that terminator"
)
STRING_PREFIX_REVIEW = (
    "string strStarts and strstarts keep kernel-style prefix checks aligned for exact, "
    "empty-prefix, shorter-input, and case-sensitive comparisons"
)
STRING_PREFIX_LENGTH_REVIEW = (
    "string strHasPrefix and str_has_prefix return the matched C-string prefix length for exact "
    "and embedded-NUL prefixes while rejecting mismatches and longer prefixes"
)
STRING_SUFFIX_REVIEW = (
    "string strEndsWith, str_ends_with, and strends keep kernel-style suffix semantics aligned "
    "for exact, empty-suffix, shorter-input, and case-sensitive comparisons"
)
STRING_MEMPARSE_REVIEW = (
    "string memparse preserves decimal, hexadecimal, suffix-bearing, and invalid inputs without "
    "changing the parsed value or rest pointer contract"
)

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "PHASE1_BITMAP_ALIAS_UNIT_REVIEW=bitmap underscore alias entry points preserve the same caller-selected window semantics as the camelCase helpers for weight bitwise range and formatting operations",
    "PHASE1_FIND_BIT_ALIAS_UNIT_REVIEW=find_bit underscore alias entry points preserve the same set, shared-bit, and zero-bit scan semantics as the camelCase helpers across the same caller-selected bit windows and tail clamps",
    "PHASE1_FIND_BIT_MASK_UNIT_REVIEW=find_bit mask and sizing helpers keep Linux-style whole-word, partial-word, and wrapped-start boundaries reviewable without relying only on indirect scan coverage",
    "PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range",
    "PHASE1_FIND_BIT_LOW_LEVEL_UNIT_REVIEW=find_bit low-level underscore entry points preserve same-word inclusive starts and tail-clamped set, shared-bit, and zero-bit scan behavior across the same caller-selected bit windows as the public helpers",
    "PHASE1_FIND_BIT_SMALL_BITMAP_UNIT_REVIEW=find_bit single-word set zero and shared-bit scans keep Linux small-bitmap semantics aligned by masking out-of-range tail bits while preserving inclusive in-range matches inside one word",
    "PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the last in-range bit reachable from an inclusive start while later starts still return nbits instead of leaking the out-of-range tail",
    "PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit scans return 0 even when backing words are populated so declared nbits stays authoritative over caller storage",
    "PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state while Linux-style rb_* alias parity remains explicitly out of scope for this closed tranche",
    "PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys",
    "PHASE1_RBTREE_REVERSE_UNIT_REVIEW=rbtree findLast, prevMatch, and iterateMatchesReverse keep reverse duplicate-key lookup walks aligned from the rightmost match back through the equal-key range while still reporting no match for missing keys",
    "PHASE1_RBTREE_ALIAS_GAP_NOTE=the closed Phase 1 rbtree tranche still excludes Linux-style rb_* alias parity for the already-ported entry points, and that remaining surface stays explicitly out of scope until a later bounded repair lands",
    RBTREE_ALIAS_GAP_GATE,
    f"PHASE1_STRING_REVIEW={STRING_SUMMARY}",
    f"PHASE1_STRING_CSTRING_UNIT_REVIEW={STRING_CSTRING_REVIEW}",
    f"PHASE1_STRING_EQUALITY_UNIT_REVIEW={STRING_EQUALITY_REVIEW}",
    f"PHASE1_STRING_ALIAS_UNIT_REVIEW={STRING_ALIAS_REVIEW}",
    f"PHASE1_STRING_PREFIX_UNIT_REVIEW={STRING_PREFIX_REVIEW}",
    f"PHASE1_STRING_PREFIX_LENGTH_UNIT_REVIEW={STRING_PREFIX_LENGTH_REVIEW}",
    f"PHASE1_STRING_SUFFIX_UNIT_REVIEW={STRING_SUFFIX_REVIEW}",
    f"PHASE1_STRING_MEMPARSE_UNIT_REVIEW={STRING_MEMPARSE_REVIEW}",
    "PHASE1_FIND_BIT_BENCH_REVIEW=find_bit benchmark smoke pins deterministic next-bit, whole-family, tail-window, same-word, zero-bit, and shared-bit scan checksums plus the live loop counts so helper-local scan regressions cannot hide behind a generic positive checksum or a silently shrunk workload",
    "PHASE1_FIND_BIT_BENCH_KEYS=PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM,PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM,PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM,PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM",
    "PHASE1_FIND_BIT_BENCH_ITERATIONS=PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS,PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS,PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS,PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS",
    "PHASE1_RBTREE_BENCH_REVIEW=rbtree benchmark smoke pins ordered traversal, duplicate-range, cached-leftmost, findAdd, and postorder-safe checksum surfaces so duplicate-owner and erase-while-walking regressions cannot hide behind the broader tree checksum alone",
    "PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test",
]

REQUIRED_WORKFLOW_MARKERS = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
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
    "const bench = b.addExecutable(.{",
    '.name = "phase1-bench",',
    "const run_bench = b.addRunArtifact(bench);",
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
]

REQUIRED_LEDGER_MARKERS = [
    "15. `docs(zigux): close bounded phase-1 helper tranche`",
    "16. `test(zigux): harden phase-1 closure gates`",
    "17. `ci(zigux): harden phase-1 closure workflow viability`",
    "18. `build(zigux): remove node-20-bound Zig action from phase-1 closure path`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
]

REQUIRED_BENCH_CHECKER_MARKERS = [
    "print('PHASE1_BENCH_SELF_TEST=pass')",
    "print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=15')",
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

REQUIRED_ITERATIONS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS": 20000,
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
    "PHASE1_BENCH_RBTREE_CHECKSUM": 1308000,
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 1188000,
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 196000,
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 3484000,
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 1484000,
}

EXPECTED_MANIFEST_FIELDS = {
    "tools/lib/bitmap.zig": {
        "fixture": "zigux/tests/fixtures/phase1_helpers.json",
        "alias_unit_test_anchor": 'tools/lib/bitmap.zig:test "bitmap underscore aliases preserve bitmap helper semantics"',
        "alias_unit_test_contract": (
            "Direct Zig unit coverage keeps bitmap_weight(), bitmap_and(), bitmap_andnot(), "
            "bitmap_or(), bitmap_xor(), bitmap_equal(), bitmap_intersects(), "
            "bitmap_subset(), bitmap_set(), bitmap_clear(), and bitmap_scnprintf() aligned with the camelCase "
            "helpers across the same caller-selected bit window."
        ),
    },
    "tools/lib/find_bit.zig": {
        "fixture": "zigux/tests/fixtures/phase1_helpers.json",
        "alias_unit_test_anchor": 'tools/lib/find_bit.zig:test "find underscore aliases preserve scan semantics"',
        "alias_unit_test_contract": (
            "Direct Zig unit coverage keeps find_first_bit(), find_first_and_bit(), "
            "find_first_zero_bit(), find_next_bit(), find_next_and_bit(), and "
            "find_next_zero_bit() aligned with the camelCase scan helpers across the same "
            "caller-selected bit windows and tail clamps."
        ),
        "mask_unit_test_anchor": 'tools/lib/find_bit.zig:test "word helpers keep linux-style mask and sizing boundaries"',
        "mask_unit_test_contract": (
            "Direct Zig unit coverage keeps bitsToWords(), firstWordMask(), and lastWordMask() "
            "aligned with Linux-style whole-word, partial-word, and wrapped-start boundaries so "
            "exported mask helpers remain reviewable without relying only on indirect scan coverage."
        ),
        "boundary_unit_test_anchor": 'tools/lib/find_bit.zig:test "empty and boundary scans return nbits"',
        "boundary_unit_test_contract": (
            "Direct Zig unit coverage keeps empty and out-of-range scan boundaries aligned by "
            "returning nbits for zero-length bitmaps, start-at-nbits searches, and fully set "
            "zero-bit windows that must not report past the declared range."
        ),
        "low_level_unit_test_anchor": 'tools/lib/find_bit.zig:test "find low-level underscore entry points preserve same-word and tail-clamped scan semantics"',
        "low_level_unit_test_contract": (
            "Direct Zig unit coverage keeps _find_first_bit(), _find_first_and_bit(), "
            "_find_first_zero_bit(), _find_next_bit(), _find_next_and_bit(), and "
            "_find_next_zero_bit() aligned with the public scan helpers across same-word "
            "inclusive starts and tail-clamped caller-selected bit windows."
        ),
        "small_bitmap_unit_test_anchor": 'tools/lib/find_bit.zig:test "single-word scans keep linux small-bitmap semantics"',
        "small_bitmap_unit_test_contract": (
            "Direct Zig unit coverage keeps single-word set, zero, and shared-bit scans aligned "
            "with Linux small-bitmap semantics by masking out-of-range tail bits while "
            "preserving inclusive in-range matches inside one word."
        ),
        "tail_start_unit_test_anchor": 'tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"',
        "tail_start_unit_test_contract": (
            "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned "
            "when the inclusive start lands on the last in-range bit, while later starts still "
            "return nbits instead of leaking the out-of-range tail."
        ),
        "zero_sized_unit_test_anchor": 'tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"',
        "zero_sized_unit_test_contract": (
            "Direct Zig unit coverage keeps zero-length set, zero, and shared-bit scans aligned by "
            "returning 0 even when backing words are populated, so declared nbits stays "
            "authoritative over caller storage."
        ),
    },
    "tools/lib/rbtree.zig": {
        "fixture": "zigux/tests/fixtures/phase1_helpers.json",
        "summary": RBTREE_SUMMARY,
        "alias_gap_note": RBTREE_ALIAS_GAP_NOTE,
        "iterator_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"',
        "iterator_unit_test_contract": (
            "Direct Zig unit coverage keeps iterateMatches() aligned so duplicate-key iteration "
            "yields only the equal-key range and cleanly reports no match for missing keys."
        ),
        "reverse_unit_test_anchor": 'tools/lib/rbtree.zig:test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"',
        "reverse_unit_test_contract": (
            "Direct Zig unit coverage keeps findLast(), prevMatch(), and iterateMatchesReverse() "
            "aligned so reverse duplicate-key lookups start at the rightmost match, walk back "
            "through the equal-key range, and cleanly report no match for missing keys."
        ),
    },
    "tools/lib/string.zig": {
        "fixture": "zigux/tests/fixtures/phase1_helpers.json",
        "summary": (
            "Committed C-backed parity coverage includes Linux-style bool parsing for true, false, "
            "and invalid forms, C-string-aware strlcpy length and truncation behavior, in-place "
            "whitespace and replacement helpers including embedded-NUL remove_spaces handling, and "
            "first-mismatch memchrInv detection, while direct Zig review anchors now also record "
            "C-string equality, prefix, prefix-length, suffix, and memparse coverage for the "
            "newer helper surface already shipped on master."
        ),
        "unit_test_anchor": 'tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"',
        "unit_test_contract": (
            "Direct Zig unit coverage keeps memchrInv honest for both aligned and misaligned long "
            "buffers beyond the short C-backed fixture cases."
        ),
        "cstring_unit_test_anchor": 'tools/lib/string.zig:test "strlcpy stops at the first embedded NUL in the source"',
        "cstring_unit_test_contract": (
            "Direct Zig unit coverage keeps strlcpy aligned with C-string semantics by stopping at "
            "the first embedded NUL, preserving truncation behavior, and leaving zero-sized "
            "destinations untouched."
        ),
        "equality_unit_test_anchor": 'tools/lib/string.zig:test "streq matches C-string equality semantics"',
        "equality_unit_test_contract": (
            "Direct Zig unit coverage keeps strEq() and streq() aligned with C-string equality "
            "semantics for exact, empty, length-mismatched, case-sensitive, and embedded-NUL "
            "comparisons."
        ),
        "alias_unit_test_anchor": 'tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"',
        "alias_unit_test_contract": (
            "Direct Zig unit coverage keeps trimSpaces and strim aligned with C-string semantics "
            "by trimming trailing whitespace that appears before the first embedded NUL while "
            "preserving bytes beyond that terminator."
        ),
        "prefix_unit_test_anchor": 'tools/lib/string.zig:test "strstarts matches kernel prefix semantics"',
        "prefix_unit_test_contract": (
            "Direct Zig unit coverage keeps strStarts and strstarts aligned with kernel-style "
            "prefix semantics for exact, empty-prefix, shorter-input, and case-sensitive "
            "comparisons."
        ),
        "prefix_length_unit_test_anchor": 'tools/lib/string.zig:test "strHasPrefix returns the matched prefix length with C-string semantics"',
        "prefix_length_unit_test_contract": (
            "Direct Zig unit coverage keeps strHasPrefix and str_has_prefix aligned by returning "
            "the matched C-string prefix length for exact and embedded-NUL prefixes while "
            "rejecting mismatches and longer prefixes."
        ),
        "suffix_unit_test_anchor": 'tools/lib/string.zig:test "str_ends_with matches kernel suffix semantics"',
        "suffix_unit_test_contract": (
            "Direct Zig unit coverage keeps strEndsWith, str_ends_with, and strends aligned with "
            "kernel-style suffix semantics for exact, empty-suffix, shorter-input, and "
            "case-sensitive comparisons."
        ),
        "memparse_unit_test_anchor": 'tools/lib/string.zig:test "memparse forwards the header-level string helper surface"',
        "memparse_unit_test_contract": (
            "Direct Zig unit coverage keeps memparse aligned by forwarding decimal, hexadecimal, "
            "suffix-bearing, and invalid inputs through the shared command-line parser without "
            "changing the parsed value or rest pointer contract."
        ),
    },
}


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "zigux" / "validate-phase1-closure.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase1-self-test:{label}:unexpected_pass")
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "none"
        raise SystemExit(
            f"phase1-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2) + "\n")


def build_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": HELPERS,
        "helper_review_notes": copy.deepcopy(EXPECTED_MANIFEST_FIELDS),
    }


def build_expectations() -> dict[str, object]:
    return {
        "status": "pass",
        "iterations": {
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
        },
        "exact_checksums": REQUIRED_EXACT_CHECKSUMS,
        "checksums": [
            "PHASE1_BENCH_HWEIGHT_CHECKSUM",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM",
        ],
    }


def create_fixture_root(root: Path) -> None:
    write_text(root / "Documentation" / "zigux" / "phase1-closure.md", "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(root / ".github" / "workflows" / "zigux-bootstrap.yml", "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")
    write_text(root / "zigux" / "tests" / "build.zig", "\n".join(REQUIRED_BUILD_MARKERS) + "\n")
    write_text(root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md", "\n".join(REQUIRED_LEDGER_MARKERS) + "\n")
    write_text(root / "scripts" / "zigux" / "check-phase1-bench.py", "\n".join(REQUIRED_BENCH_CHECKER_MARKERS) + "\n")
    write_text(root / "scripts" / "zigux" / "check-phase1-parity.py", "\n".join(REQUIRED_PARITY_CHECKER_MARKERS) + "\n")
    write_text(root / "scripts" / "zigux" / "artifact_diff.py", "# fixture\n")
    write_text(root / "scripts" / "zigux" / "install-zig.py", "# fixture\n")
    write_text(root / "zigux" / "tests" / "phase1_bench.zig", "// fixture\n")
    write_text(root / "zigux" / "tests" / "fixtures" / "phase1_helpers.json", "{}\n")
    write_text(root / "zigux" / "tests" / "fixtures" / "phase1_helpers_c_harness.c", "/* fixture */\n")
    write_json(root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json", build_manifest())
    write_json(root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json", build_expectations())
    shutil.copyfile(Path(__file__), root / "scripts" / "zigux" / "validate-phase1-closure.py")
    for helper in HELPERS:
        content = "// helper fixture\n"
        if helper == "tools/lib/rbtree.zig":
            content = "pub fn first(root: *const Root) ?*Node { _ = root; return null; }\n"
        write_text(root / helper, content)


def validate_text(label: str, text: str, markers: list[str], missing: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate_manifest(root: Path, manifest: dict[str, object], missing: list[str]) -> None:
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing.append("manifest:status=closed")
    if manifest.get("helper_count") != 13:
        missing.append("manifest:helper_count=13")
    helpers = manifest.get("helpers")
    if helpers != HELPERS:
        missing.append("manifest:helpers")
    else:
        for rel in helpers:
            if not (root / rel).exists():
                missing.append(f"manifest_file:{rel}")

    review = manifest.get("helper_review_notes", {})
    for helper, expected_fields in EXPECTED_MANIFEST_FIELDS.items():
        actual_fields = review.get(helper, {})
        for key, expected_value in expected_fields.items():
            if actual_fields.get(key) != expected_value:
                missing.append(f"manifest:{helper}:{key}")


def validate_expectations(expectations: dict[str, object], missing: list[str]) -> None:
    if expectations.get("status") != "pass":
        missing.append("bench:status=pass")
    iterations = expectations.get("iterations", {})
    exact = expectations.get("exact_checksums", {})
    checksums = expectations.get("checksums", [])
    for key, expected in REQUIRED_ITERATIONS.items():
        if iterations.get(key) != expected:
            missing.append(f"bench:iterations.{key}={expected}")
    for key, expected in REQUIRED_EXACT_CHECKSUMS.items():
        if exact.get(key) != expected:
            missing.append(f"bench:exact_checksums.{key}={expected}")
        if key in checksums:
            missing.append(f"bench:remove_loose_exact_checksum:{key}")


def validate_rbtree_alias_gap_source(root: Path, missing: list[str]) -> None:
    rbtree_source = (root / "tools" / "lib" / "rbtree.zig").read_text(encoding="utf-8")
    for marker in RBTREE_UNEXPECTED_ALIAS_MARKERS:
        if marker in rbtree_source:
            missing.append(f"rbtree_source:unexpected_alias:{marker}")


def validate_tree(root: Path) -> tuple[int, list[str]]:
    missing_files = [str(rel) for rel in REQUIRED_FILE_RELS if not (root / rel).exists()]
    if missing_files:
        return 1, [f"file:{item}" for item in missing_files]

    closure = (root / "Documentation" / "zigux" / "phase1-closure.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    build = (root / "zigux" / "tests" / "build.zig").read_text(encoding="utf-8")
    ledger = (root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md").read_text(encoding="utf-8")
    bench_checker = (root / "scripts" / "zigux" / "check-phase1-bench.py").read_text(encoding="utf-8")
    parity_checker = (root / "scripts" / "zigux" / "check-phase1-parity.py").read_text(encoding="utf-8")
    manifest = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json").read_text(encoding="utf-8"))
    expectations = json.loads((root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json").read_text(encoding="utf-8"))

    missing: list[str] = []
    validate_text("closure", closure, REQUIRED_CLOSURE_MARKERS, missing)
    validate_text("workflow", workflow, REQUIRED_WORKFLOW_MARKERS, missing)
    validate_text("build", build, REQUIRED_BUILD_MARKERS, missing)
    validate_text("ledger", ledger, REQUIRED_LEDGER_MARKERS, missing)
    validate_text("bench_checker", bench_checker, REQUIRED_BENCH_CHECKER_MARKERS, missing)
    validate_text("parity_checker", parity_checker, REQUIRED_PARITY_CHECKER_MARKERS, missing)
    validate_manifest(root, manifest, missing)
    validate_expectations(expectations, missing)
    validate_rbtree_alias_gap_source(root, missing)
    return (1 if missing else 0), missing


def replace_once(text: str, marker: str) -> str:
    return text.replace(marker, "", 1)


def mutate_helper_field(manifest: dict[str, object], helper: str, key: str, value: str) -> dict[str, object]:
    mutated = copy.deepcopy(manifest)
    mutated["helper_review_notes"][helper][key] = value
    return mutated


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        create_fixture_root(tmp_root)

        code, missing = validate_tree(tmp_root)
        if code != 0:
            raise SystemExit(f"phase1-self-test:baseline_failed:{','.join(missing)}")

        total_cases = 1

        closure_path = tmp_root / "Documentation" / "zigux" / "phase1-closure.md"
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_cases = [
            ("closure_memparse", f"PHASE1_STRING_MEMPARSE_UNIT_REVIEW={STRING_MEMPARSE_REVIEW}"),
            ("closure_string_summary", f"PHASE1_STRING_REVIEW={STRING_SUMMARY}"),
            ("closure_string_cstring", f"PHASE1_STRING_CSTRING_UNIT_REVIEW={STRING_CSTRING_REVIEW}"),
            ("closure_string_equality", f"PHASE1_STRING_EQUALITY_UNIT_REVIEW={STRING_EQUALITY_REVIEW}"),
            ("closure_string_alias", f"PHASE1_STRING_ALIAS_UNIT_REVIEW={STRING_ALIAS_REVIEW}"),
            ("closure_string_prefix", f"PHASE1_STRING_PREFIX_UNIT_REVIEW={STRING_PREFIX_REVIEW}"),
            ("closure_string_prefix_length", f"PHASE1_STRING_PREFIX_LENGTH_UNIT_REVIEW={STRING_PREFIX_LENGTH_REVIEW}"),
            ("closure_string_suffix", f"PHASE1_STRING_SUFFIX_UNIT_REVIEW={STRING_SUFFIX_REVIEW}"),
            ("closure_find_bit_mask_review", "PHASE1_FIND_BIT_MASK_UNIT_REVIEW=find_bit mask and sizing helpers keep Linux-style whole-word, partial-word, and wrapped-start boundaries reviewable without relying only on indirect scan coverage"),
            ("closure_find_bit_boundary_review", "PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range"),
            ("closure_find_bit_small_bitmap_review", "PHASE1_FIND_BIT_SMALL_BITMAP_UNIT_REVIEW=find_bit single-word set zero and shared-bit scans keep Linux small-bitmap semantics aligned by masking out-of-range tail bits while preserving inclusive in-range matches inside one word"),
            ("closure_find_bit_tail_start_review", "PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the last in-range bit reachable from an inclusive start while later starts still return nbits instead of leaking the out-of-range tail"),
            ("closure_find_bit_zero_sized_review", "PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit scans return 0 even when backing words are populated so declared nbits stays authoritative over caller storage"),
            ("closure_rbtree_iterate_review", "PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys"),
            ("closure_rbtree_reverse_review", "PHASE1_RBTREE_REVERSE_UNIT_REVIEW=rbtree findLast, prevMatch, and iterateMatchesReverse keep reverse duplicate-key lookup walks aligned from the rightmost match back through the equal-key range while still reporting no match for missing keys"),
            ("closure_rbtree_bench_keys", "PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM"),
            ("closure_rbtree_alias_gap_note", "PHASE1_RBTREE_ALIAS_GAP_NOTE=the closed Phase 1 rbtree tranche still excludes Linux-style rb_* alias parity for the already-ported entry points, and that remaining surface stays explicitly out of scope until a later bounded repair lands"),
            ("closure_rbtree_alias_gap_gate", RBTREE_ALIAS_GAP_GATE),
        ]
        for label, marker in closure_cases:
            closure_path.write_text(replace_once(original_closure, marker), encoding="utf-8")
            expect_missing_marker(label, tmp_root, f"closure:{marker}")
            closure_path.write_text(original_closure, encoding="utf-8")
            total_cases += 1

        bench_checker_path = tmp_root / "scripts" / "zigux" / "check-phase1-bench.py"
        original_bench_checker = bench_checker_path.read_text(encoding="utf-8")
        bench_checker_path.write_text(
            replace_once(original_bench_checker, "print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=15')"),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bench_self_test_count",
            tmp_root,
            "bench_checker:print('PHASE1_BENCH_SELF_TEST_CASE_COUNT=15')",
        )
        bench_checker_path.write_text(original_bench_checker, encoding="utf-8")
        total_cases += 1

        manifest_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
        original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_cases = [
            ("rbtree_summary", "tools/lib/rbtree.zig", "summary"),
            ("rbtree_alias_gap_note", "tools/lib/rbtree.zig", "alias_gap_note"),
            ("rbtree_iterator_contract", "tools/lib/rbtree.zig", "iterator_unit_test_contract"),
            ("rbtree_reverse_contract", "tools/lib/rbtree.zig", "reverse_unit_test_contract"),
            ("find_bit_mask_contract", "tools/lib/find_bit.zig", "mask_unit_test_contract"),
            ("find_bit_boundary_contract", "tools/lib/find_bit.zig", "boundary_unit_test_contract"),
            ("find_bit_low_level_contract", "tools/lib/find_bit.zig", "low_level_unit_test_contract"),
            ("find_bit_small_bitmap_contract", "tools/lib/find_bit.zig", "small_bitmap_unit_test_contract"),
            ("find_bit_tail_start_contract", "tools/lib/find_bit.zig", "tail_start_unit_test_contract"),
            ("find_bit_zero_sized_contract", "tools/lib/find_bit.zig", "zero_sized_unit_test_contract"),
            ("string_summary", "tools/lib/string.zig", "summary"),
            ("string_unit_anchor", "tools/lib/string.zig", "unit_test_anchor"),
            ("string_cstring_contract", "tools/lib/string.zig", "cstring_unit_test_contract"),
            ("string_equality_contract", "tools/lib/string.zig", "equality_unit_test_contract"),
            ("string_alias_contract", "tools/lib/string.zig", "alias_unit_test_contract"),
            ("string_prefix_contract", "tools/lib/string.zig", "prefix_unit_test_contract"),
            ("string_prefix_length_contract", "tools/lib/string.zig", "prefix_length_unit_test_contract"),
            ("string_suffix_contract", "tools/lib/string.zig", "suffix_unit_test_contract"),
            ("string_memparse_contract", "tools/lib/string.zig", "memparse_unit_test_contract"),
        ]
        for label, helper, key in manifest_cases:
            mutated_manifest = mutate_helper_field(original_manifest, helper, key, "")
            write_json(manifest_path, mutated_manifest)
            expect_missing_marker(label, tmp_root, f"manifest:{helper}:{key}")
            write_json(manifest_path, original_manifest)
            total_cases += 1

        expectations_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"
        expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
        expectations["exact_checksums"]["PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM"] = 1
        write_json(expectations_path, expectations)
        expect_missing_marker(
            "rbtree_postorder_checksum",
            tmp_root,
            "bench:exact_checksums.PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM=1484000",
        )
        total_cases += 1

        expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
        expectations["iterations"]["PHASE1_BENCH_RBTREE_ITERATIONS"] = 1
        write_json(expectations_path, expectations)
        expect_missing_marker(
            "rbtree_iterations",
            tmp_root,
            "bench:iterations.PHASE1_BENCH_RBTREE_ITERATIONS=4000",
        )
        total_cases += 1

        rbtree_path = tmp_root / "tools" / "lib" / "rbtree.zig"
        original_rbtree = rbtree_path.read_text(encoding="utf-8")
        rbtree_path.write_text(
            original_rbtree + "\npub fn rb_first(root: *const Root) ?*Node { return first(root); }\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "rbtree_alias_source",
            tmp_root,
            "rbtree_source:unexpected_alias:pub fn rb_first(",
        )
        total_cases += 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())

    code, missing = validate_tree(ROOT)
    if code != 0:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        raise SystemExit(1)

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILE_RELS)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_BUILD_MARKERS) + len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_BENCH_CHECKER_MARKERS) + len(REQUIRED_PARITY_CHECKER_MARKERS)}"
    )
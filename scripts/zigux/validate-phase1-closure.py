#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
]

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

EXPECTED_REVIEW_ANCHORS = {
    "tools/lib/bitmap.zig": {
        "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
        "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
        "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
        "cross_word_scnprintf_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
        "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
        "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
        "copy_extend_zero_aligned_anchor": 'test "bitmap copy and extend handles zero and aligned counts"',
        "zero_sized_destination_view_anchor": 'test "bitmap copy helpers keep zero-sized destination views untouched"',
        "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
        "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
        "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
        "review_packet_summary": "shared Phase 1 fixture keys now own bitmap scnprintf output, tiny-buffer, allocator, and partial-window xor replay, while helper-local anchors keep predicate tail-mask, first-word and final-partial range boundaries, cross-word scnprintf collapse, truncation, copy alias, zero-sized destination-view, zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master",
    },
    "tools/lib/find_bit.zig": {
        "same_word_start_masks": 'test "single-word next scans honor start masks"',
        "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
        "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
        "zero_sized_short_circuit": 'test "zero-sized scans ignore populated backing words"',
        "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
        "past_nbits_owner_summary": "the shared Phase 1 replay now consumes the committed past_nbits_* fixture fields directly, while the direct helper-local past-nbits test remains a review-visible boundary anchor for that path",
        "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
        "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
        "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
        "review_packet_summary": "shared Phase 1 fixture keys now own the inclusive-boundary, past-nbits, and tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, zero-window, zero-sized short-circuit, tail-word set or zero or shared skip, and underscore-alias behavior review-visible on current master",
        "parity_fixture_keys": [
            "inclusive_boundary_next",
            "inclusive_boundary_zero",
            "inclusive_boundary_and",
            "past_nbits_next",
            "past_nbits_zero",
            "past_nbits_and",
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
    "tools/lib/rbtree.zig": {
        "cached_root_alias_anchor": 'test "rbtree cached-root Linux-style aliases mirror the primary helpers"',
        "review_packet_summary": "shared find, first-match, and next-match duplicate-search parity stays explicit through the Phase 1 fixture and replay, while match-iterator coverage plus cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships dedicated shared iterator or cached-root fixture keys",
    },
    "tools/lib/string.zig": {
        "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation",
        "shared_replace_char_cstr_review_summary": "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership",
        "memparse_review_anchors": [
            'test "memparse keeps original rest when sign is not followed by digits"',
            'test "memparse saturates signed overflow instead of trapping"',
            'test "memparse clamps explicit positive signed overflow"',
            'test "memparse keeps signed values and their trailing rest aligned"',
            'test "memparse consumes suffix after saturation"',
            'test "memparse applies suffixes before signed clamping"',
        ],
    },
}

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_STATUS=closed",
    "PHASE1_HELPER_COUNT=13",
    "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py",
    "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig",
    "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py",
    "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
    "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring",
    "PHASE1_LANE_SEQUENCING_RULE=shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string reopen only for their current helper-local anchors or already-committed shared fixture keys",
    "PHASE1_FIND_BIT_ZERO_SIZED_REVIEW=helper-local zero-sized short-circuit proof stays explicit through the direct find_bit test anchor so zero-sized windows ignore populated backing words and return the caller-visible boundary without dereferencing live data",
    "PHASE1_FIND_BIT_TAIL_WORD_SET_SKIP_REVIEW=helper-local tail-word next-set skip proof stays explicit through the direct find_bit test anchor so tail-word next set scans skip earlier in-range matches before clamping to nbits",
    "PHASE1_FIND_BIT_TAIL_WORD_SKIP_REVIEW=helper-local tail-word skip proof stays explicit through the direct find_bit test anchor and the Phase 1 helper manifest so tail-word next zero and shared scans skip earlier in-range matches before clamping to nbits",
    "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, tail_and_clamped_next, tail_clamped_last, and tail_clamped_empty_last stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits",
    "PHASE1_BITMAP_SCNPRINTF_CROSS_WORD_REVIEW=helper-local bitmap.scnprintf cross-word range-collapse proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so contiguous runs crossing a machine-word boundary still render as one collapsed range instead of splitting at the word edge",
    "PHASE1_BITMAP_COPY_EXTEND_ZERO_ALIGNED_REVIEW=helper-local bitmap copy-and-extend zero-count and aligned-count proof stays explicit through the direct bitmap test anchor so zero-count copies clear the destination extension and aligned word counts preserve copied words without accidental tail masking",
    "PHASE1_BITMAP_ZERO_SIZED_DESTINATION_VIEW_REVIEW=helper-local zero-sized destination-view proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so copyClearTail, bitmap_copy_clear_tail, copyAndExtend, and bitmap_copy_and_extend leave zero-sized destination views untouched instead of clearing caller sentinel storage",
    "PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so andBits, andNotBits, equal, intersects, and subset keep empty-window identity semantics without treating zero-bit windows as live data",
    "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, singleton-erase, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships",
    "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation",
]

REQUIRED_DOCS_ROOT_MARKERS = [
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-bench.py",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "make -C zigux phase1",
    ".github/workflows/zigux-bootstrap.yml",
]

REQUIRED_SCRIPTS_README_MARKERS = [
    "validate-phase1-closure.py",
    "check-phase1-parity.py",
    "check-phase1-bench.py",
    "Documentation/zigux/phase1-closure.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
]

REQUIRED_TESTS_README_MARKERS = [
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-bench.py",
    "zig build test --build-file zigux/tests/build.zig",
    "zig build bench --build-file zigux/tests/build.zig",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "make -C zigux phase1",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-bench.py",
    ".github/workflows/zigux-bootstrap.yml",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "make -C zigux phase1",
]

REQUIRED_BUILD_MARKERS = [
    '.name = "phase1-helper-tests"',
    'const test_step = b.step("test", "Run Phase 1 helper tests");',
    '.name = "phase1-bench"',
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
]

REQUIRED_LEDGER_MARKERS = [
    "`docs(zigux): close bounded phase-1 helper tranche`",
    "`test(zigux): harden phase-1 closure gates`",
    "`ci(zigux): harden phase-1 closure workflow viability`",
    "`build(zigux): remove node-20-bound Zig action from phase-1 closure path`",
]

REQUIRED_MAKEFILE_MARKERS = [
    "phase1-validate:",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/validate-phase1-closure.py",
    "phase1-test:",
    "scripts/zigux/check-phase1-parity.py",
    "$(ZIG) build test --build-file zigux/tests/build.zig",
    "phase1-bench:",
    "scripts/zigux/check-phase1-bench.py",
    "$(ZIG) build bench --build-file zigux/tests/build.zig",
    "phase1: phase1-validate phase1-test phase1-bench",
]

REQUIRED_WORKFLOW_MARKERS = [
    "workflow_dispatch:",
    "group: ${{ github.workflow }}-${{ github.ref }}",
    "cancel-in-progress: true",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py",
    "python3 scripts/zigux/validate-bootstrap.py",
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test",
    "python3 scripts/zigux/check-phase1-installer-review-surfaces.py",
    "python3 scripts/zigux/check-phase1-installer-companion-checks.py --self-test",
    "python3 scripts/zigux/check-phase1-installer-companion-checks.py",
    "scripts/zigux/validate-phase1-closure.py",
]


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return DEFAULT_ROOT


def load_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def load_json(root: Path, rel: str) -> object:
    return json.loads(load_text(root, rel))


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def require_substrings(text: str, markers: list[str], prefix: str) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{prefix}:{marker}")
    return missing


def collect_manifest_markers(manifest: object, root: Path) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest:not_object"]
    missing: list[str] = []
    if manifest.get("phase") != "Phase 1":
        missing.append("manifest:phase")
    if manifest.get("status") != "closed":
        missing.append("manifest:status")
    if manifest.get("helper_count") != 13:
        missing.append("manifest:helper_count")
    helpers = manifest.get("helpers")
    if helpers != EXPECTED_HELPERS:
        missing.append("manifest:helpers")
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return missing + ["manifest:review_anchors"]
    for helper, expected_fields in EXPECTED_REVIEW_ANCHORS.items():
        actual = review_anchors.get(helper)
        if not isinstance(actual, dict):
            missing.append(f"manifest:{helper}")
            continue
        for key, expected_value in expected_fields.items():
            if actual.get(key) != expected_value:
                missing.append(f"manifest:{helper}:{key}")
    for rel in EXPECTED_HELPERS:
        if not (root / rel).exists():
            missing.append(f"manifest:file:{rel}")
    return missing


def collect_bench_markers(bench: object) -> list[str]:
    if not isinstance(bench, dict):
        return ["bench:not_object"]
    missing: list[str] = []
    if bench.get("status") != "pass":
        missing.append("bench:status")
    iterations = bench.get("iterations")
    if iterations != EXPECTED_BENCH_ITERATIONS:
        missing.append("bench:iterations")
    checksums = bench.get("checksums")
    if checksums != EXPECTED_BENCH_CHECKSUMS:
        missing.append("bench:checksums")
    exact_checksums = bench.get("exact_checksums")
    if not isinstance(exact_checksums, dict):
        missing.append("bench:exact_checksums")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    closure = load_text(root, "Documentation/zigux/phase1-closure.md")
    docs_root = load_text(root, "Documentation/zigux/README.md")
    review = load_text(root, "Documentation/zigux/review-checklist.md")
    scripts_readme = load_text(root, "scripts/zigux/README.md")
    tests_readme = load_text(root, "zigux/tests/README.md")
    workflow = load_text(root, ".github/workflows/zigux-bootstrap.yml")
    build_zig = load_text(root, "zigux/tests/build.zig")
    ledger = load_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    makefile = load_text(root, "zigux/Makefile")
    manifest = load_json(root, "zigux/tests/fixtures/phase1_helper_manifest.json")
    bench = load_json(root, "zigux/tests/fixtures/phase1_bench_expectations.json")

    missing: list[str] = []
    missing.extend(require_substrings(closure, REQUIRED_CLOSURE_MARKERS, "closure"))
    missing.extend(require_substrings(docs_root, REQUIRED_DOCS_ROOT_MARKERS, "docs_root"))
    missing.extend(require_substrings(review, REQUIRED_REVIEW_CHECKLIST_MARKERS, "review"))
    missing.extend(require_substrings(scripts_readme, REQUIRED_SCRIPTS_README_MARKERS, "scripts_readme"))
    missing.extend(require_substrings(tests_readme, REQUIRED_TESTS_README_MARKERS, "tests_readme"))
    missing.extend(require_substrings(workflow, REQUIRED_WORKFLOW_MARKERS, "workflow"))
    missing.extend(require_substrings(build_zig, REQUIRED_BUILD_MARKERS, "build"))
    missing.extend(require_substrings(ledger, REQUIRED_LEDGER_MARKERS, "ledger"))
    missing.extend(require_substrings(makefile, REQUIRED_MAKEFILE_MARKERS, "makefile"))
    missing.extend(collect_manifest_markers(manifest, root))
    missing.extend(collect_bench_markers(bench))
    return missing


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES + EXPECTED_HELPERS:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("// fixture\n", encoding="utf-8")

    (root / "Documentation/zigux/phase1-closure.md").write_text("\n".join(REQUIRED_CLOSURE_MARKERS) + "\n", encoding="utf-8")
    (root / "Documentation/zigux/README.md").write_text("\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n", encoding="utf-8")
    (root / "Documentation/zigux/review-checklist.md").write_text("\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS) + "\n", encoding="utf-8")
    (root / "scripts/zigux/README.md").write_text("\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux/tests/README.md").write_text("\n".join(REQUIRED_TESTS_README_MARKERS) + "\n", encoding="utf-8")
    (root / ".github/workflows/zigux-bootstrap.yml").write_text("\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux/tests/build.zig").write_text("\n".join(REQUIRED_BUILD_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").write_text("\n".join(REQUIRED_LEDGER_MARKERS) + "\n", encoding="utf-8")
    (root / "zigux/Makefile").write_text("\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n", encoding="utf-8")

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": EXPECTED_HELPERS,
        "review_anchors": EXPECTED_REVIEW_ANCHORS,
    }
    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    bench = {
        "status": "pass",
        "iterations": EXPECTED_BENCH_ITERATIONS,
        "checksums": EXPECTED_BENCH_CHECKSUMS,
        "exact_checksums": {"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1},
    }
    (root / "zigux/tests/fixtures/phase1_bench_expectations.json").write_text(
        json.dumps(bench, indent=2) + "\n", encoding="utf-8"
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[0], "", 1), encoding="utf-8")
        assert any(item.startswith("closure:PHASE1_STATUS=closed") for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_word_set_skip_anchor"] = "bad"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "manifest:tools/lib/find_bit.zig:tail_word_set_skip_anchor" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text(makefile_path.read_text(encoding="utf-8").replace("phase1: phase1-validate phase1-test phase1-bench", "", 1), encoding="utf-8")
        assert any(item.startswith("makefile:phase1: phase1-validate phase1-test phase1-bench") for item in collect_missing_markers(root))
        case_count += 1

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-tests.")
    parser.add_argument("--root", help="Validate an alternate repository root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_FILES_START")
        for rel in missing_files:
            print(rel)
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
    print("PHASE1_CLOSURE_REQUIRED_MARKER_COUNT=" + str(
        len(REQUIRED_CLOSURE_MARKERS)
        + len(REQUIRED_DOCS_ROOT_MARKERS)
        + len(REQUIRED_REVIEW_CHECKLIST_MARKERS)
        + len(REQUIRED_SCRIPTS_README_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(REQUIRED_WORKFLOW_MARKERS)
        + len(REQUIRED_BUILD_MARKERS)
        + len(REQUIRED_LEDGER_MARKERS)
        + len(REQUIRED_MAKEFILE_MARKERS)
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

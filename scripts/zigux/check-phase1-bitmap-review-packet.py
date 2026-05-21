#!/usr/bin/env python3
"""Guard the Phase 1 bitmap helper review packet against helper, manifest, and fixture drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
BITMAP_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

EXPECTED_BITMAP_SOURCE_SYMBOLS = [
    "pub fn bitmapSize(nbits: usize) usize {",
    "pub fn bitmap_size(nbits: usize) usize {",
    "pub fn zero(dst: []Word, nbits: usize) void {",
    "pub fn bitmap_zero(dst: []Word, nbits: usize) void {",
    "pub fn fill(dst: []Word, nbits: usize) void {",
    "pub fn bitmap_fill(dst: []Word, nbits: usize) void {",
    "pub fn copy(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn bitmap_copy(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn copyClearTail(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn copyAndExtend(dst: []Word, src: []const Word, count: usize, size: usize) void {",
    "pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn bitmap_copy_and_extend(dst: []Word, src: []const Word, count: usize, size: usize) void {",
    "pub fn empty(src: []const Word, nbits: usize) bool {",
    "pub fn bitmap_empty(src: []const Word, nbits: usize) bool {",
    "pub fn full(src: []const Word, nbits: usize) bool {",
    "pub fn bitmap_full(src: []const Word, nbits: usize) bool {",
    "pub fn weight(src: []const Word, nbits: usize) usize {",
    "pub fn bitmap_weight(src: []const Word, nbits: usize) usize {",
    "pub fn orBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn bitmap_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn weightedOr(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn bitmap_weighted_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn xorBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn bitmap_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn weightedXor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn bitmap_weighted_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn complement(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn bitmap_complement(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn andBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_and(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn andNotBits(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_andnot(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn equal(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_equal(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn subset(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_subset(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn setRange(map: []Word, start: usize, len: usize) void {",
    "pub fn bitmap_set(map: []Word, start: usize, len: usize) void {",
    "pub fn clearRange(map: []Word, start: usize, len: usize) void {",
    "pub fn bitmap_clear(map: []Word, start: usize, len: usize) void {",
    "pub fn scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {",
    "pub fn bitmap_scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {",
    "pub fn bitmapAlloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "pub fn bitmapZalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "pub fn bitmap_zalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "pub fn bitmapFree(allocator: std.mem.Allocator, bitmap: *?[]Word) void {",
    "pub fn bitmap_free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap range helpers preserve edges across whole-word spans"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap zero-bit logical helpers stay explicit"',
    'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    'test "bitmap and andnot equal intersects subset"',
    'test "bitmap tail-masked helpers ignore out-of-range differences"',
    'test "bitmap full empty and weight ignore out-of-range tail bits"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap or keeps caller-selected bit window"',
    'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
    'test "bitmap allocation helpers size zero fill and reset optionals"',
]

EXPECTED_BITMAP_PACKET = {
    "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
    "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
    "equal_fast_path_anchor": 'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
    "or_window_anchor": 'test "bitmap or keeps caller-selected bit window"',
    "or_multiword_tail_anchor": 'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    "weighted_tail_count_anchor": 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    "complement_tail_anchor": 'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "review_packet_summary": (
        "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, "
        "scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current master "
        "keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias "
        "behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, "
        "zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, "
        "exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range "
        "tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail "
        "xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length "
        "caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror "
        "coverage, and allocator optional-reset coverage."
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
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf truncates and keeps a terminator slot"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_zero_and_aligned_anchors": [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
    "zero_bit_noop_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
    "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
    "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    "next_safe_step_note": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor "
        "drift inside the current helper-local packet or committed shared replay drift in the bitmap "
        "parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, "
        "cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and "
        "or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical "
        "short-circuit, and Linux-style alias mirror anchors here, and if the separate bitmap "
        "closure-validator anchor-sync repair is still outstanding, treat that as the only other "
        "bitmap follow-through."
    ),
}

EXPECTED_BITMAP_FIXTURE_VALUES = {
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
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def iter_anchor_strings(expected: object) -> list[str]:
    anchors: list[str] = []
    if isinstance(expected, str):
        if expected.startswith('test "'):
            anchors.append(expected)
    elif isinstance(expected, list):
        for item in expected:
            if isinstance(item, str) and item.startswith('test "'):
                anchors.append(item)
    return anchors


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (BITMAP_HELPER_REL, BITMAP_MANIFEST_REL, BITMAP_FIXTURE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, BITMAP_HELPER_REL)
    manifest = load_json(root, BITMAP_MANIFEST_REL)
    fixture = load_json(root, BITMAP_FIXTURE_REL)
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]

    for symbol in EXPECTED_BITMAP_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"bitmap_source:{symbol}", symbol))

    seen_helper_anchors = set(EXPECTED_HELPER_TEST_ANCHORS)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"bitmap_helper:{anchor}", anchor))

    for key, expected in EXPECTED_BITMAP_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor in seen_helper_anchors:
                continue
            failures.extend(
                require_exact_occurrence(helper_text, f"bitmap_helper_packet:{key}", anchor)
            )
            seen_helper_anchors.add(anchor)

    failures.extend(
        require_exact_value(
            "bitmap_manifest:review_anchors.tools/lib.bitmap.zig.helper_test_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/bitmap.zig", "helper_test_anchors")),
            EXPECTED_HELPER_TEST_ANCHORS,
        )
    )

    for key, expected in EXPECTED_BITMAP_PACKET.items():
        if key == "helper_test_anchors":
            continue
        failures.extend(
            require_exact_value(
                f"bitmap_manifest:review_anchors.tools/lib.bitmap.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/bitmap.zig", key)),
                expected,
            )
        )

    bitmap_fixture = fixture.get("bitmap")
    if not isinstance(bitmap_fixture, dict):
        return [f"bitmap_fixture:expected=dict:actual={type(bitmap_fixture).__name__}"]
    for key, expected in EXPECTED_BITMAP_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"bitmap_fixture:{key}", bitmap_fixture.get(key), expected))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/bitmap.zig": EXPECTED_BITMAP_PACKET,
                }
            },
            indent=2,
        )
        + "\n"
    )


def sample_fixture() -> str:
    return json.dumps({"bitmap": EXPECTED_BITMAP_FIXTURE_VALUES}, indent=2) + "\n"


def build_sample_repo(root: Path) -> None:
    helper_lines = list(EXPECTED_BITMAP_SOURCE_SYMBOLS)
    seen = set(helper_lines)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        if anchor not in seen:
            helper_lines.append(anchor)
            seen.add(anchor)
    for key, expected in EXPECTED_BITMAP_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor not in seen:
                helper_lines.append(anchor)
                seen.add(anchor)

    write_file(root, BITMAP_HELPER_REL, "\n".join(helper_lines) + "\n")
    write_file(root, BITMAP_MANIFEST_REL, sample_manifest())
    write_file(root, BITMAP_FIXTURE_REL, sample_fixture())


def mutate_json_path(root: Path, relative_path: Path, path: tuple[str, ...]) -> None:
    json_path = root / relative_path
    data = json.loads(json_path.read_text(encoding="utf-8"))
    current = data
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    elif isinstance(value, bool):
        current[final_key] = not value
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_sample_root(destination: Path) -> None:
    build_sample_repo(destination)


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-review-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    mutation_specs = []
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("source_symbol", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_BITMAP_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_HELPER_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"packet_anchor_phase1_helper_replay_{kind}",
            ("packet_anchor", EXPECTED_BITMAP_PACKET["phase1_helper_replay_anchor"]),
            kind,
        )
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"manifest_{key}",
            ("manifest", ("review_anchors", "tools/lib/bitmap.zig", key)),
            "manifest",
        )
        for key in EXPECTED_BITMAP_PACKET
    )
    mutation_specs.extend(
        (
            f"fixture_{key}",
            ("fixture", ("bitmap", key)),
            "fixture",
        )
        for key in EXPECTED_BITMAP_FIXTURE_VALUES
    )
    mutation_specs.append(("manifest_missing_file", ("missing_file", BITMAP_MANIFEST_REL), "missing_file"))
    mutation_specs.append(("fixture_missing_file", ("missing_file", BITMAP_FIXTURE_REL), "missing_file"))

    for name, target, kind in mutation_specs:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-bitmap-review-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if isinstance(target, tuple) and target[0] == "source_symbol":
                path = root / BITMAP_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "helper_anchor":
                path = root / BITMAP_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "packet_anchor":
                path = root / BITMAP_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "manifest":
                mutate_json_path(root, BITMAP_MANIFEST_REL, target[1])
            elif isinstance(target, tuple) and target[0] == "fixture":
                mutate_json_path(root, BITMAP_FIXTURE_REL, target[1])
            else:
                (root / target[1]).unlink()

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument(
        "--self-test", action="store_true", help="run the built-in checker self-test"
    )
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample tree to the given directory",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-bitmap-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

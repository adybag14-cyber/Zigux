#!/usr/bin/env python3
"""Guard the Phase 1 bitmap review packet against helper, fixture, smoke, and note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/bitmap.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_SOURCE_SYMBOLS = [
    "pub fn bitmap_size(nbits: usize) usize {",
    "pub fn bitmap_zero(dst: []Word, nbits: usize) void {",
    "pub fn bitmap_fill(dst: []Word, nbits: usize) void {",
    "pub fn bitmap_copy(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn bitmap_copy_and_extend(dst: []Word, src: []const Word, count: usize, size: usize) void {",
    "pub fn bitmap_empty(src: []const Word, nbits: usize) bool {",
    "pub fn bitmap_full(src: []const Word, nbits: usize) bool {",
    "pub fn bitmap_weight(src: []const Word, nbits: usize) usize {",
    "pub fn bitmap_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn bitmap_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) void {",
    "pub fn bitmap_weighted_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn bitmap_weighted_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn bitmap_weight_and(src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn bitmap_weight_andnot(src1: []const Word, src2: []const Word, nbits: usize) usize {",
    "pub fn bitmap_and(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_andnot(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_equal(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_intersects(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_subset(src1: []const Word, src2: []const Word, nbits: usize) bool {",
    "pub fn bitmap_complement(dst: []Word, src: []const Word, nbits: usize) void {",
    "pub fn bitmap_set(map: []Word, start: usize, len: usize) void {",
    "pub fn bitmap_clear(map: []Word, start: usize, len: usize) void {",
    "pub fn bitmap_scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {",
    "pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "pub fn bitmap_zalloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {",
    "pub fn bitmap_free(allocator: std.mem.Allocator, bitmap: *?[]Word) void {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap zero-bit logical helpers stay explicit"',
    'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    'test "bitmap tail-masked helpers ignore out-of-range differences"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    'test "bitmap weighted and andnot clamp counts to the declared tail window"',
    'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    'test "bitmap scnprintf truncates and keeps a terminator slot"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
    'test "bitmap allocation helpers size zero fill and reset optionals"',
]

EXPECTED_LANE_LINES = [
    "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`",
    "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
]

EXPECTED_LANE_PARAGRAPH = (
    "- `tools/lib/bitmap.zig` owns its helper-local bitmap anchors and the committed bitmap replay keys in "
    "`zigux/tests/fixtures/phase1_helpers.json`. The restored `Documentation/zigux/phase1-closure.md` note plus "
    "`scripts/zigux/validate-phase1-closure.py` now remain live closure-side companions on current `master`, but "
    "nearby bitmap rereads should still stay on the manifest-backed anchors and that restored closure packet rather "
    "than widening back into the older missing validator-first or make-route surfaces by default. The live "
    "helper-local bitmap packet already keeps caller-window and multiword-tail `xorBits()` and `orBits()` clamp "
    "proofs review-visible beside the fill-tail, copy-alias, cross-word `scnprintf()`, empty-buffer, and "
    "allocator-reset anchors cataloged in the manifest-backed review surface."
)

EXPECTED_CLOSURE_PARAGRAPH = (
    "A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route: keep "
    "`tools/lib/bitmap.zig` parked unless a fresh reread finds new direct-anchor drift inside the manifest-backed "
    "fill-tail clamp, copy-alias, cross-word `scnprintf()`, exact-word-boundary equality fast-path masking, "
    "empty-buffer, allocator-reset, zero-bit logical short-circuit, Linux-style alias mirror, caller-window or "
    "multiword-tail `xorBits()`/`orBits()` clamp witnesses, or weighted tail-count clamp, or drift in the "
    "already-committed bitmap replay fields summarized by the manifest; do not reopen older closure-side or "
    "validator-route cue names by default. Current `master` still spells those bitmap-local anchors in "
    "`tools/lib/bitmap.zig`, the committed helper manifest, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, "
    "and the helper-local zero-bit logical test body no longer carries the one-argument `std.testing.expectEqual(...)` "
    "compile break that had briefly reopened this packet, so leave the helper parked unless one of those direct "
    "anchors or committed replay fields drifts."
)

EXPECTED_CLOSURE_DIRECT_REVIEW = (
    "- `PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet "
    "because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf "
    "output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail "
    "clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, "
    "zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary "
    "equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail "
    "xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and "
    "zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, "
    "and allocator optional-reset coverage review-visible at the helper surface`"
)

EXPECTED_MANIFEST_FIELDS = {
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
    "shared_logical_fixture_keys": [
        "weight",
        "and_result",
        "and_values",
        "andnot_result",
        "andnot_values",
        "or_values",
        "xor_values",
        "equal",
        "intersects",
        "subset",
    ],
    "shared_range_fixture_keys": [
        "range_after_set",
        "range_after_clear",
        "full_after_fill",
        "empty_after_zero",
    ],
    "partial_xor_review_fields": [
        "partial_xor_nbits",
        "partial_xor_masked_values",
    ],
    "review_packet_summary": (
        "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf "
        "output, truncation, tiny-buffer, and partial-window xor replay, while current master keeps the direct "
        "helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and "
        "extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, "
        "zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked "
        "predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or "
        "clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and "
        "zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror "
        "coverage, and allocator optional-reset coverage."
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside "
        "the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master "
        "still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary "
        "equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, "
        "allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen "
        "older closure-side or validator-route cue names by default."
    ),
}

EXPECTED_FIXTURE_VALUES = {
    "alloc_words": 2,
    "zalloc_words": 2,
    "zalloc_values": [0, 0],
    "scnprintf": "1-3,7,10-11",
    "truncated_scnprintf_len": 7,
    "truncated_scnprintf": "1-3,7,1",
    "terminator_only_scnprintf_len": 0,
    "terminator_only_nul": 0,
    "zero_length_scnprintf_len": 0,
    "partial_xor_nbits": 4,
    "partial_xor_masked_values": [14],
}

EXPECTED_SMOKE_MARKERS = [
    'const bitmap = @import("bitmap");',
    'try std.testing.expect(@hasDecl(bitmap, "setRange"));',
    'const bitmap_rendered_len = bitmap.scnprintf(&map, nbits, &rendered);',
    'test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {',
    'bitmap.copy(direct_copy[0..0], src[0..0], 0);',
    'bitmap.bitmap_copy(alias_copy[0..0], src[0..0], 0);',
    'bitmap.copyClearTail(direct_clear[0..0], src[0..0], 0);',
    'bitmap.bitmap_copy_clear_tail(alias_clear[0..0], src[0..0], 0);',
    'bitmap.copyAndExtend(direct_extend[0..0], src[0..0], 0, 0);',
    'bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0);',
    'const direct_len = bitmap.scnprintf(&empty_map, 8, &direct_buffer);',
    'const alias_len = bitmap.bitmap_scnprintf(&empty_map, 8, &alias_buffer);',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(root: Path, relative_path: Path) -> object:
    return load_json_with_duplicate_tracking(load_text(root, relative_path))


def load_json_failure(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected_current_packet"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (HELPER_REL, MANIFEST_REL, FIXTURE_REL, SMOKE_REL, LANE_NOTE_REL, CLOSURE_NOTE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    smoke_text = load_text(root, SMOKE_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    closure_text = load_text(root, CLOSURE_NOTE_REL)
    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("manifest", exc)]
    try:
        fixture = load_json(root, FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("fixture", exc)]

    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    manifest_dupes = collect_duplicate_json_key_paths(manifest)
    if manifest_dupes:
        return [f"manifest:duplicate_json_key:{path}" for path in manifest_dupes]

    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]
    fixture_dupes = collect_duplicate_json_key_paths(fixture)
    if fixture_dupes:
        return [f"fixture:duplicate_json_key:{path}" for path in fixture_dupes]

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_symbol:{symbol}", symbol))
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_anchor:{anchor}", anchor))
    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_exact_occurrence(smoke_text, f"smoke_marker:{marker}", marker))
    for line in EXPECTED_LANE_LINES:
        failures.extend(require_exact_occurrence(lane_text, f"lane_line:{line}", line))
    failures.extend(require_exact_occurrence(lane_text, "lane_paragraph", EXPECTED_LANE_PARAGRAPH))
    failures.extend(require_exact_occurrence(closure_text, "closure_paragraph", EXPECTED_CLOSURE_PARAGRAPH))
    failures.extend(require_exact_occurrence(closure_text, "closure_direct_review", EXPECTED_CLOSURE_DIRECT_REVIEW))

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors"]
    bitmap_packet = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_packet, dict):
        return ["manifest:tools/lib/bitmap.zig"]
    for field, expected in EXPECTED_MANIFEST_FIELDS.items():
        failures.extend(require_exact_value(f"manifest:{field}", bitmap_packet.get(field), expected))

    bitmap_fixture = fixture.get("bitmap")
    if not isinstance(bitmap_fixture, dict):
        return ["fixture:bitmap"]
    for field, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"fixture:{field}", bitmap_fixture.get(field), expected))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, HELPER_REL, "\n".join(EXPECTED_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS) + "\n")
    write_text(root, MANIFEST_REL, json.dumps({"review_anchors": {"tools/lib/bitmap.zig": EXPECTED_MANIFEST_FIELDS}}, indent=2) + "\n")
    write_text(root, FIXTURE_REL, json.dumps({"bitmap": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n")
    write_text(root, SMOKE_REL, "\n".join(EXPECTED_SMOKE_MARKERS) + "\n")
    write_text(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(EXPECTED_LANE_LINES + [EXPECTED_LANE_PARAGRAPH]) + "\n")
    write_text(root, CLOSURE_NOTE_REL, "# sample\n\n" + "\n".join([EXPECTED_CLOSURE_PARAGRAPH, EXPECTED_CLOSURE_DIRECT_REVIEW]) + "\n")


def insert_duplicate_json_line(root: Path, relative_path: Path, needle: str, duplicate_line: str) -> None:
    json_path = root / relative_path
    text = json_path.read_text(encoding="utf-8")
    json_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("missing_helper", "missing_file:tools/lib/bitmap.zig"),
        ("missing_symbol", "helper_symbol:pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {:expected=1:actual=0"),
        ("missing_anchor", 'helper_anchor:test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched":expected=1:actual=0'),
        ("missing_smoke_marker", 'smoke_marker:const alias_len = bitmap.bitmap_scnprintf(&empty_map, 8, &alias_buffer);:expected=1:actual=0'),
        ("missing_lane_line", f"lane_line:{EXPECTED_LANE_LINES[0]}:expected=1:actual=0"),
        ("missing_lane_paragraph", "lane_paragraph:expected=1:actual=0"),
        ("missing_closure_paragraph", "closure_paragraph:expected=1:actual=0"),
        ("missing_closure_direct_review", "closure_direct_review:expected=1:actual=0"),
        ("manifest_drift", "manifest:review_packet_summary:expected_current_packet"),
        ("manifest_partial_xor_drift", "manifest:partial_xor_review_fields:expected_current_packet"),
        ("fixture_drift", "fixture:alloc_words:expected_current_packet"),
        ("fixture_partial_xor_drift", "fixture:partial_xor_masked_values:expected_current_packet"),
        ("duplicate_anchor", 'helper_anchor:test "bitmap allocation helpers size zero fill and reset optionals":expected=1:actual=2'),
        ("manifest_invalid_json", "manifest:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1"),
        ("fixture_invalid_json", "fixture:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1"),
        ("manifest_duplicate_review_packet_summary", "manifest:duplicate_json_key:review_anchors.tools/lib/bitmap.zig.review_packet_summary"),
        ("fixture_duplicate_alloc_words", "fixture:duplicate_json_key:bitmap.alloc_words"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bitmap_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if cases[0][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_helper")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:baseline")

        helper_path = tmp_root / HELPER_REL
        smoke_path = tmp_root / SMOKE_REL
        lane_path = tmp_root / LANE_NOTE_REL
        closure_path = tmp_root / CLOSURE_NOTE_REL
        manifest_path = tmp_root / MANIFEST_REL
        fixture_path = tmp_root / FIXTURE_REL

        text = helper_path.read_text(encoding="utf-8").replace(
            "pub fn bitmap_alloc(allocator: std.mem.Allocator, nbits: usize) ![]Word {\n",
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[1][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_symbol")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(EXPECTED_HELPER_TEST_ANCHORS[9] + "\n", "", 1)
        helper_path.write_text(text, encoding="utf-8")
        if cases[2][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_anchor")

        build_sample_repo(tmp_root)
        text = smoke_path.read_text(encoding="utf-8").replace(EXPECTED_SMOKE_MARKERS[-1] + "\n", "", 1)
        smoke_path.write_text(text, encoding="utf-8")
        if cases[3][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_smoke_marker")

        build_sample_repo(tmp_root)
        text = lane_path.read_text(encoding="utf-8").replace(EXPECTED_LANE_LINES[0] + "\n", "", 1)
        lane_path.write_text(text, encoding="utf-8")
        if cases[4][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_lane_line")

        build_sample_repo(tmp_root)
        text = lane_path.read_text(encoding="utf-8").replace(EXPECTED_LANE_PARAGRAPH + "\n", "", 1)
        lane_path.write_text(text, encoding="utf-8")
        if cases[5][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_lane_paragraph")

        build_sample_repo(tmp_root)
        text = closure_path.read_text(encoding="utf-8").replace(EXPECTED_CLOSURE_PARAGRAPH + "\n", "", 1)
        closure_path.write_text(text, encoding="utf-8")
        if cases[6][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_closure_paragraph")

        build_sample_repo(tmp_root)
        text = closure_path.read_text(encoding="utf-8").replace(EXPECTED_CLOSURE_DIRECT_REVIEW + "\n", "", 1)
        closure_path.write_text(text, encoding="utf-8")
        if cases[7][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:missing_closure_direct_review")

        build_sample_repo(tmp_root)
        manifest = load_json(tmp_root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["review_packet_summary"] = "drift"
        write_text(tmp_root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if cases[8][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:manifest_drift")

        build_sample_repo(tmp_root)
        manifest = load_json(tmp_root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["partial_xor_review_fields"] = []
        write_text(tmp_root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if cases[9][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:manifest_partial_xor_drift")

        build_sample_repo(tmp_root)
        fixture = load_json(tmp_root, FIXTURE_REL)
        fixture["bitmap"]["alloc_words"] = 0
        write_text(tmp_root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
        if cases[10][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:fixture_drift")

        build_sample_repo(tmp_root)
        fixture = load_json(tmp_root, FIXTURE_REL)
        fixture["bitmap"]["partial_xor_masked_values"] = []
        write_text(tmp_root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
        if cases[11][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:fixture_partial_xor_drift")

        build_sample_repo(tmp_root)
        duplicated = EXPECTED_HELPER_TEST_ANCHORS[-1]
        text = helper_path.read_text(encoding="utf-8").replace(duplicated + "\n", duplicated + "\n" + duplicated + "\n", 1)
        helper_path.write_text(text, encoding="utf-8")
        if cases[12][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:duplicate_anchor")

        build_sample_repo(tmp_root)
        manifest_path.write_text("{\n", encoding="utf-8")
        if cases[13][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:manifest_invalid_json")

        build_sample_repo(tmp_root)
        fixture_path.write_text("{\n", encoding="utf-8")
        if cases[14][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:fixture_invalid_json")

        build_sample_repo(tmp_root)
        insert_duplicate_json_line(
            tmp_root,
            MANIFEST_REL,
            '      "review_packet_summary": "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.",',
            '      "review_packet_summary": "drifted duplicate summary",',
        )
        if cases[15][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:manifest_duplicate_review_packet_summary")

        build_sample_repo(tmp_root)
        insert_duplicate_json_line(
            tmp_root,
            FIXTURE_REL,
            '    "alloc_words": 2,',
            '    "alloc_words": 0,',
        )
        if cases[16][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-bitmap-review:self-test:fixture_duplicate_alloc_words")

    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BITMAP_REVIEW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BITMAP_REVIEW_PACKET=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_SMOKE={SMOKE_REL.as_posix()}")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_CLOSURE_NOTE={CLOSURE_NOTE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

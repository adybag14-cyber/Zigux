#!/usr/bin/env python3
"""Guard the Phase 1 find_bit review packet against helper-local drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/find_bit.zig")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")

EXPECTED_SOURCE_SYMBOLS = [
    "pub fn find_first_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn _find_first_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn _find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn findFirstAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn find_first_zero_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn _find_first_zero_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn findNextAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_zero_bit(addr: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_zero_bit(addr: []const Word, nbits: usize, start: usize) usize {",
    "pub fn getValue8(addr: []const Word, offset: usize) u8 {",
    "pub fn findNextClump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "pub fn find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "pub fn _find_next_clump8(clump: *u8, addr: []const Word, nbits: usize, offset: usize) usize {",
    "pub fn findFirstClump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "pub fn findLastBit(addr: []const Word, nbits: usize) usize {",
    "pub fn find_last_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn _find_last_bit(addr: []const Word, nbits: usize) usize {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "find first and next set bits across words, with andnot gaps explicit"',
    'test "find zero bits respects the declared bit count"',
    'test "find and bit returns the first shared set bit"',
    'test "underscore entry points reuse the public helper behavior"',
    'test "single-word next scans honor start masks"',
    'test "single-word first scans clamp to the declared bit window"',
    'test "single-word next scans clamp partial windows before returning nbits"',
    'test "word-boundary next scans start fresh on the next word"',
    'test "zero-bit windows return without reading bitmap words"',
    'test "zero-sized scans ignore populated backing words"',
    'test "next scans past nbits return without reading bitmap words"',
    'test "tail mask ignores set bits beyond nbits"',
    'test "tail mask ignores zero bits beyond nbits"',
    'test "tail mask ignores shared bits beyond nbits"',
    'test "tail-word next set scans skip earlier in-range matches before clamping"',
    'test "clump8 scans align to the containing byte and return its value"',
    'test "clump8 scans keep tail bytes reachable from partial final words"',
    'test "clump8 scans mask tail bits beyond nbits"',
    'test "clump8 scans leave the caller byte untouched when no set bit remains"',
    'test "clump8 zero-bit and past-end windows leave the caller byte untouched"',
    'test "clump8 past-end scans return without reading bitmap words"',
    'test "getValue8 reads aligned bytes from bitmap words"',
    'test "getValue8 reads the last aligned byte of a word without folding in the next word"',
    'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
    'test "find last bit scans backward across words"',
    'test "find last bit ignores storage beyond an exact word boundary"',
    'test "find last bit clamps tail words to nbits"',
    'test "find last bit returns nbits when no set bits remain"',
    'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
]

EXPECTED_LANE_LINES = [
    "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, underscore-alias and Linux-style alias coverage including the shipped find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
    "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
]

EXPECTED_LANE_PARAGRAPH = (
    "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` "
    "byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's "
    "`helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the "
    "same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate "
    "shared replay family"
)

EXPECTED_CLOSURE_PARAGRAPH = (
    "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep "
    "`tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word "
    "start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, "
    "zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, "
    "Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or "
    "tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring "
    "helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, "
    "alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the "
    "manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` "
    "keep that helper-local progress review-visible beside the narrower closure validator. That direct packet "
    "now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, "
    "so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells "
    "the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the "
    "underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail "
    "windows keep the last in-range next matches reachable from an inclusive start` proof alongside the "
    "head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or "
    "committed replay fields drifts."
)

EXPECTED_MANIFEST_PACKET = {
    "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "single_word_tail_inclusive_boundary_anchor": 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
    "tail_word_inclusive_boundary_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.",
    "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
    "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    "linux_alias_anchor": 'test "Linux-style aliases mirror the primary find helpers, including andnot"',
    "andnot_scan_entrypoints": [
        "findFirstAndNotBit",
        "find_first_andnot_bit",
        "_find_first_andnot_bit",
        "findNextAndNotBit",
        "find_next_andnot_bit",
        "_find_next_andnot_bit",
    ],
    "andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
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
    "tail_inclusive_boundary_fixture_keys": [
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
    ],
    "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
    "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",
}

EXPECTED_FIXTURE_VALUES = {
    "tail_clamped_first": 67,
    "tail_clamped_next": 69,
    "tail_zero_clamped_first": 69,
    "tail_zero_clamped_next": 69,
    "tail_and_clamped_first": 67,
    "tail_and_clamped_next": 69,
    "tail_clamped_last": 67,
    "tail_clamped_empty_last": 69,
    "tail_inclusive_boundary_next": 68,
    "tail_inclusive_boundary_zero": 68,
    "tail_inclusive_boundary_and": 68,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: Any, expected: Any) -> list[str]:
    return [] if actual == expected else [f"{label}:expected_current_packet"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (HELPER_REL, LANE_NOTE_REL, CLOSURE_NOTE_REL, MANIFEST_REL, FIXTURE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    closure_text = load_text(root, CLOSURE_NOTE_REL)
    manifest = load_json(root, MANIFEST_REL)
    fixture = load_json(root, FIXTURE_REL)

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_symbol:{symbol}", symbol))

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_anchor:{anchor}", anchor))

    for lane_line in EXPECTED_LANE_LINES:
        failures.extend(require_exact_occurrence(lane_text, f"lane_line:{lane_line}", lane_line))
    failures.extend(require_exact_occurrence(lane_text, "lane_paragraph", EXPECTED_LANE_PARAGRAPH))
    failures.extend(
        require_exact_occurrence(closure_text, "closure_paragraph", EXPECTED_CLOSURE_PARAGRAPH)
    )

    review_anchors = manifest.get("review_anchors") if isinstance(manifest, dict) else None
    if not isinstance(review_anchors, dict):
        return ["manifest:review_anchors"]
    packet = review_anchors.get("tools/lib/find_bit.zig")
    if not isinstance(packet, dict):
        return ["manifest:tools/lib/find_bit.zig"]

    for field, expected in EXPECTED_MANIFEST_PACKET.items():
        failures.extend(require_exact_value(f"manifest:{field}", packet.get(field), expected))

    find_bit_fixture = fixture.get("find_bit") if isinstance(fixture, dict) else None
    if not isinstance(find_bit_fixture, dict):
        return ["fixture:find_bit"]
    for field, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"fixture:{field}", find_bit_fixture.get(field), expected))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    helper_lines = EXPECTED_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS
    write_text(root, HELPER_REL, "\n".join(helper_lines) + "\n")
    write_text(
        root,
        LANE_NOTE_REL,
        "# sample\n\n" + "\n".join(EXPECTED_LANE_LINES + [EXPECTED_LANE_PARAGRAPH]) + "\n",
    )
    write_text(root, CLOSURE_NOTE_REL, "# sample\n\n" + EXPECTED_CLOSURE_PARAGRAPH + "\n")
    write_text(
        root,
        MANIFEST_REL,
        json.dumps({"review_anchors": {"tools/lib/find_bit.zig": EXPECTED_MANIFEST_PACKET}}, indent=2)
        + "\n",
    )
    write_text(
        root,
        FIXTURE_REL,
        json.dumps({"find_bit": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("missing_helper", "missing_file:tools/lib/find_bit.zig"),
        ("missing_symbol", "helper_symbol:pub fn findLastBit(addr: []const Word, nbits: usize) usize {:expected=1:actual=0"),
        ('missing_anchor', 'helper_anchor:test "getValue8 reads the last aligned byte of a word without folding in the next word":expected=1:actual=0'),
        ("missing_lane_line", f"lane_line:{EXPECTED_LANE_LINES[0]}:expected=1:actual=0"),
        ("missing_lane_paragraph", "lane_paragraph:expected=1:actual=0"),
        ("missing_closure_paragraph", "closure_paragraph:expected=1:actual=0"),
        ("manifest_drift", "manifest:review_packet_summary:expected_current_packet"),
        ("manifest_tail_anchor_drift", "manifest:single_word_tail_inclusive_boundary_anchor:expected_current_packet"),
        ("fixture_drift", "fixture:tail_clamped_last:expected_current_packet"),
        ("duplicate_anchor", 'helper_anchor:test "clump8 past-end scans return without reading bitmap words":expected=1:actual=2'),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if cases[0][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:missing_helper")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:baseline")

        helper_text = load_text(tmp_root, HELPER_REL).replace(EXPECTED_SOURCE_SYMBOLS[25] + "\n", "", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[1][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:missing_symbol")

        build_sample_repo(tmp_root)
        helper_text = load_text(tmp_root, HELPER_REL).replace(EXPECTED_HELPER_TEST_ANCHORS[22] + "\n", "", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[2][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:missing_anchor")

        build_sample_repo(tmp_root)
        lane_text = load_text(tmp_root, LANE_NOTE_REL).replace(EXPECTED_LANE_LINES[0] + "\n", "", 1)
        write_text(tmp_root, LANE_NOTE_REL, lane_text)
        if cases[3][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:missing_lane_line")

        build_sampleRepo(tmp_root)
        lane_text = load_text(tmp_root, LANE_NOTE_REL).replace(EXPECTED_LANE_PARAGRAPH + "\n", "", 1)
        write_text(tmp_root, LANE_NOTE_REL, lane_text)
        if cases[4][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:missing_lane_paragraph")

        build_sample_repo(tmp_root)
        closure_text = load_text(tmp_root, CLOSURE_NOTE_REL).replace(EXPECTED_CLOSURE_PARAGRAPH + "\n", "", 1)
        write_text(tmp_root, CLOSURE_NOTE_REL, closure_text)
        if cases[5][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:missing_closure_paragraph")

        build_sample_repo(tmp_root)
        manifest = load_json(tmp_root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["review_packet_summary"] = "drift"
        write_text(tmp_root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if cases[6][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:manifest_drift")

        build_sample_repo(tmp_root)
        manifest = load_json(tmp_root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["single_word_tail_inclusive_boundary_anchor"] = "drift"
        write_text(tmp_root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        if cases[7][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:manifest_tail_anchor_drift")

        build_sample_repo(tmp_root)
        fixture = load_json(tmp_root, FIXTURE_REL)
        fixture["find_bit"]["tail_clamped_last"] = 0
        write_text(tmp_root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
        if cases[8][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:fixture_drift")

        build_sample_repo(tmp_root)
        helper_text = load_text(tmp_root, HELPER_REL)
        duplicated = EXPECTED_HELPER_TEST_ANCHORS[20]
        helper_text = helper_text.replace(duplicated + "\n", duplicated + "\n" + duplicated + "\n", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[9][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-find-bit-review:self-test:duplicate_anchor")

    print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT=10")
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
        print("PHASE1_FIND_BIT_REVIEW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_REVIEW_PACKET=pass")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_CLOSURE_NOTE={CLOSURE_NOTE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

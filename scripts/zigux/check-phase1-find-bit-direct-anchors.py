#!/usr/bin/env python3
"""Guard the Phase 1 find_bit direct-anchor packet against helper-local drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
FIND_BIT_REL = Path("tools/lib/find_bit.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
PHASE1_HELPERS_REL = Path("zigux/tests/phase1_helpers.zig")

FIND_BIT_TEST_MARKERS = {
    "first_next_andnot": 'test "find first and next set bits across words, with andnot gaps explicit" {',
    "zero_bits": 'test "find zero bits respects the declared bit count" {',
    "and_bit": 'test "find and bit returns the first shared set bit" {',
    "underscore_entrypoints": 'test "underscore entry points reuse the public helper behavior" {',
    "single_word_next_start_masks": 'test "single-word next scans honor start masks" {',
    "single_word_first_tail_clamp": 'test "single-word first scans clamp to the declared bit window" {',
    "single_word_next_tail_clamp": 'test "single-word next scans clamp partial windows before returning nbits" {',
    "word_boundary_next": 'test "word-boundary next scans start fresh on the next word" {',
    "zero_bit_windows": 'test "zero-bit windows return without reading bitmap words" {',
    "zero_sized_scans": 'test "zero-sized scans ignore populated backing words" {',
    "past_nbits": 'test "next scans past nbits return without reading bitmap words" {',
    "tail_mask_set": 'test "tail mask ignores set bits beyond nbits" {',
    "tail_mask_zero": 'test "tail mask ignores zero bits beyond nbits" {',
    "tail_mask_shared": 'test "tail mask ignores shared bits beyond nbits" {',
    "tail_word_set_skip": 'test "tail-word next set scans skip earlier in-range matches before clamping" {',
    "clump8_align": 'test "clump8 scans align to the containing byte and return its value" {',
    "clump8_partial_tail": 'test "clump8 scans keep tail bytes reachable from partial final words" {',
    "clump8_tail_mask": 'test "clump8 scans mask tail bits beyond nbits" {',
    "clump8_exhausted_preserve": 'test "clump8 scans leave the caller byte untouched when no set bit remains" {',
    "clump8_zero_past_end": 'test "clump8 zero-bit and past-end windows leave the caller byte untouched" {',
    "clump8_past_end_no_read": 'test "clump8 past-end scans return without reading bitmap words" {',
    "get_value8_aligned": 'test "getValue8 reads aligned bytes from bitmap words" {',
    "get_value8_last_byte": 'test "getValue8 reads the last aligned byte of a word without folding in the next word" {',
    "head_word_inclusive_boundary": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
    "tail_word_inclusive_boundary": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
    "single_word_tail_inclusive_boundary": 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start" {',
    "find_last_backward": 'test "find last bit scans backward across words" {',
    "find_last_exact_boundary": 'test "find last bit ignores storage beyond an exact word boundary" {',
    "find_last_tail_clamp": 'test "find last bit clamps tail words to nbits" {',
    "find_last_empty": 'test "find last bit returns nbits when no set bits remain" {',
    "tail_word_zero_shared_skip": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping" {',
    "low_level_aliases": 'test "low-level underscore aliases mirror the primary find helpers, including andnot" {',
    "linux_aliases": 'test "Linux-style aliases mirror the primary find helpers, including andnot" {',
    "linux_next_or_tail": 'test "Linux-style next-or aliases clamp tail words and past-end starts" {',
    "linux_clump_tail": 'test "Linux-style clump aliases mask tail bytes and preserve exhausted caller bytes" {',
}

FIND_BIT_SOURCE_MARKERS = {
    "find_first_bit_alias": "pub fn find_first_bit(addr: []const Word, nbits: usize) usize {",
    "underscore_find_first_bit_alias": "pub fn _find_first_bit(addr: []const Word, nbits: usize) usize {",
    "find_first_andnot_bit_alias": "pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "underscore_find_first_andnot_bit_alias": "pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "find_next_or_bit_alias": "pub fn find_next_or_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "underscore_find_next_or_bit_alias": "pub fn _find_next_or_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "find_next_andnot_bit_alias": "pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "underscore_find_next_andnot_bit_alias": "pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "find_first_clump8_alias": "pub fn find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "underscore_find_first_clump8_alias": "pub fn _find_first_clump8(clump: *u8, addr: []const Word, nbits: usize) usize {",
    "find_last_bit_alias": "pub fn find_last_bit(addr: []const Word, nbits: usize) usize {",
    "underscore_find_last_bit_alias": "pub fn _find_last_bit(addr: []const Word, nbits: usize) usize {",
}

MANIFEST_MARKERS = {
    "direct_anchor_helper": '"tools/lib/find_bit.zig"',
    "same_word_start_masks": '"same_word_start_masks": "test \\"single-word next scans honor start masks\\""',
    "tail_word_contract": '"tail_word_inclusive_boundary_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail."',
    "andnot_entrypoint_contract": '"andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording."',
    "shared_replay_summary": '"review_packet_summary": "the committed Phase 1 fixture still owns the live cross-word find_bit replay through `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, and `last`, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master"',
}

SHARED_REPLAY_MARKERS = {
    "fixture_bits_per_long": "bits_per_long: usize,",
    "fixture_next_after_word": "next_after_word: usize,",
    "replay_first": "try std.testing.expectEqual(fixture.find_bit.first, find_bit.findFirstBit(&bitmap_a, nbits));",
    "replay_next_after_word": "try std.testing.expectEqual(fixture.find_bit.next_after_word, find_bit.findNextBit(&bitmap_a, nbits, fixture.find_bit.bits_per_long));",
    "replay_first_zero": "try std.testing.expectEqual(fixture.find_bit.first_zero, find_bit.findFirstZeroBit(&bitmap_b, nbits));",
    "replay_next_and": "try std.testing.expectEqual(fixture.find_bit.next_and, find_bit.findNextAndBit(&bitmap_a, &bitmap_and, nbits, fixture.find_bit.bits_per_long));",
    "replay_last": "try std.testing.expectEqual(fixture.find_bit.last, find_bit.findLastBit(&bitmap_a, nbits));",
}

MARKER_GROUPS = (
    ("find_bit_tests", FIND_BIT_TEST_MARKERS),
    ("find_bit_sources", FIND_BIT_SOURCE_MARKERS),
    ("manifest", MANIFEST_MARKERS),
    ("shared_replay", SHARED_REPLAY_MARKERS),
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def marker_failures(text: str, markers: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for label, marker in markers.items():
        count = text.count(marker)
        if count != 1:
            failures.append(f"{label}:expected=1:actual={count}")
    return failures


def validate_texts(find_bit_text: str, manifest_text: str, replay_text: str) -> tuple[str, object]:
    texts = {
        "find_bit_tests": find_bit_text,
        "find_bit_sources": find_bit_text,
        "manifest": manifest_text,
        "shared_replay": replay_text,
    }
    for group_name, markers in MARKER_GROUPS:
        failures = marker_failures(texts[group_name], markers)
        if failures:
            return (f"invalid_{group_name}_marker_counts", failures)
    return ("pass", None)


def load_text(path: Path) -> tuple[str | None, object]:
    try:
        return (path.read_text(encoding="utf-8"), None)
    except FileNotFoundError:
        return (None, path)


def load_sources(root: Path) -> tuple[str, object]:
    find_bit_text, missing = load_text(root / FIND_BIT_REL)
    if find_bit_text is None:
        return ("missing_find_bit_file", missing)
    manifest_text, missing = load_text(root / MANIFEST_REL)
    if manifest_text is None:
        return ("missing_manifest_file", missing)
    replay_text, missing = load_text(root / PHASE1_HELPERS_REL)
    if replay_text is None:
        return ("missing_phase1_helpers_file", missing)
    return validate_texts(find_bit_text, manifest_text, replay_text)


def build_sample(markers: dict[str, str], omit: str | None = None, duplicate: str | None = None) -> str:
    lines = list(markers.values())
    if omit is not None:
        lines = [line for line in lines if line != markers[omit]]
    if duplicate is not None:
        marker = markers[duplicate]
        for idx, line in enumerate(lines):
            if line == marker:
                lines.insert(idx + 1, marker)
                break
    return "\n".join(lines) + "\n"


def sample_texts(omit_group: str | None = None, duplicate_group: str | None = None, label: str | None = None) -> tuple[str, str, str]:
    samples = {}
    for group_name, markers in MARKER_GROUPS:
        samples[group_name] = build_sample(
            markers,
            omit=label if omit_group == group_name else None,
            duplicate=label if duplicate_group == group_name else None,
        )
    return (
        samples["find_bit_tests"] + samples["find_bit_sources"],
        samples["manifest"],
        samples["shared_replay"],
    )


def run_self_test() -> None:
    case_count = 0
    kind, payload = validate_texts(*sample_texts())
    assert kind == "pass", (kind, payload)
    case_count += 1

    for group_name, markers in MARKER_GROUPS:
        expected_kind = f"invalid_{group_name}_marker_counts"
        for label in markers:
            kind, payload = validate_texts(*sample_texts(omit_group=group_name, label=label))
            assert kind == expected_kind, (label, kind, payload)
            assert payload == [f"{label}:expected=1:actual=0"], (label, payload)
            case_count += 1
            kind, payload = validate_texts(*sample_texts(duplicate_group=group_name, label=label))
            assert kind == expected_kind, (label, kind, payload)
            assert payload == [f"{label}:expected=1:actual=2"], (label, payload)
            case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-find-bit-direct-anchors-") as tmp:
        root = Path(tmp)
        kind, payload = load_sources(root)
        assert kind == "missing_find_bit_file", (kind, payload)
        assert payload == root / FIND_BIT_REL
        case_count += 1

        (root / FIND_BIT_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / FIND_BIT_REL).write_text(sample_texts()[0], encoding="utf-8")
        kind, payload = load_sources(root)
        assert kind == "missing_manifest_file", (kind, payload)
        assert payload == root / MANIFEST_REL
        case_count += 1

        (root / MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / MANIFEST_REL).write_text(sample_texts()[1], encoding="utf-8")
        kind, payload = load_sources(root)
        assert kind == "missing_phase1_helpers_file", (kind, payload)
        assert payload == root / PHASE1_HELPERS_REL
        case_count += 1

        (root / PHASE1_HELPERS_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / PHASE1_HELPERS_REL).write_text(sample_texts()[2], encoding="utf-8")
        kind, payload = load_sources(root)
        assert kind == "pass", (kind, payload)
        case_count += 1

    print("PHASE1_FIND_BIT_DIRECT_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run self-test cases")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = load_sources(repo_root(args.root))
    if kind != "pass":
        print("PHASE1_FIND_BIT_DIRECT_ANCHORS=fail")
        if isinstance(payload, list):
            print("PHASE1_FIND_BIT_DIRECT_ANCHORS_REASON=" + kind)
            for failure in payload:
                print(failure)
        else:
            print(f"PHASE1_FIND_BIT_DIRECT_ANCHORS_REASON={kind}")
            print(payload)
        return 1

    print("PHASE1_FIND_BIT_DIRECT_ANCHORS=pass")
    print(f"PHASE1_FIND_BIT_DIRECT_ANCHORS_HELPER={FIND_BIT_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_DIRECT_ANCHORS_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_DIRECT_ANCHORS_SHARED_REPLAY={PHASE1_HELPERS_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

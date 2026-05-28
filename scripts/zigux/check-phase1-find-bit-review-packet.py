#!/usr/bin/env python3
"""Guard the Phase 1 find_bit review packet against helper, fixture, and note drift."""

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
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
FIND_BIT_REL = "tools/lib/find_bit.zig"


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


SOURCE_SYMBOLS = [
    "findFirstBit", "findFirstAndBit", "findFirstAndNotBit", "findFirstZeroBit",
    "findNextBit", "findNextAndBit", "findNextOrBit", "findNextAndNotBit", "findNextZeroBit",
    "findNextClump8", "findFirstClump8", "findLastBit", "getValue8",
    "find_first_bit", "_find_first_bit", "find_first_and_bit", "_find_first_and_bit",
    "find_first_andnot_bit", "_find_first_andnot_bit", "find_first_zero_bit", "_find_first_zero_bit",
    "find_next_bit", "_find_next_bit", "find_next_and_bit", "_find_next_and_bit",
    "find_next_or_bit", "_find_next_or_bit", "find_next_andnot_bit", "_find_next_andnot_bit",
    "find_next_zero_bit", "_find_next_zero_bit", "find_next_clump8", "_find_next_clump8",
    "find_first_clump8", "_find_first_clump8", "find_last_bit", "_find_last_bit",
]

HELPER_TEST_ANCHORS = [
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

PARITY_FIXTURE_KEYS = [
    "bits_per_long", "first", "next_after_6", "next_after_word", "first_zero",
    "next_zero", "first_and", "next_and", "last",
]

FIXTURE_VALUES = {
    "bits_per_long": 64, "first": 5, "next_after_6": 9, "next_after_word": 66,
    "first_zero": 3, "next_zero": 68, "first_and": 9, "next_and": 66, "last": 71,
}

MANIFEST_EXPECTED = {
    "helper_test_anchors": HELPER_TEST_ANCHORS,
    "same_word_start_masks": HELPER_TEST_ANCHORS[4],
    "inclusive_boundary_start": HELPER_TEST_ANCHORS[23],
    "tail_word_inclusive_boundary_anchor": HELPER_TEST_ANCHORS[24],
    "single_word_tail_inclusive_boundary_anchor": HELPER_TEST_ANCHORS[25],
    "tail_word_inclusive_boundary_contract": "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.",
    "zero_bit_window": HELPER_TEST_ANCHORS[8],
    "zero_sized_short_circuit_anchor": HELPER_TEST_ANCHORS[9],
    "past_nbits_short_circuit": HELPER_TEST_ANCHORS[10],
    "underscore_alias_anchor": HELPER_TEST_ANCHORS[31],
    "linux_alias_anchor": HELPER_TEST_ANCHORS[32],
    "andnot_scan_entrypoints": ["findFirstAndNotBit", "find_first_andnot_bit", "_find_first_andnot_bit", "findNextAndNotBit", "find_next_andnot_bit", "_find_next_andnot_bit"],
    "andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
    "tail_word_set_skip_anchor": HELPER_TEST_ANCHORS[14],
    "tail_word_skip_anchor": HELPER_TEST_ANCHORS[30],
    "parity_fixture_keys": PARITY_FIXTURE_KEYS,
    "review_packet_summary": "the committed Phase 1 fixture still owns the live cross-word find_bit replay through `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, and `last`, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
    "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older saved validator cues or neighboring helper families.",
}

LANE_MARKERS = [
    "PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask",
    "or for committed tail-clamped or tail-inclusive-boundary replay drift",
]

CLOSURE_MARKERS = [
    "For `tools/lib/find_bit.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.",
    "This helper should only reopen if a fresh reread finds drift in those direct anchors or in the committed shared find-bit parity fields",
    "PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
]

SMOKE_MARKERS = [
    "const word_bits = find_bit.bits_per_long;",
    "find_bit.findFirstBit(&map, nbits)",
    "find_bit.findNextBit(&map, nbits, word_bits - 1)",
    "find_bit.findLastBit(&map, nbits)",
    'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
    "find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits)",
    "find_bit.find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 2)",
    "find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4)",
    "find_bit.findFirstClump8(&clump, &clump_map, nbits)",
    "find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long)",
    "find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits)",
]


def root(path: str | None) -> Path:
    return Path(path).resolve() if path else DEFAULT_ROOT.resolve()


def load_text(repo: Path, path: Path) -> str:
    return (repo / path).read_text(encoding="utf-8")


def load_json(repo: Path, path: Path) -> Any:
    return json.loads(load_text(repo, path), object_pairs_hook=DuplicateTrackingDict)


def duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    found: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        found.extend(".".join(prefix + (key,)) for key in data.duplicate_keys)
    if isinstance(data, dict):
        for key, value in data.items():
            found.extend(duplicate_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            found.extend(duplicate_paths(item, prefix))
    return found


def exact(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def equals(label: str, actual: Any, expected: Any) -> list[str]:
    return [] if actual == expected else [f"{label}:expected_current_packet"]


def collect_failures(repo: Path) -> list[str]:
    failures: list[str] = []
    texts: dict[Path, str] = {}
    for rel in [HELPER_REL, LANE_NOTE_REL, CLOSURE_NOTE_REL, SMOKE_REL]:
        try:
            texts[rel] = load_text(repo, rel)
        except FileNotFoundError:
            failures.append(f"missing_file:{rel.as_posix()}")
            texts[rel] = ""

    decoded: dict[Path, Any] = {}
    for rel, label in [(MANIFEST_REL, "manifest"), (FIXTURE_REL, "fixture")]:
        try:
            decoded[rel] = load_json(repo, rel)
        except FileNotFoundError:
            failures.append(f"missing_file:{rel.as_posix()}")
            decoded[rel] = {}
        except json.JSONDecodeError as exc:
            failures.append(f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}")
            decoded[rel] = {}

    helper = texts[HELPER_REL]
    for symbol in SOURCE_SYMBOLS:
        failures.extend(exact(helper, f"helper_symbol:{symbol}", f"pub fn {symbol}"))
    for marker in HELPER_TEST_ANCHORS:
        failures.extend(exact(helper, f"helper_anchor:{marker}", marker))
    for marker in LANE_MARKERS:
        failures.extend(exact(texts[LANE_NOTE_REL], f"lane_marker:{marker}", marker))
    for marker in CLOSURE_MARKERS:
        failures.extend(exact(texts[CLOSURE_NOTE_REL], f"closure_marker:{marker}", marker))
    for marker in SMOKE_MARKERS:
        failures.extend(exact(texts[SMOKE_REL], f"smoke_marker:{marker}", marker))

    manifest = decoded[MANIFEST_REL]
    fixture = decoded[FIXTURE_REL]
    failures.extend(f"manifest:duplicate_json_key:{path}" for path in duplicate_paths(manifest))
    failures.extend(f"fixture:duplicate_json_key:{path}" for path in duplicate_paths(fixture))

    review = manifest.get("review_anchors", {}) if isinstance(manifest, dict) else {}
    packet = review.get(FIND_BIT_REL, {}) if isinstance(review, dict) else {}
    for key, expected in MANIFEST_EXPECTED.items():
        actual = packet.get(key) if isinstance(packet, dict) else None
        failures.extend(equals(f"manifest:{key}", actual, expected))

    find_bit = fixture.get("find_bit", {}) if isinstance(fixture, dict) else {}
    for key, expected in FIXTURE_VALUES.items():
        actual = find_bit.get(key) if isinstance(find_bit, dict) else None
        failures.extend(equals(f"fixture:{key}", actual, expected))

    return failures


def write(repo: Path, rel: Path, text: str) -> None:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def build_sample_repo(repo: Path) -> None:
    write(repo, HELPER_REL, "\n".join([f"pub fn {name}" for name in SOURCE_SYMBOLS] + HELPER_TEST_ANCHORS) + "\n")
    write(repo, LANE_NOTE_REL, "\n".join(LANE_MARKERS) + "\n")
    write(repo, CLOSURE_NOTE_REL, "\n".join(CLOSURE_MARKERS) + "\n")
    write(repo, MANIFEST_REL, json.dumps({"review_anchors": {FIND_BIT_REL: MANIFEST_EXPECTED}}, indent=2) + "\n")
    write(repo, FIXTURE_REL, json.dumps({"find_bit": FIXTURE_VALUES}, indent=2) + "\n")
    write(repo, SMOKE_REL, "\n".join(SMOKE_MARKERS) + "\n")


def expect_case(repo: Path, label: str, expected: str) -> None:
    if expected not in collect_failures(repo):
        raise SystemExit(f"phase1-find-bit-review:self-test:{label}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_review_") as tmp:
        repo = Path(tmp)
        expect_case(repo, "missing_helper", f"missing_file:{HELPER_REL.as_posix()}")
        build_sample_repo(repo)
        if collect_failures(repo):
            raise SystemExit("phase1-find-bit-review:self-test:baseline")

        helper = repo / HELPER_REL
        manifest = repo / MANIFEST_REL
        fixture = repo / FIXTURE_REL
        smoke = repo / SMOKE_REL

        helper.write_text(helper.read_text(encoding="utf-8").replace("pub fn findLastBit\n", "", 1), encoding="utf-8")
        expect_case(repo, "missing_symbol", "helper_symbol:findLastBit:expected=1:actual=0")

        build_sample_repo(repo)
        helper.write_text(helper.read_text(encoding="utf-8") + HELPER_TEST_ANCHORS[20] + "\n", encoding="utf-8")
        expect_case(repo, "duplicate_anchor", f"helper_anchor:{HELPER_TEST_ANCHORS[20]}:expected=1:actual=2")

        build_sample_repo(repo)
        data = load_json(repo, MANIFEST_REL)
        data["review_anchors"][FIND_BIT_REL]["parity_fixture_keys"] = ["bits_per_long"]
        write(repo, MANIFEST_REL, json.dumps(data, indent=2) + "\n")
        expect_case(repo, "manifest_drift", "manifest:parity_fixture_keys:expected_current_packet")

        build_sample_repo(repo)
        data = load_json(repo, FIXTURE_REL)
        data["find_bit"]["next_after_word"] = 0
        write(repo, FIXTURE_REL, json.dumps(data, indent=2) + "\n")
        expect_case(repo, "fixture_drift", "fixture:next_after_word:expected_current_packet")

        build_sample_repo(repo)
        manifest.write_text("{\ninvalid\n", encoding="utf-8")
        expect_case(repo, "manifest_invalid_json", "manifest:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1")

        build_sample_repo(repo)
        fixture_text = fixture.read_text(encoding="utf-8")
        fixture.write_text(fixture_text.replace('    "bits_per_long": 64,', '    "bits_per_long": 0,\n    "bits_per_long": 64,', 1), encoding="utf-8")
        expect_case(repo, "duplicate_fixture_key", "fixture:duplicate_json_key:find_bit.bits_per_long")

        build_sample_repo(repo)
        smoke.unlink()
        expect_case(repo, "missing_smoke", f"missing_file:{SMOKE_REL.as_posix()}")

    print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_REVIEW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1
    print("phase1-find-bit-review-packet:ok")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_SMOKE={SMOKE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

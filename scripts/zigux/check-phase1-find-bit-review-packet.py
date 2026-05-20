#!/usr/bin/env python3
"""Guard the Phase 1 find_bit helper review packet against helper, manifest, fixture, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")
FIND_BIT_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIND_BIT_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
FIND_BIT_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

EXPECTED_FIND_BIT_SOURCE_SYMBOLS = [
    "pub const Word = usize;",
    "pub const bits_per_long = @bitSizeOf(Word);",
    "pub fn findFirstBit(addr: []const Word, nbits: usize) usize {",
    "pub fn find_first_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn _find_first_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn findFirstAndBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn _find_first_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn findFirstAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {",
    "pub fn findFirstZeroBit(addr: []const Word, nbits: usize) usize {",
    "pub fn find_first_zero_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn _find_first_zero_bit(addr: []const Word, nbits: usize) usize {",
    "pub fn findNextBit(addr: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_bit(addr: []const Word, nbits: usize, start: usize) usize {",
    "pub fn findNextAndBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_and_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn findNextAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {",
    "pub fn findNextZeroBit(addr: []const Word, nbits: usize, start: usize) usize {",
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
    'test "getValue8 reads aligned bytes from bitmap words"',
    'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "find last bit scans backward across words"',
    'test "find last bit ignores storage beyond an exact word boundary"',
    'test "find last bit clamps tail words to nbits"',
    'test "find last bit returns nbits when no set bits remain"',
    'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
]

EXPECTED_FIND_BIT_PACKET = {
    "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_contract": (
        "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive "
        "start lands on the last in-range bit of the final partial word, while later starts still return nbits "
        "instead of leaking the out-of-range tail."
    ),
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
    "andnot_scan_entrypoint_contract": (
        "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit "
        "packet instead of being left implicit under generic alias wording."
    ),
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
    "review_packet_summary": (
        "shared Phase 1 fixture keys own the exact tail-clamped find_bit replay, while helper-local anchors keep "
        "same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, "
        "past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, "
        "and Linux-style alias behavior review-visible on current master"
    ),
    "next_safe_step_note": (
        "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside "
        "same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, "
        "getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan "
        "entry points, or tail-word skip anchors, or committed tail-clamped replay drift; do not reopen older saved "
        "validator cues or neighboring helper families."
    ),
}

EXPECTED_FIND_BIT_FIXTURE_VALUES = {
    "bits_per_long": 64,
    "first": 5,
    "next_after_6": 67,
    "next_after_word": 135,
    "first_zero": 3,
    "next_zero": 68,
    "first_and": 9,
    "next_and": 66,
    "last": 135,
    "inclusive_boundary_next": 63,
    "inclusive_boundary_zero": 63,
    "inclusive_boundary_and": 63,
    "tail_inclusive_boundary_next": 68,
    "tail_inclusive_boundary_zero": 68,
    "tail_inclusive_boundary_and": 68,
    "past_nbits_next": 7,
    "past_nbits_zero": 7,
    "past_nbits_and": 7,
    "tail_clamped_first": 67,
    "tail_clamped_next": 69,
    "tail_zero_clamped_first": 69,
    "tail_zero_clamped_next": 69,
    "tail_and_clamped_first": 67,
    "tail_and_clamped_next": 69,
    "tail_clamped_last": 67,
    "tail_clamped_empty_last": 69,
}

EXPECTED_FIND_BIT_LANE_MARKERS = [
    (
        "lane_direct_owner",
        "`PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word "
        "inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and "
        "findLastBit() byte-clump and backward-scan coverage, underscore-alias and Linux-style alias coverage "
        "including the shipped find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and "
        "_find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped find_bit "
        "replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
    ),
    (
        "lane_next_safe_step",
        "`PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, "
        "inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), "
        "underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word "
        "skip anchors, or for committed tail-clamped replay drift; do not reopen older saved validator cues or "
        "neighboring helper families`",
    ),
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


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

    for relative_path in (
        FIND_BIT_HELPER_REL,
        FIND_BIT_MANIFEST_REL,
        FIND_BIT_FIXTURE_REL,
        FIND_BIT_LANE_NOTE_REL,
    ):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, FIND_BIT_HELPER_REL)
    lane_text = load_text(root, FIND_BIT_LANE_NOTE_REL)
    manifest = load_json(root, FIND_BIT_MANIFEST_REL)
    fixture = load_json(root, FIND_BIT_FIXTURE_REL)
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]

    for symbol in EXPECTED_FIND_BIT_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(helper_text, f"find_bit_source:{symbol}", symbol)
        )

    seen_helper_anchors = set(EXPECTED_HELPER_TEST_ANCHORS)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(helper_text, f"find_bit_helper:{anchor}", anchor)
        )

    for key, expected in EXPECTED_FIND_BIT_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor in seen_helper_anchors:
                continue
            failures.extend(
                require_exact_occurrence(helper_text, f"find_bit_helper_packet:{key}", anchor)
            )
            seen_helper_anchors.add(anchor)

    for label, marker in EXPECTED_FIND_BIT_LANE_MARKERS:
        failures.extend(
            require_exact_occurrence(
                lane_text,
                f"find_bit_lane:{label}",
                marker,
            )
        )

    failures.extend(
        require_exact_value(
            "find_bit_manifest:review_anchors.tools/lib/find_bit.zig.helper_test_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/find_bit.zig", "helper_test_anchors")),
            EXPECTED_HELPER_TEST_ANCHORS,
        )
    )

    for key, expected in EXPECTED_FIND_BIT_PACKET.items():
        if key == "helper_test_anchors":
            continue
        failures.extend(
            require_exact_value(
                f"find_bit_manifest:review_anchors.tools/lib/find_bit.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/find_bit.zig", key)),
                expected,
            )
        )

    find_bit_fixture = fixture.get("find_bit")
    if not isinstance(find_bit_fixture, dict):
        return ["find_bit_fixture:expected=dict:actual=missing"]
    for key, expected in EXPECTED_FIND_BIT_FIXTURE_VALUES.items():
        failures.extend(
            require_exact_value(
                f"find_bit_fixture:{key}",
                find_bit_fixture.get(key),
                expected,
            )
        )

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
                    "tools/lib/find_bit.zig": EXPECTED_FIND_BIT_PACKET,
                }
            },
            indent=2,
        )
        + "\n"
    )


def sample_fixture() -> str:
    return json.dumps({"find_bit": EXPECTED_FIND_BIT_FIXTURE_VALUES}, separators=(",", ":")) + "\n"


def sample_lane_note() -> str:
    return "\n".join(marker for _, marker in EXPECTED_FIND_BIT_LANE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    helper_lines = list(EXPECTED_FIND_BIT_SOURCE_SYMBOLS)
    seen = set(helper_lines)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        if anchor not in seen:
            helper_lines.append(anchor)
            seen.add(anchor)
    for key, expected in EXPECTED_FIND_BIT_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor not in seen:
                helper_lines.append(anchor)
                seen.add(anchor)

    write_file(
        root,
        FIND_BIT_HELPER_REL,
        "\n".join(helper_lines) + "\n",
    )
    write_file(root, FIND_BIT_MANIFEST_REL, sample_manifest())
    write_file(root, FIND_BIT_FIXTURE_REL, sample_fixture())
    write_file(root, FIND_BIT_LANE_NOTE_REL, sample_lane_note())


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
    json_path.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-find-bit-review-ok-") as tmpdir:
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
        for idx, symbol in enumerate(EXPECTED_FIND_BIT_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_HELPER_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"lane_marker_{idx}_{kind}",
            ("lane_marker", marker),
            kind,
        )
        for idx, (_, marker) in enumerate(EXPECTED_FIND_BIT_LANE_MARKERS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"manifest_{key}",
            ("manifest", ("review_anchors", "tools/lib/find_bit.zig", key)),
            "manifest",
        )
        for key in EXPECTED_FIND_BIT_PACKET
    )
    mutation_specs.extend(
        (
            f"fixture_{key}",
            ("fixture", ("find_bit", key)),
            "fixture",
        )
        for key in EXPECTED_FIND_BIT_FIXTURE_VALUES
    )
    mutation_specs.append(("manifest_missing_file", ("missing_file", FIND_BIT_MANIFEST_REL), "missing_file"))
    mutation_specs.append(("fixture_missing_file", ("missing_file", FIND_BIT_FIXTURE_REL), "missing_file"))
    mutation_specs.append(("lane_note_missing_file", ("missing_file", FIND_BIT_LANE_NOTE_REL), "missing_file"))

    for name, target, kind in mutation_specs:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-find-bit-review-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if isinstance(target, tuple) and target[0] in {"source_symbol", "helper_anchor", "lane_marker"}:
                if target[0] == "lane_marker":
                    path = root / FIND_BIT_LANE_NOTE_REL
                else:
                    path = root / FIND_BIT_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "manifest":
                mutate_json_path(root, FIND_BIT_MANIFEST_REL, target[1])
            elif isinstance(target, tuple) and target[0] == "fixture":
                mutate_json_path(root, FIND_BIT_FIXTURE_REL, target[1])
            else:
                (root / target[1]).unlink()

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal passing sample repository layout to this directory",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_repo(Path(args.write_sample_root).resolve())
        print(f"sample_root_written:{Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-find-bit-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

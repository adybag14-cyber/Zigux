#!/usr/bin/env python3
"""Guard the current Phase 1 find_bit closure packet against helper and reminder drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/find_bit.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")

HELPER_MARKERS = [
    'test "find first and next set bits across words, with andnot gaps explicit"',
    'test "single-word next scans honor start masks"',
    'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
    'test "tail-word next set scans skip earlier in-range matches before clamping"',
    'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    'test "clump8 past-end scans return without reading bitmap words"',
    'test "getValue8 reads the last aligned byte of a word without folding in the next word"',
    'test "find last bit clamps tail words to nbits"',
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
]

LANE_LINES = [
    "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, plus the public, Linux-style, and underscore andnot coverage including the shipped findFirstAndNotBit(), findNextAndNotBit(), find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
    "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
    "- the existing byte-clump and `findLastBit()` proofs belong to that same `find_bit` direct-anchor packet too, so if one of those helper-local anchors drifts, refresh the current helper-family note before widening shared replay ownership",
    "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family",
]

CLOSURE_MARKERS = {
    "find_bit_review_guard": "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "find_bit_tie_breaker": "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.",
}

VALIDATOR_MARKERS = [
    'FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")',
    'FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")',
    '(FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),',
    '"find_bit_bench_anchor_guard":',
    '"find_bit_review_guard":',
    'failures.extend(require_expected_mapping(f"{MANIFEST_REL.as_posix()}:review_anchors.tools/lib/find_bit.zig", review_anchors.get("tools/lib/find_bit.zig"), EXPECTED_FIND_BIT_REVIEW_ANCHORS))',
]

REVIEW_CHECKER_MARKERS = [
    "EXPECTED_SOURCE_SYMBOLS = [",
    "EXPECTED_HELPER_TEST_ANCHORS = [",
    "EXPECTED_SMOKE_MARKERS = [",
    "EXPECTED_MANIFEST_PACKET = {",
    "EXPECTED_FIXTURE_VALUES = {",
    "tail_inclusive_boundary_fixture_keys",
    "andnot_scan_entrypoints",
    "phase1-find-bit-review-packet:ok",
]

MANIFEST_EXPECTATIONS = {
    ("lane_sequencing", "direct_anchor_followup_helpers"): [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ],
    ("review_anchors", "tools/lib/find_bit.zig", "same_word_start_masks"): 'test "single-word next scans honor start masks"',
    ("review_anchors", "tools/lib/find_bit.zig", "inclusive_boundary_start"): 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    ("review_anchors", "tools/lib/find_bit.zig", "tail_word_inclusive_boundary_anchor"): 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    ("review_anchors", "tools/lib/find_bit.zig", "single_word_tail_inclusive_boundary_anchor"): 'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start"',
    ("review_anchors", "tools/lib/find_bit.zig", "tail_word_inclusive_boundary_contract"): "Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.",
    ("review_anchors", "tools/lib/find_bit.zig", "underscore_alias_anchor"): 'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    ("review_anchors", "tools/lib/find_bit.zig", "linux_alias_anchor"): 'test "Linux-style aliases mirror the primary find helpers, including andnot"',
    ("review_anchors", "tools/lib/find_bit.zig", "andnot_scan_entrypoint_contract"): "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
    ("review_anchors", "tools/lib/find_bit.zig", "tail_word_set_skip_anchor"): 'test "tail-word next set scans skip earlier in-range matches before clamping"',
    ("review_anchors", "tools/lib/find_bit.zig", "tail_word_skip_anchor"): 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    ("review_anchors", "tools/lib/find_bit.zig", "tail_clamp_fixture_keys"): [
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last",
    ],
    ("review_anchors", "tools/lib/find_bit.zig", "tail_inclusive_boundary_fixture_keys"): [
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
    ],
    ("review_anchors", "tools/lib/find_bit.zig", "review_packet_summary"): "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
    ("review_anchors", "tools/lib/find_bit.zig", "next_safe_step_note"): "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",
}

FIXTURE_EXPECTATIONS = {
    ("find_bit", "inclusive_boundary_next"): 63,
    ("find_bit", "inclusive_boundary_zero"): 63,
    ("find_bit", "inclusive_boundary_and"): 63,
    ("find_bit", "tail_inclusive_boundary_next"): 68,
    ("find_bit", "tail_inclusive_boundary_zero"): 68,
    ("find_bit", "tail_inclusive_boundary_and"): 68,
    ("find_bit", "tail_clamped_first"): 67,
    ("find_bit", "tail_clamped_next"): 69,
    ("find_bit", "tail_zero_clamped_first"): 69,
    ("find_bit", "tail_zero_clamped_next"): 69,
    ("find_bit", "tail_and_clamped_first"): 67,
    ("find_bit", "tail_and_clamped_next"): 69,
    ("find_bit", "tail_clamped_last"): 67,
    ("find_bit", "tail_clamped_empty_last"): 69,
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(read_text(root, relative_path), object_pairs_hook=DuplicateTrackingDict)


def duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(duplicate_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for value in data:
            paths.extend(duplicate_paths(value, prefix))
    return paths


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def exact_count(text: str, needle: str) -> int:
    return text.count(needle)


def exact_line_count(text: str, needle: str) -> int:
    want = needle.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required = (
        HELPER_REL,
        MANIFEST_REL,
        FIXTURE_REL,
        LANE_NOTE_REL,
        CLOSURE_NOTE_REL,
        VALIDATOR_REL,
        REVIEW_CHECKER_REL,
    )
    for relative_path in required:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = read_text(root, HELPER_REL)
    lane_text = read_text(root, LANE_NOTE_REL)
    closure_text = read_text(root, CLOSURE_NOTE_REL)
    validator_text = read_text(root, VALIDATOR_REL)
    review_checker_text = read_text(root, REVIEW_CHECKER_REL)

    for marker in HELPER_MARKERS:
        count = exact_count(helper_text, marker)
        if count != 1:
            failures.append(f"helper:{marker}:expected=1:actual={count}")
    for line in LANE_LINES:
        count = exact_line_count(lane_text, line)
        if count != 1:
            failures.append(f"lane:{line}:expected=1:actual={count}")
    for label, marker in CLOSURE_MARKERS.items():
        count = exact_count(closure_text, marker)
        if count != 1:
            failures.append(f"closure:{label}:expected=1:actual={count}")
    for marker in VALIDATOR_MARKERS:
        count = exact_count(validator_text, marker)
        if count != 1:
            failures.append(f"validator:{marker}:expected=1:actual={count}")
    for marker in REVIEW_CHECKER_MARKERS:
        count = exact_count(review_checker_text, marker)
        if count != 1:
            failures.append(f"review_checker:{marker}:expected=1:actual={count}")

    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    dup_manifest = duplicate_paths(manifest)
    if dup_manifest:
        return [f"manifest:duplicate_json_key:{path}" for path in dup_manifest]
    for path, expected in MANIFEST_EXPECTATIONS.items():
        actual = nested_value(manifest, path)
        if actual != expected:
            failures.append(f"manifest:{'.'.join(path)}")

    try:
        fixture = load_json(root, FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [f"fixture:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    dup_fixture = duplicate_paths(fixture)
    if dup_fixture:
        return [f"fixture:duplicate_json_key:{path}" for path in dup_fixture]
    for path, expected in FIXTURE_EXPECTATIONS.items():
        actual = nested_value(fixture, path)
        if actual != expected:
            failures.append(f"fixture:{'.'.join(path)}")

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPER_REL, "\n".join(HELPER_MARKERS) + "\n")

    manifest: dict[str, object] = {"lane_sequencing": {}, "review_anchors": {"tools/lib/find_bit.zig": {}}}
    for path, value in MANIFEST_EXPECTATIONS.items():
        current = manifest
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")

    fixture: dict[str, object] = {"find_bit": {}}
    for path, value in FIXTURE_EXPECTATIONS.items():
        current = fixture
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")

    write_file(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(LANE_LINES) + "\n")
    write_file(root, CLOSURE_NOTE_REL, "# sample\n\n" + "\n".join(CLOSURE_MARKERS.values()) + "\n")
    write_file(root, VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_file(root, REVIEW_CHECKER_REL, "\n".join(REVIEW_CHECKER_MARKERS) + "\n")


def run_self_test() -> int:
    cases = [
        "baseline",
        "missing_helper_marker",
        "missing_lane_line",
        "missing_closure_marker",
        "missing_validator_marker",
        "missing_review_checker_marker",
        "manifest_drift",
        "fixture_drift",
        "manifest_duplicate_key",
        "fixture_invalid_json",
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-find-bit-closure-packet-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        if collect_failures(root):
            print("PHASE1_FIND_BIT_CLOSURE_PACKET_SELF_TEST=fail")
            return 1

        (root / HELPER_REL).write_text("\n".join(HELPER_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_helper_marker:expected_failure")
            return 1

        build_sample_repo(root)
        (root / LANE_NOTE_REL).writeText = None
        (root / LANE_NOTE_REL).write_text("# sample\n\n" + "\n".join(LANE_LINES[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_lane_line:expected_failure")
            return 1

        build_sample_repo(root)
        (root / CLOSURE_NOTE_REL).write_text("# sample\n\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_closure_marker:expected_failure")
            return 1

        build_sample_repo(root)
        (root / VALIDATOR_REL).write_text("\n".join(VALIDATOR_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_validator_marker:expected_failure")
            return 1

        build_sample_repo(root)
        (root / REVIEW_CHECKER_REL).write_text("\n".join(REVIEW_CHECKER_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_review_checker_marker:expected_failure")
            return 1

        build_sample_repo(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["tail_word_skip_anchor"] = "drift"
        (root / MANIFEST_REL).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:manifest_drift:expected_failure")
            return 1

        build_sample_repo(root)
        fixture = json.loads((root / FIXTURE_REL).read_text(encoding="utf-8"))
        fixture["find_bit"]["tail_inclusive_boundary_and"] = 0
        (root / FIXTURE_REL).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:fixture_drift:expected_failure")
            return 1

        build_sample_repo(root)
        manifest_text = (root / MANIFEST_REL).read_text(encoding="utf-8")
        (root / MANIFEST_REL).write_text(
            manifest_text.replace(
                '      "tail_word_skip_anchor": "test \\"tail-word next zero and shared scans skip earlier in-range matches before clamping\\"",',
                '      "tail_word_skip_anchor": "drift",\n      "tail_word_skip_anchor": "test \\"tail-word next zero and shared scans skip earlier in-range matches before clamping\\"",',
                1,
            ),
            encoding="utf-8",
        )
        if not collect_failures(root):
            print("self-test:manifest_duplicate_key:expected_failure")
            return 1

        build_sample_repo(root)
        (root / FIXTURE_REL).write_text("{\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:fixture_invalid_json:expected_failure")
            return 1

    print("PHASE1_FIND_BIT_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        help="write a sample marker-faithful repo root for focused replay",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_repo(Path(args.write_sample_root).resolve())
        print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_CLOSURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_CLOSURE_PACKET=pass")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_CLOSURE_NOTE={CLOSURE_NOTE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_VALIDATOR={VALIDATOR_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CLOSURE_PACKET_REVIEW_CHECKER={REVIEW_CHECKER_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

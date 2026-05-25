#!/usr/bin/env python3
"""Guard the current Phase 1 bitmap closure packet against reminder drift."""

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
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
DIRECT_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")

HELPER_MARKERS = [
    'test "bitmap range helpers preserve edges across whole-word spans"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap zero-bit logical helpers stay explicit"',
    'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    'test "bitmap tail-masked helpers ignore out-of-range differences"',
    'test "bitmap full empty and weight ignore out-of-range tail bits"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap or keeps caller-selected bit window"',
    'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
]

LANE_LINES = [
    "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`",
    "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
]

CLOSURE_MARKERS = [
    "A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route: keep `tools/lib/bitmap.zig` parked unless a fresh reread finds new direct-anchor drift inside the manifest-backed fill-tail clamp, copy-alias, cross-word `scnprintf()`, exact-word-boundary equality fast-path masking, empty-buffer, allocator-reset, zero-bit logical short-circuit, Linux-style alias mirror, caller-window or multiword-tail `xorBits()`/`orBits()` clamp witnesses, or weighted tail-count clamp, or drift in the already-committed bitmap replay fields summarized by the manifest; do not reopen older closure-side or validator-route cue names by default. Current `master` still spells those bitmap-local anchors in `tools/lib/bitmap.zig`, the committed helper manifest, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and the helper-local zero-bit logical test body no longer carries the one-argument `std.testing.expectEqual(...)` compile break that had briefly reopened this packet, so leave the helper parked unless one of those direct anchors or committed replay fields drifts.",
    "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",
    "`PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word without leaking out-of-range bits into the asserted view`",
    "`PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set, matching both the direct Zig unit test and the committed parity fixture`",
]

VALIDATOR_MARKERS = [
    "\"bitmap_direct_review\": \"`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`\",",
    "\"bitmap_unit_review\": \"`PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word without leaking out-of-range bits into the asserted view`\",",
    "\"bitmap_empty_unit_review\": \"`PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set, matching both the direct Zig unit test and the committed parity fixture`\",",
    "\"final_partial_word_anchor\": 'test \\\"bitmap range helpers preserve edges across whole-word spans\\\"',",
    "\"equal_fast_path_anchor\": 'test \\\"bitmap equal fast path ignores storage beyond an exact word boundary\\\"',",
    "\"or_window_anchor\": 'test \\\"bitmap or keeps caller-selected bit window\\\"',",
    "\"or_multiword_tail_anchor\": 'test \\\"bitmap or across a multiword tail still lets callers clamp the last word\\\"',",
    "\"weighted_tail_count_anchor\": 'test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\"',",
    "\"scnprintf_cross_word_anchor\": 'test \\\"bitmap scnprintf keeps contiguous ranges merged across word boundaries\\\"',",
    "\"empty_buffer_anchor\": 'test \\\"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\\\"',",
    "\"copy_raw_alias_anchor\": 'test \\\"bitmap copy alias preserves raw source words without tail clearing\\\"',",
    "\"zero_bit_noop_anchor\": 'test \\\"bitmap zero-bit logical helpers stay explicit\\\"',",
    "\"linux_alias_anchor\": 'test \\\"bitmap Linux-style aliases mirror copy logical range and format helpers\\\"',",
    "\"review_packet_summary\": \"shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.\",",
    "\"next_safe_step_note\": \"If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.\",",
]

DIRECT_CHECKER_MARKERS = [
    '"range_edges": \'test "bitmap range helpers preserve edges across whole-word spans" {\',',
    '"copy_raw_alias": \'test "bitmap copy alias preserves raw source words without tail clearing" {\',',
    '"copy_tail_extend_alias": \'test "bitmap copy aliases preserve tail clearing and extension semantics" {\',',
    '"zero_bit_logical": \'test "bitmap zero-bit logical helpers stay explicit" {\',',
    '"equal_fast_path": \'test "bitmap equal fast path ignores storage beyond an exact word boundary" {\',',
    '"xor_multiword_tail": \'test "bitmap xor across a multiword tail still lets callers clamp the last word" {\',',
    '"or_multiword_tail": \'test "bitmap or across a multiword tail still lets callers clamp the last word" {\',',
    '"scnprintf_cross_word": \'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries" {\',',
    '"scnprintf_empty_buffer": \'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap" {\',',
    '"linux_alias_copy_logic": \'test "bitmap Linux-style aliases mirror copy logical range and format helpers" {\',',
    'print("PHASE1_BITMAP_DIRECT_ANCHORS=pass")',
]

MANIFEST_EXPECTATIONS = {
    ("lane_sequencing", "direct_anchor_followup_helpers"): [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ],
    ("review_anchors", "tools/lib/bitmap.zig", "final_partial_word_anchor"): 'test "bitmap range helpers preserve edges across whole-word spans"',
    ("review_anchors", "tools/lib/bitmap.zig", "fill_tail_clamp_anchor"): 'test "bitmap full empty and weight ignore out-of-range tail bits"',
    ("review_anchors", "tools/lib/bitmap.zig", "equal_fast_path_anchor"): 'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    ("review_anchors", "tools/lib/bitmap.zig", "predicate_tail_mask_anchor"): 'test "bitmap tail-masked helpers ignore out-of-range differences"',
    ("review_anchors", "tools/lib/bitmap.zig", "or_window_anchor"): 'test "bitmap or keeps caller-selected bit window"',
    ("review_anchors", "tools/lib/bitmap.zig", "or_multiword_tail_anchor"): 'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    ("review_anchors", "tools/lib/bitmap.zig", "weighted_tail_count_anchor"): 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    ("review_anchors", "tools/lib/bitmap.zig", "scnprintf_cross_word_anchor"): 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    ("review_anchors", "tools/lib/bitmap.zig", "empty_buffer_anchor"): 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    ("review_anchors", "tools/lib/bitmap.zig", "copy_raw_alias_anchor"): 'test "bitmap copy alias preserves raw source words without tail clearing"',
    ("review_anchors", "tools/lib/bitmap.zig", "copy_zero_and_aligned_anchors"): [
        'test "bitmap copy and extend handles zero and aligned counts"',
        'test "bitmap copy helpers keep zero-sized destination views untouched"',
    ],
    ("review_anchors", "tools/lib/bitmap.zig", "zero_bit_noop_anchor"): 'test "bitmap zero-bit logical helpers stay explicit"',
    ("review_anchors", "tools/lib/bitmap.zig", "linux_alias_anchor"): 'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    ("review_anchors", "tools/lib/bitmap.zig", "review_packet_summary"): "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.",
    ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note"): "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.",
}

FIXTURE_EXPECTATIONS = {
    ("bitmap", "alloc_words"): 2,
    ("bitmap", "zalloc_values"): [0, 0],
    ("bitmap", "scnprintf"): "1-3,7,10-11",
    ("bitmap", "truncated_scnprintf_len"): 7,
    ("bitmap", "truncated_scnprintf"): "1-3,7,1",
    ("bitmap", "terminator_only_scnprintf_len"): 0,
    ("bitmap", "terminator_only_nul"): 0,
    ("bitmap", "zero_length_scnprintf_len"): 0,
    ("bitmap", "partial_xor_nbits"): 4,
    ("bitmap", "partial_xor_masked_values"): [14],
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


def require_once(text: str, prefix: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{prefix}:expected=1:actual={count}:{marker}"]


def require_lines(text: str, prefix: str, markers: list[str]) -> list[str]:
    failures: list[str] = []
    for marker in markers:
        failures.extend(require_once(text, prefix, marker))
    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required = (
        HELPER_REL,
        MANIFEST_REL,
        FIXTURE_REL,
        LANE_NOTE_REL,
        CLOSURE_NOTE_REL,
        VALIDATOR_REL,
        DIRECT_CHECKER_REL,
    )
    for relative_path in required:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    failures.extend(require_lines(read_text(root, HELPER_REL), "helper", HELPER_MARKERS))
    failures.extend(require_lines(read_text(root, LANE_NOTE_REL), "lane", LANE_LINES))
    failures.extend(require_lines(read_text(root, CLOSURE_NOTE_REL), "closure", CLOSURE_MARKERS))
    failures.extend(require_lines(read_text(root, VALIDATOR_REL), "validator", VALIDATOR_MARKERS))
    failures.extend(require_lines(read_text(root, DIRECT_CHECKER_REL), "direct_checker", DIRECT_CHECKER_MARKERS))

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
            failures.append(f"manifest:{'.'.join(path)}:expected={expected!r}:actual={actual!r}")

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
            failures.append(f"fixture:{'.'.join(path)}:expected={expected!r}:actual={actual!r}")

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPER_REL, "\n".join(HELPER_MARKERS) + "\n")
    write_file(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(LANE_LINES) + "\n")
    write_file(root, CLOSURE_NOTE_REL, "# sample\n\n" + "\n\n".join(CLOSURE_MARKERS) + "\n")
    write_file(root, VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_file(root, DIRECT_CHECKER_REL, "\n".join(DIRECT_CHECKER_MARKERS) + "\n")

    manifest: dict[str, object] = {"lane_sequencing": {}, "review_anchors": {"tools/lib/bitmap.zig": {}}}
    for path, value in MANIFEST_EXPECTATIONS.items():
        current: dict[str, object] = manifest
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")

    fixture: dict[str, object] = {"bitmap": {}}
    for path, value in FIXTURE_EXPECTATIONS.items():
        current = fixture
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-closure-packet-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        if collect_failures(root):
            print("PHASE1_BITMAP_CLOSURE_PACKET_SELF_TEST=fail")
            return 1
        case_count += 1

        helper_path = root / HELPER_REL
        helper_text = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(helper_text.replace(HELPER_MARKERS[0], "", 1), encoding="utf-8")
        if not any(failure.startswith("helper:") for failure in collect_failures(root)):
            print("self-test:missing_helper_marker:expected_failure")
            return 1
        case_count += 1
        helper_path.write_text(helper_text, encoding="utf-8")

        manifest_path = root / MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["equal_fast_path_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any(failure.startswith("manifest:review_anchors.tools/lib/bitmap.zig.equal_fast_path_anchor") for failure in collect_failures(root)):
            print("self-test:manifest_drift:expected_failure")
            return 1
        case_count += 1
        build_sample_repo(root)

        validator_path = root / VALIDATOR_REL
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(validator_text.replace(VALIDATOR_MARKERS[0], "", 1), encoding="utf-8")
        if not any(failure.startswith("validator:") for failure in collect_failures(root)):
            print("self-test:validator_drift:expected_failure")
            return 1
        case_count += 1

    print("PHASE1_BITMAP_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test cases")
    parser.add_argument("--write-sample-root", help="write a current-like sample repository to this path")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        build_sample_repo(root)
        print(f"PHASE1_BITMAP_CLOSURE_PACKET_SAMPLE_ROOT={root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BITMAP_CLOSURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BITMAP_CLOSURE_PACKET=pass")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_CLOSURE_NOTE={CLOSURE_NOTE_REL.as_posix()}")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_VALIDATOR={VALIDATOR_REL.as_posix()}")
    print(f"PHASE1_BITMAP_CLOSURE_PACKET_DIRECT_CHECKER={DIRECT_CHECKER_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

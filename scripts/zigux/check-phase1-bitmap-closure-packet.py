#!/usr/bin/env python3
"""Guard the current Phase 1 bitmap closure packet against helper, fixture, and reminder drift."""

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

HELPER_MARKERS = [
    'test "bitmap range helpers honor exact first-word boundaries"',
    'test "bitmap range helpers clamp the final partial word"',
    'test "bitmap fill clamps tail bits in partial words"',
    'test "bitmap predicates ignore out-of-range tail bits"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap zero-bit helpers stay explicit no-ops"',
    'test "bitmap Linux-style aliases mirror the primary helper surface"',
]

LANE_LINES = [
    "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`",
    "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`",
]

CLOSURE_PARAGRAPH = (
    "A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route: keep "
    "`tools/lib/bitmap.zig` parked unless a fresh reread finds new direct-anchor drift inside the "
    "manifest-backed fill-tail clamp, copy-alias, cross-word `scnprintf()`, exact-word-boundary equality "
    "fast-path masking, empty-buffer, allocator-reset, zero-bit logical short-circuit, Linux-style alias "
    "mirror, caller-window or multiword-tail `xorBits()`/`orBits()` clamp witnesses, or weighted tail-count "
    "clamp, or drift in the already-committed bitmap replay fields summarized by the manifest; do not reopen "
    "older closure-side or validator-route cue names by default. Current `master` still spells those "
    "bitmap-local anchors in `tools/lib/bitmap.zig`, the committed helper manifest, and "
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and the helper-local zero-bit logical test "
    "body no longer carries the one-argument `std.testing.expectEqual(...)` compile break that had briefly "
    "reopened this packet, so leave the helper parked unless one of those direct anchors or committed replay "
    "fields drifts."
)

MANIFEST_EXPECTATIONS = {
    ("lane_sequencing", "direct_anchor_followup_helpers"): [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ],
    ("review_anchors", "tools/lib/bitmap.zig", "first_word_boundary_anchor"): 'test "bitmap range helpers honor exact first-word boundaries"',
    ("review_anchors", "tools/lib/bitmap.zig", "final_partial_word_anchor"): 'test "bitmap range helpers clamp the final partial word"',
    ("review_anchors", "tools/lib/bitmap.zig", "fill_tail_clamp_anchor"): 'test "bitmap fill clamps tail bits in partial words"',
    ("review_anchors", "tools/lib/bitmap.zig", "predicate_tail_mask_anchor"): 'test "bitmap predicates ignore out-of-range tail bits"',
    ("review_anchors", "tools/lib/bitmap.zig", "copy_raw_alias_anchor"): 'test "bitmap copy alias preserves raw source words without tail clearing"',
    ("review_anchors", "tools/lib/bitmap.zig", "scnprintf_cross_word_anchor"): 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
    ("review_anchors", "tools/lib/bitmap.zig", "empty_buffer_anchor"): 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    ("review_anchors", "tools/lib/bitmap.zig", "zero_bit_noop_anchor"): 'test "bitmap zero-bit helpers stay explicit no-ops"',
    ("review_anchors", "tools/lib/bitmap.zig", "linux_alias_anchor"): 'test "bitmap Linux-style aliases mirror the primary helper surface"',
    ("review_anchors", "tools/lib/bitmap.zig", "review_packet_summary"): "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer, and partial-window xor replay, while helper-local anchors keep zero-size allocator and free-null behavior, predicate tail-mask, first-word boundary, final-partial range boundary, fill tail-clamp, cross-word scnprintf collapse, empty-bitmap caller-buffer preservation, copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master",
    ("review_anchors", "tools/lib/bitmap.zig", "next_safe_step_note"): "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen the already-closed closure-validator or validator-summary packets by default.",
}

FIXTURE_EXPECTATIONS = {
    ("bitmap", "scnprintf"): "1-3,7,10-11",
    ("bitmap", "truncated_scnprintf"): "1-3,7,1",
    ("bitmap", "alloc_words"): 2,
    ("bitmap", "zalloc_values"): [0, 0],
    ("bitmap", "copy_clear_tail_values"): [18446744073709551615, 31],
    ("bitmap", "partial_xor_masked_values"): [14],
    ("bitmap", "range_after_set"): [14, 12, 0],
    ("bitmap", "full_after_fill"): True,
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
    required = (HELPER_REL, MANIFEST_REL, FIXTURE_REL, LANE_NOTE_REL, CLOSURE_NOTE_REL)
    for relative_path in required:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = read_text(root, HELPER_REL)
    lane_text = read_text(root, LANE_NOTE_REL)
    closure_text = read_text(root, CLOSURE_NOTE_REL)

    for marker in HELPER_MARKERS:
        count = exact_count(helper_text, marker)
        if count != 1:
            failures.append(f"helper:{marker}:expected=1:actual={count}")
    for line in LANE_LINES:
        count = exact_line_count(lane_text, line)
        if count != 1:
            failures.append(f"lane:{line}:expected=1:actual={count}")
    count = exact_count(closure_text, CLOSURE_PARAGRAPH)
    if count != 1:
        failures.append(f"closure:bitmap_tie_breaker:expected=1:actual={count}")

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
    manifest: dict[str, object] = {"lane_sequencing": {}, "review_anchors": {"tools/lib/bitmap.zig": {}}}
    for path, value in MANIFEST_EXPECTATIONS.items():
        current = manifest
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
    write_file(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(LANE_LINES) + "\n")
    write_file(root, CLOSURE_NOTE_REL, "# sample\n\n" + CLOSURE_PARAGRAPH + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-closure-packet-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        if collect_failures(root):
            print("PHASE1_BITMAP_CLOSURE_PACKET_SELF_TEST=fail")
            return 1
        (root / HELPER_REL).write_text("", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_helper_markers:expected_failure")
            return 1
    print("PHASE1_BITMAP_CLOSURE_PACKET_SELF_TEST=pass")
    print("PHASE1_BITMAP_CLOSURE_PACKET_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

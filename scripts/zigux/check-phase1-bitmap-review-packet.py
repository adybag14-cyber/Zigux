#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")
BITMAP_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BITMAP_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")

EXPECTED_BITMAP_MANIFEST = {
    "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
    "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
    "predicate_tail_mask_anchor": 'test "bitmap predicates ignore out-of-range tail bits"',
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "review_packet_summary": "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, scnprintf output, tiny-buffer, and partial-window xor replay, while helper-local anchors keep zero-size allocator and free-null behavior, predicate tail-mask, first-word and final-partial range boundaries, cross-word scnprintf collapse, truncation, copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, zero-bit no-op, zero-bit binary identity, and Linux-style alias behavior review-visible on current master",
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
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
    "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
}

EXPECTED_BITMAP_CLOSURE_MARKERS = [
    "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
    "PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW=helper-local bitmap predicate tail-mask proof stays explicit through the direct bitmap test anchor so equal, intersects, and subset ignore out-of-range tail bits instead of treating tail noise as live data",
    "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it",
    "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
    "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
    "PHASE1_BITMAP_EMPTY_BUFFER_REVIEW=helper-local bitmap.scnprintf empty-bitmap caller-buffer preservation stays explicit through the direct bitmap test anchor so a non-empty caller buffer remains untouched when no bits are set instead of being silently zeroed or NUL-terminated",
    "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
    "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
    "PHASE1_BITMAP_COPY_ZERO_AND_ALIGNED_REVIEW=helper-local bitmap zero-sized and aligned copy proof stays explicit through the direct bitmap test anchors so zero-sized destination views remain untouched and aligned-word copies preserve raw aligned words while zero-filling only the requested extension space",
    "PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes",
    "PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor so zero-bit windows keep binary helpers in identity or empty-result mode without touching caller-visible storage or inventing overlap, subset, or equality drift",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface",
]

FIXTURE_BITMAP_TESTS = [
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap allocator helpers size zero and free their buffers"',
    'test "bitmap size aliases round bit counts to full words in bytes"',
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap range helpers honor exact first-word boundaries"',
    'test "bitmap range helpers clamp the final partial word"',
    'test "bitmap fill clamps tail bits in partial words"',
    'test "bitmap and andnot equal intersects subset"',
    'test "bitmap and andnot clamp tail bits in partial words"',
    'test "bitmap complement clamps tail bits and alias mirrors the primary helper"',
    'test "bitmap predicates ignore out-of-range tail bits"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
    'test "bitmap scnprintf reports full length while truncating the buffer"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap copy and extend leaves words past the requested size untouched"',
    'test "bitmap zero-bit helpers stay explicit no-ops"',
    'test "bitmap zero-bit binary helpers stay explicit identity operations"',
    'test "bitmap Linux-style aliases keep zero-bit windows explicit no-ops"',
    'test "bitmap Linux-style aliases mirror the primary helper surface"',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def extract_zig_test_names(text: str) -> list[str]:
    names: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('test "'):
            continue
        closing_quote = stripped.find('"', len('test "'))
        if closing_quote == -1:
            continue
        names.append(stripped[: closing_quote + 1])
    return names


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in (BITMAP_HELPER_REL, BITMAP_MANIFEST_REL, BITMAP_CLOSURE_REL):
        if not (root / relative_path).exists():
            missing.append(str(relative_path))
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    manifest = load_json(root, BITMAP_MANIFEST_REL)
    closure_text = load_text(root, BITMAP_CLOSURE_REL)
    bitmap_text = load_text(root, BITMAP_HELPER_REL)

    if not isinstance(manifest, dict):
        return ["bitmap_manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["bitmap_manifest:review_anchors"]

    bitmap_anchors = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_anchors, dict):
        return ["bitmap_manifest:tools/lib/bitmap.zig"]

    missing: list[str] = []
    helper_test_anchors = extract_zig_test_names(bitmap_text)
    if not helper_test_anchors:
        missing.append("bitmap_manifest:helper_test_anchors_source")
    elif bitmap_anchors.get("helper_test_anchors") != helper_test_anchors:
        missing.append("bitmap_manifest:helper_test_anchors")

    for key, expected in EXPECTED_BITMAP_MANIFEST.items():
        if bitmap_anchors.get(key) != expected:
            missing.append(f"bitmap_manifest:{key}")

    for marker in EXPECTED_BITMAP_CLOSURE_MARKERS:
        if marker not in closure_text:
            missing.append(f"bitmap_closure:{marker}")

    return missing


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_bitmap_fixture_source(test_names: list[str]) -> str:
    return "\n".join(f"{name} {{}}" for name in test_names) + "\n"


def make_fixture_root(root: Path) -> None:
    manifest = {
        "review_anchors": {
            "tools/lib/bitmap.zig": {
                "helper_test_anchors": FIXTURE_BITMAP_TESTS,
                **EXPECTED_BITMAP_MANIFEST,
            }
        }
    }
    write_text(root, BITMAP_HELPER_REL, make_bitmap_fixture_source(FIXTURE_BITMAP_TESTS))
    write_text(root, BITMAP_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
    write_text(root, BITMAP_CLOSURE_REL, "\n".join(EXPECTED_BITMAP_CLOSURE_MARKERS) + "\n")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bitmap_review_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        (root / BITMAP_HELPER_REL).unlink()
        assert str(BITMAP_HELPER_REL) in collect_missing_files(root)
        case_count += 1
        make_fixture_root(root)

        helper_path = root / BITMAP_HELPER_REL
        helper_text = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(helper_text.replace(FIXTURE_BITMAP_TESTS[-1] + " {}\n", "", 1), encoding="utf-8")
        assert "bitmap_manifest:helper_test_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / BITMAP_MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["predicate_tail_mask_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "bitmap_manifest:predicate_tail_mask_anchor" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["helper_test_anchors"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "bitmap_manifest:helper_test_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        closure_path = root / BITMAP_CLOSURE_REL
        closure_text = closure_path.read_text(encoding="utf-8")
        missing_marker = EXPECTED_BITMAP_CLOSURE_MARKERS[0]
        closure_path.write_text(closure_text.replace(missing_marker + "\n", "", 1), encoding="utf-8")
        assert f"bitmap_closure:{missing_marker}" in collect_missing_markers(root)
        case_count += 1

    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 1 bitmap review packet.")
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BITMAP_REVIEW_PACKET=fail")
        print("MISSING_PHASE1_BITMAP_REVIEW_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BITMAP_REVIEW_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_BITMAP_REVIEW_PACKET=fail")
        print("MISSING_PHASE1_BITMAP_REVIEW_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_BITMAP_REVIEW_MARKERS_END")
        return 1

    print("PHASE1_BITMAP_REVIEW_PACKET=pass")
    print(f"PHASE1_BITMAP_REVIEW_FILE_COUNT=3")
    print(
        "PHASE1_BITMAP_REVIEW_MARKER_COUNT="
        f"{len(EXPECTED_BITMAP_MANIFEST) + len(EXPECTED_BITMAP_CLOSURE_MARKERS) + 1}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

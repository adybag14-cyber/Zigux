#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


_SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase1-closure.md",
    "tools/lib/bitmap.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_helpers.zig",
]

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
    "PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary",
    "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
    "PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes",
    "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
    "PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics",
]

REQUIRED_BITMAP_TEST_ANCHORS = [
    'test "bitmap allocator helpers size zero and free their buffers"',
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap fill clamps tail bits in partial words"',
    'test "bitmap and andnot equal intersects subset"',
    'test "bitmap and andnot clamp tail bits in partial words"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap scnprintf collapses contiguous ranges"',
    'test "bitmap scnprintf reports full length while truncating the buffer"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap zero-bit helpers stay explicit no-ops"',
    'test "bitmap range helpers honor exact first-word boundaries"',
]

REQUIRED_PHASE1_HELPERS_REPLAY_MARKERS = [
    "fixture.bitmap.partial_xor_nbits",
    "fixture.bitmap.partial_xor_masked_values",
    "fixture.bitmap.scnprintf",
    "fixture.bitmap.truncated_scnprintf_len",
    "fixture.bitmap.truncated_scnprintf,",
    "fixture.bitmap.terminator_only_scnprintf_len",
    "fixture.bitmap.terminator_only_nul",
    "fixture.bitmap.zero_length_scnprintf_len",
]

EXPECTED_BITMAP_REVIEW_ANCHORS = {
    "helper_test_anchors": [
        'test "bitmap allocator helpers size zero and free their buffers"',
        'test "bitmap set clear weight and empty full helpers"',
        'test "bitmap fill clamps tail bits in partial words"',
        'test "bitmap and andnot equal intersects subset"',
        'test "bitmap and andnot clamp tail bits in partial words"',
        'test "bitmap xor keeps caller-selected bit window"',
        'test "bitmap scnprintf collapses contiguous ranges"',
        'test "bitmap scnprintf reports full length while truncating the buffer"',
        'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
        'test "bitmap copy aliases preserve tail clearing and extension semantics"',
        'test "bitmap zero-bit helpers stay explicit no-ops"',
    ],
    "first_word_boundary_anchor": 'test "bitmap range helpers honor exact first-word boundaries"',
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "parity_fixture_keys": [
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
}


def repo_root_from_arg(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        actual_count = text.count(marker)
        if actual_count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={actual_count}")
    return missing


def collect_bitmap_manifest_mismatches(root: Path) -> list[str]:
    manifest_path = root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        return ["phase1_bitmap_manifest:manifest:expected=dict:actual=non-object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["phase1_bitmap_manifest:review_anchors:expected=dict:actual=missing"]

    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review, dict):
        return ["phase1_bitmap_manifest:tools/lib/bitmap.zig:expected=dict:actual=missing"]

    mismatches: list[str] = []
    for field, expected_value in EXPECTED_BITMAP_REVIEW_ANCHORS.items():
        if bitmap_review.get(field) != expected_value:
            mismatches.append(f"phase1_bitmap_manifest:value={field}")

    for field in bitmap_review:
        if field not in EXPECTED_BITMAP_REVIEW_ANCHORS:
            mismatches.append(f"phase1_bitmap_manifest:unexpected_field={field}")

    return mismatches


def collect_missing_markers(root: Path) -> list[str]:
    closure = (root / "Documentation" / "zigux" / "phase1-closure.md").read_text(encoding="utf-8")
    bitmap = (root / "tools" / "lib" / "bitmap.zig").read_text(encoding="utf-8")
    replay = (root / "zigux" / "tests" / "phase1_helpers.zig").read_text(encoding="utf-8")

    missing: list[str] = []
    missing.extend(collect_exact_count_markers(closure, "closure_marker", REQUIRED_CLOSURE_MARKERS))
    missing.extend(collect_exact_count_markers(bitmap, "bitmap_test_anchor", REQUIRED_BITMAP_TEST_ANCHORS))
    missing.extend(
        collect_exact_count_markers(
            replay,
            "phase1_bitmap_replay_marker",
            REQUIRED_PHASE1_HELPERS_REPLAY_MARKERS,
        )
    )
    missing.extend(collect_bitmap_manifest_mismatches(root))
    return missing


def make_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")

    (tmp_root / "Documentation/zigux/phase1-closure.md").write_text(
        "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n",
        encoding="utf-8",
    )
    (tmp_root / "tools/lib/bitmap.zig").write_text(
        "\n".join(REQUIRED_BITMAP_TEST_ANCHORS) + "\n",
        encoding="utf-8",
    )
    (tmp_root / "zigux/tests/phase1_helpers.zig").write_text(
        "\n".join(REQUIRED_PHASE1_HELPERS_REPLAY_MARKERS) + "\n",
        encoding="utf-8",
    )

    manifest_path = tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"review_anchors": {"tools/lib/bitmap.zig": EXPECTED_BITMAP_REVIEW_ANCHORS}}, indent=2) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bitmap_review_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_fixture_root(tmp_root)
        assert collect_missing_files(tmp_root) == []
        assert collect_missing_markers(tmp_root) == []

        closure_path = tmp_root / "Documentation/zigux/phase1-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8").replace(
            REQUIRED_CLOSURE_MARKERS[3] + "\n",
            "",
            1,
        )
        closure_path.write_text(closure_text, encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert f"closure_marker:{REQUIRED_CLOSURE_MARKERS[3]}:expected=1:actual=0" in missing

        make_fixture_root(tmp_root)
        bitmap_path = tmp_root / "tools/lib/bitmap.zig"
        bitmap_text = bitmap_path.read_text(encoding="utf-8").replace(
            REQUIRED_BITMAP_TEST_ANCHORS[10] + "\n",
            "",
            1,
        )
        bitmap_path.write_text(bitmap_text, encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert (
            'bitmap_test_anchor:test "bitmap copy alias preserves raw source words without tail clearing":expected=1:actual=0'
            in missing
        )

        make_fixture_root(tmp_root)
        replay_path = tmp_root / "zigux/tests/phase1_helpers.zig"
        replay_text = replay_path.read_text(encoding="utf-8").replace(
            "fixture.bitmap.terminator_only_nul\n",
            "",
            1,
        )
        replay_path.write_text(replay_text, encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_bitmap_replay_marker:fixture.bitmap.terminator_only_nul:expected=1:actual=0" in missing

        make_fixture_root(tmp_root)
        manifest_path = tmp_root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/bitmap.zig"]["copy_raw_alias_anchor"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_bitmap_manifest:value=copy_raw_alias_anchor" in missing

        make_fixture_root(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["parity_fixture_keys"] = manifest["review_anchors"][
            "tools/lib/bitmap.zig"
        ]["parity_fixture_keys"][:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "phase1_bitmap_manifest:value=parity_fixture_keys" in missing

    print("PHASE1_BITMAP_REVIEW_ANCHOR_CHECK_SELF_TEST=pass")
    print("PHASE1_BITMAP_REVIEW_ANCHOR_CHECK_SELF_TEST_CASE_COUNT=6")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 1 bitmap review-anchor packet against the live helper, replay, and manifest surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BITMAP_REVIEW_ANCHOR_CHECK=fail")
        print("MISSING_PHASE1_BITMAP_REVIEW_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BITMAP_REVIEW_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_BITMAP_REVIEW_ANCHOR_CHECK=fail")
        print("MISSING_PHASE1_BITMAP_REVIEW_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_BITMAP_REVIEW_MARKERS_END")
        return 1

    print("PHASE1_BITMAP_REVIEW_ANCHOR_CHECK=pass")
    print(f"PHASE1_BITMAP_REVIEW_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BITMAP_REVIEW_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS) + len(REQUIRED_BITMAP_TEST_ANCHORS) + len(REQUIRED_PHASE1_HELPERS_REPLAY_MARKERS) + len(EXPECTED_BITMAP_REVIEW_ANCHORS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

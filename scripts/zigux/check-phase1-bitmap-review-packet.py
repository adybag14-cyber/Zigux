#!/usr/bin/env python3
"""Validate the direct Phase 1 bitmap review packet across manifest and tests."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


BITMAP_HELPER = Path("tools/lib/bitmap.zig")
PHASE1_HELPERS = Path("zigux/tests/phase1_helpers.zig")
MANIFEST = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
MANIFEST_KEY = "tools/lib/bitmap.zig"
REPLAY_ANCHOR = 'test "phase 1 helper ports match committed parity fixture"'
REVIEW_PACKET_SUMMARY = (
    "shared Phase 1 fixture keys now own bitmap scnprintf output, tiny-buffer, "
    "and partial-window xor replay, while helper-local anchors keep allocator "
    "sizing and zero-fill behavior, predicate tail-mask, first-word and "
    "final-partial range boundaries, cross-word scnprintf collapse, truncation, "
    "copy alias, raw copy alias, zero-and-aligned copy-and-extend behavior, "
    "zero-sized destination-view, zero-bit no-op, zero-bit binary identity, and "
    "Linux-style alias behavior review-visible on current master"
)
REQUIRED_HELPER_TEST_ANCHORS = (
    'test "bitmap set clear weight and empty full helpers"',
    'test "bitmap range helpers clamp the final partial word"',
    'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
    'test "bitmap scnprintf reports full length while truncating the buffer"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap zero-bit helpers stay explicit no-ops"',
    'test "bitmap zero-bit binary helpers stay explicit identity operations"',
    'test "bitmap Linux-style aliases mirror the primary helper surface"',
)
REQUIRED_MANIFEST_FIELDS = {
    "phase1_helper_replay_anchor": REPLAY_ANCHOR,
    "review_packet_summary": REVIEW_PACKET_SUMMARY,
    "final_partial_word_anchor": 'test "bitmap range helpers clamp the final partial word"',
    "cross_word_scnprintf_anchor": 'test "bitmap scnprintf collapses contiguous ranges across word boundaries"',
    "scnprintf_truncation_anchor": 'test "bitmap scnprintf reports full length while truncating the buffer"',
    "copy_alias_anchor": 'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "copy_extend_zero_aligned_anchor": 'test "bitmap copy and extend handles zero and aligned counts"',
    "zero_sized_destination_view_anchor": 'test "bitmap copy helpers keep zero-sized destination views untouched"',
    "zero_bit_noop_anchor": 'test "bitmap zero-bit helpers stay explicit no-ops"',
    "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit binary helpers stay explicit identity operations"',
    "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror the primary helper surface"',
}


def repo_root_from(value: str | None) -> Path:
    if value is not None:
        return Path(value).resolve()
    return Path(__file__).resolve().parents[2]


def load_manifest(repo_root: Path) -> dict:
    manifest_text = (repo_root / MANIFEST).read_text(encoding="utf-8")
    return json.loads(manifest_text)


def exact_count(text: str, needle: str) -> int:
    return text.count(needle)


def check_repo(repo_root: Path) -> list[str]:
    problems: list[str] = []

    manifest = load_manifest(repo_root)
    anchors = manifest.get("review_anchors", {}).get(MANIFEST_KEY)
    if not isinstance(anchors, dict):
        return [f"missing manifest review packet for {MANIFEST_KEY}"]

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = anchors.get(field)
        if actual != expected:
            problems.append(
                f"manifest field {field!r} mismatch: expected {expected!r}, actual {actual!r}"
            )

    helper_test_anchors = anchors.get("helper_test_anchors")
    if not isinstance(helper_test_anchors, list):
        problems.append("manifest field 'helper_test_anchors' is missing or not a list")
    else:
        for anchor in REQUIRED_HELPER_TEST_ANCHORS:
            count = helper_test_anchors.count(anchor)
            if count != 1:
                problems.append(
                    f"manifest helper_test_anchors entry {anchor!r} expected exactly once, found {count}"
                )

    bitmap_text = (repo_root / BITMAP_HELPER).read_text(encoding="utf-8")
    for anchor in REQUIRED_HELPER_TEST_ANCHORS:
        count = exact_count(bitmap_text, anchor)
        if count != 1:
            problems.append(
                f"{BITMAP_HELPER} anchor {anchor!r} expected exactly once, found {count}"
            )

    helpers_text = (repo_root / PHASE1_HELPERS).read_text(encoding="utf-8")
    replay_count = exact_count(helpers_text, REPLAY_ANCHOR)
    if replay_count != 1:
        problems.append(
            f"{PHASE1_HELPERS} replay anchor {REPLAY_ANCHOR!r} expected exactly once, found {replay_count}"
        )

    return problems


def expect_clean(repo_root: Path) -> None:
    problems = check_repo(repo_root)
    if problems:
        raise AssertionError(f"expected clean packet, found: {problems}")


def write_repo(root: Path) -> None:
    (root / BITMAP_HELPER.parent).mkdir(parents=True, exist_ok=True)
    (root / PHASE1_HELPERS.parent).mkdir(parents=True, exist_ok=True)
    (root / MANIFEST.parent).mkdir(parents=True, exist_ok=True)

    (root / BITMAP_HELPER).write_text(
        "\n".join(REQUIRED_HELPER_TEST_ANCHORS) + "\n",
        encoding="utf-8",
    )
    (root / PHASE1_HELPERS).write_text(REPLAY_ANCHOR + "\n", encoding="utf-8")
    (root / MANIFEST).write_text(
        json.dumps(
            {
                "review_anchors": {
                    MANIFEST_KEY: {
                        "helper_test_anchors": list(REQUIRED_HELPER_TEST_ANCHORS),
                        **REQUIRED_MANIFEST_FIELDS,
                    }
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_repo(root)

        expect_clean(root)
        cases += 1

        manifest = load_manifest(root)
        manifest["review_anchors"][MANIFEST_KEY]["review_packet_summary"] = "stale"
        (root / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        problems = check_repo(root)
        assert any("review_packet_summary" in problem for problem in problems)
        cases += 1

        write_repo(root)
        bitmap_path = root / BITMAP_HELPER
        bitmap_text = bitmap_path.read_text(encoding="utf-8")
        bitmap_path.write_text(
            bitmap_text.replace(REQUIRED_HELPER_TEST_ANCHORS[2] + "\n", "", 1),
            encoding="utf-8",
        )
        problems = check_repo(root)
        assert any("cross word" in problem.lower() or "cross-word" in problem.lower() for problem in problems)
        cases += 1

        write_repo(root)
        helpers_path = root / PHASE1_HELPERS
        helpers_path.write_text("", encoding="utf-8")
        problems = check_repo(root)
        assert any("replay anchor" in problem for problem in problems)
        cases += 1

        write_repo(root)
        manifest = load_manifest(root)
        manifest["review_anchors"][MANIFEST_KEY]["helper_test_anchors"] = list(REQUIRED_HELPER_TEST_ANCHORS[:-1])
        (root / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        problems = check_repo(root)
        assert any("helper_test_anchors entry" in problem for problem in problems)
        cases += 1

    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = repo_root_from(args.repo_root)
    problems = check_repo(repo_root)
    if problems:
        for problem in problems:
            print(problem)
        return 1

    print("phase1 bitmap review packet is aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

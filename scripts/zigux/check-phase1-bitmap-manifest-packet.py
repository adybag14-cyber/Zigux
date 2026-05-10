#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
]

EXPECTED_LANE_DIRECT_ANCHOR_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_LANE_SHARED_REPLAY_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_BITMAP_REVIEW_ANCHORS = {
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "review_packet_summary": (
        "shared Phase 1 fixture keys now own bitmap scnprintf output, tiny-buffer, and partial-window xor replay, "
        "while helper-local anchors keep allocator sizing and zero-fill behavior, predicate tail-mask, first-word "
        "and final-partial range boundaries, cross-word scnprintf collapse, truncation, copy alias, raw copy alias, "
        "zero-and-aligned copy-and-extend behavior, zero-sized destination-view, zero-bit no-op, zero-bit binary "
        "identity, and Linux-style alias behavior review-visible on current master"
    ),
}

EXPECTED_DOC_MARKERS = [
    "### Direct-Anchor Follow-Up Helpers",
    "- `tools/lib/bitmap.zig`",
    "- `tools/lib/find_bit.zig`",
    "- `tools/lib/rbtree.zig`",
    "- `tools/lib/string.zig`",
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
]


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]



def collect_doc_issues(text: str) -> list[str]:
    issues: list[str] = []
    for marker in EXPECTED_DOC_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(f"phase1_lane_doc:{marker}:expected=1:actual={count}")
    return issues



def collect_manifest_issues(manifest: dict[str, object]) -> list[str]:
    issues: list[str] = []

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return ["phase1_manifest:lane_sequencing"]

    direct_helpers = lane_sequencing.get("direct_anchor_followup_helpers")
    shared_helpers = lane_sequencing.get("shared_replay_parked_helpers")

    if direct_helpers != EXPECTED_LANE_DIRECT_ANCHOR_HELPERS:
        issues.append("phase1_manifest:direct_anchor_followup_helpers")
    if shared_helpers != EXPECTED_LANE_SHARED_REPLAY_HELPERS:
        issues.append("phase1_manifest:shared_replay_parked_helpers")

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return issues + ["phase1_manifest:review_anchors"]

    bitmap_review = review_anchors.get("tools/lib/bitmap.zig")
    if not isinstance(bitmap_review, dict):
        return issues + ["phase1_manifest:review_anchors:tools/lib/bitmap.zig"]

    for field, expected in EXPECTED_BITMAP_REVIEW_ANCHORS.items():
        actual = bitmap_review.get(field)
        if actual != expected:
            issues.append(f"phase1_manifest:tools/lib/bitmap.zig:{field}")

    return issues



def validate_root(root: Path) -> list[str]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return [f"missing_file:{item}" for item in missing_files]

    lane_doc = (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").read_text(encoding="utf-8")
    manifest = json.loads((root / "zigux/tests/fixtures/phase1_helper_manifest.json").read_text(encoding="utf-8"))

    issues: list[str] = []
    issues.extend(collect_doc_issues(lane_doc))
    issues.extend(collect_manifest_issues(manifest))
    return issues



def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def build_self_test_root(root: Path) -> None:
    write_text(
        root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        "\n".join(
            [
                "# Phase 1 Host-Helper Lane Sequencing",
                "",
                "### Direct-Anchor Follow-Up Helpers",
                "",
                "- `tools/lib/bitmap.zig`",
                "- `tools/lib/find_bit.zig`",
                "- `tools/lib/rbtree.zig`",
                "- `tools/lib/string.zig`",
                "",
                "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
                "",
            ]
        ),
    )
    write_text(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "lane_sequencing": {
                    "direct_anchor_followup_helpers": EXPECTED_LANE_DIRECT_ANCHOR_HELPERS,
                    "shared_replay_parked_helpers": EXPECTED_LANE_SHARED_REPLAY_HELPERS,
                },
                "review_anchors": {
                    "tools/lib/bitmap.zig": EXPECTED_BITMAP_REVIEW_ANCHORS,
                },
            },
            indent=2,
        )
        + "\n",
    )



def run_self_test() -> int:
    case_count = 0

    def expect(issues: list[str], *expected: str) -> None:
        nonlocal case_count
        for item in expected:
            assert item in issues
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1_bitmap_manifest_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []

        (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").unlink()
        expect(
            validate_root(root),
            "missing_file:Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        )

        build_self_test_root(root)
        write_text(root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md", "")
        expect(
            validate_root(root),
            "phase1_lane_doc:### Direct-Anchor Follow-Up Helpers:expected=1:actual=0",
            "phase1_lane_doc:- `tools/lib/bitmap.zig`:expected=1:actual=0",
        )

        build_self_test_root(root)
        manifest = json.loads((root / "zigux/tests/fixtures/phase1_helper_manifest.json").read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = EXPECTED_LANE_DIRECT_ANCHOR_HELPERS[:-1]
        write_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect(validate_root(root), "phase1_manifest:direct_anchor_followup_helpers")

        build_self_test_root(root)
        manifest = json.loads((root / "zigux/tests/fixtures/phase1_helper_manifest.json").read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"].pop("phase1_helper_replay_anchor")
        write_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect(validate_root(root), "phase1_manifest:tools/lib/bitmap.zig:phase1_helper_replay_anchor")

        build_self_test_root(root)
        manifest = json.loads((root / "zigux/tests/fixtures/phase1_helper_manifest.json").read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/bitmap.zig"]["review_packet_summary"] = "stale summary"
        write_text(root / "zigux/tests/fixtures/phase1_helper_manifest.json", json.dumps(manifest, indent=2) + "\n")
        expect(validate_root(root), "phase1_manifest:tools/lib/bitmap.zig:review_packet_summary")

    print("PHASE1_BITMAP_MANIFEST_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_MANIFEST_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 1 bitmap manifest packet and lane split stay aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage without repo files.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE1_BITMAP_MANIFEST_PACKET=fail")
        print("PHASE1_BITMAP_MANIFEST_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_BITMAP_MANIFEST_PACKET_ISSUES_END")
        return 1

    print("PHASE1_BITMAP_MANIFEST_PACKET=pass")
    print(
        "PHASE1_BITMAP_MANIFEST_PACKET_MARKER_COUNT="
        f"{len(EXPECTED_DOC_MARKERS) + len(EXPECTED_LANE_DIRECT_ANCHOR_HELPERS) + len(EXPECTED_LANE_SHARED_REPLAY_HELPERS) + len(EXPECTED_BITMAP_REVIEW_ANCHORS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

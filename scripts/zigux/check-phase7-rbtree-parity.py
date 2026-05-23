#!/usr/bin/env python3
"""Validate the current Phase 7 rbtree helper-local packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-rbtree-direct-anchor-note.md",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "lib/rbtree.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "zigux/Makefile",
]

NEXT_STEP_WRAPPER_MARKER = (
    "narrowing the next same-lane follow-up to whether dedicated "
    "`phase7-rbtree-test:` or `phase7-rbtree-survey:` wrappers materialize on current `master`"
)

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-rbtree-slice.md": [
        "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_fixture_harness_anchor`",
        "`PHASE7_LANE_KEY=P7-L13`",
        "`lib/rbtree.zig`",
        "`tools/lib/rbtree.zig`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        "helper-local implementation now remains rooted at `lib/rbtree.zig`",
    ],
    "Documentation/zigux/phase7-rbtree-direct-anchor-note.md": [
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "Machine-readable fallback provenance stays explicit through `public_fallback_non_owner_paths`",
        "Fresh authenticated GitHub reread in this slot directly returned:",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
    ],
    "scripts/zigux/check-phase7-rbtree-parity.py": [
        "PHASE7_RBTREE_PARITY=pass",
        "PHASE7_RBTREE_PARITY=fail",
        "PHASE7_RBTREE_PARITY_SELF_TEST=pass",
        "MISSING_PHASE7_RBTREE_FILES_START",
        "MISSING_PHASE7_RBTREE_FILES_END",
        "MISSING_PHASE7_RBTREE_MARKERS_START",
        "MISSING_PHASE7_RBTREE_MARKERS_END",
        '"zigux/tests/fixtures/phase7_rbtree.json": [',
        '"zigux/tests/fixtures/phase7_rbtree_c_harness.c": [',
        "NEXT_STEP_WRAPPER_MARKER = (",
    ],
    "lib/rbtree.zig": [
        "pub const Node = struct {",
        "pub const RootCached = struct {",
        "pub fn rb_find_add_cached",
        "pub fn eraseInit(node: *Node, root: *Root) void {",
        "pub fn rb_next_postorder",
    ],
    "zigux/tests/phase7_rbtree.zig": [
        "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers",
        "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries",
        "phase 7 rbtree companion replays reverse traversal aliases and detached null stops",
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        "phase 7 rbtree survey keeps the returned json fixture, C harness, and direct helper packet truthful",
        'try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree.json");',
        'try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");',
        'try expectContains(manifest.next_bounded_step, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");',
        'try expectContains(manifest.next_bounded_step, "phase7-rbtree-test:");',
        'try expectContains(manifest.next_bounded_step, "phase7-rbtree-survey:");',
        'try expectContains(makefile, "phase7-validate:");',
        'try expectContains(fixture, "\\"packet\\": \\"phase7-rbtree-parity-fixture\\"");',
    ],
    "zigux/tests/phase7_rbtree_manifest.json": [
        '"current_direct_readback_state": "direct_helper_slice_checker_test_note_survey_manifest_fixture_harness"',
        '"zigux/tests/fixtures/phase7_rbtree.json"',
        '"zigux/tests/fixtures/phase7_rbtree_c_harness.c"',
        "fixture truthfulness must keep `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as returned parity evidence",
        NEXT_STEP_WRAPPER_MARKER,
    ],
    "zigux/tests/fixtures/phase7_rbtree.json": [
        '"packet": "phase7-rbtree-parity-fixture"',
        '"ordered_duplicate_range"',
        '"cached_leftmost_promotion"',
        '"postorder_null_stop"',
        '"reverse_alias_detached"',
    ],
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c": [
        "struct phase7_rbtree_c_harness {",
        '.packet = "phase7-rbtree-parity-fixture",',
        '.current_master_state = "ordered-duplicate-cached-postorder-reverse-c-harness",',
        ".ordered_duplicate_range = {",
        ".reverse_alias_detached = {",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
    ],
}

SELF_TEST_CASE_COUNT = 10


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel}: {marker}")
    return [], missing_markers


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        write(root / rel, "\n".join(markers) + "\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_") as tmp:
        root = Path(tmp)
        write_fixture_root(root)
        assert validate(root) == ([], [])

        missing_path = root / "zigux/tests/fixtures/phase7_rbtree_c_harness.c"
        missing_path.unlink()
        assert validate(root) == (["zigux/tests/fixtures/phase7_rbtree_c_harness.c"], [])

        write_fixture_root(root)
        marker_path = root / "Documentation/zigux/phase7-rbtree-slice.md"
        marker = "`PHASE7_LANE_KEY=P7-L13`"
        marker_path.write_text(read_text(marker_path).replace(marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"Documentation/zigux/phase7-rbtree-slice.md: {marker}"])

        write_fixture_root(root)
        direct_anchor_path = root / "Documentation/zigux/phase7-rbtree-direct-anchor-note.md"
        direct_anchor_marker = "Machine-readable fallback provenance stays explicit through `public_fallback_non_owner_paths`"
        direct_anchor_path.write_text(
            read_text(direct_anchor_path).replace(direct_anchor_marker + "\n", "", 1),
            encoding="utf-8",
        )
        assert validate(root) == (
            [],
            [f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {direct_anchor_marker}"],
        )

        write_fixture_root(root)
        direct_anchor_marker = "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`"
        direct_anchor_path.write_text(
            read_text(direct_anchor_path).replace(direct_anchor_marker + "\n", "", 1),
            encoding="utf-8",
        )
        assert validate(root) == (
            [],
            [f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {direct_anchor_marker}"],
        )

        write_fixture_root(root)
        survey_path = root / "zigux/tests/phase7_rbtree_survey.zig"
        survey_marker = 'try expectContains(manifest.next_bounded_step, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])

        write_fixture_root(root)
        survey_marker = 'try expectContains(manifest.next_bounded_step, "phase7-rbtree-test:");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])

        write_fixture_root(root)
        survey_marker = 'try expectContains(manifest.next_bounded_step, "phase7-rbtree-survey:");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])

        write_fixture_root(root)
        fixture_path = root / "zigux/tests/fixtures/phase7_rbtree.json"
        fixture_marker = '"packet": "phase7-rbtree-parity-fixture"'
        fixture_path.write_text(read_text(fixture_path).replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/fixtures/phase7_rbtree.json: {fixture_marker}"])

        write_fixture_root(root)
        makefile_path = root / "zigux/Makefile"
        makefile_marker = "phase7-validate:"
        makefile_path.write_text(read_text(makefile_path).replace(makefile_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/Makefile: {makefile_marker}"])

        write_fixture_root(root)
        manifest_path = root / "zigux/tests/phase7_rbtree_manifest.json"
        manifest_path.write_text(read_text(manifest_path).replace(NEXT_STEP_WRAPPER_MARKER + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_manifest.json: {NEXT_STEP_WRAPPER_MARKER}"])

    print("PHASE7_RBTREE_PARITY_SELF_TEST=pass")
    print(f"PHASE7_RBTREE_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(args.repo_root)
    if missing_files:
        print("PHASE7_RBTREE_PARITY=fail")
        print("MISSING_PHASE7_RBTREE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_RBTREE_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_RBTREE_PARITY=fail")
        print("MISSING_PHASE7_RBTREE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_RBTREE_MARKERS_END")
        return 1

    print("PHASE7_RBTREE_PARITY=pass")
    print(f"PHASE7_RBTREE_PARITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE7_RBTREE_PARITY_REQUIRED_MARKER_COUNT=" f"{sum(len(v) for v in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
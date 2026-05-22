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
    "zigux/Makefile",
]

DIRECT_ANCHOR_FALLBACK_PROVENANCE_MARKER = (
    "Machine-readable fallback provenance stays explicit through "
    "`public_fallback_non_owner_paths` in `zigux/tests/phase7_rbtree_manifest.json`, "
    "which currently names only `zigux/tests/phase7_build.zig` because the other listed "
    "legacy or shared non-owner surfaces still rematerialized through authenticated "
    "rereads in this slot."
)

OWNERSHIP_FOCUS_FALLBACK_MARKER = (
    "machine-readable fallback provenance must stay explicit too: "
    "`public_fallback_non_owner_paths` currently names only `zigux/tests/phase7_build.zig`, "
    "because that shared non-owner surface needed public fallback in this runtime while the "
    "other listed legacy or shared non-owner surfaces still rematerialized through "
    "authenticated rereads"
)

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-rbtree-slice.md": [
        "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`",
        "`PHASE7_LANE_KEY=P7-L13`",
        "`lib/rbtree.zig`",
        "`tools/lib/rbtree.zig`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "helper-local implementation now remains rooted at `lib/rbtree.zig`",
        "older tool-root `tools/lib/rbtree.zig` stays readable as legacy runtime-family companion evidence",
        "public-fallback provenance",
    ],
    "Documentation/zigux/phase7-rbtree-direct-anchor-note.md": [
        "Current direct-readback Phase 7 rbtree helper packet now rematerializes a dedicated helper-local slice note and parity checker on current `master`",
        "Fresh current-master reread in this slot also confirmed these shared, legacy, or roadmap-adjacent non-owner surfaces:",
        "- `tools/lib/rbtree.zig`",
        "`zigux/tests/phase7_build.zig` needed the public blob and raw GitHub fallback in this slot",
        DIRECT_ANCHOR_FALLBACK_PROVENANCE_MARKER,
        "Fresh authenticated GitHub reread in this slot still returned `404` for these dedicated companion surfaces:",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
    ],
    "scripts/zigux/check-phase7-rbtree-parity.py": [
        'print("PHASE7_RBTREE_PARITY=pass")',
        'print("PHASE7_RBTREE_PARITY=fail")',
        'print("PHASE7_RBTREE_PARITY_SELF_TEST=pass")',
        '"MISSING_PHASE7_RBTREE_FILES_START"',
        '"MISSING_PHASE7_RBTREE_FILES_END"',
        '"MISSING_PHASE7_RBTREE_MARKERS_START"',
        '"MISSING_PHASE7_RBTREE_MARKERS_END"',
        '"Documentation/zigux/phase7-rbtree-slice.md": [',
        '"zigux/tests/phase7_rbtree_manifest.json": [',
        '"zigux/Makefile": [',
        '"phase7-validate:"',
        "DIRECT_ANCHOR_FALLBACK_PROVENANCE_MARKER = (",
        "OWNERSHIP_FOCUS_FALLBACK_MARKER = (",
    ],
    "lib/rbtree.zig": [
        "pub const Node = struct {",
        "pub const RootCached = struct {",
        "pub fn rb_find_add_cached",
        "pub fn eraseInit(node: *Node, root: *Root) void {",
        "pub fn rb_next_postorder",
    ],
    "zigux/tests/phase7_rbtree.zig": [
        'const rbtree = @import("../../lib/rbtree.zig");',
        "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers",
        "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries",
        "rbtree.rb_erase_init_cached",
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        'const direct_anchor_fallback_provenance_marker =',
        'const ownership_focus_fallback_marker =',
        'try expectContains(slice_note, "This slice must stay truthful about the current direct helper path. The helper-local implementation now remains rooted at `lib/rbtree.zig`, while the older tool-root `tools/lib/rbtree.zig` stays readable as legacy runtime-family companion evidence rather than proof that helper-local ownership still lives there.");',
        'try expectContains(direct_anchor_note, direct_anchor_fallback_provenance_marker);',
        'try expectSliceContains(manifest.readable_non_owner_paths, "tools/lib/rbtree.zig");',
        'try expectSliceNotContains(manifest.missing_paths, "lib/rbtree.zig");',
        'try expectSliceContains(manifest.ownership_focus, ownership_focus_fallback_marker);',
        'try expectContains(manifest.next_bounded_step, "`tools/lib/rbtree.zig` remains framed as readable legacy companion evidence");',
        'try expectContains(makefile, "phase7-validate:");',
        'try expectNotContains(makefile, "phase7-rbtree-test:");',
        'try expectNotContains(workflow, "Validate Phase 7 runtime helper gates");',
        'try expectNotContains(workflow, "Run Phase 7 runtime helper tests");',
        'try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");',
        'try expectSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");',
    ],
    "zigux/tests/phase7_rbtree_manifest.json": [
        '"current_direct_readback_state": "direct_helper_slice_checker_test_note_survey_manifest"',
        '"visible_paths": [',
        '"lib/rbtree.zig"',
        '"readable_non_owner_paths": [',
        '"tools/lib/rbtree.zig"',
        '"public_fallback_non_owner_paths": [',
        '"zigux/tests/phase7_build.zig"',
        '"missing_paths": [',
        '"zigux/tests/fixtures/phase7_rbtree.json"',
        '"zigux/tests/fixtures/phase7_rbtree_c_harness.c"',
        OWNERSHIP_FOCUS_FALLBACK_MARKER,
    ],
    "zigux/Makefile": [
        "phase7-validate:",
    ],
}

SELF_TEST_CASE_COUNT = 27


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


def expect_missing_file(root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(root)
    assert missing_files == [rel]
    assert missing_markers == []


def expect_missing_marker(root: Path, rel: str, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    assert missing_files == []
    assert missing_markers == [f"{rel}: {marker}"]


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_") as tmp:
        root = Path(tmp)
        write_fixture_root(root)
        assert validate(root) == ([], [])
        cases = 0

        path = root / "zigux" / "tests" / "phase7_rbtree_manifest.json"
        path.unlink()
        expect_missing_file(root, "zigux/tests/phase7_rbtree_manifest.json")
        cases += 1
        write_fixture_root(root)

        path = root / "Documentation/zigux/phase7-rbtree-slice.md"
        marker = "older tool-root `tools/lib/rbtree.zig` stays readable as legacy runtime-family companion evidence"
        path.write_text(read_text(path).replace(marker, "", 1), encoding="utf-8")
        expect_missing_marker(root, "Documentation/zigux/phase7-rbtree-slice.md", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "Documentation/zigux/phase7-rbtree-direct-anchor-note.md"
        marker = "- `tools/lib/rbtree.zig`"
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux/tests/phase7_rbtree_manifest.json"
        marker = '"tools/lib/rbtree.zig"'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_manifest.json", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux/tests/phase7_rbtree_manifest.json"
        marker = OWNERSHIP_FOCUS_FALLBACK_MARKER
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_manifest.json", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectSliceContains(manifest.readable_non_owner_paths, "tools/lib/rbtree.zig");'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectSliceContains(manifest.ownership_focus, ownership_focus_fallback_marker);'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectContains(direct_anchor_note, direct_anchor_fallback_provenance_marker);'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "lib" / "rbtree.zig"
        marker = "pub fn rb_find_add_cached"
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "lib/rbtree.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux/tests/phase7_rbtree.zig"
        marker = "rbtree.rb_erase_init_cached"
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = 'print("PHASE7_RBTREE_PARITY=pass")'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = 'print("PHASE7_RBTREE_PARITY=fail")'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = 'print("PHASE7_RBTREE_PARITY_SELF_TEST=pass")'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = '"MISSING_PHASE7_RBTREE_FILES_START"'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = '"MISSING_PHASE7_RBTREE_FILES_END"'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = '"MISSING_PHASE7_RBTREE_MARKERS_START"'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = '"MISSING_PHASE7_RBTREE_MARKERS_END"'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        marker = '"phase7-validate:"'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "scripts/zigux/check-phase7-rbtree-parity.py", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "Documentation/zigux/phase7-rbtree-direct-anchor-note.md"
        marker = DIRECT_ANCHOR_FALLBACK_PROVENANCE_MARKER
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "Documentation/zigux/phase7-rbtree-slice.md"
        marker = "public-fallback provenance"
        path.write_text(read_text(path).replace(marker, "", 1), encoding="utf-8")
        expect_missing_marker(root, "Documentation/zigux/phase7-rbtree-slice.md", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux/tests/phase7_rbtree_manifest.json"
        marker = '"zigux/tests/fixtures/phase7_rbtree_c_harness.c"'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_manifest.json", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectContains(makefile, "phase7-validate:");'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectNotContains(makefile, "phase7-rbtree-test:");'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectNotContains(workflow, "Validate Phase 7 runtime helper gates");'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        marker = 'try expectSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");'
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/tests/phase7_rbtree_survey.zig", marker)
        cases += 1
        write_fixture_root(root)

        path = root / "zigux/Makefile"
        marker = "phase7-validate:"
        path.write_text(read_text(path).replace(marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(root, "zigux/Makefile", marker)
        cases += 1

        assert cases == SELF_TEST_CASE_COUNT, cases

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
#!/usr/bin/env python3
"""Validate the current Phase 7 rbtree helper-local packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

PUBLIC_FALLBACK_NON_OWNER_BLOCK = '"public_fallback_non_owner_paths": [\n    "zigux/tests/phase7_build.zig"\n  ],'

REQUIRED_FILES = [
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-rbtree-direct-anchor-note.md",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "tools/lib/rbtree.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-rbtree-slice.md": [
        "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`",
        "`PHASE7_LANE_KEY=P7-L13`",
        "`tools/lib/rbtree.zig`",
        "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`",
        "`scripts/zigux/check-phase7-rbtree-parity.py`",
        "`lib/rbtree.zig`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "same-lane truthfulness keeps the returned slice note, direct-anchor note, parity checker, replay, survey, and manifest explicit",
        "Keep `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` explicit as directly readable shared-control build evidence rather than helper-local ownership.",
        "`zigux/tests/phase7_build.zig` needed public blob/raw fallback after the authenticated contents bridge returned `404`, so keep that one path framed as returned shared non-owner evidence without overstating authenticated whole-file coverage.",
        "This slice must stay truthful about the current direct helper path. The readable helper is still rooted at `tools/lib/rbtree.zig`, while the roadmap destination `lib/rbtree.zig` remains a repo-reality gap on current `master`.",
        "Keep same-lane follow-through inside this slice-backed direct-helper packet by rereading `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json` against this note for shared non-owner build-evidence and public-fallback provenance,",
    ],
    "Documentation/zigux/phase7-rbtree-direct-anchor-note.md": [
        "`scripts/zigux/check-phase7-rbtree-parity.py`",
        "Current direct-readback Phase 7 rbtree helper packet now rematerializes a dedicated helper-local slice note and parity checker on current `master`",
        "Fresh authenticated GitHub reread in this slot directly returned:",
        "- `Documentation/zigux/phase7-rbtree-slice.md`",
        "- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`",
        "- `scripts/zigux/check-phase7-rbtree-parity.py`",
        "- `tools/lib/rbtree.zig`",
        "- `zigux/tests/phase7_rbtree.zig`",
        "- `zigux/tests/phase7_rbtree_survey.zig`",
        "- `zigux/tests/phase7_rbtree_manifest.json`",
        "Fresh current-master reread in this slot also confirmed these shared non-owner surfaces:",
        "- `scripts/zigux/check-phase7-build-wiring.py`",
        "- `scripts/zigux/validate-phase7.py`",
        "- `zigux/tests/phase7_build.zig`",
        "- `zigux/Makefile`",
        "- `.github/workflows/zigux-bootstrap.yml`",
        "`lib/rbtree.zig`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        "`zigux/tests/phase7_build.zig` needed the public blob and raw GitHub fallback in this slot after the authenticated GitHub contents bridge returned `404` for that path, so keep it explicit as returned shared non-owner build evidence without overstating authenticated whole-file coverage for this one surface.",
        "Machine-readable fallback provenance stays explicit through `public_fallback_non_owner_paths` in `zigux/tests/phase7_rbtree_manifest.json`, which currently names only `zigux/tests/phase7_build.zig` because the other listed shared non-owner surfaces still rematerialized through authenticated rereads in this slot.",
        "Keep the current Phase 7 rbtree reminder surface tied to the returned tool-root helper, the dedicated slice note, the dedicated replay companion, the returned survey and manifest, and the parity checker",
        "shared build, validator, and workflow evidence",
    ],
    "scripts/zigux/check-phase7-rbtree-parity.py": [
        'print("PHASE7_RBTREE_PARITY=pass")',
        'print(f"PHASE7_RBTREE_PARITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")',
        "PHASE7_RBTREE_PARITY_SELF_TEST=pass",
        '"Documentation/zigux/phase7-rbtree-slice.md",',
        '"tools/lib/rbtree.zig",',
        '"zigux/tests/phase7_rbtree.zig",',
        '"zigux/tests/phase7_rbtree_survey.zig",',
        '"zigux/tests/phase7_rbtree_manifest.json",',
        "PUBLIC_FALLBACK_NON_OWNER_BLOCK = '",
    ],
    "tools/lib/rbtree.zig": [
        "pub const Node = struct {",
        "pub const RootCached = struct {",
        "pub fn clearNode",
        "pub fn linkNode",
        "pub fn add",
        "pub fn findAdd",
        "pub fn rb_find_add_cached",
        "pub fn eraseInit(node: *Node, root: *Root) void {",
        "pub fn last(root: *const Root) ?*Node {",
        "pub fn rb_last(root: *const Root) ?*Node {",
        "pub fn prev(node: *const Node) ?*Node {",
        "pub fn rb_prev(node: *const Node) ?*Node {",
        "pub fn firstPostorder",
        "pub fn rb_first_postorder",
        "pub fn nextPostorder",
        "pub fn rb_next_postorder",
    ],
    "zigux/tests/phase7_rbtree.zig": [
        'const rbtree = @import("../../tools/lib/rbtree.zig");',
        'test "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers" {',
        'test "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries" {',
        'test "phase 7 rbtree companion replays plain erase-init ownership boundaries" {',
        'test "phase 7 rbtree companion replays postorder aliases and null-stop handling" {',
        'test "phase 7 rbtree companion replays reverse traversal aliases and detached null stops" {',
        "rbtree.matchIterator",
        "rbtree.eraseInit(&root_entry.node, &root);",
        "rbtree.eraseInitCached(&entries[1].node, &root);",
        "rbtree.rb_erase_init_cached",
        "rbtree.last(&root)",
        "rbtree.rb_last(&root)",
        "rbtree.prev(alias_last)",
        "rbtree.rb_prev(alias_last)",
        "rbtree.firstPostorder",
        "rbtree.rb_first_postorder",
        "rbtree.nextPostorder",
        "rbtree.rb_next_postorder",
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        'const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-rbtree-parity.py");',
        'const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");',
        'try expectContains(checker, "PHASE7_RBTREE_PARITY=pass");',
        'try std.testing.expectEqualStrings("direct_helper_slice_checker_test_note_survey_manifest", manifest.current_direct_readback_state);',
        'try expectSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-slice.md");',
        'try expectSliceNotContains(manifest.missing_paths, "Documentation/zigux/phase7-rbtree-slice.md");',
        'try expectContains(slice_note, "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`");',
        'try expectContains(direct_anchor_note, "Current direct-readback Phase 7 rbtree helper packet now rematerializes a dedicated helper-local slice note and parity checker on current `master`");',
        'try expectSliceContains(manifest.public_fallback_non_owner_paths, "zigux/tests/phase7_build.zig");',
        'try expectSliceNotContains(manifest.public_fallback_non_owner_paths, "scripts/zigux/check-phase7-build-wiring.py");',
        'try expectSliceContains(manifest.ownership_focus, "machine-readable fallback provenance must stay explicit too: `public_fallback_non_owner_paths` currently names only `zigux/tests/phase7_build.zig`, because that shared non-owner surface needed public fallback in this runtime while the other listed shared-control surfaces still rematerialized through authenticated rereads");',
        'try expectContains(build_file, "../../lib/rbtree.zig");',
        'try expectContains(manifest.next_bounded_step, "public-fallback provenance");',
        'try expectContains(manifest.next_bounded_step, "shared non-owner build evidence");',
        'try expectNotContains(manifest.next_bounded_step, "`zigux/tests/phase7_build.zig`");',
        'try expectNotContains(manifest.next_bounded_step, "`scripts/zigux/validate-phase7.py`");',
    ],
    "zigux/tests/phase7_rbtree_manifest.json": [
        '"current_direct_readback_state": "direct_helper_slice_checker_test_note_survey_manifest"',
        '"Documentation/zigux/phase7-rbtree-slice.md"',
        '"scripts/zigux/check-phase7-rbtree-parity.py"',
        '"lib/rbtree.zig"',
        '"zigux/tests/fixtures/phase7_rbtree.json"',
        '"zigux/tests/fixtures/phase7_rbtree_c_harness.c"',
        '"zigux/tests/phase7_build.zig"',
        '"scripts/zigux/validate-phase7.py"',
        PUBLIC_FALLBACK_NON_OWNER_BLOCK,
        '"absent_makefile_markers": [',
        '"phase7-rbtree-test:"',
        '"phase7-rbtree-survey:"',
        '"phase7-test:"',
        '"phase7:"',
        '"absent_workflow_markers": [',
        '"Validate Phase 7 runtime helper gates"',
        '"Run Phase 7 runtime helper tests"',
        '"make -C zigux phase7-test"',
        '"public-fallback provenance"',
    ],
}

SELF_TEST_CASE_COUNT = 64


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        write(tmp_root / rel, "\n".join(REQUIRED_MARKERS[rel]) + "\n")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])
        cases_run = 0

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-rbtree-slice.md"
        slice_marker = "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`"
        slice_path.write_text(read_text(slice_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_status_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-rbtree-parity.py"
        checker_path.unlink()
        expect_missing_file("missing_checker", tmp_root, "scripts/zigux/check-phase7-rbtree-parity.py")
        cases_run += 1
        write_fixture_root(tmp_root)

        note_path = tmp_root / "Documentation" / "zigux" / "phase7-rbtree-direct-anchor-note.md"
        note_marker = "Current direct-readback Phase 7 rbtree helper packet now rematerializes a dedicated helper-local slice note and parity checker on current `master`"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_checker_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_returned_note_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "- `tools/lib/rbtree.zig`"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_returned_helper_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "- `zigux/tests/phase7_rbtree.zig`"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_returned_replay_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "- `zigux/tests/phase7_rbtree_survey.zig`"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_returned_survey_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "- `zigux/tests/phase7_rbtree_manifest.json`"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_returned_manifest_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "Fresh current-master reread in this slot also confirmed these shared non-owner surfaces:"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_shared_non_owner_header_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "- `zigux/tests/phase7_build.zig`"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_shared_build_path_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "`zigux/tests/phase7_build.zig` needed the public blob and raw GitHub fallback in this slot after the authenticated GitHub contents bridge returned `404` for that path, so keep it explicit as returned shared non-owner build evidence without overstating authenticated whole-file coverage for this one surface."
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_fallback_provenance_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "Machine-readable fallback provenance stays explicit through `public_fallback_non_owner_paths` in `zigux/tests/phase7_rbtree_manifest.json`, which currently names only `zigux/tests/phase7_build.zig` because the other listed shared non-owner surfaces still rematerialized through authenticated rereads in this slot."
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_machine_readable_fallback_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "Keep the current Phase 7 rbtree reminder surface tied to the returned tool-root helper, the dedicated slice note, the dedicated replay companion, the returned survey and manifest, and the parity checker"
        note_path.write_text(read_text(note_path).replace(note_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_current_packet_boundary_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        note_marker = "shared build, validator, and workflow evidence"
        note_path.write_text(read_text(note_path).replace(note_marker, "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_note_shared_build_evidence_phrase_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {note_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "tools" / "lib" / "rbtree.zig"
        helper_marker = "pub fn rb_find_add_cached"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_cached_alias", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub const RootCached = struct {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_cached_root_type", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn eraseInit(node: *Node, root: *Root) void {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_erase_init", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn last(root: *const Root) ?*Node {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_last", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn rb_last(root: *const Root) ?*Node {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_last_alias", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn prev(node: *const Node) ?*Node {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_prev", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn rb_prev(node: *const Node) ?*Node {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_prev_alias", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn firstPostorder"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_first_postorder", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn rb_first_postorder"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_first_postorder_alias", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn nextPostorder"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_next_postorder", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_marker = "pub fn rb_next_postorder"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_next_postorder_alias", tmp_root, f"tools/lib/rbtree.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_path = tmp_root / "zigux" / "tests" / "phase7_rbtree.zig"
        companion_marker = "rbtree.rb_erase_init_cached"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_cached_erase_alias",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = 'test "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries" {'
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_cached_ownership_replay",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = 'test "phase 7 rbtree companion replays plain erase-init ownership boundaries" {'
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_plain_erase_init_replay",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.eraseInit(&root_entry.node, &root);"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_erase_init_helper",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.eraseInitCached(&entries[1].node, &root);"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_cached_erase_init_helper",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = 'test "phase 7 rbtree companion replays postorder aliases and null-stop handling" {'
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_postorder_replay",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = 'test "phase 7 rbtree companion replays reverse traversal aliases and detached null stops" {'
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_reverse_traversal_replay",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.last(&root)"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_last_helper",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.rb_last(&root)"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_last_alias",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.prev(alias_last)"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_prev_helper",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.rb_prev(alias_last)"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_prev_alias",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.firstPostorder"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_first_postorder_helper",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.rb_first_postorder"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_first_postorder_alias",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.nextPostorder"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_next_postorder_helper",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_marker = "rbtree.rb_next_postorder"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_companion_next_postorder_alias",
            tmp_root,
            f"zigux/tests/phase7_rbtree.zig: {companion_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        survey_marker = 'try expectContains(checker, "PHASE7_RBTREE_PARITY=pass");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_checker_result_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectSliceNotContains(manifest.missing_paths, "Documentation/zigux/phase7-rbtree-slice.md");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_slice_gap_guard",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectSliceContains(manifest.public_fallback_non_owner_paths, "zigux/tests/phase7_build.zig");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_public_fallback_build_file_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectSliceNotContains(manifest.public_fallback_non_owner_paths, "scripts/zigux/check-phase7-build-wiring.py");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_public_fallback_owner_boundary_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectSliceContains(manifest.ownership_focus, "machine-readable fallback provenance must stay explicit too: `public_fallback_non_owner_paths` currently names only `zigux/tests/phase7_build.zig`, because that shared non-owner surface needed public fallback in this runtime while the other listed shared-control surfaces still rematerialized through authenticated rereads");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_fallback_ownership_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectContains(build_file, "../../lib/rbtree.zig");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_build_file_import_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectContains(manifest.next_bounded_step, "public-fallback provenance");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_next_step_fallback_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectNotContains(manifest.next_bounded_step, "`zigux/tests/phase7_build.zig`");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_next_step_build_file_exclusion_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_marker = 'try expectNotContains(manifest.next_bounded_step, "`scripts/zigux/validate-phase7.py`");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_survey_next_step_shared_validator_exclusion_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_rbtree_manifest.json"
        manifest_marker = '"current_direct_readback_state": "direct_helper_slice_checker_test_note_survey_manifest"'
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_state_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = '"Documentation/zigux/phase7-rbtree-slice.md"'
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_slice_path",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = PUBLIC_FALLBACK_NON_OWNER_BLOCK
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_public_fallback_block_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        expanded_public_fallback_block = '"public_fallback_non_owner_paths": [\n    "zigux/tests/phase7_build.zig",\n    "scripts/zigux/validate-phase7.py"\n  ],'
        manifest_path.write_text(
            read_text(manifest_path).replace(PUBLIC_FALLBACK_NON_OWNER_BLOCK, expanded_public_fallback_block, 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "expanded_manifest_public_fallback_block",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = '"public-fallback provenance"'
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_public_fallback_next_step_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = '"phase7-rbtree-test:"'
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_absent_makefile_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = '"Validate Phase 7 runtime helper gates"'
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_absent_workflow_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = '"absent_workflow_markers": ['
        manifest_path.write_text(read_text(manifest_path).replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_manifest_absent_workflow_list_marker",
            tmp_root,
            f"zigux/tests/phase7_rbtree_manifest.json: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = 'print("PHASE7_RBTREE_PARITY=pass")'
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_checker_pass_output_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = 'print(f"PHASE7_RBTREE_PARITY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")'
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_checker_required_file_count_output_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_marker = "PHASE7_RBTREE_PARITY_SELF_TEST=pass"
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_checker_selftest_marker",
            tmp_root,
            f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_marker = "Keep `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` explicit as directly readable shared-control build evidence rather than helper-local ownership."
        slice_path.write_text(read_text(slice_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_shared_validator_boundary_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_marker = "`zigux/tests/phase7_build.zig` needed public blob/raw fallback after the authenticated contents bridge returned `404`, so keep that one path framed as returned shared non-owner evidence without overstating authenticated whole-file coverage."
        slice_path.write_text(read_text(slice_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_fallback_provenance_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_marker = "This slice must stay truthful about the current direct helper path. The readable helper is still rooted at `tools/lib/rbtree.zig`, while the roadmap destination `lib/rbtree.zig` remains a repo-reality gap on current `master`."
        slice_path.write_text(read_text(slice_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_roadmap_gap_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_marker = "Keep same-lane follow-through inside this slice-backed direct-helper packet by rereading `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json` against this note for shared non-owner build-evidence and public-fallback provenance,"
        slice_path.write_text(read_text(slice_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_slice_next_step_packet_boundary_marker",
            tmp_root,
            f"Documentation/zigux/phase7-rbtree-slice.md: {slice_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run

    print("PHASE7_RBTREE_PARITY_SELF_TEST=pass")
    print(f"PHASE7_RBTREE_PARITY_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
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
    print("PHASE7_RBTREE_PARITY_REQUIRED_MARKER_COUNT=" f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
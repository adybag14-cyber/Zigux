#!/usr/bin/env python3
"""Validate the current Phase 7 rbtree helper-local packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

EXPECTED_MANIFEST_LANE_KEY = "P7-L13"
EXPECTED_MANIFEST_PHASE = "Phase 7"
EXPECTED_MANIFEST_ANCHOR = "lib/rbtree.c"
EXPECTED_MANIFEST_STATE = "direct_helper_slice_checker_test_note_survey_manifest_fixture_harness"
EXPECTED_MANIFEST_READABLE_MAKEFILE_MARKERS = [
    "phase7-validate:",
    "phase7-rbtree-test:",
    "phase7-rbtree-survey:",
]
EXPECTED_MANIFEST_PUBLIC_FALLBACK_NON_OWNER_PATHS: list[str] = []
EXPECTED_MANIFEST_MISSING_PATHS: list[str] = []
EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (
    "Stay in the same `kernel-leaf-libraries` lane and keep "
    "`zigux/tests/fixtures/phase7_rbtree.json` plus "
    "`zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as returned parity companions, "
    "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed "
    "cases, while keeping the returned `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers "
    "aligned with `zigux/tests/phase7_build.zig` so helper path, shared `phase7-validate` route, "
    "still-absent `phase7-test:` and `phase7:` markers, and legacy companion framing stay aligned "
    "without widening beyond the rbtree packet."
)

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
    "while keeping the returned `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers "
    "aligned with `zigux/tests/phase7_build.zig`"
)

NEXT_STEP_ERASE_CASES_MARKER = (
    "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases"
)

DIRECT_BUILD_READBACK_MARKER = (
    "`zigux/tests/phase7_build.zig` now rematerialized through the same authenticated reread path in this slot, "
    "so keep it explicit as returned shared non-owner build evidence without treating it as helper-local ownership."
)

SLICE_AUTHENTICATED_BUILD_MARKER = (
    "public-fallback provenance stays explicit through the now-empty `public_fallback_non_owner_paths` field in "
    "`zigux/tests/phase7_rbtree_manifest.json`, because `zigux/tests/phase7_build.zig` and the other listed legacy "
    "or shared non-owner surfaces all rematerialized through authenticated rereads in this slot"
)

SLICE_ERASE_BOUNDARY_MARKER = (
    "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases"
)

DIRECT_ERASE_SCENARIOS_MARKER = (
    "non-leftmost cached erase, singleton cached erase, and plain erase-init reseed scenarios"
)

MANIFEST_BUILD_PROVENANCE_MARKER = (
    "build-surface provenance must stay explicit: in this runtime `zigux/tests/phase7_build.zig`, `tools/lib/rbtree.zig`, "
    "`scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/Makefile`, and the helper-local "
    "rbtree packet all rematerialized through authenticated rereads, so shared non-owner build evidence stays reviewable "
    "without public-fallback caveats on current master"
)

MANIFEST_EMPTY_FALLBACK_MARKER = (
    "machine-readable fallback provenance should stay empty in this packet while the readable non-owner surfaces all "
    "rematerialize through authenticated rereads in this runtime"
)

MANIFEST_ERASE_BOUNDARY_MARKER = (
    "fixture truthfulness now also keeps the non-leftmost cached erase, singleton cached erase, and plain erase-init "
    "reseed boundaries explicit across the returned JSON fixture, returned C harness, dedicated survey, and dedicated replay"
)

MAKEFILE_POSITIVE_ROUTE_MARKER = (
    "positive shared build-route truthfulness must stay explicit too: `zigux/Makefile` now returns shared `phase7-validate` "
    "plus dedicated `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers, while `phase7-test:` and `phase7:` stay "
    "listed under `absent_makefile_markers` until broader shared-control routes really materialize"
)

DIRECT_WRAPPER_ROUTE_MARKER = (
    "`zigux/Makefile` now returns shared `phase7-validate` plus dedicated `phase7-rbtree-test:` and "
    "`phase7-rbtree-survey:` wrapper markers"
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
        SLICE_AUTHENTICATED_BUILD_MARKER,
        SLICE_ERASE_BOUNDARY_MARKER,
    ],
    "Documentation/zigux/phase7-rbtree-direct-anchor-note.md": [
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "Fresh authenticated GitHub reread in this slot directly returned:",
        "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`",
        "Fresh current-master reread in this slot also directly returned these shared, legacy, or roadmap-adjacent non-owner surfaces:",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        DIRECT_BUILD_READBACK_MARKER,
        DIRECT_ERASE_SCENARIOS_MARKER,
        DIRECT_WRAPPER_ROUTE_MARKER,
    ],
    "scripts/zigux/check-phase7-rbtree-parity.py": [
        "import json",
        'EXPECTED_MANIFEST_LANE_KEY = "P7-L13"',
        'EXPECTED_MANIFEST_PHASE = "Phase 7"',
        'EXPECTED_MANIFEST_ANCHOR = "lib/rbtree.c"',
        'EXPECTED_MANIFEST_STATE = "direct_helper_slice_checker_test_note_survey_manifest_fixture_harness"',
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
        "NEXT_STEP_ERASE_CASES_MARKER = (",
        "DIRECT_BUILD_READBACK_MARKER = (",
        "SLICE_AUTHENTICATED_BUILD_MARKER = (",
        "SLICE_ERASE_BOUNDARY_MARKER = (",
        "DIRECT_ERASE_SCENARIOS_MARKER = (",
        "MANIFEST_BUILD_PROVENANCE_MARKER = (",
        "MANIFEST_EMPTY_FALLBACK_MARKER = (",
        "MANIFEST_ERASE_BOUNDARY_MARKER = (",
        "MAKEFILE_POSITIVE_ROUTE_MARKER = (",
        "DIRECT_WRAPPER_ROUTE_MARKER = (",
        "assert cases_run == SELF_TEST_CASE_COUNT",
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
        "phase 7 rbtree companion replays non-leftmost cached erase ownership boundaries",
        "phase 7 rbtree companion replays singleton cached erase ownership until clearNode",
        "phase 7 rbtree companion replays plain erase-init ownership boundaries",
        "phase 7 rbtree companion replays reverse traversal aliases and detached null stops",
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        "phase 7 rbtree survey keeps the returned json fixture, C harness, and direct helper packet truthful",
        'try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree.json");',
        'try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");',
        'try expectSliceContains(manifest.readable_non_owner_paths, "zigux/tests/phase7_build.zig");',
        'try expectSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-test:");',
        'try expectSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-survey:");',
        'try std.testing.expectEqual(@as(usize, 0), manifest.public_fallback_non_owner_paths.len);',
        'try expectSliceContains(manifest.ownership_focus, "fixture truthfulness now also keeps the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed boundaries explicit across the returned JSON fixture, returned C harness, dedicated survey, and dedicated replay");',
        'try expectContains(manifest.next_bounded_step, "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases");',
        'try expectContains(manifest.next_bounded_step, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");',
        'try expectContains(manifest.next_bounded_step, "phase7-rbtree-test:");',
        'try expectContains(manifest.next_bounded_step, "phase7-rbtree-survey:");',
        'try expectContains(manifest.next_bounded_step, "phase7-test:");',
        'try expectContains(makefile, "phase7-validate:");',
        'try expectContains(makefile, "phase7-rbtree-test:");',
        'try expectContains(makefile, "phase7-rbtree-survey:");',
        'try expectContains(slice_note, "public-fallback provenance stays explicit through the now-empty `public_fallback_non_owner_paths` field");',
        'try expectContains(fixture, "\\"packet\\": \\"phase7-rbtree-parity-fixture\\"");',
        'try expectContains(c_harness, "ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness");',
    ],
    "zigux/tests/phase7_rbtree_manifest.json": [
        '"current_direct_readback_state": "direct_helper_slice_checker_test_note_survey_manifest_fixture_harness"',
        '"public_fallback_non_owner_paths": []',
        '"phase7-rbtree-test:"',
        '"phase7-rbtree-survey:"',
        '"zigux/tests/fixtures/phase7_rbtree.json"',
        '"zigux/tests/fixtures/phase7_rbtree_c_harness.c"',
        "fixture truthfulness must keep `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as returned parity evidence",
        MAKEFILE_POSITIVE_ROUTE_MARKER,
        MANIFEST_BUILD_PROVENANCE_MARKER,
        MANIFEST_EMPTY_FALLBACK_MARKER,
        MANIFEST_ERASE_BOUNDARY_MARKER,
        NEXT_STEP_ERASE_CASES_MARKER,
        NEXT_STEP_WRAPPER_MARKER,
    ],
    "zigux/tests/fixtures/phase7_rbtree.json": [
        '"packet": "phase7-rbtree-parity-fixture"',
        '"ordered_duplicate_range"',
        '"cached_leftmost_promotion"',
        '"non_leftmost_cached_erase"',
        '"singleton_cached_erase"',
        '"plain_erase_init_reseed"',
        '"postorder_null_stop"',
        '"reverse_alias_detached"',
    ],
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c": [
        "struct phase7_rbtree_c_harness {",
        '.packet = "phase7-rbtree-parity-fixture",',
        '.current_master_state = "ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness",',
        ".ordered_duplicate_range = {",
        ".non_leftmost_cached_erase = {",
        ".singleton_cached_erase = {",
        ".plain_erase_init_reseed = {",
        ".reverse_alias_detached = {",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "phase7-rbtree-test:",
        "phase7-rbtree-survey:",
    ],
}

SELF_TEST_CASE_COUNT = 55


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_manifest_entries(manifest: dict[str, object]) -> list[str]:
    missing: list[str] = []

    if manifest.get("readable_makefile_markers") != EXPECTED_MANIFEST_READABLE_MAKEFILE_MARKERS:
        missing.append("zigux/tests/phase7_rbtree_manifest.json: readable_makefile_markers")

    if manifest.get("public_fallback_non_owner_paths") != EXPECTED_MANIFEST_PUBLIC_FALLBACK_NON_OWNER_PATHS:
        missing.append("zigux/tests/phase7_rbtree_manifest.json: public_fallback_non_owner_paths")

    if manifest.get("missing_paths") != EXPECTED_MANIFEST_MISSING_PATHS:
        missing.append("zigux/tests/phase7_rbtree_manifest.json: missing_paths")

    if manifest.get("next_bounded_step") != EXPECTED_MANIFEST_NEXT_BOUNDED_STEP:
        missing.append("zigux/tests/phase7_rbtree_manifest.json: next_bounded_step")

    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing_files:
        return missing_files, []

    manifest = json.loads(read_text(root / "zigux/tests/phase7_rbtree_manifest.json"))
    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE_KEY:
        return [], ["zigux/tests/phase7_rbtree_manifest.json: lane_key"]
    if manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        return [], ["zigux/tests/phase7_rbtree_manifest.json: phase"]
    if manifest.get("anchor") != EXPECTED_MANIFEST_ANCHOR:
        return [], ["zigux/tests/phase7_rbtree_manifest.json: anchor"]
    if manifest.get("current_direct_readback_state") != EXPECTED_MANIFEST_STATE:
        return [], ["zigux/tests/phase7_rbtree_manifest.json: current_direct_readback_state"]

    missing_manifest_entries = collect_missing_manifest_entries(manifest)
    if missing_manifest_entries:
        return [], missing_manifest_entries

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
        if rel == "zigux/tests/phase7_rbtree_manifest.json":
            continue
        write(root / rel, "\n".join(markers) + "\n")

    write(
        root / "zigux/tests/phase7_rbtree_manifest.json",
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE_KEY,
                "phase": EXPECTED_MANIFEST_PHASE,
                "verified_on_utc": "2026-05-27T09:30:01Z",
                "anchor": EXPECTED_MANIFEST_ANCHOR,
                "roadmap_destinations": [
                    "lib/rbtree.zig",
                ],
                "current_direct_readback_state": EXPECTED_MANIFEST_STATE,
                "visible_paths": [
                    "Documentation/zigux/phase7-rbtree-slice.md",
                    "Documentation/zigux/phase7-rbtree-direct-anchor-note.md",
                    "scripts/zigux/check-phase7-rbtree-parity.py",
                    "lib/rbtree.zig",
                    "zigux/tests/phase7_rbtree.zig",
                    "zigux/tests/phase7_rbtree_survey.zig",
                    "zigux/tests/phase7_rbtree_manifest.json",
                    "zigux/tests/fixtures/phase7_rbtree.json",
                    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
                ],
                "readable_non_owner_paths": [
                    "tools/lib/rbtree.zig",
                    "scripts/zigux/check-phase7-build-wiring.py",
                    "scripts/zigux/validate-phase7.py",
                    "zigux/tests/phase7_build.zig",
                    "zigux/Makefile",
                    ".github/workflows/zigux-bootstrap.yml",
                ],
                "readable_makefile_markers": EXPECTED_MANIFEST_READABLE_MAKEFILE_MARKERS,
                "public_fallback_non_owner_paths": EXPECTED_MANIFEST_PUBLIC_FALLBACK_NON_OWNER_PATHS,
                "missing_paths": EXPECTED_MANIFEST_MISSING_PATHS,
                "absent_makefile_markers": [
                    "phase7-test:",
                    "phase7:",
                ],
                "absent_workflow_markers": [
                    "Validate Phase 7 runtime helper gates",
                    "Run Phase 7 runtime helper tests",
                    "make -C zigux phase7-test",
                ],
                "ownership_focus": [
                    "the currently readable same-lane rbtree packet now includes the direct helper at `lib/rbtree.zig`, the dedicated slice note at `Documentation/zigux/phase7-rbtree-slice.md`, the direct-anchor note, the dedicated parity checker at `scripts/zigux/check-phase7-rbtree-parity.py`, the dedicated replay at `zigux/tests/phase7_rbtree.zig`, the returned survey and manifest, the returned `zigux/tests/fixtures/phase7_rbtree.json` parity companion, and the returned `zigux/tests/fixtures/phase7_rbtree_c_harness.c` companion, so same-lane truthfulness must keep those returned surfaces explicit",
                    "path truthfulness must keep the currently returned helper rooted at `lib/rbtree.zig` explicit while `tools/lib/rbtree.zig` stays readable as legacy runtime-family companion evidence rather than helper-local ownership on current master",
                    "build-graph truthfulness must keep the split non-owner evidence explicit: `tools/lib/rbtree.zig`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` are readable",
                    MAKEFILE_POSITIVE_ROUTE_MARKER,
                    MANIFEST_BUILD_PROVENANCE_MARKER,
                    MANIFEST_EMPTY_FALLBACK_MARKER,
                    "fixture truthfulness must keep `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as returned parity evidence",
                    MANIFEST_ERASE_BOUNDARY_MARKER,
                ],
                "next_bounded_step": EXPECTED_MANIFEST_NEXT_BOUNDED_STEP,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_") as tmp:
        root = Path(tmp)
        write_fixture_root(root)
        assert validate(root) == ([], [])
        cases_run = 0

        missing_path = root / "zigux/tests/fixtures/phase7_rbtree_c_harness.c"
        missing_path.unlink()
        assert validate(root) == (["zigux/tests/fixtures/phase7_rbtree_c_harness.c"], [])
        cases_run += 1

        write_fixture_root(root)
        missing_path = root / "zigux/tests/fixtures/phase7_rbtree.json"
        missing_path.unlink()
        assert validate(root) == (["zigux/tests/fixtures/phase7_rbtree.json"], [])
        cases_run += 1

        write_fixture_root(root)
        marker_path = root / "Documentation/zigux/phase7-rbtree-slice.md"
        marker = "`PHASE7_LANE_KEY=P7-L13`"
        marker_path.write_text(read_text(marker_path).replace(marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"Documentation/zigux/phase7-rbtree-slice.md: {marker}"])
        cases_run += 1

        write_fixture_root(root)
        direct_anchor_path = root / "Documentation/zigux/phase7-rbtree-direct-anchor-note.md"
        direct_anchor_marker = "Fresh authenticated GitHub reread in this slot directly returned:"
        direct_anchor_path.write_text(
            read_text(direct_anchor_path).replace(direct_anchor_marker + "\n", "", 1),
            encoding="utf-8",
        )
        assert validate(root) == (
            [],
            [f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {direct_anchor_marker}"],
        )
        cases_run += 1

        write_fixture_root(root)
        direct_anchor_marker = "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`"
        direct_anchor_path.write_text(
            read_text(direct_anchor_path).replace(direct_anchor_marker + "\n", "", 1),
            encoding="utf-8",
        )
        assert validate(root) == (
            [],
            [f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {direct_anchor_marker}"],
        )
        cases_run += 1

        write_fixture_root(root)
        direct_anchor_marker = DIRECT_BUILD_READBACK_MARKER
        direct_anchor_path.write_text(
            read_text(direct_anchor_path).replace(direct_anchor_marker + "\n", "", 1),
            encoding="utf-8",
        )
        assert validate(root) == (
            [],
            [f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {direct_anchor_marker}"],
        )
        cases_run += 1

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
        cases_run += 1

        write_fixture_root(root)
        direct_anchor_marker = DIRECT_ERASE_SCENARIOS_MARKER
        direct_anchor_path.write_text(
            read_text(direct_anchor_path).replace(direct_anchor_marker + "\n", "", 1),
            encoding="utf-8",
        )
        assert validate(root) == (
            [],
            [f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {direct_anchor_marker}"],
        )
        cases_run += 1

        write_fixture_root(root)
        direct_anchor_marker = DIRECT_WRAPPER_ROUTE_MARKER
        direct_anchor_path.write_text(
            read_text(direct_anchor_path).replace(direct_anchor_marker + "\n", "", 1),
            encoding="utf-8",
        )
        assert validate(root) == (
            [],
            [f"Documentation/zigux/phase7-rbtree-direct-anchor-note.md: {direct_anchor_marker}"],
        )
        cases_run += 1

        write_fixture_root(root)
        checker_path = root / "scripts/zigux/check-phase7-rbtree-parity.py"
        checker_marker = "MISSING_PHASE7_RBTREE_MARKERS_START"
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}"])
        cases_run += 1

        write_fixture_root(root)
        checker_marker = "PHASE7_RBTREE_PARITY_SELF_TEST=pass"
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}"])
        cases_run += 1

        write_fixture_root(root)
        checker_marker = "PHASE7_RBTREE_PARITY=fail"
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}"])
        cases_run += 1

        write_fixture_root(root)
        checker_marker = "MANIFEST_EMPTY_FALLBACK_MARKER = ("
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}"])
        cases_run += 1

        write_fixture_root(root)
        checker_marker = "DIRECT_WRAPPER_ROUTE_MARKER = ("
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}"])
        cases_run += 1

        write_fixture_root(root)
        checker_marker = "assert cases_run == SELF_TEST_CASE_COUNT"
        checker_path.write_text(read_text(checker_path).replace(checker_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"scripts/zigux/check-phase7-rbtree-parity.py: {checker_marker}"])
        cases_run += 1

        write_fixture_root(root)
        slice_marker = SLICE_AUTHENTICATED_BUILD_MARKER
        marker_path.write_text(read_text(marker_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"Documentation/zigux/phase7-rbtree-slice.md: {slice_marker}"])
        cases_run += 1

        write_fixture_root(root)
        slice_marker = SLICE_ERASE_BOUNDARY_MARKER
        marker_path.write_text(read_text(marker_path).replace(slice_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"Documentation/zigux/phase7-rbtree-slice.md: {slice_marker}"])
        cases_run += 1

        write_fixture_root(root)
        helper_path = root / "lib/rbtree.zig"
        helper_marker = "pub const Node = struct {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"lib/rbtree.zig: {helper_marker}"])
        cases_run += 1

        write_fixture_root(root)
        helper_marker = "pub const RootCached = struct {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"lib/rbtree.zig: {helper_marker}"])
        cases_run += 1

        write_fixture_root(root)
        helper_marker = "pub fn eraseInit(node: *Node, root: *Root) void {"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"lib/rbtree.zig: {helper_marker}"])
        cases_run += 1

        write_fixture_root(root)
        helper_marker = "pub fn rb_find_add_cached"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"lib/rbtree.zig: {helper_marker}"])
        cases_run += 1

        write_fixture_root(root)
        helper_marker = "pub fn rb_next_postorder"
        helper_path.write_text(read_text(helper_path).replace(helper_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"lib/rbtree.zig: {helper_marker}"])
        cases_run += 1

        write_fixture_root(root)
        companion_path = root / "zigux/tests/phase7_rbtree.zig"
        companion_marker = "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree.zig: {companion_marker}"])
        cases_run += 1

        write_fixture_root(root)
        companion_marker = "phase 7 rbtree companion replays non-leftmost cached erase ownership boundaries"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree.zig: {companion_marker}"])
        cases_run += 1

        write_fixture_root(root)
        companion_marker = "phase 7 rbtree companion replays reverse traversal aliases and detached null stops"
        companion_path.write_text(read_text(companion_path).replace(companion_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree.zig: {companion_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_path = root / "zigux/tests/phase7_rbtree_survey.zig"
        survey_marker = 'try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree.json");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try expectSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-test:");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try expectSliceContains(manifest.ownership_focus, "fixture truthfulness now also keeps the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed boundaries explicit across the returned JSON fixture, returned C harness, dedicated survey, and dedicated replay");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try expectContains(manifest.next_bounded_step, "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try expectContains(manifest.next_bounded_step, "phase7-rbtree-test:");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try expectContains(manifest.next_bounded_step, "phase7-test:");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try expectSliceContains(manifest.readable_non_owner_paths, "zigux/tests/phase7_build.zig");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try std.testing.expectEqual(@as(usize, 0), manifest.public_fallback_non_owner_paths.len);'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        survey_marker = 'try expectContains(makefile, "phase7-rbtree-test:");'
        survey_path.write_text(read_text(survey_path).replace(survey_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_survey.zig: {survey_marker}"])
        cases_run += 1

        write_fixture_root(root)
        fixture_path = root / "zigux/tests/fixtures/phase7_rbtree.json"
        fixture_marker = '"packet": "phase7-rbtree-parity-fixture"'
        fixture_path.write_text(read_text(fixture_path).replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/fixtures/phase7_rbtree.json: {fixture_marker}"])
        cases_run += 1

        write_fixture_root(root)
        fixture_marker = '"non_leftmost_cached_erase"'
        fixture_path.write_text(read_text(fixture_path).replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/fixtures/phase7_rbtree.json: {fixture_marker}"])
        cases_run += 1

        write_fixture_root(root)
        harness_path = root / "zigux/tests/fixtures/phase7_rbtree_c_harness.c"
        harness_marker = ".non_leftmost_cached_erase = {"
        harness_path.write_text(read_text(harness_path).replace(harness_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/fixtures/phase7_rbtree_c_harness.c: {harness_marker}"])
        cases_run += 1

        write_fixture_root(root)
        harness_marker = ".reverse_alias_detached = {"
        harness_path.write_text(read_text(harness_path).replace(harness_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/fixtures/phase7_rbtree_c_harness.c: {harness_marker}"])
        cases_run += 1

        write_fixture_root(root)
        harness_marker = '.current_master_state = "ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness",'
        harness_path.write_text(read_text(harness_path).replace(harness_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/fixtures/phase7_rbtree_c_harness.c: {harness_marker}"])
        cases_run += 1

        write_fixture_root(root)
        makefile_path = root / "zigux/Makefile"
        makefile_marker = "phase7-validate:"
        makefile_path.write_text(read_text(makefile_path).replace(makefile_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/Makefile: {makefile_marker}"])
        cases_run += 1

        write_fixture_root(root)
        makefile_marker = "phase7-rbtree-test:"
        makefile_path.write_text(read_text(makefile_path).replace(makefile_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/Makefile: {makefile_marker}"])
        cases_run += 1

        write_fixture_root(root)
        makefile_marker = "phase7-rbtree-survey:"
        makefile_path.write_text(read_text(makefile_path).replace(makefile_marker + "\n", "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/Makefile: {makefile_marker}"])
        cases_run += 1

        write_fixture_root(root)
        manifest_path = root / "zigux/tests/phase7_rbtree_manifest.json"
        manifest_path.write_text(read_text(manifest_path).replace(NEXT_STEP_WRAPPER_MARKER, "", 1), encoding="utf-8")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: next_bounded_step"])
        cases_run += 1

        write_fixture_root(root)
        manifest_path.write_text(read_text(manifest_path).replace(NEXT_STEP_ERASE_CASES_MARKER, "", 1), encoding="utf-8")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: next_bounded_step"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["current_direct_readback_state"] = "fixture_only"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: current_direct_readback_state"])
        cases_run += 1

        write_fixture_root(root)
        manifest_path.write_text(read_text(manifest_path).replace(MANIFEST_EMPTY_FALLBACK_MARKER, "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_manifest.json: {MANIFEST_EMPTY_FALLBACK_MARKER}"])
        cases_run += 1

        write_fixture_root(root)
        manifest_path.write_text(read_text(manifest_path).replace(MANIFEST_ERASE_BOUNDARY_MARKER, "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_manifest.json: {MANIFEST_ERASE_BOUNDARY_MARKER}"])
        cases_run += 1

        write_fixture_root(root)
        manifest_path.write_text(read_text(manifest_path).replace(MAKEFILE_POSITIVE_ROUTE_MARKER, "", 1), encoding="utf-8")
        assert validate(root) == ([], [f"zigux/tests/phase7_rbtree_manifest.json: {MAKEFILE_POSITIVE_ROUTE_MARKER}"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["lane_key"] = "P7-L12"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: lane_key"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["phase"] = "Phase 8"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: phase"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["anchor"] = "tools/lib/rbtree.c"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: anchor"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["readable_makefile_markers"] = []
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: readable_makefile_markers"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["public_fallback_non_owner_paths"] = ["raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase7_build.zig"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: public_fallback_non_owner_paths"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["missing_paths"] = ["zigux/tests/phase7_rbtree_extra.zig"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: missing_paths"])
        cases_run += 1

        write_fixture_root(root)
        manifest = json.loads(read_text(manifest_path))
        manifest["next_bounded_step"] = "Stay in the same `kernel-leaf-libraries` lane."
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert validate(root) == ([], ["zigux/tests/phase7_rbtree_manifest.json: next_bounded_step"])
        cases_run += 1

        assert cases_run == SELF_TEST_CASE_COUNT

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

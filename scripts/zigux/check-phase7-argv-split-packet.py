#!/usr/bin/env python3
"""Validate the current Phase 7 argv_split helper packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

EXPECTED_MANIFEST_LANE_KEY = "P7-L09"
EXPECTED_MANIFEST_PHASE = "Phase 7"
EXPECTED_MANIFEST_ANCHOR = "lib/argv_split.c"
EXPECTED_MANIFEST_STATE = "helper_slice_test_fixture_survey_manifest_anchor"
EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (
    "Keep same-lane follow-through limited to the returned fixture-backed helper-local "
    "survey-manifest-checker truthfulness packet, and reopen only when a fresh reread finds "
    "the next checker-, manifest-, slice-note-, or fixture-vector drift inside that packet "
    "before widening into any new vector-backed replay proof."
)
EXPECTED_REVIEW_SURFACES = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "lib/argv_split.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "samples/zigux/README.md",
]
EXPECTED_COVERED_HELPERS = [
    "countArgc",
    "argvSplit",
    "argvSplitWithArgc",
    "argvFree",
    "ArgvSplitResult.deinit",
    "ArgvSplitResult.cArgv",
]
EXPECTED_OWNERSHIP_FOCUS = [
    "argvSplit() duplicates the caller input before tokenizing so returned tokens stay inside helper-owned storage",
    "countArgc(), cStringPrefix(), nextArgSpan(), and nextSplitArgSpan() keep token counting and separator zeroing bounded to the exported C-string prefix",
    "blank-input results reuse exported empty storage and argv sentinel views without widening beyond the returned packet",
    "whitespace-before-first-NUL input still reuses the exported empty storage and argv sentinel views because cStringPrefix() bounds blank-input handling to the first NUL",
    "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins",
    "blank, whitespace-only, whitespace-before-first-NUL, and leading-NUL inputs all reuse the same shared empty storage, argv, and cArgv() views across calls so blank-result teardown stays repeatable without hidden allocation churn",
    "non-blank sibling results keep owned storage, argv slices, and exported cArgv views isolated across calls",
    "deinit(), argvFree(), allocator-failure cleanup, and overflow rejection keep release ownership explicit without widening beyond the returned argv packet",
    "fixture vectors keep copied-storage, blank-input, whitespace-before-first-NUL blank-sentinel reuse, first-NUL truncation, and quoted-token packet expectations reviewable without widening into shared-control ownership",
    "the helper-local argv_split packet stays reviewable without treating `Documentation/zigux/phase7-helper-lane-sequencing.md` as same-lane ownership",
    "the no-standalone-argv sample boundary stays explicit only while `samples/zigux/README.md` keeps `*argv*` listed among the no-extra-sample reminders",
]

REQUIRED_FILES = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "lib/argv_split.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "samples/zigux/README.md",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "`PHASE7_STATUS=helper_local_test_packet_landed`",
        "`PHASE7_SLICE=argv-split-runtime-leaf`",
        "`zigux/tests/fixtures/phase7_argv_split_vectors.zig`",
        "Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned fixture-backed packet.",
        "Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet, and reopen only when a fresh reread finds the next checker-, manifest-, slice-note-, or fixture-vector drift inside that packet before widening into any new vector-backed replay proof.",
        "whitespace-before-first-NUL input still reuses the canonical blank storage and exported argv sentinels without allocator space",
        "leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins",
        "blank, whitespace-only, whitespace-before-first-NUL, and leading-NUL inputs all reuse the same shared empty storage, argv, and `cArgv()` views across calls, so blank-result teardown stays repeatable without hidden allocation churn",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
        "PHASE7_ARGV_SPLIT_PACKET=pass",
        "PHASE7_ARGV_SPLIT_PACKET=fail",
        "MISSING_PHASE7_ARGV_SPLIT_FILES_START",
        "MISSING_PHASE7_ARGV_SPLIT_FILES_END",
        "MISSING_PHASE7_ARGV_SPLIT_MARKERS_START",
        "MISSING_PHASE7_ARGV_SPLIT_MARKERS_END",
        "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\",",
        'EXPECTED_MANIFEST_LANE_KEY = "P7-L09"',
        'EXPECTED_MANIFEST_PHASE = "Phase 7"',
        'EXPECTED_MANIFEST_ANCHOR = "lib/argv_split.c"',
        'EXPECTED_MANIFEST_STATE = "helper_slice_test_fixture_survey_manifest_anchor"',
        "EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (",
        "EXPECTED_REVIEW_SURFACES = [",
        "EXPECTED_COVERED_HELPERS = [",
        "EXPECTED_OWNERSHIP_FOCUS = [",
        "MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_START",
        "MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_END",
    ],
    "lib/argv_split.zig": [
        "pub const ArgvSplitResult = struct {",
        "pub fn countArgc(",
        "pub fn argvSplit(",
        "pub fn argvSplitWithArgc(",
        "pub fn argvFree(allocator: std.mem.Allocator, result: *ArgvSplitResult) void {",
        "pub fn cArgv(self: *const ArgvSplitResult) [*:null]const ?[*:0]const u8 {",
        "fn nextSplitArgSpan(",
        'test "argvSplit treats whitespace before the first NUL as blank input" {',
        'test "argvSplit treats a leading NUL as blank input" {',
        'test "argvSplit reuses shared blank sentinel views without argc output" {',
        'test "blank-input deinit on one caller keeps the shared sentinel views usable for another" {',
        'test "argvFree resets released non-blank results to the shared empty exported views" {',
        'test "non-blank argvSplit results keep caller-owned teardown isolated across siblings" {',
        'test "argv_split aliases preserve helper-local count, split, and free behavior" {',
        'test "argvSplit reports overflow before sizing the null-terminated argv vector" {',
    ],
    "zigux/tests/phase7_argv_split.zig": [
        'const argv_split = @import("argv_split");',
        'const fixture_vectors = @import("fixtures/phase7_argv_split_vectors.zig");',
        'test "phase 7 argv split companion replays copied-storage token ownership" {',
        'test "phase 7 argv split companion replays non-blank cross-call ownership independence" {',
        'test "phase 7 argv split companion replays blank-input sentinel reuse and first-NUL truncation" {',
        'test "phase 7 argv split companion replays repeated blank-result sentinel reuse" {',
        'test "phase 7 argv split companion replays whitespace-before-first-NUL sentinel reuse" {',
        'test "phase 7 argv split companion replays fixture-backed leading-NUL ownership and quoted-token boundaries" {',
        'test "phase 7 argv split companion replays caller-owned teardown and failure boundaries" {',
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        '"anchor": "lib/argv_split.c"',
        '"current_master_state": "helper_slice_test_fixture_survey_manifest_anchor"',
        '"zigux/tests/fixtures/phase7_argv_split_vectors.zig"',
        "fixture-backed helper-local survey-manifest-checker truthfulness packet",
        "whitespace-before-first-NUL input still reuses the exported empty storage and argv sentinel views because cStringPrefix() bounds blank-input handling to the first NUL",
        "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins",
        "fixture vectors keep copied-storage, blank-input, whitespace-before-first-NUL blank-sentinel reuse, first-NUL truncation, and quoted-token packet expectations reviewable without widening into shared-control ownership",
        "the helper-local argv_split packet stays reviewable without treating `Documentation/zigux/phase7-helper-lane-sequencing.md` as same-lane ownership",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        'test "phase 7 argv split survey keeps the returned fixture-backed helper-local packet truthful" {',
        'try std.testing.expectEqualStrings("helper_slice_test_fixture_survey_manifest_anchor", manifest.current_master_state);',
        'const fixture_vectors = try readRepoFile(allocator, fixture_path);',
        'try std.testing.expect(!stringSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-helper-lane-sequencing.md"));',
        r'try expectNotContains(checker, "\"Documentation/zigux/phase7-helper-lane-sequencing.md\",");',
        r'try expectContains(helper, "test \"argvSplit treats whitespace before the first NUL as blank input\" {");',
        r'try expectContains(helper, "test \"argvSplit reuses shared blank sentinel views without argc output\" {");',
        r'try expectContains(helper, "test \"argvSplit reports overflow before sizing the null-terminated argv vector\" {");',
        'try expectContains(helper_companion, "phase 7 argv split companion replays repeated blank-result sentinel reuse");',
        'try expectContains(helper_companion, "phase 7 argv split companion replays whitespace-before-first-NUL sentinel reuse");',
        'try expectContains(helper_companion, "phase 7 argv split companion replays fixture-backed leading-NUL ownership and quoted-token boundaries");',
        'try expectContains(fixture_vectors, "whitespace_before_first_nul_reuses_empty_packet");',
        'try expectContains(slice_note, "leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins");',
        'try expectStringSliceContains(manifest.ownership_focus, "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins");',
    ],
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": [
        "pub const ArgvSplitVector = struct {",
        "pub const phase7_argv_split_vectors = [_]ArgvSplitVector{",
        "copied_storage_whitespace_packet",
        "blank_input_reuses_empty_packet",
        "whitespace_before_first_nul_reuses_empty_packet",
        "leading_nul_reuses_empty_packet",
        "first_nul_truncation_keeps_tail_outside_packet",
        "quoted_tokens_stay_whitespace_split",
    ],
    "samples/zigux/README.md": [
        "Current `master` still ships no standalone Phase 5 sample-root files here for:",
        "* `*argv*`",
    ],
}

COUNTED_MARKERS = {
    "samples/zigux/README.md": [
        ("* `*argv*`", 1),
    ],
}

SELF_TEST_CASE_COUNT = 80


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


def collect_mismatched_counts(root: Path) -> list[str]:
    mismatches: list[str] = []
    for rel, markers in COUNTED_MARKERS.items():
        text = read_text(root / rel)
        for marker, expected in markers:
            actual = text.count(marker)
            if actual != expected:
                mismatches.append(f"{rel}: expected {expected} occurrence(s) of {marker!r}, found {actual}")
    return mismatches


def collect_missing_manifest_entries(manifest: dict[str, object]) -> list[str]:
    missing: list[str] = []

    review_surfaces = manifest.get("review_surfaces")
    if not isinstance(review_surfaces, list):
        return ["zigux/tests/phase7_argv_split_manifest.json: review_surfaces"]
    for item in EXPECTED_REVIEW_SURFACES:
        if item not in review_surfaces:
            missing.append(f"zigux/tests/phase7_argv_split_manifest.json: review_surfaces: {item}")

    covered_helpers = manifest.get("covered_helpers")
    if not isinstance(covered_helpers, list):
        return ["zigux/tests/phase7_argv_split_manifest.json: covered_helpers"]
    for item in EXPECTED_COVERED_HELPERS:
        if item not in covered_helpers:
            missing.append(f"zigux/tests/phase7_argv_split_manifest.json: covered_helpers: {item}")

    ownership_focus = manifest.get("ownership_focus")
    if not isinstance(ownership_focus, list):
        return ["zigux/tests/phase7_argv_split_manifest.json: ownership_focus"]
    for item in EXPECTED_OWNERSHIP_FOCUS:
        if item not in ownership_focus:
            missing.append(f"zigux/tests/phase7_argv_split_manifest.json: ownership_focus: {item}")

    missing_paths = manifest.get("missing_paths")
    if missing_paths != []:
        missing.append("zigux/tests/phase7_argv_split_manifest.json: missing_paths")

    if manifest.get("next_bounded_step") != EXPECTED_MANIFEST_NEXT_BOUNDED_STEP:
        missing.append("zigux/tests/phase7_argv_split_manifest.json: next_bounded_step")

    return missing


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    manifest = json.loads(read_text(root / "zigux/tests/phase7_argv_split_manifest.json"))
    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE_KEY:
        return [], ["zigux/tests/phase7_argv_split_manifest.json: lane_key"], []
    if manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        return [], ["zigux/tests/phase7_argv_split_manifest.json: phase"], []
    if manifest.get("anchor") != EXPECTED_MANIFEST_ANCHOR:
        return [], ["zigux/tests/phase7_argv_split_manifest.json: anchor"], []
    if manifest.get("current_master_state") != EXPECTED_MANIFEST_STATE:
        return [], ["zigux/tests/phase7_argv_split_manifest.json: current_master_state"], []

    missing_manifest_entries = collect_missing_manifest_entries(manifest)
    if missing_manifest_entries:
        return [], missing_manifest_entries, []

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        return missing_files, missing_markers, []

    return missing_files, [], collect_mismatched_counts(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        if rel == "zigux/tests/phase7_argv_split_manifest.json":
            continue
        write(tmp_root / rel, "\n".join(REQUIRED_MARKERS[rel]) + "\n")

    write(
        tmp_root / "zigux/tests/phase7_argv_split_manifest.json",
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE_KEY,
                "phase": EXPECTED_MANIFEST_PHASE,
                "verified_on_utc": "2026-05-25T13:02:02Z",
                "anchor": EXPECTED_MANIFEST_ANCHOR,
                "current_master_state": EXPECTED_MANIFEST_STATE,
                "review_surfaces": EXPECTED_REVIEW_SURFACES,
                "covered_helpers": EXPECTED_COVERED_HELPERS,
                "missing_paths": [],
                "ownership_focus": EXPECTED_OWNERSHIP_FOCUS,
                "next_bounded_step": EXPECTED_MANIFEST_NEXT_BOUNDED_STEP,
            },
            indent=2,
        )
        + "\n",
    )


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, mismatched_counts = validate(tmp_root)
    assert missing_markers == [], case
    assert mismatched_counts == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, mismatched_counts = validate(tmp_root)
    assert missing_files == [], case
    assert mismatched_counts == [], case
    assert missing_markers == [marker], case


def expect_mismatched_count(case: str, tmp_root: Path, mismatch: str) -> None:
    missing_files, missing_markers, mismatched_counts = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert mismatched_counts == [mismatch], case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])
        cases_run = 0

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        fixture_path.unlink()
        expect_missing_file("missing_argv_split_fixture_vectors", tmp_root, "zigux/tests/fixtures/phase7_argv_split_vectors.zig")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_path = tmp_root / "zigux" / "tests" / "phase7_argv_split.zig"
        companion_path.unlink()
        expect_missing_file("missing_argv_split_companion", tmp_root, "zigux/tests/phase7_argv_split.zig")
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        slice_text = read_text(slice_path)
        slice_marker = "Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet, and reopen only when a fresh reread finds the next checker-, manifest-, slice-note-, or fixture-vector drift inside that packet before widening into any new vector-backed replay proof."
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_fixture_packet_marker", tmp_root, f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_text = read_text(slice_path)
        slice_marker = "whitespace-before-first-NUL input still reuses the canonical blank storage and exported argv sentinels without allocator space"
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_first_nul_blank_marker", tmp_root, f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_text = read_text(slice_path)
        slice_marker = "leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins"
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_leading_nul_blank_marker", tmp_root, f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        slice_text = read_text(slice_path)
        slice_marker = "blank, whitespace-only, whitespace-before-first-NUL, and leading-NUL inputs all reuse the same shared empty storage, argv, and `cArgv()` views across calls, so blank-result teardown stays repeatable without hidden allocation churn"
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_shared_blank_views_marker", tmp_root, f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
        checker_text = read_text(checker_path)
        checker_marker = "--self-test"
        checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_checker_selftest_flag_marker", tmp_root, f"scripts/zigux/check-phase7-argv-split-packet.py: {checker_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_text = read_text(checker_path)
        checker_marker = REQUIRED_MARKERS["scripts/zigux/check-phase7-argv-split-packet.py"][8]
        checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_checker_fixture_marker", tmp_root, f"scripts/zigux/check-phase7-argv-split-packet.py: {checker_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        checker_text = read_text(checker_path)
        checker_marker = "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass"
        checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_checker_selftest_pass_marker", tmp_root, f"scripts/zigux/check-phase7-argv-split-packet.py: {checker_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        for checker_marker, case in [
            ("PHASE7_ARGV_SPLIT_PACKET=pass", "missing_checker_pass_output_marker"),
            ("PHASE7_ARGV_SPLIT_PACKET=fail", "missing_checker_fail_output_marker"),
            ("MISSING_PHASE7_ARGV_SPLIT_FILES_START", "missing_checker_missing_files_start_marker"),
            ("MISSING_PHASE7_ARGV_SPLIT_FILES_END", "missing_checker_missing_files_end_marker"),
            ("MISSING_PHASE7_ARGV_SPLIT_MARKERS_START", "missing_checker_missing_markers_start_marker"),
            ("MISSING_PHASE7_ARGV_SPLIT_MARKERS_END", "missing_checker_missing_markers_end_marker"),
            ('EXPECTED_MANIFEST_LANE_KEY = "P7-L09"', "missing_checker_expected_manifest_lane_key"),
            ('EXPECTED_MANIFEST_PHASE = "Phase 7"', "missing_checker_expected_manifest_phase"),
            ('EXPECTED_MANIFEST_ANCHOR = "lib/argv_split.c"', "missing_checker_expected_manifest_anchor"),
            (
                'EXPECTED_MANIFEST_STATE = "helper_slice_test_fixture_survey_manifest_anchor"',
                "missing_checker_expected_manifest_state",
            ),
            ("EXPECTED_MANIFEST_NEXT_BOUNDED_STEP = (", "missing_checker_expected_manifest_next_bounded_step"),
            ("EXPECTED_OWNERSHIP_FOCUS = [", "missing_checker_expected_ownership_focus"),
            ("MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_START", "missing_checker_mismatched_counts_start_marker"),
            ("MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_END", "missing_checker_mismatched_counts_end_marker"),
        ]:
            checker_text = read_text(checker_path)
            checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
            expect_missing_marker(case, tmp_root, f"scripts/zigux/check-phase7-argv-split-packet.py: {checker_marker}")
            cases_run += 1
            write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].remove("zigux/tests/fixtures/phase7_argv_split_vectors.zig")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "missing_manifest_fixture_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: review_surfaces: zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = "whitespace-before-first-NUL input still reuses the exported empty storage and argv sentinel views because cStringPrefix() bounds blank-input handling to the first NUL"
        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(manifest_marker)
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "missing_manifest_first_nul_blank_focus",
            tmp_root,
            f"zigux/tests/phase7_argv_split_manifest.json: ownership_focus: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins"
        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(manifest_marker)
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "missing_manifest_leading_nul_blank_focus",
            tmp_root,
            f"zigux/tests/phase7_argv_split_manifest.json: ownership_focus: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = "fixture vectors keep copied-storage, blank-input, whitespace-before-first-NUL blank-sentinel reuse, first-NUL truncation, and quoted-token packet expectations reviewable without widening into shared-control ownership"
        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(manifest_marker)
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "missing_manifest_fixture_first_nul_vector_focus",
            tmp_root,
            f"zigux/tests/phase7_argv_split_manifest.json: ownership_focus: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest_marker = "the helper-local argv_split packet stays reviewable without treating `Documentation/zigux/phase7-helper-lane-sequencing.md` as same-lane ownership"
        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"].remove(manifest_marker)
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "missing_manifest_owner_boundary_marker",
            tmp_root,
            f"zigux/tests/phase7_argv_split_manifest.json: ownership_focus: {manifest_marker}",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["review_surfaces"].remove("samples/zigux/README.md")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "missing_manifest_review_surface_guard",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: review_surfaces: samples/zigux/README.md",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["covered_helpers"].remove("argvFree")
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "missing_manifest_covered_helper_guard",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: covered_helpers: argvFree",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["missing_paths"] = ["samples/zigux/argv_example.zig"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_missing_paths_must_stay_empty",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: missing_paths",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["next_bounded_step"] = (
            "Keep same-lane follow-through limited to the returned fixture-backed helper-local "
            "survey-manifest-checker truthfulness packet or one bounded vector-backed replay proof."
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_next_bounded_step_truthfulness_guard",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: next_bounded_step",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["ownership_focus"] = "helper-local ownership drift"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker(
            "manifest_ownership_focus_must_stay_list",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: ownership_focus",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["lane_key"] = "P7-L08"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("argv_split_manifest_lane_key", tmp_root, "zigux/tests/phase7_argv_split_manifest.json: lane_key")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["phase"] = "Phase 8"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("argv_split_manifest_phase", tmp_root, "zigux/tests/phase7_argv_split_manifest.json: phase")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["anchor"] = "lib/cmdline.c"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("argv_split_manifest_anchor", tmp_root, "zigux/tests/phase7_argv_split_manifest.json: anchor")
        cases_run += 1
        write_fixture_root(tmp_root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_master_state"] = "helper_slice_test_fixture_survey_manifest_checker_anchor"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("argv_split_manifest_state", tmp_root, "zigux/tests/phase7_argv_split_manifest.json: current_master_state")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][0]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_test_entrypoint_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][1]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_manifest_state_assertion", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][2]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_fixture_reader", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][3]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_owner_boundary_guard", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][4]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_checker_boundary_guard", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][5]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_first_nul_blank_proof_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][6]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_blank_without_argc_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][7]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_overflow_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][8]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_repeated_blank_replay_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][9]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_whitespace_before_first_nul_replay_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][10]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_fixture_backed_companion_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][11]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_fixture_first_nul_vector_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][12]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_slice_leading_nul_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][13]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_manifest_leading_nul_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "quoted_tokens_stay_whitespace_split"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "blank_input_reuses_empty_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_blank_input_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "whitespace_before_first_nul_reuses_empty_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_blank_prefix_first_nul_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "leading_nul_reuses_empty_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_leading_nul_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "first_nul_truncation_keeps_tail_outside_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_first_nul_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "argv_split.zig"
        helper_text = read_text(helper_path)
        helper_marker = "pub fn countArgc("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_countargc_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "pub fn argvSplit("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_argvsplit_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "pub fn argvSplitWithArgc("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_argvsplitwithargc_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "pub fn argvFree(allocator: std.mem.Allocator, result: *ArgvSplitResult) void {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_argvfree_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "pub fn cArgv(self: *const ArgvSplitResult) [*:null]const ?[*:0]const u8 {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_cargv_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "fn nextSplitArgSpan("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_nextsplitargspan_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "argvSplit treats whitespace before the first NUL as blank input" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_first_nul_blank_input_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "argvSplit treats a leading NUL as blank input" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_leading_nul_blank_input_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "argvSplit reuses shared blank sentinel views without argc output" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_blank_without_argc_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "argvSplit reports overflow before sizing the null-terminated argv vector" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_overflow_guard_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "blank-input deinit on one caller keeps the shared sentinel views usable for another" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_blank_deinit_sentinel_reuse_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "argvFree resets released non-blank results to the shared empty exported views" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_argvfree_reset_to_shared_empty_views_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "non-blank argvSplit results keep caller-owned teardown isolated across siblings" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_non_blank_teardown_isolation_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = 'test "argv_split aliases preserve helper-local count, split, and free behavior" {'
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_alias_parity_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'const fixture_vectors = @import("fixtures/phase7_argv_split_vectors.zig");'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_fixture_import_marker", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'test "phase 7 argv split companion replays copied-storage token ownership" {'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_copied_storage_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'test "phase 7 argv split companion replays non-blank cross-call ownership independence" {'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_cross_call_ownership_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'test "phase 7 argv split companion replays blank-input sentinel reuse and first-NUL truncation" {'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_blank_input_first_nul_marker", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'test "phase 7 argv split companion replays repeated blank-result sentinel reuse" {'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_repeated_blank_replay_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'test "phase 7 argv split companion replays whitespace-before-first-NUL sentinel reuse" {'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_whitespace_before_first_nul_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = 'test "phase 7 argv split companion replays fixture-backed leading-NUL ownership and quoted-token boundaries" {'
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_fixture_backed_packet_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_text = read_text(samples_path)
        samples_marker = "Current `master` still ships no standalone Phase 5 sample-root files here for:"
        samples_path.write_text(samples_text.replace(samples_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_samples_header_boundary", tmp_root, f"samples/zigux/README.md: {samples_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_text = read_text(samples_path)
        samples_marker = "* `*argv*`"
        samples_path.write_text(samples_text.replace(samples_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_samples_argv_boundary", tmp_root, f"samples/zigux/README.md: {samples_marker}")
        cases_run += 1
        write_fixture_root(tmp_root)

        samples_path.write_text(read_text(samples_path) + "* `*argv*`\n", encoding="utf-8")
        expect_mismatched_count(
            "duplicate_samples_argv_boundary",
            tmp_root,
            "samples/zigux/README.md: expected 1 occurrence(s) of '* `*argv*`', found 2",
        )
        cases_run += 1
        write_fixture_root(tmp_root)

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run

    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to validate (default: current repository root)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-tests instead of validating the repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, mismatched_counts = validate(args.repo_root)
    if missing_files:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_MARKERS_END")
        return 1

    if mismatched_counts:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_START")
        for item in mismatched_counts:
            print(item)
        print("MISMATCHED_PHASE7_ARGV_SPLIT_COUNTS_END")
        return 1

    print("PHASE7_ARGV_SPLIT_PACKET=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_ARGV_SPLIT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the current Phase 7 argv_split helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

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
        "Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet or one bounded vector-backed replay proof.",
        "whitespace-before-first-NUL input still reuses the canonical blank storage and exported argv sentinels without allocator space",
        "leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
        "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\",",
    ],
    "lib/argv_split.zig": [
        "pub const ArgvSplitResult = struct {",
        "pub fn countArgc(",
        "pub fn argvSplit(",
        "pub fn argvSplitWithArgc(",
        "pub fn argvFree(allocator: std.mem.Allocator, result: *ArgvSplitResult) void {",
        "pub fn cArgv(self: *const ArgvSplitResult) [*:null]const ?[*:0]const u8 {",
        "fn nextSplitArgSpan(",
        "test \"argvSplit treats whitespace before the first NUL as blank input\" {",
        "test \"argvSplit treats a leading NUL as blank input\" {",
        "test \"argvSplit reuses shared blank sentinel views without argc output\" {",
        "test \"blank-input deinit on one caller keeps the shared sentinel views usable for another\" {",
        "test \"argvFree resets released non-blank results to the shared empty exported views\" {",
        "test \"non-blank argvSplit results keep caller-owned teardown isolated across siblings\" {",
    ],
    "zigux/tests/phase7_argv_split.zig": [
        "const argv_split = @import(\"argv_split\");",
        "test \"phase 7 argv split companion replays copied-storage token ownership\" {",
        "test \"phase 7 argv split companion replays non-blank cross-call ownership independence\" {",
        "test \"phase 7 argv split companion replays blank-input sentinel reuse and first-NUL truncation\" {",
        "test \"phase 7 argv split companion replays repeated blank-result sentinel reuse\" {",
        "test \"phase 7 argv split companion replays fixture-backed blank-prefix ownership and quoted-token boundaries\" {",
        "test \"phase 7 argv split companion replays caller-owned teardown and failure boundaries\" {",
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        "\"anchor\": \"lib/argv_split.c\"",
        "\"current_master_state\": \"helper_slice_test_fixture_survey_manifest_anchor\"",
        "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"",
        "fixture-backed helper-local survey-manifest-checker truthfulness packet",
        "whitespace-before-first-NUL input still reuses the exported empty storage and argv sentinel views because cStringPrefix() bounds blank-input handling to the first NUL",
        "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins",
        "fixture vectors keep copied-storage, blank-input, whitespace-before-first-NUL blank-sentinel reuse, first-NUL truncation, and quoted-token packet expectations reviewable without widening into shared-control ownership",
        "the helper-local argv_split packet stays reviewable without treating `Documentation/zigux/phase7-helper-lane-sequencing.md` as same-lane ownership",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "test \"phase 7 argv split survey keeps the returned fixture-backed helper-local packet truthful\" {",
        "try std.testing.expectEqualStrings(\"helper_slice_test_fixture_survey_manifest_anchor\", manifest.current_master_state);",
        "const fixture_vectors = try readRepoFile(allocator, fixture_path);",
        "try std.testing.expect(!stringSliceContains(manifest.review_surfaces, \"Documentation/zigux/phase7-helper-lane-sequencing.md\"));",
        "try expectNotContains(checker, \"\\\"Documentation/zigux/phase7-helper-lane-sequencing.md\\\",\");",
        "try expectContains(helper, \"test \\\"argvSplit treats whitespace before the first NUL as blank input\\\" {\");",
        "try expectContains(helper, \"test \\\"argvSplit reuses shared blank sentinel views without argc output\\\" {\");",
        "try expectContains(helper_companion, \"phase 7 argv split companion replays repeated blank-result sentinel reuse\");",
        "try expectContains(helper_companion, \"phase 7 argv split companion replays fixture-backed blank-prefix ownership and quoted-token boundaries\");",
        "try expectContains(fixture_vectors, \"whitespace_before_first_nul_reuses_empty_packet\");",
        "try expectContains(slice_note, \"leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins\");",
        "try expectStringSliceContains(manifest.ownership_focus, \"leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins\");",
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

SELF_TEST_CASE_COUNT = 45


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        fixture_path.unlink()
        expect_missing_file("missing_argv_split_fixture_vectors", tmp_root, "zigux/tests/fixtures/phase7_argv_split_vectors.zig")
        write_fixture_root(tmp_root)

        companion_path = tmp_root / "zigux" / "tests" / "phase7_argv_split.zig"
        companion_path.unlink()
        expect_missing_file("missing_argv_split_companion", tmp_root, "zigux/tests/phase7_argv_split.zig")
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        slice_text = read_text(slice_path)
        slice_marker = "Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet or one bounded vector-backed replay proof."
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_fixture_packet_marker", tmp_root, f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}")
        write_fixture_root(tmp_root)

        slice_text = read_text(slice_path)
        slice_marker = "whitespace-before-first-NUL input still reuses the canonical blank storage and exported argv sentinels without allocator space"
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_first_nul_blank_marker", tmp_root, f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}")
        write_fixture_root(tmp_root)

        slice_text = read_text(slice_path)
        slice_marker = "leading-NUL input also reuses the canonical blank storage and exported argv sentinels without allocator space because `cStringPrefix()` stops before token counting or tokenization begins"
        slice_path.write_text(slice_text.replace(slice_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_slice_leading_nul_blank_marker", tmp_root, f"Documentation/zigux/phase7-argv-split-slice.md: {slice_marker}")
        write_fixture_root(tmp_root)

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
        checker_text = read_text(checker_path)
        checker_marker = "--self-test"
        checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_checker_selftest_flag_marker", tmp_root, f"scripts/zigux/check-phase7-argv-split-packet.py: {checker_marker}")
        write_fixture_root(tmp_root)

        checker_text = read_text(checker_path)
        checker_marker = "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\","
        checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_checker_fixture_marker", tmp_root, f"scripts/zigux/check-phase7-argv-split-packet.py: {checker_marker}")
        write_fixture_root(tmp_root)

        checker_text = read_text(checker_path)
        checker_marker = "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass"
        checker_path.write_text(checker_text.replace(checker_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_checker_selftest_pass_marker", tmp_root, f"scripts/zigux/check-phase7-argv-split-packet.py: {checker_marker}")
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        manifest_text = read_text(manifest_path)
        manifest_marker = "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\""
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_manifest_fixture_marker", tmp_root, f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}")
        write_fixture_root(tmp_root)

        manifest_text = read_text(manifest_path)
        manifest_marker = "whitespace-before-first-NUL input still reuses the exported empty storage and argv sentinel views because cStringPrefix() bounds blank-input handling to the first NUL"
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_manifest_first_nul_blank_focus", tmp_root, f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}")
        write_fixture_root(tmp_root)

        manifest_text = read_text(manifest_path)
        manifest_marker = "leading-NUL input also reuses the exported empty storage and argv sentinel views because cStringPrefix() stops before token counting or tokenization begins"
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_manifest_leading_nul_blank_focus", tmp_root, f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}")
        write_fixture_root(tmp_root)

        manifest_text = read_text(manifest_path)
        manifest_marker = "fixture vectors keep copied-storage, blank-input, whitespace-before-first-NUL blank-sentinel reuse, first-NUL truncation, and quoted-token packet expectations reviewable without widening into shared-control ownership"
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_manifest_fixture_first_nul_vector_focus", tmp_root, f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}")
        write_fixture_root(tmp_root)

        manifest_text = read_text(manifest_path)
        manifest_marker = "the helper-local argv_split packet stays reviewable without treating `Documentation/zigux/phase7-helper-lane-sequencing.md` as same-lane ownership"
        manifest_path.write_text(manifest_text.replace(manifest_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_manifest_owner_boundary_marker", tmp_root, f"zigux/tests/phase7_argv_split_manifest.json: {manifest_marker}")
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][2]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_fixture_reader", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][3]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_owner_boundary_guard", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][4]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_checker_boundary_guard", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][5]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_first_nul_blank_proof_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][6]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_blank_without_argc_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][7]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_repeated_blank_replay_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][8]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_fixture_backed_companion_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][9]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_fixture_first_nul_vector_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][10]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_slice_leading_nul_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        survey_text = read_text(survey_path)
        survey_marker = REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"][11]
        survey_path.write_text(survey_text.replace(survey_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_survey_manifest_leading_nul_marker", tmp_root, f"zigux/tests/phase7_argv_split_survey.zig: {survey_marker}")
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "quoted_tokens_stay_whitespace_split"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "blank_input_reuses_empty_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_blank_input_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "whitespace_before_first_nul_reuses_empty_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_blank_prefix_first_nul_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "leading_nul_reuses_empty_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_leading_nul_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        write_fixture_root(tmp_root)

        fixture_text = read_text(fixture_path)
        fixture_marker = "first_nul_truncation_keeps_tail_outside_packet"
        fixture_path.write_text(fixture_text.replace(fixture_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_fixture_first_nul_vector_case", tmp_root, f"zigux/tests/fixtures/phase7_argv_split_vectors.zig: {fixture_marker}")
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "argv_split.zig"
        helper_text = read_text(helper_path)
        helper_marker = "pub fn countArgc("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_countargc_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "pub fn argvSplit("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_argvsplit_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "pub fn argvSplitWithArgc("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_argvsplitwithargc_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "fn nextSplitArgSpan("
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_nextsplitargspan_marker", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "test \"argvSplit treats whitespace before the first NUL as blank input\" {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_first_nul_blank_input_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "test \"argvSplit treats a leading NUL as blank input\" {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_leading_nul_blank_input_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "test \"argvSplit reuses shared blank sentinel views without argc output\" {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_blank_without_argc_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "test \"blank-input deinit on one caller keeps the shared sentinel views usable for another\" {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_blank_deinit_sentinel_reuse_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "test \"argvFree resets released non-blank results to the shared empty exported views\" {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_argvfree_reset_to_shared_empty_views_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        helper_text = read_text(helper_path)
        helper_marker = "test \"non-blank argvSplit results keep caller-owned teardown isolated across siblings\" {"
        helper_path.write_text(helper_text.replace(helper_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_helper_non_blank_teardown_isolation_test", tmp_root, f"lib/argv_split.zig: {helper_marker}")
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = "test \"phase 7 argv split companion replays non-blank cross-call ownership independence\" {"
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_cross_call_ownership_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = "test \"phase 7 argv split companion replays repeated blank-result sentinel reuse\" {"
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_repeated_blank_replay_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        write_fixture_root(tmp_root)

        companion_text = read_text(companion_path)
        companion_marker = "test \"phase 7 argv split companion replays fixture-backed blank-prefix ownership and quoted-token boundaries\" {"
        companion_path.write_text(companion_text.replace(companion_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_companion_fixture_backed_packet_test", tmp_root, f"zigux/tests/phase7_argv_split.zig: {companion_marker}")
        write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_text = read_text(samples_path)
        samples_marker = "* `*argv*`"
        samples_path.write_text(samples_text.replace(samples_marker + "\n", "", 1), encoding="utf-8")
        expect_missing_marker("missing_samples_argv_boundary", tmp_root, f"samples/zigux/README.md: {samples_marker}")
        write_fixture_root(tmp_root)

        assert SELF_TEST_CASE_COUNT == 45

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

    missing_files, missing_markers = validate(args.repo_root)
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

    print("PHASE7_ARGV_SPLIT_PACKET=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_ARGV_SPLIT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
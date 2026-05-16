#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "lib/cmdline.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_build.zig",
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "PHASE7_LANE_KEY=P7-L05",
        "scope: first low-risk runtime-safe parsing helpers only",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_cmdline_manifest.json",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "make -C zigux phase7-cmdline-survey",
        "shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`;",
        "getOption() and getOptions() keep the oversized wrap contract explicit across both 32-bit boundary inputs and full-width unsigned parses,",
        "memparse() preserves suffix scaling, `simple_strtoull()`-style leading-plus rejection, stop-index reporting, and saturated oversized-prefix handling before any size-suffix shift is applied",
        "exact bare-option matching for comma-delimited flags stays reviewable through `parseOptionStr()`",
        "leading-whitespace handling keeps the Linux-style empty sentinel token",
        "leading quoted tokens that contain `=` and still split at the first equals",
        "Treat any fresh shared `phase7_build.zig` replay claim as a cross-packet follow-through that should be backed by a new direct shared replay, not just by current-master readback.",
    ],
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "cmdline packet, lane `P7-L05`:",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "scripts/zigux/check-phase7-cmdline-packet.py",
        "PHASE7_CMDLINE_LANE=P7-L05",
        "`P7-L05` owns only cmdline helper-local parity, survey, manifest, fixture, checker, or same-slice reminder drift;",
    ],
    "Documentation/zigux/review-checklist.md": [
        "there is no standalone `samples/zigux/*cmdline*` reference sample",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "lib/cmdline.zig",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_cmdline_manifest.json",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "lib/cmdline.zig",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_cmdline_manifest.json",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    ],
    "lib/cmdline.zig": [
        "pub fn getOption",
        "pub fn getOptions",
        "pub fn memparse",
        "pub fn parseOptionStr",
        "pub fn nextArg",
        'test "getOption keeps incomplete hex prefixes aligned with Linux simple_strtoull consumption"',
        'test "getOptions expands negative ranges and negative upper bounds like Linux get_range"',
        'test "parseOptionStr only matches full comma-delimited options"',
        'try std.testing.expect(!parseOptionStr("", ""));',
        'test "nextArg returns an empty sentinel token before leading whitespace and trims the following rest"',
        'test "getOption and getOptions preserve oversized wrap semantics"',
        'test "getOption preserves validator-only numeric acceptance without explicit leading plus"',
        'test "memparse saturates oversized unsigned prefixes before applying suffix handling"',
        'test "memparse keeps saturated prefixes aligned when size suffixes still apply"',
    ],
    "zigux/tests/phase7_cmdline.zig": [
        'const next_arg_vectors = @import("fixtures/phase7_cmdline_next_arg_vectors.zig");',
        "phase 7 getOption clears caller output on malformed signed and unsigned input",
        "phase 7 getOption keeps incomplete hex prefixes aligned with Linux simple_strtoull consumption",
        "phase 7 getOption and getOptions preserve oversized wrap semantics",
        "phase 7 getOption preserves validator-only numeric acceptance without explicit leading plus",
        "phase 7 getOptions expands negative ranges and negative upper bounds like Linux get_range",
        "phase 7 parseOptionStr matches only exact bare options",
        'try std.testing.expect(!cmdline.parseOptionStr("", ""));',
        "phase 7 nextArg matches serialized edge fixtures",
        "phase 7 nextArg keeps empty-input and leading-whitespace ownership explicit",
        "phase 7 nextArg keeps leading quoted param, value, and rest borrowed from the caller buffer",
        "phase 7 memparse saturates oversized unsigned prefixes before applying suffix handling",
        "phase 7 memparse keeps saturated prefixes aligned when size suffixes still apply",
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        "P7-L05",
        "scripts/zigux/check-phase7-cmdline-packet.py",
        "zigux/tests/phase7_cmdline_manifest.json",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`",
        "phase 7 getOption and getOptions preserve Linux-style range parsing",
        "phase 7 getOption clears caller output on malformed signed and unsigned input",
        "phase 7 nextArg matches serialized edge fixtures",
        "leading equals sign stays in the parameter token",
        "trailing spaces after key=value trim to empty rest",
    ],
    "zigux/tests/phase7_cmdline_manifest.json": [
        '"lane_key": "P7-L05"',
        '"anchor": "lib/cmdline.c"',
        '"lib/cmdline.zig"',
        '"zigux/tests/phase7_cmdline.zig"',
        '"zigux/tests/phase7_cmdline_survey.zig"',
        '"zigux/tests/phase7_cmdline_manifest.json"',
        '"zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"',
        '"scripts/zigux/check-phase7-cmdline-packet.py"',
        '"getOption"',
        '"getOptions"',
        '"memparse"',
        '"parseOptionStr"',
        '"nextArg"',
        '"nextArg caller-owned buffer slices"',
        '"nextArg empty-input borrowed-slice reuse"',
        '"nextArg leading-whitespace sentinel token"',
        '"validator-first shared Phase 7 replay route"',
        '"phase7-cmdline-helper"',
        '"phase7-cmdline-dedicated-tests"',
        '"phase7-cmdline-shared-fixtures"',
        '"phase7-cmdline-slice-note"',
        '"phase7-cmdline-manifest-packet"',
        '"phase7-cmdline-survey-gate"',
    ],
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig": [
        '.name = "leading quoted token with equals splits like Linux",',
        '.name = "leading quoted token with equals and no trailing token leaves empty rest",',
        '.name = "leading equals sign stays in the parameter token",',
        '.name = "unterminated quoted value consumes the token tail",',
        '.name = "trailing spaces after key=value trim to empty rest",',
        '.name = "whitespace-only tail after key=value trims to empty rest",',
    ],
}

REQUIRED_EXACT_LINES = {
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "* `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`",
        "* `python3 scripts/zigux/check-phase7-cmdline-packet.py`",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    for rel, lines in REQUIRED_EXACT_LINES.items():
        text_lines = (root / rel).read_text(encoding="utf-8").splitlines()
        for line in lines:
            if line not in text_lines:
                missing.append(f"{rel}: {line}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {}
    for rel, markers in REQUIRED_MARKERS.items():
        lines = list(markers)
        lines.extend(REQUIRED_EXACT_LINES.get(rel, []))
        fixture_text[rel] = "\n".join(lines) + "\n"
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text[rel], encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    index = original.rfind(old)
    assert index != -1, case
    updated = original[:index] + new + original[index + len(old) :]
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        (tmp_root / "zigux/tests/phase7_cmdline_manifest.json").unlink()
        expect_missing_file(
            "missing_manifest",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json",
        )
        write_fixture_root(tmp_root)

        cases = [
            (
                "docs_root_boundary_marker",
                "Documentation/zigux/README.md",
                "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
                "Documentation/zigux/README.md: current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
            ),
            (
                "slice_lane_key_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "PHASE7_LANE_KEY=P7-L05",
                "Documentation/zigux/phase7-cmdline-slice.md: PHASE7_LANE_KEY=P7-L05",
            ),
            (
                "slice_checker_selftest_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "* `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`",
                "Documentation/zigux/phase7-cmdline-slice.md: * `python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test`",
            ),
            (
                "slice_checker_live_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "* `python3 scripts/zigux/check-phase7-cmdline-packet.py`",
                "Documentation/zigux/phase7-cmdline-slice.md: * `python3 scripts/zigux/check-phase7-cmdline-packet.py`",
            ),
            (
                "slice_shared_route_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`;",
                "Documentation/zigux/phase7-cmdline-slice.md: shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`;",
            ),
            (
                "slice_wrap_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "getOption() and getOptions() keep the oversized wrap contract explicit across both 32-bit boundary inputs and full-width unsigned parses,",
                "Documentation/zigux/phase7-cmdline-slice.md: getOption() and getOptions() keep the oversized wrap contract explicit across both 32-bit boundary inputs and full-width unsigned parses,",
            ),
            (
                "slice_memparse_saturation_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "memparse() preserves suffix scaling, `simple_strtoull()`-style leading-plus rejection, stop-index reporting, and saturated oversized-prefix handling before any size-suffix shift is applied",
                "Documentation/zigux/phase7-cmdline-slice.md: memparse() preserves suffix scaling, `simple_strtoull()`-style leading-plus rejection, stop-index reporting, and saturated oversized-prefix handling before any size-suffix shift is applied",
            ),
            (
                "slice_parse_option_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "exact bare-option matching for comma-delimited flags stays reviewable through `parseOptionStr()`",
                "Documentation/zigux/phase7-cmdline-slice.md: exact bare-option matching for comma-delimited flags stays reviewable through `parseOptionStr()`",
            ),
            (
                "slice_whitespace_sentinel_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "leading-whitespace handling keeps the Linux-style empty sentinel token",
                "Documentation/zigux/phase7-cmdline-slice.md: leading-whitespace handling keeps the Linux-style empty sentinel token",
            ),
            (
                "slice_quoted_equals_marker",
                "Documentation/zigux/phase7-cmdline-slice.md",
                "leading quoted tokens that contain `=` and still split at the first equals",
                "Documentation/zigux/phase7-cmdline-slice.md: leading quoted tokens that contain `=` and still split at the first equals",
            ),
            (
                "helper_lane_checker_marker",
                "Documentation/zigux/phase7-helper-lane-sequencing.md",
                "scripts/zigux/check-phase7-cmdline-packet.py",
                "Documentation/zigux/phase7-helper-lane-sequencing.md: scripts/zigux/check-phase7-cmdline-packet.py",
            ),
            (
                "helper_lane_owner_marker",
                "Documentation/zigux/phase7-helper-lane-sequencing.md",
                "`P7-L05` owns only cmdline helper-local parity, survey, manifest, fixture, checker, or same-slice reminder drift;",
                "Documentation/zigux/phase7-helper-lane-sequencing.md: `P7-L05` owns only cmdline helper-local parity, survey, manifest, fixture, checker, or same-slice reminder drift;",
            ),
            (
                "review_checklist_boundary_marker",
                "Documentation/zigux/review-checklist.md",
                "there is no standalone `samples/zigux/*cmdline*` reference sample",
                "Documentation/zigux/review-checklist.md: there is no standalone `samples/zigux/*cmdline*` reference sample",
            ),
            (
                "samples_boundary_marker",
                "samples/zigux/README.md",
                "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;",
                "samples/zigux/README.md: current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;",
            ),
            (
                "helper_next_arg_marker",
                "lib/cmdline.zig",
                "pub fn nextArg",
                "lib/cmdline.zig: pub fn nextArg",
            ),
            (
                "helper_whitespace_sentinel_marker",
                "lib/cmdline.zig",
                'test "nextArg returns an empty sentinel token before leading whitespace and trims the following rest"',
                'lib/cmdline.zig: test "nextArg returns an empty sentinel token before leading whitespace and trims the following rest"',
            ),
            (
                "helper_negative_range_marker",
                "lib/cmdline.zig",
                'test "getOptions expands negative ranges and negative upper bounds like Linux get_range"',
                'lib/cmdline.zig: test "getOptions expands negative ranges and negative upper bounds like Linux get_range"',
            ),
            (
                "helper_parse_option_test_marker",
                "lib/cmdline.zig",
                'test "parseOptionStr only matches full comma-delimited options"',
                'lib/cmdline.zig: test "parseOptionStr only matches full comma-delimited options"',
            ),
            (
                "helper_parse_option_empty_marker",
                "lib/cmdline.zig",
                'try std.testing.expect(!parseOptionStr("", ""));',
                'lib/cmdline.zig: try std.testing.expect(!parseOptionStr("", ""));',
            ),
            (
                "helper_wrap_marker",
                "lib/cmdline.zig",
                'test "getOption and getOptions preserve oversized wrap semantics"',
                'lib/cmdline.zig: test "getOption and getOptions preserve oversized wrap semantics"',
            ),
            (
                "helper_validator_only_acceptance_marker",
                "lib/cmdline.zig",
                'test "getOption preserves validator-only numeric acceptance without explicit leading plus"',
                'lib/cmdline.zig: test "getOption preserves validator-only numeric acceptance without explicit leading plus"',
            ),
            (
                "helper_memparse_saturation_marker",
                "lib/cmdline.zig",
                'test "memparse saturates oversized unsigned prefixes before applying suffix handling"',
                'lib/cmdline.zig: test "memparse saturates oversized unsigned prefixes before applying suffix handling"',
            ),
            (
                "helper_memparse_suffix_saturation_marker",
                "lib/cmdline.zig",
                'test "memparse keeps saturated prefixes aligned when size suffixes still apply"',
                'lib/cmdline.zig: test "memparse keeps saturated prefixes aligned when size suffixes still apply"',
            ),
            (
                "tests_fixture_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 nextArg matches serialized edge fixtures",
                "zigux/tests/phase7_cmdline.zig: phase 7 nextArg matches serialized edge fixtures",
            ),
            (
                "tests_negative_range_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 getOptions expands negative ranges and negative upper bounds like Linux get_range",
                "zigux/tests/phase7_cmdline.zig: phase 7 getOptions expands negative ranges and negative upper bounds like Linux get_range",
            ),
            (
                "tests_parse_option_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 parseOptionStr matches only exact bare options",
                "zigux/tests/phase7_cmdline.zig: phase 7 parseOptionStr matches only exact bare options",
            ),
            (
                "tests_parse_option_empty_marker",
                "zigux/tests/phase7_cmdline.zig",
                'try std.testing.expect(!cmdline.parseOptionStr("", ""));',
                'zigux/tests/phase7_cmdline.zig: try std.testing.expect(!cmdline.parseOptionStr("", ""));',
            ),
            (
                "tests_whitespace_owner_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 nextArg keeps empty-input and leading-whitespace ownership explicit",
                "zigux/tests/phase7_cmdline.zig: phase 7 nextArg keeps empty-input and leading-whitespace ownership explicit",
            ),
            (
                "tests_leading_quoted_owner_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 nextArg keeps leading quoted param, value, and rest borrowed from the caller buffer",
                "zigux/tests/phase7_cmdline.zig: phase 7 nextArg keeps leading quoted param, value, and rest borrowed from the caller buffer",
            ),
            (
                "tests_wrap_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 getOption and getOptions preserve oversized wrap semantics",
                "zigux/tests/phase7_cmdline.zig: phase 7 getOption and getOptions preserve oversized wrap semantics",
            ),
            (
                "tests_validator_only_acceptance_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 getOption preserves validator-only numeric acceptance without explicit leading plus",
                "zigux/tests/phase7_cmdline.zig: phase 7 getOption preserves validator-only numeric acceptance without explicit leading plus",
            ),
            (
                "tests_memparse_saturation_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 memparse saturates oversized unsigned prefixes before applying suffix handling",
                "zigux/tests/phase7_cmdline.zig: phase 7 memparse saturates oversized unsigned prefixes before applying suffix handling",
            ),
            (
                "tests_memparse_suffix_saturation_marker",
                "zigux/tests/phase7_cmdline.zig",
                "phase 7 memparse keeps saturated prefixes aligned when size suffixes still apply",
                "zigux/tests/phase7_cmdline.zig: phase 7 memparse keeps saturated prefixes aligned when size suffixes still apply",
            ),
            (
                "survey_checker_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "scripts/zigux/check-phase7-cmdline-packet.py",
                "zigux/tests/phase7_cmdline_survey.zig: scripts/zigux/check-phase7-cmdline-packet.py",
            ),
            (
                "survey_manifest_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "zigux/tests/phase7_cmdline_manifest.json",
                "zigux/tests/phase7_cmdline_survey.zig: zigux/tests/phase7_cmdline_manifest.json",
            ),
            (
                "survey_shared_route_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`",
                "zigux/tests/phase7_cmdline_survey.zig: shared-route note: fresh 2026-05-13 current-master readback confirms `zigux/tests/phase7_build.zig` together with the sibling `string_helpers`, `argv_split`, and `rbtree` helper-local replays is directly readable on `master`",
            ),
            (
                "survey_range_parsing_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "phase 7 getOption and getOptions preserve Linux-style range parsing",
                "zigux/tests/phase7_cmdline_survey.zig: phase 7 getOption and getOptions preserve Linux-style range parsing",
            ),
            (
                "survey_clear_output_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "phase 7 getOption clears caller output on malformed signed and unsigned input",
                "zigux/tests/phase7_cmdline_survey.zig: phase 7 getOption clears caller output on malformed signed and unsigned input",
            ),
            (
                "survey_next_arg_fixture_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "phase 7 nextArg matches serialized edge fixtures",
                "zigux/tests/phase7_cmdline_survey.zig: phase 7 nextArg matches serialized edge fixtures",
            ),
            (
                "survey_fixture_name_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "leading equals sign stays in the parameter token",
                "zigux/tests/phase7_cmdline_survey.zig: leading equals sign stays in the parameter token",
            ),
            (
                "survey_trailing_spaces_marker",
                "zigux/tests/phase7_cmdline_survey.zig",
                "trailing spaces after key=value trim to empty rest",
                "zigux/tests/phase7_cmdline_survey.zig: trailing spaces after key=value trim to empty rest",
            ),
            (
                "manifest_checker_marker",
                "zigux/tests/phase7_cmdline_manifest.json",
                '"scripts/zigux/check-phase7-cmdline-packet.py"',
                'zigux/tests/phase7_cmdline_manifest.json: "scripts/zigux/check-phase7-cmdline-packet.py"',
            ),
            (
                "manifest_helper_marker",
                "zigux/tests/phase7_cmdline_manifest.json",
                '"phase7-cmdline-helper"',
                'zigux/tests/phase7_cmdline_manifest.json: "phase7-cmdline-helper"',
            ),
            (
                "manifest_ownership_marker",
                "zigux/tests/phase7_cmdline_manifest.json",
                '"nextArg leading-whitespace sentinel token"',
                'zigux/tests/phase7_cmdline_manifest.json: "nextArg leading-whitespace sentinel token"',
            ),
            (
                "fixture_quoted_equals_marker",
                "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
                '.name = "leading quoted token with equals splits like Linux",',
                'zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig: .name = "leading quoted token with equals splits like Linux",',
            ),
            (
                "fixture_quoted_equals_empty_rest_marker",
                "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
                '.name = "leading quoted token with equals and no trailing token leaves empty rest",',
                'zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig: .name = "leading quoted token with equals and no trailing token leaves empty rest",',
            ),
            (
                "fixture_case_marker",
                "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
                '.name = "leading equals sign stays in the parameter token",',
                'zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig: .name = "leading equals sign stays in the parameter token",',
            ),
        ]

        for case, rel, marker, expected in cases:
            mutate_file(tmp_root, rel, marker, "", case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = 1 + len(cases)
    print("PHASE7_CMDLINE_PACKET_SELF_TEST=pass")
    print(f"PHASE7_CMDLINE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 7 cmdline helper packet stays aligned.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_CMDLINE_PACKET=fail")
        print("MISSING_PHASE7_CMDLINE_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_CMDLINE_PACKET_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_CMDLINE_PACKET=fail")
        print("MISSING_PHASE7_CMDLINE_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_CMDLINE_PACKET_MARKERS_END")
        return 1

    print("PHASE7_CMDLINE_PACKET=pass")
    print(f"PHASE7_CMDLINE_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_CMDLINE_PACKET_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
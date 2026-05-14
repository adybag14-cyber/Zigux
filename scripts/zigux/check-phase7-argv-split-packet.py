#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "lib/argv_split.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "PHASE7_LANE_KEY=P7-L09",
        "scope: first low-risk argument-vector parsing and teardown helpers only",
        "keep stronger ownership and pointer discipline through the explicit `argvSplitWithArgc()` count mirror, `cArgv()` export, and `argvFree()` / `deinit()` teardown path",
        "keep copied-buffer ownership so later source mutation does not affect split results",
        "non-blank cross-result teardown safety where `deinit()` or `argvFree()` on one live split keeps a sibling caller's storage, argv slices, and exported `cArgv()` view intact",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "Keep this slice parked unless fresh repo inspection finds one concrete `argv_split` parity, survey, manifest, fixture, or shared reminder drift inside the current helper packet.",
    ],
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "argv-split packet, lane `P7-L09`:",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "PHASE7_ARGV_SPLIT_LANE=P7-L09",
        "PHASE7_ARGV_SPLIT_SCHEDULE_ALIAS=P7-Y07 -> P7-L09",
        "scheduled alias note: recurring scheduled lane `P7-Y07` is the older schedule label for this same argv-split packet and must be treated as the same owner, not as a second helper lane",
        "`P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, or reminder drift.",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-argv-split-slice.md",
    ],
    "lib/argv_split.zig": [
        "pub fn countArgc",
        "pub fn argvSplit",
        "pub fn argvSplitWithArgc",
        "pub fn argvFree",
        "pub fn cArgv",
        "if (!hasAnyArg(current))",
        "self.* = .{",
    ],
    "zigux/tests/phase7_argv_split.zig": [
        "const phase7_vectors = @import(\"fixtures/phase7_argv_split_vectors.zig\");",
        "phase 7 argvSplit matches focused parity fixtures",
        "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        "phase 7 argvSplit deinit on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 argvFree on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 argvFree on a non-blank result restores the canonical blank sentinels",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result",
        "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "const active_lane_key = \"P7-L09\";",
        "try std.testing.expectEqualStrings(active_lane_key, manifest.lane_key);",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split_manifest.json",
        "phase 7 argvSplit zeroes copied whitespace separators across the tokenized buffer",
        "phase 7 argvSplit zeroes carriage-return, vertical-tab, and form-feed separators too",
        "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        "phase 7 argvSplit deinit on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 argvFree on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "phase 7 argvSplit deinit clears exported storage and argv views",
        "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
        "argvFree on one live non-blank result does not disturb another caller-owned split result",
        "deinit on one live non-blank result does not disturb another caller-owned split result",
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        "\"lane_key\": \"P7-L09\"",
        "\"anchor\": \"lib/argv_split.c\"",
        "\"argv_split_pair_compile\": {",
        "\"status\": \"confirmed\"",
        "\"lib/argv_split.zig\"",
        "\"zigux/tests/phase7_argv_split.zig\"",
        "\"countArgc\"",
        "\"argvSplit\"",
        "\"argvSplitWithArgc\"",
        "\"cArgv\"",
        "\"argvFree\"",
        "\"deinit\"",
        "copied token-buffer ownership and later source-mutation isolation",
        "owned-storage reuse keeps token pointers inside caller-managed storage",
        "non-blank results keep storage, argv slices, and C-argv views distinct across callers",
        "argvFree on one live non-blank result does not disturb another caller-owned split result",
        "deinit on one live non-blank result does not disturb another caller-owned split result",
        "blank-input sentinel reuse stays stable across argvFree and deinit, including shared empty-sentinel teardown beside another blank caller",
    ],
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": [
        ".name = \"repeated whitespace collapses into separators\"",
        ".name = \"whitespace before first NUL stays blank\"",
        ".name = \"leading NUL truncates to zero argv entries\"",
        ".name = \"quote characters stay inside returned tokens\"",
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
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
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
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        (tmp_root / "zigux/tests/phase7_argv_split_manifest.json").unlink()
        expect_missing_file(
            "missing_manifest",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md",
            "PHASE7_LANE_KEY=P7-L09",
            "",
            "slice_lane_key_marker",
        )
        expect_missing_marker(
            "slice_lane_key_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: PHASE7_LANE_KEY=P7-L09",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md",
            "non-blank cross-result teardown safety where `deinit()` or `argvFree()` on one live split keeps a sibling caller's storage, argv slices, and exported `cArgv()` view intact",
            "",
            "slice_teardown_safety_marker",
        )
        expect_missing_marker(
            "slice_teardown_safety_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: non-blank cross-result teardown safety where `deinit()` or `argvFree()` on one live split keeps a sibling caller's storage, argv slices, and exported `cArgv()` view intact",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-argv-split-slice.md",
            "",
            "review_checklist_slice_marker",
        )
        expect_missing_marker(
            "review_checklist_slice_marker",
            tmp_root,
            "Documentation/zigux/review-checklist.md: Documentation/zigux/phase7-argv-split-slice.md",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "Documentation/zigux/phase7-argv-split-slice.md",
            "",
            "helper_lane_slice_reference_marker",
        )
        expect_missing_marker(
            "helper_lane_slice_reference_marker",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md: Documentation/zigux/phase7-argv-split-slice.md",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "PHASE7_ARGV_SPLIT_LANE=P7-L09",
            "",
            "helper_lane_key_marker",
        )
        expect_missing_marker(
            "helper_lane_key_marker",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md: PHASE7_ARGV_SPLIT_LANE=P7-L09",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "PHASE7_ARGV_SPLIT_SCHEDULE_ALIAS=P7-Y07 -> P7-L09",
            "",
            "helper_lane_alias_marker",
        )
        expect_missing_marker(
            "helper_lane_alias_marker",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md: PHASE7_ARGV_SPLIT_SCHEDULE_ALIAS=P7-Y07 -> P7-L09",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "scheduled alias note: recurring scheduled lane `P7-Y07` is the older schedule label for this same argv-split packet and must be treated as the same owner, not as a second helper lane",
            "",
            "helper_lane_schedule_note_marker",
        )
        expect_missing_marker(
            "helper_lane_schedule_note_marker",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md: scheduled alias note: recurring scheduled lane `P7-Y07` is the older schedule label for this same argv-split packet and must be treated as the same owner, not as a second helper lane",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md",
            "`P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, or reminder drift.",
            "",
            "helper_lane_owner_marker",
        )
        expect_missing_marker(
            "helper_lane_owner_marker",
            tmp_root,
            "Documentation/zigux/phase7-helper-lane-sequencing.md: `P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, or reminder drift.",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json",
            "copied token-buffer ownership and later source-mutation isolation",
            "",
            "manifest_ownership_marker",
        )
        expect_missing_marker(
            "manifest_ownership_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: copied token-buffer ownership and later source-mutation isolation",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json",
            "owned-storage reuse keeps token pointers inside caller-managed storage",
            "",
            "manifest_storage_pointer_marker",
        )
        expect_missing_marker(
            "manifest_storage_pointer_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json: owned-storage reuse keeps token pointers inside caller-managed storage",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig",
            "const active_lane_key = \"P7-L09\";",
            "",
            "survey_lane_key_marker",
        )
        expect_missing_marker(
            "survey_lane_key_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: const active_lane_key = \"P7-L09\";",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
            "",
            "tests_argv_free_marker",
        )
        expect_missing_marker(
            "tests_argv_free_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 argvFree on a non-blank result restores the canonical blank sentinels",
            "",
            "tests_blank_reset_marker",
        )
        expect_missing_marker(
            "tests_blank_reset_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvFree on a non-blank result restores the canonical blank sentinels",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
            ".name = \"quote characters stay inside returned tokens\"",
            "",
            "fixture_quote_marker",
        )
        expect_missing_marker(
            "fixture_quote_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: .name = \"quote characters stay inside returned tokens\"",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "lib/argv_split.zig",
            "pub fn cArgv",
            "",
            "helper_c_argv_marker",
        )
        expect_missing_marker(
            "helper_c_argv_marker",
            tmp_root,
            "lib/argv_split.zig: pub fn cArgv",
        )

    case_count = 16
    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 7 argv_split helper-local packet stays aligned.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_PACKET_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_ARGV_SPLIT_PACKET=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_PACKET_MARKERS_END")
        return 1

    print("PHASE7_ARGV_SPLIT_PACKET=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_ARGV_SPLIT_PACKET_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
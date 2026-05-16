#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "lib/argv_split.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 7 runtime helper gates",
        "make -C zigux phase7-validate",
        "Run Phase 7 runtime helper tests",
        "make -C zigux phase7-test",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "zigux/tests/phase7_argv_split_manifest.json",
        "scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "PHASE7_LANE_KEY=P7-L09",
        "scope: first low-risk argument-vector parsing and teardown helpers only",
        "keep stronger ownership and pointer discipline through the explicit `argvSplitWithArgc()` count mirror, `cArgv()` export, and `argvFree()` / `deinit()` teardown path",
        "keep copied-buffer ownership so later source mutation does not affect split results",
        "non-blank cross-result teardown safety where `deinit()` or `argvFree()` on one live split keeps a sibling caller's storage, argv slices, and exported `cArgv()` view intact",
        "blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`, including shared empty-sentinel teardown beside another blank caller",
        "exported storage and argv views resetting back to the canonical empty sentinels after teardown",
        "allocator-failure cleanup so interrupted setup frees partially built ownership state before the helper returns",
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
        "`argv_split` is parked as a landed helper-local packet with its helper, dedicated test, survey, manifest, fixture module, and dedicated packet checker still visible",
        "`P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, checker, or reminder drift.",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "`python3 scripts/zigux/check-phase7-argv-split-packet.py`",
        "make -C zigux phase7-argv-split-survey",
        "make -C zigux phase7-validate",
        "make -C zigux phase7-test",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-argv-split-slice.md`",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_build.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split_survey.zig",
        "make -C zigux phase7-validate",
    ],
    "scripts/zigux/validate-phase7.py": [
        "\"scripts/zigux/check-phase7-argv-split-packet.py\"",
        "\"zigux/tests/phase7_argv_split.zig\"",
        "\"zigux/tests/phase7_argv_split_survey.zig\"",
        "\"zigux/tests/phase7_argv_split_manifest.json\"",
        "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"",
    ],
    "lib/argv_split.zig": [
        "pub fn countArgc",
        "pub fn argvSplit",
        "pub fn argvSplitWithArgc",
        "pub fn argvFree",
        "pub fn cArgv",
        "const argc = countArgc(current);",
        "if (argc == 0) {",
        "self.* = .{",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    ],
    "zigux/tests/phase7_argv_split.zig": [
        "const phase7_vectors = @import(\"fixtures/phase7_argv_split_vectors.zig\");",
        "phase 7 argvSplit matches focused parity fixtures",
        "phase 7 argvSplit token buffer does not alias the source text",
        "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy",
        "phase 7 argvSplit zeroes copied whitespace separators across the tokenized buffer",
        "phase 7 argvSplit zeroes carriage-return, vertical-tab, and form-feed separators too",
        "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
        "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        "phase 7 argvSplit deinit on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 argvFree on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 argvFree on a non-blank result restores the canonical blank sentinels",
        "phase 7 blank argvSplit deinit on one caller keeps shared sentinel views usable for another",
        "phase 7 blank argvFree on one caller keeps shared sentinel views usable for another",
        "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned",
        "phase 7 argvSplit deinit clears exported storage and argv views",
        "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 whitespace before first NUL reuses the blank sentinels without allocator space",
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
        "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
        "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        "phase 7 argvSplit deinit on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 argvFree on one non-blank result keeps sibling caller-owned views intact",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 whitespace before first NUL reuses the blank sentinels without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "phase 7 argvFree on a non-blank result restores the canonical blank sentinels",
        "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned",
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
        "canonical blank sentinels, repeatable teardown, and a null-terminated argv view",
    ],
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": [
        ".name = \"repeated whitespace collapses into separators\"",
        ".name = \"whitespace before first NUL stays blank\"",
        ".name = \"leading NUL truncates to zero argv entries\"",
        ".name = \"first NUL stops counting and splitting\"",
        ".name = \"quote characters stay inside returned tokens\"",
    ],
    "zigux/tests/phase7_build.zig": [
        "\"phase7_argv_split.zig\"",
        "\"phase7-argv-split-survey-tests\"",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
        "phase7-argv-split-survey:",
        "phase7-test:",
        "phase7: phase7-validate phase7-test",
    ],
}

REQUIRED_EXACT_LINES = {
    "zigux/tests/README.md": [
        "  * `scripts/zigux/check-phase7-argv-split-packet.py`",
        "  * `make -C zigux phase7-validate`",
        "  * `make -C zigux phase7`",
    ],
}

MISSING_FILE_CASES = [
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase7_argv_split_manifest.json",
]

MISSING_MARKER_CASES = [
    ("Documentation/zigux/README.md", "scripts/zigux/check-phase7-argv-split-packet.py"),
    ("Documentation/zigux/phase7-argv-split-slice.md", "PHASE7_LANE_KEY=P7-L09"),
    (
        "Documentation/zigux/phase7-helper-lane-sequencing.md",
        "PHASE7_ARGV_SPLIT_SCHEDULE_ALIAS=P7-Y07 -> P7-L09",
    ),
    (
        "Documentation/zigux/phase7-helper-lane-sequencing.md",
        "`argv_split` is parked as a landed helper-local packet with its helper, dedicated test, survey, manifest, fixture module, and dedicated packet checker still visible",
    ),
    (
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "make -C zigux phase7-argv-split-survey",
    ),
    ("Documentation/zigux/review-checklist.md", "Documentation/zigux/phase7-argv-split-slice.md"),
    ("Documentation/zigux/review-checklist.md", "scripts/zigux/check-phase7-argv-split-packet.py"),
    ("Documentation/zigux/review-checklist.md", "zigux/tests/phase7_argv_split_survey.zig"),
    (
        "samples/zigux/README.md",
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep that boundary under `Documentation/zigux/phase7-argv-split-slice.md`",
    ),
    ("samples/zigux/README.md", "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"),
    ("samples/zigux/README.md", "scripts/zigux/check-phase7-argv-split-packet.py"),
    ("samples/zigux/README.md", "scripts/zigux/check-phase7-build-wiring.py"),
    ("scripts/zigux/README.md", "zigux/tests/phase7_argv_split_survey.zig"),
    ("scripts/zigux/validate-phase7.py", "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\""),
    ("lib/argv_split.zig", "pub fn cArgv"),
    ("zigux/tests/README.md", "zigux/tests/phase7_argv_split_manifest.json"),
    ("zigux/tests/README.md", "  * `scripts/zigux/check-phase7-argv-split-packet.py`"),
    ("zigux/tests/README.md", "  * `make -C zigux phase7-validate`"),
    ("zigux/tests/README.md", "  * `make -C zigux phase7`"),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 argvSplit token buffer does not alias the source text",
    ),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy",
    ),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 argvSplit zeroes copied whitespace separators across the tokenized buffer",
    ),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 argvSplit zeroes carriage-return, vertical-tab, and form-feed separators too",
    ),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned",
    ),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
    ),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 blank argvSplit deinit on one caller keeps shared sentinel views usable for another",
    ),
    (
        "zigux/tests/phase7_argv_split.zig",
        "phase 7 blank argvFree on one caller keeps shared sentinel views usable for another",
    ),
    (
        "zigux/tests/phase7_argv_split_survey.zig",
        "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
    ),
    (
        "zigux/tests/phase7_argv_split_survey.zig",
        "phase 7 whitespace before first NUL reuses the blank sentinels without allocator space",
    ),
    (
        "zigux/tests/phase7_argv_split_survey.zig",
        "phase 7 argvFree on a non-blank result restores the canonical blank sentinels",
    ),
    (
        "zigux/tests/phase7_argv_split_survey.zig",
        "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned",
    ),
    (
        "zigux/tests/phase7_argv_split_manifest.json",
        "owned-storage reuse keeps token pointers inside caller-managed storage",
    ),
    (
        "zigux/tests/phase7_argv_split_manifest.json",
        "blank-input sentinel reuse stays stable across argvFree and deinit, including shared empty-sentinel teardown beside another blank caller",
    ),
    (
        "zigux/tests/phase7_argv_split_manifest.json",
        "canonical blank sentinels, repeatable teardown, and a null-terminated argv view",
    ),
    (
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        ".name = \"first NUL stops counting and splitting\"",
    ),
    (
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        ".name = \"quote characters stay inside returned tokens\"",
    ),
    ("zigux/tests/phase7_build.zig", "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));"),
    ("zigux/Makefile", "phase7-argv-split-survey:"),
    (
        "Documentation/zigux/phase7-helper-lane-sequencing.md",
        "`P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, checker, or reminder drift.",
    ),
    (
        "Documentation/zigux/phase7-argv-split-slice.md",
        "blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`, including shared empty-sentinel teardown beside another blank caller",
    ),
]


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
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        marker_lines = list(REQUIRED_MARKERS[rel])
        exact_lines = list(REQUIRED_EXACT_LINES.get(rel, []))
        path.write_text("\n".join(marker_lines + exact_lines) + "\n", encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [expected], case


def mutate_file(tmp_root: Path, rel: str, marker: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    index = original.rfind(marker)
    assert index != -1, case
    updated = original[:index] + original[index + len(marker):]
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for rel in MISSING_FILE_CASES:
            (tmp_root / rel).unlink()
            expect_missing_file(f"missing_file::{rel}", tmp_root, rel)
            write_fixture_root(tmp_root)

        for rel, marker in MISSING_MARKER_CASES:
            mutate_file(tmp_root, rel, marker, f"missing_marker::{rel}")
            expect_missing_marker(f"missing_marker::{rel}", tmp_root, f"{rel}: {marker}")
            write_fixture_root(tmp_root)

    case_count = len(MISSING_FILE_CASES) + len(MISSING_MARKER_CASES)
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

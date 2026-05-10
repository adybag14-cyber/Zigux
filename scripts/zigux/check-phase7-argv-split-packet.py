#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "lib/argv_split.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "null-terminated pointer-vector access through `cArgv()`",
        "exported C-argv vector sizing to `argc + 1` so the trailing null sentinel stays aligned with `argvSplitWithArgc()` and `cArgv()`",
        "copied-buffer ownership so later source mutation does not affect split results",
        "copied whitespace separator runs are zeroed across the owned storage copy so each exported token stays in-place NUL-terminated",
        "helper-local owned-storage handoff reviewability through the internal `argvSplitOwnedStorage()` path, including blank owned-storage fallback to the canonical empty storage and exported argv sentinels",
        "caller-owned owned-storage reuse keeps token pointers inside the supplied storage copy, and blank owned-storage input falls back to the shared empty storage and exported argv sentinels without inventing extra allocator-backed state",
        "blank-input sentinel reuse and repeatable teardown through both `deinit()` and `argvFree()`",
        "tearing down one non-blank result does not disturb another caller's owned storage or exported C-argv view",
        "blank-input teardown on one caller keeps the shared empty storage and exported argv sentinels stable for another caller",
        "exported storage and argv views resetting back to the canonical empty sentinels after teardown",
        "allocator-failure cleanup when intermediate setup work is interrupted",
        "overflow rejection before sizing the exported null-terminated argv vector",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "PHASE7_LANE_KEY=P7-Y05",
        "`scripts/zigux/check-phase7-make-wrapper.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "`scripts/zigux/validate-phase7.py`",
        "`zigux/Makefile`",
        "`.github/workflows/zigux-bootstrap.yml`",
        "`make -C zigux phase7-validate` and `make -C zigux phase7` remain the Linux-style review routes for this shared control surface",
        "this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "lib/argv_split.zig",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/Makefile",
        "zigux/tests/phase7_build.zig",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under",
        "lib/argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_build.zig",
    ],
    "scripts/zigux/validate-phase7.py": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "samples/zigux/README.md",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "lib/argv_split.zig",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    ],
    "zigux/Makefile": [
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-argv-split-tests",
        "\"phase7_argv_split.zig\"",
        "phase7-argv-split-survey-tests",
        "\"phase7_argv_split_survey.zig\"",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
    ],
    "zigux/tests/phase7_argv_split.zig": [
        '@import("fixtures/phase7_argv_split_vectors.zig")',
        "split.cArgv()",
        "phase 7 argvSplit token buffer does not alias the source text",
        "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy",
        "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
        "phase 7 argvSplit keeps the exported C argv vector sized to argc plus one sentinel",
        "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned",
        "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        "phase 7 argvFree on one live split result does not disturb another caller",
        "phase 7 argvSplit deinit on one live split result does not disturb another caller",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "phase 7 blank argvSplit teardown on one caller keeps shared empty sentinels stable for another caller",
        "phase 7 blank argvSplit deinit on one caller keeps shared empty sentinels stable for another caller",
        "phase 7 argvSplit deinit clears exported storage and argv views",
        "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result",
        "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
        "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "zigux/tests/phase7_argv_split_manifest.json",
        "PHASE7_LANE_KEY=P7-Y07",
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        "\"id\": \"phase7-argv-split-packet-checker\"",
        "\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\"",
    ],
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": [
        "repeated whitespace collapses into separators",
        "blank input stays empty",
        "whitespace before first NUL stays blank",
        "leading NUL truncates to zero argv entries",
        "first NUL stops counting and splitting",
        "quote characters stay inside returned tokens",
    ],
    "lib/argv_split.zig": [
        "pub fn countArgc",
        "pub fn argvSplit",
        "pub fn argvSplitWithArgc",
        "pub fn argvFree",
        "pub fn cArgv",
        'test "argvSplitOwnedStorage reuses the caller-owned storage copy"',
        'test "argvSplitOwnedStorage frees blank caller-owned storage and reuses exported sentinels"',
        'test "argvSplit sizes argc and tokens from the owned copy prefix when copied storage contains an early NUL"',
        'test "argvSplit zeroes copied whitespace separators across the tokenized buffer"',
        'test "ArgvSplitResult deinit is idempotent after the exported views are cleared"',
        'test "argvSplit frees intermediate allocations when allocator failure interrupts setup"',
        'test "argvSplitOwnedStorage frees intermediate allocations when allocator failure interrupts setup"',
        'test "argvSplit reports overflow before sizing the null-terminated argv vector"',
    ],
}

EXACT_COUNT_MARKERS = {
    "zigux/tests/phase7_argv_split_manifest.json": [
        ('\"id\": \"phase7-argv-split-packet-checker\"', 1),
        ('\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\"', 1),
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    for rel, marker_counts in EXACT_COUNT_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker, expected_count in marker_counts:
            actual_count = text.count(marker)
            if actual_count != expected_count:
                missing.append(f"{rel}: {marker}:expected={expected_count}:actual={actual_count}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {
        "Documentation/zigux/phase7-argv-split-slice.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase7-argv-split-slice.md"]) + "\n",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": "\n".join(
            REQUIRED_MARKERS["Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"]
        )
        + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(
            REQUIRED_MARKERS["Documentation/zigux/review-checklist.md"]
        )
        + "\n",
        "samples/zigux/README.md": "\n".join(REQUIRED_MARKERS["samples/zigux/README.md"]) + "\n",
        "scripts/zigux/validate-phase7.py": "\n".join(REQUIRED_MARKERS["scripts/zigux/validate-phase7.py"]) + "\n",
        "scripts/zigux/check-phase7-argv-split-packet.py": "\n".join(REQUIRED_MARKERS["scripts/zigux/check-phase7-argv-split-packet.py"]) + "\n",
        "zigux/Makefile": "\n".join(REQUIRED_MARKERS["zigux/Makefile"]) + "\n",
        "zigux/tests/phase7_build.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_build.zig"]) + "\n",
        "zigux/tests/phase7_argv_split.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split.zig"]) + "\n",
        "zigux/tests/phase7_argv_split_survey.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"]) + "\n",
        "zigux/tests/phase7_argv_split_manifest.json": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split_manifest.json"]) + "\n",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/fixtures/phase7_argv_split_vectors.zig"]) + "\n",
        "lib/argv_split.zig": "\n".join(REQUIRED_MARKERS["lib/argv_split.zig"]) + "\n",
    }

    for rel, marker_counts in EXACT_COUNT_MARKERS.items():
        text = fixture_text.get(rel, "")
        for marker, _expected_count in marker_counts:
            if marker not in text:
                text += marker + "\n"
        fixture_text[rel] = text

    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert marker in missing_markers, case


def remove_first_marker(text: str, marker: str) -> str:
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if marker in line:
            updated = "".join(lines[:index] + lines[index + 1 :])
            assert updated != text
            return updated
    updated = text.replace(marker, "", 1)
    assert updated != text
    return updated


def duplicate_first_marker(text: str, marker: str) -> str:
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if marker in line:
            updated = "".join(lines[: index + 1] + [line] + lines[index + 1 :])
            assert updated != text
            return updated
    updated = text.replace(marker, f"{marker}\n{marker}", 1)
    assert updated != text
    return updated


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        checker_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
        checker_path.unlink()
        expect_missing_file(
            "missing_argv_split_packet_checker",
            tmp_root,
            "scripts/zigux/check-phase7-argv-split-packet.py",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        validator_path = tmp_root / "scripts" / "zigux" / "validate-phase7.py"
        validator_path.unlink()
        expect_missing_file(
            "missing_phase7_validator",
            tmp_root,
            "scripts/zigux/validate-phase7.py",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        survey_path.unlink()
        expect_missing_file(
            "missing_argv_split_survey",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        manifest_path.unlink()
        expect_missing_file(
            "missing_argv_split_manifest",
            tmp_root,
            "zigux/tests/phase7_argv_split_manifest.json",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        slice_note_path = tmp_root / "Documentation" / "zigux" / "phase7-make-wrapper-selftest-alignment.md"
        slice_note_path.unlink()
        expect_missing_file(
            "missing_phase7_make_wrapper_alignment_note",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        checklist_path = tmp_root / "Documentation" / "zigux" / "review-checklist.md"
        checklist_path.unlink()
        expect_missing_file(
            "missing_phase7_review_checklist_surface",
            tmp_root,
            "Documentation/zigux/review-checklist.md",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_path.unlink()
        expect_missing_file(
            "missing_argv_split_samples_boundary_note",
            tmp_root,
            "samples/zigux/README.md",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        fixture_path.unlink()
        expect_missing_file(
            "missing_argv_split_vectors_fixture",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        helper_path = tmp_root / "lib" / "argv_split.zig"
        helper_path.unlink()
        expect_missing_file(
            "missing_argv_split_helper_impl",
            tmp_root,
            "lib/argv_split.zig",
        )
        case_count += 1
        write_fixture_root(tmp_root)

        slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_shared_note_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace("copied-buffer ownership so later source mutation does not affect split results", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_source_copy_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: copied-buffer ownership so later source mutation does not affect split results",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "copied whitespace separator runs are zeroed across the owned storage copy so each exported token stays in-place NUL-terminated",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_zeroed_whitespace_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: copied whitespace separator runs are zeroed across the owned storage copy so each exported token stays in-place NUL-terminated",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "helper-local owned-storage handoff reviewability through the internal `argvSplitOwnedStorage()` path, including blank owned-storage fallback to the canonical empty storage and exported argv sentinels",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_owned_storage_surface_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: helper-local owned-storage handoff reviewability through the internal `argvSplitOwnedStorage()` path, including blank owned-storage fallback to the canonical empty storage and exported argv sentinels",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "caller-owned owned-storage reuse keeps token pointers inside the supplied storage copy, and blank owned-storage input falls back to the shared empty storage and exported argv sentinels without inventing extra allocator-backed state",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_owned_storage_tests_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: caller-owned owned-storage reuse keeps token pointers inside the supplied storage copy, and blank owned-storage input falls back to the shared empty storage and exported argv sentinels without inventing extra allocator-backed state",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "exported storage and argv views resetting back to the canonical empty sentinels after teardown",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_post_teardown_reset_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: exported storage and argv views resetting back to the canonical empty sentinels after teardown",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace("python3 scripts/zigux/check-phase7-argv-split-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_packet_checker_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        )
        case_count += 1
        slice_path.write_text(original_slice, encoding="utf-8")

        note_path = tmp_root / "Documentation" / "zigux" / "phase7-make-wrapper-selftest-alignment.md"
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace("PHASE7_LANE_KEY=P7-Y05", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_shared_note_lane_marker",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: PHASE7_LANE_KEY=P7-Y05",
        )
        case_count += 1
        note_path.write_text(original_note, encoding="utf-8")

        note_path.write_text(
            original_note.replace("`scripts/zigux/validate-phase7.py`", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_shared_note_validator_marker",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: `scripts/zigux/validate-phase7.py`",
        )
        case_count += 1
        note_path.write_text(original_note, encoding="utf-8")

        note_path.write_text(
            original_note.replace(
                "this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_shared_note_non_goal_marker",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: this note does not reopen `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, or `lib/rbtree.zig`",
        )
        case_count += 1
        note_path.write_text(original_note, encoding="utf-8")

        checklist_path = tmp_root / "Documentation" / "zigux" / "review-checklist.md"
        original_checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            original_checklist.replace("scripts/zigux/check-phase7-argv-split-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_review_checklist_checker_marker",
            tmp_root,
            "Documentation/zigux/review-checklist.md: scripts/zigux/check-phase7-argv-split-packet.py",
        )
        case_count += 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        checklist_path.write_text(
            original_checklist.replace("zigux/tests/phase7_argv_split_manifest.json", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_review_checklist_manifest_marker",
            tmp_root,
            "Documentation/zigux/review-checklist.md: zigux/tests/phase7_argv_split_manifest.json",
        )
        case_count += 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        validator_path = tmp_root / "scripts" / "zigux" / "validate-phase7.py"
        original_validator = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            original_validator.replace("samples/zigux/README.md", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_validator_samples_marker",
            tmp_root,
            "scripts/zigux/validate-phase7.py: samples/zigux/README.md",
        )
        case_count += 1
        validator_path.write_text(original_validator, encoding="utf-8")

        validator_path.write_text(
            original_validator.replace("zigux/tests/phase7_argv_split_manifest.json", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_validator_manifest_marker",
            tmp_root,
            "scripts/zigux/validate-phase7.py: zigux/tests/phase7_argv_split_manifest.json",
        )
        case_count += 1
        validator_path.write_text(original_validator, encoding="utf-8")

        samples_path = tmp_root / "samples" / "zigux" / "README.md"
        original_samples = samples_path.read_text(encoding="utf-8")
        samples_path.write_text(
            original_samples.replace(
                "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_samples_boundary_marker",
            tmp_root,
            "samples/zigux/README.md: current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample; keep `argv_split` reviewability under",
        )
        case_count += 1
        samples_path.write_text(original_samples, encoding="utf-8")

        samples_path.write_text(
            original_samples.replace("scripts/zigux/check-phase7-argv-split-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_samples_checker_marker",
            tmp_root,
            "samples/zigux/README.md: scripts/zigux/check-phase7-argv-split-packet.py",
        )
        case_count += 1
        samples_path.write_text(original_samples, encoding="utf-8")

        build_path = tmp_root / "zigux" / "tests" / "phase7_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase7-argv-split-survey-tests", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_build_survey_gate_marker",
            tmp_root,
            "zigux/tests/phase7_build.zig: phase7-argv-split-survey-tests",
        )
        case_count += 1
        build_path.write_text(original_build, encoding="utf-8")

        makefile_path = tmp_root / "zigux" / "Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase7-argv-split-packet.py --self-test", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_makefile_self_test_marker",
            tmp_root,
            "zigux/Makefile: scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        )
        case_count += 1
        makefile_path.write_text(original_makefile, encoding="utf-8")

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            remove_first_marker(original_survey, "zigux/tests/phase7_argv_split_manifest.json"),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_survey_manifest_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: zigux/tests/phase7_argv_split_manifest.json",
        )
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            remove_first_marker(original_survey, "PHASE7_LANE_KEY=P7-Y07"),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_survey_lane_key_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: PHASE7_LANE_KEY=P7-Y07",
        )
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        tests_path = tmp_root / "zigux" / "tests" / "phase7_argv_split.zig"
        original_tests = tests_path.read_text(encoding="utf-8")
        tests_path.write_text(original_tests.replace("split.cArgv()", "split.argv", 1), encoding="utf-8")
        expect_missing_marker(
            "argv_split_cargv_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: split.cArgv()",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvSplit keeps every shared token pointer inside the owned storage copy",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_storage_pointer_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit keeps every shared token pointer inside the owned storage copy",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_argc_out_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvSplit keeps the exported C argv vector sized to argc plus one sentinel",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_cargv_layout_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit keeps the exported C argv vector sized to argc plus one sentinel",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_terminator_alignment_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit keeps the final token C-string terminator and trailing argv sentinel aligned",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_distinct_owned_views_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvFree on one live split result does not disturb another caller",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_non_blank_teardown_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvFree on one live split result does not disturb another caller",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvSplit deinit on one live split result does not disturb another caller",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_non_blank_deinit_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit deinit on one live split result does not disturb another caller",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvSplit deinit clears exported storage and argv views",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_deinit_clears_views_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit deinit clears exported storage and argv views",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_allocation_failure_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 blank argvSplit teardown on one caller keeps shared empty sentinels stable for another caller",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_shared_blank_teardown_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 blank argvSplit teardown on one caller keeps shared empty sentinels stable for another caller",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        tests_path.write_text(
            original_tests.replace(
                "phase 7 blank argvSplit deinit on one caller keeps shared empty sentinels stable for another caller",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_shared_blank_deinit_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 blank argvSplit deinit on one caller keeps shared empty sentinels stable for another caller",
        )
        case_count += 1
        tests_path.write_text(original_tests, encoding="utf-8")

        fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        original_fixture = fixture_path.read_text(encoding="utf-8")
        fixture_path.write_text(
            original_fixture.replace("whitespace before first NUL stays blank", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_whitespace_before_nul_fixture_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: whitespace before first NUL stays blank",
        )
        case_count += 1
        fixture_path.write_text(original_fixture, encoding="utf-8")

        fixture_path.write_text(
            original_fixture.replace("leading NUL truncates to zero argv entries", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_leading_nul_fixture_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: leading NUL truncates to zero argv entries",
        )
        case_count += 1
        fixture_path.write_text(original_fixture, encoding="utf-8")

        fixture_path.write_text(
            original_fixture.replace("quote characters stay inside returned tokens", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_quote_fixture_marker",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig: quote characters stay inside returned tokens",
        )
        case_count += 1
        fixture_path.write_text(original_fixture, encoding="utf-8")

        helper_path = tmp_root / "lib" / "argv_split.zig"
        original_helper = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(
            original_helper.replace("pub fn argvSplitWithArgc", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_surface_marker",
            tmp_root,
            "lib/argv_split.zig: pub fn argvSplitWithArgc",
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "argvSplitOwnedStorage reuses the caller-owned storage copy"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_owned_storage_reuse_marker",
            tmp_root,
            'lib/argv_split.zig: test "argvSplitOwnedStorage reuses the caller-owned storage copy"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "argvSplitOwnedStorage frees blank caller-owned storage and reuses exported sentinels"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_owned_storage_blank_marker",
            tmp_root,
            'lib/argv_split.zig: test "argvSplitOwnedStorage frees blank caller-owned storage and reuses exported sentinels"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "argvSplit sizes argc and tokens from the owned copy prefix when copied storage contains an early NUL"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_early_nul_marker",
            tmp_root,
            'lib/argv_split.zig: test "argvSplit sizes argc and tokens from the owned copy prefix when copied storage contains an early NUL"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "argvSplit zeroes copied whitespace separators across the tokenized buffer"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_zeroed_whitespace_marker",
            tmp_root,
            'lib/argv_split.zig: test "argvSplit zeroes copied whitespace separators across the tokenized buffer"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "ArgvSplitResult deinit is idempotent after the exported views are cleared"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_deinit_idempotent_marker",
            tmp_root,
            'lib/argv_split.zig: test "ArgvSplitResult deinit is idempotent after the exported views are cleared"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "argvSplit frees intermediate allocations when allocator failure interrupts setup"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_allocation_failure_marker",
            tmp_root,
            'lib/argv_split.zig: test "argvSplit frees intermediate allocations when allocator failure interrupts setup"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "argvSplitOwnedStorage frees intermediate allocations when allocator failure interrupts setup"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_owned_storage_allocation_failure_marker",
            tmp_root,
            'lib/argv_split.zig: test "argvSplitOwnedStorage frees intermediate allocations when allocator failure interrupts setup"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        helper_path.write_text(
            original_helper.replace(
                'test "argvSplit reports overflow before sizing the null-terminated argv vector"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_helper_overflow_marker",
            tmp_root,
            'lib/argv_split.zig: test "argvSplit reports overflow before sizing the null-terminated argv vector"',
        )
        case_count += 1
        helper_path.write_text(original_helper, encoding="utf-8")

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace("\"id\": \"phase7-argv-split-packet-checker\"", "\"id\": \"phase7-argv-split-missing-checker\"", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_id_marker",
            tmp_root,
            'zigux/tests/phase7_argv_split_manifest.json: "id": "phase7-argv-split-packet-checker"',
        )
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            original_manifest.replace(
                "\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet.py\"",
                "\"zigux_destination\": \"scripts/zigux/check-phase7-argv-split-packet-drift.py\"",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_destination_marker",
            tmp_root,
            'zigux/tests/phase7_argv_split_manifest.json: "zigux_destination": "scripts/zigux/check-phase7-argv-split-packet.py"',
        )
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            duplicate_first_marker(original_manifest, '"id": "phase7-argv-split-packet-checker"'),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_id_duplicate_marker",
            tmp_root,
            'zigux/tests/phase7_argv_split_manifest.json: "id": "phase7-argv-split-packet-checker":expected=1:actual=2',
        )
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest_path.write_text(
            duplicate_first_marker(
                original_manifest,
                '"zigux_destination": "scripts/zigux/check-phase7-argv-split-packet.py"',
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_manifest_checker_destination_duplicate_marker",
            tmp_root,
            'zigux/tests/phase7_argv_split_manifest.json: "zigux_destination": "scripts/zigux/check-phase7-argv-split-packet.py":expected=1:actual=2',
        )
        case_count += 1

    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the dedicated Phase 7 argv_split packet surface.")
    parser.add_argument("--self-test", action="store_true", help="Run packet checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
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
    print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "lib/argv_split.zig",
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
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "lib/argv_split.zig",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_build.zig",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "lib/argv_split.zig",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "null-terminated pointer-vector access through `cArgv()`",
        "separate non-blank callers keep owned storage, argv slices, and exported C-argv views distinct across results",
        "zigux/tests/phase7_argv_split_manifest.json",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "lib/argv_split.zig",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_build.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "make -C zigux phase7-validate",
        "make -C zigux phase7",
    ],
    "scripts/zigux/validate-phase7.py": [
        "\"scripts/zigux/check-phase7-argv-split-packet.py\"",
        "\"zigux/tests/phase7_argv_split.zig\"",
        "\"zigux/tests/phase7_argv_split_survey.zig\"",
        "\"zigux/tests/phase7_argv_split_manifest.json\"",
        "\"zigux/tests/fixtures/phase7_argv_split_vectors.zig\"",
    ],
    "zigux/tests/README.md": [
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "make -C zigux phase7-validate",
        "make -C zigux phase7",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
        "phase7-test:",
        "phase7: phase7-validate phase7-test",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-argv-split-tests",
        "\"phase7_argv_split.zig\"",
        "phase7-argv-split-survey-tests",
        "\"phase7_argv_split_survey.zig\"",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
    ],
    "zigux/tests/phase7_argv_split.zig": [
        "phase 7 argvSplit matches focused parity fixtures",
        "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result",
        "phase 7 argvSplit deinit clears exported storage and argv views",
        "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
        "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split_manifest.json",
        "phase7-argv-split-packet-checker",
        "PHASE7_LANE_KEY=",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "phase 7 argvSplit deinit clears exported storage and argv views",
        "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
    ],
    "zigux/tests/phase7_argv_split_manifest.json": [
        "copied token-buffer ownership and later source-mutation isolation",
        "owned-storage reuse keeps token pointers inside caller-managed storage",
        "non-blank results keep storage, argv slices, and C-argv views distinct across callers",
        "argvFree on one live non-blank result does not disturb another caller-owned split result",
        "deinit on one live non-blank result does not disturb another caller-owned split result",
        "blank-input sentinel reuse stays stable across argvFree and deinit, including shared empty-sentinel teardown beside another blank caller",
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
    fixture_text.update(
        {
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "// fixture\n",
            "lib/argv_split.zig": "// fixture\n",
        }
    )
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "# fixture\n"), encoding="utf-8")


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
    missing_file_cases = [
        ("missing_review_checklist", "Documentation/zigux/review-checklist.md"),
        ("missing_alignment_note", "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"),
        ("missing_make_wrapper_checker", "scripts/zigux/check-phase7-make-wrapper.py"),
        ("missing_make_wrapper_alignment_checker", "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_tests_readme", "zigux/tests/README.md"),
        ("missing_manifest", "zigux/tests/phase7_argv_split_manifest.json"),
        ("missing_fixture_module", "zigux/tests/fixtures/phase7_argv_split_vectors.zig"),
    ]

    marker_cases = [
        (
            "docs_readme_alignment_note_marker",
            "Documentation/zigux/README.md",
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
            "",
            "Documentation/zigux/README.md: Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        ),
        (
            "review_checklist_slice_marker",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-argv-split-slice.md",
            "",
            "Documentation/zigux/review-checklist.md: Documentation/zigux/phase7-argv-split-slice.md",
        ),
        (
            "review_checklist_alignment_marker",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
            "",
            "Documentation/zigux/review-checklist.md: Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        ),
        (
            "review_checklist_build_wiring_marker",
            "Documentation/zigux/review-checklist.md",
            "scripts/zigux/check-phase7-build-wiring.py",
            "",
            "Documentation/zigux/review-checklist.md: scripts/zigux/check-phase7-build-wiring.py",
        ),
        (
            "slice_checker_marker",
            "Documentation/zigux/phase7-argv-split-slice.md",
            "python3 scripts/zigux/check-phase7-argv-split-packet.py",
            "",
            "Documentation/zigux/phase7-argv-split-slice.md: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        ),
        (
            "slice_distinct_views_marker",
            "Documentation/zigux/phase7-argv-split-slice.md",
            "separate non-blank callers keep owned storage, argv slices, and exported C-argv views distinct across results",
            "",
            "Documentation/zigux/phase7-argv-split-slice.md: separate non-blank callers keep owned storage, argv slices, and exported C-argv views distinct across results",
        ),
        (
            "samples_make_wrapper_alignment_marker",
            "samples/zigux/README.md",
            "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
            "",
            "samples/zigux/README.md: scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        ),
        (
            "scripts_readme_checker_marker",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase7-argv-split-packet.py",
            "",
            "scripts/zigux/README.md: scripts/zigux/check-phase7-argv-split-packet.py",
        ),
        (
            "scripts_readme_helper_marker",
            "scripts/zigux/README.md",
            "zigux/tests/phase7_argv_split.zig",
            "",
            "scripts/zigux/README.md: zigux/tests/phase7_argv_split.zig",
        ),
        (
            "makefile_checker_selftest_marker",
            "zigux/Makefile",
            "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
            "",
            "zigux/Makefile: scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        ),
        (
            "helper_distinct_callers_marker",
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
            "",
            "zigux/tests/phase7_argv_split.zig: phase 7 non-blank argvSplit calls keep owned storage and C-argv views distinct across callers",
        ),
        (
            "helper_blank_exported_view_marker",
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 blank argvSplit input reuses the empty exported argv view",
            "",
            "zigux/tests/phase7_argv_split.zig: phase 7 blank argvSplit input reuses the empty exported argv view",
        ),
        (
            "helper_blank_storage_sentinel_marker",
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
            "",
            "zigux/tests/phase7_argv_split.zig: phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        ),
        (
            "helper_blank_argvfree_marker",
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
            "",
            "zigux/tests/phase7_argv_split.zig: phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        ),
        (
            "helper_deinit_clears_marker",
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 argvSplit deinit clears exported storage and argv views",
            "",
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit deinit clears exported storage and argv views",
        ),
        (
            "helper_alloc_failure_marker",
            "zigux/tests/phase7_argv_split.zig",
            "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
            "",
            "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
        ),
        (
            "survey_checker_marker",
            "zigux/tests/phase7_argv_split_survey.zig",
            "scripts/zigux/check-phase7-argv-split-packet.py",
            "",
            "zigux/tests/phase7_argv_split_survey.zig: scripts/zigux/check-phase7-argv-split-packet.py",
        ),
        (
            "survey_blank_exported_view_marker",
            "zigux/tests/phase7_argv_split_survey.zig",
            "phase 7 blank argvSplit input reuses the empty exported argv view",
            "",
            "zigux/tests/phase7_argv_split_survey.zig: phase 7 blank argvSplit input reuses the empty exported argv view",
        ),
        (
            "survey_blank_storage_sentinel_marker",
            "zigux/tests/phase7_argv_split_survey.zig",
            "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
            "",
            "zigux/tests/phase7_argv_split_survey.zig: phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        ),
        (
            "survey_blank_argvfree_marker",
            "zigux/tests/phase7_argv_split_survey.zig",
            "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
            "",
            "zigux/tests/phase7_argv_split_survey.zig: phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        ),
        (
            "survey_deinit_clears_marker",
            "zigux/tests/phase7_argv_split_survey.zig",
            "phase 7 argvSplit deinit clears exported storage and argv views",
            "",
            "zigux/tests/phase7_argv_split_survey.zig: phase 7 argvSplit deinit clears exported storage and argv views",
        ),
        (
            "survey_alloc_failure_marker",
            "zigux/tests/phase7_argv_split_survey.zig",
            "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
            "",
            "zigux/tests/phase7_argv_split_survey.zig: phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
        ),
        (
            "manifest_copied_buffer_isolation_marker",
            "zigux/tests/phase7_argv_split_manifest.json",
            "copied token-buffer ownership and later source-mutation isolation",
            "",
            "zigux/tests/phase7_argv_split_manifest.json: copied token-buffer ownership and later source-mutation isolation",
        ),
        (
            "manifest_owned_storage_reuse_marker",
            "zigux/tests/phase7_argv_split_manifest.json",
            "owned-storage reuse keeps token pointers inside caller-managed storage",
            "",
            "zigux/tests/phase7_argv_split_manifest.json: owned-storage reuse keeps token pointers inside caller-managed storage",
        ),
        (
            "manifest_distinct_callers_marker",
            "zigux/tests/phase7_argv_split_manifest.json",
            "non-blank results keep storage, argv slices, and C-argv views distinct across callers",
            "",
            "zigux/tests/phase7_argv_split_manifest.json: non-blank results keep storage, argv slices, and C-argv views distinct across callers",
        ),
        (
            "manifest_argvfree_isolation_marker",
            "zigux/tests/phase7_argv_split_manifest.json",
            "argvFree on one live non-blank result does not disturb another caller-owned split result",
            "",
            "zigux/tests/phase7_argv_split_manifest.json: argvFree on one live non-blank result does not disturb another caller-owned split result",
        ),
        (
            "manifest_deinit_isolation_marker",
            "zigux/tests/phase7_argv_split_manifest.json",
            "deinit on one live non-blank result does not disturb another caller-owned split result",
            "",
            "zigux/tests/phase7_argv_split_manifest.json: deinit on one live non-blank result does not disturb another caller-owned split result",
        ),
        (
            "manifest_blank_sentinel_stability_marker",
            "zigux/tests/phase7_argv_split_manifest.json",
            "blank-input sentinel reuse stays stable across argvFree and deinit, including shared empty-sentinel teardown beside another blank caller",
            "",
            "zigux/tests/phase7_argv_split_manifest.json: blank-input sentinel reuse stays stable across argvFree and deinit, including shared empty-sentinel teardown beside another blank caller",
        ),
        (
            "build_survey_cwd_marker",
            "zigux/tests/phase7_build.zig",
            "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
            "run_argv_split_survey_tests.setCwd(b.path(\".\"));",
            "zigux/tests/phase7_build.zig: run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases)
    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 7 argv_split packet stays aligned.")
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
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
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_cmdline_manifest.json",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 7 runtime helper gates",
        "make -C zigux phase7-validate",
        "Run Phase 7 runtime helper tests",
        "make -C zigux phase7-test",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "Documentation/zigux/review-checklist.md",
        "samples/zigux/README.md",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_cmdline_manifest.json",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "zigux/Makefile",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared Phase 7 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`",
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "there is no standalone `samples/zigux/*string*` reference sample",
        "zigux/tests/phase7_cmdline_manifest.json",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_rbtree_manifest.json",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "without implying unshipped `check-phase7-build-inventory.py` or `phase7_build_inventory.json` surfaces?",
    ],
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "PHASE7_STATUS=parked",
        "current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`",
        "The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`",
        "The next honest reopen step is to restore `lib/string_helpers.zig` together with `zigux/tests/phase7_string_helpers.zig`",
        "Until those files are back on current `master`, keep this lane limited to same-packet truthfulness repairs",
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "exact bare-option matching for comma-delimited flags",
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "null-terminated pointer-vector access through `cArgv()`",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    ],
    "Documentation/zigux/phase7-rbtree-slice.md": [
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/phase7_build.zig",
        "this slice does not carry an open parity-fixture follow-up",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;",
        "treat any new `samples/zigux/*string*.zig` file as review-blocking",
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "lib/string_helpers.zig",
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "lib/cmdline.zig",
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "lib/argv_split.zig",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "lib/rbtree.zig",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_build.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/phase7_rbtree_manifest.json",
        "zigux/tests/fixtures/phase7_rbtree.json",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
        "make -C zigux phase7-validate",
        "there is no separate shared `check-phase7-build-inventory.py`",
    ],
    "scripts/zigux/check-phase7-make-wrapper.py": [
        "--self-test",
        "PHASE7_MAKE_WRAPPER_SELF_TEST=pass",
    ],
    "scripts/zigux/check-phase7-argv-split-packet.py": [
        "--self-test",
        "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
    ],
    "scripts/zigux/check-phase7-rbtree-parity.py": [
        "--self-test",
        "PHASE7_RBTREE_PARITY_SELF_TEST=pass",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase7_build.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        "\"missing_review_surfaces\": [",
        "\"lib/string_helpers.zig\"",
        "\"zigux/tests/phase7_string_helpers.zig\"",
        "\"current_master_truthfulness\":",
        "\"phase7-string-helpers-validator-truthfulness\"",
        "\"status\": \"shared_surface_drift\"",
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        "phase 7 string helpers survey keeps the current missing-helper packet truthful",
        "current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`",
        "The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`",
        "Until those files are back on current `master`, keep this lane limited to same-packet truthfulness repairs",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/validate-phase7.py --self-test",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
        "phase7-test:",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
        "phase7: phase7-validate phase7-test",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-string-helpers-tests",
        "phase7-string-helpers-sample-boundary-tests",
        "\"phase7_string_helpers_sample_boundary.zig\"",
        "run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));",
        "phase7-cmdline-tests",
        "phase7-cmdline-survey-tests",
        "\"phase7_cmdline_survey.zig\"",
        "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));",
        "phase7-argv-split-tests",
        "phase7-argv-split-survey-tests",
        "\"phase7_argv_split_survey.zig\"",
        "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));",
        "phase7-rbtree-tests",
        "phase7-rbtree-survey-tests",
        "run_rbtree_survey_tests.setCwd(b.path(\"../..\"));",
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");",
    ],
    "zigux/tests/phase7_argv_split.zig": [
        "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "Documentation/zigux/phase7-argv-split-slice.md",
        "phase 7 argvSplit matches focused parity fixtures",
        "phase 7 blank argvSplit input reuses the empty exported argv view",
        "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space",
        "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable",
        "zigux/tests/phase7_argv_split_manifest.json",
        "PHASE7_LANE_KEY=",
    ],
    "zigux/tests/phase7_rbtree_survey.zig": [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "zigux/tests/phase7_rbtree_manifest.json",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    ],
}

EXACT_COUNT_MARKERS = {
    "Documentation/zigux/review-checklist.md": [
        ("scripts/zigux/check-phase7-build-wiring.py", 5),
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        ("Documentation/zigux/review-checklist.md", 2),
        ("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", 2),
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        ("Documentation/zigux/review-checklist.md", 2),
        ("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", 2),
    ],
    "Documentation/zigux/phase7-rbtree-slice.md": [
        ("Documentation/zigux/review-checklist.md", 2),
        ("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", 2),
    ],
}

FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase7.py": "# fixture\n",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": "// fixture\n",
    "zigux/tests/phase7_cmdline.zig": "// fixture\n",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig": "// fixture\n",
    "zigux/tests/phase7_argv_split.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split.zig"]) + "\n",
    "zigux/tests/phase7_argv_split_survey.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"]) + "\n",
    "zigux/tests/phase7_argv_split_manifest.json": "{}\n",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "// fixture\n",
    "zigux/tests/phase7_rbtree.zig": "// fixture\n",
    "zigux/tests/phase7_rbtree_manifest.json": "{}\n",
    "zigux/tests/fixtures/phase7_rbtree.json": "{}\n",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c": "/* fixture */\n",
    "lib/cmdline.zig": "// fixture\n",
    "lib/argv_split.zig": "// fixture\n",
    "lib/rbtree.zig": "// fixture\n",
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


def collect_exact_count_markers(root: Path) -> list[str]:
    drift: list[str] = []
    for rel, exact_counts in EXACT_COUNT_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker, expected_count in exact_counts:
            actual_count = text.count(marker)
            if actual_count != expected_count:
                drift.append(f"{rel}: exact_count:{marker}:{actual_count}!={expected_count}")
    return drift


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root) + collect_exact_count_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {}
    for rel, markers in REQUIRED_MARKERS.items():
        lines = list(markers)
        for marker, expected_count in EXACT_COUNT_MARKERS.get(rel, []):
            extra_count = expected_count - lines.count(marker)
            if extra_count > 0:
                lines.extend([marker] * extra_count)
        fixture_text[rel] = "\n".join(lines) + "\n"
    fixture_text.update(FIXTURE_OVERRIDES)
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
    assert missing_markers == [marker], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_parity_checker", "scripts/zigux/check-phase7-rbtree-parity.py"),
        ("missing_make_wrapper_checker", "scripts/zigux/check-phase7-make-wrapper.py"),
        ("missing_argv_split_packet_checker", "scripts/zigux/check-phase7-argv-split-packet.py"),
        ("missing_samples_readme", "samples/zigux/README.md"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_phase7_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_review_checklist", "Documentation/zigux/review-checklist.md"),
        ("missing_make_wrapper_selftest_alignment_note", "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"),
        ("missing_make_wrapper_selftest_alignment_checker", "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"),
        ("missing_build_wiring_checker", "scripts/zigux/check-phase7-build-wiring.py"),
        ("missing_argv_split_vectors_fixture", "zigux/tests/fixtures/phase7_argv_split_vectors.zig"),
        ("missing_argv_split_survey", "zigux/tests/phase7_argv_split_survey.zig"),
        ("missing_argv_split_manifest", "zigux/tests/phase7_argv_split_manifest.json"),
        ("missing_cmdline_next_arg_vectors_fixture", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("missing_string_helpers_sample_boundary", "zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("missing_string_helpers_survey", "zigux/tests/phase7_string_helpers_survey.zig"),
        ("missing_string_helpers_manifest", "zigux/tests/phase7_string_helpers_manifest.json"),
        ("missing_cmdline_survey", "zigux/tests/phase7_cmdline_survey.zig"),
        ("missing_cmdline_manifest", "zigux/tests/phase7_cmdline_manifest.json"),
    ]

    marker_cases = [
        ("parity_checker_self_test_flag", "scripts/zigux/check-phase7-rbtree-parity.py", "--self-test", "", "scripts/zigux/check-phase7-rbtree-parity.py: --self-test"),
        ("make_wrapper_checker_self_test_flag", "scripts/zigux/check-phase7-make-wrapper.py", "--self-test", "", "scripts/zigux/check-phase7-make-wrapper.py: --self-test"),
        ("docs_readme_make_wrapper_selftest_alignment_marker", "Documentation/zigux/README.md", "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md", "", "Documentation/zigux/README.md: Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"),
        ("docs_readme_review_checklist_marker", "Documentation/zigux/README.md", "Documentation/zigux/review-checklist.md", "", "Documentation/zigux/README.md: Documentation/zigux/review-checklist.md"),
        ("docs_readme_validate_phase7_marker", "Documentation/zigux/README.md", "scripts/zigux/validate-phase7.py", "", "Documentation/zigux/README.md: scripts/zigux/validate-phase7.py"),
        ("docs_readme_make_wrapper_checker_marker", "Documentation/zigux/README.md", "scripts/zigux/check-phase7-make-wrapper.py", "", "Documentation/zigux/README.md: scripts/zigux/check-phase7-make-wrapper.py"),
        ("docs_readme_make_wrapper_selftest_alignment_checker_marker", "Documentation/zigux/README.md", "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py", "", "Documentation/zigux/README.md: scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"),
        ("docs_readme_samples_boundary_marker", "Documentation/zigux/README.md", "samples/zigux/README.md", "", "Documentation/zigux/README.md: samples/zigux/README.md"),
        ("docs_readme_string_helpers_test_marker", "Documentation/zigux/README.md", "zigux/tests/phase7_string_helpers.zig", "", "Documentation/zigux/README.md: zigux/tests/phase7_string_helpers.zig"),
        ("docs_readme_string_helpers_survey_marker", "Documentation/zigux/README.md", "zigux/tests/phase7_string_helpers_survey.zig", "", "Documentation/zigux/README.md: zigux/tests/phase7_string_helpers_survey.zig"),
        ("docs_readme_string_helpers_manifest_marker", "Documentation/zigux/README.md", "zigux/tests/phase7_string_helpers_manifest.json", "", "Documentation/zigux/README.md: zigux/tests/phase7_string_helpers_manifest.json"),
        ("docs_readme_string_helpers_sample_boundary_marker", "Documentation/zigux/README.md", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "", "Documentation/zigux/README.md: zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("docs_readme_cmdline_manifest_marker", "Documentation/zigux/README.md", "zigux/tests/phase7_cmdline_manifest.json", "", "Documentation/zigux/README.md: zigux/tests/phase7_cmdline_manifest.json"),
        ("docs_readme_cmdline_fixture_marker", "Documentation/zigux/README.md", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", "", "Documentation/zigux/README.md: zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("docs_readme_argv_split_manifest_marker", "Documentation/zigux/README.md", "zigux/tests/phase7_argv_split_manifest.json", "", "Documentation/zigux/README.md: zigux/tests/phase7_argv_split_manifest.json"),
        ("docs_readme_argv_split_fixture_marker", "Documentation/zigux/README.md", "zigux/tests/fixtures/phase7_argv_split_vectors.zig", "", "Documentation/zigux/README.md: zigux/tests/fixtures/phase7_argv_split_vectors.zig"),
        ("docs_readme_makefile_marker", "Documentation/zigux/README.md", "zigux/Makefile", "", "Documentation/zigux/README.md: zigux/Makefile"),
        ("docs_readme_workflow_marker", "Documentation/zigux/README.md", ".github/workflows/zigux-bootstrap.yml", "", "Documentation/zigux/README.md: .github/workflows/zigux-bootstrap.yml"),
        ("review_checklist_phase7_packet_marker", "Documentation/zigux/review-checklist.md", "if the change touches the shared Phase 7 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`", "", "Documentation/zigux/review-checklist.md: if the change touches the shared Phase 7 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`"),
        ("review_checklist_string_sample_boundary_marker", "Documentation/zigux/review-checklist.md", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "", "Documentation/zigux/review-checklist.md: zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("review_checklist_string_no_sample_phrase", "Documentation/zigux/review-checklist.md", "there is no standalone `samples/zigux/*string*` reference sample", "", "Documentation/zigux/review-checklist.md: there is no standalone `samples/zigux/*string*` reference sample"),
        ("review_checklist_cmdline_fixture_marker", "Documentation/zigux/review-checklist.md", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", "", "Documentation/zigux/review-checklist.md: zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("review_checklist_argv_fixture_marker", "Documentation/zigux/review-checklist.md", "zigux/tests/fixtures/phase7_argv_split_vectors.zig", "", "Documentation/zigux/review-checklist.md: zigux/tests/fixtures/phase7_argv_split_vectors.zig"),
        ("string_helpers_slice_parked_status", "Documentation/zigux/phase7-string-helpers-slice.md", "PHASE7_STATUS=parked", "PHASE7_STATUS=active", "Documentation/zigux/phase7-string-helpers-slice.md: PHASE7_STATUS=parked"),
        ("string_helpers_slice_missing_pair", "Documentation/zigux/phase7-string-helpers-slice.md", "current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`", "", "Documentation/zigux/phase7-string-helpers-slice.md: current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`"),
        ("string_helpers_slice_manifest_packet", "Documentation/zigux/phase7-string-helpers-slice.md", "The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`", "", "Documentation/zigux/phase7-string-helpers-slice.md: The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`"),
        ("string_helpers_slice_truthfulness_limit", "Documentation/zigux/phase7-string-helpers-slice.md", "Until those files are back on current `master`, keep this lane limited to same-packet truthfulness repairs", "", "Documentation/zigux/phase7-string-helpers-slice.md: Until those files are back on current `master`, keep this lane limited to same-packet truthfulness repairs"),
        ("samples_readme_boundary_marker", "samples/zigux/README.md", "treat any new `samples/zigux/*string*.zig` file as review-blocking", "", "samples/zigux/README.md: treat any new `samples/zigux/*string*.zig` file as review-blocking"),
        ("samples_readme_cmdline_boundary_marker", "samples/zigux/README.md", "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;", "", "samples/zigux/README.md: current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;"),
        ("samples_readme_cmdline_slice_marker", "samples/zigux/README.md", "Documentation/zigux/phase7-cmdline-slice.md", "", "samples/zigux/README.md: Documentation/zigux/phase7-cmdline-slice.md"),
        ("samples_readme_argv_boundary_marker", "samples/zigux/README.md", "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;", "", "samples/zigux/README.md: current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;"),
        ("samples_readme_argv_checker_marker", "samples/zigux/README.md", "scripts/zigux/check-phase7-argv-split-packet.py", "", "samples/zigux/README.md: scripts/zigux/check-phase7-argv-split-packet.py"),
        ("samples_readme_rbtree_boundary_marker", "samples/zigux/README.md", "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;", "", "samples/zigux/README.md: current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;"),
        ("samples_readme_rbtree_checker_marker", "samples/zigux/README.md", "scripts/zigux/check-phase7-rbtree-parity.py", "", "samples/zigux/README.md: scripts/zigux/check-phase7-rbtree-parity.py"),
        ("scripts_readme_make_wrapper_marker", "scripts/zigux/README.md", "scripts/zigux/check-phase7-make-wrapper.py", "", "scripts/zigux/README.md: scripts/zigux/check-phase7-make-wrapper.py"),
        ("scripts_readme_argv_split_packet_marker", "scripts/zigux/README.md", "scripts/zigux/check-phase7-argv-split-packet.py", "", "scripts/zigux/README.md: scripts/zigux/check-phase7-argv-split-packet.py"),
        ("scripts_readme_cmdline_survey_marker", "scripts/zigux/README.md", "zigux/tests/phase7_cmdline_survey.zig", "", "scripts/zigux/README.md: zigux/tests/phase7_cmdline_survey.zig"),
        ("scripts_readme_cmdline_fixture_marker", "scripts/zigux/README.md", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", "", "scripts/zigux/README.md: zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("scripts_readme_argv_split_survey_marker", "scripts/zigux/README.md", "zigux/tests/phase7_argv_split_survey.zig", "", "scripts/zigux/README.md: zigux/tests/phase7_argv_split_survey.zig"),
        ("scripts_readme_argv_split_manifest_marker", "scripts/zigux/README.md", "zigux/tests/phase7_argv_split_manifest.json", "", "scripts/zigux/README.md: zigux/tests/phase7_argv_split_manifest.json"),
        ("scripts_readme_rbtree_manifest_marker", "scripts/zigux/README.md", "zigux/tests/phase7_rbtree_manifest.json", "", "scripts/zigux/README.md: zigux/tests/phase7_rbtree_manifest.json"),
        ("scripts_readme_rbtree_fixture_json_marker", "scripts/zigux/README.md", "zigux/tests/fixtures/phase7_rbtree.json", "", "scripts/zigux/README.md: zigux/tests/fixtures/phase7_rbtree.json"),
        ("scripts_readme_rbtree_fixture_harness_marker", "scripts/zigux/README.md", "zigux/tests/fixtures/phase7_rbtree_c_harness.c", "", "scripts/zigux/README.md: zigux/tests/fixtures/phase7_rbtree_c_harness.c"),
        ("workflow_phase7_validate_step", ".github/workflows/zigux-bootstrap.yml", "Validate Phase 7 runtime helper gates", "", ".github/workflows/zigux-bootstrap.yml: Validate Phase 7 runtime helper gates"),
        ("workflow_phase7_test_route", ".github/workflows/zigux-bootstrap.yml", "make -C zigux phase7-test", "", ".github/workflows/zigux-bootstrap.yml: make -C zigux phase7-test"),
        ("makefile_validator_self_test_hook", "zigux/Makefile", "scripts/zigux/validate-phase7.py --self-test", "", "zigux/Makefile: scripts/zigux/validate-phase7.py --self-test"),
        ("makefile_make_wrapper_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-make-wrapper.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-make-wrapper.py --self-test"),
        ("makefile_make_wrapper_hook", "zigux/Makefile", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py", "", "zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py"),
        ("makefile_make_wrapper_selftest_alignment_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test"),
        ("makefile_make_wrapper_selftest_alignment_hook", "zigux/Makefile", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py", "", "zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"),
        ("makefile_build_wiring_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-build-wiring.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-build-wiring.py --self-test"),
        ("makefile_build_wiring_hook", "zigux/Makefile", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py", "", "zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py"),
        ("makefile_argv_split_packet_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-argv-split-packet.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-argv-split-packet.py --self-test"),
        ("makefile_parity_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-rbtree-parity.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-rbtree-parity.py --self-test"),
        ("makefile_phase7_test_summary_marker", "zigux/Makefile", "zig build test --build-file zigux/tests/phase7_build.zig --summary all", "zig build test --build-file zigux/tests/phase7_build.zig", "zigux/Makefile: zig build test --build-file zigux/tests/phase7_build.zig --summary all"),
        ("argv_split_slice_checker_gate", "Documentation/zigux/phase7-argv-split-slice.md", "python3 scripts/zigux/check-phase7-argv-split-packet.py", "", "Documentation/zigux/phase7-argv-split-slice.md: python3 scripts/zigux/check-phase7-argv-split-packet.py"),
        ("cmdline_survey_fixture_path", "zigux/tests/phase7_cmdline_survey.zig", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", "", "zigux/tests/phase7_cmdline_survey.zig: zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("cmdline_survey_fixture_import", "zigux/tests/phase7_cmdline_survey.zig", "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");", "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_vectors_drift.zig\");", "zigux/tests/phase7_cmdline_survey.zig: const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");"),
        ("argv_split_helper_double_teardown_marker", "zigux/tests/phase7_argv_split.zig", "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result", "", "zigux/tests/phase7_argv_split.zig: phase 7 argvSplit deinit stays safe when called after teardown already cleared the result"),
        ("argv_split_survey_vector_sizing_marker", "zigux/tests/phase7_argv_split_survey.zig", "phase 7 argvSplit matches focused parity fixtures", "", "zigux/tests/phase7_argv_split_survey.zig: phase 7 argvSplit matches focused parity fixtures"),
        ("argv_split_survey_final_token_marker", "zigux/tests/phase7_argv_split_survey.zig", "phase 7 blank argvSplit input reuses the empty exported argv view", "", "zigux/tests/phase7_argv_split_survey.zig: phase 7 blank argvSplit input reuses the empty exported argv view"),
        ("argv_split_survey_distinct_callers_marker", "zigux/tests/phase7_argv_split_survey.zig", "phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space", "", "zigux/tests/phase7_argv_split_survey.zig: phase 7 blank argvSplit input reuses the empty storage sentinel without allocator space"),
        ("argv_split_survey_cross_caller_teardown_marker", "zigux/tests/phase7_argv_split_survey.zig", "phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable", "", "zigux/tests/phase7_argv_split_survey.zig: phase 7 argvFree keeps the blank-input sentinel teardown safe and repeatable"),
        ("argv_split_survey_manifest_marker", "zigux/tests/phase7_argv_split_survey.zig", "zigux/tests/phase7_argv_split_manifest.json", "", "zigux/tests/phase7_argv_split_survey.zig: zigux/tests/phase7_argv_split_manifest.json"),
        ("string_helpers_manifest_missing_review_surfaces", "zigux/tests/phase7_string_helpers_manifest.json", "\"missing_review_surfaces\": [", "\"missing_review_surfaces\": null", "zigux/tests/phase7_string_helpers_manifest.json: \"missing_review_surfaces\": ["),
        ("string_helpers_manifest_missing_helper_path", "zigux/tests/phase7_string_helpers_manifest.json", "\"lib/string_helpers.zig\"", "", "zigux/tests/phase7_string_helpers_manifest.json: \"lib/string_helpers.zig\""),
        ("string_helpers_manifest_missing_test_path", "zigux/tests/phase7_string_helpers_manifest.json", "\"zigux/tests/phase7_string_helpers.zig\"", "", "zigux/tests/phase7_string_helpers_manifest.json: \"zigux/tests/phase7_string_helpers.zig\""),
        ("string_helpers_manifest_truthfulness_gap", "zigux/tests/phase7_string_helpers_manifest.json", "\"phase7-string-helpers-validator-truthfulness\"", "", "zigux/tests/phase7_string_helpers_manifest.json: \"phase7-string-helpers-validator-truthfulness\""),
        ("string_helpers_manifest_shared_surface_drift", "zigux/tests/phase7_string_helpers_manifest.json", "\"status\": \"shared_surface_drift\"", "\"status\": \"starter_landed\"", "zigux/tests/phase7_string_helpers_manifest.json: \"status\": \"shared_surface_drift\""),
        ("string_helpers_survey_truthful_packet", "zigux/tests/phase7_string_helpers_survey.zig", "phase 7 string helpers survey keeps the current missing-helper packet truthful", "", "zigux/tests/phase7_string_helpers_survey.zig: phase 7 string helpers survey keeps the current missing-helper packet truthful"),
        ("string_helpers_survey_missing_pair", "zigux/tests/phase7_string_helpers_survey.zig", "current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`", "", "zigux/tests/phase7_string_helpers_survey.zig: current `master` is missing both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`"),
        ("string_helpers_survey_manifest_record", "zigux/tests/phase7_string_helpers_survey.zig", "The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`", "", "zigux/tests/phase7_string_helpers_survey.zig: The parked string-helper packet remains recorded in `zigux/tests/phase7_string_helpers_manifest.json`"),
        ("rbtree_survey_validator_reference", "zigux/tests/phase7_rbtree_survey.zig", "scripts/zigux/validate-phase7.py", "", "zigux/tests/phase7_rbtree_survey.zig: scripts/zigux/validate-phase7.py"),
        ("cmdline_review_surface", "Documentation/zigux/phase7-cmdline-slice.md", "exact bare-option matching for comma-delimited flags", "", "Documentation/zigux/phase7-cmdline-slice.md: exact bare-option matching for comma-delimited flags"),
        ("tests_readme_phase7_rbtree_survey_marker", "zigux/tests/README.md", "zigux/tests/phase7_rbtree_survey.zig", "", "zigux/tests/README.md: zigux/tests/phase7_rbtree_survey.zig"),
        ("tests_readme_phase7_argv_split_survey_marker", "zigux/tests/README.md", "zigux/tests/phase7_argv_split_survey.zig", "", "zigux/tests/README.md: zigux/tests/phase7_argv_split_survey.zig"),
        ("tests_readme_phase7_string_helpers_sample_boundary_marker", "zigux/tests/README.md", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "", "zigux/tests/README.md: zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("tests_readme_phase7_cmdline_survey_marker", "zigux/tests/README.md", "zigux/tests/phase7_cmdline_survey.zig", "", "zigux/tests/README.md: zigux/tests/phase7_cmdline_survey.zig"),
        ("build_argv_split_survey_gate", "zigux/tests/phase7_build.zig", "phase7-argv-split-survey-tests", "", "zigux/tests/phase7_build.zig: phase7-argv-split-survey-tests"),
        ("build_argv_split_survey_source", "zigux/tests/phase7_build.zig", "\"phase7_argv_split_survey.zig\"", "\"phase7_argv_split_survey_drift.zig\"", "zigux/tests/phase7_build.zig: \"phase7_argv_split_survey.zig\""),
        ("build_argv_split_survey_cwd", "zigux/tests/phase7_build.zig", "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));", "run_argv_split_survey_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_argv_split_survey_tests.setCwd(b.path(\"../..\"));"),
        ("build_rbtree_survey_gate", "zigux/tests/phase7_build.zig", "phase7-rbtree-survey-tests", "", "zigux/tests/phase7_build.zig: phase7-rbtree-survey-tests"),
        ("build_string_helpers_sample_boundary_gate", "zigux/tests/phase7_build.zig", "phase7-string-helpers-sample-boundary-tests", "", "zigux/tests/phase7_build.zig: phase7-string-helpers-sample-boundary-tests"),
        ("build_string_helpers_sample_boundary_source", "zigux/tests/phase7_build.zig", "\"phase7_string_helpers_sample_boundary.zig\"", "\"phase7_string_helpers_sample_boundary_drift.zig\"", "zigux/tests/phase7_build.zig: \"phase7_string_helpers_sample_boundary.zig\""),
        ("build_string_helpers_sample_boundary_cwd", "zigux/tests/phase7_build.zig", "run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));", "run_string_helpers_sample_boundary_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));"),
        ("build_cmdline_survey_gate", "zigux/tests/phase7_build.zig", "phase7-cmdline-survey-tests", "", "zigux/tests/phase7_build.zig: phase7-cmdline-survey-tests"),
        ("build_cmdline_survey_source", "zigux/tests/phase7_build.zig", "\"phase7_cmdline_survey.zig\"", "\"phase7_cmdline_survey_drift.zig\"", "zigux/tests/phase7_build.zig: \"phase7_cmdline_survey.zig\""),
        ("build_cmdline_survey_cwd", "zigux/tests/phase7_build.zig", "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));", "run_cmdline_survey_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_cmdline_survey_tests.setCwd(b.path(\"../..\"));"),
        ("build_rbtree_survey_cwd", "zigux/tests/phase7_build.zig", "run_rbtree_survey_tests.setCwd(b.path(\"../..\"));", "run_rbtree_survey_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_rbtree_survey_tests.setCwd(b.path(\"../..\"));"),
    ]

    exact_count_cases = [
        (
            "review_checklist_duplicate_build_wiring_marker",
            "Documentation/zigux/review-checklist.md",
            "scripts/zigux/check-phase7-build-wiring.py",
            "Documentation/zigux/review-checklist.md: exact_count:scripts/zigux/check-phase7-build-wiring.py:6!=5",
        ),
        (
            "cmdline_slice_duplicate_review_checklist_marker",
            "Documentation/zigux/phase7-cmdline-slice.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-cmdline-slice.md: exact_count:Documentation/zigux/review-checklist.md:3!=2",
        ),
        (
            "argv_split_slice_duplicate_review_checklist_marker",
            "Documentation/zigux/phase7-argv-split-slice.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-argv-split-slice.md: exact_count:Documentation/zigux/review-checklist.md:3!=2",
        ),
        (
            "rbtree_slice_duplicate_review_checklist_marker",
            "Documentation/zigux/phase7-rbtree-slice.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-rbtree-slice.md: exact_count:Documentation/zigux/review-checklist.md:3!=2",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validator_") as tmp_dir_str:
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

        for case, rel, marker, expected in exact_count_cases:
            mutate_file(tmp_root, rel, marker, marker + "\n" + marker, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases) + len(exact_count_cases)
    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shared Phase 7 helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_VALIDATION=fail")
        print("MISSING_PHASE7_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_VALIDATION=fail")
        print("MISSING_PHASE7_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_MARKERS_END")
        return 1

    print("PHASE7_VALIDATION=pass")
    print(f"PHASE7_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values()) + sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

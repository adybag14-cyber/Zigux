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
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
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
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
]

REQUIRED_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 7 runtime helper gates",
        "make -C zigux phase7-validate",
        "Run Phase 7 runtime helper tests",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "Documentation/zigux/README.md": [
        "Phase 7 notes -",
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7",
    ],
    "Documentation/zigux/review-checklist.md": [
        "shared Phase 7 leaf-helper packet",
        "zigux/tests/phase7_rbtree_manifest.json",
        "make -C zigux phase7",
        "without implying unshipped `check-phase7-build-inventory.py` or `phase7_build_inventory.json` surfaces?",
    ],
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "string_escape_mem()",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.",
        "no `samples/zigux/*string*` Phase 5 reference sample is expected here;",
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
        "zigux/tests/phase7_build.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
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
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/validate-phase7.py --self-test",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
        "phase7-test:",
        "zig build test --build-file zigux/tests/phase7_build.zig",
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
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        "samples/zigux/string_helpers_sample.zig",
        "std.mem.indexOf(u8, entry.name, \"string\") != null",
        "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.",
        "no `samples/zigux/*string*` Phase 5 reference sample is expected here;",
    ],
    "zigux/tests/phase7_cmdline_survey.zig": [
        "Documentation/zigux/phase7-cmdline-slice.md",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_build.zig",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");",
        "phase 7 getOption and getOptions preserve Linux-style range parsing",
        "phase 7 parseOptionStr matches only exact bare options",
        "phase 7 nextArg matches serialized edge fixtures",
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        "Documentation/zigux/phase7-argv-split-slice.md",
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
    "Documentation/zigux/README.md": [
        ("Phase 7 notes -", 1),
        ("Documentation/zigux/phase7-argv-split-slice.md", 1),
        ("make -C zigux phase7", 1),
    ],
    "scripts/zigux/README.md": [
        ("scripts/zigux/check-phase7-make-wrapper.py", 1),
        ("scripts/zigux/check-phase7-argv-split-packet.py", 1),
        ("scripts/zigux/check-phase7-rbtree-parity.py", 1),
        ("zigux/tests/phase7_cmdline_survey.zig", 1),
        ("make -C zigux phase7-validate", 1),
    ],
}

FIXTURE_OVERRIDES = {
    "scripts/zigux/validate-phase7.py": "# fixture\n",
    "zigux/tests/phase7_string_helpers.zig": "// fixture\n",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": "\n".join(
        REQUIRED_MARKERS["zigux/tests/phase7_string_helpers_sample_boundary.zig"]
    )
    + "\n",
    "zigux/tests/phase7_cmdline.zig": "// fixture\n",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig": "// fixture\n",
    "zigux/tests/phase7_argv_split.zig": "// fixture\n",
    "zigux/tests/phase7_argv_split_survey.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_argv_split_survey.zig"]) + "\n",
    "zigux/tests/phase7_argv_split_manifest.json": "{}\n",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "// fixture\n",
    "zigux/tests/phase7_rbtree.zig": "// fixture\n",
    "zigux/tests/phase7_rbtree_manifest.json": "{}\n",
    "zigux/tests/fixtures/phase7_rbtree.json": "{}\n",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c": "/* fixture */\n",
    "lib/string_helpers.zig": "// fixture\n",
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
    for rel, marker_counts in EXACT_COUNT_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker, expected_count in marker_counts:
            actual_count = text.count(marker)
            if actual_count != expected_count:
                missing.append(
                    f"{rel}: {marker}:expected={expected_count}:actual={actual_count}"
                )
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
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
    assert marker in missing_markers, case


def duplicate_first_marker(text: str, marker: str) -> str:
    return text.replace(marker, f"{marker}\n{marker}", 1)


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
        ("missing_argv_split_vectors_fixture", "zigux/tests/fixtures/phase7_argv_split_vectors.zig"),
        ("missing_argv_split_survey", "zigux/tests/phase7_argv_split_survey.zig"),
        ("missing_argv_split_manifest", "zigux/tests/phase7_argv_split_manifest.json"),
        ("missing_cmdline_next_arg_vectors_fixture", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("missing_string_helpers_sample_boundary", "zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("missing_cmdline_survey", "zigux/tests/phase7_cmdline_survey.zig"),
    ]

    marker_cases = [
        ("parity_checker_self_test_flag", "scripts/zigux/check-phase7-rbtree-parity.py", "--self-test", "", "scripts/zigux/check-phase7-rbtree-parity.py: --self-test"),
        ("make_wrapper_checker_self_test_flag", "scripts/zigux/check-phase7-make-wrapper.py", "--self-test", "", "scripts/zigux/check-phase7-make-wrapper.py: --self-test"),
        ("samples_readme_boundary_marker", "samples/zigux/README.md", "treat any new `samples/zigux/*string*.zig` file as review-blocking", "", "samples/zigux/README.md: treat any new `samples/zigux/*string*.zig` file as review-blocking"),
        ("scripts_readme_make_wrapper_marker", "scripts/zigux/README.md", "scripts/zigux/check-phase7-make-wrapper.py", "", "scripts/zigux/README.md: scripts/zigux/check-phase7-make-wrapper.py"),
        ("scripts_readme_argv_split_packet_marker", "scripts/zigux/README.md", "scripts/zigux/check-phase7-argv-split-packet.py", "", "scripts/zigux/README.md: scripts/zigux/check-phase7-argv-split-packet.py"),
        ("scripts_readme_cmdline_survey_marker", "scripts/zigux/README.md", "zigux/tests/phase7_cmdline_survey.zig", "", "scripts/zigux/README.md: zigux/tests/phase7_cmdline_survey.zig"),
        ("scripts_readme_string_helpers_sample_boundary_marker", "scripts/zigux/README.md", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "", "scripts/zigux/README.md: zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("scripts_readme_cmdline_fixture_marker", "scripts/zigux/README.md", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", "", "scripts/zigux/README.md: zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("scripts_readme_argv_split_survey_marker", "scripts/zigux/README.md", "zigux/tests/phase7_argv_split_survey.zig", "", "scripts/zigux/README.md: zigux/tests/phase7_argv_split_survey.zig"),
        ("scripts_readme_argv_split_manifest_marker", "scripts/zigux/README.md", "zigux/tests/phase7_argv_split_manifest.json", "", "scripts/zigux/README.md: zigux/tests/phase7_argv_split_manifest.json"),
        ("scripts_readme_rbtree_helper_marker", "scripts/zigux/README.md", "zigux/tests/phase7_rbtree.zig", "", "scripts/zigux/README.md: zigux/tests/phase7_rbtree.zig"),
        ("scripts_readme_rbtree_survey_marker", "scripts/zigux/README.md", "zigux/tests/phase7_rbtree_survey.zig", "", "scripts/zigux/README.md: zigux/tests/phase7_rbtree_survey.zig"),
        ("scripts_readme_rbtree_manifest_marker", "scripts/zigux/README.md", "zigux/tests/phase7_rbtree_manifest.json", "", "scripts/zigux/README.md: zigux/tests/phase7_rbtree_manifest.json"),
        ("scripts_readme_rbtree_fixture_marker", "scripts/zigux/README.md", "zigux/tests/fixtures/phase7_rbtree.json", "", "scripts/zigux/README.md: zigux/tests/fixtures/phase7_rbtree.json"),
        ("scripts_readme_rbtree_c_harness_marker", "scripts/zigux/README.md", "zigux/tests/fixtures/phase7_rbtree_c_harness.c", "", "scripts/zigux/README.md: zigux/tests/fixtures/phase7_rbtree_c_harness.c"),
        ("workflow_phase7_validate_step", ".github/workflows/zigux-bootstrap.yml", "Validate Phase 7 runtime helper gates", "", ".github/workflows/zigux-bootstrap.yml: Validate Phase 7 runtime helper gates"),
        ("review_checklist_phase7_packet_marker", "Documentation/zigux/review-checklist.md", "shared Phase 7 leaf-helper packet", "", "Documentation/zigux/review-checklist.md: shared Phase 7 leaf-helper packet"),
        ("review_checklist_phase7_manifest_marker", "Documentation/zigux/review-checklist.md", "zigux/tests/phase7_rbtree_manifest.json", "", "Documentation/zigux/review-checklist.md: zigux/tests/phase7_rbtree_manifest.json"),
        ("review_checklist_phase7_make_marker", "Documentation/zigux/review-checklist.md", "make -C zigux phase7", "", "Documentation/zigux/review-checklist.md: make -C zigux phase7"),
        ("review_checklist_phase7_no_inventory_marker", "Documentation/zigux/review-checklist.md", "without implying unshipped `check-phase7-build-inventory.py` or `phase7_build_inventory.json` surfaces?", "", "Documentation/zigux/review-checklist.md: without implying unshipped `check-phase7-build-inventory.py` or `phase7_build_inventory.json` surfaces?"),
        ("makefile_validator_self_test_hook", "zigux/Makefile", "scripts/zigux/validate-phase7.py --self-test", "", "zigux/Makefile: scripts/zigux/validate-phase7.py --self-test"),
        ("makefile_make_wrapper_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-make-wrapper.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-make-wrapper.py --self-test"),
        ("makefile_make_wrapper_hook", "zigux/Makefile", "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py", "", "zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py"),
        ("makefile_argv_split_packet_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-argv-split-packet.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-argv-split-packet.py --self-test"),
        ("makefile_parity_self_test_hook", "zigux/Makefile", "scripts/zigux/check-phase7-rbtree-parity.py --self-test", "", "zigux/Makefile: scripts/zigux/check-phase7-rbtree-parity.py --self-test"),
        ("string_helpers_slice_boundary_guard_marker", "Documentation/zigux/phase7-string-helpers-slice.md", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "", "Documentation/zigux/phase7-string-helpers-slice.md: zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("string_helpers_slice_phase5_boundary_marker", "Documentation/zigux/phase7-string-helpers-slice.md", "This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.", "", "Documentation/zigux/phase7-string-helpers-slice.md: This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane."),
        ("argv_split_slice_checker_gate", "Documentation/zigux/phase7-argv-split-slice.md", "python3 scripts/zigux/check-phase7-argv-split-packet.py", "", "Documentation/zigux/phase7-argv-split-slice.md: python3 scripts/zigux/check-phase7-argv-split-packet.py"),
        ("string_helpers_boundary_missing_sample_path", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "samples/zigux/string_helpers_sample.zig", "", "zigux/tests/phase7_string_helpers_sample_boundary.zig: samples/zigux/string_helpers_sample.zig"),
        ("string_helpers_boundary_string_scan_marker", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "std.mem.indexOf(u8, entry.name, \"string\") != null", "std.mem.indexOf(u8, entry.name, \"str\") != null", "zigux/tests/phase7_string_helpers_sample_boundary.zig: std.mem.indexOf(u8, entry.name, \"string\") != null"),
        ("cmdline_survey_slice_note_path", "zigux/tests/phase7_cmdline_survey.zig", "Documentation/zigux/phase7-cmdline-slice.md", "", "zigux/tests/phase7_cmdline_survey.zig: Documentation/zigux/phase7-cmdline-slice.md"),
        ("cmdline_survey_helper_test_path", "zigux/tests/phase7_cmdline_survey.zig", "zigux/tests/phase7_cmdline.zig", "", "zigux/tests/phase7_cmdline_survey.zig: zigux/tests/phase7_cmdline.zig"),
        ("cmdline_survey_build_path", "zigux/tests/phase7_cmdline_survey.zig", "zigux/tests/phase7_build.zig", "", "zigux/tests/phase7_cmdline_survey.zig: zigux/tests/phase7_build.zig"),
        ("cmdline_survey_range_test_anchor", "zigux/tests/phase7_cmdline_survey.zig", "phase 7 getOption and getOptions preserve Linux-style range parsing", "phase 7 getOption and getOptions drift", "zigux/tests/phase7_cmdline_survey.zig: phase 7 getOption and getOptions preserve Linux-style range parsing"),
        ("cmdline_survey_fixture_path", "zigux/tests/phase7_cmdline_survey.zig", "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig", "", "zigux/tests/phase7_cmdline_survey.zig: zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig"),
        ("cmdline_survey_fixture_import", "zigux/tests/phase7_cmdline_survey.zig", "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");", "const next_arg_vectors = @import(\"fixtures/phase7_cmdline_vectors_drift.zig\");", "zigux/tests/phase7_cmdline_survey.zig: const next_arg_vectors = @import(\"fixtures/phase7_cmdline_next_arg_vectors.zig\");"),
        ("argv_split_survey_manifest_marker", "zigux/tests/phase7_argv_split_survey.zig", "zigux/tests/phase7_argv_split_manifest.json", "", "zigux/tests/phase7_argv_split_survey.zig: zigux/tests/phase7_argv_split_manifest.json"),
        ("rbtree_survey_validator_reference", "zigux/tests/phase7_rbtree_survey.zig", "scripts/zigux/validate-phase7.py", "", "zigux/tests/phase7_rbtree_survey.zig: scripts/zigux/validate-phase7.py"),
        ("cmdline_review_surface", "Documentation/zigux/phase7-cmdline-slice.md", "exact bare-option matching for comma-delimited flags", "", "Documentation/zigux/phase7-cmdline-slice.md: exact bare-option matching for comma-delimited flags"),
        ("tests_readme_phase7_rbtree_survey_marker", "zigux/tests/README.md", "zigux/tests/phase7_rbtree_survey.zig", "", "zigux/tests/README.md: zigux/tests/phase7_rbtree_survey.zig"),
        ("tests_readme_phase7_argv_split_survey_marker", "zigux/tests/README.md", "zigux/tests/phase7_argv_split_survey.zig", "", "zigux/tests/README.md: zigux/tests/phase7_argv_split_survey.zig"),
        ("tests_readme_phase7_string_helpers_sample_boundary_marker", "zigux/tests/README.md", "zigux/tests/phase7_string_helpers_sample_boundary.zig", "", "zigux/tests/README.md: zigux/tests/phase7_string_helpers_sample_boundary.zig"),
        ("tests_readme_phase7_cmdline_survey_marker", "zigux/tests/README.md", "zigux/tests/phase7_cmdline_survey.zig", "", "zigux/tests/README.md: zigux/tests/phase7_cmdline_survey.zig"),
        ("build_argv_split_survey_gate", "zigux/tests/phase7_build.zig", "phase7-argv-split-survey-tests", "", "zigux/tests/phase7_build.zig: phase7-argv-split-survey-tests"),
        ("build_argv_split_survey_source", "zigux/tests/phase7_build.zig", "\"phase7_argv_split_survey.zig\"", "\"phase7_argv_split_survey_drift.zig\"", "zigux/tests/phase7_build.zig: \"phase7_argv_split_survey.zig\"") ,
        ("build_argv_split_survey_cwd", "zigux/tests/phase7_build.zig", "run_argv_split_survey_tests.setCwd(b.path(\"../..\"));", "run_argv_split_survey_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_argv_split_survey_tests.setCwd(b.path(\"../..\"));"),
        ("build_rbtree_survey_gate", "zigux/tests/phase7_build.zig", "phase7-rbtree-survey-tests", "", "zigux/tests/phase7_build.zig: phase7-rbtree-survey-tests"),
        ("build_string_helpers_sample_boundary_gate", "zigux/tests/phase7_build.zig", "phase7-string-helpers-sample-boundary-tests", "", "zigux/tests/phase7_build.zig: phase7-string-helpers-sample-boundary-tests"),
        ("build_string_helpers_sample_boundary_source", "zigux/tests/phase7_build.zig", "\"phase7_string_helpers_sample_boundary.zig\"", "\"phase7_string_helpers_sample_boundary_drift.zig\"", "zigux/tests/phase7_build.zig: \"phase7_string_helpers_sample_boundary.zig\"") ,
        ("build_string_helpers_sample_boundary_cwd", "zigux/tests/phase7_build.zig", "run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));", "run_string_helpers_sample_boundary_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_string_helpers_sample_boundary_tests.setCwd(b.path(\"../..\"));"),
        ("build_cmdline_survey_gate", "zigux/tests/phase7_build.zig", "phase7-cmdline-survey-tests", "", "zigux/tests/phase7_build.zig: phase7-cmdline-survey-tests"),
        ("build_cmdline_survey_source", "zigux/tests/phase7_build.zig", "\"phase7_cmdline_survey.zig\"", "\"phase7_cmdline_survey_drift.zig\"", "zigux/tests/phase7_build.zig: \"phase7_cmdline_survey.zig\"") ,
        ("build_cmdline_survey_cwd", "zigux/tests/phase7_build.zig", "run_cmdline_survey_tests.setCwd(b.path(\"../..\"));", "run_cmdline_survey_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_cmdline_survey_tests.setCwd(b.path(\"../..\"));"),
        ("build_rbtree_survey_cwd", "zigux/tests/phase7_build.zig", "run_rbtree_survey_tests.setCwd(b.path(\"../..\"));", "run_rbtree_survey_tests.setCwd(b.path(\".\"));", "zigux/tests/phase7_build.zig: run_rbtree_survey_tests.setCwd(b.path(\"../..\"));"),
    ]

    exact_count_cases = [
        ("docs_readme_phase7_notes_exact_count", "Documentation/zigux/README.md", "Phase 7 notes -", "Documentation/zigux/README.md: Phase 7 notes -:expected=1:actual=2"),
        ("docs_readme_phase7_make_exact_count", "Documentation/zigux/README.md", "make -C zigux phase7", "Documentation/zigux/README.md: make -C zigux phase7:expected=1:actual=2"),
        ("scripts_readme_make_wrapper_exact_count", "scripts/zigux/README.md", "scripts/zigux/check-phase7-make-wrapper.py", "scripts/zigux/README.md: scripts/zigux/check-phase7-make-wrapper.py:expected=1:actual=2"),
        ("scripts_readme_argv_split_packet_exact_count", "scripts/zigux/README.md", "scripts/zigux/check-phase7-argv-split-packet.py", "scripts/zigux/README.md: scripts/zigux/check-phase7-argv-split-packet.py:expected=1:actual=2"),
        ("scripts_readme_phase7_validate_exact_count", "scripts/zigux/README.md", "make -C zigux phase7-validate", "scripts/zigux/README.md: make -C zigux phase7-validate:expected=1:actual=2"),
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
            path = tmp_root / rel
            original = path.read_text(encoding="utf-8")
            updated = duplicate_first_marker(original, marker)
            assert updated != original, case
            path.write_text(updated, encoding="utf-8")
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases) + len(exact_count_cases)
    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print("PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT=%d" % case_count)


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
    print(f"PHASE7_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

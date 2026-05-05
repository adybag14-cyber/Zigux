#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_argv_split.zig",
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
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "zigux/tests/phase7_build.zig",
        "make -C zigux phase7",
    ],
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "string_escape_mem()",
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
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;",
        "treat any new `samples/zigux/*string*.zig` file as review-blocking",
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_build.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "make -C zigux phase7-validate",
        "there is no separate shared `check-phase7-build-inventory.py`",
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
        "zigux/tests/phase7_argv_split.zig",
        "zigux/tests/phase7_rbtree.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/validate-phase7.py --self-test",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "phase7-test:",
        "zig build test --build-file zigux/tests/phase7_build.zig",
        "phase7: phase7-validate phase7-test",
    ],
    "zigux/tests/phase7_build.zig": [
        "phase7-string-helpers-tests",
        "phase7-string-helpers-sample-boundary-tests",
        "\"phase7_string_helpers_sample_boundary.zig\"",
        "setCwd(b.path(\"../..\"))",
        "phase7-cmdline-tests",
        "phase7-argv-split-tests",
        "phase7-rbtree-tests",
        "phase7-rbtree-survey-tests",
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
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return missing_files, collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {
        ".github/workflows/zigux-bootstrap.yml": "\n".join(REQUIRED_MARKERS[".github/workflows/zigux-bootstrap.yml"]) + "\n",
        "Documentation/zigux/README.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/README.md"]) + "\n",
        "Documentation/zigux/phase7-string-helpers-slice.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase7-string-helpers-slice.md"]) + "\n",
        "Documentation/zigux/phase7-cmdline-slice.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase7-cmdline-slice.md"]) + "\n",
        "Documentation/zigux/phase7-argv-split-slice.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase7-argv-split-slice.md"]) + "\n",
        "Documentation/zigux/phase7-rbtree-slice.md": "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase7-rbtree-slice.md"]) + "\n",
        "samples/zigux/README.md": "\n".join(REQUIRED_MARKERS["samples/zigux/README.md"]) + "\n",
        "scripts/zigux/README.md": "\n".join(REQUIRED_MARKERS["scripts/zigux/README.md"]) + "\n",
        "scripts/zigux/validate-phase7.py": "# fixture\n",
        "scripts/zigux/check-phase7-argv-split-packet.py": "\n".join(REQUIRED_MARKERS["scripts/zigux/check-phase7-argv-split-packet.py"]) + "\n",
        "scripts/zigux/check-phase7-rbtree-parity.py": "\n".join(REQUIRED_MARKERS["scripts/zigux/check-phase7-rbtree-parity.py"]) + "\n",
        "zigux/Makefile": "\n".join(REQUIRED_MARKERS["zigux/Makefile"]) + "\n",
        "zigux/tests/README.md": "\n".join(REQUIRED_MARKERS["zigux/tests/README.md"]) + "\n",
        "zigux/tests/phase7_build.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_build.zig"]) + "\n",
        "zigux/tests/phase7_string_helpers.zig": "// fixture\n",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig": "// fixture\n",
        "zigux/tests/phase7_cmdline.zig": "// fixture\n",
        "zigux/tests/phase7_argv_split.zig": "// fixture\n",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "// fixture\n",
        "zigux/tests/phase7_rbtree.zig": "// fixture\n",
        "zigux/tests/phase7_rbtree_survey.zig": "\n".join(REQUIRED_MARKERS["zigux/tests/phase7_rbtree_survey.zig"]) + "\n",
        "zigux/tests/phase7_rbtree_manifest.json": "{}\n",
        "zigux/tests/fixtures/phase7_rbtree.json": "{}\n",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c": "/* fixture */\n",
        "lib/string_helpers.zig": "// fixture\n",
        "lib/cmdline.zig": "// fixture\n",
        "lib/argv_split.zig": "// fixture\n",
        "lib/rbtree.zig": "// fixture\n",
    }

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


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        parity_path = tmp_root / "scripts" / "zigux" / "check-phase7-rbtree-parity.py"
        parity_path.unlink()
        expect_missing_file("missing_parity_checker", tmp_root, "scripts/zigux/check-phase7-rbtree-parity.py")
        write_fixture_root(tmp_root)

        argv_split_packet_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
        argv_split_packet_path.unlink()
        expect_missing_file(
            "missing_argv_split_packet_checker",
            tmp_root,
            "scripts/zigux/check-phase7-argv-split-packet.py",
        )
        write_fixture_root(tmp_root)

        samples_readme_path = tmp_root / "samples" / "zigux" / "README.md"
        samples_readme_path.unlink()
        expect_missing_file("missing_samples_readme", tmp_root, "samples/zigux/README.md")
        write_fixture_root(tmp_root)

        scripts_readme_path = tmp_root / "scripts" / "zigux" / "README.md"
        scripts_readme_path.unlink()
        expect_missing_file("missing_scripts_readme", tmp_root, "scripts/zigux/README.md")
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_path.unlink()
        expect_missing_file("missing_phase7_workflow", tmp_root, ".github/workflows/zigux-bootstrap.yml")
        write_fixture_root(tmp_root)

        argv_split_vectors_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig"
        argv_split_vectors_path.unlink()
        expect_missing_file(
            "missing_argv_split_vectors_fixture",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        )
        write_fixture_root(tmp_root)

        parity_path = tmp_root / "scripts" / "zigux" / "check-phase7-rbtree-parity.py"
        original_parity_text = parity_path.read_text(encoding="utf-8")
        parity_path.write_text(original_parity_text.replace("--self-test", "", 1), encoding="utf-8")
        expect_missing_marker(
            "parity_checker_self_test_flag",
            tmp_root,
            "scripts/zigux/check-phase7-rbtree-parity.py: --self-test",
        )
        parity_path.write_text(original_parity_text, encoding="utf-8")

        boundary_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_sample_boundary.zig"
        boundary_path.unlink()
        expect_missing_file(
            "missing_string_helpers_sample_boundary",
            tmp_root,
            "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        )
        write_fixture_root(tmp_root)

        samples_readme_path = tmp_root / "samples" / "zigux" / "README.md"
        original_samples_readme = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            original_samples_readme.replace(
                "treat any new `samples/zigux/*string*.zig` file as review-blocking",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "samples_readme_boundary_marker",
            tmp_root,
            "samples/zigux/README.md: treat any new `samples/zigux/*string*.zig` file as review-blocking",
        )
        samples_readme_path.write_text(original_samples_readme, encoding="utf-8")

        scripts_readme_path = tmp_root / "scripts" / "zigux" / "README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace("scripts/zigux/check-phase7-argv-split-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_argv_split_packet_marker",
            tmp_root,
            "scripts/zigux/README.md: scripts/zigux/check-phase7-argv-split-packet.py",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace("Validate Phase 7 runtime helper gates", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_phase7_validate_step",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: Validate Phase 7 runtime helper gates",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        makefile_path = tmp_root / "zigux" / "Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/validate-phase7.py --self-test", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_validator_self_test_hook",
            tmp_root,
            "zigux/Makefile: scripts/zigux/validate-phase7.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase7-argv-split-packet.py --self-test", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_argv_split_packet_self_test_hook",
            tmp_root,
            "zigux/Makefile: scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace("scripts/zigux/check-phase7-rbtree-parity.py --self-test", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_parity_self_test_hook",
            tmp_root,
            "zigux/Makefile: scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        argv_split_slice_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        original_argv_split_slice = argv_split_slice_path.read_text(encoding="utf-8")
        argv_split_slice_path.write_text(
            original_argv_split_slice.replace("python3 scripts/zigux/check-phase7-argv-split-packet.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_slice_checker_gate",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: python3 scripts/zigux/check-phase7-argv-split-packet.py",
        )
        argv_split_slice_path.write_text(original_argv_split_slice, encoding="utf-8")

        rbtree_survey_path = tmp_root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        original_rbtree_survey = rbtree_survey_path.read_text(encoding="utf-8")
        rbtree_survey_path.write_text(
            original_rbtree_survey.replace("scripts/zigux/validate-phase7.py", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "rbtree_survey_validator_reference",
            tmp_root,
            "zigux/tests/phase7_rbtree_survey.zig: scripts/zigux/validate-phase7.py",
        )
        rbtree_survey_path.write_text(original_rbtree_survey, encoding="utf-8")

        cmdline_doc_path = tmp_root / "Documentation" / "zigux" / "phase7-cmdline-slice.md"
        original_cmdline_doc = cmdline_doc_path.read_text(encoding="utf-8")
        cmdline_doc_path.write_text(
            original_cmdline_doc.replace("exact bare-option matching for comma-delimited flags", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "cmdline_review_surface",
            tmp_root,
            "Documentation/zigux/phase7-cmdline-slice.md: exact bare-option matching for comma-delimited flags",
        )
        cmdline_doc_path.write_text(original_cmdline_doc, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux" / "tests" / "README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace("zigux/tests/phase7_rbtree_survey.zig", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_phase7_rbtree_survey_marker",
            tmp_root,
            "zigux/tests/README.md: zigux/tests/phase7_rbtree_survey.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace("zigux/tests/phase7_string_helpers_sample_boundary.zig", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_phase7_string_helpers_sample_boundary_marker",
            tmp_root,
            "zigux/tests/README.md: zigux/tests/phase7_string_helpers_sample_boundary.zig",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        build_path = tmp_root / "zigux" / "tests" / "phase7_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase7-rbtree-survey-tests", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_rbtree_survey_gate",
            tmp_root,
            "zigux/tests/phase7_build.zig: phase7-rbtree-survey-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace("phase7-string-helpers-sample-boundary-tests", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_string_helpers_sample_boundary_gate",
            tmp_root,
            "zigux/tests/phase7_build.zig: phase7-string-helpers-sample-boundary-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace("\"phase7_string_helpers_sample_boundary.zig\"", "\"phase7_string_helpers_sample_boundary_drift.zig\"", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_string_helpers_sample_boundary_source",
            tmp_root,
            "zigux/tests/phase7_build.zig: \"phase7_string_helpers_sample_boundary.zig\"",
        )
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace("setCwd(b.path(\"../..\"))", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_string_helpers_sample_boundary_cwd",
            tmp_root,
            "zigux/tests/phase7_build.zig: setCwd(b.path(\"../..\"))",
        )

    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print("PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT=23")


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

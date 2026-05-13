#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
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
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "PHASE7_STATUS=starter_landed",
        "restored starter packet",
        "current `master` now carries both `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`",
        "The next bounded follow-through should stay inside the restored starter packet",
    ],
    "Documentation/zigux/phase7-cmdline-slice.md": [
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_cmdline_manifest.json",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "make -C zigux phase7-validate",
    ],
    "Documentation/zigux/phase7-argv-split-slice.md": [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "zigux/tests/phase7_argv_split_manifest.json",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        "make -C zigux phase7-validate",
    ],
    "Documentation/zigux/phase7-rbtree-slice.md": [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_rbtree_manifest.json",
        "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
        "make -C zigux phase7-validate",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "make -C zigux phase7-cmdline-survey",
        "make -C zigux phase7-argv-split-survey",
        "make -C zigux phase7-rbtree-survey",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_argv_split_manifest.json",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample;",
        "current `master` still ships no `samples/zigux/*argv*` Phase 5 reference sample;",
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "make -C zigux phase7-validate",
    ],
    "zigux/tests/README.md": [
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
    ],
    "zigux/tests/phase7_build.zig": [
        '"phase7_cmdline.zig"',
        '"phase7-cmdline-survey-tests"',
        '"phase7_argv_split.zig"',
        '"phase7-argv-split-survey-tests"',
        '"phase7_rbtree.zig"',
        '"phase7-rbtree-survey-tests"',
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py',
        "phase7-cmdline-survey:",
        "phase7-argv-split-survey:",
        "phase7-rbtree-survey:",
        "phase7-test:",
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        '"current_master_state": "restored_starter_packet"',
        '"lib/string_helpers.zig"',
        '"zigux/tests/phase7_string_helpers.zig"',
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        "restored starter packet",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        "restored starter packet",
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
    ],
    "lib/string_helpers.zig": [
        "pub fn skipSpaces",
        "pub fn trimSpaces",
        "pub fn sysfsStreq",
        "pub fn matchString",
        "pub fn strreplace",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        "phase 7 string helpers starter covers whitespace trimming and prefix skipping",
        "phase 7 string helpers starter keeps sysfs matching newline aware",
        "phase 7 string helpers starter matches tables through the first null entry",
        "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix",
    ],
}


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel}: {marker}")
    return [], missing_markers


def write_fixture_tree(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = REQUIRED_MARKERS.get(rel, ["fixture"])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def expect_missing_file(tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == []
    assert missing_files == [rel]


def expect_missing_marker(tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == []
    assert missing_markers == [marker]


def remove_once(tmp_root: Path, rel: str, old: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, "", 1)
    assert updated != original
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_tree(tmp_root)
        assert validate(tmp_root) == ([], [])

        (tmp_root / "zigux/tests/phase7_argv_split_manifest.json").unlink()
        expect_missing_file(tmp_root, "zigux/tests/phase7_argv_split_manifest.json")
        write_fixture_tree(tmp_root)

        remove_once(
            tmp_root,
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase7-argv-split-slice.md",
        )
        expect_missing_marker(
            tmp_root,
            "Documentation/zigux/review-checklist.md: Documentation/zigux/phase7-argv-split-slice.md",
        )
        write_fixture_tree(tmp_root)

        remove_once(
            tmp_root,
            "scripts/zigux/README.md",
            "zigux/tests/phase7_rbtree_survey.zig",
        )
        expect_missing_marker(
            tmp_root,
            "scripts/zigux/README.md: zigux/tests/phase7_rbtree_survey.zig",
        )
        write_fixture_tree(tmp_root)

        remove_once(
            tmp_root,
            "zigux/tests/phase7_string_helpers_sample_boundary.zig",
            "scripts/zigux/check-phase7-build-wiring.py",
        )
        expect_missing_marker(
            tmp_root,
            "zigux/tests/phase7_string_helpers_sample_boundary.zig: scripts/zigux/check-phase7-build-wiring.py",
        )
        write_fixture_tree(tmp_root)

        remove_once(
            tmp_root,
            "zigux/tests/phase7_build.zig",
            '"phase7-argv-split-survey-tests"',
        )
        expect_missing_marker(
            tmp_root,
            'zigux/tests/phase7_build.zig: "phase7-argv-split-survey-tests"',
        )
        write_fixture_tree(tmp_root)

        remove_once(
            tmp_root,
            "zigux/Makefile",
            "phase7-cmdline-survey:",
        )
        expect_missing_marker(
            tmp_root,
            "zigux/Makefile: phase7-cmdline-survey:",
        )
        write_fixture_tree(tmp_root)

        remove_once(
            tmp_root,
            "Documentation/zigux/phase7-rbtree-slice.md",
            "scripts/zigux/check-phase7-rbtree-parity.py",
        )
        expect_missing_marker(
            tmp_root,
            "Documentation/zigux/phase7-rbtree-slice.md: scripts/zigux/check-phase7-rbtree-parity.py",
        )

    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print("PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT=7")


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

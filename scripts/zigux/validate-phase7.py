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
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 7 runtime helper gates",
        "make -C zigux phase7-validate",
        "Run Phase 7 runtime helper tests",
        "make -C zigux phase7-test",
    ],
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "PHASE7_STATUS=starter_landed",
        "expanded starter packet",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "The next bounded follow-through should keep the expanded starter packet truthful",
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
        "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        "make -C zigux phase7-string-helpers-survey",
        "make -C zigux phase7-string-helpers-sample-boundary",
        "make -C zigux phase7-cmdline-survey",
        "make -C zigux phase7-argv-split-survey",
        "make -C zigux phase7-rbtree-survey",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "scripts/zigux/check-phase7-rbtree-parity.py",
        "zigux/tests/phase7_argv_split_manifest.json",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "Documentation/zigux/phase7-cmdline-slice.md",
        "Documentation/zigux/phase7-argv-split-slice.md",
        "Documentation/zigux/phase7-rbtree-slice.md",
    ],
    "Documentation/zigux/phase7-helper-lane-sequencing.md": [
        "PHASE7_SHARED_CONTROL_LANE=P7-Y05",
        "PHASE7_HELPER_SEQUENCING_LANE=P7-Y06",
        "PHASE7_SHARED_DOCS_ROOT_LANE=P7-Y08",
        "PHASE7_STRING_HELPERS_LANE=P7-L04",
        "PHASE7_CMDLINE_LANE=P7-L05",
        "PHASE7_ARGV_SPLIT_LANE=P7-L09",
        "PHASE7_ARGV_SPLIT_SCHEDULE_ALIAS=P7-Y07 -> P7-L09",
        "PHASE7_RBTREE_LANE=P7-L13",
        "`P7-L04` owns only string-helpers helper-local parity, survey, sample-boundary, manifest, or same-slice reminder drift;",
        "`P7-L05` owns only cmdline helper-local parity, survey, manifest, fixture, or same-slice reminder drift;",
        "`P7-L09` owns only argv-split helper-local parity, fixture, survey, manifest, or reminder drift.",
        "`P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift;",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;",
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
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_cmdline_survey.zig",
        "zigux/tests/phase7_argv_split_survey.zig",
        "zigux/tests/phase7_rbtree_survey.zig",
        "make -C zigux phase7-validate",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
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
        "\"phase7_string_helpers.zig\"",
        "\"phase7-string-helpers-tests\"",
        "\"phase7_string_helpers_survey.zig\"",
        "\"phase7-string-helpers-survey-tests\"",
        "\"phase7_string_helpers_sample_boundary.zig\"",
        "\"phase7-string-helpers-sample-boundary-tests\"",
        "\"phase7_cmdline.zig\"",
        "\"phase7-cmdline-survey-tests\"",
        "\"phase7_argv_split.zig\"",
        "\"phase7-argv-split-survey-tests\"",
        "\"phase7_rbtree.zig\"",
        "\"phase7-rbtree-survey-tests\"",
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py",
        "phase7-string-helpers-survey:",
        "phase7-string-helpers-sample-boundary:",
        "phase7-cmdline-survey:",
        "phase7-argv-split-survey:",
        "phase7-rbtree-survey:",
        "phase7-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all",
        "phase7: phase7-validate phase7-test",
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        "\"current_master_state\": \"expanded_starter_packet\"",
        "\"stringEscapeMem\"",
        "\"string_escape_str_any_np\"",
        "\"memcpyAndPad\"",
        "\"strreplace\"",
        "\"shared no-sample boundary and validator-backed reviewability\"",
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        "expanded starter packet",
        "stringEscapeMem()",
        "string_escape_str_any_np()",
        "memcpyAndPad()",
        "strreplace()",
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        "expanded helper packet",
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_string_helpers_survey.zig",
        "zigux/tests/phase7_string_helpers_manifest.json",
    ],
    "lib/string_helpers.zig": [
        "pub fn skipSpaces",
        "pub fn trimSpaces",
        "pub fn sysfsStreq",
        "pub fn matchString",
        "pub fn sysfsMatchString",
        "pub fn stringGetSize",
        "pub fn stringUnescapeAny",
        "pub fn stringEscapeMem",
        "pub fn stringEscapeStrAnyNp",
        "pub fn memcpyAndPad",
        "pub fn strreplace",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        "phase 7 string helpers starter covers whitespace trimming and prefix skipping",
        "phase 7 string helpers starter formats bounded sizes with three significant figures",
        "phase 7 string helpers starter unescapes supported escape families and preserves unsupported escapes",
        "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes",
        "phase 7 string helpers starter pads bounded copies without reading past the provided source slice",
        "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix",
    ],
}

REQUIRED_EXACT_LINES = {
    "zigux/Makefile": [
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
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
    for rel, lines in REQUIRED_EXACT_LINES.items():
        text_lines = (root / rel).read_text(encoding="utf-8").splitlines()
        for line in lines:
            if line not in text_lines:
                missing_markers.append(f"{rel}: {line}")
    return [], missing_markers


def write_fixture_tree(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = list(REQUIRED_MARKERS.get(rel, ["fixture"]))
        lines.extend(REQUIRED_EXACT_LINES.get(rel, []))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def expect_missing_file(tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == []
    assert missing_files == [rel]


def expect_missing_marker(tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == []
    assert missing_markers == [expected]


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

        (tmp_root / "zigux/tests/phase7_string_helpers_manifest.json").unlink()
        expect_missing_file(tmp_root, "zigux/tests/phase7_string_helpers_manifest.json")
        write_fixture_tree(tmp_root)

        cases = [
            (
                "phase7-string-helpers-slice next-step marker",
                "Documentation/zigux/phase7-string-helpers-slice.md",
                "The next bounded follow-through should keep the expanded starter packet truthful",
                "Documentation/zigux/phase7-string-helpers-slice.md: The next bounded follow-through should keep the expanded starter packet truthful",
            ),
            (
                "helper-lane sequencing argv lane marker",
                "Documentation/zigux/phase7-helper-lane-sequencing.md",
                "PHASE7_ARGV_SPLIT_LANE=P7-L09",
                "Documentation/zigux/phase7-helper-lane-sequencing.md: PHASE7_ARGV_SPLIT_LANE=P7-L09",
            ),
            (
                "workflow phase7 validate route",
                ".github/workflows/zigux-bootstrap.yml",
                "make -C zigux phase7-validate",
                ".github/workflows/zigux-bootstrap.yml: make -C zigux phase7-validate",
            ),
            (
                "build string helpers direct test entry",
                "zigux/tests/phase7_build.zig",
                "\"phase7-string-helpers-tests\"",
                "zigux/tests/phase7_build.zig: \"phase7-string-helpers-tests\"",
            ),
            (
                "makefile phase7 test route",
                "zigux/Makefile",
                "phase7-test:",
                "zigux/Makefile: phase7-test:",
            ),
            (
                "makefile build-wiring direct route",
                "zigux/Makefile",
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py\n",
                "zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
            ),
            (
                "string helper sample boundary expanded packet marker",
                "zigux/tests/phase7_string_helpers_sample_boundary.zig",
                "expanded helper packet",
                "zigux/tests/phase7_string_helpers_sample_boundary.zig: expanded helper packet",
            ),
            (
                "string helper survey escape marker",
                "zigux/tests/phase7_string_helpers_survey.zig",
                "stringEscapeMem()",
                "zigux/tests/phase7_string_helpers_survey.zig: stringEscapeMem()",
            ),
            (
                "string helper manifest expanded state marker",
                "zigux/tests/phase7_string_helpers_manifest.json",
                "\"current_master_state\": \"expanded_starter_packet\"",
                "zigux/tests/phase7_string_helpers_manifest.json: \"current_master_state\": \"expanded_starter_packet\"",
            ),
            (
                "lib string helpers escape function",
                "lib/string_helpers.zig",
                "pub fn stringEscapeMem",
                "lib/string_helpers.zig: pub fn stringEscapeMem",
            ),
            (
                "string helper test escape coverage",
                "zigux/tests/phase7_string_helpers.zig",
                "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes",
                "zigux/tests/phase7_string_helpers.zig: phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes",
            ),
        ]

        for _, rel, marker, expected in cases:
            remove_once(tmp_root, rel, marker)
            expect_missing_marker(tmp_root, expected)
            write_fixture_tree(tmp_root)

    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT={1 + len(cases)}")


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
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values()) + sum(len(lines) for lines in REQUIRED_EXACT_LINES.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

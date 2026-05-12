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
]

REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
        "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        "python3 scripts/zigux/check-phase7-build-wiring.py",
        "zigux/tests/phase7_build.zig",
    ],
    "samples/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py",
        "make -C zigux phase7-validate",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase7_build.zig",
        "scripts/zigux/check-phase7-build-wiring.py",
    ],
    "zigux/Makefile": [
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "scripts/zigux/check-phase7-build-wiring.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-wiring.py",
    ],
}

EXACT_COUNT_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": {
        "make -C zigux phase7-validate": 1,
        "python3 scripts/zigux/check-phase7-make-wrapper.py": 0,
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py": 0,
    },
    "zigux/Makefile": {
        "scripts/zigux/check-phase7-make-wrapper.py --self-test": 1,
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py": 1,
        "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test": 1,
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py": 1,
    },
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



def collect_count_mismatches(root: Path) -> list[str]:
    mismatches: list[str] = []
    for rel, expected_counts in EXACT_COUNT_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker, expected in expected_counts.items():
            actual = text.count(marker)
            if actual != expected:
                mismatches.append(f"{rel}: expected {expected} occurrence(s) of {marker!r}, found {actual}")
    return mismatches



def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []
    return [], collect_missing_markers(root), collect_count_mismatches(root)



def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "# fixture\n"), encoding="utf-8")

    workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text("make -C zigux phase7-validate\n", encoding="utf-8")

    makefile_path = tmp_root / "zigux/Makefile"
    makefile_text = makefile_path.read_text(encoding="utf-8")
    makefile_text = "\n".join(
        [
            makefile_text,
            "scripts/zigux/check-phase7-make-wrapper.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
        ]
    )
    makefile_path.write_text(makefile_text + "\n", encoding="utf-8")



def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, count_mismatches = validate(tmp_root)
    assert missing_files == [], case
    assert count_mismatches == [], case
    assert missing_markers == [marker], case



def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, count_mismatches = validate(tmp_root)
    assert missing_markers == [], case
    assert count_mismatches == [], case
    assert missing_files == [rel], case



def expect_count_mismatch(case: str, tmp_root: Path, mismatch: str) -> None:
    missing_files, missing_markers, count_mismatches = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [], case
    assert count_mismatches == [mismatch], case



def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")



def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_make_wrapper_alignment_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        missing_file_path = tmp_root / "scripts/zigux/check-phase7-build-wiring.py"
        missing_file_path.unlink()
        assert validate(tmp_root) == (["scripts/zigux/check-phase7-build-wiring.py"], [], [])
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.unlink()
        expect_missing_file(
            "missing_phase7_workflow_file",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml",
        )
        write_fixture_root(tmp_root)

        note_path = tmp_root / "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"
        note_text = note_path.read_text(encoding="utf-8")
        missing_note_marker = "python3 scripts/zigux/check-phase7-build-wiring.py --self-test"
        note_path.write_text(note_text.replace(missing_note_marker, "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_alignment_note_marker",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        )
        write_fixture_root(tmp_root)

        note_path = tmp_root / "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"
        note_text = note_path.read_text(encoding="utf-8")
        missing_argv_split_selftest_marker = "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test"
        note_path.write_text(note_text.replace(missing_argv_split_selftest_marker, "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_argv_split_selftest_marker",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        )
        write_fixture_root(tmp_root)

        note_path = tmp_root / "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"
        note_text = note_path.read_text(encoding="utf-8")
        missing_rbtree_direct_marker = "python3 scripts/zigux/check-phase7-rbtree-parity.py"
        note_path.write_text(note_text.replace(missing_rbtree_direct_marker, "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_rbtree_direct_marker",
            tmp_root,
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: python3 scripts/zigux/check-phase7-rbtree-parity.py",
        )
        write_fixture_root(tmp_root)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8")
        missing_makefile_marker = "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"
        makefile_path.write_text(makefile_text.replace(missing_makefile_marker, "", 1), encoding="utf-8")
        assert validate(tmp_root) == (
            [],
            ["zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"],
            [
                "zigux/Makefile: expected 1 occurrence(s) of 'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py', found 0"
            ],
        ), "missing_alignment_makefile_marker"
        write_fixture_root(tmp_root)

        checklist_path = tmp_root / "Documentation/zigux/review-checklist.md"
        checklist_text = checklist_path.read_text(encoding="utf-8")
        missing_checklist_marker = "zigux/tests/fixtures/phase7_argv_split_vectors.zig"
        checklist_path.write_text(checklist_text.replace(missing_checklist_marker, "", 1), encoding="utf-8")
        expect_missing_marker(
            "missing_checklist_marker",
            tmp_root,
            "Documentation/zigux/review-checklist.md: zigux/tests/fixtures/phase7_argv_split_vectors.zig",
        )
        write_fixture_root(tmp_root)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8")
        duplicate_make_wrapper_selftest = "scripts/zigux/check-phase7-make-wrapper.py --self-test"
        makefile_path.write_text(makefile_text + duplicate_make_wrapper_selftest + "\n", encoding="utf-8")
        expect_count_mismatch(
            "duplicate_make_wrapper_selftest",
            tmp_root,
            "zigux/Makefile: expected 1 occurrence(s) of 'scripts/zigux/check-phase7-make-wrapper.py --self-test', found 2",
        )
        write_fixture_root(tmp_root)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8")
        duplicate_alignment_hook = "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"
        makefile_path.write_text(makefile_text + duplicate_alignment_hook + "\n", encoding="utf-8")
        expect_count_mismatch(
            "duplicate_alignment_hook",
            tmp_root,
            "zigux/Makefile: expected 1 occurrence(s) of 'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py', found 2",
        )
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        duplicate_phase7_validate = "make -C zigux phase7-validate"
        workflow_path.write_text(workflow_text + duplicate_phase7_validate + "\n", encoding="utf-8")
        expect_count_mismatch(
            "duplicate_phase7_validate_workflow_route",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: expected 1 occurrence(s) of 'make -C zigux phase7-validate', found 2",
        )
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        direct_make_wrapper_hook = "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test"
        workflow_path.write_text(workflow_text + direct_make_wrapper_hook + "\n", encoding="utf-8")
        expect_count_mismatch(
            "direct_make_wrapper_workflow_hook",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: expected 0 occurrence(s) of 'python3 scripts/zigux/check-phase7-make-wrapper.py', found 1",
        )
        write_fixture_root(tmp_root)

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8")
        direct_alignment_hook = "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"
        workflow_path.write_text(workflow_text + direct_alignment_hook + "\n", encoding="utf-8")
        expect_count_mismatch(
            "direct_alignment_workflow_hook",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: expected 0 occurrence(s) of 'python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py', found 1",
        )

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_CASE_COUNT=12")



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 7 make-wrapper self-tests and direct replay hooks stay aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, count_mismatches = validate(ROOT)
    if missing_files:
        print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MARKERS_END")
        return 1

    if count_mismatches:
        print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
        print("MISMATCHED_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_COUNTS_START")
        for item in count_mismatches:
            print(item)
        print("MISMATCHED_PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_COUNTS_END")
        return 1

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    print(
        "PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_COUNT_RULE_COUNT="
        f"{sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

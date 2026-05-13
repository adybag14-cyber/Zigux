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
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase7.py",
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
        "scripts/zigux/check-phase7-make-wrapper.py",
        "make -C zigux phase7",
    ],
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md": [
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
        "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
        "python3 scripts/zigux/check-phase7-build-wiring.py",
    ],
    "samples/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper.py",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase7-make-wrapper.py",
        "make -C zigux phase7-validate",
        "make -C zigux phase7",
    ],
    "scripts/zigux/validate-phase7.py": [
        '"scripts/zigux/check-phase7-make-wrapper.py"',
        '"scripts/zigux/check-phase7-make-wrapper.py": [',
        '"--self-test"',
        '"PHASE7_MAKE_WRAPPER_SELF_TEST=pass"',
    ],
    "zigux/Makefile": [
        "phase7-validate:",
        "scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
        "phase7-test:",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
        "phase7: phase7-validate phase7-test",
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
        ("missing_phase7_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_phase7_docs_readme", "Documentation/zigux/README.md"),
        ("missing_phase7_alignment_note", "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"),
    ]

    marker_cases = [
        (
            "docs_readme_checker_marker",
            "Documentation/zigux/README.md",
            "scripts/zigux/check-phase7-make-wrapper.py",
            "",
            "Documentation/zigux/README.md: scripts/zigux/check-phase7-make-wrapper.py",
        ),
        (
            "alignment_note_selftest_marker",
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
            "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
            "",
            "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        ),
        (
            "scripts_readme_checker_marker",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase7-make-wrapper.py",
            "",
            "scripts/zigux/README.md: scripts/zigux/check-phase7-make-wrapper.py",
        ),
        (
            "validator_success_marker",
            "scripts/zigux/validate-phase7.py",
            '"PHASE7_MAKE_WRAPPER_SELF_TEST=pass"',
            '"PHASE7_MAKE_WRAPPER_DRIFT=pass"',
            'scripts/zigux/validate-phase7.py: "PHASE7_MAKE_WRAPPER_SELF_TEST=pass"',
        ),
        (
            "makefile_selftest_hook",
            "zigux/Makefile",
            "scripts/zigux/check-phase7-make-wrapper.py --self-test",
            "",
            "zigux/Makefile: scripts/zigux/check-phase7-make-wrapper.py --self-test",
        ),
        (
            "makefile_phase7_test_summary_marker",
            "zigux/Makefile",
            "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
            "zig build test --build-file zigux/tests/phase7_build.zig",
            "zigux/Makefile: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_make_wrapper_") as tmp_dir_str:
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
    print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the shared Phase 7 make-wrapper packet stays aligned.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_MAKE_WRAPPER=fail")
        print("MISSING_PHASE7_MAKE_WRAPPER_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_MAKE_WRAPPER_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_MAKE_WRAPPER=fail")
        print("MISSING_PHASE7_MAKE_WRAPPER_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_MAKE_WRAPPER_MARKERS_END")
        return 1

    print("PHASE7_MAKE_WRAPPER=pass")
    print(f"PHASE7_MAKE_WRAPPER_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_MAKE_WRAPPER_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

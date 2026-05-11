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


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_make_wrapper_alignment_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        missing_file_path = tmp_root / "scripts/zigux/check-phase7-build-wiring.py"
        missing_file_path.unlink()
        assert validate(tmp_root) == (["scripts/zigux/check-phase7-build-wiring.py"], [])
        write_fixture_root(tmp_root)

        note_path = tmp_root / "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md"
        note_text = note_path.read_text(encoding="utf-8")
        missing_note_marker = "python3 scripts/zigux/check-phase7-build-wiring.py --self-test"
        note_path.write_text(note_text.replace(missing_note_marker, "", 1), encoding="utf-8")
        assert validate(tmp_root) == (
            [],
            ["Documentation/zigux/phase7-make-wrapper-selftest-alignment.md: python3 scripts/zigux/check-phase7-build-wiring.py --self-test"],
        )
        write_fixture_root(tmp_root)

        makefile_path = tmp_root / "zigux/Makefile"
        makefile_text = makefile_path.read_text(encoding="utf-8")
        missing_makefile_marker = "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"
        makefile_path.write_text(makefile_text.replace(missing_makefile_marker, "", 1), encoding="utf-8")
        assert validate(tmp_root) == (
            [],
            ["zigux/Makefile: cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py"],
        )
        write_fixture_root(tmp_root)

        checklist_path = tmp_root / "Documentation/zigux/review-checklist.md"
        checklist_text = checklist_path.read_text(encoding="utf-8")
        missing_checklist_marker = "zigux/tests/fixtures/phase7_argv_split_vectors.zig"
        checklist_path.write_text(checklist_text.replace(missing_checklist_marker, "", 1), encoding="utf-8")
        assert validate(tmp_root) == (
            [],
            ["Documentation/zigux/review-checklist.md: zigux/tests/fixtures/phase7_argv_split_vectors.zig"],
        )

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 7 make-wrapper self-tests and direct replay hooks stay aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
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

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

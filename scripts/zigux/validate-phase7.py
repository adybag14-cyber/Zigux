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
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "zigux/tests/README.md",
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "lib/string_helpers.zig",
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
    ],
    "Documentation/zigux/README.md": [
        "restored starter packet",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    ],
    "samples/zigux/README.md": [
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample;",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/validate-phase7.py",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "make -C zigux phase7-validate",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase7_string_helpers.zig",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
        "zigux/tests/phase7_build.zig",
    ],
    "zigux/tests/phase7_build.zig": [
        '"phase7_string_helpers.zig"',
        '"phase7_string_helpers_sample_boundary.zig"',
        "phase7-string-helpers-tests",
        "phase7-string-helpers-sample-boundary-tests",
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


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        for rel in REQUIRED_FILES:
            path = tmp_root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            lines = REQUIRED_MARKERS.get(rel, ["fixture"])
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert validate(tmp_root) == ([], [])
        (tmp_root / "lib/string_helpers.zig").unlink()
        missing_files, missing_markers = validate(tmp_root)
        assert missing_markers == []
        assert missing_files == ["lib/string_helpers.zig"]
    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print("PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT=2")


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

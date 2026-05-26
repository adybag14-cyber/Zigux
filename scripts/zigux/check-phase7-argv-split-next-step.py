#!/usr/bin/env python3
"""Validate the current Phase 7 argv_split next-step packet alignment."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

EXPECTED_NEXT_BOUNDED_STEP = (
    "Keep same-lane follow-through limited to the returned fixture-backed helper-local "
    "survey-manifest-checker truthfulness packet, starting with exact `next_bounded_step` "
    "enforcement inside `scripts/zigux/check-phase7-argv-split-packet.py` before widening "
    "into any new vector-backed replay proof."
)

REQUIRED_FILES = [
    "Documentation/zigux/phase7-argv-split-slice.md",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/phase7_argv_split_survey.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-argv-split-slice.md": [
        EXPECTED_NEXT_BOUNDED_STEP,
    ],
    "zigux/tests/phase7_argv_split_survey.zig": [
        EXPECTED_NEXT_BOUNDED_STEP,
    ],
}

SELF_TEST_CASE_COUNT = 5


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    manifest = json.loads(read_text(root / "zigux/tests/phase7_argv_split_manifest.json"))
    if manifest.get("next_bounded_step") != EXPECTED_NEXT_BOUNDED_STEP:
        return [], ["zigux/tests/phase7_argv_split_manifest.json: next_bounded_step"]

    return [], collect_missing_markers(root)


def write_sample_root(root: Path) -> None:
    write(root / "Documentation/zigux/phase7-argv-split-slice.md", EXPECTED_NEXT_BOUNDED_STEP + "\n")
    write(root / "zigux/tests/phase7_argv_split_survey.zig", EXPECTED_NEXT_BOUNDED_STEP + "\n")
    write(
        root / "zigux/tests/phase7_argv_split_manifest.json",
        json.dumps({"next_bounded_step": EXPECTED_NEXT_BOUNDED_STEP}, indent=2) + "\n",
    )


def expect_missing_file(case: str, root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    assert missing_files == [], case
    assert missing_markers == [marker], case



def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_next_step_") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        assert validate(root) == ([], [])
        cases_run = 0

        manifest_path = root / "zigux/tests/phase7_argv_split_manifest.json"
        manifest = json.loads(read_text(manifest_path))
        manifest["next_bounded_step"] = "drifted next step"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_missing_marker("manifest_next_step_drift", root, "zigux/tests/phase7_argv_split_manifest.json: next_bounded_step")
        cases_run += 1
        write_sample_root(root)

        slice_path = root / "Documentation/zigux/phase7-argv-split-slice.md"
        slice_path.unlink()
        expect_missing_file("missing_slice_note", root, "Documentation/zigux/phase7-argv-split-slice.md")
        cases_run += 1
        write_sample_root(root)

        survey_path = root / "zigux/tests/phase7_argv_split_survey.zig"
        survey_path.unlink()
        expect_missing_file("missing_survey", root, "zigux/tests/phase7_argv_split_survey.zig")
        cases_run += 1
        write_sample_root(root)

        slice_path.write_text("", encoding="utf-8")
        expect_missing_marker("missing_slice_marker", root, f"Documentation/zigux/phase7-argv-split-slice.md: {EXPECTED_NEXT_BOUNDED_STEP}")
        cases_run += 1
        write_sample_root(root)

        survey_path.write_text("", encoding="utf-8")
        expect_missing_marker("missing_survey_marker", root, f"zigux/tests/phase7_argv_split_survey.zig: {EXPECTED_NEXT_BOUNDED_STEP}")
        cases_run += 1

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run

    print("PHASE7_ARGV_SPLIT_NEXT_STEP=pass")
    print(f"PHASE7_ARGV_SPLIT_NEXT_STEP_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a sample root and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE7_ARGV_SPLIT_NEXT_STEP=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_NEXT_STEP_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_NEXT_STEP_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_ARGV_SPLIT_NEXT_STEP=fail")
        print("MISSING_PHASE7_ARGV_SPLIT_NEXT_STEP_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_ARGV_SPLIT_NEXT_STEP_MARKERS_END")
        return 1

    print("PHASE7_ARGV_SPLIT_NEXT_STEP=pass")
    print(f"PHASE7_ARGV_SPLIT_NEXT_STEP_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

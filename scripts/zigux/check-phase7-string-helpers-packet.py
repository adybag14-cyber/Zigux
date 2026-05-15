#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "lib/string_helpers.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_string_helpers_sample_boundary.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "PHASE7_STATUS=starter_landed",
        "expanded starter packet",
        "stringEscapeMem()",
        "string_escape_str_any_np()",
        "The next bounded follow-through should stay inside the helper-local packet",
    ],
    "lib/string_helpers.zig": [
        "pub fn stringEscapeMem",
        "pub fn stringEscapeStrAnyNp",
        "pub fn memcpyAndPad",
        "pub fn strreplace",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes",
        "phase 7 string helpers starter pads bounded copies without reading past the provided source slice",
        "phase 7 string helpers starter replaces bytes only inside the exported c-string prefix",
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        "phase 7 string helpers survey keeps the expanded starter packet truthful",
        "\"current_master_state\": \"expanded_starter_packet\"",
        "\"stringEscapeMem\"",
        "\"memcpyAndPad\"",
        "zigux/tests/phase7_string_helpers_sample_boundary.zig",
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        "\"lane_key\": \"P7-L04\"",
        "\"current_master_state\": \"expanded_starter_packet\"",
        "\"stringEscapeMem\"",
        "\"string_escape_str_any_np\"",
        "\"memcpyAndPad\"",
        "\"strreplace\"",
        "\"ownership_focus\": [",
    ],
    "zigux/tests/phase7_string_helpers_sample_boundary.zig": [
        "phase 7 string helper boundary keeps the exact current sample inventory and no string sample",
        "phase 7 string helper boundary keeps the lane-local helper packet aligned without claiming shared control surfaces",
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample",
        "Documentation/zigux/phase7-string-helpers-slice.md",
        "zigux/tests/phase7_string_helpers_manifest.json",
        "zigux/tests/phase7_string_helpers_survey.zig",
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
        path.write_text(fixture_text[rel], encoding="utf-8")


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_string_helpers_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        (tmp_root / "zigux/tests/phase7_string_helpers_manifest.json").unlink()
        expect_missing_file(
            "missing_manifest",
            tmp_root,
            "zigux/tests/phase7_string_helpers_manifest.json",
        )
        write_fixture_root(tmp_root)

        marker_cases = [
            (
                "slice_next_step_marker",
                "Documentation/zigux/phase7-string-helpers-slice.md",
                "The next bounded follow-through should stay inside the helper-local packet",
                "",
                "Documentation/zigux/phase7-string-helpers-slice.md: The next bounded follow-through should stay inside the helper-local packet",
            ),
            (
                "helper_escape_marker",
                "lib/string_helpers.zig",
                "pub fn stringEscapeMem",
                "",
                "lib/string_helpers.zig: pub fn stringEscapeMem",
            ),
            (
                "tests_escape_marker",
                "zigux/tests/phase7_string_helpers.zig",
                "phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes",
                "",
                "zigux/tests/phase7_string_helpers.zig: phase 7 string helpers starter escapes bounded memory across flag families and dictionary modes",
            ),
            (
                "survey_boundary_marker",
                "zigux/tests/phase7_string_helpers_survey.zig",
                "zigux/tests/phase7_string_helpers_sample_boundary.zig",
                "",
                "zigux/tests/phase7_string_helpers_survey.zig: zigux/tests/phase7_string_helpers_sample_boundary.zig",
            ),
            (
                "manifest_lane_marker",
                "zigux/tests/phase7_string_helpers_manifest.json",
                "\"lane_key\": \"P7-L04\"",
                "",
                "zigux/tests/phase7_string_helpers_manifest.json: \"lane_key\": \"P7-L04\"",
            ),
            (
                "sample_boundary_marker",
                "zigux/tests/phase7_string_helpers_sample_boundary.zig",
                "phase 7 string helper boundary keeps the lane-local helper packet aligned without claiming shared control surfaces",
                "",
                "zigux/tests/phase7_string_helpers_sample_boundary.zig: phase 7 string helper boundary keeps the lane-local helper packet aligned without claiming shared control surfaces",
            ),
        ]

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    case_count = 1 + len(marker_cases)
    print("PHASE7_STRING_HELPERS_PACKET=pass")
    print(f"PHASE7_STRING_HELPERS_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 7 string_helpers helper-local packet stays aligned.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_STRING_HELPERS_PACKET=fail")
        print("MISSING_PHASE7_STRING_HELPERS_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_PACKET_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_STRING_HELPERS_PACKET=fail")
        print("MISSING_PHASE7_STRING_HELPERS_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_STRING_HELPERS_PACKET_MARKERS_END")
        return 1

    print("PHASE7_STRING_HELPERS_PACKET=pass")
    print(f"PHASE7_STRING_HELPERS_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE7_STRING_HELPERS_PACKET_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

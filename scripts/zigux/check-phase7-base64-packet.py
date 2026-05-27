#!/usr/bin/env python3
"""Validate the current Phase 7 base64 helper-local packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

EXPECTED_MANIFEST = {
    "lane_key": "P7-L14",
    "phase": "Phase 7",
    "anchor": "lib/base64.c",
    "current_master_state": "helper_slice_test_build_survey_manifest_checker_anchor",
    "roadmap_destinations": ["lib/base64.zig"],
}

EXPECTED_REVIEW_SURFACES = [
    "Documentation/zigux/phase7-base64-slice.md",
    "scripts/zigux/check-phase7-base64-packet.py",
    "lib/base64.zig",
    "zigux/tests/phase7_base64.zig",
    "zigux/tests/phase7_base64_build.zig",
    "zigux/tests/phase7_base64_survey.zig",
    "zigux/tests/phase7_base64_manifest.json",
]

EXPECTED_COVERED_HELPERS = [
    "chars",
    "bytesStd",
    "bytesUrlsafe",
    "bytesImap",
    "encodeStd",
    "encodeUrlsafe",
    "encodeImap",
    "decodeStd",
    "decodeUrlsafe",
    "decodeImap",
    "encodeStdSlice",
    "encodeStdAlloc",
    "decodeStdSlice",
    "decodeStdAlloc",
]

EXPECTED_OWNERSHIP_FOCUS = [
    "variant-pinned convenience wrappers keep the standard, urlsafe, and IMAP alphabets explicit without widening into shared streaming ownership",
    "short-tail packet checks keep one-byte and two-byte replay cases bounded to foreign-alphabet rejection and exact decoded lengths",
    "slice and allocator companions keep exact-span ownership reviewable for the same bounded standard packet",
    "the helper-local base64 packet stays separate from the broader shared Phase 7 docs-root, tests-root, Makefile, and workflow reminder surfaces",
]

EXPECTED_NEXT_STEP = (
    "Keep same-lane follow-through limited to this helper-local base64 packet and only reopen "
    "it when a fresh reread finds checker, manifest, replay, build-entrypoint, or slice-note "
    "drift inside these returned packet members before widening into any broader Phase 7 shared "
    "reminder work."
)

REQUIRED_FILES = [
    "Documentation/zigux/phase7-base64-slice.md",
    "scripts/zigux/check-phase7-base64-packet.py",
    "lib/base64.zig",
    "zigux/tests/phase7_base64.zig",
    "zigux/tests/phase7_base64_build.zig",
    "zigux/tests/phase7_base64_survey.zig",
    "zigux/tests/phase7_base64_manifest.json",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-base64-slice.md": [
        "`PHASE7_STATUS=helper_local_slice_note_test_build_survey_manifest_checker_anchor`",
        "`PHASE7_SLICE=base64-runtime-leaf`",
        "`PHASE7_LANE_KEY=P7-L14`",
        "`lib/base64.zig`",
        "`zigux/tests/phase7_base64_build.zig`",
        "urlsafe short tails stay inside the urlsafe alphabet and reject standard `+`-prefixed foreign tails",
    ],
    "scripts/zigux/check-phase7-base64-packet.py": [
        "--self-test",
        "PHASE7_BASE64_PACKET_SELF_TEST=pass",
        "PHASE7_BASE64_PACKET=pass",
        "PHASE7_BASE64_PACKET=fail",
        "MISSING_PHASE7_BASE64_FILES_START",
        "MISSING_PHASE7_BASE64_FILES_END",
        "MISSING_PHASE7_BASE64_MARKERS_START",
        "MISSING_PHASE7_BASE64_MARKERS_END",
        "MISMATCHED_PHASE7_BASE64_MANIFEST_START",
        "MISMATCHED_PHASE7_BASE64_MANIFEST_END",
        '"lane_key": "P7-L14"',
        '"anchor": "lib/base64.c"',
    ],
    "lib/base64.zig": [
        "pub const Variant = enum {",
        "pub fn bytesStd(src: []const u8, padding: bool) DecodeError!usize {",
        "pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {",
        "pub fn decodeStd(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {",
        "pub fn encodeUrlsafe(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {",
        "pub fn decodeUrlsafe(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {",
        "pub fn encodeImap(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {",
        "pub fn decodeImap(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {",
        'test "variant-pinned convenience helpers mirror the generic api" {',
    ],
    "zigux/tests/phase7_base64.zig": [
        'const base64 = @import("base64");',
        'test "phase 7 base64 companion replays standard padded convenience wrappers" {',
        'test "phase 7 base64 companion replays urlsafe short-tail wrappers without crossing into standard tails" {',
        'test "phase 7 base64 companion replays IMAP short-tail wrappers without slash-backed standard tails" {',
        'test "phase 7 base64 companion replays exact-span slice and allocator companions" {',
    ],
    "zigux/tests/phase7_base64_build.zig": [
        '.root_source_file = b.path("../../lib/base64.zig"),',
        '.root_source_file = b.path("phase7_base64.zig"),',
        'root_module.addImport("base64", base64_module);',
        '"phase7-base64-test"',
    ],
    "zigux/tests/phase7_base64_survey.zig": [
        'test "phase 7 base64 survey keeps the returned helper-local packet truthful" {',
        'try std.testing.expectEqualStrings("P7-L14", manifest.lane_key);',
        'try expectContains(checker, "PHASE7_BASE64_PACKET=pass");',
        'try expectContains(helper, "pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {");',
        'try expectContains(helper_companion, "phase 7 base64 companion replays exact-span slice and allocator companions");',
        'try expectContains(build_file, "\\"phase7-base64-test\\"");',
    ],
    "zigux/tests/phase7_base64_manifest.json": [
        '"lane_key": "P7-L14"',
        '"phase": "Phase 7"',
        '"anchor": "lib/base64.c"',
        '"current_master_state": "helper_slice_test_build_survey_manifest_checker_anchor"',
        '"Documentation/zigux/phase7-base64-slice.md"',
        '"zigux/tests/phase7_base64_build.zig"',
        '"encodeStd"',
        '"decodeStdAlloc"',
        '"the helper-local base64 packet stays separate from the broader shared Phase 7 docs-root, tests-root, Makefile, and workflow reminder surfaces"',
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def collect_manifest_mismatches(root: Path) -> list[str]:
    manifest = json.loads(read_text(root / "zigux/tests/phase7_base64_manifest.json"))
    mismatches: list[str] = []

    for key, expected in EXPECTED_MANIFEST.items():
        if manifest.get(key) != expected:
            mismatches.append(f"zigux/tests/phase7_base64_manifest.json: {key}")

    if manifest.get("review_surfaces") != EXPECTED_REVIEW_SURFACES:
        mismatches.append("zigux/tests/phase7_base64_manifest.json: review_surfaces")
    if manifest.get("covered_helpers") != EXPECTED_COVERED_HELPERS:
        mismatches.append("zigux/tests/phase7_base64_manifest.json: covered_helpers")
    if manifest.get("ownership_focus") != EXPECTED_OWNERSHIP_FOCUS:
        mismatches.append("zigux/tests/phase7_base64_manifest.json: ownership_focus")
    if manifest.get("next_bounded_step") != EXPECTED_NEXT_STEP:
        mismatches.append("zigux/tests/phase7_base64_manifest.json: next_bounded_step")

    return mismatches


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        return [], missing_markers, []

    mismatches = collect_manifest_mismatches(root)
    return [], [], mismatches


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        if rel == "zigux/tests/phase7_base64_manifest.json":
            continue
        write(root / rel, "\n".join(markers) + "\n")

    write(
        root / "zigux/tests/phase7_base64_manifest.json",
        json.dumps(
            {
                **EXPECTED_MANIFEST,
                "verified_on_utc": "2026-05-27T00:44:01Z",
                "review_surfaces": EXPECTED_REVIEW_SURFACES,
                "covered_helpers": EXPECTED_COVERED_HELPERS,
                "ownership_focus": EXPECTED_OWNERSHIP_FOCUS,
                "next_bounded_step": EXPECTED_NEXT_STEP,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_base64_packet_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_root(root)
        assert validate(root) == ([], [], [])

        missing_file_path = root / "zigux" / "tests" / "phase7_base64_build.zig"
        missing_file_path.unlink()
        missing_files, missing_markers, mismatches = validate(root)
        assert missing_files == ["zigux/tests/phase7_base64_build.zig"]
        assert missing_markers == []
        assert mismatches == []
        cases += 1

        write_fixture_root(root)
        manifest_path = root / "zigux" / "tests" / "phase7_base64_manifest.json"
        manifest = json.loads(read_text(manifest_path))
        manifest["lane_key"] = "P7-L09"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        missing_files, missing_markers, mismatches = validate(root)
        assert missing_files == []
        assert missing_markers == ['zigux/tests/phase7_base64_manifest.json: "lane_key": "P7-L14"']
        assert mismatches == []
        cases += 1

        write_fixture_root(root)
        helper_path = root / "lib" / "base64.zig"
        helper_text = read_text(helper_path)
        marker = "pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {"
        helper_path.write_text(helper_text.replace(marker + "\n", "", 1), encoding="utf-8")
        missing_files, missing_markers, mismatches = validate(root)
        assert missing_files == []
        assert mismatches == []
        assert missing_markers == [f"lib/base64.zig: {marker}"]
        cases += 1

        write_fixture_root(root)
        survey_path = root / "zigux" / "tests" / "phase7_base64_survey.zig"
        survey_text = read_text(survey_path)
        marker = 'try expectContains(build_file, "\\"phase7-base64-test\\"");'
        survey_path.write_text(survey_text.replace(marker + "\n", "", 1), encoding="utf-8")
        missing_files, missing_markers, mismatches = validate(root)
        assert missing_files == []
        assert mismatches == []
        assert missing_markers == [f"zigux/tests/phase7_base64_survey.zig: {marker}"]
        cases += 1

    print("PHASE7_BASE64_PACKET_SELF_TEST=pass")
    print(f"PHASE7_BASE64_PACKET_SELF_TEST_CASE_COUNT={cases}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, mismatches = validate(args.repo_root)
    if missing_files:
        print("PHASE7_BASE64_PACKET=fail")
        print("MISSING_PHASE7_BASE64_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_BASE64_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_BASE64_PACKET=fail")
        print("MISSING_PHASE7_BASE64_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_BASE64_MARKERS_END")
        return 1

    if mismatches:
        print("PHASE7_BASE64_PACKET=fail")
        print("MISMATCHED_PHASE7_BASE64_MANIFEST_START")
        for item in mismatches:
            print(item)
        print("MISMATCHED_PHASE7_BASE64_MANIFEST_END")
        return 1

    print("PHASE7_BASE64_PACKET=pass")
    print(f"PHASE7_BASE64_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_BASE64_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

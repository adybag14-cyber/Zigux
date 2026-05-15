#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent

STRING_HELPER_REL = "tools/lib/string.zig"
MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json"
CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md"

REQUIRED_FILES = [
    STRING_HELPER_REL,
    MANIFEST_REL,
    CLOSURE_REL,
    LANE_NOTE_REL,
]

STRING_SYSFS_ANCHOR_PREFIXES = (
    'test "sysfsStreq ',
    'test "sysfs_streq ',
    'test "sysfsMatchString ',
    'test "sysfs_match_string ',
)

EXPECTED_CLOSURE_MARKERS = [
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    "Those helper-local anchors are the bounded proof that newline-aware sysfs lookup order stays alias-locked and the long-buffer dirty-byte shortcut remains first-mismatch exact for both zero and non-zero scans across caller-visible prefix alignments.",
]

EXPECTED_LANE_NOTE_MARKERS = [
    "- Current `master` already exact-checks the string manifest's memparse, prefix and suffix, lookup, and `strnchr()` anchor groups through `scripts/zigux/validate-phase1-closure.py`, so the smallest same-lane string follow-up has narrowed to the helper-local sysfs review-anchor quartet before any wider string-local reopen.",
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens first for the helper-local sysfs review-anchor quartet because current master already exact-checks the memparse, matched-prefix and suffix, C-string lookup, and strnchr anchor groups through scripts/zigux/validate-phase1-closure.py; otherwise reopen only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; do not reopen a generic closure-validator pass`",
]

EXPECTED_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and closure note unless current master later adds dedicated shared sysfs fixture keys; until then, newline-aware equality and lookup order remain owned by the direct string tests."
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative for relative in REQUIRED_FILES if not (root / relative).exists()]


def extract_zig_test_names(text: str) -> list[str]:
    tests: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('test "'):
            continue
        closing_quote = stripped.find('"', len('test "'))
        if closing_quote == -1:
            continue
        tests.append(stripped[: closing_quote + 1])
    return tests


def expected_sysfs_review_anchors(test_names: list[str]) -> list[str]:
    return [name for name in test_names if name.startswith(STRING_SYSFS_ANCHOR_PREFIXES)]


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    lines = text.splitlines()
    missing: list[str] = []
    for marker in markers:
        count = lines.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_manifest_issues(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_REL
    try:
        manifest = json.loads(load_text(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"phase1_string_sysfs_manifest:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["phase1_string_sysfs_manifest:review_anchors"]

    string_review = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_review, dict):
        return ["phase1_string_sysfs_manifest:tools/lib/string.zig"]

    helper_tests = extract_zig_test_names(load_text(root / STRING_HELPER_REL))
    sysfs_review_anchors = string_review.get("sysfs_review_anchors")
    if sysfs_review_anchors != expected_sysfs_review_anchors(helper_tests):
        return ["phase1_string_sysfs_manifest:sysfs_review_anchors"]

    if string_review.get("next_safe_step_note") != EXPECTED_NEXT_SAFE_STEP_NOTE:
        return ["phase1_string_sysfs_manifest:next_safe_step_note"]

    return []


def collect_missing_markers(root: Path) -> list[str]:
    helper_tests = extract_zig_test_names(load_text(root / STRING_HELPER_REL))
    expected_anchors = expected_sysfs_review_anchors(helper_tests)
    missing: list[str] = []

    if len(expected_anchors) != 4:
        missing.append(f"phase1_string_sysfs_helper:test_count={len(expected_anchors)}")

    missing.extend(
        collect_exact_count_markers(
            load_text(root / CLOSURE_REL),
            "phase1_string_sysfs_closure",
            EXPECTED_CLOSURE_MARKERS,
        )
    )
    missing.extend(
        collect_exact_count_markers(
            load_text(root / LANE_NOTE_REL),
            "phase1_string_sysfs_lane_note",
            EXPECTED_LANE_NOTE_MARKERS,
        )
    )
    missing.extend(collect_manifest_issues(root))
    return missing


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    write_text(
        root,
        STRING_HELPER_REL,
        "\n".join(
            [
                'test "strtobool accepts common Linux forms" {}',
                'test "sysfsStreq treats trailing newline and NUL as equivalent" {}',
                'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence" {}',
                'test "sysfsMatchString finds newline-aware matches and preserves first-match order" {}',
                'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists" {}',
                'test "matchString finds C-string matches and preserves first-match order" {}',
            ]
        )
        + "\n",
    )
    write_text(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/string.zig": {
                        "sysfs_review_anchors": [
                            'test "sysfsStreq treats trailing newline and NUL as equivalent"',
                            'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
                            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
                            'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
                        ],
                        "next_safe_step_note": EXPECTED_NEXT_SAFE_STEP_NOTE,
                    }
                }
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root, CLOSURE_REL, "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n")
    write_text(root, LANE_NOTE_REL, "\n".join(EXPECTED_LANE_NOTE_MARKERS) + "\n")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_sysfs_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        for missing_file in REQUIRED_FILES:
            make_fixture_root(root)
            (root / missing_file).unlink()
            assert collect_missing_files(root) == [missing_file]
            case_count += 1

        for marker in EXPECTED_CLOSURE_MARKERS:
            make_fixture_root(root)
            closure_path = root / CLOSURE_REL
            closure_text = load_text(closure_path)
            closure_path.write_text(closure_text.replace(marker + "\n", "", 1), encoding="utf-8")
            assert f"phase1_string_sysfs_closure:{marker}:expected=1:actual=0" in collect_missing_markers(root)
            case_count += 1

        for marker in EXPECTED_LANE_NOTE_MARKERS:
            make_fixture_root(root)
            lane_note_path = root / LANE_NOTE_REL
            lane_note_text = load_text(lane_note_path)
            lane_note_path.write_text(lane_note_text.replace(marker + "\n", "", 1), encoding="utf-8")
            assert f"phase1_string_sysfs_lane_note:{marker}:expected=1:actual=0" in collect_missing_markers(root)
            case_count += 1

        make_fixture_root(root)
        manifest_path = root / MANIFEST_REL
        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/string.zig"]["sysfs_review_anchors"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_string_sysfs_manifest:sysfs_review_anchors" in collect_missing_markers(root)
        case_count += 1

        make_fixture_root(root)
        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/string.zig"]["next_safe_step_note"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_string_sysfs_manifest:next_safe_step_note" in collect_missing_markers(root)
        case_count += 1

        make_fixture_root(root)
        helper_path = root / STRING_HELPER_REL
        helper_text = load_text(helper_path)
        helper_path.write_text(
            helper_text.replace(
                'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists" {}\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert "phase1_string_sysfs_helper:test_count=3" in collect_missing_markers(root)
        case_count += 1

    print("PHASE1_STRING_SYSFS_REVIEW_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_STRING_SYSFS_REVIEW_ANCHOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 1 string sysfs review anchors stay aligned."
    )
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_STRING_SYSFS_REVIEW_ANCHORS=fail")
        print("MISSING_PHASE1_STRING_SYSFS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_STRING_SYSFS_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_STRING_SYSFS_REVIEW_ANCHORS=fail")
        print("MISSING_PHASE1_STRING_SYSFS_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_STRING_SYSFS_MARKERS_END")
        return 1

    print("PHASE1_STRING_SYSFS_REVIEW_ANCHORS=pass")
    print(f"PHASE1_STRING_SYSFS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_STRING_SYSFS_REQUIRED_MARKER_COUNT="
        f"{len(EXPECTED_CLOSURE_MARKERS) + len(EXPECTED_LANE_NOTE_MARKERS) + 2}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

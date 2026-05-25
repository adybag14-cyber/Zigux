#!/usr/bin/env python3
"""Guard the bounded Phase 7 cmdline-quoting helper-local packet."""

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
    "zigux/tests/phase7_string_helpers_manifest.json",
    "zigux/tests/phase7_string_helpers_survey.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase7-string-helpers-slice.md": [
        "quoted cmdline duplication that collapses trailing NULs, replaces inter-argument NULs with spaces",
        "`kstrdupQuotableCmdline()` keeps returned storage caller-owned",
    ],
    "lib/string_helpers.zig": [
        "pub fn kstrdupQuotableCmdline(",
        "pub fn kstrdup_quotable_cmdline(",
        "var end = raw.len;",
        "while (end > 0 and raw[end - 1] == 0) : (end -= 1) {}",
        "const normalized = try allocator.dupe(u8, raw[0..end]);",
        "if (ch.* == 0) ch.* = ' ';",
        "return (try kstrdupQuotable(allocator, normalized)).?;",
    ],
    "zigux/tests/phase7_string_helpers.zig": [
        'test "kstrdupQuotableCmdline collapses trailing nulls and replaces inter-argument separators before quoting" {',
        'try std.testing.expectEqualStrings("zig build\\x0A\\x22", quoted);',
        'const blank = [_]u8{ 0, 0, 0 };',
        'try std.testing.expectEqualStrings("", quoted_blank);',
        'try std.testing.expect((try kstrdupQuotableCmdline(std.testing.allocator, null)) == null);',
        'test "kstrdupQuotableCmdline reports allocation failure cleanly" {',
    ],
    "zigux/tests/phase7_string_helpers_manifest.json": [
        "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters",
        "kstrdupQuotableCmdline() keeps returned storage caller-owned, leaves the caller source buffer untouched, collapses trailing and inter-argument NULL separators only inside duplicated command-line storage, and only then applies quotable escaping",
    ],
    "zigux/tests/phase7_string_helpers_survey.zig": [
        'try expectContains(helper, "pub fn kstrdupQuotableCmdline(");',
        'try expectContains(helper, "pub fn kstrdup_quotable_cmdline(");',
        'try expectContains(helper_tests, "test \\"phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators\\" {");',
        'try expectContains(manifest, "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters");',
    ],
}

FORBIDDEN_MARKERS = {
    "lib/string_helpers.zig": [
        "pub fn parseIntArrayUser(",
        "pub fn parse_int_array_user(",
    ],
}

SELF_TEST_CASE_COUNT = 8


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write(root / rel, "\n".join(REQUIRED_MARKERS[rel]) + "\n")


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if missing_files:
        return missing_files, [], []

    missing_markers: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel}: {marker}")

    unexpected_markers: list[str] = []
    for rel, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker in text:
                unexpected_markers.append(f"{rel}: {marker}")

    return missing_files, missing_markers, unexpected_markers


def remove_once(path: Path, marker: str) -> None:
    text = read_text(path)
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def expect(result: tuple[list[str], list[str], list[str]], files: list[str], markers: list[str], unexpected: list[str], case: str) -> None:
    assert result == (files, markers, unexpected), case


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_quoting_packet_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        write_fixture_root(root)
        expect(validate(root), [], [], [], "clean_fixture")
        cases_run = 1

        missing_path = root / "lib" / "string_helpers.zig"
        missing_path.unlink()
        expect(validate(root), ["lib/string_helpers.zig"], [], [], "missing_helper")
        cases_run += 1

        write_fixture_root(root)
        helper_path = root / "lib" / "string_helpers.zig"
        marker = "pub fn kstrdupQuotableCmdline("
        remove_once(helper_path, marker)
        expect(validate(root), [], [f"lib/string_helpers.zig: {marker}"], [], "missing_helper_marker")
        cases_run += 1

        write_fixture_root(root)
        tests_path = root / "zigux" / "tests" / "phase7_string_helpers.zig"
        marker = 'try std.testing.expectEqualStrings("zig build\\x0A\\x22", quoted);'
        remove_once(tests_path, marker)
        expect(validate(root), [], [f"zigux/tests/phase7_string_helpers.zig: {marker}"], [], "missing_test_expectation")
        cases_run += 1

        write_fixture_root(root)
        manifest_path = root / "zigux" / "tests" / "phase7_string_helpers_manifest.json"
        marker = "quoted cmdline duplication that collapses trailing NULL separators into spaces before escaping special characters"
        remove_once(manifest_path, marker)
        expect(validate(root), [], [f"zigux/tests/phase7_string_helpers_manifest.json: {marker}"], [], "missing_manifest_marker")
        cases_run += 1

        write_fixture_root(root)
        survey_path = root / "zigux" / "tests" / "phase7_string_helpers_survey.zig"
        marker = 'try expectContains(helper_tests, "test \\"phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators\\" {");'
        remove_once(survey_path, marker)
        expect(validate(root), [], [f"zigux/tests/phase7_string_helpers_survey.zig: {marker}"], [], "missing_survey_marker")
        cases_run += 1

        write_fixture_root(root)
        docs_path = root / "Documentation" / "zigux" / "phase7-string-helpers-slice.md"
        marker = "`kstrdupQuotableCmdline()` keeps returned storage caller-owned"
        remove_once(docs_path, marker)
        expect(validate(root), [], [f"Documentation/zigux/phase7-string-helpers-slice.md: {marker}"], [], "missing_docs_marker")
        cases_run += 1

        write_fixture_root(root)
        helper_path = root / "lib" / "string_helpers.zig"
        forbidden = "pub fn parseIntArrayUser("
        helper_path.write_text(read_text(helper_path) + forbidden + "\n", encoding="utf-8")
        expect(validate(root), [], [], [f"lib/string_helpers.zig: {forbidden}"], "unexpected_follow_on")
        cases_run += 1

        assert cases_run == SELF_TEST_CASE_COUNT, cases_run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="write a passing sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("PHASE7_CMDLINE_QUOTING_PACKET_SELF_TEST=pass")
        print(f"PHASE7_CMDLINE_QUOTING_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
        return 0

    if args.write_sample_root is not None:
        write_fixture_root(args.write_sample_root)
        print(f"PHASE7_CMDLINE_QUOTING_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    missing_files, missing_markers, unexpected_markers = validate(args.root)
    if not any((missing_files, missing_markers, unexpected_markers)):
        print("PHASE7_CMDLINE_QUOTING_PACKET=pass")
        return 0

    print("PHASE7_CMDLINE_QUOTING_PACKET=fail")
    if missing_files:
        print("MISSING_PHASE7_CMDLINE_QUOTING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_CMDLINE_QUOTING_FILES_END")
    if missing_markers:
        print("MISSING_PHASE7_CMDLINE_QUOTING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_CMDLINE_QUOTING_MARKERS_END")
    if unexpected_markers:
        print("UNEXPECTED_PHASE7_CMDLINE_QUOTING_MARKERS_START")
        for item in unexpected_markers:
            print(item)
        print("UNEXPECTED_PHASE7_CMDLINE_QUOTING_MARKERS_END")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

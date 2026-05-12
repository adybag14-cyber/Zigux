#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
import tempfile


NOTE_PATH = Path("Documentation/zigux/phase5-kfifo-sample-survey.md")
SAMPLE_PATH = Path("samples/zigux/bytestream_fifo.zig")
SURVEY_PATH = Path("zigux/tests/phase5_bytestream_fifo_survey.zig")

REQUIRED_NOTE_MARKERS = (
    "runtime_bitmap_top_bit_contract.zig",
    "shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route for the bytestream packet",
    "without relying on a brittle aggregate build-step or test count",
    '`"hel"`',
    '`"lo"`',
    "`previewInto()`",
    "`snapshotInto()`",
)

REQUIRED_SURVEY_MARKERS = (
    "## Latest verification snapshot",
    "shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route for the bytestream packet",
    "without relying on a brittle aggregate build-step or test count",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_sample_tests(sample_text: str) -> int:
    return sum(1 for line in sample_text.splitlines() if line.startswith('test "'))


def extract_sample_check_count(text: str) -> int | None:
    match = re.search(r"passed `(\d+)/(\d+)` sample self-checks", text)
    if match is None:
        return None
    numerator = int(match.group(1))
    denominator = int(match.group(2))
    if numerator != denominator:
        return -1
    return numerator


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    required_files = (NOTE_PATH, SAMPLE_PATH, SURVEY_PATH)
    for rel_path in required_files:
        if not (root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
    if issues:
        return issues

    note_text = read_text(root / NOTE_PATH)
    sample_text = read_text(root / SAMPLE_PATH)
    survey_text = read_text(root / SURVEY_PATH)

    expected_count = count_sample_tests(sample_text)
    if expected_count == 0:
        issues.append("bytestream sample exposes zero test blocks")

    note_count = extract_sample_check_count(note_text)
    if note_count is None:
        issues.append("phase5 bytestream survey note is missing a sample self-check count marker")
    elif note_count < 0:
        issues.append("phase5 bytestream survey note uses mismatched sample self-check counts")
    elif note_count != expected_count:
        issues.append(
            f"phase5 bytestream survey note says {note_count}/{note_count} sample self-checks but sample exposes {expected_count} tests"
        )

    survey_count = extract_sample_check_count(survey_text)
    if survey_count is None:
        issues.append("phase5 bytestream survey gate is missing a sample self-check count marker")
    elif survey_count < 0:
        issues.append("phase5 bytestream survey gate uses mismatched sample self-check counts")
    elif survey_count != expected_count:
        issues.append(
            f"phase5 bytestream survey gate expects {survey_count}/{survey_count} sample self-checks but sample exposes {expected_count} tests"
        )

    aligned_marker = f"passed `{expected_count}/{expected_count}` sample self-checks"
    if aligned_marker not in note_text:
        issues.append(f"phase5 bytestream survey note is missing aligned marker: {aligned_marker}")
    if aligned_marker not in survey_text:
        issues.append(f"phase5 bytestream survey gate is missing aligned marker: {aligned_marker}")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"phase5 bytestream survey note missing marker: {marker}")

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey_text:
            issues.append(f"phase5 bytestream survey gate missing marker: {marker}")

    return issues


def write_file(root: Path, rel_path: Path, text: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_text(test_count: int) -> str:
    blocks = []
    for index in range(test_count):
        blocks.append(f'test "sample test {index}" {{}}\n')
    return "\n".join(blocks)


def build_note_text(test_count: int) -> str:
    return "\n".join(
        [
            "# Phase 5 Kfifo Sample Survey",
            "",
            "runtime_bitmap_top_bit_contract.zig",
            '`"hel"`',
            '`"lo"`',
            "`previewInto()`",
            "`snapshotInto()`",
            "## Latest verification snapshot",
            "shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route for the bytestream packet",
            "without relying on a brittle aggregate build-step or test count",
            f"passed `{test_count}/{test_count}` sample self-checks",
            "",
        ]
    )


def build_survey_text(test_count: int) -> str:
    return "\n".join(
        [
            "const required_markers = [_][]const u8{",
            '"## Latest verification snapshot",',
            '"shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route for the bytestream packet",',
            '"without relying on a brittle aggregate build-step or test count",',
            f'"passed `{test_count}/{test_count}` sample self-checks",',
            "};",
            "",
        ]
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase5_bytestream_note_") as tmp_dir:
        root = Path(tmp_dir)

        def reset(test_count: int = 5) -> None:
            write_file(root, NOTE_PATH, build_note_text(test_count))
            write_file(root, SAMPLE_PATH, build_sample_text(test_count))
            write_file(root, SURVEY_PATH, build_survey_text(test_count))

        reset()
        issues = validate(root)
        if issues:
            print("PHASE5_BYTESTREAM_NOTE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        reset()
        write_file(root, NOTE_PATH, build_note_text(4))
        issues = validate(root)
        expected = "phase5 bytestream survey note says 4/4 sample self-checks but sample exposes 5 tests"
        if expected not in issues:
            print("PHASE5_BYTESTREAM_NOTE_SELF_TEST=fail")
            print("missing expected note-drift report")
            return 1
        case_count += 1

        reset()
        write_file(root, SURVEY_PATH, build_survey_text(4))
        issues = validate(root)
        expected = "phase5 bytestream survey gate expects 4/4 sample self-checks but sample exposes 5 tests"
        if expected not in issues:
            print("PHASE5_BYTESTREAM_NOTE_SELF_TEST=fail")
            print("missing expected survey-drift report")
            return 1
        case_count += 1

        reset()
        note_text = build_note_text(5).replace("runtime_bitmap_top_bit_contract.zig\n", "", 1)
        write_file(root, NOTE_PATH, note_text)
        issues = validate(root)
        expected = "phase5 bytestream survey note missing marker: runtime_bitmap_top_bit_contract.zig"
        if expected not in issues:
            print("PHASE5_BYTESTREAM_NOTE_SELF_TEST=fail")
            print("missing expected companion-marker report")
            return 1
        case_count += 1

        reset()
        note_text = build_note_text(5).replace("without relying on a brittle aggregate build-step or test count\n", "", 1)
        write_file(root, NOTE_PATH, note_text)
        issues = validate(root)
        expected = "phase5 bytestream survey note missing marker: without relying on a brittle aggregate build-step or test count"
        if expected not in issues:
            print("PHASE5_BYTESTREAM_NOTE_SELF_TEST=fail")
            print("missing expected route-marker report")
            return 1
        case_count += 1

    print("PHASE5_BYTESTREAM_NOTE_SELF_TEST=pass")
    print(f"PHASE5_BYTESTREAM_NOTE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 5 bytestream FIFO survey packet stays aligned with the shipped sample test surface."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.repo_root)
    if issues:
        print("PHASE5_BYTESTREAM_NOTE=fail")
        for issue in issues:
            print(issue)
        return 1

    sample_text = read_text(args.repo_root / SAMPLE_PATH)
    expected_count = count_sample_tests(sample_text)
    print("PHASE5_BYTESTREAM_NOTE=pass")
    print(f"PHASE5_BYTESTREAM_NOTE_SAMPLE_TEST_COUNT={expected_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

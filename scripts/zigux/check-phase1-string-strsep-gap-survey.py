#!/usr/bin/env python3
"""Validate the Phase 1 string strsep survey note against current helper reality."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")
SURVEY_REL = Path("Documentation/zigux/phase1-string-strsep-gap-survey.md")

STRSEP_SYMBOL = "pub fn strsep(cursor: *?[]u8, delimiters: []const u8) ?[]u8 {"
STRSEP_TESTS = [
    'test "strsep splits mutable C strings and preserves empty tokens"',
    'test "strsep respects C-string delimiter and source boundaries"',
    'test "strsep with an empty delimiter set returns the remaining C string once"',
]
SURVEY_MARKERS = [
    "`PHASE1_STRING_STRSEP_SURVEY_STATUS=packet-gap-recorded`",
    "`PHASE1_STRING_STRSEP_ROADMAP_SCOPE=tools/lib/string.zig host-side helper`",
    "`PHASE1_STRING_STRSEP_LEDGER_SCOPE=Phase 1 helper train`",
    f"`PHASE1_STRING_STRSEP_SOURCE_HELPER={STRSEP_SYMBOL}`",
    "`PHASE1_STRING_STRSEP_REVIEW_PACKET_GAP=scripts/zigux/check-phase1-string-review-packet.py does not yet list the strsep symbol or its three direct helper tests in EXPECTED_STRING_SOURCE_SYMBOLS or EXPECTED_HELPER_TEST_ANCHORS`",
    "`PHASE1_STRING_STRSEP_NEXT_STEP=when the string review packet reopens, add strsep to the existing packet checker and manifest review anchors, then retire or narrow this gap survey`",
]


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def read_text(root: Path, relative_path: Path) -> str | None:
    path = root / relative_path
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def require_once(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    helper_text = read_text(root, STRING_HELPER_REL)
    survey_text = read_text(root, SURVEY_REL)

    if helper_text is None:
        failures.append(f"missing_file:{STRING_HELPER_REL.as_posix()}")
    if survey_text is None:
        failures.append(f"missing_file:{SURVEY_REL.as_posix()}")
    if failures:
        return failures

    assert helper_text is not None
    assert survey_text is not None

    failures.extend(require_once(helper_text, "string_helper:strsep_symbol", STRSEP_SYMBOL))
    for test_anchor in STRSEP_TESTS:
        failures.extend(require_once(helper_text, "string_helper:strsep_test", test_anchor))

    for marker in SURVEY_MARKERS:
        failures.extend(require_once(survey_text, "strsep_survey", marker))

    test_marker = "`PHASE1_STRING_STRSEP_TEST_ANCHORS=" + ";".join(STRSEP_TESTS) + "`"
    failures.extend(require_once(survey_text, "strsep_survey", test_marker))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_helper() -> str:
    return "\n".join([STRSEP_SYMBOL, *STRSEP_TESTS]) + "\n"


def sample_survey() -> str:
    test_marker = "`PHASE1_STRING_STRSEP_TEST_ANCHORS=" + ";".join(STRSEP_TESTS) + "`"
    return "# sample\n\n" + "\n".join([*SURVEY_MARKERS, test_marker]) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_strsep_survey_") as tmp:
        root = Path(tmp)
        missing = collect_failures(root)
        if f"missing_file:{STRING_HELPER_REL.as_posix()}" not in missing:
            raise SystemExit("phase1-string-strsep-survey:self-test:missing_helper")
        if f"missing_file:{SURVEY_REL.as_posix()}" not in missing:
            raise SystemExit("phase1-string-strsep-survey:self-test:missing_survey")

        write_file(root, STRING_HELPER_REL, sample_helper())
        write_file(root, SURVEY_REL, sample_survey())
        if collect_failures(root):
            raise SystemExit("phase1-string-strsep-survey:self-test:baseline")

        write_file(root, STRING_HELPER_REL, sample_helper().replace(STRSEP_TESTS[0] + "\n", "", 1))
        if not any(item.startswith("string_helper:strsep_test") for item in collect_failures(root)):
            raise SystemExit("phase1-string-strsep-survey:self-test:missing_strsep_test")

        write_file(root, STRING_HELPER_REL, sample_helper())
        write_file(root, SURVEY_REL, sample_survey().replace(SURVEY_MARKERS[0] + "\n", "", 1))
        if not any(item.startswith("strsep_survey") for item in collect_failures(root)):
            raise SystemExit("phase1-string-strsep-survey:self-test:missing_survey_marker")

    print("PHASE1_STRING_STRSEP_SURVEY_SELF_TEST=pass")
    print("PHASE1_STRING_STRSEP_SURVEY_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-string-strsep-gap-survey:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

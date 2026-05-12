#!/usr/bin/env python3
"""Validate the parked Phase 4 gap-packet reminders in zigux/tests/README.md."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
README_REL = Path("zigux/tests/README.md")

REQUIRED_MARKERS = [
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "make -C zigux phase4-kprobe-example-survey",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
]

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_tests_readme_file",
    "missing_kprobe_make_wrapper",
    "missing_test_fsmount_make_wrapper",
    "missing_kprobe_gap_note",
    "missing_test_fsmount_direct_entrypoint",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing marker: {old}")
    return text.replace(old, new, 1)


def validate_root(root: Path) -> list[str]:
    readme_path = root / README_REL
    if not readme_path.exists():
        return [f"file:{README_REL.as_posix()}"]

    text = read_text(readme_path)
    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{marker}")
    return failures


def build_fixture_text() -> str:
    return "\n".join(
        [
            "# zigux/tests",
            "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
            "zigux/tests/phase4_kprobe_example_manifest.json",
            "zigux/tests/phase4_kprobe_example_survey.zig",
            "zig test zigux/tests/phase4_kprobe_example_survey.zig",
            "make -C zigux phase4-kprobe-example-survey",
            "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
            "zigux/tests/phase4_test_fsmount_manifest.json",
            "zigux/tests/phase4_test_fsmount_survey.zig",
            "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
            "make -C zigux phase4-test-fsmount-survey",
            "",
        ]
    )


def expect_failure(root: Path, expected: str) -> bool:
    return expected in validate_root(root)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_tests_readme_gap_packets_") as tmp_dir:
        root = Path(tmp_dir)
        readme_path = root / README_REL
        baseline = build_fixture_text()
        write_text(readme_path, baseline)

        if validate_root(root):
            print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=fail")
            print("baseline fixture did not validate")
            return 1
        case_count += 1

        readme_path.unlink()
        if not expect_failure(root, f"file:{README_REL.as_posix()}"):
            print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=fail")
            print("missing tests README case did not fail closed")
            return 1
        case_count += 1

        write_text(
            readme_path,
            replace_once(
                baseline,
                "make -C zigux phase4-kprobe-example-survey",
                "make -C zigux phase4-kprobe-gap-survey",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:make -C zigux phase4-kprobe-example-survey",
        ):
            print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=fail")
            print("missing kprobe wrapper case did not fail closed")
            return 1
        case_count += 1

        write_text(
            readme_path,
            replace_once(
                baseline,
                "make -C zigux phase4-test-fsmount-survey",
                "make -C zigux phase4-test-fsmount-gap-survey",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:make -C zigux phase4-test-fsmount-survey",
        ):
            print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=fail")
            print("missing test_fsmount wrapper case did not fail closed")
            return 1
        case_count += 1

        write_text(
            readme_path,
            replace_once(
                baseline,
                "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
                "Documentation/zigux/phase4-kprobe-gap-survey.md",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        ):
            print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=fail")
            print("missing kprobe note case did not fail closed")
            return 1
        case_count += 1

        write_text(
            readme_path,
            replace_once(
                baseline,
                "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "zig build phase4-test-fsmount-gap-survey --build-file zigux/tests/phase4_build.zig",
            ),
        )
        if not expect_failure(
            root,
            "missing_marker:zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        ):
            print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=fail")
            print("missing test_fsmount direct entrypoint case did not fail closed")
            return 1
        case_count += 1

    if case_count != len(SELF_TEST_CASES):
        print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=fail")
        print(f"unexpected self-test case count {case_count} != {len(SELF_TEST_CASES)}")
        return 1

    print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST=pass")
    print(f"PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST_CASE_COUNT={case_count}")
    print("PHASE4_TESTS_README_GAP_PACKETS_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 4 parked gap-packet reminders in zigux/tests/README.md."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated coverage checks in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_TESTS_README_GAP_PACKETS_CHECK=fail")
        print("PHASE4_TESTS_README_GAP_PACKETS_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_TESTS_README_GAP_PACKETS_FAILURES_END")
        return 1

    print("PHASE4_TESTS_README_GAP_PACKETS_CHECK=pass")
    print(f"PHASE4_TESTS_README_GAP_PACKETS_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

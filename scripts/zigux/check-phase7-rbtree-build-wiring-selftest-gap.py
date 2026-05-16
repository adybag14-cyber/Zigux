#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

NOTE_PATH = "Documentation/zigux/phase7-rbtree-build-wiring-selftest-gap.md"
RBTREE_CHECKER_PATH = "scripts/zigux/check-phase7-rbtree-parity.py"

NOTE_REQUIRED_MARKERS = [
    "scripts/zigux/check-phase7-build-wiring.py",
    "add one missing-file self-test branch for `scripts/zigux/check-phase7-build-wiring.py`",
    "Whole-file replacement without a trustworthy full read would risk dropping unrelated checker content.",
]

CHECKER_REQUIRED_MARKERS = [
    "scripts/zigux/check-phase7-build-wiring.py",
    '("missing_json_fixture", "zigux/tests/fixtures/phase7_rbtree.json")',
    '("missing_c_harness", "zigux/tests/fixtures/phase7_rbtree_c_harness.c")',
]

CHECKER_FORBIDDEN_MARKERS = [
    '("missing_build_wiring_checker", "scripts/zigux/check-phase7-build-wiring.py")',
    '("missing_build_wiring", "scripts/zigux/check-phase7-build-wiring.py")',
]


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []
    forbidden_markers: list[str] = []

    for rel in (NOTE_PATH, RBTREE_CHECKER_PATH):
        if not (root / rel).is_file():
            missing_files.append(rel)

    if missing_files:
        return missing_files, missing_markers, forbidden_markers

    note_text = read_text(root, NOTE_PATH)
    checker_text = read_text(root, RBTREE_CHECKER_PATH)

    for marker in NOTE_REQUIRED_MARKERS:
        if marker not in note_text:
            missing_markers.append(f"{NOTE_PATH}: {marker}")

    for marker in CHECKER_REQUIRED_MARKERS:
        if marker not in checker_text:
            missing_markers.append(f"{RBTREE_CHECKER_PATH}: {marker}")

    for marker in CHECKER_FORBIDDEN_MARKERS:
        if marker in checker_text:
            forbidden_markers.append(f"{RBTREE_CHECKER_PATH}: {marker}")

    return missing_files, missing_markers, forbidden_markers


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / NOTE_PATH).write_text(
        "scripts/zigux/check-phase7-build-wiring.py\n"
        "add one missing-file self-test branch for `scripts/zigux/check-phase7-build-wiring.py`\n"
        "Whole-file replacement without a trustworthy full read would risk dropping unrelated checker content.\n",
        encoding="utf-8",
    )
    (root / RBTREE_CHECKER_PATH).write_text(
        'REQUIRED_FILES = ["scripts/zigux/check-phase7-build-wiring.py"]\n'
        'missing_file_cases = [\n'
        '    ("missing_json_fixture", "zigux/tests/fixtures/phase7_rbtree.json"),\n'
        '    ("missing_c_harness", "zigux/tests/fixtures/phase7_rbtree_c_harness.c"),\n'
        "]\n",
        encoding="utf-8",
    )


def expect_missing_marker(root: Path, expected: str) -> None:
    missing_files, missing_markers, forbidden_markers = validate(root)
    assert missing_files == []
    assert missing_markers == [expected]
    assert forbidden_markers == []


def expect_forbidden_marker(root: Path, expected: str) -> None:
    missing_files, missing_markers, forbidden_markers = validate(root)
    assert missing_files == []
    assert missing_markers == []
    assert forbidden_markers == [expected]


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_build_wiring_gap_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        write_fixture_tree(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        (tmp_root / NOTE_PATH).unlink()
        missing_files, missing_markers, forbidden_markers = validate(tmp_root)
        assert missing_files == [NOTE_PATH]
        assert missing_markers == []
        assert forbidden_markers == []

        write_fixture_tree(tmp_root)
        note_path = tmp_root / NOTE_PATH
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "add one missing-file self-test branch for `scripts/zigux/check-phase7-build-wiring.py`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            tmp_root,
            f"{NOTE_PATH}: add one missing-file self-test branch for `scripts/zigux/check-phase7-build-wiring.py`",
        )

        write_fixture_tree(tmp_root)
        checker_path = tmp_root / RBTREE_CHECKER_PATH
        checker_path.write_text(
            checker_path.read_text(encoding="utf-8").replace(
                "scripts/zigux/check-phase7-build-wiring.py",
                "scripts/zigux/check-phase7-build-inventory.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            tmp_root,
            f"{RBTREE_CHECKER_PATH}: scripts/zigux/check-phase7-build-wiring.py",
        )

        write_fixture_tree(tmp_root)
        checker_path = tmp_root / RBTREE_CHECKER_PATH
        checker_path.write_text(
            checker_path.read_text(encoding="utf-8")
            + '("missing_build_wiring_checker", "scripts/zigux/check-phase7-build-wiring.py")\n',
            encoding="utf-8",
        )
        expect_forbidden_marker(
            tmp_root,
            f'{RBTREE_CHECKER_PATH}: ("missing_build_wiring_checker", "scripts/zigux/check-phase7-build-wiring.py")',
        )

    print("PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP=pass")
    print("PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 7 rbtree build-wiring self-test gap stays explicit until the live checker is repaired."
    )
    parser.add_argument("--self-test", action="store_true", help="Run synthetic checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, forbidden_markers = validate(ROOT)
    if missing_files:
        print("PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP=fail")
        print("MISSING_PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP=fail")
        print("MISSING_PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_MARKERS_END")
        return 1

    if forbidden_markers:
        print("PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP=fail")
        print("FORBIDDEN_PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_MARKERS_START")
        for item in forbidden_markers:
            print(item)
        print("FORBIDDEN_PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_MARKERS_END")
        return 1

    print("PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP=pass")
    print("PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_FILE_COUNT=2")
    print(
        "PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_REQUIRED_MARKER_COUNT="
        f"{len(NOTE_REQUIRED_MARKERS) + len(CHECKER_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE7_RBTREE_BUILD_WIRING_SELFTEST_GAP_FORBIDDEN_MARKER_COUNT="
        f"{len(CHECKER_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the dedicated Phase 7 leaf-helper checker packet coverage."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path(__file__).resolve().parent

CHECKER_EXPECTATIONS = [
    (
        "scripts/zigux/check-phase7-cmdline-packet.py",
        [
            "--self-test",
            "PHASE7_CMDLINE_PACKET_SELF_TEST=pass",
            "PHASE7_CMDLINE_PACKET=pass",
            'EXPECTED_MANIFEST_LANE_KEY = "P7-L08"',
            'EXPECTED_MANIFEST_ANCHOR = "lib/cmdline.c"',
        ],
    ),
    (
        "scripts/zigux/check-phase7-argv-split-packet.py",
        [
            "--self-test",
            "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass",
            "PHASE7_ARGV_SPLIT_PACKET=pass",
            'EXPECTED_MANIFEST_LANE_KEY = "P7-L09"',
            'EXPECTED_MANIFEST_ANCHOR = "lib/argv_split.c"',
        ],
    ),
    (
        "scripts/zigux/check-phase7-rbtree-parity.py",
        [
            "--self-test",
            "PHASE7_RBTREE_PARITY_SELF_TEST=pass",
            "PHASE7_RBTREE_PARITY=pass",
            'EXPECTED_MANIFEST_LANE_KEY = "P7-L13"',
            'EXPECTED_MANIFEST_ANCHOR = "lib/rbtree.c"',
        ],
    ),
    (
        "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
        [
            "--self-test",
            "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass",
            "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass",
            'Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.',
        ],
    ),
]

SELF_TEST_CASE_COUNT = len(CHECKER_EXPECTATIONS) * 2


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing checker file: {path.as_posix()}") from exc


def validate(repo_root: Path) -> None:
    for rel_path, markers in CHECKER_EXPECTATIONS:
        text = read_text(repo_root / rel_path)
        for marker in markers:
            if marker not in text:
                raise ValidationError(
                    f"missing Phase 7 helper-checker marker in {rel_path}: {marker}"
                )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path, markers in CHECKER_EXPECTATIONS:
        write(root / rel_path, "\n".join(markers) + "\n")


def expect_failure(root: Path, rel_path: str, marker: str, delete_only: bool = False) -> None:
    path = root / rel_path
    if delete_only:
        path.unlink()
    else:
        original = read_text(path)
        updated = original.replace(marker, "", 1)
        if updated == original:
            raise AssertionError(f"marker not found for self-test: {marker}")
        write(path, updated)
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    cases_run = 0
    for rel_path, markers in CHECKER_EXPECTATIONS:
        case_root = Path(tempfile.mkdtemp(prefix="zigux_phase7_checker_coverage_"))
        try:
            scaffold_repo(case_root)
            expect_failure(case_root, rel_path, markers[0], delete_only=False)
            cases_run += 1
        finally:
            for child in sorted(case_root.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            case_root.rmdir()

        case_root = Path(tempfile.mkdtemp(prefix="zigux_phase7_checker_coverage_"))
        try:
            scaffold_repo(case_root)
            expect_failure(case_root, rel_path, "", delete_only=True)
            cases_run += 1
        finally:
            for child in sorted(case_root.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            case_root.rmdir()

    if cases_run != SELF_TEST_CASE_COUNT:
        raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE7_HELPER_CHECKER_COVERAGE_SELF_TEST=pass")
    print(f"PHASE7_HELPER_CHECKER_COVERAGE_SELF_TEST_CASE_COUNT={cases_run}")


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
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_HELPER_CHECKER_COVERAGE=fail: {exc}")
        return 1
    print("PHASE7_HELPER_CHECKER_COVERAGE=pass")
    print(f"PHASE7_HELPER_CHECKER_COUNT={len(CHECKER_EXPECTATIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

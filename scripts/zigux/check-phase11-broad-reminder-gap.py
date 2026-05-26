#!/usr/bin/env python3
"""Fail closed if the current Phase 11 broad-reminder gap stops being described honestly."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
GUIDE_PATH = Path("Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md")

REQUIRED_CONTRACT_MARKERS = (
    "broader contributor-facing summaries in `scripts/zigux/README.md` still skip that active packet",
    "`Documentation/zigux/README.md` still skipping the active Phase 11 packet entirely",
)

REQUIRED_GUIDE_MARKERS = (
    "## Phase 11: Simple-driver packet",
    "`make -C zigux phase11-validate`",
)

FORBIDDEN_DOCS_README_MARKERS = (
    "Phase 11 notes -",
    "## Phase 11",
)

FORBIDDEN_SCRIPTS_README_MARKERS = (
    "## Phase 11",
    "Phase 11 flow -",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path}: {marker}")


def forbid_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker in text:
            raise CheckError(f"unexpected marker in {path}: {marker}")


def run_check(root: Path) -> tuple[int, int, int, int]:
    require_markers(root / CONTRACT_PATH, REQUIRED_CONTRACT_MARKERS)
    require_markers(root / GUIDE_PATH, REQUIRED_GUIDE_MARKERS)
    forbid_markers(root / DOCS_README_PATH, FORBIDDEN_DOCS_README_MARKERS)
    forbid_markers(root / SCRIPTS_README_PATH, FORBIDDEN_SCRIPTS_README_MARKERS)
    return (
        len(REQUIRED_CONTRACT_MARKERS),
        len(REQUIRED_GUIDE_MARKERS),
        len(FORBIDDEN_DOCS_README_MARKERS),
        len(FORBIDDEN_SCRIPTS_README_MARKERS),
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


FIXTURE_CONTRACT_TEXT = """# Phase 11 Shared Replay Contract

Keep the broader reminder follow-through honest too: broader contributor-facing summaries in `scripts/zigux/README.md` still skip that active packet and live current-`master` rereads also show `Documentation/zigux/README.md` still skipping the active Phase 11 packet entirely, so treat those two broad surfaces as the next same-lane reminder follow-through instead of as already current packet members.
"""

FIXTURE_GUIDE_TEXT = """# Phase 10, 11, and 13 Validator-First Review Guide

## Phase 11: Simple-driver packet

- `make -C zigux phase11-validate`
"""

FIXTURE_DOCS_README_TEXT = """# Zigux Documentation

Phase 10 notes -
"""

FIXTURE_SCRIPTS_README_TEXT = """# scripts/zigux

## Phase 10

- current shared closure packet
"""


def build_fixture(root: Path) -> None:
    write(root / CONTRACT_PATH, FIXTURE_CONTRACT_TEXT)
    write(root / GUIDE_PATH, FIXTURE_GUIDE_TEXT)
    write(root / DOCS_README_PATH, FIXTURE_DOCS_README_TEXT)
    write(root / SCRIPTS_README_PATH, FIXTURE_SCRIPTS_README_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_broad_reminder_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_contract_marker = tmpdir / "missing_contract_marker"
        shutil.copytree(fixture, missing_contract_marker, dirs_exist_ok=True)
        write(
            missing_contract_marker / CONTRACT_PATH,
            read_text(missing_contract_marker / CONTRACT_PATH).replace(
                "active Phase 11 packet entirely",
                "",
                1,
            ),
        )
        expect_failure(missing_contract_marker, "Documentation/zigux/README.md")
        case_count += 1

        missing_guide_marker = tmpdir / "missing_guide_marker"
        shutil.copytree(fixture, missing_guide_marker, dirs_exist_ok=True)
        write(
            missing_guide_marker / GUIDE_PATH,
            read_text(missing_guide_marker / GUIDE_PATH).replace(
                "## Phase 11: Simple-driver packet",
                "",
                1,
            ),
        )
        expect_failure(missing_guide_marker, "## Phase 11: Simple-driver packet")
        case_count += 1

        docs_readme_claims_phase11 = tmpdir / "docs_readme_claims_phase11"
        shutil.copytree(fixture, docs_readme_claims_phase11, dirs_exist_ok=True)
        write(
            docs_readme_claims_phase11 / DOCS_README_PATH,
            read_text(docs_readme_claims_phase11 / DOCS_README_PATH) + "Phase 11 notes -\n",
        )
        expect_failure(docs_readme_claims_phase11, "unexpected marker")
        case_count += 1

        scripts_readme_claims_phase11 = tmpdir / "scripts_readme_claims_phase11"
        shutil.copytree(fixture, scripts_readme_claims_phase11, dirs_exist_ok=True)
        write(
            scripts_readme_claims_phase11 / SCRIPTS_README_PATH,
            read_text(scripts_readme_claims_phase11 / SCRIPTS_README_PATH) + "## Phase 11\n",
        )
        expect_failure(scripts_readme_claims_phase11, "unexpected marker")
        case_count += 1

        print("PHASE11_BROAD_REMINDER_GAP_SELF_TEST=pass")
        print(f"PHASE11_BROAD_REMINDER_GAP_SELF_TEST_CASES={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed if the current Phase 11 broad-reminder gap drifts."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    contract_count, guide_count, docs_absent_count, scripts_absent_count = run_check(
        args.root
    )
    print("PHASE11_BROAD_REMINDER_GAP=pass")
    print(f"PHASE11_BROAD_REMINDER_GAP_CONTRACT_MARKERS={contract_count}")
    print(f"PHASE11_BROAD_REMINDER_GAP_GUIDE_MARKERS={guide_count}")
    print(f"PHASE11_BROAD_REMINDER_GAP_DOCS_ABSENT_MARKERS={docs_absent_count}")
    print(f"PHASE11_BROAD_REMINDER_GAP_SCRIPTS_ABSENT_MARKERS={scripts_absent_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

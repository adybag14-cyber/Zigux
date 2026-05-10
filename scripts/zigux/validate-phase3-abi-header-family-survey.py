#!/usr/bin/env python3
"""Fail closed on the shipped Phase 3 header-family survey route."""

from __future__ import annotations

import argparse
import shutil
import tempfile
import textwrap
from pathlib import Path


DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")

SCRIPT_NAME = "validate-phase3-abi-header-family-survey.py"
SCRIPT_REL = f"scripts/zigux/{SCRIPT_NAME}"
GOVERNANCE_NOTE = "Documentation/zigux/phase3-linux-zigux-header-governance.md"

MAKEFILE_REQUIRED_COMMANDS = (
    f"cd $(ZIGUX_ROOT) && $(PYTHON) {SCRIPT_REL}",
    f"cd $(ZIGUX_ROOT) && $(PYTHON) {SCRIPT_REL} --self-test",
)

DOCS_REQUIRED_MARKERS = (
    f"`{GOVERNANCE_NOTE}`",
    f"`{SCRIPT_REL}`",
)

SCRIPTS_REQUIRED_MARKERS = (
    f"`{SCRIPT_NAME}`",
    "header-family survey",
)

SELF_TEST_CASES = (
    "baseline_round_trip",
    "missing_docs_marker",
    "missing_scripts_marker",
    "missing_makefile_command",
    "duplicate_makefile_command",
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            raise CheckError(f"missing {label} marker: {marker}")
        if count != 1:
            raise CheckError(f"unexpected {label} marker count {count}: {marker}")


def validate_makefile(makefile_text: str) -> None:
    lines = [line.strip() for line in makefile_text.splitlines()]
    for command in MAKEFILE_REQUIRED_COMMANDS:
        count = sum(1 for line in lines if line == command)
        if count == 0:
            raise CheckError(f"missing Makefile command: {command}")
        if count != 1:
            raise CheckError(f"unexpected Makefile command count {count}: {command}")


def validate_repo(root: Path) -> None:
    docs_readme = read_text(root, DOCS_README_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    makefile = read_text(root, MAKEFILE_PATH)

    require_markers(docs_readme, DOCS_REQUIRED_MARKERS, "docs README")
    require_markers(scripts_readme, SCRIPTS_REQUIRED_MARKERS, "scripts README")
    validate_makefile(makefile)


def build_self_test_repo(root: Path) -> None:
    write_text(
        root / DOCS_README_PATH,
        f"""
        # Zigux Documentation

        - `{GOVERNANCE_NOTE}`
        - `{SCRIPT_REL}`
        """,
    )
    write_text(
        root / SCRIPTS_README_PATH,
        f"""
        # scripts/zigux

        - `{SCRIPT_NAME}`

        Phase 3 flow
        - `make -C zigux phase3-validate` keeps the header-family survey wired into the shared validation route.
        """,
    )
    write_text(
        root / MAKEFILE_PATH,
        f"""
        phase3-validate:
        \t{MAKEFILE_REQUIRED_COMMANDS[0]}
        \t{MAKEFILE_REQUIRED_COMMANDS[1]}
        """,
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        validate_repo(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise CheckError(
                f"expected self-test failure containing {expected_fragment!r}, got: {exc}"
            ) from exc
        return
    raise CheckError("expected self-test mutation to fail closed")


def run_self_test() -> None:
    tempdir = Path(tempfile.mkdtemp(prefix="phase3-header-family-survey-"))
    try:
        build_self_test_repo(tempdir)
        validate_repo(tempdir)

        missing_docs = tempdir / "missing-docs"
        shutil.copytree(tempdir, missing_docs)
        write_text(
            missing_docs / DOCS_README_PATH,
            f"""
            # Zigux Documentation

            - `{SCRIPT_REL}`
            """,
        )
        expect_failure(missing_docs, "missing docs README marker")

        missing_scripts = tempdir / "missing-scripts"
        shutil.copytree(tempdir, missing_scripts)
        write_text(
            missing_scripts / SCRIPTS_README_PATH,
            """
            # scripts/zigux

            Phase 3 flow
            - `make -C zigux phase3-validate` keeps the shared validation route wired.
            """,
        )
        expect_failure(missing_scripts, "missing scripts README marker")

        missing_makefile = tempdir / "missing-makefile"
        shutil.copytree(tempdir, missing_makefile)
        write_text(
            missing_makefile / MAKEFILE_PATH,
            f"""
            phase3-validate:
            \t{MAKEFILE_REQUIRED_COMMANDS[1]}
            """,
        )
        expect_failure(missing_makefile, "missing Makefile command")

        duplicate_makefile = tempdir / "duplicate-makefile"
        shutil.copytree(tempdir, duplicate_makefile)
        write_text(
            duplicate_makefile / MAKEFILE_PATH,
            f"""
            phase3-validate:
            \t{MAKEFILE_REQUIRED_COMMANDS[0]}
            \t{MAKEFILE_REQUIRED_COMMANDS[0]}
            \t{MAKEFILE_REQUIRED_COMMANDS[1]}
            """,
        )
        expect_failure(duplicate_makefile, "unexpected Makefile command count")

        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")
        print(
            "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT="
            f"{len(SELF_TEST_CASES)}"
        )
        print(
            "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASES="
            + ",".join(SELF_TEST_CASES)
        )
    finally:
        shutil.rmtree(tempdir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shipped Phase 3 header-family survey route honest."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("root", nargs="?")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    repo_root = Path(args.root).resolve() if args.root else Path.cwd()
    validate_repo(repo_root)
    print("PHASE3_ABI_HEADER_FAMILY_SURVEY=pass")
    print(f"PHASE3_ABI_HEADER_FAMILY_SURVEY_SCRIPT={SCRIPT_REL}")
    print(f"PHASE3_ABI_HEADER_FAMILY_SURVEY_GOVERNANCE_NOTE={GOVERNANCE_NOTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

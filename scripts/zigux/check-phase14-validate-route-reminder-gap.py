#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=validate_route_reminder_gap

Fail-closed checker for the bounded Phase 14 reminder drift around the shipped
`phase14-validate` route.

This checker proves one narrow current-master gap: the Makefile and shared smoke
route checker already expose `phase14-validate`, while selected reminder
surfaces still describe that route as absent.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=validate_route_reminder_gap"
GAP_NOTE_PATH = Path("Documentation/zigux/phase14-validate-route-reminder-gap.md")
MAKEFILE_PATH = Path("zigux/Makefile")
ROUTE_CHECKER_PATH = Path("scripts/zigux/check-phase14-shared-smoke-route.py")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

REQUIRED_FILES = (
    GAP_NOTE_PATH,
    MAKEFILE_PATH,
    ROUTE_CHECKER_PATH,
    TESTS_README_PATH,
    SCRIPTS_README_PATH,
    CHECKLIST_PATH,
)

NOTE_MARKERS = (
    "- `zigux/Makefile` now ships `phase14-validate`",
    "- `scripts/zigux/check-phase14-shared-smoke-route.py` already fail-closes on that dedicated `phase14-validate` route and still rejects `phase14-smoke` and `phase14-test` as active workflow proof",
    "- `zigux/tests/README.md` still says the readable Makefile has no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "- `scripts/zigux/README.md` still says there are no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "- `Documentation/zigux/review-checklist.md` still frames `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` together as packet-local or repo-reality-gap vocabulary",
)

MAKEFILE_MARKERS = (
    "phase14-validate:",
    "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "scripts/zigux/check-phase14-shared-smoke-route.py",
    "scripts/zigux/validate-phase14.py --self-test",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
)

ROUTE_CHECKER_MARKERS = (
    "phase14-validate",
    "run: make -C zigux phase14-validate",
)

TESTS_README_MARKERS = (
    "and no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
)

SCRIPTS_README_MARKERS = (
    "there are still no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets",
)

CHECKLIST_MARKERS = (
    "while `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(errors, GAP_NOTE_PATH, read_text(root, GAP_NOTE_PATH), NOTE_MARKERS)
    require_markers(errors, MAKEFILE_PATH, read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS)
    require_markers(errors, ROUTE_CHECKER_PATH, read_text(root, ROUTE_CHECKER_PATH), ROUTE_CHECKER_MARKERS)
    require_markers(errors, TESTS_README_PATH, read_text(root, TESTS_README_PATH), TESTS_README_MARKERS)
    require_markers(errors, SCRIPTS_README_PATH, read_text(root, SCRIPTS_README_PATH), SCRIPTS_README_MARKERS)
    require_markers(errors, CHECKLIST_PATH, read_text(root, CHECKLIST_PATH), CHECKLIST_MARKERS)
    return errors


def fixture_gap_note() -> str:
    return "# Phase 14 Validate-Route Reminder Gap\n\n" + "\n".join(NOTE_MARKERS) + "\n"


def fixture_makefile() -> str:
    return """PYTHON ?= python3
ZIGUX_ROOT := ..

.PHONY: phase14-validate

phase14-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
"""


def fixture_route_checker() -> str:
    return """#!/usr/bin/env python3
PHASE14_CHECK_PACKET=shared_smoke_route
phase14-validate
run: make -C zigux phase14-validate
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, GAP_NOTE_PATH, fixture_gap_note())
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, ROUTE_CHECKER_PATH, fixture_route_checker())
    write_text(root, TESTS_README_PATH, TESTS_README_MARKERS[0] + "\n")
    write_text(root, SCRIPTS_README_PATH, SCRIPTS_README_MARKERS[0] + "\n")
    write_text(root, CHECKLIST_PATH, CHECKLIST_MARKERS[0] + "\n")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-validate-route-gap-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile().replace("phase14-validate:", "phase14-validate-missing:", 1),
        )
        if not any("phase14-validate:" in error for error in check(base)):
            print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_SELF_TEST=fail")
            print("expected missing makefile target marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            TESTS_README_PATH,
            "current `master` exposes `phase14-validate` directly now\n",
        )
        if not any(TESTS_README_MARKERS[0] in error for error in check(base)):
            print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_SELF_TEST=fail")
            print("expected stale tests-readme marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            GAP_NOTE_PATH,
            fixture_gap_note().replace("`zigux/Makefile` now ships `phase14-validate`", "`zigux/Makefile` route changed"),
        )
        if not any(NOTE_MARKERS[0] in error for error in check(base)):
            print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_SELF_TEST=fail")
            print("expected gap-note marker failure")
            return 1

        print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_SELF_TEST=pass")
        print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_SELF_TEST_CASE_COUNT=3")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP=fail")
        print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP_ISSUES_END")
        return 1

    print("PHASE14_VALIDATE_ROUTE_REMINDER_GAP=pass")
    print(f"PHASE14_VALIDATE_ROUTE_REMINDER_GAP_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

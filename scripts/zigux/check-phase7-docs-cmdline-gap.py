#!/usr/bin/env python3
"""Check the live Phase 7 docs-root reminder gap around the shipped cmdline guard."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
CMDLINE_GUARD = "scripts/zigux/check-phase7-cmdline-packet.py"
PHASE7_MARKER = "Phase 7"
EXPECTED_DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "scripts/zigux/check-phase7-shared-surface.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "scripts/zigux/validate-phase7.py",
]

SELF_TEST_CASE_COUNT = 6


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise ValidationError(f"missing expected marker in {label}: {needle}")


def require_absent(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise ValidationError(f"unexpected marker in {label}: {needle}")


def validate(repo_root: Path) -> None:
    docs_readme = read_text(repo_root / DOCS_README_PATH)
    review_checklist = read_text(repo_root / REVIEW_CHECKLIST_PATH)

    require_contains(docs_readme, PHASE7_MARKER, DOCS_README_PATH.as_posix())
    require_contains(review_checklist, PHASE7_MARKER, REVIEW_CHECKLIST_PATH.as_posix())

    for marker in EXPECTED_DOCS_ROOT_MARKERS:
        require_contains(docs_readme, marker, DOCS_README_PATH.as_posix())
        require_contains(review_checklist, marker, REVIEW_CHECKLIST_PATH.as_posix())

    require_absent(docs_readme, CMDLINE_GUARD, DOCS_README_PATH.as_posix())
    require_absent(review_checklist, CMDLINE_GUARD, REVIEW_CHECKLIST_PATH.as_posix())


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_docs() -> str:
    return "\n".join(
        [
            "# Fixture",
            PHASE7_MARKER,
            *EXPECTED_DOCS_ROOT_MARKERS,
            "lib/cmdline.zig",
        ]
    ) + "\n"


def expect_failure(root: Path, rel: Path, mutate) -> None:
    path = root / rel
    original = read_text(path)
    write(path, mutate(original))
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_docs_cmdline_gap_") as tmpdir:
        root = Path(tmpdir)
        write(root / DOCS_README_PATH, fixture_docs())
        write(root / REVIEW_CHECKLIST_PATH, fixture_docs())
        validate(root)

        mutations = [
            (DOCS_README_PATH, lambda text: text.replace(PHASE7_MARKER, "Phase Seven", 1)),
            (REVIEW_CHECKLIST_PATH, lambda text: text.replace(PHASE7_MARKER, "Phase Seven", 1)),
            (DOCS_README_PATH, lambda text: text.replace(EXPECTED_DOCS_ROOT_MARKERS[1], "scripts/zigux/check-phase7-missing.py", 1)),
            (REVIEW_CHECKLIST_PATH, lambda text: text.replace(EXPECTED_DOCS_ROOT_MARKERS[3], "scripts/zigux/check-phase7-missing.py", 1)),
            (DOCS_README_PATH, lambda text: text + CMDLINE_GUARD + "\n"),
            (REVIEW_CHECKLIST_PATH, lambda text: text + CMDLINE_GUARD + "\n"),
        ]

        for rel, mutate in mutations:
            write(root / DOCS_README_PATH, fixture_docs())
            write(root / REVIEW_CHECKLIST_PATH, fixture_docs())
            expect_failure(root, rel, mutate)
            cases += 1

    if cases != SELF_TEST_CASE_COUNT:
        raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases}")
    print("PHASE7_DOCS_CMDLINE_GAP_SELF_TEST=pass")
    print(f"PHASE7_DOCS_CMDLINE_GAP_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 7 docs-root reminder still records the shipped cmdline guard as a live gap."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_DOCS_CMDLINE_GAP=fail: {exc}")
        return 1

    print("PHASE7_DOCS_CMDLINE_GAP=pass")
    print(f"PHASE7_DOCS_CMDLINE_GAP_REQUIRED_MARKER_COUNT={len(EXPECTED_DOCS_ROOT_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

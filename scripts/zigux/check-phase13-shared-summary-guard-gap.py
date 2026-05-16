#!/usr/bin/env python3
"""Guard the current Phase 13 shared-summary missing-checker gap."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-shared-summary-guard-gap.md": [
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-release-coordination-matrix.md`",
        "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
        "`python3 scripts/zigux/validate-phase13-release.py`",
        "blocked convenience route `make -C zigux phase13`",
    ],
    "Documentation/zigux/phase13-contributor-workflow-guide.md": [
        "`scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "repo-reality gaps stay explicit instead of being promoted into shipped current-`master` evidence",
    ],
    "Documentation/zigux/phase13-release-coordination-matrix.md": [
        "shared-summary guard gap: `scripts/zigux/check-phase13-shared-summary-surfaces.py` is still absent on current `master`",
        "Keep only `scripts/zigux/check-phase13-shared-summary-surfaces.py` recorded as a shared-summary repo-reality gap",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "the dedicated shared-summary guard `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "blocked `make -C zigux phase13` convenience-route wording in `zigux/Makefile`",
    ],
}

ABSENT_PATHS = [
    "scripts/zigux/check-phase13-shared-summary-surfaces.py",
]


def read_text(root: Path, relpath: str) -> str:
    return (root / relpath).read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    for relpath, markers in REQUIRED_MARKERS.items():
        path = root / relpath
        if not path.exists():
            errors.append(f"missing_file:{relpath}")
            continue
        text = read_text(root, relpath)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing_marker:{relpath}:{marker}")

    for relpath in ABSENT_PATHS:
        if (root / relpath).exists():
            errors.append(f"unexpected_present:{relpath}")

    return errors


def populate_repo(root: Path) -> None:
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-shared-summary-guard-gap-"))
    case_count = 0
    try:
        populate_repo(tempdir)
        assert_only(validate(tempdir), [], "baseline")
        case_count += 1

        write_text(
            tempdir,
            "scripts/zigux/check-phase13-shared-summary-surfaces.py",
            "# placeholder\n",
        )
        assert_only(
            validate(tempdir),
            ["unexpected_present:scripts/zigux/check-phase13-shared-summary-surfaces.py"],
            "unexpected_present",
        )
        (tempdir / "scripts/zigux/check-phase13-shared-summary-surfaces.py").unlink()
        case_count += 1

        write_text(
            tempdir,
            "Documentation/zigux/phase13-release-coordination-matrix.md",
            "shared replay handle only\n",
        )
        assert_only(
            validate(tempdir),
            [
                "missing_marker:Documentation/zigux/phase13-release-coordination-matrix.md:shared-summary guard gap: `scripts/zigux/check-phase13-shared-summary-surfaces.py` is still absent on current `master`",
                "missing_marker:Documentation/zigux/phase13-release-coordination-matrix.md:Keep only `scripts/zigux/check-phase13-shared-summary-surfaces.py` recorded as a shared-summary repo-reality gap",
            ],
            "missing_release_matrix_markers",
        )
        populate_repo(tempdir)
        case_count += 1

        write_text(
            tempdir,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "blocked `make -C zigux phase13` convenience-route wording in `zigux/Makefile`\n",
        )
        assert_only(
            validate(tempdir),
            [
                "missing_marker:Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:the dedicated shared-summary guard `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
            ],
            "missing_tests_root_guard_marker",
        )
        case_count += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_SHARED_SUMMARY_GUARD_GAP_SELF_TEST=pass")
    print(f"PHASE13_SHARED_SUMMARY_GUARD_GAP_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(Path(args.repo_root))
    if errors:
        for error in errors:
            print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

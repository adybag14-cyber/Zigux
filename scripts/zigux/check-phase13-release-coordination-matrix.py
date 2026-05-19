#!/usr/bin/env python3
"""Guard the current Phase 13 release-coordination matrix packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MATRIX_PATH = "Documentation/zigux/phase13-release-coordination-matrix.md"
RELEASE_NOTES_PATH = "Documentation/zigux/phase13-release-notes-survey.md"
TRACEABILITY_PATH = "Documentation/zigux/phase13-roadmap-traceability.md"
WORKFLOW_GUIDE_PATH = "Documentation/zigux/phase13-contributor-workflow-guide.md"
DOCS_ROOT_PATH = "Documentation/zigux/README.md"
SCRIPTS_ROOT_PATH = "scripts/zigux/README.md"
TESTS_ROOT_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_MARKERS = {
    MATRIX_PATH: [
        "This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.",
        "- shared-summary owner: `PMO / Release Management`",
        "- shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "- tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`",
        "Keep the stable contributor-facing handle distinct from this PMO coordination companion:",
        "4. `Documentation/zigux/phase13-release-coordination-matrix.md`",
        "- `make -C zigux phase13-validate`",
        "- `make -C zigux phase13`",
        "- `scripts/zigux/validate-phase13-release.py`",
        "- `scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "- `scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "This matrix does not close the Phase 13 tranche.",
    ],
    RELEASE_NOTES_PATH: [
        "`Documentation/zigux/phase13-release-coordination-matrix.md`",
        "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces:",
        "Keep broad release wording tied to that reminder packet while the missing validator-first helpers and missing shared build route surfaces remain explicit repo-reality gaps.",
    ],
    TRACEABILITY_PATH: [
        "`Documentation/zigux/phase13-release-coordination-matrix.md`",
        "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface, and keep the returned `zigux/Makefile` file distinct from the still-missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` names",
    ],
    WORKFLOW_GUIDE_PATH: [
        "Keep `Documentation/zigux/phase13-release-coordination-matrix.md` and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` aligned as supporting shared reminder surfaces rather than as the stable contributor-facing handle itself.",
        "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
    ],
    DOCS_ROOT_PATH: [
        "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
        "- `Documentation/zigux/phase13-release-notes-survey.md`",
        "- `Documentation/zigux/phase13-roadmap-traceability.md`",
    ],
    SCRIPTS_ROOT_PATH: [
        "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
        "Phase 13 flow - the current scripts-root shared-helper packet stays reviewable through the stable contributor-facing handle, the shipped shared-summary guard, the tests-root alignment companion, the shipped helper-local `libfs`, `devres`, and Landlock packet anchors, and the adjacent notifier evidence",
        "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the route names recorded as repo-reality gaps instead of promoting the returned file into a shipped shared build handle",
    ],
    TESTS_ROOT_PATH: [
        "- `Documentation/zigux/phase13-release-coordination-matrix.md`",
        "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:",
        "Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.",
    ],
}

GAP_PATHS = (
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet-alignment.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "scripts/zigux/check-phase13-notifier-priority-signal.py",
)

FORBIDDEN_MARKERS = (
    "This matrix does close the Phase 13 tranche.",
    "a shipped Makefile-backed review handle",
    "Current `master` now exposes `make -C zigux phase13-validate`",
)


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise FileNotFoundError(relpath)
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for relpath, markers in REQUIRED_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except FileNotFoundError:
            issues.append(f"missing_file:{relpath}")
            continue

        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{relpath}:{marker}")

        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                issues.append(f"forbidden_marker:{relpath}:{marker}")

    try:
        makefile_text = read_text(root, MAKEFILE_PATH)
    except FileNotFoundError:
        issues.append(f"missing_file:{MAKEFILE_PATH}")
        makefile_text = ""

    for route in ("phase13-validate:", "phase13:"):
        if route in makefile_text:
            issues.append(f"unexpected_route:{route}")

    for relpath in GAP_PATHS:
        if (root / relpath).exists():
            issues.append(f"unexpected_returned_gap:{relpath}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_RELEASE_COORDINATION_MATRIX=fail")
    print("PHASE13_RELEASE_COORDINATION_MATRIX_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_RELEASE_COORDINATION_MATRIX_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")

    write_text(
        root,
        MAKEFILE_PATH,
        "PYTHON ?= python3\n.PHONY: phase2 phase3 phase4 phase6 phase8 phase10 phase12\n",
    )


def expect_issue(issues: list[str], expected: str) -> None:
    if expected not in issues:
        raise AssertionError(f"missing expected issue: {expected}")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-release-coordination-matrix-"))
    case_count = 0
    try:
        populate_repo(tempdir)
        if collect_issues(tempdir) != []:
            raise AssertionError("baseline fixture should pass")
        case_count += 1

        broken = tempdir / "missing_matrix_marker"
        populate_repo(broken)
        write_text(
            broken,
            MATRIX_PATH,
            read_text(broken, MATRIX_PATH).replace(
                "- `scripts/zigux/validate-phase13-release.py`\n",
                "",
                1,
            ),
        )
        expect_issue(
            collect_issues(broken),
            "missing_marker:Documentation/zigux/phase13-release-coordination-matrix.md:- `scripts/zigux/validate-phase13-release.py`",
        )
        case_count += 1

        returned_gap = tempdir / "returned_gap"
        populate_repo(returned_gap)
        write_text(returned_gap, "scripts/zigux/validate-phase13-release.py", "present\n")
        expect_issue(
            collect_issues(returned_gap),
            "unexpected_returned_gap:scripts/zigux/validate-phase13-release.py",
        )
        case_count += 1

        makefile_route = tempdir / "makefile_route"
        populate_repo(makefile_route)
        write_text(makefile_route, MAKEFILE_PATH, "phase13-validate:\n\t@true\n")
        expect_issue(
            collect_issues(makefile_route),
            "unexpected_route:phase13-validate:",
        )
        case_count += 1

        missing_release_notes = tempdir / "missing_release_notes"
        populate_repo(missing_release_notes)
        write_text(
            missing_release_notes,
            RELEASE_NOTES_PATH,
            read_text(missing_release_notes, RELEASE_NOTES_PATH).replace(
                "`Documentation/zigux/phase13-release-coordination-matrix.md`\n",
                "",
                1,
            ),
        )
        expect_issue(
            collect_issues(missing_release_notes),
            "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:`Documentation/zigux/phase13-release-coordination-matrix.md`",
        )
        case_count += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_RELEASE_COORDINATION_MATRIX_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_COORDINATION_MATRIX_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 13 PMO release-coordination matrix packet aligned with its coupled reminder surfaces."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_RELEASE_COORDINATION_MATRIX=pass")
    print(f"PHASE13_RELEASE_COORDINATION_MATRIX_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

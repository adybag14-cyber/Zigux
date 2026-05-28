#!/usr/bin/env python3
"""Guard the current Phase 13 release-packet index note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


INDEX_PATH = "Documentation/zigux/phase13-release-packet-index.md"
MATRIX_PATH = "Documentation/zigux/phase13-release-coordination-matrix.md"
NOTES_PATH = "Documentation/zigux/phase13-release-notes-survey.md"
TRACEABILITY_PATH = "Documentation/zigux/phase13-roadmap-traceability.md"
HANDOFF_PATH = "Documentation/zigux/phase12-phase13-release-handoff.md"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_MARKERS = {
    INDEX_PATH: [
        "This note is the compact PMO packet index for the active Phase 13 shared-helper release packet.",
        "- lane owner: `pmo-release`",
        "- `Documentation/zigux/phase13-release-packet-index.md`",
        "- `scripts/zigux/check-phase13-roadmap-traceability.py`",
        "- `scripts/zigux/validate-phase13-release.py`",
        "No shared Phase 13 build handle is returned on current `master`.",
        "- `make -C zigux phase13-validate`",
        "- `make -C zigux phase13`",
        "- `zigux/tests/phase13_build.zig`",
        "This index is a coordination artifact, not a closure claim.",
        "then land only the smallest reminder-side truthfulness repair and rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, `python3 scripts/zigux/check-phase13-roadmap-traceability.py`, and `python3 scripts/zigux/validate-phase13-release.py`.",
    ],
    MATRIX_PATH: [
        "release-packet index companion: `Documentation/zigux/phase13-release-packet-index.md`",
        "4. `Documentation/zigux/phase13-release-packet-index.md`",
    ],
    NOTES_PATH: [
        "`Documentation/zigux/phase13-release-packet-index.md`",
        "The release-planning handle that is directly supportable from this run stays anchored to the materialized reminder surfaces and their active shared companions:",
    ],
    TRACEABILITY_PATH: [
        "Current `master` also now materializes `scripts/zigux/check-phase13-roadmap-traceability.py`, so keep that checker explicit as the note-level guard for this roadmap-to-repo owner map rather than treating traceability as a reminder-only surface with no dedicated replay.",
    ],
    HANDOFF_PATH: [
        "- Phase 13 destination companions: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`",
        "2. Reread the Phase 13 destination packet next through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `scripts/zigux/check-phase13-tests-readme-alignment.py`.",
    ],
}

FORBIDDEN_MARKERS = {
    INDEX_PATH: [
        "This index does close the Phase 13 tranche.",
        "This index does imply a shipped shared Makefile route for Phase 13.",
    ],
}

EXPECTED_GAPS = (
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
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

        for marker in FORBIDDEN_MARKERS.get(relpath, ()):
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

    for gap_path in EXPECTED_GAPS:
        if (root / gap_path).exists():
            issues.append(f"unexpected_returned_gap:{gap_path}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_RELEASE_PACKET_INDEX=fail")
    print("PHASE13_RELEASE_PACKET_INDEX_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_RELEASE_PACKET_INDEX_ISSUES_END")
    return 1


def populate_fixture(root: Path) -> None:
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")

    write_text(
        root,
        MAKEFILE_PATH,
        "PYTHON ?= python3\n.PHONY: phase2 phase3 phase7 phase8 phase10 phase12 phase14\n",
    )


def expect_issue(issues: list[str], expected: str) -> None:
    if expected not in issues:
        raise AssertionError(f"missing expected issue: {expected}")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-release-packet-index-"))
    case_count = 0
    try:
        populate_fixture(tempdir)
        if collect_issues(tempdir) != []:
            raise AssertionError("baseline fixture should pass")
        case_count += 1

        missing_marker = tempdir / "missing_marker"
        populate_fixture(missing_marker)
        write_text(
            missing_marker,
            INDEX_PATH,
            read_text(missing_marker, INDEX_PATH).replace(
                "- `scripts/zigux/check-phase13-roadmap-traceability.py`\n",
                "",
                1,
            ),
        )
        expect_issue(
            collect_issues(missing_marker),
            "missing_marker:Documentation/zigux/phase13-release-packet-index.md:- `scripts/zigux/check-phase13-roadmap-traceability.py`",
        )
        case_count += 1

        missing_handoff = tempdir / "missing_handoff"
        populate_fixture(missing_handoff)
        write_text(
            missing_handoff,
            HANDOFF_PATH,
            read_text(missing_handoff, HANDOFF_PATH).replace(
                "`Documentation/zigux/phase13-release-packet-index.md`",
                "`Documentation/zigux/phase13-release-index.md`",
                1,
            ),
        )
        expect_issue(
            collect_issues(missing_handoff),
            "missing_marker:Documentation/zigux/phase12-phase13-release-handoff.md:- Phase 13 destination companions: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`",
        )
        case_count += 1

        returned_route = tempdir / "returned_route"
        populate_fixture(returned_route)
        write_text(returned_route, MAKEFILE_PATH, "phase13-validate:\n\t@true\n")
        expect_issue(
            collect_issues(returned_route),
            "unexpected_route:phase13-validate:",
        )
        case_count += 1

        returned_gap = tempdir / "returned_gap"
        populate_fixture(returned_gap)
        write_text(returned_gap, "zigux/tests/phase13_build.zig", "// present\n")
        expect_issue(
            collect_issues(returned_gap),
            "unexpected_returned_gap:zigux/tests/phase13_build.zig",
        )
        case_count += 1

        forbidden = tempdir / "forbidden"
        populate_fixture(forbidden)
        write_text(
            forbidden,
            INDEX_PATH,
            read_text(forbidden, INDEX_PATH)
            + "This index does imply a shipped shared Makefile route for Phase 13.\n",
        )
        expect_issue(
            collect_issues(forbidden),
            "forbidden_marker:Documentation/zigux/phase13-release-packet-index.md:This index does imply a shipped shared Makefile route for Phase 13.",
        )
        case_count += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_RELEASE_PACKET_INDEX_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_PACKET_INDEX_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 13 PMO release-packet index aligned with its coupled reminder surfaces."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_RELEASE_PACKET_INDEX=pass")
    print(f"PHASE13_RELEASE_PACKET_INDEX_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE13_RELEASE_PACKET_INDEX_GAP_COUNT={len(EXPECTED_GAPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
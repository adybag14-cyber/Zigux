#!/usr/bin/env python3
"""Fail closed on the shared Phase 13 Landlock ruleset packet surface."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase13-landlock-ruleset-packet.py"
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
CONTRIBUTOR_GUIDE_PATH = "Documentation/zigux/phase13-contributor-workflow-guide.md"
RELEASE_NOTES_PATH = "Documentation/zigux/phase13-release-notes-survey.md"
NOTIFIER_SURVEY_PATH = "Documentation/zigux/phase13-notifier-list-survey.md"
SYSCALLS_GOVERNANCE_PATH = "Documentation/zigux/phase13-landlock-syscalls-governance.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
LANE_NOTE_PATH = "Documentation/zigux/phase13-shared-helper-lane-sequencing.md"
TRACEABILITY_PATH = "Documentation/zigux/phase13-roadmap-traceability.md"
OWNERSHIP_PATH = "Documentation/zigux/phase13-landlock-ruleset-ownership.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase13-release.py"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_FILES = (
    SCRIPT_PATH,
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    CONTRIBUTOR_GUIDE_PATH,
    RELEASE_NOTES_PATH,
    NOTIFIER_SURVEY_PATH,
    SYSCALLS_GOVERNANCE_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    LANE_NOTE_PATH,
    TRACEABILITY_PATH,
    OWNERSHIP_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
)

REQUIRED_DOCS_README_MARKERS = (
    "Phase 13 notes - `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`scripts/zigux/validate-phase13-release.py`",
    "`make -C zigux phase13-validate`",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 13 release packet",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "`scripts/zigux/validate-phase13-release.py`",
)

REQUIRED_CONTRIBUTOR_GUIDE_MARKERS = (
    "Use this guide when a change touches the active Phase 13 shared-helper packet",
    "## Current Repo Reality",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "`make -C zigux phase13-validate`",
)

REQUIRED_RELEASE_NOTES_MARKERS = (
    "Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through:",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`security/landlock/ruleset.zig`",
    "`security/landlock/syscalls.zig`",
)

REQUIRED_NOTIFIER_SURVEY_MARKERS = (
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "`Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "paired Landlock",
)

REQUIRED_SYSCALLS_GOVERNANCE_MARKERS = (
    "# Phase 13 Landlock Syscalls Governance",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`scripts/zigux/validate-phase13-release.py`",
    "`make -C zigux phase13-validate`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "- `check-phase13-landlock-ruleset-packet.py`",
    "Phase 13 flow -",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`make -C zigux phase13-validate`",
)

REQUIRED_TESTS_README_MARKERS = (
    "keep the shared Phase 13 contributor-workflow packet explicit in the tests root too:",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "`scripts/zigux/validate-phase13-release.py`",
    "`make -C zigux phase13-validate`",
)

REQUIRED_LANE_NOTE_MARKERS = (
    "# Phase 13 Shared Helper Lane Sequencing",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "repo reality",
    "`make -C zigux phase13-validate`",
)

REQUIRED_TRACEABILITY_MARKERS = (
    "# Phase 13 Roadmap Traceability",
    "`landlock/ruleset` maps to the bounded shared-helper tranche and should keep its ownership boundary explicit.",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "repo-reality gaps rather than presenting them here as shipped repo evidence.",
    "`make -C zigux phase13-validate`",
)

REQUIRED_OWNERSHIP_MARKERS = (
    "# Phase 13 Landlock Ruleset Ownership Note",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`make -C zigux phase13-validate`",
    "repo-reality gaps",
)

REQUIRED_VALIDATOR_MARKERS = (
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "the current eight-test shared-helper release packet",
)

REQUIRED_MAKEFILE_MARKERS = (
    "phase13-validate:",
    "$(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    checks = (
        ("docs-readme", DOCS_README_PATH, REQUIRED_DOCS_README_MARKERS),
        ("review-checklist", REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_MARKERS),
        ("contributor-guide", CONTRIBUTOR_GUIDE_PATH, REQUIRED_CONTRIBUTOR_GUIDE_MARKERS),
        ("release-notes", RELEASE_NOTES_PATH, REQUIRED_RELEASE_NOTES_MARKERS),
        ("notifier-survey", NOTIFIER_SURVEY_PATH, REQUIRED_NOTIFIER_SURVEY_MARKERS),
        ("syscalls-governance", SYSCALLS_GOVERNANCE_PATH, REQUIRED_SYSCALLS_GOVERNANCE_MARKERS),
        ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS),
        ("tests-readme", TESTS_README_PATH, REQUIRED_TESTS_README_MARKERS),
        ("lane-note", LANE_NOTE_PATH, REQUIRED_LANE_NOTE_MARKERS),
        ("traceability", TRACEABILITY_PATH, REQUIRED_TRACEABILITY_MARKERS),
        ("ownership", OWNERSHIP_PATH, REQUIRED_OWNERSHIP_MARKERS),
        ("validator", VALIDATOR_PATH, REQUIRED_VALIDATOR_MARKERS),
        ("makefile", MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS),
    )
    for label, rel_path, markers in checks:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{label}:{marker}")
    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    write_text(root, DOCS_README_PATH, "\n".join(REQUIRED_DOCS_README_MARKERS) + "\n")
    write_text(
        root,
        REVIEW_CHECKLIST_PATH,
        "\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS) + "\n",
    )
    write_text(
        root,
        CONTRIBUTOR_GUIDE_PATH,
        "\n".join(REQUIRED_CONTRIBUTOR_GUIDE_MARKERS) + "\n",
    )
    write_text(
        root,
        RELEASE_NOTES_PATH,
        "\n".join(REQUIRED_RELEASE_NOTES_MARKERS) + "\n",
    )
    write_text(
        root,
        NOTIFIER_SURVEY_PATH,
        "\n".join(REQUIRED_NOTIFIER_SURVEY_MARKERS) + "\n",
    )
    write_text(
        root,
        SYSCALLS_GOVERNANCE_PATH,
        "\n".join(REQUIRED_SYSCALLS_GOVERNANCE_MARKERS) + "\n",
    )
    write_text(
        root,
        SCRIPTS_README_PATH,
        "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n",
    )
    write_text(root, TESTS_README_PATH, "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(root, LANE_NOTE_PATH, "\n".join(REQUIRED_LANE_NOTE_MARKERS) + "\n")
    write_text(
        root,
        TRACEABILITY_PATH,
        "\n".join(REQUIRED_TRACEABILITY_MARKERS) + "\n",
    )
    write_text(root, OWNERSHIP_PATH, "\n".join(REQUIRED_OWNERSHIP_MARKERS) + "\n")
    write_text(root, VALIDATOR_PATH, "\n".join(REQUIRED_VALIDATOR_MARKERS) + "\n")
    write_text(root, MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")


def assert_missing_case(root: Path, label: str, rel_path: str, needle: str) -> None:
    text = read_text(root, rel_path)
    if needle not in text:
        raise SystemExit(f"self-test-fixture-missing:{label}")
    write_text(root, rel_path, text.replace(needle, "", 1))
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{label}")
    expected = f"missing-marker:{label}:{needle}"
    actual = result.stdout.strip() or result.stderr.strip() or "no_output"
    if expected not in actual:
        raise SystemExit(f"self-test-mismatch:{label}:{actual}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_landlock_packet_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            ("review-checklist", REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_MARKERS[3]),
            ("contributor-guide", CONTRIBUTOR_GUIDE_PATH, REQUIRED_CONTRIBUTOR_GUIDE_MARKERS[4]),
            ("release-notes", RELEASE_NOTES_PATH, REQUIRED_RELEASE_NOTES_MARKERS[0]),
            ("notifier-survey", NOTIFIER_SURVEY_PATH, REQUIRED_NOTIFIER_SURVEY_MARKERS[0]),
            ("syscalls-governance", SYSCALLS_GOVERNANCE_PATH, REQUIRED_SYSCALLS_GOVERNANCE_MARKERS[1]),
            ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS[0]),
            ("tests-readme", TESTS_README_PATH, REQUIRED_TESTS_README_MARKERS[3]),
            ("lane-note", LANE_NOTE_PATH, REQUIRED_LANE_NOTE_MARKERS[1]),
            ("traceability", TRACEABILITY_PATH, REQUIRED_TRACEABILITY_MARKERS[3]),
            ("validator", VALIDATOR_PATH, REQUIRED_VALIDATOR_MARKERS[3]),
        )
        for label, rel_path, needle in mutations:
            case_root = Path(tmp) / f"{label}_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, label, rel_path, needle)
            cases += 1

    print("PHASE13_LANDLOCK_RULESET_PACKET_SELF_TEST=pass")
    print(f"PHASE13_LANDLOCK_RULESET_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE13_LANDLOCK_RULESET_PACKET=fail")
        print("PHASE13_LANDLOCK_RULESET_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE13_LANDLOCK_RULESET_PACKET_PROBLEMS_END")
        return 1

    print("PHASE13_LANDLOCK_RULESET_PACKET=pass")
    print(f"PHASE13_LANDLOCK_RULESET_PACKET_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

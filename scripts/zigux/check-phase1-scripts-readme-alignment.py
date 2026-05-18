#!/usr/bin/env python3
"""Guard the current Phase 1 scripts-root reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")

REQUIRED_FILES = (
    WORKFLOW_REL,
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("zigux/tests/README.md"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    SCRIPTS_README_REL,
)

REQUIRED_MARKERS = (
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, and closure-validator packet explicit from the scripts root",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

REQUIRED_WORKFLOW_MARKERS = (
    "      - name: Self-test current Phase 1 bench checker",
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)

FORBIDDEN_MARKERS = (
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/validate-phase1-closure.py` remain the current reminder-surface companions for that packet",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    text = read_text(root, SCRIPTS_README_REL)
    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"{SCRIPTS_README_REL.as_posix()}:expected_once:{marker}:actual_count={count}"
            )

    workflow_text = read_text(root, WORKFLOW_REL)
    for marker in REQUIRED_WORKFLOW_MARKERS:
        count = workflow_text.count(marker)
        if count != 1:
            failures.append(
                f"{WORKFLOW_REL.as_posix()}:expected_once:{marker}:actual_count={count}"
            )

    for marker in FORBIDDEN_MARKERS:
        count = text.count(marker)
        if count != 0:
            failures.append(
                f"{SCRIPTS_README_REL.as_posix()}:forbidden:{marker}:actual_count={count}"
            )
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == SCRIPTS_README_REL:
            write_text(root / relative_path, "\n".join(REQUIRED_MARKERS) + "\n")
        elif relative_path == WORKFLOW_REL:
            write_text(root / relative_path, "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")
        else:
            write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-") as tmpdir:
        root = Path(tmpdir)
        make_fixture_tree(root)
        if failures := collect_failures(root):
            print("phase1-scripts-readme-alignment:self-test:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1

    cases = [
        ("missing_file", lambda root: (root / SCRIPTS_README_REL).unlink()),
        ("missing_workflow_file", lambda root: (root / WORKFLOW_REL).unlink()),
        (
            "missing_marker",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                replace_once(read_text(root, SCRIPTS_README_REL), REQUIRED_MARKERS[0] + "\n", ""),
            ),
        ),
        (
            "missing_workflow_marker",
            lambda root: write_text(
                root / WORKFLOW_REL,
                replace_once(
                    read_text(root, WORKFLOW_REL),
                    REQUIRED_WORKFLOW_MARKERS[0] + "\n",
                    "",
                ),
            ),
        ),
        (
            "duplicate_marker",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                replace_once(
                    read_text(root, SCRIPTS_README_REL),
                    REQUIRED_MARKERS[2],
                    REQUIRED_MARKERS[2] + "\n" + REQUIRED_MARKERS[2],
                ),
            ),
        ),
        (
            "duplicate_workflow_command",
            lambda root: write_text(
                root / WORKFLOW_REL,
                replace_once(
                    read_text(root, WORKFLOW_REL),
                    REQUIRED_WORKFLOW_MARKERS[1],
                    REQUIRED_WORKFLOW_MARKERS[1] + "\n" + REQUIRED_WORKFLOW_MARKERS[1],
                ),
            ),
        ),
        (
            "forbidden_old_companion_line",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                read_text(root, SCRIPTS_README_REL) + FORBIDDEN_MARKERS[0] + "\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(
            prefix=f"phase1-scripts-readme-alignment-{name}-"
        ) as tmpdir:
            root = Path(tmpdir)
            make_fixture_tree(root)
            mutate(root)
            if not collect_failures(root):
                print(f"phase1-scripts-readme-alignment:{name}:expected_failure")
                return 1

    print("PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_SCRIPTS_README_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SCRIPTS_README_ALIGNMENT=pass")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(
        f"PHASE1_SCRIPTS_README_ALIGNMENT_REQUIRED_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

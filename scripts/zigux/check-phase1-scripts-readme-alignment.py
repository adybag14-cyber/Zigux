#!/usr/bin/env python3
"""Guard the Phase 1 scripts-root reminder packet wording."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
README_REL = Path("scripts/zigux/README.md")

REQUIRED_FILES = (
    README_REL,
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-find-bit-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/check-phase1-route-summary-counts.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("zigux/Makefile"),
)

REQUIRED_MARKERS = (
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

FORBIDDEN_MARKERS = (
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map, string-review, and direct-owner guards while the restored closure validator also rereads the live `find_bit` review and bench-anchor guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-find-bit-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-find-bit-bench-anchors.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, `find_bit` review, direct-owner, bench, `find_bit` bench-anchor, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py` and `scripts/zigux/check-phase1-find-bit-bench-anchors.py`; `.github/workflows/zigux-bootstrap.yml` self-tests the former and reaches the latter through `scripts/zigux/validate-phase1-closure.py`, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating either shipped guard as a repo-reality gap here",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")

    readme_path = root / README_REL
    if not readme_path.is_file():
        return failures

    text = read_text(root, README_REL)
    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"{README_REL.as_posix()}:expected_once:{marker}:actual_count={count}"
            )
    for marker in FORBIDDEN_MARKERS:
        count = text.count(marker)
        if count != 0:
            failures.append(
                f"{README_REL.as_posix()}:forbidden:{marker}:actual_count={count}"
            )
    return failures


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")
    write_text(root / README_REL, "\n".join(REQUIRED_MARKERS) + "\n")


def replace_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    checks_run = 0

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-") as tmpdir:
        root = Path(tmpdir)
        make_fixture_tree(root)
        if failures := collect_failures(root):
            print("phase1-scripts-readme-alignment:self-test:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        checks_run += 1

    cases = (
        (
            "missing_readme",
            lambda root: (root / README_REL).unlink(),
        ),
        (
            "missing_new_packet_line",
            lambda root: write_text(
                root / README_REL,
                replace_once(read_text(root, README_REL), REQUIRED_MARKERS[2] + "\n"),
            ),
        ),
        (
            "missing_new_validator_line",
            lambda root: write_text(
                root / README_REL,
                replace_once(read_text(root, README_REL), REQUIRED_MARKERS[5] + "\n"),
            ),
        ),
        (
            "duplicate_marker",
            lambda root: write_text(
                root / README_REL,
                replace_once(
                    read_text(root, README_REL),
                    REQUIRED_MARKERS[6],
                    REQUIRED_MARKERS[6] + "\n" + REQUIRED_MARKERS[6],
                ),
            ),
        ),
        (
            "forbidden_old_packet_line",
            lambda root: write_text(
                root / README_REL,
                read_text(root, README_REL) + FORBIDDEN_MARKERS[1] + "\n",
            ),
        ),
        (
            "missing_required_file",
            lambda root: (root / Path("scripts/zigux/check-phase1-find-bit-review-packet.py")).unlink(),
        ),
    )

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
            checks_run += 1

    print("PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument(
        "--self-test", action="store_true", help="run the built-in checker self-test"
    )
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
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

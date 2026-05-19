#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
README_REL = Path("scripts/zigux/README.md")

REQUIRED_PRESENT_FILES = (
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
    Path(".github/workflows/zigux-bootstrap.yml"),
)

REQUIRED_MISSING_FILES = (
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-phase1-installer-review-surfaces.py"),
    Path("scripts/zigux/check-phase1-installer-companion-checks.py"),
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
)

README_MARKERS = (
    "## Phase 1",
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, and closure-validator packet explicit from the scripts root",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`, `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py` keep the broader shared reminder packet and its workflow-backed self-test explicit beside that scripts-root reminder surface",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    readme_path = root / README_REL
    if not readme_path.exists():
        return [f"missing_file:{README_REL.as_posix()}"]

    for relative_path in REQUIRED_PRESENT_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_present_file:{relative_path.as_posix()}")

    for relative_path in REQUIRED_MISSING_FILES:
        if (root / relative_path).exists():
            failures.append(f"unexpected_materialized_gap:{relative_path.as_posix()}")

    readme_text = read_text(readme_path)
    for marker in README_MARKERS:
        count = readme_text.count(marker)
        if count != 1:
            failures.append(f"readme_marker_count:{count}:{marker}")

    return failures


def build_sample_root(root: Path) -> None:
    write_text(root / README_REL, "\n".join(README_MARKERS) + "\n")
    for relative_path in REQUIRED_PRESENT_FILES:
        write_text(root / relative_path, "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"missing marker: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(README_MARKERS) + 2 + len(REQUIRED_PRESENT_FILES) + len(REQUIRED_MISSING_FILES)

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_scripts_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_failures(root) == []
        checks_run += 1

        for marker in README_MARKERS:
            broken_root = root / "missing-marker"
            build_sample_root(broken_root)
            readme_path = broken_root / README_REL
            write_text(readme_path, replace_once(read_text(readme_path), marker))
            failures = collect_failures(broken_root)
            assert failures == [f"readme_marker_count:0:{marker}"]
            checks_run += 1

        duplicate_root = root / "duplicate-marker"
        build_sample_root(duplicate_root)
        readme_path = duplicate_root / README_REL
        duplicated = read_text(readme_path).replace(
            README_MARKERS[0],
            README_MARKERS[0] + "\n\n" + README_MARKERS[0],
            1,
        )
        write_text(readme_path, duplicated)
        failures = collect_failures(duplicate_root)
        assert failures == [f"readme_marker_count:2:{README_MARKERS[0]}]
        checks_run += 1

        missing_readme_root = root / "missing-readme"
        build_sample_root(missing_readme_root)
        (missing_readme_root / README_REL).unlink()
        failures = collect_failures(missing_readme_root)
        assert failures == [f"missing_file:{README_REL.as_posix()}]
        checks_run += 1

        for relative_path in REQUIRED_PRESENT_FILES:
            broken_root = root / ("missing-" + relative_path.name.replace(".", "-"))
            build_sample_root(broken_root)
            (broken_root / relative_path).unlink()
            failures = collect_failures(broken_root)
            assert failures == [f"missing_present_file:{relative_path.as_posix()}]
            checks_run += 1

        for relative_path in REQUIRED_MISSING_FILES:
            broken_root = root / ("returned-" + relative_path.name.replace(".", "-"))
            build_sample_root(broken_root)
            write_text(broken_root / relative_path, "returned\n")
            failures = collect_failures(broken_root)
            assert failures == [f"unexpected_materialized_gap:{relative_path.as_posix()}]
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 1 scripts-root reminder stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_SCRIPTS_README_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SCRIPTS_README_ALIGNMENT=pass")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_PRESENT_FILE_COUNT={len(REQUIRED_PRESENT_FILES)}")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_EXPECTED_GAP_COUNT={len(REQUIRED_MISSING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
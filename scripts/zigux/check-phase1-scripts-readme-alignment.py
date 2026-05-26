#!/usr/bin/env python3
"""Verify that the Phase 1 scripts-root reminder matches current repo reality."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()
README_REL = Path("scripts/zigux/README.md")

REQUIRED_PRESENT_FILES = (
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/check-phase1-route-summary-counts.py"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("zigux/Makefile"),
)

REQUIRED_MISSING_FILES = (
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-phase1-installer-review-surfaces.py"),
    Path("scripts/zigux/check-phase1-installer-companion-checks.py"),
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
)

REQUIRED_MARKERS = (
    "## Phase 1",
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

FORBIDDEN_MARKERS = (
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet",
    "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing marker: {old}")
    return text.replace(old, new, 1)


def build_sample_root(root: Path, readme_text: str | None = None) -> None:
    write_text(root / README_REL, readme_text or ("\n".join(REQUIRED_MARKERS) + "\n"))
    for relative_path in REQUIRED_PRESENT_FILES:
        write_text(root / relative_path, f"present:{relative_path.as_posix()}\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    readme_path = root / README_REL
    if not readme_path.is_file():
        return [f"missing_file:{README_REL.as_posix()}"]

    for relative_path in REQUIRED_PRESENT_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_present_file:{relative_path.as_posix()}")

    for relative_path in REQUIRED_MISSING_FILES:
        if (root / relative_path).exists():
            failures.append(f"unexpected_materialized_gap:{relative_path.as_posix()}")

    text = read_text(readme_path)
    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(f"readme_marker_count:{count}:{marker}")

    for marker in FORBIDDEN_MARKERS:
        count = text.count(marker)
        if count != 0:
            failures.append(f"forbidden_marker_count:{count}:{marker}")

    return failures


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REQUIRED_MARKERS) + 5

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        failures = collect_failures(root)
        if failures:
            print("phase1-scripts-readme-alignment:baseline:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        checks_run += 1

    for index, marker in enumerate(REQUIRED_MARKERS):
        with tempfile.TemporaryDirectory(
            prefix=f"phase1-scripts-readme-alignment-missing-marker-{index}-"
        ) as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            write_text(root / README_REL, replace_once(read_text(root / README_REL), marker + "\n"))
            failures = collect_failures(root)
            if failures != [f"readme_marker_count:0:{marker}"]:
                print(f"phase1-scripts-readme-alignment:missing-marker-{index}:unexpected={failures}")
                return 1
            checks_run += 1

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-duplicate-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        first_marker = REQUIRED_MARKERS[0]
        duplicated = replace_once(
            read_text(root / README_REL),
            first_marker,
            first_marker + "\n" + first_marker,
        )
        write_text(root / README_REL, duplicated)
        failures = collect_failures(root)
        expected = [f"readme_marker_count:2:{first_marker}"]
        if failures != expected:
            print(f"phase1-scripts-readme-alignment:duplicate-marker:unexpected={failures}")
            return 1
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-missing-readme-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        (root / README_REL).unlink()
        failures = collect_failures(root)
        if failures != [f"missing_file:{README_REL.as_posix()}"]:
            print(f"phase1-scripts-readme-alignment:missing-readme:unexpected={failures}")
            return 1
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-missing-present-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        target = REQUIRED_PRESENT_FILES[5]
        (root / target).unlink()
        failures = collect_failures(root)
        if failures != [f"missing_present_file:{target.as_posix()}"]:
            print(f"phase1-scripts-readme-alignment:missing-present:unexpected={failures}")
            return 1
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-materialized-gap-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        target = REQUIRED_MISSING_FILES[0]
        write_text(root / target, "unexpectedly present\n")
        failures = collect_failures(root)
        if failures != [f"unexpected_materialized_gap:{target.as_posix()}"]:
            print(f"phase1-scripts-readme-alignment:materialized-gap:unexpected={failures}")
            return 1
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="phase1-scripts-readme-alignment-forbidden-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        write_text(root / README_REL, read_text(root / README_REL) + FORBIDDEN_MARKERS[0] + "\n")
        failures = collect_failures(root)
        if failures != [f"forbidden_marker_count:1:{FORBIDDEN_MARKERS[0]}"]:
            print(f"phase1-scripts-readme-alignment:forbidden-marker:unexpected={failures}")
            return 1
        checks_run += 1

    if checks_run != expected_case_count:
        print(
            "phase1-scripts-readme-alignment:self-test-count:"
            f"expected={expected_case_count}:actual={checks_run}"
        )
        return 1

    print("PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample repo root to this path",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_SCRIPTS_README_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SCRIPTS_README_ALIGNMENT=pass")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_PRESENT_FILE_COUNT={len(REQUIRED_PRESENT_FILES)}")
    print(f"PHASE1_SCRIPTS_README_ALIGNMENT_EXPECTED_GAP_COUNT={len(REQUIRED_MISSING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the current Phase 1 docs-root reminder packet against stale closure wording."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")

REQUIRED_PRESENT_FILES = (
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
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

README_MARKERS = (
    "# Zigux Documentation This directory is the product documentation root for Zigux.",
    "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/README.md` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-string-review-packet.py` - `scripts/zigux/check-phase1-direct-owner-markers.py` - `scripts/zigux/check-phase1-shared-reminder-packet.py` - `scripts/zigux/check-phase1-bench.py` keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
)

# These exact older snippets used to anchor stale docs-root wording. If they reappear,
# the current Phase 1 repo-reality split has drifted backward.
FORBIDDEN_EXACT_MARKERS = (
    "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, bench, and C-harness routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
    "* current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
)


def repo_root(override: Path | None) -> Path:
    return override.resolve() if override else DEFAULT_ROOT


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    docs_root_path = root / DOCS_ROOT_REL
    if not docs_root_path.exists():
        return [f"missing_file:{DOCS_ROOT_REL.as_posix()}"]

    for relative_path in REQUIRED_PRESENT_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_present_file:{relative_path.as_posix()}")

    for relative_path in REQUIRED_MISSING_FILES:
        if (root / relative_path).exists():
            failures.append(f"unexpected_materialized_gap:{relative_path.as_posix()}")

    text = read_text(docs_root_path)
    for marker in README_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(f"docs_root_marker_count:{count}:{marker}")

    for marker in FORBIDDEN_EXACT_MARKERS:
        count = text.count(marker)
        if count != 0:
            failures.append(f"docs_root_forbidden_marker_count:{count}:{marker}")

    return failures


def build_sample_root(root: Path) -> None:
    write_text(root / DOCS_ROOT_REL, "\n".join(README_MARKERS) + "\n")
    for relative_path in REQUIRED_PRESENT_FILES:
        write_text(root / relative_path, "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"missing marker: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(README_MARKERS) + 2 + len(REQUIRED_PRESENT_FILES) + len(REQUIRED_MISSING_FILES) + len(FORBIDDEN_EXACT_MARKERS)

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_docs_root_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_failures(root) == []
        checks_run += 1

        for marker in README_MARKERS:
            broken_root = root / ("missing-" + str(checks_run))
            build_sample_root(broken_root)
            docs_root_path = broken_root / DOCS_ROOT_REL
            write_text(docs_root_path, replace_once(read_text(docs_root_path), marker))
            failures = collect_failures(broken_root)
            assert failures == [f"docs_root_marker_count:0:{marker}"]
            checks_run += 1

        duplicate_root = root / "duplicate-marker"
        build_sample_root(duplicate_root)
        docs_root_path = duplicate_root / DOCS_ROOT_REL
        duplicated = read_text(docs_root_path).replace(
            README_MARKERS[0],
            README_MARKERS[0] + "\n\n" + README_MARKERS[0],
            1,
        )
        write_text(docs_root_path, duplicated)
        failures = collect_failures(duplicate_root)
        assert failures == [f"docs_root_marker_count:2:{README_MARKERS[0]}"]
        checks_run += 1

        missing_docs_root = root / "missing-docs-root"
        build_sample_root(missing_docs_root)
        (missing_docs_root / DOCS_ROOT_REL).unlink()
        failures = collect_failures(missing_docs_root)
        assert failures == [f"missing_file:{DOCS_ROOT_REL.as_posix()}"]
        checks_run += 1

        for relative_path in REQUIRED_PRESENT_FILES:
            broken_root = root / ("missing-" + relative_path.name.replace(".", "-"))
            build_sample_root(broken_root)
            (broken_root / relative_path).unlink()
            failures = collect_failures(broken_root)
            assert failures == [f"missing_present_file:{relative_path.as_posix()}"]
            checks_run += 1

        for relative_path in REQUIRED_MISSING_FILES:
            broken_root = root / ("returned-" + relative_path.name.replace(".", "-"))
            build_sample_root(broken_root)
            write_text(broken_root / relative_path, "returned\n")
            failures = collect_failures(broken_root)
            assert failures == [f"unexpected_materialized_gap:{relative_path.as_posix()}]
            checks_run += 1

        for marker in FORBIDDEN_EXACT_MARKERS:
            broken_root = root / ("forbidden-" + str(checks_run))
            build_sample_root(broken_root)
            docs_root_path = broken_root / DOCS_ROOT_REL
            write_text(docs_root_path, read_text(docs_root_path) + marker + "\n")
            failures = collect_failures(broken_root)
            assert failures == [f"docs_root_forbidden_marker_count:1:{marker}"]
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE1_DOCS_ROOT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_DOCS_ROOT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 1 docs-root reminder packet stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_DOCS_ROOT_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DOCS_ROOT_PACKET=pass")
    print(f"PHASE1_DOCS_ROOT_PACKET_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE1_DOCS_ROOT_PACKET_PRESENT_FILE_COUNT={len(REQUIRED_PRESENT_FILES)}")
    print(f"PHASE1_DOCS_ROOT_PACKET_EXPECTED_GAP_COUNT={len(REQUIRED_MISSING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

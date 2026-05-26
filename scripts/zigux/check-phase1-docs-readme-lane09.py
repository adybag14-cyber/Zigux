#!/usr/bin/env python3
"""Guard the docs-root Lane 09 Phase 1 packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DOCS_README_REL = Path("Documentation/zigux/README.md")

REQUIRED_LINES = [
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def line_occurrences(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def collect_failures(root: Path) -> list[str]:
    readme_path = root / DOCS_README_REL
    if not readme_path.exists():
        return [f"missing_file:{DOCS_README_REL.as_posix()}"]

    text = load_text(root, DOCS_README_REL)
    failures: list[str] = []
    positions: list[int] = []

    for index, line in enumerate(REQUIRED_LINES):
        count = line_occurrences(text, line)
        if count != 1:
            failures.append(f"docs_readme:marker_{index}:expected=1:actual={count}")
            continue
        positions.append(text.index(line))

    if positions and positions != sorted(positions):
        failures.append("docs_readme:marker_order:out_of_order")

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_readme_text() -> str:
    lines = [
        "# Zigux Documentation This directory is the product documentation root for Zigux.",
        "Phase 1 notes",
        *REQUIRED_LINES,
    ]
    return "\n".join(lines) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, DOCS_README_REL, sample_readme_text())


def run_self_test() -> int:
    cases: list[tuple[str, int | None, str]] = [("success", None, "none")]
    for index in range(len(REQUIRED_LINES)):
        cases.append((f"missing_marker_{index}", index, "remove"))
        cases.append((f"duplicate_marker_{index}", index, "duplicate"))

    for name, marker_index, action in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-docs-readme-lane09-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if marker_index is not None:
                path = root / DOCS_README_REL
                text = path.read_text(encoding="utf-8")
                marker = REQUIRED_LINES[marker_index]
                if action == "remove":
                    text = text.replace(marker + "\n", "", 1)
                elif action == "duplicate":
                    text = text.replace(marker, marker + "\n" + marker, 1)
                path.write_text(text, encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_DOCS_README_LANE09_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
                continue

            if not failures:
                print("PHASE1_DOCS_README_LANE09_SELF_TEST=fail")
                print(f"self_test_case_missing_failure:{name}")
                return 1

    print("PHASE1_DOCS_README_LANE09_SELF_TEST=pass")
    print(f"PHASE1_DOCS_README_LANE09_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test",
    )
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal current-like sample root for replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_repo(Path(args.write_sample_root).resolve())
        print(f"PHASE1_DOCS_README_LANE09_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_DOCS_README_LANE09=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DOCS_README_LANE09=pass")
    print(f"PHASE1_DOCS_README_LANE09_MARKER_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

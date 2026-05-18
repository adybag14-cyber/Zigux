#!/usr/bin/env python3
"""Guard the current Phase 1 tests-root reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
TESTS_README_REL = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
    TESTS_README_REL,
    Path("zigux/Makefile"),
)

MARKERS = (
    "  * current direct-readback Phase 1 reminder packet:",
    "    `Documentation/zigux/phase1-closure.md`",
    "    `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "    `Documentation/zigux/review-checklist.md`",
    "    `scripts/zigux/README.md`",
    "    `scripts/zigux/validate-phase1-closure.py`",
    "    `scripts/zigux/check-phase1-string-review-packet.py`",
    "    `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "    `scripts/zigux/check-phase1-bench.py`",
    "    `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
)

FORBIDDEN_MARKERS = (
    "* current direct-readback Phase 1 reminder packet: `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py`",
    "* repo-reality warning for the broader Phase 1 installer-backed closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "* current direct-readback shared Phase 1 closure companions visible from the tests-root reminder:",
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

    text = read_text(root, TESTS_README_REL)
    for marker in MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"{TESTS_README_REL.as_posix()}:expected_once:{marker}:actual_count={count}"
            )
    for marker in FORBIDDEN_MARKERS:
        count = text.count(marker)
        if count != 0:
            failures.append(
                f"{TESTS_README_REL.as_posix()}:forbidden:{marker}:actual_count={count}"
            )
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == TESTS_README_REL:
            write_text(root / relative_path, "\n".join(MARKERS) + "\n")
        else:
            write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-tests-readme-alignment-") as tmpdir:
        root = Path(tmpdir)
        make_fixture_tree(root)
        if failures := collect_failures(root):
            print("phase1-tests-readme-alignment:self-test:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1

    cases = [
        ("missing_file", lambda root: (root / TESTS_README_REL).unlink()),
        (
            "missing_marker",
            lambda root: write_text(
                root / TESTS_README_REL,
                replace_once(read_text(root, TESTS_README_REL), MARKERS[0] + "\n", ""),
            ),
        ),
        (
            "duplicate_marker",
            lambda root: write_text(
                root / TESTS_README_REL,
                replace_once(
                    read_text(root, TESTS_README_REL),
                    MARKERS[10],
                    MARKERS[10] + "\n" + MARKERS[10],
                ),
            ),
        ),
        (
            "forbidden_old_marker",
            lambda root: write_text(
                root / TESTS_README_REL,
                read_text(root, TESTS_README_REL) + FORBIDDEN_MARKERS[0] + "\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(
            prefix=f"phase1-tests-readme-alignment-{name}-"
        ) as tmpdir:
            root = Path(tmpdir)
            make_fixture_tree(root)
            mutate(root)
            if not collect_failures(root):
                print(f"phase1-tests-readme-alignment:{name}:expected_failure")
                return 1

    print("PHASE1_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_TESTS_README_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE1_TESTS_README_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_TESTS_README_ALIGNMENT_REQUIRED_MARKER_COUNT={len(MARKERS)}")
    print(f"PHASE1_TESTS_README_ALIGNMENT_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

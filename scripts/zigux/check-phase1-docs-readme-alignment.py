#!/usr/bin/env python3
"""Guard the current Phase 1 docs-root reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
DOCS_README_REL = Path("Documentation/zigux/README.md")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
    DOCS_README_REL,
)

MARKERS = (
    "- `Documentation/zigux/phase1-closure.md`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.",
    "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    "  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
)

FORBIDDEN_MARKERS = (
    "- `scripts/zigux/validate-phase1.py`",
    "- `scripts/zigux/check-phase1-parity.py`",
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

    text = read_text(root, DOCS_README_REL)
    for marker in MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"{DOCS_README_REL.as_posix()}:expected_once:{marker}:actual_count={count}"
            )
    for marker in FORBIDDEN_MARKERS:
        count = text.count(marker)
        if count != 0:
            failures.append(
                f"{DOCS_README_REL.as_posix()}:forbidden:{marker}:actual_count={count}"
            )
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == DOCS_README_REL:
            write_text(root / relative_path, "\n".join(MARKERS) + "\n")
        else:
            write_text(root / relative_path, f"fixture for {relative_path.as_posix()}\n")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-docs-readme-alignment-") as tmpdir:
        root = Path(tmpdir)
        make_fixture_tree(root)
        if failures := collect_failures(root):
            print("phase1-docs-readme-alignment:self-test:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1

    cases = [
        ("missing_file", lambda root: (root / DOCS_README_REL).unlink()),
        (
            "missing_marker",
            lambda root: write_text(
                root / DOCS_README_REL,
                replace_once(read_text(root, DOCS_README_REL), MARKERS[0] + "\n", ""),
            ),
        ),
        (
            "duplicate_marker",
            lambda root: write_text(
                root / DOCS_README_REL,
                replace_once(
                    read_text(root, DOCS_README_REL),
                    MARKERS[2],
                    MARKERS[2] + "\n" + MARKERS[2],
                ),
            ),
        ),
        (
            "forbidden_old_route",
            lambda root: write_text(
                root / DOCS_README_REL,
                read_text(root, DOCS_README_REL) + FORBIDDEN_MARKERS[0] + "\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(
            prefix=f"phase1-docs-readme-alignment-{name}-"
        ) as tmpdir:
            root = Path(tmpdir)
            make_fixture_tree(root)
            mutate(root)
            if not collect_failures(root):
                print(f"phase1-docs-readme-alignment:{name}:expected_failure")
                return 1

    print("PHASE1_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_DOCS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_DOCS_README_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DOCS_README_ALIGNMENT=pass")
    print(f"PHASE1_DOCS_README_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_DOCS_README_ALIGNMENT_REQUIRED_MARKER_COUNT={len(MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

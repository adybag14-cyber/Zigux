#!/usr/bin/env python3
"""Fail closed on the returned-anchor reminder in the shared Phase 10 tests-root note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

TARGET = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")

SCRIPTS_ROOT_PHRASE = (
    "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root "
    "packet on current `master` and keep it aligned with the shared closure note, "
    "lane-sequencing note, review checklist, and tests-root reminder instead of "
    "leaving it in neighboring-surface wording."
)

REQUIRED_MARKERS = [
    "returned shared closure packet anchors: `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.",
    SCRIPTS_ROOT_PHRASE,
    "Keep the returned shared validator pair `scripts/zigux/validate-phase10.py` and `scripts/zigux/validate-phase10-closure.py` plus the returned `zigux/Makefile` explicit in that directly re-readable anchor set instead of leaving them visible only in the shared build-gate reminder.",
]


def validate(root: Path) -> list[str]:
    path = root / TARGET
    if not path.exists():
        return [f"missing-file:{TARGET.as_posix()}"]

    text = path.read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            missing.append(marker)
    return missing


def write_fixture(root: Path) -> None:
    path = root / TARGET
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(REQUIRED_MARKERS) + "\n", encoding="utf-8")


def expect_missing(root: Path, old: str, new: str, expected: str) -> None:
    path = root / TARGET
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    missing = validate(root)
    if expected not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase10-tests-root-returned-anchor-self-test:expected={expected}:actual={actual}"
        )
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_tests_root_returned_anchor_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing = validate(root)
        if missing:
            raise SystemExit(
                "phase10-tests-root-returned-anchor-self-test:baseline_failed:"
                + ",".join(missing)
            )

        cases = [
            (
                REQUIRED_MARKERS[0],
                "returned shared closure packet anchors: `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`",
                REQUIRED_MARKERS[0],
            ),
            (
                REQUIRED_MARKERS[1],
                "The returned shared build gate now runs through `zigux/tests/phase10_build.zig` only.",
                REQUIRED_MARKERS[1],
            ),
            (
                REQUIRED_MARKERS[2],
                "Current `master` does materialize `zigux/Makefile`, but keep the returned file implicit here.",
                REQUIRED_MARKERS[2],
            ),
            (
                SCRIPTS_ROOT_PHRASE,
                "Treat `scripts/zigux/README.md` as a neighboring reminder surface.",
                SCRIPTS_ROOT_PHRASE,
            ),
            (
                REQUIRED_MARKERS[4],
                "Keep the returned shared validator pair `scripts/zigux/validate-phase10-closure.py` explicit in that directly re-readable anchor set.",
                REQUIRED_MARKERS[4],
            ),
        ]

        for old, new, expected in cases:
            expect_missing(root, old, new, expected)

    print("PHASE10_TESTS_ROOT_RETURNED_ANCHOR_SELF_TEST=pass")
    print("PHASE10_TESTS_ROOT_RETURNED_ANCHOR_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the returned-anchor reminder in the shared Phase 10 tests-root note."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate(args.repo_root)
    if missing:
        print("PHASE10_TESTS_ROOT_RETURNED_ANCHOR=fail")
        print("MISSING_PHASE10_TESTS_ROOT_RETURNED_ANCHOR_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_PHASE10_TESTS_ROOT_RETURNED_ANCHOR_MARKERS_END")
        return 1

    print("PHASE10_TESTS_ROOT_RETURNED_ANCHOR=pass")
    print(f"PHASE10_TESTS_ROOT_RETURNED_ANCHOR_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

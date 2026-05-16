#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase12-validator-first-release-packet.md")

REQUIRED_EXISTING_PATHS = [
    Path("Documentation/zigux/phase12-release-sequencing.md"),
    Path("Documentation/zigux/phase12-release-closure-checklist.md"),
    Path("Documentation/zigux/phase12-release-readiness-survey.md"),
    Path("Documentation/zigux/phase12-release-coordination-matrix.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/check-build-only-phase12-surface.py"),
    Path("scripts/zigux/check-phase12-cross.py"),
    Path("scripts/zigux/check-phase12-release-readiness-packet.py"),
    Path("scripts/zigux/validate-phase12.py"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase12_build.zig"),
]

REQUIRED_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_RELEASE_CLOSED=no`",
    "release-sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`",
    "release-coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`",
    "release-closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`",
    "support-bundle checkers: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-cross.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "shared validator route: `scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`",
    "keep the validator-first support bundle explicit before the smoke-first replay order: `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`",
    "if `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order through `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
    "do not widen this note into a focused libbpf-only replay, a shared cross-build replay, or a broader shared `check-phase12-*.py` family",
    "the direct `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
]


def read_text(root: Path, rel_path: Path) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    if not (root / NOTE_PATH).exists():
        return [f"missing_file:{NOTE_PATH.as_posix()}"]

    note_text = read_text(root, NOTE_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in note_text:
            failures.append(f"missing_marker:{marker}")

    for rel_path in REQUIRED_EXISTING_PATHS:
        if not (root / rel_path).exists():
            failures.append(f"missing_companion:{rel_path.as_posix()}")

    return failures


def write_fixture_tree(root: Path) -> None:
    note_path = root / NOTE_PATH
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(
        "\n".join(
            [
                "# Phase 12 Validator-First Release Packet",
                "",
                "Fixture note.",
                "",
                "## Status",
                "",
                "- `PHASE12_STATUS=active`",
                "- `PHASE12_RELEASE_CLOSED=no`",
                "- release-sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`",
                "- release-coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`",
                "- release-closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`",
                "- support-bundle checkers: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-cross.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py`",
                "- shared validator route: `scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`",
                "",
                "## Shared Order",
                "",
                "- keep the validator-first support bundle explicit before the smoke-first replay order: `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`",
                "",
                "## Fallback Boundaries",
                "",
                "- if `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order through `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
                "- do not widen this note into a focused libbpf-only replay, a shared cross-build replay, or a broader shared `check-phase12-*.py` family",
                "- the direct `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for rel_path in REQUIRED_EXISTING_PATHS:
        full_path = root / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(f"fixture for {rel_path.as_posix()}\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    if updated == text:
        raise SystemExit(f"failed to mutate fixture: {path}:{old}")
    path.write_text(updated, encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = collect_failures(root)
    if expected not in failures:
        raise SystemExit(f"expected {expected!r}, got {failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12_validator_first_release_packet_"))
    try:
        write_fixture_tree(base)
        failures = collect_failures(base)
        if failures:
            raise SystemExit(f"unexpected failures for valid fixture: {failures!r}")

        replace_once(
            base / NOTE_PATH,
            "`Documentation/zigux/phase12-release-coordination-matrix.md`",
            "`Documentation/zigux/phase12-release-coordination-old.md`",
        )
        expect_failure(
            base,
            "missing_marker:release-coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`",
        )

        write_fixture_tree(base)
        replace_once(
            base / NOTE_PATH,
            "do not widen this note into a focused libbpf-only replay, a shared cross-build replay, or a broader shared `check-phase12-*.py` family",
            "allow the note to widen into extra shared checker inventory",
        )
        expect_failure(
            base,
            "missing_marker:do not widen this note into a focused libbpf-only replay, a shared cross-build replay, or a broader shared `check-phase12-*.py` family",
        )

        write_fixture_tree(base)
        (base / REQUIRED_EXISTING_PATHS[6]).unlink()
        expect_failure(base, "missing_companion:scripts/zigux/check-phase12-cross.py")

        write_fixture_tree(base)
        (base / NOTE_PATH).unlink()
        expect_failure(base, "missing_file:Documentation/zigux/phase12-validator-first-release-packet.md")

        print("PHASE12_VALIDATOR_FIRST_RELEASE_PACKET_SELF_TEST=pass")
        print("PHASE12_VALIDATOR_FIRST_RELEASE_PACKET_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed if the Phase 12 validator-first release packet drops its "
            "sequencing, closure, coordination, or support-bundle markers."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root containing the Phase 12 validator-first release packet.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run fixture-backed self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.repo_root)
    if failures:
        print("PHASE12_VALIDATOR_FIRST_RELEASE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE12_VALIDATOR_FIRST_RELEASE_PACKET=pass")
    print(f"PHASE12_VALIDATOR_FIRST_RELEASE_PACKET_REQUIRED_FILE_COUNT={1 + len(REQUIRED_EXISTING_PATHS)}")
    print(f"PHASE12_VALIDATOR_FIRST_RELEASE_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 HVC cleanup-prerequisite parity packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


NOTE_PATH = "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md"
SURVEY_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
DRIVER_PATH = "drivers/tty/hvc/hvc_console.zig"
PROOF_PATH = "zigux/tests/phase11_hvc_cleanup_packet_proof.zig"
SELF_PATH = "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py"

REQUIRED_FILES = (
    NOTE_PATH,
    SURVEY_PATH,
    MATRIX_PATH,
    DRIVER_PATH,
    PROOF_PATH,
    SELF_PATH,
)

FILE_EXPECTATIONS = {
    NOTE_PATH: (
        "`PHASE11_HVC_CLEANUP_PREREQUISITE_STATUS=current_head_trigger_split_reviewable`",
        "`summarizeCleanupPrerequisite()`",
        "`CleanupTrigger.final_close_only`",
        "`CleanupTrigger.hangup_only`",
        "`CleanupTrigger.final_close_and_hangup`",
        "`error.CleanupRequiresFinalCloseOrHangup`",
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`make -C zigux phase11-validate`",
        "does not claim that live `hvc_cleanup()` execution is replayed on current",
    ),
    SURVEY_PATH: (
        "`Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md`",
        "`scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`",
        "cleanup-prerequisite parity note",
        "cleanup-prerequisite packet checker",
    ),
    MATRIX_PATH: (
        "`Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md`",
        "`scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`",
        "cleanup-prerequisite trigger split",
        "dedicated teardown-prerequisite reminder guard",
    ),
    DRIVER_PATH: (
        "pub const CleanupTrigger = enum {",
        "final_close_only,",
        "hangup_only,",
        "final_close_and_hangup,",
        "pub fn summarizeCleanupPrerequisite(",
        "error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary",
    ),
    PROOF_PATH: (
        "cleanup prerequisite final-close-only trigger reviewable",
        "cleanup prerequisite hangup-only trigger reviewable",
        "cleanup prerequisite combined trigger reviewable",
        "rejects cleanup without final-close or hangup evidence",
    ),
    SELF_PATH: (
        "PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET=pass",
        "PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_SELF_TEST=pass",
    ),
}


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {relative_path}") from exc


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> None:
    missing = [path for path in REQUIRED_FILES if not (root / path).is_file()]
    if missing:
        raise ValidationError(
            "missing required Phase 11 HVC cleanup-prerequisite packet files: "
            + ", ".join(missing)
        )

    for relative_path, fragments in FILE_EXPECTATIONS.items():
        text = read_text(root, relative_path)
        for fragment in fragments:
            if fragment not in text:
                raise ValidationError(
                    f"{relative_path} is missing required fragment: {fragment!r}"
                )


def build_fixture(root: Path) -> None:
    for relative_path, fragments in FILE_EXPECTATIONS.items():
        write_text(root, relative_path, "\n".join(fragments) + "\n")


def expect_failure(root: Path, mutate, fragment: str) -> None:
    mutate(root)
    try:
        validate(root)
    except ValidationError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-hvc-cleanup-prereq-"))
    cases = 0
    try:
        fixture = temp_dir / "fixture"
        build_fixture(fixture)
        validate(fixture)
        cases += 1

        mutations = (
            (NOTE_PATH, "`summarizeCleanupPrerequisite()`"),
            (NOTE_PATH, "`CleanupTrigger.final_close_only`"),
            (NOTE_PATH, "`CleanupTrigger.hangup_only`"),
            (NOTE_PATH, "`CleanupTrigger.final_close_and_hangup`"),
            (NOTE_PATH, "`error.CleanupRequiresFinalCloseOrHangup`"),
            (NOTE_PATH, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`"),
            (SURVEY_PATH, "`Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md`"),
            (SURVEY_PATH, "`scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`"),
            (MATRIX_PATH, "`Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md`"),
            (MATRIX_PATH, "dedicated teardown-prerequisite reminder guard"),
            (DRIVER_PATH, "pub const CleanupTrigger = enum {"),
            (DRIVER_PATH, "pub fn summarizeCleanupPrerequisite("),
            (PROOF_PATH, "cleanup prerequisite final-close-only trigger reviewable"),
            (PROOF_PATH, "rejects cleanup without final-close or hangup evidence"),
        )

        for index, (relative_path, fragment) in enumerate(mutations, start=1):
            broken = temp_dir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(
                broken,
                lambda root, rel=relative_path, frag=fragment: write_text(
                    root,
                    rel,
                    read_text(root, rel).replace(frag, "", 1),
                ),
                fragment,
            )
            cases += 1

        missing = temp_dir / "missing"
        shutil.copytree(fixture, missing, dirs_exist_ok=True)
        expect_failure(
            missing,
            lambda root: (root / NOTE_PATH).unlink(),
            "missing required Phase 11 HVC cleanup-prerequisite packet files",
        )
        cases += 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_SELF_TEST=pass")
    print(f"PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the Phase 11 HVC cleanup-prerequisite packet for drift."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the Zigux repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in fixture cases instead of validating a repository checkout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        validate(Path(args.repo_root).resolve())
    except ValidationError as exc:
        print(f"PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET=pass")
    print(f"PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
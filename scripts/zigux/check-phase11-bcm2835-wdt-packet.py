#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 bcm2835 watchdog packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-bcm2835-wdt-packet.py"

REQUIRED_FILES = {
    "driver": "drivers/watchdog/bcm2835_wdt.zig",
    "survey_note": "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "teardown_note": "Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md",
    "validation_matrix": "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "shared_contract": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "test_replay": "zigux/tests/phase11_bcm2835_wdt.zig",
    "survey_replay": "zigux/tests/phase11_bcm2835_wdt_survey.zig",
    "verify_replay": "drivers/watchdog/bcm2835_wdt_verify.zig",
}

SURVEY_NOTE_MARKERS = [
    "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_survey.zig`",
    "`Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "archival packet identity remains `P11-L08`",
]

TEARDOWN_NOTE_MARKERS = [
    "PHASE11_BCM2835_WDT_TEARDOWN_STATUS=driver_teardown_truthful",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_survey.zig`",
    "`Bcm2835WdtLab.stop()`",
    "`Bcm2835WdtLab.restart()`",
    "`Bcm2835WdtLab.poweroff()`",
]

VALIDATION_MATRIX_MARKERS = [
    "PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_survey.zig`",
    "`Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`",
    "Do not claim `zigux/tests/phase11_bcm2835_wdt_manifest.json` as landed",
]

DRIVER_MARKERS = [
    'pub const anchor_path = "drivers/watchdog/bcm2835_wdt.c";',
    "pub fn summarizeProbe(request: ProbeRequest) !ProbeSummary",
    "pub fn summarizePlatformHandoff(request: PlatformHandoffRequest) !PlatformHandoffSummary",
    "pub const Bcm2835WdtLab = struct {",
    "pub fn poweroff(self: *Bcm2835WdtLab, handler_claimed: bool) PoweroffSummary",
]

TEST_REPLAY_MARKERS = [
    'test "phase11 bcm2835 watchdog replay keeps timeout helpers explicit"',
    'test "phase11 bcm2835 watchdog replay keeps probe ownership and poweroff conflict distinct"',
    'test "phase11 bcm2835 watchdog replay keeps platform handoff readiness and poweroff claim blocking explicit"',
    'test "phase11 bcm2835 watchdog replay keeps start stop restart and poweroff lifecycle explicit"',
]

SURVEY_REPLAY_MARKERS = [
    'test "phase11 bcm2835 survey keeps direct handoff and lifecycle helpers explicit"',
    'test "phase11 bcm2835 survey keeps survey, teardown, and matrix notes aligned with the direct packet"',
    'test "phase11 bcm2835 survey keeps the replay and verify helpers reviewable"',
]

VERIFY_REPLAY_MARKERS = [
    'test "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit"',
    'test "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct"',
]

SHARED_CONTRACT_MARKERS = [
    "bcm2835, gpio, HVC, and header-boundary notes plus their dedicated `check-phase11-*.py` scripts remain parked as continuity surfaces beside the shared packet",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
]

CLOSURE_NOTE_MARKERS = [
    "bcm2835 continuity on current `master` stays bounded to `drivers/watchdog/bcm2835_wdt.zig`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, and `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
]

LANE_NOTE_MARKERS = [
    "* bcm2835 lane continuity stays split: archival packet identity remains `P11-L08`, while the current same-family reminder refreshes run through `P11-L05`",
    "* contributor-note lane `P11-L18` owns the shared contributor-facing wording across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
]

MARKER_GROUPS = {
    "driver": DRIVER_MARKERS,
    "survey_note": SURVEY_NOTE_MARKERS,
    "teardown_note": TEARDOWN_NOTE_MARKERS,
    "validation_matrix": VALIDATION_MATRIX_MARKERS,
    "shared_contract": SHARED_CONTRACT_MARKERS,
    "closure_note": CLOSURE_NOTE_MARKERS,
    "lane_note": LANE_NOTE_MARKERS,
    "test_replay": TEST_REPLAY_MARKERS,
    "survey_replay": SURVEY_REPLAY_MARKERS,
    "verify_replay": VERIFY_REPLAY_MARKERS,
}


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {relative_path}: {marker}")


def run_check(root: Path) -> None:
    expect_markers(
        REQUIRED_FILES["driver"],
        read_text(root, REQUIRED_FILES["driver"]),
        DRIVER_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["survey_note"],
        read_text(root, REQUIRED_FILES["survey_note"]),
        SURVEY_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["teardown_note"],
        read_text(root, REQUIRED_FILES["teardown_note"]),
        TEARDOWN_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["validation_matrix"],
        read_text(root, REQUIRED_FILES["validation_matrix"]),
        VALIDATION_MATRIX_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["shared_contract"],
        read_text(root, REQUIRED_FILES["shared_contract"]),
        SHARED_CONTRACT_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["closure_note"],
        read_text(root, REQUIRED_FILES["closure_note"]),
        CLOSURE_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["lane_note"],
        read_text(root, REQUIRED_FILES["lane_note"]),
        LANE_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["test_replay"],
        read_text(root, REQUIRED_FILES["test_replay"]),
        TEST_REPLAY_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["survey_replay"],
        read_text(root, REQUIRED_FILES["survey_replay"]),
        SURVEY_REPLAY_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["verify_replay"],
        read_text(root, REQUIRED_FILES["verify_replay"]),
        VERIFY_REPLAY_MARKERS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(root / REQUIRED_FILES["driver"], "\n".join(DRIVER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_note"], "\n".join(SURVEY_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["teardown_note"], "\n".join(TEARDOWN_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["validation_matrix"], "\n".join(VALIDATION_MATRIX_MARKERS) + "\n")
    write(root / REQUIRED_FILES["shared_contract"], "\n".join(SHARED_CONTRACT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["closure_note"], "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["lane_note"], "\n".join(LANE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["test_replay"], "\n".join(TEST_REPLAY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_replay"], "\n".join(SURVEY_REPLAY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["verify_replay"], "\n".join(VERIFY_REPLAY_MARKERS) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_bcm2835_wdt_packet_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        marker_case_count = 0
        for label, markers in MARKER_GROUPS.items():
            relative_path = REQUIRED_FILES[label]
            for marker_index, marker in enumerate(markers, start=1):
                case_root = tmpdir / f"{label}_{marker_index}"
                shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
                path = case_root / relative_path
                path.write_text(
                    path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1),
                    encoding="utf-8",
                )
                expect_failure(case_root, marker)
                marker_case_count += 1

        missing_file_case_count = 0
        for label, relative_path in REQUIRED_FILES.items():
            case_root = tmpdir / f"missing_{label}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            (case_root / relative_path).unlink()
            expect_failure(case_root, relative_path)
            missing_file_case_count += 1

        print("PHASE11_BCM2835_WDT_PACKET_SELF_TEST=pass")
        print(
            "PHASE11_BCM2835_WDT_PACKET_SELF_TEST_CASE_COUNT="
            f"{marker_case_count + missing_file_case_count}"
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_BCM2835_WDT_PACKET=fail: {exc}")
        return 1

    print("PHASE11_BCM2835_WDT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "survey": Path("Documentation/zigux/phase11-bcm2835-wdt-survey.md"),
    "plan": Path("Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md"),
    "matrix": Path("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"),
    "driver_tests": Path("zigux/tests/phase11_bcm2835_wdt.zig"),
    "packet_survey": Path("zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig"),
    "packet_build": Path("zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig"),
}

SURVEY_MARKERS = [
    "# Phase 11 BCM2835 Watchdog Survey",
    "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed",
    "archival packet identity remains `P11-L08`",
    "`Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "driver-return proof plus a coupled verify helper",
    "current-head validation matrix",
    "manifest-backed closure or teardown-note step",
]

PLAN_MARKERS = [
    "# Phase 11 BCM2835 Watchdog Platform Validation Plan",
    "PHASE11_BCM2835_WDT_PLATFORM_VALIDATION_PLAN=starter_boundary_recorded",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`",
    "minimal driver-return proof, driver-backed verify helper, and focused tests-root replay",
    "Do not fabricate current-head proof for a manifest-backed closure packet, slice note, teardown note",
    "Do not use it to reopen `gpio_wdt`, `dw_wdt`, HVC, or shared Phase 11 wording.",
    "The next honest bcm2835-only follow-through is one explicit manifest-backed closure or teardown-note step",
]

MATRIX_MARKERS = [
    "# Phase 11 BCM2835 Watchdog Validation Matrix",
    "PHASE11_BCM2835_WDT_STATUS=driver_proof_and_matrix_packet_truthful",
    "lane: `P11-L08`",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
    "compile anchor: `zigux/tests/phase11_bcm2835_wdt.zig`",
    "verify-helper anchor: `drivers/watchdog/bcm2835_wdt_verify.zig`",
    "does not treat absent wider replay, manifest, slice, or teardown-note files as current-head evidence.",
]

DRIVER_TEST_MARKERS = [
    'test "phase11 bcm2835 watchdog starter keeps timeout and restart constants reviewable" {',
    'test "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit" {',
    'test "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct" {',
]

PACKET_SURVEY_MARKERS = [
    'test "phase11 bcm2835 manifest packet survey keeps the returned driver proof truthful" {',
    'test "phase11 bcm2835 manifest packet survey keeps the blocker plan aligned with current master" {',
    'test "phase11 bcm2835 manifest packet survey keeps the validation matrix aligned with the current driver packet" {',
    'test "phase11 bcm2835 manifest packet survey keeps the dedicated build route pointed at the current reminder packet" {',
    'try expectContains(build_file, ".name = \\"phase11-bcm2835-wdt-manifest-packet-survey-tests\\"");',
]

PACKET_BUILD_MARKERS = [
    '.root_source_file = b.path("phase11_bcm2835_wdt_manifest_packet_survey.zig")',
    '.name = "phase11-bcm2835-wdt-manifest-packet-survey-tests"',
    'Run the focused Phase 11 bcm2835 watchdog manifest packet survey',
]

MARKERS_BY_LABEL = {
    "survey": SURVEY_MARKERS,
    "plan": PLAN_MARKERS,
    "matrix": MATRIX_MARKERS,
    "driver_tests": DRIVER_TEST_MARKERS,
    "packet_survey": PACKET_SURVEY_MARKERS,
    "packet_build": PACKET_BUILD_MARKERS,
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_repo(root: Path) -> list[str]:
    failures: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            continue
        text = read_text(path)
        for marker in MARKERS_BY_LABEL[label]:
            if marker not in text:
                failures.append(f"missing_marker:{label}:{marker}")
    return failures


def seed_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

    for label, markers in MARKERS_BY_LABEL.items():
        (root / REQUIRED_FILES[label]).write_text("\n".join(markers) + "\n", encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = check_repo(root)
    if expected not in failures:
        raise SystemExit(f"expected {expected!r}, got {failures}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-bcm2835-shared-replay-") as tmpdir:
        root = Path(tmpdir)
        fixture = root / "fixture"
        seed_fixture(fixture)

        baseline = check_repo(fixture)
        if baseline:
            raise SystemExit("baseline self-test fixture failed: " + ", ".join(baseline))

        case_count = 1
        marker_cases = [
            ("survey", SURVEY_MARKERS[1]),
            ("survey", SURVEY_MARKERS[9]),
            ("plan", PLAN_MARKERS[1]),
            ("plan", PLAN_MARKERS[6]),
            ("matrix", MATRIX_MARKERS[1]),
            ("matrix", MATRIX_MARKERS[10]),
            ("driver_tests", DRIVER_TEST_MARKERS[1]),
            ("packet_survey", PACKET_SURVEY_MARKERS[2]),
            ("packet_build", PACKET_BUILD_MARKERS[2]),
        ]

        for index, (label, marker) in enumerate(marker_cases, start=1):
            case_root = root / f"marker_case_{index}"
            shutil.copytree(fixture, case_root)
            target = case_root / REQUIRED_FILES[label]
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            expect_failure(case_root, f"missing_marker:{label}:{marker}")
            case_count += 1

        missing_file_case = root / "missing_file_case"
        shutil.copytree(fixture, missing_file_case)
        (missing_file_case / REQUIRED_FILES["packet_build"]).unlink()
        expect_failure(
            missing_file_case,
            f"missing_file:{REQUIRED_FILES['packet_build'].as_posix()}",
        )
        case_count += 1

        print("PHASE11_BCM2835_SHARED_REPLAY_SURFACE_SELF_TEST=pass")
        print(f"PHASE11_BCM2835_SHARED_REPLAY_SURFACE_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 11 bcm2835 shared replay packet drifts."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in fixture self-test",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    failures = check_repo(args.repo_root)
    if failures:
        for failure in failures:
            print(failure)
        print("PHASE11_BCM2835_SHARED_REPLAY_SURFACE=fail")
        return 1

    print("PHASE11_BCM2835_SHARED_REPLAY_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

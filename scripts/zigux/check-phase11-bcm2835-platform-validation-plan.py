#!/usr/bin/env python3
"""Fail-closed checks for the Phase 11 bcm2835 platform validation plan note."""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sys
import tempfile


FILES = {
    "plan": "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md",
    "survey": "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "teardown": "Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md",
    "matrix": "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "manifest": "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "survey_gate": "zigux/tests/phase11_bcm2835_wdt_survey.zig",
    "driver": "drivers/watchdog/bcm2835_wdt.zig",
    "verify": "drivers/watchdog/bcm2835_wdt_verify.zig",
    "replay": "zigux/tests/phase11_bcm2835_wdt.zig",
}

PLAN_MARKERS = (
    "# Phase 11 BCM2835 Watchdog Platform Validation Plan",
    "PHASE11_BCM2835_WDT_PLATFORM_PLAN_STATUS=plan_landed",
    "lane family: `P11-L02`",
    "Several existing bcm2835 reminder notes now point at one explicit validation plan as the",
    "PM-base absence, PM-base readiness, and blocked-on-live-platform-registration outcomes explicit",
    "register-device intent from successful live watchdog-core registration",
    "claimed-versus-conflicting ownership remains explicit across poweroff and remove paths",
    "Keep the next bcm2835 move bcm2835-only.",
)

SURVEY_MARKERS = (
    "explicit validation plan",
    "manifest-backed archival reminder packet",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
)

TEARDOWN_MARKERS = (
    "explicit validation plan",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "archival manifest-backed reminder packet",
)

MATRIX_MARKERS = (
    "explicit validation plan",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "zigux/tests/phase11_bcm2835_wdt_survey.zig",
)

MANIFEST_MARKERS = (
    "\"lane_key\": \"P11-L08\"",
    "\"id\": \"phase11-bcm2835-wdt-live-platform-registration\"",
    "\"status\": \"blocked_on_driver_scaffold\"",
)

SURVEY_GATE_MARKERS = (
    "phase11 bcm2835 survey keeps direct handoff and lifecycle helpers explicit",
    "phase11 bcm2835 survey keeps survey, teardown, manifest, and matrix notes aligned",
    "phase11 bcm2835 survey keeps the replay and verify helpers reviewable",
)

DRIVER_MARKERS = (
    "pub fn summarizePlatformHandoff(request: PlatformHandoffRequest) !PlatformHandoffSummary",
    ".blocked_on_live_platform_registration = true,",
    "pub fn poweroff(self: *Bcm2835WdtLab, handler_claimed: bool) PoweroffSummary",
)

VERIFY_MARKERS = (
    "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit",
    "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct",
)

REPLAY_MARKERS = (
    "phase11 bcm2835 watchdog replay keeps platform handoff readiness and poweroff claim blocking explicit",
    "phase11 bcm2835 watchdog replay keeps start stop restart and poweroff lifecycle explicit",
)


def read_text(root: pathlib.Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {relative_path}") from exc


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    return [f"{label}: missing {marker}" for marker in markers if marker not in text]


def run_check(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    errors.extend(require_markers("plan", read_text(root, FILES["plan"]), PLAN_MARKERS))
    errors.extend(require_markers("survey", read_text(root, FILES["survey"]), SURVEY_MARKERS))
    errors.extend(require_markers("teardown", read_text(root, FILES["teardown"]), TEARDOWN_MARKERS))
    errors.extend(require_markers("matrix", read_text(root, FILES["matrix"]), MATRIX_MARKERS))
    errors.extend(require_markers("manifest", read_text(root, FILES["manifest"]), MANIFEST_MARKERS))
    errors.extend(require_markers("survey_gate", read_text(root, FILES["survey_gate"]), SURVEY_GATE_MARKERS))
    errors.extend(require_markers("driver", read_text(root, FILES["driver"]), DRIVER_MARKERS))
    errors.extend(require_markers("verify", read_text(root, FILES["verify"]), VERIFY_MARKERS))
    errors.extend(require_markers("replay", read_text(root, FILES["replay"]), REPLAY_MARKERS))
    return errors


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: pathlib.Path) -> None:
    write(root / FILES["plan"], "\n".join(PLAN_MARKERS) + "\n")
    write(root / FILES["survey"], "\n".join(SURVEY_MARKERS) + "\n")
    write(root / FILES["teardown"], "\n".join(TEARDOWN_MARKERS) + "\n")
    write(root / FILES["matrix"], "\n".join(MATRIX_MARKERS) + "\n")
    write(root / FILES["manifest"], "\n".join(MANIFEST_MARKERS) + "\n")
    write(root / FILES["survey_gate"], "\n".join(SURVEY_GATE_MARKERS) + "\n")
    write(root / FILES["driver"], "\n".join(DRIVER_MARKERS) + "\n")
    write(root / FILES["verify"], "\n".join(VERIFY_MARKERS) + "\n")
    write(root / FILES["replay"], "\n".join(REPLAY_MARKERS) + "\n")


def run_self_test() -> int:
    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="phase11_bcm2835_platform_plan_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_fixture(fixture_root)
        assert not run_check(fixture_root)

        case_count = 0
        for label, markers in (
            ("plan", PLAN_MARKERS),
            ("survey", SURVEY_MARKERS),
            ("teardown", TEARDOWN_MARKERS),
            ("matrix", MATRIX_MARKERS),
            ("manifest", MANIFEST_MARKERS),
            ("survey_gate", SURVEY_GATE_MARKERS),
            ("driver", DRIVER_MARKERS),
            ("verify", VERIFY_MARKERS),
            ("replay", REPLAY_MARKERS),
        ):
            for idx, marker in enumerate(markers):
                case_count += 1
                case_root = tmpdir / "cases" / f"{label}_{idx}"
                shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
                path = case_root / FILES[label]
                write(path, path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1))
                errors = run_check(case_root)
                assert any(marker in error for error in errors), (label, marker, errors)

        print("PHASE11_BCM2835_PLATFORM_PLAN_SELF_TEST=pass")
        print(f"PHASE11_BCM2835_PLATFORM_PLAN_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    errors = run_check(pathlib.Path(args.root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("PHASE11_BCM2835_PLATFORM_PLAN=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

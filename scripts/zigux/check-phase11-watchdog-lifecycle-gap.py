#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 11 bcm2835 versus dw_wdt lifecycle gap."""

from __future__ import annotations

import argparse
import pathlib
import sys


NOTE_MARKERS = (
    "`bcm2835_wdt` and `dw_wdt`",
    "starter-complete lifecycle-backed slice",
    "platform-registration follow-through open",
    "false parity claim",
)

BCM2835_SURVEY_MARKERS = (
    "the Phase 11 simple-driver roadmap gap is closed at starter depth",
    "The next honest same-lane follow-through is no longer another reminder-surface add.",
)

DW_WDT_PLAN_MARKERS = (
    "The roadmap still keeps this family inside straightforward driver delivery with teardown and failure-mode parity under `drivers/watchdog/*.zig`.",
    "That means the honest next step is still to attach the existing registration-facing handoff to one acquisition-facing platform-registration scaffold without widening into live clock, reset, IRQ, PM, or MMIO behavior.",
)

DW_WDT_MANIFEST_MARKERS = (
    '"lane_key": "P11-L05"',
    '"id": "phase11-dw-wdt-live-mmio-validation"',
    '"status": "ready_next"',
)


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    return [f"{label}: missing {marker}" for marker in markers if marker not in text]


def run_check(repo_root: pathlib.Path) -> list[str]:
    note_text = read_text(
        repo_root / "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md"
    )
    bcm2835_survey_text = read_text(
        repo_root / "Documentation/zigux/phase11-bcm2835-wdt-survey.md"
    )
    dw_wdt_plan_text = read_text(
        repo_root / "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md"
    )
    dw_wdt_manifest_text = read_text(repo_root / "zigux/tests/phase11_dw_wdt_manifest.json")

    errors: list[str] = []
    errors.extend(require_markers("note", note_text, NOTE_MARKERS))
    errors.extend(require_markers("bcm2835_survey", bcm2835_survey_text, BCM2835_SURVEY_MARKERS))
    errors.extend(require_markers("dw_wdt_plan", dw_wdt_plan_text, DW_WDT_PLAN_MARKERS))
    errors.extend(require_markers("dw_wdt_manifest", dw_wdt_manifest_text, DW_WDT_MANIFEST_MARKERS))
    return errors


def run_self_test() -> int:
    note_text = "\n".join(NOTE_MARKERS)
    bcm2835_survey_text = "\n".join(BCM2835_SURVEY_MARKERS)
    dw_wdt_plan_text = "\n".join(DW_WDT_PLAN_MARKERS)
    dw_wdt_manifest_text = "\n".join(DW_WDT_MANIFEST_MARKERS)

    assert not require_markers("note", note_text, NOTE_MARKERS)
    assert not require_markers("bcm2835_survey", bcm2835_survey_text, BCM2835_SURVEY_MARKERS)
    assert not require_markers("dw_wdt_plan", dw_wdt_plan_text, DW_WDT_PLAN_MARKERS)
    assert not require_markers("dw_wdt_manifest", dw_wdt_manifest_text, DW_WDT_MANIFEST_MARKERS)

    assert len(require_markers("note", note_text.replace(NOTE_MARKERS[0], ""), NOTE_MARKERS)) == 1
    assert (
        len(
            require_markers(
                "bcm2835_survey",
                bcm2835_survey_text.replace(BCM2835_SURVEY_MARKERS[1], ""),
                BCM2835_SURVEY_MARKERS,
            )
        )
        == 1
    )
    assert (
        len(
            require_markers(
                "dw_wdt_plan",
                dw_wdt_plan_text.replace(DW_WDT_PLAN_MARKERS[0], ""),
                DW_WDT_PLAN_MARKERS,
            )
        )
        == 1
    )
    assert (
        len(
            require_markers(
                "dw_wdt_manifest",
                dw_wdt_manifest_text.replace(DW_WDT_MANIFEST_MARKERS[2], ""),
                DW_WDT_MANIFEST_MARKERS,
            )
        )
        == 1
    )

    print("PHASE11_WATCHDOG_LIFECYCLE_GAP_SELF_TEST=pass")
    print("PHASE11_WATCHDOG_LIFECYCLE_GAP_SELF_TEST_CASE_COUNT=8")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    errors = run_check(pathlib.Path(args.repo_root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("PHASE11_WATCHDOG_LIFECYCLE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
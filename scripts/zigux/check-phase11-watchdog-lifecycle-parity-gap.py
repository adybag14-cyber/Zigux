#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 11 bcm2835 versus dw_wdt parity gap."""

from __future__ import annotations

import argparse
import pathlib
import sys


NOTE_MARKERS = (
    "`bcm2835_wdt` and `dw_wdt`",
    "bounded current-driver-depth",
    "phase11-dw-wdt-live-mmio-validation` at `ready_next`",
    "false lifecycle-parity claim",
)

BCM2835_SURVEY_MARKERS = (
    "the Phase 11 simple-driver roadmap gap is closed at bounded current-driver depth on `master`",
    "The next honest same-lane follow-through is one explicit manifest-backed closure, slice-note, or teardown-note return",
)

BCM2835_MATRIX_MARKERS = (
    "`PHASE11_BCM2835_WDT_STATUS=driver_proof_and_matrix_packet_truthful`",
    "does not treat absent wider replay, manifest, slice, or teardown-note files as current-head evidence",
)

DW_WDT_SURVEY_MARKERS = (
    "do not rematerialize",
    "The shared `zigux/tests/phase11_build.zig` route remains a shared current-head gap rather than landed evidence in this lane.",
)

DW_WDT_MATRIX_MARKERS = (
    "`PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
    "The next bounded same-lane follow-up remains the manifest-marked ready-next step: hardware-backed MMIO validation",
)

DW_WDT_MANIFEST_MARKERS = (
    '"id": "phase11-dw-wdt-live-mmio-validation"',
    '"status": "ready_next"',
    '"zigux_destination": "zigux/tests/phase11_dw_wdt.zig"',
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
    bcm2835_matrix_text = read_text(
        repo_root / "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
    )
    dw_wdt_survey_text = read_text(
        repo_root / "Documentation/zigux/phase11-dw-wdt-survey.md"
    )
    dw_wdt_matrix_text = read_text(
        repo_root / "Documentation/zigux/phase11-dw-wdt-validation-matrix.md"
    )
    dw_wdt_manifest_text = read_text(repo_root / "zigux/tests/phase11_dw_wdt_manifest.json")

    errors: list[str] = []
    errors.extend(require_markers("note", note_text, NOTE_MARKERS))
    errors.extend(require_markers("bcm2835_survey", bcm2835_survey_text, BCM2835_SURVEY_MARKERS))
    errors.extend(require_markers("bcm2835_matrix", bcm2835_matrix_text, BCM2835_MATRIX_MARKERS))
    errors.extend(require_markers("dw_wdt_survey", dw_wdt_survey_text, DW_WDT_SURVEY_MARKERS))
    errors.extend(require_markers("dw_wdt_matrix", dw_wdt_matrix_text, DW_WDT_MATRIX_MARKERS))
    errors.extend(require_markers("dw_wdt_manifest", dw_wdt_manifest_text, DW_WDT_MANIFEST_MARKERS))
    return errors


def run_self_test() -> int:
    note_text = "\n".join(NOTE_MARKERS)
    bcm2835_survey_text = "\n".join(BCM2835_SURVEY_MARKERS)
    bcm2835_matrix_text = "\n".join(BCM2835_MATRIX_MARKERS)
    dw_wdt_survey_text = "\n".join(DW_WDT_SURVEY_MARKERS)
    dw_wdt_matrix_text = "\n".join(DW_WDT_MATRIX_MARKERS)
    dw_wdt_manifest_text = "\n".join(DW_WDT_MANIFEST_MARKERS)

    assert not require_markers("note", note_text, NOTE_MARKERS)
    assert not require_markers("bcm2835_survey", bcm2835_survey_text, BCM2835_SURVEY_MARKERS)
    assert not require_markers("bcm2835_matrix", bcm2835_matrix_text, BCM2835_MATRIX_MARKERS)
    assert not require_markers("dw_wdt_survey", dw_wdt_survey_text, DW_WDT_SURVEY_MARKERS)
    assert not require_markers("dw_wdt_matrix", dw_wdt_matrix_text, DW_WDT_MATRIX_MARKERS)
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
                "bcm2835_matrix",
                bcm2835_matrix_text.replace(BCM2835_MATRIX_MARKERS[0], ""),
                BCM2835_MATRIX_MARKERS,
            )
        )
        == 1
    )
    assert (
        len(
            require_markers(
                "dw_wdt_survey",
                dw_wdt_survey_text.replace(DW_WDT_SURVEY_MARKERS[1], ""),
                DW_WDT_SURVEY_MARKERS,
            )
        )
        == 1
    )
    assert (
        len(
            require_markers(
                "dw_wdt_matrix",
                dw_wdt_matrix_text.replace(DW_WDT_MATRIX_MARKERS[1], ""),
                DW_WDT_MATRIX_MARKERS,
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

    print("PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP_SELF_TEST=pass")
    print("PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP_SELF_TEST_CASE_COUNT=12")
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

    print("PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

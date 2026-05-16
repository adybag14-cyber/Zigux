#!/usr/bin/env python3
"""Fail-closed checks for the Phase 11 bcm2835 archival watchdog packet."""

from __future__ import annotations

import argparse
import pathlib
import sys


MANIFEST_MARKERS = (
    '"lane_key": "P11-L08"',
    "55568844ac3ce835b0e0bef624c24c17f22b78a1",
)

SURVEY_NOTE_MARKERS = (
    "current scheduled continuity for the same watchdog family is tracked through `P11-L10`",
    "the focused replay `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still passes for the bounded bcm2835 packet on current `master`",
    "this archival watchdog note no longer claims that the whole current shared Phase 11 replay is green",
)

VALIDATION_MATRIX_MARKERS = (
    "PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed",
    "`P11-L08`",
    "`P11-L10`",
    "shared replay boundary: `zig build test --build-file zigux/tests/phase11_build.zig --summary all` still includes `phase11-bcm2835-wdt-tests` and `phase11-bcm2835-wdt-survey-tests`",
)

SURVEY_GATE_MARKERS = (
    'try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "shared replay boundary: `zig build test --build-file zigux/tests/phase11_build.zig --summary all` still includes `phase11-bcm2835-wdt-tests` and `phase11-bcm2835-wdt-survey-tests`") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the focused replay `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still passes for the bounded bcm2835 packet on current `master`") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_doc, "this archival watchdog note no longer claims that the whole current shared Phase 11 replay is green") != null);',
)


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    return [f"{label}: missing {marker}" for marker in markers if marker not in text]


def run_check(repo_root: pathlib.Path) -> list[str]:
    manifest_text = read_text(repo_root / "zigux/tests/phase11_bcm2835_wdt_manifest.json")
    survey_note_text = read_text(repo_root / "Documentation/zigux/phase11-bcm2835-wdt-survey.md")
    validation_matrix_text = read_text(
        repo_root / "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
    )
    survey_gate_text = read_text(repo_root / "zigux/tests/phase11_bcm2835_wdt_survey.zig")

    errors: list[str] = []
    errors.extend(require_markers("manifest", manifest_text, MANIFEST_MARKERS))
    errors.extend(require_markers("survey_note", survey_note_text, SURVEY_NOTE_MARKERS))
    errors.extend(require_markers("validation_matrix", validation_matrix_text, VALIDATION_MATRIX_MARKERS))
    errors.extend(require_markers("survey_gate", survey_gate_text, SURVEY_GATE_MARKERS))
    return errors


def run_self_test() -> int:
    manifest_text = "\n".join(MANIFEST_MARKERS)
    survey_note_text = "\n".join(SURVEY_NOTE_MARKERS)
    validation_matrix_text = "\n".join(VALIDATION_MATRIX_MARKERS)
    survey_gate_text = "\n".join(SURVEY_GATE_MARKERS)

    assert not require_markers("manifest", manifest_text, MANIFEST_MARKERS)
    assert not require_markers("survey_note", survey_note_text, SURVEY_NOTE_MARKERS)
    assert not require_markers("validation_matrix", validation_matrix_text, VALIDATION_MATRIX_MARKERS)
    assert not require_markers("survey_gate", survey_gate_text, SURVEY_GATE_MARKERS)

    assert len(require_markers("manifest", manifest_text.replace(MANIFEST_MARKERS[0], ""), MANIFEST_MARKERS)) == 1
    assert len(
        require_markers(
            "survey_note",
            survey_note_text.replace(SURVEY_NOTE_MARKERS[1], ""),
            SURVEY_NOTE_MARKERS,
        )
    ) == 1
    assert len(
        require_markers(
            "validation_matrix",
            validation_matrix_text.replace(VALIDATION_MATRIX_MARKERS[3], ""),
            VALIDATION_MATRIX_MARKERS,
        )
    ) == 1
    assert len(
        require_markers(
            "survey_gate",
            survey_gate_text.replace(SURVEY_GATE_MARKERS[2], ""),
            SURVEY_GATE_MARKERS,
        )
    ) == 1

    print("self-test passed")
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

    print("phase11 bcm2835 archival packet ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

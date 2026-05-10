#!/usr/bin/env python3
"""Fail-closed checks for the Phase 11 bcm2835 shared replay surface."""

from __future__ import annotations

import argparse
import pathlib
import sys


REQUIRED_BUILD_MARKERS = (
    'b.addTest(.{ .name = "phase11-bcm2835-wdt-tests"',
    'b.addTest(.{ .name = "phase11-bcm2835-wdt-verify-tests"',
    'b.addTest(.{ .name = "phase11-bcm2835-wdt-survey-tests"',
    "test_step.dependOn(&run_phase11_bcm2835_wdt_tests.step);",
    "test_step.dependOn(&run_bcm2835_wdt_verify_tests.step);",
    "test_step.dependOn(&run_phase11_bcm2835_wdt_survey_tests.step);",
)

REQUIRED_WORKFLOW_MARKERS = (
    "python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test",
    "python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py",
    "zig build test --build-file zigux/tests/phase11_build.zig --summary all",
)

REQUIRED_SURVEY_MARKERS = (
    "`phase11-bcm2835-wdt-tests` starter replay",
    "`phase11-bcm2835-wdt-verify-tests` verify replay",
    "`phase11-bcm2835-wdt-survey-tests` survey replay",
    "`make -C zigux phase11` still replays that same shared packet",
)

REQUIRED_MATRIX_MARKERS = (
    "phase11-bcm2835-wdt-tests",
    "phase11-bcm2835-wdt-verify-tests",
    "phase11-bcm2835-wdt-survey-tests",
    "make -C zigux phase11",
)


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> list[str]:
    return [f"{label}: missing {marker}" for marker in markers if marker not in text]


def run_check(repo_root: pathlib.Path) -> list[str]:
    build_text = read_text(repo_root / "zigux/tests/phase11_build.zig")
    workflow_text = read_text(repo_root / ".github/workflows/zigux-bootstrap.yml")
    survey_text = read_text(repo_root / "Documentation/zigux/phase11-bcm2835-wdt-survey.md")
    matrix_text = read_text(
        repo_root / "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
    )

    errors: list[str] = []
    errors.extend(require_markers("phase11_build", build_text, REQUIRED_BUILD_MARKERS))
    errors.extend(require_markers("workflow", workflow_text, REQUIRED_WORKFLOW_MARKERS))
    errors.extend(require_markers("survey_note", survey_text, REQUIRED_SURVEY_MARKERS))
    errors.extend(require_markers("validation_matrix", matrix_text, REQUIRED_MATRIX_MARKERS))
    return errors


def run_self_test() -> int:
    build_text = "\n".join(REQUIRED_BUILD_MARKERS)
    workflow_text = "\n".join(REQUIRED_WORKFLOW_MARKERS)
    survey_text = "\n".join(REQUIRED_SURVEY_MARKERS)
    matrix_text = "\n".join(REQUIRED_MATRIX_MARKERS)

    assert not require_markers("build", build_text, REQUIRED_BUILD_MARKERS)
    assert not require_markers("workflow", workflow_text, REQUIRED_WORKFLOW_MARKERS)
    assert not require_markers("survey", survey_text, REQUIRED_SURVEY_MARKERS)
    assert not require_markers("matrix", matrix_text, REQUIRED_MATRIX_MARKERS)

    missing_build = require_markers("build", build_text.replace(REQUIRED_BUILD_MARKERS[0], ""), REQUIRED_BUILD_MARKERS)
    missing_workflow = require_markers(
        "workflow",
        workflow_text.replace(REQUIRED_WORKFLOW_MARKERS[2], ""),
        REQUIRED_WORKFLOW_MARKERS,
    )
    missing_survey = require_markers(
        "survey",
        survey_text.replace(REQUIRED_SURVEY_MARKERS[1], ""),
        REQUIRED_SURVEY_MARKERS,
    )
    missing_matrix = require_markers(
        "matrix",
        matrix_text.replace(REQUIRED_MATRIX_MARKERS[3], ""),
        REQUIRED_MATRIX_MARKERS,
    )

    assert len(missing_build) == 1
    assert len(missing_workflow) == 1
    assert len(missing_survey) == 1
    assert len(missing_matrix) == 1
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

    print("phase11 bcm2835 shared replay surface ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

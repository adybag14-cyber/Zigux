#!/usr/bin/env python3
"""Fail-closed guard for the direct Phase 11 HVC verify-helper boundary note."""

from __future__ import annotations

import argparse
import pathlib
import tempfile


NOTE_PATH = pathlib.Path("Documentation/zigux/phase11-hvc-verify-helper-boundary.md")
VERIFY_PATH = pathlib.Path("drivers/tty/hvc/hvc_console_verify.zig")
SURVEY_NOTE_PATH = pathlib.Path("Documentation/zigux/phase11-hvc-console-survey.md")
VALIDATION_MATRIX_PATH = pathlib.Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")

REQUIRED_NOTE_MARKERS = (
    "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`",
    "`NotifierUnregisterTimingState.targeted_unregister_request`",
    "`targetless_dispatch_without_notifier`",
    "non-kernel sysrq literal fallback",
)

REQUIRED_VERIFY_MARKERS = (
    "CleanupTrigger.hangup_only",
    "CleanupTrigger.final_close_and_hangup",
    "NotifierUnregisterTimingState.targetless_unregister_request_sanitized",
    "NotifierUnregisterTimingState.targeted_unregister_request",
    "targetless_dispatch_without_notifier",
    "non-kernel sysrq literal fallback",
)

REQUIRED_SURVEY_NOTE_MARKERS = (
    "drivers/tty/hvc/hvc_console_verify.zig",
    "verify-side helper boundaries",
    "targetless notifier no-unregister edge",
)

REQUIRED_VALIDATION_MATRIX_MARKERS = (
    "drivers/tty/hvc/hvc_console_verify.zig",
    "cleanup prerequisite failures",
    "targetless sysrq dispatch from implying notifier callbacks",
)


def require_markers(path: pathlib.Path, markers: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [marker for marker in markers if marker not in text]


def check(root: pathlib.Path) -> list[str]:
    failures: list[str] = []

    for relpath, markers, label in (
        (NOTE_PATH, REQUIRED_NOTE_MARKERS, "note"),
        (VERIFY_PATH, REQUIRED_VERIFY_MARKERS, "verify"),
        (SURVEY_NOTE_PATH, REQUIRED_SURVEY_NOTE_MARKERS, "survey"),
        (VALIDATION_MATRIX_PATH, REQUIRED_VALIDATION_MATRIX_MARKERS, "matrix"),
    ):
        missing = require_markers(root / relpath, markers)
        if missing:
            failures.append(f"{label}:{relpath}:{' | '.join(missing)}")

    return failures


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    base_note = """# Phase 11 HVC Verify Helper Boundary

`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`
`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`
`NotifierUnregisterTimingState.targeted_unregister_request`
`targetless_dispatch_without_notifier`
non-kernel sysrq literal fallback
"""
    base_verify = """CleanupTrigger.hangup_only
CleanupTrigger.final_close_and_hangup
NotifierUnregisterTimingState.targetless_unregister_request_sanitized
NotifierUnregisterTimingState.targeted_unregister_request
targetless_dispatch_without_notifier
non-kernel sysrq literal fallback
"""
    base_survey = """drivers/tty/hvc/hvc_console_verify.zig
verify-side helper boundaries
targetless notifier no-unregister edge
"""
    base_matrix = """drivers/tty/hvc/hvc_console_verify.zig
cleanup prerequisite failures
targetless sysrq dispatch from implying notifier callbacks
"""

    cases = (
        ("missing_note_marker", NOTE_PATH, base_note.replace("non-kernel sysrq literal fallback", "")),
        ("missing_verify_marker", VERIFY_PATH, base_verify.replace("targetless_dispatch_without_notifier", "")),
        ("missing_survey_marker", SURVEY_NOTE_PATH, base_survey.replace("verify-side helper boundaries", "")),
        (
            "missing_matrix_marker",
            VALIDATION_MATRIX_PATH,
            base_matrix.replace("cleanup prerequisite failures", ""),
        ),
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        write(root / NOTE_PATH, base_note)
        write(root / VERIFY_PATH, base_verify)
        write(root / SURVEY_NOTE_PATH, base_survey)
        write(root / VALIDATION_MATRIX_PATH, base_matrix)

        baseline = check(root)
        if baseline:
            raise SystemExit(f"self-test baseline failed: {baseline}")

        for name, relpath, contents in cases:
            write(root / relpath, contents)
            failures = check(root)
            if not failures:
                raise SystemExit(f"self-test case did not fail: {name}")
            write(
                root / relpath,
                {
                    NOTE_PATH: base_note,
                    VERIFY_PATH: base_verify,
                    SURVEY_NOTE_PATH: base_survey,
                    VALIDATION_MATRIX_PATH: base_matrix,
                }[relpath],
            )

    print("PHASE11_HVC_VERIFY_HELPER_BOUNDARY_SELF_TEST=pass cases=4")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    failures = check(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE11_HVC_VERIFY_HELPER_BOUNDARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

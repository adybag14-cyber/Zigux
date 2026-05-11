#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 HVC survey packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "survey_gate": "zigux/tests/phase11_hvc_console_survey.zig",
    "survey_note": "Documentation/zigux/phase11-hvc-console-survey.md",
    "teardown_note": "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "validation_matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "cleanup_replay": "zigux/tests/phase11_hvc_cleanup.zig",
    "verify_helper": "drivers/tty/hvc/hvc_console_verify.zig",
    "sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig",
}

SURVEY_GATE_MARKERS = [
    "Documentation/zigux/phase11-hvc-console-survey.md",
    'test "phase11 hvc console survey manifest records the landed starter and remaining tty gap cleanly"',
    'test "phase11 hvc console survey keeps the shared replay separate but exposes an explicit survey step"',
    'test "phase11 hvc console survey keeps the survey note, slice note, and validation matrix aligned with the parked starter"',
    'test "phase11 hvc console survey keeps bounded exported helper signature proofs"',
    "final-close teardown handoff",
    "notifier-facing handoff",
    "hvc_cleanup() tty-port release handoff summary",
]

SURVEY_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`",
    "Phase 11 simple-production-driver gap has been closed by the bounded starter.",
    "remaining unported work is now tty-driver registration, khvcd worker execution, live sysrq execution, notifier callback execution, and host-backed transport or teardown validation",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "bounded supporting helper",
    "final-close teardown summary",
    "`hvc_cleanup()` tty-port release handoff summary",
    "tiny notifier-add open handoff summary",
    "khvcd worker-entry summary",
    "khvcd sleep-and-reschedule handoff summary",
    "`__hvc_poll` drain-order summary",
    "`hvc_hangup()` disconnect summary",
    "`hvc_remove()` handoff summary",
    "`hvc_kick()` wakeup cue",
    "notifier-IRQ helper surface through `notifier_add_irq()` and `notifier_hangup_irq()`",
    "exported-helper signature proof",
    "It does not claim tty-driver registration, notifier callback execution, khvcd polling execution, live sysrq dispatch, host-backed cleanup, or hardware-validated teardown parity.",
]

TEARDOWN_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`",
    "teardown evidence remains bounded to the landed HVC starter packet",
    "remaining follow-through is still live tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, and host-backed transport or teardown validation",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "final-close teardown boundaries",
    "`hvc_hangup()` disconnect cleanup",
    "`hvc_remove()` slot-release and handoff ordering",
    "`summarizeNotifierAddOutcome()`",
    "bounded sysrq-handling support through `drivers/tty/hvc/hvc_console_sysrq.zig` without claiming live sysrq execution",
    "It does not claim live notifier callback execution, khvcd polling behavior, tty-driver registration, host-backed cleanup, or hardware-validated teardown parity.",
]

VALIDATION_MATRIX_MARKERS = [
    "`PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-hvc-survey` archival route fail-closed",
    "targetless notifier no-unregister edge",
    "stale hangup short-circuit that preserves buffered-write state when the port count is already zero",
    "cleanup tty-port release handoff",
    "notifier callback boundary",
    "khvcd polling contract boundary",
    "`hvc_hangup()` disconnect boundary",
    "keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned whenever the close, cleanup, remove, khvcd polling-contract, or hangup-disconnect ownership story changes",
]

CLEANUP_REPLAY_MARKERS = [
    'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable"',
    'test "phase11 hvc console keeps write-teardown hangup buffering split reviewable"',
    "CleanupRequiresFinalCloseOrHangup",
    "CleanupRequiresTtyPortReference",
    "ConsoleUnavailable",
]

VERIFY_HELPER_MARKERS = [
    'test "hvc_console verify keeps remove handoff explicit when tty teardown outlives console binding"',
    'test "hvc_console verify keeps cleanup prerequisite failures explicit"',
    'test "hvc_console verify keeps open notifier-state failures explicit"',
    'test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks"',
]

SYSRQ_HELPER_MARKERS = [
    "pub const SysrqHandoffRequest",
    "pub const SysrqHandoffSnapshot",
    "pub const keeps_live_sysrq_execution_out_of_scope = true;",
    "pub fn summarizeSysrqHandoff",
    'test "phase11 hvc sysrq handoff keeps live execution out of scope"',
]

SELF_TEST_CASE_COUNT = 10


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
        REQUIRED_FILES["survey_gate"],
        read_text(root, REQUIRED_FILES["survey_gate"]),
        SURVEY_GATE_MARKERS,
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
        REQUIRED_FILES["cleanup_replay"],
        read_text(root, REQUIRED_FILES["cleanup_replay"]),
        CLEANUP_REPLAY_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["verify_helper"],
        read_text(root, REQUIRED_FILES["verify_helper"]),
        VERIFY_HELPER_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["sysrq_helper"],
        read_text(root, REQUIRED_FILES["sysrq_helper"]),
        SYSRQ_HELPER_MARKERS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / REQUIRED_FILES["survey_gate"], "\n".join(SURVEY_GATE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_note"], "\n".join(SURVEY_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["teardown_note"], "\n".join(TEARDOWN_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["validation_matrix"], "\n".join(VALIDATION_MATRIX_MARKERS) + "\n")
    write(root / REQUIRED_FILES["cleanup_replay"], "\n".join(CLEANUP_REPLAY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["verify_helper"], "\n".join(VERIFY_HELPER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["sysrq_helper"], "\n".join(SYSRQ_HELPER_MARKERS) + "\n")


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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_survey_packet_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        gate_missing = tmpdir / REQUIRED_FILES["survey_gate"]
        gate_missing.write_text(
            gate_missing.read_text(encoding="utf-8").replace(
                "hvc_cleanup() tty-port release handoff summary\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "hvc_cleanup() tty-port release handoff summary")

        build_self_test_fixture(tmpdir)
        note_missing = tmpdir / REQUIRED_FILES["survey_note"]
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(
                "exported-helper signature proof\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "exported-helper signature proof")

        build_self_test_fixture(tmpdir)
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(
                "khvcd sleep-and-reschedule handoff summary\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "khvcd sleep-and-reschedule handoff summary")

        build_self_test_fixture(tmpdir)
        teardown_missing = tmpdir / REQUIRED_FILES["teardown_note"]
        teardown_missing.write_text(
            teardown_missing.read_text(encoding="utf-8").replace(
                "`summarizeNotifierAddOutcome()`\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "`summarizeNotifierAddOutcome()`")

        build_self_test_fixture(tmpdir)
        matrix_missing = tmpdir / REQUIRED_FILES["validation_matrix"]
        matrix_missing.write_text(
            matrix_missing.read_text(encoding="utf-8").replace(
                "khvcd polling contract boundary\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "khvcd polling contract boundary")

        build_self_test_fixture(tmpdir)
        cleanup_missing = tmpdir / REQUIRED_FILES["cleanup_replay"]
        cleanup_missing.write_text(
            cleanup_missing.read_text(encoding="utf-8").replace(
                "CleanupRequiresTtyPortReference\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "CleanupRequiresTtyPortReference")

        build_self_test_fixture(tmpdir)
        verify_missing = tmpdir / REQUIRED_FILES["verify_helper"]
        verify_missing.write_text(
            verify_missing.read_text(encoding="utf-8").replace(
                'test "hvc_console verify keeps open notifier-state failures explicit"\n',
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmpdir, 'test "hvc_console verify keeps open notifier-state failures explicit"'
        )

        build_self_test_fixture(tmpdir)
        sysrq_missing = tmpdir / REQUIRED_FILES["sysrq_helper"]
        sysrq_missing.write_text(
            sysrq_missing.read_text(encoding="utf-8").replace(
                "pub fn summarizeSysrqHandoff\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "pub fn summarizeSysrqHandoff")

        build_self_test_fixture(tmpdir)
        shutil.rmtree(tmpdir / "Documentation")
        expect_failure(tmpdir, REQUIRED_FILES["survey_note"])

        print("PHASE11_HVC_SURVEY_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
        print(f"PHASE11_HVC_SURVEY_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_SURVEY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

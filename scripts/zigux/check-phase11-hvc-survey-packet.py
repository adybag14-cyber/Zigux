#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 HVC survey packet."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REQUIRED_FILES = {
    "manifest": "zigux/tests/phase11_hvc_console_manifest.json",
    "survey_gate": "zigux/tests/phase11_hvc_console_survey.zig",
    "survey_note": "Documentation/zigux/phase11-hvc-console-survey.md",
    "slice_note": "Documentation/zigux/phase11-hvc-console-slice.md",
    "teardown_note": "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "validation_matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "modem_control_split": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "poll_retry_split": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "sysrq_helper": "drivers/tty/hvc/hvc_console_sysrq.zig",
    "makefile": "zigux/Makefile",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

SURVEY_GATE_MARKERS = [
    "Documentation/zigux/phase11-hvc-console-survey.md",
    'test "phase11 hvc_console survey manifest records the landed starter and remaining tty gap cleanly"',
    'test "phase11 hvc console survey keeps the shared replay separate but exposes an explicit survey step"',
    'test "phase11 hvc console survey keeps the survey note, slice note, and validation matrix aligned with the parked starter"',
    'test "phase11 hvc console survey keeps bounded exported helper signature proofs"',
    "hvc_cleanup tty-port release handoff",
    "phase11_hvc_console_modem_control_split.zig",
    "phase11_hvc_console_poll_retry_split.zig",
]

SURVEY_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`",
    "* archival landing checkpoint:",
    "Phase 11 simple-production-driver gap has been closed by the bounded starter.",
    "remaining unported work is now tty-driver registration, khvcd worker execution, live sysrq execution, notifier callback execution, and host-backed transport or teardown validation",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "make -C zigux phase11-hvc-survey",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "bounded supporting helper",
    "final-close teardown summary",
    "tiny notifier-add open handoff summary",
    "khvcd worker-entry summary",
    "khvcd sleep-and-reschedule handoff summary",
    "`__hvc_poll` drain-order summary",
    "`hvc_hangup()` disconnect summary",
    "`hvc_remove()` handoff summary",
    "`hvc_cleanup()` tty-port release handoff summary",
    "`hvc_kick()` wakeup cue",
    "notifier-IRQ helper surface through `notifier_add_irq()` and `notifier_hangup_irq()`",
    "exported-helper signature proof",
    "`tiocmget` and `tiocmset` fallback coverage when `hv_ops` modem-control callbacks are absent",
    "`tiocmset` mask handling stays distinct even when `tiocmget` falls back",
    "sysrq toggle handoff stays distinct from literal fallback on the primary console",
    "pending sysrq dispatch stays separate from ordinary poll bytes",
    "non-kernel `^O` input stays a literal byte without toggling sysrq state",
    "sysrq handoff stays unavailable after teardown",
    "It does not claim tty-driver registration, notifier callback execution, khvcd polling execution, live sysrq dispatch, host-backed cleanup, or hardware-validated teardown parity.",
]

SLICE_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_SLICE_STATUS=starter_packet_archived`",
    "lane: `P11-L16`",
    "keep the landed teardown and failure-mode packet readable beside the shared Phase 11 replay route",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-teardown-note.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "These archival packet surfaces keep the bounded starter's teardown and failure-mode story reviewable without claiming a missing compile-local verify helper or cleanup replay.",
]

SLICE_NOTE_FORBIDDEN_MARKERS = [
    "drivers/tty/hvc/hvc_console_verify.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
]

TEARDOWN_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`",
    "teardown evidence remains bounded to the landed HVC starter packet",
    "remaining follow-through is still live tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, and host-backed transport or teardown validation",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "make -C zigux phase11-hvc-survey",
    "final-close teardown boundaries",
    "`hvc_cleanup()` tty-port release handoff",
    "`hvc_hangup()` disconnect cleanup",
    "`hvc_remove()` slot-release and handoff ordering",
    "notifier-facing teardown edges beside `summarizeNotifierAddOutcome()`",
    "bounded sysrq-handling support through `drivers/tty/hvc/hvc_console_sysrq.zig` without claiming live sysrq execution",
    "poll-retry and drain-order split",
    "modem-control fallback split",
    "tty detachment",
    "HUPCL-gated modem-line shutdown",
    "notifier ownership",
    "resize-work cancellation",
    "wait-until-sent intent",
    "buffered-write clearing",
    "stale hangup short-circuit behavior",
    "keep-IRQ-until-hangup teardown boundaries",
    "It does not claim live notifier callback execution, khvcd polling behavior, tty-driver registration, host-backed cleanup, or hardware-validated teardown parity.",
]

VALIDATION_MATRIX_MARKERS = [
    "`PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`",
    "- archival landing checkpoint:",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-hvc-survey` archival route fail-closed",
    "targetless notifier no-unregister edge",
    "cleanup tty-port release handoff",
    "notifier callback boundary",
    "`hvc_hangup()` disconnect boundary",
    "`summarizeNotifierAddOutcome()`",
    "`hvc_hangup()` disconnect evidence stays explicit through the survey gate, the teardown note, and this matrix",
    "tty-resize cancellation",
    "stale-count short-circuit behavior",
    "buffered-write clearing",
    "notifier_hangup boundary",
    "Current `master` still does not materialize direct `drivers/tty/hvc/hvc_console_verify.zig` or `zigux/tests/phase11_hvc_console.zig` companions, so keep those paths framed as repo-reality gaps rather than as shipped archival replay evidence.",
    "the shared Phase 11 reminder packet should treat missing direct `drivers/tty/hvc/hvc_console_verify.zig` and `zigux/tests/phase11_hvc_console.zig` companions as repo-reality gaps instead of reading the archival HVC packet as a direct verify-and-replay pair",
    "keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned whenever the close, remove, notifier-add, khvcd polling-contract, or hangup-disconnect ownership story changes",
    "host-free khvcd, notifier, remove, or cleanup handoff",
]

MODEM_CONTROL_SPLIT_MARKERS = [
    'test "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks"',
    'test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back"',
]

POLL_RETRY_SPLIT_MARKERS = [
    'test "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep"',
    'test "phase11 hvc console keeps partial write progress distinct from stalled __hvc_poll retries"',
    'test "phase11 hvc console keeps sysrq toggle handoff distinct from literal fallback on the primary console"',
    'test "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes"',
    'test "phase11 hvc console keeps non-kernel ^O as a literal byte without toggling sysrq state"',
    'test "phase11 hvc console keeps sysrq handoff unavailable after teardown"',
]

SYSRQ_HELPER_MARKERS = [
    "pub const SysrqHandoffRequest",
    "pub const SysrqHandoffSnapshot",
    "pub const keeps_live_sysrq_execution_out_of_scope = true;",
    "pub fn summarizeSysrqHandoff",
    'test "phase11 hvc sysrq handoff keeps live execution out of scope"',
]

MAKEFILE_MARKERS = [
    "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
    "phase11-hvc-survey:",
    "phase11: phase11-contract phase11-test phase11-hvc-survey",
]

WORKFLOW_MARKERS = [
    "- name: Run Phase 11 shared replay contract checker",
    "run: make -C zigux phase11-contract",
    "- name: Run Phase 11 watchdog and console tests",
    "run: zig build test --build-file zigux/tests/phase11_build.zig --summary all",
    "- name: Run dedicated Phase 11 hvc survey replay",
    "run: make -C zigux phase11-hvc-survey",
]

SELF_TEST_CASE_COUNT = 24


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


def expect_forbidden_markers_absent(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            raise CheckError(f"forbidden marker present in {relative_path}: {marker}")


def is_hex_commit(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(ch in "0123456789abcdef" for ch in value)
    )


def load_manifest(root: Path) -> dict[str, object]:
    manifest_text = read_text(root, REQUIRED_FILES["manifest"])
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {REQUIRED_FILES['manifest']}: {exc}") from exc

    surveyed_commit = manifest.get("surveyed_commit")
    if not is_hex_commit(surveyed_commit):
        raise CheckError(
            f"invalid surveyed_commit in {REQUIRED_FILES['manifest']}: {surveyed_commit!r}"
        )
    return manifest


def expect_surveyed_commit_provenance(
    surveyed_commit: str,
    survey_note: str,
    validation_matrix: str,
) -> None:
    if surveyed_commit not in survey_note:
        raise CheckError(
            f"missing surveyed_commit provenance in {REQUIRED_FILES['survey_note']}: {surveyed_commit}"
        )
    if surveyed_commit not in validation_matrix:
        raise CheckError(
            f"missing surveyed_commit provenance in {REQUIRED_FILES['validation_matrix']}: {surveyed_commit}"
        )


def expect_git_commit_exists(root: Path, surveyed_commit: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", f"{surveyed_commit}^{{commit}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CheckError(
            f"missing git commit for surveyed_commit in {REQUIRED_FILES['manifest']}: {surveyed_commit}"
        )


def run_check(root: Path) -> None:
    manifest = load_manifest(root)
    survey_note = read_text(root, REQUIRED_FILES["survey_note"])
    validation_matrix = read_text(root, REQUIRED_FILES["validation_matrix"])
    expect_surveyed_commit_provenance(
        manifest["surveyed_commit"],
        survey_note,
        validation_matrix,
    )
    expect_git_commit_exists(root, manifest["surveyed_commit"])
    expect_markers(
        REQUIRED_FILES["survey_gate"],
        read_text(root, REQUIRED_FILES["survey_gate"]),
        SURVEY_GATE_MARKERS,
    )
    expect_markers(REQUIRED_FILES["survey_note"], survey_note, SURVEY_NOTE_MARKERS)
    slice_note = read_text(root, REQUIRED_FILES["slice_note"])
    expect_markers(REQUIRED_FILES["slice_note"], slice_note, SLICE_NOTE_MARKERS)
    expect_forbidden_markers_absent(
        REQUIRED_FILES["slice_note"],
        slice_note,
        SLICE_NOTE_FORBIDDEN_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["teardown_note"],
        read_text(root, REQUIRED_FILES["teardown_note"]),
        TEARDOWN_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["validation_matrix"],
        validation_matrix,
        VALIDATION_MATRIX_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["modem_control_split"],
        read_text(root, REQUIRED_FILES["modem_control_split"]),
        MODEM_CONTROL_SPLIT_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["poll_retry_split"],
        read_text(root, REQUIRED_FILES["poll_retry_split"]),
        POLL_RETRY_SPLIT_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["sysrq_helper"],
        read_text(root, REQUIRED_FILES["sysrq_helper"]),
        SYSRQ_HELPER_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["makefile"],
        read_text(root, REQUIRED_FILES["makefile"]),
        MAKEFILE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["workflow"],
        read_text(root, REQUIRED_FILES["workflow"]),
        WORKFLOW_MARKERS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_self_test_repo(root: Path) -> str:
    subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.name", "Zigux Builder"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "zigux-builder@example.com"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(root), "commit", "-m", "self-test fixture"],
        check=True,
        capture_output=True,
        text=True,
    )
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return commit.stdout.strip()


def build_manifest_text(surveyed_commit: str) -> str:
    manifest = {
        "lane_key": "P11-L16",
        "phase": "Phase 11",
        "surveyed_commit": surveyed_commit,
        "anchor": "drivers/tty/hvc/hvc_console.c",
    }
    return json.dumps(manifest, indent=2) + "\n"


def build_self_test_fixture(root: Path, surveyed_commit: str = "0" * 40) -> None:
    write(root / REQUIRED_FILES["manifest"], build_manifest_text(surveyed_commit))
    write(root / REQUIRED_FILES["survey_gate"], "\n".join(SURVEY_GATE_MARKERS) + "\n")
    write(
        root / REQUIRED_FILES["survey_note"],
        "\n".join(SURVEY_NOTE_MARKERS + [surveyed_commit]) + "\n",
    )
    write(root / REQUIRED_FILES["slice_note"], "\n".join(SLICE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["teardown_note"], "\n".join(TEARDOWN_NOTE_MARKERS) + "\n")
    write(
        root / REQUIRED_FILES["validation_matrix"],
        "\n".join(VALIDATION_MATRIX_MARKERS + [surveyed_commit]) + "\n",
    )
    write(root / REQUIRED_FILES["modem_control_split"], "\n".join(MODEM_CONTROL_SPLIT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["poll_retry_split"], "\n".join(POLL_RETRY_SPLIT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["sysrq_helper"], "\n".join(SYSRQ_HELPER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["makefile"], "\n".join(MAKEFILE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["workflow"], "\n".join(WORKFLOW_MARKERS) + "\n")


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


def reset_fixture(root: Path) -> str:
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    build_self_test_fixture(root)
    commit = init_self_test_repo(root)
    write(root / REQUIRED_FILES["manifest"], build_manifest_text(commit))
    write(
        root / REQUIRED_FILES["survey_note"],
        "\n".join(SURVEY_NOTE_MARKERS + [commit]) + "\n",
    )
    write(
        root / REQUIRED_FILES["validation_matrix"],
        "\n".join(VALIDATION_MATRIX_MARKERS + [commit]) + "\n",
    )
    return commit


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_survey_packet_"))
    try:
        commit = reset_fixture(tmpdir)
        run_check(tmpdir)

        gate_missing = tmpdir / REQUIRED_FILES["survey_gate"]
        gate_missing.write_text(
            gate_missing.read_text(encoding="utf-8").replace(
                "phase11_hvc_console_poll_retry_split.zig\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase11_hvc_console_poll_retry_split.zig")

        commit = reset_fixture(tmpdir)
        note_missing = tmpdir / REQUIRED_FILES["survey_note"]
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(commit + "\n", ""),
            encoding="utf-8",
        )
        expect_failure(tmpdir, REQUIRED_FILES["survey_note"])

        reset_fixture(tmpdir)
        note_missing = tmpdir / REQUIRED_FILES["survey_note"]
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(
                "`hvc_kick()` wakeup cue\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "`hvc_kick()` wakeup cue")

        reset_fixture(tmpdir)
        note_missing = tmpdir / REQUIRED_FILES["survey_note"]
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(
                "`tiocmset` mask handling stays distinct even when `tiocmget` falls back\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmpdir,
            "`tiocmset` mask handling stays distinct even when `tiocmget` falls back",
        )

        reset_fixture(tmpdir)
        note_missing = tmpdir / REQUIRED_FILES["survey_note"]
        note_missing.write_text(
            note_missing.read_text(encoding="utf-8").replace(
                "pending sysrq dispatch stays separate from ordinary poll bytes\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "pending sysrq dispatch stays separate from ordinary poll bytes")

        reset_fixture(tmpdir)
        slice_missing = tmpdir / REQUIRED_FILES["slice_note"]
        slice_missing.write_text(
            slice_missing.read_text(encoding="utf-8").replace(
                "drivers/tty/hvc/hvc_console_sysrq.zig\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "drivers/tty/hvc/hvc_console_sysrq.zig")

        reset_fixture(tmpdir)
        slice_forbidden = tmpdir / REQUIRED_FILES["slice_note"]
        slice_forbidden.write_text(
            slice_forbidden.read_text(encoding="utf-8")
            + "drivers/tty/hvc/hvc_console_verify.zig\n",
            encoding="utf-8",
        )
        expect_failure(tmpdir, "drivers/tty/hvc/hvc_console_verify.zig")

        reset_fixture(tmpdir)
        teardown_missing = tmpdir / REQUIRED_FILES["teardown_note"]
        teardown_missing.write_text(
            teardown_missing.read_text(encoding="utf-8").replace(
                "poll-retry and drain-order split\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "poll-retry and drain-order split")

        reset_fixture(tmpdir)
        teardown_missing = tmpdir / REQUIRED_FILES["teardown_note"]
        teardown_missing.write_text(
            teardown_missing.read_text(encoding="utf-8").replace(
                "wait-until-sent intent\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "wait-until-sent intent")

        reset_fixture(tmpdir)
        teardown_missing = tmpdir / REQUIRED_FILES["teardown_note"]
        teardown_missing.write_text(
            teardown_missing.read_text(encoding="utf-8").replace(
                "keep-IRQ-until-hangup teardown boundaries\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "keep-IRQ-until-hangup teardown boundaries")

        reset_fixture(tmpdir)
        matrix_missing = tmpdir / REQUIRED_FILES["validation_matrix"]
        matrix_missing.write_text(
            matrix_missing.read_text(encoding="utf-8").replace(
                "notifier_hangup boundary\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "notifier_hangup boundary")

        reset_fixture(tmpdir)
        matrix_missing = tmpdir / REQUIRED_FILES["validation_matrix"]
        matrix_missing.write_text(
            matrix_missing.read_text(encoding="utf-8").replace(
                "the shared Phase 11 reminder packet should treat missing direct `drivers/tty/hvc/hvc_console_verify.zig` and `zigux/tests/phase11_hvc_console.zig` companions as repo-reality gaps instead of reading the archival HVC packet as a direct verify-and-replay pair\n",
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmpdir,
            "the shared Phase 11 reminder packet should treat missing direct `drivers/tty/hvc/hvc_console_verify.zig` and `zigux/tests/phase11_hvc_console.zig` companions as repo-reality gaps instead of reading the archival HVC packet as a direct verify-and-replay pair",
        )

        reset_fixture(tmpdir)
        modem_missing = tmpdir / REQUIRED_FILES["modem_control_split"]
        modem_missing.write_text(
            modem_missing.read_text(encoding="utf-8").replace(
                'test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back"\n',
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmpdir,
            'test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back"',
        )

        reset_fixture(tmpdir)
        poll_missing = tmpdir / REQUIRED_FILES["poll_retry_split"]
        poll_missing.write_text(
            poll_missing.read_text(encoding="utf-8").replace(
                'test "phase11 hvc console keeps sysrq handoff unavailable after teardown"\n',
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmpdir,
            'test "phase11 hvc console keeps sysrq handoff unavailable after teardown"',
        )

        reset_fixture(tmpdir)
        sysrq_missing = tmpdir / REQUIRED_FILES["sysrq_helper"]
        sysrq_missing.write_text(
            sysrq_missing.read_text(encoding="utf-8").replace(
                "pub fn summarizeSysrqHandoff\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "pub fn summarizeSysrqHandoff")

        reset_fixture(tmpdir)
        makefile_missing = tmpdir / REQUIRED_FILES["makefile"]
        makefile_missing.write_text(
            makefile_missing.read_text(encoding="utf-8").replace(
                "phase11-hvc-survey:\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase11-hvc-survey:")

        reset_fixture(tmpdir)
        workflow_missing = tmpdir / REQUIRED_FILES["workflow"]
        workflow_missing.write_text(
            workflow_missing.read_text(encoding="utf-8").replace(
                "run: make -C zigux phase11-hvc-survey\n", ""
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "run: make -C zigux phase11-hvc-survey")

        reset_fixture(tmpdir)
        manifest_missing = tmpdir / REQUIRED_FILES["manifest"]
        manifest_missing.unlink()
        expect_failure(tmpdir, REQUIRED_FILES["manifest"])

        reset_fixture(tmpdir)
        bad_manifest = tmpdir / REQUIRED_FILES["manifest"]
        bad_manifest.write_text(build_manifest_text("z" * 40), encoding="utf-8")
        expect_failure(tmpdir, "invalid surveyed_commit")

        reset_fixture(tmpdir)
        fake_commit = "1" * 40
        write(tmpdir / REQUIRED_FILES["manifest"], build_manifest_text(fake_commit))
        write(
            tmpdir / REQUIRED_FILES["survey_note"],
            "\n".join(SURVEY_NOTE_MARKERS + [fake_commit]) + "\n",
        )
        write(
            tmpdir / REQUIRED_FILES["validation_matrix"],
            "\n".join(VALIDATION_MATRIX_MARKERS + [fake_commit]) + "\n",
        )
        expect_failure(tmpdir, "missing git commit for surveyed_commit")

        reset_fixture(tmpdir)
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

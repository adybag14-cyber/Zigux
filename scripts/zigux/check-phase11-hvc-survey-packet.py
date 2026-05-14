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
    "build_inventory": "zigux/tests/fixtures/phase11_build_inventory.json",
    "driver_starter": "drivers/tty/hvc/hvc_console.zig",
    "verify_helper": "drivers/tty/hvc/hvc_console_verify.zig",
    "survey_gate": "zigux/tests/phase11_hvc_console_survey.zig",
    "console_replay": "zigux/tests/phase11_hvc_console.zig",
    "cleanup_replay": "zigux/tests/phase11_hvc_cleanup.zig",
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

PRESENT_DIRECT_COMPANION_MARKER = (
    "Current `master` also materializes direct "
    "`drivers/tty/hvc/hvc_console_verify.zig`, "
    "`zigux/tests/phase11_hvc_console.zig`, and "
    "`zigux/tests/phase11_hvc_cleanup.zig` companions."
)

ABSENT_DIRECT_COMPANION_MARKER = (
    "Current `master` still ships no separate direct "
    "`drivers/tty/hvc/hvc_console_verify.zig`, "
    "`zigux/tests/phase11_hvc_console.zig`, or "
    "`zigux/tests/phase11_hvc_cleanup.zig` companions"
)

ABSENT_DIRECT_COMPANION_MATRIX_MARKER = (
    "The still-absent direct `drivers/tty/hvc/hvc_console_verify.zig`, "
    "`zigux/tests/phase11_hvc_console.zig`, and "
    "`zigux/tests/phase11_hvc_cleanup.zig` companions remain repo-reality gaps."
)

BUILD_INVENTORY_MARKERS = [
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
    "../../drivers/tty/hvc/hvc_console_verify.zig",
    "phase11_hvc_console.zig",
    "phase11_hvc_cleanup.zig",
    "phase11_hvc_console_survey.zig",
]

SURVEY_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "make -C zigux phase11-hvc-survey",
    PRESENT_DIRECT_COMPANION_MARKER,
    "Phase 11 simple-production-driver gap has been closed by the bounded starter.",
    "bounded supporting helper",
    "tiny notifier-add open handoff summary",
    "khvcd worker-entry summary",
    "khvcd sleep-and-reschedule handoff summary",
    "`__hvc_poll` drain-order summary",
    "`hvc_kick()` wakeup cue",
    "notifier-IRQ helper surface",
    "`hvc_cleanup()` tty-port release handoff summary",
]

SLICE_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_SLICE_STATUS=starter_packet_archived`",
    "lane: `P11-L16`",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    PRESENT_DIRECT_COMPANION_MARKER,
    "`hvc_cleanup()` tty-port release handoff summary",
    "port-reference drop timing",
    "cleanup-time tty-port ownership",
    "tiny notifier-add open handoff summary",
    "khvcd polling-contract summary",
    "`hvc_hangup()` disconnect summary",
    "`hvc_kick()` wakeup cue",
    "notifier-IRQ helper surface",
]

TEARDOWN_NOTE_MARKERS = [
    "* `PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/phase11_hvc_cleanup.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-slice.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    "make -C zigux phase11-hvc-survey",
    PRESENT_DIRECT_COMPANION_MARKER,
    "final-close teardown boundaries and close-wait ownership",
    "`hvc_cleanup()` tty-port release handoff and cleanup-time tty-port ownership",
    "`hvc_hangup()` disconnect cleanup wording",
    "`hvc_remove()` slot-release and handoff ordering",
    "`summarizeNotifierAddOutcome()`",
    "wait-until-sent intent",
    "keep-IRQ-until-hangup teardown boundaries",
    "tty detachment",
    "HUPCL-gated modem-line shutdown",
    "notifier ownership",
    "resize-work cancellation",
    "buffered-write clearing",
    "stale hangup short-circuit behavior",
]

VALIDATION_MATRIX_MARKERS = [
    "`PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`zigux/tests/phase11_hvc_console.zig`",
    "`zigux/tests/phase11_hvc_cleanup.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "the dedicated archival replay remains separate through `make -C zigux phase11-hvc-survey`",
    "`make -C zigux phase11-hvc-survey` archival route fail-closed",
    PRESENT_DIRECT_COMPANION_MARKER,
    "khvcd polling-contract summary",
    "khvcd worker-entry summary",
    "`hvc_hangup()` disconnect summary",
    "targetless notifier no-unregister edge",
    "`hvc_cleanup()` tty-port release handoff",
    "`hvc_remove()` handoff",
    "`summarizeNotifierAddOutcome()`",
    "`drivers/tty/hvc/hvc_console_sysrq.zig`",
    "host-free khvcd, notifier, remove, or cleanup handoff",
]

DRIVER_STARTER_MARKERS = [
    "pub const CloseTeardownRequest = struct {",
    "pub fn summarizeCloseTeardown",
    "pub const TtyRegistrationRequest = struct {",
    "pub fn summarizeTtyRegistrationHandoff",
    "pub const NotifierAddRequest = struct {",
    "pub fn summarizeNotifierAddOutcome",
    "pub const KhvcdPollingContractRequest = struct {",
    "pub fn summarizeKhvcdPollingContract",
    "pub const KhvcdWorkerEntryRequest = struct {",
    "pub fn summarizeKhvcdWorkerEntry",
    "pub const CleanupHandoffRequest = struct {",
    "pub fn summarizeCleanupHandoff",
    "pub fn hvc_kick() void {}",
]

VERIFY_HELPER_MARKERS = [
    'test "hvc_console verify keeps remove handoff explicit when tty is already absent" {',
    'test "hvc_console verify keeps cleanup prerequisite failures explicit" {',
    'test "hvc_console verify keeps notifier unregister timing false for never-registered and targetless surfaces" {',
    'test "hvc_console verify keeps targetless sysrq dispatch from implying notifier callbacks" {',
]

SURVEY_GATE_MARKERS = [
    'test "phase11 hvc_console survey manifest records the landed starter and remaining tty gap cleanly"',
    'test "phase11 hvc_console survey keeps the dedicated archival packet explicit"',
    'test "phase11 hvc console survey keeps the shared replay separate but exposes an explicit survey step"',
    'test "phase11 hvc console survey keeps the survey note, slice note, and validation matrix aligned with the parked starter"',
    "try std.testing.expect(!manifest.survey_summary.hvc_console_test_present);",
]

CONSOLE_REPLAY_MARKERS = [
    'test "phase11 hvc console keeps tty-registration handoff boundaries reviewable" {',
    'test "phase11 hvc console keeps sysrq handoff boundaries reviewable" {',
    'test "phase11 hvc console keeps notifier handoff boundaries reviewable" {',
]

CLEANUP_REPLAY_MARKERS = [
    'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {',
    "try std.testing.expect(hangup_cleanup.drops_tty_port_reference);",
    "try std.testing.expectError(error.CleanupRequiresFinalCloseOrHangup, console.summarizeCleanupHandoff(.{",
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
    "pub fn summarizeSysrqHandoff",
]

MAKEFILE_MARKERS = [
    "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
    "phase11-test:",
    "phase11-hvc-survey:",
    "phase11: phase11-contract phase11-test phase11-hvc-survey",
]

WORKFLOW_MARKERS = [
    "- name: Run Phase 11 shared replay contract checker",
    "run: make -C zigux phase11-contract",
    "- name: Run dedicated Phase 11 hvc survey replay",
    "run: make -C zigux phase11-hvc-survey",
]


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
    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        raise CheckError("missing survey_summary in manifest")
    if summary.get("hvc_console_test_present") is not False:
        raise CheckError("expected hvc_console_test_present to stay false")
    return manifest


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
    surveyed_commit = manifest["surveyed_commit"]
    expect_git_commit_exists(root, surveyed_commit)

    survey_note = read_text(root, REQUIRED_FILES["survey_note"])
    slice_note = read_text(root, REQUIRED_FILES["slice_note"])
    teardown_note = read_text(root, REQUIRED_FILES["teardown_note"])
    validation_matrix = read_text(root, REQUIRED_FILES["validation_matrix"])

    if surveyed_commit not in survey_note:
        raise CheckError(
            f"missing surveyed_commit provenance in {REQUIRED_FILES['survey_note']}: {surveyed_commit}"
        )
    if surveyed_commit not in validation_matrix:
        raise CheckError(
            f"missing surveyed_commit provenance in {REQUIRED_FILES['validation_matrix']}: {surveyed_commit}"
        )

    expect_markers(REQUIRED_FILES["build_inventory"], read_text(root, REQUIRED_FILES["build_inventory"]), BUILD_INVENTORY_MARKERS)
    expect_markers(REQUIRED_FILES["driver_starter"], read_text(root, REQUIRED_FILES["driver_starter"]), DRIVER_STARTER_MARKERS)
    expect_markers(REQUIRED_FILES["verify_helper"], read_text(root, REQUIRED_FILES["verify_helper"]), VERIFY_HELPER_MARKERS)
    expect_markers(REQUIRED_FILES["survey_gate"], read_text(root, REQUIRED_FILES["survey_gate"]), SURVEY_GATE_MARKERS)
    expect_markers(REQUIRED_FILES["console_replay"], read_text(root, REQUIRED_FILES["console_replay"]), CONSOLE_REPLAY_MARKERS)
    expect_markers(REQUIRED_FILES["cleanup_replay"], read_text(root, REQUIRED_FILES["cleanup_replay"]), CLEANUP_REPLAY_MARKERS)
    expect_markers(REQUIRED_FILES["survey_note"], survey_note, SURVEY_NOTE_MARKERS)
    expect_markers(REQUIRED_FILES["slice_note"], slice_note, SLICE_NOTE_MARKERS)
    expect_markers(REQUIRED_FILES["teardown_note"], teardown_note, TEARDOWN_NOTE_MARKERS)
    expect_markers(REQUIRED_FILES["validation_matrix"], validation_matrix, VALIDATION_MATRIX_MARKERS)
    expect_markers(REQUIRED_FILES["modem_control_split"], read_text(root, REQUIRED_FILES["modem_control_split"]), MODEM_CONTROL_SPLIT_MARKERS)
    expect_markers(REQUIRED_FILES["poll_retry_split"], read_text(root, REQUIRED_FILES["poll_retry_split"]), POLL_RETRY_SPLIT_MARKERS)
    expect_markers(REQUIRED_FILES["sysrq_helper"], read_text(root, REQUIRED_FILES["sysrq_helper"]), SYSRQ_HELPER_MARKERS)
    expect_markers(REQUIRED_FILES["makefile"], read_text(root, REQUIRED_FILES["makefile"]), MAKEFILE_MARKERS)
    expect_markers(REQUIRED_FILES["workflow"], read_text(root, REQUIRED_FILES["workflow"]), WORKFLOW_MARKERS)

    expect_forbidden_markers_absent(REQUIRED_FILES["survey_note"], survey_note, [ABSENT_DIRECT_COMPANION_MARKER])
    expect_forbidden_markers_absent(REQUIRED_FILES["slice_note"], slice_note, [ABSENT_DIRECT_COMPANION_MARKER])
    expect_forbidden_markers_absent(REQUIRED_FILES["teardown_note"], teardown_note, [ABSENT_DIRECT_COMPANION_MARKER])
    expect_forbidden_markers_absent(REQUIRED_FILES["validation_matrix"], validation_matrix, [ABSENT_DIRECT_COMPANION_MATRIX_MARKER])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_manifest_text(surveyed_commit: str) -> str:
    manifest = {
        "lane_key": "P11-L16",
        "phase": "Phase 11",
        "surveyed_commit": surveyed_commit,
        "anchor": "drivers/tty/hvc/hvc_console.c",
        "survey_summary": {
            "hvc_console_test_present": False,
        },
    }
    return json.dumps(manifest, indent=2) + "\n"


def build_fixture(root: Path, surveyed_commit: str) -> None:
    write(root / REQUIRED_FILES["manifest"], build_manifest_text(surveyed_commit))
    write(root / REQUIRED_FILES["build_inventory"], "\n".join(BUILD_INVENTORY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["driver_starter"], "\n".join(DRIVER_STARTER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["verify_helper"], "\n".join(VERIFY_HELPER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_gate"], "\n".join(SURVEY_GATE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["console_replay"], "\n".join(CONSOLE_REPLAY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["cleanup_replay"], "\n".join(CLEANUP_REPLAY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_note"], "\n".join(SURVEY_NOTE_MARKERS + [surveyed_commit]) + "\n")
    write(root / REQUIRED_FILES["slice_note"], "\n".join(SLICE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["teardown_note"], "\n".join(TEARDOWN_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["validation_matrix"], "\n".join(VALIDATION_MATRIX_MARKERS + [surveyed_commit]) + "\n")
    write(root / REQUIRED_FILES["modem_control_split"], "\n".join(MODEM_CONTROL_SPLIT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["poll_retry_split"], "\n".join(POLL_RETRY_SPLIT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["sysrq_helper"], "\n".join(SYSRQ_HELPER_MARKERS) + "\n")
    write(root / REQUIRED_FILES["makefile"], "\n".join(MAKEFILE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["workflow"], "\n".join(WORKFLOW_MARKERS) + "\n")


def init_fixture_repo(root: Path) -> str:
    subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Zigux Builder"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "zigux-builder@example.com"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "commit", "-m", "fixture"], check=True, capture_output=True, text=True)
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def reset_fixture(root: Path) -> str:
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    build_fixture(root, "0" * 40)
    commit = init_fixture_repo(root)
    build_fixture(root, commit)
    return commit


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_packet_"))
    try:
        commit = reset_fixture(tmpdir)
        run_check(tmpdir)

        missing_marker_cases = [
            (REQUIRED_FILES["build_inventory"], BUILD_INVENTORY_MARKERS[3]),
            (REQUIRED_FILES["build_inventory"], BUILD_INVENTORY_MARKERS[-1]),
            (REQUIRED_FILES["verify_helper"], VERIFY_HELPER_MARKERS[1]),
            (REQUIRED_FILES["survey_note"], PRESENT_DIRECT_COMPANION_MARKER),
            (REQUIRED_FILES["survey_note"], "khvcd sleep-and-reschedule handoff summary"),
            (REQUIRED_FILES["survey_note"], "`__hvc_poll` drain-order summary"),
            (REQUIRED_FILES["slice_note"], PRESENT_DIRECT_COMPANION_MARKER),
            (REQUIRED_FILES["teardown_note"], PRESENT_DIRECT_COMPANION_MARKER),
            (REQUIRED_FILES["teardown_note"], "tty detachment"),
            (REQUIRED_FILES["teardown_note"], "HUPCL-gated modem-line shutdown"),
            (REQUIRED_FILES["teardown_note"], "stale hangup short-circuit behavior"),
            (REQUIRED_FILES["validation_matrix"], PRESENT_DIRECT_COMPANION_MARKER),
            (REQUIRED_FILES["survey_gate"], 'try std.testing.expect(!manifest.survey_summary.hvc_console_test_present);'),
            (REQUIRED_FILES["console_replay"], CONSOLE_REPLAY_MARKERS[-1]),
            (REQUIRED_FILES["cleanup_replay"], CLEANUP_REPLAY_MARKERS[-1]),
            (REQUIRED_FILES["makefile"], "phase11-hvc-survey:"),
            (REQUIRED_FILES["workflow"], "run: make -C zigux phase11-hvc-survey"),
        ]
        for relative_path, marker in missing_marker_cases:
            reset_fixture(tmpdir)
            path = tmpdir / relative_path
            text = path.read_text(encoding="utf-8").replace(marker, "", 1)
            path.write_text(text, encoding="utf-8")
            expect_failure(tmpdir, marker)

        stale_cases = [
            (REQUIRED_FILES["survey_note"], ABSENT_DIRECT_COMPANION_MARKER),
            (REQUIRED_FILES["slice_note"], ABSENT_DIRECT_COMPANION_MARKER),
            (REQUIRED_FILES["teardown_note"], ABSENT_DIRECT_COMPANION_MARKER),
            (REQUIRED_FILES["validation_matrix"], ABSENT_DIRECT_COMPANION_MATRIX_MARKER),
        ]
        for relative_path, stale_marker in stale_cases:
            reset_fixture(tmpdir)
            path = tmpdir / relative_path
            text = path.read_text(encoding="utf-8") + stale_marker + "\n"
            path.write_text(text, encoding="utf-8")
            expect_failure(tmpdir, stale_marker)

        reset_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["verify_helper"]).unlink()
        expect_failure(tmpdir, f"missing required file: {REQUIRED_FILES['verify_helper']}")

        reset_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["manifest"]).write_text(build_manifest_text("z" * 40), encoding="utf-8")
        expect_failure(tmpdir, "invalid surveyed_commit")

        reset_fixture(tmpdir)
        manifest = json.loads((tmpdir / REQUIRED_FILES["manifest"]).read_text(encoding="utf-8"))
        manifest["survey_summary"]["hvc_console_test_present"] = True
        (tmpdir / REQUIRED_FILES["manifest"]).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmpdir, "expected hvc_console_test_present to stay false")

        case_count = len(missing_marker_cases) + len(stale_cases) + 3
        print("PHASE11_HVC_SURVEY_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_COMMIT={commit}")
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

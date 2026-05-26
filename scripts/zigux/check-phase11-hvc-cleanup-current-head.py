#!/usr/bin/env python3
"""Fail-close guard for the current-head Phase 11 HVC cleanup packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
COMPANION_PATH = Path("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md")
VERIFY_PATH = Path("Documentation/zigux/phase11-hvc-verify-helper-boundary.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
DRIVER_PATH = Path("drivers/tty/hvc/hvc_console.zig")
VERIFY_HELPER_SOURCE_PATH = Path("drivers/tty/hvc/hvc_console_verify.zig")
PROOF_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig")
BUILD_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")
MODEM_CONTROL_PROOF_PATH = Path("zigux/tests/phase11_hvc_modem_control_proof.zig")
MODEM_CONTROL_BUILD_PATH = Path("zigux/tests/phase11_hvc_modem_control_proof_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
TARGETLESS_WITNESS_CHECKER_PATH = Path("scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")
TARGETLESS_WITNESS_PATH = Path("zigux/tests/phase11_hvc_targetless_unregister_gap.zig")
TARGETLESS_WITNESS_BUILD_PATH = Path("zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

SURVEY_MARKERS = (
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "- `drivers/tty/hvc/hvc_console_verify.zig`",
    "returned `drivers/tty/hvc/hvc_console_verify.zig` source plus",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`Documentation/zigux/phase11-hvc-console-slice.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "repo-reality gaps or archival vocabulary",
    "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`",
    "`make -C zigux phase11-validate`",
)

SURVEY_FORBIDDEN_MARKERS = (
    "still does not rematerialize\n  `drivers/tty/hvc/hvc_console_verify.zig`",
)

COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "`drivers/tty/hvc/hvc_console_verify.zig` and the verify boundary note stay explicit",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "returned HVC validation matrix and build-inventory checker stay explicit",
    "proof-backed HVC continuity packet remains reviewable",
    "repo-reality gaps or archival vocabulary",
)

COMPANION_FORBIDDEN_MARKERS = (
    "still does not rematerialize\n`drivers/tty/hvc/hvc_console_verify.zig`",
)

MATRIX_MARKERS = (
    "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
    "- `drivers/tty/hvc/hvc_console_verify.zig`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`scripts/zigux/check-phase11-validate-manifest-roster.py`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "`make -C zigux phase11-validate`",
    "`make -C zigux phase11-hvc-survey`",
    "`zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "repo-reality gaps instead of returned fallback evidence",
    "flush intent",
    "`hvc_install()` ownership",
    "`hvc_alloc()` slot",
    "early console setup and device selection",
    "`__hvc_resize()`",
    "`hvc_hangup()` disconnect",
    "`hvc_remove()` handoff",
    "`hvc_cleanup()` tty-port",
    "DTR/RTS shutdown",
    "`wait_until_sent()` carryover",
    "`close_wait` ownership",
    "`port_initialized` clearing",
    "`hvc_kick()` wakeup-cue",
    "notifier-irq",
    "modem-control helper summaries reviewable on current `master`",
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps helper-local remove, notifier, sysrq fallback, and cleanup-trigger summaries reviewable on current `master`.",
)

MATRIX_FORBIDDEN_MARKERS = (
    "`drivers/tty/hvc/hvc_console_verify.zig`,\n  `drivers/tty/hvc/hvc_console_sysrq.zig`",
)

VERIFY_MARKERS = (
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove",
    "`error.CleanupRequiresFinalCloseOrHangup`",
    "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`",
    "`error.NotifierDispatchRequiresTtyRegistration`",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`",
    "`NotifierUnregisterTimingState.targeted_unregister_request`",
    "`targetless_dispatch_without_notifier`",
)

DRIVER_MARKERS = (
    "pub fn summarizeFlushIntent(request: FlushIntentRequest) FlushIntentSummary {",
    "pub const CloseTeardownSummary = struct {",
    "dtr_rts_shutdown: bool,",
    "wait_until_sent_intent: bool,",
    "close_wait_ownership: bool,",
    "port_initialized_cleared: bool,",
    "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {",
    "pub fn summarizeTtyRegistrationHandoff(request: TtyRegistrationRequest) TtyRegistrationSummary {",
    "pub fn summarizeInstallOwnership(request: InstallOwnershipRequest) InstallOwnershipSummary {",
    "pub fn summarizeAllocSlotHandoff(request: AllocSlotRequest) AllocSlotSummary {",
    "pub fn summarizeConsoleSetup(request: ConsoleSetupRequest) ConsoleSetupSummary {",
    "pub fn summarizeConsoleDeviceSelection(request: ConsoleDeviceRequest) ConsoleDeviceSummary {",
    "pub fn summarizeResizeHandoff(request: ResizeHandoffRequest) ResizeHandoffSummary {",
    "pub fn summarizeNotifierAddOutcome(request: NotifierAddRequest) NotifierAddSummary {",
    "pub fn summarizeKhvcdPollingContract(request: KhvcdPollingContractRequest) KhvcdPollingContractSummary {",
    "pub fn summarizeKhvcdWorkerEntry(request: KhvcdWorkerEntryRequest) KhvcdWorkerEntrySummary {",
    "pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {",
    "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {",
    "pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {",
    "pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {",
    "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {",
    "pub fn summarizeCleanupPrerequisite(",
    "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
    "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {",
    "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {",
    "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {",
    "const targetless_hangup_short_circuit = request.notifier_registered and",
    ".targetless_hangup_short_circuit = targetless_hangup_short_circuit,",
    "try std.testing.expect(!active.targetless_hangup_short_circuit);",
    "try std.testing.expect(targetless.targetless_hangup_short_circuit);",
    "try std.testing.expect(!invalid.targetless_hangup_short_circuit);",
)

VERIFY_HELPER_SOURCE_MARKERS = (
    "pub fn summarizeRemoveHandoffWithoutBinding(",
    "pub fn summarizeNotifierUnregisterTiming(",
    "pub fn summarizeNotifierDispatch(",
    "pub fn summarizeCleanupTrigger(",
    "test \"phase11 hvc verify helper keeps targetless sysrq fallback reviewable\" {",
)

PROOF_MARKERS = (
    'test "phase11 hvc cleanup packet proof keeps missing teardown anchors explicit" {',
    'try expectContains(survey_doc, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`");',
    'try expectContains(companion_doc, "`zigux/tests/phase11_hvc_console_manifest.json`");',
    'try expectContains(matrix_doc, "repo-reality gaps instead of returned fallback evidence");',
    'test "phase11 hvc cleanup packet proof keeps route boundaries explicit" {',
    'try expectContains(survey_doc, "`make -C zigux phase11-validate`");',
    'try expectContains(survey_doc, "`make -C zigux phase11-hvc-survey`");',
    'try expectContains(matrix_doc, "`make -C zigux phase11-hvc-survey`");',
    'test "phase11 hvc cleanup packet proof keeps verify-boundary failure modes explicit" {',
    'try expectContains(verify_doc, "`error.CleanupRequiresFinalCloseOrHangup`");',
    'try expectContains(verify_doc, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`");',
    'try expectContains(verify_doc, "`targetless_dispatch_without_notifier`");',
    'test "phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence" {',
    'try expectContains(matrix_doc, "flush intent");',
    'try expectContains(matrix_doc, "`hvc_install()` ownership");',
    'try expectContains(matrix_doc, "`hvc_cleanup()` tty-port");',
    'test "phase11 hvc cleanup packet proof keeps close teardown carryover details tied to matrix evidence" {',
    'try expectContains(matrix_doc, "DTR/RTS shutdown");',
    'try expectContains(matrix_doc, "`wait_until_sent()` carryover");',
    'try expectContains(matrix_doc, "`close_wait` ownership");',
    'try expectContains(matrix_doc, "`port_initialized` clearing");',
    'try expectContains(driver, "pub const CloseTeardownSummary = struct {");',
    'try expectContains(driver, "dtr_rts_shutdown: bool,");',
    'try expectContains(driver, "wait_until_sent_intent: bool,");',
    'try expectContains(driver, "close_wait_ownership: bool,");',
    'try expectContains(driver, "port_initialized_cleared: bool,");',
    'try expectContains(driver, "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {");',
    'test "phase11 hvc cleanup packet proof keeps newer failure-mode helpers tied to matrix evidence" {',
    'try expectContains(matrix_doc, "`hvc_kick()` wakeup-cue");',
    'try expectContains(matrix_doc, "notifier-irq");',
    'try expectContains(matrix_doc, "modem-control helper summaries reviewable on current `master`");',
    'try expectContains(driver, "pub fn summarizeCleanupPrerequisite(");',
    'try expectContains(driver, ") error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {");',
    'try expectContains(driver, "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {");',
    'try expectContains(driver, "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {");',
    'try expectContains(driver, "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {");',
    'try expectContains(driver, "const targetless_hangup_short_circuit = request.notifier_registered and");',
    'try expectContains(driver, ".targetless_hangup_short_circuit = targetless_hangup_short_circuit,");',
    'try expectContains(driver, "try std.testing.expect(!active.targetless_hangup_short_circuit);");',
    'try expectContains(driver, "try std.testing.expect(targetless.targetless_hangup_short_circuit);");',
    'try expectContains(driver, "try std.testing.expect(!invalid.targetless_hangup_short_circuit);");',
)

MODEM_CONTROL_PROOF_MARKERS = (
    'test "phase11 hvc console keeps full modem control callback surfaces reviewable" {',
    'const summary = hvc_console.summarizeModemControlHandoff(.{',
    'try std.testing.expect(summary.get_surface_visible);',
    'test "phase11 hvc console keeps hupcl teardown distinct from callback-backed modem control" {',
    'try std.testing.expect(teardown.dtr_rts_shutdown);',
    'try std.testing.expect(modem.set_surface_visible);',
)

MODEM_CONTROL_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_modem_control_proof.zig"),',
    '.name = "phase11-hvc-modem-control-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC modem-control proof.");',
)

TARGETLESS_WITNESS_CHECKER_MARKERS = (
    "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass",
    'const boundary = try readRepoFile("Documentation/zigux/phase11-hvc-verify-helper-boundary.md");',
    'const companion = try readRepoFile("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md");',
    'const survey = try readRepoFile("Documentation/zigux/phase11-hvc-console-survey.md");',
    'const matrix = try readRepoFile("Documentation/zigux/phase11-hvc-console-validation-matrix.md");',
    'try expectContains(companion, "separate failure-mode replay");',
    'try expectContains(matrix, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");',
)
TARGETLESS_WITNESS_MARKERS = (
    'test "phase11 hvc notifier witness records current-head targetless unregister sanitizer" {',
    'const boundary = try readRepoFile("Documentation/zigux/phase11-hvc-verify-helper-boundary.md");',
    'const companion = try readRepoFile("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md");',
    'const survey = try readRepoFile("Documentation/zigux/phase11-hvc-console-survey.md");',
    'const matrix = try readRepoFile("Documentation/zigux/phase11-hvc-console-validation-matrix.md");',
    'try expectContains(boundary, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge");',
    'try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");',
    'try expectContains(survey, "without promoting itself into the shared three-entry build inventory");',
    'try expectContains(matrix, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");',
)

TARGETLESS_WITNESS_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_targetless_unregister_gap.zig"),',
    '.name = "phase11-hvc-targetless-unregister-gap",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC targetless-unregister gap witness.");',
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase11-hvc-survey:",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def require_absent_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker in text:
            raise CheckError(f"forbidden {label} marker present: {marker}")


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_absent_markers(root, SURVEY_PATH, "survey", SURVEY_FORBIDDEN_MARKERS)
    require_markers(root, COMPANION_PATH, "companion", COMPANION_MARKERS)
    require_absent_markers(root, COMPANION_PATH, "companion", COMPANION_FORBIDDEN_MARKERS)
    require_markers(root, VERIFY_PATH, "verify", VERIFY_MARKERS)
    require_markers(root, MATRIX_PATH, "matrix", MATRIX_MARKERS)
    require_absent_markers(root, MATRIX_PATH, "matrix", MATRIX_FORBIDDEN_MARKERS)
    require_markers(root, DRIVER_PATH, "driver", DRIVER_MARKERS)
    require_markers(root, VERIFY_HELPER_SOURCE_PATH, "verify-helper source", VERIFY_HELPER_SOURCE_MARKERS)
    require_markers(root, PROOF_PATH, "proof", PROOF_MARKERS)
    require_markers(root, MODEM_CONTROL_PROOF_PATH, "modem-control proof", MODEM_CONTROL_PROOF_MARKERS)
    require_markers(root, MODEM_CONTROL_BUILD_PATH, "modem-control build", MODEM_CONTROL_BUILD_MARKERS)
    require_markers(
        root,
        TARGETLESS_WITNESS_CHECKER_PATH,
        "targetless witness checker",
        TARGETLESS_WITNESS_CHECKER_MARKERS,
    )
    require_markers(root, TARGETLESS_WITNESS_PATH, "targetless witness", TARGETLESS_WITNESS_MARKERS)
    require_markers(
        root,
        TARGETLESS_WITNESS_BUILD_PATH,
        "targetless witness build",
        TARGETLESS_WITNESS_BUILD_MARKERS,
    )

    makefile_text = read_text(root / MAKEFILE_PATH)
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile_text:
            raise CheckError(f"forbidden Makefile marker present: {marker}")

    payload = json.loads(read_text(root / INVENTORY_PATH))
    checks = payload.get("exact_current_checks")
    if not isinstance(checks, list) or "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig" not in checks:
        raise CheckError("exact_current_checks does not match the current-head HVC packet")

    workflow_steps = payload.get("workflow_phase11_steps")
    required = {"name": "Validate current Phase 11 support bundle", "run": "make -C zigux phase11-validate"}
    if not isinstance(workflow_steps, list) or required not in workflow_steps:
        raise CheckError("workflow_phase11_steps does not match the current-head HVC packet")

    if "phase11-hvc-cleanup-packet-proof" not in read_text(root / BUILD_PATH):
        raise CheckError("missing cleanup build marker: phase11-hvc-cleanup-packet-proof")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    def copy(rel: Path) -> str:
        return read_text(DEFAULT_ROOT / rel)

    write(root / SURVEY_PATH, copy(SURVEY_PATH))
    write(root / COMPANION_PATH, copy(COMPANION_PATH))
    write(root / VERIFY_PATH, copy(VERIFY_PATH))
    write(root / MATRIX_PATH, copy(MATRIX_PATH))
    write(root / DRIVER_PATH, copy(DRIVER_PATH))
    write(root / VERIFY_HELPER_SOURCE_PATH, copy(VERIFY_HELPER_SOURCE_PATH))
    write(root / PROOF_PATH, copy(PROOF_PATH))
    write(root / BUILD_PATH, '.name = "phase11-hvc-cleanup-packet-proof"\n')
    write(root / MODEM_CONTROL_PROOF_PATH, copy(MODEM_CONTROL_PROOF_PATH))
    write(root / MODEM_CONTROL_BUILD_PATH, copy(MODEM_CONTROL_BUILD_PATH))
    write(root / TARGETLESS_WITNESS_CHECKER_PATH, copy(TARGETLESS_WITNESS_CHECKER_PATH))
    write(root / TARGETLESS_WITNESS_PATH, copy(TARGETLESS_WITNESS_PATH))
    write(root / TARGETLESS_WITNESS_BUILD_PATH, copy(TARGETLESS_WITNESS_BUILD_PATH))
    write(root / MAKEFILE_PATH, copy(MAKEFILE_PATH))
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "exact_current_checks": [
                    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
                ],
                "workflow_phase11_steps": [
                    {
                        "name": "Validate current Phase 11 support bundle",
                        "run": "make -C zigux phase11-validate",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, rel: Path, needle: str) -> None:
    text = read_text(root / rel)
    write(root / rel, text.replace(needle, ""))
    try:
        run_check(root)
    except CheckError as exc:
        if needle not in str(exc) and "exact_current_checks" not in str(exc) and "workflow_phase11_steps" not in str(exc):
            raise AssertionError(f"expected {needle!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {needle!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_cleanup_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        cases = [
            (SURVEY_PATH, "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`"),
            (SURVEY_PATH, "`.github/workflows/zigux-bootstrap.yml`"),
            (SURVEY_PATH, "- `drivers/tty/hvc/hvc_console_verify.zig`"),
            (SURVEY_PATH, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`"),
            (SURVEY_PATH, "`Documentation/zigux/phase11-hvc-console-slice.md`"),
            (SURVEY_PATH, "`scripts/zigux/check-phase11-build-inventory.py`"),
            (SURVEY_PATH, "`zigux/tests/fixtures/phase11_build_inventory.json`"),
            (SURVEY_PATH, "`scripts/zigux/validate-phase11.py`"),
            (SURVEY_PATH, "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`"),
            (SURVEY_PATH, "`zigux/tests/phase11_hvc_modem_control_proof.zig`"),
            (SURVEY_PATH, "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`"),
            (SURVEY_PATH, "`make -C zigux phase11-validate`"),
            (COMPANION_PATH, "`PHASE11_STATUS=current_head_companion_landed`"),
            (COMPANION_PATH, "`zigux/tests/phase11_hvc_console_manifest.json`"),
            (COMPANION_PATH, "`scripts/zigux/check-phase11-hvc-survey-packet.py`"),
            (MATRIX_PATH, "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`"),
            (MATRIX_PATH, "- `drivers/tty/hvc/hvc_console_verify.zig`"),
            (MATRIX_PATH, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`"),
            (MATRIX_PATH, "`scripts/zigux/check-phase11-hvc-survey-packet.py`"),
            (MATRIX_PATH, "`scripts/zigux/check-phase11-validate-manifest-roster.py`"),
            (MATRIX_PATH, "flush intent"),
            (MATRIX_PATH, "`zigux/tests/phase11_hvc_modem_control_proof.zig`"),
            (MATRIX_PATH, "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`"),
            (MATRIX_PATH, "`zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig`"),
            (MATRIX_PATH, "`hvc_hangup()` disconnect"),
            (MATRIX_PATH, "`hvc_remove()` handoff"),
            (MATRIX_PATH, "`hvc_cleanup()` tty-port"),
            (MATRIX_PATH, "DTR/RTS shutdown"),
            (MATRIX_PATH, "`wait_until_sent()` carryover"),
            (MATRIX_PATH, "`close_wait` ownership"),
            (MATRIX_PATH, "`port_initialized` clearing"),
            (MATRIX_PATH, "`hvc_kick()` wakeup-cue"),
            (MATRIX_PATH, "`hvc_alloc()` slot"),
            (MATRIX_PATH, "early console setup and device selection"),
            (MATRIX_PATH, "`__hvc_resize()`"),
            (VERIFY_PATH, "`error.CleanupRequiresFinalCloseOrHangup`"),
            (VERIFY_PATH, "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`"),
            (VERIFY_PATH, "`error.NotifierDispatchRequiresTtyRegistration`"),
            (VERIFY_PATH, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`"),
            (VERIFY_PATH, "`NotifierUnregisterTimingState.targeted_unregister_request`"),
            (VERIFY_PATH, "`targetless_dispatch_without_notifier`"),
            (DRIVER_PATH, "pub const CloseTeardownSummary = struct {"),
            (DRIVER_PATH, "dtr_rts_shutdown: bool,"),
            (DRIVER_PATH, "wait_until_sent_intent: bool,"),
            (DRIVER_PATH, "close_wait_ownership: bool,"),
            (DRIVER_PATH, "port_initialized_cleared: bool,"),
            (DRIVER_PATH, "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {"),
            (DRIVER_PATH, "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {"),
            (DRIVER_PATH, "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {"),
            (DRIVER_PATH, "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {"),
            (DRIVER_PATH, "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {"),
            (DRIVER_PATH, "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {"),
            (DRIVER_PATH, "const targetless_hangup_short_circuit = request.notifier_registered and"),
            (VERIFY_HELPER_SOURCE_PATH, "pub fn summarizeRemoveHandoffWithoutBinding("),
            (VERIFY_HELPER_SOURCE_PATH, "pub fn summarizeNotifierDispatch("),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps missing teardown anchors explicit" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps route boundaries explicit" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps verify-boundary failure modes explicit" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence" {'),
            (PROOF_PATH, 'try expectContains(matrix_doc, "flush intent");'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps close teardown carryover details tied to matrix evidence" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps newer failure-mode helpers tied to matrix evidence" {'),
            (PROOF_PATH, 'try expectContains(driver, "pub const CloseTeardownSummary = struct {");'),
            (PROOF_PATH, 'try expectContains(driver, "dtr_rts_shutdown: bool,");'),
            (PROOF_PATH, 'try expectContains(driver, "wait_until_sent_intent: bool,");'),
            (PROOF_PATH, 'try expectContains(driver, "close_wait_ownership: bool,");'),
            (PROOF_PATH, 'try expectContains(driver, "port_initialized_cleared: bool,");'),
            (PROOF_PATH, 'try expectContains(driver, "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {");'),
            (PROOF_PATH, 'try expectContains(driver, ") error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {");'),
            (PROOF_PATH, 'try expectContains(driver, "try std.testing.expect(targetless.targetless_hangup_short_circuit);");'),
            (MODEM_CONTROL_PROOF_PATH, 'test "phase11 hvc console keeps full modem control callback surfaces reviewable" {'),
            (MODEM_CONTROL_PROOF_PATH, 'try std.testing.expect(summary.get_surface_visible);'),
            (MODEM_CONTROL_BUILD_PATH, '.root_source_file = b.path("phase11_hvc_modem_control_proof.zig"),'),
            (MODEM_CONTROL_BUILD_PATH, '.name = "phase11-hvc-modem-control-proof",'),
            (MODEM_CONTROL_BUILD_PATH, 'const test_step = b.step("test", "Run the focused Phase 11 HVC modem-control proof.");'),
            (TARGETLESS_WITNESS_CHECKER_PATH, "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass"),
            (TARGETLESS_WITNESS_CHECKER_PATH, 'const boundary = try readRepoFile("Documentation/zigux/phase11-hvc-verify-helper-boundary.md");'),
            (TARGETLESS_WITNESS_CHECKER_PATH, 'const companion = try readRepoFile("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md");'),
            (TARGETLESS_WITNESS_CHECKER_PATH, 'const survey = try readRepoFile("Documentation/zigux/phase11-hvc-console-survey.md");'),
            (TARGETLESS_WITNESS_CHECKER_PATH, 'const matrix = try readRepoFile("Documentation/zigux/phase11-hvc-console-validation-matrix.md");'),
            (TARGETLESS_WITNESS_CHECKER_PATH, 'try expectContains(companion, "separate failure-mode replay");'),
            (TARGETLESS_WITNESS_CHECKER_PATH, 'try expectContains(matrix, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");'),
            (TARGETLESS_WITNESS_PATH, 'test "phase11 hvc notifier witness records current-head targetless unregister sanitizer" {'),
            (TARGETLESS_WITNESS_PATH, 'try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");'),
            (TARGETLESS_WITNESS_BUILD_PATH, '.name = "phase11-hvc-targetless-unregister-gap",'),
            (BUILD_PATH, 'phase11-hvc-cleanup-packet-proof'),
        ]

        for index, (rel, needle) in enumerate(cases, start=1):
            broken = tmpdir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(broken, rel, needle)

        forbidden_makefile_route = tmpdir / "forbidden_makefile_route"
        shutil.copytree(fixture, forbidden_makefile_route, dirs_exist_ok=True)
        write(
            forbidden_makefile_route / MAKEFILE_PATH,
            read_text(forbidden_makefile_route / MAKEFILE_PATH) + "\nphase11-hvc-survey:\n\t@true\n",
        )
        try:
            run_check(forbidden_makefile_route)
        except CheckError as exc:
            if "phase11-hvc-survey:" not in str(exc):
                raise AssertionError(
                    f"expected forbidden makefile route failure, got {exc!r}"
                ) from exc
        else:
            raise AssertionError("expected forbidden makefile route failure")

        bad_inventory = tmpdir / "bad_inventory"
        shutil.copytree(fixture, bad_inventory, dirs_exist_ok=True)
        write(bad_inventory / INVENTORY_PATH, '{"exact_current_checks":[],"workflow_phase11_steps":[]}\n')
        try:
            run_check(bad_inventory)
        except CheckError:
            pass
        else:
            raise AssertionError("expected inventory failure")

        print("PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST=pass")
        print(f"PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST_CASE_COUNT={len(cases) + 2}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_HVC_CLEANUP_CURRENT_HEAD=fail: {exc}")
        return 1

    print("PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

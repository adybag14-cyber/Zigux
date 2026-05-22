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
PROOF_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig")
BUILD_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
TARGETLESS_WITNESS_CHECKER_PATH = Path("scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")

SURVEY_MARKERS = (
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "repo-reality gaps or archival vocabulary",
    "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`",
    "`make -C zigux phase11-validate`",
)

COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "returned HVC validation matrix and build-inventory checker stay explicit",
    "proof-backed HVC continuity packet remains reviewable",
    "repo-reality gaps or archival vocabulary",
)

MATRIX_MARKERS = (
    "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-validate`",
    "`make -C zigux phase11-hvc-survey`",
    "repo-reality gaps instead of returned fallback evidence",
    "flush intent",
    "`hvc_install()` ownership",
    "`hvc_cleanup()` tty-port",
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
    "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
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


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_markers(root, COMPANION_PATH, "companion", COMPANION_MARKERS)
    require_markers(root, VERIFY_PATH, "verify", VERIFY_MARKERS)
    require_markers(root, MATRIX_PATH, "matrix", MATRIX_MARKERS)
    require_markers(root, DRIVER_PATH, "driver", DRIVER_MARKERS)
    require_markers(root, PROOF_PATH, "proof", PROOF_MARKERS)
    require_markers(
        root,
        TARGETLESS_WITNESS_CHECKER_PATH,
        "targetless witness checker",
        ("PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass",),
    )

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
    write(root / PROOF_PATH, copy(PROOF_PATH))
    write(root / BUILD_PATH, '.name = "phase11-hvc-cleanup-packet-proof"\n')
    write(root / TARGETLESS_WITNESS_CHECKER_PATH, copy(TARGETLESS_WITNESS_CHECKER_PATH))
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
            (SURVEY_PATH, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`"),
            (COMPANION_PATH, "`zigux/tests/phase11_hvc_console_manifest.json`"),
            (MATRIX_PATH, "`scripts/zigux/check-phase11-hvc-survey-packet.py`"),
            (MATRIX_PATH, "`hvc_cleanup()` tty-port"),
            (VERIFY_PATH, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`"),
            (DRIVER_PATH, "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {"),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps missing teardown anchors explicit" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps route boundaries explicit" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps verify-boundary failure modes explicit" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence" {'),
            (TARGETLESS_WITNESS_CHECKER_PATH, "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass"),
            (BUILD_PATH, 'phase11-hvc-cleanup-packet-proof'),
        ]

        for index, (rel, needle) in enumerate(cases, start=1):
            broken = tmpdir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(broken, rel, needle)

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
        print(f"PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST_CASE_COUNT={len(cases) + 1}")
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

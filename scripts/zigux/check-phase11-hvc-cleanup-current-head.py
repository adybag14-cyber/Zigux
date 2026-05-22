#!/usr/bin/env python3
"""Fail-close guard for the current-head Phase 11 HVC cleanup packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[3] if len(SELF_PATH.parents) > 3 else SELF_PATH.parent

SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
COMPANION_PATH = Path("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md")
VERIFY_PATH = Path("Documentation/zigux/phase11-hvc-verify-helper-boundary.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
DRIVER_PATH = Path("drivers/tty/hvc/hvc_console.zig")
TARGETLESS_WITNESS_CHECKER_PATH = Path(
    "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"
)
EXPORT_PROOF_PATH = Path("zigux/tests/phase11_hvc_export_surface_layout_proof.zig")
EXPORT_BUILD_PATH = Path("zigux/tests/phase11_hvc_export_surface_layout_build.zig")
HV_OPS_PROOF_PATH = Path("zigux/tests/phase11_hvc_hv_ops_layout_proof.zig")
HV_OPS_BUILD_PATH = Path("zigux/tests/phase11_hvc_hv_ops_layout_build.zig")
PROOF_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig")
BUILD_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

EXACT_CURRENT_CHECKS = [
    "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    "python3 scripts/zigux/check-phase11-build-inventory.py",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
]

BUILD_TEST_NAMES = [
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
]

MODULE_ROOT_SOURCE_FILES = {
    "hv_ops_proof_module": "phase11_hvc_hv_ops_layout_proof.zig",
    "export_surface_proof_module": "phase11_hvc_export_surface_layout_proof.zig",
    "proof_module": "phase11_hvc_cleanup_packet_proof.zig",
}

TEST_ROOT_MODULES = {
    "phase11-hvc-hv-ops-layout-proof-tests": "hv_ops_proof_module",
    "phase11-hvc-export-surface-layout-proof-tests": "export_surface_proof_module",
    "phase11-hvc-cleanup-packet-proof": "proof_module",
}

SURVEY_MARKERS = (
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "current authenticated contents readback keeps the bounded HVC current-head",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "keep the deeper verify helper, sysrq helper, focused survey replay, manifest, teardown note,",
    "current authenticated contents readback still does not rematerialize",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`,",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey` route",
)

COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "The standalone targetless-unregister witness likewise stays directly readable as a separate failure-mode replay",
    "returned HVC validation matrix and build-inventory checker stay explicit",
    "smaller proof-backed HVC continuity packet reviewable",
)

VERIFY_MARKERS = (
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit",
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.",
    "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
    "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup` keep the hangup-only and combined cleanup trigger split explicit beside the earlier final-close-only path.",
    "Current direct contents reads on `master` still do not rematerialize `drivers/tty/hvc/hvc_console_verify.zig`, so keep this note as the current-head reminder surface for those landed helper edges rather than treating the helper file itself as returned direct-readback evidence.",
    "`error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
    "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable without claiming that notifier teardown has become live runtime behavior.",
    "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
    "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.",
    "do not treat this note as proof that `drivers/tty/hvc/hvc_console_verify.zig` has returned to direct current-head readback",
)

MATRIX_MARKERS = (
    "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
    "the current matrix packet now stays aligned with the smaller",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` plus `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` witness shard now rereads the live starter and the boundary note together",
    "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet",
    "keep the proof inventory exact",
    "keep helper-local failure-mode edges reviewable through",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py` and a dedicated `make -C zigux phase11-hvc-survey` route do not",
)

TARGETLESS_WITNESS_CHECKER_MARKERS = (
    "\"\"\"Fail-closed checker for the Phase 11 HVC targetless-unregister witness packet.\"\"\"",
    "\"Documentation/zigux/phase11-hvc-console-validation-matrix.md\",",
    "\"scripts/zigux/validate-phase11.py\",",
    "\"phase11_build_inventory.json must keep the targetless-unregister witness workflow step explicit\"",
    "print(\"PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass\")",
)

DRIVER_MARKERS = (
    "pub const FlushIntentRequest = struct {",
    "pub fn summarizeFlushIntent(request: FlushIntentRequest) FlushIntentSummary {",
    "pub const CloseTeardownRequest = struct {",
    "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {",
    "pub const TtyRegistrationRequest = struct {",
    "pub fn summarizeTtyRegistrationHandoff(request: TtyRegistrationRequest) TtyRegistrationSummary {",
    "pub fn summarizeNotifierAddOutcome(request: NotifierAddRequest) NotifierAddSummary {",
    "pub fn summarizeKhvcdPollingContract(request: KhvcdPollingContractRequest) KhvcdPollingContractSummary {",
    "pub fn summarizeKhvcdWorkerEntry(request: KhvcdWorkerEntryRequest) KhvcdWorkerEntrySummary {",
    "pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {",
    "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {",
    "pub const RemoveHandoffRequest = struct {",
    "pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {",
    "pub const CleanupHandoffRequest = struct {",
    "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {",
    "pub const HangupDisconnectRequest = struct {",
    "pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {",
    "pub const CleanupPrerequisiteRequest = struct {",
    "pub fn summarizeCleanupPrerequisite(",
    "error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {",
    "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
    "targetless_unregister_request_sanitized: bool,",
    ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,",
    "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {",
    "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {",
    "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {",
    'test "phase11 hvc console keeps flush intent summary reviewable" {',
    'test "phase11 hvc console keeps final-close teardown ownership summary reviewable" {',
    'test "phase11 hvc console keeps tty-registration handoff summary reviewable" {',
    'test "phase11 hvc console keeps notifier-add open handoff summary reviewable" {',
    'test "phase11 hvc console keeps khvcd polling-contract summary reviewable" {',
    'test "phase11 hvc console keeps khvcd worker-entry handoff reviewable" {',
    'test "phase11 hvc console keeps khvcd sleep-and-reschedule handoff reviewable" {',
    'test "phase11 hvc console keeps __hvc_poll drain-order summary reviewable" {',
    'test "phase11 hvc console keeps active hangup and cleanup ownership handoffs reviewable" {',
    'test "phase11 hvc console keeps cleanup prerequisite final-close-only trigger reviewable" {',
    'test "phase11 hvc console keeps cleanup prerequisite hangup-only trigger reviewable" {',
    'test "phase11 hvc console keeps cleanup prerequisite combined trigger reviewable" {',
    'test "phase11 hvc console rejects cleanup without final-close or hangup evidence" {',
    'test "phase11 hvc console keeps stale hangup short-circuit ownership reviewable" {',
    'test "phase11 hvc console keeps remove handoff summary reviewable" {',
    'test "phase11 hvc console keeps targetless notifier no-unregister edge reviewable" {',
    'test "phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized" {',
    'test "phase11 hvc console keeps hvc_kick wakeup cue reviewable" {',
    'test "phase11 hvc console keeps notifier irq helper surface reviewable" {',
    'test "phase11 hvc console keeps modem-control helper surface reviewable" {',
)

EXPORT_PROOF_MARKERS = (
    'test "phase11 HVC exported helper proof keeps winsize layout explicit" {',
    'layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
    'try expectContains(hvc_header, "void notifier_hangup_irq(struct hvc_struct *hp, int irq);");',
)

EXPORT_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
    '.name = "phase11-hvc-export-surface-layout-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
)

HV_OPS_PROOF_MARKERS = (
    'test "phase11 hvc hv_ops layout proof keeps callback table explicit" {',
    'try layout_assert.expectOffset(HvOps, "notifier_hangup", 40);',
    'try expectContains(hvc_header, "(*dtr_rts)");',
)

HV_OPS_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig"),',
    '.name = "phase11-hvc-hv-ops-layout-proof-tests",',
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
    '.name = "phase11-hvc-export-surface-layout-proof-tests",',
    'const test_step = b.step("test", "Run the focused Phase 11 exported-header proofs");',
)

PROOF_MARKERS = (
    'test "phase11 hvc cleanup packet proof keeps current-head cleanup packet explicit" {',
    'try expectContains(survey_doc, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`");',
    'try expectContains(survey_doc, "current authenticated contents readback keeps the bounded HVC current-head");',
    'try expectContains(cleanup_companion, "smaller proof-backed HVC continuity packet reviewable");',
    'test "phase11 hvc cleanup packet proof keeps current-head cleanup handoff markers aligned" {',
    'try expectContains(matrix_doc, "the current matrix packet now stays aligned with the smaller");',
    'try expectContains(matrix_doc, "keep helper-local failure-mode edges reviewable through");',
    'test "phase11 hvc cleanup packet proof keeps standalone targetless witness packet explicit" {',
    'try expectContains(survey_doc, "standalone targetless-unregister witness pair likewise stays");',
    'try expectContains(cleanup_companion, "separate failure-mode replay");',
    'try expectContains(matrix_doc, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");',
    'test "phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence" {',
    'try expectContains(matrix_doc, "tty-registration handoff");',
    'try expectContains(matrix_doc, "khvcd polling-contract");',
    'try expectContains(matrix_doc, "`__hvc_poll` drain-order");',
    'try expectContains(driver, "pub fn summarizeTtyRegistrationHandoff(request: TtyRegistrationRequest) TtyRegistrationSummary {");',
    'try expectContains(driver, "pub fn summarizeNotifierAddOutcome(request: NotifierAddRequest) NotifierAddSummary {");',
    'try expectContains(driver, "pub fn summarizeKhvcdPollingContract(request: KhvcdPollingContractRequest) KhvcdPollingContractSummary {");',
    'try expectContains(driver, "pub fn summarizeKhvcdWorkerEntry(request: KhvcdWorkerEntryRequest) KhvcdWorkerEntrySummary {");',
    'try expectContains(driver, "pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {");',
    'try expectContains(driver, "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {");',
    'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps tty-registration handoff summary reviewable\\\\\\" {");',
    'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps notifier-add open handoff summary reviewable\\\\\\" {");',
    'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps khvcd polling-contract summary reviewable\\\\\\" {");',
    'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps khvcd worker-entry handoff reviewable\\\\\\" {");',
    'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps khvcd sleep-and-reschedule handoff reviewable\\\\\\" {");',
    'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps __hvc_poll drain-order summary reviewable\\\\\\" {");',
)

BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),',
    '.name = "phase11-hvc-cleanup-packet-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");',
)

EXPECTED_SHARED_ADJUNCT_REPLAYS = [
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
]

EXPECTED_SHARED_ADJUNCT_BUILD_REPLAYS = [
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
]


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


def read_inventory(root: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(root / INVENTORY_PATH))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {INVENTORY_PATH}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {INVENTORY_PATH}")
    return payload


def expect_equal(payload: dict[str, object], key: str, expected: object) -> None:
    if payload.get(key) != expected:
        raise CheckError(f"{key} does not match the current-head HVC packet")


def expect_mapping(payload: dict[str, object], key: str, expected: dict[str, str], lhs: str, rhs: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list):
        raise CheckError(f"expected list for {key}")
    actual: dict[str, str] = {}
    for entry in value:
        if not isinstance(entry, dict):
            raise CheckError(f"expected object entries for {key}")
        left = entry.get(lhs)
        right = entry.get(rhs)
        if not isinstance(left, str) or not isinstance(right, str):
            raise CheckError(f"invalid entry in {key}")
        actual[left] = right
    if actual != expected:
        raise CheckError(f"{key} does not match the current-head HVC packet")


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_markers(root, COMPANION_PATH, "companion", COMPANION_MARKERS)
    require_markers(root, VERIFY_PATH, "verify", VERIFY_MARKERS)
    require_markers(root, MATRIX_PATH, "matrix", MATRIX_MARKERS)
    require_markers(
        root,
        TARGETLESS_WITNESS_CHECKER_PATH,
        "targetless witness checker",
        TARGETLESS_WITNESS_CHECKER_MARKERS,
    )
    require_markers(root, DRIVER_PATH, "driver", DRIVER_MARKERS)
    require_markers(root, EXPORT_PROOF_PATH, "export proof", EXPORT_PROOF_MARKERS)
    require_markers(root, EXPORT_BUILD_PATH, "export build", EXPORT_BUILD_MARKERS)
    require_markers(root, HV_OPS_PROOF_PATH, "hv_ops proof", HV_OPS_PROOF_MARKERS)
    require_markers(root, HV_OPS_BUILD_PATH, "hv_ops build", HV_OPS_BUILD_MARKERS)
    require_markers(root, PROOF_PATH, "cleanup proof", PROOF_MARKERS)
    require_markers(root, BUILD_PATH, "cleanup build", BUILD_MARKERS)

    payload = read_inventory(root)
    expect_equal(payload, "proof_build_file", "zigux/tests/phase11_hvc_cleanup_packet_build.zig")
    expect_equal(payload, "proof_replay_command", "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig")
    expect_equal(payload, "proof_step_name", "test")
    expect_equal(payload, "proof_step_description", "Run the focused Phase 11 HVC cleanup packet proof")
    expect_equal(payload, "proof_test_artifact_name", "phase11-hvc-cleanup-packet-proof")
    expect_equal(payload, "proof_root_source_file", "phase11_hvc_cleanup_packet_proof.zig")
    expect_equal(payload, "exact_current_checks", EXACT_CURRENT_CHECKS)
    expect_equal(payload, "build_test_names", BUILD_TEST_NAMES)
    expect_equal(payload, "shared_test_depend_steps", [])
    expect_equal(payload, "forbidden_markers", ["test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);"])
    expect_equal(payload, "dedicated_survey_replays", [])
    expect_equal(payload, "shared_split_replays", [])
    expect_equal(payload, "shared_adjunct_replays", EXPECTED_SHARED_ADJUNCT_REPLAYS)
    expect_equal(payload, "shared_adjunct_build_replays", EXPECTED_SHARED_ADJUNCT_BUILD_REPLAYS)
    expect_equal(payload, "shared_replay_markers", [])
    expect_mapping(payload, "module_root_source_files", MODULE_ROOT_SOURCE_FILES, "module", "path")
    expect_mapping(payload, "test_root_modules", TEST_ROOT_MODULES, "test", "root_module")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    for rel in (
        SURVEY_PATH,
        COMPANION_PATH,
        VERIFY_PATH,
        MATRIX_PATH,
        DRIVER_PATH,
        TARGETLESS_WITNESS_CHECKER_PATH,
        EXPORT_PROOF_PATH,
        EXPORT_BUILD_PATH,
        HV_OPS_PROOF_PATH,
        HV_OPS_BUILD_PATH,
        PROOF_PATH,
        BUILD_PATH,
    ):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)

    write(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Console Survey",
                "",
                "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
                "current authenticated contents readback keeps the bounded HVC current-head packet reviewable through:",
                "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
                "keep the deeper verify helper, sysrq helper, focused survey replay, manifest, teardown note, slice, and dedicated survey checker framed as archival or repo-reality-gap vocabulary until a future reread proves they returned beside the smaller companion packet.",
                "current authenticated contents readback still does not rematerialize",
                "`scripts/zigux/check-phase11-hvc-survey-packet.py`,",
                "`scripts/zigux/check-phase11-build-inventory.py`",
                "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
                "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "`zigux/tests/fixtures/phase11_build_inventory.json`",
                "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
                "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
                "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey` route",
                "",
            ]
        ),
    )
    write(
        root / COMPANION_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Cleanup Alignment Current-Head Companion",
                "",
                "`PHASE11_STATUS=current_head_companion_landed`",
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap",
                "`scripts/zigux/check-phase11-build-inventory.py`",
                "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "`zigux/tests/fixtures/phase11_build_inventory.json`",
                "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
                "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
                "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "The standalone targetless-unregister witness likewise stays directly readable as a separate failure-mode replay that rereads the current starter against the verify-helper boundary note without promoting itself into the shared three-entry build inventory.",
                "The returned HVC validation matrix and build-inventory checker stay explicit inside that smaller current-head packet.",
                "smaller proof-backed HVC continuity packet reviewable",
                "",
            ]
        ),
    )
    write(
        root / VERIFY_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Verify Helper Boundary",
                "",
                "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit",
                "`drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.",
                "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
                "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup` keep the hangup-only and combined cleanup trigger split explicit beside the earlier final-close-only path.",
                "Current direct contents reads on `master` still do not rematerialize `drivers/tty/hvc/hvc_console_verify.zig`, so keep this note as the current-head reminder surface for those landed helper edges rather than treating the helper file itself as returned direct-readback evidence.",
                "`error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.",
                "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
                "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable without claiming that notifier teardown has become live runtime behavior.",
                "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
                "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.",
                "do not treat this note as proof that `drivers/tty/hvc/hvc_console_verify.zig` has returned to direct current-head readback",
                "",
            ]
        ),
    )
    write(
        root / MATRIX_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Console Validation Matrix",
                "",
                "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
                "the current matrix packet now stays aligned with the smaller authenticated-readback companion stack rather than the older starter-depth public-readback packet",
                "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
                "`scripts/zigux/check-phase11-build-inventory.py`",
                "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "`zigux/tests/fixtures/phase11_build_inventory.json`",
                "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
                "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
                "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` plus `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` witness shard now rereads the live starter and the boundary note together",
                "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet",
                "keep the proof inventory exact and keep helper-local failure-mode edges reviewable through the boundary note",
                "`scripts/zigux/check-phase11-hvc-survey-packet.py` and a dedicated `make -C zigux phase11-hvc-survey` route do not",
                "",
            ]
        ),
    )
    write(
        root / TARGETLESS_WITNESS_CHECKER_PATH,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "\"\"\"Fail-closed checker for the Phase 11 HVC targetless-unregister witness packet.\"\"\"",
                "\"Documentation/zigux/phase11-hvc-console-validation-matrix.md\",",
                "\"scripts/zigux/validate-phase11.py\",",
                "\"phase11_build_inventory.json must keep the targetless-unregister witness workflow step explicit\"",
                "print(\"PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass\")",
                "",
            ]
        ),
    )
    write(root / DRIVER_PATH, "\n".join([*DRIVER_MARKERS, ""]))
    write(root / EXPORT_PROOF_PATH, "\n".join([*EXPORT_PROOF_MARKERS, ""]))
    write(root / EXPORT_BUILD_PATH, "\n".join([*EXPORT_BUILD_MARKERS, ""]))
    write(root / HV_OPS_PROOF_PATH, "\n".join([*HV_OPS_PROOF_MARKERS, ""]))
    write(root / HV_OPS_BUILD_PATH, "\n".join([*HV_OPS_BUILD_MARKERS, ""]))
    write(root / PROOF_PATH, "\n".join([*PROOF_MARKERS, ""]))
    write(root / BUILD_PATH, "\n".join([*BUILD_MARKERS, ""]))
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "proof_build_file": "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
                "proof_replay_command": "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
                "proof_step_name": "test",
                "proof_step_description": "Run the focused Phase 11 HVC cleanup packet proof",
                "proof_test_artifact_name": "phase11-hvc-cleanup-packet-proof",
                "proof_root_source_file": "phase11_hvc_cleanup_packet_proof.zig",
                "exact_current_checks": EXACT_CURRENT_CHECKS,
                "build_test_names": BUILD_TEST_NAMES,
                "shared_test_depend_steps": [],
                "module_root_source_files": [{"module": k, "path": v} for k, v in MODULE_ROOT_SOURCE_FILES.items()],
                "test_root_modules": [{"test": k, "root_module": v} for k, v in TEST_ROOT_MODULES.items()],
                "forbidden_markers": ["test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);"],
                "dedicated_survey_replays": [],
                "shared_split_replays": [],
                "shared_adjunct_replays": EXPECTED_SHARED_ADJUNCT_REPLAYS,
                "shared_adjunct_build_replays": EXPECTED_SHARED_ADJUNCT_BUILD_REPLAYS,
                "shared_replay_markers": [],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_cleanup_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        cases = [
            (SURVEY_PATH, "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`"),
            (SURVEY_PATH, "`scripts/zigux/check-phase11-hvc-survey-packet.py`,"),
            (SURVEY_PATH, "current authenticated contents readback still does not rematerialize"),
            (SURVEY_PATH, "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`"),
            (SURVEY_PATH, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`"),
            (SURVEY_PATH, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`"),
            (COMPANION_PATH, "`scripts/zigux/check-phase11-build-inventory.py`"),
            (COMPANION_PATH, "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`"),
            (COMPANION_PATH, "`zigux/tests/fixtures/phase11_build_inventory.json`"),
            (COMPANION_PATH, "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`"),
            (COMPANION_PATH, "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`"),
            (COMPANION_PATH, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`"),
            (COMPANION_PATH, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`"),
            (VERIFY_PATH, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution."),
            (MATRIX_PATH, "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`"),
            (MATRIX_PATH, "`scripts/zigux/check-phase11-build-inventory.py`"),
            (MATRIX_PATH, "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`"),
            (MATRIX_PATH, "`zigux/tests/fixtures/phase11_build_inventory.json`"),
            (MATRIX_PATH, "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`"),
            (MATRIX_PATH, "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`"),
            (MATRIX_PATH, "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`"),
            (MATRIX_PATH, "the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` plus `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` witness shard now rereads the live starter and the boundary note together"),
            (MATRIX_PATH, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet"),
            (TARGETLESS_WITNESS_CHECKER_PATH, "\"phase11_build_inventory.json must keep the targetless-unregister witness workflow step explicit\""),
            (DRIVER_PATH, "pub const FlushIntentRequest = struct {"),
            (DRIVER_PATH, "pub fn summarizeFlushIntent(request: FlushIntentRequest) FlushIntentSummary {"),
            (DRIVER_PATH, "pub const CloseTeardownRequest = struct {"),
            (DRIVER_PATH, "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {"),
            (DRIVER_PATH, "pub const TtyRegistrationRequest = struct {"),
            (DRIVER_PATH, "pub fn summarizeTtyRegistrationHandoff(request: TtyRegistrationRequest) TtyRegistrationSummary {"),
            (DRIVER_PATH, "pub fn summarizeNotifierAddOutcome(request: NotifierAddRequest) NotifierAddSummary {"),
            (DRIVER_PATH, "pub fn summarizeKhvcdPollingContract(request: KhvcdPollingContractRequest) KhvcdPollingContractSummary {"),
            (DRIVER_PATH, "pub fn summarizeKhvcdWorkerEntry(request: KhvcdWorkerEntryRequest) KhvcdWorkerEntrySummary {"),
            (DRIVER_PATH, "pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {"),
            (DRIVER_PATH, "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {"),
            (DRIVER_PATH, "pub const HangupDisconnectRequest = struct {"),
            (DRIVER_PATH, "pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {"),
            (DRIVER_PATH, "pub const CleanupPrerequisiteRequest = struct {"),
            (DRIVER_PATH, "pub fn summarizeCleanupPrerequisite("),
            (DRIVER_PATH, "error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {"),
            (DRIVER_PATH, 'test "phase11 hvc console keeps flush intent summary reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps final-close teardown ownership summary reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps tty-registration handoff summary reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps notifier-add open handoff summary reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps khvcd polling-contract summary reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps khvcd worker-entry handoff reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps khvcd sleep-and-reschedule handoff reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps __hvc_poll drain-order summary reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps active hangup and cleanup ownership handoffs reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps cleanup prerequisite final-close-only trigger reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps cleanup prerequisite hangup-only trigger reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps cleanup prerequisite combined trigger reviewable" {'),
            (DRIVER_PATH, 'test "phase11 hvc console rejects cleanup without final-close or hangup evidence" {'),
            (DRIVER_PATH, 'test "phase11 hvc console keeps stale hangup short-circuit ownership reviewable" {'),
            (DRIVER_PATH, "targetless_unregister_request_sanitized: bool,"),
            (DRIVER_PATH, ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,"),
            (DRIVER_PATH, 'test "phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized" {'),
            (PROOF_PATH, 'test "phase11 hvc cleanup packet proof keeps standalone targetless witness packet explicit" {'),
            (PROOF_PATH, 'try expectContains(survey_doc, "standalone targetless-unregister witness pair likewise stays");'),
            (PROOF_PATH, 'try expectContains(cleanup_companion, "separate failure-mode replay");'),
            (PROOF_PATH, 'try expectContains(matrix_doc, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");'),
            (PROOF_PATH, 'try expectContains(matrix_doc, "tty-registration handoff");'),
            (PROOF_PATH, 'try expectContains(matrix_doc, "khvcd polling-contract");'),
            (PROOF_PATH, 'try expectContains(matrix_doc, "`__hvc_poll` drain-order");'),
            (PROOF_PATH, 'try expectContains(driver, "pub fn summarizeTtyRegistrationHandoff(request: TtyRegistrationRequest) TtyRegistrationSummary {");'),
            (PROOF_PATH, 'try expectContains(driver, "pub fn summarizeNotifierAddOutcome(request: NotifierAddRequest) NotifierAddSummary {");'),
            (PROOF_PATH, 'try expectContains(driver, "pub fn summarizeKhvcdPollingContract(request: KhvcdPollingContractRequest) KhvcdPollingContractSummary {");'),
            (PROOF_PATH, 'try expectContains(driver, "pub fn summarizeKhvcdWorkerEntry(request: KhvcdWorkerEntryRequest) KhvcdWorkerEntrySummary {");'),
            (PROOF_PATH, 'try expectContains(driver, "pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {");'),
            (PROOF_PATH, 'try expectContains(driver, "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {");'),
            (PROOF_PATH, 'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps tty-registration handoff summary reviewable\\\\\\" {");'),
            (PROOF_PATH, 'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps notifier-add open handoff summary reviewable\\\\\\" {");'),
            (PROOF_PATH, 'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps khvcd polling-contract summary reviewable\\\\\\" {");'),
            (PROOF_PATH, 'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps khvcd worker-entry handoff reviewable\\\\\\" {");'),
            (PROOF_PATH, 'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps khvcd sleep-and-reschedule handoff reviewable\\\\\\" {");'),
            (PROOF_PATH, 'try expectContains(driver, "test \\\\\\"phase11 hvc console keeps __hvc_poll drain-order summary reviewable\\\\\\" {");'),
        ]
        for index, (rel, marker) in enumerate(cases, start=1):
            broken = tmpdir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            write(broken / rel, read_text(broken / rel).replace(marker, "", 1))
            expect_failure(broken, marker)

        bad_inventory = tmpdir / "bad_inventory"
        shutil.copytree(fixture, bad_inventory, dirs_exist_ok=True)
        payload = read_inventory(bad_inventory)
        payload["exact_current_checks"] = payload["exact_current_checks"][:-1]
        write(bad_inventory / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(bad_inventory, "exact_current_checks")

        missing_file = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file, dirs_exist_ok=True)
        (missing_file / SURVEY_PATH).unlink()
        expect_failure(missing_file, str(SURVEY_PATH))

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

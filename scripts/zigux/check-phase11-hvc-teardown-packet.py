#!/usr/bin/env python3
"""Fail-closed checker for the current-head Phase 11 HVC teardown packet."""

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
CLEANUP_CHECKER_PATH = Path("scripts/zigux/check-phase11-hvc-cleanup-current-head.py")
TARGETLESS_CHECKER_PATH = Path("scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
MAKEFILE_PATH = Path("zigux/Makefile")

SURVEY_MARKERS = (
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "repo-reality gaps or archival vocabulary",
    "`make -C zigux phase11-validate`",
)

COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "build-inventory checker",
    "cleanup-current-head checker",
    "targetless-unregister witness checker",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "repo-reality gaps or archival vocabulary",
    "standalone targetless-unregister witness",
    "dedicated modem-control proof pair",
    "proof-backed continuity packet remains reviewable",
)

VERIFY_MARKERS = (
    "`error.CleanupRequiresFinalCloseOrHangup`",
    "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`",
    "`error.NotifierDispatchRequiresTtyRegistration`",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`",
    "`NotifierUnregisterTimingState.targeted_unregister_request`",
    "`targetless_dispatch_without_notifier`",
)

MATRIX_MARKERS = (
    "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "repo-reality gaps instead of returned fallback evidence",
    "`hvc_hangup()` disconnect",
    "`hvc_remove()` handoff",
    "`hvc_cleanup()` tty-port",
    "modem-control helper summaries reviewable on current `master`",
    "targetless-unregister witness explicit as standalone direct-readback coverage",
)

DRIVER_MARKERS = (
    "pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {",
    "pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {",
    "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {",
    "pub fn summarizeCleanupPrerequisite(",
    "error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary",
    "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
    "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {",
    "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {",
    "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {",
    'test "phase11 hvc console keeps active hangup and cleanup ownership handoffs reviewable" {',
    'test "phase11 hvc console keeps stale hangup short-circuit ownership reviewable" {',
    'test "phase11 hvc console keeps remove handoff summary reviewable" {',
    'test "phase11 hvc console keeps targetless notifier no-unregister edge reviewable" {',
)

CLEANUP_CHECKER_MARKERS = (
    "PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "phase11_hvc_targetless_unregister_gap_build.zig",
)

TARGETLESS_CHECKER_MARKERS = (
    "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass",
    "standalone targetless-unregister witness",
    "phase11-hvc-targetless-unregister-gap",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase11-hvc-survey:",
)

REQUIRED_PACKET_FILES = (
    SURVEY_PATH,
    COMPANION_PATH,
    VERIFY_PATH,
    MATRIX_PATH,
    DRIVER_PATH,
    CLEANUP_CHECKER_PATH,
    TARGETLESS_CHECKER_PATH,
    INVENTORY_PATH,
    MAKEFILE_PATH,
)


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, markers: tuple[str, ...], label: str) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise ValidationError(f"missing {label} marker: {marker}")


def require_inventory(root: Path) -> None:
    try:
        payload = json.loads(read_text(root / INVENTORY_PATH))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{INVENTORY_PATH} is not valid JSON") from exc

    exact_current_checks = payload.get("exact_current_checks")
    if not isinstance(exact_current_checks, list):
        raise ValidationError("phase11_build_inventory.json must keep exact_current_checks as a JSON array")

    required_checks = (
        "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
        "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
        "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test",
        "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
        "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
        "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
        "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    )
    for command in required_checks:
        if command not in exact_current_checks:
            raise ValidationError(f"phase11_build_inventory.json must keep {command!r} in exact_current_checks")

    workflow_steps = payload.get("workflow_phase11_steps")
    required_step = {"name": "Validate current Phase 11 support bundle", "run": "make -C zigux phase11-validate"}
    if not isinstance(workflow_steps, list) or required_step not in workflow_steps:
        raise ValidationError("phase11_build_inventory.json must keep the phase11-validate workflow step explicit")

    focused_direct = payload.get("focused_direct_build_replays")
    if not isinstance(focused_direct, list):
        raise ValidationError("phase11_build_inventory.json must keep focused_direct_build_replays as a JSON array")
    for rel in (
        "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
        "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    ):
        if rel not in focused_direct:
            raise ValidationError(f"phase11_build_inventory.json must keep {rel!r} in focused_direct_build_replays")


def validate(root: Path) -> None:
    missing = [str(rel) for rel in REQUIRED_PACKET_FILES if not (root / rel).is_file()]
    if missing:
        raise ValidationError("missing required Phase 11 HVC teardown packet files: " + ", ".join(missing))

    require_markers(root, SURVEY_PATH, SURVEY_MARKERS, "survey")
    require_markers(root, COMPANION_PATH, COMPANION_MARKERS, "companion")
    require_markers(root, VERIFY_PATH, VERIFY_MARKERS, "verify")
    require_markers(root, MATRIX_PATH, MATRIX_MARKERS, "matrix")
    require_markers(root, DRIVER_PATH, DRIVER_MARKERS, "driver")
    require_markers(root, CLEANUP_CHECKER_PATH, CLEANUP_CHECKER_MARKERS, "cleanup checker")
    require_markers(root, TARGETLESS_CHECKER_PATH, TARGETLESS_CHECKER_MARKERS, "targetless checker")
    require_inventory(root)

    makefile_text = read_text(root / MAKEFILE_PATH)
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile_text:
            raise ValidationError(f"forbidden Makefile marker present: {marker}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, "\n".join(("survey", *SURVEY_MARKERS)) + "\n")
    write(root / COMPANION_PATH, "\n".join(("companion", *COMPANION_MARKERS)) + "\n")
    write(root / VERIFY_PATH, "\n".join(("verify", *VERIFY_MARKERS)) + "\n")
    write(root / MATRIX_PATH, "\n".join(("matrix", *MATRIX_MARKERS)) + "\n")
    write(root / DRIVER_PATH, "\n".join(("driver", *DRIVER_MARKERS)) + "\n")
    write(root / CLEANUP_CHECKER_PATH, "\n".join(("cleanup", *CLEANUP_CHECKER_MARKERS)) + "\n")
    write(root / TARGETLESS_CHECKER_PATH, "\n".join(("targetless", *TARGETLESS_CHECKER_MARKERS)) + "\n")
    write(root / MAKEFILE_PATH, "phase11-validate:\n\t@true\n")
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "exact_current_checks": [
                    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
                    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
                    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test",
                    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
                    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
                    "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
                    "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
                ],
                "workflow_phase11_steps": [
                    {
                        "name": "Validate current Phase 11 support bundle",
                        "run": "make -C zigux phase11-validate",
                    }
                ],
                "focused_direct_build_replays": [
                    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
                    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def expect_failure(root: Path, rel: Path, needle: str) -> None:
    text = read_text(root / rel)
    write(root / rel, text.replace(needle, "", 1))
    try:
        validate(root)
    except ValidationError as exc:
        if needle not in str(exc) and "phase11_build_inventory.json" not in str(exc):
            raise AssertionError(f"expected {needle!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {needle!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_teardown_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        validate(fixture)

        cases = [
            (SURVEY_PATH, "`make -C zigux phase11-validate`"),
            (SURVEY_PATH, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`"),
            (COMPANION_PATH, "standalone targetless-unregister witness"),
            (VERIFY_PATH, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`"),
            (MATRIX_PATH, "`hvc_cleanup()` tty-port"),
            (MATRIX_PATH, "targetless-unregister witness explicit as standalone direct-readback coverage"),
            (DRIVER_PATH, "pub fn summarizeCleanupPrerequisite("),
            (DRIVER_PATH, 'test "phase11 hvc console keeps stale hangup short-circuit ownership reviewable" {'),
            (CLEANUP_CHECKER_PATH, "`zigux/tests/phase11_hvc_modem_control_proof.zig`"),
            (TARGETLESS_CHECKER_PATH, "phase11-hvc-targetless-unregister-gap"),
        ]

        for index, (rel, needle) in enumerate(cases, start=1):
            broken = tmpdir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(broken, rel, needle)

        bad_inventory = tmpdir / "bad_inventory"
        shutil.copytree(fixture, bad_inventory, dirs_exist_ok=True)
        write(
            bad_inventory / INVENTORY_PATH,
            json.dumps(
                {
                    "exact_current_checks": [],
                    "workflow_phase11_steps": [],
                    "focused_direct_build_replays": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        try:
            validate(bad_inventory)
        except ValidationError:
            pass
        else:
            raise AssertionError("expected inventory validation failure")

        forbidden_makefile = tmpdir / "forbidden_makefile"
        shutil.copytree(fixture, forbidden_makefile, dirs_exist_ok=True)
        write(forbidden_makefile / MAKEFILE_PATH, "phase11-validate:\n\t@true\nphase11-hvc-survey:\n\t@true\n")
        try:
            validate(forbidden_makefile)
        except ValidationError as exc:
            if "phase11-hvc-survey:" not in str(exc):
                raise AssertionError(f"expected forbidden route failure, got {exc!r}") from exc
        else:
            raise AssertionError("expected forbidden route failure")

        print("PHASE11_HVC_TEARDOWN_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_TEARDOWN_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 2}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current-head Phase 11 HVC teardown packet for drift."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--repo-root", type=Path, dest="root_override")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root_override if args.root_override is not None else args.root
    try:
        validate(root.resolve())
    except ValidationError as exc:
        print(f"PHASE11_HVC_TEARDOWN_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_TEARDOWN_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

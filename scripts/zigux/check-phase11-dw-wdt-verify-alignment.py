#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare verify-alignment packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "note": "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "platform_plan": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "verify": "drivers/watchdog/dw_wdt_verify.zig",
    "pm": "drivers/watchdog/dw_wdt_pm.zig",
}

EXPECTED_MANIFEST_LANE = "P11-L05"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_STATUS = "starter_landed"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"

NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- lane family: `P11-L10`",
    "- active current-head continuity: `P11-L05`",
    "- current authenticated contents no longer keep the older returned validation-matrix story directly readable through the same bridge that serves the rest of this packet",
    "- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` still records continuity `P11-L05` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still records that the broader direct-driver and replay-backed packet does not currently rematerialize through the same authenticated-contents bridge",
    "- `drivers/watchdog/dw_wdt_verify.zig` keeps `test \"phase11 dw_wdt verify keeps registration-blocking failure paths explicit\"`",
    "- `drivers/watchdog/dw_wdt_pm.zig` keeps `test \"phase11 dw_wdt pm suspend keeps missing drvdata explicit\"`",
    "`test \"phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore\"`",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`",
    "- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` should keep this narrower current-head packet fail-closed instead of asserting the older returned validation-matrix stack",
]

PLATFORM_PLAN_MARKERS = [
    "Current authenticated contents rereads in this run do not rematerialize",
    "the broader direct-driver or replay-backed packet this note used to claim",
    "the two current DesignWare truthfulness checkers",
    "- the bounded PM helper pair `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig`",
]

VERIFY_MARKERS = [
    'const dw_wdt = @import("dw_wdt.zig");',
    'test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit" {',
    "try testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_timer_clock, missing_timer_clock.state);",
    'test "phase11 dw_wdt verify keeps mmio-blocked registration handoff explicit" {',
    "try testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_on_live_mmio, blocked_handoff.state);",
    'test "phase11 dw_wdt verify keeps imported-running handoff and shared-clock fallback explicit" {',
    "try testing.expectEqual(dw_wdt.RegistrationScaffoldState.import_running_state_then_register, handoff.state);",
    'test "phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit" {',
    "try testing.expectEqual(dw_wdt.TeardownOutcome.continued_heartbeat, stop_summary.outcome);",
    'test "phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct" {',
    "try testing.expectEqual(dw_wdt.TeardownOutcome.reset_control_stop, stop_summary.outcome);",
    'test "phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit" {',
    "try testing.expectEqual(dw_wdt.TeardownOutcome.idle_noop, stop_summary.outcome);",
]

PM_MARKERS = [
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt pm suspend keeps missing drvdata explicit" {',
    "try std.testing.expectEqual(PmSuspendState.blocked_missing_drvdata, summary.state);",
    'test "phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit" {',
    "try std.testing.expectEqual(PmSuspendState.running_suspend_requires_stop, summary.state);",
    'test "phase11 dw_wdt pm suspend keeps idle path explicit without teardown hooks" {',
    "try std.testing.expectEqual(PmSuspendState.idle_suspend_ready, summary.state);",
    'test "phase11 dw_wdt pm suspend keeps missing hook teardown explicit during running stop" {',
    'test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {',
    "PmResumeState.import_running_state_then_restore_hooks,",
    'test "phase11 dw_wdt pm resume keeps idle restore path explicit" {',
    "try std.testing.expectEqual(PmResumeState.restore_idle_hooks, summary.state);",
    'test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore" {',
    "PmResumeState.blocked_live_mmio_timeout_reprogram,",
    'test "phase11 dw_wdt pm shutdown keeps missing drvdata explicit" {',
    "try std.testing.expectEqual(PmShutdownState.blocked_missing_drvdata, summary.state);",
    'test "phase11 dw_wdt pm shutdown keeps running teardown stop and hook removal explicit" {',
    "try std.testing.expectEqual(PmShutdownState.running_shutdown_requires_stop, summary.state);",
    'test "phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit" {',
    "try std.testing.expect(summary.pretimeout_mask_requested);",
    'test "phase11 dw_wdt pm shutdown keeps idle hook teardown explicit without stop" {',
    'test "phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit" {',
]


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def read_manifest(root: Path) -> dict[str, object]:
    path = root / FILES["manifest"]
    try:
        value = json.loads(read_text(root, FILES["manifest"]))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError("manifest root must be an object")
    return value


def expect_manifest_state(manifest: dict[str, object]) -> None:
    lane_key = manifest.get("lane_key")
    surveyed_commit = manifest.get("surveyed_commit")
    if lane_key != EXPECTED_MANIFEST_LANE:
        raise CheckError(
            f"manifest lane_key mismatch: expected {EXPECTED_MANIFEST_LANE}, got {lane_key!r}"
        )
    if surveyed_commit != EXPECTED_MANIFEST_PIN:
        raise CheckError(
            "manifest surveyed_commit mismatch: "
            f"expected {EXPECTED_MANIFEST_PIN}, got {surveyed_commit!r}"
        )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("manifest gaps must be a list")

    found_verify = False
    found_pm = False
    found_next = False
    for entry in gaps:
        if not isinstance(entry, dict):
            raise CheckError("manifest gaps entries must be objects")
        if entry.get("id") == VERIFY_GAP_ID:
            if entry.get("zigux_destination") != VERIFY_DESTINATION:
                raise CheckError(
                    "manifest teardown-parity destination mismatch: "
                    f"expected {VERIFY_DESTINATION}, got {entry.get('zigux_destination')!r}"
                )
            if entry.get("status") != VERIFY_STATUS:
                raise CheckError(
                    "manifest teardown-parity status mismatch: "
                    f"expected {VERIFY_STATUS!r}, got {entry.get('status')!r}"
                )
            found_verify = True
        if entry.get("id") == PM_GAP_ID:
            if entry.get("zigux_destination") != PM_DESTINATION:
                raise CheckError(
                    "manifest pm destination mismatch: "
                    f"expected {PM_DESTINATION}, got {entry.get('zigux_destination')!r}"
                )
            if entry.get("status") != "starter_landed":
                raise CheckError(
                    "manifest pm status mismatch: "
                    f"expected 'starter_landed', got {entry.get('status')!r}"
                )
            found_pm = True
        if entry.get("id") == NEXT_GAP_ID:
            if entry.get("zigux_destination") != NEXT_DESTINATION:
                raise CheckError(
                    "manifest next-step destination mismatch: "
                    f"expected {NEXT_DESTINATION}, got {entry.get('zigux_destination')!r}"
                )
            if entry.get("status") != "ready_next":
                raise CheckError(
                    "manifest next-step status mismatch: "
                    f"expected 'ready_next', got {entry.get('status')!r}"
                )
            found_next = True

    if not found_verify:
        raise CheckError(f"manifest missing gap entry: {VERIFY_GAP_ID}")
    if not found_pm:
        raise CheckError(f"manifest missing gap entry: {PM_GAP_ID}")
    if not found_next:
        raise CheckError(f"manifest missing gap entry: {NEXT_GAP_ID}")


def run_check(root: Path) -> None:
    note = read_text(root, FILES["note"])
    platform_plan = read_text(root, FILES["platform_plan"])
    manifest = read_manifest(root)
    verify = read_text(root, FILES["verify"])
    pm = read_text(root, FILES["pm"])

    expect_markers("note", note, NOTE_MARKERS)
    expect_markers("platform_plan", platform_plan, PLATFORM_PLAN_MARKERS)
    expect_markers("verify", verify, VERIFY_MARKERS)
    expect_markers("pm", pm, PM_MARKERS)
    expect_manifest_state(manifest)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["note"], "\n".join(NOTE_MARKERS) + "\n")
    write(root / FILES["platform_plan"], "\n".join(PLATFORM_PLAN_MARKERS) + "\n")
    write(root / FILES["verify"], "\n".join(VERIFY_MARKERS) + "\n")
    write(root / FILES["pm"], "\n".join(PM_MARKERS) + "\n")
    write(
        root / FILES["manifest"],
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE,
                "surveyed_commit": EXPECTED_MANIFEST_PIN,
                "gaps": [
                    {
                        "id": VERIFY_GAP_ID,
                        "status": VERIFY_STATUS,
                        "zigux_destination": VERIFY_DESTINATION,
                    },
                    {
                        "id": PM_GAP_ID,
                        "status": "starter_landed",
                        "zigux_destination": PM_DESTINATION,
                    },
                    {
                        "id": NEXT_GAP_ID,
                        "status": "ready_next",
                        "zigux_destination": NEXT_DESTINATION,
                    },
                ],
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
            raise AssertionError(
                f"expected self-test failure containing {fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-dw-wdt-verify-alignment-") as tmpdir:
        root = Path(tmpdir)
        fixture = root / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        bad_lane = root / "bad-lane"
        shutil.copytree(fixture, bad_lane)
        manifest_path = bad_lane / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P11-L10"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(bad_lane, "manifest lane_key mismatch")
        case_count += 1

        missing_marker = root / "missing-marker"
        shutil.copytree(fixture, missing_marker)
        note_path = missing_marker / FILES["note"]
        note_path.write_text("# Phase 11 DesignWare Verify Alignment Gap\n", encoding="utf-8")
        expect_failure(missing_marker, "missing marker in note")
        case_count += 1

        missing_platform_plan_marker = root / "missing-platform-plan-marker"
        shutil.copytree(fixture, missing_platform_plan_marker)
        platform_plan_path = missing_platform_plan_marker / FILES["platform_plan"]
        platform_plan_path.write_text(
            platform_plan_path.read_text(encoding="utf-8").replace(
                PLATFORM_PLAN_MARKERS[3],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_platform_plan_marker,
            f"missing marker in platform_plan: {PLATFORM_PLAN_MARKERS[3]}",
        )
        case_count += 1

        missing_verify_marker = root / "missing-verify-marker"
        shutil.copytree(fixture, missing_verify_marker)
        verify_path = missing_verify_marker / FILES["verify"]
        verify_path.write_text(
            verify_path.read_text(encoding="utf-8").replace(
                VERIFY_MARKERS[7],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_verify_marker,
            f"missing marker in verify: {VERIFY_MARKERS[7]}",
        )
        case_count += 1

        missing_idle_restore = root / "missing-idle-restore"
        shutil.copytree(fixture, missing_idle_restore)
        pm_path = missing_idle_restore / FILES["pm"]
        pm_path.write_text(
            pm_path.read_text(encoding="utf-8").replace(
                'test "phase11 dw_wdt pm resume keeps idle restore path explicit" {\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_idle_restore,
            'missing marker in pm: test "phase11 dw_wdt pm resume keeps idle restore path explicit" {',
        )
        case_count += 1

        missing_pretimeout_mask = root / "missing-pretimeout-mask"
        shutil.copytree(fixture, missing_pretimeout_mask)
        pm_path = missing_pretimeout_mask / FILES["pm"]
        pm_path.write_text(
            pm_path.read_text(encoding="utf-8").replace(
                "try std.testing.expect(summary.pretimeout_mask_requested);",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_pretimeout_mask,
            "missing marker in pm: try std.testing.expect(summary.pretimeout_mask_requested);",
        )
        case_count += 1

        missing_note_timeout_reprogram = root / "missing-note-timeout-reprogram"
        shutil.copytree(fixture, missing_note_timeout_reprogram)
        note_path = missing_note_timeout_reprogram / FILES["note"]
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                NOTE_MARKERS[9] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_note_timeout_reprogram,
            f"missing marker in note: {NOTE_MARKERS[9]}",
        )
        case_count += 1

        missing_note_ready_next = root / "missing-note-ready-next"
        shutil.copytree(fixture, missing_note_ready_next)
        note_path = missing_note_ready_next / FILES["note"]
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                NOTE_MARKERS[10] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_note_ready_next,
            f"missing marker in note: {NOTE_MARKERS[10]}",
        )
        case_count += 1

        print("PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELFTEST=pass")
        print(f"PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELFTEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root).resolve())
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_VERIFY_ALIGNMENT=fail:{exc}")
        return 1

    print("PHASE11_DW_WDT_VERIFY_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
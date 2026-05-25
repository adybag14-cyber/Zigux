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
    "matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "platform_plan": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "verify": "drivers/watchdog/dw_wdt_verify.zig",
    "pm": "drivers/watchdog/dw_wdt_pm.zig",
}

EXPECTED_MANIFEST_LANE = "P11-L10"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_STATUS = "starter_landed"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
PM_WHY_NOW_MARKER = (
    "The bounded PM helper now keeps suspend, resume, and shutdown handoff reviewable "
    "across missing-drvdata blocks, running-hardware suspend stop intent with "
    "stop-on-reboot unregister and restart-priority clear, idle suspend without "
    "teardown hooks, imported-running resume recovery plus stop-on-reboot and "
    "restart-priority restore, idle restore hooks, timeout-reprogram blocks, running "
    "shutdown stop intent with pretimeout-mask teardown, and idle shutdown cleanup "
    "before live MMIO-backed PM work lands."
)
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"

NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- lane family: `P11-L12`",
    "- active current-head continuity note owner: `P11-Y03`",
    "- current authenticated contents now keep the returned validation matrix directly readable through the same bridge that serves the rest of this narrower packet",
    "- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` now records deeper platform-registration scaffold continuity `P11-L10` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- the active routing split now keeps owner-note truthfulness on `P11-Y03`, survey-only follow-through on `P11-L09`, and deeper platform-registration scaffold follow-through on `P11-L10`; do not reserve `P11-L05` unless the packet collapses back to the older survey-era shape",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`, and the returned verify helper now remains directly readable on the same authenticated bridge, so teardown-parity ownership and evidence both stay explicit without reopening the broader direct-driver packet",
    "- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope",
    "- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now keeps the returned DesignWare matrix readable on current `master` while still parking hardware-backed MMIO validation as the next bounded same-lane step",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`, but this note does not itself own that later implementation step",
    "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still records that the broader direct-driver and replay-backed packet does not currently rematerialize through the same authenticated-contents bridge even though the verify helper has returned inside the smaller packet",
    "- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` should keep this narrower current-head packet fail-closed around the returned validation matrix, the manifest-routed teardown-parity ownership, the returned verify helper, the platform-plan boundary, and the bounded PM helper instead of asserting direct readability for the broader direct-driver stack",
]

MATRIX_MARKERS = [
    "- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
    "- current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- active watchdog continuity for this matrix and its coupled survey packet is",
    "- `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_verify.zig`",
    "- The next bounded same-lane follow-up remains the manifest-marked ready-next",
    "hardware-backed MMIO validation around suspend, resume, and",
]

PLATFORM_PLAN_MARKERS = [
    "Current authenticated contents rereads on `master` now keep this owner note,",
    "`drivers/watchdog/dw_wdt_verify.zig`,",
    "the broader direct-driver or replay-backed packet this note used to claim",
    "the returned verify helper `drivers/watchdog/dw_wdt_verify.zig`",
    "- the bounded PM helper pair `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig`",
]

VERIFY_MARKERS = [
    'const dw_wdt_pm = @import("dw_wdt_pm.zig");',
    'const dw_wdt_restart = @import("dw_wdt_restart.zig");',
    'test "dw_wdt verify keeps restart blockers and register-write readiness aligned" {',
    'test "dw_wdt verify keeps PM helper ordering and blocker branches explicit" {',
    'test "dw_wdt verify keeps PM scaffold dispositions aligned with the stronger helper packet" {',
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

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        raise CheckError("manifest survey_summary must be an object")
    if summary.get("dw_wdt_pm_helper_present") is not True:
        raise CheckError(
            "manifest pm helper survey flag mismatch: "
            f"expected True, got {summary.get('dw_wdt_pm_helper_present')!r}"
        )
    if summary.get("dw_wdt_verify_helper_present") is not True:
        raise CheckError(
            "manifest verify helper survey flag mismatch: "
            f"expected True, got {summary.get('dw_wdt_verify_helper_present')!r}"
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
            if entry.get("why_now") != PM_WHY_NOW_MARKER:
                raise CheckError(
                    "manifest pm why_now mismatch: "
                    f"expected {PM_WHY_NOW_MARKER!r}, got {entry.get('why_now')!r}"
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
    matrix = read_text(root, FILES["matrix"])
    platform_plan = read_text(root, FILES["platform_plan"])
    manifest = read_manifest(root)
    verify = read_text(root, FILES["verify"])
    pm = read_text(root, FILES["pm"])

    expect_markers("note", note, NOTE_MARKERS)
    expect_markers("matrix", matrix, MATRIX_MARKERS)
    expect_markers("platform_plan", platform_plan, PLATFORM_PLAN_MARKERS)
    expect_markers("verify", verify, VERIFY_MARKERS)
    expect_markers("pm", pm, PM_MARKERS)
    expect_manifest_state(manifest)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["note"], "\n".join(NOTE_MARKERS) + "\n")
    write(root / FILES["matrix"], "\n".join(MATRIX_MARKERS) + "\n")
    write(root / FILES["platform_plan"], "\n".join(PLATFORM_PLAN_MARKERS) + "\n")
    write(root / FILES["verify"], "\n".join(VERIFY_MARKERS) + "\n")
    write(root / FILES["pm"], "\n".join(PM_MARKERS) + "\n")
    write(
        root / FILES["manifest"],
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE,
                "surveyed_commit": EXPECTED_MANIFEST_PIN,
                "survey_summary": {
                    "dw_wdt_pm_helper_present": True,
                    "dw_wdt_verify_helper_present": True,
                },
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
                        "why_now": PM_WHY_NOW_MARKER,
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
        manifest["lane_key"] = "P11-L05"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(bad_lane, "manifest lane_key mismatch")
        case_count += 1

        missing_survey_summary = root / "missing-survey-summary"
        shutil.copytree(fixture, missing_survey_summary)
        manifest_path = missing_survey_summary / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"] = "missing"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(missing_survey_summary, "manifest survey_summary must be an object")
        case_count += 1

        bad_pm_helper_flag = root / "bad-pm-helper-flag"
        shutil.copytree(fixture, bad_pm_helper_flag)
        manifest_path = bad_pm_helper_flag / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["dw_wdt_pm_helper_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(bad_pm_helper_flag, "manifest pm helper survey flag mismatch")
        case_count += 1

        bad_verify_helper_flag = root / "bad-verify-helper-flag"
        shutil.copytree(fixture, bad_verify_helper_flag)
        manifest_path = bad_verify_helper_flag / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["dw_wdt_verify_helper_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(bad_verify_helper_flag, "manifest verify helper survey flag mismatch")
        case_count += 1

        missing_marker = root / "missing-marker"
        shutil.copytree(fixture, missing_marker)
        note_path = missing_marker / FILES["note"]
        note_path.write_text("# Phase 11 DesignWare Verify Alignment Gap\n", encoding="utf-8")
        expect_failure(missing_marker, "missing marker in note")
        case_count += 1

        missing_matrix_marker = root / "missing-matrix-marker"
        shutil.copytree(fixture, missing_matrix_marker)
        matrix_path = missing_matrix_marker / FILES["matrix"]
        matrix_path.write_text(
            matrix_path.read_text(encoding="utf-8").replace(MATRIX_MARKERS[5], "", 1),
            encoding="utf-8",
        )
        expect_failure(
            missing_matrix_marker,
            f"missing marker in matrix: {MATRIX_MARKERS[5]}",
        )
        case_count += 1

        missing_platform_plan_marker = root / "missing-platform-plan-marker"
        shutil.copytree(fixture, missing_platform_plan_marker)
        platform_plan_path = missing_platform_plan_marker / FILES["platform_plan"]
        platform_plan_path.write_text(
            platform_plan_path.read_text(encoding="utf-8").replace(
                PLATFORM_PLAN_MARKERS[4],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_platform_plan_marker,
            f"missing marker in platform_plan: {PLATFORM_PLAN_MARKERS[4]}",
        )
        case_count += 1

        missing_verify_marker = root / "missing-verify-marker"
        shutil.copytree(fixture, missing_verify_marker)
        verify_path = missing_verify_marker / FILES["verify"]
        verify_path.write_text(
            verify_path.read_text(encoding="utf-8").replace(
                VERIFY_MARKERS[2],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_verify_marker,
            f"missing marker in verify: {VERIFY_MARKERS[2]}",
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

        missing_why_now = root / "missing-why-now"
        shutil.copytree(fixture, missing_why_now)
        manifest_path = missing_why_now / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["gaps"]:
            if entry["id"] == PM_GAP_ID:
                entry["why_now"] = "stale"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(missing_why_now, "manifest pm why_now mismatch")
        case_count += 1

        wrong_verify_destination = root / "wrong-verify-destination"
        shutil.copytree(fixture, wrong_verify_destination)
        manifest_path = wrong_verify_destination / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["gaps"]:
            if entry["id"] == VERIFY_GAP_ID:
                entry["zigux_destination"] = PM_DESTINATION
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(wrong_verify_destination, "manifest teardown-parity destination mismatch")
        case_count += 1

        missing_next_gap = root / "missing-next-gap"
        shutil.copytree(fixture, missing_next_gap)
        manifest_path = missing_next_gap / FILES["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"] = [entry for entry in manifest["gaps"] if entry["id"] != NEXT_GAP_ID]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(missing_next_gap, f"manifest missing gap entry: {NEXT_GAP_ID}")
        case_count += 1

        print("PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
        else:
            run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_VERIFY_ALIGNMENT=fail: {exc}")
        return 1
    except AssertionError as exc:
        print(str(exc))
        return 1

    if not args.self_test:
        print("PHASE11_DW_WDT_VERIFY_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

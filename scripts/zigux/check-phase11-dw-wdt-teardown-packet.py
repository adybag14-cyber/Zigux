#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "alignment_note": Path("Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md"),
    "gap_note": Path("Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md"),
    "clock_plan": Path("Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md"),
    "platform_plan": Path("Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md"),
    "manifest": Path("zigux/tests/phase11_dw_wdt_manifest.json"),
    "registration_scaffold": Path("zigux/tests/phase11_dw_wdt_registration_scaffold.zig"),
    "verify": Path("drivers/watchdog/dw_wdt_verify.zig"),
    "pm": Path("drivers/watchdog/dw_wdt_pm.zig"),
}

ALIGNMENT_NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- current authenticated contents no longer keep the older returned validation-matrix story directly readable through the same bridge that serves the rest of this packet",
    "- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` still records continuity `P11-L05` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- `drivers/watchdog/dw_wdt_verify.zig` still keeps registration-blocking failure paths, MMIO-blocked registration handoff, imported-running shared-clock fallback, and teardown and failure-mode parity explicit without claiming platform registration execution, clock or reset acquisition, IRQ ownership, live PM execution, or live MMIO validation",
    "- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope",
]

GAP_NOTE_MARKERS = [
    "- current authenticated contents rereads keep `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` directly reviewable in this smaller current-head packet",
    "- those same authenticated contents rereads still do not rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, or `zigux/tests/phase11_dw_wdt_survey.zig`, so keep that broader helper, replay, and reminder stack framed as larger same-lane vocabulary until a future authenticated reread proves it returned through the same contents bridge",
    "- public-tree fallback rereads may still surface some of those broader DesignWare reminder or replay paths, but this note should not mix that fallback visibility into the smaller authenticated current-head packet without naming the different read path explicitly",
    "- the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle remains historical context until a future reread proves it returned",
    "- the stale reminder noise this lane carried was not missing restart or PM helper coverage anymore; it was readback wording that blurred the smaller authenticated current-head packet together with the larger fallback-visible DesignWare stack",
]

CLOCK_PLAN_MARKERS = [
    "- current direct contents rereads now materialize `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`",
    "- keep the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as historical context until a future reread proves it returned",
    "- keep the next code move bounded to one timer-clock acquisition helper inside the returned `drivers/watchdog/dw_wdt.zig` packet",
    "- keep the returned direct helper trio, replay pair, validation matrix, teardown note, and checker pair explicit while the next helper stays pre-registration and host-free",
    "- keep `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` aligned with the returned helper, replay, reminder, scaffold, and checker packet before reopening driver-backed follow-through",
    "- this note keeps the returned `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, and the paired DesignWare checkers explicit as current-head evidence",
]

PLATFORM_PLAN_MARKERS = [
    "Keep the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as historical context until a future reread proves it returned.",
    "The live DesignWare packet is therefore no longer just a docs-only owner stack, but it is also not yet the broader direct-driver or replay-backed packet this note used to claim: it now truthfully centers the directly readable continuity notes, the manifest-backed registration scaffold, the returned restart helper, the bounded PM helper pair, and the two current DesignWare truthfulness checkers while leaving the wider driver, verify-helper, and replay stack unpromoted.",
    "- the current starter-laned gap inventory in `zigux/tests/phase11_dw_wdt_manifest.json`",
    "- the returned restart helper `drivers/watchdog/dw_wdt_restart.zig`, which keeps missing-drvdata and missing-timeout-image restart blocks explicit beside restart-priority registration, timeout-range and control-register writes, and reset-pulse expectations without widening into live MMIO execution",
    "- the bounded PM helper pair `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig`",
    "- the dedicated fail-closed companions `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`",
]

REGISTRATION_SCAFFOLD_MARKERS = [
    'test "platform registration scaffold summary keeps imported-running resetless registration explicit" {',
    "dw_wdt.RegistrationScaffoldState.import_running_state_then_register",
    'try std.testing.expectEqualStrings("reset_control_deassert", summary.reset_release_call);',
    "try std.testing.expect(!summary.reset_release_requested);",
    'test "platform registration scaffold summary keeps optional reset-control absence explicit" {',
    "dw_wdt.RegistrationScaffoldState.ready_to_register",
]

VERIFY_MARKERS = [
    'const dw_wdt = @import("dw_wdt.zig");',
    'test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit" {',
    "try testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_timer_clock, missing_timer_clock.state);",
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

EXPECTED_MANIFEST_LANE = "P11-L05"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"

MARKERS_BY_LABEL = {
    "alignment_note": ALIGNMENT_NOTE_MARKERS,
    "gap_note": GAP_NOTE_MARKERS,
    "clock_plan": CLOCK_PLAN_MARKERS,
    "platform_plan": PLATFORM_PLAN_MARKERS,
    "registration_scaffold": REGISTRATION_SCAFFOLD_MARKERS,
    "verify": VERIFY_MARKERS,
    "pm": PM_MARKERS,
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_manifest(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / REQUIRED_FILES["manifest"]
    if not manifest_path.is_file():
        return [f"missing_file:{REQUIRED_FILES['manifest'].as_posix()}"]

    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid_json:{manifest_path.as_posix()}:{exc}"]

    if manifest.get("lane_key") != EXPECTED_MANIFEST_LANE:
        failures.append(f"manifest_lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_MANIFEST_PIN:
        failures.append(f"manifest_surveyed_commit:{manifest.get('surveyed_commit')!r}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        failures.append("manifest_survey_summary:missing_or_not_object")
    else:
        for flag in (
            "dw_wdt_zig_present",
            "dw_wdt_test_present",
            "dw_wdt_registration_scaffold_present",
            "dw_wdt_survey_gate_present",
            "dw_wdt_survey_note_present",
            "dw_wdt_pm_helper_present",
        ):
            if summary.get(flag) is not True:
                failures.append(f"manifest_flag:{flag}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        failures.append("manifest_gaps:missing_or_not_list")
        return failures

    gap_map = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}

    verify_gap = gap_map.get(VERIFY_GAP_ID)
    if verify_gap is None:
        failures.append(f"manifest_missing_gap:{VERIFY_GAP_ID}")
    else:
        if verify_gap.get("zigux_destination") != VERIFY_DESTINATION:
            failures.append(f"manifest_verify_destination:{verify_gap.get('zigux_destination')!r}")
        if verify_gap.get("status") != "starter_landed":
            failures.append(f"manifest_verify_status:{verify_gap.get('status')!r}")

    pm_gap = gap_map.get(PM_GAP_ID)
    if pm_gap is None:
        failures.append(f"manifest_missing_gap:{PM_GAP_ID}")
    else:
        if pm_gap.get("zigux_destination") != PM_DESTINATION:
            failures.append(f"manifest_pm_destination:{pm_gap.get('zigux_destination')!r}")
        if pm_gap.get("status") != "starter_landed":
            failures.append(f"manifest_pm_status:{pm_gap.get('status')!r}")

    next_gap = gap_map.get(NEXT_GAP_ID)
    if next_gap is None:
        failures.append(f"manifest_missing_gap:{NEXT_GAP_ID}")
    else:
        if next_gap.get("zigux_destination") != NEXT_DESTINATION:
            failures.append(f"manifest_next_destination:{next_gap.get('zigux_destination')!r}")
        if next_gap.get("status") != "ready_next":
            failures.append(f"manifest_next_status:{next_gap.get('status')!r}")

    return failures


def check_repo(root: Path) -> list[str]:
    failures: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if label == "manifest":
            continue
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")
            continue
        text = read_text(path)
        for marker in MARKERS_BY_LABEL[label]:
            if marker not in text:
                failures.append(f"missing_marker:{label}:{marker}")
    failures.extend(check_manifest(root))
    return failures


def seed_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

    for label, markers in MARKERS_BY_LABEL.items():
        (root / REQUIRED_FILES[label]).write_text("\n".join(markers) + "\n", encoding="utf-8")

    manifest = {
        "lane_key": EXPECTED_MANIFEST_LANE,
        "surveyed_commit": EXPECTED_MANIFEST_PIN,
        "survey_summary": {
            "dw_wdt_zig_present": True,
            "dw_wdt_test_present": True,
            "dw_wdt_registration_scaffold_present": True,
            "dw_wdt_survey_gate_present": True,
            "dw_wdt_survey_note_present": True,
            "dw_wdt_pm_helper_present": True,
        },
        "gaps": [
            {
                "id": VERIFY_GAP_ID,
                "status": "starter_landed",
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
    }
    (root / REQUIRED_FILES["manifest"]).write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = check_repo(root)
    if expected not in failures:
        raise SystemExit(f"expected {expected!r}, got {failures}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-dw-wdt-teardown-") as tmpdir:
        root = Path(tmpdir)
        fixture = root / "fixture"
        seed_fixture(fixture)

        baseline = check_repo(fixture)
        if baseline:
            raise SystemExit("baseline self-test fixture failed: " + ", ".join(baseline))

        case_count = 1

        marker_cases = [
            ("alignment_note", ALIGNMENT_NOTE_MARKERS[2]),
            ("clock_plan", CLOCK_PLAN_MARKERS[0]),
            ("platform_plan", PLATFORM_PLAN_MARKERS[1]),
            ("gap_note", GAP_NOTE_MARKERS[1]),
            ("verify", VERIFY_MARKERS[3]),
            ("pm", PM_MARKERS[8]),
            ("pm", PM_MARKERS[13]),
        ]
        for index, (label, marker) in enumerate(marker_cases, start=1):
            case_root = root / f"marker_case_{index}"
            shutil.copytree(fixture, case_root)
            target = case_root / REQUIRED_FILES[label]
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            expect_failure(case_root, f"missing_marker:{label}:{marker}")
            case_count += 1

        manifest_lane_case = root / "manifest_lane_case"
        shutil.copytree(fixture, manifest_lane_case)
        manifest_path = manifest_lane_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["lane_key"] = "P11-L10"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_lane_case, "manifest_lane_key:'P11-L10'")
        case_count += 1

        manifest_pm_case = root / "manifest_pm_case"
        shutil.copytree(fixture, manifest_pm_case)
        manifest_path = manifest_pm_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][1]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_pm_case, "manifest_pm_status:'ready_next'")
        case_count += 1

        manifest_next_case = root / "manifest_next_case"
        shutil.copytree(fixture, manifest_next_case)
        manifest_path = manifest_next_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][2]["zigux_destination"] = "drivers/watchdog/dw_wdt.zig"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_next_case, "manifest_next_destination:'drivers/watchdog/dw_wdt.zig'")
        case_count += 1

        print("PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail-close the current returned Phase 11 DesignWare watchdog teardown packet."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    failures = check_repo(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE11_DW_WDT_TEARDOWN_PACKET=pass")
    print(f"PHASE11_DW_WDT_TEARDOWN_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE11_DW_WDT_TEARDOWN_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS_BY_LABEL.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
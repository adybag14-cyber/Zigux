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
    "provenance": Path("Documentation/zigux/phase11-dw-wdt-provenance-readback.md"),
    "validation_matrix": Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md"),
    "survey": Path("Documentation/zigux/phase11-dw-wdt-survey.md"),
    "manifest": Path("zigux/tests/phase11_dw_wdt_manifest.json"),
    "registration_scaffold": Path("zigux/tests/phase11_dw_wdt_registration_scaffold.zig"),
    "restart": Path("drivers/watchdog/dw_wdt_restart.zig"),
    "verify": Path("drivers/watchdog/dw_wdt_verify.zig"),
    "pm": Path("drivers/watchdog/dw_wdt_pm.zig"),
    "pm_scaffold": Path("drivers/watchdog/dw_wdt_pm_scaffold.zig"),
}

ALIGNMENT_NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- current authenticated contents now keep the returned validation matrix directly readable through the same bridge that serves the rest of this narrower packet",
    "- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` now records deeper platform-registration scaffold continuity `P11-L10` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still records that the broader direct-driver and replay-backed packet does not currently rematerialize through the same authenticated-contents bridge even though the verify helper has returned inside the smaller packet",
    "- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope",
]

GAP_NOTE_MARKERS = [
    "- current authenticated contents rereads keep `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` directly reviewable in this smaller current-head packet",
    "- those same authenticated contents rereads still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, or `zigux/tests/phase11_dw_wdt.zig`, so keep that broader direct-driver, direct replay, and older reminder stack framed as larger same-lane vocabulary until a future authenticated reread proves it returned through the same contents bridge",
    "- public-tree fallback rereads may still surface some of those broader DesignWare reminder or replay paths, but this note should not mix that fallback visibility into the smaller authenticated current-head packet without naming the different read path explicitly",
    "- the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle remains historical context until a future reread proves it returned",
    "- the stale reminder noise this lane carried was not missing restart, verify, or PM helper coverage anymore; it was readback wording that blurred the smaller authenticated current-head packet together with the larger fallback-visible DesignWare stack",
]

CLOCK_PLAN_MARKERS = [
    "- current direct contents rereads now materialize `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`",
    "- keep the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as historical context until a future reread proves it returned",
    "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps named-`tclk`, shared-clock fallback, blocked-no-clock preflight, optional APB clock handling, optional reset-control absence, and registration-order intent explicit without claiming live platform execution",
    "- keep the next same-lane move bounded to one acquisition-facing scaffold or one coupled truthfulness surface inside the returned smaller DesignWare packet",
    "- keep the returned validation matrix, survey note, survey gate, registration scaffold, restart helper, returned verify helper, bounded PM helper pair, and paired DesignWare checkers explicit while the broader direct driver, driver-test, slice, and teardown-note stack stays outside this direct contents bridge",
    "- preserve the registration-scaffold proof that optional reset-control absence remains a ready-to-register branch rather than a fabricated blocker",
]

PLATFORM_PLAN_MARKERS = [
    "Current authenticated contents rereads on `master` now keep this owner note,",
    "`drivers/watchdog/dw_wdt_verify.zig`,",
    "the broader direct-driver or replay-backed packet this note used to claim",
    "the returned verify helper `drivers/watchdog/dw_wdt_verify.zig`",
    "- the bounded PM helper pair `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig`",
]

PROVENANCE_MARKERS = [
    "# Phase 11 DesignWare Watchdog Provenance Readback",
    "- current authenticated contents reads now materialize `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`.",
    "- current authenticated contents reads still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, or `zigux/tests/phase11_dw_wdt.zig`, so those broader driver, direct-replay, and older reminder surfaces remain fallback-visible evidence in this environment rather than part of the same authenticated current-head packet.",
    "- the authenticated current-head packet is now internally aligned on the shared build-route boundary and the current bounded lifecycle inventory: the manifest still marks `phase11-build-gate` as `shared_gap_current_head` with `preexisting_phase11_build_present` false, keeps `dw_wdt_zig_present`, `dw_wdt_test_present`, and `dw_wdt_slice_note_present` explicitly false, and keeps the returned verify helper, restart summary, PM helper, survey note, validation matrix, and focused survey gate explicit.",
    "- the roadmap still keeps this family inside Phase 11 simple-driver starter discipline: keep owner-packet truthfulness and scaffold truthfulness bounded, and leave the next substantive step on platform-backed acquisition or MMIO follow-through rather than widening into unrelated watchdog behavior.",
]

VALIDATION_MATRIX_MARKERS = [
    "# Phase 11 DesignWare Watchdog Validation Matrix",
    "`PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
    "current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "`zigux/tests/phase11_dw_wdt_manifest.json` and",
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_verify.zig`,",
    "`zigux/tests/phase11_build.zig` is still a shared current-head gap rather",
    "The next bounded same-lane follow-up remains the manifest-marked ready-next",
]

SURVEY_MARKERS = [
    "# Phase 11 DesignWare Watchdog Survey",
    "The current lane-local packet is `P11-L10`. Authenticated current-head rereads",
    "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,",
    "`Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`,",
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_pm.zig`,",
    "`drivers/watchdog/dw_wdt_verify.zig`,",
    "Those same authenticated contents rereads do not rematerialize",
    "The shared `zigux/tests/phase11_build.zig` route remains a shared current-head",
    "The next bounded same-lane step is still the ready-next manifest gap:",
]

REGISTRATION_SCAFFOLD_MARKERS = [
    'test "platform registration scaffold summary keeps imported-running resetless registration explicit" {',
    "dw_wdt.RegistrationScaffoldState.import_running_state_then_register",
    'try std.testing.expectEqualStrings("reset_control_deassert", summary.reset_release_call);',
    "try std.testing.expect(!summary.reset_release_requested);",
    'test "platform registration scaffold summary keeps optional reset-control absence explicit" {',
    "dw_wdt.RegistrationScaffoldState.ready_to_register",
]

RESTART_MARKERS = [
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt restart summary keeps missing drvdata explicit" {',
    "try std.testing.expectEqual(RestartState.blocked_missing_drvdata, summary.state);",
    'test "phase11 dw_wdt restart summary keeps missing timeout image explicit" {',
    "try std.testing.expectEqual(RestartState.blocked_missing_timeout_image, summary.state);",
    'test "phase11 dw_wdt restart summary keeps restart register writes explicit" {',
    'try std.testing.expectEqualStrings("watchdog_set_restart_priority",',
    'test "phase11 dw_wdt restart summary preserves explicit in-scope replay overrides" {',
    "try std.testing.expect(summary.blocked_on_live_mmio);",
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

PM_SCAFFOLD_MARKERS = [
    'pub const anchor_path = "drivers/watchdog/dw_wdt.c";',
    'test "phase11 dw_wdt pm scaffold keeps idle suspend and resume explicit" {',
    "try std.testing.expectEqual(SuspendDisposition.idle_noop, suspend_report.disposition);",
    "try std.testing.expectEqual(ResumeDisposition.idle_noop, resume_report.disposition);",
    'test "phase11 dw_wdt pm scaffold quiesces a stoppable watchdog before suspend" {',
    "try std.testing.expectEqual(SuspendDisposition.quiesce_before_suspend, suspend_report.disposition);",
    'test "phase11 dw_wdt pm scaffold keeps no-way-out hardware running across suspend and resume" {',
    "try std.testing.expectEqual(ResumeDisposition.keep_running_without_restore, resume_report.disposition);",
    'test "phase11 dw_wdt pm scaffold keeps live-mmio blocker explicit for running hardware" {',
    "try std.testing.expectEqual(ResumeDisposition.blocked_on_live_mmio, resume_report.disposition);",
]

EXPECTED_MANIFEST_LANE = "P11-L10"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
RESTART_GAP_ID = "phase11-dw-wdt-restart-summary"
RESTART_DESTINATION = "drivers/watchdog/dw_wdt_restart.zig"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"

MARKERS_BY_LABEL = {
    "alignment_note": ALIGNMENT_NOTE_MARKERS,
    "gap_note": GAP_NOTE_MARKERS,
    "clock_plan": CLOCK_PLAN_MARKERS,
    "platform_plan": PLATFORM_PLAN_MARKERS,
    "provenance": PROVENANCE_MARKERS,
    "validation_matrix": VALIDATION_MATRIX_MARKERS,
    "survey": SURVEY_MARKERS,
    "registration_scaffold": REGISTRATION_SCAFFOLD_MARKERS,
    "restart": RESTART_MARKERS,
    "verify": VERIFY_MARKERS,
    "pm": PM_MARKERS,
    "pm_scaffold": PM_SCAFFOLD_MARKERS,
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
        expected_flags = {
            "dw_wdt_zig_present": False,
            "dw_wdt_test_present": False,
            "dw_wdt_registration_scaffold_present": True,
            "dw_wdt_registration_order_present": True,
            "dw_wdt_slice_note_present": False,
            "dw_wdt_survey_gate_present": True,
            "dw_wdt_survey_note_present": True,
            "dw_wdt_pm_helper_present": True,
            "dw_wdt_restart_helper_present": True,
            "dw_wdt_verify_helper_present": True,
        }
        for flag, expected in expected_flags.items():
            if summary.get(flag) is not expected:
                failures.append(f"manifest_flag:{flag}:{summary.get(flag)!r}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        failures.append("manifest_gaps:missing_or_not_list")
        return failures

    gap_map = {gap.get("id"): gap for gap in gaps if isinstance(gap, dict)}

    restart_gap = gap_map.get(RESTART_GAP_ID)
    if restart_gap is None:
        failures.append(f"manifest_missing_gap:{RESTART_GAP_ID}")
    else:
        if restart_gap.get("zigux_destination") != RESTART_DESTINATION:
            failures.append(f"manifest_restart_destination:{restart_gap.get('zigux_destination')!r}")
        if restart_gap.get("status") != "starter_landed":
            failures.append(f"manifest_restart_status:{restart_gap.get('status')!r}")

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
            "dw_wdt_zig_present": False,
            "dw_wdt_test_present": False,
            "dw_wdt_registration_scaffold_present": True,
            "dw_wdt_registration_order_present": True,
            "dw_wdt_slice_note_present": False,
            "dw_wdt_survey_gate_present": True,
            "dw_wdt_survey_note_present": True,
            "dw_wdt_pm_helper_present": True,
            "dw_wdt_restart_helper_present": True,
            "dw_wdt_verify_helper_present": True,
        },
        "gaps": [
            {"id": VERIFY_GAP_ID, "status": "starter_landed", "zigux_destination": VERIFY_DESTINATION},
            {"id": RESTART_GAP_ID, "status": "starter_landed", "zigux_destination": RESTART_DESTINATION},
            {"id": PM_GAP_ID, "status": "starter_landed", "zigux_destination": PM_DESTINATION},
            {"id": NEXT_GAP_ID, "status": "ready_next", "zigux_destination": NEXT_DESTINATION},
        ],
    }
    (root / REQUIRED_FILES["manifest"]).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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
            ("alignment_note", ALIGNMENT_NOTE_MARKERS[4]),
            ("clock_plan", CLOCK_PLAN_MARKERS[0]),
            ("clock_plan", CLOCK_PLAN_MARKERS[4]),
            ("platform_plan", PLATFORM_PLAN_MARKERS[1]),
            ("platform_plan", PLATFORM_PLAN_MARKERS[4]),
            ("gap_note", GAP_NOTE_MARKERS[1]),
            ("provenance", PROVENANCE_MARKERS[1]),
            ("provenance", PROVENANCE_MARKERS[3]),
            ("validation_matrix", VALIDATION_MATRIX_MARKERS[1]),
            ("validation_matrix", VALIDATION_MATRIX_MARKERS[2]),
            ("validation_matrix", VALIDATION_MATRIX_MARKERS[5]),
            ("survey", SURVEY_MARKERS[2]),
            ("survey", SURVEY_MARKERS[8]),
            ("registration_scaffold", REGISTRATION_SCAFFOLD_MARKERS[0]),
            ("registration_scaffold", REGISTRATION_SCAFFOLD_MARKERS[4]),
            ("restart", RESTART_MARKERS[1]),
            ("restart", RESTART_MARKERS[5]),
            ("verify", VERIFY_MARKERS[2]),
            ("verify", VERIFY_MARKERS[4]),
            ("pm", PM_MARKERS[8]),
            ("pm", PM_MARKERS[13]),
            ("pm_scaffold", PM_SCAFFOLD_MARKERS[1]),
            ("pm_scaffold", PM_SCAFFOLD_MARKERS[8]),
        ]
        for index, (label, marker) in enumerate(marker_cases, start=1):
            case_root = root / f"marker_case_{index}"
            shutil.copytree(fixture, case_root)
            target = case_root / REQUIRED_FILES[label]
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            expect_failure(case_root, f"missing_marker:{label}:{marker}")
            case_count += 1

        missing_matrix_case = root / "missing_matrix_case"
        shutil.copytree(fixture, missing_matrix_case)
        (missing_matrix_case / REQUIRED_FILES["validation_matrix"]).unlink()
        expect_failure(
            missing_matrix_case,
            f"missing_file:{REQUIRED_FILES['validation_matrix'].as_posix()}",
        )
        case_count += 1

        manifest_lane_case = root / "manifest_lane_case"
        shutil.copytree(fixture, manifest_lane_case)
        manifest_path = manifest_lane_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["lane_key"] = "P11-L05"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_lane_case, "manifest_lane_key:'P11-L05'")
        case_count += 1

        manifest_pin_case = root / "manifest_pin_case"
        shutil.copytree(fixture, manifest_pin_case)
        manifest_path = manifest_pin_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["surveyed_commit"] = "0000000000000000000000000000000000000000"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_pin_case, "manifest_surveyed_commit:'0000000000000000000000000000000000000000'")
        case_count += 1

        manifest_registration_order_flag_case = root / "manifest_registration_order_flag_case"
        shutil.copytree(fixture, manifest_registration_order_flag_case)
        manifest_path = manifest_registration_order_flag_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["survey_summary"]["dw_wdt_registration_order_present"] = False
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_registration_order_flag_case, "manifest_flag:dw_wdt_registration_order_present:False")
        case_count += 1

        manifest_slice_note_flag_case = root / "manifest_slice_note_flag_case"
        shutil.copytree(fixture, manifest_slice_note_flag_case)
        manifest_path = manifest_slice_note_flag_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["survey_summary"]["dw_wdt_slice_note_present"] = True
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_slice_note_flag_case, "manifest_flag:dw_wdt_slice_note_present:True")
        case_count += 1

        manifest_pm_helper_flag_case = root / "manifest_pm_helper_flag_case"
        shutil.copytree(fixture, manifest_pm_helper_flag_case)
        manifest_path = manifest_pm_helper_flag_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["survey_summary"]["dw_wdt_pm_helper_present"] = False
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_pm_helper_flag_case, "manifest_flag:dw_wdt_pm_helper_present:False")
        case_count += 1

        manifest_restart_helper_flag_case = root / "manifest_restart_helper_flag_case"
        shutil.copytree(fixture, manifest_restart_helper_flag_case)
        manifest_path = manifest_restart_helper_flag_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["survey_summary"]["dw_wdt_restart_helper_present"] = False
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_restart_helper_flag_case, "manifest_flag:dw_wdt_restart_helper_present:False")
        case_count += 1

        manifest_verify_flag_case = root / "manifest_verify_flag_case"
        shutil.copytree(fixture, manifest_verify_flag_case)
        manifest_path = manifest_verify_flag_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["survey_summary"]["dw_wdt_verify_helper_present"] = False
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_verify_flag_case, "manifest_flag:dw_wdt_verify_helper_present:False")
        case_count += 1

        manifest_verify_gap_case = root / "manifest_verify_gap_case"
        shutil.copytree(fixture, manifest_verify_gap_case)
        manifest_path = manifest_verify_gap_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][0]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_verify_gap_case, "manifest_verify_status:'ready_next'")
        case_count += 1

        manifest_restart_gap_case = root / "manifest_restart_gap_case"
        shutil.copytree(fixture, manifest_restart_gap_case)
        manifest_path = manifest_restart_gap_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][1]["zigux_destination"] = "drivers/watchdog/dw_wdt_pm.zig"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_restart_gap_case, "manifest_restart_destination:'drivers/watchdog/dw_wdt_pm.zig'")
        case_count += 1

        manifest_pm_case = root / "manifest_pm_case"
        shutil.copytree(fixture, manifest_pm_case)
        manifest_path = manifest_pm_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][2]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_pm_case, "manifest_pm_status:'ready_next'")
        case_count += 1

        manifest_next_case = root / "manifest_next_case"
        shutil.copytree(fixture, manifest_next_case)
        manifest_path = manifest_next_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][3]["zigux_destination"] = "drivers/watchdog/dw_wdt_pm.zig"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(manifest_next_case, "manifest_next_destination:'drivers/watchdog/dw_wdt_pm.zig'")
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

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
    "plan": Path("Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md"),
    "manifest": Path("zigux/tests/phase11_dw_wdt_manifest.json"),
    "registration_scaffold": Path("zigux/tests/phase11_dw_wdt_registration_scaffold.zig"),
}

ALIGNMENT_NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- `drivers/watchdog/dw_wdt_verify.zig` currently keeps stop-teardown ownership, inactive-versus-missing-`drvdata` teardown branching, and restart failure-mode coverage explicit without claiming platform registration execution, clock or reset acquisition, IRQ ownership, PM behavior, or live MMIO validation",
    "- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` now keeps the resolved matrix-versus-manifest alignment and the current verify-helper scope fail-closed",
    "- the next substantive non-doc move should remain one platform-backed acquisition scaffold only",
]

GAP_NOTE_MARKERS = [
    "current direct tree readback still materializes `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, and `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`",
    "current direct tree readback did not rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, or `scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md` already keeps those missing helper, matrix, survey, slice, teardown, replay, and packet-checker surfaces framed as repo-reality gaps, but `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md` still narrates the next slice as if the direct helper pair and direct replay are current-head evidence",
]

PLAN_MARKERS = [
    "current direct contents rereads do not rematerialize `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so keep them framed as last-known packet members or repo-reality gaps instead of current-head evidence",
    "when `drivers/watchdog/dw_wdt.zig` rematerializes again, land only one timer-clock acquisition helper that records named-`tclk` success, shared-clock fallback success, and blocked-no-clock failure",
    "optional reset-control absence can still remain a ready-to-register scaffold branch while `reset_control_deassert` stays visible as an unrequested outcome rather than an implicit blocker",
    "preserve the registration-scaffold proof that model reset-control availability and reset-release intent as explicit outcome-bearing steps while preserving the already-readable ready-to-register branch when reset control is absent",
    "keep optional reset-control absence explicit as a ready-to-register scaffold branch so the bounded packet does not overstate reset wiring as mandatory before host-free registration review",
]

REGISTRATION_SCAFFOLD_MARKERS = [
    'test "platform registration scaffold summary keeps imported-running resetless registration explicit" {',
    "dw_wdt.RegistrationScaffoldState.import_running_state_then_register",
    'try std.testing.expectEqualStrings("reset_control_deassert", summary.reset_release_call);',
    "try std.testing.expect(!summary.reset_release_requested);",
]

EXPECTED_MANIFEST_LANE = "P11-L05"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
READY_NEXT_GAP_ID = "phase11-dw-wdt-live-platform-pm"
READY_NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"

MARKERS_BY_LABEL = {
    "alignment_note": ALIGNMENT_NOTE_MARKERS,
    "gap_note": GAP_NOTE_MARKERS,
    "plan": PLAN_MARKERS,
    "registration_scaffold": REGISTRATION_SCAFFOLD_MARKERS,
}

SELF_TEST_CASES = (
    ("alignment_note_marker_missing", "alignment_note", ALIGNMENT_NOTE_MARKERS[1]),
    ("gap_note_marker_missing", "gap_note", GAP_NOTE_MARKERS[1]),
    ("plan_marker_missing", "plan", PLAN_MARKERS[0]),
    (
        "registration_scaffold_marker_missing",
        "registration_scaffold",
        REGISTRATION_SCAFFOLD_MARKERS[0],
    ),
)


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
        if summary.get("dw_wdt_registration_scaffold_present") is not True:
            failures.append("manifest_registration_scaffold_present")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        failures.append("manifest_gaps:missing_or_not_list")
        return failures

    verify_gap = None
    ready_next_gap = None
    for gap in gaps:
        if not isinstance(gap, dict):
            failures.append("manifest_gap:not_object")
            continue
        if gap.get("id") == VERIFY_GAP_ID:
            verify_gap = gap
        if gap.get("id") == READY_NEXT_GAP_ID:
            ready_next_gap = gap

    if verify_gap is None:
        failures.append(f"manifest_missing_gap:{VERIFY_GAP_ID}")
    else:
        if verify_gap.get("zigux_destination") != VERIFY_DESTINATION:
            failures.append(
                "manifest_verify_destination:"
                f"{verify_gap.get('zigux_destination')!r}"
            )
        if verify_gap.get("status") != "starter_landed":
            failures.append(f"manifest_verify_status:{verify_gap.get('status')!r}")

    if ready_next_gap is None:
        failures.append(f"manifest_missing_gap:{READY_NEXT_GAP_ID}")
    else:
        if ready_next_gap.get("status") != "ready_next":
            failures.append(f"manifest_ready_next_status:{ready_next_gap.get('status')!r}")
        if ready_next_gap.get("zigux_destination") != READY_NEXT_DESTINATION:
            failures.append(
                "manifest_ready_next_destination:"
                f"{ready_next_gap.get('zigux_destination')!r}"
            )

    return failures


def check_repo(root: Path) -> list[str]:
    missing: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if label == "manifest":
            continue
        path = root / rel_path
        if not path.is_file():
            missing.append(f"missing_file:{rel_path.as_posix()}")
            continue
        text = read_text(path)
        for marker in MARKERS_BY_LABEL[label]:
            if marker not in text:
                missing.append(f"missing_marker:{label}:{marker}")
    missing.extend(check_manifest(root))
    return missing


def seed_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

    for label, markers in MARKERS_BY_LABEL.items():
        (root / REQUIRED_FILES[label]).write_text("\n".join(markers), encoding="utf-8")

    (root / REQUIRED_FILES["manifest"]).writeText = None
    (root / REQUIRED_FILES["manifest"]).write_text(
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE,
                "surveyed_commit": EXPECTED_MANIFEST_PIN,
                "survey_summary": {
                    "dw_wdt_registration_scaffold_present": True,
                },
                "gaps": [
                    {
                        "id": VERIFY_GAP_ID,
                        "status": "starter_landed",
                        "zigux_destination": VERIFY_DESTINATION,
                    },
                    {
                        "id": READY_NEXT_GAP_ID,
                        "status": "ready_next",
                        "zigux_destination": READY_NEXT_DESTINATION,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-dw-wdt-teardown-") as tmpdir:
        root = Path(tmpdir)
        seed_fixture(root)

        baseline = check_repo(root)
        if baseline:
            raise SystemExit("baseline self-test fixture failed: " + ", ".join(baseline))

        case_count = 1
        for case_name, label, marker in SELF_TEST_CASES:
            case_root = root / case_name
            shutil.copytree(root, case_root)
            target = case_root / REQUIRED_FILES[label]
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            failures = check_repo(case_root)
            expected = f"missing_marker:{label}:{marker}"
            if expected not in failures:
                raise SystemExit(
                    f"self-test case {case_name} did not fail as expected: {failures}"
                )
            case_count += 1

        manifest_lane_case = root / "manifest_lane_case"
        shutil.copytree(root, manifest_lane_case)
        manifest_path = manifest_lane_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["lane_key"] = "P11-L10"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        failures = check_repo(manifest_lane_case)
        if "manifest_lane_key:'P11-L10'" not in failures:
            raise SystemExit(f"manifest lane self-test failed: {failures}")
        case_count += 1

        manifest_destination_case = root / "manifest_destination_case"
        shutil.copytree(root, manifest_destination_case)
        manifest_path = manifest_destination_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][0]["zigux_destination"] = "drivers/watchdog/dw_wdt.zig"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        failures = check_repo(manifest_destination_case)
        if "manifest_verify_destination:'drivers/watchdog/dw_wdt.zig'" not in failures:
            raise SystemExit(f"manifest destination self-test failed: {failures}")
        case_count += 1

        manifest_ready_next_case = root / "manifest_ready_next_case"
        shutil.copytree(root, manifest_ready_next_case)
        manifest_path = manifest_ready_next_case / REQUIRED_FILES["manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][1]["status"] = "starter_landed"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        failures = check_repo(manifest_ready_next_case)
        if "manifest_ready_next_status:'starter_landed'" not in failures:
            raise SystemExit(f"manifest ready-next self-test failed: {failures}")
        case_count += 1

        missing_file_case = root / "missing_file_case"
        shutil.copytree(root, missing_file_case)
        (missing_file_case / REQUIRED_FILES["alignment_note"]).unlink()
        failures = check_repo(missing_file_case)
        expected_missing = f"missing_file:{REQUIRED_FILES['alignment_note'].as_posix()}"
        if expected_missing not in failures:
            raise SystemExit(f"missing-file self-test failed: {failures}")
        case_count += 1

        print("PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_root = script_path.parents[2] if len(script_path.parents) > 2 else Path.cwd()
    parser = argparse.ArgumentParser(
        description="Fail-close the current Phase 11 DesignWare watchdog teardown packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in checker self-tests instead of inspecting a repo",
    )
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

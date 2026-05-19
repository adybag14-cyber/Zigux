#!/usr/bin/env python3
"""Fail-closed checker for the resolved Phase 11 DesignWare verify-alignment packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "note": "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "verify": "drivers/watchdog/dw_wdt_verify.zig",
    "pm": "drivers/watchdog/dw_wdt_pm.zig",
}

EXPECTED_MATRIX_LANE = "P11-L05"
EXPECTED_MATRIX_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
EXPECTED_MANIFEST_LANE = "P11-L05"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
PM_DESTINATION = "drivers/watchdog/dw_wdt_pm.zig"
PM_GAP_ID = "phase11-dw-wdt-live-platform-pm"
NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"
NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"

NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- lane: `P11-L10`",
    "- current `master` no longer has a matrix-versus-manifest continuity split for the DesignWare verify packet: both `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` and `zigux/tests/phase11_dw_wdt_manifest.json` record continuity `P11-L05` with surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- `drivers/watchdog/dw_wdt_verify.zig` currently keeps registration-blocking failure paths, MMIO-blocked registration handoff, imported-running shared-clock fallback, and teardown and failure-mode parity explicit without claiming platform registration execution, clock or reset acquisition, IRQ ownership, live PM execution, or live MMIO validation",
    "- `drivers/watchdog/dw_wdt_pm.zig` now also keeps bounded suspend and resume handoff summaries explicit across missing-drvdata blocks, running-hardware suspend stop intent, imported-running resume recovery, and timeout-reprogram blocks while still keeping live PM execution out of scope",
    "This note now exists as a closed-gap companion: it records that the shared validation matrix and manifest agree again, it records that the adjacent bounded PM helper is now landed, and it keeps a small fail-closed checker in place so future lane or surveyed-head drift reopens immediately instead of hiding inside Phase 11 reminder surfaces.",
    "- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` describes the active continuity as `P11-L05` with surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` matches that same lane key and surveyed commit while still routing `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` also marks `phase11-dw-wdt-live-platform-pm` as `starter_landed` at `drivers/watchdog/dw_wdt_pm.zig` and keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`",
    "- `drivers/watchdog/dw_wdt_verify.zig` keeps `test \"phase11 dw_wdt verify keeps registration-blocking failure paths explicit\"`, `test \"phase11 dw_wdt verify keeps mmio-blocked registration handoff explicit\"`, `test \"phase11 dw_wdt verify keeps imported-running handoff and shared-clock fallback explicit\"`, `test \"phase11 dw_wdt verify keeps continued-heartbeat teardown and remove failure modes explicit\"`, `test \"phase11 dw_wdt verify keeps reset-backed teardown and remove cleanup distinct\"`, and `test \"phase11 dw_wdt verify keeps idle no-op teardown and remove paths explicit\"` reviewable on current `master`",
    "- `drivers/watchdog/dw_wdt_pm.zig` keeps `test \"phase11 dw_wdt pm suspend keeps missing drvdata explicit\"`, `test \"phase11 dw_wdt pm suspend keeps running-hardware stop handoff explicit\"`, `test \"phase11 dw_wdt pm resume keeps imported-running handoff explicit\"`, and `test \"phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore\"` reviewable on current `master`",
    "- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` now keeps the resolved matrix-versus-manifest alignment, the adjacent bounded PM-helper landing, and the current next-step scope fail-closed",
    "- the next substantive non-doc move should now remain the manifest-backed live-MMIO validation step, still without widening beyond the bounded platform-backed probe, remove, suspend, and resume edges already named by the current packet",
]

MATRIX_MARKERS = [
    "# Phase 11 DesignWare Watchdog Validation Matrix",
    "current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "active watchdog continuity for this matrix and its coupled survey packet is `P11-L05`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
]

VERIFY_MARKERS = [
    'const dw_wdt = @import("dw_wdt.zig");',
    'test "phase11 dw_wdt verify keeps registration-blocking failure paths explicit" {',
    "try testing.expectEqual(dw_wdt.RegistrationScaffoldState.blocked_missing_drvdata, missing_drvdata.state);",
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
    'test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {',
    "PmResumeState.import_running_state_then_restore_hooks,",
    'test "phase11 dw_wdt pm resume keeps timeout reprogram block explicit before idle restore" {',
    "PmResumeState.blocked_live_mmio_timeout_reprogram,",
    "try std.testing.expectEqual(PmResumeState.restore_idle_hooks, restored.state);",
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
    matrix = read_text(root, FILES["matrix"])
    manifest = read_manifest(root)
    verify = read_text(root, FILES["verify"])
    pm = read_text(root, FILES["pm"])

    expect_markers("note", note, NOTE_MARKERS)
    expect_markers("matrix", matrix, MATRIX_MARKERS)
    expect_markers("verify", verify, VERIFY_MARKERS)
    expect_markers("pm", pm, PM_MARKERS)
    expect_manifest_state(manifest)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["note"], "\n".join(NOTE_MARKERS) + "\n")
    write(root / FILES["matrix"], "\n".join(MATRIX_MARKERS) + "\n")
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_verify_alignment_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        marker_cases = (
            [("note", marker) for marker in NOTE_MARKERS]
            + [("matrix", marker) for marker in MATRIX_MARKERS]
            + [("verify", marker) for marker in VERIFY_MARKERS]
            + [("pm", marker) for marker in PM_MARKERS]
        )
        for idx, (label, marker) in enumerate(marker_cases, start=1):
            case_root = tmpdir / f"marker_{idx}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            write(path, path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1))
            expect_failure(case_root, marker)

        manifest_lane_case = tmpdir / "manifest_lane_case"
        shutil.copytree(fixture, manifest_lane_case, dirs_exist_ok=True)
        manifest_path = manifest_lane_case / FILES["manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["lane_key"] = "P11-L10"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(manifest_lane_case, "manifest lane_key mismatch")

        manifest_pin_case = tmpdir / "manifest_pin_case"
        shutil.copytree(fixture, manifest_pin_case, dirs_exist_ok=True)
        manifest_path = manifest_pin_case / FILES["manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["surveyed_commit"] = "6726fdd9da4eef55498fb06c38815317a684bcbf"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(manifest_pin_case, "manifest surveyed_commit mismatch")

        manifest_gap_case = tmpdir / "manifest_gap_case"
        shutil.copytree(fixture, manifest_gap_case, dirs_exist_ok=True)
        manifest_path = manifest_gap_case / FILES["manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["gaps"][1]["status"] = "ready_next"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(manifest_gap_case, "manifest pm status mismatch")

        self_test_case_count = len(marker_cases) + 3
        print("PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST=pass")
        print(
            f"PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST_CASE_COUNT={self_test_case_count}"
        )
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
        print(f"PHASE11_DW_WDT_VERIFY_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_VERIFY_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

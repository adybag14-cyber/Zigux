#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 bcm2835 versus dw_wdt lifecycle gap note."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "note": "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
    "bcm_packet": "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig",
    "dw_plan": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "dw_verify_gap": "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "dw_manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
    "dw_scaffold": "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
}

NOTE_MARKERS = [
    "# Phase 11 Watchdog Lifecycle Parity Gap",
    "- lane: `P11-L07`",
    "- scope: `drivers/watchdog/bcm2835_wdt` and `drivers/watchdog/dw_wdt` straightforward watchdog lifecycle parity",
    "- the Phase 11 roadmap still keeps simple production drivers on straightforward lifecycles together with teardown and failure-mode parity around `drivers/watchdog/*.zig`",
    "- current `master` keeps `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig` directly readable as the bcm2835 lifecycle-backed packet survey",
    "- current `master` keeps `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` directly readable as the narrower DesignWare owner packet",
    "- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig` still requires `drivers/watchdog/bcm2835_wdt.zig` to expose `maxTimeoutSeconds(...)`, `secondsToWatchdogTicks(...)`, `summarizeProbe(...)`, `summarizePlatformHandoff(...)`, `Bcm2835WdtLab.importBootloaderRunning(...)`, and `Bcm2835WdtLab.poweroff(...)`",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps `phase11-dw-wdt-platform-registration-scaffold` at `starter_landed` and keeps `phase11-dw-wdt-live-platform-pm` at `ready_next`",
    "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` still keeps named-`tclk` acquisition, shared-clock fallback, optional APB clock, optional reset-control absence, imported-running registration handoff, and blocked-missing-timer-clock outcomes explicit before live platform registration",
    "Current repo reality therefore does not yet show straightforward cross-driver lifecycle parity between `bcm2835_wdt` and `dw_wdt`.",
    "- keep `dw_wdt` on one acquisition-facing platform-registration scaffold or summary extension only",
]

BCM_PACKET_MARKERS = [
    'try expectContains(driver, "pub fn maxTimeoutSeconds() u32");',
    'try expectContains(driver, "pub fn secondsToWatchdogTicks(seconds: u32) !u32");',
    'try expectContains(driver, "pub fn summarizeProbe(request: ProbeRequest) !ProbeSummary");',
    'try expectContains(driver, "pub fn summarizePlatformHandoff(request: PlatformHandoffRequest) !PlatformHandoffSummary");',
    'try expectContains(driver, "pub fn importBootloaderRunning(self: *Bcm2835WdtLab) !void");',
    'try expectContains(driver, "pub fn poweroff(self: *Bcm2835WdtLab, handler_claimed: bool) PoweroffSummary");',
    'try expectContains(replay, "phase11 bcm2835 watchdog replay keeps start stop restart and poweroff lifecycle explicit");',
    'try expectContains(verify, "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct");',
]

DW_PLAN_MARKERS = [
    "# Phase 11 DesignWare Watchdog Platform Registration Plan",
    "The next bounded follow-up is still to attach the existing registration-facing",
    "The preferred first packet is:",
    "1. model timer-clock acquisition and optional APB clock acquisition as explicit outcome-bearing steps",
    "2. model reset-control availability and reset-release intent as explicit outcome-bearing steps while preserving the already-readable ready-to-register branch when reset control is absent",
    "- live MMIO reads or writes",
    "- IRQ request or handler execution",
    "- suspend or resume behavior",
]

DW_VERIFY_GAP_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- `drivers/watchdog/dw_wdt_verify.zig` currently keeps stop-teardown ownership, inactive-versus-missing-`drvdata` teardown branching, and restart failure-mode coverage explicit without claiming platform registration execution, clock or reset acquisition, IRQ ownership, PM behavior, or live MMIO validation",
    "- the next substantive non-doc move should remain one platform-backed acquisition scaffold only",
]

DW_SCAFFOLD_MARKERS = [
    'test "platform resource preflight keeps named acquisition surfaces explicit"',
    'test "platform resource preflight keeps shared fallback and missing-clock block explicit"',
    'test "platform handoff keeps imported-running registration state explicit"',
    'test "platform registration scaffold summary keeps optional reset-control absence explicit"',
    'test "platform registration scaffold summary keeps missing timer clock block explicit"',
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
    path = root / FILES["dw_manifest"]
    try:
        value = json.loads(read_text(root, FILES["dw_manifest"]))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError("dw manifest root must be an object")
    return value


def expect_dw_gap(manifest: dict[str, object], gap_id: str, expected_status: str) -> None:
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("dw manifest gaps must be a list")
    for entry in gaps:
        if not isinstance(entry, dict):
            raise CheckError("dw manifest gaps entries must be objects")
        if entry.get("id") == gap_id:
            status = entry.get("status")
            if status != expected_status:
                raise CheckError(
                    f"dw manifest {gap_id} status mismatch: expected {expected_status}, got {status!r}"
                )
            return
    raise CheckError(f"dw manifest missing gap entry: {gap_id}")


def run_check(root: Path) -> None:
    note = read_text(root, FILES["note"])
    bcm_packet = read_text(root, FILES["bcm_packet"])
    dw_plan = read_text(root, FILES["dw_plan"])
    dw_verify_gap = read_text(root, FILES["dw_verify_gap"])
    dw_manifest = read_manifest(root)
    dw_scaffold = read_text(root, FILES["dw_scaffold"])

    expect_markers("note", note, NOTE_MARKERS)
    expect_markers("bcm_packet", bcm_packet, BCM_PACKET_MARKERS)
    expect_markers("dw_plan", dw_plan, DW_PLAN_MARKERS)
    expect_markers("dw_verify_gap", dw_verify_gap, DW_VERIFY_GAP_MARKERS)
    expect_markers("dw_scaffold", dw_scaffold, DW_SCAFFOLD_MARKERS)
    expect_dw_gap(dw_manifest, "phase11-dw-wdt-platform-registration-scaffold", "starter_landed")
    expect_dw_gap(dw_manifest, "phase11-dw-wdt-live-platform-pm", "ready_next")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["note"], "\n".join(NOTE_MARKERS) + "\n")
    write(root / FILES["bcm_packet"], "\n".join(BCM_PACKET_MARKERS) + "\n")
    write(root / FILES["dw_plan"], "\n".join(DW_PLAN_MARKERS) + "\n")
    write(root / FILES["dw_verify_gap"], "\n".join(DW_VERIFY_GAP_MARKERS) + "\n")
    write(root / FILES["dw_scaffold"], "\n".join(DW_SCAFFOLD_MARKERS) + "\n")
    write(
        root / FILES["dw_manifest"],
        json.dumps(
            {
                "gaps": [
                    {
                        "id": "phase11-dw-wdt-platform-registration-scaffold",
                        "status": "starter_landed",
                    },
                    {
                        "id": "phase11-dw-wdt-live-platform-pm",
                        "status": "ready_next",
                    },
                ]
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_watchdog_lifecycle_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        marker_cases = (
            [("note", marker) for marker in NOTE_MARKERS]
            + [("bcm_packet", marker) for marker in BCM_PACKET_MARKERS]
            + [("dw_plan", marker) for marker in DW_PLAN_MARKERS]
            + [("dw_verify_gap", marker) for marker in DW_VERIFY_GAP_MARKERS]
            + [("dw_scaffold", marker) for marker in DW_SCAFFOLD_MARKERS]
        )
        for idx, (label, marker) in enumerate(marker_cases, start=1):
            case_root = tmpdir / f"marker_{idx}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            write(path, path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1))
            expect_failure(case_root, marker)

        gap_case = tmpdir / "gap_case"
        shutil.copytree(fixture, gap_case, dirs_exist_ok=True)
        manifest_path = gap_case / FILES["dw_manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["gaps"][0]["status"] = "ready_next"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(gap_case, "dw manifest phase11-dw-wdt-platform-registration-scaffold status mismatch")

        pm_case = tmpdir / "pm_case"
        shutil.copytree(fixture, pm_case, dirs_exist_ok=True)
        manifest_path = pm_case / FILES["dw_manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["gaps"][1]["status"] = "starter_landed"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(pm_case, "dw manifest phase11-dw-wdt-live-platform-pm status mismatch")

        self_test_case_count = len(marker_cases) + 2
        print("PHASE11_WATCHDOG_LIFECYCLE_GAP_SELF_TEST=pass")
        print(f"PHASE11_WATCHDOG_LIFECYCLE_GAP_SELF_TEST_CASE_COUNT={self_test_case_count}")
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
        print(f"PHASE11_WATCHDOG_LIFECYCLE_GAP=fail: {exc}")
        return 1

    print("PHASE11_WATCHDOG_LIFECYCLE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

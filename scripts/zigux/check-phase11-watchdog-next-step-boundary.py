#!/usr/bin/env python3
"""Fail-closed checker for the merged Phase 11 watchdog next-step boundary."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "bcm_survey": "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "dw_gap": "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "dw_manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
}

BCM_SURVEY_MARKERS = [
    "# Phase 11 BCM2835 Watchdog Survey",
    "* archival packet identity remains `P11-L08`",
    "* the Phase 11 simple-driver roadmap gap is closed at starter depth",
    "* remaining blocked work is still live platform registration, PM-base plumbing, watchdog-core registration, shared poweroff-handler execution, and hardware-backed validation beyond the current helper-backed packet",
    "* bounded watchdog-lab state transitions for `start()`, `stop()`, `restart()`, and `poweroff()`",
    "## Next Bounded Step",
    "The next honest same-lane follow-through is no longer another reminder-surface add.",
    "Keep future bcm2835 work inside a later driver-local or explicit validation-plan step",
]

DW_GAP_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- current `master` no longer has a matrix-versus-manifest continuity split",
    "- `drivers/watchdog/dw_wdt_pm.zig` now also keeps bounded suspend and resume handoff summaries explicit",
    "- nearby continuity notes in the memory folder already treat this alignment drift as closed",
    "- `zigux/tests/phase11_dw_wdt_manifest.json` also marks `phase11-dw-wdt-live-platform-pm` as `starter_landed` at `drivers/watchdog/dw_wdt_pm.zig` and keeps `phase11-dw-wdt-live-mmio-validation` parked as `ready_next` at `zigux/tests/phase11_dw_wdt.zig`",
    "- the next substantive non-doc move should now remain the manifest-backed live-MMIO validation step",
]

EXPECTED_MANIFEST_LANE = "P11-L05"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
EXPECTED_GAPS = {
    "phase11-dw-wdt-live-platform-pm": {
        "status": "starter_landed",
        "zigux_destination": "drivers/watchdog/dw_wdt_pm.zig",
    },
    "phase11-dw-wdt-live-mmio-validation": {
        "status": "ready_next",
        "zigux_destination": "zigux/tests/phase11_dw_wdt.zig",
    },
}


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
        raise CheckError("manifest root must be an object")
    return value


def expect_manifest(manifest: dict[str, object]) -> None:
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

    remaining = dict(EXPECTED_GAPS)
    for entry in gaps:
        if not isinstance(entry, dict):
            raise CheckError("manifest gaps entries must be objects")
        gap_id = entry.get("id")
        if gap_id not in remaining:
            continue
        expected = remaining.pop(gap_id)
        if entry.get("status") != expected["status"]:
            raise CheckError(
                f"manifest {gap_id} status mismatch: expected {expected['status']!r}, got {entry.get('status')!r}"
            )
        if entry.get("zigux_destination") != expected["zigux_destination"]:
            raise CheckError(
                "manifest "
                f"{gap_id} destination mismatch: expected {expected['zigux_destination']}, got {entry.get('zigux_destination')!r}"
            )

    if remaining:
        raise CheckError(
            "manifest missing gap entries: " + ", ".join(sorted(remaining.keys()))
        )


def run_check(root: Path) -> None:
    bcm_survey = read_text(root, FILES["bcm_survey"])
    dw_gap = read_text(root, FILES["dw_gap"])
    manifest = read_manifest(root)

    expect_markers("bcm survey", bcm_survey, BCM_SURVEY_MARKERS)
    expect_markers("dw gap", dw_gap, DW_GAP_MARKERS)
    expect_manifest(manifest)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["bcm_survey"], "\n".join(BCM_SURVEY_MARKERS) + "\n")
    write(root / FILES["dw_gap"], "\n".join(DW_GAP_MARKERS) + "\n")
    write(
        root / FILES["dw_manifest"],
        json.dumps(
            {
                "lane_key": EXPECTED_MANIFEST_LANE,
                "surveyed_commit": EXPECTED_MANIFEST_PIN,
                "gaps": [
                    {
                        "id": "phase11-dw-wdt-live-platform-pm",
                        "status": "starter_landed",
                        "zigux_destination": "drivers/watchdog/dw_wdt_pm.zig",
                    },
                    {
                        "id": "phase11-dw-wdt-live-mmio-validation",
                        "status": "ready_next",
                        "zigux_destination": "zigux/tests/phase11_dw_wdt.zig",
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_watchdog_next_step_boundary_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        marker_cases = (
            [("bcm_survey", marker) for marker in BCM_SURVEY_MARKERS]
            + [("dw_gap", marker) for marker in DW_GAP_MARKERS]
        )
        for idx, (label, marker) in enumerate(marker_cases, start=1):
            case_root = tmpdir / f"marker_{idx}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            write(path, path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1))
            expect_failure(case_root, marker)

        lane_case = tmpdir / "lane_case"
        shutil.copytree(fixture, lane_case, dirs_exist_ok=True)
        manifest_path = lane_case / FILES["dw_manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["lane_key"] = "P11-L10"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(lane_case, "manifest lane_key mismatch")

        gap_case = tmpdir / "gap_case"
        shutil.copytree(fixture, gap_case, dirs_exist_ok=True)
        manifest_path = gap_case / FILES["dw_manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["gaps"][1]["status"] = "starter_landed"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(gap_case, "manifest phase11-dw-wdt-live-mmio-validation status mismatch")

        self_test_case_count = len(marker_cases) + 2
        print("PHASE11_WATCHDOG_NEXT_STEP_BOUNDARY_SELF_TEST=pass")
        print(
            f"PHASE11_WATCHDOG_NEXT_STEP_BOUNDARY_SELF_TEST_CASE_COUNT={self_test_case_count}"
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
        print(f"PHASE11_WATCHDOG_NEXT_STEP_BOUNDARY=fail: {exc}")
        return 1

    print("PHASE11_WATCHDOG_NEXT_STEP_BOUNDARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed checker for the current directly readable Phase 11 DesignWare packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "note": "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "plan": "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
}

EXPECTED_MANIFEST_LANE = "P11-L05"
EXPECTED_MANIFEST_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"

NOTE_MARKERS = [
    "# Phase 11 DesignWare Verify Alignment Gap",
    "- lane: `P11-L11`",
    "- the surviving directly readable DesignWare owner packet on current `master` is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "- current contents reads in this lane still return missing for `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "- the current `zigux/tests/phase11_dw_wdt_manifest.json` keeps lane key `P11-L05` pinned to surveyed commit `75f8336c4305beed127d7abfae37d3999b7cc57c`",
    "- the manifest still routes `phase11-dw-wdt-teardown-parity` to `drivers/watchdog/dw_wdt_verify.zig`, so the compile-local verify packet remains part of the DesignWare continuity story even while direct contents reads for that file stay missing in this environment",
    "- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py` now fails closed on that smaller directly readable owner packet instead of the older matrix-versus-manifest mismatch story",
    "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
    "- `zigux/tests/phase11_dw_wdt_manifest.json`",
    "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "- `Documentation/zigux/phase11-driver-lane-sequencing.md`",
]

PLAN_MARKERS = [
    "# Phase 11 DesignWare Watchdog Platform Registration Plan",
    "Current contents reads in this run still return missing for `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py`, so keep those as last-known DesignWare packet members until a future reread confirms them again.",
    "- the current starter-laned gap inventory in `zigux/tests/phase11_dw_wdt_manifest.json`",
    "The last-known DesignWare packet still reserves compile-local teardown ownership and restart failure-mode parity for `drivers/watchdog/dw_wdt_verify.zig`",
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

    for entry in gaps:
        if not isinstance(entry, dict):
            raise CheckError("manifest gaps entries must be objects")
        if entry.get("id") == VERIFY_GAP_ID:
            if entry.get("zigux_destination") != VERIFY_DESTINATION:
                raise CheckError(
                    "manifest teardown-parity destination mismatch: "
                    f"expected {VERIFY_DESTINATION}, got {entry.get('zigux_destination')!r}"
                )
            return

    raise CheckError(f"manifest missing gap entry: {VERIFY_GAP_ID}")


def run_check(root: Path) -> None:
    note = read_text(root, FILES["note"])
    plan = read_text(root, FILES["plan"])
    manifest = read_manifest(root)

    expect_markers("note", note, NOTE_MARKERS)
    expect_markers("plan", plan, PLAN_MARKERS)
    expect_manifest_state(manifest)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["note"], "\n".join(NOTE_MARKERS) + "\n")
    write(root / FILES["plan"], "\n".join(PLAN_MARKERS) + "\n")
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
                    }
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

        marker_cases = [("note", marker) for marker in NOTE_MARKERS] + [
            ("plan", marker) for marker in PLAN_MARKERS
        ]
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
        data["gaps"][0]["zigux_destination"] = "drivers/watchdog/dw_wdt.zig"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(manifest_gap_case, "manifest teardown-parity destination mismatch")

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

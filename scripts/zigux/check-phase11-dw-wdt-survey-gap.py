#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare survey/manifest gap."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "survey": "zigux/tests/phase11_dw_wdt_survey.zig",
    "manifest": "zigux/tests/phase11_dw_wdt_manifest.json",
}

SURVEY_LANE = "P11-L05"
SURVEY_PIN = "75f8336c4305beed127d7abfae37d3999b7cc57c"
MANIFEST_LANE = "P11-L10"
MANIFEST_PIN = "6726fdd9da4eef55498fb06c38815317a684bcbf"
VERIFY_GAP_ID = "phase11-dw-wdt-teardown-parity"
VERIFY_DESTINATION = "drivers/watchdog/dw_wdt_verify.zig"

SURVEY_MARKERS = [
    'try std.testing.expectEqualStrings("P11-L05", manifest.lane_key);',
    'try std.testing.expectEqualStrings("75f8336c4305beed127d7abfae37d3999b7cc57c", manifest.surveyed_commit);',
    "try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);",
    "try std.testing.expect(manifest.survey_summary.preexisting_phase11_bcm2835_lane_present);",
    'if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-live-platform-pm")) {',
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
    if lane_key != MANIFEST_LANE:
        raise CheckError(
            f"manifest lane_key mismatch: expected {MANIFEST_LANE}, got {lane_key!r}"
        )
    if surveyed_commit != MANIFEST_PIN:
        raise CheckError(
            "manifest surveyed_commit mismatch: "
            f"expected {MANIFEST_PIN}, got {surveyed_commit!r}"
        )

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        raise CheckError("manifest survey_summary must be an object")
    if "preexisting_phase11_gpio_lane_present" in summary:
        raise CheckError("manifest unexpectedly restored preexisting gpio lane summary marker")
    if "preexisting_phase11_bcm2835_lane_present" in summary:
        raise CheckError("manifest unexpectedly restored preexisting bcm2835 lane summary marker")
    if summary.get("dw_wdt_registration_scaffold_present") is not True:
        raise CheckError("manifest missing current registration scaffold summary marker")

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
    survey = read_text(root, FILES["survey"])
    manifest = read_manifest(root)

    expect_markers("survey", survey, SURVEY_MARKERS)
    expect_manifest_state(manifest)

    if SURVEY_LANE == MANIFEST_LANE:
        raise CheckError("expected documented lane mismatch collapsed unexpectedly")
    if SURVEY_PIN == MANIFEST_PIN:
        raise CheckError("expected documented surveyed-pin mismatch collapsed unexpectedly")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / FILES["survey"], "\n".join(SURVEY_MARKERS) + "\n")
    write(
        root / FILES["manifest"],
        json.dumps(
            {
                "lane_key": MANIFEST_LANE,
                "surveyed_commit": MANIFEST_PIN,
                "survey_summary": {
                    "dw_wdt_registration_scaffold_present": True,
                },
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_survey_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        for idx, marker in enumerate(SURVEY_MARKERS, start=1):
            case_root = tmpdir / f"survey_marker_{idx}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            survey_path = case_root / FILES["survey"]
            write(
                survey_path,
                survey_path.read_text(encoding="utf-8").replace(marker, "__mutated__", 1),
            )
            expect_failure(case_root, marker)

        manifest_lane_case = tmpdir / "manifest_lane_case"
        shutil.copytree(fixture, manifest_lane_case, dirs_exist_ok=True)
        manifest_path = manifest_lane_case / FILES["manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["lane_key"] = SURVEY_LANE
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(manifest_lane_case, "manifest lane_key mismatch")

        manifest_pin_case = tmpdir / "manifest_pin_case"
        shutil.copytree(fixture, manifest_pin_case, dirs_exist_ok=True)
        manifest_path = manifest_pin_case / FILES["manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["surveyed_commit"] = SURVEY_PIN
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(manifest_pin_case, "manifest surveyed_commit mismatch")

        summary_case = tmpdir / "summary_case"
        shutil.copytree(fixture, summary_case, dirs_exist_ok=True)
        manifest_path = summary_case / FILES["manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["survey_summary"]["preexisting_phase11_gpio_lane_present"] = True
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(summary_case, "manifest unexpectedly restored preexisting gpio lane summary marker")

        destination_case = tmpdir / "destination_case"
        shutil.copytree(fixture, destination_case, dirs_exist_ok=True)
        manifest_path = destination_case / FILES["manifest"]
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["gaps"][0]["zigux_destination"] = "drivers/watchdog/dw_wdt.zig"
        write(manifest_path, json.dumps(data, indent=2) + "\n")
        expect_failure(destination_case, "manifest teardown-parity destination mismatch")

        self_test_case_count = len(SURVEY_MARKERS) + 4
        print("PHASE11_DW_WDT_SURVEY_GAP_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_SURVEY_GAP_SELF_TEST_CASE_COUNT={self_test_case_count}")
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
        print(f"PHASE11_DW_WDT_SURVEY_GAP=fail: {exc}")
        return 1

    print("PHASE11_DW_WDT_SURVEY_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

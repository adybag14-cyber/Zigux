#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 DesignWare live-MMIO review shard."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd()

FILES = {
    "survey": Path("Documentation/zigux/phase11-dw-wdt-survey.md"),
    "matrix": Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md"),
    "manifest": Path("zigux/tests/phase11_dw_wdt_manifest.json"),
    "build_inventory": Path("zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json"),
    "build": Path("zigux/tests/phase11_dw_wdt_build.zig"),
    "live_mmio_review": Path("zigux/tests/phase11_dw_wdt_live_mmio_review.zig"),
    "driver": Path("drivers/watchdog/dw_wdt.zig"),
    "pm": Path("drivers/watchdog/dw_wdt_pm.zig"),
}

EXPECTED_LANE_KEY = "P11-L10"
EXPECTED_SURVEYED_COMMIT = "75f8336c4305beed127d7abfae37d3999b7cc57c"
EXPECTED_NEXT_GAP_ID = "phase11-dw-wdt-live-mmio-validation"
EXPECTED_NEXT_DESTINATION = "zigux/tests/phase11_dw_wdt.zig"
EXPECTED_SHARED_BUILD = "zigux/tests/phase11_dw_wdt_build.zig"
EXPECTED_REPLAY_COMMAND = "zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig"
EXPECTED_BUILD_TEST = "phase11-dw-wdt-live-mmio-review-tests"

SURVEY_MARKERS = (
    "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
    "The next bounded same-lane step",
    "hardware-backed MMIO validation around",
    "suspend, resume, and platform-backed probe or remove execution",
)

MATRIX_MARKERS = (
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keeps timer-clock choice",
    "`drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig` now rematerialize on current `master`",
    "The next bounded same-lane follow-up remains the manifest-marked ready-next step: hardware-backed MMIO validation around suspend, resume, and platform-backed probe or remove execution, without widening into unrelated driver behavior.",
)

BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_dw_wdt_live_mmio_review.zig")',
    'live_mmio_review_module.addImport("dw_wdt", dw_wdt_module);',
    'live_mmio_review_module.addImport("dw_wdt_pm", dw_wdt_pm_module);',
    '.name = "phase11-dw-wdt-live-mmio-review-tests"',
    "test_step.dependOn(&run_live_mmio_review_tests.step);",
)

LIVE_MMIO_REVIEW_MARKERS = (
    'test "phase11 dw_wdt keeps live mmio timeout barriers aligned across probe and resume" {',
    'test "phase11 dw_wdt keeps imported-running handoff free of fabricated live mmio blockers" {',
    'test "phase11 dw_wdt keeps remove-time live mmio stop boundaries explicit" {',
)

DRIVER_MARKERS = (
    "pub const PlatformHandoffRequest = struct {",
    "pub const PlatformHandoffSummary = struct {",
    "pub fn platformHandoffSummary(request: PlatformHandoffRequest) PlatformHandoffSummary {",
    "pub fn removeTeardownSummary(request: RemoveTeardownRequest) RemoveTeardownSummary {",
)

PM_MARKERS = (
    'test "phase11 dw_wdt pm resume keeps imported-running handoff explicit" {',
    'test "phase11 dw_wdt pm resume keeps timeout reprogram blocker explicit" {',
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def read_json(root: Path, relative_path: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {relative_path.as_posix()}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {relative_path.as_posix()}")
    return value


def require_markers(root: Path, label: str, relative_path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(root, relative_path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def check_manifest(root: Path) -> None:
    manifest = read_json(root, FILES["manifest"])
    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        raise CheckError("manifest lane_key mismatch")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        raise CheckError("manifest surveyed_commit mismatch")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        raise CheckError("manifest gaps must be a list")

    gap_map = {entry.get("id"): entry for entry in gaps if isinstance(entry, dict)}
    next_gap = gap_map.get(EXPECTED_NEXT_GAP_ID)
    if not next_gap:
        raise CheckError("manifest next gap missing")
    if next_gap.get("status") != "ready_next":
        raise CheckError("manifest next gap status mismatch")
    if next_gap.get("zigux_destination") != EXPECTED_NEXT_DESTINATION:
        raise CheckError("manifest next gap destination mismatch")


def check_build_inventory(root: Path) -> None:
    inventory = read_json(root, FILES["build_inventory"])
    if inventory.get("shared_build_file") != EXPECTED_SHARED_BUILD:
        raise CheckError("build inventory shared_build_file mismatch")
    if inventory.get("shared_replay_command") != EXPECTED_REPLAY_COMMAND:
        raise CheckError("build inventory shared_replay_command mismatch")

    build_test_names = inventory.get("build_test_names")
    if not isinstance(build_test_names, list) or EXPECTED_BUILD_TEST not in build_test_names:
        raise CheckError("build inventory missing live-mmio review test name")

    module_entries = inventory.get("module_root_source_files")
    if not isinstance(module_entries, list):
        raise CheckError("build inventory module_root_source_files must be a list")
    module_paths = {
        entry.get("module"): entry.get("path")
        for entry in module_entries
        if isinstance(entry, dict)
    }
    if module_paths.get("live_mmio_review_module") != "phase11_dw_wdt_live_mmio_review.zig":
        raise CheckError("build inventory live_mmio_review_module path mismatch")

    test_entries = inventory.get("test_root_modules")
    if not isinstance(test_entries, list):
        raise CheckError("build inventory test_root_modules must be a list")
    test_roots = {
        entry.get("test"): entry.get("root_module")
        for entry in test_entries
        if isinstance(entry, dict)
    }
    if test_roots.get(EXPECTED_BUILD_TEST) != "live_mmio_review_module":
        raise CheckError("build inventory live-mmio review root module mismatch")


def run_check(root: Path) -> None:
    require_markers(root, "survey", FILES["survey"], SURVEY_MARKERS)
    require_markers(root, "matrix", FILES["matrix"], MATRIX_MARKERS)
    require_markers(root, "build", FILES["build"], BUILD_MARKERS)
    require_markers(root, "live_mmio_review", FILES["live_mmio_review"], LIVE_MMIO_REVIEW_MARKERS)
    require_markers(root, "driver", FILES["driver"], DRIVER_MARKERS)
    require_markers(root, "pm", FILES["pm"], PM_MARKERS)
    check_manifest(root)
    check_build_inventory(root)


def write(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root, FILES["survey"], "\n".join(SURVEY_MARKERS) + "\n")
    write(root, FILES["matrix"], "\n".join(MATRIX_MARKERS) + "\n")
    write(root, FILES["build"], "\n".join(BUILD_MARKERS) + "\n")
    write(root, FILES["live_mmio_review"], "\n".join(LIVE_MMIO_REVIEW_MARKERS) + "\n")
    write(root, FILES["driver"], "\n".join(DRIVER_MARKERS) + "\n")
    write(root, FILES["pm"], "\n".join(PM_MARKERS) + "\n")
    write(
        root,
        FILES["manifest"],
        json.dumps(
            {
                "lane_key": EXPECTED_LANE_KEY,
                "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
                "gaps": [
                    {
                        "id": EXPECTED_NEXT_GAP_ID,
                        "status": "ready_next",
                        "zigux_destination": EXPECTED_NEXT_DESTINATION,
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root,
        FILES["build_inventory"],
        json.dumps(
            {
                "shared_build_file": EXPECTED_SHARED_BUILD,
                "shared_replay_command": EXPECTED_REPLAY_COMMAND,
                "build_test_names": [EXPECTED_BUILD_TEST],
                "module_root_source_files": [
                    {"module": "live_mmio_review_module", "path": "phase11_dw_wdt_live_mmio_review.zig"}
                ],
                "test_root_modules": [
                    {"test": EXPECTED_BUILD_TEST, "root_module": "live_mmio_review_module"}
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
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_dw_wdt_live_mmio_review_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_marker = tmpdir / "missing_marker"
        shutil.copytree(fixture, missing_marker)
        write(
            missing_marker,
            FILES["live_mmio_review"],
            read_text(missing_marker, FILES["live_mmio_review"]).replace(
                LIVE_MMIO_REVIEW_MARKERS[2],
                "",
                1,
            ),
        )
        expect_failure(missing_marker, "missing marker in live_mmio_review")
        case_count += 1

        bad_gap = tmpdir / "bad_gap"
        shutil.copytree(fixture, bad_gap)
        manifest = read_json(bad_gap, FILES["manifest"])
        manifest["gaps"][0]["status"] = "starter_landed"
        write(bad_gap, FILES["manifest"], json.dumps(manifest, indent=2) + "\n")
        expect_failure(bad_gap, "manifest next gap status mismatch")
        case_count += 1

        bad_inventory = tmpdir / "bad_inventory"
        shutil.copytree(fixture, bad_inventory)
        inventory = read_json(bad_inventory, FILES["build_inventory"])
        inventory["module_root_source_files"][0]["path"] = "phase11_dw_wdt.zig"
        write(bad_inventory, FILES["build_inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(bad_inventory, "build inventory live_mmio_review_module path mismatch")
        case_count += 1

        print("PHASE11_DW_WDT_LIVE_MMIO_REVIEW_SELF_TEST=pass")
        print(f"PHASE11_DW_WDT_LIVE_MMIO_REVIEW_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            return run_self_test()
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_DW_WDT_LIVE_MMIO_REVIEW=fail: {exc}")
        return 1
    except AssertionError as exc:
        print(str(exc))
        return 1

    print("PHASE11_DW_WDT_LIVE_MMIO_REVIEW=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

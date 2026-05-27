#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 watchdog lifecycle-parity note."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "parity_note": Path("Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md"),
    "bcm_survey": Path("Documentation/zigux/phase11-bcm2835-wdt-survey.md"),
    "bcm_matrix": Path("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"),
    "bcm_manifest": Path("zigux/tests/phase11_bcm2835_wdt_manifest.json"),
    "dw_survey": Path("Documentation/zigux/phase11-dw-wdt-survey.md"),
    "dw_matrix": Path("Documentation/zigux/phase11-dw-wdt-validation-matrix.md"),
    "dw_manifest": Path("zigux/tests/phase11_dw_wdt_manifest.json"),
}

PARITY_NOTE_MARKERS = [
    "# Phase 11 Watchdog Lifecycle Parity Gap",
    "bounded current-driver-depth",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json` keeps the remaining",
    "blocked on current-head platform registration, shared",
    "poweroff-callback ownership, and hardware-backed validation",
    "returned driver, direct tests-root replay, restart helper, verify helper,",
    "registration scaffold, and bounded PM-helper packet explicit on current",
    "`phase11-build-gate` as a shared current-head gap",
    "`phase11-dw-wdt-live-mmio-validation` at `ready_next`",
    "bcm2835 reads as a bounded current-driver-depth closure",
    "DesignWare reads as a returned starter-plus-test",
    "next bounded step is still live MMIO validation",
]

BCM_SURVEY_MARKERS = [
    "the Phase 11 simple-driver roadmap gap is closed at bounded current-driver depth on `master`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
]

BCM_MATRIX_MARKERS = [
    "# Phase 11 BCM2835 Watchdog Validation Matrix",
    "`drivers/watchdog/bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`",
]

DW_SURVEY_MARKERS = [
    "# Phase 11 DesignWare Watchdog Survey",
    "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
    "The next bounded same-lane step",
    "hardware-backed MMIO validation",
]

DW_MATRIX_MARKERS = [
    "# Phase 11 DesignWare Watchdog Validation Matrix",
    "`drivers/watchdog/dw_wdt.zig` now rematerializes on current `master`",
    "`drivers/watchdog/dw_wdt_restart.zig`, `drivers/watchdog/dw_wdt_verify.zig`,",
    "hardware-backed MMIO validation",
]

EXPECTED_BCM_MANIFEST = {
    "lane_key": "P11-L08",
    "blocked_gaps": {
        "phase11-bcm2835-platform-registration": "blocked_current_head",
        "phase11-bcm2835-shared-poweroff-callback-ownership": "blocked_current_head",
        "phase11-bcm2835-hardware-backed-validation": "blocked_current_head",
    },
}

EXPECTED_DW_MANIFEST = {
    "lane_key": "P11-L10",
    "starter_gaps": {
        "phase11-dw-wdt-driver-starter": "starter_landed",
        "phase11-dw-wdt-driver-tests": "starter_landed",
        "phase11-dw-wdt-teardown-parity": "starter_landed",
        "phase11-dw-wdt-live-platform-pm": "starter_landed",
    },
    "next_gap": {
        "id": "phase11-dw-wdt-live-mmio-validation",
        "status": "ready_next",
    },
    "shared_gap": {
        "id": "phase11-build-gate",
        "status": "shared_gap_current_head",
    },
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(read_text(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def require_markers(path: Path, markers: list[str]) -> list[str]:
    failures: list[str] = []
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            failures.append(f"missing_marker:{path.as_posix()}:{marker}")
    return failures


def gap_status_map(manifest: dict[str, object]) -> dict[str, str]:
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return {}
    result: dict[str, str] = {}
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        gap_id = gap.get("id")
        status = gap.get("status")
        if isinstance(gap_id, str) and isinstance(status, str):
            result[gap_id] = status
    return result


def check_repo(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES.values():
        path = root / rel_path
        if not path.is_file():
            failures.append(f"missing_file:{rel_path.as_posix()}")

    if failures:
        return failures

    failures.extend(require_markers(root / REQUIRED_FILES["parity_note"], PARITY_NOTE_MARKERS))
    failures.extend(require_markers(root / REQUIRED_FILES["bcm_survey"], BCM_SURVEY_MARKERS))
    failures.extend(require_markers(root / REQUIRED_FILES["bcm_matrix"], BCM_MATRIX_MARKERS))
    failures.extend(require_markers(root / REQUIRED_FILES["dw_survey"], DW_SURVEY_MARKERS))
    failures.extend(require_markers(root / REQUIRED_FILES["dw_matrix"], DW_MATRIX_MARKERS))

    bcm_manifest = read_json(root / REQUIRED_FILES["bcm_manifest"])
    if bcm_manifest.get("lane_key") != EXPECTED_BCM_MANIFEST["lane_key"]:
        failures.append(f"bcm_lane_key:{bcm_manifest.get('lane_key')!r}")
    bcm_gap_map = gap_status_map(bcm_manifest)
    for gap_id, expected_status in EXPECTED_BCM_MANIFEST["blocked_gaps"].items():
        if bcm_gap_map.get(gap_id) != expected_status:
            failures.append(f"bcm_gap_status:{gap_id}:{bcm_gap_map.get(gap_id)!r}")

    dw_manifest = read_json(root / REQUIRED_FILES["dw_manifest"])
    if dw_manifest.get("lane_key") != EXPECTED_DW_MANIFEST["lane_key"]:
        failures.append(f"dw_lane_key:{dw_manifest.get('lane_key')!r}")
    dw_gap_map = gap_status_map(dw_manifest)
    for gap_id, expected_status in EXPECTED_DW_MANIFEST["starter_gaps"].items():
        if dw_gap_map.get(gap_id) != expected_status:
            failures.append(f"dw_gap_status:{gap_id}:{dw_gap_map.get(gap_id)!r}")
    shared_gap = EXPECTED_DW_MANIFEST["shared_gap"]
    if dw_gap_map.get(shared_gap["id"]) != shared_gap["status"]:
        failures.append(f"dw_shared_gap_status:{shared_gap['id']}:{dw_gap_map.get(shared_gap['id'])!r}")
    next_gap = EXPECTED_DW_MANIFEST["next_gap"]
    if dw_gap_map.get(next_gap["id"]) != next_gap["status"]:
        failures.append(f"dw_next_gap_status:{next_gap['id']}:{dw_gap_map.get(next_gap['id'])!r}")

    return failures


def seed_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES.values():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

    (root / REQUIRED_FILES["parity_note"]).write_text("\n".join(PARITY_NOTE_MARKERS) + "\n", encoding="utf-8")
    (root / REQUIRED_FILES["bcm_survey"]).write_text("\n".join(BCM_SURVEY_MARKERS) + "\n", encoding="utf-8")
    (root / REQUIRED_FILES["bcm_matrix"]).write_text("\n".join(BCM_MATRIX_MARKERS) + "\n", encoding="utf-8")
    (root / REQUIRED_FILES["dw_survey"]).write_text("\n".join(DW_SURVEY_MARKERS) + "\n", encoding="utf-8")
    (root / REQUIRED_FILES["dw_matrix"]).write_text("\n".join(DW_MATRIX_MARKERS) + "\n", encoding="utf-8")

    bcm_manifest = {
        "lane_key": EXPECTED_BCM_MANIFEST["lane_key"],
        "gaps": [
            {"id": gap_id, "status": status}
            for gap_id, status in EXPECTED_BCM_MANIFEST["blocked_gaps"].items()
        ],
    }
    (root / REQUIRED_FILES["bcm_manifest"]).write_text(
        json.dumps(bcm_manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    dw_manifest = {
        "lane_key": EXPECTED_DW_MANIFEST["lane_key"],
        "gaps": [
            {"id": gap_id, "status": status}
            for gap_id, status in EXPECTED_DW_MANIFEST["starter_gaps"].items()
        ]
        + [
            EXPECTED_DW_MANIFEST["shared_gap"],
            EXPECTED_DW_MANIFEST["next_gap"],
        ],
    }
    (root / REQUIRED_FILES["dw_manifest"]).write_text(
        json.dumps(dw_manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = check_repo(root)
    if expected not in failures and not any(expected in item for item in failures):
        raise SystemExit(f"expected {expected!r}, got {failures}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-watchdog-lifecycle-gap-") as tmpdir:
        root = Path(tmpdir)
        fixture = root / "fixture"
        seed_fixture(fixture)

        baseline = check_repo(fixture)
        if baseline:
            raise SystemExit("baseline self-test fixture failed: " + ", ".join(baseline))

        case_count = 1

        marker_cases = [
            (REQUIRED_FILES["parity_note"], PARITY_NOTE_MARKERS[5]),
            (REQUIRED_FILES["parity_note"], PARITY_NOTE_MARKERS[7]),
            (REQUIRED_FILES["parity_note"], PARITY_NOTE_MARKERS[10]),
            (REQUIRED_FILES["bcm_survey"], BCM_SURVEY_MARKERS[0]),
            (REQUIRED_FILES["dw_survey"], DW_SURVEY_MARKERS[1]),
            (REQUIRED_FILES["dw_matrix"], DW_MATRIX_MARKERS[1]),
        ]
        for index, (rel_path, marker) in enumerate(marker_cases, start=1):
            case_root = root / f"marker_case_{index}"
            shutil.copytree(fixture, case_root)
            target = case_root / rel_path
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            expect_failure(case_root, marker)
            case_count += 1

        bcm_lane_case = root / "bcm_lane_case"
        shutil.copytree(fixture, bcm_lane_case)
        manifest_path = bcm_lane_case / REQUIRED_FILES["bcm_manifest"]
        data = json.loads(read_text(manifest_path))
        data["lane_key"] = "P11-L99"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(bcm_lane_case, "bcm_lane_key:'P11-L99'")
        case_count += 1

        bcm_gap_case = root / "bcm_gap_case"
        shutil.copytree(fixture, bcm_gap_case)
        manifest_path = bcm_gap_case / REQUIRED_FILES["bcm_manifest"]
        data = json.loads(read_text(manifest_path))
        data["gaps"][0]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            bcm_gap_case,
            "bcm_gap_status:phase11-bcm2835-platform-registration:'ready_next'",
        )
        case_count += 1

        dw_lane_case = root / "dw_lane_case"
        shutil.copytree(fixture, dw_lane_case)
        manifest_path = dw_lane_case / REQUIRED_FILES["dw_manifest"]
        data = json.loads(read_text(manifest_path))
        data["lane_key"] = "P11-L11"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(dw_lane_case, "dw_lane_key:'P11-L11'")
        case_count += 1

        dw_next_case = root / "dw_next_case"
        shutil.copytree(fixture, dw_next_case)
        manifest_path = dw_next_case / REQUIRED_FILES["dw_manifest"]
        data = json.loads(read_text(manifest_path))
        for gap in data["gaps"]:
            if gap["id"] == "phase11-dw-wdt-live-mmio-validation":
                gap["status"] = "starter_landed"
        manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            dw_next_case,
            "dw_next_gap_status:phase11-dw-wdt-live-mmio-validation:'starter_landed'",
        )
        case_count += 1

        missing_file_case = root / "missing_file_case"
        shutil.copytree(fixture, missing_file_case)
        (missing_file_case / REQUIRED_FILES["dw_matrix"]).unlink()
        expect_failure(
            missing_file_case,
            REQUIRED_FILES["dw_matrix"].as_posix(),
        )
        case_count += 1

        print("PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP_SELF_TEST=pass")
        print(f"PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP_SELF_TEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the Phase 11 watchdog lifecycle-parity gap note for drift."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    failures = check_repo(args.root.resolve())
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP=pass")
    print(f"PHASE11_WATCHDOG_LIFECYCLE_PARITY_GAP_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

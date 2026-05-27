#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 bcm2835 archival packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "survey": Path("Documentation/zigux/phase11-bcm2835-wdt-survey.md"),
    "matrix": Path("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"),
    "manifest": Path("zigux/tests/phase11_bcm2835_wdt_manifest.json"),
    "survey_gate": Path("zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig"),
    "survey_gate_build": Path("zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig"),
}

EXPECTED_ARCHIVAL_IDENTITY = "P11-L08"
EXPECTED_CONTINUITY_LANE = "P11-L10"

SURVEY_MARKERS = [
    "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed",
    "archival packet identity remains `P11-L08`",
    "current scheduled continuity for this archival bcm2835 packet is tracked through `P11-L10`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
]

MATRIX_MARKERS = [
    "# Phase 11 BCM2835 Watchdog Validation Matrix",
    "archival packet identity: `P11-L08`",
    "current scheduled continuity for this archival bcm2835 packet is tracked",
    "through `P11-L10`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
]

SURVEY_GATE_MARKERS = [
    "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed",
    "archival packet identity remains `P11-L08`",
    "phase11-bcm2835-wdt-platform-validation-plan.md",
    "phase11-bcm2835-wdt-validation-matrix.md",
    "phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
]

SURVEY_GATE_BUILD_MARKERS = [
    '.root_source_file = b.path("phase11_bcm2835_wdt_manifest_packet_survey.zig")',
    '.name = "phase11-bcm2835-wdt-manifest-packet-survey-tests"',
    "Run the focused Phase 11 bcm2835 watchdog manifest packet survey",
]

EXPECTED_BLOCKED_GAPS = {
    "phase11-bcm2835-platform-registration": "blocked_current_head",
    "phase11-bcm2835-shared-poweroff-callback-ownership": "blocked_current_head",
    "phase11-bcm2835-hardware-backed-validation": "blocked_current_head",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


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

    failures.extend(require_markers(root / REQUIRED_FILES["survey"], SURVEY_MARKERS))
    failures.extend(require_markers(root / REQUIRED_FILES["matrix"], MATRIX_MARKERS))
    failures.extend(require_markers(root / REQUIRED_FILES["survey_gate"], SURVEY_GATE_MARKERS))
    failures.extend(require_markers(root / REQUIRED_FILES["survey_gate_build"], SURVEY_GATE_BUILD_MARKERS))

    manifest = read_json(root / REQUIRED_FILES["manifest"])
    if manifest.get("lane_key") != EXPECTED_ARCHIVAL_IDENTITY:
        failures.append(f"manifest_lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("archival_packet_identity") != EXPECTED_ARCHIVAL_IDENTITY:
        failures.append(
            f"manifest_archival_identity:{manifest.get('archival_packet_identity')!r}"
        )
    if manifest.get("current_scheduled_continuity_lane") != EXPECTED_CONTINUITY_LANE:
        failures.append(
            "manifest_current_scheduled_continuity_lane:"
            f"{manifest.get('current_scheduled_continuity_lane')!r}"
        )

    gap_map = gap_status_map(manifest)
    for gap_id, expected_status in EXPECTED_BLOCKED_GAPS.items():
        if gap_map.get(gap_id) != expected_status:
            failures.append(f"manifest_gap_status:{gap_id}:{gap_map.get(gap_id)!r}")

    return failures


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES.values():
        (root / rel_path).parent.mkdir(parents=True, exist_ok=True)

    write(root / REQUIRED_FILES["survey"], "\n".join(SURVEY_MARKERS) + "\n")
    write(root / REQUIRED_FILES["matrix"], "\n".join(MATRIX_MARKERS) + "\n")
    write(root / REQUIRED_FILES["survey_gate"], "\n".join(SURVEY_GATE_MARKERS) + "\n")
    write(
        root / REQUIRED_FILES["survey_gate_build"],
        "\n".join(SURVEY_GATE_BUILD_MARKERS) + "\n",
    )
    write(
        root / REQUIRED_FILES["manifest"],
        json.dumps(
            {
                "lane_key": EXPECTED_ARCHIVAL_IDENTITY,
                "phase": "Phase 11",
                "anchor": "drivers/watchdog/bcm2835_wdt.c",
                "archival_packet_identity": EXPECTED_ARCHIVAL_IDENTITY,
                "current_scheduled_continuity_lane": EXPECTED_CONTINUITY_LANE,
                "gaps": [
                    {"id": gap_id, "status": status}
                    for gap_id, status in EXPECTED_BLOCKED_GAPS.items()
                ],
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> None:
    seed_fixture(root)


def expect_failure(root: Path, expected: str) -> None:
    failures = check_repo(root)
    if expected not in failures and not any(expected in item for item in failures):
        raise SystemExit(f"expected {expected!r}, got {failures}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11-bcm2835-archival-") as tmpdir:
        root = Path(tmpdir)
        fixture = root / "fixture"
        seed_fixture(fixture)

        baseline = check_repo(fixture)
        if baseline:
            raise SystemExit("baseline self-test fixture failed: " + ", ".join(baseline))

        case_count = 1

        marker_cases = [
            (REQUIRED_FILES["survey"], SURVEY_MARKERS[2]),
            (REQUIRED_FILES["matrix"], MATRIX_MARKERS[3]),
            (REQUIRED_FILES["survey_gate"], SURVEY_GATE_MARKERS[4]),
            (REQUIRED_FILES["survey_gate_build"], SURVEY_GATE_BUILD_MARKERS[1]),
        ]
        for index, (rel_path, marker) in enumerate(marker_cases, start=1):
            case_root = root / f"marker_case_{index}"
            shutil.copytree(fixture, case_root)
            target = case_root / rel_path
            target.write_text(read_text(target).replace(marker, "", 1), encoding="utf-8")
            expect_failure(case_root, marker)
            case_count += 1

        manifest_lane_case = root / "manifest_lane_case"
        shutil.copytree(fixture, manifest_lane_case)
        manifest_path = manifest_lane_case / REQUIRED_FILES["manifest"]
        payload = json.loads(read_text(manifest_path))
        payload["current_scheduled_continuity_lane"] = "P11-L09"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            manifest_lane_case,
            "manifest_current_scheduled_continuity_lane:'P11-L09'",
        )
        case_count += 1

        archival_identity_case = root / "archival_identity_case"
        shutil.copytree(fixture, archival_identity_case)
        manifest_path = archival_identity_case / REQUIRED_FILES["manifest"]
        payload = json.loads(read_text(manifest_path))
        payload["archival_packet_identity"] = "P11-L10"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            archival_identity_case,
            "manifest_archival_identity:'P11-L10'",
        )
        case_count += 1

        blocked_gap_case = root / "blocked_gap_case"
        shutil.copytree(fixture, blocked_gap_case)
        manifest_path = blocked_gap_case / REQUIRED_FILES["manifest"]
        payload = json.loads(read_text(manifest_path))
        payload["gaps"][0]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            blocked_gap_case,
            "manifest_gap_status:phase11-bcm2835-platform-registration:'ready_next'",
        )
        case_count += 1

        missing_file_case = root / "missing_file_case"
        shutil.copytree(fixture, missing_file_case)
        (missing_file_case / REQUIRED_FILES["survey_gate_build"]).unlink()
        expect_failure(
            missing_file_case,
            REQUIRED_FILES["survey_gate_build"].as_posix(),
        )
        case_count += 1

        print("PHASE11_BCM2835_ARCHIVAL_PACKET_SELF_TEST=pass")
        print(f"PHASE11_BCM2835_ARCHIVAL_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the Phase 11 bcm2835 archival packet for drift."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0
    if args.self_test:
        run_self_test()
        return 0

    failures = check_repo(args.root.resolve())
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE11_BCM2835_ARCHIVAL_PACKET=pass")
    print(f"PHASE11_BCM2835_ARCHIVAL_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 12 NVMe PCI packet."""

from __future__ import annotations

import argparse
from datetime import date
import json
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_NVME_PCI_PACKET"

MANIFEST_PATH = Path("zigux/tests/phase12_nvme_pci_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase12-nvme-pci-survey.md")
DIRECT_BUILD_PATH = Path("zigux/tests/phase12_nvme_pci_build.zig")
DIRECT_REPLAY_PATH = Path("zigux/tests/phase12_nvme_pci.zig")
SHARED_BUILD_PATH = Path("zigux/tests/phase12_build.zig")
VERIFIER_PATH = Path("drivers/nvme/host/pci_verify.zig")

EXPECTED_LANE_KEY = "P12-L08"
EXPECTED_PHASE = "Phase 12"
EXPECTED_ANCHOR = "drivers/nvme/host/pci.c"
EXPECTED_ROADMAP_DESTINATIONS = ["drivers/nvme/host/pci.zig", "zigux/tests/"]

EXPECTED_STATUS = "starter_verifier_direct_replay_manifest_and_survey_gate_present_dedicated_build_present_shared_build_unwired"
EXPECTED_QUEUEING_STATUS = "starter_verifier_direct_test_manifest_and_survey_gate_present_shared_build_unwired"
EXPECTED_SEGMENTED_STATUS = "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_shared_build_unwired"
EXPECTED_DIRECT_REPLAY_STATUS = "landed_on_master_dedicated_build_present"
EXPECTED_SHARED_BUILD_STATUS = "direct_replay_present_shared_build_unwired_survey_gate_standalone"
EXPECTED_SURVEY_NOTE_STATUS = "survey_present_dedicated_direct_replay_route_only"

SURVEY_MARKERS = (
    f"`PHASE12_STATUS={EXPECTED_STATUS}`",
    "the bounded packet remains driver-local because `zigux/tests/phase12_build.zig` does not wire the NVMe direct replay into the shared `phase12-smoke` or `phase12` routes",
    "the dedicated `zigux/tests/phase12_nvme_pci_build.zig` route keeps the direct replay reviewable outside the shared build packet",
    "the dedicated survey gate still stays packet-local beside the manifest and survey note",
)

DIRECT_BUILD_MARKERS = (
    "phase12_nvme_pci.zig",
    "phase12-nvme-pci-direct-tests",
    "phase12-nvme-pci-direct-test",
)

DIRECT_REPLAY_MARKERS = (
    "phase12 nvme pci direct replay keeps stale recovery reservation debt explicit",
    "phase12 nvme pci direct replay keeps rollback-gate parity explicit through recovery",
)

VERIFIER_MARKERS = (
    "nvme pci recovery rollback gate verifier keeps blocker transitions and DMA parity explicit",
    "nvme pci recovery reservation replay preflight marks stale PRP metadata and planner-limited replay debt",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def require_path(root: Path, relative_path: Path) -> None:
    if not (root / relative_path).exists():
        raise CheckFailure(f"missing required packet path: {relative_path}")


def require_iso_date(value: object, label: str) -> None:
    require(isinstance(value, str) and value, f"{label} missing")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise CheckFailure(f"{label} is not an ISO date") from exc


def check_manifest(root: Path) -> None:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    require(manifest.get("lane_key") == EXPECTED_LANE_KEY, "nvme manifest lane_key drifted")
    require(manifest.get("phase") == EXPECTED_PHASE, "nvme manifest phase drifted")
    require(manifest.get("anchor") == EXPECTED_ANCHOR, "nvme manifest anchor drifted")
    require(
        manifest.get("roadmap_destinations") == EXPECTED_ROADMAP_DESTINATIONS,
        "nvme manifest roadmap destinations drifted",
    )
    require_iso_date(manifest.get("verified_on"), "nvme manifest verified_on")

    gap_check = manifest.get("roadmap_gap_check")
    require(isinstance(gap_check, dict), "nvme roadmap_gap_check missing")
    require(
        gap_check.get("queueing_correctness", {}).get("status") == EXPECTED_QUEUEING_STATUS,
        "nvme queueing status drifted",
    )
    require(
        gap_check.get("segmented_rollout", {}).get("status") == EXPECTED_SEGMENTED_STATUS,
        "nvme segmented-rollout status drifted",
    )
    require(
        "shared Phase 12 build route still leaves the NVMe direct replay outside the shared smoke-first packet"
        in gap_check.get("queueing_correctness", {}).get("current_surface", ""),
        "nvme queueing surface lost shared-build-unwired wording",
    )

    gaps = manifest.get("gaps")
    require(isinstance(gaps, list), "nvme gaps missing")
    gap_map = {
        gap["id"]: gap
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    require(
        gap_map.get("phase12-nvme-direct-replay", {}).get("status") == EXPECTED_DIRECT_REPLAY_STATUS,
        "nvme direct replay gap drifted",
    )
    require(
        gap_map.get("phase12-nvme-shared-build-route", {}).get("status")
        == EXPECTED_SHARED_BUILD_STATUS,
        "nvme shared build gap drifted",
    )
    require(
        gap_map.get("phase12-nvme-survey-note", {}).get("status") == EXPECTED_SURVEY_NOTE_STATUS,
        "nvme survey note gap drifted",
    )


def check_paths(root: Path) -> None:
    for path in (
        MANIFEST_PATH,
        SURVEY_PATH,
        DIRECT_BUILD_PATH,
        DIRECT_REPLAY_PATH,
        SHARED_BUILD_PATH,
        VERIFIER_PATH,
    ):
        require_path(root, path)

    require_markers(read_text(root, SURVEY_PATH), SURVEY_MARKERS, str(SURVEY_PATH))
    require_markers(read_text(root, DIRECT_BUILD_PATH), DIRECT_BUILD_MARKERS, str(DIRECT_BUILD_PATH))
    require_markers(read_text(root, DIRECT_REPLAY_PATH), DIRECT_REPLAY_MARKERS, str(DIRECT_REPLAY_PATH))
    require_markers(read_text(root, VERIFIER_PATH), VERIFIER_MARKERS, str(VERIFIER_PATH))

    shared_build_text = read_text(root, SHARED_BUILD_PATH)
    require(
        "phase12_nvme_pci.zig" not in shared_build_text,
        "nvme direct replay unexpectedly entered the shared Phase 12 build route",
    )


def check(root: Path) -> None:
    check_manifest(root)
    check_paths(root)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture(root: Path) -> None:
    manifest = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": "7f9b8703b96d4de67447791a88584023950b1de7",
        "verified_on": "2026-05-24",
        "anchor": EXPECTED_ANCHOR,
        "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "roadmap_gap_check": {
            "queueing_correctness": {
                "required_by_roadmap": True,
                "status": EXPECTED_QUEUEING_STATUS,
                "current_surface": "shared Phase 12 build route still leaves the NVMe direct replay outside the shared smoke-first packet",
            },
            "segmented_rollout": {
                "required_by_roadmap": True,
                "status": EXPECTED_SEGMENTED_STATUS,
            },
        },
        "gaps": [
            {"id": "phase12-nvme-direct-replay", "status": EXPECTED_DIRECT_REPLAY_STATUS},
            {"id": "phase12-nvme-shared-build-route", "status": EXPECTED_SHARED_BUILD_STATUS},
            {"id": "phase12-nvme-survey-note", "status": EXPECTED_SURVEY_NOTE_STATUS},
        ],
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 12 NVMe PCI Survey",
                "",
                f"- `PHASE12_STATUS={EXPECTED_STATUS}`",
                "- the bounded packet remains driver-local because `zigux/tests/phase12_build.zig` does not wire the NVMe direct replay into the shared `phase12-smoke` or `phase12` routes",
                "- the dedicated `zigux/tests/phase12_nvme_pci_build.zig` route keeps the direct replay reviewable outside the shared build packet",
                "- the dedicated survey gate still stays packet-local beside the manifest and survey note",
                "",
            ]
        ),
    )
    write_text(root / DIRECT_BUILD_PATH, "\n".join(DIRECT_BUILD_MARKERS) + "\n")
    write_text(root / DIRECT_REPLAY_PATH, "\n".join(DIRECT_REPLAY_MARKERS) + "\n")
    write_text(root / VERIFIER_PATH, "\n".join(VERIFIER_MARKERS) + "\n")
    write_text(root / SHARED_BUILD_PATH, "const std = @import(\"std\");\n")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-nvme-pci-packet-") as tmp:
        root = Path(tmp)
        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        data = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
        data["roadmap_gap_check"]["queueing_correctness"]["status"] = "broken"
        write_text(root / MANIFEST_PATH, json.dumps(data, indent=2) + "\n")
        try:
            check(root)
        except CheckFailure as exc:
            if "queueing status" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected queueing drift failure")

        write_fixture(root)
        write_text(root / SHARED_BUILD_PATH, "phase12_nvme_pci.zig\n")
        try:
            check(root)
        except CheckFailure as exc:
            if "unexpectedly entered the shared Phase 12 build route" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected shared-build wiring failure")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        check(Path(args.root))
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail")
        print(f"{CHECK_NAME}_ERROR={exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_SCOPE=nvme_driver_local_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

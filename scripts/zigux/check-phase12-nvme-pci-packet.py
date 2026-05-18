#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 12 NVMe PCI packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_NVME_PCI_PACKET"

MANIFEST_PATH = Path("zigux/tests/phase12_nvme_pci_manifest.json")

EXPECTED_LANE_KEY = "P12-L08"
EXPECTED_PHASE = "Phase 12"
EXPECTED_ANCHOR = "drivers/nvme/host/pci.c"
EXPECTED_ROADMAP_DESTINATIONS = ["drivers/nvme/host/pci.zig", "zigux/tests/"]

EXPECTED_SUMMARY_FLAGS = (
    "preexisting_nvme_pci_zig_present",
    "preexisting_nvme_pci_verifier_present",
    "preexisting_phase12_direct_test_present",
    "preexisting_phase12_manifest_present",
    "preexisting_phase12_build_present",
    "preexisting_phase12_make_targets_present",
    "preexisting_phase12_fallback_note_present",
    "preexisting_phase12_reopen_governance_present",
    "preexisting_phase12_slice_note_present",
    "preexisting_phase12_survey_note_present",
    "preexisting_phase12_survey_gate_present",
)

EXPECTED_ROADMAP_GAP_CHECK = {
    "dma_safe_abstractions": {
        "status": "starter_planner_present_runtime_dma_blocked",
        "current_surface_markers": (
            "queue-pair planning",
            "PRP buffer-shape accounting",
            "transport-backed queue execution",
        ),
        "blocked_by_markers": (
            "DMA-safe request ownership",
            "PRP or SGL construction",
            "runtime queue submission",
        ),
    },
    "queueing_correctness": {
        "status": "starter_verifier_direct_test_manifest_and_survey_gate_present_shared_build_unwired",
        "current_surface_markers": (
            "dedicated survey gate",
            "shared build wiring",
            "live queue execution",
        ),
        "blocked_by_markers": (
            "shared Phase 12 build route",
            "transport-backed queue execution",
        ),
    },
    "throughput_and_recovery_parity": {
        "status": "recovery_budget_summary_and_survey_gate_present_throughput_gate_missing",
        "current_surface_markers": (
            "reset freeze state",
            "PRP span pressure",
            "frozen queue-restore host-DMA budgeting",
        ),
        "blocked_by_markers": (
            "No throughput benchmark",
            "transport-backed reset replay",
        ),
    },
    "segmented_rollout": {
        "status": "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_shared_build_unwired",
        "current_surface_markers": (
            "fallback map",
            "reopen-governance note",
            "dedicated slice note",
        ),
        "blocked_by_markers": (
            "shared Phase 12 build route",
            "transport-backed queue execution",
        ),
    },
}

EXPECTED_GAPS = {
    "phase12-nvme-fallback-note": {
        "status": "landed_on_master",
        "kind": "documentation",
        "zigux_destination": "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    },
    "phase12-nvme-reopen-governance": {
        "status": "landed_on_master",
        "kind": "documentation",
        "zigux_destination": "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
    },
    "phase12-nvme-direct-replay": {
        "status": "landed_on_master",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase12_nvme_pci.zig",
    },
    "phase12-nvme-manifest-anchor": {
        "status": "landed_on_master",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase12_nvme_pci_manifest.json",
    },
    "phase12-nvme-shared-build-route": {
        "status": "direct_replay_present_shared_build_unwired",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase12_build.zig",
    },
    "phase12-nvme-slice-note": {
        "status": "landed_on_master",
        "kind": "documentation",
        "zigux_destination": "Documentation/zigux/phase12-nvme-pci-slice.md",
    },
    "phase12-nvme-survey-note": {
        "status": "survey_present",
        "kind": "documentation",
        "zigux_destination": "Documentation/zigux/phase12-nvme-pci-survey.md",
    },
    "phase12-nvme-survey-gate": {
        "status": "survey_present",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase12_nvme_pci_survey.zig",
    },
}

EXTRA_REQUIRED_PATHS = (
    "drivers/nvme/host/pci.zig",
    "drivers/nvme/host/pci_verify.zig",
)


class CheckFailure(RuntimeError):
    """Raised when the packet checker finds drift."""


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def require_markers(text: str, markers: tuple[str, ...], message_prefix: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{message_prefix} missing marker: {marker}")


def require_existing_path(root: Path, relative_path: str) -> None:
    if not (root / relative_path).exists():
        raise CheckFailure(f"missing required packet path: {relative_path}")


def check_manifest(root: Path) -> int:
    manifest = json.loads(read_text(root, MANIFEST_PATH))

    require(
        manifest.get("lane_key") == EXPECTED_LANE_KEY,
        "nvme_pci manifest lane_key drifted",
    )
    require(
        manifest.get("phase") == EXPECTED_PHASE,
        "nvme_pci manifest phase drifted",
    )
    require(
        manifest.get("anchor") == EXPECTED_ANCHOR,
        "nvme_pci manifest anchor drifted",
    )
    require(
        manifest.get("roadmap_destinations") == EXPECTED_ROADMAP_DESTINATIONS,
        "nvme_pci manifest roadmap destinations drifted",
    )

    surveyed_commit = manifest.get("surveyed_commit", "")
    require(
        len(surveyed_commit) == 40
        and all(ch in "0123456789abcdef" for ch in surveyed_commit),
        "nvme_pci manifest surveyed_commit is not a 40-char lowercase hex sha",
    )

    summary = manifest.get("survey_summary")
    require(isinstance(summary, dict), "nvme_pci survey_summary is not a mapping")
    for flag in EXPECTED_SUMMARY_FLAGS:
        require(summary.get(flag) is True, f"nvme_pci survey_summary flag missing: {flag}")

    roadmap_gap_check = manifest.get("roadmap_gap_check")
    require(
        isinstance(roadmap_gap_check, dict),
        "nvme_pci roadmap_gap_check is not a mapping",
    )
    for slug, expected in EXPECTED_ROADMAP_GAP_CHECK.items():
        section = roadmap_gap_check.get(slug)
        require(isinstance(section, dict), f"nvme_pci roadmap gap section missing: {slug}")
        require(
            section.get("required_by_roadmap") is True,
            f"nvme_pci roadmap gap section lost required_by_roadmap: {slug}",
        )
        require(
            section.get("status") == expected["status"],
            f"nvme_pci roadmap gap status drifted: {slug}",
        )
        require_markers(
            section.get("current_surface", ""),
            expected["current_surface_markers"],
            f"nvme_pci roadmap current_surface[{slug}]",
        )
        require_markers(
            section.get("blocked_by", ""),
            expected["blocked_by_markers"],
            f"nvme_pci roadmap blocked_by[{slug}]",
        )

    gaps = manifest.get("gaps")
    require(isinstance(gaps, list), "nvme_pci manifest gaps field is not a list")
    gap_map = {}
    for gap in gaps:
        if isinstance(gap, dict) and isinstance(gap.get("id"), str):
            gap_map[gap["id"]] = gap

    for gap_id, expected in EXPECTED_GAPS.items():
        gap = gap_map.get(gap_id)
        require(gap is not None, f"nvme_pci manifest missing gap: {gap_id}")
        require(gap.get("status") == expected["status"], f"nvme_pci gap status drifted: {gap_id}")
        require(gap.get("kind") == expected["kind"], f"nvme_pci gap kind drifted: {gap_id}")
        require(
            gap.get("zigux_destination") == expected["zigux_destination"],
            f"nvme_pci gap destination drifted: {gap_id}",
        )
        require_existing_path(root, expected["zigux_destination"])

    for relative_path in EXTRA_REQUIRED_PATHS:
        require_existing_path(root, relative_path)

    return len(gaps)


def write_fixture(root: Path) -> None:
    fixture_files = {
        MANIFEST_PATH: json.dumps(
            {
                "lane_key": EXPECTED_LANE_KEY,
                "phase": EXPECTED_PHASE,
                "surveyed_commit": "0123456789abcdef0123456789abcdef01234567",
                "anchor": EXPECTED_ANCHOR,
                "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
                "survey_summary": {flag: True for flag in EXPECTED_SUMMARY_FLAGS},
                "roadmap_gap_check": {
                    slug: {
                        "required_by_roadmap": True,
                        "status": expected["status"],
                        "current_surface": " ".join(expected["current_surface_markers"]),
                        "blocked_by": " ".join(expected["blocked_by_markers"]),
                    }
                    for slug, expected in EXPECTED_ROADMAP_GAP_CHECK.items()
                },
                "gaps": [
                    {
                        "id": gap_id,
                        "status": expected["status"],
                        "kind": expected["kind"],
                        "zigux_destination": expected["zigux_destination"],
                    }
                    for gap_id, expected in EXPECTED_GAPS.items()
                ],
            },
            indent=2,
        )
        + "\n",
    }

    for relative_path, text in fixture_files.items():
        absolute_path = root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text(text, encoding="utf-8")

    for expected in EXPECTED_GAPS.values():
        absolute_path = root / expected["zigux_destination"]
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        if absolute_path == root / MANIFEST_PATH:
            continue
        absolute_path.write_text("fixture\n", encoding="utf-8")

    for relative_path in EXTRA_REQUIRED_PATHS:
        absolute_path = root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text("fixture\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_fixture(root)

        check_manifest(root)
        cases += 1

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P12-L02"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            check_manifest(root)
        except CheckFailure as exc:
            if "lane_key" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected lane-key drift to fail")

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["surveyed_commit"] = "0123456789ABCDEF0123456789abcdef01234567"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            check_manifest(root)
        except CheckFailure as exc:
            if "surveyed_commit" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected surveyed_commit drift to fail")

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["preexisting_phase12_survey_gate_present"] = False
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            check_manifest(root)
        except CheckFailure as exc:
            if "preexisting_phase12_survey_gate_present" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected survey-summary drift to fail")

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_gap_check"]["throughput_and_recovery_parity"]["current_surface"] = (
            "reset freeze state and frozen queue-restore host-DMA budgeting"
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            check_manifest(root)
        except CheckFailure as exc:
            if "throughput_and_recovery_parity" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected roadmap current-surface drift to fail")

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"][4]["status"] = "landed_on_master"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            check_manifest(root)
        except CheckFailure as exc:
            if "phase12-nvme-shared-build-route" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected shared-build-route drift to fail")

        write_fixture(root)
        (root / "drivers/nvme/host/pci_verify.zig").unlink()
        try:
            check_manifest(root)
        except CheckFailure as exc:
            if "pci_verify.zig" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected required-path drift to fail")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        gap_count = check_manifest(Path(args.root))
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail")
        print(f"{CHECK_NAME}_ERROR={exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_GAP_COUNT={gap_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

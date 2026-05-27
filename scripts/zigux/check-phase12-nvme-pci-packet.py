#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 12 NVMe PCI packet."""

from __future__ import annotations

import argparse
from datetime import date
import json
import sys
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_NVME_PCI_PACKET"

MANIFEST_PATH = "zigux/tests/phase12_nvme_pci_manifest.json"
DIRECT_BUILD_PATH = "zigux/tests/phase12_nvme_pci_build.zig"
SURVEY_BUILD_PATH = "zigux/tests/phase12_nvme_pci_survey_build.zig"
DIRECT_REPLAY_PATH = "zigux/tests/phase12_nvme_pci.zig"
VERIFIER_PATH = "drivers/nvme/host/pci_verify.zig"
FALLBACK_MAP_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
SLICE_PATH = "Documentation/zigux/phase12-nvme-pci-slice.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase12-nvme-pci-survey.md"
REOPEN_GOVERNANCE_PATH = "Documentation/zigux/phase12-nvme-pci-reopen-governance.md"
SURVEY_GATE_PATH = "zigux/tests/phase12_nvme_pci_survey.zig"

EXPECTED_LANE_KEY = "P12-L08"
EXPECTED_PHASE = "Phase 12"
EXPECTED_ANCHOR = "drivers/nvme/host/pci.c"
EXPECTED_ROADMAP_DESTINATIONS = ["drivers/nvme/host/pci.zig", "zigux/tests/"]
EXPECTED_COMMIT = "0123456789abcdef0123456789abcdef01234567"

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
        "status": "starter_verifier_direct_test_manifest_and_survey_gate_present_dedicated_build_present_shared_build_absent",
        "current_surface_markers": (
            "dedicated direct-build route",
            "dedicated survey gate",
            "`zigux/tests/phase12_build.zig` still stays virtio_net-only",
        ),
        "blocked_by_markers": (
            "dedicated survey gate",
            "dedicated direct-build route",
            "transport-backed queue execution",
        ),
    },
    "throughput_and_recovery_parity": {
        "status": "recovery_budget_summary_and_survey_gate_present_throughput_gate_missing",
        "current_surface_markers": (
            "reset freeze state",
            "recovery reservation replay preflight",
            "PRP span pressure",
            "frozen queue-restore host-DMA budgeting",
        ),
        "blocked_by_markers": (
            "No throughput benchmark",
            "transport-backed reset replay",
        ),
    },
    "segmented_rollout": {
        "status": "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_dedicated_build_present_shared_build_absent",
        "current_surface_markers": (
            "fallback map",
            "dedicated direct-build route",
            "`zigux/tests/phase12_build.zig` still remains virtio_net-only",
        ),
        "blocked_by_markers": (
            "dedicated survey gate",
            "dedicated direct-build route",
            "transport-backed queue execution",
        ),
    },
}

EXPECTED_GAPS = {
    "phase12-nvme-fallback-note": {
        "status": "landed_on_master",
        "kind": "documentation",
        "zigux_destination": FALLBACK_MAP_PATH,
    },
    "phase12-nvme-reopen-governance": {
        "status": "landed_on_master",
        "kind": "documentation",
        "zigux_destination": REOPEN_GOVERNANCE_PATH,
    },
    "phase12-nvme-direct-replay": {
        "status": "landed_on_master_dedicated_build_present",
        "kind": "validation",
        "zigux_destination": DIRECT_REPLAY_PATH,
    },
    "phase12-nvme-manifest-anchor": {
        "status": "landed_on_master",
        "kind": "validation",
        "zigux_destination": MANIFEST_PATH,
    },
    "phase12-nvme-shared-build-route": {
        "status": "shared_build_absent_dedicated_build_present_survey_gate_standalone",
        "kind": "validation",
        "zigux_destination": "zigux/tests/phase12_build.zig",
    },
    "phase12-nvme-slice-note": {
        "status": "landed_on_master",
        "kind": "documentation",
        "zigux_destination": SLICE_PATH,
    },
    "phase12-nvme-survey-note": {
        "status": "survey_present_dedicated_direct_build_only",
        "kind": "documentation",
        "zigux_destination": SURVEY_NOTE_PATH,
    },
    "phase12-nvme-survey-gate": {
        "status": "survey_present_dedicated_route_retained",
        "kind": "validation",
        "zigux_destination": SURVEY_GATE_PATH,
    },
}

EXTRA_REQUIRED_PATHS = (
    "drivers/nvme/host/pci.zig",
    VERIFIER_PATH,
    DIRECT_BUILD_PATH,
    SURVEY_BUILD_PATH,
    DIRECT_REPLAY_PATH,
)

TEXT_MARKERS = {
    DIRECT_BUILD_PATH: (
        "phase12_nvme_pci.zig",
        "phase12-nvme-pci-direct-tests",
        "phase12-nvme-pci-direct-test",
        "Run the direct Phase 12 NVMe PCI replay, helper-local wrapper proof, and driver-local verifier in isolation",
    ),
    SURVEY_BUILD_PATH: (
        "phase12_nvme_pci_survey.zig",
        "phase12-nvme-pci-survey-tests",
        "run_tests.setCwd(b.path(\"../..\"));",
        "phase12-nvme-pci-survey-test",
        "Run the Phase 12 NVMe PCI survey gate tests in isolation",
    ),
    DIRECT_REPLAY_PATH: (
        "phase12 nvme pci direct replay keeps stale recovery reservation debt explicit",
        "phase12 nvme pci direct replay keeps rollback-gate parity explicit through recovery",
        "phase12 nvme pci direct replay keeps admin replay blocker explicit even after IO counts recover",
        "phase12 nvme pci direct replay keeps dropped backlog retirement blocked until admin replay completes even after IO parity recovers",
    ),
    VERIFIER_PATH: (
        "nvme pci recovery rollback gate verifier keeps blocker transitions and DMA parity explicit",
        "nvme pci recovery reservation replay preflight marks stale PRP metadata and planner-limited replay debt",
        "nvme pci rollback gate keeps admin replay blocked even after queue and DMA parity recover",
        "nvme pci recovery reservation replay debt summary keeps admin replay blocker ahead of stale descriptor debt",
    ),
    FALLBACK_MAP_PATH: (
        "## Current-Master Raw Path Map",
        "Base raw URL prefix:",
        "`https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/`",
        "- starter shard raw path: `drivers/nvme/host/pci.zig`",
        "- verifier shard raw path: `drivers/nvme/host/pci_verify.zig`",
        "- direct replay raw path: `zigux/tests/phase12_nvme_pci.zig`",
        "- dedicated direct-build raw path: `zigux/tests/phase12_nvme_pci_build.zig`",
        "- slice note raw path: `Documentation/zigux/phase12-nvme-pci-slice.md`",
        "- survey note raw path: `Documentation/zigux/phase12-nvme-pci-survey.md`",
        "- survey gate raw path: `zigux/tests/phase12_nvme_pci_survey.zig`",
        "- manifest anchor raw path: `zigux/tests/phase12_nvme_pci_manifest.json`",
        "- reopen-governance raw path: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`",
    ),
    SLICE_PATH: (
        "queue-pair planning",
        "IO queue reservation sizing",
        "recovery reservation replay debt",
        "recovery reservation replay preflight",
        "applied summaries",
        "queue-numbering restart review",
        "PRP buffer-shape accounting",
        "PRP metadata budgeting",
        "dropped-backlog retirement review",
        "rollback-gate review",
        "frozen queue-restore budgeting",
        "It stays below live DMA mapping",
    ),
    SURVEY_NOTE_PATH: (
        "PHASE12_STATUS=starter_verifier_direct_replay_manifest_and_survey_gate_present_dedicated_build_present_shared_build_absent",
        "lane owner: `P12-L08`",
        "drivers/nvme/host/pci.zig",
        "drivers/nvme/host/pci_verify.zig",
        "zigux/tests/phase12_nvme_pci.zig",
        "zigux/tests/phase12_nvme_pci_build.zig",
        "dedicated `phase12-nvme-pci-direct-test` route in `zigux/tests/phase12_nvme_pci_build.zig`",
        "`zigux/tests/phase12_build.zig` route still stays virtio-net-only",
        "survey gate still stays packet-local",
        "IO queue reservation sizing",
        "recovery reservation replay debt",
        "PRP metadata budgeting",
        "live DMA mapping",
        "transport-backed queue execution",
    ),
    REOPEN_GOVERNANCE_PATH: (
        "dedicated `phase12-nvme-pci-direct-test` route in `zigux/tests/phase12_nvme_pci_build.zig`",
        "`zigux/tests/phase12_build.zig` still stays virtio_net-only",
        "must not promote the bounded NVMe starter beyond its current dedicated direct-build claim",
        "phase12-smoke",
        "phase12-test",
        "phase12",
    ),
    SURVEY_GATE_PATH: (
        "phase12 nvme pci survey manifest keeps the bounded starter packet truthful",
        "phase12 nvme pci survey note keeps the roadmap gap and dedicated-build split explicit",
        "phase12 nvme pci reopen governance note keeps the dedicated direct replay and packet-local survey split explicit",
        "phase12 nvme pci slice note keeps the bounded recovery-preflight packet explicit",
        "phase12 nvme pci survey gate keeps present packet files explicit",
        "phase12 nvme pci survey gate keeps the dedicated direct route driver-local for NVMe",
        "phase12 nvme pci survey gate keeps the make wrapper surface explicit",
        "phase12 nvme pci survey gate keeps the current recovery helper packet explicit",
    ),
}

FORBIDDEN_MARKERS = {
    SURVEY_NOTE_PATH: (
        "now wires the NVMe direct replay into the shared `phase12-smoke` and `phase12` routes",
    ),
    REOPEN_GOVERNANCE_PATH: (
        "shares one bounded direct replay through the shared `phase12-smoke` and `phase12` routes",
        "`zigux/tests/phase12_build.zig` now wires the NVMe direct replay into the smoke-first shared route",
    ),
}


class CheckFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def forbid_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise CheckFailure(f"{label} contains forbidden marker: {marker}")


def check_manifest(root: Path) -> int:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    require(manifest.get("lane_key") == EXPECTED_LANE_KEY, "nvme_pci manifest lane_key drifted")
    require(manifest.get("phase") == EXPECTED_PHASE, "nvme_pci manifest phase drifted")
    require(manifest.get("anchor") == EXPECTED_ANCHOR, "nvme_pci manifest anchor drifted")
    require(
        manifest.get("roadmap_destinations") == EXPECTED_ROADMAP_DESTINATIONS,
        "nvme_pci manifest roadmap destinations drifted",
    )

    surveyed_commit = manifest.get("surveyed_commit", "")
    require(
        len(surveyed_commit) == 40 and all(ch in "0123456789abcdef" for ch in surveyed_commit),
        "nvme_pci manifest surveyed_commit is not a 40-char lowercase hex sha",
    )
    try:
        date.fromisoformat(manifest.get("verified_on", ""))
    except ValueError as exc:
        raise CheckFailure("nvme_pci manifest verified_on is not an ISO date") from exc

    summary = manifest.get("survey_summary")
    require(isinstance(summary, dict), "nvme_pci survey_summary is not a mapping")
    for flag in EXPECTED_SUMMARY_FLAGS:
        require(summary.get(flag) is True, f"nvme_pci survey_summary flag missing: {flag}")

    roadmap_gap_check = manifest.get("roadmap_gap_check")
    require(isinstance(roadmap_gap_check, dict), "nvme_pci roadmap_gap_check is not a mapping")
    for slug, expected in EXPECTED_ROADMAP_GAP_CHECK.items():
        section = roadmap_gap_check.get(slug)
        require(isinstance(section, dict), f"nvme_pci roadmap gap section missing: {slug}")
        require(section.get("required_by_roadmap") is True, f"nvme_pci roadmap gap section lost required_by_roadmap: {slug}")
        require(section.get("status") == expected["status"], f"nvme_pci roadmap gap status drifted: {slug}")
        require_markers(section.get("current_surface", ""), expected["current_surface_markers"], f"nvme_pci roadmap current_surface[{slug}]")
        require_markers(section.get("blocked_by", ""), expected["blocked_by_markers"], f"nvme_pci roadmap blocked_by[{slug}]")

    gaps = manifest.get("gaps")
    require(isinstance(gaps, list), "nvme_pci manifest gaps field is not a list")
    gap_map = {gap["id"]: gap for gap in gaps if isinstance(gap, dict) and isinstance(gap.get("id"), str)}
    for gap_id, expected in EXPECTED_GAPS.items():
        gap = gap_map.get(gap_id)
        require(gap is not None, f"nvme_pci manifest missing gap: {gap_id}")
        require(gap.get("status") == expected["status"], f"nvme_pci gap status drifted: {gap_id}")
        require(gap.get("kind") == expected["kind"], f"nvme_pci gap kind drifted: {gap_id}")
        require(gap.get("zigux_destination") == expected["zigux_destination"], f"nvme_pci gap destination drifted: {gap_id}")
        require((root / expected["zigux_destination"]).exists(), f"missing required packet path: {expected['zigux_destination']}")

    for relative_path in EXTRA_REQUIRED_PATHS:
        require((root / relative_path).exists(), f"missing required packet path: {relative_path}")

    for relative_path, markers in TEXT_MARKERS.items():
        text = read_text(root, relative_path)
        require_markers(text, markers, relative_path)
        if relative_path in FORBIDDEN_MARKERS:
            forbid_markers(text, FORBIDDEN_MARKERS[relative_path], relative_path)

    require(surveyed_commit in read_text(root, SURVEY_NOTE_PATH), "nvme_pci survey note lost the manifest surveyed_commit pin")
    return len(gaps)


def write_fixture(root: Path) -> None:
    manifest = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": EXPECTED_COMMIT,
        "verified_on": "2026-05-22",
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
    }

    fixture_files = {
        MANIFEST_PATH: json.dumps(manifest, indent=2) + "\n",
        DIRECT_BUILD_PATH: "\n".join(TEXT_MARKERS[DIRECT_BUILD_PATH]) + "\n",
        SURVEY_BUILD_PATH: "\n".join(TEXT_MARKERS[SURVEY_BUILD_PATH]) + "\n",
        DIRECT_REPLAY_PATH: "\n".join(TEXT_MARKERS[DIRECT_REPLAY_PATH]) + "\n",
        VERIFIER_PATH: "\n".join(TEXT_MARKERS[VERIFIER_PATH]) + "\n",
        FALLBACK_MAP_PATH: "\n".join(TEXT_MARKERS[FALLBACK_MAP_PATH]) + "\n",
        SLICE_PATH: "\n".join(TEXT_MARKERS[SLICE_PATH]) + "\n",
        SURVEY_NOTE_PATH: "\n".join(TEXT_MARKERS[SURVEY_NOTE_PATH] + (EXPECTED_COMMIT,)) + "\n",
        REOPEN_GOVERNANCE_PATH: "\n".join(TEXT_MARKERS[REOPEN_GOVERNANCE_PATH]) + "\n",
        SURVEY_GATE_PATH: "\n".join(TEXT_MARKERS[SURVEY_GATE_PATH]) + "\n",
        "drivers/nvme/host/pci.zig": "fixture\n",
        "zigux/tests/phase12_build.zig": "fixture\n",
    }

    for relative_path, text in fixture_files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def rewrite(root: Path, relative_path: str, content: str) -> None:
    (root / relative_path).write_text(content, encoding="utf-8")


def expect_failure(root: Path, token: str) -> None:
    try:
        check_manifest(root)
    except CheckFailure as exc:
        if token not in str(exc):
            raise
    else:
        raise AssertionError(f"expected {token} drift to fail")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        write_fixture(root)
        check_manifest(root)
        cases += 1

        manifest_path = root / MANIFEST_PATH

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P12-L02"
        rewrite(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "lane_key")
        cases += 1

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["surveyed_commit"] = "0123456789ABCDEF0123456789abcdef01234567"
        rewrite(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "surveyed_commit")
        cases += 1

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["verified_on"] = "2026/05/22"
        rewrite(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "verified_on")
        cases += 1

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_summary"]["preexisting_phase12_survey_gate_present"] = False
        rewrite(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "preexisting_phase12_survey_gate_present")
        cases += 1

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_gap_check"]["throughput_and_recovery_parity"]["current_surface"] = "reset freeze state only"
        rewrite(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "throughput_and_recovery_parity")
        cases += 1

        write_fixture(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["gaps"][4]["status"] = "landed_on_master"
        rewrite(root, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "phase12-nvme-shared-build-route")
        cases += 1

        write_fixture(root)
        rewrite(root, FALLBACK_MAP_PATH, "## Current-Master Raw Path Map\n")
        expect_failure(root, FALLBACK_MAP_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, DIRECT_BUILD_PATH, "phase12_nvme_pci.zig\n")
        expect_failure(root, DIRECT_BUILD_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, SURVEY_BUILD_PATH, "phase12_nvme_pci_survey.zig\n")
        expect_failure(root, SURVEY_BUILD_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, DIRECT_REPLAY_PATH, "phase12 nvme pci direct replay keeps stale recovery reservation debt explicit\n")
        expect_failure(root, DIRECT_REPLAY_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, VERIFIER_PATH, "nvme pci recovery rollback gate verifier keeps blocker transitions and DMA parity explicit\n")
        expect_failure(root, VERIFIER_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, SURVEY_NOTE_PATH, TEXT_MARKERS[SURVEY_NOTE_PATH][0] + "\n")
        expect_failure(root, SURVEY_NOTE_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, SURVEY_NOTE_PATH, "\n".join(TEXT_MARKERS[SURVEY_NOTE_PATH] + FORBIDDEN_MARKERS[SURVEY_NOTE_PATH] + (EXPECTED_COMMIT,)) + "\n")
        expect_failure(root, "forbidden marker")
        cases += 1

        write_fixture(root)
        rewrite(root, REOPEN_GOVERNANCE_PATH, TEXT_MARKERS[REOPEN_GOVERNANCE_PATH][0] + "\n")
        expect_failure(root, REOPEN_GOVERNANCE_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, REOPEN_GOVERNANCE_PATH, "\n".join(TEXT_MARKERS[REOPEN_GOVERNANCE_PATH] + FORBIDDEN_MARKERS[REOPEN_GOVERNANCE_PATH]) + "\n")
        expect_failure(root, "forbidden marker")
        cases += 1

        write_fixture(root)
        rewrite(root, SLICE_PATH, "queue-pair planning\n")
        expect_failure(root, SLICE_PATH)
        cases += 1

        write_fixture(root)
        rewrite(root, SURVEY_GATE_PATH, TEXT_MARKERS[SURVEY_GATE_PATH][0] + "\n")
        expect_failure(root, SURVEY_GATE_PATH)
        cases += 1

        write_fixture(root)
        (root / DIRECT_BUILD_PATH).unlink()
        expect_failure(root, "phase12_nvme_pci_build.zig")
        cases += 1

        write_fixture(root)
        (root / SURVEY_BUILD_PATH).unlink()
        expect_failure(root, "phase12_nvme_pci_survey_build.zig")
        cases += 1

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
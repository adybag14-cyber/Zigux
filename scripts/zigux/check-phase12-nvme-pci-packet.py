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
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
SURVEY_PATH = Path("zigux/tests/phase12_nvme_pci_survey.zig")
SURVEY_NOTE_PATH = Path("Documentation/zigux/phase12-nvme-pci-survey.md")
REOPEN_PATH = Path("Documentation/zigux/phase12-nvme-pci-reopen-governance.md")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_GAP_STATUSES = {
    "queueing": "starter_verifier_direct_test_manifest_and_survey_gate_present_shared_direct_replay_present",
    "throughput": "recovery_budget_summary_shared_direct_replay_present_throughput_gate_missing",
    "segmented": "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_shared_direct_replay_present",
    "shared_route": "shared_build_present_direct_replay_only_survey_gate_standalone",
    "survey_note": "survey_present_shared_direct_replay_dedicated_verify_and_survey_retained",
    "survey_gate": "survey_present_packet_local_route_retained",
}


class CheckFailure(RuntimeError):
    pass


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise CheckFailure(msg)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {rel.as_posix()}") from exc


def check(root: Path) -> int:
    manifest = json.loads(read_text(root, MANIFEST_PATH))
    require(manifest["lane_key"] == "P12-L08", "manifest lane drifted")
    require(manifest["phase"] == "Phase 12", "manifest phase drifted")
    require(manifest["anchor"] == "drivers/nvme/host/pci.c", "manifest anchor drifted")
    statuses_blob = json.dumps(manifest, sort_keys=True)
    for status in EXPECTED_GAP_STATUSES.values():
        require(status in statuses_blob, f"manifest missing status: {status}")

    survey_note = read_text(root, SURVEY_NOTE_PATH)
    require("PHASE12_STATUS=starter_verifier_direct_replay_manifest_and_survey_gate_present_shared_direct_replay_present" in survey_note, "survey note status drifted")
    require("the shared `zigux/tests/phase12_build.zig` route now wires the bounded NVMe direct replay into `phase12-smoke`, `phase12-test`, and `phase12`" in survey_note, "survey note lost shared direct replay wording")
    require("route still stays virtio-net-only" not in survey_note, "survey note kept stale virtio-net-only wording")

    reopen = read_text(root, REOPEN_PATH)
    require("shares one bounded direct replay through the shared `phase12-smoke`, `phase12-test`, and `phase12` routes" in reopen, "reopen note lost shared direct replay wording")
    require("still stays virtio_net-only" not in reopen, "reopen note kept stale exclusivity wording")

    shared_build = read_text(root, BUILD_PATH)
    require("phase12_nvme_pci.zig" in shared_build, "shared build lost nvme direct replay root")
    require("phase12-nvme-pci-direct-tests" in shared_build, "shared build lost nvme direct test name")
    require("phase12_nvme_pci_survey.zig" not in shared_build, "shared build wrongly absorbed packet-local survey gate")
    require(shared_build.count("b.createModule(.{") == 13, "shared build module count drifted")
    require(shared_build.count(".addImport(") == 6, "shared build import count drifted")
    require(shared_build.count("b.addTest(.{") == 7, "shared build test count drifted")
    require(shared_build.count("b.addRunArtifact(") == 7, "shared build run-artifact count drifted")

    survey_gate = read_text(root, SURVEY_PATH)
    require("phase12 nvme pci survey manifest keeps the bounded starter packet truthful" in survey_gate, "survey gate lost manifest test")
    require("phase12 nvme pci survey gate keeps the shared build and make wrapper surface explicit" in survey_gate, "survey gate lost shared build test")

    makefile = read_text(root, MAKEFILE_PATH)
    for marker in ("phase12-smoke:", "phase12-test:", "phase12-nvme-pci-direct-test:", "phase12-nvme-pci-survey-test:", "phase12: phase12-validate phase12-smoke phase12-test"):
        require(marker in makefile, f"makefile marker missing: {marker}")

    return len(manifest["gaps"])


def write_fixture(root: Path) -> None:
    from shutil import copyfile

    src_root = Path("/workspace/zigux_phase12_patch")
    needed = [MANIFEST_PATH, BUILD_PATH, SURVEY_PATH, SURVEY_NOTE_PATH, REOPEN_PATH, MAKEFILE_PATH]
    for rel in needed:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        copyfile(src_root / rel, dst)


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-nvme-packet-") as tmp:
        root = Path(tmp)
        write_fixture(root)
        check(root)
        cases += 1

        bad_manifest = root / MANIFEST_PATH
        manifest = json.loads(bad_manifest.read_text(encoding="utf-8"))
        manifest["lane_key"] = "P12-L00"
        bad_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            require("lane drifted" in str(exc), "self-test expected lane failure")
        else:
            raise SystemExit("expected lane failure")
        cases += 1

        write_fixture(root)
        (root / SURVEY_NOTE_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            require("survey note" in str(exc), "self-test expected survey-note failure")
        else:
            raise SystemExit("expected survey-note failure")
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
        gap_count = check(Path(args.root))
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail")
        print(f"{CHECK_NAME}_ERROR={exc}")
        return 1
    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_GAP_COUNT={gap_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase12.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_libbpf_segments.zig",
]

MAKE_MARKERS = [
    "PHONY += phase12-validate phase12-test phase12",
    "phase12-validate:",
    "scripts/zigux/validate-phase12.py",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-validate phase12-test",
]
WORKFLOW_MARKERS = [
    "Validate Phase 12 degraded-workflow bundle",
    "make -C zigux phase12-validate",
    "Run Phase 12 complex driver tests",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
]
README_MARKERS = [
    "validate-phase12.py",
    "Phase 12 flow",
    "make -C zigux phase12-validate",
    "phase12_virtio_net_manifest.json",
    "phase12_nvme_pci_manifest.json",
    "phase12_virtio_scsi_manifest.json",
    "phase12_libbpf_manifest.json",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, and the four Phase 12 manifests still agree on the same bounded tranche, shared replay contract, and explicit DMA versus object-model blocker posture?",
    "if the change touches the shared Phase 12 degraded-workflow packet, do the workflow path, README notes, review checklist, and `zigux/tests/phase12_virtio_scsi_survey.zig` still agree that `make -C zigux phase12` runs the validator before the shared Zig replay?",
]
BUILD_MARKERS = [
    "phase12-nvme-pci-tests",
    "phase12-nvme-pci-survey-tests",
    "phase12-virtio-net-tests",
    "phase12-virtio-net-survey-tests",
    "phase12-virtio-scsi-tests",
    "phase12-virtio-scsi-survey-tests",
    "phase12-libbpf-segment-survey-tests",
    "phase12-libbpf-reviewability-tests",
    "test_step.dependOn(&run_phase12_nvme_pci_tests.step);",
    "test_step.dependOn(&run_phase12_nvme_pci_survey_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_net_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_net_survey_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_scsi_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_scsi_survey_tests.step);",
    "test_step.dependOn(&run_phase12_libbpf_segments_tests.step);",
    "test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);",
]

MANIFEST_SPECS = {
    "phase12_virtio_net_manifest.json": {
        "lane_key": "P12-L01",
        "anchor": "drivers/net/virtio_net.c",
        "gap_count": 9,
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "survey_path": "zigux/tests/phase12_virtio_net_survey.zig",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_nvme_pci_manifest.json": {
        "lane_key": "P12-L05",
        "anchor": "drivers/nvme/host/pci.c",
        "gap_count": 11,
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "survey_path": "zigux/tests/phase12_nvme_pci_survey.zig",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_virtio_scsi_manifest.json": {
        "lane_key": "P12-L09",
        "anchor": "drivers/scsi/virtio_scsi.c",
        "gap_count": 12,
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "survey_path": "zigux/tests/phase12_virtio_scsi_survey.zig",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_libbpf_manifest.json": {
        "lane_key": "P12-L13",
        "anchor": "tools/lib/bpf/libbpf.c",
        "gap_count": 12,
        "allowed_statuses": {"starter_landed", "blocked_on_object_model"},
        "survey_path": "zigux/tests/phase12_libbpf_segments.zig",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("ready_next_count", "ready_next"), ("blocked_count", "blocked_on_object_model")],
    },
}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_manifest(name: str) -> dict[str, object]:
    return json.loads(text(f"zigux/tests/{name}"))


def count_statuses(manifest: dict[str, object], match: str) -> int:
    total = 0
    for gap in manifest.get("gaps", []):
        status = gap.get("status")
        if not isinstance(status, str):
            continue
        if status == match:
            total += 1
    return total


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE12_VALIDATION=fail")
    print("MISSING_PHASE12_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE12_FILES_END")
    sys.exit(1)

missing: list[str] = []
for name, source, markers in [
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("script_readme", text("scripts/zigux/README.md"), README_MARKERS),
    ("review_checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
    ("phase12_build", text("zigux/tests/phase12_build.zig"), BUILD_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

starter_total = 0
blocked_dma_total = 0
blocked_object_total = 0
for name, spec in MANIFEST_SPECS.items():
    manifest = load_manifest(name)
    if manifest.get("phase") != "Phase 12":
        missing.append(f"{name}:phase")
    if manifest.get("lane_key") != spec["lane_key"]:
        missing.append(f"{name}:lane_key")
    if manifest.get("anchor") != spec["anchor"]:
        missing.append(f"{name}:anchor")
    if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
        missing.append(f"{name}:surveyed_commit")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != spec["gap_count"]:
        missing.append(f"{name}:gap_count")
        continue

    seen: set[str] = set()
    for gap in gaps:
        gap_id = gap.get("id")
        status = gap.get("status")
        if not isinstance(gap_id, str) or gap_id in seen:
            missing.append(f"{name}:gap_id")
            continue
        seen.add(gap_id)
        if status not in spec["allowed_statuses"]:
            missing.append(f"{name}:status:{gap_id}")
            continue
        if status == "starter_landed":
            starter_total += 1
        elif status == "blocked_on_dma_transport":
            blocked_dma_total += 1
        elif status == "blocked_on_object_model":
            blocked_object_total += 1

    survey_text = text(spec["survey_path"])
    commit = str(manifest.get("surveyed_commit", ""))
    if commit not in survey_text:
        missing.append(f"{name}:survey_commit_pin")
    for variable_name, status_match in spec["survey_count_markers"]:
        expected_count = count_statuses(manifest, status_match)
        count_marker = f'expectEqual(@as(usize, {expected_count}), {variable_name});'
        if count_marker not in survey_text:
            missing.append(f"{name}:survey_count:{variable_name}={expected_count}")

if starter_total != 39:
    missing.append(f"starter_total:{starter_total}")
if blocked_dma_total != 3:
    missing.append(f"blocked_dma_total:{blocked_dma_total}")
if blocked_object_total != 2:
    missing.append(f"blocked_object_total:{blocked_object_total}")

if missing:
    print("PHASE12_VALIDATION=fail")
    print("PHASE12_VALIDATION_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE12_VALIDATION_MISSING_END")
    sys.exit(1)

print("PHASE12_VALIDATION=pass")
print("PHASE12_MANIFEST_COUNT=4")
print(f"PHASE12_STARTER_STATUS_COUNT={starter_total}")
print(f"PHASE12_BLOCKED_DMA_STATUS_COUNT={blocked_dma_total}")
print(f"PHASE12_BLOCKED_OBJECT_STATUS_COUNT={blocked_object_total}")

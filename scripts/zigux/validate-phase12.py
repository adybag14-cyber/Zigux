#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase12-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")

FILES = [
    "scripts/zigux/validate-phase12.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/fixtures/phase12_build_inventory.json",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_libbpf_segments.zig",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
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
    "phase12_build_inventory.json",
    "phase12_virtio_net_manifest.json",
    "phase12_nvme_pci_manifest.json",
    "phase12_virtio_scsi_manifest.json",
    "phase12_libbpf_manifest.json",
    "shared build inventory snapshot",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, and the four Phase 12 manifests still agree on the same bounded tranche, approved roadmap destinations, shared replay contract, and explicit DMA versus object-model blocker posture?",
    "if the change touches the shared Phase 12 degraded-workflow packet, do the workflow path, README notes, review checklist, and `zigux/tests/phase12_virtio_scsi_survey.zig` still agree that `make -C zigux phase12` runs the validator before the shared Zig replay?",
    "if the change touches the shared Phase 12 tooling path, do `zigux/tests/phase12_build.zig`, `zigux/tests/fixtures/phase12_build_inventory.json`, and the shared Phase 12 manifests still agree on the exact shared build inventory instead of leaving the replay shape implicit?",
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
FORBIDDEN_BUILD_MARKERS: list[str] = []
BUILD_INVENTORY_FIXTURE = "zigux/tests/fixtures/phase12_build_inventory.json"

MANIFEST_SPECS = {
    "phase12_virtio_net_manifest.json": {
        "lane_key": "P12-L01",
        "anchor": "drivers/net/virtio_net.c",
        "gap_count": 11,
        "roadmap_destinations": ["drivers/net/virtio_net.zig", "zigux/tests/"],
        "shared_allowed_destinations": {
            "Documentation/zigux/",
            "zigux/Makefile",
            "drivers/virtio/virtio.zig",
            "drivers/virtio/virtio_ring.zig",
        },
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "expected_status_totals": {"starter_landed": 10, "blocked_on_dma_transport": 1},
        "survey_path": "zigux/tests/phase12_virtio_net_survey.zig",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_nvme_pci_manifest.json": {
        "lane_key": "P12-L05",
        "anchor": "drivers/nvme/host/pci.c",
        "gap_count": 12,
        "roadmap_destinations": ["drivers/nvme/host/pci.zig", "zigux/tests/", "Documentation/zigux/"],
        "shared_allowed_destinations": {
            "zigux/Makefile",
            "drivers/net/virtio_net.zig",
            "drivers/scsi/virtio_scsi.zig",
        },
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "expected_status_totals": {"starter_landed": 11, "blocked_on_dma_transport": 1},
        "survey_path": "zigux/tests/phase12_nvme_pci_survey.zig",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_virtio_scsi_manifest.json": {
        "lane_key": "P12-L09",
        "anchor": "drivers/scsi/virtio_scsi.c",
        "gap_count": 13,
        "roadmap_destinations": ["drivers/scsi/virtio_scsi.zig", "zigux/tests/", "Documentation/zigux/"],
        "shared_allowed_destinations": {
            "zigux/Makefile",
            "drivers/virtio/virtio.zig",
            "drivers/virtio/virtio_ring.zig",
        },
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "expected_status_totals": {"starter_landed": 12, "blocked_on_dma_transport": 1},
        "survey_path": "zigux/tests/phase12_virtio_scsi_survey.zig",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_libbpf_manifest.json": {
        "lane_key": "P12-L13",
        "anchor": "tools/lib/bpf/libbpf.c",
        "gap_count": 12,
        "roadmap_destinations": ["tools/lib/bpf/zigux_segments/", "zigux/tests/", "Documentation/zigux/"],
        "shared_allowed_destinations": {"zigux/Makefile"},
        "allowed_statuses": {"starter_landed", "blocked_on_object_model"},
        "expected_status_totals": {"starter_landed": 10, "blocked_on_object_model": 2},
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


def destination_allowed(destination: str, spec: dict[str, object]) -> bool:
    roadmap_destinations = tuple(str(item) for item in spec["roadmap_destinations"])
    if destination.startswith(roadmap_destinations):
        return True
    for allowed in spec.get("shared_allowed_destinations", set()):
        if allowed.endswith("/") and destination.startswith(allowed):
            return True
        if destination == allowed:
            return True
    return False


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

build_text = text("zigux/tests/phase12_build.zig")
for marker in FORBIDDEN_BUILD_MARKERS:
    if marker in build_text:
        missing.append(f"phase12_build:forbidden:{marker}")

build_inventory = json.loads(text(BUILD_INVENTORY_FIXTURE))
expected_build_test_names = build_inventory.get("build_test_names")
if not isinstance(expected_build_test_names, list) or not all(isinstance(item, str) for item in expected_build_test_names):
    missing.append("phase12_build_fixture:build_test_names")
else:
    actual_build_test_names = BUILD_TEST_NAME_RE.findall(build_text)
    if actual_build_test_names != expected_build_test_names:
        missing.append("phase12_build_fixture:build_test_names_mismatch")

expected_depend_steps = build_inventory.get("shared_test_depend_steps")
if not isinstance(expected_depend_steps, list) or not all(isinstance(item, str) for item in expected_depend_steps):
    missing.append("phase12_build_fixture:shared_test_depend_steps")
else:
    actual_depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
    if actual_depend_steps != expected_depend_steps:
        missing.append("phase12_build_fixture:shared_test_depend_steps_mismatch")

expected_forbidden_markers = build_inventory.get("forbidden_markers")
if expected_forbidden_markers != FORBIDDEN_BUILD_MARKERS:
    missing.append("phase12_build_fixture:forbidden_markers")

dedicated_survey_replays = build_inventory.get("dedicated_survey_replays")
if dedicated_survey_replays != []:
    missing.append("phase12_build_fixture:dedicated_survey_replays")

starter_total = 0
blocked_dma_total = 0
blocked_object_total = 0
expected_starter_total = 0
expected_blocked_dma_total = 0
expected_blocked_object_total = 0
for name, spec in MANIFEST_SPECS.items():
    manifest = load_manifest(name)
    if manifest.get("phase") != "Phase 12":
        missing.append(f"{name}:phase")
    if manifest.get("lane_key") != spec["lane_key"]:
        missing.append(f"{name}:lane_key")
    if manifest.get("anchor") != spec["anchor"]:
        missing.append(f"{name}:anchor")
    if manifest.get("roadmap_destinations") != spec["roadmap_destinations"]:
        missing.append(f"{name}:roadmap_destinations")
    if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
        missing.append(f"{name}:surveyed_commit")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != spec["gap_count"]:
        missing.append(f"{name}:gap_count")
        continue

    seen: set[str] = set()
    manifest_status_totals: dict[str, int] = {}
    for gap in gaps:
        gap_id = gap.get("id")
        status = gap.get("status")
        destination = gap.get("zigux_destination")
        if not isinstance(gap_id, str) or gap_id in seen:
            missing.append(f"{name}:gap_id")
            continue
        seen.add(gap_id)
        if status not in spec["allowed_statuses"]:
            missing.append(f"{name}:status:{gap_id}")
            continue
        if not isinstance(destination, str) or not destination_allowed(destination, spec):
            missing.append(f"{name}:destination:{gap_id}")
            continue
        manifest_status_totals[status] = manifest_status_totals.get(status, 0) + 1
        if status == "starter_landed":
            starter_total += 1
        elif status == "blocked_on_dma_transport":
            blocked_dma_total += 1
        elif status == "blocked_on_object_model":
            blocked_object_total += 1

    for status, expected_total in spec["expected_status_totals"].items():
        actual_total = manifest_status_totals.get(status, 0)
        if actual_total != expected_total:
            missing.append(f"{name}:status_total:{status}={actual_total}")
        if status == "starter_landed":
            expected_starter_total += expected_total
        elif status == "blocked_on_dma_transport":
            expected_blocked_dma_total += expected_total
        elif status == "blocked_on_object_model":
            expected_blocked_object_total += expected_total

    survey_text = text(spec["survey_path"])
    commit = str(manifest.get("surveyed_commit", ""))
    if commit not in survey_text:
        missing.append(f"{name}:survey_commit_pin")
    for variable_name, status_match in spec["survey_count_markers"]:
        expected_count = count_statuses(manifest, status_match)
        count_marker = f'expectEqual(@as(usize, {expected_count}), {variable_name});'
        if count_marker not in survey_text:
            missing.append(f"{name}:survey_count:{variable_name}={expected_count}")

if starter_total != expected_starter_total:
    missing.append(f"starter_total:{starter_total}")
if blocked_dma_total != expected_blocked_dma_total:
    missing.append(f"blocked_dma_total:{blocked_dma_total}")
if blocked_object_total != expected_blocked_object_total:
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
print(f"PHASE12_SHARED_BUILD_TEST_COUNT={len(expected_build_test_names)}")
print(f"PHASE12_SHARED_BUILD_DEPEND_STEP_COUNT={len(expected_depend_steps)}")
print(f"PHASE12_STARTER_STATUS_COUNT={starter_total}")
print(f"PHASE12_BLOCKED_DMA_STATUS_COUNT={blocked_dma_total}")
print(f"PHASE12_BLOCKED_OBJECT_STATUS_COUNT={blocked_object_total}")

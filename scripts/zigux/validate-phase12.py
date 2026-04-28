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
    "scripts/zigux/check-phase12-build-inventory.py",
    "scripts/zigux/validate-phase12.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
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
    "scripts/zigux/check-phase12-build-inventory.py",
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
    "check-phase12-build-inventory.py",
    "validate-phase12.py",
    "Phase 12 flow",
    "make -C zigux phase12-validate",
    "phase12_build_inventory.json",
    "phase12_virtio_net_manifest.json",
    "phase12_nvme_pci_manifest.json",
    "phase12_virtio_scsi_manifest.json",
    "phase12_libbpf_manifest.json",
    "shared build inventory snapshot",
    "survey notes pinned to each manifest's exact `surveyed_commit`",
]
DOCS_ROOT_MARKERS = [
    "Phase 12 notes",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "the active Phase 12 storage-driver survey packet now keeps the bounded `drivers/scsi/virtio_scsi.zig` queue-layout, recovery, probe snapshot, host-limit summary, and io-queue-map starters visible from the top-level docs index",
    "`zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` now keep that same storage-driver survey packet reviewable through the shared Phase 12 tranche",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, the four Phase 12 manifests, and the four Phase 12 survey notes still agree on the same bounded tranche, exact surveyed commits, approved roadmap destinations, shared replay contract, and explicit DMA versus object-model blocker posture?",
    "if the change touches the shared Phase 12 degraded-workflow packet, do the workflow path, README notes, review checklist, and `zigux/tests/phase12_virtio_scsi_survey.zig` still agree that `make -C zigux phase12` runs the validator before the shared Zig replay?",
    "if the change touches the shared Phase 12 tooling path, do `scripts/zigux/check-phase12-build-inventory.py`, `zigux/tests/phase12_build.zig`, `zigux/tests/fixtures/phase12_build_inventory.json`, and the shared Phase 12 manifests still agree on the exact shared build inventory instead of leaving the replay shape implicit?",
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
        "gap_count": 13,
        "roadmap_destinations": ["drivers/net/virtio_net.zig", "zigux/tests/"],
        "shared_allowed_destinations": {
            "Documentation/zigux/",
            "zigux/Makefile",
            "drivers/virtio/virtio.zig",
            "drivers/virtio/virtio_ring.zig",
        },
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "expected_status_totals": {"starter_landed": 12, "blocked_on_dma_transport": 1},
        "survey_path": "zigux/tests/phase12_virtio_net_survey.zig",
        "survey_note_path": "Documentation/zigux/phase12-virtio-net-survey.md",
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
        "survey_note_path": "Documentation/zigux/phase12-nvme-pci-survey.md",
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
        "survey_note_path": "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
        "raw_fallback_catalog_path": "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        "raw_fallback_tree_urls": [
            "https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi",
            "https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux",
            "https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests",
        ],
        "raw_fallback_artifact_paths": [
            "drivers/scsi/virtio_scsi.zig",
            "zigux/tests/phase12_virtio_scsi.zig",
            "zigux/tests/phase12_virtio_scsi_manifest.json",
            "zigux/tests/phase12_virtio_scsi_survey.zig",
            "zigux/tests/phase12_build.zig",
            "Documentation/zigux/phase12-virtio-scsi-slice.md",
            "Documentation/zigux/phase12-virtio-scsi-survey.md",
            "scripts/zigux/validate-phase12.py",
            "zigux/Makefile",
        ],
        "raw_fallback_raw_paths": [
            "drivers/scsi/virtio_scsi.c",
            "drivers/scsi/virtio_scsi.zig",
            "zigux/tests/phase12_virtio_scsi.zig",
            "zigux/tests/phase12_virtio_scsi_manifest.json",
            "zigux/tests/phase12_virtio_scsi_survey.zig",
            "zigux/tests/phase12_build.zig",
            "Documentation/zigux/phase12-virtio-scsi-slice.md",
            "Documentation/zigux/phase12-virtio-scsi-survey.md",
            "scripts/zigux/validate-phase12.py",
            "zigux/Makefile",
        ],
    },
    "phase12_libbpf_manifest.json": {
        "lane_key": "P12-L13",
        "anchor": "tools/lib/bpf/libbpf.c",
        "gap_count": 14,
        "roadmap_destinations": ["tools/lib/bpf/zigux_segments/", "zigux/tests/", "Documentation/zigux/"],
        "shared_allowed_destinations": {"zigux/Makefile"},
        "allowed_statuses": {"starter_landed", "blocked_on_object_model", "deferred_high_risk"},
        "expected_status_totals": {"starter_landed": 11, "blocked_on_object_model": 1, "deferred_high_risk": 2},
        "survey_path": "zigux/tests/phase12_libbpf_segments.zig",
        "survey_note_path": "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("ready_next_count", "ready_next"), ("blocked_count", "blocked_on_object_model"), ("deferred_count", "deferred_high_risk")],
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


def expect_catalog_marker(catalog_text: str, marker: str, missing_key: str, missing: list[str]) -> None:
    if marker not in catalog_text:
        missing.append(missing_key)


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
    ("docs_root_readme", text("Documentation/zigux/README.md"), DOCS_ROOT_MARKERS),
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

expected_step_count = build_inventory.get("expected_step_count")
expected_test_count = build_inventory.get("expected_test_count")
expected_summary_line = build_inventory.get("expected_summary_line")
if not isinstance(expected_step_count, int) or expected_step_count <= 0:
    missing.append("phase12_build_fixture:expected_step_count")
if not isinstance(expected_test_count, int) or expected_test_count <= 0:
    missing.append("phase12_build_fixture:expected_test_count")
if not isinstance(expected_summary_line, str) or not expected_summary_line:
    missing.append("phase12_build_fixture:expected_summary_line")
elif isinstance(expected_step_count, int) and isinstance(expected_test_count, int):
    canonical_summary_line = (
        f"Build Summary: {expected_step_count}/{expected_step_count} steps succeeded; "
        f"{expected_test_count}/{expected_test_count} tests passed"
    )
    if expected_summary_line != canonical_summary_line:
        missing.append("phase12_build_fixture:expected_summary_line_mismatch")

starter_total = 0
blocked_dma_total = 0
blocked_object_total = 0
deferred_high_risk_total = 0
expected_starter_total = 0
expected_blocked_dma_total = 0
expected_blocked_object_total = 0
expected_deferred_high_risk_total = 0
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
        elif status == "deferred_high_risk":
            deferred_high_risk_total += 1

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
        elif status == "deferred_high_risk":
            expected_deferred_high_risk_total += expected_total

    survey_text = text(spec["survey_path"])
    commit = str(manifest.get("surveyed_commit", ""))
    if commit not in survey_text:
        missing.append(f"{name}:survey_commit_pin")
    for variable_name, status_match in spec["survey_count_markers"]:
        expected_count = count_statuses(manifest, status_match)
        count_marker = f'expectEqual(@as(usize, {expected_count}), {variable_name});'
        if count_marker not in survey_text:
            missing.append(f"{name}:survey_count:{variable_name}={expected_count}")

    survey_note_text = text(str(spec["survey_note_path"]))
    if "PHASE12_STATUS=active" not in survey_note_text:
        missing.append(f"{name}:survey_note_status")
    if str(manifest.get("anchor")) not in survey_note_text:
        missing.append(f"{name}:survey_note_anchor")
    if commit not in survey_note_text:
        missing.append(f"{name}:survey_note_commit_pin")
    if "make -C zigux phase12" not in survey_note_text:
        missing.append(f"{name}:survey_note_make_target")

    raw_fallback_catalog_path = spec.get("raw_fallback_catalog_path")
    if isinstance(raw_fallback_catalog_path, str):
        raw_fallback_catalog_text = text(raw_fallback_catalog_path)
        survey_summary = manifest.get("survey_summary")
        if not isinstance(survey_summary, dict):
            missing.append(f"{name}:survey_summary")
        else:
            tree_count = survey_summary.get("raw_github_tree_fallback_count")
            file_count = survey_summary.get("raw_github_file_fallback_count")
            expect_catalog_marker(
                raw_fallback_catalog_text,
                f"verified_master_head: `{commit}`",
                f"{name}:raw_fallback_catalog_verified_head",
                missing,
            )
            expect_catalog_marker(
                raw_fallback_catalog_text,
                f"inspected_master_head: `{commit}`",
                f"{name}:raw_fallback_catalog_inspected_head",
                missing,
            )
            expect_catalog_marker(
                raw_fallback_catalog_text,
                f"raw_github_tree_fallback_count: `{tree_count}`",
                f"{name}:raw_fallback_catalog_tree_count",
                missing,
            )
            expect_catalog_marker(
                raw_fallback_catalog_text,
                f"raw_github_file_fallback_count: `{file_count}`",
                f"{name}:raw_fallback_catalog_file_count",
                missing,
            )
            expect_catalog_marker(
                raw_fallback_catalog_text,
                f"fallback_anchor_path: `{manifest.get('anchor')}`",
                f"{name}:raw_fallback_catalog_anchor",
                missing,
            )

        for tree_url in spec.get("raw_fallback_tree_urls", []):
            expect_catalog_marker(
                raw_fallback_catalog_text,
                tree_url,
                f"{name}:raw_fallback_catalog_tree_url:{tree_url}",
                missing,
            )
        for artifact_path in spec.get("raw_fallback_artifact_paths", []):
            expect_catalog_marker(
                raw_fallback_catalog_text,
                artifact_path,
                f"{name}:raw_fallback_catalog_artifact:{artifact_path}",
                missing,
            )
        for raw_path in spec.get("raw_fallback_raw_paths", []):
            raw_url = f"https://raw.githubusercontent.com/adybag14-cyber/Zigux/{commit}/{raw_path}"
            expect_catalog_marker(
                raw_fallback_catalog_text,
                raw_url,
                f"{name}:raw_fallback_catalog_raw_url:{raw_path}",
                missing,
            )
        expect_catalog_marker(
            raw_fallback_catalog_text,
            "shared_validator_command: `python3 scripts/zigux/validate-phase12.py`",
            f"{name}:raw_fallback_catalog_validator_command",
            missing,
        )
        expect_catalog_marker(
            raw_fallback_catalog_text,
            "focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`",
            f"{name}:raw_fallback_catalog_survey_command",
            missing,
        )

if starter_total != expected_starter_total:
    missing.append(f"starter_total:{starter_total}")
if blocked_dma_total != expected_blocked_dma_total:
    missing.append(f"blocked_dma_total:{blocked_dma_total}")
if blocked_object_total != expected_blocked_object_total:
    missing.append(f"blocked_object_total:{blocked_object_total}")
if deferred_high_risk_total != expected_deferred_high_risk_total:
    missing.append(f"deferred_high_risk_total:{deferred_high_risk_total}")

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
print(f"PHASE12_EXPECTED_SUMMARY_LINE={expected_summary_line}")
print(f"PHASE12_STARTER_STATUS_COUNT={starter_total}")
print(f"PHASE12_BLOCKED_DMA_STATUS_COUNT={blocked_dma_total}")
print(f"PHASE12_BLOCKED_OBJECT_STATUS_COUNT={blocked_object_total}")
print(f"PHASE12_DEFERRED_HIGH_RISK_STATUS_COUNT={deferred_high_risk_total}")
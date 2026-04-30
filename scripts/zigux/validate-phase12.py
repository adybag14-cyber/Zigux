#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase12-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_MODULE_RE = re.compile(
    r'const ([A-Za-z0-9_]+) = b\.createModule\(\.\{\s*'
    r'\.root_source_file = b\.path\("([^"]+)"\),',
    re.S,
)
BUILD_IMPORT_RE = re.compile(r'([A-Za-z0-9_]+)\.addImport\("([^"]+)", ([A-Za-z0-9_]+)\);')
BUILD_TEST_ROOT_MODULE_RE = re.compile(
    r'\.name = "(phase12-[^"]+)",\s*'
    r'\.root_module = ([A-Za-z0-9_]+),',
    re.S,
)

FILES = [
    "scripts/zigux/check-phase12-build-inventory.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
    "scripts/zigux/validate-phase12.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "drivers/net/virtio_net.zig",
    "drivers/nvme/host/pci.zig",
    "drivers/scsi/virtio_scsi.zig",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/fixtures/phase12_build_inventory.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_nvme_pci.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
]

MAKE_MARKERS = [
    "PHONY += phase12-validate phase12-test phase12",
    "phase12-validate:",
    "scripts/zigux/check-phase12-build-inventory.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
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
    "check-phase12-libbpf-snapshot.py",
    "validate-phase12.py",
    "Phase 12 flow",
    "make -C zigux phase12-validate",
    "phase12_build_inventory.json",
    "phase12_virtio_net_manifest.json",
    "phase12_nvme_pci_manifest.json",
    "phase12_virtio_scsi_manifest.json",
    "phase12_libbpf_manifest.json",
    "shared build inventory snapshot",
    "phase12_libbpf_snapshot.json",
    "survey notes pinned to each manifest's exact `surveyed_commit`",
    "the current active storage-driver survey packet stays explicit through `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, and the paired `zigux/tests/phase12_virtio_scsi_{manifest,survey}.zig` files, so the queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters remain visible without overstating the still-blocked DMA-backed queue ownership, `Scsi_Host` lifecycle, or blk-mq follow-up.",
]
DOCS_ROOT_MARKERS = [
    "Phase 12 notes",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "the active Phase 12 network-driver survey packet now keeps the bounded `drivers/net/virtio_net.zig` probe snapshot, queue-recovery summary, queue-resume summary, `hdr_len`, receive-path, and mergeable-refill helpers visible from the top-level docs index",
    "the same top-level Phase 12 packet now also keeps the bounded `drivers/nvme/host/pci.zig` queue planner, PRP buffer-shape helper, and pointer-selection helper visible from the docs index",
    "the active Phase 12 storage-driver survey packet now keeps the bounded `drivers/scsi/virtio_scsi.zig` queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters visible from the top-level docs index",
    "`zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` now keep that same storage-driver survey packet reviewable through the shared Phase 12 tranche",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, the four Phase 12 manifests, and the four Phase 12 survey notes still agree on the same bounded tranche, exact surveyed commits, approved roadmap destinations, shared replay contract, and explicit DMA versus object-model blocker posture?",
    "if the change touches the shared Phase 12 degraded-workflow packet, do the workflow path, README notes, review checklist, and `zigux/tests/phase12_virtio_scsi_survey.zig` still agree that `make -C zigux phase12` runs the validator before the shared Zig replay?",
    "if the change touches the shared Phase 12 tooling path, do `scripts/zigux/check-phase12-build-inventory.py`, `zigux/tests/phase12_build.zig`, `zigux/tests/fixtures/phase12_build_inventory.json`, and the shared Phase 12 manifests still agree on the exact shared build inventory instead of leaving the replay shape implicit?",
    "if the change touches the shared Phase 12 libbpf snapshot packet, do `scripts/zigux/check-phase12-libbpf-snapshot.py`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and `tools/lib/bpf/zigux_segments/manifest.json` still agree on the same bounded five-file reproducibility packet and exact surveyed commit instead of leaving repeat-run stability in run memory only?",
]
PHASE12_PACKET_MARKERS = {
    "phase12_virtio_net_test": (
        "phase12 virtio net probe starter stays anchored to virtio_net.c",
        "phase12 virtio net freeze and restore preserve queue recovery intent",
        "phase12 virtio net queue resume planning distinguishes renegotiation from reset",
        "phase12 virtio net upgrades hdr_len shape for udp tunnel support",
        "phase12 virtio net flags big-packet receive planning for guest gso throughput",
        "phase12 virtio net plans mergeable refill budgets from mtu and header state",
    ),
    "phase12_virtio_net_survey": (
        "probe snapshot helper plus matching queue-recovery, queue-resume, `hdr_len`, receive-path, and mergeable-refill summaries",
        "records an explicit queue recovery action that distinguishes bounded queue-pair clamping from true single-queue fallback",
        "the lab can report whether the remembered queue plan is ready to resume immediately, needs feature renegotiation, or still requires reset",
        "the probe snapshot mirrors the `hdr_len` branch in `virtnet_probe()`",
        "the probe snapshot records whether probe should expect small buffers, mergeable receive buffers, or big-packet refill pressure",
        "the lab can turn queue-entry count plus negotiated `hdr_len`, MTU, and headroom state into packet budget bytes and a minimum buffer length summary",
    ),
    "phase12_nvme_pci_test": (
        "phase12 nvme pci freezes queue planning across reset and restarts io numbering afterward",
        "phase12 nvme pci prp shape helper records first-page offset and list bounds",
        "phase12 nvme pci data pointer strategy selects prp, threshold sgl, and forced sgl paths",
    ),
    "phase12_nvme_pci_slice": (
        "freezes queue planning during reset and clears planned I/O queue numbering only after reset completion",
        "records one tiny PRP buffer-shape summary with first-page offset, rounded span, and page-list bound checks without claiming live PRP chaining or DMA mapping",
        "records one tiny PRP-versus-SGL selection summary around admin-versus-I/O queues, page-gap forcing, user-command forcing, integrity-segment forcing, and average-segment threshold preference without claiming live descriptor allocation or DMA mapping",
    ),
    "phase12_virtio_scsi_test": (
        "phase12 virtio scsi recovery queue plan mirrors the frozen topology",
        "phase12 virtio scsi recovery io queue map summary mirrors the frozen topology",
        "phase12 virtio scsi freeze blocks derived capture helpers until restore",
    ),
    "phase12_virtio_scsi_slice": (
        "derives one restore-time queue reinitialization plan from the frozen control, event, default-request, and poll-request topology, blocks queue-depth capture while transport is still frozen, then clears the old queue snapshot so the next step must replan instead of pretending virtqueues stayed live",
        "records one queue-depth summary that reuses the bounded host-limit snapshot to mirror `virtscsi_change_queue_depth()`, clamping a requested depth against effective `cmd_per_lun` while keeping `track_queue_depth` reviewable before any live `Scsi_Host` registration work",
        "derives one recovery-time blk-mq queue-map restore summary from the frozen queue layout so the bounded default, read, and poll map counts plus their offsets remain reviewable across transport reset without claiming a live `map_queues` callback or CPU-affinity restore",
    ),
}
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
PHASE12_LIBBPF_SNAPSHOT_FIXTURE = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"

MANIFEST_SPECS = {
    "phase12_virtio_net_manifest.json": {
        "lane_key": "P12-L04",
        "anchor": "drivers/net/virtio_net.c",
        "gap_count": 14,
        "roadmap_destinations": ["drivers/net/virtio_net.zig", "zigux/tests/"],
        "shared_allowed_destinations": {
            "Documentation/zigux/",
            "zigux/Makefile",
            "drivers/virtio/virtio.zig",
            "drivers/virtio/virtio_ring.zig",
        },
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "expected_status_totals": {"starter_landed": 13, "blocked_on_dma_transport": 1},
        "survey_path": "zigux/tests/phase12_virtio_net_survey.zig",
        "survey_note_path": "Documentation/zigux/phase12-virtio-net-survey.md",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_nvme_pci_manifest.json": {
        "lane_key": "P12-L08",
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
        "gap_count": 15,
        "roadmap_destinations": ["drivers/scsi/virtio_scsi.zig", "zigux/tests/", "Documentation/zigux/"],
        "shared_allowed_destinations": {
            "zigux/Makefile",
            "drivers/virtio/virtio.zig",
            "drivers/virtio/virtio_ring.zig",
        },
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "expected_status_totals": {"starter_landed": 14, "blocked_on_dma_transport": 1},
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
        "lane_key": "P12-L16",
        "anchor": "tools/lib/bpf/libbpf.c",
        "gap_count": 17,
        "roadmap_destinations": ["tools/lib/bpf/zigux_segments/", "zigux/tests/", "Documentation/zigux/"],
        "shared_allowed_destinations": {"zigux/Makefile"},
        "allowed_statuses": {"starter_landed", "blocked_on_object_model", "deferred_high_risk"},
        "expected_status_totals": {"starter_landed": 12, "blocked_on_object_model": 1, "deferred_high_risk": 4},
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


def expect_libbpf_snapshot_fixture(
    snapshot: dict[str, object], manifest: dict[str, object], missing: list[str]
) -> None:
    if snapshot.get("lane_key") != manifest.get("lane_key"):
        missing.append("phase12_libbpf_snapshot_fixture:lane_key")
    if snapshot.get("phase") != manifest.get("phase"):
        missing.append("phase12_libbpf_snapshot_fixture:phase")
    if snapshot.get("surveyed_commit") != manifest.get("surveyed_commit"):
        missing.append("phase12_libbpf_snapshot_fixture:surveyed_commit")

    files = snapshot.get("files")
    if not isinstance(files, list) or not all(isinstance(item, dict) for item in files):
        missing.append("phase12_libbpf_snapshot_fixture:files")
        return

    tracked_file_count = snapshot.get("tracked_file_count")
    if tracked_file_count != len(files):
        missing.append("phase12_libbpf_snapshot_fixture:tracked_file_count")

    expected_paths = [
        "zigux/tests/phase12_libbpf_manifest.json",
        "zigux/tests/phase12_libbpf_segments.zig",
        "zigux/tests/phase12_libbpf_reviewability.zig",
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "tools/lib/bpf/zigux_segments/manifest.json",
    ]
    actual_paths = [entry.get("path") for entry in files]
    if actual_paths != expected_paths:
        missing.append("phase12_libbpf_snapshot_fixture:paths")
        return

    for entry, expected_path in zip(files, expected_paths):
        file_bytes = (ROOT / expected_path).read_bytes()
        if entry.get("bytes") != len(file_bytes):
            missing.append(f"phase12_libbpf_snapshot_fixture:bytes:{expected_path}")
        if entry.get("sha256") != hashlib.sha256(file_bytes).hexdigest():
            missing.append(f"phase12_libbpf_snapshot_fixture:sha256:{expected_path}")

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
phase12_libbpf_snapshot_fixture = json.loads(text(PHASE12_LIBBPF_SNAPSHOT_FIXTURE))
expected_build_test_names = build_inventory.get("build_test_names")
if not isinstance(expected_build_test_names, list) or not all(isinstance(item, str) for item in expected_build_test_names):
    missing.append("phase12_build_fixture:build_test_names")
else:
    actual_build_test_names = BUILD_TEST_NAME_RE.findall(build_text)
    if actual_build_test_names != expected_build_test_names:
        missing.append("phase12_build_fixture:build_test_names_mismatch")

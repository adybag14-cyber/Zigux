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
BUILD_RUN_ARTIFACT_RE = re.compile(r"const ([A-Za-z0-9_]+) = b\.addRunArtifact\(")
BUILD_STEP_RE = re.compile(r'b\.step\("([^"]+)",')
TEST_DECL_RE = re.compile(r'^\s*test\s*(?:"[^"]*"|\{)', re.M)
LOCAL_ZIG_IMPORT_RE = re.compile(r'@import\("([^"]+\.zig)"\)')

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
SURVEY_NOTE_MARKERS = {
    "phase12_libbpf_manifest.json": (
        "## Rollback And Reversible Delivery",
        "owner: `BPF Tooling Lane`",
        "rollback owner: `BPF Tooling Lane`",
        "fallback path: keep `tools/lib/bpf/libbpf.c` as the source of truth",
        "reversible delivery evidence: this Phase 12 packet only adds `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, and this survey note around preexisting helper foundations",
        "repair `scripts/zigux/check-phase12-libbpf-snapshot.py` plus `zigux/tests/fixtures/phase12_libbpf_snapshot.json` first",
        "phase12-libbpf-segment-survey-tests",
        "phase12-libbpf-reviewability-tests",
        "rollback drill: run `make -C zigux phase12-validate`",
        "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    ),
    "phase12_virtio_scsi_manifest.json": (
        "## Rollback And Reversible Delivery",
        "owner: `Storage Driver Lane`",
        "rollback owner: `Storage Driver Lane`",
        "fallback path: keep `drivers/scsi/virtio_scsi.c` as the source of truth",
        "phase12-virtio-scsi-tests",
        "phase12-virtio-scsi-survey-tests",
        "rollback drill: run `make -C zigux phase12-validate`",
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
        "lane_key": "P12-L01",
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
#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import json
import re
import sys
import tempfile


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
    "scripts/zigux/check-phase12-libbpf-packet.py",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "scripts/zigux/check-phase12-raw-github-coverage.py",
    "scripts/zigux/validate-phase12.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase12-shared-replay-contract.md",
    "zigux/tests/README.md",
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
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_nvme_pci.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_raw_github_coverage_survey.zig",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
]

MAKE_MARKERS = [
    "PHONY += phase12-validate phase12-test phase12",
    "phase12-validate:",
    "scripts/zigux/check-phase12-build-inventory.py --self-test",
    "scripts/zigux/check-phase12-build-inventory.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
    "scripts/zigux/check-phase12-libbpf-packet.py --self-test",
    "scripts/zigux/check-phase12-libbpf-packet.py",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "scripts/zigux/check-phase12-raw-github-coverage.py --self-test",
    "scripts/zigux/check-phase12-raw-github-coverage.py",
    "scripts/zigux/validate-phase12.py",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-validate phase12-test",
]
WORKFLOW_MARKERS = [
    "Validate Phase 12 degraded-workflow bundle",
    "make -C zigux phase12-validate",
    "Run Phase 12 complex driver tests",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    "check-phase12-libbpf-focused-replay.py --self-test",
    "check-phase12-libbpf-focused-replay.py",
]
README_MARKERS = [
    "check-phase12-build-inventory.py",
    "check-phase12-libbpf-snapshot.py",
    "check-phase12-libbpf-packet.py",
    "check-phase12-libbpf-focused-replay.py",
    "check-phase12-raw-github-coverage.py",
    "validate-phase12.py",
    "Phase 12 flow",
    "make -C zigux phase12-validate",
    "phase12_build_inventory.json",
    "phase12_raw_github_coverage_manifest.json",
    "phase12-raw-github-coverage-survey.md",
    "phase12_virtio_net_manifest.json",
    "phase12_nvme_pci_manifest.json",
    "phase12_virtio_scsi_manifest.json",
    "phase12_libbpf_manifest.json",
    "phase12_libbpf_only_build.zig",
    "shared build inventory snapshot",
    "phase12_libbpf_snapshot.json",
    "survey notes pinned to each manifest's exact `surveyed_commit`",
    "keep the roadmap-wide public-read split reviewable through the raw GitHub fallback coverage packet",
    "repeat-run and artifact-drift self-test",
    "focused libbpf-only replay hook",
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
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "the active Phase 12 network-driver survey packet now keeps the bounded `drivers/net/virtio_net.zig` probe snapshot, queue-recovery summary, queue-resume summary, `hdr_len`, receive-path, and mergeable-refill helpers visible from the top-level docs index",
    "the same top-level Phase 12 packet now also keeps the bounded `drivers/nvme/host/pci.zig` queue planner, PRP buffer-shape helper, and pointer-selection helper visible from the docs index",
    "the active Phase 12 storage-driver survey packet now keeps the bounded `drivers/scsi/virtio_scsi.zig` queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters visible from the top-level docs index",
    "the active Phase 12 heavy-helper survey packet now also keeps the bounded `tools/lib/bpf/zigux_segments/` helper foundations, the reproducibility snapshot, and the blocked object-model, loader, and relocation split visible from the top-level docs index",
    "`zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `tools/lib/bpf/zigux_segments/manifest.json`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-packet.py`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` now keep that same heavy-helper survey packet reviewable through the shared Phase 12 tranche",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "scripts/zigux/check-phase12-libbpf-packet.py",
    "`zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` now keep that same storage-driver survey packet reviewable through the shared Phase 12 tranche",
    "the same shared Phase 12 rollback-lab packet now also keeps the active rollback owners and C-anchor fallback path explicit at the docs root: `Network Driver Lane` owns the bounded `virtio_net` packet against `drivers/net/virtio_net.c`, `Storage Driver Lane` owns the bounded `nvme_pci` and `virtio_scsi` packets against `drivers/nvme/host/pci.c` and `drivers/scsi/virtio_scsi.c`, and `BPF Tooling Lane` owns the bounded libbpf helper packet against `tools/lib/bpf/libbpf.c`.",
    "reversible delivery remains limited to the bounded Zig starters, survey notes, review gates, and snapshot fixtures around those C anchors, and `make -C zigux phase12-validate` stays the shared rollback drill before `zig build test --build-file zigux/tests/phase12_build.zig --summary all` reruns the current Phase 12 tranche.",
]
CONTRACT_NOTE_MARKERS = [
    "The focused libbpf-only replay checker is intentionally part of that stack before the broader validator runs",
    "- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`",
    "- `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`",
]
TESTS_ROOT_README_MARKERS = [
    "keep `Documentation/zigux/phase12-shared-replay-contract.md`, `zigux/tests/phase12_build.zig`, `zigux/tests/phase12_libbpf_only_build.zig`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, and `zigux/tests/phase12_libbpf_manifest.json` aligned so the tests root names the same shared-versus-focused libbpf replay boundary as the docs-root contract note instead of leaving the dedicated shard implied behind the broader shared build inventory.",
]
TESTS_ROOT_README_EXACT_COUNTS = {
    TESTS_ROOT_README_MARKERS[0]: 1,
}
CHECKLIST_MARKERS = [
    "is there a stated rollback owner and fallback path?",
    "if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, the four Phase 12 manifests, and the four Phase 12 survey notes still agree on the same bounded tranche, exact surveyed commits, approved roadmap destinations, shared replay contract, and explicit DMA versus object-model blocker posture?",
    "if the change touches the shared Phase 12 degraded-workflow packet, do `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, `zigux/tests/phase12_raw_github_coverage_survey.zig`, `scripts/zigux/check-phase12-raw-github-coverage.py`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, and `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` still keep the roadmap-wide public-read split explicit, including the current one commit-pinned raw catalog, one archival raw map, and two shared-tree-only anchors, instead of implying equivalent commit-pinned fallback coverage for every Phase 12 anchor?",
    "if the change touches the shared Phase 12 degraded-workflow packet, do the workflow path, README notes, review checklist, and `zigux/tests/phase12_virtio_scsi_survey.zig` still agree that `make -C zigux phase12` runs the validator before the shared Zig replay?",
    "if the change touches the shared Phase 12 tooling path, do `scripts/zigux/check-phase12-build-inventory.py`, `zigux/tests/phase12_build.zig`, `zigux/tests/fixtures/phase12_build_inventory.json`, and the shared Phase 12 manifests still agree on the exact shared build inventory instead of leaving the replay shape implicit?",
    "if the change touches the shared Phase 12 libbpf snapshot packet, do `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and `tools/lib/bpf/zigux_segments/manifest.json` still agree on the same bounded five-file reproducibility packet, exact surveyed commit, and repeat-run-stable self-test contract instead of leaving the bounded libbpf snapshot discipline in run memory only?",
    "if the change touches the focused Phase 12 libbpf-only replay packet, do `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_libbpf_only_build.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree on the same dedicated replay shard, review-note hook, and validator-first rollback path instead of leaving that narrower libbpf gate implied behind the broader packet checks?",
]
CHECKLIST_EXACT_COUNTS = {
    "if the change touches the focused Phase 12 libbpf-only replay packet, do `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_libbpf_only_build.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree on the same dedicated replay shard, review-note hook, and validator-first rollback path instead of leaving that narrower libbpf gate implied behind the broader packet checks?": 1,
}
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
    "phase12_virtio_net_manifest.json": (
        "## Rollback And Reversible Delivery",
        "owner: `Network Driver Lane`",
        "rollback owner: `Network Driver Lane`",
        "fallback path: keep `drivers/net/virtio_net.c` as the source of truth",
        "phase12-virtio-net-tests",
        "phase12-virtio-net-survey-tests",
        "phase12-virtio-net-syntax-lab-tests",
        "rollback drill: run `make -C zigux phase12-validate`",
        "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    ),
    "phase12_nvme_pci_manifest.json": (
        "## Rollback And Reversible Delivery",
        "owner: `Storage Driver Lane`",
        "rollback owner: `Storage Driver Lane`",
        "fallback path: keep `drivers/nvme/host/pci.c` as the source of truth",
        "phase12-nvme-pci-tests",
        "phase12-nvme-pci-survey-tests",
        "rollback drill: run `make -C zigux phase12-validate`",
        "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    ),
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
    "phase12-virtio-net-syntax-lab-tests",
    "phase12-virtio-scsi-syntax-lab-tests",
    "phase12-virtio-scsi-tests",
    "phase12-virtio-scsi-survey-tests",
    "phase12-raw-github-coverage-survey-tests",
    "phase12-libbpf-segment-survey-tests",
    "phase12-libbpf-reviewability-tests",
    "test_step.dependOn(&run_phase12_nvme_pci_tests.step);",
    "test_step.dependOn(&run_phase12_nvme_pci_survey_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_net_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_net_survey_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_net_syntax_lab_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_scsi_syntax_lab_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_scsi_tests.step);",
    "test_step.dependOn(&run_phase12_virtio_scsi_survey_tests.step);",
    "test_step.dependOn(&run_phase12_raw_github_coverage_survey_tests.step);",
    "test_step.dependOn(&run_phase12_libbpf_segments_tests.step);",
    "test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);",
]
FORBIDDEN_BUILD_MARKERS: list[str] = []
BUILD_INVENTORY_FIXTURE = "zigux/tests/fixtures/phase12_build_inventory.json"
PHASE12_LIBBPF_SNAPSHOT_FIXTURE = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
SELF_TEST_SOURCE_MARKERS = [
    'def run_self_test() -> int:',
    'if "--self-test" in sys.argv[1:]:',
    'PHASE12_VALIDATOR_SELF_TEST=pass',
    'PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT=5',
]

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
        "gap_count": 13,
        "roadmap_destinations": ["drivers/nvme/host/pci.zig", "zigux/tests/", "Documentation/zigux/"],
        "shared_allowed_destinations": {
            "zigux/Makefile",
            "drivers/net/virtio_net.zig",
            "drivers/scsi/virtio_scsi.zig",
        },
        "allowed_statuses": {"starter_landed", "blocked_on_dma_transport"},
        "expected_status_totals": {"starter_landed": 12, "blocked_on_dma_transport": 1},
        "survey_path": "zigux/tests/phase12_nvme_pci_survey.zig",
        "survey_note_path": "Documentation/zigux/phase12-nvme-pci-survey.md",
        "survey_count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_dma_transport")],
    },
    "phase12_virtio_scsi_manifest.json": {
        "lane_key": "P12-L12",
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
            "zigux/tests/phase12_virtio_scsi_survey.zig",
            "zigux/tests/phase12_virtio_scsi_manifest.json",
            "Documentation/zigux/phase12-virtio-scsi-survey.md",
            "Documentation/zigux/phase12-virtio-scsi-slice.md",
        ],
        "raw_fallback_raw_paths": [
            "drivers/scsi/virtio_scsi.c",
            "drivers/scsi/scsi_debug.c",
        ],
        "raw_fallback_current_markers": [
            "current direct fallback coverage remains intentionally narrow",
            "shared-tree-only fallback anchors for the phase docs root and tests root",
            "the current active coverage stays limited to one commit-pinned raw catalog for `drivers/scsi/virtio_scsi.c` and one archival commit-pinned fallback map for `drivers/nvme/host/pci.c`",
            "no commit-pinned raw fallback is claimed for `drivers/net/virtio_net.c` or `tools/lib/bpf/libbpf.c`",
        ],
        "raw_fallback_latest_recheck_markers": [
            "latest raw fallback recheck",
            "still no raw fallback coverage claim for `drivers/net/virtio_net.c` or `tools/lib/bpf/libbpf.c`",
            "the storage packet remains anchored to one current commit-pinned raw catalog and one archival nvme map only",
        ],
        "raw_fallback_rollback_markers": [
            "## Rollback And Reversible Delivery",
            "owner: `Storage Driver Lane`",
            "rollback owner: `Storage Driver Lane`",
            "fallback path: keep `drivers/scsi/virtio_scsi.c` as the source of truth",
            "phase12-virtio-scsi-tests",
            "phase12-virtio-scsi-survey-tests",
            "rollback drill: run `python3 scripts/zigux/validate-phase12.py`",
            "make -C zigux phase12-validate",
            "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
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

def read_text(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def validate_self_test_surface(source_text: str, manifest_specs: dict[str, object]) -> list[str]:
    missing: list[str] = []
    for marker in SELF_TEST_SOURCE_MARKERS:
        if marker not in source_text:
            missing.append(f"validator_source:{marker}")

    focused_replay_marker = CHECKLIST_MARKERS[-1]
    focused_replay_count = source_text.count(focused_replay_marker)
    if focused_replay_count != 1:
        missing.append(
            "validator_source_count:"
            f"{focused_replay_marker}:expected=1:actual={focused_replay_count}"
        )

    nvme_spec = manifest_specs.get("phase12_nvme_pci_manifest.json")
    if not isinstance(nvme_spec, dict) or nvme_spec.get("lane_key") != "P12-L08":
        missing.append("validator_source:phase12_nvme_pci_manifest.json:lane_key=P12-L08")

    return missing


def expect_self_test_missing(
    label: str,
    source_text: str,
    manifest_specs: dict[str, object],
    expected_marker: str,
) -> None:
    missing = validate_self_test_surface(source_text, manifest_specs)
    if expected_marker not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase12-validator-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    source_text = Path(__file__).read_text(encoding="utf-8")
    baseline_missing = validate_self_test_surface(source_text, MANIFEST_SPECS)
    if baseline_missing:
        raise SystemExit(
            "phase12-validator-self-test:baseline_failed:"
            f"{','.join(baseline_missing)}"
        )

    expect_self_test_missing(
        "pass_token",
        source_text.replace("PHASE12_VALIDATOR_SELF_TEST=pass", "PHASE12_VALIDATOR_SELF_TEST=drift", 1),
        MANIFEST_SPECS,
        "validator_source:PHASE12_VALIDATOR_SELF_TEST=pass",
    )

    expect_self_test_missing(
        "case_count_token",
        source_text.replace(
            "PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT=5",
            "PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT=6",
            1,
        ),
        MANIFEST_SPECS,
        "validator_source:PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT=5",
    )

    expect_self_test_missing(
        "entrypoint_guard",
        source_text.replace(
            'if "--self-test" in sys.argv[1:]:',
            'if "--phase12-self-test" in sys.argv[1:]:',
            1,
        ),
        MANIFEST_SPECS,
        'validator_source:if "--self-test" in sys.argv[1:]:',
    )

    expect_self_test_missing(
        "focused_replay_duplicate_review_hook",
        source_text + "\n" + CHECKLIST_MARKERS[-1],
        MANIFEST_SPECS,
        "validator_source_count:"
        f"{CHECKLIST_MARKERS[-1]}:expected=1:actual=2",
    )

    drifted_manifest_specs = json.loads(json.dumps(MANIFEST_SPECS))
    drifted_manifest_specs["phase12_nvme_pci_manifest.json"]["lane_key"] = "P12-L05"
    expect_self_test_missing(
        "nvme_lane_key",
        source_text,
        drifted_manifest_specs,
        "validator_source:phase12_nvme_pci_manifest.json:lane_key=P12-L08",
    )

    print("PHASE12_VALIDATOR_SELF_TEST=pass")
    print("PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT=5")
    return 0


def text(path: str) -> str:
    return read_text(ROOT, path)


def load_manifest(name: str) -> dict[str, object]:
    return json.loads(text(f"zigux/tests/{name}"))


def count_transitive_tests(path: Path, seen: set[Path]) -> int:
    resolved_path = path.resolve()
    if resolved_path in seen:
        return 0
    seen.add(resolved_path)

    source = resolved_path.read_text(encoding="utf-8")
    total = len(TEST_DECL_RE.findall(source))
    for import_path in LOCAL_ZIG_IMPORT_RE.findall(source):
        child_path = (resolved_path.parent / import_path).resolve()
        if ROOT not in child_path.parents:
            continue
        if not child_path.is_file():
            continue
        total += count_transitive_tests(child_path, seen)
    return total


def derive_expected_step_count(build_text: str) -> int:
    return (
        len(BUILD_TEST_NAME_RE.findall(build_text))
        + len(BUILD_RUN_ARTIFACT_RE.findall(build_text))
        + len(BUILD_STEP_RE.findall(build_text))
    )


def derive_expected_test_count(
    test_root_modules: list[dict[str, str]],
    module_root_source_files: list[dict[str, str]],
) -> int:
    module_paths = {
        entry["module"]: (ROOT / "zigux/tests" / entry["path"]).resolve()
        for entry in module_root_source_files
    }
    seen: set[Path] = set()
    total = 0
    for entry in test_root_modules:
        total += count_transitive_tests(module_paths[entry["root_module"]], seen)
    return total


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


def collect_exact_count_misses(text: str, expected_counts: dict[str, int], prefix: str) -> list[str]:
    missing: list[str] = []
    for marker, expected_count in expected_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{prefix}:{marker}:expected={expected_count}:actual={actual_count}")
    return missing


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


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


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
    ("contract_note", text("Documentation/zigux/phase12-shared-replay-contract.md"), CONTRACT_NOTE_MARKERS),
    ("tests_root_readme", text("zigux/tests/README.md"), TESTS_ROOT_README_MARKERS),
    ("review_checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
    ("phase12_build", text("zigux/tests/phase12_build.zig"), BUILD_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

missing.extend(
    collect_exact_count_misses(
        text("Documentation/zigux/review-checklist.md"),
        CHECKLIST_EXACT_COUNTS,
        "review_checklist_count",
    )
)
missing.extend(
    collect_exact_count_misses(
        text("zigux/tests/README.md"),
        TESTS_ROOT_README_EXACT_COUNTS,
        "tests_root_readme_count",
    )
)

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

expected_depend_steps = build_inventory.get("shared_test_depend_steps")
if not isinstance(expected_depend_steps, list) or not all(isinstance(item, str) for item in expected_depend_steps):
    missing.append("phase12_build_fixture:shared_test_depend_steps")
else:
    actual_depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
    if actual_depend_steps != expected_depend_steps:
        missing.append("phase12_build_fixture:shared_test_depend_steps_mismatch")

expected_module_roots = build_inventory.get("module_root_source_files")
if not isinstance(expected_module_roots, list) or not all(isinstance(item, dict) for item in expected_module_roots):
    missing.append("phase12_build_fixture:module_root_source_files")
else:
    actual_module_roots = [
        {"module": module_name, "path": root_path}
        for module_name, root_path in BUILD_MODULE_RE.findall(build_text)
    ]
    if actual_module_roots != expected_module_roots:
        missing.append("phase12_build_fixture:module_root_source_files_mismatch")

expected_module_imports = build_inventory.get("module_imports")
if not isinstance(expected_module_imports, list) or not all(isinstance(item, dict) for item in expected_module_imports):
    missing.append("phase12_build_fixture:module_imports")
else:
    actual_module_imports = [
        {
            "module": module_name,
            "import_name": import_name,
            "imported_module": imported_module,
        }
        for module_name, import_name, imported_module in BUILD_IMPORT_RE.findall(build_text)
    ]
    if actual_module_imports != expected_module_imports:
        missing.append("phase12_build_fixture:module_imports_mismatch")

expected_test_root_modules = build_inventory.get("test_root_modules")
if not isinstance(expected_test_root_modules, list) or not all(isinstance(item, dict) for item in expected_test_root_modules):
    missing.append("phase12_build_fixture:test_root_modules")
else:
    actual_test_root_modules = [
        {"test": test_name, "root_module": root_module}
        for test_name, root_module in BUILD_TEST_ROOT_MODULE_RE.findall(build_text)
    ]
    if actual_test_root_modules != expected_test_root_modules:
        missing.append("phase12_build_fixture:test_root_modules_mismatch")

expected_step_count = build_inventory.get("expected_step_count")
if not isinstance(expected_step_count, int):
    missing.append("phase12_build_fixture:expected_step_count")
else:
    actual_expected_step_count = derive_expected_step_count(build_text)
    if expected_step_count != actual_expected_step_count:
        missing.append("phase12_build_fixture:expected_step_count_mismatch")

expected_test_count = build_inventory.get("expected_test_count")
if not isinstance(expected_test_count, int):
    missing.append("phase12_build_fixture:expected_test_count")
elif (
    isinstance(expected_test_root_modules, list)
    and all(isinstance(item, dict) for item in expected_test_root_modules)
    and isinstance(expected_module_roots, list)
    and all(isinstance(item, dict) for item in expected_module_roots)
):
    actual_expected_test_count = derive_expected_test_count(expected_test_root_modules, expected_module_roots)
    if expected_test_count != actual_expected_test_count:
        missing.append("phase12_build_fixture:expected_test_count_mismatch")

expected_summary_line = build_inventory.get("expected_summary_line")
if not isinstance(expected_summary_line, str):
    missing.append("phase12_build_fixture:expected_summary_line")
elif isinstance(expected_step_count, int) and isinstance(expected_test_count, int):
    actual_expected_summary_line = (
        f"Build Summary: {expected_step_count}/{expected_step_count} steps succeeded; "
        f"{expected_test_count}/{expected_test_count} tests passed"
    )
    if expected_summary_line != actual_expected_summary_line:
        missing.append("phase12_build_fixture:expected_summary_line_mismatch")

for key, expected_value in [
    ("forbidden_markers", FORBIDDEN_BUILD_MARKERS),
    ("dedicated_survey_replays", []),
]:
    value = build_inventory.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        missing.append(f"phase12_build_fixture:{key}")
    elif value != expected_value:
        missing.append(f"phase12_build_fixture:{key}_mismatch")

packet_sources = {
    "phase12_virtio_net_test": text("zigux/tests/phase12_virtio_net.zig"),
    "phase12_virtio_net_survey": text("Documentation/zigux/phase12-virtio-net-survey.md"),
    "phase12_nvme_pci_test": text("zigux/tests/phase12_nvme_pci.zig"),
    "phase12_nvme_pci_slice": text("Documentation/zigux/phase12-nvme-pci-slice.md"),
    "phase12_virtio_scsi_test": text("zigux/tests/phase12_virtio_scsi.zig"),
    "phase12_virtio_scsi_slice": text("Documentation/zigux/phase12-virtio-scsi-slice.md"),
}
for source_name, markers in PHASE12_PACKET_MARKERS.items():
    source_text = packet_sources[source_name]
    for marker in markers:
        if marker not in source_text:
            missing.append(f"{source_name}:{marker}")

starter_total = 0
ready_total = 0
blocked_total = 0
deferred_total = 0
raw_fallback_total = 0

for manifest_name, spec in MANIFEST_SPECS.items():
    manifest = load_manifest(manifest_name)
    if manifest.get("lane_key") != spec["lane_key"]:
        missing.append(f"{manifest_name}:lane_key")
    if manifest.get("phase") != "Phase 12":
        missing.append(f"{manifest_name}:phase")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
        missing.append(f"{manifest_name}:surveyed_commit")
    if manifest.get("anchor") != spec["anchor"]:
        missing.append(f"{manifest_name}:anchor")

    roadmap_destinations = manifest.get("roadmap_destinations")
    if roadmap_destinations != spec["roadmap_destinations"]:
        missing.append(f"{manifest_name}:roadmap_destinations")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append(f"{manifest_name}:gaps")
        continue
    if len(gaps) != spec["gap_count"]:
        missing.append(f"{manifest_name}:gap_count")

    survey_text = text(spec["survey_path"])
    survey_note_text = text(spec["survey_note_path"])
    if not isinstance(surveyed_commit, str) or surveyed_commit not in survey_note_text:
        missing.append(f"{manifest_name}:survey_note:surveyed_commit")
    for marker in SURVEY_NOTE_MARKERS.get(manifest_name, ()):
        if marker not in survey_note_text:
            missing.append(f"{manifest_name}:survey_note:{marker}")

    for count_marker, status_name in spec["survey_count_markers"]:
        count = count_statuses(manifest, status_name)
        expected_line = f"try std.testing.expectEqual(@as(usize, {count}), {count_marker});"
        if expected_line not in survey_text:
            missing.append(f"{manifest_name}:{count_marker}")

    status_totals = spec["expected_status_totals"]
    for status_name, expected_total in status_totals.items():
        actual_total = count_statuses(manifest, status_name)
        if actual_total != expected_total:
            missing.append(f"{manifest_name}:status_total:{status_name}")

    for index, gap in enumerate(gaps):
        if not isinstance(gap, dict):
            missing.append(f"{manifest_name}:gap:{index}")
            continue
        gap_id = gap.get("id")
        status = gap.get("status")
        kind = gap.get("kind")
        destination = gap.get("zigux_destination")
        why_now = gap.get("why_now")
        if not isinstance(gap_id, str) or not gap_id:
            missing.append(f"{manifest_name}:gap_id:{index}")
        if not isinstance(status, str) or status not in spec["allowed_statuses"]:
            missing.append(f"{manifest_name}:status:{gap_id or index}")
        if not isinstance(kind, str) or not kind:
            missing.append(f"{manifest_name}:kind:{gap_id or index}")
        if not isinstance(destination, str) or not destination_allowed(destination, spec):
            missing.append(f"{manifest_name}:destination:{gap_id or index}")
        if not isinstance(why_now, str) or not why_now:
            missing.append(f"{manifest_name}:why_now:{gap_id or index}")

    starter_total += count_statuses(manifest, "starter_landed")
    ready_total += count_statuses(manifest, "ready_next")
    blocked_total += count_statuses(manifest, "blocked_on_dma_transport")
    blocked_total += count_statuses(manifest, "blocked_on_object_model")
    deferred_total += count_statuses(manifest, "deferred_high_risk")

    raw_fallback_catalog_path = spec.get("raw_fallback_catalog_path")
    if isinstance(raw_fallback_catalog_path, str):
        raw_fallback_total += 1
        catalog_text = text(raw_fallback_catalog_path)
        if not isinstance(surveyed_commit, str) or surveyed_commit not in catalog_text:
            missing.append(f"{manifest_name}:raw_fallback_catalog:surveyed_commit")
        for url in spec.get("raw_fallback_tree_urls", []):
            expect_catalog_marker(catalog_text, str(url), f"{manifest_name}:raw_fallback_tree:{url}", missing)
        for path in spec.get("raw_fallback_artifact_paths", []):
            expect_catalog_marker(catalog_text, str(path), f"{manifest_name}:raw_fallback_artifact:{path}", missing)
        for raw_path in spec.get("raw_fallback_raw_paths", []):
            if not isinstance(surveyed_commit, str):
                break
            raw_url = f"https://raw.githubusercontent.com/adybag14-cyber/Zigux/{surveyed_commit}/{raw_path}"
            expect_catalog_marker(catalog_text, raw_url, f"{manifest_name}:raw_fallback_raw:{raw_path}", missing)
        for marker in spec.get("raw_fallback_rollback_markers", []):
            expect_catalog_marker(catalog_text, str(marker), f"{manifest_name}:raw_fallback_rollback:{marker}", missing)
        for marker in spec.get("raw_fallback_current_markers", []):
            expect_catalog_marker(catalog_text, str(marker), f"{manifest_name}:raw_fallback_current:{marker}", missing)
        for marker in spec.get("raw_fallback_latest_recheck_markers", []):
            expect_catalog_marker(catalog_text, str(marker), f"{manifest_name}:raw_fallback_latest_recheck:{marker}", missing)

expect_libbpf_snapshot_fixture(
    phase12_libbpf_snapshot_fixture,
    load_manifest("phase12_libbpf_manifest.json"),
    missing,
)

if missing:
    print("PHASE12_VALIDATION=fail")
    print("PHASE12_VALIDATION_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE12_VALIDATION_MISSING_END")
    sys.exit(1)

print("PHASE12_VALIDATION=pass")
print(f"PHASE12_REQUIRED_FILE_COUNT={len(FILES)}")
print(f"PHASE12_SHARED_BUILD_TEST_COUNT={len(expected_build_test_names)}")
print(f"PHASE12_SHARED_BUILD_DEPEND_STEP_COUNT={len(expected_depend_steps)}")
print(f"PHASE12_SHARED_BUILD_MODULE_ROOT_COUNT={len(expected_module_roots)}")
print(f"PHASE12_SHARED_BUILD_IMPORT_COUNT={len(expected_module_imports)}")
print(f"PHASE12_SHARED_BUILD_TEST_ROOT_COUNT={len(expected_test_root_modules)}")
print(f"PHASE12_STARTER_STATUS_COUNT={starter_total}")
print(f"PHASE12_READY_NEXT_STATUS_COUNT={ready_total}")
print(f"PHASE12_BLOCKED_STATUS_COUNT={blocked_total}")
print(f"PHASE12_DEFERRED_STATUS_COUNT={deferred_total}")
print(f"PHASE12_RAW_FALLBACK_CATALOG_COUNT={raw_fallback_total}")
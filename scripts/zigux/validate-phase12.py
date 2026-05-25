#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
PHASE12_COMPLEX_DRIVER_LANE_PATH = (
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
)
PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH = (
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
)
VIRTIO_NET_SURVEY_PATH = "Documentation/zigux/phase12-virtio-net-survey.md"
VIRTIO_SCSI_FALLBACK_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
VIRTIO_SCSI_SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
VIRTIO_SCSI_SURVEY_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
NVME_FALLBACK_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
NVME_REOPEN_GOVERNANCE_PATH = (
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md"
)
NVME_SLICE_PATH = "Documentation/zigux/phase12-nvme-pci-slice.md"
NVME_SURVEY_PATH = "Documentation/zigux/phase12-nvme-pci-survey.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
COMPLEX_DRIVER_LANE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-complex-driver-lane-packet.py"
)
LIBBPF_SNAPSHOT_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-snapshot.py"
LIBBPF_LANE_MARKER_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-lane-marker.py"
LIBBPF_SEGMENT_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
LIBBPF_SEGMENT_GATE_PATH = "zigux/tests/phase12_libbpf_segments.zig"
HEAVY_CONSUMER_PACKET_CHECKER_PATH = (
    "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py"
)
VIRTIO_NET_PACKET_CHECKER_PATH = "scripts/zigux/check-phase12-virtio-net-packet.py"
VIRTIO_SCSI_PACKET_CHECKER_PATH = "scripts/zigux/check-phase12-virtio-scsi-packet.py"
VIRTIO_SCSI_BOUNDARY_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py"
)
VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-scsi-rollback-coverage.py"
)
VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-scsi-repeated-rollback-packet.py"
)
NVME_PACKET_CHECKER_PATH = "scripts/zigux/check-phase12-nvme-pci-packet.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
VIRTIO_NET_MANIFEST_PATH = "zigux/tests/phase12_virtio_net_manifest.json"
VIRTIO_SCSI_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
VIRTIO_SCSI_SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
VIRTIO_SCSI_SUPPORT_MANIFEST_PATH = (
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"
)
LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
LIBBPF_SNAPSHOT_DETERMINISM_PATH = (
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
)
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

# Keep the shared validator fail-closed against the returned Phase 12 packet
# guards it already names, without widening into blocked transport behavior.
PHASE12_PACKET_CHECKERS = (
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    COMPLEX_DRIVER_LANE_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    HEAVY_CONSUMER_PACKET_CHECKER_PATH,
    NVME_PACKET_CHECKER_PATH,
    VIRTIO_NET_PACKET_CHECKER_PATH,
    VIRTIO_SCSI_PACKET_CHECKER_PATH,
)

# Keep the shared Phase 12 validator scoped to stable support-surface wording.
# Exact blob pins in the raw-coverage note belong to the neighboring fallback lane.
RAW_GITHUB_BRIDGE_MARKERS = [
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`scripts/zigux/validate-phase12.py`",
    "`scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`scripts/zigux/README.md`",
    "`zigux/Makefile`",
    "`zigux/tests/phase12_build.zig`",
]

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    FREEZE_MAP_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_PATH,
    PHASE12_COMPLEX_DRIVER_LANE_PATH,
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH,
    VIRTIO_NET_SURVEY_PATH,
    VIRTIO_SCSI_FALLBACK_PATH,
    VIRTIO_SCSI_SLICE_PATH,
    VIRTIO_SCSI_SURVEY_PATH,
    NVME_FALLBACK_PATH,
    NVME_REOPEN_GOVERNANCE_PATH,
    NVME_SLICE_PATH,
    NVME_SURVEY_PATH,
    SCRIPTS_README_PATH,
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    COMPLEX_DRIVER_LANE_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    LIBBPF_SEGMENT_SURVEY_PATH,
    LIBBPF_SEGMENT_GATE_PATH,
    HEAVY_CONSUMER_PACKET_CHECKER_PATH,
    VIRTIO_NET_PACKET_CHECKER_PATH,
    VIRTIO_SCSI_PACKET_CHECKER_PATH,
    VIRTIO_SCSI_BOUNDARY_CHECKER_PATH,
    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH,
    VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH,
    NVME_PACKET_CHECKER_PATH,
    VALIDATOR_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    VIRTIO_NET_MANIFEST_PATH,
    VIRTIO_SCSI_MANIFEST_PATH,
    VIRTIO_SCSI_SURVEY_GATE_PATH,
    VIRTIO_SCSI_SUPPORT_MANIFEST_PATH,
    LIBBPF_SNAPSHOT_PATH,
    LIBBPF_SNAPSHOT_DETERMINISM_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof",
        "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
    ],
    TESTS_README_PATH: [
        "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
        "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
        "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while still keeping the validator-first support packet distinct from deeper driver-delivery claims.",
        "the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`",
        "`scripts/zigux/check-build-only-phase12-surface.py` remains the bounded build-only contract checker",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again, so this sequencing note should treat that validator-first then smoke-first wrapper set as shipped current-`master` evidence beside the directly readable rerun surfaces `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.",
        "the directly readable rerun surfaces in the shared packet are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.",
        "Keep the degraded-workflow validator-side support bundle explicit beside that same order too:",
        "`Documentation/zigux/phase12-nvme-pci-reopen-governance.md` owner-map companion outside the wired shared release route",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
        "Do not invent a focused libbpf-only replay, a cross-build replay, or another unshipped closure route while using the degraded path.",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
        "the shipped packet-local `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py` guard",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "- exact coverage evidence checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `24946f6a72b3b67faa6be4d54ed09d59518fa210`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `9d437058691bec8c7db0ca72422430c52b5a5e8f`, `scripts/zigux/validate-phase12.py` `cfd57eeff2d705fc4f02a9a85a3e1763c19a17f2`, `scripts/zigux/check-phase12-release-readiness-packet.py` `6989a61948e2e5d585275fba3af4fbecbe743b78`, `.github/workflows/zigux-bootstrap.yml` `f72787f799d497897122b86ddc65fd1ada31d77e`, `scripts/zigux/README.md` `5aff90b361628405898c7e83766acb43bcc4ef54`, `zigux/Makefile` `adcb33fc7dd30009e24210b2c44e3412427854fb`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`",
        "- exact runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `30f30f327e8205a667d1b843c1dbd69a09beef17` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
        *RAW_GITHUB_BRIDGE_MARKERS,
        "keep the directly readable build-only checker, release-readiness checker, workflow, scripts-root README, current Makefile, and current `zigux/tests/phase12_build.zig` as bounded reminder evidence only",
        "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`, so `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are current wrapper proof on `master`.",
        "The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
        "The readable build file currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` through the shared `smoke` and `test` steps, and the readable Makefile now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`, so that checker-plus-validator-plus-workflow-plus-scripts-plus-Makefile-plus-build-file set stays direct support evidence only rather than proof for the larger starter-present `virtio_net`, rollback-lab `virtio_scsi`, or driver-local NVMe packet.",
    ],
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: [
        "Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, and the helper-local `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` determinism companion, while treating the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as parked note-owned boundaries until they land again on current `master`, while keeping `tools/lib/bpf/zigux_segments/verify.zig` explicit as the directly readable compile-together shard for the current helper footing, and while keeping `tools/lib/bpf/zigux_segments/manifest.json` explicit as the directly readable helper-first packet catalog rather than as proof of a shipped shared replay route.",
        "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, so keep `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` explicit here as shipped wrapper evidence and keep the directly readable support bundle explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `scripts/zigux/validate-phase12.py` beside the returned smoke-and-test wrappers.",
        "The shipped heavy-consumer guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
        "The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.",
    ],
    VIRTIO_NET_SURVEY_PATH: [
        "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
        "lane owner: `P12-L04`",
        "`zigux/tests/phase12_build.zig` plus `zigux/Makefile` now keep the dedicated `virtio_net_queue_resume`, `virtio_net_receive_refill_replay`, `virtio_net_transmit_recycle`, `virtio_net_post_reset_replay`, throughput-parity, and `phase12_virtio_net_survey` gates reachable through the shared Phase 12 validate, smoke, and test routes",
        "the throughput helper remains review-only throughput-ratio checks, but now also surfaces explicit receive-refill and transmit-recycle readiness booleans rather than measured transport throughput evidence",
        "the shared Phase 12 build route includes the queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate replays, and current `zigux/Makefile` now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`",
        "the packet still does not claim live DMA-safe receive ownership, page-pool wiring, refill execution, transport-backed submit flow, interrupt-backed completion handling, or full `net_device` lifecycle parity",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`",
        "- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`",
        "- survey gate: `scripts/zigux/check-phase12-virtio-scsi-packet.py`",
        "- `scripts/zigux/validate-phase12.py`",
        "- `.github/workflows/zigux-bootstrap.yml` now replays the current shared Phase 12 support bundle and adjacent shared reruns in the exact order `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test`, `python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test`, `python3 scripts/zigux/check-phase12-cross-compile-smoke.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
        "- exact current shared support-bundle and replay order is `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
        "- `make -C zigux phase12-validate` is current repo evidence again and now reruns the shared build-only, complex-driver, cross-compile smoke, release-readiness, libbpf snapshot, libbpf heavy-consumer, and `virtio_net` packet checkers plus `scripts/zigux/validate-phase12.py`",
        "current authoritative packet truth therefore lives in the rollback-evidence survey companions on `master`",
    ],
    VIRTIO_SCSI_SURVEY_PATH: [
        "PHASE12_STATUS=rollback-evidence-only-live-starter-missing",
        "PHASE12_LANE=P12-L09",
        "fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "still does not claim live DMA-safe request submission",
        "rollback-only split machine-checkable",
        "reversible-delivery evidence: current `master` preserves the survey note, fixture manifest, survey manifest, survey gate, checker, shared build bundle, and `zigux/Makefile` as rollback evidence while the driver-local starter and replay gates remain absent",
    ],
    VIRTIO_NET_PACKET_CHECKER_PATH: [
        "PHASE12_VIRTIO_NET_PACKET_SELF_TEST=pass",
        "Documentation/zigux/phase12-virtio-net-survey.md",
        "zigux/tests/phase12_virtio_net_manifest.json",
        "zigux/tests/phase12_build.zig",
        "phase12_virtio_net_post_reset_replay.zig",
        "phase12-virtio-net-post-reset-replay-tests",
    ],
    HEAVY_CONSUMER_PACKET_CHECKER_PATH: [
        "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass",
        "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
        "scripts/zigux/check-phase12-libbpf-snapshot.py",
    ],
    LIBBPF_SEGMENT_SURVEY_PATH: [
        "PHASE12_LANE_KEY=P12-L16",
    ],
    LIBBPF_SEGMENT_GATE_PATH: [
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "PHASE12_LANE_KEY=P12-L16",
        "try std.testing.expectEqualStrings(\"P12-L16\", manifest.lane_key);",
    ],
    VIRTIO_NET_MANIFEST_PATH: [
        "\"lane_key\": \"P12-L04\"",
        "\"phase\": \"Phase 12\"",
        "\"anchor\": \"drivers/net/virtio_net.c\"",
        "\"roadmap_gap_check\"",
        "\"status\": \"split_queue_resume_receive_refill_transmit_recycle_post_reset_replay_and_direct_gates_present_shared_smoke_present\"",
        "\"status\": \"throughput_parity_helper_present_review_only_runtime_completion_missing\"",
        "\"status\": \"split_helper_packet_direct_replays_and_survey_gate_present_shared_route_sextet_complete\"",
        "\"id\": \"phase12-build-gate\"",
        "\"status\": \"shared_build_present_with_queue_resume_receive_refill_transmit_recycle_post_reset_throughput_and_survey_gate_replays\"",
        "\"id\": \"phase12-virtio-net-survey-gate\"",
        "\"zigux_destination\": \"zigux/tests/phase12_virtio_net_survey.zig\"",
        "\"id\": \"phase12-virtio-net-runtime-data-path\"",
        "\"status\": \"blocked_on_dma_transport_runtime\"",
    ],
    VIRTIO_SCSI_MANIFEST_PATH: [
        "\"lane_key\": \"P12-L09\"",
        "\"phase\": \"Phase 12\"",
        "\"anchor\": \"drivers/scsi/virtio_scsi.c\"",
        "\"roadmap_gap_check\"",
        "\"phase12-virtio-scsi-runtime-request-flow\"",
    ],
    VIRTIO_SCSI_SURVEY_GATE_PATH: [
        "test \"phase12 virtio scsi survey manifest keeps the rollback-only packet truthful\"",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        "scripts/zigux/check-phase12-virtio-scsi-packet.py",
    ],
    NVME_FALLBACK_PATH: [
        "`PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`",
        "- starter shard: `drivers/nvme/host/pci.zig`",
        "- verifier shard: `drivers/nvme/host/pci_verify.zig`",
        "- direct replay: `zigux/tests/phase12_nvme_pci.zig`",
        "- survey gate: `zigux/tests/phase12_nvme_pci_survey.zig`",
        "- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`",
        "- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes",
    ],
    MAKEFILE_PATH: [
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
        "phase3: phase3-validate",
        "phase10: phase10-validate phase10-test",
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH: [
        "PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=pass",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "zigux/tests/phase12_virtio_scsi_survey.zig",
        "zigux/tests/phase12_build.zig",
    ],
    VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH: [
        "PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=pass",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "zigux/tests/phase12_build.zig",
        "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    ],
    VALIDATOR_PATH: [
        BUILD_ONLY_CHECKER_PATH,
        RELEASE_READINESS_CHECKER_PATH,
        COMPLEX_DRIVER_LANE_CHECKER_PATH,
        LIBBPF_SNAPSHOT_CHECKER_PATH,
        LIBBPF_LANE_MARKER_CHECKER_PATH,
        LIBBPF_SEGMENT_SURVEY_PATH,
        LIBBPF_SEGMENT_GATE_PATH,
        HEAVY_CONSUMER_PACKET_CHECKER_PATH,
        VIRTIO_NET_PACKET_CHECKER_PATH,
        VIRTIO_SCSI_PACKET_CHECKER_PATH,
        VIRTIO_SCSI_BOUNDARY_CHECKER_PATH,
        VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH,
        VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH,
        NVME_PACKET_CHECKER_PATH,
        VIRTIO_NET_MANIFEST_PATH,
        VIRTIO_SCSI_MANIFEST_PATH,
        VIRTIO_SCSI_SURVEY_GATE_PATH,
        "PHASE12_VALIDATOR_SELF_TEST=pass",
        "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass",
        "PHASE12_LIBBPF_LANE_MARKER_SELF_TEST=pass",
        "make -C zigux phase12-validate",
        "scripts-side support packet",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 build-only surface checker",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Check current Phase 12 build-only surface",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py",
        "- name: Self-test current Phase 12 complex-driver lane packet checker",
        "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
        "- name: Check current Phase 12 complex-driver lane packet",
        "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py",
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Check current Phase 12 release-readiness packet",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
        "- name: Self-test current Phase 12 libbpf snapshot checker",
        "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
        "- name: Check current Phase 12 libbpf snapshot packet",
        "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
        "- name: Self-test current Phase 12 libbpf heavy-consumer packet checker",
        "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
        "- name: Check current Phase 12 libbpf heavy-consumer packet",
        "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
        "- name: Validate current Phase 12 support bundle",
        "run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 smoke packet",
        "run: make -C zigux phase12-smoke",
        "- name: Run current Phase 12 shared test packet",
        "run: make -C zigux phase12-test",
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
        "- name: Run current Phase 12 throughput-parity anchor",
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig",
    ],
}

EXACT_COUNT_MARKERS = {
    RELEASE_COORDINATION_MATRIX_PATH: {
        "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`": 1,
    },
    RAW_GITHUB_COVERAGE_PATH: {
        "- exact coverage evidence checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `24946f6a72b3b67faa6be4d54ed09d59518fa210`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `9d437058691bec8c7db0ca72422430c52b5a5e8f`, `scripts/zigux/validate-phase12.py` `cfd57eeff2d705fc4f02a9a85a3e1763c19a17f2`, `scripts/zigux/check-phase12-release-readiness-packet.py` `6989a61948e2e5d585275fba3af4fbecbe743b78`, `.github/workflows/zigux-bootstrap.yml` `f72787f799d497897122b86ddc65fd1ada31d77e`, `scripts/zigux/README.md` `5aff90b361628405898c7e83766acb43bcc4ef54`, `zigux/Makefile` `adcb33fc7dd30009e24210b2c44e3412427854fb`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`": 1,
        "- exact runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `30f30f327e8205a667d1b843c1dbd69a09beef17` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`": 1,
    },
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: [
        "phase12: phase12-smoke phase12-test",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "the shipped `make -C zigux phase12-validate` route keeps",
        "must not treat the shipped `make -C zigux phase12-validate` route",
        "`make -C zigux phase12-validate` stays reminder-only validator wrapper vocabulary until that wrapper returns on current `master`",
    ],
    VALIDATOR_PATH: [
        "RUNTIME_EVIDENCE_PATHS = [",
        "RUNTIME_EVIDENCE_ERROR = (",
        "RUNTIME_EVIDENCE_SUFFIX = (",
        "git_blob_sha(",
    ],
}


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")
    if missing:
        return missing, []

    drift: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                drift.append(f"missing_marker:{rel_path}:{marker}")
    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker, expected_count in markers.items():
            actual_count = text.count(marker)
            if actual_count != expected_count:
                drift.append(
                    "wrong_count:"
                    f"{rel_path}:{marker}:expected={expected_count}:actual={actual_count}"
                )
    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                drift.append(f"forbidden_marker:{rel_path}:{marker}")
    return [], drift


def run_checker(root: Path, rel_path: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / rel_path), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []

    failures = [f"phase12_checker_failed:{rel_path}:exit={result.returncode}"]
    combined_output = [
        line.strip()
        for line in f"{result.stdout}\n{result.stderr}".splitlines()
        if line.strip()
    ]
    failures.extend(f"phase12_checker_output:{line}" for line in combined_output)
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    body = "\n".join(f"- {marker}" for marker in markers)
    return f"{title}\n\n{body}\n"


FIXTURE_TEXT = {
    DOCS_README_PATH: marker_fixture(
        "# Zigux Documentation",
        REQUIRED_MARKERS[DOCS_README_PATH],
    ),
    REVIEW_CHECKLIST_PATH: marker_fixture(
        "# Zigux Review Checklist",
        REQUIRED_MARKERS[REVIEW_CHECKLIST_PATH],
    ),
    FREEZE_MAP_PATH: "# Zigux Freeze Map\n",
    RELEASE_READINESS_SURVEY_PATH: marker_fixture(
        "# Phase 12 Release Readiness Survey",
        REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH],
    ),
    RELEASE_SEQUENCING_PATH: marker_fixture(
        "# Phase 12 Release Sequencing",
        REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH],
    ),
    RELEASE_CLOSURE_CHECKLIST_PATH: marker_fixture(
        "# Phase 12 Release Closure Checklist",
        REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH],
    ),
    RELEASE_COORDINATION_MATRIX_PATH: marker_fixture(
        "# Phase 12 Release Coordination Matrix",
        REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH],
    ),
    RAW_GITHUB_COVERAGE_PATH: marker_fixture(
        "# Phase 12 Raw GitHub Coverage Survey",
        REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_PATH],
    ),
    PHASE12_COMPLEX_DRIVER_LANE_PATH: marker_fixture(
        "# Phase 12 Complex-Driver Lane Sequencing",
        REQUIRED_MARKERS[PHASE12_COMPLEX_DRIVER_LANE_PATH],
    ),
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: marker_fixture(
        "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
        REQUIRED_MARKERS[PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH],
    ),
    LIBBPF_SEGMENT_SURVEY_PATH: marker_fixture(
        "# Phase 12 Libbpf Segment Survey",
        REQUIRED_MARKERS[LIBBPF_SEGMENT_SURVEY_PATH],
    ),
    LIBBPF_SEGMENT_GATE_PATH: "\n".join(REQUIRED_MARKERS[LIBBPF_SEGMENT_GATE_PATH]) + "\n",
    VIRTIO_NET_SURVEY_PATH: marker_fixture(
        "# Phase 12 Virtio Net Survey",
        REQUIRED_MARKERS[VIRTIO_NET_SURVEY_PATH],
    ),
    VIRTIO_SCSI_FALLBACK_PATH: marker_fixture(
        "# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog",
        REQUIRED_MARKERS[VIRTIO_SCSI_FALLBACK_PATH],
    ),
    VIRTIO_SCSI_SLICE_PATH: "# Phase 12 virtio_scsi Slice\n",
    VIRTIO_SCSI_SURVEY_PATH: marker_fixture(
        "# Phase 12 Virtio SCSI Survey",
        REQUIRED_MARKERS[VIRTIO_SCSI_SURVEY_PATH],
    ),
    NVME_FALLBACK_PATH: marker_fixture(
        "# Phase 12 NVMe PCI Raw GitHub Fallback Map",
        REQUIRED_MARKERS[NVME_FALLBACK_PATH],
    ),
    NVME_REOPEN_GOVERNANCE_PATH: "# Phase 12 NVMe PCI Reopen Governance\n",
    NVME_SLICE_PATH: "# Phase 12 NVMe PCI Slice\n",
    NVME_SURVEY_PATH: "# Phase 12 NVMe PCI Survey\n",
    SCRIPTS_README_PATH: marker_fixture(
        "# scripts/zigux",
        REQUIRED_MARKERS[SCRIPTS_README_PATH],
    ),
    BUILD_ONLY_CHECKER_PATH: "#!/usr/bin/env python3\n",
    RELEASE_READINESS_CHECKER_PATH: "#!/usr/bin/env python3\n",
    COMPLEX_DRIVER_LANE_CHECKER_PATH: "#!/usr/bin/env python3\n",
    LIBBPF_SNAPSHOT_CHECKER_PATH: "#!/usr/bin/env python3\n",
    HEAVY_CONSUMER_PACKET_CHECKER_PATH: "\n".join(
        REQUIRED_MARKERS[HEAVY_CONSUMER_PACKET_CHECKER_PATH]
    )
    + "\n",
    VIRTIO_NET_PACKET_CHECKER_PATH: "\n".join(
        REQUIRED_MARKERS[VIRTIO_NET_PACKET_CHECKER_PATH]
    )
    + "\n",
    VIRTIO_SCSI_PACKET_CHECKER_PATH: "#!/usr/bin/env python3\n",
    VIRTIO_SCSI_BOUNDARY_CHECKER_PATH: "#!/usr/bin/env python3\n",
    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH: "\n".join(
        REQUIRED_MARKERS[VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH]
    )
    + "\n",
    VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH: "\n".join(
        REQUIRED_MARKERS[VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH]
    )
    + "\n",
    NVME_PACKET_CHECKER_PATH: "#!/usr/bin/env python3\n",
    VALIDATOR_PATH: "\n".join(REQUIRED_MARKERS[VALIDATOR_PATH]) + "\n",
    TESTS_README_PATH: marker_fixture(
        "# zigux/tests",
        REQUIRED_MARKERS[TESTS_README_PATH],
    ),
    MAKEFILE_PATH: "\n".join(REQUIRED_MARKERS[MAKEFILE_PATH]) + "\n",
    PHASE12_BUILD_PATH: "// phase12 build fixture\n",
    VIRTIO_NET_MANIFEST_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_NET_MANIFEST_PATH]) + "\n",
    VIRTIO_SCSI_MANIFEST_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_SCSI_MANIFEST_PATH]) + "\n",
    VIRTIO_SCSI_SURVEY_GATE_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_SCSI_SURVEY_GATE_PATH]) + "\n",
    VIRTIO_SCSI_SUPPORT_MANIFEST_PATH: (
        "{\n"
        '  "lane_key": "P12-L09",\n'
        '  "source_manifest": "zigux/tests/phase12_virtio_scsi_manifest.json"\n'
        "}\n"
    ),
    LIBBPF_SNAPSHOT_PATH: '{\n  "lane_key": "P12-L16"\n}\n',
    LIBBPF_SNAPSHOT_DETERMINISM_PATH: '{\n  "lane_key": "P12-L17"\n}\n',
    WORKFLOW_PATH: "\n".join(REQUIRED_MARKERS[WORKFLOW_PATH]) + "\n",
}


def write_fixture_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, FIXTURE_TEXT.get(rel_path, "// fixture\n"))


def expect_failure(root: Path, expected: str) -> None:
    missing, drift = validate(root)
    failures = missing + drift
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "")
    updated = updated.replace(marker, "")
    if updated == text:
        raise SystemExit(f"marker not removable: {marker}")
    path.write_text(updated, encoding="utf-8")


def add_forbidden_marker(path: Path, marker: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + f"{marker}\n", encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-validator-"))
    try:
        write_fixture_root(base)
        missing, drift = validate(base)
        if missing or drift:
            raise SystemExit(f"fixture tree should pass but failed: {(missing + drift)!r}")

        missing_file_cases = list(REQUIRED_FILES)
        for rel_path in missing_file_cases:
            write_fixture_root(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_root(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        exact_count_cases = [
            (rel_path, marker, expected_count)
            for rel_path, markers in EXACT_COUNT_MARKERS.items()
            for marker, expected_count in markers.items()
        ]
        for rel_path, marker, expected_count in exact_count_cases:
            write_fixture_root(base)
            add_forbidden_marker(base / rel_path, marker)
            expect_failure(
                base,
                "wrong_count:"
                f"{rel_path}:{marker}:expected={expected_count}:actual={expected_count + 1}"
            )

        forbidden_cases = [
            (rel_path, marker)
            for rel_path, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_root(base)
            add_forbidden_marker(base / rel_path, marker)
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = (
            len(missing_file_cases)
            + len(marker_cases)
            + len(exact_count_cases)
            + len(forbidden_cases)
        )
        print("PHASE12_VALIDATOR_SELF_TEST=pass")
        print(f"PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 shared support bundle around the release "
            "packet, fallback packet, shared anti-overlap companions, driver-local "
            "surveys, and current master route reality."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test without reading repo files.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing, drift = validate(args.root)
    if missing:
        print("PHASE12_VALIDATION=fail")
        print("MISSING_PHASE12_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE12_FILES_END")
        return 1
    if drift:
        print("PHASE12_VALIDATION=fail")
        print("PHASE12_PACKET_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE12_PACKET_DRIFT_END")
        return 1

    checker_failures: list[str] = []
    for checker_path in PHASE12_PACKET_CHECKERS:
        checker_failures.extend(run_checker(args.root, checker_path))
    if checker_failures:
        print("PHASE12_VALIDATION=fail")
        print("PHASE12_PACKET_DRIFT_START")
        for item in checker_failures:
            print(item)
        print("PHASE12_PACKET_DRIFT_END")
        return 1

    print("PHASE12_VALIDATION=pass")
    print(f"PHASE12_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE12_REQUIRED_MARKER_COUNT=" f"{sum(len(v) for v in REQUIRED_MARKERS.values())}")
    print(
        "PHASE12_EXACT_COUNT_MARKER_COUNT="
        f"{sum(len(v) for v in EXACT_COUNT_MARKERS.values())}"
    )
    print("PHASE12_FORBIDDEN_MARKER_COUNT=" f"{sum(len(v) for v in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
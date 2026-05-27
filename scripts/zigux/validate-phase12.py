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
CROSS_COMPILE_SMOKE_PATH = "Documentation/zigux/phase12-cross-compile-smoke.md"
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
CROSS_COMPILE_SMOKE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-cross-compile-smoke.py"
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
    CROSS_COMPILE_SMOKE_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    HEAVY_CONSUMER_PACKET_CHECKER_PATH,
    NVME_PACKET_CHECKER_PATH,
    VIRTIO_NET_PACKET_CHECKER_PATH,
    VIRTIO_SCSI_PACKET_CHECKER_PATH,
    VIRTIO_SCSI_BOUNDARY_CHECKER_PATH,
    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH,
    VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH,
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
    CROSS_COMPILE_SMOKE_PATH,
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
    CROSS_COMPILE_SMOKE_CHECKER_PATH,
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
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and the shipped wrapper name `make -C zigux phase12-validate`",
        "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
        "the shipped packet-local `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py` guard",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "- exact coverage evidence checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `24946f6a72b3b67faa6be4d54ed09d59518fa210`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `9d437058691bec8c7db0ca72422430c52b5a5e8f`, `scripts/zigux/validate-phase12.py` `cfd57eeff2d705fc4f02a9a85a3e1763c19a17f2`, `scripts/zigux/check-phase12-release-readiness-packet.py` `6989a61948e2e5d585275fba3af4fbecbe743b78`, `.github/workflows/zigux-bootstrap.yml` `f72787f799d497897122b86ddc65fd1ada31d77e`, `scripts/zigux/README.md` `5aff90b361628405898c7e83766acb43bcc4ef54`, `zigux/Makefile` `adcb33fc7dd30009e24210b2c44e3412427854fb`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`",
        "- exact same-day support-bundle refresh checked later on `2026-05-25`: the current GitHub contents bridge now directly reads `scripts/zigux/validate-phase12.py` `f5c2db6f5b154c8f8576046bf4e75cc1d843f54e`, `scripts/zigux/check-phase12-release-readiness-packet.py` `5c7fffadc13b53b3b44e2c3fd5053a3caa47547b`, and `.github/workflows/zigux-bootstrap.yml` `30f30f327e8205a667d1b843c1dbd69a09beef17`; keep this later same-day readback explicit so the support-bundle inventory stays truthful after the readiness checker and workflow moved again while the rest of the returned `2026-05-25` bridge set remained unchanged.",
        "- exact latest same-day support-bundle refresh checked on `2026-05-25`: the current GitHub contents bridge now directly reads `scripts/zigux/validate-phase12.py` `53aa081f2ab503707ecdb34cf49ec96ecc11d7d5`, `scripts/zigux/check-phase12-release-readiness-packet.py` `ee26948c12322848ca8e772899d8714efb33e403`, `.github/workflows/zigux-bootstrap.yml` `ffc17180c68e54714ce28a59a6cf3c0757caf9fe`, and `scripts/zigux/README.md` `f81fcac2f5e8f07c3f60a565503fe5d2a374d1c2`; keep this latest same-day refresh explicit so the support-bundle inventory stays truthful after the validator, readiness checker, workflow, and scripts-root companion moved again while the rest of the returned `2026-05-25` bridge set remained unchanged.",
        "- exact current support-bundle reread checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `1b10a8a4d36fbc3fe0c7297cde21406914401f0e`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `222dab688ce63e50229704668a0a91e4299043b8`, `scripts/zigux/validate-phase12.py` `4c494494019845cd4cfec9bbc1ba9f1de32ed53e`, `scripts/zigux/check-phase12-release-readiness-packet.py` `e422f7d3b2bd9962e905f2c99aaf688729533ad2`, `.github/workflows/zigux-bootstrap.yml` `ffc17180c68e54714ce28a59a6cf3c0757caf9fe`, `scripts/zigux/README.md` `b4fa028577161eea393eda37efcd78908a73e736`, `zigux/Makefile` `770082f5313b8125f55300dc3f0b2805cf2f6551`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`.",
        "- exact current support-bundle reread checked on `2026-05-26`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `1b10a8a4d36fbc3fe0c7297cde21406914401f0e`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `277554397ab1a236c71f1dac9061ffe4cfbeaf67`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `272fd3f230c35ed8c32aa588c269f5c675525871`, `scripts/zigux/validate-phase12.py` `260f3079620687ff922006176909c9513a60be77`, `scripts/zigux/check-phase12-release-readiness-packet.py` `4a10382b6d897afccad318bdeccbb959a6373087`, `.github/workflows/zigux-bootstrap.yml` `68d194259d116554c7afb4a275abf4d5be3f1623`, `scripts/zigux/README.md` `eae84316a0c18edacc1be06e93aeae2557c79fa9`, `zigux/Makefile` `4d572bfda15dc6ae7cd419cc4c7f858d973cda26`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`.",
        "- exact runtime-reality evidence checked on `2026-05-23`: the directly readable `zigux/Makefile` blob `b2a4e6aa129ccedf690ad3fa10a862f6edc82ca5` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again",
        "- exact runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `30f30f327e8205a667d1b843c1dbd69a09beef17` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
        "- exact latest runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `ffc17180c68e54714ce28a59a6cf3c0757caf9fe` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
        "- exact current runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `770082f5313b8125f55300dc3f0b2805cf2f6551` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `ffc17180c68e54714ce28a59a6cf3c0757caf9fe` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
        "- exact current runtime-reality evidence checked on `2026-05-26`: the directly readable `zigux/Makefile` blob `4d572bfda15dc6ae7cd419cc4c7f858d973cda26` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `68d194259d116554c7afb4a275abf4d5be3f1623` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
    ],
    WORKFLOW_PATH: [
        "run: python3 scripts/zigux/validate-phase12.py",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "run: zig build smoke --build-file zigux/tests/phase12_build.zig --summary all",
        "run: zig build test --build-file zigux/tests/phase12_build.zig --summary all",
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "\t$(PYTHON) ../scripts/zigux/validate-phase12.py",
        "phase12-smoke:",
        "\t$(ZIG) build smoke --build-file tests/phase12_build.zig --summary all",
        "phase12-test:",
        "\t$(ZIG) build test --build-file tests/phase12_build.zig --summary all",
        "phase12: phase12-validate phase12-smoke phase12-test",
        "phase12-virtio-net-throughput-parity-test:",
        "\t$(ZIG) build phase12-virtio-net-throughput-parity --build-file tests/phase12_build.zig --summary all",
    ],
    PHASE12_BUILD_PATH: [
        'const throughput_parity_step = b.step("phase12-virtio-net-throughput-parity", "Run the Phase 12 virtio_net throughput parity checks");',
        'throughput_parity_step.dependOn(&throughput_parity_tests.step);',
    ],
    RELEASE_READINESS_CHECKER_PATH: [
        '"run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",',
    ],
}

# remainder of file unchanged...

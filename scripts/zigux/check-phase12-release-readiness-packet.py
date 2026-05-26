#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase12-release-readiness-survey.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RAW_GITHUB_COVERAGE_SURVEY_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
PHASE12_COMPLEX_DRIVER_LANE_PATH = (
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
)
PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH = (
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
)
SCRIPTS_README_PATH = "scripts/zigux/README.md"
LIBBPF_LANE_MARKER_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-lane-marker.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    DOCS_README_PATH,
    FREEZE_MAP_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    PHASE12_COMPLEX_DRIVER_LANE_PATH,
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH,
    SCRIPTS_README_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
        "current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.",
        "the shared route stays the six-file `virtio_net` smoke-and-test sextet in `zigux/tests/phase12_build.zig`",
    ],
    FREEZE_MAP_PATH: [
        "- `net/core/skbuff.c`",
        "- `kernel/workqueue.c`",
        "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof",
        "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
        "The active shared build route on current `master` is the six-file `virtio_net` smoke-and-test packet in `zigux/tests/phase12_build.zig`: `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` are the directly wired shared reruns",
        "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
        "the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, and `.github/workflows/zigux-bootstrap.yml`",
        "`scripts/zigux/check-build-only-phase12-surface.py` remains the bounded build-only contract checker",
        "`scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py` remains the packet-local boundary guard that keeps the rollback-only `virtio_scsi` survey packet distinct from the parked libbpf reviewability packet inside the shared Phase 12 release story.",
        "`scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` remain the parked libbpf support guards",
        "Fresh repo-first rereads now confirm that `scripts/zigux/check-phase12-release-readiness-packet.py` already matches the returned `phase12-validate` wrapper and the six-file shared `virtio_net` follow-up sextet on current `master`, so this note should no longer send the next same-lane pass back to that already-closed checker-side repair.",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
        "Current workflow-side fallback recovery evidence: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` path by first trying the pinned `third_party` archive, then the Zig community-mirror list, and finally `ziglang.org`, so this sequencing note should treat the local Makefile fallback as a restorable local-first path before attached-`ZIG=<attached-zig-path>` reruns rather than as a one-shot cache hit.",
        "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
        "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "keep `make -C zigux phase12-validate` explicit here as shipped wrapper evidence again on current `master`.",
        "The active shared build packet on current `master` is the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`",
        "The current driver-local `virtio_scsi` split must stay explicit too: current `master` keeps the dedicated `Documentation/zigux/phase12-virtio-scsi-slice.md` plus `Documentation/zigux/phase12-virtio-scsi-survey.md` pair together with `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig`, while `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` remain absent on current `master`.",
        "The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and the shipped wrapper name `make -C zigux phase12-validate`",
        "shared replay wiring: `zigux/tests/phase12_build.zig` and `.github/workflows/zigux-bootstrap.yml`; `zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on `master`",
        "The active shared build packet is the returned six-file `virtio_net` sextet only:",
        "`zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py` while keeping that storage-facing rollback-evidence packet and its dedicated survey-build rerun outside the shared `smoke` and `test` build route.",
        "Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "  * current contents-bridge shared support bundle during degraded contents reads:",
        "- exact coverage evidence checked on `2026-05-23`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` on current `master`, and browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`",
        "- exact coverage evidence checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `24946f6a72b3b67faa6be4d54ed09d59518fa210`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `9d437058691bec8c7db0ca72422430c52b5a5e8f`, `scripts/zigux/validate-phase12.py` `cfd57eeff2d705fc4f02a9a85a3e1763c19a17f2`, `scripts/zigux/check-phase12-release-readiness-packet.py` `6989a61948e2e5d585275fba3af4fbecbe743b78`, `.github/workflows/zigux-bootstrap.yml` `f72787f799d497897122b86ddc65fd1ada31d77e`, `scripts/zigux/README.md` `5aff90b361628405898c7e83766acb43bcc4ef54`, `zigux/Makefile` `adcb33fc7dd30009e24210b2c44e3412427854fb`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`",
        "- exact same-day support-bundle refresh checked later on `2026-05-25`: the current GitHub contents bridge now directly reads `scripts/zigux/validate-phase12.py` `f5c2db6f5b154c8f8576046bf4e75cc1d843f54e`, `scripts/zigux/check-phase12-release-readiness-packet.py` `5c7fffadc13b53b3b44e2c3fd5053a3caa47547b`, and `.github/workflows/zigux-bootstrap.yml` `30f30f327e8205a667d1b843c1dbd69a09beef17`; keep this later same-day readback explicit so the support-bundle inventory stays truthful after the readiness checker and workflow moved again while the rest of the returned `2026-05-25` bridge set remained unchanged.",
        "- exact latest same-day support-bundle refresh checked on `2026-05-25`: the current GitHub contents bridge now directly reads `scripts/zigux/validate-phase12.py` `53aa081f2ab503707ecdb34cf49ec96ecc11d7d5`, `scripts/zigux/check-phase12-release-readiness-packet.py` `ee26948c12322848ca8e772899d8714efb33e403`, `.github/workflows/zigux-bootstrap.yml` `ffc17180c68e54714ce28a59a6cf3c0757caf9fe`, and `scripts/zigux/README.md` `f81fcac2f5e8f07c3f60a565503fe5d2a374d1c2`; keep this latest same-day refresh explicit so the support-bundle inventory stays truthful after the validator, readiness checker, workflow, and scripts-root companion moved again while the rest of the returned `2026-05-25` bridge set remained unchanged.",
        "- exact current support-bundle reread checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `1b10a8a4d36fbc3fe0c7297cde21406914401f0e`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `222dab688ce63e50229704668a0a91e4299043b8`, `scripts/zigux/validate-phase12.py` `4c494494019845cd4cfec9bbc1ba9f1de32ed53e`, `scripts/zigux/check-phase12-release-readiness-packet.py` `e422f7d3b2bd9962e905f2c99aaf688729533ad2`, `.github/workflows/zigux-bootstrap.yml` `ffc17180c68e54714ce28a59a6cf3c0757caf9fe`, `scripts/zigux/README.md` `b4fa028577161eea393eda37efcd78908a73e736`, `zigux/Makefile` `770082f5313b8125f55300dc3f0b2805cf2f6551`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`.",
        "exact runtime-reality evidence checked on `2026-05-23`: the directly readable `zigux/Makefile` blob `b2a4e6aa129ccedf690ad3fa10a862f6edc82ca5` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again",
        "- exact runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `30f30f327e8205a667d1b843c1dbd69a09beef17` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
        "- exact latest runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `ffc17180c68e54714ce28a59a6cf3c0757caf9fe` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
        "- exact current runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `770082f5313b8125f55300dc3f0b2805cf2f6551` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `ffc17180c68e54714ce28a59a6cf3c0757caf9fe` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
        "- exact current runtime-shell evidence checked on `2026-05-25`: direct `git clone https://github.com/adybag14-cyber/Zigux.git` also fails in this runtime with CONNECT tunnel `403`, so same-runtime exact verification still depends on GitHub contents readback plus browser-side raw GitHub fallback rather than a trustworthy current-head local checkout.",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`",
        "The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test`, `python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12`.",
        "The readable build file currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` through the shared `smoke` and `test` steps",
    ],
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: [
        "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`",
        "The shipped heavy-consumer guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
        "the current scripts-root complex-driver reminder should keep the shared release packet reviewable through the build-only checker, the readiness-note checker, the dedicated anti-overlap checker, the validator entrypoint, the returned `phase12-validate` / `phase12-smoke` / `phase12-test` / `phase12` wrapper split, and the split-helper `virtio_net` evidence packet while keeping the rollback-evidence `virtio_scsi` survey family, the published-but-unwired NVMe foothold, and the parked libbpf packet distinct",
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    ],
    VALIDATOR_PATH: [
        "BUILD_ONLY_CHECKER_PATH = \"scripts/zigux/check-build-only-phase12-surface.py\"",
        "RELEASE_READINESS_CHECKER_PATH = (",
        "make -C zigux phase12-validate",
        "scripts-side support packet",
        "PHASE12_VALIDATION=pass",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    TESTS_README_PATH: [
        "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
        "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
        "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Validate current Phase 12 support bundle",
        "run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
    ],
}

EXACT_COUNT_MARKERS = {
    RAW_GITHUB_COVERAGE_SURVEY_PATH: {
        "- exact coverage evidence checked on `2026-05-23`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` on current `master`, and browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`": 1,
        "- exact coverage evidence checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `24946f6a72b3b67faa6be4d54ed09d59518fa210`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `9d437058691bec8c7db0ca72422430c52b5a5e8f`, `scripts/zigux/validate-phase12.py` `cfd57eeff2d705fc4f02a9a85a3e1763c19a17f2`, `scripts/zigux/check-phase12-release-readiness-packet.py` `6989a61948e2e5d585275fba3af4fbecbe743b78`, `.github/workflows/zigux-bootstrap.yml` `f72787f799d497897122b86ddc65fd1ada31d77e`, `scripts/zigux/README.md` `5aff90b361628405898c7e83766acb43bcc4ef54`, `zigux/Makefile` `adcb33fc7dd30009e24210b2c44e3412427854fb`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`": 1,
        "- exact same-day support-bundle refresh checked later on `2026-05-25`: the current GitHub contents bridge now directly reads `scripts/zigux/validate-phase12.py` `f5c2db6f5b154c8f8576046bf4e75cc1d843f54e`, `scripts/zigux/check-phase12-release-readiness-packet.py` `5c7fffadc13b53b3b44e2c3fd5053a3caa47547b`, and `.github/workflows/zigux-bootstrap.yml` `30f30f327e8205a667d1b843c1dbd69a09beef17`; keep this later same-day readback explicit so the support-bundle inventory stays truthful after the readiness checker and workflow moved again while the rest of the returned `2026-05-25` bridge set remained unchanged.": 1,
        "- exact latest same-day support-bundle refresh checked on `2026-05-25`: the current GitHub contents bridge now directly reads `scripts/zigux/validate-phase12.py` `53aa081f2ab503707ecdb34cf49ec96ecc11d7d5`, `scripts/zigux/check-phase12-release-readiness-packet.py` `ee26948c12322848ca8e772899d8714efb33e403`, `.github/workflows/zigux-bootstrap.yml` `ffc17180c68e54714ce28a59a6cf3c0757caf9fe`, and `scripts/zigux/README.md` `f81fcac2f5e8f07c3f60a565503fe5d2a374d1c2`; keep this latest same-day refresh explicit so the support-bundle inventory stays truthful after the validator, readiness checker, workflow, and scripts-root companion moved again while the rest of the returned `2026-05-25` bridge set remained unchanged.": 1,
        "- exact current support-bundle reread checked on `2026-05-25`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `1793b998777d7d402b79108690ecd0ba070a5492`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `1b10a8a4d36fbc3fe0c7297cde21406914401f0e`, `scripts/zigux/check-phase12-libbpf-snapshot.py` `92759632d6db2a6419de41d561aa8c5ffba6dd05`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` `222dab688ce63e50229704668a0a91e4299043b8`, `scripts/zigux/validate-phase12.py` `4c494494019845cd4cfec9bbc1ba9f1de32ed53e`, `scripts/zigux/check-phase12-release-readiness-packet.py` `e422f7d3b2bd9962e905f2c99aaf688729533ad2`, `.github/workflows/zigux-bootstrap.yml` `ffc17180c68e54714ce28a59a6cf3c0757caf9fe`, `scripts/zigux/README.md` `b4fa028577161eea393eda37efcd78908a73e736`, `zigux/Makefile` `770082f5313b8125f55300dc3f0b2805cf2f6551`, and `zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c` on current `master`; browser-side raw GitHub readback remains the matching public-read fallback for the shipped Phase 12 support bundle while direct container-side `curl`, `wget`, and `urllib` raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`.": 1,
        "exact runtime-reality evidence checked on `2026-05-23`: the directly readable `zigux/Makefile` blob `b2a4e6aa129ccedf690ad3fa10a862f6edc82ca5` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again": 1,
        "- exact runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `30f30f327e8205a667d1b843c1dbd69a09beef17` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`": 1,
        "- exact latest runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `34654c70c864378012494bd0068ccf260678ec0d` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `ffc17180c68e54714ce28a59a6cf3c0757caf9fe` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`": 1,
        "- exact current runtime-reality evidence checked on `2026-05-25`: the directly readable `zigux/Makefile` blob `770082f5313b8125f55300dc3f0b2805cf2f6551` still prefers the repo-local `.zig-toolchain` executable through `ZIG_PINNED_EXECUTABLE`, `ZIG_LOCAL_TOOLCHAIN`, `ZIG_PINNED_TOOLCHAIN`, and `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)`, and the directly readable workflow blob `ffc17180c68e54714ce28a59a6cf3c0757caf9fe` still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`.": 1,
        "- exact current runtime-shell evidence checked on `2026-05-25`: direct `git clone https://github.com/adybag14-cyber/Zigux.git` also fails in this runtime with CONNECT tunnel `403`, so same-runtime exact verification still depends on GitHub contents readback plus browser-side raw GitHub fallback rather than a trustworthy current-head local checkout.": 1,
    },
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker, expected_count in markers.items():
            actual_count = text.count(marker)
            if actual_count != expected_count:
                failures.append(
                    "wrong_count:"
                    f"{rel_path}:{marker}:expected={expected_count}:actual={actual_count}"
                )

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    if rel_path in REQUIRED_MARKERS:
        title = {
            DOCS_README_PATH: "# Zigux Documentation",
            FREEZE_MAP_PATH: "# Zigux Freeze Map",
            REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
            RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
            RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            PHASE12_COMPLEX_DRIVER_LANE_PATH: "# Phase 12 Complex-Driver Lane Sequencing",
            PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
            SCRIPTS_README_PATH: "# scripts/zigux",
            TESTS_README_PATH: "# zigux/tests",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path in {VALIDATOR_PATH, MAKEFILE_PATH, WORKFLOW_PATH}:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".yml"):
        return "name: zigux-bootstrap\n"
    return ""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    if marker in updated:
        updated = updated.replace(marker, "__REMOVED_PHASE12_MARKER__", 1)
    if updated == text:
        raise SystemExit(f"unable to mutate marker in fixture: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = REQUIRED_FILES[:]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        exact_count_cases = [
            (rel_path, marker, expected_count)
            for rel_path, markers in EXACT_COUNT_MARKERS.items()
            for marker, expected_count in markers.items()
        ]
        for rel_path, marker, expected_count in exact_count_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + marker + "\n",
            )
            expect_failure(
                base,
                "wrong_count:"
                f"{rel_path}:{marker}:expected={expected_count}:actual={expected_count + 1}"
            )

        case_count = (
            len(missing_file_cases)
            + len(marker_cases)
            + len(exact_count_cases)
        )
        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
        print(f"PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current narrow Phase 12 release-readiness support bundle "
            "around the shared release notes, fallback split, and returned wrapper "
            "state."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_RELEASE_READINESS_PACKET=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_RELEASE_READINESS_PACKET=pass")
    print(f"PHASE12_RELEASE_READINESS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_RELEASE_READINESS_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print("PHASE12_RELEASE_READINESS_PACKET_FORBIDDEN_MARKER_COUNT=0")
    print(
        "PHASE12_RELEASE_READINESS_PACKET_EXACT_COUNT_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

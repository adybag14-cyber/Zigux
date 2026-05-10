#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
PHASE12_SEQUENCE_PATH = "Documentation/zigux/phase12-release-sequencing.md"
PHASE12_CLOSURE_CHECKLIST_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
PHASE12_RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
PHASE12_COMPLEX_DRIVER_LANE_PATH = "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
PHASE12_RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
NVME_FALLBACK_MAP_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
VIRTIO_SCSI_FALLBACK_PATH = "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
PHASE12_VIRTIO_SCSI_SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
VIRTIO_NET_SURVEY_PATH = "Documentation/zigux/phase12-virtio-net-survey.md"
LIBBPF_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
PHASE12_COORDINATION_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_VIRTIO_NET_MANIFEST_PATH = "zigux/tests/phase12_virtio_net_manifest.json"
PHASE12_VIRTIO_NET_SURVEY_TEST_PATH = "zigux/tests/phase12_virtio_net_survey.zig"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

FORBIDDEN_FILES = [
    "scripts/zigux/validate-phase12.py",
]

FORBIDDEN_GLOBS = [
    "scripts/zigux/check-phase12-*.py",
]

DOCS_PHASE12_FREEZE_REMINDER_MARKER = (
    "the PMO closure companion, the adjacent release-readiness survey, the compact "
    "release-coordination matrix, the freeze-boundary reminder, the driver-only "
    "anti-overlap companion, and the shared fallback-overview note"
)

REQUIRED_FILE_MARKERS = {
    DOCS_README_PATH: [
        "Phase 12 notes",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        DOCS_PHASE12_FREEZE_REMINDER_MARKER,
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "`Documentation/zigux/phase12-libbpf-segment-survey.md`",
        "`drivers/nvme/host/pci_verify.zig`",
        "`zigux/tests/phase12_virtio_net_manifest.json`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_manifest.json`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`zigux/tests/phase12_libbpf_manifest.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "`make -C zigux phase12-smoke`",
        "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
        "there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the shared Phase 12 complex-driver packet",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`Documentation/zigux/freeze-map.md`",
        "`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
        "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "`drivers/nvme/host/pci_verify.zig`",
        "`zigux/tests/phase12_virtio_net_manifest.json`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_manifest.json`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`zigux/tests/phase12_libbpf_manifest.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`",
    ],
    PHASE12_SEQUENCE_PATH: [
        "PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml` keep the build-only contract fail-closed",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "Keep those checker reruns before or beside the attached-toolchain Make reruns so build-only contract drift still fails closed when the fallback path is in use.",
        "This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.",
        "the checker-local closure-companion update is landed",
        "the next bounded same-lane follow-through is drift control",
        "the bounded `virtio_scsi` rollback drill plus the repeated transport-reset generation, restore queue rebind, request-queue restart, event rearm, event-buffer ownership, and rollback summaries are reviewable release evidence",
    ],
    PHASE12_CLOSURE_CHECKLIST_PATH: [
        "Phase 12 Release Closure Checklist",
        "compact release-coordination matrix: `Documentation/zigux/phase12-release-coordination-matrix.md`",
        "adjacent release-readiness note: `Documentation/zigux/phase12-release-readiness-survey.md`",
        "complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "scripts/zigux/check-build-only-phase12-surface.py",
        "Documentation/zigux/phase12-raw-github-coverage-survey.md",
        "two commit-pinned artifacts plus two shared-tree-only anchors",
        "now explicitly pins `Documentation/zigux/phase12-release-closure-checklist.md` inside its fail-closed marker set",
        "`Documentation/zigux/freeze-map.md` keeps `net/core/skbuff.c` frozen in C and keeps `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` in boundary-study-only status",
        "must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "the smallest same-lane follow-through is now shared-surface drift control",
    ],
    PHASE12_RELEASE_READINESS_SURVEY_PATH: [
        "`PHASE12_TRANCHE=driver-and-libbpf-survey-bundle`",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "freeze-boundary authority: `Documentation/zigux/freeze-map.md`",
        "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
        "`python3 scripts/zigux/check-build-only-phase12-surface.py`",
        "build-only contract drift still fails closed when the local runtime needs the fallback path.",
        "the compact release-coordination matrix",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.",
        "There is no shipped shared `scripts/zigux/validate-phase12.py`, no dedicated `check-phase12-*.py` release packet, and no `make -C zigux phase12-validate` target on `master`, so this release-facing note should not imply validator-first, dedicated PMO checker, focused libbpf-only replay, raw-coverage checker, or cross-build routes as part of the active shared release path.",
        "The public fallback split must stay explicit: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are the only commit-pinned fallback artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors.",
        "The bounded `virtio_scsi` rollback drill remains storage-lane-local release evidence, not a tranche-wide recovery claim.",
        "That bounded storage packet now covers repeated transport-reset generation plus restore queue rebind, request-queue restart, event rearm, event-buffer ownership, and rollback summaries as lab-only reversible-delivery scaffolding, not as closure-ready runtime recovery.",
        "The landed `virtio_net` segmented-rollout boundary remains lane-local review evidence, not DMA-safe transport readiness, runtime recovery proof, or live runtime-data-path progress.",
        "Queueing, throughput, rollback, and recovery wording in this release-facing note must stay below active delivery claims against frozen `net/core/skbuff.c` and below boundary-study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` until a broader Phase 12 packet actually lands.",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "complex-driver scope in this note: `virtio_net`, `nvme_pci`, and `virtio_scsi`",
        "excluded from this note on purpose: the shared PMO release packet and the non-driver libbpf helper packet",
        "`Documentation/zigux/phase12-release-sequencing.md`",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` keeps the shared libbpf reviewability lane",
        "`Documentation/zigux/phase12-libbpf-segment-survey.md` and `tools/lib/bpf/zigux_segments/manifest.json` remain real Phase 12 evidence",
        "they belong to the non-driver helper packet and should not be absorbed into this driver-only map.",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "That rollback drill is storage-lane-local evidence, not a shared Phase 12 recovery claim.",
    ],
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: [
        "Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
        "shipped shared coordination surfaces on `master`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "shared reviewability surfaces that describe or gate the live Phase 12 libbpf packet",
        "shared reviewability owns the survey, manifest, deterministic snapshot fixture, snapshot determinism replay, reviewability gate, and shared build alignment",
    ],
    PHASE12_RAW_GITHUB_COVERAGE_PATH: [
        "commit-pinned fallback artifacts:",
        "`PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`",
        "shared-tree-only anchors:",
        "`PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`",
        "freeze-boundary guard: `Documentation/zigux/freeze-map.md`; queueing, throughput, rollback, and recovery wording in this shared fallback overview must stay below active delivery claims against frozen `net/core/skbuff.c` and below boundary-study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c`",
        "The shipped Phase 12 packet on `master` still keeps the same four-step smoke-first replay order used by the PMO sequencing and closure companion notes.",
        "PHASE12_SHARED_SMOKE_SURFACE_COUNT=6",
        "current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "`make -C zigux phase12-smoke`",
        "`make -C zigux phase12`",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion",
        "Keep `Documentation/zigux/phase12-release-readiness-survey.md` visible beside this shared fallback overview, the PMO closure companion, and `Documentation/zigux/phase12-release-coordination-matrix.md` so adjacent tranche-readiness wording stays tied to the same two-artifact-plus-two-anchor split and smoke-first release packet instead of drifting into its own broader route.",
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview",
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes so the fallback split does not blur the shared reviewability lane, the tracked pure-helper lane, the landed helper-foundation lane, the deferred bridge and queue-routing lane, and the blocked object-model wall back into one vague `libbpf` bucket.",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and the direct PMO drift-control reruns are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` plus `python3 scripts/zigux/check-build-only-phase12-surface.py` before or beside the workflow-backed replay in `.github/workflows/zigux-bootstrap.yml`, so this shared fallback-overview wording stays aligned with the shipped PMO release packet.",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion",
        "PHASE12_LIBBPF_TRACKED_HELPER_COUNT=5",
    ],
    PHASE12_COORDINATION_MATRIX_PATH: [
        "Phase 12 Release Coordination Matrix",
        "PHASE12_RELEASE_CLOSED=no",
        "PHASE12_TRANCHE=driver-and-libbpf-survey-bundle",
        "release-order authority: `Documentation/zigux/phase12-release-sequencing.md`",
        "PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`",
        "adjacent release-readiness note: `Documentation/zigux/phase12-release-readiness-survey.md`",
        "shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "driver-only anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "freeze-boundary authority: `Documentation/zigux/freeze-map.md`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
        "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
        "PHASE12_SHARED_SMOKE_SURFACE_COUNT=6",
        "build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml`",
        "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
        "`python3 scripts/zigux/check-build-only-phase12-surface.py`",
        "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` remain part of the shipped build-only contract packet beside the workflow-backed replay and must not be rounded up into a validator-first, focused libbpf-only, raw-coverage, or `phase12-validate` route",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "the landed `virtio_net` segmented-rollout boundary remains lane-local review evidence inside this active packet",
        "the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill remains lab-only reversible-delivery evidence inside this active packet",
        "that bounded storage packet specifically keeps repeated transport-reset generation plus restore queue rebind, request-queue restart, event rearm, event-buffer ownership, and rollback summaries reviewable as lab-only reversible-delivery scaffolding inside the active Phase 12 PMO packet",
        "there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` packet, no focused libbpf-only replay route, no raw-coverage packet guard, no cross-build replay packet, and no `make -C zigux phase12-validate` target on `master`",
    ],
    NVME_FALLBACK_MAP_PATH: [
        "PMO closure companion",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
        "current nvme smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig` and `drivers/nvme/host/pci_verify.zig`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback map, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback map into a second sequencing document.",
        "The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "PMO closure companion",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
        "current virtio_scsi smoke packet surfaces: `zigux/tests/phase12_virtio_scsi.zig` and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback catalog, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback catalog into a second sequencing document.",
        "The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`",
        "## Current Verification Evidence",
        "latest visible public `master` head checked before this catalog refresh:",
        "`PHASE12_TREE_VIEW_COUNT=19`",
        "`PHASE12_RAW_VIEW_COUNT=19`",
        "`PHASE12_VERIFIED_FILE_COUNT=19`",
        "public GitHub commits-page readback for the visible `master` head",
        "public GitHub raw fallback readback for the bounded packet",
        "authenticated blob-identity readback for every covered file listed below",
        "- current blob identities for the covered packet:",
        "- `drivers/scsi/virtio_scsi.zig`: `5f76c9e23a470545238df3ec10db60b91ab12786`",
        "- `Documentation/zigux/phase12-virtio-scsi-survey.md`: `73269ae39f8381b9ea3b559ecdbe9ec09b9886d1`",
        "- `zigux/tests/phase12_virtio_scsi_manifest.json`: `30b6878de70003eb2f893cb3b16b65441017dbc7`",
        "- `zigux/Makefile`: `06d4605ed21ec25e9c6793d0a713b72852ad1822`",
        "- bounded coverage result: the current public tree and raw fallback packet still resolves cleanly for all 19 listed surfaces",
    ],
    PHASE12_VIRTIO_SCSI_SLICE_PATH: [
        "records one bounded restore-time event-buffer ownership summary",
        "lab-only transport freeze or restore boundary",
        "records one bounded freeze-time request-queue quiesce summary",
        "`virtscsi_restore()` calling `find_vqs`, `virtio_device_ready()`, and event rearm",
        "records one bounded request-queue restart summary",
        "records one bounded request-queue ownership summary",
        "records one bounded recovery event-rearm summary",
        "records one bounded recovery rollback summary",
        "This slice does not claim DMA mapping",
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-smoke` rerun this bounded `virtio scsi` starter before the broader survey-backed replay",
        "Keep this slice parked until the roadmap approves queue ownership, SCSI host registration, or DMA-backed queue work",
    ],
    VIRTIO_NET_SURVEY_PATH: [
        "public fallback posture: shared-tree-only anchor",
        "segmented rollout boundary",
        "runtime-data-path boundary remains blocked",
    ],
    LIBBPF_SURVEY_PATH: [
        "public fallback posture: shared-tree-only anchor",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "keep the five shipped helper paths explicit in a deterministic tracked-helper snapshot fixture",
        "exact-check the ordered helper-path snapshot digest through a dedicated replay",
        "the older segment catalog still leaves two bounded shared-bridge helpers explicitly nearer than the object-model wall",
    ],
    SCRIPTS_README_PATH: [
        "Phase 12 flow",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "`Documentation/zigux/freeze-map.md`",
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
        "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
        "`make -C zigux phase12-smoke`",
        "`make -C zigux phase12`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_manifest.json`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "`check-build-only-phase12-surface.py --self-test` and `check-build-only-phase12-surface.py` keep the docs-root, scripts-root, tests-root, and Makefile build-only contract fail-closed",
        "there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`",
    ],
    TESTS_README_PATH: [
        "keep `Documentation/zigux/phase12-release-closure-checklist.md` visible beside `Documentation/zigux/phase12-release-sequencing.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "`Documentation/zigux/phase12-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "`Documentation/zigux/freeze-map.md`",
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
        "`zigux/tests/phase12_virtio_net_manifest.json`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`scripts/zigux/check-build-only-phase12-surface.py`",
        "`make -C zigux phase12-smoke`",
        "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
        "`make -C zigux phase12`",
    ],
    PHASE12_VIRTIO_NET_MANIFEST_PATH: [
        '"lane_key": "P12-L04"',
        '"phase": "Phase 12"',
        '"anchor": "drivers/net/virtio_net.c"',
        '"id": "phase12-virtio-net-syntax-lab-gate"',
        '"id": "phase12-virtio-net-segmented-rollout-boundary"',
    ],
    PHASE12_VIRTIO_NET_SURVEY_TEST_PATH: [
        'try std.testing.expectEqualStrings("P12-L04", manifest.lane_key);',
        'try std.testing.expectEqualStrings("Phase 12", manifest.phase);',
        'try std.testing.expectEqualStrings("drivers/net/virtio_net.c", manifest.anchor);',
        'if (std.mem.eql(u8, gap.id, "phase12-virtio-net-syntax-lab-gate")) {',
        'try std.testing.expectEqualStrings("zigux/tests/phase12_virtio_net_syntax_lab.zig", gap.zigux_destination);',
        'if (std.mem.eql(u8, gap.id, "phase12-virtio-net-segmented-rollout-boundary")) {',
    ],
    PHASE12_BUILD_PATH: [
        'const smoke_step = b.step("smoke", "Run Phase 12 direct driver and syntax-lab smoke tests");',
        'const test_step = b.step("test", "Run Phase 12 driver and survey tests");',
        "phase12_virtio_net_syntax_lab_module",
        "phase12_virtio_scsi_syntax_lab_module",
        "run_phase12_nvme_pci_verify_tests.step",
        "run_phase12_virtio_scsi_syntax_lab_tests.step",
        "phase12_libbpf_reviewability_module",
        "phase12_libbpf_snapshot_determinism_module",
        "run_phase12_libbpf_snapshot_determinism_tests.step",
    ],
    MAKEFILE_PATH: [
        "PHONY += phase12-smoke",
        "phase12-smoke:",
        "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
        "phase12-test:",
        "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
        "phase12: phase12-smoke phase12-test",
    ],
    WORKFLOW_PATH: [
        "Self-test Phase 12 build-only surface checker",
        "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "Check Phase 12 build-only surface",
        "python3 scripts/zigux/check-build-only-phase12-surface.py",
        "Run focused Phase 12 smoke shard",
        "make -C zigux phase12-smoke",
        "Run Phase 12 complex driver and libbpf tests",
        "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    ],
}

EXACT_COUNT_FILE_MARKERS = {
    DOCS_README_PATH: {
        DOCS_PHASE12_FREEZE_REMINDER_MARKER: 1,
        "`zigux/tests/phase12_virtio_net_manifest.json`": 1,
        "`zigux/tests/phase12_libbpf_manifest.json`": 1,
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`": 1,
        "`zigux/tests/phase12_virtio_scsi_manifest.json`": 1,
    },
    SCRIPTS_README_PATH: {
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`": 1,
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`": 1,
        "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`": 1,
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`": 1,
        "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`": 1,
        "`make -C zigux phase12-smoke`": 1,
        "`make -C zigux phase12`": 1,
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`": 1,
        "`zigux/tests/phase12_virtio_scsi_manifest.json`": 1,
    },
    TESTS_README_PATH: {
        "`Documentation/zigux/freeze-map.md` visible beside `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, and the shipped smoke-first replay order so queueing, throughput, rollback, and recovery wording stays below frozen `net/core/skbuff.c` and boundary-study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c`, and so the shared libbpf ownership split does not blur back into the driver-only lanes": 1,
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`": 1,
        "`make -C zigux phase12-smoke`": 1,
        "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`": 1,
        "`make -C zigux phase12`": 1,
    },
    REVIEW_CHECKLIST_PATH: {
        "`zigux/tests/phase12_virtio_net_manifest.json`": 1,
        "`zigux/tests/phase12_libbpf_manifest.json`": 1,
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`": 1,
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`": 1,
        "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`": 1,
    },
    PHASE12_RAW_GITHUB_COVERAGE_PATH: {
        "`PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`": 1,
        "`PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`": 1,
        "PHASE12_SHARED_SMOKE_SURFACE_COUNT=6": 1,
        "current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`": 1,
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`": 1,
        "`make -C zigux phase12-smoke`": 1,
        "`make -C zigux phase12`": 1,
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, deterministic libbpf artifact companions, and smoke-set summary remain reviewable together without turning this survey into a second sequencing document.": 1,
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and the direct PMO drift-control reruns are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` plus `python3 scripts/zigux/check-build-only-phase12-surface.py` before or beside the workflow-backed replay in `.github/workflows/zigux-bootstrap.yml`, so this shared fallback-overview wording stays aligned with the shipped PMO release packet.": 1,
        "PHASE12_LIBBPF_TRACKED_HELPER_COUNT=5": 1,
    },
    PHASE12_COORDINATION_MATRIX_PATH: {
        "PHASE12_RELEASE_CLOSED=no": 1,
    },
    VIRTIO_SCSI_FALLBACK_PATH: {
        "## Current Verification Evidence": 1,
        "`PHASE12_TREE_VIEW_COUNT=19`": 1,
        "`PHASE12_RAW_VIEW_COUNT=19`": 1,
        "`PHASE12_VERIFIED_FILE_COUNT=19`": 1,
        "- `drivers/scsi/virtio_scsi.zig`: `5f76c9e23a470545238df3ec10db60b91ab12786`": 1,
        "- `Documentation/zigux/phase12-virtio-scsi-survey.md`: `73269ae39f8381b9ea3b559ecdbe9ec09b9886d1`": 1,
        "- `zigux/tests/phase12_virtio_scsi_manifest.json`: `30b6878de70003eb2f893cb3b16b65441017dbc7`": 1,
        "- `zigux/Makefile`: `06d4605ed21ec25e9c6793d0a713b72852ad1822`": 1,
    },
    PHASE12_VIRTIO_SCSI_SLICE_PATH: {
        "records one bounded request-queue restart summary": 1,
        "records one bounded request-queue ownership summary": 1,
        "records one bounded recovery event-rearm summary": 1,
        "records one bounded recovery rollback summary": 1,
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-smoke` rerun this bounded `virtio scsi` starter before the broader survey-backed replay": 1,
    },
}

FORBIDDEN_TEXT_MARKERS = {
    DOCS_README_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
    PHASE12_CLOSURE_CHECKLIST_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
    PHASE12_RELEASE_READINESS_SURVEY_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
    PHASE12_RAW_GITHUB_COVERAGE_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
    PHASE12_COORDINATION_MATRIX_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
    SCRIPTS_README_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
    TESTS_README_PATH: [
        "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.zig`",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_content(rel_path: str, markers: list[str]) -> str:
    title = Path(rel_path).name
    lines = [f"# fixture:{title}"]
    lines.extend(f"- {marker}" for marker in markers)
    return "\n".join(lines) + "\n"


def write_fixture_tree(root: Path) -> None:
    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        combined_markers = list(markers)
        for marker in EXACT_COUNT_FILE_MARKERS.get(rel_path, {}):
            if marker not in combined_markers:
                combined_markers.append(marker)
        write(root, rel_path, fixture_content(rel_path, combined_markers))


def mutation_label(rel_path: str, marker: str) -> str:
    stem = Path(rel_path).stem.replace(".", "-")
    compact = marker.replace("`", "").replace('"', "").replace("'", "")
    compact = compact.replace("<", "").replace(">", "")
    compact = compact.replace("/", "-").replace(" ", "-")
    compact = compact.replace("(", "").replace(")", "")
    compact = compact.replace(":", "").replace(",", "")
    compact = compact.replace(".", "-").replace("*", "star")
    compact = compact.replace("+", "plus").replace("=", "eq")
    compact = compact[:56].strip("-")
    return f"{stem}-{compact or 'marker'}-guard"


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_FILE_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    for rel_path in FORBIDDEN_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    for pattern in FORBIDDEN_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                failures.append(f"unexpected_file:{path.relative_to(root)}")

    if failures:
        return failures

    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel_path}:{marker}")

    for rel_path, markers in EXACT_COUNT_FILE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker, expected_count in markers.items():
            actual_count = text.count(marker)
            if actual_count != expected_count:
                failures.append(
                    f"{rel_path}:{marker}:expected={expected_count}:actual={actual_count}"
                )

    for rel_path, markers in FORBIDDEN_TEXT_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                failures.append(f"{rel_path}:forbidden_marker:{marker}")

    return failures


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase12-build-only-surface-") as tmp:
        root = Path(tmp)
        write_fixture_tree(root)

        failures = validate(root)
        if failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

        for rel_path, markers in REQUIRED_FILE_MARKERS.items():
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            for marker in markers:
                broken = original.replace(marker, "")
                path.write_text(broken, encoding="utf-8")
                failures = validate(root)
                expected = f"{rel_path}:{marker}"
                if expected not in failures:
                    print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
                    print(mutation_label(rel_path, marker))
                    for failure in failures:
                        print(failure)
                    return 1
                path.write_text(original, encoding="utf-8")
                case_count += 1

        for rel_path, markers in EXACT_COUNT_FILE_MARKERS.items():
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            for marker, expected_count in markers.items():
                path.write_text(
                    original + f"- duplicate {marker}\n",
                    encoding="utf-8",
                )
                failures = validate(root)
                expected_exact_count = (
                    f"{rel_path}:{marker}:expected={expected_count}:actual={expected_count + 1}"
                )
                if expected_exact_count not in failures:
                    print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
                    print(mutation_label(rel_path, marker))
                    for failure in failures:
                        print(failure)
                    return 1
                path.write_text(original, encoding="utf-8")
                case_count += 1

        for rel_path, markers in FORBIDDEN_TEXT_MARKERS.items():
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            for marker in markers:
                path.write_text(original + f"- stale {marker}\n", encoding="utf-8")
                failures = validate(root)
                expected = f"{rel_path}:forbidden_marker:{marker}"
                if expected not in failures:
                    print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
                    print(mutation_label(rel_path, marker))
                    for failure in failures:
                        print(failure)
                    return 1
                path.write_text(original, encoding="utf-8")
                case_count += 1

        missing_required = root / PHASE12_CLOSURE_CHECKLIST_PATH
        missing_required.unlink()
        failures = validate(root)
        expected_missing = f"missing_file:{PHASE12_CLOSURE_CHECKLIST_PATH}"
        if failures != [expected_missing]:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("phase12-release-closure-checklist-missing-file-guard")
            for failure in failures:
                print(failure)
            return 1
        write(
            root,
            PHASE12_CLOSURE_CHECKLIST_PATH,
            fixture_content(
                PHASE12_CLOSURE_CHECKLIST_PATH,
                REQUIRED_FILE_MARKERS[PHASE12_CLOSURE_CHECKLIST_PATH],
            ),
        )
        case_count += 1

        forbidden_file = FORBIDDEN_FILES[0]
        write(root, forbidden_file, "# forbidden fixture\n")
        failures = validate(root)
        expected_forbidden = f"unexpected_file:{forbidden_file}"
        if failures != [expected_forbidden]:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("phase12-validate-file-forbidden-guard")
            for failure in failures:
                print(failure)
            return 1
        (root / forbidden_file).unlink()
        case_count += 1

        forbidden_glob = "scripts/zigux/check-phase12-temporary.py"
        write(root, forbidden_glob, "# forbidden glob fixture\n")
        failures = validate(root)
        expected_glob = f"unexpected_file:{forbidden_glob}"
        if failures != [expected_glob]:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("phase12-checker-glob-forbidden-guard")
            for failure in failures:
                print(failure)
            return 1
        (root / forbidden_glob).unlink()
        case_count += 1

    print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    print(f"PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the shared Phase 12 build-only review surface.")
    parser.add_argument("root", nargs="?", default=ROOT, type=Path, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_BUILD_ONLY_SURFACE=fail")
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_END")
        return 1

    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(f"PHASE12_BUILD_ONLY_SURFACE_MARKER_COUNT={sum(len(v) for v in REQUIRED_FILE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

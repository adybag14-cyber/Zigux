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
PHASE12_LIBBPF_SEGMENT_SURVEY_PATH = (
    "Documentation/zigux/phase12-libbpf-segment-survey.md"
)
PHASE12_LIBBPF_VERIFY_SHARD_NOTE_PATH = (
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
)
PHASE12_VIRTIO_SCSI_SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
PHASE12_VIRTIO_SCSI_SURVEY_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
LIBBPF_SNAPSHOT_DETERMINISM_PATH = (
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
)
PHASE12_VIRTIO_SCSI_FIXTURE_MANIFEST_PATH = (
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"
)
PHASE12_VIRTIO_SCSI_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
PHASE12_VIRTIO_SCSI_SURVEY_TEST_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py"
)
SCRIPTS_README_PATH = "scripts/zigux/README.md"
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
    PHASE12_LIBBPF_SEGMENT_SURVEY_PATH,
    PHASE12_LIBBPF_VERIFY_SHARD_NOTE_PATH,
    PHASE12_VIRTIO_SCSI_SLICE_PATH,
    PHASE12_VIRTIO_SCSI_SURVEY_PATH,
    LIBBPF_SNAPSHOT_PATH,
    LIBBPF_SNAPSHOT_DETERMINISM_PATH,
    PHASE12_VIRTIO_SCSI_FIXTURE_MANIFEST_PATH,
    PHASE12_VIRTIO_SCSI_MANIFEST_PATH,
    PHASE12_VIRTIO_SCSI_SURVEY_TEST_PATH,
    BUILD_ONLY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH,
    SCRIPTS_README_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "keep the bounded Phase 12 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle instead of letting the docs root drift away from the active-not-closed release packet on current `master`.",
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, and `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns on current `master`.",
        "current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.",
        "keep the degraded rerun order honest here too: rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile` before attached-Zig rerun vocabulary, and if that local fallback is absent keep `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` framed only as last-resort rerun vocabulary while `make -C zigux phase12-validate` remains reminder-only text.",
        "keep the bounded driver-family split explicit here too: the shared route stays the five-file `virtio_net` smoke-and-test quintet in `zigux/tests/phase12_build.zig`, `virtio_scsi` remains the rollback-lab packet through its dedicated survey companions outside the shared route, `nvme_pci` remains the bounded driver-local foothold outside the shared route, and the parked libbpf packet stays tied to `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being promoted into a focused shared replay claim.",
    ],
    FREEZE_MAP_PATH: [
        "- `net/core/skbuff.c`",
        "- `kernel/workqueue.c`",
        "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`",
        "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while `make -C zigux phase12-validate` remains reminder-only vocabulary",
        "keep the repo-local `.zig-toolchain` fallback before the attached-Zig degraded rerun order explicit",
        "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
        "keep the bounded release packet below DMA, queue-restart, throughput, or deeper transport claims until fresh current-`master` proof lands?",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "The route story on current `master` is split rather than absent: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again, but it still does not provide `phase12-validate`.",
        "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
        "`zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig` after the shared `phase12-smoke` and `phase12-test` reruns, but that throughput-parity anchor still belongs to the adjacent bounded `virtio_net` packet rather than to the shared PMO release route.",
        "`zigux/tests/fixtures/phase12_libbpf_snapshot.json` remains the parked visibility anchor for the note-owned libbpf reviewability packet on current `master`, while `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remains the helper-local determinism companion for directly readable `tools/lib/bpf/zigux_segments/pin_path.zig`",
        "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py`, while `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` remain absent on current `master`; keep that storage-facing rollback-evidence packet adjacent to the shared route rather than treating it as shared `smoke` or `test` build output.",
    ],
    RELEASE_SEQUENCING_PATH: [
        "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
        "readiness-note support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`",
        "Current repo-reality override: `zigux/Makefile` still omits `phase12-validate` on current `master`, but it now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` wrappers again.",
        "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
        "keep the reminder-only `make -C zigux phase12-validate` vocabulary explicit ahead of the shipped wrapper reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
        "Keep the degraded-workflow validator-side support bundle explicit beside that same order too:",
        "  * `scripts/zigux/validate-phase12.py`",
        "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig`, because those are the five files the current `smoke` step actually runs.",
        "Current `zigux/tests/phase12_build.zig` wires that same five-file bounded `virtio_net` follow-up quintet through both `smoke` and `test`, so the shared release packet should keep those bounded queue-resume, receive-refill replay, transmit-disposition, post-reset replay, and throughput-parity replays explicit without rounding them up into live interrupt-backed transmit completion parity, queue-restart parity, or transport-backed throughput delivery.",
        "The broader starter-present `virtio_net` direct and syntax-lab packet, the driver-local `virtio_scsi` rollback-lab packet, and the published-but-still-unwired NVMe foothold remain adjacent review surfaces in the PMO note set, but they are not wired shared `smoke` or `test` build outputs in current `zigux/tests/phase12_build.zig`.",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
        "The directly readable validator-first support bundle still reruns as `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `python3 scripts/zigux/validate-phase12.py`; keep `make -C zigux phase12-validate` here only as reminder-only wrapper vocabulary until `zigux/Makefile` rematerializes that route on current `master`.",
        "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence and still omits `phase12-validate`.",
        "The shared smoke-first replay packet still stays wired through `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`; treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped wrapper evidence again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.",
        "The active shared build packet on current `master` is the five-file `virtio_net` follow-up quintet wired through `zigux/tests/phase12_build.zig`: `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig`.",
        "If `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
        "attached-Zig rerun vocabulary only until the wrapper returns: `make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "attached-Zig rerun vocabulary only until the wrapper returns: `make -C zigux phase12-test ZIG=<attached-zig-path>`",
        "attached-Zig rerun vocabulary only until the wrapper returns: `make -C zigux phase12 ZIG=<attached-zig-path>`",
        "The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required before the shared release packet can be described as ready for closure review.",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
        "`zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-smoke`, `phase12-test`, and `phase12` on `master` while still omitting `phase12-validate`",
        "Shared fallback and anti-overlap packet: keep `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, and `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` aligned with the same active smoke-first packet, the same one-catalog plus one-gap-note plus two-anchor fallback split, and the same release-planning-only boundary.",
        "`.github/workflows/zigux-bootstrap.yml` still runs `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig` after the shared `phase12-smoke` and `phase12-test` reruns, but that workflow-only throughput-parity anchor remains adjacent bounded `virtio_net` evidence rather than shared PMO route proof.",
        "the shipped packet-local `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py` guard,",
        "The active shared build packet is the returned five-file `virtio_net` quintet only:",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "It is a compact fallback overview, not a new replay surface and not a commit-pinned artifact itself.",
        "  * current contents-bridge shared support bundle during degraded contents reads:",
        "    * `scripts/zigux/validate-phase12.py`",
        "    * `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "    * `.github/workflows/zigux-bootstrap.yml`",
        "    * `scripts/zigux/README.md`",
        "    * `zigux/Makefile`",
        "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime",
        "This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-smoke`, `phase12-test`, and `phase12` again, while `phase12-validate` is still absent, so only `make -C zigux phase12-validate` stays reminder vocabulary while `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are current wrapper proof on `master`.",
        "The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, while only `make -C zigux phase12-validate` stays documented as shared reminder text until that wrapper returns on current `master`.",
        "Keep the current direct-read bridge split explicit too: fresh repo-first readback now returns `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` on current `master`. The readable build file currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig` through the shared `smoke` and `test` steps, and the readable Makefile now exposes `phase12-smoke`, `phase12-test`, and `phase12` even though `phase12-validate` is still missing, so that checker-plus-validator-plus-workflow-plus-scripts-plus-Makefile-plus-build-file set stays direct support evidence only rather than proof for the larger starter-present `virtio_net`, rollback-lab `virtio_scsi`, or driver-local NVMe packet.",
        "keep the shared-build coverage explicit too: `zigux/tests/phase12_build.zig` currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, and `zigux/tests/phase12_virtio_net_throughput_parity.zig` through shared `smoke` and `test`, so this anti-overlap note should track all five shared-route proofs instead of reviving the older four-replay split",
        "keep those five `virtio_net` follow-ups framed as bounded queue-resume, receive-refill replay, transmit-disposition, post-reset replay, and throughput-parity reviewability inside the shared packet rather than as live DMA-safe receive ownership, queue restart parity, transport-backed queue flow, or completion-path parity",
    ],
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: [
        "- `PHASE12_LANE=libbpf-heavy-consumer-shared-release-packet`",
        "- Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-smoke`, `phase12-test`, and `phase12` on current `master` while still omitting `phase12-validate`, so keep only `make -C zigux phase12-validate` here as reminder vocabulary and keep the directly readable support bundle explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `scripts/zigux/validate-phase12.py` beside the returned smoke-and-test wrappers.",
        "- The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.",
    ],
    PHASE12_LIBBPF_SEGMENT_SURVEY_PATH: [
        "the shared shipped replay order is still narrower than that mixed direct-plus-parked libbpf packet.",
        "`scripts/zigux/check-build-only-phase12-surface.py` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.",
        "current `master` now also ships the validator-side support bundle through `scripts/zigux/check-phase12-release-readiness-packet.py` and `scripts/zigux/validate-phase12.py`, while `make -C zigux phase12-validate` remains reminder-only vocabulary because current `zigux/Makefile` still omits that wrapper;",
    ],
    PHASE12_LIBBPF_VERIFY_SHARD_NOTE_PATH: [
        "- shared survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`",
        "- snapshot checker: `scripts/zigux/check-phase12-libbpf-snapshot.py`",
        "- the current validator-first support bundle remains separate: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and the reminder-only wrapper name `make -C zigux phase12-validate` keep the shared release packet fail-closed without turning this parked note into a second direct replay route, while the returned `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` wrappers stay evidence for the broader shared smoke-first packet rather than proof for this parked note by themselves`",
    ],
    PHASE12_VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH: [
        "PHASE12_CHECK_PACKET=virtio_scsi_libbpf_boundary",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate` stays reminder-only vocabulary until the wrapper returns on current `master`",
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
        "keep the repo-local `.zig-toolchain` then attached-Zig degraded rerun order explicit here too: rely on the Makefile fallback first, then name `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` only as last-resort rerun vocabulary while `make -C zigux phase12-validate` remains reminder-only text",
    ],
    VALIDATOR_PATH: [
        "RELEASE_READINESS_CHECKER_PATH",
        "BUILD_ONLY_CHECKER_PATH",
        "make -C zigux phase12-validate",
        "stale reminder vocabulary",
        "scripts-side support packet",
    ],
    MAKEFILE_PATH: [
        "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
    TESTS_README_PATH: [
        "Keep `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` explicit as the shipped shared support bundle so the tests-root summary does not undercount the dedicated release-readiness checker.",
        "Current `master` keeps the shared Phase 12 rerun story split rather than absent: `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.",
        "Keep `Documentation/zigux/phase12-raw-github-coverage-survey.md` explicit as the shared degraded-read companion so the tests-root reminder stays aligned with the same one-catalog plus one-current-master-gap-note companion plus shared-support-bundle fallback split already named by the PMO release packet.",
        "Keep `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` explicit as the shared anti-overlap companion so the tests-root reminder stays aligned with the same complex-driver packet boundary already named by the release-order, closure, coordination, and fallback notes.",
        "Keep `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` explicit as the shared heavy-helper anti-overlap companion so the tests-root reminder stays aligned with the same parked libbpf boundary already named by the release-order, closure, readiness, coordination, fallback, and complex-driver notes.",
        "keep the degraded rerun order honest by relying on the repo-local `.zig-toolchain` fallback in `zigux/Makefile` before the attached-Zig `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` vocabulary.",
        "Keep `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` explicit as the current shared smoke-first build gate, while `virtio_net` remains the split-helper queue-resume, receive-refill replay, transmit-recycle, post-reset replay, and throughput-parity shared packet, `virtio_scsi` remains the driver-local rollback-lab packet outside the shared smoke-and-test route, and `nvme_pci` stays driver-local outside the shared smoke-and-test route.",
        "Keep the bounded packet split explicit here too: `virtio_net` remains the split-helper shared smoke-and-test quintet, `virtio_scsi` remains the driver-local rollback-lab packet outside the shared smoke-and-test route, and `nvme_pci` stays driver-local outside the shared smoke-and-test route.",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 build-only surface checker",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Check current Phase 12 build-only surface",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py",
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Check current Phase 12 release-readiness packet",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
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

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ]
}

EXACT_LINE_MARKER_PATHS = {
    WORKFLOW_PATH,
}

EXACT_COUNT_MARKERS = {
    DOCS_README_PATH: {
        "current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`, so keep the shared build gate explicit from the docs root too.": 1,
    },
    RELEASE_READINESS_SURVEY_PATH: {
        "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.": 1,
    },
    RELEASE_CLOSURE_CHECKLIST_PATH: {
        "The directly readable validator-first support bundle still reruns as `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `python3 scripts/zigux/validate-phase12.py`; keep `make -C zigux phase12-validate` here only as reminder-only wrapper vocabulary until `zigux/Makefile` rematerializes that route on current `master`.": 1,
        "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence and still omits `phase12-validate`.": 1,
    },
    RELEASE_COORDINATION_MATRIX_PATH: {
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`": 1,
        "the shipped packet-local `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py` guard,": 1,
    },
    RAW_GITHUB_COVERAGE_SURVEY_PATH: {
        "  * current contents-bridge shared support bundle during degraded contents reads:": 1,
        "    * `scripts/zigux/validate-phase12.py`": 1,
        "    * `scripts/zigux/check-phase12-release-readiness-packet.py`": 1,
        "    * `.github/workflows/zigux-bootstrap.yml`": 1,
        "    * `scripts/zigux/README.md`": 1,
        "    * `zigux/Makefile`": 1,
        "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime": 1,
    },
    SCRIPTS_README_PATH: {
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`": 1,
    },
    TESTS_README_PATH: {
        "Keep `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` explicit as the shipped shared support bundle so the tests-root summary does not undercount the dedicated release-readiness checker.": 1,
        "Current `master` keeps the shared Phase 12 rerun story split rather than absent: `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.": 1,
        "Keep `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` explicit as the shared heavy-helper anti-overlap companion so the tests-root reminder stays aligned with the same parked libbpf boundary already named by the release-order, closure, readiness, coordination, fallback, and complex-driver notes.": 1,
    },
}


def has_required_marker(rel_path: str, text: str, marker: str) -> bool:
    if rel_path in EXACT_LINE_MARKER_PATHS:
        return marker in [line.lstrip() for line in text.splitlines()]
    return marker in text


def count_marker_occurrences(rel_path: str, text: str, marker: str) -> int:
    if rel_path in EXACT_LINE_MARKER_PATHS:
        return sum(1 for line in text.splitlines() if line.lstrip() == marker)
    return text.count(marker)


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
            if not has_required_marker(rel_path, text, marker):
                failures.append(f"missing_marker:{rel_path}:{marker}")
    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker, expected_count in markers.items():
            actual_count = count_marker_occurrences(rel_path, text, marker)
            if actual_count != expected_count:
                failures.append(
                    "wrong_count:"
                    f"{rel_path}:{marker}:expected={expected_count}:actual={actual_count}"
                )

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

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
            PHASE12_LIBBPF_SEGMENT_SURVEY_PATH: "# Phase 12 Libbpf Segment Survey",
            PHASE12_LIBBPF_VERIFY_SHARD_NOTE_PATH: "# Phase 12 Libbpf Verify Shard Note",
            SCRIPTS_README_PATH: "# scripts/zigux",
            TESTS_README_PATH: "# zigux/tests",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path in {
            VALIDATOR_PATH,
            MAKEFILE_PATH,
            WORKFLOW_PATH,
        }:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path in {
        LIBBPF_SNAPSHOT_PATH,
        PHASE12_VIRTIO_SCSI_FIXTURE_MANIFEST_PATH,
        PHASE12_VIRTIO_SCSI_MANIFEST_PATH,
    }:
        return '{\n  "lane_key": "P12-L16"\n}\n'
    if rel_path == LIBBPF_SNAPSHOT_DETERMINISM_PATH:
        return '{\n  "lane_key": "P12-L16",\n  "kind": "determinism"\n}\n'
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".yml"):
        return "name: zigux-bootstrap\n"
    if rel_path.endswith(".json"):
        return "{}\n"
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
        marker_cases = [(rel_path, marker) for rel_path, markers in REQUIRED_MARKERS.items() for marker in markers]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")
        exact_count_cases = [(rel_path, marker, expected_count) for rel_path, markers in EXACT_COUNT_MARKERS.items() for marker, expected_count in markers.items()]
        for rel_path, marker, expected_count in exact_count_cases:
            write_fixture_tree(base)
            write_text(base / rel_path, (base / rel_path).read_text(encoding="utf-8") + marker + "\n")
            expect_failure(base, "wrong_count:" f"{rel_path}:{marker}:expected={expected_count}:actual={expected_count + 1}")
        forbidden_cases = [(MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][0]), (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][1])]
        for rel_path, marker in forbidden_cases:
            write_fixture_tree(base)
            write_text(base / rel_path, (base / rel_path).read_text(encoding="utf-8") + marker + "\n")
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")
        case_count = (
            len(missing_file_cases)
            + len(marker_cases)
            + len(exact_count_cases)
            + len(forbidden_cases)
        )
        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
        print(f"PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=("Validate the current narrow Phase 12 release-readiness support bundle around the release notes, shared reminder surfaces, degraded fallback wording, and shared Makefile routes."))
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate. Defaults to the script directory.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
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
    print("PHASE12_RELEASE_READINESS_PACKET_REQUIRED_MARKER_COUNT=" f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    print("PHASE12_RELEASE_READINESS_PACKET_FORBIDDEN_MARKER_COUNT=" f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}")
    print("PHASE12_RELEASE_READINESS_PACKET_EXACT_COUNT_MARKER_COUNT=" f"{sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "scripts/zigux/README.md").exists() and (candidate / ".github/workflows/zigux-bootstrap.yml").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SCRIPTS_README_PATH = "scripts/zigux/README.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
PHASE12_RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
PHASE12_RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
PHASE12_RELEASE_CLOSURE_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
PHASE12_RELEASE_COORDINATION_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
PHASE12_COMPLEX_DRIVER_LANE_PATH = "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
PHASE12_LIBBPF_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
PHASE12_LIBBPF_VERIFY_SHARD_NOTE_PATH = "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
PHASE12_RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
PHASE12_LIBBPF_VERIFY_PATH = "tools/lib/bpf/zigux_segments/verify.zig"

REQUIRED_PHASE12_PATHS = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    FREEZE_MAP_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    PHASE12_RELEASE_SEQUENCING_PATH,
    PHASE12_RELEASE_CLOSURE_PATH,
    PHASE12_RELEASE_READINESS_PATH,
    PHASE12_RELEASE_COORDINATION_PATH,
    PHASE12_COMPLEX_DRIVER_LANE_PATH,
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH,
    PHASE12_RAW_GITHUB_COVERAGE_PATH,
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    PHASE12_LIBBPF_SURVEY_PATH,
    PHASE12_LIBBPF_VERIFY_SHARD_NOTE_PATH,
    "drivers/nvme/host/pci_verify.zig",
    PHASE12_BUILD_PATH,
    "zigux/tests/phase12_nvme_pci.zig",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
    "zigux/tests/phase12_libbpf_snapshot_determinism.zig",
    PHASE12_LIBBPF_VERIFY_PATH,
    "tools/lib/bpf/zigux_segments/manifest.json",
]

FORBIDDEN_PHASE12_PATHS = [
    "scripts/zigux/validate-phase12.py",
    "scripts/zigux/check-phase12-build-inventory.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "zigux/tests/phase12_cross_build.zig",
]

PHASE12_REMOVED_SURFACE_MARKER = (
    "without implying removed `validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, "
    "cross-build, or `phase12-validate` surfaces that are not on `master`."
)
PHASE12_DOCS_ARTIFACT_MARKER = (
    "only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and "
    "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned artifacts, "
    "while `virtio_net` and `libbpf` remain shared-tree-only anchors rather than implied fallback maps."
)
PHASE12_DOCS_REMOVED_VALIDATOR_MARKER = (
    "there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target "
    "on `master`; future Phase 12 reviewability claims should name only shipped survey, build, and make "
    "surfaces until new validator files actually land."
)
PHASE12_REVIEW_CHECKLIST_MARKER = (
    "without implying removed `validate-phase12.py`, `check-phase12-*.py`, raw-coverage, or focused-libbpf-only "
    "replay surfaces that are not on `master`?"
)
PHASE12_FREEZE_MAP_MARKER = (
    "queueing, throughput, rollback, and recovery wording there must stay bounded to driver-local review evidence, "
    "lab-only reversible-delivery scaffolding, and shared anti-overlap notes without implying active delivery "
    "against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`"
)
PHASE12_RELEASE_SEQUENCING_CHECKER_INTRO_MARKER = (
    "Keep the degraded-workflow checker pair explicit beside that same order too:"
)
PHASE12_RELEASE_SEQUENCING_CHECKER_SELF_TEST_MARKER = (
    "- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`"
)
PHASE12_RELEASE_SEQUENCING_CHECKER_RUN_MARKER = (
    "- `python3 scripts/zigux/check-build-only-phase12-surface.py`"
)
PHASE12_RELEASE_SEQUENCING_FALLBACK_SPLIT_MARKER = (
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md` is the compact reminder for that two-versus-two split and should stay aligned with this note whenever fallback wording changes."
)
PHASE12_RELEASE_SEQUENCING_UNSHIPPED_ROUTE_MARKER = (
    "There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route on current `master`, so this sequencing note must keep naming only the shipped checker pair, smoke shard, full test replay, and Linux-style `phase12` route."
)
PHASE12_RELEASE_READINESS_CHECKER_MARKER = (
    "Keep the same degraded-workflow validation pair explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` "
    "and `python3 scripts/zigux/check-build-only-phase12-surface.py` should run before or beside those attached-toolchain Make reruns "
    "so build-only contract drift still fails closed when the local runtime needs the fallback path."
)
PHASE12_RELEASE_READINESS_FALLBACK_SPLIT_MARKER = (
    "The public fallback split must stay explicit: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` "
    "and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are the only commit-pinned fallback artifacts, "
    "while `virtio_net` and `libbpf` remain shared-tree-only anchors."
)
PHASE12_RELEASE_READINESS_RAW_READ_ANCHOR_MARKER = (
    "During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and "
    "`scripts/zigux/check-build-only-phase12-surface.py` remain the shared-tree anchors for the smoke-first packet, "
    "so fallback wording should keep them visible without promoting them into extra commit-pinned artifacts."
)
PHASE12_RELEASE_READINESS_VERIFY_SHARD_MARKER = (
    "Current `master` already keeps the compact release-coordination matrix explicit about the dedicated verify-shard companion, and the shared release-sequencing note now does the same, so the next honest same-lane follow-through is whichever remaining one-file shared reminder drifts next while keeping the smoke-first replay packet, the checker pair, the verify-shard companion, and the two-versus-two fallback split aligned without overstating closure."
)
PHASE12_RELEASE_CLOSURE_REPLAY_BOUNDARY_MARKER = (
    "It is not a closure claim, and it is not itself a shipped replay surface."
)
PHASE12_RELEASE_CLOSURE_VERIFY_SHARD_MARKER = (
    "  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`"
)
PHASE12_RELEASE_CLOSURE_FALLBACK_MARKER = (
    "shared fallback overview note: `Documentation/zigux/phase12-raw-github-coverage-survey.md` keeps the mixed raw-read split explicit and must stay aligned with the two commit-pinned fallback artifacts without being treated as a third commit-pinned fallback artifact"
)
PHASE12_RELEASE_CLOSURE_UNSHIPPED_ROUTE_MARKER = (
    "There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, or `make -C zigux phase12-validate` route on `master`."
)
PHASE12_RELEASE_CLOSURE_ATTACHED_TOOLCHAIN_MARKER = (
    "That reread must keep the attached-toolchain override explicit as part of the shipped smoke-first order whenever `zig` is unavailable on `PATH`."
)
PHASE12_RELEASE_COORDINATION_FALLBACK_MARKER = (
    "rule: keep this two-versus-two split explicit in PMO release wording and do not promote the shared-tree anchors into commit-pinned fallback artifacts unless new dedicated files actually land"
)
PHASE12_RELEASE_COORDINATION_VERIFY_SHARD_MARKER = (
    "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`"
)
PHASE12_RELEASE_COORDINATION_UNSHIPPED_ROUTE_MARKER = (
    "There is still no shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route on current `master`, so release-planning notes should keep naming only the shipped smoke-first packet and the build-only checker."
)
PHASE12_COMPLEX_DRIVER_LANE_TRUTHFULNESS_MARKER = (
    "Shared-packet follow-through here should prefer one-file truthfulness repairs in `Documentation/zigux/README.md`, "
    "`Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, "
    "`Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, "
    "`Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, "
    "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, "
    "`scripts/zigux/README.md`, `zigux/tests/README.md`, or `scripts/zigux/check-build-only-phase12-surface.py` before reopening driver-local behavior."
)
PHASE12_COMPLEX_DRIVER_LANE_NEXT_STEP_MARKER = (
    "If this lane reopens soon, rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, then reread "
    "`Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, "
    "`Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, "
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, "
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the same smoke-first Phase 12 packet, "
    "the same checker pair, and the same two-versus-two fallback split."
)
PHASE12_LIBBPF_HEAVY_CONSUMER_PHASE8_MARKER = (
    "The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet."
)
PHASE12_LIBBPF_HEAVY_CONSUMER_MANIFEST_ONLY_MARKER = (
    "Keep the deterministic tracked-helper snapshot and reviewability wording explicit so the release-facing libbpf packet does not collapse back to manifest-only prose."
)
PHASE12_LIBBPF_SURVEY_FALLBACK_MARKER = (
    "public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this libbpf note is not a commit-pinned raw GitHub fallback artifact."
)
PHASE12_LIBBPF_SURVEY_ROLLBACK_MARKER = (
    "rollback owner and reversible-delivery drill: this shared survey packet rolls back by restoring the last truthful libbpf-survey wording in this note and then rerunning `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`"
)
PHASE12_LIBBPF_SURVEY_CLOSURE_MARKER = (
    "Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO closure companion when judging whether this shared-tree libbpf survey packet is close enough to describe the active Phase 12 tranche as release-closed."
)
PHASE12_LIBBPF_SURVEY_COORDINATION_MARKER = (
    "Keep `Documentation/zigux/phase12-release-coordination-matrix.md` visible beside that same PMO closure companion when judging whether the compact lane-owner split, fallback split, and smoke-set summary still match this shared-tree libbpf packet."
)
PHASE12_LIBBPF_SURVEY_DETERMINISM_MARKER = (
    "the deterministic Phase 12 tracked-helper snapshot still stays narrower than that shared bridge file"
)
PHASE12_RAW_GITHUB_COVERAGE_LIBBPF_ANTI_OVERLAP_MARKER = (
    "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes"
)
PHASE12_RAW_GITHUB_COVERAGE_DRIVER_ANTI_OVERLAP_MARKER = (
    "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion"
)

REQUIRED_SCRIPTS_README_MARKERS = [
    "Phase 12 flow",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    f"`{PHASE12_LIBBPF_VERIFY_SHARD_NOTE_PATH}`",
    "`zigux/tests/phase12_build.zig`",
    "`make -C zigux phase12-smoke`",
    "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
    PHASE12_REMOVED_SURFACE_MARKER,
]
REQUIRED_DOCS_README_MARKERS = [
    "Phase 12 notes -",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`tools/lib/bpf/zigux_segments/verify.zig`",
    "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
    PHASE12_DOCS_ARTIFACT_MARKER,
    PHASE12_DOCS_REMOVED_VALIDATOR_MARKER,
]
REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 12 complex-driver packet, do `Documentation/zigux/README.md`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    PHASE12_REVIEW_CHECKLIST_MARKER,
]
REQUIRED_FREEZE_MAP_MARKERS = [
    "the shared Phase 12 PMO release packet also stays release-planning-only beside",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    PHASE12_FREEZE_MAP_MARKER,
]
REQUIRED_PHASE12_RELEASE_SEQUENCING_MARKERS = [
    PHASE12_RELEASE_SEQUENCING_CHECKER_INTRO_MARKER,
    PHASE12_RELEASE_SEQUENCING_CHECKER_SELF_TEST_MARKER,
    PHASE12_RELEASE_SEQUENCING_CHECKER_RUN_MARKER,
    PHASE12_RELEASE_SEQUENCING_FALLBACK_SPLIT_MARKER,
    PHASE12_RELEASE_SEQUENCING_UNSHIPPED_ROUTE_MARKER,
]
REQUIRED_PHASE12_RELEASE_READINESS_MARKERS = [
    PHASE12_RELEASE_READINESS_CHECKER_MARKER,
    PHASE12_RELEASE_READINESS_FALLBACK_SPLIT_MARKER,
    PHASE12_RELEASE_READINESS_RAW_READ_ANCHOR_MARKER,
    PHASE12_RELEASE_READINESS_VERIFY_SHARD_MARKER,
]
REQUIRED_PHASE12_RELEASE_CLOSURE_MARKERS = [
    PHASE12_RELEASE_CLOSURE_REPLAY_BOUNDARY_MARKER,
    PHASE12_RELEASE_CLOSURE_VERIFY_SHARD_MARKER,
    PHASE12_RELEASE_CLOSURE_FALLBACK_MARKER,
    PHASE12_RELEASE_CLOSURE_UNSHIPPED_ROUTE_MARKER,
    PHASE12_RELEASE_CLOSURE_ATTACHED_TOOLCHAIN_MARKER,
]
REQUIRED_PHASE12_RELEASE_COORDINATION_MARKERS = [
    PHASE12_RELEASE_COORDINATION_FALLBACK_MARKER,
    PHASE12_RELEASE_COORDINATION_VERIFY_SHARD_MARKER,
    PHASE12_RELEASE_COORDINATION_UNSHIPPED_ROUTE_MARKER,
]
REQUIRED_PHASE12_COMPLEX_DRIVER_LANE_MARKERS = [
    PHASE12_COMPLEX_DRIVER_LANE_TRUTHFULNESS_MARKER,
    PHASE12_COMPLEX_DRIVER_LANE_NEXT_STEP_MARKER,
]
REQUIRED_PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_MARKERS = [
    PHASE12_LIBBPF_HEAVY_CONSUMER_PHASE8_MARKER,
    PHASE12_LIBBPF_HEAVY_CONSUMER_MANIFEST_ONLY_MARKER,
]
REQUIRED_PHASE12_LIBBPF_SURVEY_MARKERS = [
    PHASE12_LIBBPF_SURVEY_FALLBACK_MARKER,
    PHASE12_LIBBPF_SURVEY_ROLLBACK_MARKER,
    PHASE12_LIBBPF_SURVEY_CLOSURE_MARKER,
    PHASE12_LIBBPF_SURVEY_COORDINATION_MARKER,
    PHASE12_LIBBPF_SURVEY_DETERMINISM_MARKER,
]
REQUIRED_PHASE12_RAW_GITHUB_COVERAGE_MARKERS = [
    PHASE12_RAW_GITHUB_COVERAGE_LIBBPF_ANTI_OVERLAP_MARKER,
    PHASE12_RAW_GITHUB_COVERAGE_DRIVER_ANTI_OVERLAP_MARKER,
]
REQUIRED_TESTS_README_MARKERS = [
    "keep the shared Phase 12 complex-driver packet explicit in the tests root too:",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
    "`zigux/tests/phase12_libbpf_manifest.json`",
    f"`{PHASE12_LIBBPF_VERIFY_PATH}`",
    "`zigux/tests/phase12_libbpf_snapshot_determinism.zig`",
    "`make -C zigux phase12-smoke`",
    PHASE12_REMOVED_SURFACE_MARKER.rstrip("."),
]
REQUIRED_WORKFLOW_MARKERS = [
    "Self-test Phase 12 build-only surface checker",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "Check Phase 12 build-only surface",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "Run focused Phase 12 smoke shard",
    "make -C zigux phase12-smoke",
    "Run Phase 12 complex driver and libbpf tests",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
]
FORBIDDEN_WORKFLOW_MARKERS = [
    "Validate Phase 12 files",
    "python3 scripts/zigux/validate-phase12.py",
    "Run focused Phase 12 libbpf replay",
    "Run Phase 12 cross-build replay",
]
REQUIRED_MAKEFILE_MARKERS = [
    "phase12-smoke:",
    "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-smoke phase12-test",
]
FORBIDDEN_MAKEFILE_MARKERS = [
    "phase12-validate:",
    "phase12-libbpf-test:",
    "phase12-cross:",
]
REQUIRED_PHASE12_BUILD_MARKERS = [
    'b.path("phase12_virtio_net_syntax_lab.zig")',
    'b.path("phase12_virtio_scsi_syntax_lab.zig")',
    '.name = "phase12-virtio-net-syntax-lab-tests"',
    '.name = "phase12-virtio-scsi-syntax-lab-tests"',
    '.name = "phase12-libbpf-reviewability-tests"',
    '.name = "phase12-libbpf-snapshot-determinism-tests"',
    'const smoke_step = b.step("smoke", "Run Phase 12 direct driver and syntax-lab smoke tests");',
    'smoke_step.dependOn(&run_phase12_nvme_pci_tests.step);',
    'smoke_step.dependOn(&run_phase12_nvme_pci_verify_tests.step);',
    'smoke_step.dependOn(&run_phase12_virtio_net_tests.step);',
    'smoke_step.dependOn(&run_phase12_virtio_net_syntax_lab_tests.step);',
    'smoke_step.dependOn(&run_phase12_virtio_scsi_tests.step);',
    'smoke_step.dependOn(&run_phase12_virtio_scsi_syntax_lab_tests.step);',
    'const test_step = b.step("test", "Run Phase 12 driver and survey tests");',
    'test_step.dependOn(smoke_step);',
    'test_step.dependOn(&run_phase12_nvme_pci_survey_tests.step);',
    'test_step.dependOn(&run_phase12_virtio_net_survey_tests.step);',
    'test_step.dependOn(&run_phase12_virtio_scsi_survey_tests.step);',
    'test_step.dependOn(&run_phase12_libbpf_segments_tests.step);',
    'test_step.dependOn(&run_phase12_libbpf_segments_verify_tests.step);',
    'test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);',
    'test_step.dependOn(&run_phase12_libbpf_snapshot_determinism_tests.step);',
]

EXACT_COUNT_MAPS = {
    "scripts_readme": {PHASE12_REMOVED_SURFACE_MARKER: 1},
    "docs_readme": {
        PHASE12_DOCS_ARTIFACT_MARKER: 1,
        PHASE12_DOCS_REMOVED_VALIDATOR_MARKER: 1,
    },
    "review_checklist": {PHASE12_REVIEW_CHECKLIST_MARKER: 1},
    "freeze_map": {PHASE12_FREEZE_MAP_MARKER: 1},
    "phase12_release_sequencing": {
        PHASE12_RELEASE_SEQUENCING_CHECKER_INTRO_MARKER: 1,
        PHASE12_RELEASE_SEQUENCING_CHECKER_SELF_TEST_MARKER: 1,
        PHASE12_RELEASE_SEQUENCING_CHECKER_RUN_MARKER: 1,
        PHASE12_RELEASE_SEQUENCING_FALLBACK_SPLIT_MARKER: 1,
        PHASE12_RELEASE_SEQUENCING_UNSHIPPED_ROUTE_MARKER: 1,
    },
    "phase12_release_readiness": {
        PHASE12_RELEASE_READINESS_CHECKER_MARKER: 1,
        PHASE12_RELEASE_READINESS_FALLBACK_SPLIT_MARKER: 1,
        PHASE12_RELEASE_READINESS_RAW_READ_ANCHOR_MARKER: 1,
        PHASE12_RELEASE_READINESS_VERIFY_SHARD_MARKER: 1,
    },
    "phase12_release_closure": {
        PHASE12_RELEASE_CLOSURE_REPLAY_BOUNDARY_MARKER: 1,
        PHASE12_RELEASE_CLOSURE_VERIFY_SHARD_MARKER: 1,
        PHASE12_RELEASE_CLOSURE_FALLBACK_MARKER: 1,
        PHASE12_RELEASE_CLOSURE_UNSHIPPED_ROUTE_MARKER: 1,
        PHASE12_RELEASE_CLOSURE_ATTACHED_TOOLCHAIN_MARKER: 1,
    },
    "phase12_release_coordination": {
        PHASE12_RELEASE_COORDINATION_FALLBACK_MARKER: 1,
        PHASE12_RELEASE_COORDINATION_VERIFY_SHARD_MARKER: 1,
        PHASE12_RELEASE_COORDINATION_UNSHIPPED_ROUTE_MARKER: 1,
    },
    "phase12_complex_driver_lane": {
        PHASE12_COMPLEX_DRIVER_LANE_TRUTHFULNESS_MARKER: 1,
        PHASE12_COMPLEX_DRIVER_LANE_NEXT_STEP_MARKER: 1,
    },
    "phase12_libbpf_heavy_consumer_lane": {
        PHASE12_LIBBPF_HEAVY_CONSUMER_PHASE8_MARKER: 1,
        PHASE12_LIBBPF_HEAVY_CONSUMER_MANIFEST_ONLY_MARKER: 1,
    },
    "phase12_libbpf_survey": {
        PHASE12_LIBBPF_SURVEY_FALLBACK_MARKER: 1,
        PHASE12_LIBBPF_SURVEY_ROLLBACK_MARKER: 1,
        PHASE12_LIBBPF_SURVEY_CLOSURE_MARKER: 1,
        PHASE12_LIBBPF_SURVEY_COORDINATION_MARKER: 1,
    },
    "phase12_raw_github_coverage": {
        PHASE12_RAW_GITHUB_COVERAGE_LIBBPF_ANTI_OVERLAP_MARKER: 1,
        PHASE12_RAW_GITHUB_COVERAGE_DRIVER_ANTI_OVERLAP_MARKER: 1,
    },
    "tests_readme": {PHASE12_REMOVED_SURFACE_MARKER.rstrip("."): 1},
    "phase12_build": {
        "b.addTest(.{": 13,
        "smoke_step.dependOn(": 6,
        "test_step.dependOn(": 8,
    },
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def ensure_absent(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            failures.append(f"{label}_forbidden:{marker}")


def ensure_exact_counts(failures: list[str], label: str, text: str, expected_counts: dict[str, int]) -> None:
    for marker, expected in expected_counts.items():
        actual = text.count(marker)
        if actual != expected:
            failures.append(f"{label}_exact_count:{marker}:expected={expected}:actual={actual}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_PHASE12_PATHS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    for rel_path in FORBIDDEN_PHASE12_PATHS:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    if failures:
        return failures

    docs_readme = read_text(root, DOCS_README_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    freeze_map = read_text(root, FREEZE_MAP_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    phase12_build = read_text(root, PHASE12_BUILD_PATH)
    phase12_release_sequencing = read_text(root, PHASE12_RELEASE_SEQUENCING_PATH)
    phase12_release_readiness = read_text(root, PHASE12_RELEASE_READINESS_PATH)
    phase12_release_closure = read_text(root, PHASE12_RELEASE_CLOSURE_PATH)
    phase12_release_coordination = read_text(root, PHASE12_RELEASE_COORDINATION_PATH)
    phase12_complex_driver_lane = read_text(root, PHASE12_COMPLEX_DRIVER_LANE_PATH)
    phase12_libbpf_heavy_consumer_lane = read_text(root, PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH)
    phase12_libbpf_survey = read_text(root, PHASE12_LIBBPF_SURVEY_PATH)
    phase12_raw_github_coverage = read_text(root, PHASE12_RAW_GITHUB_COVERAGE_PATH)

    ensure_contains(failures, "scripts_readme", scripts_readme, REQUIRED_SCRIPTS_README_MARKERS)
    ensure_contains(failures, "docs_readme", docs_readme, REQUIRED_DOCS_README_MARKERS)
    ensure_contains(failures, "review_checklist", review_checklist, REQUIRED_REVIEW_CHECKLIST_MARKERS)
    ensure_contains(failures, "freeze_map", freeze_map, REQUIRED_FREEZE_MAP_MARKERS)
    ensure_contains(failures, "phase12_release_sequencing", phase12_release_sequencing, REQUIRED_PHASE12_RELEASE_SEQUENCING_MARKERS)
    ensure_contains(failures, "phase12_release_readiness", phase12_release_readiness, REQUIRED_PHASE12_RELEASE_READINESS_MARKERS)
    ensure_contains(failures, "phase12_release_closure", phase12_release_closure, REQUIRED_PHASE12_RELEASE_CLOSURE_MARKERS)
    ensure_contains(failures, "phase12_release_coordination", phase12_release_coordination, REQUIRED_PHASE12_RELEASE_COORDINATION_MARKERS)
    ensure_contains(failures, "phase12_complex_driver_lane", phase12_complex_driver_lane, REQUIRED_PHASE12_COMPLEX_DRIVER_LANE_MARKERS)
    ensure_contains(
        failures,
        "phase12_libbpf_heavy_consumer_lane",
        phase12_libbpf_heavy_consumer_lane,
        REQUIRED_PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_MARKERS,
    )
    ensure_contains(failures, "phase12_libbpf_survey", phase12_libbpf_survey, REQUIRED_PHASE12_LIBBPF_SURVEY_MARKERS)
    ensure_contains(
        failures,
        "phase12_raw_github_coverage",
        phase12_raw_github_coverage,
        REQUIRED_PHASE12_RAW_GITHUB_COVERAGE_MARKERS,
    )
    ensure_contains(failures, "tests_readme", tests_readme, REQUIRED_TESTS_README_MARKERS)
    ensure_contains(failures, "workflow", workflow, REQUIRED_WORKFLOW_MARKERS)
    ensure_contains(failures, "makefile", makefile, REQUIRED_MAKEFILE_MARKERS)
    ensure_contains(failures, "phase12_build", phase12_build, REQUIRED_PHASE12_BUILD_MARKERS)

    ensure_absent(failures, "workflow", workflow, FORBIDDEN_WORKFLOW_MARKERS)
    ensure_absent(failures, "makefile", makefile, FORBIDDEN_MAKEFILE_MARKERS)

    ensure_exact_counts(failures, "scripts_readme", scripts_readme, EXACT_COUNT_MAPS["scripts_readme"])
    ensure_exact_counts(failures, "docs_readme", docs_readme, EXACT_COUNT_MAPS["docs_readme"])
    ensure_exact_counts(failures, "review_checklist", review_checklist, EXACT_COUNT_MAPS["review_checklist"])
    ensure_exact_counts(failures, "freeze_map", freeze_map, EXACT_COUNT_MAPS["freeze_map"])
    ensure_exact_counts(
        failures,
        "phase12_release_sequencing",
        phase12_release_sequencing,
        EXACT_COUNT_MAPS["phase12_release_sequencing"],
    )
    ensure_exact_counts(
        failures,
        "phase12_release_readiness",
        phase12_release_readiness,
        EXACT_COUNT_MAPS["phase12_release_readiness"],
    )
    ensure_exact_counts(
        failures,
        "phase12_release_closure",
        phase12_release_closure,
        EXACT_COUNT_MAPS["phase12_release_closure"],
    )
    ensure_exact_counts(
        failures,
        "phase12_release_coordination",
        phase12_release_coordination,
        EXACT_COUNT_MAPS["phase12_release_coordination"],
    )
    ensure_exact_counts(
        failures,
        "phase12_complex_driver_lane",
        phase12_complex_driver_lane,
        EXACT_COUNT_MAPS["phase12_complex_driver_lane"],
    )
    ensure_exact_counts(
        failures,
        "phase12_libbpf_heavy_consumer_lane",
        phase12_libbpf_heavy_consumer_lane,
        EXACT_COUNT_MAPS["phase12_libbpf_heavy_consumer_lane"],
    )
    ensure_exact_counts(
        failures,
        "phase12_libbpf_survey",
        phase12_libbpf_survey,
        EXACT_COUNT_MAPS["phase12_libbpf_survey"],
    )
    ensure_exact_counts(
        failures,
        "phase12_raw_github_coverage",
        phase12_raw_github_coverage,
        EXACT_COUNT_MAPS["phase12_raw_github_coverage"],
    )
    ensure_exact_counts(failures, "tests_readme", tests_readme, EXACT_COUNT_MAPS["tests_readme"])
    ensure_exact_counts(failures, "phase12_build", phase12_build, EXACT_COUNT_MAPS["phase12_build"])

    return failures


def minimal_marker_doc(title: str, markers: list[str]) -> str:
    return "\n".join([f"# {title}", *markers, ""])


def minimal_phase12_build() -> str:
    lines = [
        'const phase12_virtio_net_syntax_lab_module = b.createModule(.{ .root_source_file = b.path("phase12_virtio_net_syntax_lab.zig"), });',
        'const phase12_virtio_scsi_syntax_lab_module = b.createModule(.{ .root_source_file = b.path("phase12_virtio_scsi_syntax_lab.zig"), });',
        'const phase12_nvme_pci_tests = b.addTest(.{ .name = "phase12-nvme-pci-tests", });',
        'const phase12_nvme_pci_verify_tests = b.addTest(.{ .name = "phase12-nvme-pci-verify-tests", });',
        'const phase12_nvme_pci_survey_tests = b.addTest(.{ .name = "phase12-nvme-pci-survey-tests", });',
        'const phase12_virtio_net_tests = b.addTest(.{ .name = "phase12-virtio-net-tests", });',
        'const phase12_virtio_net_syntax_lab_tests = b.addTest(.{ .name = "phase12-virtio-net-syntax-lab-tests", .root_module = phase12_virtio_net_syntax_lab_module, });',
        'const phase12_virtio_net_survey_tests = b.addTest(.{ .name = "phase12-virtio-net-survey-tests", });',
        'const phase12_virtio_scsi_tests = b.addTest(.{ .name = "phase12-virtio-scsi-tests", });',
        'const phase12_virtio_scsi_syntax_lab_tests = b.addTest(.{ .name = "phase12-virtio-scsi-syntax-lab-tests", .root_module = phase12_virtio_scsi_syntax_lab_module, });',
        'const phase12_virtio_scsi_survey_tests = b.addTest(.{ .name = "phase12-virtio-scsi-survey-tests", });',
        'const phase12_libbpf_segments_tests = b.addTest(.{ .name = "phase12-libbpf-segment-survey-tests", });',
        'const phase12_libbpf_segments_verify_tests = b.addTest(.{ .name = "phase12-libbpf-segments-verify-tests", });',
        'const phase12_libbpf_reviewability_tests = b.addTest(.{ .name = "phase12-libbpf-reviewability-tests", });',
        'const phase12_libbpf_snapshot_determinism_tests = b.addTest(.{ .name = "phase12-libbpf-snapshot-determinism-tests", });',
        'const smoke_step = b.step("smoke", "Run Phase 12 direct driver and syntax-lab smoke tests");',
        'smoke_step.dependOn(&run_phase12_nvme_pci_tests.step);',
        'smoke_step.dependOn(&run_phase12_nvme_pci_verify_tests.step);',
        'smoke_step.dependOn(&run_phase12_virtio_net_tests.step);',
        'smoke_step.dependOn(&run_phase12_virtio_net_syntax_lab_tests.step);',
        'smoke_step.dependOn(&run_phase12_virtio_scsi_tests.step);',
        'smoke_step.dependOn(&run_phase12_virtio_scsi_syntax_lab_tests.step);',
        'const test_step = b.step("test", "Run Phase 12 driver and survey tests");',
        'test_step.dependOn(smoke_step);',
        'test_step.dependOn(&run_phase12_nvme_pci_survey_tests.step);',
        'test_step.dependOn(&run_phase12_virtio_net_survey_tests.step);',
        'test_step.dependOn(&run_phase12_virtio_scsi_survey_tests.step);',
        'test_step.dependOn(&run_phase12_libbpf_segments_tests.step);',
        'test_step.dependOn(&run_phase12_libbpf_segments_verify_tests.step);',
        'test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);',
        'test_step.dependOn(&run_phase12_libbpf_snapshot_determinism_tests.step);',
    ]
    return "\n".join(lines) + "\n"


def placeholder_for(rel_path: str) -> str:
    if rel_path == PHASE12_BUILD_PATH:
        return minimal_phase12_build()
    if rel_path == SCRIPTS_README_PATH:
        return minimal_marker_doc("scripts/zigux", REQUIRED_SCRIPTS_README_MARKERS)
    if rel_path == DOCS_README_PATH:
        return minimal_marker_doc("Documentation/zigux", REQUIRED_DOCS_README_MARKERS)
    if rel_path == REVIEW_CHECKLIST_PATH:
        return minimal_marker_doc("Documentation/zigux/review-checklist", REQUIRED_REVIEW_CHECKLIST_MARKERS)
    if rel_path == FREEZE_MAP_PATH:
        return minimal_marker_doc("Documentation/zigux/freeze-map", REQUIRED_FREEZE_MAP_MARKERS)
    if rel_path == TESTS_README_PATH:
        return minimal_marker_doc("zigux/tests", REQUIRED_TESTS_README_MARKERS)
    if rel_path == PHASE12_RELEASE_SEQUENCING_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-release-sequencing", REQUIRED_PHASE12_RELEASE_SEQUENCING_MARKERS)
    if rel_path == PHASE12_RELEASE_READINESS_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-release-readiness-survey", REQUIRED_PHASE12_RELEASE_READINESS_MARKERS)
    if rel_path == PHASE12_RELEASE_CLOSURE_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-release-closure-checklist", REQUIRED_PHASE12_RELEASE_CLOSURE_MARKERS)
    if rel_path == PHASE12_RELEASE_COORDINATION_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-release-coordination-matrix", REQUIRED_PHASE12_RELEASE_COORDINATION_MARKERS)
    if rel_path == PHASE12_COMPLEX_DRIVER_LANE_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-complex-driver-lane-sequencing", REQUIRED_PHASE12_COMPLEX_DRIVER_LANE_MARKERS)
    if rel_path == PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing", REQUIRED_PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_MARKERS)
    if rel_path == PHASE12_LIBBPF_SURVEY_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-libbpf-segment-survey", REQUIRED_PHASE12_LIBBPF_SURVEY_MARKERS)
    if rel_path == PHASE12_RAW_GITHUB_COVERAGE_PATH:
        return minimal_marker_doc("Documentation/zigux/phase12-raw-github-coverage-survey", REQUIRED_PHASE12_RAW_GITHUB_COVERAGE_MARKERS)
    if rel_path == WORKFLOW_PATH:
        return "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n"
    if rel_path == MAKEFILE_PATH:
        return "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n"
    if rel_path.endswith(".zig"):
        return "// phase12 placeholder\n"
    if rel_path.endswith(".json"):
        return "{}\n"
    return "# phase12 placeholder\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_PHASE12_PATHS:
        write_text(root / rel_path, placeholder_for(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        scripts_readme_path = base / SCRIPTS_README_PATH
        docs_readme_path = base / DOCS_README_PATH
        review_checklist_path = base / REVIEW_CHECKLIST_PATH
        tests_readme_path = base / TESTS_README_PATH
        phase12_release_sequencing_path = base / PHASE12_RELEASE_SEQUENCING_PATH
        phase12_release_readiness_path = base / PHASE12_RELEASE_READINESS_PATH
        phase12_release_closure_path = base / PHASE12_RELEASE_CLOSURE_PATH
        phase12_release_coordination_path = base / PHASE12_RELEASE_COORDINATION_PATH
        phase12_complex_driver_lane_path = base / PHASE12_COMPLEX_DRIVER_LANE_PATH
        phase12_libbpf_survey_path = base / PHASE12_LIBBPF_SURVEY_PATH
        phase12_raw_github_coverage_path = base / PHASE12_RAW_GITHUB_COVERAGE_PATH
        workflow_path = base / WORKFLOW_PATH
        makefile_path = base / MAKEFILE_PATH
        phase12_build_path = base / PHASE12_BUILD_PATH

        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(PHASE12_REMOVED_SURFACE_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"scripts_readme:{PHASE12_REMOVED_SURFACE_MARKER}")

        write_fixture_tree(base)
        docs_readme_path.write_text(
            docs_readme_path.read_text(encoding="utf-8").replace(PHASE12_DOCS_REMOVED_VALIDATOR_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"docs_readme:{PHASE12_DOCS_REMOVED_VALIDATOR_MARKER}")

        write_fixture_tree(base)
        review_checklist_path.write_text(
            review_checklist_path.read_text(encoding="utf-8").replace(PHASE12_REVIEW_CHECKLIST_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"review_checklist:{PHASE12_REVIEW_CHECKLIST_MARKER}")

        write_fixture_tree(base)
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(f"`{PHASE12_LIBBPF_VERIFY_PATH}`", "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"tests_readme:`{PHASE12_LIBBPF_VERIFY_PATH}`")

        write_fixture_tree(base)
        phase12_release_sequencing_path.write_text(
            phase12_release_sequencing_path.read_text(encoding="utf-8").replace(PHASE12_RELEASE_SEQUENCING_UNSHIPPED_ROUTE_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_release_sequencing:{PHASE12_RELEASE_SEQUENCING_UNSHIPPED_ROUTE_MARKER}")

        write_fixture_tree(base)
        phase12_release_readiness_path.write_text(
            phase12_release_readiness_path.read_text(encoding="utf-8").replace(PHASE12_RELEASE_READINESS_FALLBACK_SPLIT_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_release_readiness:{PHASE12_RELEASE_READINESS_FALLBACK_SPLIT_MARKER}")

        write_fixture_tree(base)
        phase12_release_readiness_path.write_text(
            phase12_release_readiness_path.read_text(encoding="utf-8").replace(PHASE12_RELEASE_READINESS_RAW_READ_ANCHOR_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_release_readiness:{PHASE12_RELEASE_READINESS_RAW_READ_ANCHOR_MARKER}")

        write_fixture_tree(base)
        phase12_release_readiness_path.write_text(
            phase12_release_readiness_path.read_text(encoding="utf-8").replace(PHASE12_RELEASE_READINESS_VERIFY_SHARD_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_release_readiness:{PHASE12_RELEASE_READINESS_VERIFY_SHARD_MARKER}")

        write_fixture_tree(base)
        phase12_release_closure_path.write_text(
            phase12_release_closure_path.read_text(encoding="utf-8").replace(PHASE12_RELEASE_CLOSURE_VERIFY_SHARD_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_release_closure:{PHASE12_RELEASE_CLOSURE_VERIFY_SHARD_MARKER}")

        write_fixture_tree(base)
        phase12_release_closure_path.write_text(
            phase12_release_closure_path.read_text(encoding="utf-8").replace(PHASE12_RELEASE_CLOSURE_ATTACHED_TOOLCHAIN_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_release_closure:{PHASE12_RELEASE_CLOSURE_ATTACHED_TOOLCHAIN_MARKER}")

        write_fixture_tree(base)
        phase12_release_coordination_path.write_text(
            phase12_release_coordination_path.read_text(encoding="utf-8").replace(PHASE12_RELEASE_COORDINATION_VERIFY_SHARD_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_release_coordination:{PHASE12_RELEASE_COORDINATION_VERIFY_SHARD_MARKER}")

        write_fixture_tree(base)
        phase12_complex_driver_lane_path.write_text(
            phase12_complex_driver_lane_path.read_text(encoding="utf-8").replace(PHASE12_COMPLEX_DRIVER_LANE_TRUTHFULNESS_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_complex_driver_lane:{PHASE12_COMPLEX_DRIVER_LANE_TRUTHFULNESS_MARKER}")

        write_fixture_tree(base)
        phase12_libbpf_survey_path.write_text(
            phase12_libbpf_survey_path.read_text(encoding="utf-8").replace(PHASE12_LIBBPF_SURVEY_ROLLBACK_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_libbpf_survey:{PHASE12_LIBBPF_SURVEY_ROLLBACK_MARKER}")

        write_fixture_tree(base)
        phase12_raw_github_coverage_path.write_text(
            phase12_raw_github_coverage_path.read_text(encoding="utf-8").replace(PHASE12_RAW_GITHUB_COVERAGE_LIBBPF_ANTI_OVERLAP_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"phase12_raw_github_coverage:{PHASE12_RAW_GITHUB_COVERAGE_LIBBPF_ANTI_OVERLAP_MARKER}")

        write_fixture_tree(base)
        workflow_path.write_text(workflow_path.read_text(encoding="utf-8").replace("make -C zigux phase12-smoke", "", 1), encoding="utf-8")
        expect_failure(base, "workflow:make -C zigux phase12-smoke")

        write_fixture_tree(base)
        makefile_path.write_text(makefile_path.read_text(encoding="utf-8") + "phase12-validate:\n", encoding="utf-8")
        expect_failure(base, "makefile_forbidden:phase12-validate:")

        write_fixture_tree(base)
        phase12_build_path.write_text(
            phase12_build_path.read_text(encoding="utf-8").replace(
                'smoke_step.dependOn(&run_phase12_virtio_scsi_syntax_lab_tests.step);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(base, "phase12_build:smoke_step.dependOn(&run_phase12_virtio_scsi_syntax_lab_tests.step);")

        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=16")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 12 build-only fallback surface against the surviving current-master packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the repository root inferred from this script.",
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
        print("PHASE12_BUILD_ONLY_SURFACE=fail")
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_END")
        return 1

    marker_count = (
        len(REQUIRED_PHASE12_PATHS)
        + len(REQUIRED_SCRIPTS_README_MARKERS)
        + len(REQUIRED_DOCS_README_MARKERS)
        + len(REQUIRED_REVIEW_CHECKLIST_MARKERS)
        + len(REQUIRED_FREEZE_MAP_MARKERS)
        + len(REQUIRED_PHASE12_RELEASE_SEQUENCING_MARKERS)
        + len(REQUIRED_PHASE12_RELEASE_READINESS_MARKERS)
        + len(REQUIRED_PHASE12_RELEASE_CLOSURE_MARKERS)
        + len(REQUIRED_PHASE12_RELEASE_COORDINATION_MARKERS)
        + len(REQUIRED_PHASE12_COMPLEX_DRIVER_LANE_MARKERS)
        + len(REQUIRED_PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_MARKERS)
        + len(REQUIRED_PHASE12_LIBBPF_SURVEY_MARKERS)
        + len(REQUIRED_PHASE12_RAW_GITHUB_COVERAGE_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(REQUIRED_WORKFLOW_MARKERS)
        + len(REQUIRED_MAKEFILE_MARKERS)
        + len(REQUIRED_PHASE12_BUILD_MARKERS)
    )
    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(f"PHASE12_BUILD_ONLY_SURFACE_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

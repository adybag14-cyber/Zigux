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
        if (candidate / "scripts/zigux/README.md").exists() and (
            candidate / ".github/workflows/zigux-bootstrap.yml"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
COMPLEX_DRIVER_LANE_SEQUENCING_PATH = (
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
)
LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_PATH = (
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
)
LIBBPF_VERIFY_SHARD_NOTE_PATH = (
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
)
LIBBPF_SEGMENT_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
RAW_GITHUB_COVERAGE_SURVEY_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
PHASE12_VIRTIO_SCSI_RAW_GITHUB_FALLBACK_CATALOG_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
PHASE12_NVME_PCI_RAW_GITHUB_FALLBACK_MAP_PATH = (
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
)
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
PHASE12_VIRTIO_NET_DRIVER_PATH = "drivers/net/virtio_net.zig"
PHASE12_VIRTIO_NET_TEST_PATH = "zigux/tests/phase12_virtio_net.zig"
PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH = "zigux/tests/phase12_virtio_net_syntax_lab.zig"
PHASE12_VIRTIO_NET_MANIFEST_PATH = "zigux/tests/phase12_virtio_net_manifest.json"
PHASE12_VIRTIO_NET_SURVEY_PATH = "zigux/tests/phase12_virtio_net_survey.zig"
PHASE12_VIRTIO_SCSI_DRIVER_PATH = "drivers/scsi/virtio_scsi.zig"
PHASE12_VIRTIO_SCSI_TEST_PATH = "zigux/tests/phase12_virtio_scsi.zig"
PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH = "zigux/tests/phase12_virtio_scsi_syntax_lab.zig"
PHASE12_REPEATED_REPLAN_PATH = "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig"
PHASE12_PACKET_PATH = "zigux/tests/phase12_virtio_scsi_packet.zig"
PHASE12_LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
PHASE12_VALIDATE_PATH = "scripts/zigux/validate-phase12.py"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    COMPLEX_DRIVER_LANE_SEQUENCING_PATH,
    LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_PATH,
    LIBBPF_VERIFY_SHARD_NOTE_PATH,
    LIBBPF_SEGMENT_SURVEY_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    PHASE12_VIRTIO_SCSI_RAW_GITHUB_FALLBACK_CATALOG_PATH,
    PHASE12_NVME_PCI_RAW_GITHUB_FALLBACK_MAP_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    PHASE12_VIRTIO_NET_DRIVER_PATH,
    PHASE12_VIRTIO_NET_TEST_PATH,
    PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH,
    PHASE12_VIRTIO_NET_MANIFEST_PATH,
    PHASE12_VIRTIO_NET_SURVEY_PATH,
    PHASE12_VIRTIO_SCSI_DRIVER_PATH,
    PHASE12_VIRTIO_SCSI_TEST_PATH,
    PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH,
    PHASE12_REPEATED_REPLAN_PATH,
    PHASE12_PACKET_PATH,
    PHASE12_LIBBPF_SNAPSHOT_PATH,
    PHASE12_VALIDATE_PATH,
]

DOCS_ROOT_MARKERS = [
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`drivers/net/virtio_net.zig`",
    "`zigux/tests/phase12_virtio_net.zig`",
    "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`scripts/zigux/validate-phase12.py`",
    "the current starter-present `virtio_net` plus smoke-first `virtio_scsi` release packet reviewable from the docs root through the shipped build-only contract",
    "while broader `nvme_pci` and direct libbpf replay files stay recorded only through the shared fallback, survey, verify-shard, or anti-overlap notes until they actually land on `master`",
    "`make -C zigux phase12-smoke` plus `make -C zigux phase12` keep the shared smoke-first release order visible",
    "`scripts/zigux/validate-phase12.py` exists only as an unwired helper",
    "only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts, while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keeps the parked libbpf reviewability packet visible without promoting the direct `phase12_libbpf_*` replay files or `tools/lib/bpf/zigux_segments/manifest.json` into shipped current-`master` evidence.",
]

DOCS_ROOT_FORBIDDEN_MARKERS = [
    "`Documentation/zigux/phase12-nvme-pci-slice.md`",
    "`Documentation/zigux/phase12-nvme-pci-survey.md`",
]

REVIEW_CHECKLIST_MARKERS = [
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12`",
    "while the direct `virtio_net` starter packet now stays explicit through `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig`",
    "and the still-absent direct `phase12_nvme_pci` and `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
    "avoid implying a shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route that current `master` does not ship",
]

SCRIPTS_README_MARKERS = [
    "`check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`Documentation/zigux/phase12-virtio-net-survey.md`",
    "`Documentation/zigux/phase12-libbpf-segment-survey.md`",
    "the current starter-present `virtio_net` plus smoke-first `virtio_scsi` release packet and the parked verify-shard-backed libbpf survey packet reviewable from the scripts root",
    "`Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, and the direct `phase12_nvme_pci` plus `phase12_libbpf_*` replay files stay recorded only through the shared fallback, survey, verify-shard, or anti-overlap notes until they actually land on `master`",
    "without implying removed `validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build, or `phase12-validate` surfaces that are not on `master`.",
    "only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned artifacts, while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors, `Documentation/zigux/phase12-libbpf-verify-shard-note.md` keeps the parked libbpf snapshot boundary explicit, and `scripts/zigux/validate-phase12.py` stays an unwired helper rather than a shipped `phase12-validate` route.",
]

TESTS_README_MARKERS = [
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
    "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
    "`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
    "`Documentation/zigux/phase12-virtio-net-survey.md`",
    "`Documentation/zigux/phase12-libbpf-segment-survey.md`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`scripts/zigux/validate-phase12.py`",
    "while the direct `virtio_net` starter packet now stays explicit through `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig`",
    "the still-absent direct `phase12_nvme_pci` and `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
    "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12-smoke`",
    "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12`",
]

RELEASE_READINESS_SURVEY_MARKERS = [
    "`PHASE12_STATUS=active`",
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "the parked verify-shard note still governs the shared libbpf packet",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py`",
    "the next honest same-lane follow-through is to leave this note parked unless the shared Phase 12 packet itself changes",
]

RELEASE_SEQUENCING_MARKERS = [
    "`PHASE12_STATUS=active`",
    "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
    "verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12-smoke`",
    "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12`",
    "starter-present `virtio_net` packet plus the shipped `virtio_scsi` build-only packet",
    "`make -C zigux phase12-validate` route, wired validator-first replay packet, focused libbpf-only replay, or cross-build replay on current `master`; `scripts/zigux/validate-phase12.py` exists as an unwired helper",
]

RELEASE_COORDINATION_MATRIX_MARKERS = [
    "`PHASE12_STATUS=active`",
    "verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
    "shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`",
    "starter-present `virtio_net` packet while that family still lacks a separate slice note",
    "the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` stay recorded only through the parked verify-shard packet until those files land again on current `master`.",
    "rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO wording",
]

RELEASE_CLOSURE_CHECKLIST_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "the bounded storage rollback drill",
    "the shared build-and-make replay path",
    "the active shipped build packet on current `master` is the starter-present `virtio_net` plus smoke-first `virtio_scsi` replay",
    "The current driver-local doc split must stay explicit too: `virtio_scsi` still ships the dedicated `Documentation/zigux/phase12-virtio-scsi-slice.md` plus `Documentation/zigux/phase12-virtio-scsi-survey.md` pair, while `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the truthful `nvme_pci` boundary until live `master` actually lands dedicated `Documentation/zigux/phase12-nvme-pci-slice.md` and `Documentation/zigux/phase12-nvme-pci-survey.md` surfaces, and `Documentation/zigux/phase12-virtio-net-survey.md` plus the direct `virtio_net` replay files now form a starter-present packet even though a separate `Documentation/zigux/phase12-virtio-net-slice.md` surface still does not exist on current `master`.",
    "There is still no shipped shared `make -C zigux phase12-validate` route, even though `scripts/zigux/validate-phase12.py` now exists as an unwired helper on current `master`.",
]

COMPLEX_DRIVER_LANE_SEQUENCING_MARKERS = [
    "`PHASE12_LANE=complex-driver-shared-release-packet`",
    "Treat the current `virtio_net` family as a starter-present direct-replay packet",
    "`drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` are now present on `master`",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "starter-present `virtio_net` syntax-lab and direct contract packet",
    "stops undercounting the newly landed `virtio_net` starter",
]

LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_MARKERS = [
    "`PHASE12_LANE=libbpf-heavy-consumer-shared-release-packet`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts",
    "treat the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` as parked note-owned boundaries until they land again on current `master`.",
    "Current `master` does ship `scripts/zigux/validate-phase12.py` as an unwired helper, but there is still no shipped shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route.",
]

LIBBPF_VERIFY_SHARD_NOTE_MARKERS = [
    "`PHASE12_STATUS=parked`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` stay recorded only through shared survey, parked, or anti-overlap notes until they land again on current `master`",
    "the snapshot anchor remains the truthful bounded signal here while those direct replay files stay absent from the shipped checkout",
]

LIBBPF_SEGMENT_SURVEY_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` stay recorded only through the survey, verify-shard, and anti-overlap notes until they land again on current `master`",
    "The helper footing is real, while the shared Phase 12 smoke-and-test order is still narrower than the parked libbpf reviewability packet described only through those note-owned boundaries.",
]

RAW_GITHUB_COVERAGE_SURVEY_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py`",
    "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
    "`make -C zigux phase12 ZIG=<attached-zig-path>`",
    "current `master` ships `scripts/zigux/validate-phase12.py`",
    "there is still no shipped `make -C zigux phase12-validate` route",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 12 build-only surface checker",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "Check Phase 12 build-only surface",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "Run focused Phase 12 smoke shard",
    "make -C zigux phase12-smoke",
    "Run Phase 12 complex driver and libbpf tests",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
]

MAKEFILE_MARKERS = [
    "phase12-smoke:",
    "$(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "$(PYTHON) scripts/zigux/check-build-only-phase12-surface.py",
    "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-smoke phase12-test",
]

PHASE12_BUILD_MARKERS = [
    '../../drivers/net/virtio_net.zig',
    '"phase12_virtio_net.zig"',
    '"phase12_virtio_net_syntax_lab.zig"',
    '"phase12_virtio_scsi.zig"',
    '"phase12_virtio_scsi_syntax_lab.zig"',
    '"phase12_virtio_scsi_repeated_replan_gate.zig"',
    '"phase12_virtio_scsi_packet.zig"',
    '.name = "phase12-virtio-net-tests"',
    '.name = "phase12-virtio-net-syntax-lab-tests"',
    '.name = "phase12-virtio-scsi-tests"',
    '.name = "phase12-virtio-scsi-syntax-lab-tests"',
    '.name = "phase12-virtio-scsi-repeated-replan-gate-tests"',
    '.name = "phase12-virtio-scsi-packet-tests"',
    'run_virtio_net_contract_tests.setCwd(b.path("../.."));',
    'run_virtio_net_syntax_tests.setCwd(b.path("../.."));',
    'run_contract_tests.setCwd(b.path("../.."));',
    'run_syntax_tests.setCwd(b.path("../.."));',
    'run_repeated_replan_tests.setCwd(b.path("../.."));',
    'run_packet_tests.setCwd(b.path("../.."));',
    'const smoke_step = b.step("smoke", "Run Phase 12 virtio syntax smoke");',
    'smoke_step.dependOn(&run_virtio_net_syntax_tests.step);',
    'smoke_step.dependOn(&run_syntax_tests.step);',
    'smoke_step.dependOn(&run_repeated_replan_tests.step);',
    'smoke_step.dependOn(&run_packet_tests.step);',
    'const test_step = b.step("test", "Run Phase 12 virtio packet tests");',
    'test_step.dependOn(&run_virtio_net_contract_tests.step);',
    'test_step.dependOn(&run_virtio_net_syntax_tests.step);',
    'test_step.dependOn(&run_contract_tests.step);',
    'test_step.dependOn(&run_syntax_tests.step);',
    'test_step.dependOn(&run_repeated_replan_tests.step);',
    'test_step.dependOn(&run_packet_tests.step);',
]

PHASE12_BUILD_EXACT_COUNTS = {
    "b.addTest(.{": 6,
    "setCwd(": 6,
    "smoke_step.dependOn(": 4,
    "test_step.dependOn(": 6,
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


def ensure_exact_counts(
    failures: list[str], label: str, text: str, expected_counts: dict[str, int]
) -> None:
    for marker, expected in expected_counts.items():
        actual = text.count(marker)
        if actual != expected:
            failures.append(
                f"{label}_exact_count:{marker}:expected={expected}:actual={actual}"
            )


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    checks = [
        ("docs_root", DOCS_README_PATH, DOCS_ROOT_MARKERS),
        ("review_checklist", REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS),
        ("scripts_readme", SCRIPTS_README_PATH, SCRIPTS_README_MARKERS),
        ("tests_readme", TESTS_README_PATH, TESTS_README_MARKERS),
        (
            "release_readiness_survey",
            RELEASE_READINESS_SURVEY_PATH,
            RELEASE_READINESS_SURVEY_MARKERS,
        ),
        ("release_sequencing", RELEASE_SEQUENCING_PATH, RELEASE_SEQUENCING_MARKERS),
        (
            "release_coordination_matrix",
            RELEASE_COORDINATION_MATRIX_PATH,
            RELEASE_COORDINATION_MATRIX_MARKERS,
        ),
        (
            "release_closure_checklist",
            RELEASE_CLOSURE_CHECKLIST_PATH,
            RELEASE_CLOSURE_CHECKLIST_MARKERS,
        ),
        (
            "complex_driver_lane_sequencing",
            COMPLEX_DRIVER_LANE_SEQUENCING_PATH,
            COMPLEX_DRIVER_LANE_SEQUENCING_MARKERS,
        ),
        (
            "libbpf_heavy_consumer_lane_sequencing",
            LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_PATH,
            LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_MARKERS,
        ),
        (
            "libbpf_verify_shard_note",
            LIBBPF_VERIFY_SHARD_NOTE_PATH,
            LIBBPF_VERIFY_SHARD_NOTE_MARKERS,
        ),
        (
            "libbpf_segment_survey",
            LIBBPF_SEGMENT_SURVEY_PATH,
            LIBBPF_SEGMENT_SURVEY_MARKERS,
        ),
        (
            "raw_github_coverage_survey",
            RAW_GITHUB_COVERAGE_SURVEY_PATH,
            RAW_GITHUB_COVERAGE_SURVEY_MARKERS,
        ),
        ("workflow", WORKFLOW_PATH, WORKFLOW_MARKERS),
        ("makefile", MAKEFILE_PATH, MAKEFILE_MARKERS),
        ("phase12_build", PHASE12_BUILD_PATH, PHASE12_BUILD_MARKERS),
    ]
    for label, rel_path, markers in checks:
        ensure_contains(failures, label, read_text(root, rel_path), markers)

    ensure_absent(
        failures,
        "docs_root",
        read_text(root, DOCS_README_PATH),
        DOCS_ROOT_FORBIDDEN_MARKERS,
    )

    ensure_exact_counts(
        failures,
        "phase12_build",
        read_text(root, PHASE12_BUILD_PATH),
        PHASE12_BUILD_EXACT_COUNTS,
    )

    return failures


def minimal_join(title: str, markers: list[str]) -> str:
    return "\n".join([title, *markers, ""])


def minimal_phase12_build() -> str:
    return """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/net/virtio_net.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const virtio_scsi_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/scsi/virtio_scsi.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const virtio_net_contract_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net.zig\"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_contract_root_module.addImport(\"virtio_net\", virtio_net_module);

    const virtio_net_syntax_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_syntax_lab.zig\"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_syntax_root_module.addImport(\"virtio_net\", virtio_net_module);

    const contract_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi.zig\"),
        .target = target,
        .optimize = optimize,
    });
    contract_root_module.addImport(\"virtio_scsi\", virtio_scsi_module);

    const syntax_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi_syntax_lab.zig\"),
        .target = target,
        .optimize = optimize,
    });
    syntax_root_module.addImport(\"virtio_scsi\", virtio_scsi_module);

    const repeated_replan_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi_repeated_replan_gate.zig\"),
        .target = target,
        .optimize = optimize,
    });
    repeated_replan_root_module.addImport(\"virtio_scsi\", virtio_scsi_module);

    const packet_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_scsi_packet.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const virtio_net_contract_tests = b.addTest(.{
        .name = \"phase12-virtio-net-tests\",
        .root_module = virtio_net_contract_root_module,
    });
    const run_virtio_net_contract_tests = b.addRunArtifact(virtio_net_contract_tests);
    run_virtio_net_contract_tests.setCwd(b.path(\"../..\"));

    const virtio_net_syntax_tests = b.addTest(.{
        .name = \"phase12-virtio-net-syntax-lab-tests\",
        .root_module = virtio_net_syntax_root_module,
    });
    const run_virtio_net_syntax_tests = b.addRunArtifact(virtio_net_syntax_tests);
    run_virtio_net_syntax_tests.setCwd(b.path(\"../..\"));

    const contract_tests = b.addTest(.{
        .name = \"phase12-virtio-scsi-tests\",
        .root_module = contract_root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path(\"../..\"));

    const syntax_tests = b.addTest(.{
        .name = \"phase12-virtio-scsi-syntax-lab-tests\",
        .root_module = syntax_root_module,
    });
    const run_syntax_tests = b.addRunArtifact(syntax_tests);
    run_syntax_tests.setCwd(b.path(\"../..\"));

    const repeated_replan_tests = b.addTest(.{
        .name = \"phase12-virtio-scsi-repeated-replan-gate-tests\",
        .root_module = repeated_replan_root_module,
    });
    const run_repeated_replan_tests = b.addRunArtifact(repeated_replan_tests);
    run_repeated_replan_tests.setCwd(b.path(\"../..\"));

    const packet_tests = b.addTest(.{
        .name = \"phase12-virtio-scsi-packet-tests\",
        .root_module = packet_root_module,
    });
    const run_packet_tests = b.addRunArtifact(packet_tests);
    run_packet_tests.setCwd(b.path(\"../..\"));

    const smoke_step = b.step(\"smoke\", \"Run Phase 12 virtio syntax smoke\");
    smoke_step.dependOn(&run_virtio_net_syntax_tests.step);
    smoke_step.dependOn(&run_syntax_tests.step);
    smoke_step.dependOn(&run_repeated_replan_tests.step);
    smoke_step.dependOn(&run_packet_tests.step);

    const test_step = b.step(\"test\", \"Run Phase 12 virtio packet tests\");
    test_step.dependOn(&run_virtio_net_contract_tests.step);
    test_step.dependOn(&run_virtio_net_syntax_tests.step);
    test_step.dependOn(&run_contract_tests.step);
    test_step.dependOn(&run_syntax_tests.step);
    test_step.dependOn(&run_repeated_replan_tests.step);
    test_step.dependOn(&run_packet_tests.step);
}
"""


def placeholder_for(rel_path: str) -> str:
    mapping = {
        DOCS_README_PATH: minimal_join("# Zigux Documentation", DOCS_ROOT_MARKERS),
        REVIEW_CHECKLIST_PATH: minimal_join(
            "# Zigux Review Checklist", REVIEW_CHECKLIST_MARKERS
        ),
        SCRIPTS_README_PATH: minimal_join("# scripts/zigux", SCRIPTS_README_MARKERS),
        TESTS_README_PATH: minimal_join("# zigux/tests", TESTS_README_MARKERS),
        RELEASE_READINESS_SURVEY_PATH: minimal_join(
            "# Phase 12 Release Readiness Survey", RELEASE_READINESS_SURVEY_MARKERS
        ),
        RELEASE_SEQUENCING_PATH: minimal_join(
            "# Phase 12 Release Sequencing", RELEASE_SEQUENCING_MARKERS
        ),
        RELEASE_COORDINATION_MATRIX_PATH: minimal_join(
            "# Phase 12 Release Coordination Matrix",
            RELEASE_COORDINATION_MATRIX_MARKERS,
        ),
        RELEASE_CLOSURE_CHECKLIST_PATH: minimal_join(
            "# Phase 12 Release Closure Checklist",
            RELEASE_CLOSURE_CHECKLIST_MARKERS,
        ),
        COMPLEX_DRIVER_LANE_SEQUENCING_PATH: minimal_join(
            "# Phase 12 Complex-Driver Lane Sequencing",
            COMPLEX_DRIVER_LANE_SEQUENCING_MARKERS,
        ),
        LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_PATH: minimal_join(
            "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
            LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_MARKERS,
        ),
        LIBBPF_VERIFY_SHARD_NOTE_PATH: minimal_join(
            "# Phase 12 Libbpf Verify Shard Note", LIBBPF_VERIFY_SHARD_NOTE_MARKERS
        ),
        LIBBPF_SEGMENT_SURVEY_PATH: minimal_join(
            "# Phase 12 Libbpf Segment Survey", LIBBPF_SEGMENT_SURVEY_MARKERS
        ),
        RAW_GITHUB_COVERAGE_SURVEY_PATH: minimal_join(
            "# Phase 12 Raw GitHub Coverage Survey",
            RAW_GITHUB_COVERAGE_SURVEY_MARKERS,
        ),
        WORKFLOW_PATH: minimal_join("name: zigux-bootstrap", WORKFLOW_MARKERS),
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
        PHASE12_BUILD_PATH: minimal_phase12_build(),
    }
    if rel_path in mapping:
        return mapping[rel_path]
    if rel_path.endswith(".zig"):
        return "// phase12 placeholder\n"
    return ""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
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

        write_fixture_tree(base)
        (base / PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH}")

        write_fixture_tree(base)
        (base / PHASE12_VIRTIO_NET_MANIFEST_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE12_VIRTIO_NET_MANIFEST_PATH}")

        write_fixture_tree(base)
        (base / PHASE12_VIRTIO_NET_SURVEY_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE12_VIRTIO_NET_SURVEY_PATH}")

        write_fixture_tree(base)
        (base / PHASE12_LIBBPF_SNAPSHOT_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE12_LIBBPF_SNAPSHOT_PATH}")

        write_fixture_tree(base)
        (base / PHASE12_VIRTIO_SCSI_RAW_GITHUB_FALLBACK_CATALOG_PATH).unlink()
        expect_failure(
            base,
            f"missing_file:{PHASE12_VIRTIO_SCSI_RAW_GITHUB_FALLBACK_CATALOG_PATH}",
        )

        write_fixture_tree(base)
        (base / PHASE12_NVME_PCI_RAW_GITHUB_FALLBACK_MAP_PATH).unlink()
        expect_failure(
            base,
            f"missing_file:{PHASE12_NVME_PCI_RAW_GITHUB_FALLBACK_MAP_PATH}",
        )

        write_fixture_tree(base)
        (base / PHASE12_VALIDATE_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE12_VALIDATE_PATH}")

        write_fixture_tree(base)
        docs_root_path = base / DOCS_README_PATH
        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(
                DOCS_ROOT_MARKERS[13], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"docs_root:{DOCS_ROOT_MARKERS[13]}")

        write_fixture_tree(base)
        docs_root_path = base / DOCS_README_PATH
        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8").replace(
                DOCS_ROOT_MARKERS[17], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"docs_root:{DOCS_ROOT_MARKERS[17]}")

        write_fixture_tree(base)
        docs_root_path = base / DOCS_README_PATH
        docs_root_path.write_text(
            docs_root_path.read_text(encoding="utf-8")
            + DOCS_ROOT_FORBIDDEN_MARKERS[0]
            + "\n",
            encoding="utf-8",
        )
        expect_failure(base, f"docs_root_forbidden:{DOCS_ROOT_FORBIDDEN_MARKERS[0]}")

        write_fixture_tree(base)
        review_checklist_path = base / REVIEW_CHECKLIST_PATH
        review_checklist_path.write_text(
            review_checklist_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[6], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"review_checklist:{REVIEW_CHECKLIST_MARKERS[6]}",
        )

        write_fixture_tree(base)
        readiness_path = base / RELEASE_READINESS_SURVEY_PATH
        readiness_path.write_text(
            readiness_path.read_text(encoding="utf-8").replace(
                RELEASE_READINESS_SURVEY_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_readiness_survey:{RELEASE_READINESS_SURVEY_MARKERS[2]}",
        )

        write_fixture_tree(base)
        readiness_path = base / RELEASE_READINESS_SURVEY_PATH
        readiness_path.write_text(
            readiness_path.read_text(encoding="utf-8").replace(
                RELEASE_READINESS_SURVEY_MARKERS[4], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_readiness_survey:{RELEASE_READINESS_SURVEY_MARKERS[4]}",
        )

        write_fixture_tree(base)
        readiness_path = base / RELEASE_READINESS_SURVEY_PATH
        readiness_path.write_text(
            readiness_path.read_text(encoding="utf-8").replace(
                RELEASE_READINESS_SURVEY_MARKERS[7], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_readiness_survey:{RELEASE_READINESS_SURVEY_MARKERS[7]}",
        )

        write_fixture_tree(base)
        sequencing_path = base / RELEASE_SEQUENCING_PATH
        sequencing_path.write_text(
            sequencing_path.read_text(encoding="utf-8").replace(
                RELEASE_SEQUENCING_MARKERS[1], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_sequencing:{RELEASE_SEQUENCING_MARKERS[1]}",
        )

        write_fixture_tree(base)
        sequencing_path = base / RELEASE_SEQUENCING_PATH
        sequencing_path.write_text(
            sequencing_path.read_text(encoding="utf-8").replace(
                RELEASE_SEQUENCING_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_sequencing:{RELEASE_SEQUENCING_MARKERS[2]}",
        )

        write_fixture_tree(base)
        coordination_matrix_path = base / RELEASE_COORDINATION_MATRIX_PATH
        coordination_matrix_path.write_text(
            coordination_matrix_path.read_text(encoding="utf-8").replace(
                RELEASE_COORDINATION_MATRIX_MARKERS[1], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "release_coordination_matrix:"
            f"{RELEASE_COORDINATION_MATRIX_MARKERS[1]}",
        )

        write_fixture_tree(base)
        coordination_matrix_path = base / RELEASE_COORDINATION_MATRIX_PATH
        coordination_matrix_path.write_text(
            coordination_matrix_path.read_text(encoding="utf-8").replace(
                RELEASE_COORDINATION_MATRIX_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "release_coordination_matrix:"
            f"{RELEASE_COORDINATION_MATRIX_MARKERS[2]}",
        )

        write_fixture_tree(base)
        raw_coverage_path = base / RAW_GITHUB_COVERAGE_SURVEY_PATH
        raw_coverage_path.write_text(
            raw_coverage_path.read_text(encoding="utf-8").replace(
                RAW_GITHUB_COVERAGE_SURVEY_MARKERS[5],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"raw_github_coverage_survey:{RAW_GITHUB_COVERAGE_SURVEY_MARKERS[5]}",
        )

        write_fixture_tree(base)
        tests_readme_path = base / TESTS_README_PATH
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(
                TESTS_README_MARKERS[13],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"tests_readme:{TESTS_README_MARKERS[13]}",
        )

        write_fixture_tree(base)
        tests_readme_path = base / TESTS_README_PATH
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(
                TESTS_README_MARKERS[14],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"tests_readme:{TESTS_README_MARKERS[14]}",
        )

        write_fixture_tree(base)
        scripts_readme_path = base / SCRIPTS_README_PATH
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                SCRIPTS_README_MARKERS[14],
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"scripts_readme:{SCRIPTS_README_MARKERS[14]}",
        )

        write_fixture_tree(base)
        closure_checklist_path = base / RELEASE_CLOSURE_CHECKLIST_PATH
        closure_checklist_path.write_text(
            closure_checklist_path.read_text(encoding="utf-8").replace(
                RELEASE_CLOSURE_CHECKLIST_MARKERS[5], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"release_closure_checklist:{RELEASE_CLOSURE_CHECKLIST_MARKERS[5]}",
        )

        write_fixture_tree(base)
        lane_note_path = base / COMPLEX_DRIVER_LANE_SEQUENCING_PATH
        lane_note_path.write_text(
            lane_note_path.read_text(encoding="utf-8").replace(
                COMPLEX_DRIVER_LANE_SEQUENCING_MARKERS[5], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"complex_driver_lane_sequencing:{COMPLEX_DRIVER_LANE_SEQUENCING_MARKERS[5]}",
        )

        write_fixture_tree(base)
        libbpf_lane_path = base / LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_PATH
        libbpf_lane_path.write_text(
            libbpf_lane_path.read_text(encoding="utf-8").replace(
                LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_MARKERS[4], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "libbpf_heavy_consumer_lane_sequencing:"
            f"{LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_MARKERS[4]}",
        )

        write_fixture_tree(base)
        verify_note_path = base / LIBBPF_VERIFY_SHARD_NOTE_PATH
        verify_note_path.write_text(
            verify_note_path.read_text(encoding="utf-8").replace(
                LIBBPF_VERIFY_SHARD_NOTE_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"libbpf_verify_shard_note:{LIBBPF_VERIFY_SHARD_NOTE_MARKERS[2]}",
        )

        write_fixture_tree(base)
        survey_path = base / LIBBPF_SEGMENT_SURVEY_PATH
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                LIBBPF_SEGMENT_SURVEY_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"libbpf_segment_survey:{LIBBPF_SEGMENT_SURVEY_MARKERS[2]}",
        )

        write_fixture_tree(base)
        build_path = base / PHASE12_BUILD_PATH
        build_path.write_text(
            build_path.read_text(encoding="utf-8").replace(
                'smoke_step.dependOn(&run_virtio_net_syntax_tests.step);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "phase12_build:smoke_step.dependOn(&run_virtio_net_syntax_tests.step);",
        )

        write_fixture_tree(base)
        build_path = base / PHASE12_BUILD_PATH
        build_path.write_text(
            build_path.read_text(encoding="utf-8").replace(
                "const packet_tests = b.addTest(.{",
                "const packet_tests = b.addExecutable(.{",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "phase12_build_exact_count:b.addTest(.{:expected=6:actual=5",
        )

        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=29")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 12 build-only contract around the "
            "starter-present virtio-net packet, the shipped virtio-scsi smoke route, "
            "and the shared complex-driver release reminders."
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
        print("PHASE12_BUILD_ONLY_SURFACE=fail")
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_END")
        return 1

    marker_count = (
        len(REQUIRED_FILES)
        + len(DOCS_ROOT_MARKERS)
        + len(DOCS_ROOT_FORBIDDEN_MARKERS)
        + len(REVIEW_CHECKLIST_MARKERS)
        + len(SCRIPTS_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(RELEASE_READINESS_SURVEY_MARKERS)
        + len(RELEASE_SEQUENCING_MARKERS)
        + len(RELEASE_COORDINATION_MATRIX_MARKERS)
        + len(RELEASE_CLOSURE_CHECKLIST_MARKERS)
        + len(COMPLEX_DRIVER_LANE_SEQUENCING_MARKERS)
        + len(LIBBPF_HEAVY_CONSUMER_LANE_SEQUENCING_MARKERS)
        + len(LIBBPF_VERIFY_SHARD_NOTE_MARKERS)
        + len(LIBBPF_SEGMENT_SURVEY_MARKERS)
        + len(RAW_GITHUB_COVERAGE_SURVEY_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(MAKEFILE_MARKERS)
        + len(PHASE12_BUILD_MARKERS)
        + len(PHASE12_BUILD_EXACT_COUNTS)
    )
    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(f"PHASE12_BUILD_ONLY_SURFACE_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

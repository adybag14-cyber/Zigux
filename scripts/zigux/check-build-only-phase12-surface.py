#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/tests/phase12_build.zig").exists() and (
            candidate / "zigux/Makefile"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
BUILD_INVENTORY_CHECKER_PATH = "scripts/zigux/check-phase12-build-inventory.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
DOCS_ROOT_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH = (
    "drivers/net/virtio_net_queue_resume.zig"
)
PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH = (
    "drivers/net/virtio_net_transmit_recycle.zig"
)
PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_DRIVER_PATH = (
    "drivers/net/virtio_net_receive_refill_replay.zig"
)
PHASE12_VIRTIO_NET_POST_RESET_REPLAY_DRIVER_PATH = (
    "drivers/net/virtio_net_post_reset_replay.zig"
)
PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_DRIVER_PATH = (
    "drivers/net/virtio_net_throughput_parity.zig"
)
PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_queue_resume.zig"
)
PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig"
)
PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_receive_refill_replay.zig"
)
PHASE12_VIRTIO_NET_POST_RESET_REPLAY_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_post_reset_replay.zig"
)
PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_throughput_parity.zig"
)
PHASE12_VIRTIO_NET_SURVEY_TEST_PATH = "zigux/tests/phase12_virtio_net_survey.zig"
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
VIRTIO_SCSI_FALLBACK_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
NVME_FALLBACK_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
RELEASE_COORDINATION_MATRIX_MARKERS = [
    "readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`",
    "verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
    "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "- `scripts/zigux/check-phase12-complex-driver-lane-packet.py`",
    "- `scripts/zigux/check-phase12-libbpf-snapshot.py`",
    "- `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`",
]
DOCS_ROOT_MARKERS = [
    "* keep the degraded-read fallback split explicit here too: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the one commit-pinned direct replay catalog, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` is the driver-local current-master gap-note companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than extra commit-pinned fallback artifacts.\n",
]
REVIEW_CHECKLIST_MARKERS = [
    "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof",
    "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
]
RELEASE_SEQUENCING_MARKERS = [
    "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
    "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
    "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
    "Current workflow-side fallback recovery evidence: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` path by first trying the pinned `third_party` archive, then the Zig community-mirror list, and finally `ziglang.org`, so this sequencing note should treat the local Makefile fallback as a restorable local-first path before attached-`ZIG=<attached-zig-path>` reruns rather than as a one-shot cache hit.",
]
RELEASE_CLOSURE_CHECKLIST_MARKERS = [
    "- shared fallback companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "- The fallback split stays truthful: one commit-pinned `virtio_scsi` replay catalog, one current-master `nvme_pci` gap-inventory companion, and two shared-tree anchors.",
    "If `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    "shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
    "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-test ZIG=<attached-zig-path>`",
    "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12 ZIG=<attached-zig-path>`",
]
SCRIPTS_README_MARKERS = [
    "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
]
TESTS_README_MARKERS = [
    "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
    "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
    "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
]
RAW_GITHUB_COVERAGE_SURVEY_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
RAW_GITHUB_COVERAGE_MARKER = (
    "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, "
    "the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed "
    "shared support bundle are distinct evidence states in this runtime"
)
RAW_GITHUB_COVERAGE_RETURNED_WRAPPER_MARKER = (
    "now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again, so treat the readable Makefile as bounded support evidence for the returned validator-first plus smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable"
)
RAW_GITHUB_COVERAGE_LOCAL_FIRST_WORKFLOW_MARKER = (
    "`.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org`, so treat the Makefile fallback as a restorable local-first degraded-workflow path before falling back to attached `ZIG=<attached-zig-path>` reruns"
)
VIRTIO_SCSI_FALLBACK_MARKERS = [
    "- exact current shared support-bundle and replay order is `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
    "- `make -C zigux phase12-validate` is current repo evidence again and now reruns the shared build-only, complex-driver, cross-compile smoke, release-readiness, libbpf snapshot, libbpf heavy-consumer, and `virtio_net` packet checkers plus `scripts/zigux/validate-phase12.py`",
]
NVME_FALLBACK_MARKERS = [
    "Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local gap note too:",
    "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
    "5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
    "6. shipped wrapper evidence on current `master`: `make -C zigux phase12`",
]
MAKEFILE_FALLBACK_MARKERS = [
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
]
STALE_SHARED_ROUTE_MARKERS = [
    '"phase12_virtio_net.zig"',
    '"phase12_virtio_net_syntax_lab.zig"',
    '"phase12_virtio_scsi.zig"',
    '"phase12_virtio_scsi_syntax_lab.zig"',
    '"phase12_virtio_scsi_repeated_replan_gate.zig"',
    '"phase12_virtio_scsi_repeated_rollback_gate.zig"',
    '"phase12_virtio_scsi_packet.zig"',
    "phase12-virtio-net-tests",
    "phase12-virtio-net-syntax-lab-tests",
]

REQUIRED_FILES = [
    BUILD_ONLY_CHECKER_PATH,
    BUILD_INVENTORY_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    DOCS_ROOT_README_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
    PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH,
    PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH,
    PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_DRIVER_PATH,
    PHASE12_VIRTIO_NET_POST_RESET_REPLAY_DRIVER_PATH,
    PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_DRIVER_PATH,
    PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH,
    PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH,
    PHASE12_VIRTIO_NET_RECEIVE_REFILL_REPLAY_TEST_PATH,
    PHASE12_VIRTIO_NET_POST_RESET_REPLAY_TEST_PATH,
    PHASE12_VIRTIO_NET_THROUGHPUT_PARITY_TEST_PATH,
    PHASE12_VIRTIO_NET_SURVEY_TEST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    VIRTIO_SCSI_FALLBACK_PATH,
    NVME_FALLBACK_PATH,
]

REQUIRED_MARKERS = {
    VALIDATOR_PATH: [
        BUILD_ONLY_CHECKER_PATH,
        BUILD_INVENTORY_CHECKER_PATH,
        RELEASE_READINESS_CHECKER_PATH,
        "make -C zigux phase12-validate",
        "stale reminder vocabulary",
        "scripts-side support packet",
    ],
    DOCS_ROOT_README_PATH: DOCS_ROOT_MARKERS,
    REVIEW_CHECKLIST_PATH: REVIEW_CHECKLIST_MARKERS,
    RELEASE_SEQUENCING_PATH: RELEASE_SEQUENCING_MARKERS,
    RELEASE_CLOSURE_CHECKLIST_PATH: RELEASE_CLOSURE_CHECKLIST_MARKERS,
    SCRIPTS_README_PATH: SCRIPTS_README_MARKERS,
    TESTS_README_PATH: TESTS_README_MARKERS,
    MAKEFILE_PATH: [
        *MAKEFILE_FALLBACK_MARKERS,
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    PHASE12_BUILD_PATH: [
        '"phase12_virtio_net_queue_resume.zig"',
        '"phase12_virtio_net_transmit_recycle.zig"',
        '"phase12_virtio_net_receive_refill_replay.zig"',
        '"phase12_virtio_net_post_reset_replay.zig"',
        '"phase12_virtio_net_throughput_parity.zig"',
        '"phase12_virtio_net_survey.zig"',
        '"phase12-virtio-net-survey-tests"',
        '"phase12-virtio-net-throughput-parity"',
        "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_survey_tests.step);",
        "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
        "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);",
        "test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);",
        "test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "test_step.dependOn(&run_virtio_net_survey_tests.step);",
        "throughput_parity_step.dependOn(&run_virtio_net_throughput_parity_tests.step);",
        "throughput-parity, and survey-gate smoke tests",
        "throughput-parity, and survey-gate tests",
        "throughput-parity replay in isolation",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 build-only surface checker",
        "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Check current Phase 12 build-only surface",
        "        run: python3 scripts/zigux/check-build-only-phase12-surface.py",
        "- name: Self-test current Phase 12 build inventory checker",
        "        run: python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
        "- name: Check current Phase 12 build inventory packet",
        "        run: python3 scripts/zigux/check-phase12-build-inventory.py",
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Check current Phase 12 release-readiness packet",
        "        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
        "- name: Validate current Phase 12 support bundle",
        "        run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 smoke packet",
        "        run: make -C zigux phase12-smoke",
        "- name: Run current Phase 12 shared test packet",
        "        run: make -C zigux phase12-test",
        "- name: Run current Phase 12 aggregate route",
        "        run: make -C zigux phase12",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: RELEASE_COORDINATION_MATRIX_MARKERS,
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        RAW_GITHUB_COVERAGE_MARKER,
        RAW_GITHUB_COVERAGE_RETURNED_WRAPPER_MARKER,
        RAW_GITHUB_COVERAGE_LOCAL_FIRST_WORKFLOW_MARKER,
        "    * `scripts/zigux/check-phase12-complex-driver-lane-packet.py`",
        "    * `scripts/zigux/check-phase12-libbpf-snapshot.py`",
        "    * `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: VIRTIO_SCSI_FALLBACK_MARKERS,
    NVME_FALLBACK_PATH: NVME_FALLBACK_MARKERS,
}

PHASE12_BUILD_EXACT_COUNTS = {
    "b.createModule(.{": 11,
    ".addImport(": 5,
    "b.addTest(.{": 6,
    "b.addRunArtifact(": 6,
    "smoke_step.dependOn(": 6,
    "test_step.dependOn(": 6,
    "b.step(": 3,
}

FORBIDDEN_MARKERS = {
    PHASE12_BUILD_PATH: [*STALE_SHARED_ROUTE_MARKERS],
    MAKEFILE_PATH: [*STALE_SHARED_ROUTE_MARKERS],
    WORKFLOW_PATH: [*STALE_SHARED_ROUTE_MARKERS],
}

EXACT_LINE_MARKER_PATHS = {WORKFLOW_PATH, SCRIPTS_README_PATH}


def normalize_exact_line(text: str) -> str:
    normalized = text.lstrip()
    if normalized.startswith("- "):
        return normalized[2:]
    return normalized


def has_required_marker(rel_path: str, text: str, marker: str) -> bool:
    if rel_path in EXACT_LINE_MARKER_PATHS:
        normalized_marker = normalize_exact_line(marker)
        return normalized_marker in [
            normalize_exact_line(line) for line in text.splitlines()
        ]
    return marker in text


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

    build_text = (root / PHASE12_BUILD_PATH).read_text(encoding="utf-8")
    for marker, expected in PHASE12_BUILD_EXACT_COUNTS.items():
        actual = build_text.count(marker)
        if actual != expected:
            failures.append(
                f"exact_count:{PHASE12_BUILD_PATH}:{marker}:expected={expected}:actual={actual}"
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


def minimal_phase12_build() -> str:
    return """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const virtio_net_queue_resume_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/net/virtio_net_queue_resume.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_queue_resume_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_queue_resume.zig\"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_queue_resume_root_module.addImport(
        \"virtio_net_queue_resume\",
        virtio_net_queue_resume_module,
    );

    const virtio_net_transmit_recycle_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/net/virtio_net_transmit_recycle.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_transmit_recycle_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_transmit_recycle.zig\"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_transmit_recycle_root_module.addImport(
        \"virtio_net_transmit_recycle\",
        virtio_net_transmit_recycle_module,
    );

    const virtio_net_receive_refill_replay_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/net/virtio_net_receive_refill_replay.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_receive_refill_replay_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_receive_refill_replay.zig\"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_receive_refill_replay_root_module.addImport(
        \"virtio_net_receive_refill_replay\",
        virtio_net_receive_refill_replay_module,
    );

    const virtio_net_post_reset_replay_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/net/virtio_net_post_reset_replay.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_post_reset_replay_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_post_reset_replay.zig\"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_post_reset_replay_root_module.addImport(
        \"virtio_net_post_reset_replay\",
        virtio_net_post_reset_replay_module,
    );

    const virtio_net_throughput_parity_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/net/virtio_net_throughput_parity.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const virtio_net_throughput_parity_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_throughput_parity.zig\"),
        .target = target,
        .optimize = optimize,
    });
    virtio_net_throughput_parity_root_module.addImport(
        \"virtio_net_throughput_parity\",
        virtio_net_throughput_parity_module,
    );

    const virtio_net_survey_root_module = b.createModule(.{
        .root_source_file = b.path(\"phase12_virtio_net_survey.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const phase12_virtio_net_queue_resume_tests = b.addTest(.{
        .name = \"phase12-virtio-net-queue-resume-tests\",
        .root_module = virtio_net_queue_resume_root_module,
    });
    const run_virtio_net_queue_resume_tests = b.addRunArtifact(
        phase12_virtio_net_queue_resume_tests,
    );

    const phase12_virtio_net_transmit_recycle_tests = b.addTest(.{
        .name = \"phase12-virtio-net-transmit-recycle-tests\",
        .root_module = virtio_net_transmit_recycle_root_module,
    });
    const run_virtio_net_transmit_recycle_tests = b.addRunArtifact(
        phase12_virtio_net_transmit_recycle_tests,
    );

    const phase12_virtio_net_receive_refill_replay_tests = b.addTest(.{
        .name = \"phase12-virtio-net-receive-refill-replay-tests\",
        .root_module = virtio_net_receive_refill_replay_root_module,
    });
    const run_virtio_net_receive_refill_replay_tests = b.addRunArtifact(
        phase12_virtio_net_receive_refill_replay_tests,
    );

    const phase12_virtio_net_post_reset_replay_tests = b.addTest(.{
        .name = \"phase12-virtio-net-post-reset-replay-tests\",
        .root_module = virtio_net_post_reset_replay_root_module,
    });
    const run_virtio_net_post_reset_replay_tests = b.addRunArtifact(
        phase12_virtio_net_post_reset_replay_tests,
    );

    const phase12_virtio_net_throughput_parity_tests = b.addTest(.{
        .name = \"phase12-virtio-net-throughput-parity-tests\",
        .root_module = virtio_net_throughput_parity_root_module,
    });
    const run_virtio_net_throughput_parity_tests = b.addRunArtifact(
        phase12_virtio_net_throughput_parity_tests,
    );

    const phase12_virtio_net_survey_tests = b.addTest(.{
        .name = \"phase12-virtio-net-survey-tests\",
        .root_module = virtio_net_survey_root_module,
    });
    const run_virtio_net_survey_tests = b.addRunArtifact(
        phase12_virtio_net_survey_tests,
    );

    const smoke_step = b.step(
        \"smoke\",
        \"Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate smoke tests\",
    );
    smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    smoke_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    smoke_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    smoke_step.dependOn(&run_virtio_net_survey_tests.step);

    const test_step = b.step(
        \"test\",
        \"Run the Phase 12 virtio_net queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate tests\",
    );
    test_step.dependOn(&run_virtio_net_queue_resume_tests.step);
    test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);
    test_step.dependOn(&run_virtio_net_receive_refill_replay_tests.step);
    test_step.dependOn(&run_virtio_net_post_reset_replay_tests.step);
    test_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
    test_step.dependOn(&run_virtio_net_survey_tests.step);

    const throughput_parity_step = b.step(
        \"phase12-virtio-net-throughput-parity\",
        \"Run the Phase 12 virtio_net throughput-parity replay in isolation\",
    );
    throughput_parity_step.dependOn(&run_virtio_net_throughput_parity_tests.step);
}
"""


def fixture_text(rel_path: str) -> str:
    if rel_path in REQUIRED_MARKERS:
        title = {
            VALIDATOR_PATH: "# Phase 12 Support Validator",
            DOCS_ROOT_README_PATH: "# Zigux Documentation",
            REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
            SCRIPTS_README_PATH: "# scripts/zigux",
            TESTS_README_PATH: "# zigux/tests",
            WORKFLOW_PATH: "name: zigux-bootstrap",
            RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            VIRTIO_SCSI_FALLBACK_PATH: "# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog",
            NVME_FALLBACK_PATH: "# Phase 12 NVMe PCI Raw GitHub Fallback Map",
        }.get(rel_path, "# Fixture")
        if rel_path == PHASE12_BUILD_PATH:
            return minimal_phase12_build()
        if rel_path in {VALIDATOR_PATH, MAKEFILE_PATH, WORKFLOW_PATH}:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    return "fixture\n"


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
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def corrupt_exact_count(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    replacement = {
        "b.createModule(.{": "b.createExecutable(.{",
        ".addImport(": ".addAnonymousImport(",
        "b.addTest(.{": "b.addExecutable(.{",
        "b.addRunArtifact(": "b.addInstallArtifact(",
        "smoke_step.dependOn(": "smoke_step.addError(",
        "test_step.dependOn(": "test_step.addError(",
        "b.step(": "b.option(",
    }[marker]
    updated = text.replace(marker, replacement, 1)
    if updated == text:
        raise SystemExit(f"exact-count marker not corruptible: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
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

        for rel_path, markers in FORBIDDEN_MARKERS.items():
            for marker in markers:
                write_fixture_tree(base)
                write_text(
                    base / rel_path,
                    (base / rel_path).read_text(encoding="utf-8") + f"{marker}\n",
                )
                expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        for marker, expected in PHASE12_BUILD_EXACT_COUNTS.items():
            write_fixture_tree(base)
            corrupt_exact_count(base / PHASE12_BUILD_PATH, marker)
            expect_failure(
                base,
                f"exact_count:{PHASE12_BUILD_PATH}:{marker}:expected={expected}:actual={expected - 1}",
            )

        write_fixture_tree(base)
        scripts_readme_path = base / SCRIPTS_README_PATH
        remove_marker(scripts_readme_path, SCRIPTS_README_MARKERS[1])
        expect_failure(
            base,
            "missing_marker:" f"{SCRIPTS_README_PATH}:{SCRIPTS_README_MARKERS[1]}",
        )

        write_fixture_tree(base)
        tests_readme_path = base / TESTS_README_PATH
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(
                TESTS_README_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:" f"{TESTS_README_PATH}:{TESTS_README_MARKERS[2]}",
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
            "missing_marker:"
            f"{RELEASE_SEQUENCING_PATH}:{RELEASE_SEQUENCING_MARKERS[1]}",
        )

        write_fixture_tree(base)
        review_checklist_path = base / REVIEW_CHECKLIST_PATH
        review_checklist_path.write_text(
            review_checklist_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[0], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:"
            f"{REVIEW_CHECKLIST_PATH}:{REVIEW_CHECKLIST_MARKERS[0]}",
        )

        write_fixture_tree(base)
        review_checklist_path = base / REVIEW_CHECKLIST_PATH
        review_checklist_path.write_text(
            review_checklist_path.read_text(encoding="utf-8").replace(
                REVIEW_CHECKLIST_MARKERS[1], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:"
            f"{REVIEW_CHECKLIST_PATH}:{REVIEW_CHECKLIST_MARKERS[1]}",
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
            "missing_marker:"
            f"{RELEASE_COORDINATION_MATRIX_PATH}:{RELEASE_COORDINATION_MATRIX_MARKERS[1]}",
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
            "missing_marker:"
            f"{RELEASE_COORDINATION_MATRIX_PATH}:{RELEASE_COORDINATION_MATRIX_MARKERS[2]}",
        )

        write_fixture_tree(base)
        coordination_matrix_path = base / RELEASE_COORDINATION_MATRIX_PATH
        coordination_matrix_path.write_text(
            coordination_matrix_path.read_text(encoding="utf-8").replace(
                RELEASE_COORDINATION_MATRIX_MARKERS[3], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:"
            f"{RELEASE_COORDINATION_MATRIX_PATH}:{RELEASE_COORDINATION_MATRIX_MARKERS[3]}",
        )

        write_fixture_tree(base)
        raw_coverage_path = base / RAW_GITHUB_COVERAGE_SURVEY_PATH
        raw_coverage_path.write_text(
            raw_coverage_path.read_text(encoding="utf-8").replace(
                RAW_GITHUB_COVERAGE_MARKER, "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:"
            f"{RAW_GITHUB_COVERAGE_SURVEY_PATH}:{RAW_GITHUB_COVERAGE_MARKER}",
        )

        write_fixture_tree(base)
        raw_coverage_path = base / RAW_GITHUB_COVERAGE_SURVEY_PATH
        raw_coverage_path.write_text(
            raw_coverage_path.read_text(encoding="utf-8").replace(
                RAW_GITHUB_COVERAGE_RETURNED_WRAPPER_MARKER, "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:"
            f"{RAW_GITHUB_COVERAGE_SURVEY_PATH}:{RAW_GITHUB_COVERAGE_RETURNED_WRAPPER_MARKER}",
        )

        write_fixture_tree(base)
        raw_coverage_path = base / RAW_GITHUB_COVERAGE_SURVEY_PATH
        raw_coverage_path.write_text(
            raw_coverage_path.read_text(encoding="utf-8").replace(
                RAW_GITHUB_COVERAGE_LOCAL_FIRST_WORKFLOW_MARKER, "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:"
            f"{RAW_GITHUB_COVERAGE_SURVEY_PATH}:{RAW_GITHUB_COVERAGE_LOCAL_FIRST_WORKFLOW_MARKER}",
        )

        write_fixture_tree(base)
        workflow_path = base / WORKFLOW_PATH
        workflow_path.write_text(
            "\n".join(
                f"    {line}"
                for line in workflow_path.read_text(encoding="utf-8").splitlines()
            )
            + "\n",
            encoding="utf-8",
        )
        failures = validate(base)
        if failures:
            raise SystemExit(
                "indented workflow fixture should still pass but failed: "
                f"{failures!r}"
            )

        case_count = (
            len(REQUIRED_FILES)
            + len(marker_cases)
            + sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
            + len(PHASE12_BUILD_EXACT_COUNTS)
            + 12
        )
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print(f"PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 12 build-only contract around the "
            "returned smoke-and-test wrappers, the build-inventory contract, the docs-root, review-checklist, "
            "release-sequencing, scripts-root, tests-root, and closure-checklist "
            "degraded fallback wording, the two fallback-note smoke-order reminders, "
            "and the split-helper virtio_net packet."
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
            print(f"PHASE12_BUILD_ONLY_SURFACE=fail:{failure}")
        return 1

    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(f"PHASE12_BUILD_ONLY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
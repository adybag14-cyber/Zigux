#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
VIRTIO_SCSI_FALLBACK_PATH = "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
RUNTIME_EVIDENCE_PATHS = [
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]
RUNTIME_EVIDENCE_ERROR = (
    f"{RAW_GITHUB_COVERAGE_PATH}: exact runtime-reality evidence line drifted from current "
    "blob SHAs for scripts/zigux/check-phase12-release-readiness-packet.py, zigux/Makefile, "
    "and .github/workflows/zigux-bootstrap.yml"
)
RUNTIME_EVIDENCE_SUFFIX = (
    "; `zigux/Makefile` now first tries the repo-local `.zig-toolchain` fallback through "
    "`ZIG_PINNED_TOOLCHAIN`, `ZIG_LOCAL_TOOLCHAIN`, and `ZIG ?= $(if "
    "$(ZIG_LOCAL_TOOLCHAIN),$(ZIG_LOCAL_TOOLCHAIN),zig)` before any attached override is "
    "needed, so the bounded degraded-workflow support route stays the shipped "
    "`make -C zigux phase12-validate` plus the same `phase12-smoke` and `phase12` "
    "Make routes rather than a second direct replay packet."
)

REQUIRED_FILES = [
    "drivers/net/virtio_net.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/scsi/virtio_scsi.zig",
    "drivers/nvme/host/pci.zig",
    "drivers/nvme/host/pci_verify.zig",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    RAW_GITHUB_COVERAGE_PATH,
    VIRTIO_SCSI_FALLBACK_PATH,
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    "zigux/tests/phase12_virtio_scsi_packet.zig",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_nvme_pci.zig",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "scripts/zigux/check-build-only-phase12-surface.py",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "scripts/zigux/check-phase12-virtio-scsi-packet.py",
    "scripts/zigux/validate-phase12.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

EXPECTED_ABSENT_FILES: list[str] = []

REQUIRED_MARKERS = {
    "Documentation/zigux/phase12-release-readiness-survey.md": [
        "`PHASE12_STATUS=active`",
        "`PHASE12_RELEASE_CLOSED=no`",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "make -C zigux phase12-validate",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
        "- `scripts/zigux/validate-phase12.py`",
        "- `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "- `zigux/Makefile`",
        "- `.github/workflows/zigux-bootstrap.yml`",
        "- `make -C zigux phase12-validate`",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "`PHASE12_STATUS=active`",
        "- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`",
        "- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`",
        "- survey replay: `zigux/tests/phase12_virtio_scsi_survey.zig`",
        "- `scripts/zigux/validate-phase12.py`",
        "- `make -C zigux phase12-validate`",
        "shared-tree current-master survey companions",
    ],
    "Documentation/zigux/phase12-virtio-net-survey.md": [
        "`PHASE12_STATUS=starter-present-transmit-recycle-followup`",
        "current `master` now also carries `drivers/net/virtio_net_transmit_recycle.zig`",
        "summarizeTransmitRecycle()",
        "current `master` now carries `zigux/tests/phase12_virtio_net_transmit_recycle.zig`",
        "still does not claim live DMA-safe receive ownership",
    ],
    "Documentation/zigux/phase12-virtio-scsi-survey.md": [
        "`PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey`",
        "`PHASE12_LANE=P12-L13`",
        "current `master` now carries `drivers/scsi/virtio_scsi.zig`",
        "captureRequestSubmitSequencingSummary()",
        "captureCompletionHandbackSummary()",
        "captureCommandBufferOwnershipSummary()",
        "phase12_virtio_scsi_repeated_rollback_gate.zig",
        "fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "make -C zigux phase12-smoke",
        "still does not claim live DMA-safe request submission",
    ],
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md": [
        "`PHASE12_STATUS=active`",
        "`PHASE12_SLICE=nvme-pci-raw-github-fallback-map`",
        "`PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`",
        "Current `master` now ships seven bounded NVMe reviewability surfaces:",
        "- starter shard: `drivers/nvme/host/pci.zig`",
        "- verifier shard: `drivers/nvme/host/pci_verify.zig`",
        "- direct replay: `zigux/tests/phase12_nvme_pci.zig`",
        "- survey gate: `zigux/tests/phase12_nvme_pci_survey.zig`",
        "- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`",
        "- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes",
        "- use this file only as a read-only routing inventory; it does not add a new replay surface",
    ],
    "Documentation/zigux/phase12-nvme-pci-survey.md": [
        "`PHASE12_STATUS=starter-present-slice-note-survey-packet`",
        "`PHASE12_LANE=P12-L08`",
        "current `master` now carries `drivers/nvme/host/pci.zig`",
        "planPrpBufferShape()",
        "recoveryQueueRestoreSummary()",
        "summarizeDroppedIoRetirement()",
        "still does not wire the bounded NVMe direct replay into `zigux/tests/phase12_build.zig`",
    ],
    "zigux/tests/phase12_build.zig": [
        "../../drivers/net/virtio_net.zig",
        '"phase12_virtio_net.zig"',
        '"phase12_virtio_net_syntax_lab.zig"',
        "phase12-virtio-net-tests",
        "phase12-virtio-net-syntax-lab-tests",
        "run_virtio_net_contract_tests.setCwd(b.path(\"../..\"));",
        "run_virtio_net_syntax_tests.setCwd(b.path(\"../..\"));",
        "../../drivers/net/virtio_net_transmit_recycle.zig",
        '"phase12_virtio_net_transmit_recycle.zig"',
        "phase12-virtio-net-transmit-recycle-tests",
        "run_virtio_net_transmit_recycle_tests.setCwd(b.path(\"../..\"));",
        "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_syntax_tests.step);",
        "test_step.dependOn(&run_virtio_net_contract_tests.step);",
        "../../drivers/scsi/virtio_scsi.zig",
        '"phase12_virtio_scsi.zig"',
        '"phase12_virtio_scsi_syntax_lab.zig"',
        '"phase12_virtio_scsi_repeated_replan_gate.zig"',
        '"phase12_virtio_scsi_repeated_rollback_gate.zig"',
        '"phase12_virtio_scsi_packet.zig"',
        "phase12-virtio-scsi-tests",
        "phase12-virtio-scsi-syntax-lab-tests",
        "phase12-virtio-scsi-repeated-replan-gate-tests",
        "phase12-virtio-scsi-repeated-rollback-gate-tests",
        "phase12-virtio-scsi-packet-tests",
        "run_contract_tests.setCwd(b.path(\"../..\"));",
        "run_syntax_tests.setCwd(b.path(\"../..\"));",
        "run_repeated_replan_tests.setCwd(b.path(\"../..\"));",
        "run_repeated_rollback_tests.setCwd(b.path(\"../..\"));",
        "run_packet_tests.setCwd(b.path(\"../..\"));",
        "b.step(\"smoke\", \"Run Phase 12 virtio syntax smoke\")",
        "smoke_step.dependOn(&run_repeated_rollback_tests.step);",
        "b.step(\"test\", \"Run Phase 12 virtio packet tests\")",
        "test_step.dependOn(&run_repeated_rollback_tests.step);",
    ],
    "zigux/tests/phase12_virtio_net_manifest.json": [
        "\"lane_key\": \"P12-L01\"",
        "\"phase\": \"Phase 12\"",
        "\"anchor\": \"drivers/net/virtio_net.c\"",
        "\"preexisting_phase12_build_present\": true",
        "\"preexisting_phase12_survey_note_present\": true",
        "\"preexisting_virtio_net_zig_present\": true",
        "\"phase12-build-gate\"",
        "\"shared_build_present_with_direct_virtio_net_syntax_lab_and_transmit_recycle_replay\"",
        "\"phase12-virtio-net-transmit-recycle-followup\"",
        "\"blocked_on_dma_transport_runtime\"",
    ],
    "zigux/tests/phase12_virtio_net_survey.zig": [
        "phase12 virtio net survey manifest keeps the bounded transmit-recycle packet truthful",
        "phase12 virtio net survey note stays aligned with the bounded transmit-recycle follow-up",
        "phase12 virtio net survey gate keeps present lane files explicit",
        "Documentation/zigux/phase12-virtio-net-survey.md",
        "drivers/net/virtio_net_transmit_recycle.zig",
        "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    ],
    "zigux/tests/phase12_virtio_scsi_manifest.json": [
        "\"lane_key\": \"P12-L13\"",
        "\"phase\": \"Phase 12\"",
        "\"anchor\": \"drivers/scsi/virtio_scsi.c\"",
        "\"preexisting_phase12_repeated_rollback_gate_present\": true",
        "\"preexisting_phase12_support_packet_present\": true",
        "\"preexisting_phase12_survey_note_present\": true",
        "\"preexisting_phase12_fallback_catalog_present\": true",
        "\"preexisting_phase12_survey_gate_present\": true",
        "\"blocked_on_dma_scsi_host_runtime\"",
    ],
    "zigux/tests/phase12_virtio_scsi_survey.zig": [
        "phase12 virtio scsi survey manifest keeps the bounded queue-and-recovery packet truthful",
        "phase12 virtio scsi survey note stays aligned with the bounded queue-and-recovery starter",
        "phase12 virtio scsi survey gate keeps present lane files explicit",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    ],
    "zigux/tests/phase12_nvme_pci_manifest.json": [
        "\"lane_key\": \"P12-L08\"",
        "\"phase\": \"Phase 12\"",
        "\"anchor\": \"drivers/nvme/host/pci.c\"",
        "\"preexisting_nvme_pci_zig_present\": true",
        "\"preexisting_nvme_pci_verifier_present\": true",
        "\"preexisting_phase12_direct_test_present\": true",
        "\"preexisting_phase12_survey_note_present\": true",
        "\"preexisting_phase12_survey_gate_present\": true",
    ],
    "zigux/tests/phase12_nvme_pci_survey.zig": [
        "phase12 nvme pci survey manifest keeps the bounded queue-and-recovery packet truthful",
        "phase12 nvme pci survey note stays aligned with the bounded queue-and-recovery starter",
        "phase12 nvme pci survey gate keeps present lane files explicit",
        "Documentation/zigux/phase12-nvme-pci-survey.md",
        "drivers/nvme/host/pci_verify.zig",
        "zigux/tests/phase12_nvme_pci.zig",
    ],
    "scripts/zigux/validate-phase12.py": [
        "--self-test",
        "PHASE12_VALIDATION=pass",
        "PHASE12_VALIDATOR_SELF_TEST=pass",
        RAW_GITHUB_COVERAGE_PATH,
        VIRTIO_SCSI_FALLBACK_PATH,
        "Documentation/zigux/phase12-virtio-net-survey.md",
        "drivers/net/virtio_net_transmit_recycle.zig",
        "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
        "zigux/tests/phase12_virtio_net_manifest.json",
        "zigux/tests/phase12_virtio_net_survey.zig",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "zigux/tests/phase12_virtio_scsi_survey.zig",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
        "Documentation/zigux/phase12-nvme-pci-slice.md",
        "Documentation/zigux/phase12-nvme-pci-survey.md",
        "zigux/tests/phase12_nvme_pci.zig",
        "zigux/tests/phase12_nvme_pci_manifest.json",
        "zigux/tests/phase12_nvme_pci_survey.zig",
        "scripts/zigux/check-phase12-release-readiness-packet.py",
        "scripts/zigux/check-phase12-virtio-scsi-packet.py",
        "PHASE12_EXPECTED_ABSENT_FILE_COUNT=0",
    ],
}

FIXTURE_OVERRIDES = {
    "drivers/net/virtio_net.zig": "// fixture\n",
    "drivers/net/virtio_net_transmit_recycle.zig": "// fixture\n",
    "drivers/scsi/virtio_scsi.zig": "// fixture\n",
    "drivers/nvme/host/pci.zig": "// fixture\n",
    "drivers/nvme/host/pci_verify.zig": "// fixture\n",
    "Documentation/zigux/phase12-release-closure-checklist.md": "# fixture\n",
    "Documentation/zigux/phase12-virtio-net-survey.md": "\n".join(
        REQUIRED_MARKERS["Documentation/zigux/phase12-virtio-net-survey.md"]
    )
    + "\n",
    "Documentation/zigux/phase12-virtio-scsi-slice.md": "# fixture\n",
    "Documentation/zigux/phase12-virtio-scsi-survey.md": "\n".join(
        REQUIRED_MARKERS["Documentation/zigux/phase12-virtio-scsi-survey.md"]
    )
    + "\n",
    VIRTIO_SCSI_FALLBACK_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_SCSI_FALLBACK_PATH]) + "\n",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md": "\n".join(
        REQUIRED_MARKERS["Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"]
    )
    + "\n",
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md": "# fixture\n",
    "Documentation/zigux/phase12-nvme-pci-slice.md": "# fixture\n",
    "Documentation/zigux/phase12-nvme-pci-survey.md": "\n".join(
        REQUIRED_MARKERS["Documentation/zigux/phase12-nvme-pci-survey.md"]
    )
    + "\n",
    "zigux/tests/phase12_virtio_net.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_net_survey.zig": "\n".join(
        f"// {marker}" for marker in REQUIRED_MARKERS["zigux/tests/phase12_virtio_net_survey.zig"]
    )
    + "\n",
    "zigux/tests/phase12_virtio_net_manifest.json": "{\n  \"lane_key\": \"P12-L01\",\n  \"phase\": \"Phase 12\",\n  \"anchor\": \"drivers/net/virtio_net.c\",\n  \"survey_summary\": {\n    \"preexisting_phase12_build_present\": true,\n    \"preexisting_phase12_survey_note_present\": true,\n    \"preexisting_virtio_net_zig_present\": true\n  },\n  \"gaps\": [\n    {\n      \"id\": \"phase12-build-gate\",\n      \"status\": \"shared_build_present_with_direct_virtio_net_syntax_lab_and_transmit_recycle_replay\"\n    },\n    {\n      \"id\": \"phase12-virtio-net-transmit-recycle-followup\",\n      \"status\": \"landed_on_master\"\n    },\n    {\n      \"id\": \"phase12-virtio-net-runtime-data-path\",\n      \"status\": \"blocked_on_dma_transport_runtime\"\n    }\n  ]\n}\n",
    "zigux/tests/phase12_virtio_scsi.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_packet.zig": "// fixture\n",
    "zigux/tests/phase12_virtio_scsi_manifest.json": "{\n  \"lane_key\": \"P12-L13\",\n  \"phase\": \"Phase 12\",\n  \"anchor\": \"drivers/scsi/virtio_scsi.c\",\n  \"survey_summary\": {\n    \"preexisting_phase12_repeated_rollback_gate_present\": true,\n    \"preexisting_phase12_support_packet_present\": true,\n    \"preexisting_phase12_survey_note_present\": true,\n    \"preexisting_phase12_fallback_catalog_present\": true,\n    \"preexisting_phase12_survey_gate_present\": true\n  },\n  \"gaps\": [\n    {\n      \"id\": \"phase12-virtio-scsi-runtime-request-flow\",\n      \"status\": \"blocked_on_dma_scsi_host_runtime\"\n    }\n  ]\n}\n",
    "zigux/tests/phase12_virtio_scsi_survey.zig": "\n".join(
        f"// {marker}" for marker in REQUIRED_MARKERS["zigux/tests/phase12_virtio_scsi_survey.zig"]
    )
    + "\n",
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json": "{\n  \"lane_key\": \"P12-L12\"\n}\n",
    "zigux/tests/phase12_nvme_pci.zig": "// fixture\n",
    "zigux/tests/phase12_nvme_pci_manifest.json": "{\n  \"lane_key\": \"P12-L08\",\n  \"phase\": \"Phase 12\",\n  \"anchor\": \"drivers/nvme/host/pci.c\",\n  \"survey_summary\": {\n    \"preexisting_nvme_pci_zig_present\": true,\n    \"preexisting_nvme_pci_verifier_present\": true,\n    \"preexisting_phase12_direct_test_present\": true,\n    \"preexisting_phase12_survey_note_present\": true,\n    \"preexisting_phase12_survey_gate_present\": true\n  }\n}\n",
    "zigux/tests/phase12_nvme_pci_survey.zig": "// phase12 nvme pci survey manifest keeps the bounded queue-and-recovery packet truthful\n// phase12 nvme pci survey note stays aligned with the bounded queue-and-recovery starter\n// phase12 nvme pci survey gate keeps present lane files explicit\n// Documentation/zigux/phase12-nvme-pci-survey.md\n// drivers/nvme/host/pci_verify.zig\n// zigux/tests/phase12_nvme_pci.zig\n",
    "scripts/zigux/check-build-only-phase12-surface.py": "#!/usr/bin/env python3\n",
    "scripts/zigux/check-phase12-release-readiness-packet.py": "#!/usr/bin/env python3\n",
    "scripts/zigux/check-phase12-virtio-scsi-packet.py": "#!/usr/bin/env python3\n",
    "zigux/Makefile": "phase12-validate:\n\t@true\n",
    ".github/workflows/zigux-bootstrap.yml": "name: zigux-bootstrap\n",
}

def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def runtime_evidence_line_fragment(root: Path) -> str:
    checker_sha = git_blob_sha(root / "scripts/zigux/check-phase12-release-readiness-packet.py")
    makefile_sha = git_blob_sha(root / "zigux/Makefile")
    workflow_sha = git_blob_sha(root / ".github/workflows/zigux-bootstrap.yml")
    return (
        ": current `master` ships "
        f"`scripts/zigux/check-phase12-release-readiness-packet.py` at blob `{checker_sha}`, "
        f"`zigux/Makefile` at blob `{makefile_sha}`, "
        f"and `.github/workflows/zigux-bootstrap.yml` at blob `{workflow_sha}`"
        f"{RUNTIME_EVIDENCE_SUFFIX}"
    )


def has_exact_runtime_evidence_line(root: Path) -> bool:
    expected_fragment = runtime_evidence_line_fragment(root)
    lines = (root / RAW_GITHUB_COVERAGE_PATH).read_text(encoding="utf-8").splitlines()
    matches = [
        line
        for line in lines
        if line.startswith("- exact runtime-reality evidence checked on `")
        and line.endswith(expected_fragment)
    ]
    return len(matches) == 1


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    if not has_exact_runtime_evidence_line(root):
        missing.append(RUNTIME_EVIDENCE_ERROR)
    return missing


def collect_unexpected_files(root: Path) -> list[str]:
    return [rel for rel in EXPECTED_ABSENT_FILES if (root / rel).exists()]


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, [], []

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        return [], missing_markers, []

    return [], [], collect_unexpected_files(root)


def write_raw_github_coverage_fixture(root: Path) -> None:
    survey_text = "\n".join(
        [
            "# Phase 12 Raw GitHub Coverage Survey",
            "",
            "- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
            "- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
            "- `scripts/zigux/validate-phase12.py`",
            "- `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "- `zigux/Makefile`",
            "- `.github/workflows/zigux-bootstrap.yml`",
            "- `make -C zigux phase12-validate`",
            f"- exact runtime-reality evidence checked on `2026-05-15`{runtime_evidence_line_fragment(root)}",
            "",
        ]
    )
    path = root / RAW_GITHUB_COVERAGE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(survey_text, encoding="utf-8")


def write_fixture_root(tmp_root: Path) -> None:
    fixture_text = {rel: "\n".join(markers) + "\n" for rel, markers in REQUIRED_MARKERS.items()}
    fixture_text.update(FIXTURE_OVERRIDES)
    for rel in REQUIRED_FILES:
        if rel == RAW_GITHUB_COVERAGE_PATH:
            continue
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text.get(rel, "// fixture\n"), encoding="utf-8")
    write_raw_github_coverage_fixture(tmp_root)


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_markers == [], case
    assert unexpected_files == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers, unexpected_files = validate(tmp_root)
    assert missing_files == [], case
    assert unexpected_files == [], case
    assert marker in missing_markers, case
    extras = [item for item in missing_markers if item != marker]
    assert extras in ([], [RUNTIME_EVIDENCE_ERROR]), case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def mutate_runtime_evidence_blob(tmp_root: Path) -> None:
    path = tmp_root / RAW_GITHUB_COVERAGE_PATH
    original = path.read_text(encoding="utf-8")
    makefile_sha = git_blob_sha(tmp_root / "zigux/Makefile")
    updated = original.replace(
        f"`zigux/Makefile` at blob `{makefile_sha}`",
        "`zigux/Makefile` at blob `0000000000000000000000000000000000000000`",
        1,
    )
    assert updated != original, "missing_raw_github_runtime_evidence_blob"
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_phase12_virtio_net_transmit_recycle_driver", "drivers/net/virtio_net_transmit_recycle.zig"),
        ("missing_phase12_virtio_net_transmit_recycle_test", "zigux/tests/phase12_virtio_net_transmit_recycle.zig"),
        ("missing_phase12_nvme_driver", "drivers/nvme/host/pci.zig"),
        ("missing_phase12_nvme_verify_shard", "drivers/nvme/host/pci_verify.zig"),
        (
            "missing_phase12_release_closure_checklist",
            "Documentation/zigux/phase12-release-closure-checklist.md",
        ),
        ("missing_phase12_raw_github_coverage_survey", RAW_GITHUB_COVERAGE_PATH),
        ("missing_phase12_virtio_scsi_fallback_catalog", VIRTIO_SCSI_FALLBACK_PATH),
        (
            "missing_phase12_virtio_scsi_slice_note",
            "Documentation/zigux/phase12-virtio-scsi-slice.md",
        ),
        (
            "missing_phase12_virtio_scsi_survey_note",
            "Documentation/zigux/phase12-virtio-scsi-survey.md",
        ),
        ("missing_phase12_nvme_survey_note", "Documentation/zigux/phase12-nvme-pci-survey.md"),
        (
            "missing_phase12_nvme_fallback_note",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        ),
        (
            "missing_phase12_nvme_reopen_governance",
            "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
        ),
        ("missing_phase12_nvme_slice_note", "Documentation/zigux/phase12-nvme-pci-slice.md"),
        (
            "missing_phase12_direct_repeated_rollback_gate",
            "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
        ),
        (
            "missing_phase12_virtio_scsi_survey_manifest",
            "zigux/tests/phase12_virtio_scsi_manifest.json",
        ),
        (
            "missing_phase12_virtio_scsi_survey_gate",
            "zigux/tests/phase12_virtio_scsi_survey.zig",
        ),
        (
            "missing_phase12_virtio_scsi_support_manifest",
            "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
        ),
        ("missing_phase12_nvme_direct_test", "zigux/tests/phase12_nvme_pci.zig"),
        ("missing_phase12_nvme_manifest", "zigux/tests/phase12_nvme_pci_manifest.json"),
        ("missing_phase12_nvme_survey_gate", "zigux/tests/phase12_nvme_pci_survey.zig"),
        (
            "missing_phase12_build_only_surface_checker",
            "scripts/zigux/check-build-only-phase12-surface.py",
        ),
        (
            "missing_phase12_release_readiness_checker",
            "scripts/zigux/check-phase12-release-readiness-packet.py",
        ),
        (
            "missing_phase12_virtio_scsi_packet_checker",
            "scripts/zigux/check-phase12-virtio-scsi-packet.py",
        ),
    ]

    marker_cases = [
        (
            "missing_release_readiness_status_marker",
            "Documentation/zigux/phase12-release-readiness-survey.md",
            "`PHASE12_STATUS=active`",
            "`PHASE12_STATUS=inactive`",
            "Documentation/zigux/phase12-release-readiness-survey.md: `PHASE12_STATUS=active`",
        ),
        (
            "missing_release_readiness_closure_checklist_marker",
            "Documentation/zigux/phase12-release-readiness-survey.md",
            "`Documentation/zigux/phase12-release-closure-checklist.md`",
            "`Documentation/zigux/phase12-release-closure-checklist-missing.md`",
            "Documentation/zigux/phase12-release-readiness-survey.md: `Documentation/zigux/phase12-release-closure-checklist.md`",
        ),
        (
            "missing_raw_github_makefile_marker",
            RAW_GITHUB_COVERAGE_PATH,
            "- `zigux/Makefile`",
            "- `zigux/Makefile-missing`",
            f"{RAW_GITHUB_COVERAGE_PATH}: - `zigux/Makefile`",
        ),
        (
            "missing_virtio_net_survey_status_marker",
            "Documentation/zigux/phase12-virtio-net-survey.md",
            "`PHASE12_STATUS=starter-present-transmit-recycle-followup`",
            "`PHASE12_STATUS=starter-present-missing`",
            "Documentation/zigux/phase12-virtio-net-survey.md: `PHASE12_STATUS=starter-present-transmit-recycle-followup`",
        ),
        (
            "missing_virtio_net_manifest_lane_key_marker",
            "zigux/tests/phase12_virtio_net_manifest.json",
            "\"lane_key\": \"P12-L01\"",
            "\"lane_key\": \"P12-L99\"",
            "zigux/tests/phase12_virtio_net_manifest.json: \"lane_key\": \"P12-L01\"",
        ),
        (
            "missing_virtio_net_manifest_build_gate_marker",
            "zigux/tests/phase12_virtio_net_manifest.json",
            "\"shared_build_present_with_direct_virtio_net_syntax_lab_and_transmit_recycle_replay\"",
            "\"shared_build_present_with_direct_virtio_net_syntax_lab_only\"",
            "zigux/tests/phase12_virtio_net_manifest.json: \"shared_build_present_with_direct_virtio_net_syntax_lab_and_transmit_recycle_replay\"",
        ),
        (
            "missing_virtio_net_manifest_transmit_recycle_gap_marker",
            "zigux/tests/phase12_virtio_net_manifest.json",
            "\"phase12-virtio-net-transmit-recycle-followup\"",
            "\"phase12-virtio-net-followup-missing\"",
            "zigux/tests/phase12_virtio_net_manifest.json: \"phase12-virtio-net-transmit-recycle-followup\"",
        ),
        (
            "missing_virtio_net_manifest_runtime_gap_marker",
            "zigux/tests/phase12_virtio_net_manifest.json",
            "\"blocked_on_dma_transport_runtime\"",
            "\"runtime_gap_missing\"",
            "zigux/tests/phase12_virtio_net_manifest.json: \"blocked_on_dma_transport_runtime\"",
        ),
        (
            "missing_virtio_net_survey_gate_marker",
            "zigux/tests/phase12_virtio_net_survey.zig",
            "phase12 virtio net survey gate keeps present lane files explicit",
            "phase12 virtio net survey gate keeps lane files explicit",
            "zigux/tests/phase12_virtio_net_survey.zig: phase12 virtio net survey gate keeps present lane files explicit",
        ),
        (
            "missing_phase12_build_transmit_recycle_source_marker",
            "zigux/tests/phase12_build.zig",
            "../../drivers/net/virtio_net_transmit_recycle.zig",
            "../../drivers/net/virtio_net_transmit_recycle_missing.zig",
            "zigux/tests/phase12_build.zig: ../../drivers/net/virtio_net_transmit_recycle.zig",
        ),
        (
            "missing_phase12_build_transmit_recycle_root_marker",
            "zigux/tests/phase12_build.zig",
            '"phase12_virtio_net_transmit_recycle.zig"',
            '"phase12_virtio_net_transmit_recycle_missing.zig"',
            'zigux/tests/phase12_build.zig: "phase12_virtio_net_transmit_recycle.zig"',
        ),
        (
            "missing_phase12_build_transmit_recycle_smoke_step_marker",
            "zigux/tests/phase12_build.zig",
            "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
            "smoke_step.dependOn(&run_repeated_replan_tests.step);",
            "zigux/tests/phase12_build.zig: smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        ),
        (
            "missing_phase12_build_transmit_recycle_test_step_marker",
            "zigux/tests/phase12_build.zig",
            "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
            "test_step.dependOn(&run_contract_tests.step);",
            "zigux/tests/phase12_build.zig: test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        ),
        (
            "missing_virtio_scsi_fallback_validate_route_marker",
            VIRTIO_SCSI_FALLBACK_PATH,
            "- `make -C zigux phase12-validate`",
            "- `make -C zigux phase12-validate-missing`",
            f"{VIRTIO_SCSI_FALLBACK_PATH}: - `make -C zigux phase12-validate`",
        ),
        (
            "missing_virtio_scsi_survey_lane_marker",
            "Documentation/zigux/phase12-virtio-scsi-survey.md",
            "`PHASE12_LANE=P12-L13`",
            "`PHASE12_LANE=P12-L12`",
            "Documentation/zigux/phase12-virtio-scsi-survey.md: `PHASE12_LANE=P12-L13`",
        ),
        (
            "missing_virtio_scsi_survey_fallback_marker",
            "Documentation/zigux/phase12-virtio-scsi-survey.md",
            "fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
            "fallback path: `Documentation/zigux/phase12-virtio-scsi-fallback-missing.md`",
            "Documentation/zigux/phase12-virtio-scsi-survey.md: fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        ),
        (
            "missing_phase12_build_repeated_rollback_source_marker",
            "zigux/tests/phase12_build.zig",
            '"phase12_virtio_scsi_repeated_rollback_gate.zig"',
            '"phase12_virtio_scsi_repeated_rollback_gate_missing.zig"',
            'zigux/tests/phase12_build.zig: "phase12_virtio_scsi_repeated_rollback_gate.zig"',
        ),
        (
            "missing_phase12_build_repeated_rollback_step_marker",
            "zigux/tests/phase12_build.zig",
            "smoke_step.dependOn(&run_repeated_rollback_tests.step);",
            "smoke_step.dependOn(&run_repeated_replan_tests.step);",
            "zigux/tests/phase12_build.zig: smoke_step.dependOn(&run_repeated_rollback_tests.step);",
        ),
        (
            "missing_virtio_scsi_manifest_lane_key_marker",
            "zigux/tests/phase12_virtio_scsi_manifest.json",
            "\"lane_key\": \"P12-L13\"",
            "\"lane_key\": \"P12-L12\"",
            "zigux/tests/phase12_virtio_scsi_manifest.json: \"lane_key\": \"P12-L13\"",
        ),
        (
            "missing_virtio_scsi_manifest_runtime_gap_marker",
            "zigux/tests/phase12_virtio_scsi_manifest.json",
            "\"blocked_on_dma_scsi_host_runtime\"",
            "\"runtime_gap_missing\"",
            "zigux/tests/phase12_virtio_scsi_manifest.json: \"blocked_on_dma_scsi_host_runtime\"",
        ),
        (
            "missing_virtio_scsi_survey_gate_marker",
            "zigux/tests/phase12_virtio_scsi_survey.zig",
            "phase12 virtio scsi survey gate keeps present lane files explicit",
            "phase12 virtio scsi survey gate keeps lane files explicit",
            "zigux/tests/phase12_virtio_scsi_survey.zig: phase12 virtio scsi survey gate keeps present lane files explicit",
        ),
        (
            "missing_nvme_fallback_status_marker",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
            "`PHASE12_STATUS=active`",
            "`PHASE12_STATUS=inactive`",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md: `PHASE12_STATUS=active`",
        ),
        (
            "missing_nvme_fallback_direct_packet_marker",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
            "`PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`",
            "`PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_missing`",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md: `PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`",
        ),
        (
            "missing_nvme_fallback_shared_build_gap_marker",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
            "- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes",
            "- `zigux/tests/phase12_build.zig` now wires the bounded NVMe direct replay into the shared `phase12-smoke` and `phase12` routes",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md: - `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes",
        ),
        (
            "missing_nvme_survey_lane_marker",
            "Documentation/zigux/phase12-nvme-pci-survey.md",
            "`PHASE12_LANE=P12-L08`",
            "`PHASE12_LANE=P12-L07`",
            "Documentation/zigux/phase12-nvme-pci-survey.md: `PHASE12_LANE=P12-L08`",
        ),
        (
            "missing_nvme_survey_recovery_marker",
            "Documentation/zigux/phase12-nvme-pci-survey.md",
            "recoveryQueueRestoreSummary()",
            "recoveryRestoreSummary()",
            "Documentation/zigux/phase12-nvme-pci-survey.md: recoveryQueueRestoreSummary()",
        ),
        (
            "missing_nvme_manifest_lane_key_marker",
            "zigux/tests/phase12_nvme_pci_manifest.json",
            "\"lane_key\": \"P12-L08\"",
            "\"lane_key\": \"P12-L05\"",
            "zigux/tests/phase12_nvme_pci_manifest.json: \"lane_key\": \"P12-L08\"",
        ),
        (
            "missing_nvme_manifest_survey_gate_marker",
            "zigux/tests/phase12_nvme_pci_manifest.json",
            "\"preexisting_phase12_survey_gate_present\": true",
            "\"preexisting_phase12_survey_gate_present\": false",
            "zigux/tests/phase12_nvme_pci_manifest.json: \"preexisting_phase12_survey_gate_present\": true",
        ),
        (
            "missing_nvme_survey_gate_marker",
            "zigux/tests/phase12_nvme_pci_survey.zig",
            "phase12 nvme pci survey gate keeps present lane files explicit",
            "phase12 nvme pci survey gate keeps lane files explicit",
            "zigux/tests/phase12_nvme_pci_survey.zig: phase12 nvme pci survey gate keeps present lane files explicit",
        ),
        (
            "missing_validator_self_test_flag",
            "scripts/zigux/validate-phase12.py",
            "--self-test",
            "--selftest",
            "scripts/zigux/validate-phase12.py: --self-test",
        ),
        (
            "missing_validator_virtio_net_survey_note_marker",
            "scripts/zigux/validate-phase12.py",
            "Documentation/zigux/phase12-virtio-net-survey.md",
            "Documentation/zigux/phase12-virtio-net-survey-missing.md",
            "scripts/zigux/validate-phase12.py: Documentation/zigux/phase12-virtio-net-survey.md",
        ),
        (
            "missing_validator_virtio_net_manifest_marker",
            "scripts/zigux/validate-phase12.py",
            "zigux/tests/phase12_virtio_net_manifest.json",
            "zigux/tests/phase12_virtio_net_manifest_missing.json",
            "scripts/zigux/validate-phase12.py: zigux/tests/phase12_virtio_net_manifest.json",
        ),
        (
            "missing_validator_raw_github_coverage_marker",
            "scripts/zigux/validate-phase12.py",
            RAW_GITHUB_COVERAGE_PATH,
            "Documentation/zigux/phase12-raw-github-coverage-survey-missing.md",
            f"scripts/zigux/validate-phase12.py: {RAW_GITHUB_COVERAGE_PATH}",
        ),
        (
            "missing_validator_virtio_scsi_fallback_marker",
            "scripts/zigux/validate-phase12.py",
            VIRTIO_SCSI_FALLBACK_PATH,
            "Documentation/zigux/phase12-virtio-scsi-fallback-missing.md",
            f"scripts/zigux/validate-phase12.py: {VIRTIO_SCSI_FALLBACK_PATH}",
        ),
        (
            "missing_validator_virtio_scsi_survey_note_marker",
            "scripts/zigux/validate-phase12.py",
            "Documentation/zigux/phase12-virtio-scsi-survey.md",
            "Documentation/zigux/phase12-virtio-scsi-survey-missing.md",
            "scripts/zigux/validate-phase12.py: Documentation/zigux/phase12-virtio-scsi-survey.md",
        ),
        (
            "missing_validator_virtio_scsi_manifest_marker",
            "scripts/zigux/validate-phase12.py",
            "zigux/tests/phase12_virtio_scsi_manifest.json",
            "zigux/tests/phase12_virtio_scsi_manifest_missing.json",
            "scripts/zigux/validate-phase12.py: zigux/tests/phase12_virtio_scsi_manifest.json",
        ),
        (
            "missing_validator_release_closure_checklist_marker",
            "scripts/zigux/validate-phase12.py",
            "Documentation/zigux/phase12-release-closure-checklist.md",
            "Documentation/zigux/phase12-release-closure-checklist-missing.md",
            "scripts/zigux/validate-phase12.py: Documentation/zigux/phase12-release-closure-checklist.md",
        ),
        (
            "missing_validator_nvme_survey_note_marker",
            "scripts/zigux/validate-phase12.py",
            "Documentation/zigux/phase12-nvme-pci-survey.md",
            "Documentation/zigux/phase12-nvme-pci-survey-missing.md",
            "scripts/zigux/validate-phase12.py: Documentation/zigux/phase12-nvme-pci-survey.md",
        ),
        (
            "missing_validator_release_readiness_checker_marker",
            "scripts/zigux/validate-phase12.py",
            "scripts/zigux/check-phase12-release-readiness-packet.py",
            "scripts/zigux/check-phase12-release-readiness-missing.py",
            "scripts/zigux/validate-phase12.py: scripts/zigux/check-phase12-release-readiness-packet.py",
        ),
        (
            "missing_validator_virtio_scsi_packet_checker_marker",
            "scripts/zigux/validate-phase12.py",
            "scripts/zigux/check-phase12-virtio-scsi-packet.py",
            "scripts/zigux/check-phase12-virtio-scsi-packet-missing.py",
            "scripts/zigux/validate-phase12.py: scripts/zigux/check-phase12-virtio-scsi-packet.py",
        ),
        (
            "missing_validator_expected_absent_count_marker",
            "scripts/zigux/validate-phase12.py",
            "PHASE12_EXPECTED_ABSENT_FILE_COUNT=0",
            "PHASE12_EXPECTED_ABSENT_FILE_COUNT=1",
            "scripts/zigux/validate-phase12.py: PHASE12_EXPECTED_ABSENT_FILE_COUNT=0",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase12_validator_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

        mutate_runtime_evidence_blob(tmp_root)
        expect_missing_marker(
            "missing_raw_github_runtime_evidence_blob",
            tmp_root,
            RUNTIME_EVIDENCE_ERROR,
        )
        write_fixture_root(tmp_root)

    case_count = len(missing_file_cases) + len(marker_cases) + 1
    print("PHASE12_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 shipped packet, the shared release-readiness "
            "fallback note, the bounded virtio_net starter-plus-transmit-recycle survey "
            "packet, the virtio_scsi survey packet, the raw-coverage companion, the "
            "release-closure companion, the dedicated support checkers, and the bounded "
            "NVMe starter, verifier shard, direct replay, survey packet, and manifest surfaces."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run validator self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, unexpected_files = validate(ROOT)
    if missing_files:
        print("PHASE12_VALIDATION=fail")
        print("MISSING_PHASE12_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE12_FILES_END")
        return 1

    if missing_markers:
        print("PHASE12_VALIDATION=fail")
        print("MISSING_PHASE12_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE12_MARKERS_END")
        return 1

    if unexpected_files:
        print("PHASE12_VALIDATION=fail")
        print("UNEXPECTED_PHASE12_FILES_START")
        for item in unexpected_files:
            print(item)
        print("UNEXPECTED_PHASE12_FILES_END")
        return 1

    print("PHASE12_VALIDATION=pass")
    print(f"PHASE12_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE12_EXPECTED_ABSENT_FILE_COUNT={len(EXPECTED_ABSENT_FILES)}")
    print(
        "PHASE12_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
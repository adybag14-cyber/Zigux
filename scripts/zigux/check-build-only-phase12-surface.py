#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase12-release-readiness-survey.md").exists() and (
            candidate / "zigux/Makefile"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
PHASE12_COMPLEX_DRIVER_LANE_PATH = (
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
)
RAW_GITHUB_COVERAGE_SURVEY_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE12_VIRTIO_NET_SURVEY_PATH = "Documentation/zigux/phase12-virtio-net-survey.md"
PHASE12_VIRTIO_NET_DRIVER_PATH = "drivers/net/virtio_net.zig"
PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH = (
    "drivers/net/virtio_net_transmit_recycle.zig"
)
PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH = (
    "drivers/net/virtio_net_queue_resume.zig"
)
PHASE12_VIRTIO_NET_TEST_PATH = "zigux/tests/phase12_virtio_net.zig"
PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig"
)
PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH = (
    "zigux/tests/phase12_virtio_net_queue_resume.zig"
)
PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH = "zigux/tests/phase12_virtio_net_syntax_lab.zig"
PHASE12_VIRTIO_NET_MANIFEST_PATH = "zigux/tests/phase12_virtio_net_manifest.json"
PHASE12_VIRTIO_NET_SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_net_survey.zig"
PHASE12_VIRTIO_SCSI_SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
PHASE12_VIRTIO_SCSI_SURVEY_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
PHASE12_VIRTIO_SCSI_DRIVER_PATH = "drivers/scsi/virtio_scsi.zig"
PHASE12_VIRTIO_SCSI_TEST_PATH = "zigux/tests/phase12_virtio_scsi.zig"
PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH = "zigux/tests/phase12_virtio_scsi_syntax_lab.zig"
PHASE12_VIRTIO_SCSI_REPLAN_PATH = "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig"
PHASE12_VIRTIO_SCSI_ROLLBACK_PATH = "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig"
PHASE12_VIRTIO_SCSI_PACKET_PATH = "zigux/tests/phase12_virtio_scsi_packet.zig"
PHASE12_VIRTIO_SCSI_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
PHASE12_VIRTIO_SCSI_SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
PHASE12_NVME_SLICE_PATH = "Documentation/zigux/phase12-nvme-pci-slice.md"
PHASE12_NVME_SURVEY_PATH = "Documentation/zigux/phase12-nvme-pci-survey.md"
PHASE12_NVME_REOPEN_GOVERNANCE_PATH = (
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md"
)
PHASE12_NVME_RAW_GAP_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
PHASE12_NVME_DRIVER_PATH = "drivers/nvme/host/pci.zig"
PHASE12_NVME_VERIFY_PATH = "drivers/nvme/host/pci_verify.zig"
PHASE12_NVME_TEST_PATH = "zigux/tests/phase12_nvme_pci.zig"
PHASE12_NVME_MANIFEST_PATH = "zigux/tests/phase12_nvme_pci_manifest.json"
PHASE12_NVME_SURVEY_GATE_PATH = "zigux/tests/phase12_nvme_pci_survey.zig"
PHASE12_LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH = (
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
)
SCRIPTS_README_PATH = "scripts/zigux/README.md"

REQUIRED_FILES = [
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    PHASE12_COMPLEX_DRIVER_LANE_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    SCRIPTS_README_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
    PHASE12_VIRTIO_NET_SURVEY_PATH,
    PHASE12_VIRTIO_NET_DRIVER_PATH,
    PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH,
    PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH,
    PHASE12_VIRTIO_NET_TEST_PATH,
    PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_TEST_PATH,
    PHASE12_VIRTIO_NET_QUEUE_RESUME_TEST_PATH,
    PHASE12_VIRTIO_NET_SYNTAX_LAB_PATH,
    PHASE12_VIRTIO_NET_MANIFEST_PATH,
    PHASE12_VIRTIO_NET_SURVEY_GATE_PATH,
    PHASE12_VIRTIO_SCSI_SLICE_PATH,
    PHASE12_VIRTIO_SCSI_SURVEY_PATH,
    PHASE12_VIRTIO_SCSI_DRIVER_PATH,
    PHASE12_VIRTIO_SCSI_TEST_PATH,
    PHASE12_VIRTIO_SCSI_SYNTAX_LAB_PATH,
    PHASE12_VIRTIO_SCSI_REPLAN_PATH,
    PHASE12_VIRTIO_SCSI_ROLLBACK_PATH,
    PHASE12_VIRTIO_SCSI_PACKET_PATH,
    PHASE12_VIRTIO_SCSI_MANIFEST_PATH,
    PHASE12_VIRTIO_SCSI_SURVEY_GATE_PATH,
    PHASE12_NVME_SLICE_PATH,
    PHASE12_NVME_SURVEY_PATH,
    PHASE12_NVME_REOPEN_GOVERNANCE_PATH,
    PHASE12_NVME_RAW_GAP_PATH,
    PHASE12_NVME_DRIVER_PATH,
    PHASE12_NVME_VERIFY_PATH,
    PHASE12_NVME_TEST_PATH,
    PHASE12_NVME_MANIFEST_PATH,
    PHASE12_NVME_SURVEY_GATE_PATH,
    PHASE12_LIBBPF_SNAPSHOT_PATH,
    PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH,
]

REQUIRED_MARKERS = {
    RELEASE_READINESS_SURVEY_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "current `zigux/Makefile` now provides shared `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again, but it still does not provide `phase12-validate`.",
        "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: `zigux/Makefile` still omits `phase12-validate` on current `master`, but it now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` wrappers again.",
        "the directly readable rerun surfaces in the shared packet are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.",
        "`zigux/tests/phase12_build.zig` also wires `zigux/tests/phase12_virtio_net_transmit_recycle.zig` and `zigux/tests/phase12_virtio_net_queue_resume.zig` through both `smoke` and `test`",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "`zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-smoke`, `phase12-test`, and `phase12` on `master` while still omitting `phase12-validate`",
        "Current `master` now ships the degraded-workflow evidence packet `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py`, while `make -C zigux phase12-validate` remains reminder-only vocabulary until the wrapper returns.",
        "build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "current `zigux/Makefile` now ships `phase12-smoke`, `phase12-test`, and `phase12` again, while `phase12-validate` is still absent, so only `make -C zigux phase12-validate` stays reminder vocabulary while `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are current wrapper proof on `master`.",
        "The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, while only `make -C zigux phase12-validate` stays documented as shared reminder text until that wrapper returns on current `master`.",
        "Keep the current partial direct-read bridge explicit too: `Documentation/zigux/phase12-raw-github-coverage-survey.md` now records that `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, and `zigux/Makefile` are directly readable on current `master`, while `zigux/tests/phase12_build.zig` still fails through the same bridge, and the readable Makefile now exposes `phase12-smoke`, `phase12-test`, and `phase12` even though `phase12-validate` is still missing, so that checker-plus-workflow-plus-scripts-plus-Makefile set stays split support evidence only rather than proof for the larger shared packet.",
        "keep those two `virtio_net` follow-ups framed as bounded transmit-disposition and queue-resume reviewability inside the shared packet rather than as live DMA-safe receive ownership, queue restart parity, transport-backed queue flow, or completion-path parity",
        "keep those `virtio_scsi` files framed as one directly readable bounded driver-local packet, but leave exact survey-packet lane-key and verified-on realignment to the packet-local survey follow-through in `P12-L09` rather than reopening broader shared PMO wording or driver-local code from this anti-overlap note alone",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
        "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence and still omits `phase12-validate`.",
    ],
    # Keep this checker scoped to stable PMO wording. Exact blob-pin refreshes in the
    # raw-coverage note belong to the adjacent fallback lane.
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "- exact coverage evidence checked on `2026-05-19`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py`",
        "`scripts/zigux/check-phase12-release-readiness-packet.py`",
        "`.github/workflows/zigux-bootstrap.yml`",
        "`scripts/zigux/README.md`",
        "`zigux/Makefile`",
        "while a direct contents read for `zigux/tests/phase12_build.zig` still returns `404` through the same current `master` bridge",
        "keep the directly readable build-only checker, release-readiness checker, workflow, scripts-root README, and current Makefile as bounded reminder evidence only",
        "the raw-URL-backed fallback pair and the contents-bridge-backed shared support bundle are distinct evidence paths in this runtime",
        "now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` again while still omitting `phase12-validate`",
        "keep the same reminder-only validator route plus shipped wrapper reruns explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate` stays reminder-only vocabulary until the wrapper returns on current `master`",
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
        "keep the repo-local `.zig-toolchain` then attached-Zig degraded rerun order explicit here too: rely on the Makefile fallback first, then name `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` only as last-resort rerun vocabulary while `make -C zigux phase12-validate` remains reminder-only text",
    ],
    VALIDATOR_PATH: [
        "BUILD_ONLY_CHECKER_PATH",
        "RELEASE_READINESS_CHECKER_PATH",
        "stale reminder vocabulary",
    ],
    MAKEFILE_PATH: [
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
    PHASE12_BUILD_PATH: [
        '"phase12_virtio_net_transmit_recycle.zig"',
        '"phase12_virtio_net_queue_resume.zig"',
        "smoke_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "smoke_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
        "test_step.dependOn(&run_virtio_net_transmit_recycle_tests.step);",
        "test_step.dependOn(&run_virtio_net_queue_resume_tests.step);",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 build-only surface checker",
        "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Check current Phase 12 build-only surface",
        "        run: python3 scripts/zigux/check-build-only-phase12-surface.py",
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


def has_required_marker(rel_path: str, text: str, marker: str) -> bool:
    if rel_path in EXACT_LINE_MARKER_PATHS:
        return marker in text.splitlines()
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
            RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
            RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            PHASE12_COMPLEX_DRIVER_LANE_PATH: "# Phase 12 Complex-Driver Lane Sequencing",
            RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            SCRIPTS_README_PATH: "# scripts/zigux",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path in {
            VALIDATOR_PATH,
            MAKEFILE_PATH,
            WORKFLOW_PATH,
        }:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".json"):
        return "{}\n"
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
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = [
            RELEASE_READINESS_SURVEY_PATH,
            RELEASE_COORDINATION_MATRIX_PATH,
            PHASE12_COMPLEX_DRIVER_LANE_PATH,
            RAW_GITHUB_COVERAGE_SURVEY_PATH,
            SCRIPTS_README_PATH,
            RELEASE_READINESS_CHECKER_PATH,
            VALIDATOR_PATH,
            MAKEFILE_PATH,
            PHASE12_BUILD_PATH,
            WORKFLOW_PATH,
            PHASE12_VIRTIO_NET_TRANSMIT_RECYCLE_DRIVER_PATH,
            PHASE12_VIRTIO_NET_QUEUE_RESUME_DRIVER_PATH,
            PHASE12_VIRTIO_SCSI_MANIFEST_PATH,
            PHASE12_NVME_VERIFY_PATH,
            PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH,
        ]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][0]),
            (RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][1]),
            (RELEASE_READINESS_SURVEY_PATH, REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH][2]),
            (RELEASE_SEQUENCING_PATH, REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH][0]),
            (RELEASE_SEQUENCING_PATH, REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH][1]),
            (RELEASE_SEQUENCING_PATH, REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH][2]),
            (RELEASE_COORDINATION_MATRIX_PATH, REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH][0]),
            (RELEASE_COORDINATION_MATRIX_PATH, REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH][1]),
            (RELEASE_COORDINATION_MATRIX_PATH, REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH][2]),
            (PHASE12_COMPLEX_DRIVER_LANE_PATH, REQUIRED_MARKERS[PHASE12_COMPLEX_DRIVER_LANE_PATH][0]),
            (PHASE12_COMPLEX_DRIVER_LANE_PATH, REQUIRED_MARKERS[PHASE12_COMPLEX_DRIVER_LANE_PATH][1]),
            (PHASE12_COMPLEX_DRIVER_LANE_PATH, REQUIRED_MARKERS[PHASE12_COMPLEX_DRIVER_LANE_PATH][2]),
            (PHASE12_COMPLEX_DRIVER_LANE_PATH, REQUIRED_MARKERS[PHASE12_COMPLEX_DRIVER_LANE_PATH][3]),
            (PHASE12_COMPLEX_DRIVER_LANE_PATH, REQUIRED_MARKERS[PHASE12_COMPLEX_DRIVER_LANE_PATH][4]),
            (RELEASE_CLOSURE_CHECKLIST_PATH, REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH][0]),
            (RELEASE_CLOSURE_CHECKLIST_PATH, REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH][1]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][0]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][1]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][2]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][3]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][4]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][5]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][6]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][7]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][8]),
            (RAW_GITHUB_COVERAGE_SURVEY_PATH, REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_SURVEY_PATH][9]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][0]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][1]),
            (SCRIPTS_README_PATH, REQUIRED_MARKERS[SCRIPTS_README_PATH][2]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][0]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][1]),
            (VALIDATOR_PATH, REQUIRED_MARKERS[VALIDATOR_PATH][2]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][0]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][1]),
            (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][2]),
            (PHASE12_BUILD_PATH, REQUIRED_MARKERS[PHASE12_BUILD_PATH][0]),
            (PHASE12_BUILD_PATH, REQUIRED_MARKERS[PHASE12_BUILD_PATH][1]),
            (PHASE12_BUILD_PATH, REQUIRED_MARKERS[PHASE12_BUILD_PATH][2]),
            (PHASE12_BUILD_PATH, REQUIRED_MARKERS[PHASE12_BUILD_PATH][3]),
            (PHASE12_BUILD_PATH, REQUIRED_MARKERS[PHASE12_BUILD_PATH][4]),
            (PHASE12_BUILD_PATH, REQUIRED_MARKERS[PHASE12_BUILD_PATH][5]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][0]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][1]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][2]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][3]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][4]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][5]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][6]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][7]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][8]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][9]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][10]),
            (WORKFLOW_PATH, REQUIRED_MARKERS[WORKFLOW_PATH][11]),
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        forbidden_cases = [
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][0]),
            (MAKEFILE_PATH, FORBIDDEN_MARKERS[MAKEFILE_PATH][1]),
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + f"{marker}\n",
            )
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = len(missing_file_cases) + len(marker_cases) + len(forbidden_cases)
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print(f"PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 12 build-only contract around the "
            "returned smoke-and-test wrappers, the still-missing validate wrapper, and "
            "the shipped driver-local packet companions."
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
    print(f"PHASE12_BUILD_ONLY_REQUIRED_MARKER_COUNT={sum(len(m) for m in REQUIRED_MARKERS.values())}")
    print(f"PHASE12_BUILD_ONLY_FORBIDDEN_MARKER_COUNT={sum(len(m) for m in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
VIRTIO_NET_FALLBACK_PATH = (
    "Documentation/zigux/phase12-virtio-net-raw-github-fallback-map.md"
)
VIRTIO_SCSI_FALLBACK_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
NVME_FALLBACK_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
BUILD_INVENTORY_CHECKER_PATH = "scripts/zigux/check-phase12-build-inventory.py"
VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-net-manifest-presence.py"
)
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
COMPLEX_DRIVER_CHECKER_PATH = (
    "scripts/zigux/check-phase12-complex-driver-lane-packet.py"
)
NVME_PACKET_COHERENCE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-nvme-packet-coherence.py"
)
CROSS_COMPILE_CHECKER_PATH = "scripts/zigux/check-phase12-cross-compile-smoke.py"
VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-scsi-rollback-coverage.py"
)
VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py"
)
LIBBPF_SNAPSHOT_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-snapshot.py"
LIBBPF_LANE_MARKER_CHECKER_PATH = (
    "scripts/zigux/check-phase12-libbpf-lane-marker.py"
)
LIBBPF_HEAVY_CONSUMER_CHECKER_PATH = (
    "scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py"
)
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

CHECKER_PATHS = (
    BUILD_ONLY_CHECKER_PATH,
    BUILD_INVENTORY_CHECKER_PATH,
    VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    COMPLEX_DRIVER_CHECKER_PATH,
    NVME_PACKET_COHERENCE_CHECKER_PATH,
    CROSS_COMPILE_CHECKER_PATH,
    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH,
    VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    LIBBPF_HEAVY_CONSUMER_CHECKER_PATH,
)

REQUIRED_FILES = (
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_PATH,
    VIRTIO_NET_FALLBACK_PATH,
    VIRTIO_SCSI_FALLBACK_PATH,
    NVME_FALLBACK_PATH,
    SCRIPTS_README_PATH,
    *CHECKER_PATHS,
    VALIDATOR_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
)

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while the directly readable scripts-side support packet stays explicit as shared reminder evidence rather than as broader driver-delivery proof",
        "keep `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the smoke-first and rollback-lab `virtio_scsi` packet",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
        "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
        "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
        "The dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route is now part of that rollback-only lab packet too",
        "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "The fallback split stays truthful: one commit-pinned `virtio_scsi` replay catalog, one current-master `nvme_pci` gap-inventory companion, and two shared-tree anchors.",
        "If `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
        "shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
        "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12-test ZIG=<attached-zig-path>`",
        "attached-Zig rerun vocabulary for the same shipped route: `make -C zigux phase12 ZIG=<attached-zig-path>`",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and the shipped wrapper name `make -C zigux phase12-validate`",
        "Keep the rollback-evidence-only `virtio_scsi` packet explicit through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py` while keeping that storage-facing rollback-evidence packet and its dedicated survey-build rerun outside the shared `smoke` and `test` build route.",
        "Keep the bounded NVMe foothold explicit through `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` while leaving it outside the shared smoke-and-test route.",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "- driver-local current-master fallback maps:",
        "- `Documentation/zigux/phase12-virtio-net-raw-github-fallback-map.md`",
        "- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
        "- `scripts/zigux/check-phase12-build-inventory.py`",
        "- exact runtime-reality evidence checked on `2026-05-27`: direct container-side `curl`, `wget`, `urllib`, and `git clone https://github.com/adybag14-cyber/Zigux.git` still fail in this runtime through the proxy tunnel with HTTP `403`",
        "- exact runtime-reality evidence checked on `2026-05-27`: the directly readable `zigux/Makefile` blob `09f92bc2f9903fc4fd58d6335e93da13e7f0793b` still prefers the repo-local `.zig-toolchain` executable",
    ],
    VIRTIO_NET_FALLBACK_PATH: [
        "- support checker bundle: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-build-inventory.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig`",
        "- current shared route shape: `zigux/tests/phase12_build.zig` wires the queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate sextet through shared `smoke` and shared `test`, while current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, `make -C zigux phase12-virtio-net-syntax-lab-test`, and `make -C zigux phase12-virtio-net-throughput-parity-test`",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "- exact current shared support-bundle and replay order is `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
        "- `make -C zigux phase12-validate` is current repo evidence again and now reruns the shared build-only, complex-driver, cross-compile smoke, release-readiness, libbpf snapshot, libbpf heavy-consumer, and `virtio_net` packet checkers plus `scripts/zigux/validate-phase12.py`",
    ],
    NVME_FALLBACK_PATH: [
        "Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local gap note too:",
        "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
        "3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
        "5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
        "6. shipped wrapper evidence on current `master`: `make -C zigux phase12`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, and `scripts/zigux/check-phase12-cross-compile-smoke.py` keep the directly readable complex-driver support packet explicit from the scripts root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep that returned wrapper set explicit as shipped evidence on current `master`.",
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    ],
    TESTS_README_PATH: [
        "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.",
        "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.",
        "Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-build-only-phase12-surface.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-build-inventory.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-release-readiness-packet.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-complex-driver-lane-packet.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-cross-compile-smoke.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-virtio-scsi-libbpf-boundary.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-libbpf-snapshot.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-libbpf-lane-marker.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase12-libbpf-heavy-consumer-packet.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase12.py",
        "phase12-smoke:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
        "phase12-test:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
        "phase12-virtio-net-syntax-lab-test:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all",
        "phase12-virtio-net-throughput-parity-test:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    PHASE12_BUILD_PATH: [
        "\"phase12_virtio_net_queue_resume.zig\"",
        "\"phase12_virtio_net_receive_refill_replay.zig\"",
        "\"phase12_virtio_net_transmit_recycle.zig\"",
        "\"phase12_virtio_net_post_reset_replay.zig\"",
        "\"phase12_virtio_net_throughput_parity.zig\"",
        "\"phase12_virtio_net_survey.zig\"",
        "\"phase12-virtio-net-throughput-parity\"",
    ],
    WORKFLOW_PATH: [
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "run: python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "run: python3 scripts/zigux/validate-phase12.py",
        "run: make -C zigux phase12-smoke",
        "run: make -C zigux phase12-test",
        "run: make -C zigux phase12",
    ],
    VALIDATOR_PATH: [
        BUILD_INVENTORY_CHECKER_PATH,
        VIRTIO_NET_MANIFEST_PRESENCE_CHECKER_PATH,
        NVME_PACKET_COHERENCE_CHECKER_PATH,
        VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH,
        VIRTIO_SCSI_LIBBPF_BOUNDARY_CHECKER_PATH,
        VIRTIO_NET_FALLBACK_PATH,
        "Validate the current Phase 12 shared PMO packet, fallback packet, current-master virtio_net fallback companion, scripts-root reminder, tests-root reminder, driver-local NVMe boundary packet, and returned wrapper contract.",
    ],
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: [
        "phase12: phase12-smoke phase12-test",
    ],
}

EXACT_LINE_MARKER_PATHS = {
    WORKFLOW_PATH,
}


def validate_markers(root: Path) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    drift: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")

    if missing:
        return missing, drift

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        normalized_lines = {line.strip() for line in text.splitlines()}
        for marker in markers:
            marker_present = (
                marker.strip() in normalized_lines
                if rel_path in EXACT_LINE_MARKER_PATHS
                else marker in text
            )
            if not marker_present:
                drift.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                drift.append(f"forbidden_marker:{rel_path}:{marker}")

    return missing, drift


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
    combined = [
        line.strip()
        for line in f"{result.stdout}\n{result.stderr}".splitlines()
        if line.strip()
    ]
    failures.extend(f"phase12_checker_output:{line}" for line in combined)
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    body = "\n".join(f"- {marker}" for marker in markers)
    return f"{title}\n\n{body}\n"


FIXTURE_TITLES = {
    DOCS_README_PATH: "# Zigux Documentation",
    REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
    RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
    RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
    RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
    RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
    RAW_GITHUB_COVERAGE_PATH: "# Phase 12 Raw GitHub Coverage Survey",
    VIRTIO_NET_FALLBACK_PATH: "# Phase 12 Virtio Net Raw GitHub Fallback Map",
    VIRTIO_SCSI_FALLBACK_PATH: "# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog",
    NVME_FALLBACK_PATH: "# Phase 12 NVMe PCI Raw GitHub Fallback Map",
    SCRIPTS_README_PATH: "# scripts/zigux",
    TESTS_README_PATH: "# zigux/tests",
}


def fixture_text(rel_path: str) -> str:
    if rel_path in CHECKER_PATHS:
        return (
            "#!/usr/bin/env python3\n"
            "from __future__ import annotations\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(0)\n"
        )

    if rel_path == MAKEFILE_PATH:
        return "\n".join(REQUIRED_MARKERS[MAKEFILE_PATH]) + "\n"

    if rel_path == WORKFLOW_PATH:
        return "name: zigux-bootstrap\n" + "\n".join(REQUIRED_MARKERS[WORKFLOW_PATH]) + "\n"

    if rel_path == PHASE12_BUILD_PATH:
        return "\n".join(
            [
                "// phase12 build fixture",
                *REQUIRED_MARKERS[PHASE12_BUILD_PATH],
            ]
        ) + "\n"

    if rel_path == VALIDATOR_PATH:
        return "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "",
                *REQUIRED_MARKERS[VALIDATOR_PATH],
                "",
            ]
        )

    if rel_path in FIXTURE_TITLES:
        return marker_fixture(FIXTURE_TITLES[rel_path], REQUIRED_MARKERS[rel_path])

    raise ValueError(f"no fixture text for {rel_path}")


def write_fixture_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    missing, drift = validate_markers(root)
    failures = missing + drift
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    if updated == text:
        raise SystemExit(f"marker not removable: {marker}")
    path.write_text(updated, encoding="utf-8")


def add_forbidden_marker(path: Path, marker: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + f"{marker}\n", encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-validator-"))
    try:
        write_fixture_root(base)
        missing, drift = validate_markers(base)
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

        forbidden_cases = [
            (rel_path, marker)
            for rel_path, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_root(base)
            add_forbidden_marker(base / rel_path, marker)
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = len(missing_file_cases) + len(marker_cases) + len(forbidden_cases)
        print("PHASE12_VALIDATOR_SELF_TEST=pass")
        print(f"PHASE12_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 shared PMO packet, fallback packet, "
            "current-master virtio_net fallback companion, scripts-root reminder, "
            "tests-root reminder, driver-local NVMe boundary packet, and returned wrapper contract."
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

    missing, drift = validate_markers(args.root)
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
    for checker_path in CHECKER_PATHS:
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
    print(f"PHASE12_REQUIRED_MARKER_COUNT={sum(len(v) for v in REQUIRED_MARKERS.values())}")
    print(f"PHASE12_FORBIDDEN_MARKER_COUNT={sum(len(v) for v in FORBIDDEN_MARKERS.values())}")
    print(f"PHASE12_CHECKER_COUNT={len(CHECKER_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

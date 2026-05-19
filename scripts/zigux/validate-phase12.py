#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
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
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

# Keep the shared Phase 12 validator scoped to stable support-surface wording.
# Exact blob pins in the raw-coverage note belong to the neighboring fallback lane.
RAW_GITHUB_BRIDGE_MARKERS = [
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`scripts/zigux/README.md`",
    "`zigux/Makefile`",
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
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    RELEASE_READINESS_SURVEY_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "current `zigux/Makefile` now provides shared `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again, but it still does not provide `phase12-validate`.",
        "the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`",
        "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
        "`scripts/zigux/check-build-only-phase12-surface.py` remains the bounded build-only contract checker",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: `zigux/Makefile` still omits `phase12-validate` on current `master`, but it now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` wrappers again.",
        "the directly readable rerun surfaces in the shared packet are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.",
        "while `make -C zigux phase12-validate` remains stale reminder vocabulary until same-lane work rematerializes the wrapper",
        "`Documentation/zigux/phase12-nvme-pci-reopen-governance.md` owner-map companion outside the wired shared release route",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
        "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
        "attached-Zig rerun vocabulary only until the wrapper returns: `make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "attached-Zig rerun vocabulary only until the wrapper returns: `make -C zigux phase12 ZIG=<attached-zig-path>`",
        "Do not invent a focused libbpf-only replay, a cross-build replay, or another unshipped closure route while using the degraded path.",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "`zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-smoke`, `phase12-test`, and `phase12` on `master` while still omitting `phase12-validate`",
        "the shipped packet-local `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py` guard",
        "Current `master` now ships the degraded-workflow evidence packet `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py`, while `make -C zigux phase12-validate` remains reminder-only vocabulary until the wrapper returns.",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "- exact coverage evidence checked on `2026-05-19`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py`",
        *RAW_GITHUB_BRIDGE_MARKERS,
        "while a direct contents read for `zigux/tests/phase12_build.zig` still returns `404` through the same current `master` bridge",
        "keep the directly readable build-only checker, release-readiness checker, workflow, scripts-root README, and current Makefile as bounded reminder evidence only",
        "the raw-URL-backed fallback pair and the contents-bridge-backed shared support bundle are distinct evidence paths in this runtime",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-smoke`, `phase12-test`, and `phase12` again, while `phase12-validate` is still absent, so only `make -C zigux phase12-validate` stays reminder vocabulary while `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are current wrapper proof on `master`.",
        "The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, while only `make -C zigux phase12-validate` stays documented as shared reminder text until that wrapper returns on current `master`.",
        "keep those two `virtio_net` follow-ups framed as bounded transmit-disposition and queue-resume reviewability inside the shared packet rather than as live DMA-safe receive ownership, queue restart parity, transport-backed queue flow, or completion-path parity",
    ],
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: [
        "Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, while treating the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as parked note-owned boundaries until they land again on current `master`, while keeping `tools/lib/bpf/zigux_segments/verify.zig` explicit as the directly readable compile-together shard for the current helper footing, and while keeping `tools/lib/bpf/zigux_segments/manifest.json` explicit as the directly readable legacy helper catalog on current `master`.",
        "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-smoke`, `phase12-test`, and `phase12` on current `master` while still omitting `phase12-validate`, so keep only `make -C zigux phase12-validate` here as reminder vocabulary and keep the directly readable support bundle explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `scripts/zigux/validate-phase12.py` beside the returned smoke-and-test wrappers.",
        "The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.",
    ],
    VIRTIO_NET_SURVEY_PATH: [
        "`PHASE12_STATUS=starter-present-post-reset-replay-followup`",
        "lane owner: `P12-L02`",
        "current `master` now also carries `drivers/net/virtio_net_post_reset_replay.zig`",
        "the shared Phase 12 smoke and test routes keep the dedicated `virtio_net` syntax-lab shard plus the queue-resume and transmit-recycle replays reachable beside the direct starter packet",
        "while the post-reset replay still remains a dedicated driver-local test outside the shared Phase 12 build route",
        "the packet still does not claim live DMA-safe receive ownership, page-pool wiring, refill execution, transport-backed submit flow, interrupt-backed completion handling, or full `net_device` lifecycle parity",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`",
        "- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`",
        "- survey replay: `zigux/tests/phase12_virtio_scsi_survey.zig`",
        "- `scripts/zigux/validate-phase12.py`",
        "- reminder-only validator wrapper vocabulary until it returns: `make -C zigux phase12-validate`",
        "current authoritative packet truth now lives in the shared-tree survey companions and validator surfaces reread for this lane",
    ],
    VIRTIO_SCSI_SURVEY_PATH: [
        "PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey",
        "PHASE12_LANE=P12-L13",
        "fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
        "still does not claim live DMA-safe request submission",
        "control-path governance",
        "frozen control-path restore-order surface inside `recoveryControlPathGovernanceSummary()`",
    ],
    VIRTIO_NET_PACKET_CHECKER_PATH: [
        "PHASE12_VIRTIO_NET_PACKET_SELF_TEST=pass",
        "Documentation/zigux/phase12-virtio-net-survey.md",
        "zigux/tests/phase12_virtio_net_manifest.json",
        "zigux/tests/phase12_build.zig",
        "phase12_virtio_net_post_reset_replay.zig",
        "phase12-virtio-net-post-reset-replay-tests",
    ],
    VIRTIO_NET_MANIFEST_PATH: [
        '"lane_key": "P12-L02"',
        '"phase": "Phase 12"',
        '"anchor": "drivers/net/virtio_net.c"',
        '"id": "phase12-build-gate"',
        '"id": "phase12-virtio-net-post-reset-replay-followup"',
        '"id": "phase12-virtio-net-runtime-data-path"',
        '"status": "blocked_on_dma_transport_runtime"',
    ],
    VIRTIO_SCSI_MANIFEST_PATH: [
        "\"lane_key\": \"P12-L13\"",
        "\"phase\": \"Phase 12\"",
        "\"anchor\": \"drivers/scsi/virtio_scsi.c\"",
        "\"roadmap_gap_check\"",
        "\"phase12-virtio-scsi-runtime-request-flow\"",
    ],
    VIRTIO_SCSI_SURVEY_GATE_PATH: [
        "test \"phase12 virtio scsi survey manifest keeps the bounded queue-and-recovery packet truthful\"",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        "scripts/zigux/check-phase12-virtio-scsi-packet.py",
    ],
    NVME_FALLBACK_PATH: [
        "`PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`",
        "- starter shard: `drivers/nvme/host/pci.zig`",
        "- verifier shard: `drivers/nvme/host/pci_verify.zig`",
        "- direct replay: `zigux/tests/phase12_nvme_pci.zig`",
        "- survey gate: `zigux/tests/phase12_nvme_pci_survey.zig`",
        "- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`",
        "- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes",
    ],
    MAKEFILE_PATH: [
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
        "phase3: phase3-validate",
        "phase10: phase10-validate phase10-test",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH: [
        "PHASE12_VIRTIO_SCSI_ROLLBACK_COVERAGE_SELF_TEST=pass",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "zigux/tests/phase12_virtio_scsi_survey.zig",
        "zigux/tests/phase12_build.zig",
    ],
    VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH: [
        "PHASE12_VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_SELF_TEST=pass",
        "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "zigux/tests/phase12_virtio_scsi_manifest.json",
        "zigux/tests/phase12_build.zig",
        "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    ],
    VALIDATOR_PATH: [
        VIRTIO_NET_PACKET_CHECKER_PATH,
        VIRTIO_SCSI_PACKET_CHECKER_PATH,
        VIRTIO_SCSI_BOUNDARY_CHECKER_PATH,
        VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH,
        VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH,
        NVME_PACKET_CHECKER_PATH,
        VIRTIO_NET_MANIFEST_PATH,
        VIRTIO_SCSI_MANIFEST_PATH,
        VIRTIO_SCSI_SURVEY_GATE_PATH,
        "PHASE12_VALIDATOR_SELF_TEST=pass",
        "make -C zigux phase12-validate",
        "stale reminder vocabulary",
        "scripts-side support packet",
    ],
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "the shipped `make -C zigux phase12-validate` route keeps",
        "must not treat the shipped `make -C zigux phase12-validate` route",
    ],
    VALIDATOR_PATH: [
        "RUNTIME_EVIDENCE_PATHS = [",
        "RUNTIME_EVIDENCE_ERROR = (",
        "RUNTIME_EVIDENCE_SUFFIX = (",
        "git_blob_sha(",
    ],
}


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")
    if missing:
        return missing, []

    drift: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                drift.append(f"missing_marker:{rel_path}:{marker}")
    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                drift.append(f"forbidden_marker:{rel_path}:{marker}")
    return [], drift


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    body = "\n".join(f"- {marker}" for marker in markers)
    return f"{title}\n\n{body}\n"


FIXTURE_TEXT = {
    DOCS_README_PATH: "# Zigux Documentation\n",
    REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist\n",
    FREEZE_MAP_PATH: "# Zigux Freeze Map\n",
    RELEASE_READINESS_SURVEY_PATH: marker_fixture(
        "# Phase 12 Release Readiness Survey",
        REQUIRED_MARKERS[RELEASE_READINESS_SURVEY_PATH],
    ),
    RELEASE_SEQUENCING_PATH: marker_fixture(
        "# Phase 12 Release Sequencing",
        REQUIRED_MARKERS[RELEASE_SEQUENCING_PATH],
    ),
    RELEASE_CLOSURE_CHECKLIST_PATH: marker_fixture(
        "# Phase 12 Release Closure Checklist",
        REQUIRED_MARKERS[RELEASE_CLOSURE_CHECKLIST_PATH],
    ),
    RELEASE_COORDINATION_MATRIX_PATH: marker_fixture(
        "# Phase 12 Release Coordination Matrix",
        REQUIRED_MARKERS[RELEASE_COORDINATION_MATRIX_PATH],
    ),
    RAW_GITHUB_COVERAGE_PATH: marker_fixture(
        "# Phase 12 Raw GitHub Coverage Survey",
        REQUIRED_MARKERS[RAW_GITHUB_COVERAGE_PATH],
    ),
    PHASE12_COMPLEX_DRIVER_LANE_PATH: marker_fixture(
        "# Phase 12 Complex-Driver Lane Sequencing",
        REQUIRED_MARKERS[PHASE12_COMPLEX_DRIVER_LANE_PATH],
    ),
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: marker_fixture(
        "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
        REQUIRED_MARKERS[PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH],
    ),
    VIRTIO_NET_SURVEY_PATH: marker_fixture(
        "# Phase 12 Virtio Net Survey",
        REQUIRED_MARKERS[VIRTIO_NET_SURVEY_PATH],
    ),
    VIRTIO_SCSI_FALLBACK_PATH: marker_fixture(
        "# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog",
        REQUIRED_MARKERS[VIRTIO_SCSI_FALLBACK_PATH],
    ),
    VIRTIO_SCSI_SLICE_PATH: "# Phase 12 virtio_scsi Slice\n",
    VIRTIO_SCSI_SURVEY_PATH: marker_fixture(
        "# Phase 12 Virtio SCSI Survey",
        REQUIRED_MARKERS[VIRTIO_SCSI_SURVEY_PATH],
    ),
    NVME_FALLBACK_PATH: marker_fixture(
        "# Phase 12 NVMe PCI Raw GitHub Fallback Map",
        REQUIRED_MARKERS[NVME_FALLBACK_PATH],
    ),
    NVME_REOPEN_GOVERNANCE_PATH: "# Phase 12 NVMe PCI Reopen Governance\n",
    NVME_SLICE_PATH: "# Phase 12 NVMe PCI Slice\n",
    NVME_SURVEY_PATH: "# Phase 12 NVMe PCI Survey\n",
    SCRIPTS_README_PATH: "# scripts/zigux\n",
    BUILD_ONLY_CHECKER_PATH: "#!/usr/bin/env python3\n",
    RELEASE_READINESS_CHECKER_PATH: "#!/usr/bin/env python3\n",
    VIRTIO_NET_PACKET_CHECKER_PATH: "\n".join(
        REQUIRED_MARKERS[VIRTIO_NET_PACKET_CHECKER_PATH]
    )
    + "\n",
    VIRTIO_SCSI_PACKET_CHECKER_PATH: "#!/usr/bin/env python3\n",
    VIRTIO_SCSI_BOUNDARY_CHECKER_PATH: "#!/usr/bin/env python3\n",
    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH: "\n".join(
        REQUIRED_MARKERS[VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH]
    )
    + "\n",
    VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH: "\n".join(
        REQUIRED_MARKERS[VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH]
    )
    + "\n",
    NVME_PACKET_CHECKER_PATH: "#!/usr/bin/env python3\n",
    VALIDATOR_PATH: "\n".join(REQUIRED_MARKERS[VALIDATOR_PATH]) + "\n",
    TESTS_README_PATH: "# zigux/tests\n",
    MAKEFILE_PATH: "\n".join(REQUIRED_MARKERS[MAKEFILE_PATH]) + "\n",
    PHASE12_BUILD_PATH: "// phase12 build fixture\n",
    VIRTIO_NET_MANIFEST_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_NET_MANIFEST_PATH]) + "\n",
    VIRTIO_SCSI_MANIFEST_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_SCSI_MANIFEST_PATH]) + "\n",
    VIRTIO_SCSI_SURVEY_GATE_PATH: "\n".join(REQUIRED_MARKERS[VIRTIO_SCSI_SURVEY_GATE_PATH]) + "\n",
    VIRTIO_SCSI_SUPPORT_MANIFEST_PATH: (
        "{\n"
        '  "lane_key": "P12-L13",\n'
        '  "source_manifest": "zigux/tests/phase12_virtio_scsi_manifest.json"\n'
        "}\n"
    ),
    LIBBPF_SNAPSHOT_PATH: '{\n  "lane_key": "P12-L16"\n}\n',
    WORKFLOW_PATH: "name: zigux-bootstrap\n",
}


def write_fixture_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, FIXTURE_TEXT.get(rel_path, "// fixture\n"))


def expect_failure(root: Path, expected: str) -> None:
    missing, drift = validate(root)
    failures = missing + drift
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "")
    updated = updated.replace(marker, "")
    if updated == text:
        raise SystemExit(f"marker not removable: {marker}")
    path.write_text(updated, encoding="utf-8")


def add_forbidden_marker(path: Path, marker: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + f"{marker}\n", encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-validator-"))
    try:
        write_fixture_root(base)
        missing, drift = validate(base)
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
            "Validate the current Phase 12 shared support bundle around the release "
            "packet, fallback packet, shared anti-overlap companions, driver-local "
            "surveys, and current master route reality."
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

    missing, drift = validate(args.root)
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

    print("PHASE12_VALIDATION=pass")
    print(f"PHASE12_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE12_REQUIRED_MARKER_COUNT=" f"{sum(len(v) for v in REQUIRED_MARKERS.values())}")
    print("PHASE12_FORBIDDEN_MARKER_COUNT=" f"{sum(len(v) for v in FORBIDDEN_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=release_readiness_packet

Fail-closed checker for the bounded Phase 12 release-readiness note and shipped validation route.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE12_CHECK_PACKET=release_readiness_packet"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
ROADMAP_PATH = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE12_SECTION_HEADING = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers"

ROADMAP_ANCHORS = [
    "`drivers/net/virtio_net.c`",
    "`drivers/nvme/host/pci.c`",
    "`drivers/scsi/virtio_scsi.c`",
    "`tools/lib/bpf/libbpf.c`",
]

RELEASE_READINESS_MARKERS = [
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
    "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`zigux/tests/phase12_build.zig` wires `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` into the active `smoke` and `test` steps",
    "The shared release packet now also carries the bounded `virtio_net_transmit_recycle` follow-up through `drivers/net/virtio_net_transmit_recycle.zig` and `zigux/tests/phase12_virtio_net_transmit_recycle.zig`: current `zigux/tests/phase12_build.zig` runs that replay in both `smoke` and `test`, but the release reading must keep it framed as transmit-disposition reviewability rather than as live interrupt-backed completion, refill execution, or DMA parity.",
    "The broader shared-summary packet is now aligned on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` already keep the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard plus the shipped `make -C zigux phase12-validate` route explicit, `zigux/tests/README.md` does the same in its Phase 12 inventory, and `scripts/zigux/README.md` now carries a dedicated Phase 12 flow block naming `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and the shipped validator-first then smoke-first routes.",
    "`scripts/zigux/check-build-only-phase12-surface.py` now matches that shipped support-checker-plus-validate-route reminder too, so `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and this readiness note can stay parked together until another shared reminder surface actually drifts, rather than reopening driver-local, fallback-catalog, or verify-shard wording first.",
    "The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a focused libbpf-only replay or a cross-build replay, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.",
    "Keep the same degraded-workflow validation trio explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.",
    "Current `master` keeps the release-order, readiness, coordination, closure, workflow, Makefile, docs-root, review-checklist, scripts-root, and tests-root companions aligned around the starter-present `virtio_net` plus smoke-first `virtio_scsi` packet, including the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor and the shipped `phase12-validate` support bundle. Leave this same-lane packet parked unless one of those shared reminder surfaces drifts again; if it reopens, refresh only the smallest reminder that moved before widening into any new driver claims.",
]

REVIEW_CHECKLIST_MARKERS = [
    "avoid implying a broader shared `check-phase12-*.py` family, focused-libbpf-only replay, or cross-build replay, while keeping the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` checker plus the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route",
    "if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes, do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?",
]

FREEZE_MAP_MARKERS = [
    "the shared Phase 12 PMO release packet also stays release-planning-only beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`",
    "queueing, throughput, rollback, and recovery wording there, in the shipped validator-first `make -C zigux phase12-validate` support bundle, and in the smoke-first shared replay packet must stay bounded to driver-local review evidence, lab-only reversible-delivery scaffolding, and shared anti-overlap notes without implying active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`",
]

SCRIPTS_README_MARKERS = [
    "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned across `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `zigux/tests/phase12_build.zig`, the starter-present `virtio_net` packet, the shipped `virtio_scsi` packet, and the bounded NVMe starter-plus-verifier-plus-direct-test-plus-manifest packet before the shared validator-first then smoke-first routes run.",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` keep the degraded-workflow support bundle explicit in this scripts-root summary so the shipped validator-first route stays visible as support-bundle evidence rather than as a second direct replay route.",
]

MAKEFILE_MARKERS = [
    "phase12-validate:",
    "scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "scripts/zigux/validate-phase12.py",
    "phase12: phase12-validate phase12-smoke phase12-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 12 degraded-workflow bundle",
    "run: make -C zigux phase12-validate",
    "Run focused Phase 12 smoke shard",
    "Run Phase 12 complex driver tests",
]


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def extract_phase12_anchor_bullets(text: str) -> list[str]:
    lines = text.splitlines()
    in_phase12 = False
    in_anchor_list = False
    anchors: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == PHASE12_SECTION_HEADING:
            in_phase12 = True
            continue
        if in_phase12 and stripped.startswith("## "):
            break
        if not in_phase12:
            continue
        if stripped == "Primary Linux anchors:":
            in_anchor_list = True
            continue
        if in_anchor_list:
            if stripped.startswith("- "):
                anchors.append(stripped[2:])
                continue
            if anchors:
                break
    return anchors


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    required_files = [
        RELEASE_READINESS_PATH,
        SCRIPTS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        FREEZE_MAP_PATH,
        ROADMAP_PATH,
        BUILD_ONLY_CHECKER_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ]

    for rel_path in required_files:
        if not (root / rel_path).exists():
            errors.append(f"missing file: {rel_path}")
    if errors:
        return errors

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    require_exact_count(
        errors,
        RELEASE_READINESS_PATH,
        read_text(root / RELEASE_READINESS_PATH),
        RELEASE_READINESS_MARKERS,
    )
    require_exact_count(
        errors,
        REVIEW_CHECKLIST_PATH,
        read_text(root / REVIEW_CHECKLIST_PATH),
        REVIEW_CHECKLIST_MARKERS,
    )
    require_exact_count(
        errors,
        FREEZE_MAP_PATH,
        read_text(root / FREEZE_MAP_PATH),
        FREEZE_MAP_MARKERS,
    )
    require_exact_count(
        errors,
        SCRIPTS_README_PATH,
        read_text(root / SCRIPTS_README_PATH),
        SCRIPTS_README_MARKERS,
    )
    require_exact_count(
        errors,
        MAKEFILE_PATH,
        read_text(root / MAKEFILE_PATH),
        MAKEFILE_MARKERS,
    )
    require_exact_count(
        errors,
        WORKFLOW_PATH,
        read_text(root / WORKFLOW_PATH),
        WORKFLOW_MARKERS,
    )

    anchors = extract_phase12_anchor_bullets(read_text(root / ROADMAP_PATH))
    if anchors != ROADMAP_ANCHORS:
        errors.append("roadmap Phase 12 anchor list drifted from the expected four-entry set")

    return errors


def good_release_readiness_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Release Readiness Survey",
            "",
            "## Status",
            "- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
            "- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "",
            "## Current Release Reading",
            "- `zigux/tests/phase12_build.zig` wires `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` into the active `smoke` and `test` steps, with the `smoke` step already running the `virtio_net` syntax lab beside the shipped `virtio_scsi` packet.",
            "- The shared release packet now also carries the bounded `virtio_net_transmit_recycle` follow-up through `drivers/net/virtio_net_transmit_recycle.zig` and `zigux/tests/phase12_virtio_net_transmit_recycle.zig`: current `zigux/tests/phase12_build.zig` runs that replay in both `smoke` and `test`, but the release reading must keep it framed as transmit-disposition reviewability rather than as live interrupt-backed completion, refill execution, or DMA parity.",
            "- The broader shared-summary packet is now aligned on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` already keep the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard plus the shipped `make -C zigux phase12-validate` route explicit, `zigux/tests/README.md` does the same in its Phase 12 inventory, and `scripts/zigux/README.md` now carries a dedicated Phase 12 flow block naming `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and the shipped validator-first then smoke-first routes.",
            "- `scripts/zigux/check-build-only-phase12-surface.py` now matches that shipped support-checker-plus-validate-route reminder too, so `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and this readiness note can stay parked together until another shared reminder surface actually drifts, rather than reopening driver-local, fallback-catalog, or verify-shard wording first.",
            "- The smaller validator-first boundary in the lane is now shipped: current `master` carries `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, the Linux-style `make -C zigux phase12-validate` route, and the bootstrap workflow step that reruns that same route, but it still does not expose a focused libbpf-only replay or a cross-build replay, so release-planning notes should treat `phase12-validate` as shipped validation evidence while keeping the parked survey and fallback companions explicit.",
            "- Keep the same degraded-workflow validation trio explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` should stay ahead of the attached-toolchain smoke and full replay routes so contract drift still fails closed when the local runtime needs the fallback path.",
            "",
            "## Next Bounded Step",
            "- Current `master` keeps the release-order, readiness, coordination, closure, workflow, Makefile, docs-root, review-checklist, scripts-root, and tests-root companions aligned around the starter-present `virtio_net` plus smoke-first `virtio_scsi` packet, including the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor and the shipped `phase12-validate` support bundle. Leave this same-lane packet parked unless one of those shared reminder surfaces drifts again; if it reopens, refresh only the smallest reminder that moved before widening into any new driver claims.",
            "",
        ]
    )


def good_review_checklist_text() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "",
            "- avoid implying a broader shared `check-phase12-*.py` family, focused-libbpf-only replay, or cross-build replay, while keeping the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` checker plus the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route?",
            "- if the change touches that same shared Phase 12 complex-driver packet after the shipped validator-first support bundle changes, do `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/Makefile`, and `make -C zigux phase12-validate` keep the dedicated support checker plus the shipped validator-first support route explicit as support-bundle evidence instead of treating them as a second direct replay route or as an absent shared surface?",
            "",
        ]
    )


def good_freeze_map_text() -> str:
    return "\n".join(
        [
            "# Zigux Freeze Map",
            "",
            "- the shared Phase 12 PMO release packet also stays release-planning-only beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`: queueing, throughput, rollback, and recovery wording there, in the shipped validator-first `make -C zigux phase12-validate` support bundle, and in the smoke-first shared replay packet must stay bounded to driver-local review evidence, lab-only reversible-delivery scaffolding, and shared anti-overlap notes without implying active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`",
            "",
        ]
    )


def good_scripts_readme_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned across `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `zigux/tests/phase12_build.zig`, the starter-present `virtio_net` packet, the shipped `virtio_scsi` packet, and the bounded NVMe starter-plus-verifier-plus-direct-test-plus-manifest packet before the shared validator-first then smoke-first routes run.",
            "- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` keep the degraded-workflow support bundle explicit in this scripts-root summary so the shipped validator-first route stays visible as support-bundle evidence rather than as a second direct replay route.",
            "",
        ]
    )


def good_roadmap_text() -> str:
    return "\n".join(
        [
            "# Roadmap",
            "",
            PHASE12_SECTION_HEADING,
            "",
            "Primary Linux anchors:",
            *[f"- {anchor}" for anchor in ROADMAP_ANCHORS],
            "",
        ]
    )


def good_makefile_text() -> str:
    return "\n".join(
        [
            "phase12-validate:",
            "\t$(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test",
            "\t$(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
            "\t$(PYTHON) scripts/zigux/validate-phase12.py",
            "",
            "phase12: phase12-validate phase12-smoke phase12-test",
            "",
        ]
    )


def good_workflow_text() -> str:
    return "\n".join(
        [
            "- name: Validate Phase 12 degraded-workflow bundle",
            "  run: make -C zigux phase12-validate",
            "- name: Run focused Phase 12 smoke shard",
            "  run: make -C zigux phase12-smoke",
            "- name: Run Phase 12 complex driver tests",
            "  run: zig build test --build-file zigux/tests/phase12_build.zig --summary all",
            "",
        ]
    )


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        raise SystemExit(f"{label}: {errors!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-check-"))
    case_count = 0
    try:
        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write_text(tmp_root / FREEZE_MAP_PATH, good_freeze_map_text())
        write_text(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write_text(tmp_root / ROADMAP_PATH, good_roadmap_text())
        write_text(tmp_root / BUILD_ONLY_CHECKER_PATH, "#!/usr/bin/env python3\n")
        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())

        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`\n",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
            "missing build-only-contract marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                "- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`\n",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "missing support-checker marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                RELEASE_READINESS_MARKERS[2],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "`zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`",
            "missing rollback-lab gate marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                RELEASE_READINESS_MARKERS[3],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "virtio_net_transmit_recycle",
            "missing transmit-recycle release marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                RELEASE_READINESS_MARKERS[4],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "The broader shared-summary packet is now aligned on current `master`",
            "missing broader-shared-summary marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                RELEASE_READINESS_MARKERS[5],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "support-checker-plus-validate-route reminder",
            "missing build-only-checker alignment marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                RELEASE_READINESS_MARKERS[6],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "The smaller validator-first boundary in the lane is now shipped",
            "missing validator-first support-bundle marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                RELEASE_READINESS_MARKERS[7],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Keep the same degraded-workflow validation trio explicit too",
            "missing degraded-workflow trio marker",
        )

        write_text(tmp_root / RELEASE_READINESS_PATH, good_release_readiness_text())
        write_text(
            tmp_root / RELEASE_READINESS_PATH,
            good_release_readiness_text().replace(
                RELEASE_READINESS_MARKERS[8],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Leave this same-lane packet parked unless one of those shared reminder surfaces drifts again",
            "missing parked-next-step marker",
        )

        write_text(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write_text(
            tmp_root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                SCRIPTS_README_MARKERS[0],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SCRIPTS_README_MARKERS[0],
            "missing scripts-readme phase12-flow marker",
        )

        write_text(tmp_root / SCRIPTS_README_PATH, good_scripts_readme_text())
        write_text(
            tmp_root / SCRIPTS_README_PATH,
            good_scripts_readme_text().replace(
                SCRIPTS_README_MARKERS[1],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            SCRIPTS_README_MARKERS[1],
            "missing scripts-readme degraded-workflow marker",
        )

        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write_text(
            tmp_root / REVIEW_CHECKLIST_PATH,
            good_review_checklist_text().replace(
                REVIEW_CHECKLIST_MARKERS[0],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "support-bundle evidence rather than as a second direct replay route",
            "missing review-checklist marker",
        )

        write_text(tmp_root / REVIEW_CHECKLIST_PATH, good_review_checklist_text())
        write_text(
            tmp_root / REVIEW_CHECKLIST_PATH,
            good_review_checklist_text().replace(
                REVIEW_CHECKLIST_MARKERS[1],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            REVIEW_CHECKLIST_MARKERS[1],
            "missing review-checklist support-route marker",
        )

        write_text(tmp_root / FREEZE_MAP_PATH, good_freeze_map_text())
        write_text(
            tmp_root / FREEZE_MAP_PATH,
            good_freeze_map_text().replace(
                FREEZE_MAP_MARKERS[0],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            FREEZE_MAP_MARKERS[0],
            "missing freeze-map marker",
        )

        write_text(tmp_root / FREEZE_MAP_PATH, good_freeze_map_text())
        write_text(
            tmp_root / FREEZE_MAP_PATH,
            good_freeze_map_text().replace(
                FREEZE_MAP_MARKERS[1],
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            FREEZE_MAP_MARKERS[1],
            "missing freeze-map support-bundle boundary marker",
        )

        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "phase12-validate:",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "phase12-validate:",
            "missing makefile validate target marker",
        )

        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "scripts/zigux/check-build-only-phase12-surface.py --self-test",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "scripts/zigux/check-build-only-phase12-surface.py --self-test",
            "missing makefile build-only checker marker",
        )

        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
            "missing makefile readiness-checker marker",
        )

        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "scripts/zigux/validate-phase12.py",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "scripts/zigux/validate-phase12.py",
            "missing makefile validate-phase12 marker",
        )

        write_text(tmp_root / MAKEFILE_PATH, good_makefile_text())
        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "phase12: phase12-validate phase12-smoke phase12-test",
                "phase12: phase12-smoke phase12-test",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "phase12: phase12-validate phase12-smoke phase12-test",
            "missing makefile route",
        )

        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())
        write_text(
            tmp_root / WORKFLOW_PATH,
            good_workflow_text().replace(
                "Validate Phase 12 degraded-workflow bundle",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Validate Phase 12 degraded-workflow bundle",
            "missing workflow validate-step title",
        )

        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())
        write_text(
            tmp_root / WORKFLOW_PATH,
            good_workflow_text().replace(
                "run: make -C zigux phase12-validate",
                "run: make -C zigux phase12-smoke",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "run: make -C zigux phase12-validate",
            "missing workflow route",
        )

        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())
        write_text(
            tmp_root / WORKFLOW_PATH,
            good_workflow_text().replace(
                "Run focused Phase 12 smoke shard",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Run focused Phase 12 smoke shard",
            "missing workflow smoke-step title",
        )

        write_text(tmp_root / WORKFLOW_PATH, good_workflow_text())
        write_text(
            tmp_root / WORKFLOW_PATH,
            good_workflow_text().replace(
                "Run Phase 12 complex driver tests",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Run Phase 12 complex driver tests",
            "missing workflow test-step title",
        )

        write_text(tmp_root / ROADMAP_PATH, good_roadmap_text())
        write_text(
            tmp_root / ROADMAP_PATH,
            good_roadmap_text().replace("- `drivers/scsi/virtio_scsi.c`\n", "", 1),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "roadmap Phase 12 anchor list drifted",
            "roadmap anchor drift not detected",
        )

        case_count += 1
        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "missing checker marker not detected",
        )
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
    print(f"PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="repository root to validate (defaults to the checker directory)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("phase12 release-readiness packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

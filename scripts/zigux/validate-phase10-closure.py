#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else _SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
]

CLOSURE_MARKERS = [
    "PHASE10_STATUS=active",
    "PHASE10_TRANCHE=virtio-lab-bundle",
    "PHASE10_CLOSURE_EVIDENCE=verified",
    "PHASE10_DOC_COUNT=9",
    "PHASE10_MANIFEST_COUNT=4",
    "PHASE10_DRIVER_COUNT=4",
    "PHASE10_TEST_COUNT=9",
    "PHASE10_HAS_VIRTIO_MMIO_ZIG=yes",
    "PHASE10_ROADMAP_PARITY_SCOREBOARD=present",
    "PHASE10_ROADMAP_SCOREBOARD_ROW_COUNT=4",
    "PHASE10_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed",
    "PHASE10_ROADMAP_MMIO_WRAPPERS=starter_landed",
    "PHASE10_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
    "PHASE10_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
    "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md",
    "PHASE10_FREEZE_BOUNDARY_STATUS=aligned",
    "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
    "phase10-mmio-interrupt-ack-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-registration-lifecycle",
    "kernel/workqueue_bridge.zig",
    "kernel/trace/ring_buffer.zig",
    "shared closure validator now also fails closed if the MMIO interrupt-ack rung disappears from the closure packet",
    "The machine-checked MMIO closure subset therefore reaches the current landed helper ladder through interrupt acknowledgement rather than stopping one rung earlier.",
]

DOCS_README_MARKERS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
]

CHECKLIST_MARKERS = [
    "if the change is a Phase 10 virtio slice, do `Documentation/zigux/phase10-closure-evidence.md`",
    "if the change touches the Phase 10 scoreboard or closure packet, do the Phase 5 sample lane and the current Phase 9 runtime loader-gap ownership packet still stay outside the Phase 10 virtio parity readout",
    "if the change widens a Phase 10 virtio transport-facing path, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-closure-evidence.md`, and the ring/input/MMIO survey manifests still keep the risky transport posture explicit",
    "if the change touches the Phase 10 freeze-boundary packet, do `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, and `Documentation/zigux/review-checklist.md` still keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicitly owned by the separate Phase 14 boundary-map and concurrency-audit lane",
]

FREEZE_MAP_MARKERS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "Architecture Council",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_STATUS=active",
    "PHASE10_LEDGER_TRANCHE=virtio-lab-bundle",
    "PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md",
    "PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json",
    "PHASE10_LEDGER_SURVEY_CORE_COMMIT=bc71a85e989bb3d4f0a7d19067f4f1f47527c505",
    "PHASE10_LEDGER_SURVEY_RING_COMMIT=fe8a43ea2e186da0da152198b571dff57ea3c38c",
    "PHASE10_LEDGER_SURVEY_INPUT_COMMIT=b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38",
    "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=0945df1cf664a3582d7241f859183a13f3f04adb",
    "PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed",
    "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed",
    "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
    "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
    "PHASE10_LEDGER_MAKEFILE=zigux/Makefile",
    "PHASE10_LEDGER_WORKFLOW=.github/workflows/zigux-bootstrap.yml",
    "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_EXACT_CHECK_2=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_LEDGER_EXACT_CHECK_3=make -C zigux phase10-validate",
    "PHASE10_LEDGER_EXACT_CHECK_4=make -C zigux phase10-test",
    "PHASE10_LEDGER_EXACT_CHECK_5=make -C zigux phase10",
    "PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_phase10-mmio-lifecycle-and-irq-paths_splits_smaller",
    "PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths",
]

MAKEFILE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
    "scripts/zigux/validate-phase10.py --self-test",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py --self-test",
    "scripts/zigux/validate-phase10-closure.py",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 10 shared validator",
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
]

PHASE10_BUILD_MARKERS = [
    '.name = "phase10-virtio-core-tests",',
    '.name = "phase10-virtio-core-survey-tests",',
    '.name = "phase10-virtio-ring-tests",',
    '.name = "phase10-virtio-ring-reset-reuse-tests",',
    '.name = "phase10-virtio-ring-survey-tests",',
    '.name = "phase10-virtio-input-tests",',
    '.name = "phase10-virtio-input-survey-tests",',
    '.name = "phase10-virtio-mmio-tests",',
    '.name = "phase10-virtio-mmio-survey-tests",',
]

SURVEY_TEXT_MARKERS = {
    "Documentation/zigux/phase10-virtio-core-survey.md": [
        "phase10-config-delivery-disposition-helper",
        "phase10-core-probe-remove-lifecycle",
    ],
    "Documentation/zigux/phase10-virtio-ring-survey.md": [
        "phase10-mmio-config-write-helper",
        "phase10-mmio-interrupt-ack-helper",
        "no smaller ready transport follow-up remains ahead of the still-blocked lifecycle and IRQ packet",
    ],
    "Documentation/zigux/phase10-virtio-input-survey.md": [
        "phase10-virtio-input-registration-preflight-helper",
        "phase10-virtio-input-queue-callback-preflight-helper",
        "phase10-virtio-input-registration-lifecycle",
    ],
    "Documentation/zigux/phase10-virtio-mmio-survey.md": [
        "phase10-mmio-config-write-helper",
        "phase10-mmio-interrupt-ack-helper",
        "phase10-mmio-lifecycle-and-irq-paths",
        "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md",
        "PHASE10_FREEZE_BOUNDARY_STATUS=aligned",
        "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
        "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no",
        "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
        "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
        "boundary maps",
        "concurrency audits",
        "explicit stay-in-C decisions where warranted",
        "wrapper-first or study-only posture",
        "drivers/virtio/*.zig",
    ],
}

TEST_MARKERS = {
    "zigux/tests/phase10_virtio_core_survey.zig": [
        'const landed_core_helper_evidence = closure_manifest.object.get("landed_core_helper_evidence") orelse return error.TestUnexpectedResult;',
        '"phase10-config-generation-summary-helper",',
        '"phase10-config-delivery-disposition-helper",',
    ],
    "zigux/tests/phase10_virtio_ring_survey.zig": [
        'const landed_ring_helper_evidence = closure_manifest.object.get("landed_ring_helper_evidence") orelse return error.TestUnexpectedResult;',
        '"phase10-queue-reset-helper",',
        '"phase10-mmio-interrupt-ack-helper"',
        '"phase10-mmio-lifecycle-and-irq-paths"',
    ],
    "zigux/tests/phase10_virtio_input_survey.zig": [
        'const landed_input_helper_evidence = closure_manifest.object.get("landed_input_helper_evidence") orelse return error.TestUnexpectedResult;',
        '"phase10-virtio-input-capability-setup-helper",',
        '"phase10-virtio-input-multitouch-slot-helper",',
        '"phase10-virtio-input-teardown-observation-helper",',
        '"phase10-virtio-input-registration-preflight-helper",',
        '"phase10-virtio-input-queue-callback-preflight-helper",',
    ],
    "zigux/tests/phase10_virtio_mmio.zig": [
        'test "phase10 virtio mmio summarizes bounded interrupt state and reset cleanup without claiming irq delivery" {',
        'test "phase10 virtio mmio acknowledges only pending bounded interrupt bits" {',
        "try std.testing.expectError(error.UnsupportedInterruptBits, window.acknowledgeInterrupt(0x8));",
    ],
    "zigux/tests/phase10_virtio_mmio_survey.zig": [
        'const landed_mmio_helper_evidence = closure_manifest.object.get("landed_mmio_helper_evidence") orelse return error.TestUnexpectedResult;',
        '"phase10-mmio-config-write-helper",',
        '"phase10-mmio-interrupt-ack-helper",',
        'if (std.mem.eql(u8, gap.id, "phase10-mmio-interrupt-ack-helper")) {',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase10-mmio-interrupt-ack-helper") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FREEZE_BOUNDARY_STATUS=aligned") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/workqueue.c") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "kernel/trace/ring_buffer.c") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "boundary maps") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "concurrency audits") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "explicit stay-in-C decisions where warranted") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "wrapper-first or study-only posture") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/virtio/*.zig") != null);',
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []

    check_markers(missing, "closure", read_text(root, "Documentation/zigux/phase10-closure-evidence.md"), CLOSURE_MARKERS)
    check_markers(missing, "docs_readme", read_text(root, "Documentation/zigux/README.md"), DOCS_README_MARKERS)
    check_markers(missing, "checklist", read_text(root, "Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS)
    check_markers(missing, "freeze_map", read_text(root, "Documentation/zigux/freeze-map.md"), FREEZE_MAP_MARKERS)
    check_markers(missing, "ledger", read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"), LEDGER_MARKERS)
    check_markers(missing, "makefile", read_text(root, "zigux/Makefile"), MAKEFILE_MARKERS)
    check_markers(missing, "workflow", read_text(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)
    check_markers(missing, "phase10_build", read_text(root, "zigux/tests/phase10_build.zig"), PHASE10_BUILD_MARKERS)

    for rel_path, markers in SURVEY_TEXT_MARKERS.items():
        check_markers(missing, rel_path, read_text(root, rel_path), markers)
    for rel_path, markers in TEST_MARKERS.items():
        check_markers(missing, rel_path, read_text(root, rel_path), markers)

    manifest = load_json(root, "zigux/tests/phase10_closure_manifest.json")
    if not isinstance(manifest, dict):
        missing.append("manifest:type")
        return [], missing

    expected_scalars = {
        "phase": "Phase 10",
        "status": "active",
        "tranche": "virtio-lab-bundle",
        "doc_count": 9,
        "manifest_count": 4,
        "driver_count": 4,
        "test_count": 9,
        "has_virtio_mmio_zig": True,
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "review_checklist": "Documentation/zigux/review-checklist.md",
        "risky_transport_posture": "blocked_on_risky_transport",
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
    }
    for key, value in expected_scalars.items():
        if manifest.get(key) != value:
            missing.append(f"manifest:{key}={manifest.get(key)!r}")

    scoreboard = manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        missing.append("manifest:roadmap_parity_scoreboard")
    else:
        expected_statuses = {
            "virtqueue_wrappers": "starter_landed",
            "mmio_wrappers": "starter_landed",
            "lab_only_driver_validation": "starter_landed",
            "dual_implementations_for_risky_areas": "blocked_on_risky_transport",
        }
        for key, status in expected_statuses.items():
            entry = scoreboard.get(key)
            if not isinstance(entry, dict) or entry.get("status") != status:
                missing.append(f"manifest:scoreboard:{key}")

    landed_core = manifest.get("landed_core_helper_evidence")
    expected_landed_core = {
        "zigux/tests/phase10_virtio_core_manifest.json": [
            "phase10-config-generation-summary-helper",
            "phase10-config-delivery-disposition-helper",
        ]
    }
    if landed_core != expected_landed_core:
        missing.append("manifest:landed_core_helper_evidence")

    landed_ring = manifest.get("landed_ring_helper_evidence")
    expected_landed_ring = {
        "zigux/tests/phase10_virtio_ring_manifest.json": [
            "phase10-virtqueue-shape-helper",
            "phase10-used-buffer-polling-helper",
            "phase10-callback-disable-helper",
            "phase10-callback-enable-helper",
            "phase10-callback-enable-prepare-helper",
            "phase10-callback-delay-helper",
            "phase10-notify-prepare-helper",
            "phase10-queue-reset-guard-helper",
            "phase10-queue-reset-helper",
        ]
    }
    if landed_ring != expected_landed_ring:
        missing.append("manifest:landed_ring_helper_evidence")

    landed_mmio = manifest.get("landed_mmio_helper_evidence")
    expected_landed_mmio = {
        "zigux/tests/phase10_virtio_mmio_manifest.json": [
            "phase10-mmio-register-window-helper",
            "phase10-mmio-queue-register-helper",
            "phase10-mmio-queue-notify-helper",
            "phase10-mmio-queue-address-helper",
            "phase10-mmio-config-window-helper",
            "phase10-mmio-config-write-helper",
            "phase10-mmio-interrupt-ack-helper",
        ]
    }
    if landed_mmio != expected_landed_mmio:
        missing.append("manifest:landed_mmio_helper_evidence")

    landed_input = manifest.get("landed_input_helper_evidence")
    expected_landed_input = {
        "zigux/tests/phase10_virtio_input_manifest.json": [
            "phase10-virtio-input-capability-setup-helper",
            "phase10-virtio-input-multitouch-slot-helper",
            "phase10-virtio-input-teardown-observation-helper",
            "phase10-virtio-input-registration-preflight-helper",
            "phase10-virtio-input-queue-callback-preflight-helper",
        ]
    }
    if landed_input != expected_landed_input:
        missing.append("manifest:landed_input_helper_evidence")

    blocked = manifest.get("blocked_transport_gaps")
    expected_blocked = {
        "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
        "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
    }
    if blocked != expected_blocked:
        missing.append("manifest:blocked_transport_gaps")

    ready_transport_followups = manifest.get("ready_transport_followups")
    if ready_transport_followups != {}:
        missing.append("manifest:ready_transport_followups")

    survey_provenance = manifest.get("survey_provenance")
    expected_survey_provenance = {
        "source": "manifest_derived",
        "lane_keys": {
            "core": "P10-L03",
            "ring": "P10-L08",
            "input": "P10-L13",
            "mmio": "P10-L18",
        },
        "surveyed_commits": {
            "core": "bc71a85e989bb3d4f0a7d19067f4f1f47527c505",
            "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
            "input": "b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38",
            "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
        },
    }
    if survey_provenance != expected_survey_provenance:
        missing.append("manifest:survey_provenance")

    exact_checks = manifest.get("exact_checks")
    expected_exact_checks = [
        "python3 scripts/zigux/validate-phase10-closure.py",
        "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
    ]
    if exact_checks != expected_exact_checks:
        missing.append("manifest:exact_checks")

    return [], missing


def write_fixture(root: Path) -> None:
    texts = {
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_MARKERS),
        "Documentation/zigux/README.md": "\n".join(DOCS_README_MARKERS),
        "Documentation/zigux/review-checklist.md": "\n".join(CHECKLIST_MARKERS),
        "Documentation/zigux/freeze-map.md": "\n".join(FREEZE_MAP_MARKERS),
        "Documentation/zigux/phase10-virtio-core-survey.md": "\n".join(SURVEY_TEXT_MARKERS["Documentation/zigux/phase10-virtio-core-survey.md"]),
        "Documentation/zigux/phase10-virtio-ring-survey.md": "\n".join(SURVEY_TEXT_MARKERS["Documentation/zigux/phase10-virtio-ring-survey.md"]),
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(SURVEY_TEXT_MARKERS["Documentation/zigux/phase10-virtio-input-survey.md"]),
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(SURVEY_TEXT_MARKERS["Documentation/zigux/phase10-virtio-mmio-survey.md"]),
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(LEDGER_MARKERS),
        "zigux/Makefile": "\n".join(MAKEFILE_MARKERS),
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS),
        "zigux/tests/phase10_build.zig": "\n".join(PHASE10_BUILD_MARKERS),
        "zigux/tests/phase10_virtio_core_survey.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_core_survey.zig"]),
        "zigux/tests/phase10_virtio_ring_survey.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_ring_survey.zig"]),
        "zigux/tests/phase10_virtio_input_survey.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_input_survey.zig"]),
        "zigux/tests/phase10_virtio_mmio.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_mmio.zig"]),
        "zigux/tests/phase10_virtio_mmio_survey.zig": "\n".join(TEST_MARKERS["zigux/tests/phase10_virtio_mmio_survey.zig"]),
    }
    manifest = {
        "phase": "Phase 10",
        "status": "active",
        "tranche": "virtio-lab-bundle",
        "doc_count": 9,
        "manifest_count": 4,
        "driver_count": 4,
        "test_count": 9,
        "has_virtio_mmio_zig": True,
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "review_checklist": "Documentation/zigux/review-checklist.md",
        "risky_transport_posture": "blocked_on_risky_transport",
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
        "roadmap_parity_scoreboard": {
            "virtqueue_wrappers": {"status": "starter_landed"},
            "mmio_wrappers": {"status": "starter_landed"},
            "lab_only_driver_validation": {"status": "starter_landed"},
            "dual_implementations_for_risky_areas": {"status": "blocked_on_risky_transport"},
        },
        "survey_provenance": {
            "source": "manifest_derived",
            "lane_keys": {
                "core": "P10-L03",
                "ring": "P10-L08",
                "input": "P10-L13",
                "mmio": "P10-L18",
            },
            "surveyed_commits": {
                "core": "bc71a85e989bb3d4f0a7d19067f4f1f47527c505",
                "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
                "input": "b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38",
                "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
            },
        },
        "landed_core_helper_evidence": {
            "zigux/tests/phase10_virtio_core_manifest.json": [
                "phase10-config-generation-summary-helper",
                "phase10-config-delivery-disposition-helper",
            ]
        },
        "landed_ring_helper_evidence": {
            "zigux/tests/phase10_virtio_ring_manifest.json": [
                "phase10-virtqueue-shape-helper",
                "phase10-used-buffer-polling-helper",
                "phase10-callback-disable-helper",
                "phase10-callback-enable-helper",
                "phase10-callback-enable-prepare-helper",
                "phase10-callback-delay-helper",
                "phase10-notify-prepare-helper",
                "phase10-queue-reset-guard-helper",
                "phase10-queue-reset-helper",
            ]
        },
        "landed_mmio_helper_evidence": {
            "zigux/tests/phase10_virtio_mmio_manifest.json": [
                "phase10-mmio-register-window-helper",
                "phase10-mmio-queue-register-helper",
                "phase10-mmio-queue-notify-helper",
                "phase10-mmio-queue-address-helper",
                "phase10-mmio-config-window-helper",
                "phase10-mmio-config-write-helper",
                "phase10-mmio-interrupt-ack-helper",
            ]
        },
        "landed_input_helper_evidence": {
            "zigux/tests/phase10_virtio_input_manifest.json": [
                "phase10-virtio-input-capability-setup-helper",
                "phase10-virtio-input-multitouch-slot-helper",
                "phase10-virtio-input-teardown-observation-helper",
                "phase10-virtio-input-registration-preflight-helper",
                "phase10-virtio-input-queue-callback-preflight-helper",
            ]
        },
        "blocked_transport_gaps": {
            "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
            "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
        },
        "ready_transport_followups": {},
        "exact_checks": [
            "python3 scripts/zigux/validate-phase10-closure.py",
            "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
            "make -C zigux phase10-validate",
            "make -C zigux phase10-test",
            "make -C zigux phase10",
        ],
    }

    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path.endswith(".json"):
            path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(texts.get(rel_path, "fixture\n"), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-closure-self-test:{label}:missing_files:{','.join(missing_files)}")
    if marker not in missing_markers:
        raise SystemExit(
            f"phase10-closure-self-test:{label}:expected:{marker}:actual:{','.join(missing_markers) if missing_markers else 'none'}"
        )


def expect_missing_file(label: str, root: Path, expected_file: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            f"phase10-closure-self-test:{label}:unexpected_markers:{','.join(missing_markers)}"
        )
    if expected_file not in missing_files:
        raise SystemExit(
            f"phase10-closure-self-test:{label}:expected_file:{expected_file}:actual:{','.join(missing_files) if missing_files else 'none'}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        fixture_root = Path(tmp_dir) / "repo"
        write_fixture(fixture_root)

        missing_files, missing_markers = validate(fixture_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-closure-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        core_slice_path = fixture_root / "Documentation/zigux/phase10-virtio-core-slice.md"
        core_slice_path.unlink()
        expect_missing_file(
            "core_slice_required_file",
            fixture_root,
            "Documentation/zigux/phase10-virtio-core-slice.md",
        )
        write_fixture(fixture_root)

        core_manifest_path = fixture_root / "zigux/tests/phase10_virtio_core_manifest.json"
        core_manifest_path.unlink()
        expect_missing_file(
            "core_manifest_required_file",
            fixture_root,
            "zigux/tests/phase10_virtio_core_manifest.json",
        )
        write_fixture(fixture_root)

        input_path = fixture_root / "zigux/tests/phase10_virtio_input_survey.zig"
        original_input = input_path.read_text(encoding="utf-8")
        input_path.write_text(
            original_input.replace(
                'const landed_input_helper_evidence = closure_manifest.object.get("landed_input_helper_evidence") orelse return error.TestUnexpectedResult;',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "input_helper_evidence_guard",
            fixture_root,
            'zigux/tests/phase10_virtio_input_survey.zig:const landed_input_helper_evidence = closure_manifest.object.get("landed_input_helper_evidence") orelse return error.TestUnexpectedResult;',
        )
        input_path.write_text(original_input, encoding="utf-8")

        manifest_path = fixture_root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["landed_input_helper_evidence"] = {}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "landed_input_helper_manifest_guard",
            fixture_root,
            "manifest:landed_input_helper_evidence",
        )
        write_fixture(fixture_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["landed_core_helper_evidence"] = {}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "landed_core_helper_manifest_guard",
            fixture_root,
            "manifest:landed_core_helper_evidence",
        )
        write_fixture(fixture_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["landed_ring_helper_evidence"]["zigux/tests/phase10_virtio_ring_manifest.json"].pop()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "landed_ring_helper_manifest_guard",
            fixture_root,
            "manifest:landed_ring_helper_evidence",
        )
        write_fixture(fixture_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["landed_mmio_helper_evidence"]["zigux/tests/phase10_virtio_mmio_manifest.json"].pop()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "mmio_interrupt_ack_manifest",
            fixture_root,
            "manifest:landed_mmio_helper_evidence",
        )
        write_fixture(fixture_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ready_transport_followups"] = {
            "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-interrupt-ack-helper"
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "parked_ready_transport_followups",
            fixture_root,
            "manifest:ready_transport_followups",
        )
        write_fixture(fixture_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["blocked_transport_gaps"]["zigux/tests/phase10_virtio_mmio_manifest.json"] = "phase10-mmio-config-write-helper"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "parked_mmio_blocker_guard",
            fixture_root,
            "manifest:blocked_transport_gaps",
        )
        write_fixture(fixture_root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["surveyed_commits"]["mmio"] = "deadbeef"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "survey_provenance_commit_guard",
            fixture_root,
            "manifest:survey_provenance",
        )
        write_fixture(fixture_root)

        closure_path = fixture_root / "Documentation/zigux/phase10-closure-evidence.md"
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(
            original_closure.replace(
                "PHASE10_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
                "PHASE10_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_roadmap_scoreboard",
            fixture_root,
            "closure:PHASE10_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
        )
        write_fixture(fixture_root)

        ledger_path = fixture_root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
                "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_roadmap_scoreboard",
            fixture_root,
            "ledger:PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
        )
        write_fixture(fixture_root)

        survey_note_path = fixture_root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        original_survey_note = survey_note_path.read_text(encoding="utf-8")
        survey_note_path.write_text(
            original_survey_note.replace(
                "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
                "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "mmio_freeze_boundary_note_guard",
            fixture_root,
            "Documentation/zigux/phase10-virtio-mmio-survey.md:PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
        )
        write_fixture(fixture_root)

        mmio_survey_test_path = fixture_root / "zigux/tests/phase10_virtio_mmio_survey.zig"
        original_mmio_survey_test = mmio_survey_test_path.read_text(encoding="utf-8")
        mmio_survey_test_path.write_text(
            original_mmio_survey_test.replace(
                'try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates") != null);',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "mmio_freeze_boundary_test_guard",
            fixture_root,
            'zigux/tests/phase10_virtio_mmio_survey.zig:try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates") != null);',
        )

    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=14")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_CLOSURE_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_CLOSURE_MARKERS_END")
    sys.exit(1)

total_markers = (
    len(CLOSURE_MARKERS)
    + len(DOCS_README_MARKERS)
    + len(CHECKLIST_MARKERS)
    + len(FREEZE_MAP_MARKERS)
    + len(LEDGER_MARKERS)
    + len(MAKEFILE_MARKERS)
    + len(WORKFLOW_MARKERS)
    + len(PHASE10_BUILD_MARKERS)
    + sum(len(v) for v in SURVEY_TEXT_MARKERS.values())
    + sum(len(v) for v in TEST_MARKERS.values())
)
print("PHASE10_CLOSURE_VALIDATION=pass")
print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE10_CLOSURE_REQUIRED_MARKER_COUNT={total_markers}")
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

DOCS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

MANIFESTS = [
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

DRIVERS = [
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_mmio.zig",
]

TESTS = [
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
]

EXPECTED_ALLOWED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]

EXPECTED_ALLOWED_EVIDENCE_KINDS = [
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
]

EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS = [
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]

EXPECTED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase10-closure-inventory.py",
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10"
]

EXPECTED_CLOSURE_MANIFEST = {
    "phase": "Phase 10",
    "status": "active",
    "tranche": "virtio-lab-bundle",
    "doc_count": 9,
    "manifest_count": 4,
    "driver_count": 4,
    "test_count": 11,
    "has_virtio_mmio_zig": True,
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "review_checklist": "Documentation/zigux/review-checklist.md",
    "risky_transport_posture": "blocked_on_risky_transport",
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}

EXPECTED_SURVEY_LANE_KEYS = {
    "core": "P10-L01",
    "ring": "P10-L07",
    "input": "P10-L13",
    "mmio": "P10-L18",
}

EXPECTED_SURVEYED_COMMITS = {
    "core": "d30cbe483a2f019ae797b309a29556bd58fe00d0",
    "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
    "input": "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21",
    "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
}

EXPECTED_LANDED_INPUT_HELPER_EVIDENCE = {
    "zigux/tests/phase10_virtio_input_manifest.json": [
        "phase10-virtio-input-capability-setup-helper",
        "phase10-virtio-input-multitouch-slot-helper",
        "phase10-virtio-input-teardown-observation-helper",
        "phase10-virtio-input-registration-preflight-helper",
        "phase10-virtio-input-queue-callback-preflight-helper",
        "phase10-virtio-input-probe-preflight-helper"
    ]
}

EXPECTED_FOCUSED_HARNESS_REPLAYS = {
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        "phase10 ring drained-reset reuse replay"
    ],
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig": [
        "phase10 input multitouch-ready preflight replay"
    ],
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig": [
        "phase10 mmio multi-queue isolation replay",
        "phase10 mmio reset clears legacy and modern queue address plans after queue selection changes"
    ]
}

TESTS_README_MARKERS = [
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "scripts/zigux/check-phase10-core-packet.py",
    "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
]

REQUIRED_FILES = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux/tests/README.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    *DOCS,
    *MANIFESTS,
    *DRIVERS,
    *TESTS,
]

CLOSURE_MARKERS = [
    "PHASE10_STATUS=active",
    "PHASE10_TRANCHE=virtio-lab-bundle",
    "PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/",
    "PHASE10_SURVEY_PROVENANCE_SOURCE=manifest_derived",
    "PHASE10_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_SURVEY_RING_LANE=P10-L07",
    "PHASE10_SURVEY_INPUT_LANE=P10-L13",
    "PHASE10_SURVEY_MMIO_LANE=P10-L18",
    "PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "phase10-mmio-interrupt-ack-helper",
    "phase10-mmio-lifecycle-and-irq-paths"
]

CLOSURE_EXACT_ONCE_MARKERS = [
    "PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_TEST_COUNT=11"
]

DOCS_README_MARKERS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "python3 scripts/zigux/check-phase10-closure-inventory.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "make -C zigux phase10-validate",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "focused harness replays",
    "queue-handling and ready-state gate"
]

DOCS_README_EXACT_ONCE_MARKERS = [
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "focused harness replays",
    "queue-handling and ready-state gate"
]

CHECKLIST_MARKERS = [
    "phase10-closure-evidence.md",
    "phase10_closure_manifest.json",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c"
]

FREEZE_MAP_MARKERS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c"
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_STATUS=active",
    "PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json",
    "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L07",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L18",
    "PHASE10_LEDGER_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/",
    "PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE=zigux/tests/phase10_build.zig,zigux/tests/phase10_virtio_input_multitouch_preflight.zig,zigux/tests/phase10_virtio_mmio_queue_isolation.zig,scripts/zigux/check-phase10-harness-coverage.py,scripts/zigux/check-phase10-closure-inventory.py,scripts/zigux/validate-phase10.py,scripts/zigux/validate-phase10-closure.py,Documentation/zigux/phase10-closure-evidence.md,zigux/Makefile,.github/workflows/zigux-bootstrap.yml"
]

LEDGER_EXACT_ONCE_MARKERS = [
    "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "PHASE10_LEDGER_EXACT_CHECK_3=python3 scripts/zigux/check-phase10-harness-coverage.py"
]

MAKEFILE_MARKERS = [
    "phase10-validate:",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10-closure.py"
]

WORKFLOW_MARKERS = [
    "Self-test Phase 10 harness coverage checker",
    "Validate Phase 10 focused harness coverage",
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests"
]

BUILD_MARKERS = [
    "phase10-virtio-core-survey-tests",
    "phase10-virtio-ring-reset-reuse-tests",
    "phase10-virtio-input-multitouch-preflight-tests",
    "phase10-virtio-mmio-queue-isolation-tests",
    "phase10-virtio-ring-survey-tests",
    "phase10-virtio-input-survey-tests",
    "phase10-virtio-mmio-survey-tests"
]

CORE_SURVEY_MARKERS = [
    "phase10-config-generation-summary-helper",
    "phase10-config-delivery-disposition-helper",
    "phase10-core-probe-remove-lifecycle"
]

RING_SURVEY_MARKERS = [
    "phase10-broken-queue-recovery-helper",
    "phase10-mmio-interrupt-ack-helper",
    "phase10-mmio-lifecycle-and-irq-paths"
]

INPUT_SURVEY_MARKERS = [
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-registration-lifecycle"
]

MMIO_SURVEY_MARKERS = [
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
    "zigux/kernel/",
    "zigux/helpers/"
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def check_exact_count(
    missing: list[str], label: str, text: str, marker: str, expected: int = 1
) -> None:
    actual = text.count(marker)
    if actual != expected:
        missing.append(f"{label}:count:{marker}={actual}")


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return None
    for gap in gaps:
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []

    closure_text = read_text(root, "Documentation/zigux/phase10-closure-evidence.md")
    docs_readme_text = read_text(root, "Documentation/zigux/README.md")
    tests_readme_text = read_text(root, "zigux/tests/README.md")
    ledger_text = read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md")

    check_markers(missing, "closure", closure_text, CLOSURE_MARKERS)
    check_markers(missing, "docs_readme", docs_readme_text, DOCS_README_MARKERS)
    check_markers(missing, "tests_readme", tests_readme_text, TESTS_README_MARKERS)
    check_markers(missing, "checklist", read_text(root, "Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS)
    check_markers(missing, "freeze_map", read_text(root, "Documentation/zigux/freeze-map.md"), FREEZE_MAP_MARKERS)
    check_markers(missing, "ledger", ledger_text, LEDGER_MARKERS)
    check_markers(missing, "makefile", read_text(root, "zigux/Makefile"), MAKEFILE_MARKERS)
    check_markers(missing, "workflow", read_text(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)
    check_markers(missing, "phase10_build", read_text(root, "zigux/tests/phase10_build.zig"), BUILD_MARKERS)
    check_markers(missing, "core_survey", read_text(root, "Documentation/zigux/phase10-virtio-core-survey.md"), CORE_SURVEY_MARKERS)
    check_markers(missing, "ring_survey", read_text(root, "Documentation/zigux/phase10-virtio-ring-survey.md"), RING_SURVEY_MARKERS)
    check_markers(missing, "input_survey", read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md"), INPUT_SURVEY_MARKERS)
    check_markers(missing, "mmio_survey", read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md"), MMIO_SURVEY_MARKERS)

    for marker in CLOSURE_EXACT_ONCE_MARKERS:
        check_exact_count(missing, "closure", closure_text, marker)
    for marker in DOCS_README_EXACT_ONCE_MARKERS:
        check_exact_count(missing, "docs_readme", docs_readme_text, marker)
    for marker in LEDGER_EXACT_ONCE_MARKERS:
        check_exact_count(missing, "ledger", ledger_text, marker)

    closure_manifest = load_json(root, "zigux/tests/phase10_closure_manifest.json")
    if not isinstance(closure_manifest, dict):
        missing.append("closure_manifest:type")
    else:
        for key, expected in EXPECTED_CLOSURE_MANIFEST.items():
            if closure_manifest.get(key) != expected:
                missing.append(f"closure_manifest:{key}")

        expected_arrays = {
            "docs": [
                "Documentation/zigux/phase10-virtio-core-slice.md",
                "Documentation/zigux/phase10-virtio-core-survey.md",
                "Documentation/zigux/phase10-virtio-ring-slice.md",
                "Documentation/zigux/phase10-virtio-ring-survey.md",
                "Documentation/zigux/phase10-virtio-input-slice.md",
                "Documentation/zigux/phase10-virtio-input-module-slice.md",
                "Documentation/zigux/phase10-virtio-input-survey.md",
                "Documentation/zigux/phase10-virtio-mmio-slice.md",
                "Documentation/zigux/phase10-virtio-mmio-survey.md"
            ],
            "manifests": MANIFESTS,
            "drivers": DRIVERS,
            "tests": TESTS,
            "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "exact_checks": EXPECTED_EXACT_CHECKS,
        }
        for key, expected in expected_arrays.items():
            if closure_manifest.get(key) != expected:
                missing.append(f"closure_manifest:{key}")

        survey_provenance = closure_manifest.get("survey_provenance")
        if not isinstance(survey_provenance, dict):
            missing.append("closure_manifest:survey_provenance")
        else:
            if survey_provenance.get("source") != "manifest_derived":
                missing.append("closure_manifest:survey_provenance:source")
            if survey_provenance.get("lane_keys") != EXPECTED_SURVEY_LANE_KEYS:
                missing.append("closure_manifest:survey_provenance:lane_keys")
            if survey_provenance.get("surveyed_commits") != EXPECTED_SURVEYED_COMMITS:
                missing.append("closure_manifest:survey_provenance:surveyed_commits")

        lab_validation = closure_manifest.get("roadmap_parity_scoreboard")
        if not isinstance(lab_validation, dict):
            missing.append("closure_manifest:roadmap_parity_scoreboard")
        else:
            row = lab_validation.get("lab_only_driver_validation")
            if not isinstance(row, dict):
                missing.append("closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation")
            else:
                if row.get("status") != "starter_landed":
                    missing.append("closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:status")
                evidence = row.get("evidence")
                if not isinstance(evidence, list):
                    missing.append("closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence")
                else:
                    for path in [
                        "zigux/tests/phase10_build.zig",
                        "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
                        "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
                        "scripts/zigux/check-phase10-harness-coverage.py",
                        "scripts/zigux/check-phase10-closure-inventory.py",
                        "scripts/zigux/validate-phase10-closure.py"
                    ]:
                        if path not in evidence:
                            missing.append(f"closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation:evidence:{path}")

        if closure_manifest.get("landed_input_helper_evidence") != EXPECTED_LANDED_INPUT_HELPER_EVIDENCE:
            missing.append("closure_manifest:landed_input_helper_evidence")
        if closure_manifest.get("focused_harness_replays") != EXPECTED_FOCUSED_HARNESS_REPLAYS:
            missing.append("closure_manifest:focused_harness_replays")

    ring_manifest = load_json(root, "zigux/tests/phase10_virtio_ring_manifest.json")
    if not isinstance(ring_manifest, dict):
        missing.append("ring_manifest:type")
    else:
        ring_gap = find_gap(ring_manifest, "phase10-broken-queue-recovery-helper")
        if ring_gap is None:
            missing.append("ring_manifest:gap:phase10-broken-queue-recovery-helper")
        else:
            if ring_gap.get("status") != "starter_landed":
                missing.append("ring_manifest:gap_status:phase10-broken-queue-recovery-helper")
            why_now = str(ring_gap.get("why_now", ""))
            if "broken-queue recovery helper" not in why_now:
                missing.append("ring_manifest:gap_why:broken_queue_recovery_helper")
            if "teardown-safe queue reuse" not in why_now:
                missing.append("ring_manifest:gap_why:teardown_safe_queue_reuse")

    return [], missing


def write_fixture(root: Path) -> None:
    text_fixture = {
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_MARKERS) + "\nPHASE10_TEST_COUNT=11\n",
        "Documentation/zigux/README.md": "\n".join(DOCS_README_MARKERS) + "\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(CHECKLIST_MARKERS) + "\n",
        "Documentation/zigux/freeze-map.md": "\n".join(FREEZE_MAP_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-core-survey.md": "\n".join(CORE_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-ring-survey.md": "\n".join(RING_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(INPUT_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(MMIO_SURVEY_MARKERS) + "\n",
        "scripts/zigux/check-phase10-harness-coverage.py": "fixture\n",
        "scripts/zigux/check-phase10-closure-inventory.py": "fixture\n",
        "scripts/zigux/check-phase10-core-packet.py": "fixture\n",
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(LEDGER_MARKERS + LEDGER_EXACT_ONCE_MARKERS[3:4]) + "\n",
        "zigux/Makefile": "\n".join(MAKEFILE_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
    }

    closure_manifest = {
        **EXPECTED_CLOSURE_MANIFEST,
        "docs": [
            "Documentation/zigux/phase10-virtio-core-slice.md",
            "Documentation/zigux/phase10-virtio-core-survey.md",
            "Documentation/zigux/phase10-virtio-ring-slice.md",
            "Documentation/zigux/phase10-virtio-ring-survey.md",
            "Documentation/zigux/phase10-virtio-input-slice.md",
            "Documentation/zigux/phase10-virtio-input-module-slice.md",
            "Documentation/zigux/phase10-virtio-input-survey.md",
            "Documentation/zigux/phase10-virtio-mmio-slice.md",
            "Documentation/zigux/phase10-virtio-mmio-survey.md"
        ],
        "manifests": MANIFESTS,
        "drivers": DRIVERS,
        "tests": TESTS,
        "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
        "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
        "exact_checks": EXPECTED_EXACT_CHECKS,
        "survey_provenance": {
            "source": "manifest_derived",
            "lane_keys": EXPECTED_SURVEY_LANE_KEYS,
            "surveyed_commits": EXPECTED_SURVEYED_COMMITS
        },
        "roadmap_parity_scoreboard": {
            "lab_only_driver_validation": {
                "status": "starter_landed",
                "evidence": [
                    "zigux/tests/phase10_build.zig",
                    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
                    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
                    "scripts/zigux/check-phase10-harness-coverage.py",
                    "scripts/zigux/check-phase10-closure-inventory.py",
                    "scripts/zigux/validate-phase10.py",
                    "scripts/zigux/validate-phase10-closure.py",
                    "Documentation/zigux/phase10-closure-evidence.md",
                    "zigux/Makefile",
                    ".github/workflows/zigux-bootstrap.yml"
                ]
            }
        },
        "landed_input_helper_evidence": EXPECTED_LANDED_INPUT_HELPER_EVIDENCE,
        "focused_harness_replays": EXPECTED_FOCUSED_HARNESS_REPLAYS
    }

    ring_manifest = {
        "gaps": [
            {
                "id": "phase10-broken-queue-recovery-helper",
                "status": "starter_landed",
                "why_now": "The live ring slice now includes a tiny broken-queue recovery helper that reuses the drained reset discipline after a bounded broken-queue marker, so the survey records teardown-safe queue reuse without claiming transport-backed reset execution, descriptor reclamation, or IRQ delivery."
            }
        ]
    }

    json_fixture = {
        "zigux/tests/phase10_closure_manifest.json": closure_manifest,
        "zigux/tests/phase10_virtio_ring_manifest.json": ring_manifest,
        "zigux/tests/phase10_virtio_core_manifest.json": {},
        "zigux/tests/phase10_virtio_input_manifest.json": {},
        "zigux/tests/phase10_virtio_mmio_manifest.json": {}
    }

    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path in json_fixture:
            path.write_text(json.dumps(json_fixture[rel_path], indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(text_fixture.get(rel_path, "fixture\n"), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase10-closure-self-test:{label}:missing_files:{','.join(missing_files)}")
    if marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-closure-self-test:{label}:expected:{marker}:actual:{actual}")


def expect_missing_file(label: str, root: Path, rel_path: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"phase10-closure-self-test:{label}:unexpected_markers:{','.join(missing_markers)}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"phase10-closure-self-test:{label}:expected_file:{rel_path}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-closure-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        closure_manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["test_count"] = 9
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("test_count_guard", root, "closure_manifest:test_count")
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["tests"] = [path for path in TESTS if not path.endswith("phase10_virtio_mmio_queue_isolation.zig")]
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("tests_inventory_guard", root, "closure_manifest:tests")
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["survey_provenance"]["lane_keys"]["input"] = "P10-Y05"
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("survey_lane_guard", root, "closure_manifest:survey_provenance:lane_keys")
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["landed_input_helper_evidence"]["zigux/tests/phase10_virtio_input_manifest.json"] = [
            "phase10-virtio-input-capability-setup-helper",
            "phase10-virtio-input-multitouch-slot-helper",
            "phase10-virtio-input-teardown-observation-helper",
            "phase10-virtio-input-registration-preflight-helper",
            "phase10-virtio-input-queue-callback-preflight-helper"
        ]
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("landed_input_probe_preflight_guard", root, "closure_manifest:landed_input_helper_evidence")
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["focused_harness_replays"]["zigux/tests/phase10_virtio_mmio_queue_isolation.zig"] = [
            "phase10 mmio multi-queue isolation replay"
        ]
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("focused_harness_replays_guard", root, "closure_manifest:focused_harness_replays")
        write_fixture(root)

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace("phase10-virtio-input-multitouch-preflight-tests", "phase10-input-preflight-drift", 1),
            encoding="utf-8"
        )
        expect_missing_marker("build_marker_guard", root, "phase10_build:phase10-virtio-input-multitouch-preflight-tests")
        write_fixture(root)

        closure_note_path = root / "Documentation/zigux/phase10-closure-evidence.md"
        original_closure_note = closure_note_path.read_text(encoding="utf-8")
        closure_note_path.write_text(
            original_closure_note.replace("zigux/tests/phase10_virtio_mmio_queue_isolation.zig", "zigux/tests/phase10_virtio_mmio_queue_drift.zig", 1),
            encoding="utf-8"
        )
        expect_missing_marker("closure_note_queue_isolation_guard", root, "closure:zigux/tests/phase10_virtio_mmio_queue_isolation.zig")
        write_fixture(root)

        closure_note_path.write_text(
            original_closure_note.replace("PHASE10_SURVEY_INPUT_LANE=P10-L13", "PHASE10_SURVEY_INPUT_LANE=P10-Y05", 1),
            encoding="utf-8"
        )
        expect_missing_marker("closure_note_input_lane_guard", root, "closure:PHASE10_SURVEY_INPUT_LANE=P10-L13")
        write_fixture(root)

        closure_note_path.write_text(
            original_closure_note.replace(
                "PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py",
                "PHASE10_HARNESS_COVERAGE_GATE=missing",
                1
            ),
            encoding="utf-8"
        )
        expect_missing_marker("closure_note_harness_gate_guard", root, "closure:PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py")
        write_fixture(root)

        closure_note_path = root / "Documentation/zigux/phase10-closure-evidence.md"
        original_closure_note = closure_note_path.read_text(encoding="utf-8")
        closure_note_path.write_text(
            original_closure_note + "\nPHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py\n",
            encoding="utf-8"
        )
        expect_missing_marker(
            "closure_note_harness_gate_duplicate",
            root,
            "closure:count:PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py=2"
        )
        write_fixture(root)

        closure_note_path.write_text(
            original_closure_note + "\nPHASE10_TEST_COUNT=11\n",
            encoding="utf-8"
        )
        expect_missing_marker(
            "closure_note_test_count_duplicate",
            root,
            "closure:count:PHASE10_TEST_COUNT=11=2"
        )
        write_fixture(root)

        mmio_survey_path = root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        original_mmio_survey = mmio_survey_path.read_text(encoding="utf-8")
        mmio_survey_path.write_text(
            original_mmio_survey.replace(
                "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
                "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=drift",
                1
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "mmio_survey_reopen_guard",
            root,
            "mmio_survey:PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes"
        )
        write_fixture(root)

        docs_readme_path = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "python3 scripts/zigux/check-phase10-harness-coverage.py",
                "python3 scripts/zigux/check-phase10-harness-coverage-drift.py",
                1
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "docs_readme_harness_gate_guard",
            root,
            "docs_readme:python3 scripts/zigux/check-phase10-harness-coverage.py"
        )
        write_fixture(root)

        docs_readme_path = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "queue-handling and ready-state gate",
                "queue-handling gate drift",
                1,
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "docs_readme_ready_state_phrase_guard",
            root,
            "docs_readme:queue-handling and ready-state gate"
        )
        write_fixture(root)

        docs_readme_path = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme + "\nqueue-handling and ready-state gate\n",
            encoding="utf-8"
        )
        expect_missing_marker(
            "docs_readme_ready_state_phrase_duplicate",
            root,
            "docs_readme:count:queue-handling and ready-state gate=2"
        )
        write_fixture(root)

        docs_readme_path.write_text(
            original_docs_readme + "\npython3 scripts/zigux/check-phase10-harness-coverage.py\n",
            encoding="utf-8"
        )
        expect_missing_marker(
            "docs_readme_harness_gate_duplicate",
            root,
            "docs_readme:count:python3 scripts/zigux/check-phase10-harness-coverage.py=2"
        )
        write_fixture(root)

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "zigux-alpha/PHASE10_LEDGER_DRIFT.md",
                1,
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "tests_readme_closure_ledger_guard",
            root,
            "tests_readme:zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        )
        write_fixture(root)

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "scripts/zigux/check-phase10-core-packet.py",
                "scripts/zigux/check-phase10-core-packet-drift.py",
                1,
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "tests_readme_core_packet_guard",
            root,
            "tests_readme:scripts/zigux/check-phase10-core-packet.py",
        )
        write_fixture(root)

        tests_readme_path = root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
                "three survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
                1,
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "tests_readme_survey_manifest_guard",
            root,
            "tests_readme:four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
        )
        write_fixture(root)

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
                "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-Y05",
                1
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "ledger_input_lane_guard",
            root,
            "ledger:PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13"
        )
        write_fixture(root)

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace("PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig", "PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=drift", 1),
            encoding="utf-8"
        )
        expect_missing_marker("ledger_preflight_guard", root, "ledger:PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig")
        write_fixture(root)

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
                "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=drift",
                1
            ),
            encoding="utf-8"
        )
        expect_missing_marker(
            "ledger_harness_gate_guard",
            root,
            "ledger:PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py"
        )
        write_fixture(root)

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger + "\nPHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py\n",
            encoding="utf-8"
        )
        expect_missing_marker(
            "ledger_harness_gate_duplicate",
            root,
            "ledger:count:PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py=2"
        )
        write_fixture(root)

        ledger_path.write_text(
            original_ledger + "\nPHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig\n",
            encoding="utf-8"
        )
        expect_missing_marker(
            "ledger_queue_isolation_duplicate",
            root,
            "ledger:count:PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig=2"
        )
        write_fixture(root)

        ring_manifest_path = root / "zigux/tests/phase10_virtio_ring_manifest.json"
        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["gaps"][0]["why_now"] = "broken-queue recovery helper without the reuse claim"
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("ring_reuse_guard", root, "ring_manifest:gap_why:teardown_safe_queue_reuse")
        write_fixture(root)

        (root / "scripts/zigux/check-phase10-harness-coverage.py").unlink()
        expect_missing_file("harness_checker_file_guard", root, "scripts/zigux/check-phase10-harness-coverage.py")
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_mmio_queue_isolation.zig").unlink()
        expect_missing_file("queue_isolation_file_guard", root, "zigux/tests/phase10_virtio_mmio_queue_isolation.zig")

    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=26")
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
    + len(CLOSURE_EXACT_ONCE_MARKERS)
    + len(DOCS_README_MARKERS)
    + len(DOCS_README_EXACT_ONCE_MARKERS)
    + len(TESTS_README_MARKERS)
    + len(CHECKLIST_MARKERS)
    + len(FREEZE_MAP_MARKERS)
    + len(LEDGER_MARKERS)
    + len(LEDGER_EXACT_ONCE_MARKERS)
    + len(MAKEFILE_MARKERS)
    + len(WORKFLOW_MARKERS)
    + len(BUILD_MARKERS)
    + len(CORE_SURVEY_MARKERS)
    + len(RING_SURVEY_MARKERS)
    + len(INPUT_SURVEY_MARKERS)
    + len(MMIO_SURVEY_MARKERS)
)
print("PHASE10_CLOSURE_VALIDATION=pass")
print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE10_CLOSURE_REQUIRED_MARKER_COUNT={total_markers}")
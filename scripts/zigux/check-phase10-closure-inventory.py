#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

CLOSURE_NOTE = "Documentation/zigux/phase10-closure-evidence.md"
DOCS_ROOT = "Documentation/zigux/README.md"
CLOSURE_MANIFEST = "zigux/tests/phase10_closure_manifest.json"
CLOSURE_LEDGER = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"

EXPECTED_DOCS = [
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-ring-slice.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-slice.md",
    "Documentation/zigux/phase10-virtio-input-module-slice.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

EXPECTED_MANIFESTS = [
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

EXPECTED_DRIVERS = [
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_mmio.zig",
]

EXPECTED_TESTS = [
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
]

EXPECTED_ALLOWED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
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

EXPECTED_FREEZE_IN_C_ANCHORS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]

EXPECTED_STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

EXPECTED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase10-closure-inventory.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

EXPECTED_CROSS_PHASE_BOUNDARY = {
    "reference_samples": {
        "status": "out_of_scope",
        "evidence": [
            "samples/zigux",
            "zigux/tests/phase5_build.zig",
            "Documentation/zigux/review-checklist.md",
        ],
    },
    "runtime_starters": {
        "status": "out_of_scope",
        "evidence": [
            "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
            "Documentation/zigux/phase9-runtime-loader-substrate-plan.md",
            "zigux/tests/runtime_loader_gap_manifest.json",
            "zigux/tests/runtime_loader_gap_survey.zig",
            "zigux/tests/runtime_trace_events_manifest.json",
            "zigux/tests/phase9_build.zig",
            "zigux/kernel/runtime_loader.zig",
            "zigux/helpers/allocator_policy.zig",
            "samples/zigux/runtime_atomic64_loader.zig",
            "samples/zigux/runtime_bitmap_loader.zig",
            "samples/zigux/runtime_kretprobe_loader.zig",
            "samples/zigux/runtime_trace_events.zig",
        ],
    },
}

EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY = {
    "status": "separate_phase14_lane",
    "anchors": EXPECTED_STUDY_ONLY_ANCHORS,
    "required_phase14_evidence_features": [
        "boundary maps",
        "concurrency audits",
        "explicit stay-in-C decisions where warranted",
        "wrapper-first or study-only posture",
    ],
    "future_destinations": [
        "kernel/workqueue_bridge.zig",
        "kernel/trace/ring_buffer.zig",
    ],
    "future_destination_policy": (
        "kernel/trace/ring_buffer.zig remains a future destination only if years "
        "of evidence justify it"
    ),
}

EXPECTED_SCOREBOARD = {
    "virtqueue_wrappers": {
        "status": "starter_landed",
        "evidence": [
            "drivers/virtio/virtio_ring.zig",
            "zigux/tests/phase10_virtio_ring.zig",
            "zigux/tests/phase10_virtio_ring_manifest.json",
            "Documentation/zigux/phase10-virtio-ring-survey.md",
        ],
    },
    "mmio_wrappers": {
        "status": "starter_landed",
        "evidence": [
            "drivers/virtio/virtio_mmio.zig",
            "zigux/tests/phase10_virtio_mmio.zig",
            "zigux/tests/phase10_virtio_mmio_manifest.json",
            "Documentation/zigux/phase10-virtio-mmio-slice.md",
            "Documentation/zigux/phase10-virtio-mmio-survey.md",
        ],
    },
    "lab_only_driver_validation": {
        "status": "starter_landed",
        "evidence": [
            "zigux/tests/phase10_build.zig",
            "scripts/zigux/check-phase10-closure-inventory.py",
            "scripts/zigux/validate-phase10.py",
            "scripts/zigux/validate-phase10-closure.py",
            "Documentation/zigux/phase10-closure-evidence.md",
            "zigux/Makefile",
            ".github/workflows/zigux-bootstrap.yml",
        ],
    },
    "dual_implementations_for_risky_areas": {
        "status": "blocked_on_risky_transport",
        "evidence": [
            "Documentation/zigux/phase10-closure-evidence.md",
            "zigux/tests/phase10_virtio_ring_manifest.json",
            "zigux/tests/phase10_virtio_input_manifest.json",
            "zigux/tests/phase10_virtio_mmio_manifest.json",
        ],
    },
}

EXPECTED_SURVEY_PROVENANCE = {
    "source": "manifest_derived",
    "lane_keys": {
        "core": "P10-L03",
        "ring": "P10-L08",
        "input": "P10-L13",
        "mmio": "P10-L18",
    },
    "surveyed_commits": {
        "core": "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21",
        "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
        "input": "b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38",
        "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
    },
}

EXPECTED_LANDED_CORE_HELPERS = {
    "zigux/tests/phase10_virtio_core_manifest.json": [
        "phase10-config-generation-summary-helper",
        "phase10-config-delivery-disposition-helper",
    ]
}

EXPECTED_LANDED_RING_HELPERS = {
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
        "phase10-broken-queue-recovery-helper",
    ]
}

EXPECTED_LANDED_INPUT_HELPERS = {
    "zigux/tests/phase10_virtio_input_manifest.json": [
        "phase10-virtio-input-capability-setup-helper",
        "phase10-virtio-input-multitouch-slot-helper",
        "phase10-virtio-input-teardown-observation-helper",
        "phase10-virtio-input-registration-preflight-helper",
        "phase10-virtio-input-queue-callback-preflight-helper",
        "phase10-virtio-input-probe-preflight-helper",
    ]
}

EXPECTED_LANDED_MMIO_HELPERS = {
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

EXPECTED_BLOCKED_TRANSPORT_GAPS = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

EXPECTED_READY_TRANSPORT_FOLLOWUPS: dict[str, str] = {}

EXPECTED_MANIFEST_SCALARS = {
    "phase": "Phase 10",
    "status": "active",
    "tranche": "virtio-lab-bundle",
    "doc_count": len(EXPECTED_DOCS),
    "manifest_count": len(EXPECTED_MANIFESTS),
    "driver_count": len(EXPECTED_DRIVERS),
    "test_count": len(EXPECTED_TESTS),
    "has_virtio_mmio_zig": True,
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "review_checklist": "Documentation/zigux/review-checklist.md",
    "risky_transport_posture": "blocked_on_risky_transport",
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}

REQUIRED_FILES = [
    CLOSURE_NOTE,
    DOCS_ROOT,
    CLOSURE_MANIFEST,
    CLOSURE_LEDGER,
    *EXPECTED_DOCS,
    *EXPECTED_MANIFESTS,
    *EXPECTED_DRIVERS,
    *EXPECTED_TESTS,
]

CLOSURE_NOTE_MARKERS = [
    "PHASE10_DOC_COUNT=9",
    "PHASE10_MANIFEST_COUNT=4",
    "PHASE10_DRIVER_COUNT=4",
    "PHASE10_TEST_COUNT=9",
    "PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
    "PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/helpers/",
    "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
    "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
    "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no",
    "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
]

DOCS_ROOT_MARKERS = [
    "shared Phase 10 closure note plus the same nine published Phase 10 docs named by the shared closure packet",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py",
    "PHASE10_LEDGER_CORE_SLICE=Documentation/zigux/phase10-virtio-core-slice.md",
    "PHASE10_LEDGER_CORE_SURVEY=Documentation/zigux/phase10-virtio-core-survey.md",
    "PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md",
    "PHASE10_LEDGER_INPUT_SURVEY=Documentation/zigux/phase10-virtio-input-survey.md",
    "PHASE10_LEDGER_MMIO_SURVEY=Documentation/zigux/phase10-virtio-mmio-survey.md",
    "PHASE10_LEDGER_CORE_LAB_GATE=zigux/tests/phase10_virtio_core.zig",
    "PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig",
    "PHASE10_LEDGER_RING_SURVEY_GATE=zigux/tests/phase10_virtio_ring_survey.zig",
    "PHASE10_LEDGER_INPUT_SURVEY_GATE=zigux/tests/phase10_virtio_input_survey.zig",
    "PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig",
    "PHASE10_LEDGER_CORE_MANIFEST=zigux/tests/phase10_virtio_core_manifest.json",
    "PHASE10_LEDGER_RING_MANIFEST=zigux/tests/phase10_virtio_ring_manifest.json",
    "PHASE10_LEDGER_INPUT_MANIFEST=zigux/tests/phase10_virtio_input_manifest.json",
    "PHASE10_LEDGER_MMIO_MANIFEST=zigux/tests/phase10_virtio_mmio_manifest.json",
    "PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json",
    "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L03",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L08",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L18",
    "PHASE10_LEDGER_SURVEY_CORE_COMMIT=f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21",
    "PHASE10_LEDGER_SURVEY_RING_COMMIT=fe8a43ea2e186da0da152198b571dff57ea3c38c",
    "PHASE10_LEDGER_SURVEY_INPUT_COMMIT=b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38",
    "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=0945df1cf664a3582d7241f859183a13f3f04adb",
    "PHASE10_LEDGER_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/helpers/",
    "PHASE10_LEDGER_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
    "PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
    "PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no",
    "PHASE10_LEDGER_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
    "PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c",
    "PHASE10_LEDGER_MAKEFILE=zigux/Makefile",
    "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_EXACT_CHECK_3=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_LEDGER_EXACT_CHECK_4=make -C zigux phase10-validate",
    "PHASE10_LEDGER_EXACT_CHECK_5=make -C zigux phase10-test",
    "PHASE10_LEDGER_EXACT_CHECK_6=make -C zigux phase10",
    "PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths",
    "PHASE10_LEDGER_LANDED_MMIO_HELPERS=phase10-mmio-register-window-helper,phase10-mmio-queue-register-helper,phase10-mmio-queue-notify-helper,phase10-mmio-queue-address-helper,phase10-mmio-config-window-helper,phase10-mmio-config-write-helper,phase10-mmio-interrupt-ack-helper",
]


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
    check_markers(missing, "closure", read_text(root, CLOSURE_NOTE), CLOSURE_NOTE_MARKERS)
    check_markers(missing, "docs_root", read_text(root, DOCS_ROOT), DOCS_ROOT_MARKERS)
    check_markers(missing, "ledger", read_text(root, CLOSURE_LEDGER), LEDGER_MARKERS)

    manifest = load_json(root, CLOSURE_MANIFEST)
    if not isinstance(manifest, dict):
        return [], ["manifest:type"]

    for key, value in EXPECTED_MANIFEST_SCALARS.items():
        if manifest.get(key) != value:
            missing.append(f"manifest:{key}")

    expected_arrays = {
        "docs": EXPECTED_DOCS,
        "manifests": EXPECTED_MANIFESTS,
        "drivers": EXPECTED_DRIVERS,
        "tests": EXPECTED_TESTS,
        "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
        "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
        "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
        "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
        "exact_checks": EXPECTED_EXACT_CHECKS,
    }
    for key, value in expected_arrays.items():
        if manifest.get(key) != value:
            missing.append(f"manifest:{key}")

    expected_objects = {
        "roadmap_parity_scoreboard": EXPECTED_SCOREBOARD,
        "cross_phase_scoreboard_boundary": EXPECTED_CROSS_PHASE_BOUNDARY,
        "survey_provenance": EXPECTED_SURVEY_PROVENANCE,
        "landed_core_helper_evidence": EXPECTED_LANDED_CORE_HELPERS,
        "landed_ring_helper_evidence": EXPECTED_LANDED_RING_HELPERS,
        "landed_input_helper_evidence": EXPECTED_LANDED_INPUT_HELPERS,
        "landed_mmio_helper_evidence": EXPECTED_LANDED_MMIO_HELPERS,
        "blocked_transport_gaps": EXPECTED_BLOCKED_TRANSPORT_GAPS,
        "ready_transport_followups": EXPECTED_READY_TRANSPORT_FOLLOWUPS,
        "phase14_study_only_boundary": EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY,
    }
    for key, value in expected_objects.items():
        if manifest.get(key) != value:
            missing.append(f"manifest:{key}")

    return [], missing


def write_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == CLOSURE_NOTE:
            path.write_text("\n".join(CLOSURE_NOTE_MARKERS) + "\n", encoding="utf-8")
        elif rel_path == DOCS_ROOT:
            path.write_text("\n".join(DOCS_ROOT_MARKERS) + "\n", encoding="utf-8")
        elif rel_path == CLOSURE_LEDGER:
            path.write_text("\n".join(LEDGER_MARKERS) + "\n", encoding="utf-8")
        elif rel_path == CLOSURE_MANIFEST:
            manifest = dict(EXPECTED_MANIFEST_SCALARS)
            manifest.update(
                {
                    "docs": EXPECTED_DOCS,
                    "manifests": EXPECTED_MANIFESTS,
                    "drivers": EXPECTED_DRIVERS,
                    "tests": EXPECTED_TESTS,
                    "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
                    "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
                    "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
                    "roadmap_parity_scoreboard": EXPECTED_SCOREBOARD,
                    "cross_phase_scoreboard_boundary": EXPECTED_CROSS_PHASE_BOUNDARY,
                    "survey_provenance": EXPECTED_SURVEY_PROVENANCE,
                    "ready_transport_followups": EXPECTED_READY_TRANSPORT_FOLLOWUPS,
                    "landed_core_helper_evidence": EXPECTED_LANDED_CORE_HELPERS,
                    "landed_ring_helper_evidence": EXPECTED_LANDED_RING_HELPERS,
                    "landed_input_helper_evidence": EXPECTED_LANDED_INPUT_HELPERS,
                    "landed_mmio_helper_evidence": EXPECTED_LANDED_MMIO_HELPERS,
                    "blocked_transport_gaps": EXPECTED_BLOCKED_TRANSPORT_GAPS,
                    "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
                    "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
                    "phase14_study_only_boundary": EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY,
                    "exact_checks": EXPECTED_EXACT_CHECKS,
                }
            )
            path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        elif rel_path.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_files:{','.join(missing_files)}")
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected:{expected_marker}:actual:{actual}")


def expect_missing_file(label: str, root: Path, expected_file: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"{label}:unexpected_markers:{','.join(missing_markers)}")
    if expected_file not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"{label}:expected_file:{expected_file}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        (root / "Documentation/zigux/phase10-virtio-input-module-slice.md").unlink()
        expect_missing_file(
            "missing_input_module_slice_doc",
            root,
            "Documentation/zigux/phase10-virtio-input-module-slice.md",
        )
        write_fixture(root)

        (root / CLOSURE_LEDGER).unlink()
        expect_missing_file("missing_closure_ledger", root, CLOSURE_LEDGER)
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_core.zig").unlink()
        expect_missing_file(
            "missing_core_lab_gate",
            root,
            "zigux/tests/phase10_virtio_core.zig",
        )
        write_fixture(root)

        note_path = root / CLOSURE_NOTE
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
                "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_note_architecture_council_flag",
            root,
            "closure:PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
        )
        note_path.write_text(original_note, encoding="utf-8")

        docs_root_path = root / DOCS_ROOT
        original_docs_root = docs_root_path.read_text(encoding="utf-8")
        docs_root_path.write_text(
            original_docs_root.replace(
                "shared Phase 10 closure note plus the same nine published Phase 10 docs named by the shared closure packet",
                "shared Phase 10 closure note plus nine docs",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_root_phase10_summary_sentence",
            root,
            "docs_root:shared Phase 10 closure note plus the same nine published Phase 10 docs named by the shared closure packet",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")

        ledger_path = root / CLOSURE_LEDGER
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L18",
                "PHASE10_LEDGER_SURVEY_MMIO_LANE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_mmio_lane_marker",
            root,
            "ledger:PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L18",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md",
                "PHASE10_LEDGER_RING_SURVEY=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_ring_survey_marker",
            root,
            "ledger:PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_MMIO_MANIFEST=zigux/tests/phase10_virtio_mmio_manifest.json",
                "PHASE10_LEDGER_MMIO_MANIFEST=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_mmio_manifest_marker",
            root,
            "ledger:PHASE10_LEDGER_MMIO_MANIFEST=zigux/tests/phase10_virtio_mmio_manifest.json",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        manifest_path = root / CLOSURE_MANIFEST

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["docs"] = EXPECTED_DOCS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_docs_inventory", root, "manifest:docs")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["freeze_map"] = "Documentation/zigux/missing-freeze-map.md"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_freeze_map", root, "manifest:freeze_map")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = EXPECTED_TESTS[:-1] + ["zigux/tests/phase10_virtio_mmio_missing.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_tests_inventory", root, "manifest:tests")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_parity_scoreboard"]["mmio_wrappers"]["status"] = "ready_next"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_mmio_scoreboard_status",
            root,
            "manifest:roadmap_parity_scoreboard",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["surveyed_commits"]["mmio"] = "deadbeef"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_survey_provenance_commit",
            root,
            "manifest:survey_provenance",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["landed_mmio_helper_evidence"] = {
            "zigux/tests/phase10_virtio_mmio_manifest.json": [
                "phase10-mmio-register-window-helper"
            ]
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_landed_mmio_helpers",
            root,
            "manifest:landed_mmio_helper_evidence",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["landed_input_helper_evidence"] = {}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_landed_input_helpers",
            root,
            "manifest:landed_input_helper_evidence",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["blocked_transport_gaps"] = {
            "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-config-write-helper"
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_blocked_transport_gaps",
            root,
            "manifest:blocked_transport_gaps",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ready_transport_followups"] = {
            "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-interrupt-ack-helper"
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_ready_transport_followups",
            root,
            "manifest:ready_transport_followups",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["allowed_roadmap_destinations"] = ["drivers/virtio/*.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_allowed_roadmap_destinations",
            root,
            "manifest:allowed_roadmap_destinations",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["allowed_evidence_kinds"] = ["driver_local_lab_slices", "survey_manifests"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_allowed_evidence_kinds",
            root,
            "manifest:allowed_evidence_kinds",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["study_only_anchors"] = ["kernel/workqueue.c"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_study_only_anchors",
            root,
            "manifest:study_only_anchors",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["freeze_in_c_anchors"] = EXPECTED_FREEZE_IN_C_ANCHORS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_freeze_in_c_anchors",
            root,
            "manifest:freeze_in_c_anchors",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"] = EXPECTED_EXACT_CHECKS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_exact_checks", root, "manifest:exact_checks")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["phase14_study_only_boundary"]["anchors"] = ["kernel/workqueue.c"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_phase14_boundary",
            root,
            "manifest:phase14_study_only_boundary",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["cross_phase_scoreboard_boundary"]["reference_samples"]["status"] = "starter_landed"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_cross_phase_boundary",
            root,
            "manifest:cross_phase_scoreboard_boundary",
        )

    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST=pass")
    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST_CASE_COUNT=26")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_CLOSURE_INVENTORY=fail")
        print("MISSING_PHASE10_CLOSURE_INVENTORY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_INVENTORY_FILES_END")
        return 1
    if missing_markers:
        print("PHASE10_CLOSURE_INVENTORY=fail")
        print("MISSING_PHASE10_CLOSURE_INVENTORY_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CLOSURE_INVENTORY_MARKERS_END")
        return 1

    print("PHASE10_CLOSURE_INVENTORY=pass")
    print(f"PHASE10_CLOSURE_INVENTORY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE10_CLOSURE_INVENTORY_REQUIRED_GROUP_COUNT=17")
    return 0


if __name__ == "__main__":
    sys.exit(main())

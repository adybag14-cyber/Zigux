#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

CLOSURE_NOTE = "Documentation/zigux/phase10-closure-evidence.md"
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
    "future_destination_policy": "kernel/trace/ring_buffer.zig remains a future destination only if years of evidence justify it",
}

REQUIRED_FILES = [CLOSURE_NOTE, CLOSURE_MANIFEST, CLOSURE_LEDGER] + EXPECTED_DOCS + EXPECTED_MANIFESTS + EXPECTED_DRIVERS + EXPECTED_TESTS

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
    "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py",
    "PHASE10_LEDGER_CORE_LAB_GATE=zigux/tests/phase10_virtio_core.zig",
    "PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig",
    "PHASE10_LEDGER_RING_SURVEY_GATE=zigux/tests/phase10_virtio_ring_survey.zig",
    "PHASE10_LEDGER_INPUT_SURVEY_GATE=zigux/tests/phase10_virtio_input_survey.zig",
    "PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig",
    "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_EXACT_CHECK_3=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_LEDGER_EXACT_CHECK_4=make -C zigux phase10-validate",
    "PHASE10_LEDGER_EXACT_CHECK_5=make -C zigux phase10-test",
    "PHASE10_LEDGER_EXACT_CHECK_6=make -C zigux phase10",
    "PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    closure_note = read_text(root, CLOSURE_NOTE)
    for marker in CLOSURE_NOTE_MARKERS:
        if marker not in closure_note:
            missing.append(f"closure:{marker}")

    closure_ledger = read_text(root, CLOSURE_LEDGER)
    for marker in LEDGER_MARKERS:
        if marker not in closure_ledger:
            missing.append(f"ledger:{marker}")

    manifest = load_json(root, CLOSURE_MANIFEST)
    if not isinstance(manifest, dict):
        missing.append("manifest:type")
        return [], missing

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
    }
    for key, expected in expected_arrays.items():
        if manifest.get(key) != expected:
            missing.append(f"manifest:{key}")

    expected_counts = {
        "doc_count": len(EXPECTED_DOCS),
        "manifest_count": len(EXPECTED_MANIFESTS),
        "driver_count": len(EXPECTED_DRIVERS),
        "test_count": len(EXPECTED_TESTS),
    }
    for key, expected in expected_counts.items():
        if manifest.get(key) != expected:
            missing.append(f"manifest:{key}")

    if manifest.get("cross_phase_scoreboard_boundary") != EXPECTED_CROSS_PHASE_BOUNDARY:
        missing.append("manifest:cross_phase_scoreboard_boundary")

    if manifest.get("phase14_study_only_boundary") != EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY:
        missing.append("manifest:phase14_study_only_boundary")

    return [], missing


def write_fixture(root: Path) -> None:
    closure_note = "\n".join(CLOSURE_NOTE_MARKERS) + "\n"
    closure_ledger = "\n".join(LEDGER_MARKERS) + "\n"
    closure_manifest = {
        "phase": "Phase 10",
        "status": "active",
        "tranche": "virtio-lab-bundle",
        "doc_count": len(EXPECTED_DOCS),
        "manifest_count": len(EXPECTED_MANIFESTS),
        "driver_count": len(EXPECTED_DRIVERS),
        "test_count": len(EXPECTED_TESTS),
        "docs": EXPECTED_DOCS,
        "manifests": EXPECTED_MANIFESTS,
        "drivers": EXPECTED_DRIVERS,
        "tests": EXPECTED_TESTS,
        "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
        "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
        "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
        "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
        "cross_phase_scoreboard_boundary": EXPECTED_CROSS_PHASE_BOUNDARY,
        "phase14_study_only_boundary": EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY,
    }

    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == CLOSURE_NOTE:
            path.write_text(closure_note, encoding="utf-8")
        elif rel_path == CLOSURE_LEDGER:
            path.write_text(closure_ledger, encoding="utf-8")
        elif rel_path == CLOSURE_MANIFEST:
            path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        elif rel_path.endswith(".json"):
            path.write_text("{}\n", encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")


def expect_missing_file(label: str, root: Path, rel_path: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:unexpected_markers:{','.join(missing_markers)}"
        )
    if rel_path not in missing_files:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:expected_missing_file:{rel_path}:actual:{','.join(missing_files) if missing_files else 'none'}"
        )


def expect_missing_marker(label: str, root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:unexpected_files:{','.join(missing_files)}"
        )
    if marker not in missing_markers:
        raise SystemExit(
            f"phase10-closure-inventory-self-test:{label}:expected_marker:{marker}:actual:{','.join(missing_markers) if missing_markers else 'none'}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_inventory_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-closure-inventory-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        (root / "Documentation/zigux/phase10-virtio-input-module-slice.md").unlink()
        expect_missing_file(
            "missing_slice_doc",
            root,
            "Documentation/zigux/phase10-virtio-input-module-slice.md",
        )
        write_fixture(root)

        (root / CLOSURE_LEDGER).unlink()
        expect_missing_file("missing_closure_ledger", root, CLOSURE_LEDGER)
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_core.zig").unlink()
        expect_missing_file("missing_core_lab_gate", root, "zigux/tests/phase10_virtio_core.zig")
        write_fixture(root)

        closure_note_path = root / CLOSURE_NOTE
        original_closure_note = closure_note_path.read_text(encoding="utf-8")
        closure_note_path.write_text(
            original_closure_note.replace(
                "PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
                "PHASE10_CLOSURE_INVENTORY_GATE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_inventory_gate_marker",
            root,
            "closure:PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
        )
        closure_note_path.write_text(original_closure_note, encoding="utf-8")

        manifest_path = root / CLOSURE_MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["docs"] = EXPECTED_DOCS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_docs_inventory", root, "manifest:docs")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["manifests"] = EXPECTED_MANIFESTS[:-1] + ["zigux/tests/phase10_virtio_mmio_missing.json"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_manifest_inventory", root, "manifest:manifests")
        write_fixture(root)

        ledger_path = root / CLOSURE_LEDGER
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py",
                "PHASE10_LEDGER_INVENTORY_VALIDATE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_inventory_validator_marker",
            root,
            "ledger:PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py",
                "PHASE10_LEDGER_SHARED_VALIDATE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_shared_validator_marker",
            root,
            "ledger:PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig",
                "PHASE10_LEDGER_CORE_SURVEY_GATE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_core_survey_gate_marker",
            root,
            "ledger:PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig",
                "PHASE10_LEDGER_MMIO_SURVEY_GATE=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_mmio_survey_gate_marker",
            root,
            "ledger:PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py",
                "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10-closure.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_exact_check_order",
            root,
            "ledger:PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tests"] = EXPECTED_TESTS[:-1] + ["zigux/tests/phase10_virtio_mmio_missing.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_tests_inventory", root, "manifest:tests")
        write_fixture(root)

        closure_note_path.write_text(
            original_closure_note.replace(
                "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
                "PHASE10_ALLOWED_EVIDENCE_KINDS=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_allowed_evidence_marker",
            root,
            "closure:PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
        )
        write_fixture(root)

        closure_note_path.write_text(
            original_closure_note.replace(
                "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
                "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_forbidden_transport_claims_marker",
            root,
            "closure:PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
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
        manifest["drivers"] = EXPECTED_DRIVERS[:-1] + ["drivers/virtio/virtio_missing.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_driver_inventory", root, "manifest:drivers")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["cross_phase_scoreboard_boundary"]["reference_samples"]["status"] = "starter_landed"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_cross_phase_boundary",
            root,
            "manifest:cross_phase_scoreboard_boundary",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["phase14_study_only_boundary"]["required_phase14_evidence_features"].pop()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_phase14_boundary",
            root,
            "manifest:phase14_study_only_boundary",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["study_only_anchors"] = EXPECTED_STUDY_ONLY_ANCHORS[:-1]
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

    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST=pass")
    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST_CASE_COUNT=21")
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
    print("PHASE10_CLOSURE_INVENTORY_REQUIRED_GROUP_COUNT=9")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]


required_files = [
    ROOT / "Documentation" / "zigux" / "phase10-closure-evidence.md",
    ROOT / "Documentation" / "zigux" / "freeze-map.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-core-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-ring-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-ring-survey.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-module-slice.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-input-survey.md",
    ROOT / "Documentation" / "zigux" / "phase10-virtio-mmio-survey.md",
    ROOT / "scripts" / "zigux" / "validate-phase10-closure.py",
    ROOT / "zigux" / "Makefile",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
    ROOT / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md",
    ROOT / "drivers" / "virtio" / "virtio.zig",
    ROOT / "drivers" / "virtio" / "virtio_ring.zig",
    ROOT / "drivers" / "virtio" / "virtio_input.zig",
    ROOT / "zigux" / "tests" / "phase10_build.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_core.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_input.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_input_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_mmio_survey.zig",
    ROOT / "zigux" / "tests" / "phase10_virtio_ring_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_virtio_input_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_virtio_mmio_manifest.json",
    ROOT / "zigux" / "tests" / "phase10_closure_manifest.json",
]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE10_CLOSURE_FILES_END")
    sys.exit(1)

closure = (ROOT / "Documentation" / "zigux" / "phase10-closure-evidence.md").read_text(encoding="utf-8")
freeze_map = (ROOT / "Documentation" / "zigux" / "freeze-map.md").read_text(encoding="utf-8")
review_checklist = (ROOT / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
manifest = load_json(ROOT / "zigux" / "tests" / "phase10_closure_manifest.json")
ring_manifest = load_json(ROOT / "zigux" / "tests" / "phase10_virtio_ring_manifest.json")
input_manifest = load_json(ROOT / "zigux" / "tests" / "phase10_virtio_input_manifest.json")
mmio_manifest = load_json(ROOT / "zigux" / "tests" / "phase10_virtio_mmio_manifest.json")

required_closure_markers = [
    "PHASE10_STATUS=active",
    "PHASE10_TRANCHE=virtio-lab-bundle",
    "PHASE10_CLOSURE_EVIDENCE=verified",
    "PHASE10_DOC_COUNT=7",
    "PHASE10_MANIFEST_COUNT=3",
    "PHASE10_DRIVER_COUNT=3",
    "PHASE10_TEST_COUNT=6",
    "PHASE10_HAS_VIRTIO_MMIO_ZIG=no",
    "PHASE10_ROADMAP_PARITY_SCOREBOARD=present",
    "PHASE10_ROADMAP_SCOREBOARD_ROW_COUNT=4",
    "PHASE10_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed",
    "PHASE10_ROADMAP_MMIO_WRAPPERS=survey_backed_ready_next",
    "PHASE10_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
    "PHASE10_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
    "PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md",
    "PHASE10_FREEZE_BOUNDARY_STATUS=aligned",
    "PHASE10_FREEZE_STATUS_CHANGE_CLAIM=no",
    "PHASE10_FREEZE_IN_C_ANCHOR_COUNT=4",
    "PHASE10_STUDY_ONLY_ANCHOR_COUNT=2",
    "PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/helpers/",
    "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
    "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes",
    "PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no",
    "PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=virtio_mmio.zig,queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
    "Documentation/zigux/review-checklist.md",
    "phase10-mmio-register-window-helper",
    "phase10-virtio-input-registration-lifecycle",
    "phase10-mmio-lifecycle-and-irq-paths",
    "blocked_on_risky_transport",
]
required_freeze_map_markers = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "Architecture Council",
]
required_makefile_markers = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10-test:",
    "$(ZIG) build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
]
required_workflow_markers = [
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
]
required_checklist_markers = [
    "if the change is a Phase 10 virtio slice, do `Documentation/zigux/phase10-closure-evidence.md`, its roadmap parity scoreboard, the three Phase 10 survey manifests, and the shared `zigux/tests/phase10_build.zig` entrypoint still agree on the same bounded lab-only scope, exact replay commands, and explicit MMIO blocker posture?",
    "if the change widens a Phase 10 virtio transport-facing path, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-closure-evidence.md`, and the ring/input/MMIO survey manifests still keep the risky transport posture explicit instead of silently widening MMIO, queue setup or reset, IRQ, registration, DMA, or probe/remove lifecycle claims?",
]
missing_markers: list[str] = []
for marker in required_closure_markers:
    if marker not in closure:
        missing_markers.append(f"closure:{marker}")
for marker in required_freeze_map_markers:
    if marker not in freeze_map:
        missing_markers.append(f"freeze_map:{marker}")
for marker in required_makefile_markers:
    if marker not in makefile:
        missing_markers.append(f"make:{marker}")
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f"workflow:{marker}")
for marker in required_checklist_markers:
    if marker not in review_checklist:
        missing_markers.append(f"checklist:{marker}")

if manifest.get("phase") != "Phase 10":
    missing_markers.append("manifest:phase=Phase 10")
if manifest.get("status") != "active":
    missing_markers.append("manifest:status=active")
if manifest.get("tranche") != "virtio-lab-bundle":
    missing_markers.append("manifest:tranche=virtio-lab-bundle")
if manifest.get("doc_count") != 7:
    missing_markers.append(f'manifest:doc_count={manifest.get("doc_count")}')
if manifest.get("manifest_count") != 3:
    missing_markers.append(f'manifest:manifest_count={manifest.get("manifest_count")}')
if manifest.get("driver_count") != 3:
    missing_markers.append(f'manifest:driver_count={manifest.get("driver_count")}')
if manifest.get("test_count") != 6:
    missing_markers.append(f'manifest:test_count={manifest.get("test_count")}')
if manifest.get("has_virtio_mmio_zig") is not False:
    missing_markers.append(f'manifest:has_virtio_mmio_zig={manifest.get("has_virtio_mmio_zig")}')
if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
    missing_markers.append(f'manifest:freeze_map={manifest.get("freeze_map")}')
if manifest.get("freeze_boundary_status") != "aligned":
    missing_markers.append(
        f'manifest:freeze_boundary_status={manifest.get("freeze_boundary_status")} '
    )
if manifest.get("freeze_status_change_claimed") is not False:
    missing_markers.append(
        "manifest:freeze_status_change_claimed=true"
    )
if manifest.get("review_checklist") != "Documentation/zigux/review-checklist.md":
    missing_markers.append(f'manifest:review_checklist={manifest.get("review_checklist")}')
if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
    missing_markers.append(f'manifest:risky_transport_posture={manifest.get("risky_transport_posture")}')
expected_allowed_roadmap_destinations = [
    "drivers/virtio/*.zig",
    "zigux/helpers/",
]
if manifest.get("allowed_roadmap_destinations") != expected_allowed_roadmap_destinations:
    missing_markers.append("manifest:allowed_roadmap_destinations:mismatch")
expected_allowed_evidence_kinds = [
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
]
if manifest.get("allowed_evidence_kinds") != expected_allowed_evidence_kinds:
    missing_markers.append("manifest:allowed_evidence_kinds:mismatch")
if manifest.get("architecture_council_reopen_required") is not True:
    missing_markers.append("manifest:architecture_council_reopen_required=false")
if manifest.get("architecture_council_reopen_attached") is not False:
    missing_markers.append("manifest:architecture_council_reopen_attached=true")
expected_forbidden_transport_claims = [
    "virtio_mmio.zig",
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]
if manifest.get("forbidden_transport_claims") != expected_forbidden_transport_claims:
    missing_markers.append("manifest:forbidden_transport_claims:mismatch")

expected_freeze_in_c_anchors = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]
expected_study_only_anchors = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]
if manifest.get("freeze_in_c_anchors") != expected_freeze_in_c_anchors:
    missing_markers.append("manifest:freeze_in_c_anchors:mismatch")
if manifest.get("study_only_anchors") != expected_study_only_anchors:
    missing_markers.append("manifest:study_only_anchors:mismatch")

for field in ("docs", "manifests", "drivers", "tests", "exact_checks"):
    value = manifest.get(field)
    if not isinstance(value, list) or not value:
        missing_markers.append(f"manifest:{field}:expected_non_empty_list")
        continue
    for rel in value:
        if not isinstance(rel, str):
            missing_markers.append(f"manifest:{field}:non_string_entry")
            continue
        if field != "exact_checks" and not (ROOT / rel).exists():
            missing_markers.append(f"manifest_file:{rel}")

expected_exact_checks = {
    "python3 scripts/zigux/validate-phase10-closure.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
}
if set(manifest.get("exact_checks", [])) != expected_exact_checks:
    missing_markers.append("manifest:exact_checks:mismatch")

expected_roadmap_parity_scoreboard = {
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
        "status": "survey_backed_ready_next",
        "evidence": [
            "zigux/tests/phase10_virtio_mmio_manifest.json",
            "Documentation/zigux/phase10-virtio-mmio-survey.md",
        ],
    },
    "lab_only_driver_validation": {
        "status": "starter_landed",
        "evidence": [
            "zigux/tests/phase10_build.zig",
            "scripts/zigux/validate-phase10-closure.py",
            "Documentation/zigux/phase10-closure-evidence.md",
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
roadmap_parity_scoreboard = manifest.get("roadmap_parity_scoreboard")
if roadmap_parity_scoreboard != expected_roadmap_parity_scoreboard:
    missing_markers.append("manifest:roadmap_parity_scoreboard:mismatch")
else:
    for item in roadmap_parity_scoreboard.values():
        for rel in item.get("evidence", []):
            if not (ROOT / rel).exists():
                missing_markers.append(f"manifest:roadmap_parity_scoreboard:evidence_missing:{rel}")

ready_transport_followups = manifest.get("ready_transport_followups")
expected_ready_transport_followups = {
    "zigux/tests/phase10_virtio_ring_manifest.json": "phase10-mmio-register-window-helper",
}
if ready_transport_followups != expected_ready_transport_followups:
    missing_markers.append("manifest:ready_transport_followups:mismatch")

blocked_transport_gaps = manifest.get("blocked_transport_gaps")
expected_blocked_transport_gaps = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}
if blocked_transport_gaps != expected_blocked_transport_gaps:
    missing_markers.append("manifest:blocked_transport_gaps:mismatch")


def validate_lane_manifest(phase_manifest: object, lane_name: str) -> None:
    if not isinstance(phase_manifest, dict):
        missing_markers.append(f"{lane_name}:expected_object")
        return
    if phase_manifest.get("phase") != "Phase 10":
        missing_markers.append(f"{lane_name}:phase=Phase 10")
    anchor = phase_manifest.get("anchor")
    if not isinstance(anchor, str) or not anchor.startswith("drivers/virtio/"):
        missing_markers.append(f"{lane_name}:anchor=drivers/virtio/*")
    if anchor in expected_freeze_in_c_anchors or anchor in expected_study_only_anchors:
        missing_markers.append(f"{lane_name}:anchor:freeze_map_overlap")
    if phase_manifest.get("roadmap_destinations") != expected_allowed_roadmap_destinations:
        missing_markers.append(f"{lane_name}:roadmap_destinations:mismatch")


def has_gap_status(phase_manifest: object, gap_id: str, status: str) -> bool:
    if not isinstance(phase_manifest, dict):
        return False
    gaps = phase_manifest.get("gaps")
    if not isinstance(gaps, list):
        return False
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        if gap.get("id") == gap_id and gap.get("status") == status:
            return True
    return False


if not has_gap_status(ring_manifest, "phase10-mmio-register-window-helper", "ready_next"):
    missing_markers.append("phase10_virtio_ring_manifest:phase10-mmio-register-window-helper:ready_next")
if not has_gap_status(input_manifest, "phase10-virtio-input-registration-lifecycle", "blocked_on_risky_transport"):
    missing_markers.append("phase10_virtio_input_manifest:phase10-virtio-input-registration-lifecycle:blocked_on_risky_transport")
if not has_gap_status(mmio_manifest, "phase10-mmio-lifecycle-and-irq-paths", "blocked_on_risky_transport"):
    missing_markers.append("phase10_virtio_mmio_manifest:phase10-mmio-lifecycle-and-irq-paths:blocked_on_risky_transport")

validate_lane_manifest(ring_manifest, "phase10_virtio_ring_manifest")
validate_lane_manifest(input_manifest, "phase10_virtio_input_manifest")
validate_lane_manifest(mmio_manifest, "phase10_virtio_mmio_manifest")

if missing_markers:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_MARKERS_START")
    for marker in missing_markers:
        print(marker)
    print("MISSING_PHASE10_CLOSURE_MARKERS_END")
    sys.exit(1)

print("PHASE10_CLOSURE_VALIDATION=pass")
print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE10_CLOSURE_REQUIRED_MARKER_COUNT="
    f"{len(required_closure_markers) + len(required_freeze_map_markers) + len(required_makefile_markers) + len(required_workflow_markers)}"
)

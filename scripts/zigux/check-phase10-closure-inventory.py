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
HARNESS_CHECKER = "scripts/zigux/check-phase10-harness-coverage.py"
CORE_PACKET_CHECKER = "scripts/zigux/check-phase10-core-packet.py"
SHARED_VALIDATOR = "scripts/zigux/validate-phase10.py"
CLOSURE_VALIDATOR = "scripts/zigux/validate-phase10-closure.py"
INPUT_BLOCKER_BUILD = "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"

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
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
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
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10"
]

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
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
            "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
            "scripts/zigux/check-phase10-harness-coverage.py",
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
            "zigux/tests/phase10_virtio_core_manifest.json",
            "zigux/tests/phase10_virtio_ring_manifest.json",
            "zigux/tests/phase10_virtio_input_manifest.json",
            "zigux/tests/phase10_virtio_mmio_manifest.json",
        ],
    },
}

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
            "samples/zigux/runtime_trace_events_loader.zig",
            "samples/zigux/runtime_trace_events.zig",
        ],
    },
}

EXPECTED_SURVEY_PROVENANCE = {
    "source": "manifest_derived",
    "lane_keys": {
      "core": "P10-L01",
      "ring": "P10-L07",
      "input": "P10-L13",
      "mmio": "P10-L18",
    },
    "surveyed_commits": {
      "core": "d30cbe483a2f019ae797b309a29556bd58fe00d0",
      "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
      "input": "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21",
      "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
    },
}

EXPECTED_LANDED_CORE_HELPERS = {
    "zigux/tests/phase10_virtio_core_manifest.json": [
        "phase10-config-generation-summary-helper",
        "phase10-config-delivery-disposition-helper",
        "phase10-config-driver-toggle-guard-helper",
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
        "phase10-virtio-input-registration-blocker-helper",
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
        "phase10-mmio-probe-preflight-helper",
    ]
}

EXPECTED_FOCUSED_HARNESS_REPLAYS = {
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
        "phase10 ring drained-reset reuse replay"
    ],
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig": [
        "phase10 input multitouch-ready preflight replay"
    ],
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig": [
        "phase10 input registration-blocker replay build"
    ],
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig": [
        "phase10 mmio multi-queue isolation replay",
        "phase10 mmio reset clears legacy and modern queue address plans after queue selection changes",
    ],
}

EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY = {
    "status": "separate_phase14_lane",
    "anchors": [
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
    ],
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

EXPECTED_BLOCKED_TRANSPORT_GAPS = {
    "zigux/tests/phase10_virtio_core_manifest.json": "phase10-core-probe-remove-lifecycle",
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

EXPECTED_READY_TRANSPORT_FOLLOWUPS = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

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
    HARNESS_CHECKER,
    CORE_PACKET_CHECKER,
    SHARED_VALIDATOR,
    CLOSURE_VALIDATOR,
    INPUT_BLOCKER_BUILD,
    *EXPECTED_DOCS,
    *EXPECTED_MANIFESTS,
    *EXPECTED_DRIVERS,
    *EXPECTED_TESTS,
]

CLOSURE_NOTE_MARKERS = [
    "PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/",
    "PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
    "PHASE10_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_SURVEY_RING_LANE=P10-L07",
    "PHASE10_SURVEY_INPUT_LANE=P10-L13",
    "PHASE10_SURVEY_MMIO_LANE=P10-L18",
    "PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_CROSS_PHASE_SCOREBOARD_BOUNDARY=phase5_reference_samples_and_phase9_runtime_starters_do_not_count_as_phase10_virtio_driver_evidence",
    "zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
    "phase10-core-probe-remove-lifecycle",
    "phase10-virtio-input-registration-lifecycle",
    "phase10-mmio-lifecycle-and-irq-paths",
]

DOCS_ROOT_MARKERS = [
    "shared Phase 10 closure note plus the same nine published Phase 10 docs named by the shared closure packet",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "queue-handling and ready-state gate",
]

CLOSURE_NOTE_EXACT_ONCE_MARKERS = [
    "PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py",
]

DOCS_ROOT_EXACT_ONCE_MARKERS = [
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "queue-handling and ready-state gate",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L07",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L18",
    "PHASE10_LEDGER_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/",
    "PHASE10_LEDGER_INPUT_REGISTRATION_BLOCKER_BUILD=zigux/tests/phase10_virtio_input_registration_blocker_build.zig",
    "PHASE10_LEDGER_BLOCKERS=phase10-core-probe-remove-lifecycle,phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths",
    "PHASE10_LEDGER_LANDED_CORE_HELPERS=phase10-config-generation-summary-helper,phase10-config-delivery-disposition-helper,phase10-config-driver-toggle-guard-helper",
    "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_LEDGER_RING_RESET_REUSE_GATE=zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
]

LEDGER_EXACT_ONCE_MARKERS = [
    "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_LEDGER_RING_RESET_REUSE_GATE=zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
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

def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    closure_text = read_text(root, CLOSURE_NOTE)
    docs_root_text = read_text(root, DOCS_ROOT)
    ledger_text = read_text(root, CLOSURE_LEDGER)
    check_markers(missing, "closure", closure_text, CLOSURE_NOTE_MARKERS)
    check_markers(missing, "docs_root", docs_root_text, DOCS_ROOT_MARKERS)
    check_markers(missing, "ledger", ledger_text, LEDGER_MARKERS)
    for marker in CLOSURE_NOTE_EXACT_ONCE_MARKERS:
        check_exact_count(missing, "closure", closure_text, marker)
    for marker in DOCS_ROOT_EXACT_ONCE_MARKERS:
        check_exact_count(missing, "docs_root", docs_root_text, marker)
    for marker in LEDGER_EXACT_ONCE_MARKERS:
        check_exact_count(missing, "ledger", ledger_text, marker)

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
        "focused_harness_replays": EXPECTED_FOCUSED_HARNESS_REPLAYS,
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
        elif rel_path == HARNESS_CHECKER:
            path.write_text("fixture\n", encoding="utf-8")
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
                    "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
                    "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
                    "exact_checks": EXPECTED_EXACT_CHECKS,
                    "roadmap_parity_scoreboard": EXPECTED_SCOREBOARD,
                    "cross_phase_scoreboard_boundary": EXPECTED_CROSS_PHASE_BOUNDARY,
                    "survey_provenance": EXPECTED_SURVEY_PROVENANCE,
                    "landed_core_helper_evidence": EXPECTED_LANDED_CORE_HELPERS,
                    "landed_ring_helper_evidence": EXPECTED_LANDED_RING_HELPERS,
                    "landed_input_helper_evidence": EXPECTED_LANDED_INPUT_HELPERS,
                    "landed_mmio_helper_evidence": EXPECTED_LANDED_MMIO_HELPERS,
                    "focused_harness_replays": EXPECTED_FOCUSED_HARNESS_REPLAYS,
                    "blocked_transport_gaps": EXPECTED_BLOCKED_TRANSPORT_GAPS,
                    "ready_transport_followups": EXPECTED_READY_TRANSPORT_FOLLOWUPS,
                    "phase14_study_only_boundary": EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY,
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

def expect_missing_file(label: str, root: Path, rel_path: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_markers:
        raise SystemExit(f"{label}:unexpected_markers:{','.join(missing_markers)}")
    if rel_path not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(f"{label}:expected_file:{rel_path}:actual:{actual}")

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

        manifest_path = root / CLOSURE_MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ready_transport_followups"] = {}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("ready_followups_guard", root, "manifest:ready_transport_followups")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"] = [
            check
            for check in manifest["exact_checks"]
            if check != "python3 scripts/zigux/check-phase10-core-packet.py"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "core_packet_exact_check_guard",
            root,
            "manifest:exact_checks",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["cross_phase_scoreboard_boundary"]["runtime_starters"]["status"] = "starter_landed"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("runtime_boundary_guard", root, "manifest:cross_phase_scoreboard_boundary")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            path
            for path in manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if path != "scripts/zigux/check-phase10-harness-coverage.py"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "lab_validation_scoreboard_harness_evidence_guard",
            root,
            "manifest:roadmap_parity_scoreboard",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            path
            for path in manifest["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if path != "zigux/tests/phase10_virtio_input_registration_blocker_build.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "lab_validation_scoreboard_registration_blocker_build_guard",
            root,
            "manifest:roadmap_parity_scoreboard",
        )
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["lane_keys"]["core"] = "P10-L03"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("survey_lane_guard", root, "manifest:survey_provenance")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["survey_provenance"]["surveyed_commits"]["input"] = "0000000000000000000000000000000000000000"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("survey_commit_guard", root, "manifest:survey_provenance")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["landed_core_helper_evidence"] = {
            "zigux/tests/phase10_virtio_core_manifest.json": [
                "phase10-config-generation-summary-helper",
                "phase10-config-delivery-disposition-helper"
            ]
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("core_helper_guard", root, "manifest:landed_core_helper_evidence")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["focused_harness_replays"] = {
            "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
                "phase10 ring drained-reset reuse replay"
            ],
            "zigux/tests/phase10_virtio_input_multitouch_preflight.zig": [
                "phase10 input multitouch-ready preflight replay"
            ],
            "zigux/tests/phase10_virtio_mmio_queue_isolation.zig": [
                "phase10 mmio multi-queue isolation drift"
            ],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("focused_harness_replays_guard", root, "manifest:focused_harness_replays")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["phase14_study_only_boundary"]["future_destinations"] = [
            "kernel/workqueue_bridge.zig"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("phase14_study_only_boundary_guard", root, "manifest:phase14_study_only_boundary")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["allowed_roadmap_destinations"] = ["drivers/virtio/*.zig", "zigux/helpers/"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("allowed_destinations_guard", root, "manifest:allowed_roadmap_destinations")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"] = [
            check
            for check in manifest["exact_checks"]
            if check != "python3 scripts/zigux/validate-phase10.py"
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "shared_validator_exact_check_guard",
            root,
            "manifest:exact_checks",
        )
        write_fixture(root)

        note_path = root / CLOSURE_NOTE
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/",
                "PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/helpers/",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_note_destinations_guard",
            root,
            "closure:PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/",
        )
        write_fixture(root)

        note_path.write_text(
            original_note + "\nPHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "closure_note_harness_gate_duplicate",
            root,
            "closure:count:PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py=2",
        )
        write_fixture(root)

        docs_root_path = root / DOCS_ROOT
        original_docs_root = docs_root_path.read_text(encoding="utf-8")
        docs_root_path.write_text(
            original_docs_root + "\nqueue-handling and ready-state gate\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_root_ready_state_duplicate",
            root,
            "docs_root:count:queue-handling and ready-state gate=2",
        )
        write_fixture(root)

        ledger_path = root / CLOSURE_LEDGER
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
                "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L03",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_core_lane_guard",
            root,
            "ledger:PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
        )
        write_fixture(root)

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_RING_RESET_REUSE_GATE=zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                "PHASE10_LEDGER_RING_RESET_REUSE_GATE=drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_ring_gate_guard",
            root,
            "ledger:PHASE10_LEDGER_RING_RESET_REUSE_GATE=zigux/tests/phase10_virtio_ring_reset_reuse.zig",
        )
        write_fixture(root)

        ledger_path.write_text(
            original_ledger + "\nPHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_harness_validate_duplicate",
            root,
            "ledger:count:PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py=2",
        )
        write_fixture(root)

        ledger_path.write_text(
            original_ledger + "\nPHASE10_LEDGER_RING_RESET_REUSE_GATE=zigux/tests/phase10_virtio_ring_reset_reuse.zig\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_ring_gate_duplicate",
            root,
            "ledger:count:PHASE10_LEDGER_RING_RESET_REUSE_GATE=zigux/tests/phase10_virtio_ring_reset_reuse.zig=2",
        )
        write_fixture(root)

        ledger_path.write_text(
            original_ledger + "\nPHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_mmio_gate_duplicate",
            root,
            "ledger:count:PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig=2",
        )
        write_fixture(root)

        (root / CORE_PACKET_CHECKER).unlink()
        expect_missing_file("core_packet_checker_file_guard", root, CORE_PACKET_CHECKER)
        write_fixture(root)

        (root / SHARED_VALIDATOR).unlink()
        expect_missing_file("shared_validator_file_guard", root, SHARED_VALIDATOR)
        write_fixture(root)

        (root / CLOSURE_VALIDATOR).unlink()
        expect_missing_file("closure_validator_file_guard", root, CLOSURE_VALIDATOR)
        write_fixture(root)

        (root / INPUT_BLOCKER_BUILD).unlink()
        expect_missing_file("input_blocker_build_file_guard", root, INPUT_BLOCKER_BUILD)
        write_fixture(root)

        harness_checker_path = root / HARNESS_CHECKER
        harness_checker_path.unlink()
        missing_files, missing_markers = validate(root)
        if HARNESS_CHECKER not in missing_files or missing_markers:
            raise SystemExit("required_file_guard_failed")

    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST=pass")
    print("PHASE10_CLOSURE_INVENTORY_SELF_TEST_CASE_COUNT=25")
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
    print("PHASE10_CLOSURE_INVENTORY_REQUIRED_GROUP_COUNT=10")
    return 0

if __name__ == "__main__":
    sys.exit(main())

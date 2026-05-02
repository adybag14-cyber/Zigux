#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

CLOSURE_MARKERS = [
    "PHASE10_STATUS=active",
    "PHASE10_TRANCHE=virtio-lab-bundle",
    "PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py",
    "PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate",
    "PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test",
    "PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10",
    "phase10-mmio-interrupt-ack-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
]

DOCS_README_MARKERS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
]

CHECKLIST_MARKERS = [
    "phase10-closure-evidence.md",
    "phase10_closure_manifest.json",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

FREEZE_MAP_MARKERS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

LEDGER_MARKERS = [
    "PHASE10_LEDGER_STATUS=active",
    "PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json",
    "PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths",
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
    "PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed",
    "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE=drivers/virtio/virtio_ring.zig,zigux/tests/phase10_virtio_ring.zig,zigux/tests/phase10_virtio_ring_manifest.json,Documentation/zigux/phase10-virtio-ring-survey.md",
    "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed",
    "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-slice.md,Documentation/zigux/phase10-virtio-mmio-survey.md",
    "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
    "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE=zigux/tests/phase10_build.zig,scripts/zigux/check-phase10-closure-inventory.py,scripts/zigux/validate-phase10.py,scripts/zigux/validate-phase10-closure.py,Documentation/zigux/phase10-closure-evidence.md,zigux/Makefile,.github/workflows/zigux-bootstrap.yml",
    "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
    "PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md,zigux/tests/phase10_virtio_ring_manifest.json,zigux/tests/phase10_virtio_input_manifest.json,zigux/tests/phase10_virtio_mmio_manifest.json",
]

MAKEFILE_MARKERS = [
    "phase10-validate:",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
]

WORKFLOW_MARKERS = [
    "Validate Phase 10 closure evidence",
    "make -C zigux phase10-validate",
    "Run Phase 10 virtio helper tests",
]

BUILD_MARKERS = [
    "phase10-virtio-core-survey-tests",
    "phase10-virtio-ring-survey-tests",
    "phase10-virtio-input-survey-tests",
    "phase10-virtio-mmio-survey-tests",
]

CORE_SURVEY_MARKERS = [
    "phase10-config-generation-summary-helper",
    "phase10-config-delivery-disposition-helper",
    "phase10-core-probe-remove-lifecycle",
]

RING_SURVEY_MARKERS = [
    "phase10-broken-queue-recovery-helper",
    "phase10-mmio-interrupt-ack-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
]

INPUT_SURVEY_MARKERS = [
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-registration-lifecycle",
]

MMIO_SURVEY_MARKERS = [
    "phase10-mmio-config-write-helper",
    "phase10-mmio-interrupt-ack-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
]

EXPECTED_CLOSURE_MANIFEST = {
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

EXPECTED_CORE_HELPERS = [
    "phase10-config-generation-summary-helper",
    "phase10-config-delivery-disposition-helper",
]

EXPECTED_RING_HELPERS = [
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

EXPECTED_INPUT_HELPERS = [
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-probe-preflight-helper",
]

EXPECTED_MMIO_HELPERS = [
    "phase10-mmio-register-window-helper",
    "phase10-mmio-queue-register-helper",
    "phase10-mmio-queue-notify-helper",
    "phase10-mmio-queue-address-helper",
    "phase10-mmio-config-window-helper",
    "phase10-mmio-config-write-helper",
    "phase10-mmio-interrupt-ack-helper",
]

EXPECTED_BLOCKED_GAPS = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

EXPECTED_SCOREBOARD_STATUSES = {
    "virtqueue_wrappers": "starter_landed",
    "mmio_wrappers": "starter_landed",
    "lab_only_driver_validation": "starter_landed",
    "dual_implementations_for_risky_areas": "blocked_on_risky_transport",
}

EXPECTED_SURVEYED_COMMITS = {
    "core": "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21",
    "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
    "input": "b24f990e2e5504ac3ed4a1a0f1f97c41e06ddd38",
    "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
}

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

EXPECTED_PHASE14_BOUNDARY = {
    "status": "separate_phase14_lane",
    "anchors": ["kernel/workqueue.c", "kernel/trace/ring_buffer.c"],
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


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def check_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


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

    check_markers(missing, "closure", read_text(root, "Documentation/zigux/phase10-closure-evidence.md"), CLOSURE_MARKERS)
    check_markers(missing, "docs_readme", read_text(root, "Documentation/zigux/README.md"), DOCS_README_MARKERS)
    check_markers(missing, "checklist", read_text(root, "Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS)
    check_markers(missing, "freeze_map", read_text(root, "Documentation/zigux/freeze-map.md"), FREEZE_MAP_MARKERS)
    check_markers(missing, "ledger", read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"), LEDGER_MARKERS)
    check_markers(missing, "makefile", read_text(root, "zigux/Makefile"), MAKEFILE_MARKERS)
    check_markers(missing, "workflow", read_text(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)
    check_markers(missing, "phase10_build", read_text(root, "zigux/tests/phase10_build.zig"), BUILD_MARKERS)
    check_markers(
        missing,
        "core_survey",
        read_text(root, "Documentation/zigux/phase10-virtio-core-survey.md"),
        CORE_SURVEY_MARKERS,
    )
    check_markers(missing, "ring_survey", read_text(root, "Documentation/zigux/phase10-virtio-ring-survey.md"), RING_SURVEY_MARKERS)
    check_markers(missing, "input_survey", read_text(root, "Documentation/zigux/phase10-virtio-input-survey.md"), INPUT_SURVEY_MARKERS)
    check_markers(missing, "mmio_survey", read_text(root, "Documentation/zigux/phase10-virtio-mmio-survey.md"), MMIO_SURVEY_MARKERS)

    closure_manifest = load_json(root, "zigux/tests/phase10_closure_manifest.json")
    if not isinstance(closure_manifest, dict):
        missing.append("closure_manifest:type")
    else:
        for key, expected in EXPECTED_CLOSURE_MANIFEST.items():
            if closure_manifest.get(key) != expected:
                missing.append(f"closure_manifest:{key}")
        if closure_manifest.get("allowed_roadmap_destinations") != EXPECTED_ALLOWED_ROADMAP_DESTINATIONS:
            missing.append("closure_manifest:allowed_roadmap_destinations")
        if closure_manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
            missing.append("closure_manifest:allowed_evidence_kinds")
        if closure_manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
            missing.append("closure_manifest:forbidden_transport_claims")
        landed_core = closure_manifest.get("landed_core_helper_evidence")
        if landed_core != {"zigux/tests/phase10_virtio_core_manifest.json": EXPECTED_CORE_HELPERS}:
            missing.append("closure_manifest:landed_core_helper_evidence")
        landed_ring = closure_manifest.get("landed_ring_helper_evidence")
        if landed_ring != {"zigux/tests/phase10_virtio_ring_manifest.json": EXPECTED_RING_HELPERS}:
            missing.append("closure_manifest:landed_ring_helper_evidence")
        landed_input = closure_manifest.get("landed_input_helper_evidence")
        if landed_input != {"zigux/tests/phase10_virtio_input_manifest.json": EXPECTED_INPUT_HELPERS}:
            missing.append("closure_manifest:landed_input_helper_evidence")
        landed_mmio = closure_manifest.get("landed_mmio_helper_evidence")
        if landed_mmio != {"zigux/tests/phase10_virtio_mmio_manifest.json": EXPECTED_MMIO_HELPERS}:
            missing.append("closure_manifest:landed_mmio_helper_evidence")
        if closure_manifest.get("blocked_transport_gaps") != EXPECTED_BLOCKED_GAPS:
            missing.append("closure_manifest:blocked_transport_gaps")
        if closure_manifest.get("exact_checks") != EXPECTED_EXACT_CHECKS:
            missing.append("closure_manifest:exact_checks")
        if closure_manifest.get("cross_phase_scoreboard_boundary") != EXPECTED_CROSS_PHASE_BOUNDARY:
            missing.append("closure_manifest:cross_phase_scoreboard_boundary")
        if closure_manifest.get("phase14_study_only_boundary") != EXPECTED_PHASE14_BOUNDARY:
            missing.append("closure_manifest:phase14_study_only_boundary")
        scoreboard = closure_manifest.get("roadmap_parity_scoreboard")
        if not isinstance(scoreboard, dict):
            missing.append("closure_manifest:roadmap_parity_scoreboard")
        else:
            for key, expected in EXPECTED_SCOREBOARD_STATUSES.items():
                entry = scoreboard.get(key)
                if not isinstance(entry, dict) or entry.get("status") != expected:
                    missing.append(f"closure_manifest:roadmap_parity_scoreboard:{key}")
        survey_provenance = closure_manifest.get("survey_provenance")
        if not isinstance(survey_provenance, dict):
            missing.append("closure_manifest:survey_provenance")
        else:
            if survey_provenance.get("source") != "manifest_derived":
                missing.append("closure_manifest:survey_provenance:source")
            lane_keys = survey_provenance.get("lane_keys")
            if lane_keys != {"core": "P10-L03", "ring": "P10-L08", "input": "P10-L13", "mmio": "P10-L18"}:
                missing.append("closure_manifest:survey_provenance:lane_keys")
            surveyed_commits = survey_provenance.get("surveyed_commits")
            if surveyed_commits != EXPECTED_SURVEYED_COMMITS:
                missing.append("closure_manifest:survey_provenance:surveyed_commits")

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
    texts = {
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_MARKERS) + "\n",
        "Documentation/zigux/README.md": "\n".join(DOCS_README_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(CHECKLIST_MARKERS) + "\n",
        "Documentation/zigux/freeze-map.md": "\n".join(FREEZE_MAP_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-core-survey.md": "\n".join(CORE_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-ring-survey.md": "\n".join(RING_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-input-survey.md": "\n".join(INPUT_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(MMIO_SURVEY_MARKERS) + "\n",
        "scripts/zigux/check-phase10-closure-inventory.py": "fixture\n",
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(LEDGER_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKEFILE_MARKERS) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "\n".join(WORKFLOW_MARKERS) + "\n",
        "zigux/tests/phase10_build.zig": "\n".join(BUILD_MARKERS) + "\n",
        "zigux/tests/phase10_virtio_core_manifest.json": "{}\n",
        "zigux/tests/phase10_virtio_input_manifest.json": "{}\n",
        "zigux/tests/phase10_virtio_mmio_manifest.json": "{}\n",
    }

    closure_manifest = {
        **EXPECTED_CLOSURE_MANIFEST,
        "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
        "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
        "roadmap_parity_scoreboard": {
            key: {"status": value} for key, value in EXPECTED_SCOREBOARD_STATUSES.items()
        },
        "cross_phase_scoreboard_boundary": EXPECTED_CROSS_PHASE_BOUNDARY,
        "phase14_study_only_boundary": EXPECTED_PHASE14_BOUNDARY,
        "exact_checks": EXPECTED_EXACT_CHECKS,
        "survey_provenance": {
            "source": "manifest_derived",
            "lane_keys": {"core": "P10-L03", "ring": "P10-L08", "input": "P10-L13", "mmio": "P10-L18"},
            "surveyed_commits": EXPECTED_SURVEYED_COMMITS,
        },
        "landed_core_helper_evidence": {
            "zigux/tests/phase10_virtio_core_manifest.json": EXPECTED_CORE_HELPERS,
        },
        "landed_ring_helper_evidence": {
            "zigux/tests/phase10_virtio_ring_manifest.json": EXPECTED_RING_HELPERS,
        },
        "landed_input_helper_evidence": {
            "zigux/tests/phase10_virtio_input_manifest.json": EXPECTED_INPUT_HELPERS,
        },
        "landed_mmio_helper_evidence": {
            "zigux/tests/phase10_virtio_mmio_manifest.json": EXPECTED_MMIO_HELPERS,
        },
        "blocked_transport_gaps": EXPECTED_BLOCKED_GAPS,
    }

    ring_manifest = {
        "gaps": [
            {
                "id": "phase10-broken-queue-recovery-helper",
                "status": "starter_landed",
                "why_now": "The live ring slice now includes a tiny broken-queue recovery helper that reuses the drained reset discipline after a bounded broken-queue marker, so the survey records teardown-safe queue reuse without claiming transport-backed reset execution, descriptor reclamation, or IRQ delivery.",
            }
        ]
    }

    json_texts = {
        "zigux/tests/phase10_closure_manifest.json": closure_manifest,
        "zigux/tests/phase10_virtio_ring_manifest.json": ring_manifest,
    }

    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path in json_texts:
            path.write_text(json.dumps(json_texts[rel_path], indent=2) + "\n", encoding="utf-8")
        else:
            path.write_text(texts.get(rel_path, "fixture\n"), encoding="utf-8")


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
        closure_manifest["landed_ring_helper_evidence"] = {
            "zigux/tests/phase10_virtio_ring_manifest.json": EXPECTED_RING_HELPERS[:-1]
        }
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "ring_helper_guard",
            root,
            "closure_manifest:landed_ring_helper_evidence",
        )
        write_fixture(root)

        docs_readme_path = root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "zigux-alpha/PHASE10_CLOSURE_LEDGER_DRIFT.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_root_closure_ledger_marker",
            root,
            "docs_readme:zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        )
        write_fixture(root)

        core_survey_path = root / "Documentation/zigux/phase10-virtio-core-survey.md"
        original_core_survey = core_survey_path.read_text(encoding="utf-8")
        core_survey_path.write_text(
            original_core_survey.replace(
                "phase10-config-delivery-disposition-helper",
                "phase10-config-delivery-marker-drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "core_survey_marker_guard",
            root,
            "core_survey:phase10-config-delivery-disposition-helper",
        )
        write_fixture(root)

        build_path = root / "zigux/tests/phase10_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                "phase10-virtio-core-survey-tests",
                "phase10-core-survey-build-drift",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "core_survey_build_guard",
            root,
            "phase10_build:phase10-virtio-core-survey-tests",
        )
        write_fixture(root)

        (root / "zigux/tests/phase10_virtio_core_survey.zig").unlink()
        expect_missing_file(
            "core_survey_gate_file_guard",
            root,
            "zigux/tests/phase10_virtio_core_survey.zig",
        )
        write_fixture(root)

        ring_manifest_path = root / "zigux/tests/phase10_virtio_ring_manifest.json"
        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["gaps"][0]["status"] = "blocked_on_risky_transport"
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "broken_queue_status_guard",
            root,
            "ring_manifest:gap_status:phase10-broken-queue-recovery-helper",
        )
        write_fixture(root)

        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["gaps"][0]["why_now"] = "broken-queue recovery helper without the reuse claim"
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "broken_queue_why_guard",
            root,
            "ring_manifest:gap_why:teardown_safe_queue_reuse",
        )
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["exact_checks"] = EXPECTED_EXACT_CHECKS[:-1]
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "exact_checks_guard",
            root,
            "closure_manifest:exact_checks",
        )
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["blocked_transport_gaps"] = {
            "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
            "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-config-write-helper",
        }
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "blocked_transport_gap_guard",
            root,
            "closure_manifest:blocked_transport_gaps",
        )
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["survey_provenance"]["source"] = "repo_scan"
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "survey_provenance_source_guard",
            root,
            "closure_manifest:survey_provenance:source",
        )
        write_fixture(root)

        closure_manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        closure_manifest["survey_provenance"]["surveyed_commits"]["ring"] = "0000000000000000000000000000000000000000"
        closure_manifest_path.write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "surveyed_commits_guard",
            root,
            "closure_manifest:survey_provenance:surveyed_commits",
        )
        write_fixture(root)

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        original_ledger = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-slice.md,Documentation/zigux/phase10-virtio-mmio-survey.md",
                "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-survey.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_mmio_scoreboard_evidence_guard",
            root,
            "ledger:PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-slice.md,Documentation/zigux/phase10-virtio-mmio-survey.md",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

        ledger_path.write_text(
            original_ledger.replace(
                "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=0945df1cf664a3582d7241f859183a13f3f04adb",
                "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=0000000000000000000000000000000000000000",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "ledger_mmio_commit_guard",
            root,
            "ledger:PHASE10_LEDGER_SURVEY_MMIO_COMMIT=0945df1cf664a3582d7241f859183a13f3f04adb",
        )
        ledger_path.write_text(original_ledger, encoding="utf-8")

    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=13")
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
    + len(BUILD_MARKERS)
    + len(CORE_SURVEY_MARKERS)
    + len(RING_SURVEY_MARKERS)
    + len(INPUT_SURVEY_MARKERS)
    + len(MMIO_SURVEY_MARKERS)
)
print("PHASE10_CLOSURE_VALIDATION=pass")
print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE10_CLOSURE_REQUIRED_MARKER_COUNT={total_markers}")
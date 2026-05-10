#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path(__file__).resolve().parent

CORE_MANIFEST_PATH = "zigux/tests/phase10_virtio_core_manifest.json"
RING_MANIFEST_PATH = "zigux/tests/phase10_virtio_ring_manifest.json"
INPUT_MANIFEST_PATH = "zigux/tests/phase10_virtio_input_manifest.json"
MMIO_MANIFEST_PATH = "zigux/tests/phase10_virtio_mmio_manifest.json"
CLOSURE_MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py"

EXPECTED_SHARED_FIELDS = [
    "freeze_map",
    "freeze_boundary_status",
    "freeze_status_change_claimed",
    "risky_transport_posture",
    "allowed_evidence_kinds",
    "forbidden_transport_claims",
    "architecture_council_reopen_required",
    "architecture_council_reopen_attached",
]

EXPECTED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
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

EXPECTED_COMPONENTS = {
    "core": {
        "manifest_path": CORE_MANIFEST_PATH,
        "lane_key": "P10-L01",
        "surveyed_commit": "31e9763eea7964dad7085d1a24bc098b4af49789",
        "blocked_gap": "phase10-core-probe-remove-lifecycle",
        "landed_helper_key": "landed_core_helper_evidence",
        "landed_helper_evidence": [
            "phase10-queue-shape-bookkeeping-helper",
            "phase10-config-generation-bookkeeping-helper",
            "phase10-interrupt-ack-bookkeeping-helper",
            "phase10-lifecycle-guard-bookkeeping-helper",
            "phase10-driver-validation-narrowing-helper",
            "phase10-reset-replay-bookkeeping-helper",
        ],
    },
    "ring": {
        "manifest_path": RING_MANIFEST_PATH,
        "lane_key": "P10-L07",
        "surveyed_commit": "bdfe88e865b94387b3c3bd41ca98054c452f78b9",
        "landed_helper_key": "landed_ring_helper_evidence",
        "landed_helper_evidence": [
            "phase10-virtqueue-shape-helper",
            "phase10-used-buffer-polling-helper",
            "phase10-callback-enable-helper",
            "phase10-callback-delay-helper",
            "phase10-notify-prepare-helper",
            "phase10-notification-data-summary-helper",
            "phase10-broken-queue-poll-guard",
            "phase10-queue-reset-helper",
            "phase10-queue-reset-readiness-helper",
            "phase10-ring-verify-replay",
            "phase10-virtio-ring-slice-note",
        ],
    },
    "input": {
        "manifest_path": INPUT_MANIFEST_PATH,
        "lane_key": "P10-L13",
        "surveyed_commit": "aab20011833191e49e31bcdf2a0fcfcd4c0451d0",
        "blocked_gap": "phase10-virtio-input-registration-lifecycle",
        "ready_followup": "phase10-virtio-input-registration-lifecycle",
        "landed_helper_key": "landed_input_helper_evidence",
        "landed_helper_evidence": [
            "phase10-virtio-input-capability-setup-helper",
            "phase10-virtio-input-multitouch-slot-helper",
            "phase10-virtio-input-teardown-observation-helper",
            "phase10-virtio-input-registration-preflight-helper",
            "phase10-virtio-input-queue-callback-preflight-helper",
            "phase10-virtio-input-status-drain-helper",
        ],
    },
    "mmio": {
        "manifest_path": MMIO_MANIFEST_PATH,
        "lane_key": "P10-L10",
        "surveyed_commit": "84f90e23ad1c28ae345905d5293a8c5395f37d43",
        "blocked_gap": "phase10-mmio-lifecycle-and-irq-paths",
        "ready_followup": "phase10-mmio-lifecycle-and-irq-paths",
        "landed_helper_key": "landed_mmio_helper_evidence",
        "landed_helper_evidence": [
            "phase10-mmio-register-window-helper",
            "phase10-mmio-queue-size-helper",
            "phase10-mmio-feature-word-selector-helper",
            "phase10-mmio-feature-negotiation-summary-helper",
            "phase10-mmio-config-window-helper",
            "phase10-mmio-config-write-plan-helper",
            "phase10-mmio-transport-identity-helper",
            "phase10-mmio-probe-preflight-helper",
            "phase10-mmio-config-write-disposition-helper",
            "phase10-mmio-selected-queue-readiness-helper",
            "phase10-mmio-configured-queue-coverage-helper",
        ],
    },
}

EXPECTED_RING_WRAPPER_EVIDENCE = [
    "drivers/virtio/virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    RING_MANIFEST_PATH,
    "Documentation/zigux/phase10-virtio-ring-survey.md",
]

EXPECTED_MMIO_WRAPPER_EVIDENCE = [
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    MMIO_MANIFEST_PATH,
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

EXPECTED_LAB_VALIDATION_EVIDENCE = [
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "drivers/virtio/virtio_verify.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "scripts/zigux/check-phase10-core-packet.py",
    "scripts/zigux/check-phase10-ring-packet.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

EXPECTED_DUAL_IMPL_EVIDENCE = [
    "Documentation/zigux/phase10-closure-evidence.md",
    CORE_MANIFEST_PATH,
    RING_MANIFEST_PATH,
    INPUT_MANIFEST_PATH,
    MMIO_MANIFEST_PATH,
]

EXPECTED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/check-phase10-ring-packet.py",
    "python3 scripts/zigux/check-phase10-input-packet.py",
    "python3 scripts/zigux/check-phase10-mmio-packet.py",
    FREEZE_BOUNDARY_CHECK,
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]


def read_json(root: Path, rel_path: str) -> dict:
    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    required_paths = [CLOSURE_MANIFEST_PATH] + [component["manifest_path"] for component in EXPECTED_COMPONENTS.values()]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            missing_files.append(rel_path)
    if missing_files:
        return missing_files, missing_markers

    closure_manifest = read_json(root, CLOSURE_MANIFEST_PATH)
    manifests = {
        name: read_json(root, component["manifest_path"])
        for name, component in EXPECTED_COMPONENTS.items()
    }

    for manifest in manifests.values():
        if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
            missing_markers.append(f"{manifest['lane_key']}:roadmap_destinations")
        for key in EXPECTED_SHARED_FIELDS:
            if closure_manifest.get(key) != manifest.get(key):
                missing_markers.append(f"shared_field:{key}:{manifest['lane_key']}")

    if closure_manifest.get("allowed_roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing_markers.append("closure_manifest:allowed_roadmap_destinations")
    if closure_manifest.get("freeze_in_c_anchors") != EXPECTED_FREEZE_IN_C_ANCHORS:
        missing_markers.append("closure_manifest:freeze_in_c_anchors")
    if closure_manifest.get("study_only_anchors") != EXPECTED_STUDY_ONLY_ANCHORS:
        missing_markers.append("closure_manifest:study_only_anchors")

    phase14_boundary = closure_manifest.get("phase14_study_only_boundary")
    if not isinstance(phase14_boundary, dict):
        missing_markers.append("closure_manifest:phase14_study_only_boundary")
    else:
        if phase14_boundary.get("status") != EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY["status"]:
            missing_markers.append("closure_manifest:phase14_study_only_boundary.status")
        if phase14_boundary.get("anchors") != EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY["anchors"]:
            missing_markers.append("closure_manifest:phase14_study_only_boundary.anchors")
        if phase14_boundary.get("required_phase14_evidence_features") != EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY["required_phase14_evidence_features"]:
            missing_markers.append("closure_manifest:phase14_study_only_boundary.required_phase14_evidence_features")
        if phase14_boundary.get("future_destinations") != EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY["future_destinations"]:
            missing_markers.append("closure_manifest:phase14_study_only_boundary.future_destinations")
        if phase14_boundary.get("future_destination_policy") != EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY["future_destination_policy"]:
            missing_markers.append("closure_manifest:phase14_study_only_boundary.future_destination_policy")

    scoreboard = closure_manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        missing_markers.append("closure_manifest:roadmap_parity_scoreboard")
    else:
        ring_wrappers = scoreboard.get("virtqueue_wrappers")
        if not isinstance(ring_wrappers, dict):
            missing_markers.append("closure_manifest:virtqueue_wrappers")
        else:
            if ring_wrappers.get("status") != "starter_landed":
                missing_markers.append("closure_manifest:virtqueue_wrappers.status")
            if ring_wrappers.get("evidence") != EXPECTED_RING_WRAPPER_EVIDENCE:
                missing_markers.append("closure_manifest:virtqueue_wrappers.evidence")

        mmio_wrappers = scoreboard.get("mmio_wrappers")
        if not isinstance(mmio_wrappers, dict):
            missing_markers.append("closure_manifest:mmio_wrappers")
        else:
            if mmio_wrappers.get("status") != "starter_landed":
                missing_markers.append("closure_manifest:mmio_wrappers.status")
            if mmio_wrappers.get("evidence") != EXPECTED_MMIO_WRAPPER_EVIDENCE:
                missing_markers.append("closure_manifest:mmio_wrappers.evidence")

        lab_validation = scoreboard.get("lab_only_driver_validation")
        if not isinstance(lab_validation, dict):
            missing_markers.append("closure_manifest:lab_only_driver_validation")
        else:
            if lab_validation.get("status") != "starter_landed":
                missing_markers.append("closure_manifest:lab_only_driver_validation.status")
            if lab_validation.get("evidence") != EXPECTED_LAB_VALIDATION_EVIDENCE:
                missing_markers.append("closure_manifest:lab_only_driver_validation.evidence")

        dual_impl = scoreboard.get("dual_implementations_for_risky_areas")
        if not isinstance(dual_impl, dict):
            missing_markers.append("closure_manifest:dual_implementations_for_risky_areas")
        else:
            if dual_impl.get("status") != manifests["mmio"].get("risky_transport_posture"):
                missing_markers.append("closure_manifest:dual_implementations_for_risky_areas.status")
            if dual_impl.get("evidence") != EXPECTED_DUAL_IMPL_EVIDENCE:
                missing_markers.append("closure_manifest:dual_implementations_for_risky_areas.evidence")

    survey_provenance = closure_manifest.get("survey_provenance")
    if not isinstance(survey_provenance, dict):
        missing_markers.append("closure_manifest:survey_provenance")
    else:
        lane_keys = survey_provenance.get("lane_keys")
        if not isinstance(lane_keys, dict):
            missing_markers.append("closure_manifest:survey_provenance.lane_keys")
        else:
            for name, component in EXPECTED_COMPONENTS.items():
                if lane_keys.get(name) != manifests[name].get("lane_key"):
                    missing_markers.append(f"closure_manifest:survey_provenance.lane_keys.{name}")
                if lane_keys.get(name) != component["lane_key"]:
                    missing_markers.append(f"closure_manifest:survey_provenance.expected_lane_key.{name}")

        surveyed_commits = survey_provenance.get("surveyed_commits")
        if not isinstance(surveyed_commits, dict):
            missing_markers.append("closure_manifest:survey_provenance.surveyed_commits")
        else:
            for name, component in EXPECTED_COMPONENTS.items():
                if surveyed_commits.get(name) != manifests[name].get("surveyed_commit"):
                    missing_markers.append(f"closure_manifest:survey_provenance.surveyed_commits.{name}")
                if surveyed_commits.get(name) != component["surveyed_commit"]:
                    missing_markers.append(f"closure_manifest:survey_provenance.expected_surveyed_commit.{name}")

    blocked_transport_gaps = closure_manifest.get("blocked_transport_gaps")
    if not isinstance(blocked_transport_gaps, dict):
        missing_markers.append("closure_manifest:blocked_transport_gaps")
    else:
        for name, component in EXPECTED_COMPONENTS.items():
            blocker = component.get("blocked_gap")
            if blocker and blocked_transport_gaps.get(component["manifest_path"]) != blocker:
                missing_markers.append(f"closure_manifest:blocked_transport_gaps.{name}")

    ready_transport_followups = closure_manifest.get("ready_transport_followups")
    if not isinstance(ready_transport_followups, dict):
        missing_markers.append("closure_manifest:ready_transport_followups")
    else:
        for name, component in EXPECTED_COMPONENTS.items():
            followup = component.get("ready_followup")
            if followup and ready_transport_followups.get(component["manifest_path"]) != followup:
                missing_markers.append(f"closure_manifest:ready_transport_followups.{name}")

    for component in EXPECTED_COMPONENTS.values():
        landed = closure_manifest.get(component["landed_helper_key"])
        if not isinstance(landed, dict):
            missing_markers.append(f"closure_manifest:{component['landed_helper_key']}")
            continue
        if landed.get(component["manifest_path"]) != component["landed_helper_evidence"]:
            missing_markers.append(f"closure_manifest:{component['landed_helper_key']}.{component['manifest_path']}")

    exact_checks = closure_manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        missing_markers.append("closure_manifest:exact_checks")
    else:
        for marker in EXPECTED_EXACT_CHECKS:
            if marker not in exact_checks:
                missing_markers.append(f"closure_manifest:exact_checks:{marker}")
        if exact_checks.count(FREEZE_BOUNDARY_CHECK) != 1:
            missing_markers.append("closure_manifest:exact_checks:freeze_boundary_count")

    return missing_files, missing_markers


def write_json(target: Path, payload: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def baseline_manifest(lane_key: str, surveyed_commit: str, anchor: str) -> dict:
    return {
        "lane_key": lane_key,
        "phase": "Phase 10",
        "surveyed_commit": surveyed_commit,
        "anchor": anchor,
        "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "risky_transport_posture": "blocked_on_risky_transport",
        "allowed_evidence_kinds": [
            "driver_local_lab_slices",
            "survey_manifests",
            "shared_validation_gates",
        ],
        "forbidden_transport_claims": [
            "queue_setup_reset_paths",
            "irq_parity",
            "dma_paths",
            "input_registration_lifecycle",
            "probe_remove_lifecycle",
        ],
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
    }


def baseline_manifests() -> tuple[dict[str, dict], dict]:
    manifests = {
        "core": baseline_manifest("P10-L01", "31e9763eea7964dad7085d1a24bc098b4af49789", "drivers/virtio/virtio.c"),
        "ring": baseline_manifest("P10-L07", "bdfe88e865b94387b3c3bd41ca98054c452f78b9", "drivers/virtio/virtio_ring.c"),
        "input": baseline_manifest("P10-L13", "aab20011833191e49e31bcdf2a0fcfcd4c0451d0", "drivers/virtio/virtio_input.c"),
        "mmio": baseline_manifest("P10-L10", "84f90e23ad1c28ae345905d5293a8c5395f37d43", "drivers/virtio/virtio_mmio.c"),
    }
    closure_manifest = {
        "freeze_map": manifests["mmio"]["freeze_map"],
        "freeze_boundary_status": manifests["mmio"]["freeze_boundary_status"],
        "freeze_status_change_claimed": manifests["mmio"]["freeze_status_change_claimed"],
        "risky_transport_posture": manifests["mmio"]["risky_transport_posture"],
        "allowed_roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": manifests["mmio"]["allowed_evidence_kinds"],
        "architecture_council_reopen_required": manifests["mmio"]["architecture_council_reopen_required"],
        "architecture_council_reopen_attached": manifests["mmio"]["architecture_council_reopen_attached"],
        "forbidden_transport_claims": manifests["mmio"]["forbidden_transport_claims"],
        "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
        "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
        "phase14_study_only_boundary": EXPECTED_PHASE14_STUDY_ONLY_BOUNDARY,
        "roadmap_parity_scoreboard": {
            "virtqueue_wrappers": {
                "status": "starter_landed",
                "evidence": EXPECTED_RING_WRAPPER_EVIDENCE,
            },
            "mmio_wrappers": {
                "status": "starter_landed",
                "evidence": EXPECTED_MMIO_WRAPPER_EVIDENCE,
            },
            "lab_only_driver_validation": {
                "status": "starter_landed",
                "evidence": EXPECTED_LAB_VALIDATION_EVIDENCE,
            },
            "dual_implementations_for_risky_areas": {
                "status": manifests["mmio"]["risky_transport_posture"],
                "evidence": EXPECTED_DUAL_IMPL_EVIDENCE,
            },
        },
        "survey_provenance": {
            "source": "manifest_derived",
            "lane_keys": {name: manifest["lane_key"] for name, manifest in manifests.items()},
            "surveyed_commits": {name: manifest["surveyed_commit"] for name, manifest in manifests.items()},
        },
        "ready_transport_followups": {
            INPUT_MANIFEST_PATH: EXPECTED_COMPONENTS["input"]["ready_followup"],
            MMIO_MANIFEST_PATH: EXPECTED_COMPONENTS["mmio"]["ready_followup"],
        },
        "blocked_transport_gaps": {
            CORE_MANIFEST_PATH: EXPECTED_COMPONENTS["core"]["blocked_gap"],
            INPUT_MANIFEST_PATH: EXPECTED_COMPONENTS["input"]["blocked_gap"],
            MMIO_MANIFEST_PATH: EXPECTED_COMPONENTS["mmio"]["blocked_gap"],
        },
        "landed_core_helper_evidence": {
            CORE_MANIFEST_PATH: EXPECTED_COMPONENTS["core"]["landed_helper_evidence"],
        },
        "landed_ring_helper_evidence": {
            RING_MANIFEST_PATH: EXPECTED_COMPONENTS["ring"]["landed_helper_evidence"],
        },
        "landed_input_helper_evidence": {
            INPUT_MANIFEST_PATH: EXPECTED_COMPONENTS["input"]["landed_helper_evidence"],
        },
        "landed_mmio_helper_evidence": {
            MMIO_MANIFEST_PATH: EXPECTED_COMPONENTS["mmio"]["landed_helper_evidence"],
        },
        "exact_checks": EXPECTED_EXACT_CHECKS,
    }
    return manifests, closure_manifest


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_freeze_boundary_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        manifests, closure_manifest = baseline_manifests()
        for name, component in EXPECTED_COMPONENTS.items():
            write_json(tmp_root / component["manifest_path"], manifests[name])
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-mmio-freeze-boundary-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        (tmp_root / MMIO_MANIFEST_PATH).unlink()
        missing_files, _ = validate(tmp_root)
        if MMIO_MANIFEST_PATH not in missing_files:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_missing_mmio_manifest")
        write_json(tmp_root / MMIO_MANIFEST_PATH, manifests["mmio"])

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["freeze_boundary_status"] = "drifted"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "shared_field:freeze_boundary_status:P10-L01" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_freeze_status_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["survey_provenance"]["lane_keys"]["core"] = "P10-L18"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:survey_provenance.lane_keys.core" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_core_lane_key_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["survey_provenance"]["surveyed_commits"]["mmio"] = "phase10-mmio-drifted-commit"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:survey_provenance.surveyed_commits.mmio" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_mmio_surveyed_commit_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            "zigux/tests/phase10_build.zig"
        ]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:lab_only_driver_validation.evidence" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_lab_validation_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["landed_core_helper_evidence"][CORE_MANIFEST_PATH] = ["phase10-queue-shape-bookkeeping-helper"]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if f"closure_manifest:landed_core_helper_evidence.{CORE_MANIFEST_PATH}" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_core_helper_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["landed_ring_helper_evidence"][RING_MANIFEST_PATH] = ["phase10-virtqueue-shape-helper"]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if f"closure_manifest:landed_ring_helper_evidence.{RING_MANIFEST_PATH}" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_ring_helper_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["blocked_transport_gaps"][CORE_MANIFEST_PATH] = "phase10-core-ready-now"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:blocked_transport_gaps.core" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_blocked_gap_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["ready_transport_followups"][MMIO_MANIFEST_PATH] = "phase10-mmio-ready-now"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:ready_transport_followups.mmio" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_ready_followup_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["exact_checks"] = [FREEZE_BOUNDARY_CHECK, FREEZE_BOUNDARY_CHECK]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:exact_checks:freeze_boundary_count" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_freeze_boundary_count_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["exact_checks"] = ["python3 scripts/zigux/check-phase10-core-packet.py"]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:exact_checks:python3 scripts/zigux/check-phase10-ring-packet.py" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_exact_check_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["freeze_in_c_anchors"] = ["kernel/sched/core.c"]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:freeze_in_c_anchors" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_freeze_in_c_anchor_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["study_only_anchors"] = ["kernel/workqueue.c"]
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:study_only_anchors" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_study_only_anchor_marker_missing")
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, closure_manifest)

        drifted = json.loads((tmp_root / CLOSURE_MANIFEST_PATH).read_text(encoding="utf-8"))
        drifted["phase14_study_only_boundary"]["future_destination_policy"] = "phase14 drifted"
        write_json(tmp_root / CLOSURE_MANIFEST_PATH, drifted)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:phase14_study_only_boundary.future_destination_policy" not in missing_markers:
            raise SystemExit("phase10-mmio-freeze-boundary-self-test:expected_phase14_boundary_policy_marker_missing")

    print("PHASE10_MMIO_FREEZE_BOUNDARY=pass")
    print("PHASE10_MMIO_FREEZE_BOUNDARY_SELF_TEST_CASE_COUNT=14")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate shared Phase 10 closure-manifest parity against the shipped core, ring, input, and MMIO manifests."
    )
    parser.add_argument("--self-test", action="store_true", help="Run synthetic drift checks against temporary manifests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_MMIO_FREEZE_BOUNDARY=fail")
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_MMIO_FREEZE_BOUNDARY=fail")
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_MMIO_FREEZE_BOUNDARY_MARKERS_END")
        return 1

    print("PHASE10_MMIO_FREEZE_BOUNDARY=pass")
    print("PHASE10_MMIO_FREEZE_BOUNDARY_REQUIRED_FILE_COUNT=5")
    return 0


if __name__ == "__main__":
    sys.exit(main())

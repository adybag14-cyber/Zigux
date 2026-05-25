#!/usr/bin/env python3
"""Fail closed when Phase 10 closure-manifest summary counts or route anchors drift."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
LEDGER_PATH = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"

COUNT_FIELDS = {
    "doc_count": "docs",
    "manifest_count": "manifests",
    "driver_count": "drivers",
    "test_count": "tests",
}

REQUIRED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase10-bootstrap-route.py",
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "python3 scripts/zigux/check-phase10-ring-packet.py",
    "python3 scripts/zigux/check-phase10-input-packet.py",
    "python3 scripts/zigux/check-phase10-mmio-packet.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "python3 scripts/zigux/check-phase10-closure-manifest-counts.py",
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

REQUIRED_RING_SCOREBOARD_EVIDENCE = [
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_publish_readiness.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
]

REQUIRED_MMIO_SCOREBOARD_EVIDENCE = [
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

REQUIRED_LAB_VALIDATION_EVIDENCE = [
    "scripts/zigux/check-phase10-core-packet.py",
    "scripts/zigux/check-phase10-closure-manifest-counts.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE = [
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
]

REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE = [
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
]

REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE = [
    "samples/zigux",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/review-checklist.md",
]

REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE = [
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
]

REQUIRED_CORE_LAB_VALIDATION_EVIDENCE = [
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "drivers/virtio/virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
]

REQUIRED_LANDED_CORE_HELPER_EVIDENCE = {
    "zigux/tests/phase10_virtio_core_manifest.json": [
        "phase10-queue-shape-bookkeeping-helper",
        "phase10-config-generation-bookkeeping-helper",
        "phase10-interrupt-ack-bookkeeping-helper",
        "phase10-lifecycle-guard-bookkeeping-helper",
        "phase10-driver-validation-narrowing-helper",
        "phase10-core-attribute-summary-helper",
        "phase10-reset-replay-bookkeeping-helper",
    ],
}

REQUIRED_FOCUSED_HARNESS_REPLAYS = {
    "zigux/tests/phase10_virtio_driver_id.zig": [
        "phase10 driver-id review path replay",
    ],
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig": [
        "phase10 core interrupt-compound-ack replay",
    ],
    "zigux/tests/phase10_virtio_core_reset_queue.zig": [
        "phase10 core reset-queue replay",
    ],
    "drivers/virtio/virtio_ring_publish_readiness.zig": [
        "phase10 ring publish-readiness wrapper replay",
    ],
    "zigux/tests/phase10_virtio_mmio.zig": [
        "phase10 mmio lab replay",
    ],
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig": [
        "phase10 mmio apply-observation replay",
    ],
    "zigux/tests/phase10_virtio_mmio_survey.zig": [
        "phase10 mmio survey replay",
    ],
}

REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

REQUIRED_SURVEY_PROVENANCE_SOURCE = "manifest_derived"
REQUIRED_SURVEY_LANE_KEYS = {
    "core": "P10-L01",
    "ring": "P10-L10",
    "input": "P10-L22",
    "mmio": "P10-L11",
}
REQUIRED_SURVEY_COMMITS = {
    "core": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "ring": "0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
    "input": "ee789f026f11a0c5c70ded9a868979cdf4f55393",
    "mmio": "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
}

LEDGER_STATUS_FIELDS = {
    "virtqueue_wrappers": "PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS",
    "mmio_wrappers": "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS",
    "lab_only_driver_validation": "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION",
    "dual_implementations_for_risky_areas": "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS",
}

LEDGER_EVIDENCE_FIELDS = {
    "virtqueue_wrappers": "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE",
    "mmio_wrappers": "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE",
    "lab_only_driver_validation": "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE",
    "dual_implementations_for_risky_areas": "PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE",
}

REQUIRED_CORE_BLOCKED_TRANSPORT_PATH = "zigux/tests/phase10_virtio_core_manifest.json"
REQUIRED_CORE_BLOCKED_TRANSPORT_GAP = "phase10-core-probe-remove-lifecycle"
REQUIRED_INPUT_READY_TRANSPORT_PATH = "zigux/tests/phase10_virtio_input_manifest.json"
REQUIRED_INPUT_READY_TRANSPORT_GAP = "phase10-virtio-input-registration-lifecycle"
REQUIRED_MMIO_READY_TRANSPORT_PATH = "zigux/tests/phase10_virtio_mmio_manifest.json"
REQUIRED_MMIO_READY_TRANSPORT_GAP = "phase10-mmio-lifecycle-and-irq-paths"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_expected_ledger_lines(manifest: dict) -> list[str]:
    scoreboard = manifest.get("roadmap_parity_scoreboard")
    provenance = manifest.get("survey_provenance")
    if not isinstance(scoreboard, dict) or not isinstance(provenance, dict):
        return []

    lane_keys = provenance.get("lane_keys")
    surveyed_commits = provenance.get("surveyed_commits")
    if not isinstance(lane_keys, dict) or not isinstance(surveyed_commits, dict):
        return []

    lines = [f"PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE={MANIFEST_PATH}"]
    source = provenance.get("source")
    if isinstance(source, str) and source:
        lines.append(f"PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE={source}")

    for key in ("core", "ring", "input", "mmio"):
        lane = lane_keys.get(key)
        if isinstance(lane, str) and lane:
            lines.append(f"PHASE10_LEDGER_SURVEY_{key.upper()}_LANE={lane}")
        commit = surveyed_commits.get(key)
        if isinstance(commit, str) and commit:
            lines.append(f"PHASE10_LEDGER_SURVEY_{key.upper()}_COMMIT={commit}")

    for key, ledger_key in LEDGER_STATUS_FIELDS.items():
        row = scoreboard.get(key)
        if not isinstance(row, dict):
            continue
        status = row.get("status")
        if isinstance(status, str) and status:
            lines.append(f"{ledger_key}={status}")

    for key, ledger_key in LEDGER_EVIDENCE_FIELDS.items():
        row = scoreboard.get(key)
        if not isinstance(row, dict):
            continue
        evidence = row.get("evidence")
        if isinstance(evidence, list) and evidence:
            lines.append(f"{ledger_key}={','.join(evidence)}")

    return lines


def collect_ledger_drift(manifest: dict, ledger_text: str) -> list[str]:
    drift: list[str] = []
    expected_lines = build_expected_ledger_lines(manifest)
    if not expected_lines:
        drift.append("ledger:expected_lines:missing")
        return drift

    for line in expected_lines:
        if line not in ledger_text:
            drift.append(f"ledger:{line}")

    return drift


def collect_drift(manifest: dict) -> list[str]:
    drift: list[str] = []
    for count_field, list_field in COUNT_FIELDS.items():
        listed = manifest.get(list_field)
        if not isinstance(listed, list) or not listed:
            drift.append(f"{list_field}:missing")
            continue

        count = manifest.get(count_field)
        if not isinstance(count, int):
            drift.append(f"{count_field}:missing")
            continue

        actual = len(listed)
        if count != actual:
            drift.append(f"{count_field}:{count}!=len({list_field}):{actual}")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list) or not exact_checks:
        drift.append("exact_checks:missing")
        return drift

    indexes: list[int] = []
    for item in REQUIRED_EXACT_CHECKS:
        if item not in exact_checks:
            drift.append(f"exact_checks:{item!r}:missing")
            continue
        indexes.append(exact_checks.index(item))

    if len(indexes) == len(REQUIRED_EXACT_CHECKS) and indexes != sorted(indexes):
        drift.append("exact_checks:closure_route:out_of_order")

    scoreboard = manifest.get("roadmap_parity_scoreboard", {})
    if not isinstance(scoreboard, dict):
        drift.append("roadmap_parity_scoreboard:missing")
        return drift

    virtqueue_wrappers = scoreboard.get("virtqueue_wrappers")
    if not isinstance(virtqueue_wrappers, dict):
        drift.append("roadmap_parity_scoreboard:virtqueue_wrappers:missing")
        return drift

    ring_evidence = virtqueue_wrappers.get("evidence")
    if not isinstance(ring_evidence, list) or not ring_evidence:
        drift.append("roadmap_parity_scoreboard:virtqueue_wrappers:evidence:missing")
        return drift

    for item in REQUIRED_RING_SCOREBOARD_EVIDENCE:
        if item not in ring_evidence:
            drift.append(
                "roadmap_parity_scoreboard:virtqueue_wrappers:"
                f"{item!r}:missing"
            )

    mmio_wrappers = scoreboard.get("mmio_wrappers")
    if not isinstance(mmio_wrappers, dict):
        drift.append("roadmap_parity_scoreboard:mmio_wrappers:missing")
        return drift

    mmio_evidence = mmio_wrappers.get("evidence")
    if not isinstance(mmio_evidence, list) or not mmio_evidence:
        drift.append("roadmap_parity_scoreboard:mmio_wrappers:evidence:missing")
        return drift

    for item in REQUIRED_MMIO_SCOREBOARD_EVIDENCE:
        if item not in mmio_evidence:
            drift.append(
                "roadmap_parity_scoreboard:mmio_wrappers:"
                f"{item!r}:missing"
            )

    lab_only_driver_validation = scoreboard.get("lab_only_driver_validation")
    if not isinstance(lab_only_driver_validation, dict):
        drift.append("roadmap_parity_scoreboard:lab_only_driver_validation:missing")
        return drift

    lab_validation_evidence = lab_only_driver_validation.get("evidence")
    if not isinstance(lab_validation_evidence, list) or not lab_validation_evidence:
        drift.append(
            "roadmap_parity_scoreboard:lab_only_driver_validation:evidence:missing"
        )
        return drift

    for item in REQUIRED_LAB_VALIDATION_EVIDENCE:
        if item not in lab_validation_evidence:
            drift.append(
                "roadmap_parity_scoreboard:lab_only_driver_validation:"
                f"{item!r}:missing"
            )

    for item in REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE:
        if item not in lab_validation_evidence:
            drift.append(
                "roadmap_parity_scoreboard:lab_only_driver_validation:"
                f"{item!r}:missing"
            )

    for item in REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE:
        if item not in lab_validation_evidence:
            drift.append(
                "roadmap_parity_scoreboard:lab_only_driver_validation:"
                f"{item!r}:missing"
            )

    for item in REQUIRED_CORE_LAB_VALIDATION_EVIDENCE:
        if item not in lab_validation_evidence:
            drift.append(
                "roadmap_parity_scoreboard:lab_only_driver_validation:"
                f"{item!r}:missing"
            )

    dual_implementations = scoreboard.get("dual_implementations_for_risky_areas")
    if not isinstance(dual_implementations, dict):
        drift.append(
            "roadmap_parity_scoreboard:dual_implementations_for_risky_areas:missing"
        )
        return drift

    dual_implementation_evidence = dual_implementations.get("evidence")
    if not isinstance(dual_implementation_evidence, list) or not dual_implementation_evidence:
        drift.append(
            "roadmap_parity_scoreboard:dual_implementations_for_risky_areas:evidence:missing"
        )
        return drift

    for item in REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE:
        if item not in dual_implementation_evidence:
            drift.append(
                "roadmap_parity_scoreboard:dual_implementations_for_risky_areas:"
                f"{item!r}:missing"
            )

    provenance = manifest.get("survey_provenance")
    if not isinstance(provenance, dict):
        drift.append("survey_provenance:missing")
        return drift

    if provenance.get("source") != REQUIRED_SURVEY_PROVENANCE_SOURCE:
        drift.append(
            "survey_provenance:source:"
            f"{provenance.get('source')!r}!={REQUIRED_SURVEY_PROVENANCE_SOURCE!r}"
        )

    lane_keys = provenance.get("lane_keys")
    if not isinstance(lane_keys, dict):
        drift.append("survey_provenance:lane_keys:missing")
        return drift
    for key, expected in REQUIRED_SURVEY_LANE_KEYS.items():
        actual = lane_keys.get(key)
        if actual != expected:
            drift.append(f"survey_provenance:lane_keys:{key}:{actual!r}!={expected!r}")

    surveyed_commits = provenance.get("surveyed_commits")
    if not isinstance(surveyed_commits, dict):
        drift.append("survey_provenance:surveyed_commits:missing")
        return drift
    for key, expected in REQUIRED_SURVEY_COMMITS.items():
        actual = surveyed_commits.get(key)
        if actual != expected:
            drift.append(
                f"survey_provenance:surveyed_commits:{key}:{actual!r}!={expected!r}"
            )

    cross_phase_boundary = manifest.get("cross_phase_scoreboard_boundary")
    if not isinstance(cross_phase_boundary, dict):
        drift.append("cross_phase_scoreboard_boundary:missing")
        return drift

    reference_samples = cross_phase_boundary.get("reference_samples")
    if not isinstance(reference_samples, dict):
        drift.append("cross_phase_scoreboard_boundary:reference_samples:missing")
        return drift
    if reference_samples.get("status") != "out_of_scope":
        drift.append(
            "cross_phase_scoreboard_boundary:reference_samples:status:"
            f"{reference_samples.get('status')!r}!='out_of_scope'"
        )
    reference_sample_evidence = reference_samples.get("evidence")
    if not isinstance(reference_sample_evidence, list) or not reference_sample_evidence:
        drift.append(
            "cross_phase_scoreboard_boundary:reference_samples:evidence:missing"
        )
        return drift
    for item in REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE:
        if item not in reference_sample_evidence:
            drift.append(
                "cross_phase_scoreboard_boundary:reference_samples:"
                f"{item!r}:missing"
            )

    runtime_starters = cross_phase_boundary.get("runtime_starters")
    if not isinstance(runtime_starters, dict):
        drift.append("cross_phase_scoreboard_boundary:runtime_starters:missing")
        return drift
    if runtime_starters.get("status") != "out_of_scope":
        drift.append(
            "cross_phase_scoreboard_boundary:runtime_starters:status:"
            f"{runtime_starters.get('status')!r}!='out_of_scope'"
        )
    runtime_starter_evidence = runtime_starters.get("evidence")
    if not isinstance(runtime_starter_evidence, list) or not runtime_starter_evidence:
        drift.append(
            "cross_phase_scoreboard_boundary:runtime_starters:evidence:missing"
        )
        return drift
    for item in REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE:
        if item not in runtime_starter_evidence:
            drift.append(
                "cross_phase_scoreboard_boundary:runtime_starters:"
                f"{item!r}:missing"
            )

    landed_core_helper_evidence = manifest.get("landed_core_helper_evidence")
    if not isinstance(landed_core_helper_evidence, dict):
        drift.append("landed_core_helper_evidence:missing")
        return drift

    for path, required_labels in REQUIRED_LANDED_CORE_HELPER_EVIDENCE.items():
        helper_labels = landed_core_helper_evidence.get(path)
        if not isinstance(helper_labels, list) or not helper_labels:
            drift.append(f"landed_core_helper_evidence:{path}:missing")
            continue
        for label in required_labels:
            if label not in helper_labels:
                drift.append(
                    f"landed_core_helper_evidence:{path}:{label!r}:missing"
                )

    focused_harness_replays = manifest.get("focused_harness_replays")
    if not isinstance(focused_harness_replays, dict):
        drift.append("focused_harness_replays:missing")
        return drift

    for path, required_labels in REQUIRED_FOCUSED_HARNESS_REPLAYS.items():
        replay_labels = focused_harness_replays.get(path)
        if not isinstance(replay_labels, list) or not replay_labels:
            drift.append(f"focused_harness_replays:{path}:missing")
            continue
        for label in required_labels:
            if label not in replay_labels:
                drift.append(
                    f"focused_harness_replays:{path}:{label!r}:missing"
                )

    ready_transport_followups = manifest.get("ready_transport_followups")
    if not isinstance(ready_transport_followups, dict):
        drift.append("ready_transport_followups:missing")
        return drift

    input_followup = ready_transport_followups.get(REQUIRED_INPUT_READY_TRANSPORT_PATH)
    if input_followup != REQUIRED_INPUT_READY_TRANSPORT_GAP:
        drift.append(
            "ready_transport_followups:"
            f"{REQUIRED_INPUT_READY_TRANSPORT_PATH}:{input_followup!r}!={REQUIRED_INPUT_READY_TRANSPORT_GAP!r}"
        )

    mmio_followup = ready_transport_followups.get(REQUIRED_MMIO_READY_TRANSPORT_PATH)
    if mmio_followup != REQUIRED_MMIO_READY_TRANSPORT_GAP:
        drift.append(
            "ready_transport_followups:"
            f"{REQUIRED_MMIO_READY_TRANSPORT_PATH}:{mmio_followup!r}!={REQUIRED_MMIO_READY_TRANSPORT_GAP!r}"
        )

    blocked_transport_gaps = manifest.get("blocked_transport_gaps")
    if not isinstance(blocked_transport_gaps, dict):
        drift.append("blocked_transport_gaps:missing")
        return drift

    core_blocked_gap = blocked_transport_gaps.get(REQUIRED_CORE_BLOCKED_TRANSPORT_PATH)
    if core_blocked_gap != REQUIRED_CORE_BLOCKED_TRANSPORT_GAP:
        drift.append(
            "blocked_transport_gaps:"
            f"{REQUIRED_CORE_BLOCKED_TRANSPORT_PATH}:{core_blocked_gap!r}!={REQUIRED_CORE_BLOCKED_TRANSPORT_GAP!r}"
        )

    input_blocked_gap = blocked_transport_gaps.get(REQUIRED_INPUT_READY_TRANSPORT_PATH)
    if input_blocked_gap != REQUIRED_INPUT_READY_TRANSPORT_GAP:
        drift.append(
            "blocked_transport_gaps:"
            f"{REQUIRED_INPUT_READY_TRANSPORT_PATH}:{input_blocked_gap!r}!={REQUIRED_INPUT_READY_TRANSPORT_GAP!r}"
        )

    mmio_blocked_gap = blocked_transport_gaps.get(REQUIRED_MMIO_READY_TRANSPORT_PATH)
    if mmio_blocked_gap != REQUIRED_MMIO_READY_TRANSPORT_GAP:
        drift.append(
            "blocked_transport_gaps:"
            f"{REQUIRED_MMIO_READY_TRANSPORT_PATH}:{mmio_blocked_gap!r}!={REQUIRED_MMIO_READY_TRANSPORT_GAP!r}"
        )

    return drift


def validate(root: Path) -> tuple[list[str], list[str]]:
    tracked_paths = [MANIFEST_PATH, LEDGER_PATH]
    missing_files = [rel_path for rel_path in tracked_paths if not (root / rel_path).exists()]
    if missing_files:
        return missing_files, []

    manifest = read_json(root / MANIFEST_PATH)
    drift = collect_drift(manifest)
    drift.extend(collect_ledger_drift(manifest, (root / LEDGER_PATH).read_text(encoding="utf-8")))
    return [], drift


def fixture_manifest() -> dict:
    return {
        "doc_count": 7,
        "manifest_count": 4,
        "driver_count": 4,
        "test_count": 21,
        "docs": [f"doc-{index}" for index in range(7)],
        "manifests": [f"manifest-{index}" for index in range(4)],
        "drivers": [f"driver-{index}" for index in range(4)],
        "tests": [f"test-{index}" for index in range(21)],
        "exact_checks": REQUIRED_EXACT_CHECKS,
        "roadmap_parity_scoreboard": {
            "virtqueue_wrappers": {
                "status": "starter_landed",
                "evidence": REQUIRED_RING_SCOREBOARD_EVIDENCE,
            },
            "mmio_wrappers": {
                "status": "starter_landed",
                "evidence": REQUIRED_MMIO_SCOREBOARD_EVIDENCE,
            },
            "lab_only_driver_validation": {
                "status": "starter_landed",
                "evidence": REQUIRED_LAB_VALIDATION_EVIDENCE
                + REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE
                + REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE
                + REQUIRED_CORE_LAB_VALIDATION_EVIDENCE,
            },
            "dual_implementations_for_risky_areas": {
                "status": "blocked_on_risky_transport",
                "evidence": REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE,
            },
        },
        "survey_provenance": {
            "source": REQUIRED_SURVEY_PROVENANCE_SOURCE,
            "lane_keys": REQUIRED_SURVEY_LANE_KEYS,
            "surveyed_commits": REQUIRED_SURVEY_COMMITS,
        },
        "cross_phase_scoreboard_boundary": {
            "reference_samples": {
                "status": "out_of_scope",
                "evidence": REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE,
            },
            "runtime_starters": {
                "status": "out_of_scope",
                "evidence": REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE,
            },
        },
        "landed_core_helper_evidence": REQUIRED_LANDED_CORE_HELPER_EVIDENCE,
        "focused_harness_replays": REQUIRED_FOCUSED_HARNESS_REPLAYS,
        "ready_transport_followups": {
            REQUIRED_INPUT_READY_TRANSPORT_PATH: REQUIRED_INPUT_READY_TRANSPORT_GAP,
            REQUIRED_MMIO_READY_TRANSPORT_PATH: REQUIRED_MMIO_READY_TRANSPORT_GAP,
        },
        "blocked_transport_gaps": {
            REQUIRED_CORE_BLOCKED_TRANSPORT_PATH: REQUIRED_CORE_BLOCKED_TRANSPORT_GAP,
            REQUIRED_INPUT_READY_TRANSPORT_PATH: REQUIRED_INPUT_READY_TRANSPORT_GAP,
            REQUIRED_MMIO_READY_TRANSPORT_PATH: REQUIRED_MMIO_READY_TRANSPORT_GAP,
        },
    }


def build_fixture_ledger(manifest: dict) -> str:
    lines = build_expected_ledger_lines(manifest)
    return "\n".join(f"- `{line}`" for line in lines) + "\n"


def write_fixture(root: Path) -> None:
    manifest = fixture_manifest()
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(root / LEDGER_PATH, build_fixture_ledger(manifest))


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_manifest_counts_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, drift = validate(root)
        if missing_files or drift:
            raise SystemExit(
                "phase10-manifest-counts-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"drift={','.join(drift) or 'none'}"
            )

        manifest_path = root / MANIFEST_PATH
        ledger_path = root / LEDGER_PATH
        original = read_json(manifest_path)
        original_ledger = ledger_path.read_text(encoding="utf-8")

        def write_manifest(data: dict) -> None:
            write_text(manifest_path, json.dumps(data, indent=2) + "\n")

        def write_ledger(text: str) -> None:
            write_text(ledger_path, text)

        cases = 0

        broken = dict(original)
        broken["doc_count"] = 6
        write_manifest(broken)
        expect_contains(validate(root)[1], "doc_count:6!=len(docs):7", "phase10-manifest-counts-self-test")
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["manifest_count"] = 5
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "manifest_count:5!=len(manifests):4",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["driver_count"] = 3
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "driver_count:3!=len(drivers):4",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["test_count"] = 20
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "test_count:20!=len(tests):21",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        del broken["doc_count"]
        write_manifest(broken)
        expect_contains(validate(root)[1], "doc_count:missing", "phase10-manifest-counts-self-test")
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["tests"] = []
        write_manifest(broken)
        expect_contains(validate(root)[1], "tests:missing", "phase10-manifest-counts-self-test")
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-bootstrap-route.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-bootstrap-route.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-core-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-core-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-shared-freeze-boundary.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-ring-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-ring-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-input-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-input-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-mmio-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-mmio-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-harness-coverage.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-harness-coverage.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-closure-manifest-counts.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-closure-manifest-counts.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/validate-phase10.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/validate-phase10.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/validate-phase10-closure.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/validate-phase10-closure.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "make -C zigux phase10-validate"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'make -C zigux phase10-validate':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "zig build test --build-file zigux/tests/phase10_build.zig --summary all"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'zig build test --build-file zigux/tests/phase10_build.zig --summary all':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "make -C zigux phase10-test"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'make -C zigux phase10-test':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "make -C zigux phase10"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'make -C zigux phase10':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        reordered = list(REQUIRED_EXACT_CHECKS)
        reordered[-1], reordered[-2] = reordered[-2], reordered[-1]
        broken["exact_checks"] = reordered
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:closure_route:out_of_order",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        del broken["exact_checks"]
        write_manifest(broken)
        expect_contains(validate(root)[1], "exact_checks:missing", "phase10-manifest-counts-self-test")
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["virtqueue_wrappers"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["virtqueue_wrappers"]["evidence"]
            if item != "drivers/virtio/virtio_ring_publish_readiness.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:virtqueue_wrappers:'drivers/virtio/virtio_ring_publish_readiness.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["mmio_wrappers"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["mmio_wrappers"]["evidence"]
            if item != "Documentation/zigux/phase10-virtio-mmio-survey.md"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:mmio_wrappers:'Documentation/zigux/phase10-virtio-mmio-survey.md':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "scripts/zigux/check-phase10-core-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'scripts/zigux/check-phase10-core-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "Documentation/zigux/phase10-virtio-core-survey.md"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'Documentation/zigux/phase10-virtio-core-survey.md':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "drivers/virtio/virtio_driver_id.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'drivers/virtio/virtio_driver_id.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "zigux/tests/phase10_virtio_driver_id.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'zigux/tests/phase10_virtio_driver_id.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "scripts/zigux/check-phase10-closure-manifest-counts.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'scripts/zigux/check-phase10-closure-manifest-counts.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "zigux/Makefile"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'zigux/Makefile':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "drivers/virtio/virtio_input_teardown_preflight.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'drivers/virtio/virtio_input_teardown_preflight.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "zigux/tests/phase10_virtio_input_teardown_preflight.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'zigux/tests/phase10_virtio_input_teardown_preflight.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["lab_only_driver_validation"]["evidence"]
            if item != "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:lab_only_driver_validation:'zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["dual_implementations_for_risky_areas"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["dual_implementations_for_risky_areas"]["evidence"]
            if item != "zigux/tests/phase10_virtio_mmio_manifest.json"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:dual_implementations_for_risky_areas:'zigux/tests/phase10_virtio_mmio_manifest.json':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["survey_provenance"]["source"] = "static"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "survey_provenance:source:'static'!='manifest_derived'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["survey_provenance"]["lane_keys"]["mmio"] = "P10-L12"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "survey_provenance:lane_keys:mmio:'P10-L12'!='P10-L11'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["survey_provenance"]["surveyed_commits"]["mmio"] = "deadbeef"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "survey_provenance:surveyed_commits:mmio:'deadbeef'!='b53ec2bd507d0b3283486e76acc273b184ad5bf8'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["cross_phase_scoreboard_boundary"]["reference_samples"]["evidence"] = [
            item
            for item in broken["cross_phase_scoreboard_boundary"]["reference_samples"]["evidence"]
            if item != "samples/zigux"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "cross_phase_scoreboard_boundary:reference_samples:'samples/zigux':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["cross_phase_scoreboard_boundary"]["runtime_starters"]["status"] = "starter_landed"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "cross_phase_scoreboard_boundary:runtime_starters:status:'starter_landed'!='out_of_scope'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["cross_phase_scoreboard_boundary"]["runtime_starters"]["evidence"] = [
            item
            for item in broken["cross_phase_scoreboard_boundary"]["runtime_starters"]["evidence"]
            if item != "zigux/tests/runtime_trace_events_survey.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "cross_phase_scoreboard_boundary:runtime_starters:'zigux/tests/runtime_trace_events_survey.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["landed_core_helper_evidence"]["zigux/tests/phase10_virtio_core_manifest.json"] = [
            item
            for item in broken["landed_core_helper_evidence"]["zigux/tests/phase10_virtio_core_manifest.json"]
            if item != "phase10-driver-validation-narrowing-helper"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "landed_core_helper_evidence:zigux/tests/phase10_virtio_core_manifest.json:'phase10-driver-validation-narrowing-helper':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_driver_id.zig"] = []
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "focused_harness_replays:zigux/tests/phase10_virtio_driver_id.zig:missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig"] = []
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "focused_harness_replays:zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig:missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_core_reset_queue.zig"] = []
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "focused_harness_replays:zigux/tests/phase10_virtio_core_reset_queue.zig:missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["focused_harness_replays"]["drivers/virtio/virtio_ring_publish_readiness.zig"] = []
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "focused_harness_replays:drivers/virtio/virtio_ring_publish_readiness.zig:missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_mmio.zig"] = [
            "phase10 mmio companion drift",
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "focused_harness_replays:zigux/tests/phase10_virtio_mmio.zig:'phase10 mmio lab replay':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig"] = [
            "phase10 mmio apply-observation drift",
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "focused_harness_replays:zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig:'phase10 mmio apply-observation replay':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        del broken["focused_harness_replays"]["zigux/tests/phase10_virtio_mmio_survey.zig"]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "focused_harness_replays:zigux/tests/phase10_virtio_mmio_survey.zig:missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["ready_transport_followups"][REQUIRED_INPUT_READY_TRANSPORT_PATH] = "phase10-input-helper-drift"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "ready_transport_followups:zigux/tests/phase10_virtio_input_manifest.json:'phase10-input-helper-drift'!='phase10-virtio-input-registration-lifecycle'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["ready_transport_followups"][REQUIRED_MMIO_READY_TRANSPORT_PATH] = "phase10-mmio-helper-drift"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "ready_transport_followups:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-helper-drift'!='phase10-mmio-lifecycle-and-irq-paths'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["blocked_transport_gaps"][REQUIRED_CORE_BLOCKED_TRANSPORT_PATH] = "phase10-core-helper-drift"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "blocked_transport_gaps:zigux/tests/phase10_virtio_core_manifest.json:'phase10-core-helper-drift'!='phase10-core-probe-remove-lifecycle'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["blocked_transport_gaps"][REQUIRED_INPUT_READY_TRANSPORT_PATH] = "phase10-input-helper-drift"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "blocked_transport_gaps:zigux/tests/phase10_virtio_input_manifest.json:'phase10-input-helper-drift'!='phase10-virtio-input-registration-lifecycle'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        broken["blocked_transport_gaps"][REQUIRED_MMIO_READY_TRANSPORT_PATH] = "phase10-mmio-helper-drift"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "blocked_transport_gaps:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-helper-drift'!='phase10-mmio-lifecycle-and-irq-paths'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        broken = dict(original)
        del broken["roadmap_parity_scoreboard"]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:virtqueue_wrappers:missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        write_ledger(original_ledger.replace(
            "PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json",
            "PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_old_manifest.json",
            1,
        ))
        expect_contains(
            validate(root)[1],
            "ledger:PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        write_ledger(original_ledger.replace(
            "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8",
            "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=deadbeef",
            1,
        ))
        expect_contains(
            validate(root)[1],
            "ledger:PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        write_ledger(original_ledger.replace(
            "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-survey.md",
            "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-survey.md",
            1,
        ))
        expect_contains(
            validate(root)[1],
            "ledger:PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-survey.md",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        write_ledger(original_ledger.replace(
            "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
            "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=starter_landed",
            1,
        ))
        expect_contains(
            validate(root)[1],
            "ledger:PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
            "phase10-manifest-counts-self-test",
        )
        cases += 1
        write_fixture(root)

        ledger_path.unlink()
        missing_files, drift = validate(root)
        if drift:
            actual = ",".join(drift)
            raise SystemExit(f"phase10-manifest-counts-self-test:unexpected_drift={actual}")
        if missing_files != [LEDGER_PATH]:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(
                "phase10-manifest-counts-self-test:"
                f"expected_missing={LEDGER_PATH}:actual={actual}"
            )
        cases += 1
        write_fixture(root)

        manifest_path.unlink()
        missing_files, drift = validate(root)
        if drift:
            actual = ",".join(drift)
            raise SystemExit(f"phase10-manifest-counts-self-test:unexpected_drift={actual}")
        if missing_files != [MANIFEST_PATH]:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(
                "phase10-manifest-counts-self-test:"
                f"expected_missing={MANIFEST_PATH}:actual={actual}"
            )
        cases += 1

    print("PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 10 closure manifest summary-count packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, drift = validate(args.repo_root)
    if missing_files:
        print("PHASE10_CLOSURE_MANIFEST_COUNTS=fail")
        print("MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_END")
        return 1

    if drift:
        print("PHASE10_CLOSURE_MANIFEST_COUNTS=fail")
        print("PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_END")
        return 1

    print("PHASE10_CLOSURE_MANIFEST_COUNTS=pass")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_FIELD_COUNT={len(COUNT_FIELDS)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_EXACT_CHECK_COUNT={len(REQUIRED_EXACT_CHECKS)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_RING_EVIDENCE_COUNT={len(REQUIRED_RING_SCOREBOARD_EVIDENCE)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_MMIO_EVIDENCE_COUNT={len(REQUIRED_MMIO_SCOREBOARD_EVIDENCE)}")
    print(
        "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LAB_VALIDATION_EVIDENCE_COUNT="
        f"{len(REQUIRED_LAB_VALIDATION_EVIDENCE) + len(REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE) + len(REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE) + len(REQUIRED_CORE_LAB_VALIDATION_EVIDENCE)}"
    )
    print(
        "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_REFERENCE_SAMPLE_EVIDENCE_COUNT="
        f"{len(REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE)}"
    )
    print(
        "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_RUNTIME_STARTER_EVIDENCE_COUNT="
        f"{len(REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE)}"
    )
    print(
        "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_CORE_HELPER_COUNT="
        f"{sum(len(labels) for labels in REQUIRED_LANDED_CORE_HELPER_EVIDENCE.values())}"
    )
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_FOCUSED_HARNESS_REPLAY_COUNT={len(REQUIRED_FOCUSED_HARNESS_REPLAYS)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_DUAL_IMPLEMENTATION_EVIDENCE_COUNT={len(REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LEDGER_LINE_COUNT={len(build_expected_ledger_lines(read_json(args.repo_root / MANIFEST_PATH)))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

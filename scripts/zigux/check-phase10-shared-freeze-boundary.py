#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

CHECK_COMMAND = "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py"
EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC = (
    "Documentation/zigux/phase10-freeze-boundary-gap-survey.md"
)

COMMON_DRIVER_MANIFEST_FILES = [
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

REQUIRED_FILES = [
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC,
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    *COMMON_DRIVER_MANIFEST_FILES,
]

FREEZE_IN_C_ANCHORS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]

STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

PHASE14_EVIDENCE_FEATURES = [
    "boundary maps",
    "concurrency audits",
    "explicit stay-in-C decisions where warranted",
    "wrapper-first or study-only posture",
]

PHASE14_FUTURE_DESTINATIONS = [
    "kernel/workqueue_bridge.zig",
    "kernel/trace/ring_buffer.zig",
]

PHASE14_FUTURE_DESTINATION_POLICY = (
    "kernel/trace/ring_buffer.zig remains a future destination only if years of evidence justify it"
)

EXPECTED_SURVEY_PROVENANCE = {
    "source": "manifest_derived",
    "lane_keys": {
        "core": "P10-L01",
        "ring": "P10-L10",
        "input": "P10-L22",
        "mmio": "P10-L11",
    },
}

EXPECTED_READY_TRANSPORT_FOLLOWUPS = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

EXPECTED_BLOCKED_TRANSPORT_GAPS = {
    "zigux/tests/phase10_virtio_core_manifest.json": "phase10-core-probe-remove-lifecycle",
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

CLOSURE_ALLOWED_ROADMAP_DESTINATIONS = [
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
]

CLOSURE_FORBIDDEN_TRANSPORT_CLAIMS = [
    "queue_setup_reset_paths",
    "queue_reset_execution",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
    "freeze_restore_lifecycle",
]

COMMON_DRIVER_FIELD_VALUES = {
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "allowed_evidence_kinds": [
        "driver_local_lab_slices",
        "survey_manifests",
        "shared_validation_gates",
    ],
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}

EXPECTED_DRIVER_MANIFEST_FIELDS = {
    "zigux/tests/phase10_virtio_ring_manifest.json": {
        **COMMON_DRIVER_FIELD_VALUES,
        "forbidden_transport_claims": [
            "queue_setup_reset_paths",
            "irq_parity",
            "dma_paths",
            "input_registration_lifecycle",
            "probe_remove_lifecycle",
        ],
    },
    "zigux/tests/phase10_virtio_input_manifest.json": {
        **COMMON_DRIVER_FIELD_VALUES,
        "forbidden_transport_claims": [
            "queue_setup_reset_paths",
            "irq_parity",
            "dma_paths",
            "input_registration_lifecycle",
            "probe_remove_lifecycle",
        ],
    },
    "zigux/tests/phase10_virtio_mmio_manifest.json": {
        **COMMON_DRIVER_FIELD_VALUES,
        "forbidden_transport_claims": [
            "queue_setup_reset_paths",
            "queue_reset_execution",
            "irq_parity",
            "dma_paths",
            "probe_remove_lifecycle",
            "freeze_restore_lifecycle",
        ],
    },
}

TEXT_MARKERS = {
    "scripts/zigux/check-phase10-shared-freeze-boundary.py": [
        f'CHECK_COMMAND = "{CHECK_COMMAND}"',
        '"kernel/workqueue.c"',
        '"kernel/trace/ring_buffer.c"',
        '"kernel/sched/core.c"',
        '"net/core/skbuff.c"',
    ],
    "Documentation/zigux/README.md": [
        "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
    ],
    "Documentation/zigux/freeze-map.md": [
        "`kernel/sched/core.c`",
        "`mm/page_alloc.c`",
        "`kernel/rcu/tree.c`",
        "`net/core/skbuff.c`",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "there is no silent exception path around the stay-in-C policy",
    ],
    EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC: [
        "# Phase 10 Freeze-Boundary Gap Survey",
        "`Documentation/zigux/freeze-map.md` explicit as the governing freeze source",
        "`scripts/zigux/check-phase10-shared-freeze-boundary.py` explicit as the fail-closed review gate for freeze-boundary drift",
        "Study-only anchors that remain outside Phase 10 delivery and stay parked in the separate Phase 14 family:",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "It must not present them as active virtio closure evidence, bridge-readiness proof, or status-change candidates.",
    ],
    "Documentation/zigux/phase10-closure-evidence.md": [
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
    ],
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md": [
        "keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
    ],
    "Documentation/zigux/phase15-study-only-anchor-accounting.md": [
        "### `kernel/workqueue.c`",
        "### `kernel/trace/ring_buffer.c`",
        "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
    ],
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": [
        "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
        "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
        "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
        "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
        "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
        "PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in TEXT_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{Path(rel_path).name}:{marker}")

    closure_manifest = json.loads(read_text(root, "zigux/tests/phase10_closure_manifest.json"))
    if closure_manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
        missing_markers.append(
            f"closure_manifest:freeze_map={closure_manifest.get('freeze_map')!r}"
        )
    if closure_manifest.get("freeze_boundary_status") != "aligned":
        missing_markers.append(
            "closure_manifest:freeze_boundary_status="
            + repr(closure_manifest.get("freeze_boundary_status"))
        )
    if closure_manifest.get("freeze_status_change_claimed") is not False:
        missing_markers.append(
            "closure_manifest:freeze_status_change_claimed="
            + repr(closure_manifest.get("freeze_status_change_claimed"))
        )
    if closure_manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing_markers.append(
            "closure_manifest:risky_transport_posture="
            + repr(closure_manifest.get("risky_transport_posture"))
        )
    if (
        closure_manifest.get("allowed_roadmap_destinations")
        != CLOSURE_ALLOWED_ROADMAP_DESTINATIONS
    ):
        missing_markers.append("closure_manifest:allowed_roadmap_destinations")
    if (
        closure_manifest.get("allowed_evidence_kinds")
        != COMMON_DRIVER_FIELD_VALUES["allowed_evidence_kinds"]
    ):
        missing_markers.append("closure_manifest:allowed_evidence_kinds")
    if (
        closure_manifest.get("forbidden_transport_claims")
        != CLOSURE_FORBIDDEN_TRANSPORT_CLAIMS
    ):
        missing_markers.append("closure_manifest:forbidden_transport_claims")
    if closure_manifest.get("architecture_council_reopen_required") is not True:
        missing_markers.append(
            "closure_manifest:architecture_council_reopen_required="
            + repr(closure_manifest.get("architecture_council_reopen_required"))
        )
    if closure_manifest.get("architecture_council_reopen_attached") is not False:
        missing_markers.append(
            "closure_manifest:architecture_council_reopen_attached="
            + repr(closure_manifest.get("architecture_council_reopen_attached"))
        )
    if closure_manifest.get("ready_transport_followups") != EXPECTED_READY_TRANSPORT_FOLLOWUPS:
        missing_markers.append("closure_manifest:ready_transport_followups")
    if closure_manifest.get("blocked_transport_gaps") != EXPECTED_BLOCKED_TRANSPORT_GAPS:
        missing_markers.append("closure_manifest:blocked_transport_gaps")
    if closure_manifest.get("freeze_in_c_anchors") != FREEZE_IN_C_ANCHORS:
        missing_markers.append("closure_manifest:freeze_in_c_anchors")
    if closure_manifest.get("study_only_anchors") != STUDY_ONLY_ANCHORS:
        missing_markers.append("closure_manifest:study_only_anchors")

    docs = closure_manifest.get("docs")
    if not isinstance(docs, list):
        missing_markers.append("closure_manifest:docs")
    elif EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC not in docs:
        missing_markers.append(
            "closure_manifest:docs:missing_phase10_freeze_boundary_gap_survey"
        )

    phase14_boundary = closure_manifest.get("phase14_study_only_boundary")
    if not isinstance(phase14_boundary, dict):
        missing_markers.append("closure_manifest:phase14_study_only_boundary")
    else:
        if phase14_boundary.get("status") != "separate_phase14_lane":
            missing_markers.append(
                "closure_manifest:phase14_study_only_boundary:status="
                + repr(phase14_boundary.get("status"))
            )
        if phase14_boundary.get("anchors") != STUDY_ONLY_ANCHORS:
            missing_markers.append("closure_manifest:phase14_study_only_boundary:anchors")
        if (
            phase14_boundary.get("required_phase14_evidence_features")
            != PHASE14_EVIDENCE_FEATURES
        ):
            missing_markers.append(
                "closure_manifest:phase14_study_only_boundary:required_phase14_evidence_features"
            )
        if phase14_boundary.get("future_destinations") != PHASE14_FUTURE_DESTINATIONS:
            missing_markers.append(
                "closure_manifest:phase14_study_only_boundary:future_destinations"
            )
        if (
            phase14_boundary.get("future_destination_policy")
            != PHASE14_FUTURE_DESTINATION_POLICY
        ):
            missing_markers.append(
                "closure_manifest:phase14_study_only_boundary:future_destination_policy="
                + repr(phase14_boundary.get("future_destination_policy"))
            )

    survey_provenance = closure_manifest.get("survey_provenance")
    if not isinstance(survey_provenance, dict):
        missing_markers.append("closure_manifest:survey_provenance")
    else:
        if survey_provenance.get("source") != EXPECTED_SURVEY_PROVENANCE["source"]:
            missing_markers.append(
                "closure_manifest:survey_provenance:source="
                + repr(survey_provenance.get("source"))
            )
        if survey_provenance.get("lane_keys") != EXPECTED_SURVEY_PROVENANCE["lane_keys"]:
            missing_markers.append("closure_manifest:survey_provenance:lane_keys")

    for rel_path, expected_fields in EXPECTED_DRIVER_MANIFEST_FIELDS.items():
        manifest = json.loads(read_text(root, rel_path))
        label = Path(rel_path).name
        for field, expected in expected_fields.items():
            actual = manifest.get(field)
            if actual != expected:
                missing_markers.append(f"{label}:{field}={actual!r}")

    return [], missing_markers


def build_fixture_manifest() -> str:
    return json.dumps(
        {
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "risky_transport_posture": "blocked_on_risky_transport",
            "allowed_roadmap_destinations": CLOSURE_ALLOWED_ROADMAP_DESTINATIONS,
            "allowed_evidence_kinds": COMMON_DRIVER_FIELD_VALUES["allowed_evidence_kinds"],
            "forbidden_transport_claims": CLOSURE_FORBIDDEN_TRANSPORT_CLAIMS,
            "architecture_council_reopen_required": True,
            "architecture_council_reopen_attached": False,
            "ready_transport_followups": EXPECTED_READY_TRANSPORT_FOLLOWUPS,
            "blocked_transport_gaps": EXPECTED_BLOCKED_TRANSPORT_GAPS,
            "freeze_in_c_anchors": FREEZE_IN_C_ANCHORS,
            "study_only_anchors": STUDY_ONLY_ANCHORS,
            "docs": [EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC],
            "phase14_study_only_boundary": {
                "status": "separate_phase14_lane",
                "anchors": STUDY_ONLY_ANCHORS,
                "required_phase14_evidence_features": PHASE14_EVIDENCE_FEATURES,
                "future_destinations": PHASE14_FUTURE_DESTINATIONS,
                "future_destination_policy": PHASE14_FUTURE_DESTINATION_POLICY,
            },
            "survey_provenance": EXPECTED_SURVEY_PROVENANCE,
            "exact_checks": [CHECK_COMMAND],
        },
        indent=2,
    ) + "\n"


def build_driver_manifest(rel_path: str, lane_key: str) -> str:
    manifest = {
        "lane_key": lane_key,
        **EXPECTED_DRIVER_MANIFEST_FIELDS[rel_path],
        "gaps": [],
    }
    return json.dumps(manifest, indent=2) + "\n"


def build_fixture_files() -> dict[str, str]:
    return {
        "scripts/zigux/check-phase10-shared-freeze-boundary.py": "\n".join(
            TEXT_MARKERS["scripts/zigux/check-phase10-shared-freeze-boundary.py"]
        )
        + "\n",
        "Documentation/zigux/README.md": "\n".join(TEXT_MARKERS["Documentation/zigux/README.md"])
        + "\n",
        "Documentation/zigux/freeze-map.md": "\n".join(TEXT_MARKERS["Documentation/zigux/freeze-map.md"])
        + "\n",
        EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC: "\n".join(
            TEXT_MARKERS[EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC]
        )
        + "\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase10-closure-evidence.md"]
        )
        + "\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"]
        )
        + "\n",
        "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"]
        )
        + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"]
        )
        + "\n",
        "Documentation/zigux/phase15-study-only-anchor-accounting.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase15-study-only-anchor-accounting.md"]
        )
        + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/review-checklist.md"]
        )
        + "\n",
        "zigux/tests/phase10_closure_manifest.json": build_fixture_manifest(),
        "zigux/tests/phase10_virtio_ring_manifest.json": build_driver_manifest(
            "zigux/tests/phase10_virtio_ring_manifest.json", "P10-L10"
        ),
        "zigux/tests/phase10_virtio_input_manifest.json": build_driver_manifest(
            "zigux/tests/phase10_virtio_input_manifest.json", "P10-L22"
        ),
        "zigux/tests/phase10_virtio_mmio_manifest.json": build_driver_manifest(
            "zigux/tests/phase10_virtio_mmio_manifest.json", "P10-L11"
        ),
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(
            TEXT_MARKERS["zigux-alpha/PHASE10_CLOSURE_LEDGER.md"]
        )
        + "\n",
    }


def reset_fixture(root: Path) -> None:
    for rel_path, content in build_fixture_files().items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-shared-freeze-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def run_manifest_case(root: Path, key: str, value: object, expected: str) -> None:
    path = root / "zigux/tests/phase10_closure_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest[key] = value
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-shared-freeze-self-test:expected={expected}:actual={actual}")


def run_phase14_case(root: Path, key: str, value: object, expected: str) -> None:
    path = root / "zigux/tests/phase10_closure_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    phase14 = manifest["phase14_study_only_boundary"]
    phase14[key] = value
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-shared-freeze-self-test:expected={expected}:actual={actual}")


def run_driver_manifest_case(
    root: Path, rel_path: str, key: str, value: object, expected: str
) -> None:
    path = root / rel_path
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest[key] = value
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-shared-freeze-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_shared_freeze_") as tmp_dir:
        root = Path(tmp_dir)
        reset_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-shared-freeze-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        cases = [
            (
                "Documentation/zigux/README.md",
                "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
                "`kernel/workqueue_bridge.zig` is Phase 9 runtime readiness evidence.",
                "README.md:`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
            ),
            (
                EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC,
                "`scripts/zigux/check-phase10-shared-freeze-boundary.py` explicit as the fail-closed review gate for freeze-boundary drift",
                "`scripts/zigux/check-phase10-shared-freeze-boundary.py` is optional context",
                "phase10-freeze-boundary-gap-survey.md:`scripts/zigux/check-phase10-shared-freeze-boundary.py` explicit as the fail-closed review gate for freeze-boundary drift",
            ),
            (
                "Documentation/zigux/phase10-closure-evidence.md",
                "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
                "`kernel/workqueue_bridge.zig` remains Phase 10 closure evidence.",
                "phase10-closure-evidence.md:`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
                "Phase 10 owns kernel/workqueue.c directly",
                "phase10-phase11-phase13-tests-root-review-companion.md:Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
            ),
            (
                "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
                "keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family",
                "treat `kernel/workqueue.c` as active Phase 10 evidence",
                "phase10-phase11-phase13-validator-first-review-guide.md:keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
                "Move kernel/workqueue.c into the current Phase 10 packet",
                "phase10-virtio-driver-lane-sequencing.md:Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
            ),
            (
                "Documentation/zigux/phase15-study-only-anchor-accounting.md",
                "### `kernel/trace/ring_buffer.c`",
                "### `kernel/trace/ring_buffer.zig`",
                "phase15-study-only-anchor-accounting.md:### `kernel/trace/ring_buffer.c`",
            ),
            (
                "Documentation/zigux/review-checklist.md",
                "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
                "if a shared reminder surface summarizes the study-only freeze-map anchors, direct routing is optional",
                "review-checklist.md:if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            ),
            (
                "Documentation/zigux/freeze-map.md",
                "`kernel/trace/ring_buffer.c`",
                "`kernel/trace/ring_buffer.zig`",
                "freeze-map.md:`kernel/trace/ring_buffer.c`",
            ),
            (
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
                "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manual_note",
                "PHASE10_CLOSURE_LEDGER.md:PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
            ),
            (
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
                "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L99",
                "PHASE10_CLOSURE_LEDGER.md:PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
            ),
            (
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c",
                "PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue_bridge.zig",
                "PHASE10_CLOSURE_LEDGER.md:PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c",
            ),
        ]

        for rel_path, old, new, expected in cases:
            expect_missing_marker(root, rel_path, old, new, expected)

        run_manifest_case(
            root,
            "freeze_boundary_status",
            "drifted",
            "closure_manifest:freeze_boundary_status='drifted'",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "freeze_status_change_claimed",
            True,
            "closure_manifest:freeze_status_change_claimed=True",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "risky_transport_posture",
            "starter_landed",
            "closure_manifest:risky_transport_posture='starter_landed'",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "allowed_roadmap_destinations",
            ["drivers/virtio/*.zig"],
            "closure_manifest:allowed_roadmap_destinations",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "allowed_evidence_kinds",
            ["driver_local_lab_slices"],
            "closure_manifest:allowed_evidence_kinds",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "forbidden_transport_claims",
            ["queue_setup_reset_paths", "irq_parity"],
            "closure_manifest:forbidden_transport_claims",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "architecture_council_reopen_required",
            False,
            "closure_manifest:architecture_council_reopen_required=False",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "architecture_council_reopen_attached",
            True,
            "closure_manifest:architecture_council_reopen_attached=True",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "ready_transport_followups",
            {
                "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle"
            },
            "closure_manifest:ready_transport_followups",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "blocked_transport_gaps",
            {
                "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths"
            },
            "closure_manifest:blocked_transport_gaps",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "freeze_in_c_anchors",
            FREEZE_IN_C_ANCHORS[:-1],
            "closure_manifest:freeze_in_c_anchors",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "study_only_anchors",
            ["kernel/workqueue.c"],
            "closure_manifest:study_only_anchors",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "docs",
            [],
            "closure_manifest:docs:missing_phase10_freeze_boundary_gap_survey",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "survey_provenance",
            {
                "source": "manual_note",
                "lane_keys": EXPECTED_SURVEY_PROVENANCE["lane_keys"],
            },
            "closure_manifest:survey_provenance:source='manual_note'",
        )
        reset_fixture(root)

        run_manifest_case(
            root,
            "survey_provenance",
            {
                "source": EXPECTED_SURVEY_PROVENANCE["source"],
                "lane_keys": {
                    "core": "P10-L01",
                    "ring": "P10-L10",
                    "input": "P10-L22",
                    "mmio": "P10-L99",
                },
            },
            "closure_manifest:survey_provenance:lane_keys",
        )
        reset_fixture(root)

        run_phase14_case(
            root,
            "status",
            "phase10_lane",
            "closure_manifest:phase14_study_only_boundary:status='phase10_lane'",
        )
        reset_fixture(root)

        run_phase14_case(
            root,
            "future_destination_policy",
            "ring buffer is ready now",
            "closure_manifest:phase14_study_only_boundary:future_destination_policy='ring buffer is ready now'",
        )
        reset_fixture(root)

        run_driver_manifest_case(
            root,
            "zigux/tests/phase10_virtio_ring_manifest.json",
            "freeze_boundary_status",
            "drifted",
            "phase10_virtio_ring_manifest.json:freeze_boundary_status='drifted'",
        )
        reset_fixture(root)

        run_driver_manifest_case(
            root,
            "zigux/tests/phase10_virtio_input_manifest.json",
            "freeze_status_change_claimed",
            True,
            "phase10_virtio_input_manifest.json:freeze_status_change_claimed=True",
        )
        reset_fixture(root)

        run_driver_manifest_case(
            root,
            "zigux/tests/phase10_virtio_input_manifest.json",
            "allowed_evidence_kinds",
            ["driver_local_lab_slices"],
            "phase10_virtio_input_manifest.json:allowed_evidence_kinds=['driver_local_lab_slices']",
        )
        reset_fixture(root)

        run_driver_manifest_case(
            root,
            "zigux/tests/phase10_virtio_mmio_manifest.json",
            "forbidden_transport_claims",
            ["queue_setup_reset_paths", "irq_parity"],
            "phase10_virtio_mmio_manifest.json:forbidden_transport_claims=['queue_setup_reset_paths', 'irq_parity']",
        )
        reset_fixture(root)

        run_driver_manifest_case(
            root,
            "zigux/tests/phase10_virtio_mmio_manifest.json",
            "architecture_council_reopen_attached",
            True,
            "phase10_virtio_mmio_manifest.json:architecture_council_reopen_attached=True",
        )
        reset_fixture(root)

    print("PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST=pass")
    print("PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST_CASE_COUNT=34")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_SHARED_FREEZE_BOUNDARY=fail")
    print("MISSING_PHASE10_SHARED_FREEZE_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_SHARED_FREEZE_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_SHARED_FREEZE_BOUNDARY=fail")
    print("MISSING_PHASE10_SHARED_FREEZE_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_SHARED_FREEZE_MARKERS_END")
    sys.exit(1)

total_manifest_checks = 21 + sum(
    len(fields) for fields in EXPECTED_DRIVER_MANIFEST_FIELDS.values()
)

print("PHASE10_SHARED_FREEZE_BOUNDARY=pass")
print(f"PHASE10_SHARED_FREEZE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(
    "PHASE10_SHARED_FREEZE_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for markers in TEXT_MARKERS.values()) + total_manifest_checks}"
)

#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FILES = [
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "zigux/tests/phase10_closure_manifest.json",
]

TEXT_MARKERS = {
    "Documentation/zigux/freeze-map.md": [
        "The shared Phase 10 virtio packet also stays review-first beside",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "any adjacency to `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` remains Phase 14 study-only evidence rather than a Phase 10 delivery claim",
    ],
    "Documentation/zigux/phase10-closure-evidence.md": [
        "`Documentation/zigux/freeze-map.md`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
        "risky transport work remains blocked",
        "dual-implementation requirement remains parked",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
        "the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
        "Treat the shared reminder notes and Linux-style make routes above together with the directly readable `zigux/tests/phase10_closure_manifest.json`",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "Treat the separate Phase 5 `reference_samples` boundary and the separate Phase 9 `runtime_starters` boundary as adjacent evidence only, not counted Phase 10 closure progress.",
        "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit instead of letting those anchors drift into the Phase 10 virtio packet.",
        "When a shared reminder surface refreshes freeze-boundary wording, keep the parked `P10-L11` owner",
    ],
}

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

EXPECTED_PHASE14_BOUNDARY = {
    "status": "separate_phase14_lane",
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


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in TEXT_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{Path(rel_path).name}:{marker}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_closure_manifest.json"))
    if manifest.get("freeze_map") != "Documentation/zigux/freeze-map.md":
        missing_markers.append(f"closure_manifest:freeze_map={manifest.get('freeze_map')!r}")
    if manifest.get("freeze_boundary_status") != "aligned":
        missing_markers.append(
            f"closure_manifest:freeze_boundary_status={manifest.get('freeze_boundary_status')!r}"
        )
    if manifest.get("freeze_status_change_claimed") is not False:
        missing_markers.append(
            "closure_manifest:freeze_status_change_claimed="
            + repr(manifest.get("freeze_status_change_claimed"))
        )
    if manifest.get("risky_transport_posture") != "blocked_on_risky_transport":
        missing_markers.append(
            f"closure_manifest:risky_transport_posture={manifest.get('risky_transport_posture')!r}"
        )

    if manifest.get("freeze_in_c_anchors") != EXPECTED_FREEZE_IN_C_ANCHORS:
        missing_markers.append("closure_manifest:freeze_in_c_anchors")
    if manifest.get("study_only_anchors") != EXPECTED_STUDY_ONLY_ANCHORS:
        missing_markers.append("closure_manifest:study_only_anchors")

    phase14_boundary = manifest.get("phase14_study_only_boundary")
    if not isinstance(phase14_boundary, dict):
        missing_markers.append("closure_manifest:phase14_study_only_boundary")
    else:
        if phase14_boundary.get("anchors") != EXPECTED_STUDY_ONLY_ANCHORS:
            missing_markers.append("closure_manifest:phase14_study_only_boundary.anchors")
        for key, expected in EXPECTED_PHASE14_BOUNDARY.items():
            if phase14_boundary.get(key) != expected:
                missing_markers.append(f"closure_manifest:phase14_study_only_boundary.{key}")

    return [], missing_markers


def write_fixture(root: Path) -> None:
    for rel_path, markers in TEXT_MARKERS.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")

    manifest = {
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "risky_transport_posture": "blocked_on_risky_transport",
        "freeze_in_c_anchors": EXPECTED_FREEZE_IN_C_ANCHORS,
        "study_only_anchors": EXPECTED_STUDY_ONLY_ANCHORS,
        "phase14_study_only_boundary": {
            "status": "separate_phase14_lane",
            "anchors": EXPECTED_STUDY_ONLY_ANCHORS,
            "required_phase14_evidence_features": EXPECTED_PHASE14_BOUNDARY["required_phase14_evidence_features"],
            "future_destinations": EXPECTED_PHASE14_BOUNDARY["future_destinations"],
            "future_destination_policy": EXPECTED_PHASE14_BOUNDARY["future_destination_policy"],
        },
    }
    manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def expect_missing_marker(root: Path, expected: str) -> None:
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase10-shared-freeze-self-test:expected={expected}:actual={actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_shared_freeze_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-shared-freeze-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        freeze_map = root / "Documentation/zigux/freeze-map.md"
        original = freeze_map.read_text(encoding="utf-8")
        freeze_map.write_text(
            original.replace(
                "any adjacency to `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` remains Phase 14 study-only evidence rather than a Phase 10 delivery claim",
                "Phase 14 adjacency wording missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "freeze-map.md:any adjacency to `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` remains Phase 14 study-only evidence rather than a Phase 10 delivery claim",
        )
        freeze_map.write_text(original, encoding="utf-8")

        closure = root / "Documentation/zigux/phase10-closure-evidence.md"
        original = closure.read_text(encoding="utf-8")
        closure.write_text(
            original.replace(
                "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
                "Phase 14 note missing",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "phase10-closure-evidence.md:`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
        )
        closure.write_text(original, encoding="utf-8")

        companion = root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        original = companion.read_text(encoding="utf-8")
        companion.write_text(
            original.replace(
                "the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
                "Phase 14 ownership omitted",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "phase10-phase11-phase13-tests-root-review-companion.md:the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
        )
        companion.write_text(original, encoding="utf-8")

        lane_note = root / "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"
        original = lane_note.read_text(encoding="utf-8")
        lane_note.write_text(
            original.replace(
                "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit instead of letting those anchors drift into the Phase 10 virtio packet.",
                "Shared boundary wording omitted",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "phase10-virtio-driver-lane-sequencing.md:Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit instead of letting those anchors drift into the Phase 10 virtio packet.",
        )
        lane_note.write_text(original, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["study_only_anchors"] = ["kernel/workqueue_bridge.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(root, "closure_manifest:study_only_anchors")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["phase14_study_only_boundary"]["future_destination_policy"] = "policy drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(root, "closure_manifest:phase14_study_only_boundary.future_destination_policy")
        write_fixture(root)

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["freeze_status_change_claimed"] = True
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(root, "closure_manifest:freeze_status_change_claimed=True")

    print("PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST=pass")
    print("PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST_CASE_COUNT=6")
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

print("PHASE10_SHARED_FREEZE_BOUNDARY=pass")
print(f"PHASE10_SHARED_FREEZE_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE10_SHARED_FREEZE_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for markers in TEXT_MARKERS.values()) + 4 + len(EXPECTED_FREEZE_IN_C_ANCHORS) + len(EXPECTED_STUDY_ONLY_ANCHORS) + len(EXPECTED_PHASE14_BOUNDARY) + 1}"
)

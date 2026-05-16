#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

CHECK_COMMAND = "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py"

REQUIRED_FILES = [
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
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

TEXT_MARKERS = {
    "scripts/zigux/check-phase10-shared-freeze-boundary.py": [
        f'CHECK_COMMAND = "{CHECK_COMMAND}"',
        '"kernel/workqueue.c"',
        '"kernel/trace/ring_buffer.c"',
        '"kernel/sched/core.c"',
        '"net/core/skbuff.c"',
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
    "Documentation/zigux/phase10-closure-evidence.md": [
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
    ],
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": [
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
    if manifest.get("freeze_in_c_anchors") != FREEZE_IN_C_ANCHORS:
        missing_markers.append("closure_manifest:freeze_in_c_anchors")
    if manifest.get("study_only_anchors") != STUDY_ONLY_ANCHORS:
        missing_markers.append("closure_manifest:study_only_anchors")

    phase14_boundary = manifest.get("phase14_study_only_boundary")
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
        if phase14_boundary.get("required_phase14_evidence_features") != PHASE14_EVIDENCE_FEATURES:
            missing_markers.append(
                "closure_manifest:phase14_study_only_boundary:required_phase14_evidence_features"
            )
        if phase14_boundary.get("future_destinations") != PHASE14_FUTURE_DESTINATIONS:
            missing_markers.append("closure_manifest:phase14_study_only_boundary:future_destinations")
        if phase14_boundary.get("future_destination_policy") != PHASE14_FUTURE_DESTINATION_POLICY:
            missing_markers.append(
                "closure_manifest:phase14_study_only_boundary:future_destination_policy="
                + repr(phase14_boundary.get("future_destination_policy"))
            )

    return [], missing_markers


def build_fixture_manifest() -> str:
    return json.dumps(
        {
            "freeze_map": "Documentation/zigux/freeze-map.md",
            "freeze_boundary_status": "aligned",
            "freeze_status_change_claimed": False,
            "freeze_in_c_anchors": FREEZE_IN_C_ANCHORS,
            "study_only_anchors": STUDY_ONLY_ANCHORS,
            "phase14_study_only_boundary": {
                "status": "separate_phase14_lane",
                "anchors": STUDY_ONLY_ANCHORS,
                "required_phase14_evidence_features": PHASE14_EVIDENCE_FEATURES,
                "future_destinations": PHASE14_FUTURE_DESTINATIONS,
                "future_destination_policy": PHASE14_FUTURE_DESTINATION_POLICY,
            },
            "exact_checks": [CHECK_COMMAND],
        },
        indent=2,
    ) + "\n"


def build_fixture_files() -> dict[str, str]:
    return {
        "scripts/zigux/check-phase10-shared-freeze-boundary.py": "\n".join(
            TEXT_MARKERS["scripts/zigux/check-phase10-shared-freeze-boundary.py"]
        )
        + "\n",
        "Documentation/zigux/freeze-map.md": "\n".join(TEXT_MARKERS["Documentation/zigux/freeze-map.md"])
        + "\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase10-closure-evidence.md"]
        )
        + "\n",
        "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"]
        )
        + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(
            TEXT_MARKERS["Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"]
        )
        + "\n",
        "zigux/tests/phase10_closure_manifest.json": build_fixture_manifest(),
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": "\n".join(
            TEXT_MARKERS["zigux-alpha/PHASE10_CLOSURE_LEDGER.md"]
        )
        + "\n",
    }


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


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_shared_freeze_") as tmp_dir:
        root = Path(tmp_dir)
        for rel_path, content in build_fixture_files().items():
            path = root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-shared-freeze-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        cases = [
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
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
                "Move kernel/workqueue.c into the current Phase 10 packet",
                "phase10-virtio-driver-lane-sequencing.md:Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
            ),
            (
                "Documentation/zigux/freeze-map.md",
                "`kernel/trace/ring_buffer.c`",
                "`kernel/trace/ring_buffer.zig`",
                "freeze-map.md:`kernel/trace/ring_buffer.c`",
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
        for rel_path, content in build_fixture_files().items():
            (root / rel_path).write_text(content, encoding="utf-8")

        run_manifest_case(
            root,
            "freeze_status_change_claimed",
            True,
            "closure_manifest:freeze_status_change_claimed=True",
        )
        for rel_path, content in build_fixture_files().items():
            (root / rel_path).write_text(content, encoding="utf-8")

        run_manifest_case(
            root,
            "freeze_in_c_anchors",
            FREEZE_IN_C_ANCHORS[:-1],
            "closure_manifest:freeze_in_c_anchors",
        )
        for rel_path, content in build_fixture_files().items():
            (root / rel_path).write_text(content, encoding="utf-8")

        run_manifest_case(
            root,
            "study_only_anchors",
            ["kernel/workqueue.c"],
            "closure_manifest:study_only_anchors",
        )
        for rel_path, content in build_fixture_files().items():
            (root / rel_path).write_text(content, encoding="utf-8")

        run_phase14_case(
            root,
            "status",
            "phase10_lane",
            "closure_manifest:phase14_study_only_boundary:status='phase10_lane'",
        )
        for rel_path, content in build_fixture_files().items():
            (root / rel_path).write_text(content, encoding="utf-8")

        run_phase14_case(
            root,
            "future_destination_policy",
            "ring buffer is ready now",
            "closure_manifest:phase14_study_only_boundary:future_destination_policy='ring buffer is ready now'",
        )
        for rel_path, content in build_fixture_files().items():
            (root / rel_path).write_text(content, encoding="utf-8")

    print("PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST=pass")
    print("PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST_CASE_COUNT=11")
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
print(f"PHASE10_SHARED_FREEZE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(
    "PHASE10_SHARED_FREEZE_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for markers in TEXT_MARKERS.values()) + 8}"
)

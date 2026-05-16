#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 2
    else Path(__file__).resolve().parent
)

SURVEYED_COMMIT = "9b98d3b9c812840bf279508030be0b8de093736c"
LANE_KEY = "P14-L04"
BLOCKED_GAP = "phase14-workqueue-live-execution-blocker"

DIRECT_PACKET_FILES = [
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-workqueue-bridge-slice.md",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    "Documentation/zigux/review-checklist.md",
    "kernel/workqueue_bridge.zig",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_workqueue_reviewability.zig",
]

MARKERS = {
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "`zigux/tests/phase14_workqueue_reviewability.zig`",
        "`phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`",
        "focused workqueue reviewability replay",
        "workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, "
        f"surveyed commit `{SURVEYED_COMMIT}`, ready-next `none currently recorded`, blocked `{BLOCKED_GAP}`",
        "the same packet also keeps the two landed bridge-backed roadmap destinations explicit by tying "
        "`phase14-workqueue-bridge-tests` to `../../kernel/workqueue_bridge.zig` and "
        "`phase14-skbuff-bridge-tests` to `../../net/core/skbuff_bridge.zig`, instead of letting the matrix "
        "collapse to test-root names alone.",
    ],
    "Documentation/zigux/phase14-core-boundary-traceability.md": [
        f"lane key: `{LANE_KEY}`",
        f"surveyed commit: `{SURVEYED_COMMIT}`",
        "ready-next gap: none currently recorded",
        f"blocked gap: `{BLOCKED_GAP}`",
    ],
    "Documentation/zigux/phase14-workqueue-bridge-survey.md": [
        "PHASE14_STATUS=blocked_maintenance",
        f"PHASE14_LANE_KEY={LANE_KEY}",
        f"PHASE14_SURVEYED_COMMIT={SURVEYED_COMMIT}",
        "phase14-workqueue-delayed-requeue-governance",
        "phase14-workqueue-flush-drain-governance",
        "phase14-workqueue-rescuer-mayday-governance",
        "phase14-workqueue-scheduler-visible-worker-state-refinement",
        "hotplug-topology-rebinding",
        "scheduler-visible-worker-state-refinement",
        "CPU-hotplug pool rebinding",
        "scheduler-facing runnable-state transitions",
        "delayed-work requeue control",
        "runtime `max_active` retuning ownership",
        "## Reviewability guardrails",
        f"lane `{LANE_KEY}`",
        f"surveyed commit `{SURVEYED_COMMIT}`",
        "Do not treat this lane as permission to claim wrapper ownership",
        "Leave this lane in blocked maintenance",
        "flush-drain active-color governance note",
        "timer-base ownership",
        "CPU affinity",
        "delayed-work requeue ownership",
        "runtime `max_active` retuning boundary",
        "live execution in C",
        "`make -C zigux phase14-test`",
    ],
    "Documentation/zigux/phase14-workqueue-bridge-slice.md": [
        "# Phase 14 Workqueue Bridge Slice",
        f"`PHASE14_LANE_KEY={LANE_KEY}`",
        f"`{SURVEYED_COMMIT}`",
        "`kernel/workqueue_bridge.zig`",
        "`zigux/tests/phase14_workqueue_bridge.zig`",
        "`zigux/tests/phase14_workqueue_reviewability.zig`",
        "eight boundary areas",
        "fifteen review-only audit checkpoints",
        "seven blocked live behaviors",
        "delayed-work timer expiry",
        "flush, drain, and cancellation completion ownership",
        "hotplug-driven worker migration and topology rebinding",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared Phase 14 smoke packet",
        "`zigux/tests/phase14_workqueue_reviewability.zig`",
        "`zigux/tests/phase14_workqueue_bridge.zig`",
        "`zigux/tests/phase14_workqueue_bridge_manifest.json`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` kept explicit as the two boundary-study-only anchors",
        "`kernel/rcu/tree.c` plus `net/core/skbuff.c` kept explicit as the two freeze-in-C-governed anchors",
        "without implying an active deep-core port claim",
    ],
    "zigux/tests/phase14_build.zig": [
        "../../kernel/workqueue_bridge.zig",
        "../../net/core/skbuff_bridge.zig",
    ],
    "zigux/tests/phase14_end_to_end_smoke_manifest.json": [
        "\"zigux/tests/phase14_workqueue_reviewability.zig\"",
        "\"label\": \"phase14-workqueue-reviewability-tests\"",
        "\"root_source\": \"phase14_workqueue_reviewability.zig\"",
        "\"coverage\": \"full_bundle_only\"",
    ],
    "zigux/tests/phase14_workqueue_reviewability.zig": [
        "phase14 shared smoke manifest keeps workqueue reviewability explicit",
        "phase14 workqueue anchor packet keeps the delayed-work governance follow-through explicit",
        "phase14 workqueue survey keeps hotplug and scheduler-visible checkpoints explicit",
        "phase14 workqueue survey keeps reviewer guardrails explicit",
        f"\"lane_key\": \"{LANE_KEY}\"",
        f"\"surveyed_commit\": \"{SURVEYED_COMMIT}\"",
        f"\"blocked_gap\": \"{BLOCKED_GAP}\"",
        "phase14-workqueue-delayed-requeue-governance",
        "phase14-workqueue-scheduler-visible-worker-state-refinement",
        "phase14-workqueue-pending-bit-audit",
    ],
    "zigux/tests/phase14_workqueue_bridge.zig": [
        "phase14-workqueue-live-execution-blocker",
        "blocked_maintenance",
        "delayed-work",
        "scheduler-visible",
    ],
    "kernel/workqueue_bridge.zig": [
        "phase14-workqueue-delayed-requeue-governance",
        "phase14-workqueue-flush-drain-governance",
        "phase14-workqueue-rescuer-mayday-governance",
        "phase14-workqueue-scheduler-visible-worker-state-refinement",
        "hotplug-topology-rebinding",
    ],
}

ABSENT_MARKERS = {
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "phase14-workqueue-pending-bit-audit",
    ],
    "Documentation/zigux/phase14-core-boundary-traceability.md": [
        "phase14-workqueue-pending-bit-audit",
        "lane key: `P14-L01`",
        "`007f00d0c6b6b430bfbb2110555544cc5faefe8b`",
    ],
    "Documentation/zigux/phase14-workqueue-bridge-survey.md": [
        "`make -C zigux phase14-smoke`",
    ],
    "zigux/tests/phase14_workqueue_reviewability.zig": [
        "\"ready_next_gap\": \"phase14-workqueue-pending-bit-audit\"",
    ],
}

MANIFEST_SCALARS = {
    "lane_key": LANE_KEY,
    "phase": "Phase 14",
    "surveyed_commit": SURVEYED_COMMIT,
    "anchor": "kernel/workqueue.c",
}

EXPECTED_ROADMAP_DESTINATIONS = [
    "kernel/workqueue_bridge.zig",
    "zigux/tests/",
    "Documentation/zigux/",
]

EXPECTED_SURVEY_SUMMARY = {
    "workqueue_c_lines": 8439,
    "workqueue_internal_h_lines": 84,
    "test_workqueue_c_lines": 294,
    "preexisting_kernel_export_shim_present": True,
    "preexisting_phase14_build_present": True,
    "preexisting_phase14_make_target_present": True,
    "preexisting_workqueue_bridge_present": True,
    "preexisting_phase14_workqueue_test_present": True,
    "preexisting_phase14_workqueue_manifest_present": True,
    "preexisting_phase14_workqueue_slice_note_present": True,
    "preexisting_phase14_workqueue_survey_note_present": True,
}

EXPECTED_REPLAY = [
    "zig test zigux/tests/phase14_workqueue_reviewability.zig",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]

EXPECTED_GAP_IDS = {
    "phase14-build-gate",
    "phase14-make-target",
    "phase14-kernel-export-shim-foundation",
    "phase14-workqueue-boundary-map-starter",
    "phase14-workqueue-test-gate",
    "phase14-workqueue-slice-note",
    "phase14-workqueue-survey-note",
    "phase14-workqueue-concurrency-audit-outline",
    "phase14-workqueue-max-active-audit",
    "phase14-workqueue-lock-handoff-audit",
    "phase14-workqueue-pending-bit-followup",
    "phase14-workqueue-delayed-submission-alias-followup",
    "phase14-workqueue-delayed-timer-expiry-followup",
    "phase14-workqueue-delayed-requeue-governance",
    "phase14-workqueue-flush-drain-governance",
    "phase14-workqueue-rescuer-mayday-governance",
    "phase14-workqueue-scheduler-visible-worker-state-refinement",
    BLOCKED_GAP,
}

EXPECTED_BLOCKED_STATUS = {
    BLOCKED_GAP: "blocked_on_live_concurrency",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in DIRECT_PACKET_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []

    for rel_path, markers in MARKERS.items():
        text = read_text(root, rel_path)
        label = Path(rel_path).name
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{label}:{marker}")

    for rel_path, markers in ABSENT_MARKERS.items():
        text = read_text(root, rel_path)
        label = Path(rel_path).name
        for marker in markers:
            if marker in text:
                missing_markers.append(f"{label}:unexpected:{marker}")

    manifest_text = read_text(root, "zigux/tests/phase14_workqueue_bridge_manifest.json")
    manifest = json.loads(manifest_text)

    for key, value in MANIFEST_SCALARS.items():
        if manifest.get(key) != value:
            missing_markers.append(f"manifest:{key}={manifest.get(key)!r}")

    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing_markers.append("manifest:roadmap_destinations")

    survey_summary = manifest.get("survey_summary", {})
    for key, value in EXPECTED_SURVEY_SUMMARY.items():
        if survey_summary.get(key) != value:
            missing_markers.append(f"manifest:survey_summary:{key}={survey_summary.get(key)!r}")

    handoff = manifest.get("maintenance_handoff", {})
    if handoff.get("current_lane_posture") != "blocked_maintenance":
        missing_markers.append(
            f"manifest:maintenance_handoff:current_lane_posture={handoff.get('current_lane_posture')!r}"
        )
    if handoff.get("replay_before_trusting") != EXPECTED_REPLAY:
        missing_markers.append("manifest:maintenance_handoff:replay_before_trusting")
    if BLOCKED_GAP not in handoff.get("next_future_target", ""):
        missing_markers.append("manifest:maintenance_handoff:next_future_target")
    if "blocked-maintenance handoff" not in handoff.get("next_future_target", ""):
        missing_markers.append("manifest:maintenance_handoff:bridge_local_handoff")

    gap_index = {
        gap.get("id"): gap for gap in manifest.get("gaps", []) if isinstance(gap, dict)
    }
    if set(gap_index) != EXPECTED_GAP_IDS:
        missing_markers.append("manifest:gaps")

    for gap_id, expected_status in EXPECTED_BLOCKED_STATUS.items():
        gap = gap_index.get(gap_id)
        if gap is None or gap.get("status") != expected_status:
            missing_markers.append(
                f"manifest:gap_status:{gap_id}={None if gap is None else gap.get('status')!r}"
            )

    blocked_count = sum(
        1 for gap in gap_index.values() if gap.get("status") == "blocked_on_live_concurrency"
    )
    if blocked_count != 1:
        missing_markers.append(f"manifest:blocked_on_live_concurrency={blocked_count}")

    starter_count = sum(1 for gap in gap_index.values() if gap.get("status") == "starter_landed")
    if starter_count < 17:
        missing_markers.append(f"manifest:starter_landed={starter_count}")

    if "phase14-workqueue-pending-bit-audit" in manifest_text:
        missing_markers.append("manifest:unexpected:phase14-workqueue-pending-bit-audit")

    return [], missing_markers


def write_fixture(root: Path) -> None:
    manifest = {
        **MANIFEST_SCALARS,
        "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
        "survey_summary": EXPECTED_SURVEY_SUMMARY,
        "maintenance_handoff": {
            "current_lane_posture": "blocked_maintenance",
            "replay_before_trusting": EXPECTED_REPLAY,
            "reopen_conditions": [
                "the dedicated workqueue survey, slice note, manifest, or reviewability test drifts on surveyed commit, blocked gap, blocked-maintenance posture, or blocked live-execution wording",
                "the directly coupled shared smoke or core traceability packet reintroduces a stale lane key, ready-next record, or blocked-gap record for the workqueue anchor",
                "genuinely narrower stay-in-C evidence appears around delayed-work timer expiry, delayed-work requeue governance, flush-drain ownership, hotplug topology rebinding, or scheduler-visible worker-state transitions without implying live execution ownership",
            ],
            "next_future_target": (
                "stay in blocked maintenance unless one of those packet-local reopen conditions fires; "
                f"if a future truthfulness drift is workqueue-local, reread kernel/workqueue_bridge.zig, zigux/tests/phase14_workqueue_bridge.zig, zigux/tests/phase14_workqueue_reviewability.zig, zigux/tests/phase14_workqueue_bridge_manifest.json, Documentation/zigux/phase14-workqueue-bridge-slice.md, and Documentation/zigux/phase14-workqueue-bridge-survey.md together until the bridge-local blocked-maintenance handoff is aligned again for {BLOCKED_GAP}"
            ),
        },
        "gaps": [
            {
                "id": gap_id,
                "status": EXPECTED_BLOCKED_STATUS.get(gap_id, "starter_landed"),
                "kind": "synthetic",
                "zigux_destination": "synthetic",
                "why_now": f"synthetic:{gap_id}",
            }
            for gap_id in sorted(EXPECTED_GAP_IDS)
        ],
    }

    fixture = {
        "Documentation/zigux/phase14-core-boundary-traceability.md": "\n".join(
            MARKERS["Documentation/zigux/phase14-core-boundary-traceability.md"]
        )
        + "\n",
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md": "\n".join(
            MARKERS["Documentation/zigux/phase14-end-to-end-smoke-survey.md"]
        )
        + "\n",
        "Documentation/zigux/phase14-workqueue-bridge-slice.md": "\n".join(
            MARKERS["Documentation/zigux/phase14-workqueue-bridge-slice.md"]
        )
        + "\n",
        "Documentation/zigux/phase14-workqueue-bridge-survey.md": "\n".join(
            MARKERS["Documentation/zigux/phase14-workqueue-bridge-survey.md"]
        )
        + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(
            MARKERS["Documentation/zigux/review-checklist.md"]
        )
        + "\n",
        "kernel/workqueue_bridge.zig": "\n".join(MARKERS["kernel/workqueue_bridge.zig"]) + "\n",
        "zigux/tests/phase14_build.zig": "\n".join(MARKERS["zigux/tests/phase14_build.zig"]) + "\n",
        "zigux/tests/phase14_end_to_end_smoke_manifest.json": "\n".join(
            MARKERS["zigux/tests/phase14_end_to_end_smoke_manifest.json"]
        )
        + "\n",
        "zigux/tests/phase14_workqueue_bridge.zig": "\n".join(
            MARKERS["zigux/tests/phase14_workqueue_bridge.zig"]
        )
        + "\n",
        "zigux/tests/phase14_workqueue_bridge_manifest.json": json.dumps(manifest, indent=2)
        + "\n",
        "zigux/tests/phase14_workqueue_reviewability.zig": "\n".join(
            MARKERS["zigux/tests/phase14_workqueue_reviewability.zig"]
        )
        + "\n",
    }

    for rel_path, content in fixture.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase14_workqueue_reviewability_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase14-workqueue-reviewability-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        case_count = 0

        def expect_missing_marker(expected: str) -> None:
            nonlocal case_count
            _, markers = validate(root)
            if expected not in markers:
                raise SystemExit(
                    "phase14-workqueue-reviewability-self-test:"
                    f"expected_marker_missing:{expected}"
                )
            case_count += 1

        def expect_missing_file(expected: str) -> None:
            nonlocal case_count
            files, _ = validate(root)
            if expected not in files:
                raise SystemExit(
                    "phase14-workqueue-reviewability-self-test:"
                    f"expected_file_missing:{expected}"
                )
            case_count += 1

        def replace_once(rel_path: str, old: str, new: str, expected: str) -> None:
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace(old, new, 1), encoding="utf-8")
            expect_missing_marker(expected)
            path.write_text(original, encoding="utf-8")

        def mutate_manifest(mutator, expected: str) -> None:
            path = root / "zigux/tests/phase14_workqueue_bridge_manifest.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            manifest = json.loads(json.dumps(original))
            mutator(manifest)
            path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            expect_missing_marker(expected)
            path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")

        replace_once(
            "Documentation/zigux/phase14-workqueue-bridge-survey.md",
            f"PHASE14_LANE_KEY={LANE_KEY}",
            "PHASE14_LANE_KEY=P14-L02",
            f"phase14-workqueue-bridge-survey.md:PHASE14_LANE_KEY={LANE_KEY}",
        )
        replace_once(
            "Documentation/zigux/phase14-core-boundary-traceability.md",
            "ready-next gap: none currently recorded",
            "ready-next gap: phase14-workqueue-pending-bit-audit",
            "phase14-core-boundary-traceability.md:unexpected:phase14-workqueue-pending-bit-audit",
        )
        replace_once(
            "Documentation/zigux/phase14-workqueue-bridge-slice.md",
            "fifteen review-only audit checkpoints",
            "fourteen review-only audit checkpoints",
            "phase14-workqueue-bridge-slice.md:fifteen review-only audit checkpoints",
        )
        replace_once(
            "zigux/tests/phase14_workqueue_reviewability.zig",
            f"\"blocked_gap\": \"{BLOCKED_GAP}\"",
            "\"blocked_gap\": \"phase14-workqueue-pending-bit-audit\"",
            "phase14_workqueue_reviewability.zig:\"blocked_gap\": \"phase14-workqueue-live-execution-blocker\"",
        )
        mutate_manifest(
            lambda manifest: manifest["maintenance_handoff"].__setitem__(
                "current_lane_posture", "ready_next"
            ),
            "manifest:maintenance_handoff:current_lane_posture='ready_next'",
        )
        mutate_manifest(
            lambda manifest: manifest["gaps"].append(
                {
                    "id": "phase14-workqueue-pending-bit-audit",
                    "status": "starter_landed",
                    "kind": "synthetic",
                    "zigux_destination": "synthetic",
                    "why_now": "synthetic",
                }
            ),
            "manifest:gaps",
        )

        path = root / "Documentation/zigux/phase14-workqueue-bridge-survey.md"
        original = path.read_text(encoding="utf-8")
        path.unlink()
        expect_missing_file("Documentation/zigux/phase14-workqueue-bridge-survey.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(original, encoding="utf-8")

        print("PHASE14_WORKQUEUE_REVIEWABILITY_PACKET_SELF_TEST=pass")
        print(f"PHASE14_WORKQUEUE_REVIEWABILITY_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 14 workqueue reviewability packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a synthetic fixture tree.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the detected repo root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE14_WORKQUEUE_REVIEWABILITY_PACKET=fail")
        print("MISSING_PHASE14_WORKQUEUE_REVIEWABILITY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE14_WORKQUEUE_REVIEWABILITY_FILES_END")
        return 1

    if missing_markers:
        print("PHASE14_WORKQUEUE_REVIEWABILITY_PACKET=fail")
        print("MISSING_PHASE14_WORKQUEUE_REVIEWABILITY_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE14_WORKQUEUE_REVIEWABILITY_MARKERS_END")
        return 1

    print("PHASE14_WORKQUEUE_REVIEWABILITY_PACKET=pass")
    print(f"PHASE14_WORKQUEUE_REVIEWABILITY_REQUIRED_FILE_COUNT={len(DIRECT_PACKET_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

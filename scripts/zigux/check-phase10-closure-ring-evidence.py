#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parent

RING_MANIFEST_PATH = "zigux/tests/phase10_virtio_ring_manifest.json"
CLOSURE_MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
CLOSURE_NOTE_PATH = "Documentation/zigux/phase10-closure-evidence.md"
RING_DESTINATION = "drivers/virtio/virtio_ring.zig"

BASELINE_RING_HELPERS = [
    "phase10-virtqueue-shape-helper",
    "phase10-used-buffer-polling-helper",
    "phase10-callback-enable-helper",
    "phase10-callback-delay-helper",
    "phase10-notify-prepare-helper",
    "phase10-broken-queue-poll-guard",
    "phase10-queue-reset-helper",
    "phase10-queue-reset-readiness-helper",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def read_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def derived_ring_helpers(ring_manifest: dict) -> list[str]:
    helpers: list[str] = []
    for gap in ring_manifest.get("gaps", []):
        if not isinstance(gap, dict):
            continue
        if gap.get("status") != "starter_landed":
            continue
        if gap.get("zigux_destination") != RING_DESTINATION:
            continue
        gap_id = gap.get("id")
        if isinstance(gap_id, str):
            helpers.append(gap_id)
    return helpers


def validate(root: Path) -> tuple[list[str], list[str]]:
    required_files = [RING_MANIFEST_PATH, CLOSURE_MANIFEST_PATH, CLOSURE_NOTE_PATH]
    missing_files = [path for path in required_files if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    ring_manifest = read_json(root, RING_MANIFEST_PATH)
    closure_manifest = read_json(root, CLOSURE_MANIFEST_PATH)
    closure_note = read_text(root, CLOSURE_NOTE_PATH)

    missing_markers: list[str] = []
    expected_ring_helpers = derived_ring_helpers(ring_manifest)
    closure_ring_helpers = (
        closure_manifest.get("landed_ring_helper_evidence", {})
        .get(RING_MANIFEST_PATH, [])
    )

    if expected_ring_helpers != closure_ring_helpers:
        missing_markers.append("closure_manifest:ring_helper_evidence_parity")

    ring_lane_key = ring_manifest.get("lane_key")
    closure_ring_lane_key = (
        closure_manifest.get("survey_provenance", {})
        .get("lane_keys", {})
        .get("ring")
    )
    if ring_lane_key != closure_ring_lane_key:
        missing_markers.append("closure_manifest:ring_lane_key_parity")

    if RING_MANIFEST_PATH not in closure_manifest.get("roadmap_parity_scoreboard", {}).get(
        "virtqueue_wrappers", {}
    ).get("evidence", []):
        missing_markers.append("closure_manifest:virtqueue_wrappers_evidence")

    if "Documentation/zigux/phase10-virtio-ring-survey.md" not in closure_manifest.get(
        "roadmap_parity_scoreboard", {}
    ).get("virtqueue_wrappers", {}).get("evidence", []):
        missing_markers.append("closure_manifest:virtqueue_wrappers_survey_note")

    for helper_id in expected_ring_helpers:
        if helper_id not in closure_note:
            missing_markers.append(f"closure_note:{helper_id}")

    return missing_files, missing_markers


def write_text(root: Path, rel_path: str, content: str) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def write_json(root: Path, rel_path: str, payload: object) -> None:
    write_text(root, rel_path, json.dumps(payload, indent=2) + "\n")


def baseline_fixture(root: Path) -> None:
    ring_manifest = {
        "lane_key": "P10-L07",
        "gaps": [
            {
                "id": helper_id,
                "status": "starter_landed",
                "zigux_destination": RING_DESTINATION,
            }
            for helper_id in BASELINE_RING_HELPERS
        ]
        + [
            {
                "id": "phase10-mmio-lifecycle-and-irq-paths",
                "status": "blocked_on_risky_transport",
                "zigux_destination": "drivers/virtio/virtio_mmio.zig",
            }
        ],
    }
    closure_manifest = {
        "survey_provenance": {"lane_keys": {"ring": "P10-L07"}},
        "roadmap_parity_scoreboard": {
            "virtqueue_wrappers": {
                "evidence": [
                    "drivers/virtio/virtio_ring.zig",
                    RING_MANIFEST_PATH,
                    "Documentation/zigux/phase10-virtio-ring-survey.md",
                ]
            }
        },
        "landed_ring_helper_evidence": {
            RING_MANIFEST_PATH: list(BASELINE_RING_HELPERS)
        },
    }
    closure_note = "\n".join(
        [
            "# Phase 10 Closure Evidence",
            "The shared closure note keeps the current ring helper ladder explicit.",
        ]
        + [f"- `{helper_id}`" for helper_id in BASELINE_RING_HELPERS]
    )

    write_json(root, RING_MANIFEST_PATH, ring_manifest)
    write_json(root, CLOSURE_MANIFEST_PATH, closure_manifest)
    write_text(root, CLOSURE_NOTE_PATH, closure_note + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_ring_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        baseline_fixture(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-closure-ring-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        closure_manifest_path = tmp_root / CLOSURE_MANIFEST_PATH
        original_closure_manifest = json.loads(
            closure_manifest_path.read_text(encoding="utf-8")
        )

        drift_manifest = json.loads(json.dumps(original_closure_manifest))
        drift_manifest["landed_ring_helper_evidence"][RING_MANIFEST_PATH][-1] = (
            "phase10-broken-queue-recovery-helper"
        )
        write_json(tmp_root, CLOSURE_MANIFEST_PATH, drift_manifest)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:ring_helper_evidence_parity" not in missing_markers:
            raise SystemExit(
                "phase10-closure-ring-self-test:expected_ring_helper_parity_marker_missing"
            )
        write_json(tmp_root, CLOSURE_MANIFEST_PATH, original_closure_manifest)

        drift_manifest = json.loads(json.dumps(original_closure_manifest))
        drift_manifest["survey_provenance"]["lane_keys"]["ring"] = "P10-L08"
        write_json(tmp_root, CLOSURE_MANIFEST_PATH, drift_manifest)
        _, missing_markers = validate(tmp_root)
        if "closure_manifest:ring_lane_key_parity" not in missing_markers:
            raise SystemExit(
                "phase10-closure-ring-self-test:expected_lane_key_marker_missing"
            )
        write_json(tmp_root, CLOSURE_MANIFEST_PATH, original_closure_manifest)

        closure_note_path = tmp_root / CLOSURE_NOTE_PATH
        original_closure_note = closure_note_path.read_text(encoding="utf-8")
        closure_note_path.write_text(
            original_closure_note.replace(
                "- `phase10-queue-reset-readiness-helper`\n", "", 1
            ),
            encoding="utf-8",
        )
        _, missing_markers = validate(tmp_root)
        if "closure_note:phase10-queue-reset-readiness-helper" not in missing_markers:
            raise SystemExit(
                "phase10-closure-ring-self-test:expected_closure_note_marker_missing"
            )

    print("PHASE10_CLOSURE_RING_EVIDENCE_SELF_TEST=pass")
    print("PHASE10_CLOSURE_RING_EVIDENCE_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 10 closure packet against the live ring packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in drift checks against a synthetic fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE10_CLOSURE_RING_EVIDENCE=fail")
        print("MISSING_PHASE10_CLOSURE_RING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_RING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE10_CLOSURE_RING_EVIDENCE=fail")
        print("MISSING_PHASE10_CLOSURE_RING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CLOSURE_RING_MARKERS_END")
        return 1

    print("PHASE10_CLOSURE_RING_EVIDENCE=pass")
    print(f"PHASE10_CLOSURE_RING_EXPECTED_HELPER_COUNT={len(BASELINE_RING_HELPERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

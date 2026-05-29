#!/usr/bin/env python3
"""Check that the Phase 10 ring survey replay stays visible in scoreboard evidence."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path("zigux/tests/phase10_closure_manifest.json")
CLOSURE_NOTE_PATH = Path("Documentation/zigux/phase10-closure-evidence.md")
RING_MANIFEST_PATH = Path("zigux/tests/phase10_virtio_ring_manifest.json")

RING_SURVEY_REPLAY = "zigux/tests/phase10_virtio_ring_survey.zig"
RING_SURVEY_GAP_ID = "phase10-virtio-ring-survey-gate"
RING_SURVEY_NOTE = "Documentation/zigux/phase10-virtio-ring-survey.md"
RING_MANIFEST = "zigux/tests/phase10_virtio_ring_manifest.json"

MANIFEST_TEST_MARKERS = [
    RING_SURVEY_REPLAY,
    RING_MANIFEST,
    RING_SURVEY_NOTE,
]

CLOSURE_NOTE_MARKERS = [
    RING_SURVEY_REPLAY,
    RING_MANIFEST,
    RING_SURVEY_NOTE,
    "virtqueue_wrappers=starter_landed",
]

RING_PACKET_MARKERS = [
    RING_SURVEY_GAP_ID,
    RING_SURVEY_REPLAY,
    "starter_landed",
    "validation",
]


def read_json(root: Path, rel_path: Path) -> dict:
    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def require_list_members(drift: list[str], label: str, value: object, required: list[str]) -> None:
    if not isinstance(value, list) or not value:
        drift.append(f"{label}:missing")
        return
    for item in required:
        if item not in value:
            drift.append(f"{label}:{item}:missing")


def require_text_markers(drift: list[str], label: str, text: str, required: list[str]) -> None:
    for marker in required:
        if marker not in text:
            drift.append(f"{label}:{marker}:missing")


def collect_drift(root: Path) -> tuple[list[str], list[str]]:
    required_files = [MANIFEST_PATH, CLOSURE_NOTE_PATH, RING_MANIFEST_PATH]
    missing_files = [str(path) for path in required_files if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    drift: list[str] = []
    manifest = read_json(root, MANIFEST_PATH)
    ring_manifest = read_json(root, RING_MANIFEST_PATH)
    closure_note = (root / CLOSURE_NOTE_PATH).read_text(encoding="utf-8")

    require_list_members(drift, "phase10_closure_manifest.tests", manifest.get("tests"), [RING_SURVEY_REPLAY])

    scoreboard = manifest.get("roadmap_parity_scoreboard")
    if not isinstance(scoreboard, dict):
        drift.append("roadmap_parity_scoreboard:missing")
    else:
        virtqueue = scoreboard.get("virtqueue_wrappers")
        if not isinstance(virtqueue, dict):
            drift.append("roadmap_parity_scoreboard.virtqueue_wrappers:missing")
        else:
            require_list_members(
                drift,
                "roadmap_parity_scoreboard.virtqueue_wrappers.evidence",
                virtqueue.get("evidence"),
                [RING_MANIFEST, RING_SURVEY_NOTE],
            )

    require_text_markers(drift, "phase10_closure_evidence", closure_note, CLOSURE_NOTE_MARKERS)

    gap = next(
        (
            item
            for item in ring_manifest.get("gaps", [])
            if isinstance(item, dict) and item.get("id") == RING_SURVEY_GAP_ID
        ),
        None,
    )
    if not isinstance(gap, dict):
        drift.append(f"phase10_virtio_ring_manifest.gaps:{RING_SURVEY_GAP_ID}:missing")
    else:
        for key, expected in (
            ("status", "starter_landed"),
            ("kind", "validation"),
            ("zigux_destination", RING_SURVEY_REPLAY),
        ):
            actual = gap.get(key)
            if actual != expected:
                drift.append(f"phase10_virtio_ring_manifest.gaps:{RING_SURVEY_GAP_ID}:{key}:{actual!r}!={expected!r}")
        why_now = gap.get("why_now")
        if not isinstance(why_now, str) or "survey replay" not in why_now:
            drift.append(f"phase10_virtio_ring_manifest.gaps:{RING_SURVEY_GAP_ID}:why_now:missing_survey_replay")

    return [], drift


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture(root: Path) -> None:
    closure_manifest = {
        "tests": [RING_SURVEY_REPLAY],
        "roadmap_parity_scoreboard": {
            "virtqueue_wrappers": {"evidence": [RING_MANIFEST, RING_SURVEY_NOTE]},
        },
    }
    ring_manifest = {
        "gaps": [
            {
                "id": RING_SURVEY_GAP_ID,
                "status": "starter_landed",
                "kind": "validation",
                "zigux_destination": RING_SURVEY_REPLAY,
                "why_now": "The dedicated ring survey replay is directly readable evidence.",
            }
        ]
    }
    closure_note = "\n".join(CLOSURE_NOTE_MARKERS) + "\n"
    write_text(root / MANIFEST_PATH, json.dumps(closure_manifest, indent=2) + "\n")
    write_text(root / RING_MANIFEST_PATH, json.dumps(ring_manifest, indent=2) + "\n")
    write_text(root / CLOSURE_NOTE_PATH, closure_note)


def expect_drift(root: Path, expected: str) -> None:
    _, drift = collect_drift(root)
    if expected not in drift:
        actual = ",".join(drift) if drift else "none"
        raise SystemExit(f"phase10-ring-survey-scoreboard-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_survey_scoreboard_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        missing_files, drift = collect_drift(root)
        if missing_files or drift:
            raise SystemExit(
                "phase10-ring-survey-scoreboard-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:drift={','.join(drift) or 'none'}"
            )
        cases = 1

        manifest_path = root / MANIFEST_PATH
        manifest = read_json(root, MANIFEST_PATH)
        manifest["tests"] = ["zigux/tests/phase10_virtio_ring.zig"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_drift(root, f"phase10_closure_manifest.tests:{RING_SURVEY_REPLAY}:missing")
        cases += 1

        write_fixture(root)
        manifest = read_json(root, MANIFEST_PATH)
        manifest["roadmap_parity_scoreboard"]["virtqueue_wrappers"]["evidence"] = [RING_MANIFEST]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_drift(
            root,
            f"roadmap_parity_scoreboard.virtqueue_wrappers.evidence:{RING_SURVEY_NOTE}:missing",
        )
        cases += 1

        write_fixture(root)
        note_path = root / CLOSURE_NOTE_PATH
        note_path.write_text(note_path.read_text(encoding="utf-8").replace(RING_SURVEY_REPLAY, "missing-ring-survey.zig"), encoding="utf-8")
        expect_drift(root, f"phase10_closure_evidence:{RING_SURVEY_REPLAY}:missing")
        cases += 1

        write_fixture(root)
        ring_manifest_path = root / RING_MANIFEST_PATH
        ring_manifest = read_json(root, RING_MANIFEST_PATH)
        ring_manifest["gaps"][0]["status"] = "blocked_on_risky_transport"
        write_text(ring_manifest_path, json.dumps(ring_manifest, indent=2) + "\n")
        expect_drift(
            root,
            f"phase10_virtio_ring_manifest.gaps:{RING_SURVEY_GAP_ID}:status:'blocked_on_risky_transport'!='starter_landed'",
        )
        cases += 1

    print("PHASE10_RING_SURVEY_SCOREBOARD_SELF_TEST=pass")
    print(f"PHASE10_RING_SURVEY_SCOREBOARD_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 10 ring survey scoreboard evidence.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    missing_files, drift = collect_drift(args.repo_root)
    if missing_files:
        print("PHASE10_RING_SURVEY_SCOREBOARD=fail")
        print("MISSING_PHASE10_RING_SURVEY_SCOREBOARD_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_RING_SURVEY_SCOREBOARD_FILES_END")
        return 1
    if drift:
        print("PHASE10_RING_SURVEY_SCOREBOARD=fail")
        print("PHASE10_RING_SURVEY_SCOREBOARD_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_RING_SURVEY_SCOREBOARD_DRIFT_END")
        return 1
    print("PHASE10_RING_SURVEY_SCOREBOARD=pass")
    print(f"PHASE10_RING_SURVEY_SCOREBOARD_REQUIRED_MANIFEST_MARKERS={len(MANIFEST_TEST_MARKERS)}")
    print(f"PHASE10_RING_SURVEY_SCOREBOARD_REQUIRED_NOTE_MARKERS={len(CLOSURE_NOTE_MARKERS)}")
    print(f"PHASE10_RING_SURVEY_SCOREBOARD_REQUIRED_RING_PACKET_MARKERS={len(RING_PACKET_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

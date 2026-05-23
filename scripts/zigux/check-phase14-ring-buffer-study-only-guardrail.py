#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
NOTE_PATH = "Documentation/zigux/phase14-ring-buffer-survey.md"
MANIFEST_PATH = "zigux/tests/phase14_ring_buffer_manifest.json"

NOTE_MARKERS = [
    "`PHASE14_STATUS=study_only`",
    "The Phase 14 roadmap explicitly names `kernel/trace/ring_buffer.c` as a boundary-study target first, not a rewrite target.",
    "It also says `kernel/trace/ring_buffer.zig` is only appropriate if years of evidence justify it.",
    "- landed `phase14-ring-buffer-boundary-decision-checklist`",
    "- blocked `phase14-ring-buffer-zig-port-blocker`",
    "- current lane posture: `maintenance_mode`",
    "genuinely narrower stay-in-C evidence appears around reserve or commit publication, remote-reader metadata, reader-page consume, read-page extraction, or tracefs reader serialization that could justify a new dedicated survey audit without implying `kernel/trace/ring_buffer.zig`",
    "Keep this ring-buffer lane parked unless the shared Phase 14 smoke packet, this survey note, the manifest, or the returned survey companions drift.",
]

REQUIRED_MANIFEST_VALUES = {
    ("lane_key",): "P14-L08",
    ("study_only_governance", "status_bucket"): "study_only",
    ("study_only_governance", "blocked_gap"): "phase14-ring-buffer-zig-port-blocker",
    ("study_only_governance", "lane_reopen_scope"): "same_packet_truthfulness_repairs_only",
    ("maintenance_handoff", "current_lane_posture"): "maintenance_mode",
    ("maintenance_handoff", "replay_before_trusting"): [
        "zig test zigux/tests/phase14_ring_buffer_survey.zig",
        "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    ],
}

REQUIRED_DECISION_IDS = [
    "reserve-commit-publication",
    "remote-reader-metadata",
    "tracefs-reader-serialization-boundary",
]

FORBIDDEN_NOTE_MARKERS = [
    "parity claim",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / NOTE_PATH).exists() and (candidate / MANIFEST_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    note = root / NOTE_PATH
    manifest = root / MANIFEST_PATH

    if not note.exists():
        failures.append(f"missing_file:{NOTE_PATH}")
    if not manifest.exists():
        failures.append(f"missing_file:{MANIFEST_PATH}")
    if failures:
        return failures

    note_text = note.read_text(encoding="utf-8")
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            failures.append(f"missing_marker:{NOTE_PATH}:{marker}")
    for marker in FORBIDDEN_NOTE_MARKERS:
        if marker in note_text:
            failures.append(f"forbidden_marker:{NOTE_PATH}:{marker}")

    try:
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid_json:{MANIFEST_PATH}:{exc.msg}")
        return failures

    for path, expected in REQUIRED_MANIFEST_VALUES.items():
        try:
            actual = lookup_path(manifest_payload, path)
        except KeyError:
            failures.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            failures.append(
                "manifest_value_mismatch:"
                f"{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )

    try:
        decision_checklist = lookup_path(manifest_payload, ("decision_checklist",))
    except KeyError:
        failures.append("missing_manifest_key:decision_checklist")
        return failures

    checklist_ids = {entry.get("id") for entry in decision_checklist if isinstance(entry, dict)}
    for decision_id in REQUIRED_DECISION_IDS:
        if decision_id not in checklist_ids:
            failures.append(f"missing_decision_id:{decision_id}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FIXTURE_NOTE = """# Phase 14 Ring Buffer Survey
This document records the bounded Phase 14 survey lane around `kernel/trace/ring_buffer.c`.

## Status
- `PHASE14_STATUS=study_only`

## Why this slice exists
The Phase 14 roadmap explicitly names `kernel/trace/ring_buffer.c` as a boundary-study target first, not a rewrite target.
It also says `kernel/trace/ring_buffer.zig` is only appropriate if years of evidence justify it.

## Maintenance-Mode Handoff
- current lane posture: `maintenance_mode`
- reopen only when one of the packet-local conditions below becomes true:
  - genuinely narrower stay-in-C evidence appears around reserve or commit publication, remote-reader metadata, reader-page consume, read-page extraction, or tracefs reader serialization that could justify a new dedicated survey audit without implying `kernel/trace/ring_buffer.zig`

## Recorded gaps
- landed `phase14-ring-buffer-boundary-decision-checklist`
- blocked `phase14-ring-buffer-zig-port-blocker`

## Next bounded step
Keep this ring-buffer lane parked unless the shared Phase 14 smoke packet, this survey note, the manifest, or the returned survey companions drift.
"""

FIXTURE_MANIFEST = {
    "lane_key": "P14-L08",
    "study_only_governance": {
        "status_bucket": "study_only",
        "blocked_gap": "phase14-ring-buffer-zig-port-blocker",
        "lane_reopen_scope": "same_packet_truthfulness_repairs_only",
    },
    "maintenance_handoff": {
        "current_lane_posture": "maintenance_mode",
        "replay_before_trusting": [
            "zig test zigux/tests/phase14_ring_buffer_survey.zig",
            "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
        ],
    },
    "decision_checklist": [
        {"id": "reserve-commit-publication"},
        {"id": "remote-reader-metadata"},
        {"id": "tracefs-reader-serialization-boundary"},
    ],
}


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-ring-buffer-guardrail-"))
    try:
        write_text(base / NOTE_PATH, FIXTURE_NOTE)
        write_text(base / MANIFEST_PATH, json.dumps(FIXTURE_MANIFEST, indent=2) + "\n")
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        cases = [
            (
                "remove-status",
                NOTE_PATH,
                "`PHASE14_STATUS=study_only`",
                f"missing_marker:{NOTE_PATH}:`PHASE14_STATUS=study_only`",
            ),
            (
                "remove-roadmap-caution",
                NOTE_PATH,
                "It also says `kernel/trace/ring_buffer.zig` is only appropriate if years of evidence justify it.",
                "missing_marker:Documentation/zigux/phase14-ring-buffer-survey.md:It also says `kernel/trace/ring_buffer.zig` is only appropriate if years of evidence justify it.",
            ),
            (
                "remove-maintenance-posture",
                NOTE_PATH,
                "- current lane posture: `maintenance_mode`",
                "missing_marker:Documentation/zigux/phase14-ring-buffer-survey.md:- current lane posture: `maintenance_mode`",
            ),
            (
                "remove-lane-key",
                MANIFEST_PATH,
                '"lane_key": "P14-L08"',
                "missing_manifest_key:lane_key",
            ),
        ]

        for name, rel_path, marker, expected in cases:
            write_text(base / NOTE_PATH, FIXTURE_NOTE)
            write_text(base / MANIFEST_PATH, json.dumps(FIXTURE_MANIFEST, indent=2) + "\n")
            target = base / rel_path
            text = target.read_text(encoding="utf-8")
            if rel_path == MANIFEST_PATH:
                payload = json.loads(text)
                if name == "remove-lane-key":
                    payload.pop("lane_key", None)
                write_text(target, json.dumps(payload, indent=2) + "\n")
            else:
                write_text(target, text.replace(marker, "", 1))
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_text(base / NOTE_PATH, FIXTURE_NOTE + "\nparity claim\n")
        write_text(base / MANIFEST_PATH, json.dumps(FIXTURE_MANIFEST, indent=2) + "\n")
        failures = validate(base)
        if f"forbidden_marker:{NOTE_PATH}:parity claim" not in failures:
            raise SystemExit(f"expected forbidden marker failure, got {failures!r}")

        payload = dict(FIXTURE_MANIFEST)
        payload["decision_checklist"] = [{"id": "reserve-commit-publication"}]
        write_text(base / NOTE_PATH, FIXTURE_NOTE)
        write_text(base / MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        failures = validate(base)
        if "missing_decision_id:remote-reader-metadata" not in failures:
            raise SystemExit(f"expected missing decision id failure, got {failures!r}")

        print("PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL_SELF_TEST=pass")
        print("PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the dedicated Phase 14 ring-buffer study-only packet stays "
            "aligned with its maintenance-mode stay-in-C guardrail."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL=fail")
        print("PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL_DRIFT_END")
        return 1

    print("PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL=pass")
    print(f"PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE14_RING_BUFFER_STUDY_ONLY_GUARDRAIL_DECISION_ID_COUNT={len(REQUIRED_DECISION_IDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
NOTE_PATH = "Documentation/zigux/phase14-workqueue-bridge-survey.md"
MANIFEST_PATH = "zigux/tests/phase14_workqueue_bridge_manifest.json"

GUARDRAIL_MARKER = (
    "- manifest-backed guardrail: `phase14-workqueue-study-only-guardrail` keeps this "
    "study-only packet fail-closed until the same bridge-local packet carries narrower "
    "stay-in-C evidence instead of a lighter bridge-presence or shared-route claim."
)
REQUIRED_EVIDENCE_HEADING = "- required evidence before any trust promotion:"
REQUIRED_EVIDENCE_MARKERS = [
    "- direct bridge-local trust gate: `zig test zigux/tests/phase14_workqueue_reviewability.zig`",
    "- bridge-local reread of `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `Documentation/zigux/phase14-workqueue-bridge-slice.md`, and `Documentation/zigux/phase14-workqueue-bridge-survey.md`",
    "- explicit blocker retention for `phase14-workqueue-live-execution-blocker` together with the current `blocked_maintenance` posture",
]
RETURN_TO_BLOCKED_HEADING = "- automatic return-to-blocked triggers:"
RETURN_TO_BLOCKED_MARKERS = [
    "- any wording that treats `make -C zigux phase14-validate` or shared packet-local validation as a replacement for the direct bridge-local trust gate",
    "- missing `phase14-workqueue-live-execution-blocker`, `blocked_maintenance`, or `shared_packet_local_only` wording in the active survey or manifest",
    "- any claim of live worker execution, callback dispatch ownership, flush or drain completion ownership, delayed-work requeue control, scheduler-visible worker-state parity, rescuer execution ownership, or hotplug-driven topology rebinding ownership",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

REQUIRED_NOTE_MARKERS = [
    "`PHASE14_STATUS=blocked_maintenance`",
    "`PHASE14_LANE_KEY=P14-L04`",
    "`PHASE14_ANCHOR=kernel/workqueue.c`",
    "`PHASE14_CURRENT_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`",
    "`PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
    "`PHASE14_BLOCKER=phase14-workqueue-live-execution-blocker`",
    "the bridge-local trusted rerun still stops at `zig test zigux/tests/phase14_workqueue_reviewability.zig`, while `make -C zigux phase14-validate` remains the broader shared packet-local validation route rather than bridge-local proof",
    GUARDRAIL_MARKER,
    "`scripts/zigux/check-phase14-workqueue-study-only-guardrail.py`",
    REQUIRED_EVIDENCE_HEADING,
    *REQUIRED_EVIDENCE_MARKERS,
    RETURN_TO_BLOCKED_HEADING,
    *RETURN_TO_BLOCKED_MARKERS,
]

MANIFEST_REQUIRED_MARKERS = [
    '"lane_key": "P14-L04"',
    '"anchor": "kernel/workqueue.c"',
    '"current_lane_posture": "blocked_maintenance"',
    '"productization_posture": "shared_packet_local_only"',
    '"shared_packet_local_validation": "make -C zigux phase14-validate"',
    '"python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py --self-test"',
    '"python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py"',
    '"phase14-workqueue-study-only-guardrail"',
    '"direct_bridge_local_trust_gate": "zig test zigux/tests/phase14_workqueue_reviewability.zig"',
    '"phase14-workqueue-live-execution-blocker"',
]

FORBIDDEN_NOTE_MARKERS = [
    "returned make-backed focused workqueue route",
]


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
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            failures.append(f"missing_note_marker:{marker}")
    for marker in FORBIDDEN_NOTE_MARKERS:
        if marker in note_text:
            failures.append(f"forbidden_note_marker:{marker}")

    manifest_text = manifest.read_text(encoding="utf-8")
    for marker in MANIFEST_REQUIRED_MARKERS:
        if marker not in manifest_text:
            failures.append(f"missing_manifest_marker:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FIXTURE_NOTE = """# Phase 14 Workqueue Bridge Survey
## Status
- `PHASE14_STATUS=blocked_maintenance`
- `PHASE14_LANE_KEY=P14-L04`
- `PHASE14_ANCHOR=kernel/workqueue.c`
- `PHASE14_CURRENT_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`
- `PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`
- `PHASE14_BLOCKER=phase14-workqueue-live-execution-blocker`
- the bridge-local trusted rerun still stops at `zig test zigux/tests/phase14_workqueue_reviewability.zig`, while `make -C zigux phase14-validate` remains the broader shared packet-local validation route rather than bridge-local proof
## Study-Only Guardrail
""" + GUARDRAIL_MARKER + """
- machine-check surface: `scripts/zigux/check-phase14-workqueue-study-only-guardrail.py` keeps the dedicated survey and manifest fail-closed on the lane key, blocked-maintenance posture, bridge-local trust gate, shared packet-local validation posture, blocked gap, and required reread evidence.
""" + REQUIRED_EVIDENCE_HEADING + """
""" + "\n".join(f"  {marker}" for marker in REQUIRED_EVIDENCE_MARKERS) + """
""" + RETURN_TO_BLOCKED_HEADING + """
""" + "\n".join(f"  {marker}" for marker in RETURN_TO_BLOCKED_MARKERS) + """
"""

FIXTURE_MANIFEST = """{
  "lane_key": "P14-L04",
  "anchor": "kernel/workqueue.c",
  "maintenance_handoff": {
    "current_lane_posture": "blocked_maintenance",
    "productization_posture": "shared_packet_local_only",
    "productization_exact_checks": [
      "python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py --self-test",
      "python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py"
    ]
  },
  "study_only_guardrail": {
    "guardrail_id": "phase14-workqueue-study-only-guardrail",
    "direct_bridge_local_trust_gate": "zig test zigux/tests/phase14_workqueue_reviewability.zig",
    "shared_packet_local_validation": "make -C zigux phase14-validate",
    "required_evidence": [
      "retain phase14-workqueue-live-execution-blocker with blocked_maintenance posture"
    ]
  },
  "gaps": [
    {
      "id": "phase14-workqueue-live-execution-blocker"
    }
  ]
}
"""


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-workqueue-guardrail-"))
    try:
        write_text(base / NOTE_PATH, FIXTURE_NOTE)
        write_text(base / MANIFEST_PATH, FIXTURE_MANIFEST)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        cases = [
            (NOTE_PATH, "`PHASE14_LANE_KEY=P14-L04`", "missing_note_marker:`PHASE14_LANE_KEY=P14-L04`"),
            (NOTE_PATH, GUARDRAIL_MARKER, f"missing_note_marker:{GUARDRAIL_MARKER}"),
            (NOTE_PATH, REQUIRED_EVIDENCE_HEADING, f"missing_note_marker:{REQUIRED_EVIDENCE_HEADING}"),
            (NOTE_PATH, RETURN_TO_BLOCKED_MARKERS[0], f"missing_note_marker:{RETURN_TO_BLOCKED_MARKERS[0]}"),
            (MANIFEST_PATH, '"phase14-workqueue-study-only-guardrail"', 'missing_manifest_marker:"phase14-workqueue-study-only-guardrail"'),
            (MANIFEST_PATH, '"shared_packet_local_validation": "make -C zigux phase14-validate"', 'missing_manifest_marker:"shared_packet_local_validation": "make -C zigux phase14-validate"'),
            (MANIFEST_PATH, '"python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py --self-test"', 'missing_manifest_marker:"python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py --self-test"'),
            (MANIFEST_PATH, '"python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py"', 'missing_manifest_marker:"python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py"'),
        ]
        for rel_path, marker, expected in cases:
            write_text(base / NOTE_PATH, FIXTURE_NOTE)
            write_text(base / MANIFEST_PATH, FIXTURE_MANIFEST)
            target = base / rel_path
            target.write_text(target.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_text(base / NOTE_PATH, FIXTURE_NOTE + "\n- returned make-backed focused workqueue route\n")
        write_text(base / MANIFEST_PATH, FIXTURE_MANIFEST)
        failures = validate(base)
        if "forbidden_note_marker:returned make-backed focused workqueue route" not in failures:
            raise SystemExit(f"expected forbidden marker failure, got {failures!r}")

        print("PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL_SELF_TEST=pass")
        print("PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL_SELF_TEST_CASE_COUNT=9")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the dedicated Phase 14 workqueue survey and manifest stay aligned "
            "with the current study-only guardrail and direct bridge-local trust gate."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL=fail")
        print("PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL_DRIFT_END")
        return 1

    print("PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL=pass")
    print(f"PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL_NOTE_MARKER_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    print(f"PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL_MANIFEST_MARKER_COUNT={len(MANIFEST_REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

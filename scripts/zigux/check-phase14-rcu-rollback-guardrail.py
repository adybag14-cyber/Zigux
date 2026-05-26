#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
NOTE_PATH = "Documentation/zigux/phase14-rcu-tree-survey.md"
MANIFEST_PATH = "zigux/tests/phase14_rcu_tree_manifest.json"

ROLLBACK_THRESHOLD_MARKER = (
    "- manifest-backed guardrail: `phase14-rcu-tree-rollback-threshold-guardrail` "
    "keeps this freeze-in-C packet fail-closed until the same review packet carries "
    "the required reopen evidence instead of a lighter status-review claim."
)
COMPANION_CONFIRMATION_HEADING = (
    "executable packet companions confirmed on current `master` through public GitHub fallback:"
)
COMPANION_PARTIAL_MARKER = (
    "authenticated contents-path readback still stays partial for those executable companions"
)
DIRECT_PACKET_SURFACES_HEADING = "directly readable dedicated packet surfaces on current `master`:"
DIRECT_BRIDGE_SURFACE_MARKER = "  - `kernel/rcu/tree_bridge.zig`"
OWNER_MAP_TIEBACK_HEADING = (
    "- shared Phase 14 reminder surfaces that still carry the bounded owner-map tie-back:"
)
OWNER_MAP_TIEBACK_MARKERS = [
    "- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "- `Documentation/zigux/phase14-core-boundary-traceability.md`",
]
REQUIRED_EVIDENCE_HEADING = "- required evidence before any status review:"
REQUIRED_EVIDENCE_MARKERS = [
    "- `Architecture Council` reopen record linked from the active review packet",
    "- parity scorecard evidence and benchmark notes attached to the same review packet",
    "- validation replay command and evidence archive path recorded beside the latest blocker disposition",
]
RETURN_TO_BLOCKED_HEADING = "- automatic return-to-blocked triggers:"
RETURN_TO_BLOCKED_MARKERS = [
    "- any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the `Architecture Council` reopen record",
    "- missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
    "- freeze-map, survey note, or dedicated-check drift that drops the blocked bridge disposition, the companion-readback warning, or the rollback owner",
]
MANIFEST_REQUIRED_MARKERS = [
    '"lane_key": "P14-L16"',
    '"anchor": "kernel/rcu/tree.c"',
    '"rollback_owner": "Repo Tooling Pod"',
    '"phase14-rcu-tree-rollback-threshold-guardrail"',
]
MANIFEST_REQUIRED_ROLLBACK_FIELDS = {
    "status_bucket": "freeze_in_c",
    "review_blocker_status": "blocked_on_stay_in_c_evidence",
    "owner": "Core-Adjacent Pod",
    "rollback_owner": "Repo Tooling Pod",
    "required_evidence": [
        "Architecture Council reopen record linked from the reviewable packet",
        "parity scorecard evidence and benchmark notes attached to the reviewable packet",
        "validation replay command plus evidence archive path recorded beside the blocker disposition",
    ],
    "rollback_triggers": [
        "any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record",
        "missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
        "freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner",
    ],
}
MANIFEST_REQUIRED_SUMMARY_FLAGS = {
    "rollback_threshold_note_present": True,
    "rollback_threshold_checklist_present": True,
    "rollback_threshold_freeze_map_rule_present": True,
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / NOTE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

REQUIRED_MARKERS = [
    "`PHASE14_LANE_KEY=P14-L16`",
    "`PHASE14_STATUS_BUCKET=freeze_in_c`",
    "`PHASE14_ANCHOR=kernel/rcu/tree.c`",
    "`PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker`",
    DIRECT_PACKET_SURFACES_HEADING,
    DIRECT_BRIDGE_SURFACE_MARKER,
    COMPANION_CONFIRMATION_HEADING,
    "`zigux/tests/phase14_rcu_tree_manifest.json`",
    "`zigux/tests/phase14_rcu_tree_survey.zig`",
    COMPANION_PARTIAL_MARKER,
    OWNER_MAP_TIEBACK_HEADING,
    *OWNER_MAP_TIEBACK_MARKERS,
    "dedicated rollback guard surface:",
    "`scripts/zigux/check-phase14-rcu-rollback-guardrail.py`",
    "`phase14-rcu-tree-rollback-threshold-guardrail`",
    ROLLBACK_THRESHOLD_MARKER,
    "rollback owner: `Repo Tooling Pod`",
    REQUIRED_EVIDENCE_HEADING,
    *REQUIRED_EVIDENCE_MARKERS,
    RETURN_TO_BLOCKED_HEADING,
    *RETURN_TO_BLOCKED_MARKERS,
]

FORBIDDEN_MARKERS = [
    "current review packet:",
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
    for marker in REQUIRED_MARKERS:
        if marker not in note_text:
            failures.append(f"missing_marker:{marker}")
    for marker in FORBIDDEN_MARKERS:
        if marker in note_text:
            failures.append(f"forbidden_marker:{marker}")

    manifest_text = manifest.read_text(encoding="utf-8")
    for marker in MANIFEST_REQUIRED_MARKERS:
        if marker not in manifest_text:
            failures.append(f"missing_manifest_marker:{marker}")

    try:
        manifest_payload = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        failures.append(f"invalid_manifest_json:{exc.msg}")
        return failures

    rollback_threshold = manifest_payload.get("rollback_threshold")
    if not isinstance(rollback_threshold, dict):
        failures.append("missing_manifest_object:rollback_threshold")
    else:
        for key, expected in MANIFEST_REQUIRED_ROLLBACK_FIELDS.items():
            actual = rollback_threshold.get(key)
            if actual != expected:
                failures.append(
                    f"manifest_rollback_threshold_mismatch:{key}:expected={expected!r}:actual={actual!r}"
                )

    survey_summary = manifest_payload.get("survey_summary")
    if not isinstance(survey_summary, dict):
        failures.append("missing_manifest_object:survey_summary")
    else:
        for key, expected in MANIFEST_REQUIRED_SUMMARY_FLAGS.items():
            actual = survey_summary.get(key)
            if actual != expected:
                failures.append(
                    f"manifest_survey_summary_mismatch:{key}:expected={expected!r}:actual={actual!r}"
                )

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FIXTURE_NOTE = """# Phase 14 RCU Tree Survey
This document records the current Phase 14 boundary-study packet for `kernel/rcu/tree.c` as it exists on verified `master`.
## Status
- `PHASE14_LANE_KEY=P14-L16`
- `PHASE14_STATUS_BUCKET=freeze_in_c`
- `PHASE14_ANCHOR=kernel/rcu/tree.c`
- `PHASE14_ROADMAP_DESTINATION=kernel/rcu/tree_bridge.zig`
- `PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker`
- survey provenance captured against verified `master` head `4c889233d157960514b241bcd5aff7cac5fda312`
- """ + DIRECT_PACKET_SURFACES_HEADING + """
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `kernel/rcu/tree_bridge.zig`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- """ + COMPANION_CONFIRMATION_HEADING + """
  - `zigux/tests/phase14_rcu_tree_manifest.json`
  - `zigux/tests/phase14_rcu_tree_survey.zig`
- authenticated contents-path readback still stays partial for those executable companions, so this note keeps the freeze-in-C blocker as the owner surface rather than claiming restored local replay or ownership
- dedicated rollback guard surface:
  - `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`
## Exact evidence captured
""" + OWNER_MAP_TIEBACK_HEADING + """
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
## Rollback guardrail
""" + ROLLBACK_THRESHOLD_MARKER + """
- machine-check surface: `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` keeps the dedicated note fail-closed on its lane key, blocked gap, companion-readback wording, rollback owner, and required reopen evidence.
- rollback owner: `Repo Tooling Pod`
""" + REQUIRED_EVIDENCE_HEADING + """
""" + "\n".join(f"  {marker}" for marker in REQUIRED_EVIDENCE_MARKERS) + """
""" + RETURN_TO_BLOCKED_HEADING + """
""" + "\n".join(f"  {marker}" for marker in RETURN_TO_BLOCKED_MARKERS) + """
"""

FIXTURE_MANIFEST = """{
  "lane_key": "P14-L16",
  "anchor": "kernel/rcu/tree.c",
  "survey_summary": {
    "rollback_threshold_note_present": true,
    "rollback_threshold_checklist_present": true,
    "rollback_threshold_freeze_map_rule_present": true
  },
  "rollback_threshold": {
    "status_bucket": "freeze_in_c",
    "review_blocker_status": "blocked_on_stay_in_c_evidence",
    "owner": "Core-Adjacent Pod",
    "rollback_owner": "Repo Tooling Pod",
    "required_evidence": [
      "Architecture Council reopen record linked from the reviewable packet",
      "parity scorecard evidence and benchmark notes attached to the reviewable packet",
      "validation replay command plus evidence archive path recorded beside the blocker disposition"
    ],
    "rollback_triggers": [
      "any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record",
      "missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
      "freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner"
    ]
  },
  "gaps": [
    {
      "id": "phase14-rcu-tree-rollback-threshold-guardrail"
    }
  ]
}
"""


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-rcu-guardrail-"))
    try:
        write_text(base / NOTE_PATH, FIXTURE_NOTE)
        write_text(base / MANIFEST_PATH, FIXTURE_MANIFEST)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        cases = [
            ("remove-note-lane-key", NOTE_PATH, "`PHASE14_LANE_KEY=P14-L16`", "missing_marker:`PHASE14_LANE_KEY=P14-L16`"),
            (
                "remove-direct-bridge-surface",
                NOTE_PATH,
                DIRECT_BRIDGE_SURFACE_MARKER,
                f"missing_marker:{DIRECT_BRIDGE_SURFACE_MARKER}",
            ),
            (
                "remove-companion-heading",
                NOTE_PATH,
                COMPANION_CONFIRMATION_HEADING,
                f"missing_marker:{COMPANION_CONFIRMATION_HEADING}",
            ),
            (
                "remove-companion-partial-marker",
                NOTE_PATH,
                COMPANION_PARTIAL_MARKER,
                f"missing_marker:{COMPANION_PARTIAL_MARKER}",
            ),
            (
                "remove-owner-map-tieback-heading",
                NOTE_PATH,
                OWNER_MAP_TIEBACK_HEADING,
                f"missing_marker:{OWNER_MAP_TIEBACK_HEADING}",
            ),
            (
                "remove-checker",
                NOTE_PATH,
                "- dedicated rollback guard surface:\n  - `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`\n",
                "missing_marker:dedicated rollback guard surface:",
            ),
            (
                "remove-threshold-guardrail",
                NOTE_PATH,
                ROLLBACK_THRESHOLD_MARKER,
                f"missing_marker:{ROLLBACK_THRESHOLD_MARKER}",
            ),
            (
                "remove-required-evidence-heading",
                NOTE_PATH,
                REQUIRED_EVIDENCE_HEADING,
                f"missing_marker:{REQUIRED_EVIDENCE_HEADING}",
            ),
            (
                "remove-return-to-blocked-trigger",
                NOTE_PATH,
                RETURN_TO_BLOCKED_MARKERS[0],
                f"missing_marker:{RETURN_TO_BLOCKED_MARKERS[0]}",
            ),
            (
                "remove-manifest-lane-key",
                MANIFEST_PATH,
                '"lane_key": "P14-L16"',
                'missing_manifest_marker:"lane_key": "P14-L16"',
            ),
            (
                "remove-manifest-guardrail-id",
                MANIFEST_PATH,
                '"phase14-rcu-tree-rollback-threshold-guardrail"',
                'missing_manifest_marker:"phase14-rcu-tree-rollback-threshold-guardrail"',
            ),
            (
                "change-manifest-review-blocker",
                MANIFEST_PATH,
                '"review_blocker_status": "blocked_on_stay_in_c_evidence"',
                '"review_blocker_status": "review_in_progress"',
                "manifest_rollback_threshold_mismatch:review_blocker_status:expected='blocked_on_stay_in_c_evidence':actual='review_in_progress'",
            ),
            (
                "change-manifest-summary-flag",
                MANIFEST_PATH,
                '"rollback_threshold_freeze_map_rule_present": true',
                '"rollback_threshold_freeze_map_rule_present": false',
                "manifest_survey_summary_mismatch:rollback_threshold_freeze_map_rule_present:expected=True:actual=False",
            ),
        ]
        for case in cases:
            write_text(base / NOTE_PATH, FIXTURE_NOTE)
            write_text(base / MANIFEST_PATH, FIXTURE_MANIFEST)
            if len(case) == 4:
                _, rel_path, marker, expected = case
                target = base / rel_path
                write_text(target, target.read_text(encoding="utf-8").replace(marker, "", 1))
            else:
                _, rel_path, old, new, expected = case
                target = base / rel_path
                write_text(target, target.read_text(encoding="utf-8").replace(old, new, 1))
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_text(base / NOTE_PATH, FIXTURE_NOTE + "\n- current review packet:\n")
        write_text(base / MANIFEST_PATH, FIXTURE_MANIFEST)
        failures = validate(base)
        if "forbidden_marker:current review packet:" not in failures:
            raise SystemExit(f"expected forbidden marker failure, got {failures!r}")

        note_and_manifest_missing = Path(tempfile.mkdtemp(prefix="phase14-rcu-guardrail-missing-"))
        try:
            missing_failures = validate(note_and_manifest_missing)
            expected_missing = {
                f"missing_file:{NOTE_PATH}",
                f"missing_file:{MANIFEST_PATH}",
            }
            if set(missing_failures) != expected_missing:
                raise SystemExit(
                    f"expected missing-file failures {expected_missing!r}, got {missing_failures!r}"
                )
        finally:
            shutil.rmtree(note_and_manifest_missing, ignore_errors=True)

        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass")
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST_CASE_COUNT=15")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the dedicated Phase 14 RCU rollback note stays aligned with the "
            "current freeze-in-C guardrail markers and keeps its manifest-backed reopen "
            "evidence contract honest."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL=fail")
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_DRIFT_END")
        return 1

    print("PHASE14_RCU_ROLLBACK_GUARDRAIL=pass")
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_MANIFEST_MARKER_COUNT={len(MANIFEST_REQUIRED_MARKERS)}")
    print(
        "PHASE14_RCU_ROLLBACK_GUARDRAIL_MANIFEST_ROLLBACK_FIELD_COUNT="
        f"{len(MANIFEST_REQUIRED_ROLLBACK_FIELDS)}"
    )
    print(
        "PHASE14_RCU_ROLLBACK_GUARDRAIL_MANIFEST_SUMMARY_FLAG_COUNT="
        f"{len(MANIFEST_REQUIRED_SUMMARY_FLAGS)}"
    )
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_FORBIDDEN_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
MANIFEST_REQUIRED_FIELDS = {
    ("lane_key",): "P14-L16",
    ("anchor",): "kernel/rcu/tree.c",
    ("rollback_threshold", "status_bucket"): "freeze_in_c",
    ("rollback_threshold", "review_blocker_status"): "blocked_on_stay_in_c_evidence",
    ("rollback_threshold", "owner"): "Core-Adjacent Pod",
    ("rollback_threshold", "rollback_owner"): "Repo Tooling Pod",
}
MANIFEST_REQUIRED_LISTS = {
    ("rollback_threshold", "required_evidence"): [
        "Architecture Council reopen record linked from the reviewable packet",
        "parity scorecard evidence and benchmark notes attached to the same review packet",
        "validation replay command and evidence archive path recorded beside the latest blocker disposition",
    ],
    ("rollback_threshold", "rollback_triggers"): [
        "any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record",
        "missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
        "freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner",
    ],
}
MANIFEST_REQUIRED_GAP_IDS = {
    "phase14-rcu-tree-rollback-threshold-guardrail",
    "phase14-rcu-tree-bridge-blocker",
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


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def require_manifest_fields(failures: list[str], manifest: object) -> None:
    for path, expected in MANIFEST_REQUIRED_FIELDS.items():
        try:
            actual = lookup_path(manifest, path)
        except KeyError:
            failures.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            failures.append(
                f"manifest_field_mismatch:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )

    for path, expected in MANIFEST_REQUIRED_LISTS.items():
        try:
            actual = lookup_path(manifest, path)
        except KeyError:
            failures.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            failures.append(
                f"manifest_list_mismatch:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )

    if not isinstance(manifest, dict):
        failures.append("manifest_not_object")
        return

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        failures.append("missing_manifest_key:gaps")
        return

    gap_ids = {entry.get("id") for entry in gaps if isinstance(entry, dict)}
    for expected_gap_id in sorted(MANIFEST_REQUIRED_GAP_IDS):
        if expected_gap_id not in gap_ids:
            failures.append(f"missing_manifest_gap_id:{expected_gap_id}")


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

    try:
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid_json:{MANIFEST_PATH}:{exc.msg}")
        return failures

    require_manifest_fields(failures, manifest_payload)
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
  "rollback_threshold": {
    "status_bucket": "freeze_in_c",
    "review_blocker_status": "blocked_on_stay_in_c_evidence",
    "owner": "Core-Adjacent Pod",
    "rollback_owner": "Repo Tooling Pod",
    "required_evidence": [
      "Architecture Council reopen record linked from the reviewable packet",
      "parity scorecard evidence and benchmark notes attached to the same review packet",
      "validation replay command and evidence archive path recorded beside the latest blocker disposition"
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
    },
    {
      "id": "phase14-rcu-tree-bridge-blocker"
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
                "change-manifest-lane-key",
                MANIFEST_PATH,
                '"lane_key": "P14-L16"',
                "manifest_field_mismatch:lane_key:expected='P14-L16':actual='P14-L12'",
            ),
            (
                "change-manifest-status-bucket",
                MANIFEST_PATH,
                '"status_bucket": "freeze_in_c"',
                "manifest_field_mismatch:rollback_threshold.status_bucket:expected='freeze_in_c':actual='study_only'",
            ),
            (
                "change-manifest-owner",
                MANIFEST_PATH,
                '"owner": "Core-Adjacent Pod"',
                "manifest_field_mismatch:rollback_threshold.owner:expected='Core-Adjacent Pod':actual='Repo Tooling Pod'",
            ),
            (
                "drop-manifest-required-evidence",
                MANIFEST_PATH,
                '"required_evidence": [',
                "manifest_list_mismatch:rollback_threshold.required_evidence:expected=['Architecture Council reopen record linked from the reviewable packet', 'parity scorecard evidence and benchmark notes attached to the same review packet', 'validation replay command and evidence archive path recorded beside the latest blocker disposition']:actual=['parity scorecard evidence and benchmark notes attached to the same review packet', 'validation replay command and evidence archive path recorded beside the latest blocker disposition']",
            ),
            (
                "drop-manifest-rollback-trigger",
                MANIFEST_PATH,
                '"rollback_triggers": [',
                "manifest_list_mismatch:rollback_threshold.rollback_triggers:expected=['any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record', 'missing parity scorecard evidence, benchmark notes, or replay command in the active review packet', 'freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner']:actual=['missing parity scorecard evidence, benchmark notes, or replay command in the active review packet', 'freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner']",
            ),
            (
                "drop-manifest-bridge-gap",
                MANIFEST_PATH,
                '"id": "phase14-rcu-tree-bridge-blocker"',
                "missing_manifest_gap_id:phase14-rcu-tree-bridge-blocker",
            ),
        ]
        for name, rel_path, marker, expected in cases:
            write_text(base / NOTE_PATH, FIXTURE_NOTE)
            write_text(base / MANIFEST_PATH, FIXTURE_MANIFEST)
            target = base / rel_path
            text = target.read_text(encoding="utf-8")
            if name == "change-manifest-lane-key":
                updated = text.replace('"lane_key": "P14-L16"', '"lane_key": "P14-L12"', 1)
            elif name == "change-manifest-status-bucket":
                updated = text.replace('"status_bucket": "freeze_in_c"', '"status_bucket": "study_only"', 1)
            elif name == "change-manifest-owner":
                updated = text.replace('"owner": "Core-Adjacent Pod"', '"owner": "Repo Tooling Pod"', 1)
            elif name == "drop-manifest-required-evidence":
                updated = text.replace(
                    '      "Architecture Council reopen record linked from the reviewable packet",\n',
                    "",
                    1,
                )
            elif name == "drop-manifest-rollback-trigger":
                updated = text.replace(
                    '      "any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record",\n',
                    "",
                    1,
                )
            else:
                updated = text.replace(marker, "", 1)
            write_text(target, updated)
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"case {name!r} expected {expected!r}, got {failures!r}")

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
        print("PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST_CASE_COUNT=17")
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
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_MANIFEST_FIELD_COUNT={len(MANIFEST_REQUIRED_FIELDS)}")
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_MANIFEST_LIST_COUNT={len(MANIFEST_REQUIRED_LISTS)}")
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_MANIFEST_GAP_COUNT={len(MANIFEST_REQUIRED_GAP_IDS)}")
    print(f"PHASE14_RCU_ROLLBACK_GUARDRAIL_FORBIDDEN_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

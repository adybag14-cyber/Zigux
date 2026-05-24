#!/usr/bin/env python3
"""Validate the dedicated Zigux freeze-map governance surface."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
GOVERNANCE_NOTE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
MANIFEST_PATH = Path("zigux/tests/phase15_freeze_map_manifest.json")

REQUIRED_FILES = (
    FREEZE_MAP_PATH,
    GOVERNANCE_NOTE_PATH,
    REVIEW_CHECKLIST_PATH,
    STUDY_ONLY_PATH,
    MANIFEST_PATH,
)

EXPECTED_FREEZE_IN_C_TARGETS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]

EXPECTED_STUDY_ONLY_TARGETS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

FREEZE_MAP_MARKERS = (
    "# Zigux Freeze Map",
    "## Freeze In C Initially",
    "## Study / Boundary Only",
    "## Governance For Freeze-Map Changes",
    "## Stay-In-C Policy",
    "changes to either list require an explicit Architecture Council decision with written rationale",
    "owner, phase, status bucket, validation gate summary, and rollback owner",
    "required approver set",
    "evidence archive path",
    "latest blocker disposition",
    "automatic return-to-blocked trigger",
    "`retired_from_active_discussion` state",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
    "governance lane sequencing link or explicit scope note",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
    "there is no silent exception path around the stay-in-C policy",
    "if evidence is not overwhelming, keep the code in C and document why",
)

GOVERNANCE_NOTE_MARKERS = (
    "# Phase 15 Freeze-Map Governance",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`zigux/tests/phase15_freeze_map_manifest.json`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`scripts/zigux/validate-phase15.py`",
    "`phase15-validate`, `phase15-test`, or `phase15`",
    "replay before trusting this packet",
    "zig test zigux/tests/phase15_freeze_map_governance.zig",
    "keep the current freeze anchor set and blocker posture explicit",
)

REVIEW_CHECKLIST_MARKERS = (
    "status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?",
    "does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?",
    "route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
)

STUDY_ONLY_MARKERS = (
    "# Phase 15 Study-Only Anchor Accounting",
    "tracked outside the freeze-in-C scorecard",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
)

EXPECTED_MANIFEST_REQUIREMENT_IDS = [
    "freeze-map-council-decision",
    "freeze-map-lane-ownership",
    "freeze-map-review-process-field-sync",
    "freeze-map-governance-lane-scope-sync",
    "freeze-map-study-only-accounting-sync",
    "freeze-map-parity-gate",
    "freeze-map-stay-in-c-policy",
    "freeze-map-stay-in-c-closeout",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _count_targets(lines: list[str], heading: str) -> list[str]:
    try:
        start = lines.index(heading)
    except ValueError:
        return []

    targets: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("- `") and line.endswith("`"):
            targets.append(line[3:-1])
    return targets


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    governance_note = _read_text(root / GOVERNANCE_NOTE_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    study_only_note = _read_text(root / STUDY_ONLY_PATH)
    manifest = json.loads(_read_text(root / MANIFEST_PATH))

    freeze_lines = freeze_map.splitlines()
    freeze_in_c_targets = _count_targets(freeze_lines, "## Freeze In C Initially")
    study_only_targets = _count_targets(freeze_lines, "## Study / Boundary Only")
    if freeze_in_c_targets != EXPECTED_FREEZE_IN_C_TARGETS:
        failures.append(f"freeze_in_c_targets:{freeze_in_c_targets!r}")
    if study_only_targets != EXPECTED_STUDY_ONLY_TARGETS:
        failures.append(f"study_only_targets:{study_only_targets!r}")

    for marker in FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            failures.append(f"missing_freeze_map_marker:{marker}")
    for marker in GOVERNANCE_NOTE_MARKERS:
        if marker not in governance_note:
            failures.append(f"missing_governance_note_marker:{marker}")
    for marker in REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            failures.append(f"missing_review_checklist_marker:{marker}")
    for marker in STUDY_ONLY_MARKERS:
        if marker not in study_only_note:
            failures.append(f"missing_study_only_marker:{marker}")

    for target in EXPECTED_FREEZE_IN_C_TARGETS:
        if f"`{target}`" not in freeze_map:
            failures.append(f"missing_freeze_map_anchor:{target}")
        if f"`{target}`" not in governance_note:
            failures.append(f"missing_governance_anchor:{target}")

    for target in EXPECTED_STUDY_ONLY_TARGETS:
        if f"`{target}`" not in freeze_map:
            failures.append(f"missing_freeze_map_study_anchor:{target}")
        if f"`{target}`" not in review_checklist:
            failures.append(f"missing_review_study_anchor:{target}")
        if f"`{target}`" not in study_only_note:
            failures.append(f"missing_study_only_anchor:{target}")

    if manifest.get("anchor") != str(FREEZE_MAP_PATH):
        failures.append(f"manifest_anchor:{manifest.get('anchor')!r}")
    if manifest.get("freeze_in_c_targets") != EXPECTED_FREEZE_IN_C_TARGETS:
        failures.append("manifest_freeze_in_c_targets")
    if manifest.get("study_only_targets") != EXPECTED_STUDY_ONLY_TARGETS:
        failures.append("manifest_study_only_targets")

    requirement_ids = [item.get("id") for item in manifest.get("governance_requirements", [])]
    if requirement_ids != EXPECTED_MANIFEST_REQUIREMENT_IDS:
        failures.append(f"manifest_governance_requirement_ids:{requirement_ids!r}")

    handoff = manifest.get("maintenance_handoff", {})
    replay_before_trusting = handoff.get("replay_before_trusting", [])
    if "zig test zigux/tests/phase15_freeze_map_governance.zig" not in replay_before_trusting:
        failures.append("manifest_missing_freeze_map_replay")
    next_future_target = handoff.get("next_future_target", "")
    if "Documentation/zigux/freeze-map.md" not in next_future_target:
        failures.append("manifest_next_future_target_missing_freeze_map")
    if "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py" not in next_future_target:
        failures.append("manifest_next_future_target_missing_alignment_checker")

    return failures


def _seed_fixture(root: Path) -> None:
    _write_text(
        root / FREEZE_MAP_PATH,
        """# Zigux Freeze Map

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- changes to either list require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate summary, and rollback owner in the reviewable record for that lane
- freeze-map status-change requests must keep the exact Linux anchor path, current roadmap phase, lane owner, rollback owner, current status bucket, requested decision bucket, decision record ID, required approver set, validation gate summary, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, benchmark notes, replay command, rollback threshold, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, governance lane sequencing link or explicit scope note, study-only anchor accounting link or explicit freeze-map-anchor confirmation, explicit non-goals, and written rationale explicit beside those minimum lane fields

## Stay-In-C Policy
- if evidence is not overwhelming, keep the code in C and document why
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review
""",
    )
    _write_text(
        root / GOVERNANCE_NOTE_PATH,
        """# Phase 15 Freeze-Map Governance

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `zigux/tests/phase15_freeze_map_manifest.json`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `scripts/zigux/validate-phase15.py`
- `phase15-validate`, `phase15-test`, or `phase15`

This packet helps keep the current freeze anchor set and blocker posture explicit.

## Freeze-In-C Anchor Governance Inventory
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Maintenance-Mode Handoff
- replay before trusting this packet
- `zig test zigux/tests/phase15_freeze_map_governance.zig`
""",
    )
    _write_text(
        root / REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist

- is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?
- does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?
- route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence
""",
    )
    _write_text(
        root / STUDY_ONLY_PATH,
        """# Phase 15 Study-Only Anchor Accounting

This note is tracked outside the freeze-in-C scorecard.

## Study-Only Anchor Inventory
### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`

## Accounting Rules
- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
""",
    )
    _write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "anchor": str(FREEZE_MAP_PATH),
                "freeze_in_c_targets": EXPECTED_FREEZE_IN_C_TARGETS,
                "study_only_targets": EXPECTED_STUDY_ONLY_TARGETS,
                "governance_requirements": [
                    {"id": requirement_id} for requirement_id in EXPECTED_MANIFEST_REQUIREMENT_IDS
                ],
                "maintenance_handoff": {
                    "replay_before_trusting": [
                        "python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
                        "zig test zigux/tests/phase15_freeze_map_governance.zig",
                    ],
                    "next_future_target": "reread Documentation/zigux/freeze-map.md and scripts/zigux/check-phase15-review-checklist-study-only-alignment.py before keeping the repair inside the dedicated freeze-map packet.",
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="freeze_map_validate_") as tmpdir:
        root = Path(tmpdir)

        baseline = root / "baseline"
        _seed_fixture(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        cases += 1

        bad_freeze = root / "bad_freeze"
        _seed_fixture(bad_freeze)
        text = _read_text(bad_freeze / FREEZE_MAP_PATH).replace(
            "- `kernel/trace/ring_buffer.c`\n", "", 1
        )
        _write_text(bad_freeze / FREEZE_MAP_PATH, text)
        failures = collect_failures(bad_freeze)
        expected = [
            "study_only_targets:['kernel/workqueue.c']",
            "missing_freeze_map_study_anchor:kernel/trace/ring_buffer.c",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for bad_freeze: {failures}")
        cases += 1

        bad_manifest = root / "bad_manifest"
        _seed_fixture(bad_manifest)
        manifest = json.loads(_read_text(bad_manifest / MANIFEST_PATH))
        manifest["governance_requirements"] = [{"id": "freeze-map-council-decision"}]
        _write_text(bad_manifest / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(bad_manifest)
        expected = [
            "manifest_governance_requirement_ids:['freeze-map-council-decision']"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for bad_manifest: {failures}")
        cases += 1

        bad_review = root / "bad_review"
        _seed_fixture(bad_review)
        text = _read_text(bad_review / REVIEW_CHECKLIST_PATH).replace(
            "route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
            "",
            1,
        )
        _write_text(bad_review / REVIEW_CHECKLIST_PATH, text)
        failures = collect_failures(bad_review)
        expected = [
            "missing_review_checklist_marker:route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "missing_review_checklist_marker:`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
            "missing_review_study_anchor:kernel/workqueue.c",
            "missing_review_study_anchor:kernel/trace/ring_buffer.c",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for bad_review: {failures}")
        cases += 1

    print("FREEZE_MAP_VALIDATOR_SELF_TEST=pass")
    print(f"FREEZE_MAP_VALIDATOR_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Zigux freeze-map governance surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Zigux freeze-map docs",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic fixture coverage for the freeze-map validator",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Freeze-map governance validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

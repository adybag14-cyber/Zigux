#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-next-steps-survey.py")

EXPECTED_LANE_KEY = "P15-L12"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-25"
RETIRED_MARKERS = (
    "PHASE15_LANE_KEY=P15-L11",
    "current-master-readback-2026-05-18",
    "no dedicated handoff-specific manifest or Zig replay is directly materialized on current `master`",
)
REQUIRED_BOUNDARY_MARKERS = (
    "keep the four freeze-in-C anchors parked",
    "keep the two roadmap study-only anchors parked",
    "do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged",
)
REQUIRED_GAP_MARKERS = (
    "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.",
)
REQUIRED_NEXT_STEP_MARKERS = (
    "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet",
    "reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here",
    "revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves",
)
REQUIRED_FUTURE_TARGET_MARKERS = (
    "reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift",
    "reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts",
    "keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there",
    "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet",
)
REQUIRED_HANDOFF_RULE_MARKERS = (
    "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts, refresh this handoff note",
    "if dedicated `phase15*` wrapper routes or a dedicated shared-CI route are published later, reread this note together with those new direct paths before presenting them as current evidence here",
    "if the freeze-map anchor set or any blocker disposition changes, reopen `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md` before widening this note",
)
REQUIRED_NON_GOALS = (
    "an Architecture Council approval workflow implementation",
    "a direct port-readiness decision for any Phase 15 anchor",
    "that the broader dedicated `phase15*` wrapper routes or shared-CI route are already shipped on current `master`",
)

SAMPLE_MANIFEST = {
    "lane_key": "P15-L12",
    "phase": "Phase 15",
    "surveyed_commit": "current-master-readback-2026-05-25",
    "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "checker": "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "present_paths": [
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-deep-core-blocker-survey.md",
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-parity-scorecard-survey.md",
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        "Documentation/zigux/phase15-study-only-anchor-accounting.md",
        "Documentation/zigux/phase15-shared-summary-gap.md",
        "zigux/tests/phase15_freeze_map_governance.zig",
        "zigux/tests/phase15_parity_scorecard.json",
        "zigux/tests/phase15_parity_scorecard.zig",
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        "zigux/tests/phase15_architecture_council_review_process.zig",
        "zigux/tests/phase15_architecture_council_review_process_build.zig",
        "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
        "zigux/tests/phase15_governance_lane_sequencing.zig",
        "zigux/tests/phase15_readiness_gate_manifest.json",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "zigux/tests/phase15_build.zig",
        "zigux/tests/phase15_indefinite_c_policy.json",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        "scripts/zigux/check-phase15-docs-readme-alignment.py",
        "scripts/zigux/check-phase15-scripts-readme-alignment.py",
        "scripts/zigux/check-phase15-review-process-handoff.py",
        "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
        "scripts/zigux/check-phase15-readiness-gate-packet.py",
        "scripts/zigux/check-phase15-tests-readme-alignment.py",
        "scripts/zigux/check-phase15-shared-summary-gap.py",
        "scripts/zigux/check-phase15-handoff-note-alignment.py",
        "scripts/zigux/validate-phase15.py",
    ],
    "still_missing_paths": [],
    "required_markers": [
        "PHASE15_STATUS=handoff_next_steps_survey_landed",
        "PHASE15_LANE_KEY=P15-L12",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`",
        "The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.",
        "The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master` and keeps the roadmap-versus-current-master blocker crosswalk explicit beside the broader handoff packet.",
        "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.",
        "The dedicated validator `scripts/zigux/validate-phase15.py` and shared build companion `zigux/tests/phase15_build.zig` are directly materialized on current `master`, but they do not by themselves land the broader dedicated `phase15*` wrapper routes or shared-CI route.",
        "an Architecture Council approval workflow implementation",
        "a direct port-readiness decision for any Phase 15 anchor",
    ],
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _placeholder_for(rel: str) -> str:
    if rel.endswith(".md"):
        return f"# Placeholder for {rel}\n"
    if rel.endswith(".json"):
        return "{}\n"
    if rel.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel.endswith(".zig"):
        return 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n'
    return "\n"


def _sample_manifest() -> str:
    return json.dumps(SAMPLE_MANIFEST, indent=2) + "\n"


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

This note records the bounded Phase 15 handoff surface for the existing governance packet on current `master`.

## Status

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L12`
- `PHASE15_SLICE=existing_governance_packet_handoff_inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`
- role: keep next-phase prep explicit for the Phase 15 surfaces that already exist on current `master` after the current 2026-05-25 owner-packet reread, without implying that the broader docs-root, scripts-root, tests-root, wrapper-route, or shared-CI reminder surfaces are fully aligned

## Why this note exists

The roadmap's Phase 15 work is about governance discipline and honest handoff, not one more deep-core implementation push.

Current `master` already carries the freeze map, the freeze-map governance note, the Architecture Council review-process note, the Architecture Council decision-record template, the indefinite-C policy note, the parity scorecard, the parity-scorecard survey, the readiness-gate survey, the governance-lane sequencing note, the deep-core blocker survey, the study-only anchor accounting note, the shared-summary gap note, the focused freeze-map governance replay, the focused parity-scorecard machine-readable companion plus focused replay, the focused review-process manifest plus focused replay plus focused build replay, the focused governance-lane sequencing manifest plus focused replay, the dedicated handoff-specific manifest plus focused handoff-specific replay, the shared Phase 15 build companion, the focused indefinite-C policy companions, the focused review-checklist study-only alignment checker, the focused docs-readme alignment checker, the focused scripts-readme alignment checker, the focused readiness-packet checker, the focused tests-readme alignment checker, the shared-summary gap checker, the focused handoff-note checker, and the dedicated validator maintenance gate.

The older handoff target that treated the shared build companion as still missing was no longer precise enough for the current packet. The dedicated validator, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries, while the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears.

The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`.

The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.

The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master` and keeps the roadmap-versus-current-master blocker crosswalk explicit beside the broader handoff packet.

Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.

This refresh closes the dedicated handoff undercount around the already-landed docs-readme alignment checker, scripts-readme alignment checker, validator maintenance gate, shared build companion, governance-lane sequencing companions, deep-core blocker survey, freeze-map governance companion, and parity-scorecard focused companions. Reviewers can now read this note against the current 2026-05-25 governance packet instead of reconciling it against an older handoff inventory by hand.

## Current handed-off packet on current master

- `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-deep-core-blocker-survey.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, and `Documentation/zigux/phase15-shared-summary-gap.md`
- `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused docs-readme checker, one focused scripts-readme checker, one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`
- `scripts/zigux/validate-phase15.py`, which keeps the dedicated validator directly materialized as a maintenance gate without implying that the broader dedicated `phase15*` wrapper routes or shared-CI route are landed
- `zigux/tests/phase15_build.zig`, which keeps the shared Phase 15 governance replay materialized beside `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, and `scripts/zigux/validate-phase15.py` without implying that dedicated `phase15*` wrapper routes or a shared-CI route have landed
- the broad docs-root reminder surface `Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet
- the broad scripts-root reminder surface `scripts/zigux/README.md`, which should be reread with `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet rather than being treated as a dedicated handoff-local truth source by default
- the broad `zigux/tests/README.md` reminder surface, which should be reread with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of being carried here as an unlanded future target by default

## Current governance posture to preserve

- keep the four freeze-in-C anchors parked: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
- treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence
- do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged

## Roadmap-backed open handoff gaps

The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.

The dedicated validator `scripts/zigux/validate-phase15.py` and shared build companion `zigux/tests/phase15_build.zig` are directly materialized on current `master`, but they do not by themselves land the broader dedicated `phase15*` wrapper routes or shared-CI route.

- no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`
- no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`
- no Architecture Council approval is currently recorded for a freeze-map status change, so the packet remains in maintenance-mode blocker accounting rather than port-readiness
- These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.

## Pending next-step order

1. tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet
2. reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here
3. revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves

## Next bounded future targets

1. reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift
2. reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default
3. keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there, reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py`, and only treat it as routine drift-follow-through after that wording exists and starts to diverge from the directly materialized governance packet
4. keep the landed `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, and `scripts/zigux/validate-phase15.py` companions aligned with the shared-summary gap note before any freeze-map status change discussion
5. if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet

## Handoff rules

- if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts, refresh this handoff note so it points to the current direct surfaces, the focused docs-readme checker, the focused scripts-readme checker, the focused tests-readme checker, the checker-backed shared-gap packet, the focused handoff-note checker, the focused handoff-specific replay, and the shared Phase 15 build companion instead of carrying stale future-target language
- if dedicated `phase15*` wrapper routes or a dedicated shared-CI route are published later, reread this note together with those new direct paths before presenting them as current evidence here
- if the freeze-map anchor set or any blocker disposition changes, reopen `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md` before widening this note

## Non-goals

This note does not claim:

- an Architecture Council approval workflow implementation
- a direct port-readiness decision for any Phase 15 anchor
- that the broader dedicated `phase15*` wrapper routes or shared-CI route are already shipped on current `master`

## Next bounded step

Keep this note parked until one broad Phase 15 reminder surface drifts away from the materialized governance packet above, one existing governance packet changes enough that the roadmap-backed gap list or future-target inventory above becomes stale, or one of the broader dedicated `phase15*` wrapper routes or shared-CI routes returns on current `master`.
"""


def write_sample_root(root: Path) -> None:
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    for rel in SAMPLE_MANIFEST["present_paths"]:
        if rel == MANIFEST_PATH.as_posix():
            continue
        _write(root / rel, _placeholder_for(rel))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = [HANDOFF_NOTE_PATH, MANIFEST_PATH]
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel.as_posix()}")
    if failures:
        return failures

    note = _read_text(root / HANDOFF_NOTE_PATH)
    manifest = json.loads(_read_text(root / MANIFEST_PATH))

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"manifest_lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"manifest_phase:{manifest.get('phase')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"manifest_surveyed_commit:{manifest.get('surveyed_commit')!r}")

    for retired in RETIRED_MARKERS:
        if retired in note:
            failures.append(f"retired_marker_present:{retired}")

    for marker in REQUIRED_BOUNDARY_MARKERS + REQUIRED_GAP_MARKERS + REQUIRED_NEXT_STEP_MARKERS + REQUIRED_FUTURE_TARGET_MARKERS + REQUIRED_HANDOFF_RULE_MARKERS + REQUIRED_NON_GOALS:
        if marker not in note:
            failures.append(f"missing_note_marker:{marker}")

    for marker in manifest.get("required_markers", []):
        if marker not in note:
            failures.append(f"missing_manifest_marker:{marker}")

    for path in manifest.get("present_paths", []):
        marker = f"`{path}`"
        if marker not in note:
            failures.append(f"missing_present_path_marker:{path}")
        if not (root / path).exists():
            failures.append(f"missing_present_path:{path}")

    for path in manifest.get("still_missing_paths", []):
        marker = f"`{path}`"
        if marker not in note:
            failures.append(f"missing_gap_path_marker:{path}")
        if (root / path).exists():
            failures.append(f"gap_path_returned:{path}")

    return failures


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_handoff_survey_") as tmpdir:
        root = Path(tmpdir)

        baseline = root / "baseline"
        write_sample_root(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        retired_root = root / "retired"
        write_sample_root(retired_root)
        _write(retired_root / HANDOFF_NOTE_PATH, _sample_handoff_note() + "\n- no dedicated handoff-specific manifest or Zig replay is directly materialized on current `master`\n")
        failures = collect_failures(retired_root)
        expected = ["retired_marker_present:no dedicated handoff-specific manifest or Zig replay is directly materialized on current `master`"]
        if failures != expected:
            raise AssertionError(f"unexpected retired-marker failure: {failures}")

        next_step_root = root / "next_step"
        write_sample_root(next_step_root)
        _write(
            next_step_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "2. reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here\n",
                "",
                1,
            ),
        )
        failures = collect_failures(next_step_root)
        expected = [
            "missing_note_marker:reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected next-step failure: {failures}")

        present_path_root = root / "present_path"
        write_sample_root(present_path_root)
        (present_path_root / "zigux/tests/phase15_handoff_next_steps.zig").unlink()
        failures = collect_failures(present_path_root)
        expected = ["missing_present_path:zigux/tests/phase15_handoff_next_steps.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected present-path failure: {failures}")

        lane_root = root / "lane"
        write_sample_root(lane_root)
        mutated = _sample_manifest().replace('"lane_key": "P15-L12"', '"lane_key": "P15-L07"', 1)
        _write(lane_root / MANIFEST_PATH, mutated)
        failures = collect_failures(lane_root)
        expected = ["manifest_lane_key:'P15-L07'"]
        if failures != expected:
            raise AssertionError(f"unexpected lane failure: {failures}")

        future_target_root = root / "future_target"
        write_sample_root(future_target_root)
        _write(
            future_target_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "5. if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet\n",
                "",
                1,
            ),
        )
        failures = collect_failures(future_target_root)
        expected = [
            "missing_note_marker:if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected future-target failure: {failures}")

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST=pass")
    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 handoff-next-steps survey stays aligned with the current roadmap-backed governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample root for focused validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_HANDOFF_NEXT_STEPS_SURVEY=pass")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_PRESENT_PATH_COUNT={len(SAMPLE_MANIFEST['present_paths'])}")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_SURVEY_MISSING_PATH_COUNT={len(SAMPLE_MANIFEST['still_missing_paths'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

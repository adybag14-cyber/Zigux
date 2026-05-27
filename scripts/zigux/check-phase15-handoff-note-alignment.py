#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-note-alignment.py")

EXPECTED_LANE_KEY = "P15-L12"
EXPECTED_PHASE = "Phase 15"
RETIRED_MISSING_REPLAY_MARKER = (
    "no dedicated handoff-specific Zig replay is directly materialized on current `master`"
)
REQUIRED_BOUNDARY_MARKERS = (
    "keep the four freeze-in-C anchors parked",
    "keep the two roadmap study-only anchors parked",
    "treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
    "do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged",
)
REQUIRED_FREEZE_IN_C_PATHS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)
REQUIRED_STUDY_ONLY_PATHS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)

SAMPLE_MANIFEST = json.loads('{\n  "lane_key": "P15-L12",\n  "phase": "Phase 15",\n  "surveyed_commit": "current-master-readback-2026-05-26",\n  "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",\n  "checker": "scripts/zigux/check-phase15-handoff-note-alignment.py",\n  "present_paths": [\n    "Documentation/zigux/freeze-map.md",\n    "Documentation/zigux/review-checklist.md",\n    "Documentation/zigux/phase15-freeze-map-governance.md",\n    "Documentation/zigux/phase15-deep-core-blocker-survey.md",\n    "Documentation/zigux/phase15-architecture-council-review-process.md",\n    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",\n    "Documentation/zigux/phase15-architecture-council-decision-index.md",\n    "Documentation/zigux/phase15-indefinite-c-policy.md",\n    "Documentation/zigux/phase15-parity-scorecard.md",\n    "Documentation/zigux/phase15-parity-scorecard-survey.md",\n    "Documentation/zigux/phase15-readiness-gate-survey.md",\n    "Documentation/zigux/phase15-governance-lane-sequencing.md",\n    "Documentation/zigux/phase15-study-only-anchor-accounting.md",\n    "Documentation/zigux/phase15-shared-summary-gap.md",\n    "zigux-alpha/README.md",\n    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",\n    "zigux/tests/phase15_freeze_map_governance.zig",\n    "zigux/tests/phase15_parity_scorecard.json",\n    "zigux/tests/phase15_parity_scorecard.zig",\n    "zigux/tests/phase15_architecture_council_review_process_manifest.json",\n    "zigux/tests/phase15_architecture_council_review_process.zig",\n    "zigux/tests/phase15_architecture_council_review_process_build.zig",\n    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",\n    "zigux/tests/phase15_governance_lane_sequencing.zig",\n    "zigux/tests/phase15_readiness_gate_manifest.json",\n    "zigux/tests/phase15_handoff_next_steps_manifest.json",\n    "zigux/tests/phase15_handoff_next_steps.zig",\n    "zigux/tests/phase15_build.zig",\n    "zigux/tests/phase15_indefinite_c_policy.json",\n    "zigux/tests/phase15_indefinite_c_policy.zig",\n    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",\n    "scripts/zigux/check-phase15-docs-readme-alignment.py",\n    "scripts/zigux/check-phase15-scripts-readme-alignment.py",\n    "scripts/zigux/check-phase15-review-process-handoff.py",\n    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",\n    "scripts/zigux/check-phase15-readiness-gate-packet.py",\n    "scripts/zigux/check-phase15-tests-readme-alignment.py",\n    "scripts/zigux/check-phase15-architecture-council-packet.py",\n    "scripts/zigux/check-phase15-shared-summary-gap.py",\n    "scripts/zigux/check-phase15-handoff-note-alignment.py",\n    "scripts/zigux/validate-phase15.py"\n  ],\n  "still_missing_paths": [],\n  "required_markers": [\n    "PHASE15_STATUS=handoff_next_steps_survey_landed",\n    "PHASE15_LANE_KEY=P15-L12",\n    "PHASE15_PROVENANCE_MODE=dated_master_readback",\n    "The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`",\n    "The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.",\n    "The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master` and keeps the roadmap-versus-current-master blocker crosswalk explicit beside the broader handoff packet.",\n    "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.",\n    "The dedicated validator `scripts/zigux/validate-phase15.py`, the dedicated Architecture Council packet checker `scripts/zigux/check-phase15-architecture-council-packet.py`, and shared build companion `zigux/tests/phase15_build.zig` are directly materialized on current `master`, but they do not by themselves land the broader dedicated `phase15*` wrapper routes or shared-CI route.",\n    "an Architecture Council approval workflow implementation",\n    "a direct port-readiness decision for any Phase 15 anchor"\n  ],\n  "checker_group_markers": [\n    "one focused docs-readme checker",\n    "one focused scripts-readme checker",\n    "one focused review-process checker",\n    "one focused review-checklist study-only checker",\n    "one focused readiness-packet checker",\n    "one focused tests-readme checker",\n    "one focused Architecture Council packet checker",\n    "the shared-summary gap checker",\n    "the focused handoff-note checker"\n  ],\n  "handoff_rule_markers": [\n    "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",\n    "if dedicated `phase15*` wrapper routes or a dedicated shared-CI route are published later, reread this note together with those new direct paths before presenting them as current evidence here"\n  ],\n  "roadmap_alignment_markers": [\n    "The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.",\n    "`zigux-alpha/README.md` and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` keep the bootstrap boundary explicit: the ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so later-lane Phase 15 status still has to be confirmed in the live product docs, current repo tree, and active lane notes.",\n    "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features."\n  ],\n  "pending_next_step_markers": [\n    "compare the live Phase 15 governance packet against the roadmap first and use the bootstrap ledger only as early-tranche context, because the ledger does not own later-lane status",\n    "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet",\n    "reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here",\n    "revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves"\n  ],\n  "missing_route_markers": [\n    "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",\n    "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`"\n  ]\n}\n')


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
- surveyed against dated current-master readback marker `current-master-readback-2026-05-26`
- role: keep next-phase prep explicit for the Phase 15 surfaces that already exist on current `master` after the current 2026-05-26 owner-packet reread, without implying that the broader docs-root, scripts-root, tests-root, wrapper-route, or shared-CI reminder surfaces are fully aligned

## Why this note exists

The roadmap's Phase 15 work is about governance discipline and honest handoff, not one more deep-core implementation push.

Current `master` already carries the freeze map, the freeze-map governance note, the Architecture Council review-process note, the Architecture Council decision-record template, the Architecture Council decision index, the indefinite-C policy note, the parity scorecard, the parity-scorecard survey, the readiness-gate survey, the governance-lane sequencing note, the deep-core blocker survey, the study-only anchor accounting note, the shared-summary gap note, the focused freeze-map governance replay, the focused parity-scorecard machine-readable companion plus focused replay, the focused review-process manifest plus focused replay plus focused build replay, the focused governance-lane sequencing manifest plus focused replay, the dedicated handoff-specific manifest plus focused handoff-specific replay, the shared Phase 15 build companion, the focused indefinite-C policy companions, the focused review-checklist study-only alignment checker, the focused docs-readme alignment checker, the focused scripts-readme alignment checker, the focused readiness-packet checker, the focused tests-readme alignment checker, the dedicated Architecture Council packet checker, the shared-summary gap checker, the focused handoff-note checker, and the dedicated validator maintenance gate.

The older handoff target that treated the shared build companion as still missing was no longer precise enough for the current packet. The dedicated validator, the dedicated Architecture Council packet checker, the shared build companion, the governance-lane sequencing companions, and the directly materialized reminder-surface checkers now define the tighter same-lane boundaries, while the broader wrapper-route and shared-CI follow-through should only reopen when fresh drift actually appears.

`zigux-alpha/README.md` and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` keep the bootstrap boundary explicit: the ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so later-lane Phase 15 status still has to be confirmed in the live product docs, current repo tree, and active lane notes.

The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`.

The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.

The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master` and keeps the roadmap-versus-current-master blocker crosswalk explicit beside the broader handoff packet.

Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.

This refresh closes the dedicated handoff undercount around the already-landed docs-readme alignment checker, scripts-readme alignment checker, validator maintenance gate, shared build companion, governance-lane sequencing companions, deep-core blocker survey, freeze-map governance companion, parity-scorecard focused companions, and the explicit bootstrap-ledger boundary that limits what the early commit train can say about current Phase 15 status. Reviewers can now read this note against the current 2026-05-26 governance packet instead of reconciling it against an older handoff inventory by hand.

## Current handed-off packet on current master

- `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-deep-core-blocker-survey.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-architecture-council-decision-index.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, and `Documentation/zigux/phase15-shared-summary-gap.md`
- `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused docs-readme checker, one focused scripts-readme checker, one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`
- `scripts/zigux/validate-phase15.py`, which keeps the dedicated validator directly materialized as a maintenance gate without implying that the broader dedicated `phase15*` wrapper routes or shared-CI route are landed
- `zigux/tests/phase15_build.zig`, which keeps the shared Phase 15 governance replay materialized beside `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, and `scripts/zigux/validate-phase15.py` without implying that dedicated `phase15*` wrapper routes or a shared-CI route have landed
- `zigux-alpha/README.md` and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, which remain bootstrap provenance companions and explicitly limit the ledger to the early commit train through the broadened Phase 2 tranche rather than a standalone Phase 15 truth source
- the broad docs-root reminder surface `Documentation/zigux/README.md`, which still stops at Phase 14 on current `master` and should stay treated as an active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands and aligns with `scripts/zigux/check-phase15-docs-readme-alignment.py` plus the directly materialized governance packet
- the broad scripts-root reminder surface `scripts/zigux/README.md`, which should be reread with `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet rather than being treated as a dedicated handoff-local truth source by default
- the broad `zigux/tests/README.md` reminder surface, which should be reread with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet instead of being carried here as an unlanded future target by default

## Current governance posture to preserve

- keep the four freeze-in-C anchors parked: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
- treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence
- do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged

## Roadmap and ledger synthesis boundary

The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.

`zigux-alpha/README.md` and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` keep the bootstrap boundary explicit: the ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so later-lane Phase 15 status still has to be confirmed in the live product docs, current repo tree, and active lane notes.

That means current Phase 15 handoff synthesis should start from the live governance packet plus the roadmap, and only use the bootstrap ledger as early-tranche provenance when a reminder surface needs historical context.

## Roadmap-backed open handoff gaps

The dedicated validator `scripts/zigux/validate-phase15.py` and shared build companion `zigux/tests/phase15_build.zig` are directly materialized on current `master`, but they do not by themselves land the broader dedicated `phase15*` wrapper routes or shared-CI route.

- no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`
- no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`
- no Architecture Council approval is currently recorded for a freeze-map status change, so the packet remains in maintenance-mode blocker accounting rather than port-readiness
- These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.

## Pending next-step order

1. compare the live Phase 15 governance packet against the roadmap first and use the bootstrap ledger only as early-tranche context, because the ledger does not own later-lane status
2. tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet
3. reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here
4. revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves

## Next bounded future targets

1. reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift
2. reread `zigux/tests/README.md` together with `scripts/zigux/check-phase15-tests-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the current directly materialized governance packet whenever the tests-root reminder drifts, rather than treating a dedicated Phase 15 review section as still-unlanded by default
3. keep the broad docs-root reminder surface `Documentation/zigux/README.md` in the shared-summary gap bucket until a dedicated Phase 15 reminder lands there, reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py`, and only treat it as routine drift-follow-through after that wording exists and starts to diverge from the directly materialized governance packet
4. if `zigux-alpha/README.md` or `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` changes its scope note, reread this handoff note before using the ledger to explain any later-lane Phase 15 next step
5. keep the landed `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-architecture-council-decision-index.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_architecture_council_review_process_build.zig`, `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, and `scripts/zigux/validate-phase15.py` companions aligned with the shared-summary gap note before any freeze-map status change discussion
6. if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet

## Handoff rules

- if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts, refresh this handoff note so it points to the current direct surfaces, the focused docs-readme checker, the focused scripts-readme checker, the focused tests-readme checker, the checker-backed shared-gap packet, the focused handoff-note checker, the focused handoff-specific replay, the shared Phase 15 build companion, and the explicit bootstrap-ledger boundary instead of carrying stale future-target language
- if dedicated `phase15*` wrapper routes or a dedicated shared-CI route are published later, reread this note together with those new direct paths before presenting them as current evidence here
- if the freeze-map anchor set or any blocker disposition changes, reopen `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md` before widening this note

## Non-goals

This note does not claim:

- an Architecture Council approval workflow implementation
- a direct port-readiness decision for any Phase 15 anchor
- that the broader dedicated `phase15*` wrapper routes or shared-CI route are already shipped on current `master`

## Next bounded step

Keep this note parked until one broad Phase 15 reminder surface drifts away from the materialized governance packet above, one existing governance packet changes enough that the roadmap-backed gap list or future-target inventory above becomes stale, the bootstrap ledger boundary changes enough that this handoff synthesis needs a narrower reminder, or one of the broader dedicated `phase15*` wrapper routes or shared-CI routes returns on current `master`.
"""


def collect_failures(root: Path) -> list[str]:
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    failures: list[str] = []

    if manifest["lane_key"] != EXPECTED_LANE_KEY:
        failures.append(f"handoff manifest lane key drifted from {EXPECTED_LANE_KEY}: {manifest['lane_key']}")
    if manifest["phase"] != EXPECTED_PHASE:
        failures.append(f"handoff manifest phase drifted from {EXPECTED_PHASE}: {manifest['phase']}")
    if manifest["handoff_note"] != HANDOFF_NOTE_PATH.as_posix():
        failures.append(f"handoff manifest note path drifted from {HANDOFF_NOTE_PATH.as_posix()}: {manifest['handoff_note']}")
    if manifest["checker"] != CHECKER_PATH.as_posix():
        failures.append(f"handoff manifest checker path drifted from {CHECKER_PATH.as_posix()}: {manifest['checker']}")
    if manifest["surveyed_commit"] not in handoff_note:
        failures.append("handoff note is missing the manifest surveyed_commit marker")
    if f"`{manifest['checker']}`" not in handoff_note:
        failures.append("handoff note is missing the focused handoff-note checker path")
    if RETIRED_MISSING_REPLAY_MARKER in handoff_note:
        failures.append("handoff note still frames the focused handoff replay as missing")

    for key, label in (
        ("required_markers", "required marker"),
        ("checker_group_markers", "checker-group marker"),
        ("handoff_rule_markers", "handoff-rule marker"),
        ("roadmap_alignment_markers", "roadmap-alignment marker"),
        ("pending_next_step_markers", "pending-next-step marker"),
        ("missing_route_markers", "missing-route marker"),
    ):
        for marker in manifest[key]:
            if marker not in handoff_note:
                failures.append(f"handoff note is missing {label}: {marker}")

    for marker in REQUIRED_BOUNDARY_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing boundary marker: {marker}")

    for repo_path in manifest["present_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing present-path marker: {marker}")
        if not (root / repo_path).exists():
            failures.append(f"handoff note claims present path missing from repo: {marker}")

    for repo_path in manifest["still_missing_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing gap-path marker: {marker}")
        if (root / repo_path).exists():
            failures.append(f"handoff note still frames shipped path as missing gap: {marker}")

    for repo_path in REQUIRED_FREEZE_IN_C_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing freeze-in-c path marker: {marker}")

    for repo_path in REQUIRED_STUDY_ONLY_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing study-only path marker: {marker}")

    return failures


def _seed_present_paths(root: Path, manifest: dict) -> None:
    for repo_path in manifest["present_paths"]:
        if repo_path == MANIFEST_PATH.as_posix():
            continue
        _write(root / repo_path, "# fixture\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_handoff_note_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(root / MANIFEST_PATH)
        _seed_present_paths(root, manifest)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_boundary_root = root / "missing_gap_boundary"
        _write(
            missing_boundary_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence\n",
                "",
                1,
            ),
        )
        _write(missing_boundary_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_boundary_root / MANIFEST_PATH)
        _seed_present_paths(missing_boundary_root, manifest)
        failures = collect_failures(missing_boundary_root)
        expected = [
            "handoff note is missing boundary marker: treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-gap-boundary failure: {failures}")

        identity_root = root / "manifest_identity_drift"
        _write(identity_root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        mutated = _sample_manifest().replace('"lane_key": "P15-L12"', '"lane_key": "P15-L99"', 1)
        mutated = mutated.replace('"phase": "Phase 15"', '"phase": "Phase 15 drift"', 1)
        mutated = mutated.replace('"handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md"', '"handoff_note": "Documentation/zigux/phase15-handoff-next-step-survey.md"', 1)
        mutated = mutated.replace('"checker": "scripts/zigux/check-phase15-handoff-note-alignment.py"', '"checker": "scripts/zigux/check-phase15-handoff-alignment.py"', 1)
        _write(identity_root / MANIFEST_PATH, mutated)
        manifest = _read_manifest(identity_root / MANIFEST_PATH)
        _seed_present_paths(identity_root, manifest)
        failures = collect_failures(identity_root)
        expected = [
            "handoff manifest lane key drifted from P15-L12: P15-L99",
            "handoff manifest phase drifted from Phase 15: Phase 15 drift",
            "handoff manifest note path drifted from Documentation/zigux/phase15-handoff-next-steps-survey.md: Documentation/zigux/phase15-handoff-next-step-survey.md",
            "handoff manifest checker path drifted from scripts/zigux/check-phase15-handoff-note-alignment.py: scripts/zigux/check-phase15-handoff-alignment.py",
            "handoff note is missing the focused handoff-note checker path",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected manifest-identity-drift failure: {failures}")

        missing_commit_root = root / "missing_surveyed_commit"
        _write(
            missing_commit_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace("`current-master-readback-2026-05-26`", "`current-master-readback-YYYY-MM-DD`", 1),
        )
        _write(missing_commit_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_commit_root / MANIFEST_PATH)
        _seed_present_paths(missing_commit_root, manifest)
        failures = collect_failures(missing_commit_root)
        if failures != ["handoff note is missing the manifest surveyed_commit marker"]:
            raise AssertionError(f"unexpected missing-surveyed-commit failure: {failures}")

        missing_checker_root = root / "missing_checker_path"
        _write(
            missing_checker_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-readiness-gate-packet.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-handoff-note-alignment.py`, which together keep one focused docs-readme checker, one focused scripts-readme checker, one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker materialized on current `master`\n",
                "",
                1,
            ),
        )
        _write(missing_checker_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_checker_root / MANIFEST_PATH)
        _seed_present_paths(missing_checker_root, manifest)
        failures = collect_failures(missing_checker_root)
        expected = [
            "handoff note is missing the focused handoff-note checker path",
            "handoff note is missing checker-group marker: one focused docs-readme checker",
            "handoff note is missing checker-group marker: one focused scripts-readme checker",
            "handoff note is missing checker-group marker: one focused review-process checker",
            "handoff note is missing checker-group marker: one focused review-checklist study-only checker",
            "handoff note is missing checker-group marker: one focused readiness-packet checker",
            "handoff note is missing checker-group marker: one focused tests-readme checker",
            "handoff note is missing present-path marker: `scripts/zigux/check-phase15-review-process-handoff.py`",
            "handoff note is missing present-path marker: `scripts/zigux/check-phase15-shared-summary-gap.py`",
            "handoff note is missing present-path marker: `scripts/zigux/check-phase15-handoff-note-alignment.py`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-checker-path failure: {failures}")

        missing_route_root = root / "missing_route_marker"
        _write(
            missing_route_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`\n",
                "",
                1,
            ),
        )
        _write(missing_route_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(missing_route_root / MANIFEST_PATH)
        _seed_present_paths(missing_route_root, manifest)
        failures = collect_failures(missing_route_root)
        expected = [
            "handoff note is missing missing-route marker: no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-route-marker failure: {failures}")

        retired_gap_root = root / "retired_gap"
        _write(
            retired_gap_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note() + "\n- no dedicated handoff-specific Zig replay is directly materialized on current `master`\n",
        )
        _write(retired_gap_root / MANIFEST_PATH, _sample_manifest())
        manifest = _read_manifest(retired_gap_root / MANIFEST_PATH)
        _seed_present_paths(retired_gap_root, manifest)
        failures = collect_failures(retired_gap_root)
        if failures != ["handoff note still frames the focused handoff replay as missing"]:
            raise AssertionError(f"unexpected retired-gap failure: {failures}")

    print("PHASE15_HANDOFF_NOTE_ALIGNMENT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that the Phase 15 handoff note stays aligned with the current governance packet and dedicated handoff manifest.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests")
    parser.add_argument("--self-test", action="store_true", help="exercise the checker against synthetic repo fixtures")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE15_HANDOFF_NOTE_ALIGNMENT_FAILURE={failure}")
        return 1

    print("PHASE15_HANDOFF_NOTE_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

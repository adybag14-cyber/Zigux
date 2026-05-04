# Phase 15 Parity Scorecard

This document records the bounded Phase 15 governance lane for the deep-core freeze set.

## Status

- `PHASE15_LANE_KEY=P15-Y03`
- `PHASE15_STATUS=freeze_in_c_governance`
- `PHASE15_SLICE=current-parity-tracking-gap-survey`
- scope: a reviewable scorecard that captures council inputs, evidence thresholds, validation gates, rollback ownership, rollback thresholds, evidence-archive reporting, reserved per-anchor decision-record templates, retained stay-in-C closeout state, explicit per-anchor owner tracking for the active freeze-in-C anchors, and one explicit roadmap-vs-repo parity-tracking gap survey now that the landed Phase 15 governance bundle already replays in the shared workflow
- survey provenance refreshed against verified `master` head `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-evidence-archives/`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `zigux/tests/phase15_parity_scorecard.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The roadmap says Phase 15 is about honest long-term governance for the final mixed-language steady state. The live repo already records the freeze set in `Documentation/zigux/freeze-map.md`, and it already has the bounded reporting step that says where each frozen anchor keeps its Architecture Council evidence packet, but those reserved paths still needed real template files.

That gap matters because the current anchors are still large and deeply coupled: `kernel/sched/core.c` is 11,235 lines, `mm/page_alloc.c` is 7,795 lines, `kernel/rcu/tree.c` is 4,931 lines, `kernel/rcu/tree_plugin.h` is 1,369 lines, `kernel/rcu/tree_exp.h` is 1,118 lines, `kernel/rcu/tree_nocb.h` is 1,702 lines, `net/core/skbuff.c` is 7,476 lines, and `include/linux/skbuff.h` adds another 5,467 lines of shared metadata and inline rules. The repo also already carries Phase 14 blocker evidence for `kernel/rcu/tree.c` and `net/core/skbuff.c`, which makes reserved decision-record templates the next honest step instead of another implementation starter.

## Roadmap Handoff Evidence

- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` Phase 15, `Full-Parity Blockers and Long-Term Governance`
- roadmap handoff: Phase 15 must keep the freeze map, Architecture Council review process, parity scorecard, and policy for code that remains in C indefinitely visible as one honest governance bundle
- bootstrap ledger anchor: `docs(zigux): add documentation root, review checklist, and freeze map`
- current repo handoff: the ledger's documentation root and freeze-map start point is now carried forward by `Documentation/zigux/README.md`, the landed Phase 15 review-process note, parity scorecard, indefinite-C policy note, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, the reserved evidence-archive templates, the dedicated Zig manifest and test, the shared `zigux/tests/phase15_build.zig` gate, the `make -C zigux phase15` convenience target, and the shared bootstrap workflow replay
- maintenance-mode next step: keep the Phase 15 governance lane parked until one of the named reopen triggers fires or the deep-core blocker posture changes

## Current Parity-Tracking Gap

The current roadmap-vs-repo parity-tracking gap inside this lane is no longer a missing local governance artifact.

The roadmap-required parity-tracking bundle is already present locally:

- freeze map governance exists in `Documentation/zigux/freeze-map.md`
- the Architecture Council review process exists in `Documentation/zigux/phase15-architecture-council-review-process.md`
- the dedicated parity scorecard packet exists in `Documentation/zigux/phase15-parity-scorecard.md`
- the indefinite-C policy packet exists in `Documentation/zigux/phase15-indefinite-c-policy.md`
- the dedicated manifest and Zig test keep the scorecard machine-checkable in `zigux/tests/phase15_parity_scorecard.json` and `zigux/tests/phase15_parity_scorecard.zig`
- `Documentation/zigux/README.md`, `zigux/tests/phase15_build.zig`, and `make -C zigux phase15` keep the same governance bundle visible on the docs root and shared replay path

That means the current parity-tracking gap is narrower and maintenance-only: keep the scorecard's lane identity, surveyed-master provenance, roadmap wording, rollback-threshold field sync, and replay-backed evidence packet current so the roadmap requirement stays explicitly satisfied instead of drifting into stale metadata.

That closes the current parity-tracking gap for the roadmap requirement `parity scorecard`.

The remaining blocked work is still the already-recorded deep-core status-change blocker rather than another missing parity-tracking artifact.

## Coverage Summary

- freeze-in-C anchors tracked: `4`
- anchors with Phase 14 survey evidence linked: `2 / 4`
- reserved evidence-archive templates present: `4 / 4`
- anchors with explicit blocker dispositions recorded: `4 / 4`
- anchors with explicit lane-owner plus rollback-owner coverage: `4 / 4`
- required review-process record fields tracked in the manifest: `15`
- reopen-trigger catalog entries tracked in the manifest: `3`
- repo evidence checks currently green: `15 / 15`
- landed scorecard gaps: `19 / 20`
- blocked scorecard gaps: `1 / 20`
- replay surfaces currently recorded: `3 / 3`

This summary is a reporting layer for the current maintenance-mode packet, not a new status claim. It says the governance bundle is fully inventoried and replay-backed across the dedicated `zigux/tests/phase15_build.zig` gate, the `make -C zigux phase15` convenience target, and the shared bootstrap workflow. It also shows that every freeze-in-C anchor still carries both a current lane owner and a rollback owner, while still keeping one explicit blocked gap for deep-core status changes.

## Scorecard Entries

### `kernel/sched/core.c`

- current status: `freeze_in_c`
- lane owner: `Architecture Council`
- current repo evidence:
  - active freeze-map anchor with no Zig surface or dedicated Phase 15 validation gate
  - large 11,235-line scheduler core still exceeds the current bounded-lane posture
- council inputs:
  - Architecture Council decision naming a narrow ownership seam
  - PMO or Release Management sign-off on rollback and release blast radius
  - Validation and Perf Team sign-off on the benchmark and regression plan
- evidence thresholds:
  - a written seam inventory that isolates one bounded scheduler responsibility
  - a proof that the candidate slice does not widen into class balancing, hotplug, or wakeup policy ownership
  - a benchmark plan with explicit latency and fairness regression thresholds
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - a future lane-local parity harness before any status change
  - explicit rollback rehearsal and owner
- rollback owner: `Architecture Council + PMO / Release Management`
- evidence archive reporting:
  - decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
  - linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-parity-scorecard.md`
  - benchmark notes: `pending_until_bounded_scheduler_seam_exists`
  - replay command: `zig build test --build-file zigux/tests/phase15_build.zig`
  - latest blocker disposition: `blocked_no_bounded_scheduler_seam`
  - rollback threshold: `If the decision record, scorecard evidence, benchmark notes, replay command, rollback owner, or bounded scheduler seam proof stops being explicit, or if the candidate seam widens into class balancing, hotplug, or wakeup policy ownership, return this anchor to blocked review posture.`

### `mm/page_alloc.c`

- current status: `freeze_in_c`
- lane owner: `Architecture Council`
- current repo evidence:
  - active freeze-map anchor with no Zig surface or dedicated Phase 15 validation gate
  - large 7,795-line allocator core still exceeds the current bounded-lane posture
- council inputs:
  - Architecture Council decision naming a narrow ownership seam
  - Toolchain and Kbuild Team confirmation that the build surface stays bounded
  - Validation and Perf Team sign-off on allocator-sensitive stress coverage
- evidence thresholds:
  - a written seam inventory that isolates one bounded allocator-facing responsibility
  - proof that watermarks, reclaim interaction, and zone-balancing ownership stay in C
  - a stress-validation plan with explicit failure and rollback criteria
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - a future lane-local parity harness before any status change
  - explicit rollback rehearsal and owner
- rollback owner: `Architecture Council + Validation and Perf Team`
- evidence archive reporting:
  - decision record path: `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
  - linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-parity-scorecard.md`
  - benchmark notes: `pending_until_bounded_allocator_seam_exists`
  - replay command: `zig build test --build-file zigux/tests/phase15_build.zig`
  - latest blocker disposition: `blocked_no_bounded_allocator_seam`
  - rollback threshold: `If the decision record, scorecard evidence, benchmark notes, replay command, rollback owner, or bounded allocator seam proof stops being explicit, or if the candidate seam widens into watermarks, reclaim interaction, or zone balancing ownership, return this anchor to blocked review posture.`

### `kernel/rcu/tree.c`

- current status: `freeze_in_c`
- lane owner: `ABI and Runtime Team`
- current repo evidence:
  - active freeze-map anchor with a published Phase 14 survey and blocker evidence
  - `kernel/rcu/tree.c` is 4,931 lines, with `tree_plugin.h`, `tree_exp.h`, and `tree_nocb.h` still documenting tight sidecar coupling
- council inputs:
  - Architecture Council review of the existing Phase 14 survey package
  - ABI and Runtime Team sign-off on any proposed seam ownership
  - Validation and Perf Team sign-off on quiescent-state and ordering coverage
- evidence thresholds:
  - the Phase 14 survey blockers must be answered with a narrower follow-up than the current freeze boundary
  - proof that grace-period sequencing, expedited-GP behavior, and NOCB wakeup ownership remain explicit
  - a documented ordering-validation plan before any status change
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - existing Phase 14 survey evidence must stay green
  - a future lane-local parity harness before any status change
- rollback owner: `Architecture Council + ABI and Runtime Team`
- evidence archive reporting:
  - decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
  - linked evidence: `Documentation/zigux/phase14-rcu-tree-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-parity-scorecard.md`
  - benchmark notes: `pending_until_rcu_followup_is_narrower_than_freeze_boundary`
  - replay command: `zig build test --build-file zigux/tests/phase15_build.zig`
  - latest blocker disposition: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
  - rollback threshold: `If the decision record, scorecard evidence, benchmark notes, replay command, rollback owner, or narrowed RCU follow-up stops being explicit, or if the candidate seam widens back across grace-period sequencing, expedited-GP behavior, or NOCB wakeup ownership, return this anchor to blocked review posture.`

### `net/core/skbuff.c`

- current status: `freeze_in_c`
- lane owner: `Shared Subsystems Pod`
- current repo evidence:
  - active freeze-map anchor with a published Phase 14 skbuff boundary survey
  - `net/core/skbuff.c` is 7,476 lines and `include/linux/skbuff.h` adds 5,467 lines of shared metadata and inline rules
- council inputs:
  - Architecture Council review of the existing Phase 14 skbuff survey package
  - Shared Subsystems Pod sign-off on the candidate boundary
  - Validation and Perf Team sign-off on packet-lifetime and checksum coverage
- evidence thresholds:
  - the Phase 14 survey blockers must be answered with a narrower follow-up than the current lifetime boundary
  - proof that refcounted lifetime, destructor ordering, checksum ownership, and segmentation ownership remain explicit
  - a documented packet-path validation plan before any status change
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - existing Phase 14 survey evidence must stay green
  - a future lane-local parity harness before any status change
- rollback owner: `Architecture Council + Shared Subsystems Pod`
- evidence archive reporting:
  - decision record path: `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
  - linked evidence: `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-parity-scorecard.md`
  - benchmark notes: `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`
  - replay command: `zig build test --build-file zigux/tests/phase15_build.zig`
  - latest blocker disposition: `blocked_packet_lifetime_boundary_still_too_wide`
  - rollback threshold: `If the decision record, scorecard evidence, benchmark notes, replay command, rollback owner, or narrowed skbuff follow-up stops being explicit, or if the candidate seam widens back across packet lifetime, destructor ordering, checksum ownership, or segmentation ownership, return this anchor to blocked review posture.`

## Recorded Gaps

The current lane state is:

- landed `phase15-freeze-map-governance-note`
- landed `phase15-review-checklist-scorecard-question`
- landed `phase15-parity-scorecard-note`
- landed `phase15-council-review-gate`
- landed `phase15-parity-scorecard-manifest`
- landed `phase15-parity-scorecard-test`
- landed `phase15-build-gate`
- landed `phase15-make-target`
- landed `phase15-evidence-archive-reporting`
- landed `phase15-blocker-disposition-summary-metric`
- landed `phase15-decision-record-template-followup`
- landed `phase15-template-field-sync-followup`
- landed `phase15-anchor-owner-tracking`
- landed `phase15-stay-in-c-retirement-rule`
- landed `phase15-reopen-trigger-catalog-followup`
- landed `phase15-roadmap-handoff-evidence-followup`
- landed `phase15-readme-governance-index`
- landed `phase15-maintenance-mode-handoff-sync`
- landed `phase15-scorecard-review-packet-field-sync`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane honest: Zigux now has a reviewable Phase 15 scorecard for the frozen anchors, a concrete reporting block that says where Architecture Council evidence belongs, reserved packet templates at those paths, one explicit retained stay-in-C closeout state for anchors that leave active discussion without leaving C, a visible roadmap-handoff note, a top-level docs index for the Phase 15 governance bundle, shared bootstrap replay for the landed governance bundle, and one explicit maintenance-mode handoff note. It still does not claim a scheduler slice, allocator slice, new RCU bridge, or direct skbuff rewrite.

## Current Maintenance-Mode Handoff

The current roadmap-vs-repo handoff task inside this scorecard lane is no longer a missing local governance artifact or a local-versus-shared replay mismatch.

The roadmap-required bundle is already present locally:

- freeze map
- Architecture Council review process
- parity scorecard
- policy for code that remains in C indefinitely

The landed bundle is now enforced and tracked through both local replay and the published shared workflow:

- local replay exists through `zig build test --build-file zigux/tests/phase15_build.zig`
- local replay exists through `make -C zigux phase15`
- the published shared bootstrap workflow now runs the landed Phase 15 governance bundle through `make -C zigux phase15`

That closes the old shared-CI follow-up for this scorecard packet and leaves `phase15-maintenance-mode-handoff-sync` as the landed synthesis note, while the deep-core blocker records remain separately blocked on stronger stay-in-C exception evidence.

## Architecture Council Review Gate

Before a freeze-in-C anchor can enter active status-review discussion, the scorecard record must carry one Architecture Council decision record that names:

- the current roadmap phase, the decision record ID, and the lane owner responsible for the proposed seam
- the current validation gate set and the rollback owner who would return the anchor to C-only operation
- the evidence archive path that preserves linked surveys and blocker follow-ups, benchmark notes, and replay commands
- the latest blocker disposition stating whether the anchor remains blocked, is ready for narrower follow-up, or has been rejected for status change
- the automatic return-to-blocked trigger that sends the anchor back to blocked review posture when the packet goes stale or incomplete
- the rollback threshold that names which stale, missing, contradictory, or widened evidence returns the anchor to blocked review posture
- the indefinite-C policy link, or an explicit note saying why the packet is not yet entering that policy posture
- the retained discussion state showing whether the anchor closes review as `retired_from_active_discussion`
- the reopen triggers that name which evidence changes can reopen the stay-in-C discussion later without implying approval
- the trigger-specific refreshed evidence by path, together with the current blocker disposition restatement, for every cited reopen trigger
- refreshed lane-owner and rollback-owner evidence whenever the cited reopen trigger is `ownership_or_validation_changed`
- the written rationale for why the current product state needs council attention now

A frozen anchor leaves active discussion only after the current roadmap phase, Architecture Council sign-off, validation evidence links, rollback ownership, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, rollback threshold, indefinite-C policy link or applicability note, retained discussion state, reopen triggers, trigger-specific refreshed evidence by path, refreshed ownership records when `ownership_or_validation_changed` is cited, and written rationale are all recorded together in the scorecard.

If any one of those fields is missing, stale, or contradicted by the linked evidence, the anchor remains in the freeze-in-C set and the review closes with an explicit stay-in-C outcome.

## Stay-in-C Retirement Rule

When a freeze-in-C anchor closes review without a status change, the scorecard records one retained discussion state: `retired_from_active_discussion`.

That retained state does not mean the blocker disappeared. It means the active discussion is closed for now, the anchor remains governed as in-C, and the evidence archive still has to preserve the decision record, linked evidence, benchmark-note status, replay command, rollback threshold, and latest blocker disposition that justified the closeout.

Each closeout packet must also record the reopen triggers that would bring the anchor back into active discussion. The minimum catalog is:

- `narrower_followup_answers_blocker`: a narrower seam inventory that answers the latest blocker disposition
- `evidence_packet_stale_or_contradictory`: linked validation, benchmark, or blocker evidence becoming stale or contradictory
- `ownership_or_validation_changed`: rollback ownership or validation gates changing enough to invalidate the closed stay-in-C packet

Any later reopen packet must restate the current blocker disposition and point reviewers at the trigger-specific refreshed evidence by path for every cited catalog item. If the cited item is `ownership_or_validation_changed`, the reopened packet must refresh both the current lane owner and the rollback owner before active review resumes.

## Reopen Trigger Catalog

The bounded reopen-trigger catalog for retired stay-in-C packets is:

- `narrower_followup_answers_blocker`: use when a narrower seam inventory or follow-up now answers the current blocker without widening the allowed boundary
- `evidence_packet_stale_or_contradictory`: use when linked validation, benchmark, survey, or blocker evidence no longer agrees with the closed packet
- `ownership_or_validation_changed`: use when rollback ownership, lane ownership, or validation gates changed enough that the closed packet must be reviewed again

Every reopen packet must cite the trigger-specific refreshed evidence by path for each named catalog item and restate the current blocker disposition it is trying to change. When the cited item is `ownership_or_validation_changed`, the packet must also refresh both the current lane owner and the rollback owner instead of reusing stale closeout ownership.

## Evidence Archive Reporting Standard

Each frozen anchor now carries one reporting block that reserves:

- the lane owner responsible for keeping the blocked or retired packet current
- one decision record path under `Documentation/zigux/phase15-evidence-archives/`
- the linked evidence set that reviewers must be able to open from the scorecard
- a benchmark-notes status line that says whether performance notes exist yet
- the replay command reviewers should run before trusting the current packet
- the latest blocker disposition that keeps the stay-in-C posture explicit
- the rollback threshold that names which stale, missing, contradictory, or widened evidence returns the anchor to blocked review posture
- the retained discussion state and one or more named catalog reopen triggers that explain how a closed review stays reviewable later

These reporting fields do not claim a decision record already exists. They standardize where the record will live and what still remains missing until a narrower seam earns Architecture Council review.

## Reserved Decision Record Templates

The scorecard's reserved evidence-archive paths now exist as template packet files:

- `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`

Each template keeps the current status bucket, requested decision bucket, decision record ID, ownership, validation gate summary, linked evidence, benchmark-notes status, replay command, latest blocker disposition, automatic return-to-blocked trigger, rollback threshold, indefinite-C policy link, retained discussion state, reopen triggers, explicit non-goals, and written rationale visible in one place without claiming that any Architecture Council approval has already happened.

## Non-goals

This scorecard slice does not claim:

- a `kernel/sched/core.zig` surface
- a `mm/page_alloc.zig` surface
- a new `kernel/rcu/tree_bridge.zig`
- a direct `net/core/skbuff.c` rewrite
- Architecture Council approval for any status change
- completed parity harnesses for any deep-core anchor

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The next honest action inside this scorecard lane is to wait for one of the named reopen triggers to fit the evidence packet again or for the deep-core blocker posture to change enough to justify another bounded follow-up.

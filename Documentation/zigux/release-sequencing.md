# Release Sequencing

This note turns the roadmap order into a current-master-safe release plan for Zigux.

It is a PMO and release-management artifact, not a claim that every named phase is already closed.

## Sequencing Rules

- keep the roadmap order authoritative: move from bounded helper and tooling tranches into ABI and validation work before runtime pilots or drivers
- treat current `master` readback as higher authority than older reminder wording when the two disagree
- reopen one tranche at a time; do not widen a release lane just because a neighboring phase has active work
- do not schedule Phase 10 and later delivery as active release work until the earlier gates are actually green, matching the roadmap rule

## Release Buckets

### Release A: Foundation Hold

Roadmap coverage:
- Phase 1 host-side helpers
- Phase 2 toolchain and kbuild enablement

Current repo posture:
- `Documentation/zigux/phase1-closure.md` keeps Phase 1 parked with an explicit current reminder packet and an explicit repo-reality gap packet
- `Documentation/zigux/phase2-closure.md` does the same for the bounded Phase 2 toolchain tranche
- current `master` already has the closure-side notes needed to keep this foundation tranche reviewable without reopening it by default

Release rule:
- treat Release A as a parked foundation tranche
- reopen it only for shared reminder drift or if missing closure companions return on current `master`

### Release B: ABI And Rollback Preview

Roadmap coverage:
- Phase 3 ABI and interop substrate
- Phase 4 differential validation and rollback

Current repo posture:
- `Documentation/zigux/phase3-validator-support-surface.md` shows that current `master` carries bounded Phase 3 starter, helper, and policy slices, not a full broad ABI closure packet
- `Documentation/zigux/phase4-reversible-delivery-evidence.md` and `Documentation/zigux/phase4-validation-matrix.md` keep the rollback-readiness packet reviewable, but both still record explicit partial-readback or remaining-gap posture

Release rule:
- keep Release B in preview
- do not call it closed while Phase 3 is still framed as bounded starter slices and while Phase 4 still relies on remaining-gap or partial-readback wording

### Release C: Developer Enablement Backlog

Roadmap coverage:
- Phase 5 samples and reference patterns
- Phase 6 greenfield leaf helpers
- Phase 7 in-kernel leaf libraries
- Phase 8 userspace-adjacent tooling expansion

Current repo posture:
- `Documentation/zigux/phase5-sample-lane-sequencing.md` gives Phase 5 a truthful same-lane sequencing note on current `master`
- this PMO pass did not find a current-master release packet for Phase 6 or Phase 7
- `scripts/zigux/validate-phase8.py` is directly readable on current `master`, but direct contents read for `Documentation/zigux/phase8-tooling-lane-sequencing.md` returned missing during this pass

Release rule:
- do not treat Release C as a combined releasable tranche yet
- Phase 5 may continue through bounded reminder-surface repairs, but keep Phases 6 through 8 parked until they have direct current-master coordination artifacts rather than split validator-only or roadmap-only evidence

### Release D: Runtime And Driver Expansion

Roadmap coverage:
- Phase 9 runtime pilot modules
- Phases 10 through 15 drivers, shared subsystems, core-adjacent work, and long-term governance

Current repo posture:
- this band is still downstream of the earlier release buckets
- the roadmap explicitly says Phase 10 and later should not be scheduled until the earlier gates are actually green

Release rule:
- keep Release D unscheduled as active release work
- any future opening step must name which earlier bucket turned green and which rollback and validation owners cleared the handoff

## Coordination Rules

When release-planning work reopens, use this order:

1. keep Release A parked unless a closure packet drifts
2. keep Release B focused on turning preview evidence into a narrower true closure packet before widening any later release band
3. treat Release C as coordination debt first: fill missing Phase 6 and Phase 7 release packets and restore the missing Phase 8 sequencing note before calling that band ready
4. leave Release D blocked until the earlier release buckets stop depending on explicit gap wording

## Next PMO Step

The next bounded same-lane follow-through is to align one shared reminder surface with this release plan, preferably the docs root or another release-facing index, so the repo advertises the same release buckets that the current closure and sequencing notes now imply.

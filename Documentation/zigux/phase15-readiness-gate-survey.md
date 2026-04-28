# Phase 15 Tranche Readiness Gate Survey

This document records the bounded Phase 15 readiness lane for surveying the remaining tranche-readiness gaps against the roadmap and bootstrap ledger.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_SLICE=tranche-readiness-gap-survey`
- scope: one readiness survey note, one dedicated manifest and Zig test, one shared `phase15_build.zig` follow-up, one shared bootstrap-workflow replay step, and the later handoff-and-next-step packet that together keep the roadmap requirements, bootstrap ledger anchor, current repo evidence, and remaining blocked readiness gaps reviewable in one place
- survey provenance refreshed against verified `master` head `0875a574c226ed5091e06e3e9e59c64ed9e5bf37`
- product boundary:
  - `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
  - `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
  - `zigux/tests/phase15_readiness_gate_manifest.json`
  - `zigux/tests/phase15_readiness_gate.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why this slice exists

The roadmap says Phase 15 is the governance tranche for the final mixed-language steady state. The bootstrap ledger, by contrast, only anchors the first documentation step: the documentation root, review checklist, and freeze map.

Current `master` is farther along than that ledger starting point. Zigux now already carries the freeze map, the review checklist hook, the Architecture Council review-process note, the parity scorecard, the indefinite-C policy note, the dedicated `phase15_build.zig` replay gate, the `make -C zigux phase15` convenience target, and the later handoff-and-next-step survey that keeps the parked maintenance contract explicit.

What was still missing was one dedicated readiness packet that compares those three views together:

- what the roadmap requires
- what the bootstrap ledger originally anchored
- what the live repo has actually landed and what remains blocked

That comparison still matters because the remaining Phase 15 gaps are no longer "missing governance documents" or missing shared replay wiring. The shared bootstrap workflow still runs the Phase 15 governance bundle, the full shared Phase 15 replay is green on current `master`, and no deep-core anchor yet has evidence strong enough to leave the freeze-in-C posture.

The honest bounded step therefore remains maintenance of the existing readiness packet, not another new governance policy surface or a neighboring replay-fix lane.

## Roadmap Versus Ledger

- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` Phase 15, `Full-Parity Blockers and Long-Term Governance`
- roadmap-required Phase 15 bundle:
  - freeze map
  - Architecture Council review process
  - parity scorecard
  - policy for code that remains in C indefinitely
- bootstrap ledger anchor: `docs(zigux): add documentation root, review checklist, and freeze map`
- ledger implication: the ledger only starts the documentation root and freeze-map family; it does not, by itself, prove the later Phase 15 governance bundle is present or enforced

## Current Repo Readiness

- `Documentation/zigux/freeze-map.md` is present and keeps the freeze-in-C and study-only anchors explicit
- `Documentation/zigux/review-checklist.md` is present and now asks for parity-scorecard evidence, decision records, rollback ownership, retained stay-in-C state, reopen triggers, and current lane ownership when freeze-map anchors are reviewed
- `Documentation/zigux/phase15-architecture-council-review-process.md` is present and records the required review packet plus bounded decision buckets
- `Documentation/zigux/phase15-parity-scorecard.md` is present and records the four freeze-in-C anchors, their lane owners, evidence thresholds, rollback owners, archive paths, and blocker dispositions
- `Documentation/zigux/phase15-indefinite-c-policy.md` is present and records the source-of-truth, exception, reopen, and retained-closeout posture for long-term C ownership
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` is present and records the parked handoff contract, named reopen conditions, and maintenance-mode next step for the already-landed governance bundle
- `zigux/tests/phase15_build.zig` is present, and focused replay on current `master` is green with `Build Summary: 13/13 steps succeeded; 16/16 tests passed`
- `zigux/Makefile` is present and exposes `make -C zigux phase15`, and the target remains aligned with the same shared replay path
- `.github/workflows/zigux-bootstrap.yml` is present and still runs `Run Phase 15 governance tests`, and that shared replay surface is once again reviewable as green on current `master`

That means the roadmap-required governance bundle is landed locally on current `master`, the bootstrap ledger anchor has already been carried forward into a fuller Phase 15 review surface, and the parked next-step handoff is also explicit inside the same governance family. It also means the tranche is governance-landed and replay-clean on current `master`, but deep-core status changes remain blocked.

## Remaining Readiness Gaps

### Deep-Core Status Changes Still Blocked

The live repo still does not have evidence strong enough to move any freeze-in-C anchor out of the current stay-in-C posture.

- `kernel/sched/core.c`: blocked by the absence of a bounded scheduler seam
- `mm/page_alloc.c`: blocked by the absence of a bounded allocator seam
- `kernel/rcu/tree.c`: blocked because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c`: blocked because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary

This means the Phase 15 tranche is governance-landed, replay-clean, and maintenance-ready on current `master`, but it is still not status-change-ready.

## Readiness Gate

The current readiness gate for trusting the Phase 15 tranche is:

1. the roadmap-required governance bundle is present and internally aligned
2. the bootstrap ledger anchor is still visible as the originating documentation root and freeze-map step
3. the local and shared-bootstrap Phase 15 replay surfaces stay present and green on current `master`
4. the parked handoff-and-next-step packet stays aligned with the same governance bundle
5. the remaining gaps stay explicit as blocked deep-core status changes pending stronger stay-in-C exception evidence

If any of those five conditions stops being true, the tranche is no longer ready for maintenance-mode governance.

## Recorded Gaps

The current lane state is:

- landed `phase15-readiness-gate-survey-doc`
- landed `phase15-readiness-gate-manifest`
- landed `phase15-readiness-gate-test`
- landed `phase15-build-gate-readiness`
- landed `phase15-shared-ci-coverage`
- landed `phase15-handoff-next-steps-synthesis`
- landed `phase15-shared-replay-recovery`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight. Zigux now has one reviewable readiness packet that says the roadmap bundle is landed, the ledger anchor is still visible, the shared bootstrap workflow still points at the current Phase 15 gate, the parked handoff-and-next-step packet is present in the same governance family, the broader replay path is green on current `master`, and the remaining Phase 15 readiness blocker is the still-blocked deep-core status-change posture.

## Non-goals

This slice does not claim:

- a new Phase 15 policy family beyond the already-landed governance bundle
- any Architecture Council approval for a freeze-map status change
- any new deep-core Zig bridge, wrapper, or direct port

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Keep the Phase 15 governance tranche in maintenance mode and treat the shared replay as recovered on current `master`. Reopen this readiness packet only if the shared Phase 15 replay drifts again or if the deep-core blocker posture changes enough to justify a narrower follow-up.

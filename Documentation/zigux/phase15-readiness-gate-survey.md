# Phase 15 Tranche Readiness Gate Survey

This document records the bounded Phase 15 readiness lane for surveying the remaining tranche-readiness gaps against the roadmap and bootstrap ledger.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_SLICE=tranche-readiness-gap-survey`
- scope: one readiness survey note, one dedicated manifest and Zig test, one shared `phase15_build.zig` follow-up, one shared bootstrap-workflow replay step, and one docs-root release-evidence comparison that together keep the roadmap requirements, bootstrap ledger anchor, current repo evidence, and remaining blocked readiness gaps reviewable in one place
- survey provenance refreshed against verified `master` head `ef7b33b6922d05e5ef514fb4efa588316ce6dda8`
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
  - `Documentation/zigux/README.md`
  - `zigux/tests/phase15_readiness_gate_manifest.json`
  - `zigux/tests/phase15_readiness_gate.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why this slice exists

The roadmap says Phase 15 is the governance tranche for the final mixed-language steady state. The bootstrap ledger, by contrast, only anchors the first documentation step: the documentation root, review checklist, and freeze map.

Current `master` is farther along than that ledger starting point. Zigux now already carries the freeze map, the review checklist hook, the Architecture Council review-process note, the parity scorecard, the indefinite-C policy note, the dedicated `phase15_build.zig` replay gate, the `make -C zigux phase15` convenience target, and the later handoff-and-next-step survey that keeps the parked maintenance contract explicit.

What this packet still needs to answer is narrower now:

- what the roadmap requires
- what the bootstrap ledger originally anchored
- what the live repo has actually landed and what remains blocked

That comparison still matters because the remaining Phase 15 gap is no longer a missing governance document or a missing shared replay wire-up. The dedicated replay surfaces are green on current `master`, but the docs-root Phase 15 summary still says the handoff includes remaining broader replay drift on current `master` even though the dedicated readiness and handoff packets now record the shared Phase 15 replay as green.

The honest bounded step therefore remains maintenance of the existing readiness packet, not another new governance policy surface or a neighboring replay-fix lane.

## Roadmap Versus Ledger

- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` Phase 15, `Full-Parity Blockers and Long-Term Governance`
- roadmap-required Phase 15 bundle:
  - freeze map
  - Architecture Council review process
  - parity scorecard
  - policy for code that remains in C indefinitely
- bootstrap ledger anchor: `docs(zigux): add documentation root, review checklist, and freeze map`
- ledger implication: the ledger only starts the documentation root and freeze-map family; it does not, by itself, prove the later Phase 15 governance bundle is present or that the top-level docs root stays aligned with the later maintenance packet

## Current Repo Readiness

- `Documentation/zigux/freeze-map.md` is present and keeps the freeze-in-C and study-only anchors explicit
- `Documentation/zigux/review-checklist.md` is present and now asks for parity-scorecard evidence, decision records, rollback ownership, retained stay-in-C state, reopen triggers, and current lane ownership when freeze-map anchors are reviewed
- `Documentation/zigux/phase15-architecture-council-review-process.md` is present and records the required review packet plus bounded decision buckets
- `Documentation/zigux/phase15-parity-scorecard.md` is present and records the four freeze-in-C anchors, their lane owners, evidence thresholds, rollback owners, archive paths, and blocker dispositions
- `Documentation/zigux/phase15-indefinite-c-policy.md` is present and records the source-of-truth, exception, reopen, and retained-closeout posture for long-term C ownership
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` is present and records the parked handoff contract, named reopen conditions, and maintenance-mode next step for the already-landed governance bundle
- `zigux/tests/phase15_build.zig` is present and defines the shared Phase 15 replay surface for the current governance bundle
- `zigux/Makefile` is present and exposes `make -C zigux phase15`, and the target remains aligned with the same shared replay path
- `.github/workflows/zigux-bootstrap.yml` is present and runs `Run Phase 15 governance tests`, so the same shared replay surface remains the published Phase 15 gate on current `master`
- `Documentation/zigux/README.md` exposes the Phase 15 governance notes and the direct handoff pointer from the docs root, but it still summarizes the handoff as if broader replay drift remains on current `master`
- the dedicated readiness and handoff packets both record the shared Phase 15 replay as green on current `master`

That means the roadmap-required governance bundle is landed on current `master`, the bootstrap ledger anchor has already been carried forward into a fuller Phase 15 review surface, and the shared replay surfaces are green. But the tranche is still not fully readiness-clean because the docs-root Phase 15 summary is not aligned with the dedicated readiness and handoff packet, and the longer-lived blocker is still whether any deep-core anchor ever earns evidence strong enough to leave the freeze-in-C posture.

## Remaining Readiness Gaps

### Docs-Root Phase 15 Summary Still Drifts

The docs-root Phase 15 summary still says the handoff includes remaining broader replay drift on current `master` even though the dedicated readiness and handoff packets now record the shared Phase 15 replay as green.

- `Documentation/zigux/README.md` still uses the stale broader-drift wording
- `Documentation/zigux/phase15-readiness-gate-survey.md` records the dedicated replay posture as green
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` records the same replay posture as green

This keeps the lane honest: the repo does not need another governance note or another replay wire-up here, but it does still need the top-level Phase 15 release evidence aligned with the already-landed dedicated packet.

### Deep-Core Status Changes Still Blocked

The live repo still does not have evidence strong enough to move any freeze-in-C anchor out of the current stay-in-C posture.

- `kernel/sched/core.c`: blocked by the absence of a bounded scheduler seam
- `mm/page_alloc.c`: blocked by the absence of a bounded allocator seam
- `kernel/rcu/tree.c`: blocked because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c`: blocked because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary

This means the Phase 15 tranche is governance-landed and the dedicated replay surfaces are green on current `master`, but it is still not status-change-ready and still not fully readiness-clean because the docs-root Phase 15 release evidence remains stale.

## Readiness Gate

The current readiness gate for trusting the Phase 15 tranche is:

1. the roadmap-required governance bundle is present and internally aligned
2. the bootstrap ledger anchor is still visible as the originating documentation root and freeze-map step
3. the local and shared-bootstrap Phase 15 replay surfaces stay present and green on current `master`
4. the parked handoff-and-next-step packet stays aligned with the same governance bundle
5. the docs-root Phase 15 summary matches that current replay posture instead of reintroducing stale broader-drift wording
6. the remaining gaps stay explicit as a docs-root release-evidence drift plus blocked deep-core status changes pending stronger stay-in-C exception evidence

If any of those six conditions stops being true, the tranche is no longer ready for maintenance-mode governance review.

## Recorded Gaps

The current lane state is:

- landed `phase15-readiness-gate-survey-doc`
- landed `phase15-readiness-gate-manifest`
- landed `phase15-readiness-gate-test`
- landed `phase15-build-gate-readiness`
- landed `phase15-shared-ci-coverage`
- landed `phase15-handoff-next-steps-synthesis`
- blocked `phase15-docs-root-summary-drift-blocker`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight. Zigux now has one reviewable readiness packet that says the roadmap bundle is landed, the ledger anchor is still visible, the shared bootstrap workflow still points at the current Phase 15 gate, the parked handoff-and-next-step packet is present in the same governance family, the dedicated replay path is green on current `master`, and the remaining honest gaps are the stale docs-root summary plus the unchanged deep-core status-change posture.

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

Keep this readiness lane parked unless the docs-root Phase 15 summary is refreshed to match the dedicated readiness and handoff packet, or the deep-core blocker posture changes. When either happens, rerun the dedicated readiness guard, `python3 scripts/zigux/validate-phase15.py`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15` before refreshing neighboring governance packets.

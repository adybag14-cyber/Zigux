# Phase 15 Tranche Readiness Gate Survey

This document records the bounded Phase 15 readiness lane for surveying the remaining tranche-readiness gaps against the roadmap and bootstrap ledger.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_SLICE=tranche-readiness-gap-survey`
- scope: one readiness survey note, one dedicated manifest and Zig test, one shared `phase15_build.zig` follow-up, one shared bootstrap-workflow replay step, and the later handoff-and-next-step packet that together keep the roadmap requirements, bootstrap ledger anchor, current repo evidence, and remaining blocked readiness gaps reviewable in one place
- survey provenance refreshed against verified `master` head `cdf383232e3e457496e49a630ee20f3df86bae86`
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

That comparison still matters because the remaining Phase 15 gaps are no longer "missing governance documents" or missing shared replay wiring. The shared bootstrap workflow still runs the Phase 15 governance bundle, but the full shared Phase 15 replay is currently red on `master`, and no deep-core anchor yet has evidence strong enough to leave the freeze-in-C posture.

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
- `zigux/tests/phase15_build.zig` is present, but focused replay on current `master` is red because `phase15_architecture_council_review_process.zig` and `phase15_handoff_next_steps.zig` still hit `error.StreamTooLong` while reading `Documentation/zigux/README.md`
- `zigux/Makefile` is present and exposes `make -C zigux phase15`, but the target currently fails for the same shared replay drift because it delegates to `zigux/tests/phase15_build.zig`
- `.github/workflows/zigux-bootstrap.yml` is present and still runs `Run Phase 15 governance tests`, but that shared replay surface cannot currently be treated as green until the same read-limit drift is repaired

That means the roadmap-required governance bundle is landed locally on current `master`, the bootstrap ledger anchor has already been carried forward into a fuller Phase 15 review surface, and the parked next-step handoff is also explicit inside the same governance family. It also means the tranche is governance-landed but not fully readiness-clean: one shared replay drift still blocks the broader gate, and deep-core status changes remain blocked.

## Remaining Readiness Gaps

### Shared Phase 15 Replay Drift Still Blocked

The live repo still does not have a clean current-master replay for the wider shared Phase 15 gate.

- `zig build test --build-file zigux/tests/phase15_build.zig --summary all`: currently fails because `phase15_architecture_council_review_process.zig` and `phase15_handoff_next_steps.zig` exceed their current `Documentation/zigux/README.md` read limits and raise `error.StreamTooLong`
- `make -C zigux phase15`: currently fails for the same reason because it delegates to `zigux/tests/phase15_build.zig`
- `.github/workflows/zigux-bootstrap.yml`: still carries `Run Phase 15 governance tests`, but the shared replay surface is not currently green until the same reader-limit drift is repaired in a neighboring Phase 15 maintenance lane

### Deep-Core Status Changes Still Blocked

The live repo still does not have evidence strong enough to move any freeze-in-C anchor out of the current stay-in-C posture.

- `kernel/sched/core.c`: blocked by the absence of a bounded scheduler seam
- `mm/page_alloc.c`: blocked by the absence of a bounded allocator seam
- `kernel/rcu/tree.c`: blocked because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c`: blocked because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary

This means the Phase 15 tranche is governance-landed, but it is not yet fully maintenance-ready and it is still not status-change-ready.

## Readiness Gate

The current readiness gate for trusting the Phase 15 tranche is:

1. the roadmap-required governance bundle is present and internally aligned
2. the bootstrap ledger anchor is still visible as the originating documentation root and freeze-map step
3. the local and shared-bootstrap Phase 15 replay surfaces stay present and green on current `master`
4. the parked handoff-and-next-step packet stays aligned with the same governance bundle
5. the remaining gaps stay explicit as:
   - blocked shared Phase 15 replay drift pending the neighboring reader-limit repair
   - blocked deep-core status changes pending stronger stay-in-C exception evidence

If any of those five conditions stops being true, the tranche is no longer ready for maintenance-mode governance.

## Recorded Gaps

The current lane state is:

- landed `phase15-readiness-gate-survey-doc`
- landed `phase15-readiness-gate-manifest`
- landed `phase15-readiness-gate-test`
- landed `phase15-build-gate-readiness`
- landed `phase15-shared-ci-coverage`
- landed `phase15-handoff-next-steps-synthesis`
- blocked `phase15-shared-replay-drift-blocker`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight. Zigux now has one reviewable readiness packet that says the roadmap bundle is landed, the ledger anchor is still visible, the shared bootstrap workflow still points at the current Phase 15 gate, the parked handoff-and-next-step packet is present in the same governance family, the broader replay path is presently drifted on current `master`, and the remaining Phase 15 readiness blockers are that shared replay drift plus the still-blocked deep-core status-change posture.

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

Keep the Phase 15 governance tranche in maintenance mode, but do not treat it as fully readiness-clean again until a neighboring Phase 15 maintenance lane repairs the `Documentation/zigux/README.md` read limits in `phase15_architecture_council_review_process.zig` and `phase15_handoff_next_steps.zig`. After that replay fix lands, rerun the full Phase 15 build and confirm that the deep-core status-change posture is the only remaining readiness blocker.

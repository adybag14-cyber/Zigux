# Phase 15 Tranche Readiness Gate Survey

This document records the bounded Phase 15 readiness lane for surveying the remaining tranche-readiness gaps against the roadmap and bootstrap ledger.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_SLICE=tranche-readiness-gap-survey`
- scope: one readiness survey note, one dedicated manifest and Zig test, one shared `phase15_build.zig` follow-up, and one shared bootstrap-workflow replay step that keep the roadmap requirements, bootstrap ledger anchor, current repo evidence, and remaining blocked readiness gaps reviewable in one place
- survey provenance refreshed against verified `master` head `783e573845f21769925870e53a591e48878bb7f0`
- product boundary:
  - `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
  - `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `zigux/tests/phase15_readiness_gate_manifest.json`
  - `zigux/tests/phase15_readiness_gate.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why this slice exists

The roadmap says Phase 15 is the governance tranche for the final mixed-language steady state. The bootstrap ledger, by contrast, only anchors the first documentation step: the documentation root, review checklist, and freeze map.

Current `master` is farther along than that ledger starting point. Zigux now already carries the freeze map, the review checklist hook, the Architecture Council review-process note, the parity scorecard, the indefinite-C policy note, the dedicated `phase15_build.zig` replay gate, and the `make -C zigux phase15` convenience target.

What was still missing was one dedicated readiness packet that compares those three views together:

- what the roadmap requires
- what the bootstrap ledger originally anchored
- what the live repo has actually landed and what remains blocked

That comparison still matters because the remaining Phase 15 gap is no longer “missing governance documents” or missing shared replay coverage. The shared bootstrap workflow now runs the Phase 15 governance bundle, and the only remaining readiness blocker is that no deep-core anchor has evidence strong enough to leave the freeze-in-C posture.

The honest bounded step therefore remains maintenance of the existing readiness packet, not another new governance policy surface.

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
- `zigux/tests/phase15_build.zig` is present and replays the Phase 15 governance bundle locally
- `zigux/Makefile` is present and exposes `make -C zigux phase15`
- `.github/workflows/zigux-bootstrap.yml` is present and now runs `Run Phase 15 governance tests` so the current governance bundle is also replayed in the shared bootstrap workflow

That means the roadmap-required governance bundle is landed locally on current `master`, and the bootstrap ledger anchor has already been carried forward into a fuller Phase 15 review surface.

## Remaining Readiness Gaps

### Deep-Core Status Changes Still Blocked

The live repo still does not have evidence strong enough to move any freeze-in-C anchor out of the current stay-in-C posture.

- `kernel/sched/core.c`: blocked by the absence of a bounded scheduler seam
- `mm/page_alloc.c`: blocked by the absence of a bounded allocator seam
- `kernel/rcu/tree.c`: blocked because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c`: blocked because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary

This means the Phase 15 tranche is governance-ready but not status-change-ready.

## Readiness Gate

The current readiness gate for trusting the Phase 15 tranche is:

1. the roadmap-required governance bundle is present and internally aligned
2. the bootstrap ledger anchor is still visible as the originating documentation root and freeze-map step
3. the local and shared-bootstrap Phase 15 replay surfaces stay green
4. the remaining gaps stay explicit as:
   - blocked deep-core status changes pending stronger stay-in-C exception evidence

If any of those four conditions stops being true, the tranche is no longer ready for maintenance-mode governance.

## Recorded Gaps

The current lane state is:

- landed `phase15-readiness-gate-survey-doc`
- landed `phase15-readiness-gate-manifest`
- landed `phase15-readiness-gate-test`
- landed `phase15-build-gate-readiness`
- landed `phase15-shared-ci-coverage`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight. Zigux now has one reviewable readiness packet that says the roadmap bundle is landed, the ledger anchor is still visible, the shared bootstrap workflow replays the current Phase 15 gate, and the only remaining Phase 15 readiness gap is the still-blocked deep-core status-change posture.

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

Keep the Phase 15 governance tranche in maintenance mode. The next honest action inside this readiness lane is to wait for new deep-core evidence that actually changes one of the current blocker dispositions.

# Phase 15 Tranche Readiness Gate Survey

This document records the bounded Phase 15 readiness lane for surveying the remaining tranche-readiness gaps against the roadmap and bootstrap ledger.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_SLICE=tranche-readiness-gap-survey`
- scope: one readiness survey note, one dedicated manifest and Zig test, one shared `phase15_build.zig` follow-up, one shared bootstrap-workflow replay step, and the later handoff-and-next-step packet that together keep the roadmap requirements, bootstrap ledger anchor, current repo evidence, and remaining blocked readiness gaps reviewable in one place
- survey provenance refreshed against verified `master` head `b4e2a41748d166b129cd1a0d95d2d9046f877c78`
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

That comparison still matters because the remaining Phase 15 gap is no longer a missing governance document or a missing shared replay wire-up. The shared bootstrap workflow still runs the Phase 15 governance bundle, but the full shared Phase 15 replay is not currently green on `master`, and the longer-lived blocker is still whether any deep-core anchor ever earns evidence strong enough to leave the freeze-in-C posture.

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
- `zigux/tests/phase15_build.zig` is present and still defines the shared Phase 15 replay surface, but current `master` no longer supports an honest replay-green claim for that surface
- `zigux/Makefile` is present and exposes `make -C zigux phase15`, and the target remains aligned with the same shared replay path
- `.github/workflows/zigux-bootstrap.yml` is present and still runs `Run Phase 15 governance tests`, so the same shared replay surface remains the published Phase 15 gate on current `master`
- `Documentation/zigux/README.md` no longer exposes the dedicated `Phase 15 notes` block or the direct `phase15-handoff-next-steps-survey.md` pointer that earlier readiness and handoff packets were using as docs-index evidence
- `zigux/tests/phase15_parity_scorecard.zig` is truncated mid-review-gate on current `master`, so the shared replay cannot currently finish that neighboring scorecard assertion path

That means the roadmap-required governance bundle is landed locally on current `master`, the bootstrap ledger anchor has already been carried forward into a fuller Phase 15 review surface, and the parked next-step handoff is also explicit inside the same governance family. It also means the tranche is governance-landed, but not yet maintenance-ready as a governance packet because the shared replay surface has drifted and the deep-core status-change posture remains blocked.

## Remaining Readiness Gaps

### Shared Replay Surface Is Red

The current shared replay is blocked by adjacent Phase 15 packet drift on current `master`.

- `Documentation/zigux/README.md` no longer carries the expected `Phase 15 notes` block or the direct `phase15-handoff-next-steps-survey.md` pointer named by the neighboring review-process and handoff packets
- `zigux/tests/phase15_parity_scorecard.zig` is truncated mid-review-gate, so the scorecard-side replay path is not currently trustworthy on published `master`
- `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, and `Documentation/zigux/phase15-handoff-next-steps-survey.md` still describe a landed governance family, but the broader replay should be treated as red until a neighboring repair lane restores those readback surfaces

That is enough to keep both `zig build test --build-file zigux/tests/phase15_build.zig --summary all` and `make -C zigux phase15` out of maintenance-ready territory on current `master`, even though the dedicated validator-first packet and the longer-lived deep-core blocker posture remain explicit.

### Deep-Core Status Changes Still Blocked

The live repo still does not have evidence strong enough to move any freeze-in-C anchor out of the current stay-in-C posture.

- `kernel/sched/core.c`: blocked by the absence of a bounded scheduler seam
- `mm/page_alloc.c`: blocked by the absence of a bounded allocator seam
- `kernel/rcu/tree.c`: blocked because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c`: blocked because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary

This means the Phase 15 tranche is governance-landed on current `master`, but it is not yet maintenance-ready or status-change-ready.

## Readiness Gate

The current readiness gate for trusting the Phase 15 tranche is:

1. the roadmap-required governance bundle is present and internally aligned
2. the bootstrap ledger anchor is still visible as the originating documentation root and freeze-map step
3. the local and shared-bootstrap Phase 15 replay surfaces stay present, and any replay-red drift is named explicitly before maintenance-ready claims are made
4. the parked handoff-and-next-step packet stays aligned with the same governance bundle
5. the docs index, the neighboring scorecard replay sources, and the handoff wording stay aligned enough that the shared Phase 15 replay can be trusted again
6. the remaining gaps stay explicit as blocked deep-core status changes pending stronger stay-in-C exception evidence

If any of those six conditions stops being true, the tranche is no longer ready for maintenance-mode governance.

## Recorded Gaps

The current lane state is:

- landed `phase15-readiness-gate-survey-doc`
- landed `phase15-readiness-gate-manifest`
- landed `phase15-readiness-gate-test`
- landed `phase15-build-gate-readiness`
- landed `phase15-shared-ci-coverage`
- landed `phase15-handoff-next-steps-synthesis`
- ready_next `phase15-shared-replay-drift-blocker`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight. Zigux now has one reviewable readiness packet that says the roadmap bundle is landed, the ledger anchor is still visible, the shared bootstrap workflow still points at the current Phase 15 gate, the parked handoff-and-next-step packet is present in the same governance family, the broader replay path is currently red on current `master` because of a docs-index plus parity-scorecard replay drift, and the remaining longer-lived Phase 15 blocker is still the deep-core status-change posture.

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

Keep this readiness lane parked until an adjacent replay-repair lane restores the shared Phase 15 replay or the deep-core blocker posture changes. When the replay repair lands, rerun the dedicated readiness guard, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15` before refreshing neighboring governance packets.
# Phase 15 Tranche Readiness Gate Survey

This document records the bounded Phase 15 readiness lane for surveying the remaining tranche-readiness gaps against the roadmap and bootstrap ledger.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_SLICE=tranche-readiness-gap-survey`
- scope: one readiness survey note, one dedicated manifest and Zig test, one shared `phase15_build.zig` follow-up, one shared bootstrap-workflow replay step, and one docs-root release-evidence alignment readback that together keep the roadmap requirements, bootstrap ledger anchor, current repo evidence, and remaining blocked readiness gaps reviewable in one place
- survey provenance last refreshed against reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`; later repo movement touching this readiness packet now requires a fresh bounded provenance refresh before this note should make a new current-`master` claim
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
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `zigux/tests/phase15_readiness_gate_manifest.json`
  - `zigux/tests/phase15_readiness_gate.zig`
  - `zigux/tests/phase15_docs_root_reviewability.zig`
  - `zigux/tests/phase15_evidence_archive_templates.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Why this slice exists

The roadmap says Phase 15 is the governance tranche for the final mixed-language steady state. The bootstrap ledger, by contrast, only anchors the first documentation step: the documentation root, review checklist, and freeze map.

Reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4` was already farther along than that ledger starting point. Zigux had already landed the freeze map, the review checklist hook, the Architecture Council review-process note, the parity scorecard, the indefinite-C policy note, the dedicated `phase15_build.zig` replay gate, the dedicated `check-phase15-review-process-handoff.py` route, the `make -C zigux phase15` convenience target, and the later handoff-and-next-step survey that keeps the parked maintenance contract explicit.

What this packet still needs to answer is narrower now:

- what the roadmap requires
- what the bootstrap ledger originally anchored
- what the reviewed repo head had actually landed and what remained blocked

That comparison still matters because the remaining Phase 15 gap is no longer a missing governance document, a missing shared replay wire-up, or a docs-root release-evidence contradiction. The dedicated replay surfaces were green at reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`, the dedicated handoff-checker route remained explicit there through `scripts/zigux/check-phase15-review-process-handoff.py --self-test` and `scripts/zigux/check-phase15-review-process-handoff.py`, and the docs-root Phase 15 summary was aligned with the dedicated readiness and handoff packet there.

The honest bounded step therefore remains maintenance of the existing readiness packet, not another new governance policy surface or a neighboring replay-fix lane.

## Roadmap Versus Ledger

- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` Phase 15, `Full-Parity Blockers and Long-Term Governance`
- roadmap-required Phase 15 bundle:
  - freeze map
  - Architecture Council review process
  - parity scorecard
  - policy for code that remains in C indefinitely
- bootstrap ledger anchor: `docs(zigux): add documentation root, review checklist, and freeze map`
- ledger implication: the ledger only starts the documentation root and freeze-map family; it does not, by itself, prove the later Phase 15 governance bundle is present or that the maintenance-mode packet stays aligned on the docs root

## Readiness at Reviewed Head

At reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`, the repo already had:

- `Documentation/zigux/freeze-map.md` is present and keeps the freeze-in-C and study-only anchors explicit
- `Documentation/zigux/review-checklist.md` is present and now asks for parity-scorecard evidence, decision records, rollback ownership, retained stay-in-C state, reopen triggers, and current lane ownership when freeze-map anchors are reviewed
- `Documentation/zigux/phase15-architecture-council-review-process.md` is present and records the required review packet plus bounded decision buckets
- `scripts/zigux/check-phase15-review-process-handoff.py` is present and keeps the dedicated review-process handoff inventory, readiness packet, docs-root reviewability guard, scripts-root validator path, dedicated handoff-checker route, and tests-root guidance path explicit before the broader validator-first and shared replay route is trusted
- `Documentation/zigux/phase15-parity-scorecard.md` is present and records the four freeze-in-C anchors, their lane owners, evidence thresholds, rollback owners, archive paths, and blocker dispositions
- `Documentation/zigux/phase15-indefinite-c-policy.md` is present and records the source-of-truth, exception, reopen, and retained-closeout posture for long-term C ownership
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` is present and records the parked handoff contract, named reopen conditions, and maintenance-mode next step for the already-landed governance bundle
- `scripts/zigux/validate-phase15.py` is present and stays the dedicated validator script for the Phase 15 governance packet
- `zigux/tests/phase15_build.zig` is present and defines the shared Phase 15 replay surface for the current governance bundle
- `zigux/Makefile` is present and exposes `make -C zigux phase15-validate`, so the dedicated handoff checker route and validator-first target remain reviewable as separate gates before the shared replay path is trusted
- `zigux/Makefile` is present and exposes `make -C zigux phase15`, and the target remains aligned with the same shared replay path
- `.github/workflows/zigux-bootstrap.yml` is present and runs `Run Phase 15 governance tests`, so the same shared replay surface remained the published Phase 15 gate at reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`
- `Documentation/zigux/README.md` exposes the Phase 15 governance notes, the direct handoff pointer, and the same maintenance-mode posture as the dedicated readiness and handoff packet
- `zigux/tests/phase15_docs_root_reviewability.zig` is present and keeps the docs-root Phase 15 summary aligned with the dedicated readiness and handoff packet under that same shared replay surface
- `zigux/tests/phase15_evidence_archive_templates.zig` is present and keeps the reserved evidence-archive decision-record templates reviewable under that same shared replay surface
- the dedicated readiness and handoff packets both record the shared Phase 15 replay as green at reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`

That means the roadmap-required governance bundle was present at reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`, the bootstrap ledger anchor had already been carried forward into a fuller Phase 15 review surface there, the dedicated handoff-checker route, validator script, and validator-first target stayed explicit as release evidence before the shared replay surface was trusted there, the dedicated evidence-archive template guard kept the reserved archive packet reviewable there, and the dedicated readiness plus handoff notes recorded that same reviewed-head posture. Later repo movement still requires a fresh bounded provenance refresh before this note should restate any of that as a new current-`master` claim.

## Remaining Readiness Gaps

### Deep-Core Status Changes Still Blocked

The reviewed Phase 15 packet still did not have evidence strong enough to move any freeze-in-C anchor out of the current stay-in-C posture.

- `kernel/sched/core.c`: blocked by the absence of a bounded scheduler seam
- `mm/page_alloc.c`: blocked by the absence of a bounded allocator seam
- `kernel/rcu/tree.c`: blocked because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c`: blocked because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary

This means the Phase 15 tranche was governance-landed, the dedicated replay surfaces were green, the dedicated handoff-checker route remained explicit, and the docs-root release evidence was aligned at reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`, but it was still not status-change-ready there. Later repo movement now requires a fresh bounded provenance refresh before this note should restate those green or aligned claims for current `master`.

## Readiness Gate

The readiness gate recorded by this packet is:

1. the roadmap-required governance bundle is present and internally aligned
2. the bootstrap ledger anchor is still visible as the originating documentation root and freeze-map step
3. the dedicated handoff-checker route, the dedicated validator script, and `make -C zigux phase15-validate` target stay present before the shared replay and shared-bootstrap surfaces are trusted on current `master`
4. the parked handoff-and-next-step packet stays aligned with the same governance bundle
5. the docs-root Phase 15 summary stays aligned with that current replay posture and maintenance-mode handoff
6. the dedicated docs-root reviewability guard stays aligned with the same readiness and handoff packet instead of leaving that top-level release-evidence path implicit
7. the dedicated evidence-archive template guard stays explicit inside the same shared replay path instead of leaving the reserved per-anchor decision-record packet implicit
8. the remaining gap stays explicit as blocked deep-core status changes pending stronger stay-in-C exception evidence

If any one of those eight conditions stops being true, the tranche is no longer ready for maintenance-mode governance review.

## Recorded Gaps

The current lane state is:

- landed `phase15-readiness-gate-survey-doc`
- landed `phase15-readiness-gate-manifest`
- landed `phase15-readiness-gate-test`
- landed `phase15-build-gate-readiness`
- landed `phase15-shared-ci-coverage`
- landed `phase15-handoff-next-steps-synthesis`
- landed `phase15-docs-root-summary-alignment`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight. At reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`, Zigux had one reviewable readiness packet that said the roadmap bundle was landed, the ledger anchor was still visible, the dedicated handoff-checker route, validator script, and validator-first target remained explicit before the shared replay, the shared bootstrap workflow still pointed at the reviewed Phase 15 gate, the parked handoff-and-next-step packet was present in the same governance family, the dedicated docs-root reviewability guard remained visible inside that same review path, the dedicated evidence-archive template guard remained visible inside that same review path, the dedicated replay path was green there, the docs-root Phase 15 summary matched that same maintenance-mode packet there, and any new current-`master` restatement now requires a fresh bounded provenance refresh, while the remaining honest gap is the unchanged deep-core status-change posture.

## Non-goals

This slice does not claim:

- a new Phase 15 policy family beyond the already-landed governance bundle
- any Architecture Council approval for a freeze-map status change
- any new deep-core Zig bridge, wrapper, or direct port

## Gates

1. run the validator-first gate
- `python3 scripts/zigux/validate-phase15.py`
- `make -C zigux phase15-validate`

2. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

3. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Keep this readiness lane parked unless the shared Phase 15 replay drifts, a named reopen trigger now fits the evidence packet again, or the deep-core blocker posture changes. When one of those conditions changes, rerun the dedicated readiness guard, `python3 scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15` before refreshing neighboring governance packets.

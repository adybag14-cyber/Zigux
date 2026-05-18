# Zigux Release Sequencing

This note is the top-level PMO sequencing companion for the current `master` packet set.

It is a release-planning artifact, not a tranche-closure claim and not a substitute for helper-local validation.

## Status

- `RELEASE_PLAN_STATE=active`
- `RELEASE_PLAN_SCOPE=phase sequencing, tranche closure, and release coordination artifacts`
- roadmap authority: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- bootstrap ledger authority: `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- release-sequencing guard: `python3 scripts/zigux/check-release-sequencing.py`
- foundation closures: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase2-closure.md`

## Sequencing Baseline

- `RELEASE_FOUNDATION_PHASES=phase1,phase2`
- `RELEASE_ACTIVE_GATING_PHASES=phase3,phase4`
- `RELEASE_CONDITIONAL_RELEASE_PHASES=phase5`
- `RELEASE_SUPPORTING_PHASES=phase6,phase8,phase13`

Keep the current release story ordered this way:

1. Phase 1 and Phase 2 stay parked as the release foundation unless reminder drift or returned repo material forces a same-lane reread.
2. Phase 3 and Phase 4 are the active pre-release gating tranche because they carry the ABI, interop, rollback, and reversible-delivery packet work needed before broader release claims become credible.
3. Phase 5 stays conditional on the active Phase 3 and Phase 4 gates remaining aligned because it is a sample-facing release surface, not an alternate closure route.
4. Phase 6, Phase 8, and Phase 13 stay supporting release evidence and must not be presented as substitutes for the active Phase 3 and Phase 4 gating tranche.

## Current Tranche Map

- `phase1`: parked foundation closure packet. Keep `Documentation/zigux/phase1-closure.md` and its reminder guards as the release-baseline helper tranche rather than reopening older missing routes.
- `phase2`: parked toolchain closure packet. Keep `Documentation/zigux/phase2-closure.md` and the shipped toolchain and kbuild reminder packet as the release-baseline build tranche.
- `phase3`: active ABI and interop gating tranche. Anchor release wording to `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-shared-reminder-gap.md`, and the starter-packet validator family.
- `phase4`: active reversible-delivery gating tranche. Anchor release wording to `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `Documentation/zigux/phase4-validation-matrix.md` while keeping broader missing checker and build companions explicit as gaps.
- `phase5`: conditional release-facing sample tranche. Keep `Documentation/zigux/phase5-sample-lane-sequencing.md` and `Documentation/zigux/phase5-sample-review-guide.md` aligned, but do not count sample-root progress as a replacement for Phase 3 or Phase 4 closure.
- `phase6`: supporting helper-evidence tranche. Keep `Documentation/zigux/phase6-helper-evidence-catalog.md` truthful as supporting evidence without promoting it into the active release gate.
- `phase8`: supporting tooling-helper tranche. Keep `Documentation/zigux/phase8-tooling-lane-sequencing.md` and the shipped helper packet explicit without widening it into deeper userspace-adjacent release claims.
- `phase13`: supporting shared-helper release tranche. Keep `Documentation/zigux/phase13-release-coordination-matrix.md` and its workflow companion aligned without treating the missing Phase 13 validate routes as already shipped release handles.

## Release Order For Current Master

1. Preserve the Phase 1 and Phase 2 closure packets as fixed release foundations.
2. Finish the Phase 3 shared-reminder follow-through before widening release claims around the ABI substrate.
3. Recheck the Phase 4 validation matrix and reversible-delivery packet after any Phase 3 movement.
4. Keep Phase 5 sample guidance aligned to the Phase 3 and Phase 4 gate posture.
5. Keep Phase 6, Phase 8, and Phase 13 contributor-facing and truthful as supporting release surfaces.

## Open Coordination Risks

- `RELEASE_RISK_PHASE3_SHARED_REMINDER=active`: current `master` still carries a Phase 3 shared-reminder gap and broader missing companion surfaces, so PMO should treat Phase 3 as active release work rather than closed substrate proof.
- `RELEASE_RISK_PHASE4_MISSING_COMPANIONS=active`: current `master` still keeps broader Phase 4 checker and build companions in repo-reality-gap wording, so release coordination should not overstate gate completeness.
- `RELEASE_RISK_PHASE13_VALIDATE_ROUTE=active`: current `master` still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so the Phase 13 matrix remains a coordination surface instead of a shipped release-validation handle.

## Review Use

When release-planning wording changes:

1. reread this note beside the phase-local closure and coordination notes it references
2. rerun `python3 scripts/zigux/check-release-sequencing.py`
3. keep foundation, active-gating, conditional, and supporting phases in the same order unless roadmap-backed repo reality changes
4. leave helper-local validation or closure expansion to the owning phase lane

## Boundaries

- This note does not close Phase 3 or Phase 4.
- This note does not reopen Phase 1 or Phase 2.
- This note does not convert Phase 6, Phase 8, or Phase 13 into release-gate substitutes.

## Next PMO Step

- `RELEASE_NEXT_PMO_STEP=refresh the docs-root release handle only if the phase-local closure or coordination notes drift against this sequencing baseline, otherwise keep the release order parked and let the active gating work stay in phase-local lanes`

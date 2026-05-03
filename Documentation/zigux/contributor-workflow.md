# Zigux Contributor Workflow

This guide is the short path for contributors who need to land one bounded Zigux improvement without widening scope or guessing at the repo's current delivery rules.

## Start With The Product Packet

Before editing anything, inspect the current packet that owns your slice.

Read these in order:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/freeze-map.md` when the slice is near deep-core or study-only boundaries
- the owning phase note under `Documentation/zigux/`
- the owning validator under `scripts/zigux/`
- the owning shared replay entrypoint under `zigux/Makefile` or `zigux/tests/`
- the manifest, survey note, or fixture packet that the validator already treats as source-of-truth evidence

If those files do not point at the same bounded lane, fix that drift first instead of adding more surface area.

## Choose Work That Counts

Prefer contributions that:
- improve a real helper, ABI slice, harness, validator, manifest, or review packet
- close a real docs or workflow gap around an already-landed tranche
- make a bounded phase packet more trustworthy by keeping docs, manifests, workflow hooks, and replay entrypoints aligned
- clarify rollback posture, explicit non-goals, or blocked-next-step status for a shipped slice

Avoid changes that mostly create noise:
- new wrappers or dumps without new validation or product value
- mixed-phase edits in one change
- fake parallel subsystem growth under a Zigux namespace
- experimental ZAR-shaped surfaces that do not reduce current Zigux product risk

## Working Rules

Use these rules on every change:
- keep one roadmap-backed lane per change
- keep the Linux anchor, phase, and status bucket explicit in docs and review notes
- keep runtime-risky or ABI-risky work validator-first
- keep survey or manifest packets honest about what is shipped, what is blocked, and what is only review scaffolding
- keep unsafe scope narrow and visibly owned
- keep deep-core freeze boundaries explicit unless the roadmap and governance packet say otherwise

## Validator-First Flow

The default Zigux workflow is:
1. choose one bounded slice
2. update the code or docs that own that slice
3. update the paired manifest, survey note, shared replay file, or Makefile hook in the same change when needed
4. run the validator-first command for that phase
5. run the broader replay command for that phase if the validator is green
6. report exactly what ran, what passed, and what remains blocked

Use these published entrypoints:
- Phase 1: `python3 scripts/zigux/validate-phase1.py` and `python3 scripts/zigux/validate-phase1-closure.py`
- Phase 2: `make -C zigux phase2-validate` then `make -C zigux phase2`
- Phase 3: `make -C zigux phase3-validate` then `make -C zigux phase3`
- Phase 4: `make -C zigux phase4-validate` then `make -C zigux phase4`
- Phase 5: `make -C zigux phase5-validate` then `make -C zigux phase5`
- Phase 6: `make -C zigux phase6-validate` then `make -C zigux phase6`
- Phase 7: `make -C zigux phase7-validate` then `make -C zigux phase7`
- Phase 8: `make -C zigux phase8-validate` then `make -C zigux phase8`
- Phase 9: `make -C zigux phase9-validate` then `make -C zigux phase9`
- Phase 10: `make -C zigux phase10-validate` then `make -C zigux phase10`
- Phase 11: `make -C zigux phase11-validate` then `make -C zigux phase11`
- Phase 12: `make -C zigux phase12-validate` then `make -C zigux phase12`
- Phase 13: `make -C zigux phase13-validate` then `make -C zigux phase13`
- Phase 14: `make -C zigux phase14-validate` then `make -C zigux phase14`
- Phase 15: `make -C zigux phase15-validate` then `make -C zigux phase15`

If your slice has a more focused replay, run it too.
Examples already published in the repo include `make -C zigux phase8-perf-buffer-poll-test`, `make -C zigux phase9-trace-events-survey`, `make -C zigux phase11-hvc-survey`, and `make -C zigux phase14-smoke`.

## Keep The Shared Surfaces Aligned

Contributors should check these shared surfaces whenever a packet changes:
- `Documentation/zigux/README.md` for the docs-root index and current phase summary
- `Documentation/zigux/review-checklist.md` for merge-time review questions
- `scripts/zigux/README.md` for validator-first routes and helper responsibilities
- `zigux/tests/README.md` for replay, survey, and shared-build guidance

When a slice is manifest-backed or survey-backed, keep the owning manifest, survey note, validator, and replay path aligned in the same change. Do not rely on run memory or an issue thread to explain missing context.

## How To Describe Results

A good close-out says:
- which lane, phase, and bounded target were changed
- why that change was the highest-value unfinished step inside the packet
- which validator-first and broader replay commands ran
- whether the result is fully green or partially blocked
- what the next bounded step is

If something is blocked, say what is blocked and what evidence is still missing. Do not turn partial validation into a closure claim.

## When To Stop

Stop and escalate instead of widening the change when:
- the next step crosses into another phase or lane
- the current packet needs a roadmap or governance decision first
- the deep-core freeze map would need a status change
- the validator and the docs disagree about what the packet owns
- the only available follow-up is wrapper churn rather than a real product improvement

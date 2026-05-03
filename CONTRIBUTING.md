# Contributing to Zigux

Zigux is roadmap-driven product work, not a general experiment bucket.

Before changing code or docs:
- read `Documentation/zigux/README.md` for the active product packet and current phase notes
- read `Documentation/zigux/review-checklist.md` before opening or merging work
- check `Documentation/zigux/freeze-map.md` if the change is anywhere near deep-core scheduler, MM, RCU, tracing, networking core, or other study-only areas
- keep one bounded roadmap-backed lane per change instead of mixing phases or widening scope mid-run

## Preferred change shape

Good contributions usually do one of these things:
- add or tighten a real helper, ABI slice, harness, manifest, or validator
- close a docs, checklist, or survey gap around an already-landed tranche
- fix drift between a manifest, survey note, shared build entrypoint, Makefile route, workflow hook, and validator
- improve reviewability or rollback clarity for a bounded roadmap packet

Avoid:
- mirror-tree sprawl
- wrapper or dump proliferation without new capability or validation value
- broad phase jumps in one change
- treating ZAR research as Zigux product progress unless it directly reduces Zigux product risk

## Workflow

1. Pick one roadmap-backed phase and one bounded target family.
2. Read the owning packet before editing.
   The minimum packet is usually the phase note in `Documentation/zigux/`, the relevant validator in `scripts/zigux/`, the shared replay entrypoint in `zigux/tests/` or `zigux/Makefile`, and the manifest or survey file for that slice.
3. Make the smallest coherent change that improves the packet.
4. Update the paired docs or evidence files in the same change.
   If you touch a manifest-backed slice, keep the survey note, validator, and replay path aligned too.
5. Run the validator-first command before the broader replay command.
6. Record blockers honestly.
   If validation is partial, say exactly what ran and what is still blocked.

## Validator-first commands

Use the narrowest published entrypoint for the phase you touched.

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

When a phase note or script documents a more focused shard such as `phase8-perf-buffer-poll-test` or `phase11-hvc-survey`, run that narrower entrypoint too when it matches your slice.

## Documentation expectations

Keep contributor-facing guidance aligned when you land a bounded workflow change:
- `Documentation/zigux/README.md` for the docs-root index and phase packet summaries
- `Documentation/zigux/review-checklist.md` for merge-time review questions
- `scripts/zigux/README.md` for validator-first entrypoints and helper responsibilities
- `zigux/tests/README.md` for shared replay and survey guidance

If one of those surfaces changes for your packet, update it in the same change instead of leaving the workflow implied.

## More detail

For the longer contributor playbook, including packet-selection guidance and the shared docs surfaces to inspect before editing, see `Documentation/zigux/contributor-workflow.md`.

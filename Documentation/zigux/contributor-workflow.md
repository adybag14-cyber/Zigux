# Zigux Contributor Workflow Guide

This guide is the shared contributor-facing workflow for Zigux product changes.

## Purpose

Use this guide when a change touches Zigux product code, validation, manifests, surveys, or review-facing documentation.

The goal is to keep every bounded Zigux slice reviewable in the same way:

- name the roadmap phase and Linux anchor clearly
- keep owner, validation gate, and rollback path explicit
- update the code, manifests, docs, and replay entrypoints together
- prefer validator-first review paths before broader replay commands

## Start here

Before editing a Zigux packet:

1. identify the roadmap phase, bounded slice, and owning lane
2. name the Linux anchor file or tree path
3. read `CONTRIBUTING.md` for the short contributor entrypoint and phase-first validator map
4. check `Documentation/zigux/review-checklist.md` for the shared review prompts
5. find the packet's validator-first entrypoint in `scripts/zigux/README.md`
6. find the focused replay or survey entrypoint in `zigux/tests/README.md`

If the change touches a Phase 5 sample or a later `runtime_*` starter under `samples/zigux/`, also check `samples/zigux/README.md` so approved reference samples do not drift into runtime-follow-on claims.

## Shared packet rule

Treat each bounded Zigux slice as one review packet.

When you change one part of the packet, update the other parts that make the same claim:

- implementation file or helper root
- manifest or fixture snapshot
- survey or slice note under `Documentation/zigux/`
- focused replay under `zigux/tests/`
- validator or checker under `scripts/zigux/`
- shared make or workflow entrypoint when that packet is already wired there

Do not leave a slice reviewable only from code or only from prose.

## Validator-first workflow

Use the narrowest honest validation path first.

1. run the packet's checker or validator from `scripts/zigux/README.md`
2. run the focused replay named by `zigux/tests/README.md` or `samples/zigux/README.md`
3. run the broader `make -C zigux phaseX-validate` or shared build path only when that packet already belongs to a wider tranche
4. record blockers plainly when a broader shared replay is red for unrelated reasons

Examples from current `master`:

- Phase 5 samples use `make -C zigux phase5-validate` before the shared `phase5_build.zig` replay
- Phase 9 runtime work keeps `make -C zigux phase9-validate` explicit before `make -C zigux phase9`
- Phase 13 release-discipline work keeps `make -C zigux phase13-validate` explicit before the shared replay

## Contributor-facing docs to keep aligned

Use these files as the shared contributor packet, depending on scope:

- `CONTRIBUTING.md` for the short contributor entrypoint and phase-first validator map
- `Documentation/zigux/review-checklist.md` for review prompts and boundary checks
- `scripts/zigux/README.md` for validator-first commands and checker ownership
- `zigux/tests/README.md` for focused replay and survey entrypoints
- `samples/zigux/README.md` for approved Phase 5 sample boundaries and later runtime follow-ons
- the owning phase note under `Documentation/zigux/` for bounded scope, non-goals, and surveyed-commit evidence

If a change alters how contributors are supposed to review or replay a slice, update every applicable guide in the same pass.

## Review reminders

Keep these repo-wide rules explicit in contributor work:

- avoid mirror-tree sprawl and deep-core scope creep
- keep freeze-map or study-only boundaries explicit instead of implied
- prefer bounded helper, harness, manifest, and survey work over wrapper proliferation
- keep `surveyed_commit` or equivalent inspected-head markers in sync when the packet uses them
- separate approved Phase 5 reference samples from later Phase 9 runtime starters in the same tree

## Done criteria

A contributor-facing packet is ready when:

- the review checklist, validator path, focused replay path, and owning note all describe the same bounded slice
- any workflow-only change keeps `CONTRIBUTING.md` plus this guide aligned with the same review checklist, scripts guide, and tests guide packet
- the updated packet has a narrow validation result or an explicit blocker note
- the change does not overstate runtime parity, transport scope, or frozen-area status

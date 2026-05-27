# Contributing to Zigux

Zigux moves forward through small, reviewable, roadmap-backed slices. Treat each change as one bounded product step, not a broad rewrite.

## Start Here

Read these files before you open or update a change:

1. `Documentation/zigux/README.md`
2. `Documentation/zigux/review-checklist.md`
3. `Documentation/zigux/freeze-map.md`
4. `Documentation/zigux/contributor-entrypoints.md`
5. `Documentation/zigux/contributor-workflow.md`
6. `scripts/zigux/README.md`
7. `zigux/tests/README.md`

Use `Documentation/zigux/contributor-entrypoints.md` to pick the right bounded guide for docs, checklist, or workflow work, and use `Documentation/zigux/contributor-workflow.md` for the routine edit loop once the lane is chosen.

Keep the top-level contributor onboarding packet aligned through:

1. `CONTRIBUTING.md`
2. `Documentation/zigux/contributor-entrypoints.md`
3. `Documentation/zigux/contributor-workflow.md`

Top-level onboarding guard: `python3 scripts/zigux/check-contributor-onboarding-packet.py`

If your change touches the shared contributor packet for Phase 13, also reread:

1. `Documentation/zigux/phase13-contributor-workflow-guide.md`
2. `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
3. `Documentation/zigux/phase13-release-coordination-matrix.md`

## Scope Rules

- Name the roadmap phase and the owning Linux anchor path.
- Keep the status bucket explicit: active port work, dual implementation, study only, or freeze in C initially.
- Prefer one coherent improvement per change.
- Keep product code co-located with the owning Linux subsystem when appropriate.
- Do not treat repetitive wrapper growth or reminder churn as real progress by itself.

## Freeze And Boundary Rules

- `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` stay frozen in C unless the documented Architecture Council path says otherwise.
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` are study-only boundaries, not active delivery targets.
- Do not widen a contributor or docs change into a status-change claim for a frozen or study-only anchor.

## Validation Expectations

Every change should keep these explicit:

- bounded scope
- validation gate or replay path
- rollback owner and fallback path
- any repo-reality gaps that are still gaps on current `master`

If you update the top-level contributor onboarding packet, rerun `python3 scripts/zigux/check-contributor-onboarding-packet.py` so the start-here entrypoint, onboarding guide, and routine workflow note stay aligned.

If you update a shared reminder surface, reread the neighboring docs, scripts, and tests notes together so they keep describing the same shipped packet.

## Phase 13 Shared-Helper Reminder Work

If your change is shared Phase 13 contributor wording rather than helper-local proof, use this bounded loop:

1. reread `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together first
2. keep `Documentation/zigux/phase13-release-coordination-matrix.md` and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` aligned as supporting coordination companions rather than the stable contributor-facing handle itself
3. rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`, `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`, and `python3 scripts/zigux/validate-phase13-release.py`
4. keep `zigux/Makefile` distinct from the still-missing `make -C zigux phase13-validate` and `make -C zigux phase13` routes

## Phase 13 Contributor Packet

The current shared contributor-facing handle runs through:

1. `Documentation/zigux/phase13-contributor-workflow-guide.md`
2. `scripts/zigux/README.md`
3. `zigux/tests/README.md`

Keep helper ownership split by packet instead of flattening Phase 13 into one generic summary:

- `libfs`
- `devres`
- `landlock/ruleset`
- `landlock/syscalls`

Adjacent notifier evidence supports release-surface truthfulness, but it is not a fifth helper family.

`zigux/Makefile` is readable on current `master`, but it is not by itself proof that missing Phase 13 `make -C zigux phase13-validate` or `make -C zigux phase13` routes have returned.

## Review Before Landing

Before landing a change, confirm that:

1. the roadmap phase, owner, validation gate, and rollback owner are explicit
2. the relevant docs, scripts, and tests surfaces still describe the same bounded packet
3. the change does not imply missing repo paths or routes are already shipped
4. the change stays inside the requested lane or helper family
5. any top-level onboarding wording still agrees across `CONTRIBUTING.md`, `Documentation/zigux/contributor-entrypoints.md`, and `Documentation/zigux/contributor-workflow.md`
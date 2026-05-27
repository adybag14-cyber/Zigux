# Phase 8 Deferred-Exec Gap Survey

This note records the bounded deferred-execution gap for the current Phase 8 `exec-cmd` packet against the Zigux roadmap.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=deferred-exec-gap-readback`
- roadmap anchor: `tools/lib/subcmd/exec-cmd.c`
- intended Zigux destination: `tools/lib/subcmd/exec-cmd.zig`
- scope: reviewability, roadmap comparison, and bounded next-step selection only

## Why this survey exists

The Phase 8 roadmap is about proving Zigux inside serious repo-hosted tooling while staying helper-first and output-stable. The current `exec-cmd` work already lands that helper-first foothold, but it does not yet authorize a deferred-execution substrate, queueing surface, or any scheduler-facing transport claim.

This survey keeps that line explicit so later reminder work does not accidentally promote a parked Phase 8 helper packet into a Phase 14-style execution-ownership story.

## Current landed packet

Current `master` already keeps the bounded deferred-exec review packet explicit through:

- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `tools/lib/subcmd/exec-cmd.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `scripts/zigux/check-phase8-exec-cmd-packet.py`
- `scripts/zigux/validate-phase8.py`
- `make -C zigux phase8-exec-cmd-test`
- `make -C zigux phase8-validate`

That packet already proves the bounded helper-first surface around path preparation, environment shaping, argv collection, `buildDeferredExeclCall()`, `buildDeferredExecvCall()`, the focused exec-cmd build shard, and the existing packet checker that keeps the shared reminder surfaces honest.

## Current bounded gap

The current Phase 8 packet still does not claim:

- no direct `execvp()` side effects
- no waiting or retry scheduling
- no queue ownership
- no scheduler-facing transport
- no handoff into `kernel/workqueue.c`
- no deferred-execution substrate ownership

That gap is consistent with the roadmap. Phase 8 gets a helper-first tooling foothold; it does not cross into runtime-substrate or workqueue behavior. `kernel/workqueue.c` remains a Phase 14 study-only boundary, so the current packet must stay launch-free and ownership-free even when it models future deferred handoff shapes.

## Roadmap comparison

Against the roadmap, the current state is honest and still helper-first:

- the landed packet belongs to Phase 8 because it stays in repo-hosted tooling under `tools/lib/subcmd/exec-cmd.c`
- the remaining deferred-exec gap is still intentionally parked because process launch, execution ownership, and queue transport would overclaim beyond the Phase 8 helper-first boundary
- any future workqueue-style or scheduler-facing execution substrate belongs to later boundary-study work, not this packet

## Next bounded step

Keep follow-up in this family limited to reminder-surface or validator truthfulness around the current deferred handoff packet, its focused build shard, and its existing packet checker unless a separate roadmap-backed lane explicitly reopens execution ownership.
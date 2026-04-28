# Phase 9 Runtime Loader Gap Survey

This document records the shared boot/runtime loader gap that still separates the landed `samples/zigux/runtime_*` starter surface from any future `zigux/kernel/runtime_loader.zig` consumer.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- scope: shared survey note, manifest-backed survey gate, explicit roadmap-boundary note for the mixed Phase 6 schedule wording, and a bounded shared runtime-loader request surface that keeps allocator plus init or exit handoff machine-checkable without claiming real runtime execution
- product boundary:
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`
  - `zigux/tests/runtime_loader_gap_manifest.json`
  - `zigux/tests/runtime_loader_gap_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/helpers/allocator_policy.zig`

## Why this slice exists

The schedule prompt for this lane mixes a `Phase 6` label with a runtime allocator and init-flow topic. The roadmap does not place runtime loader work in Phase 6.

Phase 6 stays limited to low-risk leaf helpers such as `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`. Runtime pilot modules do not appear until Phase 9, where the roadmap explicitly calls for `zigux/tests/runtime_*` plus `samples/zigux/runtime_*`.

The roadmap's first command and environment plumbing surfaces also sit outside this runtime lane. Those controls belong to `Phase 8`, where the product plan points at `tools/lib/subcmd/exec-cmd.c` and `tools/lib/subcmd/help.c` rather than any Phase 6 helper or already-landed Phase 9 runtime starter.

The live repo already reflects that split:

- the full bounded Phase 6 leaf-helper set is landed
- four Phase 9 runtime starter samples are landed under `samples/zigux/runtime_*`
- two sample-side loader plans are landed under `samples/zigux/runtime_*_loader.zig`
- the `runtime_atomic64` and `runtime_trace_events` starters still do not have shared loader-plan projections, so only half of the current runtime starters can emit the shared request contract
- a shared `zigux/kernel/runtime_loader.zig` request surface now exists

This survey keeps the lane honest by recording what is now landed and what is still blocked instead of pretending that runtime scheduling, polling, or event-loop work should be pulled forward into Phase 6.

The freeze map also keeps the adjacent scheduler substrate boundary explicit. `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this shared runtime-loader packet may record request-shape and blocker evidence, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

The review checklist also remains part of this bounded governance surface. For this runtime-loader starter family, the checklist still needs to keep three review cues explicit:

- no hidden runtime services
- no implicit allocation posture beyond the explicit allocator-handoff contract
- no unclear panic or unsafe ownership story

## Delivery ownership map

The manifest-backed catalog for this slice now names which file owns each part of the current delivery packet:

- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` owns the roadmap-boundary note, blocker posture, and bounded replay contract
- `Documentation/zigux/review-checklist.md` owns the runtime review guardrails and ownership prompts for the same evidence packet
- `Documentation/zigux/freeze-map.md` owns the study-only `kernel/workqueue.c` boundary and the Architecture Council reopen rule for any status change tied to scheduler-facing runtime substrate work
- `zigux/tests/runtime_loader_gap_manifest.json` owns the manifest-backed catalog and ownership map for the current delivery packet
- `zigux/tests/runtime_loader_gap_survey.zig` owns the machine-checkable replay of the manifest, note, and shared request surface
- `zigux/tests/phase9_build.zig` owns the shared Phase 9 runtime bundle replay entrypoint
- `zigux/kernel/runtime_loader.zig` owns the shared request contract plus allocator and init or exit handoff fields
- `samples/zigux/runtime_bitmap_loader.zig` owns the bitmap loader-plan projection into the shared runtime request surface
- `samples/zigux/runtime_kretprobe_loader.zig` owns the kretprobe loader-plan projection into the shared runtime request surface

## Current blocker posture

The current runtime pilot surface already exposes reviewable loader inputs:

- `samples/zigux/runtime_bitmap_loader.zig` records explicit entry and exit symbol names, `requires_runtime_substrate`, `provides_selftest_hook`, and a bounded handoff stage
- `samples/zigux/runtime_kretprobe_loader.zig` records the same loader-shape inputs for the kretprobe starter
- `zigux/helpers/allocator_policy.zig` already records the explicit caller-vs-fallback allocator posture that a future runtime loader must consume rather than bypass

What is now landed is the smallest shared consumer contract:

- `zigux/kernel/runtime_loader.zig` defines a common loader-stage vocabulary for shared runtime handoff
- the shared request shape carries module identity, Linux anchor provenance, entry and exit symbol names, and a tagged payload for either bitmap or kretprobe facts
- the shared request also consumes `zigux/helpers/allocator_policy.zig` through an explicit allocator-handoff record instead of leaving allocator posture in prose
- the bitmap and kretprobe loader scaffolds can now emit that shared request shape while still stopping at `waiting_on_runtime_substrate`

What is still missing is actual runtime execution behavior:

- no shared loader-plan projection yet exists for `samples/zigux/runtime_atomic64.zig` or `samples/zigux/runtime_trace_events.zig`, so half of the current Phase 9 starters still stop before the shared `zigux/kernel/runtime_loader.zig` request contract
- no real runtime loader owns thread creation, task scheduling, polling, or event-loop behavior
- no shared runtime command or environment control surface records whether bring-up is selected by command name, argv policy, or environment-derived activation cues
- no path here claims module registration parity, live init invocation, or live exit teardown
- no path here claims workqueue parity, scheduler-facing runtime transport ownership, or a freeze-map status change for `kernel/workqueue.c` without an explicit Architecture Council decision

That means the current runtime surface is now a bounded shared request contract, not a real loadable runtime path.

## Roadmap-alignment note

The roadmap boundary matters here:

- `Phase 6` is still a leaf-helper phase and should not absorb runtime allocator or boot/init work
- `Phase 8` owns the first repo-level command and environment plumbing surfaces under `tools/lib/subcmd/*.zig`, so this survey records their absence from the runtime path instead of inventing a parallel control stack
- `Phase 9` is the first runtime-module phase, so this survey is recorded there even though the scheduled lane key is `P6-L01`

This slice therefore stays deliberately pre-execution. It does not claim runtime scheduling, polling, or event-loop implementation and it does not move runtime allocator or init-flow ownership into Phase 6.
It also stays underneath the freeze-map study boundary for `kernel/workqueue.c`, so the shared loader packet must keep workqueue parity and any scheduler-core status change blocked until the Architecture Council explicitly reopens that anchor with fresh evidence.

## Gates

1. run the release-discipline validator
- `python3 scripts/zigux/validate-phase9.py`

2. run the shared Phase 9 runtime survey bundle
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience targets
- `make -C zigux phase9-validate`
- `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a loadable runtime module path
- command-name, argv-policy, or environment-derived activation controls
- allocator ownership changes beyond the shared handoff contract built from `zigux/helpers/allocator_policy.zig`
- parity or ownership for `kernel/workqueue.c`
- Phase 6 runtime implementation progress

## Next bounded step

If a future runtime lane reopens this blocker, keep the next step narrow: add one shared loader-plan projection for either `samples/zigux/runtime_atomic64.zig` or `samples/zigux/runtime_trace_events.zig` so another existing runtime starter can reuse `zigux/kernel/runtime_loader.zig` without adding execution behavior, or add one explicit command or environment activation field once the separate Phase 8 tooling posture gives that control surface a real owner, while keeping `kernel/workqueue.c` in study-only status unless the Architecture Council explicitly reopens that boundary.

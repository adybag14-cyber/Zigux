# Phase 9 Runtime Loader Gap Survey

This document records the shared boot/runtime loader gap that still separates the landed `samples/zigux/runtime_*` starter surface from any future `zigux/kernel/runtime_loader.zig` consumer.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- scope: shared survey note, manifest-backed survey gate, explicit roadmap-boundary note for the mixed Phase 6 schedule wording, and a bounded shared runtime-loader request surface that keeps allocator plus init or exit handoff machine-checkable without claiming real runtime execution
- product boundary:
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `Documentation/zigux/review-checklist.md`
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
- a shared `zigux/kernel/runtime_loader.zig` request surface now exists

This survey keeps the lane honest by recording what is now landed and what is still blocked instead of pretending that runtime scheduling, polling, or event-loop work should be pulled forward into Phase 6.

The review checklist also remains part of this bounded governance surface. For this runtime-loader starter family, the checklist still needs to keep three review cues explicit:

- no hidden runtime services
- no implicit allocation posture beyond the explicit allocator-handoff contract
- no unclear panic or unsafe ownership story

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

- no real runtime loader owns thread creation, task scheduling, polling, or event-loop behavior
- no shared runtime command or environment control surface records whether bring-up is selected by command name, argv policy, or environment-derived activation cues
- no path here claims module registration parity, live init invocation, or live exit teardown

That means the current runtime surface is now a bounded shared request contract, not a real loadable runtime path.

## Roadmap-alignment note

The roadmap boundary matters here:

- `Phase 6` is still a leaf-helper phase and should not absorb runtime allocator or boot/init work
- `Phase 8` owns the first repo-level command and environment plumbing surfaces under `tools/lib/subcmd/*.zig`, so this survey records their absence from the runtime path instead of inventing a parallel control stack
- `Phase 9` is the first runtime-module phase, so this survey is recorded there even though the scheduled lane key is `P6-L01`

This slice therefore stays deliberately pre-execution. It does not claim runtime scheduling, polling, or event-loop implementation and it does not move runtime allocator or init-flow ownership into Phase 6.

## Gates

1. run the shared Phase 9 runtime survey bundle
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a loadable runtime module path
- command-name, argv-policy, or environment-derived activation controls
- allocator ownership changes beyond the shared handoff contract built from `zigux/helpers/allocator_policy.zig`
- Phase 6 runtime implementation progress

## Next bounded step

If a future runtime lane reopens this blocker, keep the next step narrow: extend the shared `zigux/kernel/runtime_loader.zig` request surface only where a new runtime starter can reuse it, or add one explicit command or environment activation field once the separate Phase 8 tooling posture gives that control surface a real owner.

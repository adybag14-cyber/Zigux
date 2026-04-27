# Phase 9 Runtime Loader Gap Survey

This document records the shared boot/runtime loader gap that still separates the landed `samples/zigux/runtime_*` starter surface from any future `zigux/kernel/runtime_loader.zig` consumer.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- scope: shared survey note, manifest-backed survey gate, explicit roadmap-boundary note for the mixed Phase 6 schedule wording, and blocker language for allocator plus init or exit handoff work that still lacks a runtime-loader consumer
- product boundary:
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `zigux/tests/runtime_loader_gap_manifest.json`
  - `zigux/tests/runtime_loader_gap_survey.zig`
  - `zigux/tests/phase9_build.zig`
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
- there is still no `zigux/kernel/runtime_loader.zig`

This survey keeps the lane honest by recording the real blocker instead of pretending that allocator or init-flow work should be pulled forward into Phase 6.

## Current blocker posture

The current runtime pilot surface already exposes reviewable loader inputs:

- `samples/zigux/runtime_bitmap_loader.zig` records explicit entry and exit symbol names, `requires_runtime_substrate`, `provides_selftest_hook`, and a bounded handoff stage
- `samples/zigux/runtime_kretprobe_loader.zig` records the same loader-shape inputs for the kretprobe starter
- `zigux/helpers/allocator_policy.zig` already records the explicit caller-vs-fallback allocator posture that a future runtime loader must consume rather than bypass

What is still missing is the shared consumer:

- no `zigux/kernel/runtime_loader.zig` exists to accept those loader plans
- no shared runtime allocator handoff binds the existing allocator policy to module bring-up or failure cleanup
- no shared init or exit flow consumes the staged entry and exit symbol names from the sample-side loader plans
- no shared runtime command or environment control surface records whether bring-up is selected by command name, argv policy, or environment-derived activation cues

That means the current runtime surface is still a set of bounded survey and starter inputs, not a real loadable runtime path.

## Roadmap-alignment note

The roadmap boundary matters here:

- `Phase 6` is still a leaf-helper phase and should not absorb runtime allocator or boot/init work
- `Phase 8` owns the first repo-level command and environment plumbing surfaces under `tools/lib/subcmd/*.zig`, so this survey records their absence from the runtime path instead of inventing a parallel control stack
- `Phase 9` is the first runtime-module phase, so this survey is recorded there even though the scheduled lane key is `P6-L01`

This slice therefore stays survey-only. It does not claim a runtime implementation and it does not move runtime allocator or init-flow code into Phase 6.

## Gates

1. run the shared Phase 9 runtime survey bundle
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This slice does not yet claim:

- a new `zigux/kernel/runtime_loader.zig` implementation
- a loadable runtime module path
- allocator ownership changes beyond the existing `zigux/helpers/allocator_policy.zig` policy surface
- Phase 6 runtime implementation progress

## Next bounded step

If a future runtime lane reopens this blocker, keep the next step narrow: define the smallest manifest-backed `zigux/kernel/runtime_loader.zig` contract that consumes the already-landed loader-plan inputs, states the allocator handoff explicitly, records init or exit sequencing, and says whether command or environment activation is intentionally absent or passed through from the separate Phase 8 tooling posture.

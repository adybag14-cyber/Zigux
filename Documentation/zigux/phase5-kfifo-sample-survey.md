# Phase 5 Kfifo Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kfifo-reference-sample-survey`
- scope: roadmap-vs-repo survey, approved reference-sample idiom guidance, and the smallest documentation updates needed so future `samples/zigux/` work does not confuse Phase 5 sample ports with later runtime-module lanes
- product boundary:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the four Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection shows that `samples/zigux/` already carries runtime-oriented starters for:

- `runtime_atomic64.zig`
- `runtime_bitmap.zig`
- `runtime_kretprobe.zig`
- `runtime_trace_events.zig`

That is useful later-phase work, but it does not yet explain the earlier Phase 5 reference-sample style or what a kfifo-shaped Zigux sample is allowed to claim before runtime substrate exists.

## Survey findings

- `samples/kfifo/bytestream-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - bounded in-memory FIFO behavior such as `kfifo_in`, `kfifo_out`, `kfifo_put`, `kfifo_get`, `kfifo_skip`, and `kfifo_peek`
  - lifecycle setup and teardown around `example_init()` and `example_exit()`
  - procfs and user-copy plumbing through `proc_create`, `kfifo_from_user`, `kfifo_to_user`, and mutex-protected read or write paths
- the live Zigux repo does not yet ship any Phase 5 side-by-side sample under `samples/zigux/` for `kfifo`, `kobject`, or the non-runtime reading of `kretprobe_example.c`.
- the generic review checklist already covers scope, safety, validation, ABI, and product discipline, but it does not yet say how a reference sample should distinguish "reviewable idiom" from "runtime-ready module."

## Approved idiom for a future kfifo-style sample

Until a bounded runtime substrate exists, a Phase 5 `samples/zigux/` reference sample for this anchor should:

- model FIFO state and ordered operations entirely in memory
- keep the Linux anchor path explicit in a descriptor or note
- include a tiny self-check or fixture-backed replay for the queue-order expectations that make the sample useful to reviewers
- show ownership and lifetime boundaries clearly, especially initialization, reset, and teardown
- keep procfs, user-copy, blocking lock behavior, and module-registration claims out of scope unless a later lane lands the required substrate first

In practice, that means the approved first idiom is a side-by-side behavior sample, not a claim that Zigux already has `proc_create()`, `kfifo_from_user()`, or module-load parity.

## Recorded gap vs roadmap

The current gap is not "Zigux lacks every sample." The more precise gap is:

- the repo has later runtime-oriented starters in `samples/zigux/`
- the roadmap still expects a Phase 5 reference-sample layer
- there is no reviewable note that tells contributors how the `kfifo` anchor should be translated into an approved Zigux sample idiom without over-claiming runtime support

This survey closes that documentation gap so the next bounded Phase 5 step can be a real sample or guide update instead of another round of ambiguous sample naming.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example
- `rg -n "samples/kfifo/bytestream-example.c|Phase 5" Documentation/zigux samples /workspace/agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP\ \(1\).md`

2. confirm the current `samples/zigux/` surface stays distinct from this reference-sample lane
- `find samples/zigux -maxdepth 1 -type f | sort`

## Non-goals

This survey does not yet claim:

- a landed `samples/zigux/bytestream_fifo.zig` reference port
- procfs parity
- `kfifo_from_user()` or `kfifo_to_user()` parity
- loadable-module wiring or runtime registration support

## Next bounded step

Stay in the Phase 5 samples-and-reference-patterns lane and add one small honest kfifo-shaped sample artifact next, most likely a side-by-side `samples/zigux/bytestream_fifo.zig` starter plus a focused review note or fixture-backed self-check that proves queue-order behavior without claiming procfs or user-copy substrate.

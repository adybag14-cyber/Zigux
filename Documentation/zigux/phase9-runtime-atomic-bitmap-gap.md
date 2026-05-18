# Phase 9 Runtime Atomic And Bitmap Gap Survey

This note records the current Phase 9 state for the runtime atomic and bitmap pilots on `master`.

The key survey result for `P9-L01` is no longer "bitmap is missing." The sharper repo-first read is this:

- the direct shared reminder packet still skews trace-events-first
- the public current tree shows that both atomic64 and bitmap runtime pilot families have returned sample, loader, and shared build coverage
- the remaining roadmap gap is now the shared live runtime-loader binding, not an atomic-versus-bitmap parity mismatch

## Roadmap target

Phase 9 is still the runtime-pilot tranche.

- primary Linux anchors:
  - `lib/atomic64_test.c`
  - `lib/test_bitmap.c`
  - `samples/trace_events/trace-events-sample.c`
  - `samples/kprobes/kretprobe_example.c`
- required Zigux features:
  - first loadable Zigux runtime modules
  - selftest hooks
  - runtime module lifecycle parity
- recommended Zigux destinations:
  - `zigux/tests/runtime_*`
  - `samples/zigux/runtime_*`

For this lane, the roadmap question is whether the atomic64 and bitmap pilots still differ materially on first-loadable runtime-module parity.

## Current repo reality on `master`

The directly readable shared reminder packet is still narrow and review-first.

Shared reminder surfaces that are directly readable through the authenticated contents route:
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`

Those shared reminder surfaces still emphasize the surviving trace-events packet, and they are more conservative than the full public current tree.

A fresh public-tree reread of current `master` shows the broader runtime atomic and bitmap packet is present again:
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/kernel/runtime_loader.zig`

The shared Phase 9 build surface wires both families directly:
- `phase9-runtime-atomic64-loader-tests`
- `phase9-runtime-bitmap-loader-tests`
- `phase9-runtime-bitmap-top-bit-contract-tests`
- shared runtime-loader contract tests

That means the cross-family parity picture is stronger than the reminder packet alone suggests.

## Atomic and bitmap parity state

The atomic64 side is directly present on current `master` through:
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- the shared `zigux/tests/phase9_build.zig` route

The bitmap side is directly present on current `master` through:
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- the shared `zigux/tests/phase9_build.zig` route

The loader pair now exposes the same first-loadable family shape that this lane previously treated as missing: both families project a loader plan into the shared runtime-loader contract through `toSharedLoadPlan(...)` and `runtime_loader.prepareRequest(...)`.

So the honest current claim is:
- the atomic64-versus-bitmap parity gap is largely closed on the public current tree
- both families now have sample-root and loader-side proof surfaces
- the remaining blocker is shared and sits below both families equally

## Remaining roadmap gap

The remaining roadmap gap is the shared live runtime-loader binding that would consume the prepared request and complete full runtime-module lifecycle parity in a true runtime environment.

That blocker is shared across both families:
- it is not specific to atomic64 anymore
- it is not specific to bitmap anymore
- it should be treated as shared runtime-loader work rather than another `P9-L01` family-parity repair

A smaller docs-truthfulness gap also remains:
- the authenticated reminder packet still understates the broader public-tree runtime atomic and bitmap packet
- future reminder maintenance should reconcile that split carefully instead of regressing back to the older missing-bitmap story

## Recommended next bounded step

For `P9-L01`, the honest next move is now conservative:
1. leave family-parity claims parked unless a fresh reread finds new atomic-versus-bitmap drift
2. hand shared live-loader completion back to the shared runtime-loader lane rather than reopening family-local survey churn here
3. if same-lane documentation work reopens, keep it to one reminder-surface truthfulness repair that aligns the shared note packet with the current public-tree runtime atomic and bitmap evidence

## Anti-overlap rule

This lane should not use the current survey state as an excuse to reopen:
- Phase 2 bridge surfaces
- Phase 3 export-boundary surfaces
- Phase 4 broader validator or perf-promotion work
- Phase 5 non-runtime sample bookkeeping
- deep runtime-loader substrate claims across `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`

Until a fresh reread proves otherwise, treat Phase 9 atomic and bitmap parity as substantially aligned and treat the remaining blocker as shared runtime-loader follow-through.
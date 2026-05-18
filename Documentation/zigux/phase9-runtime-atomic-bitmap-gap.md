# Phase 9 Runtime Atomic And Bitmap Gap Survey

This note records the current Phase 9 gap between the roadmap target for runtime atomic and bitmap pilots and the repo surfaces that are directly readable on current `master`.

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

For this lane, the important detail is narrower: Phase 9 should eventually expose runtime atomic and runtime bitmap pilots as real runtime-module evidence, not just as older backlog names or helper-local reminders.

## Current repo reality on `master`

Current `master` keeps the shared Phase 9 reminder family narrow and trace-events-first.

Directly readable shared Phase 9 reminder surfaces:
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`

Directly readable runtime-module sample proof on current `master`:
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

That surviving runtime sample packet already proves one real Phase 9 foothold:
- `.provides_selftest_hook = true`
- initialized, selftest_complete, and exited lifecycle tracking
- fail-closed runtime registration edges through the unregistered and re-entry gate companions

The atomic side is stronger than the bitmap side, but it is still not at first-loadable-module parity.

Directly readable atomic-side runtime evidence on current `master`:
- `zigux/tests/atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`
- `Documentation/zigux/phase4-validation-matrix.md`

That packet proves bounded runtime-style atomic64 replay coverage and phase-tracked survey evidence, but it is still tests-root differential coverage. It is not yet a directly readable `samples/zigux/runtime_atomic64*.zig` sample-root module family, and it is not yet backed by a current shared Phase 9 build or loader surface.

The bitmap side is still further behind on directly readable runtime-pilot evidence.

Current `master` does not directly expose these runtime bitmap and shared loader/build surfaces:
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_manifest.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`
- shared `zigux/tests/runtime_*` replay packet
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- dedicated `make -C zigux phase9*` route family
- dedicated shared `validate-phase9.py`

## Gap summary

Current repo reality is asymmetric:

- trace-events has a directly readable runtime-module sample family with selftest-hook and lifecycle evidence
- atomic64 has directly readable runtime differential-gate coverage and survey evidence, but not a directly readable sample-root runtime module family
- bitmap still does not have directly readable runtime sample, tests-root module, or shared build/loader evidence on current `master`

That means Phase 9 is not blocked by total absence. It is blocked by parity imbalance.

The next honest claim is not "Phase 9 runtime modules are present for atomic and bitmap." The honest claim is narrower:
- one direct runtime sample family survives today
- atomic64 has partial runtime parity support through tests-root differential replay
- bitmap remains a roadmap-backed runtime backlog target rather than direct current-`master` proof

## Recommended next bounded step

Stay inside the Phase 9 runtime-pilot lane and close the smallest parity imbalance first.

Recommended order:
1. restore one directly readable runtime bitmap packet before widening loader or kernel-substrate claims
2. keep that packet bounded to sample-root plus tests-root proof, not `kernel/workqueue.c`, ring-buffer, or broader runtime-loader ownership
3. once one bitmap packet is directly readable again, decide whether atomic64 should gain a matching sample-root runtime module or remain explicitly scoped to differential-gate support under the shared Phase 9 reminder surfaces

The smallest high-value follow-up from this note is:
- rematerialize one bounded runtime bitmap proof surface that current shared reminders can point at directly on `master`

## Anti-overlap rule

This lane should not use the atomic/bitmap gap as an excuse to reopen:
- Phase 2 bridge surfaces
- Phase 3 export-boundary surfaces
- Phase 4 broader validator or perf-promotion work
- Phase 5 non-runtime sample bookkeeping
- runtime-loader substrate claims across `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`

Until a fresh repo reread proves otherwise, keep Phase 9 atomic/bitmap wording tied to the narrow facts above.

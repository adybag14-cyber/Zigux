# Phase 9 Runtime Atomic And Bitmap Gap Survey

This note records the current `P9-L01` state for the Phase 9 runtime atomic and bitmap pilots on `master`.

The repo-first result is narrower than the roadmap and stronger than the oldest reminder wording:

- the atomic64 and bitmap pilot families both already have sample-root proof
- both families already have loader-facing proof
- the shared Phase 9 build already wires those families into bounded replay routes
- the remaining gap is not family-local parity drift; it is the shared live runtime-loader follow-through needed for true loadable runtime-module parity

## Roadmap target

Phase 9 is the runtime-pilot tranche.

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

For `P9-L01`, the key roadmap question is whether the runtime atomic64 and runtime bitmap pilots still differ materially on first-loadable runtime-module parity.

## Current repo reality on `master`

Fresh authenticated rereads show that both runtime pilot families are already present in the live tree.

Atomic64 surfaces directly present on current `master`:
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_module.zig`

Bitmap surfaces directly present on current `master`:
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `samples/zigux/runtime_bitmap_direct_init_contract.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_survey.zig`

Shared Phase 9 build and loader surfaces directly present on current `master`:
- `zigux/tests/phase9_build.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_first_loadable_parity_behavior.zig`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

The shared Phase 9 build currently exposes bounded replay routes for both families, including:
- `phase9-runtime-atomic64-sample-tests`
- `phase9-runtime-atomic64-loader-tests`
- `phase9-runtime-atomic64-diff-tests`
- `phase9-runtime-atomic64-module-tests`
- `phase9-runtime-bitmap-sample-tests`
- `phase9-runtime-bitmap-loader-tests`
- `phase9-runtime-bitmap-diff-tests`
- `phase9-runtime-bitmap-module-tests`
- `phase9-runtime-bitmap-top-bit-tests`
- `phase9-first-loadable-runtime-module-parity-behavior-tests`

That means the live tree no longer supports the older story that bitmap parity is simply missing.

## Parity state

The atomic64 and bitmap families now match on the core Phase 9 starter claims that matter for this lane:

- both advertise `.requires_runtime_substrate = true`
- both advertise `.provides_selftest_hook = true`
- both expose explicit lifecycle stages from cold through exit
- both ship sample-local loader witnesses
- both are wired into the shared Phase 9 build packet

The shared cross-family replay in `zigux/tests/runtime_first_loadable_parity_behavior.zig` strengthens that read further. Current `master` already has one bounded place where first-loadable runtime-module behavior is checked across pilot families instead of only inside each family separately.

So the honest `P9-L01` claim is now:

- atomic64-versus-bitmap starter parity is substantially present on current `master`
- the live gap is below both families equally
- the next missing step is shared runtime-loader completion rather than another family-local parity repair

## Remaining roadmap gap

The remaining roadmap gap is the shared live runtime-loader follow-through that would turn the prepared Phase 9 plans into true loadable runtime-module execution parity.

`zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig` already keep the bounded contract reviewable:

- approved pilot-family metadata is explicit
- handoff-stage expectations are explicit
- selftest-hook evidence is explicit
- prepared-request drift is rejected before handoff

What those files do not yet prove is a live runtime substrate that actually consumes the prepared request and completes the load/unload path in a real runtime environment.

That blocker is shared:

- it is not atomic64-specific
- it is not bitmap-specific
- it should be treated as shared Phase 9 runtime-loader work, not reopened as `P9-L01` family churn

## Recommended next bounded step

The best next step after this note is outside `P9-L01`:

1. keep atomic64/bitmap parity parked unless a fresh reread finds new family-local drift
2. hand live loader completion back to the shared runtime-loader lane
3. if Phase 9 reminder wording drifts again, keep the repair to one reminder surface at a time instead of reopening runtime behavior here

## Anti-overlap rule

This lane should not use the current survey result as a reason to reopen:

- Phase 2 bridge surfaces
- Phase 3 export-boundary surfaces
- trace-events or kretprobe family-local work
- deeper runtime-substrate claims under study-only or shared-owner areas

Treat `P9-L01` as a repo-truthfulness lane for runtime atomic and bitmap parity, not as the owner of shared runtime-loader closure.

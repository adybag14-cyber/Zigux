# Phase 9 Runtime Loader Gap Survey

## Status

- `PHASE9_STATUS=shared-reminder-follow-through-open`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- `PHASE9_LANE_KEY=P9-L18`

## Current Repo Reality

Current `master` ships the shared loader-facing packet directly:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/phase9_build.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

The current honest shared replay routes are literal on `master`:

1. `make -C zigux phase9-runtime-loader-shared-tests`
2. `make -C zigux phase9-test`
3. `make -C zigux phase9`

There is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`,
or `phase9-validate` route on current `master`.

## What Is Reviewable Now

- the shared request lifecycle remains explicit through `prepared`,
  `waiting_on_runtime_substrate`, and `released_without_substrate`
- `zigux/tests/runtime_loader_allocator_init_flow.zig` keeps the shared allocator
  and init-flow proof bundle explicit for the four shipped pilot families
- `samples/zigux/runtime_trace_events_loader.zig` keeps
  `registrationSnapshot`, `prepareSharedRequest`,
  `requestSharedRuntimeLoad`, and `releaseSharedWithoutSubstrate`
  reviewable as metadata-only loader handoff evidence

## Boundaries

The shared loader packet is still a review-only handoff surface, not a shipped
publication surface.

- `.modinfo`
- `MODULE_ALIAS()`
- `modules.alias`
- `modules.order`
- `modules.builtin`
- module install-root state
- `depmod` script or manifest state

Those publication surfaces remain blocked boundaries rather than landed Phase 9
runtime-module delivery evidence.

Keep the older Phase 8 command and environment cue owners out of this packet:

- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`

Keep the earlier-phase config-surface and symbol-export owners out of this
packet too:

- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `rust/exports.c`
- `zigux/kernel/export_shim.zig`

Those surfaces remain Phase 2 config-surface bridge references and Phase 3
symbol-export boundary references rather than Phase 9 runtime evidence.

## Next Bounded Step

Fresh repo-first inspection now shows `Documentation/zigux/README.md` and
`zigux/tests/README.md` already defer the exact shared owner map back to
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` and keep the
blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`,
`modules.builtin`, module install-root state, and `depmod` script or manifest
state boundary explicit, but `scripts/zigux/README.md` still undercounts the
live shared loader packet by omitting
`Documentation/zigux/phase9-runtime-loader-gap-survey.md`,
`zigux/tests/runtime_loader_gap_manifest.json`, and
`zigux/tests/runtime_loader_gap_survey.zig` from its Phase 9 summary.

Repair `scripts/zigux/README.md` first, then tighten
`scripts/zigux/check-phase9-build-only-surface.py` so the scripts-root
summary fails closed on that loader-gap survey trio before reopening any
broader shared reminder pass.

Keep future follow-through inside the smallest regressed shared surface instead
of reopening pilot-family behavior, loader implementation, or new checker
growth.

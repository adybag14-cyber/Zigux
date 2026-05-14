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

## Current Shared Reminder State

Fresh repo-first inspection now shows `Documentation/zigux/README.md` and
`scripts/zigux/README.md` both keep
`Documentation/zigux/phase9-runtime-loader-gap-survey.md`,
`zigux/tests/runtime_loader_gap_manifest.json`, and
`zigux/tests/runtime_loader_gap_survey.zig` explicit beside
`zigux/tests/runtime_loader_allocator_init_flow.zig`,
`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`,
the shared `zigux/tests/phase9_build.zig` replay, and the focused
`make -C zigux phase9-runtime-loader-shared-tests` route, while still deferring
the exact shared owner map and blocked publication boundary back to
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`.

Fresh repo-first inspection now also shows `zigux/tests/README.md` keeps that
same shared Phase 9 loader-gap packet explicit through a dedicated Phase 9 flow
section that names `Documentation/zigux/phase9-runtime-loader-gap-survey.md`,
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`,
`scripts/zigux/check-phase9-build-only-surface.py`,
`zigux/tests/runtime_loader_gap_manifest.json`,
`zigux/tests/runtime_loader_gap_survey.zig`,
`zigux/tests/runtime_loader_allocator_init_flow.zig`,
`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`,
and the focused `make -C zigux phase9-runtime-loader-shared-tests`,
`make -C zigux phase9-test`, and `make -C zigux phase9` replay routes instead
of leaving that packet blurred into the tail of the Phase 8 flow.

That means the earlier docs-root undercount and the later tests-root undercount
are both cleared on current `master`; the remaining same-lane follow-through is
now future reminder drift around the blocked module-metadata and
depmod-publication boundary rather than shared packet inventory sync.

## Historical Reminder Wording

The last narrower shared reminder pass recorded the older docs-root drift like
this before the docs-root summary caught up:

Fresh repo-first inspection now shows `scripts/zigux/README.md` and
`zigux/tests/README.md` already keep
`Documentation/zigux/phase9-runtime-loader-gap-survey.md`,
`zigux/tests/runtime_loader_gap_manifest.json`, and
`zigux/tests/runtime_loader_gap_survey.zig` explicit inside the shared loader
packet while still deferring the exact shared owner map back to
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, but
`Documentation/zigux/README.md` still undercounts that same live packet by
omitting the loader-gap survey note plus the manifest-backed survey trio from
its Phase 9 summary.

Repair `Documentation/zigux/README.md` first, then re-read
`Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and
`zigux/tests/README.md` before reopening any broader shared reminder pass.

The tests-root follow-through that just closed read like this before
`zigux/tests/README.md` caught up:

Fresh repo-first inspection also shows `zigux/tests/README.md` still keeps the
shared Phase 9 build and survey files visible, but its key entrypoint list
still blurs that packet into the tail of the Phase 8 flow and does not yet call
out `Documentation/zigux/phase9-runtime-loader-gap-survey.md` or
`zigux/tests/runtime_loader_gap_manifest.json` beside the shared loader-facing
packet.

Keep that historical wording visible until the dedicated
`zigux/tests/runtime_loader_gap_survey.zig` guard is refreshed too, so future
runs can still see exactly which packet-local drift the previous follow-through
closed.

## Next Bounded Step

Leave this note parked unless `Documentation/zigux/README.md`,
`scripts/zigux/README.md`, `zigux/tests/README.md`, or
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` drifts again
around the shared loader-gap packet or the blocked module-metadata and
depmod-publication boundary.

When that happens, start with the smallest shared reminder surface that
regresses, keep the exact owner map and blocked publication boundary deferred
back to `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, and keep
future follow-through inside shared reminder truthfulness instead of reopening
pilot-family behavior, loader implementation, or new checker growth.
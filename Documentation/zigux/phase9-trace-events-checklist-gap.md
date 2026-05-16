# Phase 9 Trace-Events Checklist Gap

## Status

- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP=present`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_KIND=review_checklist_runtime_loader_overclaim`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_SCOPE=surviving_trace_events_packet_only`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_STATUS_BUCKET=runtime_pilot_review_only`
- `PHASE9_TRACE_EVENTS_CHECKLIST_GAP_OWNER=Runtime Pilot Lane`
- verified against current `master` head `65a2d4977479c1b4ea87614bfd7683addfefe02f`

## Why this gap note exists

The Phase 9 roadmap still targets runtime pilot modules, selftest hooks, and
runtime lifecycle parity through tests and samples. On current `master`, that
goal is now carried by one surviving direct sample plus reminder surfaces rather
than the older shared runtime-loader packet.

Current repo evidence already narrows the live packet:

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` says current
  `master` keeps a narrow Phase 9 runtime-pilot packet and names
  `samples/zigux/runtime_trace_events.zig` as the surviving direct
  runtime-module sample.
- `zigux/tests/README.md` keeps that same sample explicit through
  `.provides_selftest_hook = true` together with initialized,
  selftest_complete, and exited lifecycle tracking while also warning that
  there is no shared `zigux/tests/runtime_*` replay packet,
  `zigux/tests/phase9_build.zig`, `make -C zigux phase9*` route family, or
  dedicated shared `validate-phase9.py` visible on current `master`.
- `samples/zigux/runtime_trace_events.zig` still carries the direct
  selftest-hook and lifecycle parity evidence through `runSelftest()`, `exit()`,
  and the focused lifecycle regression tests.

## Current bounded gap

`Documentation/zigux/review-checklist.md` still overclaims the removed shared
runtime-loader family. It keeps the older shared-loader wording plus the
removed `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, and
`samples/zigux/runtime_*_loader.zig` scaffolds framed as current shared packet
evidence even though the direct current-`master` packet has narrowed to the
surviving trace-events sample and reminder surfaces.

That leaves a review-surface truthfulness gap: the lane-sequencing note, the
tests guide, and the sample are already honest about the narrowed packet, but
the shared checklist still describes the older wider inventory.

## Next bounded fix

Refresh `Documentation/zigux/review-checklist.md` and
`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` so they:

- switch from shared runtime-loader packet wording to the surviving
  trace-events runtime packet
- keep `samples/zigux/runtime_trace_events.zig`,
  `.provides_selftest_hook = true`, and initialized, selftest_complete, and
  exited lifecycle tracking explicit
- keep `zigux/tests/phase9_build.zig`, shared `zigux/tests/runtime_*` replays,
  `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`,
  `zigux/Makefile`, and the older `samples/zigux/runtime_*_loader.zig`
  scaffolds recorded only as absent backlog references until a fresh reread
  proves they have returned
- keep `scripts/zigux/kconfig/conf_bridge.zig`,
  `scripts/zigux/kconfig/confdata_bridge.zig`, `rust/exports.c`, and
  `zigux/kernel/export_shim.zig` explicit as cross-phase boundary references
  rather than runtime-pilot evidence
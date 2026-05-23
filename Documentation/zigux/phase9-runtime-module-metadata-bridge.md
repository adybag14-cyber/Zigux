# Phase 9 Runtime Module Metadata Bridge

This note records a bounded Phase 9 improvement: current `master` now has a dedicated sidecar contract for runtime module metadata and depmod publication planning through `zigux/kernel/runtime_module_metadata_bridge.zig` and `zigux/tests/runtime_module_metadata_bridge.zig`.

## Roadmap anchor

Phase 9 is still the runtime pilot tranche.

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

## What landed

The new sidecar helper does not widen the shared runtime-loader contract. Instead, it gives the repo a focused place to describe:

- approved Phase 9 pilot-family identities
- module metadata fields that belong beside runtime pilot modules
- staged install-root and depmod output paths
- explicit blocked-publication state without pretending depmod execution or install-root delivery already landed

The accompanying tests keep two current runtime pilot families explicit:

- `runtime_trace_events`
- `runtime_bitmap`

## Why this is bounded progress

Before this change, Phase 9 notes could only describe `.modinfo`, alias, install-root, and depmod-publication work as blocked vocabulary. The new helper turns that into a typed sidecar surface with direct tests, while keeping the repo honest about what still is not complete.

This helper is not proof that:

- runtime module publication is complete
- depmod scripts or manifests are shipped
- install-root wiring exists on `master`
- the shared runtime-loader packet now owns publication behavior

It is proof that the metadata and depmod planning boundary is now represented in code and can be checked directly without overloading the loader contract.

## Recommended next step

Wire the new sidecar bridge packet into the existing Phase 9 build shard or sample-root runtime helpers one surface at a time, keeping publication state staged until a later lane lands real install-root or depmod execution support.
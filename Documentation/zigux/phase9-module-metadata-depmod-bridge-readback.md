# Phase 9 Module Metadata and Depmod Bridge Readback

## Status

- `PHASE9_STATUS=shared-owner-readback-recorded`
- `PHASE9_SLICE=module-metadata-depmod-bridge-readback`
- `PHASE9_LANE_KEY=P9-L07`

## Roadmap Boundary

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

That roadmap boundary still does not justify treating module publication metadata or depmod output as shipped runtime evidence unless current `master` exposes a shared owner surface for it.

## Current Repo Reality

Trusted rereads on 2026-05-20 show that the older dedicated module-metadata packet is still gone on current `master`.

- there is no surviving dedicated `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/runtime_module_metadata_manifest.json`, `zigux/tests/runtime_module_metadata_survey.zig`, or `scripts\zigux/check_phase9_module_metadata_packet.zig` packet on the trusted current-master path
- the live direct runtime proof remains the narrow trace-events packet through `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig`
- the live shared loader packet remains review-first shared-owner evidence through `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds
- `zigux/tests/phase9_build.zig` currently proves only the bounded `phase9-runtime-atomic64-diff`, `phase9-runtime-bitmap-tests`, `phase9-runtime-bitmap-top-bit-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests` shard; it is not direct proof that publication metadata, install-root, or depmod bridge work returned

## Module Metadata And Depmod Boundary

Current shared-owner surfaces still keep module metadata and depmod publication in the blocked-boundary bucket rather than in the shipped runtime-pilot packet.

- blocked module-publication vocabulary still includes `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, `Module.symvers`, module install-root state, and `depmod` script, manifest, or alias publication state
- `zigux/kernel/runtime_loader_contract.zig` may expose review-only contract fields such as `registration_snapshot`, `module_symvers_path`, and `depmod_aliases`, but those remain review evidence for a blocked boundary rather than proof that a publication bridge landed
- the current truthful owner map is therefore narrower than the older dedicated lane packet: Phase 9 currently proves runtime reviewability, selftest hooks, and lifecycle parity in the trace-events family plus review-first allocator/init-flow loader evidence, but not publication metadata completion

## Gap Judgment Versus The Roadmap

Compared with the Phase 9 roadmap, current `master` is still honest but incomplete in this lane family.

- the roadmap-backed runtime pilot evidence is present through trace-events sample-local reviewability and the shared loader allocator/init-flow packet
- the remaining same-family gap is not missing lifecycle proof; it is the still-blocked publication boundary around module metadata, install-root state, and depmod output
- because no dedicated current-owner packet exists for that blocked boundary, the safe same-lane work is readback and reminder hygiene only

## Non-Overlap Rule

This lane should stay bounded to repo-reality readback and reminder truthfulness for the blocked module-metadata and depmod boundary.

- do not reopen trace-events runtime behavior already owned by the direct Phase 9 packet
- do not reopen shared loader lifecycle-guard work already owned by adjacent shared lanes
- do not promote `zigux/tests/phase9_build.zig` into proof that publication metadata or depmod bridge work is complete

## Next Bounded Step

If Phase 9 shared reminder surfaces drift again, reread `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` together first, then repair only the smallest stale reminder surface that misstates the blocked module-metadata and depmod-publication boundary.

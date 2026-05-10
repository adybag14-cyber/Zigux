# Phase 3 Substrate Lane Sequencing

This note turns the current `master` evidence for the bounded Phase 3 ABI substrate into one explicit anti-overlap map for scheduled substrate lanes.

It is a coordination artifact, not a closure claim.

## Current posture

- `PHASE3_STATUS=active`
- `PHASE3_SEQUENCE=substrate-lane-anti-overlap`
- shared validator-first entrypoint: `python3 scripts/zigux/validate-phase3.py`
- bounded shared replay entrypoint: `python3 scripts/zigux/validate-phase3.py --slug abi`
- shared interop route: `python3 scripts/zigux/run-phase3-checks.py --slug abi`
- shared build replay entrypoints: `zig build phase3-test --build-file zigux/tests/build.zig` and `zig build phase3-dump --build-file zigux/tests/build.zig`
- Linux-style replay routes: `make -C zigux phase3-validate`, `make -C zigux phase3-abi`, and `make -C zigux phase3`

The current bounded Phase 3 decision is no longer whether the substrate still needs generic starter scaffolding. Live `master` already carries a real shared ABI packet plus dedicated export/UAPI, policy/unsafe, and low-level wrapper review surfaces. The coordination risk now is packet overlap: nearby runs can still reopen the same helper, survey, or validator surface from different directions unless the owner split stays explicit.

## Why this note exists

The Phase 3 roadmap still wants one permanent C and Zigux boundary through:

- explicit export shims
- curated bindings
- layout assertions
- explicit panic and allocator policy
- approved atomic, barrier, and MMIO wrappers
- a narrow unsafe surface

Live `master` now proves those requirements through one shared ABI packet and three directly coupled boundary packets:

- the shared ABI and bindings packet rooted in `Documentation/zigux/phase3-abi-slice.md`
- the export/UAPI starter packet rooted in `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- the policy and unsafe packet rooted in `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- the low-level wrapper packet rooted in `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`

That split is real progress, but it also means helper-local and survey-local follow-through must stay inside the right packet instead of flattening back into one broad Phase 3 cleanup lane.

## Lane map

### 1. Shared ABI and bindings lane

Use this lane only for shared ABI route, binding, manifest, dump, catalog, or generated-wrapper drift that affects the whole substrate packet.

Own:

- `Documentation/zigux/phase3-abi-slice.md`
- `include/zigux/abi.h`
- `include/zigux/dev_t.h`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase3_abi_dump.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
- `scripts/zigux/survey-phase3-abi-constant-parity.py`
- `scripts/zigux/check-phase3-abi-dump-gate.py`
- `scripts/zigux/check-phase3-catalog-selftest.py`
- `scripts/zigux/check-phase3-readme-tooling-inventory.py`
- `scripts/zigux/check-phase3-selftest-surface.py`
- `scripts/zigux/phase3_catalog.py`
- `scripts/zigux/phase3_check_lib.py`
- `scripts/zigux/generate-phase3-check-wrappers.py`
- `scripts/zigux/run-phase3-checks.py`
- the generated legacy wrapper alias `scripts/zigux/check-phase3-abi.py`

Do not use this lane for packet-local export/UAPI wording, policy-byte wording, or focused low-level replay changes unless the shared route itself moved.

### 2. Export and UAPI starter lane

Use this lane for starter boundary growth or truthfulness work tied to the export shim, starter UAPI helpers, direct behavior replay, focused layout replay, packet-local validator, or dedicated Linux-header governance note.

Own:

- `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
- `Documentation/zigux/phase3-linux-zigux-header-governance.md`
- `zigux/kernel/export_shim.zig`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/tests/phase3_export_uapi.zig`
- `zigux/tests/phase3_export_uapi_build.zig`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `zigux/tests/phase3_export_uapi_layout_build.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- the starter-boundary claims around `include/linux/zigux.h`

Keep this lane narrow.

- this lane owns both the direct `phase3_export_uapi.zig` behavior replay and the focused `phase3_export_uapi_layout.zig` replay, plus their paired build wrappers
- the shared ABI slice still owns the broader `include/linux/zigux.h` aggregation rule
- this lane owns only the starter export/UAPI subset it directly proves, including the current `version.zig` and `dev_t.zig` starter helpers
- if a new top-level boundary family lands, refresh this packet and the shared ABI packet together instead of treating header growth alone as closure

### 3. Policy and unsafe lane

Use this lane only for policy wording, shared policy-byte reviewability, or narrow unsafe survey drift.

Own:

- `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
- `scripts/zigux/validate-phase3-policy-unsafe-survey.py`
- `scripts/zigux/check-phase3-policy-byte-guards.py`
- `zigux/helpers/allocator_policy.zig` when the change is about explicit caller-policy, fallback-policy, or one-byte policy reviewability
- `zigux/helpers/mmio.zig` only when the change is about the helper's explicit interop-policy byte or typed-policy wording as reviewed by the shared policy-byte guard
- `zigux/unsafe/narrow.zig` only when the change is about explicit unsafe-scope policy decoding or survey-local policy wording

Do not use this lane for direct MMIO width, range, atomic, barrier, or focused low-level replay growth. Those belong to the low-level wrapper packet.

### 4. Low-level wrapper lane

Use this lane for helper-local low-level surface movement and the focused replay that proves it.

Own:

- `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
- `zigux/helpers/atomic.zig`
- `zigux/helpers/barrier.zig`
- `zigux/helpers/mmio.zig` when the change is about direct read or write surface, width coverage, range descriptors, ordering behavior, or focused replay truthfulness
- `zigux/unsafe/narrow.zig` when the change is about the raw pointer bridge that exists to support the low-level replay
- `zigux/tests/phase3_low_level_wrappers.zig`
- `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`

This lane owns the helper-surface and focused-replay view of MMIO and narrow unsafe. If the work is only shared policy wording or policy-byte checker coverage, keep it in the policy and unsafe lane instead.

## Shared summary follow-through

When a shared Phase 3 reminder surface drifts, point it back to this owner map instead of trying to restate every packet boundary from scratch.

Shared reminder surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Keep those follow-through edits bounded to one shared summary at a time. If a wording fix requires helper or validator behavior changes, split the behavior change back into the owning lane above.

## Current anti-overlap correction

Today the strongest Phase 3 sequencing correction is to keep the current substrate split explicit:

- shared ABI and bindings work stays with the shared route, manifest, catalog, and generated-wrapper packet
- export/UAPI work stays with the starter boundary survey, `version.zig` plus `dev_t.zig` starter helpers, direct behavior and focused layout replays, paired build wrappers, validator, and dedicated Linux-header governance note
- policy and unsafe work stays with the survey wording, policy-byte checker, and explicit caller-policy surfaces
- low-level wrapper work stays with the atomic, barrier, MMIO, and narrow-unsafe helper packet plus the focused low-level replay
- MMIO and narrow unsafe are the overlap hotspots, so use the reason for the change to choose the lane: policy-byte and policy-wording changes stay policy-owned, while helper-surface and replay changes stay low-level-wrapper-owned

This keeps future Phase 3 follow-up small and reviewable without reopening already-parked adjacent packets just because they share one helper file.

## Recommended next-step order

1. shared-summary refresh only if one of the shared reminder surfaces drifts after this note lands
2. packet-local survey or validator sync if one of the four owning packets drifts but the helper surface itself has not changed
3. shared ABI route or manifest work only when the replay route, generated wrappers, catalog, or bounded shared packet inventory itself moves
4. no cross-packet reopen unless the changed surface really belongs to more than one owner packet and both notes need the same bounded refresh

## Anti-overlap rule

If a scheduled Phase 3 run is assigned a substrate family lane, keep the work inside that family's packet plus the smallest unavoidable shared-ABI touch. If the shared ABI lane is assigned, do not consume export/UAPI, policy/unsafe, or low-level-wrapper backlog just because the shared lane has spare room.

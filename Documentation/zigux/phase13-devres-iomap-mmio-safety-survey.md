# Phase 13 devres iomap MMIO Safety Survey

## Purpose

This note records the exact current-`master` safety behavior around the Phase 13 `devm_of_iomap()` planner packet without overstating it as a live MMIO implementation.

It ties the shipped Phase 13 `devres` planning surface back to the already-landed shared MMIO safety substrate in `zigux/helpers/mmio.zig` and the corresponding wrapper evidence in `zigux/tests/phase3_low_level_wrappers.zig`.

## Bounded finding

Current `master` keeps the Phase 13 `devres` iomap slice planning-only while routing actual volatile-MMIO permission checks through the shared Phase 3 helper surface.

- `Documentation/zigux/phase13-devres-iomap-planner.md` still describes a pure `devm_of_iomap()` planning surface in `lib/devres.zig`
- `zigux/tests/phase13_devres_iomap_planner.zig` still replays translation-miss, request-region-denial, remap-failure, and cleanup-handoff cases without claiming live mapping side effects
- the shipped helper descriptor in `lib/devres.zig` keeps `.touches_live_mmio = false`
- the shipped MMIO gate in `zigux/helpers/mmio.zig` only permits the volatile-MMIO unsafe scope and rejects the safe-only scope, the raw-pointer bridge scope, and reserved-byte misuse

## Exact MMIO safety evidence

The current shared MMIO helper exports the explicit gate and access entry points directly in `zigux/helpers/mmio.zig`:

- `pub fn allowsInteropPolicyBytes`
- `pub fn requireInteropPolicyBytes`
- `pub fn readScoped`
- `pub fn writeScoped`
- `pub fn readInteropPolicyBytes`
- `pub fn writeInteropPolicyBytes`
- `pub fn exchangeInteropPolicyBytes`
- `pub fn writeMaskedInteropPolicyBytes`

The live behavior recorded by the shipped tests is:

- `unsafe_scope = 1` with `reserved = 0` is the allowed volatile-MMIO byte-policy form
- `unsafe_scope = 0` is denied with `error.UnsafeScopeDenied`
- `unsafe_scope = 2` is denied for MMIO even though it remains valid for the separate raw-pointer bridge surface
- any non-zero reserved byte is rejected as `error.InvalidInteropPolicy`
- denied MMIO writes stay side-effect free in the wrapper tests before any register value changes

The current exact wrapper evidence lives in `zigux/tests/phase3_low_level_wrappers.zig`:

- `phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff`
- `phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates`
- `phase3 low-level wrappers keep MMIO single-byte interop-policy shorthands explicit`
- `phase3 low-level wrappers keep whole-record MMIO interop-policy helpers explicit`
- `phase3 low-level wrappers keep direct MMIO scope gates explicit`

Those tests currently show:

- denied `mmio.writeInteropPolicyBytes(u32, 0, 0, ...)` leaves the register unchanged
- denied `mmio.readInteropPolicyBytes(u32, 1, 1, ...)` fails on reserved-byte misuse
- allowed `mmio.writeInteropPolicyBytes(u32, 1, 0, ...)` and `mmio.readInteropPolicyBytes(u32, 1, 0, ...)` succeed on the same register path
- denied `mmio.writeScoped(..., .raw_pointer_bridge, ...)` leaves the register unchanged
- allowed `.volatile_mmio` scoped reads, writes, exchanges, and masked writes succeed only after the explicit scope gate

## Phase 13 boundary evidence

The current Phase 13 packet keeps this safety surface downstream from the `devres` planner instead of pretending the planner already owns live MMIO state.

The exact planning-only evidence remains:

- `Documentation/zigux/phase13-devres-iomap-planner.md` says the packet records one pure `devm_of_iomap()` planning surface
- `Documentation/zigux/phase13-devres-iomap-planner.md` says it does not claim live MMIO mapping state
- `zigux/tests/phase13_devres_iomap_planner.zig` checks translation-miss, request-region-denial, remap-failure, and cleanup-handoff behavior
- `zigux/tests/phase13_devres_iomap_planner.zig` keeps `plan.reaches_managed_ioremap_resource`, `plan.request_region_denied`, `plan.releases_region_on_remap_failure`, and `handoff.hands_off_to_iounmap_cleanup` reviewable as helper-first planning outputs

That means the current truthful repo posture is:

- Phase 13 `devres` iomap work plans whether a managed MMIO path would advance
- the shared MMIO helper owns the actual volatile-MMIO access gate
- live MMIO mapping state, live device-tree walks, and arch memtype mutation remain blocked repo-reality gaps

## Replay handles

- `zig test --build-file zigux/tests/phase3_low_level_wrappers_build.zig phase3-low-level-wrappers-test`
- `zig test --dep devres -Mroot=zigux/tests/phase13_devres_iomap_planner.zig -Mdevres=lib/devres.zig`
- `zig run scripts/zigux/check_phase13_devres_iomap_mmio_safety_survey.zig`

## Boundaries

- This note does not claim `devm_of_iomap()` is implemented as a live MMIO mapper in Zigux today.
- This note does not move the raw-pointer bridge surface into the MMIO allow-list.
- This note does not claim live device-tree traversal, live remap ownership, or live arch memtype mutation.
- This note only records the exact current safety evidence already shipped on `master`.

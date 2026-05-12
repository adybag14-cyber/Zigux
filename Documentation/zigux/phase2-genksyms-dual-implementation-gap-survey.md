# Phase 2 Genksyms Dual-Implementation Gap Survey

This note records the current `master` gap between the Phase 2 roadmap target for `scripts/genksyms/genksyms.c` and the Zigux product surfaces that are actually present today.

## Roadmap Target

Phase 2 treats `scripts/genksyms/genksyms.c` as one of the bounded toolchain and kbuild-facing dual-implementation targets.
The roadmap and commit ledger both describe a wrapper-first Zigux packet centered on `scripts/zigux/genksyms.zig`.

## Current Master Evidence

- `Documentation/zigux/phase2-closure.md` still describes a live `22-case` `genksyms` bridge packet under `zigux/tests/fixtures/genksyms_bridge/`.
- `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still name `scripts/zigux/genksyms.zig`, `scripts/zigux/check-genksyms-bridge.py`, `zig test scripts/zigux/genksyms.zig`, and the `genksyms_bridge` fixture family as shipped current-`master` surfaces.
- `zigux/tests/fixtures/phase2_tool_manifest.json` still lists `genksyms_bridge` as one of the active Phase 2 families.
- Direct current-`master` file reads do not materialize the bridge packet itself: `scripts/zigux/genksyms.zig`, `scripts/zigux/check-genksyms-bridge.py`, and `zigux/tests/fixtures/genksyms_bridge/` are absent on current `master`.
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` only lists `genksyms_crc` and `mk_elfconfig`, which matches the live artifact-tool subset and reinforces that the CRC lane exists while the broader `genksyms` bridge packet does not currently land beside it.

## Gap Summary

Current `master` keeps the `genksyms` roadmap target visible in shared Phase 2 reminder surfaces, but the wrapper-first dual-implementation packet itself is not present.
That means the live repository currently holds a Phase 2 `genksyms` documentation-and-manifest claim without the matching bridge implementation, checker, fixtures, or direct replay entrypoint.

## Missing Packet

The smallest roadmap-backed missing packet is still the ledger-backed bridge family:

- `scripts/zigux/genksyms.zig`
- `scripts/zigux/check-genksyms-bridge.py`
- `zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- bounded expected-output artifacts under `zigux/tests/fixtures/genksyms_bridge/`

## Next Bounded Step

Stay inside the same Phase 2 `genksyms` lane family and let `P2-L08` land the smallest truthful bridge packet first:

1. add `scripts/zigux/genksyms.zig` with one bounded wrapper-first option-parsing slice
2. add the paired `check-genksyms-bridge.py` checker plus the smallest fixture packet needed to compare Zig and C behavior for that slice
3. widen the shared Phase 2 reminder surfaces only after the bridge packet exists on `master`

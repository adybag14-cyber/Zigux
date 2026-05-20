# Phase 3 `abi.h` Boundary Next Step

This note keeps the current `include/zigux/abi.h` boundary truthful on `master` without widening into broader shared ABI closure claims.

## Scope

- `PHASE3_ABI_H_PATH=include/zigux/abi.h`
- `PHASE3_ABI_H_PACKET=shared Phase 3 ABI header boundary only`
- `PHASE3_ABI_H_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md`
- `PHASE3_ABI_H_FOCUSED_CHECKER=scripts/zigux/check-phase3-abi.py`
- `PHASE3_ABI_H_REPLAY=zigux/tests/phase3_abi.zig`
- `PHASE3_ABI_H_DUMP_REPLAY=zigux/tests/phase3_abi_dump_current.zig`
- `PHASE3_ABI_H_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json`
- this note is limited to the already-landed `include/zigux/abi.h` packet and the directly coupled review surfaces that keep that header readable on current `master`

## Current State

- `include/zigux/abi.h` remains the canonical owner for `zigux_boundary_header`, `zigux_export_status`, `zigux_interop_policy`, the chrdev budget-window layout constants and structs, the notifier/list/hlist relay structs, and the inline header/status/policy helpers.
- Current `master` still pairs that canonical header with `zigux/bindings/abi.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/layout_assert.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump_current.zig`, `scripts/zigux/check-phase3-abi.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json`.
- The shared ABI replay already keeps the notifier priority helpers, malformed list detection helpers, layout assertions, status helpers, and interop-policy decoding visible beside the published header surface.
- The focused checker already fails closed on many shared ABI header markers, but current repo evidence still leaves the notifier source markers themselves as the next direct same-packet guard to tighten rather than a reason to grow `include/zigux/abi.h` again.

## Next Safe Step

- Do not add another ABI-header surface in this lane just to keep activity moving.
- The next same-packet move is to publish one focused `scripts/zigux/check-phase3-abi.py` tightening so it fails closed if `zigux_notifier_chain_priority_increase`, `zigux_notifier_first_chain_priority_increase()`, or `zigux_notifier_chain_has_nonincreasing_priority()` disappear from `include/zigux/abi.h`.
- If that checker repair lands, refresh this note only as needed to keep the focused-checker claim and directly coupled file list honest.

## Boundary

- Keep binding growth, export/UAPI relay work, low-level-wrapper follow-through, and broader shared ABI manifest reshaping on their own lanes.
- Reopen this note only if it drifts from the shipped header, the directly coupled replay files, the focused checker, or the manifest-backed packet inventory.

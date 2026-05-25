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
- Current `master` still pairs that canonical header with `zigux/bindings/abi.zig`, `zigux/bindings/header_family.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/layout_assert.zig`, `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump_current.zig`, `scripts/zigux/check-phase3-abi.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json`.
- The shared ABI replay already keeps the raw boundary-header rejection path, header canonicalization and extra-byte helpers, Linux-facing header-family relay checks, notifier priority helpers, malformed list detection helpers, layout assertions, status helpers, and interop-policy decoding visible beside the published header surface.
- The focused checker now also fails closed on notifier source markers inside `zigux_notifier_chain_has_nonincreasing_priority()` and `zigux_notifier_first_chain_priority_increase()`, and on the shipped `zigux_hlist_first_pprev_matches_head()` guard, so priority-sequence and first-node prev-link regressions in the inline header helpers no longer hide behind signature-only coverage.

## Next Safe Step

- Do not add another ABI-header surface in this lane just to keep activity moving.
- Keep this note parked unless a fresh current-master reread finds a smaller same-packet checker or replay drift around the already-landed raw boundary-header guard, header-family relay proof, notifier guard, hlist-head guard, header helpers, or manifest-backed packet inventory.
- If that future reread finds drift, refresh this note only as needed to keep the focused-checker claim and directly coupled file list honest.

## Boundary

- Keep binding growth, export/UAPI relay work, low-level-wrapper follow-through, and broader shared ABI manifest reshaping on their own lanes.
- Reopen this note only if it drifts from the shipped header, the directly coupled replay files, the focused checker, or the manifest-backed packet inventory.

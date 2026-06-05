# Phase 3 Docs-Root Helper Slice Index

This note records the Backup audit B correction for the docs-root Phase 3 helper-slice index.

## Corrected Index Requirement

The docs-root Phase 3 reminder index must name the helper slice notes that are directly served by current `master`:

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `Documentation/zigux/phase3-list-hlist-slice.md`

Those notes belong beside the existing Phase 3 ABI, err_ptr/xarray, xarray-slot, policy, validator-support, export/UAPI, header-family, low-level-wrapper, catalog, and manifest surfaces.

## Boundary

This correction is an index and reminder truthfulness fix. It does not widen Phase 3 into broader shared replay, broader header-family completion, intrusive list mutation ownership, container-of recovery, exported ABI struct completion, scheduler-affinity policy, or full interop parity claims.

## Replay

Use `zig build docs-root-phase3-helper-slice-index-contract --build-file zigux/tests/docs_root_phase3_helper_slice_index_contract_build.zig` to keep this correction reviewable from Zig.

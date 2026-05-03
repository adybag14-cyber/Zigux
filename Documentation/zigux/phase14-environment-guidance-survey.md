# Phase 14 Environment Guidance Survey

This note records the operational contract for the shared Phase 14 smoke packet.

## Purpose

Phase 14 is still a study-only and stay-in-C boundary for `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c`. That means the attached toolchain fallback should stay reviewable as an operational wrapper contract, not as a shortcut that bypasses the existing validator-backed packet.

This survey closes one narrow gap: it makes the environment guidance explicit in one dedicated note and pairs it with a dedicated checker so later shared-smoke maintenance can prove the fallback contract still matches the repo surfaces that already own it.

## Environment Contract

- run the shared packet from a real repo-root checkout or mounted tree so `make -C zigux ...` resolves the published wrapper entrypoints against the current Zigux paths
- keep `python3` available for `make -C zigux phase14-validate`; the shared packet is validator-first before any broader replay
- use the published `make -C zigux` wrappers instead of ad hoc nested-directory `zig build` calls when claiming Phase 14 shared-packet validation
- if `zig` is not on `PATH`, keep the same wrapper path and pass the attached toolchain through `ZIG=<attached-zig-path>`
- treat the fallback as an execution detail only; the source of truth remains the shared packet and the four anchor-local manifests plus survey notes already checked by `scripts/zigux/validate-phase14.py`

## Exact Attached-Toolchain Commands

- `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`
- `make -C zigux phase14-smoke ZIG=<attached-zig-path>`
- `make -C zigux phase14-test ZIG=<attached-zig-path>`
- `make -C zigux phase14 ZIG=<attached-zig-path>`

## Dedicated Guidance Check

Use the dedicated checker when a run is specifically about attached-toolchain or environment guidance drift:

- `python3 scripts/zigux/check-phase14-environment-guidance.py`
- `python3 scripts/zigux/check-phase14-environment-guidance.py --self-test`

The checker stays intentionally narrow. It only proves that the current guidance still agrees across:

- `scripts/zigux/README.md`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/Makefile`
- `scripts/zigux/validate-phase14.py`

## Non-Goals

This survey does not claim:

- live workqueue execution parity
- skbuff ownership or destructor parity
- a `kernel/trace/ring_buffer.zig` implementation
- a `kernel/rcu/tree_bridge.zig` implementation
- a replacement for `scripts/zigux/validate-phase14.py`

## Next Bounded Step

Leave this note parked unless one of the shared Phase 14 wrapper commands, the `PYTHON` or `ZIG` wrapper contract, or the shared packet's attached-toolchain wording drifts. If it does, update this note and the dedicated checker together instead of widening into anchor-local bridge work.

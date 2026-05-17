# Phase 2 Toolchain Bootstrap Notes

This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.

## Current direct packet

- `scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`, keeps the minimum version in lockstep, limits archive digests to `x86_64-linux`, and names `phase2-toolchain` plus `phase2-validate` as the required Linux-style make routes when those routes are rematerialized.
- `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, and `scripts/zigux/check-phase2-cross-selftest-alignment.py` are the current shipped Phase 2 reminder and alignment guards visible on `master`.
- `scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.
- `zigux/tests/README.md`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster keep the bounded tests-facing, toolchain, fixture-backed artifact-diff support, and bridge packet reviewable without widening into missing closure routes.

## Current repo-reality gaps

- Repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, and `make -C zigux phase2`.
- Treat the absent validator-first, cross-route, cross-target, installer, and Linux-style make replay names as historical packet members until same-lane work rematerializes them on `master`.

## Follow-through

- Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, kbuild-route reminders, tests-root truthfulness, kconfig bridge alignment, or fixture-backed artifact-diff support.
- Do not widen this note into fixdep semantics, genksyms parser behavior, conf or confdata bridge semantics, or cross-target execution claims until current `master` materializes those companion routes directly.

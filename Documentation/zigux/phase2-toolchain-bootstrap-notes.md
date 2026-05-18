# Phase 2 Toolchain Bootstrap Notes

This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.

## Current direct packet

- `scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`, keeps the minimum version in lockstep, limits archive digests to `x86_64-linux`, and names `phase2-toolchain` plus `phase2-validate` as the required Linux-style make routes when those routes are rematerialized.
- `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-required-make-routes.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, and `scripts/zigux/check-phase2-cross-selftest-alignment.py` are the current shipped Phase 2 reminder and alignment guards visible on `master`.
- `scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.
- `scripts/zigux/install-zig.py` is directly readable on current `master` as the bounded installer helper, but the live bootstrap packet still does not rerun `python3 scripts/zigux/install-zig.py --self-test`, so keep the helper itself explicit without implying the self-test hook has returned.
- `.github/workflows/zigux-bootstrap.yml` also derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, and `ZIGUX_ZIG_URL` from `scripts/zigux/zig-toolchain-policy.json`, tries `community-mirrors.txt` before the direct Zig download URL, and reruns `python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"` inside each install attempt so the pinned bootstrap setup path stays reviewable at the same policy-driven boundary as the later reminder hooks.
- `.github/workflows/zigux-bootstrap.yml` now runs `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, so the live bootstrap packet exercises both the pinned-channel and pinned-archive integrity paths instead of leaving archive validation as notes-only policy text.
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, toolchain, fixture-backed artifact-diff support, and bridge packet reviewable without widening back into older installer or direct cross-route claims.
- Within that live kconfig roster, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` now records the full sixteen-mode `conf_bridge` packet, including the explicit empty `allmodconfig` `allconfig` override packet beside the `randconfig` override packet and the dedicated `randconfig_env_packet`, so reminder surfaces should mirror the current manifest-backed bridge evidence instead of the older narrower override story.
- The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`, so keep those routes in the present packet instead of the repo-reality-gap list.

## Current repo-reality gaps

- Repeated authenticated reads on current `master` still return missing for `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`.
- Treat the still-unhooked installer self-test and direct cross-route names as historical packet members until same-lane work rematerializes them on `master`.

## Follow-through

- Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, kconfig bridge alignment, or fixture-backed artifact-diff support.
- Do not widen this note into fixdep semantics, genksyms parser behavior, conf or confdata bridge semantics, or direct cross-target execution claims until current `master` materializes those companion installer or direct cross-route surfaces.

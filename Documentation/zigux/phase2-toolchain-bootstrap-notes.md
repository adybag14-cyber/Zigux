# Phase 2 Toolchain Bootstrap Notes

This note records the bounded Phase 2 toolchain pinning, build-check, and kbuild-facing replay surface that the shared reminder packet already names across the docs root, review checklist, scripts index, tests root, and Makefile.

## Shared Guard Surface

- policy file: `scripts/zigux/zig-toolchain-policy.json`
- shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`
- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
- shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`
- shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`
- shared cross selftest-alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- shared cross selftest-alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- shared fixdep gate self-test: `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- shared fixdep gate: `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- shared fixdep diff self-test: `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- shared fixdep diff gate: `python3 scripts/zigux/check-fixdep-diff.py`
- shared genksyms CRC parity gate: `python3 scripts/zigux/check-genksyms-crc-diff.py`
- shared mk_elfconfig parity self-test: `python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test`
- shared mk_elfconfig parity gate: `python3 scripts/zigux/check-mk-elfconfig-diff.py`
- direct mk_elfconfig Zig replay: `zig test scripts/zigux/mk_elfconfig.zig`
- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`
- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`
- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`
- direct artifact-tools manifest: `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- direct genksyms CRC Zig replay: `zig test scripts/zigux/genksyms_crc.zig`
- direct kconfig bridge Zig replay: `zig test scripts/zigux/kconfig/conf_bridge.zig`
- direct confdata bridge Zig replay: `zig test scripts/zigux/kconfig/confdata_bridge.zig`
- guard self-test: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- guard: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- shared validator gate: `python3 scripts/zigux/validate-phase2.py`
- closure validator gate: `python3 scripts/zigux/validate-phase2-closure.py`
- Linux-style toolchain route: `make -C zigux phase2-toolchain`
- Linux-style validator route: `make -C zigux phase2-validate`
- Linux-style tools route: `make -C zigux phase2-tools`
- Linux-style kconfig route: `make -C zigux phase2-kconfig`
- Linux-style cross route: `make -C zigux phase2-cross`
- Linux-style tranche route: `make -C zigux phase2`

## Pin Scope

- closure note: `Documentation/zigux/phase2-closure.md`
- workflow install path: `python3 scripts/zigux/install-zig.py --dest .zig-toolchain`
- workflow verification path: `python3 scripts/zigux/check-zig-toolchain.py`
- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`
- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`
- current pinned bootstrap archive target: `x86_64-linux`
- current pinned bootstrap archive sha256 (`x86_64-linux`): `a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858`
- `PHASE2_LINUX_STYLE_ROUTE_COUNT=6`
- `PHASE2_LINUX_STYLE_ROUTES=phase2-toolchain,phase2-validate,phase2-tools,phase2-kconfig,phase2-cross,phase2`
- the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence
- the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin
- the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset currently stays anchored in this dedicated note, `scripts/zigux/README.md`, and `scripts/zigux/check-phase2-toolchain-pin-scope.py` until the broader shared reminder surfaces restate the same detail explicitly and keep the same six-route inventory visible

## Alignment Notes

- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py` keep this dedicated bootstrap note aligned with `zigux/tests/fixtures/phase2_cross_targets.json`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase2.py`, and `scripts/zigux/validate-phase2-closure.py` so the bounded three-target compile matrix stays reviewable from the same Phase 2 note instead of being implied only by sibling reminder surfaces
- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `artifact_tools` (`genksyms_crc` plus `mk_elfconfig`), `kconfig`, and `confdata` packet links it pins, `.github/workflows/zigux-bootstrap.yml`, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator
- the dedicated fixdep gate checker keeps the bounded fixdep workflow gate paired with the direct `zig test scripts/zigux/fixdep.zig` replay and the shared tools route
- the direct fixdep parity checker keeps the direct fixdep parity surface reviewable beside the same artifact packet and Linux-style tool replay
- the shared and closure validators above are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text
- the Linux-style `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` replay routes keep this dedicated note tied to the same kbuild-facing replay surface named by `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, the shared validator pair, and the closure note
- the six-route inventory above should stay byte-for-byte aligned with the active Phase 2 entries in `zigux/Makefile` so future reminder-surface widening does not silently drop the dedicated toolchain or cross compile routes

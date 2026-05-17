# Phase 2 Toolchain Bootstrap Notes

This note records the bounded Phase 2 toolchain pinning, build-check, and kbuild-facing replay surface that the shared reminder packet already names across the docs root, review checklist, scripts index, tests root, and Makefile.

## Shared Guard Surface

- policy file: `scripts/zigux/zig-toolchain-policy.json`
- shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`
- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- shared kconfig selftest-alignment gate: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- shared kconfig bridge gate: `python3 scripts/zigux/check-kconfig-bridge.py`
- shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`
- shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`
- shared cross selftest-alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- shared cross selftest-alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
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
- the broader fixdep, genksyms, artifact-tools, and manifest packet should stay documented through `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` instead of restating the full broader checker inventory in this dedicated pin-scope note

## Pin Scope

- closure note: `Documentation/zigux/phase2-closure.md`
- workflow install path remains historical on this branch until `scripts/zigux/install-zig.py` is restored: `python3 scripts/zigux/install-zig.py --dest .zig-toolchain`
- workflow verification path: `python3 scripts/zigux/check-zig-toolchain.py`
- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`
- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`
- current pinned bootstrap archive target: `x86_64-linux`
- current pinned bootstrap archive sha256 (`x86_64-linux`): `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`
- `PHASE2_LINUX_STYLE_ROUTE_COUNT=6`
- `PHASE2_LINUX_STYLE_ROUTES=phase2-toolchain,phase2-validate,phase2-tools,phase2-kconfig,phase2-cross,phase2`
- the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence
- the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin
- the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset now stays explicit across this dedicated note, `Documentation/zigux/README.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, while `scripts/zigux/check-phase2-toolchain-pin-scope.py` keeps the pin-scope guard fail-closed on the same six-route inventory

## Upgrade Policy

- the Phase 2 toolchain policy keeps `channel` and `minimum_version` in lockstep so the pinned bootstrap archive and the minimum accepted Zig version do not drift apart
- the Phase 2 toolchain policy requires refreshing the pinned `x86_64-linux` archive sha256 whenever the pinned channel changes
- the Phase 2 toolchain policy requires rerunning `make -C zigux phase2-toolchain` and `make -C zigux phase2-validate` before landing any pinned Zig change

## Alignment Notes

- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py` keep this dedicated bootstrap note aligned with `zigux/tests/fixtures/phase2_cross_targets.json`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase2.py`, and `scripts/zigux/validate-phase2-closure.py` so the bounded three-target compile matrix stays reviewable from the same Phase 2 note instead of being implied only by sibling reminder surfaces
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py` keep this dedicated bootstrap note aligned with `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-confdata-bridge-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` so the shipped `16-case` conf bridge plus `13-case` confdata fixture replay stays reviewable from the same Phase 2 note instead of being implied only by sibling reminder surfaces
- the shared tests README alignment self-test and gate keep this dedicated bootstrap note aligned with `zigux/tests/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` replay surface instead of leaving this note coupled to the broader Phase 2 packet by implication alone
- the closure note, tests root, and Makefile keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json` plus `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` packet, the bounded direct `zig test scripts/zigux/fixdep.zig` replay, the committed genksyms bridge fixture packet, and the checker-backed kconfig bridge plus confdata manifest packet reviewable without reopening the dedicated genksyms or kconfig lanes from this bootstrap note
- the active Phase 2 closure note and Makefile keep the validator-routed direct `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/kconfig/conf_bridge.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` replays explicit beside the same bounded Phase 2 tools and kconfig routes, while `zigux/tests/README.md` keeps the corresponding fixdep, genksyms bridge, and kconfig manifest packet reviewable without restating every direct tests-root replay command
- the shared and closure validators above are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text
- the Linux-style `make -C zigux phase2-validate` and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the docs-root summary, the shared validators, the closure note, and the shared review checklist
- the Linux-style `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` replay routes keep this dedicated note tied to the same kbuild-facing replay surface named by `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, the shared validator pair, and the closure note
- the six-route inventory above should stay byte-for-byte aligned with the active Phase 2 entries in `zigux/Makefile` so future reminder-surface widening does not silently drop the dedicated toolchain or cross compile routes

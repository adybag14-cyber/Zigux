# Phase 2 Closure

This note records the bounded Phase 2 toolchain, build-check, and kbuild-facing closure packet that current Zigux reminder surfaces already name across the docs root, review checklist, scripts index, tests root, workflow, and Linux-style make routes.

## Status

- `PHASE2_STATUS=closed`
- `PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1`
- `PHASE2_TOOLCHAIN_PIN_TARGETS=x86_64-linux`
- `PHASE2_LINUX_STYLE_ROUTE_COUNT=6`
- `PHASE2_LINUX_STYLE_ROUTES=phase2-toolchain,phase2-validate,phase2-tools,phase2-kconfig,phase2-cross,phase2`
- the pinned bootstrap archive stays limited to `x86_64-linux` while the compile matrix remains a separate three-target Phase 2 replay surface under `zigux/tests/fixtures/phase2_cross_targets.json`
- the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset remains part of the active shared Phase 2 packet together with `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`

## Closure Packet

- `PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- shared validator gate: `python3 scripts/zigux/validate-phase2.py`
- closure validator gate: `python3 scripts/zigux/validate-phase2-closure.py`
- shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`
- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`
- shared tool-manifest packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`
- shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`
- shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`
- shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- shared kconfig selftest-alignment gate: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- shared kconfig bridge gate: `python3 scripts/zigux/check-kconfig-bridge.py`
- shared fixdep gate self-test: `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- shared fixdep gate: `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- shared fixdep diff self-test: `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- shared fixdep diff gate: `python3 scripts/zigux/check-fixdep-diff.py`
- shared genksyms bridge selftest-alignment self-test: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`
- shared genksyms bridge selftest-alignment gate: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`
- direct genksyms bridge self-test: `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- direct genksyms bridge gate: `python3 scripts/zigux/check-genksyms-bridge.py`
- direct genksyms CRC artifact gate: `python3 scripts/zigux/check-genksyms-crc-diff.py`
- direct mk_elfconfig artifact self-test: `python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test`
- direct mk_elfconfig artifact gate: `python3 scripts/zigux/check-mk-elfconfig-diff.py`
- direct Zig replays: `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/genksyms_crc.zig`, `zig test scripts/zigux/kconfig/conf_bridge.zig`, `zig test scripts/zigux/kconfig/confdata_bridge.zig`, and `zig test scripts/zigux/mk_elfconfig.zig`
- Linux-style routes: `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2`

## Review Notes

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md` remains the dedicated pin-scope companion note for the pinned `0.17.0-dev.87+9b177a7d2` channel, the minimum-version policy, the bootstrap archive SHA, and the boundary between the single pinned bootstrap host target and the separate cross-target compile matrix
- `zigux/tests/fixtures/phase2_tool_manifest.json` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the committed `fixdep`, `genksyms`, `genksyms_crc`, `mk_elfconfig`, `kconfig`, and `confdata` packet visible to the shared validators instead of leaving the bounded tool tranche implicit
- the dedicated tests README alignment checker keeps `Documentation/zigux/README.md`, this closure note, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes aligned around the same bounded toolchain packet
- `PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard`
- the current `fixdep` closure packet now stays explicit as the ten-case artifact replay under `zigux/tests/fixtures/fixdep/cases.json`, including the concatenated same-target dep tail and the bounded `/dev/full` stdout-write cases that preserve the original parse-error or missing-dependency stderr contract
- the live fixdep closure packet is still present on current `master` through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, even while some broader Phase 2 bridge-checker families named by the full route inventory still do not materialize as standalone scripts under `scripts/zigux/`
- the dedicated Phase 2 `genksyms` bridge packet remains the live `27-case` bridge surface under `zigux/tests/fixtures/genksyms_bridge/`, and the shared alignment checker plus scripts-root summary should keep that case count explicit instead of drifting back to older undercounts
- the six-route inventory above now keeps the dedicated toolchain and cross compile wrappers explicit beside the broader tranche route, which matches the active `zigux/Makefile` Phase 2 packet and reduces reminder-surface undercounts during future closure maintenance
- rollback remains toolchain-first and bounded: keep C authoritative, remove or disable the failing Zigux Phase 2 helper replay from shared make and workflow wiring, and preserve the pinned toolchain policy plus closure-note truthfulness until the bounded packet is green again

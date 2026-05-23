# Phase 2 Closure

This note records the bounded Phase 2 toolchain, build-check, and kbuild-facing closure packet that current Zigux reminder surfaces already name across the docs root, review checklist, scripts index, tests root, workflow, and Linux-style make routes.

## Status

- `PHASE2_STATUS=closed`
- `PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1`
- `PHASE2_TOOLCHAIN_PIN_TARGETS=x86_64-linux`
- `PHASE2_LINUX_STYLE_ROUTE_COUNT=8`
- `PHASE2_LINUX_STYLE_ROUTES=phase2-toolchain,phase2-tools,phase2-kconfig,phase2-cross,phase2-genksyms,phase2-fixdep,phase2-validate,phase2`
- the pinned bootstrap archive stays limited to `x86_64-linux` while the compile matrix remains a separate three-target Phase 2 replay surface under `zigux/tests/fixtures/phase2_cross_targets.json`
- the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, `phase2-validate`, and `phase2` routes when `ZIG` is unset remains part of the active shared Phase 2 packet together with `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`

## Closure Packet

- `PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json`
- `PHASE2_TOOLCHAIN_SELF_TEST=python3 scripts/zigux/check-zig-toolchain.py --self-test`
- `PHASE2_TOOLCHAIN_POLICY_ONLY_GATE=python3 scripts/zigux/check-zig-toolchain.py --policy-only`
- `PHASE2_TOOLCHAIN_ARCHIVE_ONLY_GATE=python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
- `PHASE2_LOCAL_ARCHIVE_WORKFLOW_SELF_TEST=python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`
- `PHASE2_LOCAL_ARCHIVE_WORKFLOW_GATE=python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`
- `PHASE2_LOCAL_ARCHIVE_README_SELF_TEST=python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`
- `PHASE2_LOCAL_ARCHIVE_README_GATE=python3 scripts/zigux/check-lane05-local-archive-readme.py`
- `PHASE2_INSTALL_ZIG_SELF_TEST=python3 scripts/zigux/install-zig.py --self-test`
- `PHASE2_INSTALL_ARCHIVE_VERIFICATION_SELF_TEST=python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`
- `PHASE2_INSTALL_ARCHIVE_VERIFICATION_GATE=python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`
- `PHASE2_STAGE_PINNED_ARCHIVE_SELF_TEST=python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`
- `PHASE2_STAGE_HELPER_CONTRACT_SELF_TEST=python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`
- `PHASE2_STAGE_HELPER_CONTRACT_GATE=python3 scripts/zigux/check-lane05-stage-helper-contract.py`
- `PHASE2_STAGE_HELPER_SELFTEST_SELF_TEST=python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`
- `PHASE2_STAGE_HELPER_SELFTEST_GATE=python3 scripts/zigux/check-lane05-stage-helper-selftest.py`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- shared validator gate: `python3 scripts/zigux/validate-phase2.py`
- closure validator gate: `python3 scripts/zigux/validate-phase2-closure.py`
- shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`
- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
- shared kconfig README alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test`
- shared kconfig README alignment gate: `python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py`
- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- shared kconfig bridge gate: `python3 scripts/zigux/check-kconfig-bridge.py`
- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`
- shared tool-manifest packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`
- shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`
- shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`
- shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- shared kconfig selftest-alignment gate: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- shared fixdep gate self-test: `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- shared fixdep gate: `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- shared fixdep diff self-test: `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- shared fixdep diff gate: `python3 scripts/zigux/check-fixdep-diff.py`
- shared genksyms bridge self-test: `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- shared genksyms bridge gate: `python3 scripts/zigux/check-genksyms-bridge.py`
- committed genksyms bridge fixture packet: `zigux/tests/fixtures/genksyms_bridge/`
- committed artifact-tools manifest packet: `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, which keeps the parked `genksyms_crc` and `mk_elfconfig` artifact-tool names explicit on current `master` without implying standalone `zigux/tests/fixtures/genksyms_crc/` or `zigux/tests/fixtures/mk_elfconfig/` directories
- direct replay owners stay bounded on current `master`: `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/kconfig/conf_bridge.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` remain the shipped direct Phase 2 Zig replays, while the broader artifact-tools packet stays documented through `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, `zigux/tests/README.md`, and `zigux/Makefile` instead of implying extra standalone artifact replay entrypoints on current `master`
- Linux-style routes: `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`

## Review Notes

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md` remains the dedicated pin-scope companion note for the pinned `0.17.0-dev.87+9b177a7d2` channel, the minimum-version policy, the bootstrap archive SHA, the repo-local archive staging helper packet, and the boundary between the single pinned bootstrap host target and the separate cross-target compile matrix
- `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` keep the committed `fixdep`, `genksyms`, `genksyms_crc`, `mk_elfconfig`, `kconfig`, `confdata`, archive-support, artifact-support, archive-staging, and stage-helper packet visible to the shared validators instead of leaving the bounded tool tranche implicit
- the shared tool-manifest packet stays present in the workflow and Linux-style make routes indirectly through `python3 scripts/zigux/validate-phase2.py`: the bootstrap workflow reruns that shared validator directly, `make -C zigux phase2-tools` reaches the same validator through `zigux/Makefile`, and the validator in turn reruns `scripts/zigux/check-phase2-tool-manifest-packets.py` so the committed manifest packet remains part of the bounded kbuild-facing closure route without needing duplicate dedicated workflow steps
- `third_party/README.md`, `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` now stay explicit inside the shared Phase 2 toolchain packet, so the closure note matches the live `phase2-toolchain` route and shipped validator instead of leaving the newer archive-staging helper packet implied only by the workflow or manifest surfaces
- `Documentation/zigux/phase2-fixdep-next-step-note.md` and `Documentation/zigux/phase2-confdata-bridge-survey.md` are active Phase 2 companion notes on current `master`: the fixdep note records that `scripts/zigux/check-phase2-fixdep-gate.py`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase2-closure.md`, and `zigux/tests/fixtures/fixdep/cases.json` already agree on the same live twelve-case packet and keeps the parked validation rerun explicit, and the confdata survey keeps the roadmap-backed scaffold marked closed so future reopening stays bridge-local instead of recreating missing-scaffold claims.
- the dedicated tests README alignment checker keeps `Documentation/zigux/README.md`, this closure note, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the Linux-style `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, `phase2-validate`, and `phase2` routes aligned around the same bounded toolchain packet
- `PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard`
- the current `fixdep` closure packet now stays explicit as the twelve-case artifact replay under `zigux/tests/fixtures/fixdep/cases.json`, including the plain escaped-newline dependency continuation case, the escaped-newline rustc-style pre-target comment case, the concatenated same-target dep tail, and the bounded `/dev/full` stdout-write cases that preserve the original parse-error or missing-dependency stderr contract
- the live fixdep closure packet is still present on current `master` through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, and the broader shared Phase 2 checker stack named by the route inventory now ships through `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-phase2-cross.py`, and `scripts/zigux/check-phase2-kconfig-selftest-alignment.py` while the direct artifact-tools and kconfig bridge replays stay documented through manifests, `zigux/tests/README.md`, and `zigux/Makefile` instead of being framed as missing standalone scripts
- the current `kconfig` closure packet now stays explicit as the `16-case` conf bridge plus `13-case` confdata fixture replay under `zigux/tests/fixtures/kconfig_bridge/cases.json`, with `scripts/zigux/check-kconfig-bridge.py`, `syncconfig` `nosilentupdate`, explicit `allconfig` overrides, the `defconfig` and `savedefconfig` mode-argument packet, the rewrite-mode trio (`yes2modconfig`, `mod2yesconfig`, `mod2noconfig`), and the duplicate-malformed quoted reassignment replay all carried through the shared checker and committed expected outputs instead of leaving those later bridge expansions implicit
- the live confdata closure packet now also keeps the later helper-local bridge coverage explicit on current `master`: uppercase tristate recognition, ignored non-`CONFIG_` lines, empty symbol-name rejection, malformed unset comment rejection, last-state transition coverage, duplicate malformed quoted reassignment coverage, and the shared kconfig selftest-alignment gate all agree on the same bounded `13-case` external fixture replay instead of collapsing those later bridge tightenings back into generic scaffold wording
- the dedicated `Phase 2 genksyms` bridge packet remains the live `23-case` bridge surface under `zigux/tests/fixtures/genksyms_bridge/`, and the shared reminder surfaces should keep that fixture-backed bridge evidence explicit without drifting back to older undercounts or claiming standalone checker scripts that are not present on current `master`
- the eight-route inventory above now keeps the dedicated toolchain, genksyms, and fixdep wrappers explicit beside the broader tranche route, which matches the active `zigux/Makefile` Phase 2 packet and reduces reminder-surface undercounts during future closure maintenance
- rollback remains toolchain-first and bounded: keep C authoritative, preserve the pinned toolchain policy plus closure-note truthfulness, and if a future Phase 2 helper replay fails, remove or disable the failing replay from shared make and workflow wiring until the bounded packet is green again

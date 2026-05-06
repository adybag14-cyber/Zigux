# Phase 2 Closure

This document closes the broadened bounded Phase 2 toolchain and Kbuild tranche for Zigux.

## Status

- `PHASE2_STATUS=closed`
- scope: bounded host-tool and bridge tranche only
- product boundary: `scripts/zigux/*`, `scripts/zigux/kconfig/*`, `zigux/Makefile`
- authority: current Linux C tools remain authoritative for risky parser-heavy behavior

## Closed Tool Set

The bounded Phase 2 tool set is:

- `scripts/zigux/fixdep.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_crc.zig`
- `scripts/zigux/mk_elfconfig.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`

- `PHASE2_TOOL_COUNT=6`
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`

## Closed Cross Target Set

The bounded Phase 2 cross-target compile set is:

- `x86_64-linux-musl`
- `aarch64-linux-musl`
- `riscv64-linux-musl`

- `PHASE2_CROSS_TARGET_COUNT=3`
- manifest: `zigux/tests/fixtures/phase2_cross_targets.json`

## Closure Gates

Phase 2 is only considered closed when all of the following are green:

1. bounded fixdep artifact parity
- `python3 scripts/zigux/check-fixdep-diff.py`

2. bounded genksyms CRC artifact parity
- `python3 scripts/zigux/check-genksyms-crc-diff.py`

3. bounded genksyms wrapper-first bridge parity
- `python3 scripts/zigux/check-genksyms-bridge.py`

4. bounded mk_elfconfig artifact parity
- `python3 scripts/zigux/check-mk-elfconfig-diff.py`

5. bounded kconfig bridge parity
- `python3 scripts/zigux/check-kconfig-bridge.py`

6. bounded phase2 cross-target compile gate
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- `python3 scripts/zigux/check-phase2-cross.py`

7. bounded phase2 cross-target self-test alignment gate
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`

8. bounded phase2 toolchain pin-scope gate
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`

9. bounded phase2 tests README alignment gate
- `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`

10. bounded phase2 unit gates
- `zig test scripts/zigux/fixdep.zig`
- `zig test scripts/zigux/genksyms.zig`
- `zig test scripts/zigux/genksyms_crc.zig`
- `zig test scripts/zigux/mk_elfconfig.zig`
- `zig test scripts/zigux/kconfig/conf_bridge.zig`
- `zig test scripts/zigux/kconfig/confdata_bridge.zig`

11. closure validation
- `python3 scripts/zigux/validate-phase2-closure.py`

- `PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py`
- `PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py`
- `PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test`
- `PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py`
- `PHASE2_CROSS_MANIFEST_POLICY=check-phase2-cross.py rejects duplicate tool entries, duplicate requested targets, unexpected explicit targets, duplicate manifest targets, and manifest-count drift before live compile replay`
- `PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `PHASE2_TESTS_README_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
- `PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py`
- `PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard`

## Toolchain Pin Boundary

The bounded Phase 2 bootstrap archive pin stays separate from the cross-target compile matrix:

- `PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1`
- `PHASE2_TOOLCHAIN_PIN_TARGETS=x86_64-linux`
- `scripts/zigux/zig-toolchain-policy.json` keeps the current bootstrap archive pin limited to `x86_64-linux` until new runner evidence lands.
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` keep that pinning note tied to the same shared validator and closure packet instead of leaving it as stand-alone reference text.

## Linux-Style Entry Point

The bounded Phase 2 entry point is:

- `zigux/Makefile`

This exists to keep the tranche callable in a Linux-style workflow without pretending that Zigux already replaces the native Kbuild flow.

## Rollback

Rollback owner:
- Zigux product maintainers working in `scripts/zigux` and `Documentation/zigux`

Fallback rule:
- if a tool or bridge regresses, keep the current Linux C tool authoritative and remove the failing Zigux lane from workflow wiring

Disable path:
- remove the failing bridge or tool from `.github/workflows/zigux-bootstrap.yml`
- remove the failing bridge or tool from `zigux/Makefile`
- reduce `zigux/tests/fixtures/phase2_tool_manifest.json` only if scope is deliberately reopened

- `PHASE2_ROLLBACK=keep C kbuild tools authoritative and remove failing Zigux bridge/tool from workflow wiring`

## Boundary

Phase 2 closure does not imply:

- full `scripts/genksyms/genksyms.c` parser parity
- full `scripts/kconfig/conf.c` rewrite
- full `scripts/kconfig/confdata.c` rewrite
- a full Kbuild replacement
- runtime kernel ABI closure

Phase 2 closes the bounded product tranche:

- selected dual implementations where behavior is small enough to prove
- wrapper-first bridge scaffolding for parser-heavy tooling, including `genksyms`
- deterministic artifact checks
- explicit cross-target compile gating

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
- `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `python3 scripts/zigux/check-fixdep-diff.py`

2. bounded genksyms CRC artifact parity
- `python3 scripts/zigux/check-genksyms-crc-diff.py`

3. bounded genksyms wrapper-first bridge parity
- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `python3 scripts/zigux/check-genksyms-bridge.py`

4. bounded Phase 2 genksyms bridge self-test alignment gate
- `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`

5. bounded mk_elfconfig artifact parity
- `python3 scripts/zigux/check-mk-elfconfig-diff.py`

6. bounded kconfig bridge parity
- `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- `python3 scripts/zigux/check-kconfig-bridge.py`

7. bounded Phase 2 kconfig self-test alignment gate
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`

8. bounded phase2 cross-target compile gate
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- `python3 scripts/zigux/check-phase2-cross.py`

9. bounded phase2 cross-target self-test alignment gate
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`

10. bounded phase2 toolchain pin-scope gate
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`

11. bounded phase2 tests README alignment gate
- `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`

12. bounded phase2 unit gates
- `zig test scripts/zigux/fixdep.zig`
- `zig test scripts/zigux/genksyms.zig`
- `zig test scripts/zigux/genksyms_crc.zig`
- `zig test scripts/zigux/mk_elfconfig.zig`
- `zig test scripts/zigux/kconfig/conf_bridge.zig`
- `zig test scripts/zigux/kconfig/confdata_bridge.zig`

13. closure validation
- `python3 scripts/zigux/validate-phase2-closure.py`

- `PHASE2_FIXDEP_SELF_TEST=python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `PHASE2_GENKSYMS_BRIDGE_SELF_TEST=python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `PHASE2_GENKSYMS_BRIDGE_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`
- `PHASE2_GENKSYMS_BRIDGE_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`
- `PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py`
- `PHASE2_KCONFIG_BRIDGE_SELF_TEST=python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- `PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py`
- `PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- `PHASE2_KCONFIG_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
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

## Fixdep Closure Packet

The bounded fixdep closure packet currently keeps four committed artifact cases plus focused helper-local guards reviewable:

- `PHASE2_FIXDEP_CASE_COUNT=4`
- `PHASE2_FIXDEP_CASES=sample,sample_multi_target,sample_comment_only,sample_missing_dep`
- `PHASE2_FIXDEP_STDOUT_PACKET=sample_expected.txt,sample_multi_target_expected.txt,sample_comment_only_expected.txt,sample_missing_dep_expected.txt`
- `PHASE2_FIXDEP_STDERR_PACKET=sample_comment_only_expected.stderr.txt,sample_missing_dep_expected.stderr.txt`
- `PHASE2_FIXDEP_PACKET=zigux/tests/fixtures/fixdep/manifest.json`
- `PHASE2_FIXDEP_HELPER_LOCAL_ANCHOR_COUNT=4`
- the shared Phase 2 tool manifest points at the same tool-local packet through `fixdep_packet`, keeping the committed fixdep case list and stdout/stderr packet reviewable without widening the broader Phase 2 manifest surface
- success coverage stays anchored by `sample_expected.txt` and `sample_multi_target_expected.txt`
- bounded failure coverage stays anchored by the comment-only parse error and missing-dependency open error fixtures in `zigux/tests/fixtures/fixdep/`
- helper-local anchors in `zig test scripts/zigux/fixdep.zig` now include `dep parsing returns NoTargets for comment-only depfiles`, `dep parsing skips bytes after the first embedded NUL`, `dependency file reads beyond the legacy one mebibyte ceiling`, and `output write failure uses C-style wording`

## Genksyms Bridge Closure Packet

The bounded genksyms wrapper-first bridge packet now records the committed request-plan and CLI-process fixtures explicitly so bridge-local review does not rely on the gate name alone:

- `PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=16`
- `PHASE2_GENKSYMS_BRIDGE_CASES=minimal,debug_reference_types,long_options,abbreviated_long_options,quiet_overrides_warning,explicit_option_terminator,positional_passthrough,help,abbreviated_help,version,abbreviated_version,invalid_option,missing_reference_argument,unsupported_long_option,missing_long_reference_argument,missing_long_dump_types_argument`
- `PHASE2_GENKSYMS_BRIDGE_STDOUT_PACKET=minimal_expected.json,debug_reference_types_expected.json,long_options_expected.json,abbreviated_long_options_expected.json,quiet_overrides_warning_expected.json,explicit_option_terminator_expected.json,positional_passthrough_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_PROCESS_PACKET=help_expected.json,version_expected.json,abbreviated_version_expected.json,invalid_option_expected.json,missing_reference_argument_expected.json,unsupported_long_option_expected.json,missing_long_reference_argument_expected.json,missing_long_dump_types_argument_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_NORMALIZED_STDERR_PACKET=invalid_option_expected.json,missing_reference_argument_expected.json,unsupported_long_option_expected.json,missing_long_reference_argument_expected.json,missing_long_dump_types_argument_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_ACTION_ABBREV_CASES=abbreviated_help,abbreviated_version`
- bridge-plan coverage stays anchored by the minimal invocation, repeated short-flag request, long-option request, unambiguous abbreviated-long-option request, quiet-overrides-warning request, explicit option terminator request, and positional passthrough request fixtures in `zigux/tests/fixtures/genksyms_bridge/`
- bridge-process coverage stays anchored by the help and abbreviated help fixtures, the version side-effect fixtures including `abbreviated_version_expected.json`, and the normalized invalid-option and missing-argument error fixtures in the same bounded packet
- helper-local anchors in `zig test scripts/zigux/genksyms.zig` now include `genksyms bridge accepts unambiguous abbreviated long options`

## Kconfig Conf Bridge Closure Packet

The bounded kconfig conf bridge packet now records the current request-plan fixtures explicitly so bridge-local review does not rely on the gate name alone:

- `PHASE2_KCONFIG_BRIDGE_CONF_CASE_COUNT=11`
- `PHASE2_KCONFIG_BRIDGE_CONF_CASES=olddefconfig,syncconfig,alldefconfig,allmodconfig,randconfig,yes2modconfig,mod2yesconfig,mod2noconfig,defconfig,savedefconfig,listnewconfig`
- `PHASE2_KCONFIG_BRIDGE_CONF_STDOUT_PACKET=olddefconfig_expected.json,syncconfig_expected.json,alldefconfig_expected.json,allmodconfig_expected.json,randconfig_expected.json,yes2modconfig_expected.json,mod2yesconfig_expected.json,mod2noconfig_expected.json,defconfig_expected.json,savedefconfig_expected.json,listnewconfig_expected.json`
- `PHASE2_KCONFIG_BRIDGE_ALLCONFIG_SENTINEL_PACKET=allmodconfig_expected.json`
- request-plan coverage stays anchored by the olddefconfig baseline, syncconfig auto-output env injection, alldefconfig mode selection, allmodconfig allconfig sentinel forwarding, randconfig seed and probability forwarding, yes2modconfig/mod2yesconfig/mod2noconfig mode selection, defconfig/savedefconfig mode-argument ordering, and listnewconfig request-plan fixtures in `zigux/tests/fixtures/kconfig_bridge/`
- allconfig sentinel coverage stays anchored by `allmodconfig_expected.json`, which keeps the bounded `allmodconfig` bridge packet explicit about forwarding `KCONFIG_ALLCONFIG=1`
- helper-local anchors in `zig test scripts/zigux/kconfig/conf_bridge.zig` now include `conf bridge emits syncconfig auto files`, `conf bridge emits alldefconfig argv and env`, `conf bridge emits allmodconfig argv and env`, `conf bridge emits randconfig tunables when present`, `conf bridge emits yes2modconfig argv and env`, `conf bridge emits defconfig mode argument before kconfig`, `conf bridge emits savedefconfig mode argument before kconfig`, and `conf bridge escapes low control bytes in JSON strings`

## Kconfig Confdata Bridge Closure Packet

The bounded kconfig confdata bridge packet now records the committed config inputs and expected JSON artifacts explicitly so confdata review does not rely on the shared gate name alone:

- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=10`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASES=sample,escaped_strings,escaped_control_sequences,trailing_escaped_backslash,sample_crlf,explicit_n_tristate,final_trailing_carriage_return,final_unterminated_unset_comment,uppercase_tristate,non_config_lines`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_EXPECTED_PACKET=sample_expected.json,escaped_strings_expected.json,escaped_control_sequences_expected.json,trailing_escaped_backslash_expected.json,sample_crlf_expected.json,explicit_n_tristate_expected.json,final_trailing_carriage_return_expected.json,final_unterminated_unset_comment_expected.json,uppercase_tristate_expected.json,non_config_lines_expected.json`
- input coverage stays anchored by `sample.config`, `escaped_strings.config`, `escaped_control_sequences.config`, `trailing_escaped_backslash.config`, `sample_crlf.config`, `explicit_n_tristate.config`, `final_trailing_carriage_return.config`, `final_unterminated_unset_comment.config`, `uppercase_tristate.config`, and `non_config_lines.config` in `zigux/tests/fixtures/kconfig_bridge/`
- expected-output coverage stays anchored by `sample_expected.json`, `escaped_strings_expected.json`, `escaped_control_sequences_expected.json`, `trailing_escaped_backslash_expected.json`, `sample_crlf_expected.json`, `explicit_n_tristate_expected.json`, `final_trailing_carriage_return_expected.json`, `final_unterminated_unset_comment_expected.json`, `uppercase_tristate_expected.json`, and `non_config_lines_expected.json` in the same bounded packet
- helper-local anchors in `zig test scripts/zigux/kconfig/confdata_bridge.zig` now include `confdata bridge decodes escaped quoted strings`, `confdata bridge decodes escaped control sequences in quoted strings`, `confdata bridge keeps trailing escaped backslashes in quoted strings`, `confdata bridge accepts CRLF config lines`, `confdata bridge preserves trailing carriage return on final unterminated value line`, `confdata bridge ignores unterminated unset comment with trailing carriage return`, `confdata bridge keeps explicit n assignments as tristate values`, `confdata bridge recognizes uppercase tristate assignments`, and `confdata bridge ignores non-CONFIG lines like upstream confdata`

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

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

1. shared artifact diff self-test
- `python3 scripts/zigux/artifact_diff.py --self-test`

2. bounded fixdep artifact parity and deterministic failure coverage
- `python3 scripts/zigux/check-fixdep-diff.py`
- repeat-run determinism is required for both the bounded C helper and the Zig tool before closure evidence stays green
- committed fixdep evidence now includes the primary, multi-target, escaped-whitespace, concatenated-depfile, comment-only, missing-dependency, and stdout write-failure cases under `zigux/tests/fixtures/fixdep/`
- the bounded stdout write-failure proof is anchored by `zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt`, which keeps the C-style `fixdep: not all data was written to the output` exit-1 surface explicit inside the closed Phase 2 packet
- `scripts/zigux/fixdep.zig` now keeps dependency-file reads aligned with the C helper by reading the full file size and mapping short writes to the same output error surface
- `PHASE2_FIXDEP_CASE_COUNT=7`
- `PHASE2_FIXDEP_OUTPUT_WRITE_CASE=zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt`

3. bounded genksyms CRC artifact parity
- `python3 scripts/zigux/check-genksyms-crc-diff.py`

4. bounded genksyms wrapper-first bridge parity
- `python3 scripts/zigux/check-genksyms-bridge.py`

5. bounded mk_elfconfig artifact parity
- `python3 scripts/zigux/check-mk-elfconfig-diff.py`

6. bounded kconfig bridge parity
- `python3 scripts/zigux/check-kconfig-bridge.py`

7. bounded phase2 cross-target compile gate
- `python3 scripts/zigux/check-phase2-cross.py`

8. bounded phase2 unit gates
- `zig test scripts/zigux/fixdep.zig`
- `zig test scripts/zigux/genksyms.zig`
- `zig test scripts/zigux/genksyms_crc.zig`
- `zig test scripts/zigux/mk_elfconfig.zig`
- `zig test scripts/zigux/kconfig/conf_bridge.zig`
- `zig test scripts/zigux/kconfig/confdata_bridge.zig`

9. closure validation
- `python3 scripts/zigux/validate-phase2-closure.py`

- `PHASE2_ARTIFACT_DIFF_SELF_TEST=python3 scripts/zigux/artifact_diff.py --self-test`
- `PHASE2_FIXDEP_GATE=python3 scripts/zigux/check-fixdep-diff.py`
- `PHASE2_FIXDEP_DETERMINISM=check-fixdep-diff.py replays C and Zig outputs twice before comparing artifacts`
- `PHASE2_FIXDEP_FULL_READ_POLICY=fixdep.zig reads dependency files at full C-helper size and maps short writes to fixdep output errors`
- `PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py`
- `PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py`
- `PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py`
- `PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py`

## Fixdep Evidence

The bounded `fixdep` closure packet remains closed because both the shared artifact lane and the helper-local unit lane cover the published edge cases:

- shared fixture packet:
  `sample_expected.txt`, `sample_multi_target_expected.txt`, `sample_escaped_space_expected.txt`, `sample_concatenated_expected.txt`, `sample_comment_only_expected.stderr.txt`, `sample_missing_dep_expected.stderr.txt`, `sample_output_write_expected.stderr.txt`
- helper-local anchors in `scripts/zigux/fixdep.zig`:
  `dep parsing keeps the first source across concatenated target entries`
  `output writer maps print and flush failures to fixdep output-write errors`

- `PHASE2_FIXDEP_EVIDENCE=artifact fixtures plus direct concatenated-target and output-write unit anchors are required for closure`

## Genksyms Bridge Evidence

The bounded `genksyms` closure packet remains closed because both the shared bridge fixtures and the helper-local unit lane cover the published getopt-style wrapper behavior:

- shared fixture packet:
  `minimal_expected.json`, `debug_reference_types_expected.json`, `short_inline_reference_dump_types_expected.json`, `long_options_expected.json`, `abbreviated_long_options_expected.json`, `quiet_overrides_warning_expected.json`, `explicit_option_terminator_expected.json`, `positional_passthrough_expected.json`, `lone_dash_passthrough_expected.json`, `explicit_terminator_positional_passthrough_expected.json`, `help_expected.json`, `version_expected.json`, `invalid_option_expected.json`, `missing_reference_argument_expected.json`, `unsupported_long_option_expected.json`, `ambiguous_abbreviated_long_option_expected.json`, `empty_long_option_name_expected.json`, `unexpected_long_option_argument_expected.json`, `abbreviated_unexpected_long_option_argument_expected.json`, `missing_long_reference_argument_expected.json`, `abbreviated_missing_long_reference_argument_expected.json`, `missing_long_dump_types_argument_expected.json`, `abbreviated_missing_long_dump_types_argument_expected.json`
- helper-local anchors in `scripts/zigux/genksyms.zig`:
  `genksyms bridge accepts abbreviated unique long options`
  `genksyms bridge treats lone dash as positional passthrough`
  `genksyms bridge permutes prior positionals behind explicit terminator`
  `genksyms bridge canonicalizes abbreviated dump-types missing-argument errors`

- `PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=23`
- `PHASE2_GENKSYMS_BRIDGE_INLINE_SHORT_CASE=zigux/tests/fixtures/genksyms_bridge/short_inline_reference_dump_types_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_POSITIONAL_CASES=zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_terminator_positional_passthrough_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_EVIDENCE=artifact fixtures plus abbreviated-long, inline-short, lone-dash, explicit-terminator, empty-long-name, and abbreviated-dump-types coverage are required for closure`

## Kconfig Bridge Evidence

The bounded `kconfig` bridge closure packet remains closed because both the shared fixture packet and the helper-local unit lane cover the published wrapper and confdata summary edges:

- shared fixture packet:
  `listnewconfig_expected.json`, `helpnewconfig_expected.json`, `duplicate_assignments_expected.json`, `escaped_control_sequences_expected.json`, `escaped_low_control_bytes_expected.json`
- helper-local anchors in `scripts/zigux/kconfig/confdata_bridge.zig`:
  `confdata bridge decodes escaped control sequences in quoted strings`
  `confdata bridge escapes low control bytes in emitted json`

- `PHASE2_KCONFIG_BRIDGE_LOW_CONTROL_CASE=zigux/tests/fixtures/kconfig_bridge/escaped_low_control_bytes_expected.json`
- `PHASE2_KCONFIG_BRIDGE_EVIDENCE=artifact fixtures plus confdata escaped-control decode and low-control JSON emission anchors are required for closure`

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

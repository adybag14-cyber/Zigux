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

## Toolchain Pin Scope

The bounded Phase 2 bootstrap archive pin remains intentionally limited to the current workflow host runner target:

- `x86_64-linux`
- policy file: `scripts/zigux/zig-toolchain-policy.json`
- guard: `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- the archive pin must not broaden beyond `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence
- `PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json keeps the bootstrap archive pin limited to x86_64-linux until a new runner target gains first-class workflow evidence`

## Closure Gates

Phase 2 is only considered closed when all of the following are green:

1. shared artifact diff self-test and CLI contract replay
- `python3 scripts/zigux/artifact_diff.py --self-test`
- `python3 scripts/zigux/check-artifact-diff-contract.py`

2. bounded fixdep artifact parity and deterministic failure coverage
- `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- the checker self-test must stay in the Linux-style `phase2-tools` path before live artifact replay so case-manifest drift, explicit-tool drift, and unsupported stdout-mode changes cannot hide behind a locally passing parity run
- `python3 scripts/zigux/check-fixdep-diff.py`
- repeat-run determinism is required for both the bounded C helper and the Zig tool before closure evidence stays green
- committed fixdep evidence now includes eleven bounded review cases under `zigux/tests/fixtures/fixdep/`: primary, multi-target, escaped-whitespace, escaped-colon, concatenated-depfile, comment-continued, comment-only, comment-only stdout-full, missing-dependency, missing-dependency stdout-full, and stdout write-failure
- the bounded stdout write-failure proof is anchored by `zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt`, which keeps the C-style `fixdep: not all data was written to the output` exit-1 surface explicit inside the closed Phase 2 packet
- `scripts/zigux/fixdep.zig` now keeps dependency-file reads aligned with the C helper by reading the full file size and mapping short writes to the same output error surface
- `PHASE2_FIXDEP_CASE_COUNT=11`
- `PHASE2_FIXDEP_SHARED_STDOUT_PACKET=zigux/tests/fixtures/fixdep/sample_expected.txt,zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt,zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt,zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt,zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt,zigux/tests/fixtures/fixdep/sample_comment_continued_expected.txt,zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt,zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt,zigux/tests/fixtures/fixdep/sample_output_write_expected.txt`
- `PHASE2_FIXDEP_SHARED_STDERR_PACKET=zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt,zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt,zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt`
- `PHASE2_FIXDEP_OUTPUT_WRITE_CASE=zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt`

3. bounded genksyms CRC artifact parity and determinism
- `python3 scripts/zigux/check-genksyms-crc-diff.py --self-test`
- the checker self-test must stay in the Linux-style `phase2-tools` path before live artifact replay so explicit-tool passthrough drift, mismatch-contract drift, and repeat-run compare coverage cannot hide behind local compiler or Zig availability
- `python3 scripts/zigux/check-genksyms-crc-diff.py`

4. bounded genksyms wrapper-first bridge parity
- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- the checker self-test must stay in the Linux-style `phase2-tools` path before live bridge replay so missing-expected-fixture drift, duplicate expected-fixture wiring, stderr-mode contract drift, and repeat-run compare coverage cannot hide behind a locally passing parity run
- `python3 scripts/zigux/check-genksyms-bridge.py`
- `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`
- the dedicated alignment checker keeps the bridge checker, shared validator, closure validator, workflow wiring, Makefile route, scripts index, and 26-case manifest packet in sync before closure evidence stays green

5. bounded mk_elfconfig artifact parity and determinism
- `python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test`
- the checker self-test must stay in the Linux-style `phase2-tools` path before live artifact replay so fixture-shape and explicit-tool drift cannot hide behind local compiler or Zig availability
- `python3 scripts/zigux/check-mk-elfconfig-diff.py`
- repeat-run determinism is required for both the bounded C tool and the Zig tool before closure evidence stays green

6. bounded kconfig bridge parity and determinism
- `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- `python3 scripts/zigux/check-kconfig-bridge.py`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- the checker self-test must stay in the Linux-style `phase2-kconfig` path before live replay so manifest-ordering and failure-shape drift cannot hide behind the bounded bridge artifacts
- the checker self-test must emit `KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=6` so the bounded synthetic four-conf-case plus two-confdata-case packet stays explicit before live replay
- the dedicated alignment checker keeps `check-kconfig-bridge.py`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/tests/fixtures/kconfig_bridge/cases.json`, the bootstrap workflow route, and `zigux/Makefile` in sync before closure evidence stays green
- the conf bridge packet must keep required positional input rejection explicit: empty `Kconfig`, `.config`, and `ARCH` values must fail before bridge JSON emission
- conf and confdata repeat-run JSON determinism is required before closure evidence stays green, and confdata replay must also stay stable across a second binary rebuild in the same check packet

7. bounded phase2 cross-target compile gate
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- the checker self-test must stay in the Linux-style `phase2-cross` path before live compile replay so duplicate tool entries, duplicate requested targets, unexpected explicit targets, duplicate manifest targets, manifest-count drift, and explicit-target failure drift cannot hide behind local Zig availability
- `python3 scripts/zigux/check-phase2-cross.py`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- the dedicated alignment checker keeps `check-phase2-cross.py`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `Documentation/zigux/phase2-closure.md`, and `zigux/tests/fixtures/phase2_cross_targets.json` in sync before closure evidence stays green

8. bounded phase2 toolchain pin-scope guard
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- the dedicated pin-scope guard keeps `scripts/zigux/zig-toolchain-policy.json`, the bootstrap workflow `install-zig.py --dest .zig-toolchain` and `check-zig-toolchain.py` steps, and `scripts/zigux/validate-phase2.py` aligned around the current `x86_64-linux`-only archive pin until a new bootstrap runner target gains first-class workflow evidence

9. bounded shared phase2 validator gate
- `python3 scripts/zigux/validate-phase2.py`

10. bounded phase2 unit gates
- `zig test scripts/zigux/fixdep.zig`
- `zig test scripts/zigux/genksyms.zig`
- `zig test scripts/zigux/genksyms_crc.zig`
- `zig test scripts/zigux/mk_elfconfig.zig`
- `zig test scripts/zigux/kconfig/conf_bridge.zig`
- `zig test scripts/zigux/kconfig/confdata_bridge.zig`

11. closure validation
- `python3 scripts/zigux/validate-phase2-closure.py`

- `PHASE2_ARTIFACT_DIFF_SELF_TEST=python3 scripts/zigux/artifact_diff.py --self-test`
- `PHASE2_ARTIFACT_DIFF_CONTRACT=python3 scripts/zigux/check-artifact-diff-contract.py`
- `PHASE2_FIXDEP_SELF_TEST=python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `PHASE2_FIXDEP_GATE=python3 scripts/zigux/check-fixdep-diff.py`
- `PHASE2_FIXDEP_DETERMINISM=check-fixdep-diff.py replays C and Zig outputs twice before comparing artifacts`
- `PHASE2_FIXDEP_FULL_READ_POLICY=fixdep.zig reads dependency files at full C-helper size and maps short writes to fixdep output errors`
- `PHASE2_GENKSYMS_CRC_SELF_TEST=python3 scripts/zigux/check-genksyms-crc-diff.py --self-test`
- `PHASE2_GENKSYMS_CRC_GATE=python3 scripts/zigux/check-genksyms-crc-diff.py`
- `PHASE2_GENKSYMS_CRC_DETERMINISM=check-genksyms-crc-diff.py replays C and Zig outputs twice before comparing artifacts`
- `PHASE2_MK_ELFCONFIG_SELF_TEST=python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test`
- `PHASE2_GENKSYMS_BRIDGE_SELF_TEST=python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py`
- `PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`
- `PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`
- `PHASE2_GENKSYMS_BRIDGE_DETERMINISM=check-genksyms-bridge.py replays C and Zig bridge outputs twice before comparing artifacts`
- `PHASE2_MK_ELFCONFIG_GATE=python3 scripts/zigux/check-mk-elfconfig-diff.py`
- `PHASE2_MK_ELFCONFIG_DETERMINISM=check-mk-elfconfig-diff.py replays C and Zig outputs twice before comparing artifacts`
- `PHASE2_KCONFIG_BRIDGE_SELF_TEST=python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- `PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py`
- `PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- `PHASE2_KCONFIG_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `PHASE2_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=6`
- `PHASE2_KCONFIG_BRIDGE_DETERMINISM=check-kconfig-bridge.py replays conf and confdata outputs twice and compares a rebuilt confdata binary against the same JSON artifacts`
- `PHASE2_KCONFIG_BRIDGE_REQUIRED_INPUT_POLICY=conf bridge rejects empty Kconfig, .config, and ARCH positional inputs before emitting bridge JSON`
- `PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test`
- `PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py`
- `PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `PHASE2_CROSS_MANIFEST_POLICY=check-phase2-cross.py rejects duplicate tool entries, duplicate requested targets, unexpected explicit targets, duplicate manifest targets, and manifest-count drift before live compile replay`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json keeps the bootstrap archive pin limited to x86_64-linux until a new runner target gains first-class workflow evidence`
- `PHASE2_SHARED_VALIDATOR=python3 scripts/zigux/validate-phase2.py`
- `PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py`

## Fixdep Evidence

The bounded `fixdep` closure packet remains closed because both the shared artifact lane and the helper-local unit lane cover the published edge cases:

- shared fixture packet:
  `cases.json`, `sample_expected.txt`, `sample_multi_target_expected.txt`, `sample_escaped_space_expected.txt`, `sample_escaped_colon_expected.txt`, `sample_concatenated_expected.txt`, `sample_comment_continued_expected.txt`, `sample_comment_only_expected.txt`, `sample_comment_only_expected.stderr.txt`, `sample_missing_dep_expected.txt`, `sample_missing_dep_expected.stderr.txt`, `sample_output_write_expected.txt`, `sample_output_write_expected.stderr.txt`
- helper-local anchors in `scripts/zigux/fixdep.zig`:
  `dep parsing skips escaped-newline comments before the first target`
  `dep parsing continues dependency tokens across escaped newlines`
  `dep parsing keeps the first source across concatenated target entries`
  `dep parsing unescapes escaped hash and colon tokens once`
  `dependency file error messages keep C helper wording`
  `missing dependency path is preserved for later error reporting`
  `output writer maps print and flush failures to fixdep output-write errors`
  `preserving a primary error ignores late output flush failures`

- `PHASE2_FIXDEP_EVIDENCE=artifact fixtures plus direct escaped-newline-comment, dep-continuation, concatenated-target, escaped-token, dependency-file-error, missing-path-preservation, output-write, and primary-error-preservation unit anchors are required for closure`

## Genksyms Bridge Evidence

The bounded `genksyms` closure packet remains closed because both the shared bridge fixtures and the helper-local unit lane cover the published getopt-style wrapper behavior:

- shared fixture packet:
  `minimal_expected.json`, `debug_reference_types_expected.json`, `short_inline_reference_dump_types_expected.json`, `clustered_short_inline_reference_expected.json`, `long_options_expected.json`, `abbreviated_long_options_expected.json`, `quiet_overrides_warning_expected.json`, `explicit_option_terminator_expected.json`, `positional_passthrough_expected.json`, `lone_dash_passthrough_expected.json`, `explicit_terminator_positional_passthrough_expected.json`, `help_expected.json`, `version_expected.json`, `invalid_option_expected.json`, `missing_reference_argument_expected.json`, `missing_dump_types_argument_expected.json`, `unsupported_long_option_expected.json`, `ambiguous_abbreviated_long_option_expected.json`, `empty_long_option_name_expected.json`, `unexpected_long_option_argument_expected.json`, `abbreviated_unexpected_long_option_argument_expected.json`, `missing_long_reference_argument_expected.json`, `abbreviated_missing_long_reference_argument_expected.json`, `missing_long_dump_types_argument_expected.json`, `abbreviated_missing_long_dump_types_argument_expected.json`, `too_many_reference_files_expected.json`
- success-path stderr silence:
  `check-genksyms-bridge.py` now captures stderr for every `stdout_json` bridge fixture, rejects any success-path stderr drift for both the bounded C harness and the Zig tool, and replays those stderr captures twice so repeat-run determinism stays explicit instead of assuming quiet success
- alignment guard:
  `check-phase2-genksyms-bridge-selftest-alignment.py` now keeps the bridge checker self-test markers, the published scripts index and closure note, the shared validator pair, the workflow route, the Makefile route, and the committed 26-case fixture manifest aligned as one bounded review packet instead of leaving that relationship implicit
- helper-local anchors in `scripts/zigux/genksyms.zig`:
  `genksyms bridge parses clustered short flags before inline reference argument`
  `genksyms bridge accepts abbreviated unique long options`
  `genksyms bridge treats lone dash as positional passthrough`
  `genksyms bridge permutes prior positionals behind explicit terminator`
  `genksyms bridge reports missing short dump-types argument in getopt style`
  `genksyms bridge canonicalizes abbreviated dump-types missing-argument errors`
  `genksyms bridge rejects reference lists beyond the bounded C harness limit`

- `PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=26`
- `PHASE2_GENKSYMS_BRIDGE_INLINE_SHORT_CASE=zigux/tests/fixtures/genksyms_bridge/short_inline_reference_dump_types_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_CLUSTERED_SHORT_INLINE_CASE=zigux/tests/fixtures/genksyms_bridge/clustered_short_inline_reference_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_MISSING_SHORT_DUMP_TYPES_CASE=zigux/tests/fixtures/genksyms_bridge/missing_dump_types_argument_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_POSITIONAL_CASES=zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_terminator_positional_passthrough_expected.json`
- `PHASE2_GENKSYMS_BRIDGE_STDERR_POLICY=success-path stderr silence plus repeat-run stderr determinism are required for closure`
- `PHASE2_GENKSYMS_BRIDGE_EVIDENCE=artifact fixtures plus abbreviated-long, inline-short, clustered-short-inline, missing-short-dump-types, lone-dash, explicit-terminator, empty-long-name, abbreviated-dump-types, and reference-limit coverage are required for closure`

## Kconfig Bridge Evidence

The bounded `kconfig` bridge closure packet remains closed because the shared fixture packet, manifest-determinism gate, and helper-local unit lanes cover the published wrapper and confdata summary edges:

- shared wrapper and summary packet:
  `oldaskconfig_expected.json`, `olddefconfig_expected.json`, `oldconfig_expected.json`, `listnewconfig_expected.json`, `helpnewconfig_expected.json`, `yes2modconfig_expected.json`, `mod2yesconfig_expected.json`, `defconfig_expected.json`, `savedefconfig_expected.json`, `mod2noconfig_expected.json`, `allnoconfig_expected.json`, `allyesconfig_expected.json`, `allmodconfig_expected.json`, `alldefconfig_expected.json`, `randconfig_expected.json`, `syncconfig_expected.json`, `duplicate_assignments_expected.json`, `empty_string_expected.json`, `empty_symbol_names_expected.json`, `escaped_control_sequences_expected.json`, `escaped_low_control_bytes_expected.json`, `escaped_strings_expected.json`, `explicit_n_tristate_expected.json`, `final_trailing_carriage_return_expected.json`, `final_unterminated_unset_comment_expected.json`, `ignore_non_config_lines_expected.json`, `malformed_quoted_string_expected.json`, `negative_signed_numeric_kinds_expected.json`, `numeric_kinds_expected.json`, `quoted_suffix_bytes_expected.json`, `sample_expected.json`, `sample_crlf_expected.json`, `signed_numeric_kinds_expected.json`, `trailing_escaped_backslash_expected.json`
- bridge manifest hardening:
  `check-kconfig-bridge.py` rejects uncovered conf bridge modes, unsorted conf-case order, malformed manifest shape, duplicate fixture references, orphaned fixture files, and non-canonical confdata fixture naming before replaying the bounded artifacts
- checker self-test breadth marker:
  `check-kconfig-bridge.py --self-test` now emits `KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=6` so the bounded synthetic four-conf-case plus two-confdata-case packet stays explicit before live replay
- helper-local anchors in `scripts/zigux/kconfig/conf_bridge.zig`:
  `conf bridge emits allconfig env for allconfig family modes`
  `conf bridge requires mode arg for defconfig modes`
  `conf bridge emits savedefconfig mode argument before kconfig`
  `conf bridge rejects empty Kconfig path arguments`
  `conf bridge rejects empty config path arguments`
  `conf bridge rejects empty arch arguments`
  `conf bridge escapes low control bytes in argv and env values`
- helper-local anchors in `scripts/zigux/kconfig/confdata_bridge.zig`:
  `confdata bridge decodes escaped control sequences in quoted strings`
  `confdata bridge keeps empty quoted strings as string values`
  `confdata bridge keeps explicit n assignments as tristate values`
  `confdata bridge skips entries with empty symbol names`
  `confdata bridge skips malformed quoted strings`
  `confdata bridge distinguishes integer, hex, and fallback scalar values`
  `confdata bridge keeps quoted payloads before trailing suffix bytes`
  `confdata bridge accepts CRLF config lines`
  `confdata bridge rejects empty config path arguments`
  `confdata bridge escapes low control bytes in emitted json`

- `PHASE2_KCONFIG_BRIDGE_CONF_CASE_COUNT=16`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=18`
- `PHASE2_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=6`
- `PHASE2_KCONFIG_BRIDGE_ALLCONFIG_CASES=zigux/tests/fixtures/kconfig_bridge/allnoconfig_expected.json,zigux/tests/fixtures/kconfig_bridge/randconfig_expected.json`
- `PHASE2_KCONFIG_BRIDGE_ARGUMENT_CASES=zigux/tests/fixtures/kconfig_bridge/defconfig_expected.json,zigux/tests/fixtures/kconfig_bridge/savedefconfig_expected.json`
- `PHASE2_KCONFIG_BRIDGE_LOW_CONTROL_CASE=zigux/tests/fixtures/kconfig_bridge/escaped_low_control_bytes_expected.json`
- `PHASE2_KCONFIG_BRIDGE_MANIFEST_POLICY=check-kconfig-bridge.py rejects uncovered modes, malformed manifests, duplicate fixture references, orphaned fixture files, and non-canonical confdata names before replay`
- `PHASE2_KCONFIG_BRIDGE_EVIDENCE=artifact fixtures plus conf bridge mode coverage, allconfig env, mode-arg, manifest-determinism, confdata escaped-control decode, empty-string, empty-symbol, explicit-n, malformed-quote, signed-numeric, trailing-unset-comment, quoted-suffix, CRLF, trailing-escaped-backslash, empty-path rejection, and low-control JSON emission anchors are required for closure`

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

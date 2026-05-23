#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain pinning packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
EXPECTED_ARCHIVE_SIZES = {"x86_64-linux": 58_159_088}
ARCHIVE_README_REQUIRED_MARKER_COUNT = 10

SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py",
    ROOT / "scripts" / "zigux" / "check-lane05-install-zig-archive-verification.py",
    ROOT / "scripts" / "zigux" / "stage-pinned-zig-archive.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-contract.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-selftest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-genksyms-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-artifact-tools-manifest.py",
    ROOT / "scripts" / "zigux" / "artifact_diff.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
    ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "scripts" / "zigux" / "genksyms_version_before_invalid_long_option_test.zig",
    ROOT / "scripts" / "zigux" / "genksyms_version_before_ambiguous_long_option_test.zig",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    THIRD_PARTY_README,
    ROOT / "zigux" / "Makefile",
    POLICY_PATH,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    TOOL_MANIFEST_PATH,
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "help_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "minimal_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "debug_reference_types_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "long_options_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "abbreviated_long_options_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "quiet_overrides_warning_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "explicit_option_terminator_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "positional_passthrough_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "lone_dash_passthrough_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "dash_prefixed_long_option_arguments_as_data_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "abbreviated_version_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "ambiguous_long_option_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "invalid_option_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "missing_long_dump_types_argument_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "missing_long_reference_argument_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "missing_reference_argument_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "too_many_reference_files_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "unsupported_long_option_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "unexpected_long_help_argument_expected.json",
)

WORKFLOW_SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: make -C zigux phase2-fixdep",
    "run: python3 scripts/zigux/validate-phase2.py",
)

BOOTSTRAP_PRESENT_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
)

BOOTSTRAP_GAP_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.",
)

PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-fixdep`",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-fixdep`",
)

TESTS_MARKERS = SCRIPTS_MARKERS

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel_minimum_lockstep": True,
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
}

EXPECTED_TOOL_MANIFEST = json.loads(
    r"""{"notes":["Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the dedicated genksyms selftest-alignment guard, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the fixdep governance and parity checker pair, and the restored tranche-closure note.","Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.","Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.","Keep the dedicated manifest guards, the primary artifact_diff helper, and the dedicated genksyms selftest-alignment guard explicit through scripts/zigux/check-phase2-tool-manifest.py, scripts/zigux/check-phase2-artifact-tools-manifest.py, scripts/zigux/artifact_diff.py, and scripts/zigux/check-phase2-genksyms-selftest-alignment.py so Phase 2 packet drift fails closed beside the other reminder checkers.","Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.","Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket."],"phase":"Phase 2","present_surfaces":{"archive_support":["third_party/README.md","third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"],"artifact_support":["scripts/zigux/artifact_diff.py","scripts/zigux/check-phase2-artifact-tools-manifest.py","zigux/tests/fixtures/phase2_artifact_tools_manifest.json"],"bootstrap_helpers":["scripts/zigux/install-zig.py","scripts/zigux/stage-pinned-zig-archive.py"],"bridge_helpers":["scripts/zigux/kconfig/conf_bridge.zig","scripts/zigux/kconfig/confdata_bridge.zig","scripts/zigux/genksyms.zig","scripts/zigux/genksyms_version_before_invalid_long_option_test.zig","scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"],"checkers":["scripts/zigux/check-zig-toolchain.py","scripts/zigux/check-lane05-local-first-archive-workflow.py","scripts/zigux/check-lane05-local-archive-readme.py","scripts/zigux/check-lane05-install-zig-archive-verification.py","scripts/zigux/check-lane05-stage-helper-contract.py","scripts/zigux/check-lane05-stage-helper-selftest.py","scripts/zigux/check-kconfig-bridge.py","scripts/zigux/check-phase2-kconfig-selftest-alignment.py","scripts/zigux/check-phase2-genksyms-selftest-alignment.py","scripts/zigux/check-phase2-kbuild-routes.py","scripts/zigux/check-phase2-tests-readme-alignment.py","scripts/zigux/check-phase2-cross.py","scripts/zigux/check-phase2-cross-selftest-alignment.py","scripts/zigux/check-phase2-toolchain-pinning.py","scripts/zigux/check-phase2-toolchain-pin-scope.py","scripts/zigux/check-phase2-required-make-routes.py","scripts/zigux/check-phase2-docs-shared-reminder.py","scripts/zigux/check-phase2-tool-manifest.py","scripts/zigux/check-phase2-artifact-tools-manifest.py","scripts/zigux/check-genksyms-bridge.py","scripts/zigux/check-phase2-fixdep-gate.py","scripts/zigux/check-fixdep-diff.py"],"closure_notes":["Documentation/zigux/phase2-closure.md","Documentation/zigux/phase2-toolchain-bootstrap-notes.md"],"cross_route_support":["scripts/zigux/check-phase2-cross.py","zigux/tests/fixtures/phase2_cross_targets.json"],"fixdep_support":["scripts/basic/fixdep.c","scripts/zigux/check-phase2-fixdep-gate.py","scripts/zigux/check-fixdep-diff.py","scripts/zigux/fixdep.zig","zigux/tests/fixtures/fixdep/cases.json","zigux/tests/fixtures/fixdep/dep\\ name.rmeta","zigux/tests/fixtures/fixdep/escaped\\ space-config.h","zigux/tests/fixtures/fixdep/sample-config.h","zigux/tests/fixtures/fixdep/sample.c","zigux/tests/fixtures/fixdep/sample.d","zigux/tests/fixtures/fixdep/sample.h","zigux/tests/fixtures/fixdep/sample.rmeta","zigux/tests/fixtures/fixdep/sample2-config.h","zigux/tests/fixtures/fixdep/sample2.c","zigux/tests/fixtures/fixdep/sample2.so","zigux/tests/fixtures/fixdep/sample_comment_continuation.d","zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so","zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt","zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c","zigux/tests/fixtures/fixdep/sample_comment_continuation_source.rmeta","zigux/tests/fixtures/fixdep/sample_comment_only.d","zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt","zigux/tests/fixtures/fixdep/sample_concatenated.d","zigux/tests/fixtures/fixdep/sample_concatenated_dep.h","zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt","zigux/tests/fixtures/fixdep/sample_concatenated_source.c","zigux/tests/fixtures/fixdep/sample_concatenated_temp.c","zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h","zigux/tests/fixtures/fixdep/sample_dependency_continuation.d","zigux/tests/fixtures/fixdep/sample_dependency_continuation_dep.so","zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt","zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c","zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.rmeta","zigux/tests/fixtures/fixdep/sample_double_backslash_comment.d","zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.txt","zigux/tests/fixtures/fixdep/sample_double_backslash_comment_source.rmeta","zigux/tests/fixtures/fixdep/sample_escaped_colon.d","zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt","zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c","zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta","zigux/tests/fixtures/fixdep/sample_escaped_space.d","zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt","zigux/tests/fixtures/fixdep/sample_escaped_space_source.c","zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta","zigux/tests/fixtures/fixdep/sample_expected.txt","zigux/tests/fixtures/fixdep/sample_missing_dep.d","zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt","zigux/tests/fixtures/fixdep/sample_missing_dep_source.c","zigux/tests/fixtures/fixdep/sample_multi_target.d","zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt","zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_output_write_expected.txt","zigux/tests/fixtures/fixdep/shared#config.h","zigux/tests/fixtures/fixdep/shared:config.h"],"fixture_roster":["zigux/tests/fixtures/kconfig_bridge/cases.json","zigux/tests/fixtures/kconfig_bridge/conf_manifest.json","zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json","zigux/tests/fixtures/kconfig_bridge/oldaskconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/syncconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/oldconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/allnoconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/allyesconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/allmodconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/alldefconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/randconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/defconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/savedefconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/listnewconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/helpnewconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/olddefconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/yes2modconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/mod2yesconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/mod2noconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/sample.config","zigux/tests/fixtures/kconfig_bridge/escaped_strings.config","zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences.config","zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash.config","zigux/tests/fixtures/kconfig_bridge/sample_crlf.config","zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate.config","zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return.config","zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment.config","zigux/tests/fixtures/kconfig_bridge/uppercase_tristate.config","zigux/tests/fixtures/kconfig_bridge/non_config_lines.config","zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names.config","zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens.config","zigux/tests/fixtures/kconfig_bridge/last_state_transitions.config","zigux/tests/fixtures/kconfig_bridge/duplicate_assignments.config","zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment.config","zigux/tests/fixtures/kconfig_bridge/sample_expected.json","zigux/tests/fixtures/kconfig_bridge/escaped_strings_expected.json","zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences_expected.json","zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash_expected.json","zigux/tests/fixtures/kconfig_bridge/sample_crlf_expected.json","zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate_expected.json","zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return_expected.json","zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment_expected.json","zigux/tests/fixtures/kconfig_bridge/uppercase_tristate_expected.json","zigux/tests/fixtures/kconfig_bridge/non_config_lines_expected.json","zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names_expected.json","zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens_expected.json","zigux/tests/fixtures/kconfig_bridge/last_state_transitions_expected.json","zigux/tests/fixtures/kconfig_bridge/duplicate_assignments_expected.json","zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment_expected.json","zigux/tests/fixtures/genksyms_bridge/cases.json","zigux/tests/fixtures/genksyms_bridge/help_expected.json","zigux/tests/fixtures/genksyms_bridge/manifest.json","zigux/tests/fixtures/genksyms_bridge/minimal_expected.json","zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json","zigux/tests/fixtures/genksyms_bridge/long_options_expected.json","zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json","zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json","zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json","zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json","zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json","zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json","zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json","zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json","zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json","zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json","zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json","zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json","zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json","zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json","zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"],"make_wrappers":["zigux/Makefile","make -C zigux phase2-toolchain","make -C zigux phase2-tools","make -C zigux phase2-kconfig","make -C zigux phase2-cross","make -C zigux phase2-genksyms","make -C zigux phase2-fixdep","make -C zigux phase2-validate","make -C zigux phase2"],"policy":["scripts/zigux/zig-toolchain-policy.json"],"review_surfaces":["Documentation/zigux/README.md","Documentation/zigux/phase2-closure.md","Documentation/zigux/review-checklist.md","zigux/tests/README.md"],"validators":["scripts/zigux/validate-phase2.py","scripts/zigux/validate-phase2-closure.py"]},"repo_reality_gaps":[],"scope":"current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet","status":"active","workflow":".github/workflows/zigux-bootstrap.yml"}"""
)

EXPECTED_SELF_TEST_CASE_COUNT = 13


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def extract_markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    start = text.find("\n", start)
    if start == -1:
        return ""
    start += 1
    end = text.find("\n## ", start)
    if end == -1:
        end = len(text)
    return text[start:end]


def expected_archive_filename(target: str, channel: str) -> str:
    return f"zig-{target}-{channel}.tar.xz"


def duplicate_archive_name(expected_filename: str) -> str:
    return f"{expected_filename[:-len('.tar.xz')]} (1).tar.xz"


def archive_readme_markers(target: str, channel: str, sha256: str, expected_size: int) -> tuple[str, ...]:
    expected_filename = expected_archive_filename(target, channel)
    return (
        f"`third_party/{expected_filename}`",
        f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/{expected_filename} --archive-target {target}`",
        f"`{sha256}`",
        f"`{expected_size}`",
        f"`{duplicate_archive_name(expected_filename)}`",
        "repo-local pinned archive filename",
        "digest",
        "size",
        "duplicate-copy boundary",
        "archive-only",
    )


def load_policy(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, POLICY_PATH)))


def load_tool_manifest(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, TOOL_MANIFEST_PATH)))


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = load_policy(root)
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]
    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]
    if upgrade_policy.get("channel_minimum_lockstep") is not EXPECTED_POLICY["channel_minimum_lockstep"]:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep"))))
    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade_policy.get("archive_target_scope"))))
    if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY[